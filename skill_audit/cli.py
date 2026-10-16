"""Command Line Interface for Skill-Audit using Click and Rich."""

from __future__ import annotations

import json
import shutil
import sys
import zipfile
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from skill_audit.engine import AuditEngine
from skill_audit.exporters import (
    CSVExporter,
    ReportExporter,
    SkillExporter,
    WebExporter,
)
from skill_audit.models import AuditDomain, AuditPack, RiskLevel
from skill_audit.validation import validate_audit_pack

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="skill-audit")
def cli() -> None:
    """Skill-Audit: Engine & Agent Skill for Comprehensive Document & Audit Dossier Auditing."""
    pass


@cli.command("doc")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--output", "-o", default="output", help="Output directory for generated audit pack.")
@click.option("--format", "-f", "fmt", type=click.Choice(["pack", "report", "web", "all"]), default="all", help="Output format.")
@click.option("--title", "-t", default=None, help="Custom audit title.")
def audit_doc(file_path: str, output: str, fmt: str, title: str | None) -> None:
    """Audit a single document (PDF, Excel, Word, Text)."""
    p = Path(file_path)
    console.print(f"[bold cyan]🔍 Mengaudit Dokumen Tunggal:[/] [white]{p.name}[/]")

    engine = AuditEngine()
    pack = engine.audit(p, title=title)
    _render_summary_panel(pack)
    _export_deliverables(pack, output, fmt)


@cli.command("dossier")
@click.argument("dossier_path", type=click.Path(exists=True))
@click.option("--output", "-o", default="output", help="Output directory for generated audit pack.")
@click.option("--format", "-f", "fmt", type=click.Choice(["pack", "report", "web", "all"]), default="all", help="Output format.")
@click.option("--checklist", "-c", default=None, help="Path to custom checklist YAML file.")
@click.option("--title", "-t", default=None, help="Custom audit title.")
def audit_dossier(dossier_path: str, output: str, fmt: str, checklist: str | None, title: str | None) -> None:
    """Audit an entire dossier folder or ZIP bundle with 3-Way Matching and cross-checks."""
    p = Path(dossier_path)
    console.print(f"[bold cyan]📂 Mengaudit Berkas Audit Keseluruhan (Dossier):[/] [white]{p.name}[/]")

    engine = AuditEngine(checklist_config=checklist)
    pack = engine.audit(p, title=title)
    _render_summary_panel(pack)
    _export_deliverables(pack, output, fmt)


@cli.command("cross-check")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--output", "-o", default="output", help="Output directory.")
@click.option("--title", "-t", default="Uji Silang Dokumen (Cross-Check)", help="Audit title.")
def cross_check(files: tuple[str, ...], output: str, title: str) -> None:
    """Run 3-Way Matching and multi-document reconciliation across 2+ files."""
    if len(files) < 2:
        console.print("[bold red]Error:[/] Uji silang membutuhkan minimal 2 dokumen (misal: Kontrak vs Invoice vs BAST).")
        sys.exit(1)

    console.print(f"[bold cyan]⚖️ Menjalankan Uji Silang atas {len(files)} Dokumen...[/]")
    engine = AuditEngine()
    pack = engine.cross_check_files(list(files), title=title)
    _render_summary_panel(pack)
    _export_deliverables(pack, output, "all")


@cli.command("verify")
@click.argument("pack_yaml", type=click.Path(exists=True))
@click.option("--strict", is_flag=True, help="Strict mode: require verbatim source quotes for every finding.")
@click.option("--json", "json_mode", is_flag=True, help="Output results in JSON format.")
def verify(pack_yaml: str, strict: bool, json_mode: bool) -> None:
    """Validate AuditPack integrity, 5C completeness, and evidence grounding (CI/CD gate)."""
    pack = AuditPack.from_yaml(pack_yaml)
    report = validate_audit_pack(pack, strict=strict)

    if json_mode:
        console.print(json.dumps(report.to_dict(), indent=2))
        sys.exit(0 if report.ok else 1)

    # Rich formatting
    table = Table(title=f"Hasil Validasi AuditPack: {pack.title}", border_style="cyan")
    table.add_column("Tingkat", style="bold")
    table.add_column("Kode", style="dim")
    table.add_column("Pesan Validasi")

    for err in report.errors:
        table.add_row("[red]ERROR[/red]", err.code, err.message)
    for warn in report.warnings:
        table.add_row("[yellow]WARN[/yellow]", warn.code, warn.message)

    console.print(table)
    console.print(f"\n[bold]Grounding Rate:[/] {report.metrics.get('grounding_percentage', 0)}% "
                  f"({report.metrics.get('cited_findings', 0)}/{report.metrics.get('total_findings', 0)} temuan dengan kutipan bukti)")

    if report.ok:
        console.print("\n[bold green]✓ Validasi Berhasil! AuditPack memenuhi standar integritas.[/]")
        sys.exit(0)
    else:
        console.print(f"\n[bold red]✗ Validasi Gagal! Terdapat {len(report.errors)} pelanggaran integritas.[/]")
        sys.exit(1)


@cli.command("export")
@click.argument("pack_yaml", type=click.Path(exists=True))
@click.option("--format", "-f", "fmt", type=click.Choice(["report", "web", "csv", "skill", "all"]), required=True, help="Export target format.")
@click.option("--output", "-o", default="output", help="Output directory.")
def export_pack(pack_yaml: str, fmt: str, output: str) -> None:
    """Export existing AuditPack to report, web dashboard, CSV, or AI Agent Skill."""
    pack = AuditPack.from_yaml(pack_yaml)
    _export_deliverables(pack, output, fmt)


@cli.command("share")
@click.argument("pack_yaml", type=click.Path(exists=True))
@click.option("--output", "-o", default="output", help="Output directory.")
def share_pack(pack_yaml: str, output: str) -> None:
    """Generate self-contained offline HTML audit dashboard and a ready-to-send ZIP archive."""
    pack = AuditPack.from_yaml(pack_yaml)
    out_dir = Path(output)
    out_dir.mkdir(parents=True, exist_ok=True)

    slug = pack.audit_ref.lower().replace("-", "_")
    bundle_dir = out_dir / f"{slug}_share"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    web_exp = WebExporter()
    web_exp.export(pack, bundle_dir / "index.html")

    report_exp = ReportExporter()
    report_exp.export_report(pack, bundle_dir / "Laporan_Hasil_Audit.md")
    report_exp.export_working_papers(pack, bundle_dir / "Kertas_Kerja_Audit.md")

    zip_file = out_dir / f"{slug}_bundle.zip"
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as z:
        for file in bundle_dir.rglob("*"):
            z.write(file, arcname=file.relative_to(bundle_dir))

    console.print(f"[bold green]✓ Paket Berbagi Berhasil Dibuat![/]")
    console.print(f"  • Dasbor Web Offline: [cyan]{bundle_dir / 'index.html'}[/]")
    console.print(f"  • Berkas ZIP Siap Kirim: [green]{zip_file}[/]")


@cli.command("install-skill")
@click.option("--target", "-t", type=click.Choice(["antigravity", "claude", "cursor", "local"]), default="antigravity", help="Target agent platform.")
def install_skill(target: str) -> None:
    """Install document-auditor plugin/skill directly into Antigravity, Claude, or Cursor."""
    base_proj = Path(__file__).resolve().parent.parent
    bundled_skill = base_proj / "skills" / "document-auditor"

    if not bundled_skill.exists():
        console.print("[bold red]Error:[/] Bundled skill directory not found at " + str(bundled_skill))
        sys.exit(1)

    exporter = SkillExporter()
    dest = exporter.install_to_agent(bundled_skill, target_platform=target)

    console.print(f"[bold green]✓ Berhasil Menginstal Skill ke {target.upper()}![/]")
    console.print(f"  Lokasi: [cyan]{dest}[/]")
    console.print("  Sekarang agen AI Anda dapat langsung menggunakan keahlian audit dokumen secara otomatis.")


@cli.command("info")
@click.argument("pack_yaml", type=click.Path(exists=True))
def pack_info(pack_yaml: str) -> None:
    """Display quick summary and finding matrix of an AuditPack."""
    pack = AuditPack.from_yaml(pack_yaml)
    _render_summary_panel(pack)

    if pack.findings:
        table = Table(title="Daftar Temuan Audit (5C Finding Matrix)", border_style="cyan")
        table.add_column("ID", style="bold")
        table.add_column("Risiko")
        table.add_column("Judul Temuan")
        table.add_column("Kategori")
        table.add_column("Bukti")

        for f in pack.findings:
            r_color = {"critical": "red", "high": "orange3", "medium": "yellow", "low": "green"}.get(f.risk_level.value, "white")
            table.add_row(
                f.id,
                f"[{r_color}]{f.risk_level.value.upper()}[/{r_color}]",
                f.title,
                f.category,
                f"{len(f.evidence)} Kutipan",
            )
        console.print(table)


# ======================================================================
# Internal Helpers
# ======================================================================


def _render_summary_panel(pack: AuditPack) -> None:
    crit = pack.metrics.findings_by_risk.get("critical", 0)
    high = pack.metrics.findings_by_risk.get("high", 0)
    med = pack.metrics.findings_by_risk.get("medium", 0)
    low = pack.metrics.findings_by_risk.get("low", 0)

    summary_text = (
        f"[bold white]{pack.title}[/]  (Ref: `{pack.audit_ref}`)\n\n"
        f"• Total Dokumen Diuji  : [cyan]{len(pack.documents)} Berkas[/]\n"
        f"• Skor Kepatuhan       : [bold {'green' if pack.metrics.compliance_score >= 80 else 'red'}]{pack.metrics.compliance_score:.1f}%[/]\n"
        f"• Akurasi Aritmatika   : [bold {'green' if pack.metrics.arithmetic_accuracy >= 90 else 'yellow'}]{pack.metrics.arithmetic_accuracy:.1f}%[/]\n"
        f"• Bukti Terverifikasi  : [bold green]{pack.metrics.evidence_grounding_rate:.1f}%[/]\n"
        f"• Total Temuan         : [bold]{len(pack.findings)}[/] "
        f"([red]{crit} Kritis[/], [orange3]{high} Tinggi[/], [yellow]{med} Sedang[/], [green]{low} Rendah[/])"
    )
    console.print(Panel(summary_text, title="📊 Ringkasan Hasil Pemeriksaan Audit", border_style="blue"))


def _export_deliverables(pack: AuditPack, output_dir: str, fmt: str) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    slug = pack.audit_ref.lower().replace("-", "_")

    if fmt in ["pack", "all"]:
        yaml_path = out / f"{slug}_pack.yaml"
        pack.to_yaml(yaml_path)
        console.print(f"  • AuditPack YAML  : [cyan]{yaml_path}[/]")

    if fmt in ["report", "all"]:
        rep_exp = ReportExporter()
        report_path = out / f"{slug}_Laporan_Hasil_Audit.md"
        kka_path = out / f"{slug}_Kertas_Kerja_Audit.md"
        rep_exp.export_report(pack, report_path)
        rep_exp.export_working_papers(pack, kka_path)
        console.print(f"  • Laporan LHA (MD): [cyan]{report_path}[/]")
        console.print(f"  • Kertas Kerja KKA: [cyan]{kka_path}[/]")

    if fmt in ["web", "all"]:
        web_exp = WebExporter()
        web_path = out / f"{slug}_dashboard.html"
        web_exp.export(pack, web_path)
        console.print(f"  • Dasbor Web HTML : [green]{web_path}[/]")

    if fmt in ["csv", "all"]:
        csv_exp = CSVExporter()
        csv_fnd = out / f"{slug}_findings.csv"
        csv_kka = out / f"{slug}_working_papers.csv"
        csv_exp.export_findings(pack, csv_fnd)
        csv_exp.export_working_papers(pack, csv_kka)
        console.print(f"  • CSV Temuan      : [cyan]{csv_fnd}[/]")

    if fmt in ["skill", "all"]:
        skill_exp = SkillExporter()
        skill_path = skill_exp.export(pack, out)
        console.print(f"  • Agent Skill Dir : [magenta]{skill_path}[/]")


if __name__ == "__main__":
    cli()
