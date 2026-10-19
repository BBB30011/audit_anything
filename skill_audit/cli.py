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
from skill_audit.evidence_bundle import (
    create_evidence_bundle,
    export_evidence_bundle_zip,
    verify_evidence_bundle,
)
from skill_audit.exporters import (
    CSVExporter,
    ReportExporter,
    SkillExporter,
    WebExporter,
)
from skill_audit.analyzers.benford_analyzer import BenfordForensicAnalyzer
from skill_audit.analyzers.terrain_detector import DomainTerrainDetector
from skill_audit.knowledge.domain_profiles import DOMAIN_TERRAIN_PROFILES, list_all_terrains
from skill_audit.knowledge.saaipi_standards import evaluate_saaipi_compliance
from skill_audit.models import (
    APIPConclusion,
    AuditDomain,
    AuditPack,
    HumanSignOff,
    RiskLevel,
    UnknownStatus,
)
from skill_audit.parsers import parse_path
from skill_audit.triage import run_interactive_triage
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


@cli.command("risk")
@click.argument("target", type=click.Path(exists=True))
def show_risk_heatmap(target: str) -> None:
    """Evaluate Enterprise Risk Management (ERM) 5x5 Heatmap matrix."""
    p = Path(target)
    if p.suffix.lower() in [".yaml", ".yml"]:
        pack = AuditPack.from_yaml(p)
    else:
        engine = AuditEngine()
        pack = engine.audit(p)

    console.print(f"\n[bold red]🔥 Matriks Risiko 5x5 Enterprise Risk Management (ISO 31000 / COSO ERM)[/]")
    console.print(f"Penugasan: [bold]{pack.title}[/] (`{pack.audit_ref}`)\n")

    grid = pack.risk_heatmap.get("grid", {})
    table = Table(title="5x5 Heatmap (Likelihood Y vs Impact X)", border_style="red")
    table.add_column("Likelihood (Y)", style="bold")
    table.add_column("1 - Insig", justify="center")
    table.add_column("2 - Minor", justify="center")
    table.add_column("3 - Mod", justify="center")
    table.add_column("4 - Mayor", justify="center")
    table.add_column("5 - Katas", justify="center")

    l_labels = {5: "5 - Hampir Pasti", 4: "4 - Sering", 3: "3 - Mungkin", 2: "2 - Jarang", 1: "1 - Sangat Jarang"}
    for l in range(5, 0, -1):
        row_cells = [l_labels[l]]
        for i in range(1, 6):
            f_ids = grid.get(f"{l}_{i}", [])
            score = l * i
            if score >= 16:
                color = "red"
            elif score >= 10:
                color = "dark_orange"
            elif score >= 5:
                color = "yellow"
            else:
                color = "green"

            cell_text = f"[{color}]{', '.join(f_ids) if f_ids else '-'}[/{color}]"
            row_cells.append(cell_text)
        table.add_row(*row_cells)

    console.print(table)
    counts = pack.risk_heatmap.get("zone_counts", {})
    console.print(
        f"Zona Risiko: [red]{counts.get('critical_red', 0)} Kritis[/] | "
        f"[dark_orange]{counts.get('high_amber', 0)} Tinggi[/] | "
        f"[yellow]{counts.get('medium_yellow', 0)} Sedang[/] | "
        f"[green]{counts.get('low_green', 0)} Rendah[/]\n"
    )


@cli.command("sod")
@click.argument("target", type=click.Path(exists=True))
def check_sod(target: str) -> None:
    """Analyze Segregation of Duties (SoD) conflicts across signatories and users."""
    p = Path(target)
    if p.suffix.lower() in [".yaml", ".yml"]:
        pack = AuditPack.from_yaml(p)
    else:
        engine = AuditEngine()
        pack = engine.audit(p)

    console.print(f"\n[bold magenta]🛡️ Pengujian Pemisahan Tugas (Segregation of Duties - SoD)[/]")
    console.print(f"Penugasan: [bold]{pack.title}[/]\n")

    if not pack.sod_conflicts:
        console.print("[bold green]✓ Tidak ditemukan benturan pemisahan tugas. Struktur peran memadai.[/]")
        return

    table = Table(title=f"Ditemukan {len(pack.sod_conflicts)} Benturan SoD", border_style="magenta")
    table.add_column("ID", style="bold")
    table.add_column("Nama Individu")
    table.add_column("Peran Saling Bertentangan")
    table.add_column("Risiko Fraud")

    for s in pack.sod_conflicts:
        table.add_row(
            s.conflict_id,
            f"[bold]{s.individual_name}[/]",
            f"[red]{s.role_a}[/red] vs [red]{s.role_b}[/red]",
            s.risk_explanation,
        )
    console.print(table)


@cli.command("governance")
@click.argument("target", type=click.Path(exists=True))
def check_governance(target: str) -> None:
    """Evaluate Delegation of Authority (DoA) limits and GCG compliance."""
    p = Path(target)
    if p.suffix.lower() in [".yaml", ".yml"]:
        pack = AuditPack.from_yaml(p)
    else:
        engine = AuditEngine()
        pack = engine.audit(p)

    console.print(f"\n[bold blue]🏛️ Evaluasi Tata Kelola Korporasi (GCG) & Batas Wewenang (DoA)[/]")
    console.print(f"Skor Tata Kelola: [bold {'green' if pack.governance_score >= 80 else 'red'}]{pack.governance_score:.1f}%[/]\n")

    if not pack.doa_violations:
        console.print("[bold green]✓ Seluruh pengesahan transaksi berada dalam batas wewenang yang sah.[/]")
        return

    table = Table(title=f"Ditemukan {len(pack.doa_violations)} Pelampauan DoA", border_style="blue")
    table.add_column("ID", style="bold")
    table.add_column("Pejabat")
    table.add_column("Nilai Transaksi", justify="right")
    table.add_column("Batas Wewenang", justify="right")
    table.add_column("Pelampauan", justify="right", style="bold red")
    table.add_column("Dokumen")

    for d in pack.doa_violations:
        table.add_row(
            d.violation_id,
            f"{d.approver_name} ({d.approver_title})",
            f"Rp {d.transaction_amount:,.0f}",
            f"Rp {d.authorized_limit:,.0f}",
            f"+Rp {d.excess_amount:,.0f}",
            d.document_ref,
        )
    console.print(table)


@cli.group("framework")
def framework_group() -> None:
    """Manage and inspect built-in enterprise audit frameworks and programs."""
    pass


@framework_group.command("list")
def list_frameworks() -> None:
    """List all available business process, governance, COSO, and ITGC frameworks."""
    from skill_audit.knowledge.business_processes import ALL_PROGRAMS
    from skill_audit.knowledge.governance import GCG_PRINCIPLES
    from skill_audit.knowledge.internal_controls import COSO_17_PRINCIPLES
    from skill_audit.knowledge.technical_audit import ITGC_DOMAINS

    table = Table(title="Daftar Kerangka Kerja & Program Audit Terintegrasi", border_style="cyan")
    table.add_column("Kategori", style="bold")
    table.add_column("Kode")
    table.add_column("Nama Program / Framework")
    table.add_column("Cakupan Prosedur")

    # Business Processes
    for prog in ALL_PROGRAMS:
        table.add_row("Proses Bisnis", prog.cycle_code, prog.name, f"{len(prog.procedures)} Titik Kontrol")

    # COSO
    table.add_row("Pengendalian Internal", "COSO-2013", "COSO Internal Control Integrated Framework", f"{len(COSO_17_PRINCIPLES)} Prinsip")

    # Governance
    table.add_row("Tata Kelola (GRC)", "GCG-TARIF", "Prinsip Dasar Good Corporate Governance", f"{len(GCG_PRINCIPLES)} Pilar TARIF")

    # ITGC
    table.add_row("Teknis & IT", "ITGC-ISO27K", "IT General Controls & Cyber Security", f"{len(ITGC_DOMAINS)} Domain ITGC")

    # ERM
    table.add_row("Manajemen Risiko", "ISO-31000", "Enterprise Risk Management 5x5 Matrix", "5x5 Likelihood x Impact")

    console.print(table)


@cli.command("unknowns")
@click.argument("target", type=click.Path(exists=True))
def list_unknowns(target: str) -> None:
    """Inspect the REA Unknowns & Inquiries Ledger (evidentiary gaps)."""
    p = Path(target)
    if p.suffix.lower() in [".yaml", ".yml"]:
        pack = AuditPack.from_yaml(p)
    else:
        engine = AuditEngine()
        pack = engine.audit(p)

    console.print(f"\n[bold yellow]❓ Buku Besar Pertanyaan Terbuka & Ambiguitas Bukti (Ledger of Unknowns)[/]")
    console.print(f"Penugasan: [bold]{pack.title}[/] (`{pack.audit_ref}`)\n")

    if not pack.unknowns:
        console.print("[bold green]✓ Tidak ada pertanyaan menggantung. Seluruh bukti lengkap.[/]")
        return

    table = Table(title=f"Ditemukan {len(pack.unknowns)} Inquiry / Pertanyaan Terbuka", border_style="yellow")
    table.add_column("ID", style="bold")
    table.add_column("Pertanyaan & Ambiguitas Bukti")
    table.add_column("Kategori")
    table.add_column("Status", justify="center")
    table.add_column("Bukti yang Dibutuhkan")

    for u in pack.unknowns:
        st_color = "green" if u.status == UnknownStatus.RESOLVED else ("yellow" if u.status == UnknownStatus.OPEN else "dim")
        table.add_row(
            u.id,
            f"[bold]{u.question}[/]",
            u.category,
            f"[{st_color}]{u.status.value.upper()}[/{st_color}]",
            u.evidence_required,
        )
    console.print(table)


@cli.command("resolve-unknown")
@click.argument("pack_path", type=click.Path(exists=True))
@click.option("--id", "unknown_id", required=True, help="ID of the unknown item to resolve (e.g. UNK-01).")
@click.option("--notes", required=True, help="Resolution rationale or explanation from management.")
@click.option("--evidence", default="", help="Reference document or citation supporting resolution.")
@click.option("--auditor", default="Lead Auditor", help="Name of the resolving auditor.")
def resolve_unknown_cmd(pack_path: str, unknown_id: str, notes: str, evidence: str, auditor: str) -> None:
    """Resolve an open audit unknown in the pack with evidence and rationale."""
    p = Path(pack_path)
    pack = AuditPack.from_yaml(p)

    target_u = next((u for u in pack.unknowns if u.id.upper() == unknown_id.upper()), None)
    if not target_u:
        console.print(f"[bold red]Error: Unknown with ID {unknown_id} not found in {pack_path}[/]")
        sys.exit(1)

    target_u.status = UnknownStatus.RESOLVED
    target_u.resolution_notes = notes
    target_u.evidence_ref = evidence
    target_u.resolved_by = auditor
    pack.to_yaml(p)
    console.print(f"[bold green]✓ Berhasil menyelesaikan {unknown_id}![/]")
    console.print(f"  • Keterangan : {notes}")
    console.print(f"  • Bukti      : {evidence or 'Klarifikasi Manajemen'}")
    console.print(f"  • Disimpan ke: {p}")


@cli.command("obligations")
@click.argument("target", type=click.Path(exists=True))
def list_obligations(target: str) -> None:
    """Evaluate audit obligations and standards compliance coverage."""
    p = Path(target)
    if p.suffix.lower() in [".yaml", ".yml"]:
        pack = AuditPack.from_yaml(p)
    else:
        engine = AuditEngine()
        pack = engine.audit(p)

    console.print(f"\n[bold cyan]🛡️ Evaluasi Pemenuhan Kewajiban Audit (Audit Obligations & Coverage)[/]")
    console.print(f"Penugasan: [bold]{pack.title}[/] (`{pack.audit_ref}`)\n")

    table = Table(title="Ketercakupan Kewajiban Audit & Kerangka Regulasi", border_style="cyan")
    table.add_column("ID", style="bold")
    table.add_column("Prosedur Standar Audit")
    table.add_column("Dasar Regulasi")
    table.add_column("Status", justify="center")
    table.add_column("Catatan Pengujian")

    satisfied_count = sum(1 for o in pack.obligations if o.status == "satisfied")
    for o in pack.obligations:
        st_color = "green" if o.status == "satisfied" else ("red" if o.status == "violated" else "yellow")
        table.add_row(
            o.id,
            f"[bold]{o.title}[/]",
            o.standard_ref,
            f"[{st_color}]{o.status.upper()}[/{st_color}]",
            o.coverage_notes,
        )
    console.print(table)
    cov_pct = (satisfied_count / len(pack.obligations) * 100.0) if pack.obligations else 100.0
    console.print(f"Tingkat Pemenuhan: [bold {'green' if cov_pct >= 80 else 'yellow'}]{cov_pct:.1f}%[/] ({satisfied_count}/{len(pack.obligations)} terpenuhi)\n")


@cli.command("bundle")
@click.argument("pack_or_dossier", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output path for evidence bundle ZIP.")
def export_bundle_cmd(pack_or_dossier: str, output: str | None) -> None:
    """Export standalone, court-ready cryptographic Evidence Bundle ZIP archive."""
    p = Path(pack_or_dossier)
    if p.suffix.lower() in [".yaml", ".yml"]:
        pack = AuditPack.from_yaml(p)
    else:
        engine = AuditEngine()
        pack = engine.audit(p)

    out_zip = output or f"{pack.audit_ref.lower().replace('-', '_')}_evidence_bundle.zip"
    zip_path = export_evidence_bundle_zip(pack, out_zip)
    console.print(f"[bold green]✓ Berhasil mengekspor Cryptographic Evidence Bundle![/]")
    console.print(f"  • Berkas ZIP   : [cyan]{zip_path}[/]")
    console.print(f"  • Bundle ID    : [magenta]{pack.evidence_bundle.get('bundle_id', 'EVD-AUTO')}[/]")
    console.print(f"  • Total Dokumen: {len(pack.documents)} Berkas dengan SHA-256 Digest")


@cli.command("verify-bundle")
@click.argument("pack_file", type=click.Path(exists=True))
def verify_bundle_cmd(pack_file: str) -> None:
    """Forensically verify documents in an audit pack against bundle SHA-256 manifest."""
    p = Path(pack_file)
    pack = AuditPack.from_yaml(p)

    console.print(f"\n[bold cyan]🔐 Verifikasi Forensik Integritas Bukti (SHA-256 Tamper Verification)[/]")
    res = verify_evidence_bundle(pack.evidence_bundle, pack.documents)

    table = Table(title="Hasil Pengujian Integritas Kriptografis Dokumen", border_style="cyan")
    table.add_column("Nama Dokumen")
    table.add_column("Status Forensik", justify="center")
    table.add_column("Catatan / Hash SHA-256")

    for item in res.get("details", []):
        st = item.get("status")
        st_color = "green" if st == "VERIFIED_INTACT" else "red"
        notes = item.get("sha256", item.get("notes", ""))
        table.add_row(item.get("document", ""), f"[{st_color}]{st}[/{st_color}]", notes)

    console.print(table)
    if res["verified_intact"]:
        console.print("[bold green]✓ Seluruh berkas bukti diverifikasi utuh dan tidak mengalami manipulasi (Tamper-Free).[/]\n")
    else:
        console.print(f"[bold red]✗ PERINGATAN: Ditemukan {res['tampered_count']} berkas yang tidak cocok dengan digest awal![/]\n")
        sys.exit(1)


@cli.command("triage")
@click.argument("pack_file", type=click.Path(exists=True))
def triage_cmd(pack_file: str) -> None:
    """Start interactive Human-AI collaborative triage and review session."""
    run_interactive_triage(pack_file)


@cli.command("signoff")
@click.argument("pack_file", type=click.Path(exists=True))
@click.option("--name", default="", help="Full name of Lead Auditor / Ketua Tim.")
@click.option("--role", default="", help="Professional role or title.")
@click.option("--nip", default="", help="Registration / NIP / CPA license number.")
@click.option(
    "--conclusion",
    type=click.Choice([
        "sangat_efektif",
        "efektif_dengan_catatan",
        "kurang_efektif",
        "tidak_efektif",
        "telah_direviu",
        "konsultansi_advis",
    ], case_sensitive=False),
    default=None,
    help="Simpulan Pengawasan APIP sesuai Standar AAIPI 2400 / PP 60/2008 SPIP.",
)
@click.option("--opinion", default=None, help="Official audit conclusion opinion.")
@click.option("--at", "anggota_tim", default="", help="Nama/NIP Anggota Tim.")
@click.option("--kt", "ketua_tim", default="", help="Nama/NIP Ketua Tim Pengawasan Intern.")
@click.option("--dalnis", "pengendali_teknis", default="", help="Nama/NIP Pengendali Teknis (Dalnis).")
@click.option("--pm", "pengendali_mutu", default="", help="Nama/NIP Pengendali Mutu / Irban.")
@click.option("--inspektur", default="", help="Nama/NIP Inspektur / Penanggung Jawab APIP.")
@click.option("--notes", default="", help="Auditor final comments or professional judgement.")
def signoff_cmd(
    pack_file: str,
    name: str,
    role: str,
    nip: str,
    conclusion: str | None,
    opinion: str | None,
    anggota_tim: str,
    ketua_tim: str,
    pengendali_teknis: str,
    pengendali_mutu: str,
    inspektur: str,
    notes: str,
) -> None:
    """Formally sign-off on an audit pack with professional auditor opinion or SAAIPI APIP conclusion."""
    from datetime import datetime, timezone

    p = Path(pack_file)
    pack = AuditPack.from_yaml(p)

    is_apip = (
        conclusion is not None
        or bool(ketua_tim or pengendali_teknis or pengendali_mutu or inspektur)
        or pack.domain == AuditDomain.GOVERNMENT
        or pack.human_sign_off.signoff_type == "aaipi"
        or bool(pack.human_sign_off.apip_conclusion)
        or any("saaipi" in str(r).lower() or "apip" in str(r).lower() for r in pack.terrain_profile.detected_regulations)
        or any("saaipi" in d.content.lower() or "apip" in d.content.lower() for d in pack.documents)
    )

    conclusion_map = {
        "sangat_efektif": APIPConclusion.SANGAT_EFEKTIF.value,
        "efektif_dengan_catatan": APIPConclusion.EFEKTIF_DENGAN_CATATAN.value,
        "kurang_efektif": APIPConclusion.KURANG_EFEKTIF.value,
        "tidak_efektif": APIPConclusion.TIDAK_EFEKTIF.value,
        "telah_direviu": APIPConclusion.TELAH_DIREVIU.value,
        "konsultansi_advis": APIPConclusion.KONSULTANSI_ADVIS.value,
    }

    if conclusion:
        final_conclusion = conclusion_map.get(conclusion.lower(), conclusion)
    elif opinion:
        final_conclusion = opinion
    elif is_apip:
        final_conclusion = APIPConclusion.EFEKTIF_DENGAN_CATATAN.value
    else:
        final_conclusion = "Adequate with Improvements (Memadai dengan Catatan)"

    signer_name = name or (ketua_tim or "Drs. Bambang Wijaya, Ak., CA, CRMO")
    signer_role = role or ("Ketua Tim Pengawasan Intern APIP" if is_apip else "Lead Internal Auditor")

    pack.human_sign_off = HumanSignOff(
        reviewer_name=signer_name,
        reviewer_role=signer_role,
        reviewer_license_or_nip=nip,
        audit_opinion=final_conclusion,
        signed_at=datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC"),
        comments=notes or (
            "Tata kelola dan sistem pengendalian intern (SPIP) dinilai memadai dengan beberapa catatan rekomendasi perbaikan kepatuhan prosedur."
            if is_apip else "Pengendalian internal dinilai memadai dengan beberapa catatan koreksi administratif."
        ),
        is_signed=True,
        signoff_type="aaipi" if is_apip else "general",
        apip_conclusion=final_conclusion if is_apip else "",
        anggota_tim=anggota_tim or pack.human_sign_off.anggota_tim,
        ketua_tim=ketua_tim or signer_name,
        pengendali_teknis=pengendali_teknis or pack.human_sign_off.pengendali_teknis,
        pengendali_mutu=pengendali_mutu or pack.human_sign_off.pengendali_mutu,
        inspektur=inspektur or pack.human_sign_off.inspektur,
    )
    pack.to_yaml(p)

    # Re-export HTML and LHA reports to reflect sign-off immediately
    rep_exp = ReportExporter()
    web_exp = WebExporter()
    parent = p.parent
    base_name = p.stem.replace("_pack", "")
    rep_exp.export_report(pack, parent / f"{base_name}_Laporan_Hasil_Audit.md")
    web_exp.export(pack, parent / f"{base_name}_dashboard.html")

    console.print(f"[bold green]✓ Berhasil mengesahkan AuditPack secara resmi![/]")
    console.print(f"  • Penanggung Jawab : [bold white]{signer_name}[/] ({signer_role})")
    console.print(f"  • Simpulan/Opini   : [bold cyan]{final_conclusion}[/]")
    if is_apip:
        console.print(f"  • Standar          : [yellow]PER-01/AAIPI/DPN/2021 (SAAIPI) & PP 60/2008 SPIP[/]")
        if ketua_tim or pengendali_teknis or pengendali_mutu or inspektur:
            console.print(f"  • Tim APIP         : KT: {ketua_tim or '-'} | Dalnis: {pengendali_teknis or '-'} | PM: {pengendali_mutu or '-'} | Inspektur: {inspektur or '-'}")
    console.print(f"  • Disimpan ke      : [green]{p}[/]")


@cli.command("audit")
@click.argument("target_path", type=click.Path(exists=True))
@click.option("--output", "-o", default="output", help="Output directory for generated audit pack.")
@click.option("--format", "-f", "fmt", type=click.Choice(["pack", "report", "web", "csv", "all"]), default="all", help="Output format.")
@click.option("--domain", "-d", default="auto", help="Audit domain/terrain (auto, procurement, financial, healthcare, government, hr_payroll, supply_chain, forensic_fraud, tax_customs, banking_fintech, esg_sustainability, it_security).")
@click.option("--checklist", "-c", default=None, help="Path to custom checklist YAML file.")
@click.option("--title", "-t", default=None, help="Custom audit title.")
def audit_universal(target_path: str, output: str, fmt: str, domain: str, checklist: str | None, title: str | None) -> None:
    """Universal audit command for any document, dossier, or multi-domain evidence folder."""
    p = Path(target_path)
    console.print(f"[bold cyan]🔍 Menjalankan Audit Anything (Segala Medan):[/] [white]{p.name}[/]")

    try:
        domain_enum = AuditDomain(domain.lower())
    except ValueError:
        domain_enum = AuditDomain.AUTO

    engine = AuditEngine(checklist_config=checklist)
    pack = engine.audit(p, title=title, domain=domain_enum)
    _render_summary_panel(pack)
    _export_deliverables(pack, output, fmt)


@cli.command("benford")
@click.argument("target", type=click.Path(exists=True))
def benford_cmd(target: str) -> None:
    """Run forensic Benford's Law distribution analysis across all numeric figures."""
    p = Path(target)
    if p.suffix.lower() in [".yaml", ".yml", ".json"]:
        pack = AuditPack.from_yaml(p)
        benford_res = pack.benford_analysis
        total_nums = benford_res.total_numbers
        analyzed = benford_res.analyzed_digits
        mad = benford_res.mad_score
        chi_sq = benford_res.chi_square
        status = benford_res.conformity_status
        anomalies = benford_res.critical_anomalies
        dist = benford_res.digit_distribution
    else:
        documents = parse_path(p)
        analyzer = BenfordForensicAnalyzer()
        benford_res, _ = analyzer.analyze(documents)
        total_nums = benford_res.total_numbers
        analyzed = benford_res.analyzed_digits
        mad = benford_res.mad_score
        chi_sq = benford_res.chi_square
        status = benford_res.conformity_status
        anomalies = benford_res.critical_anomalies
        dist = benford_res.digit_distribution

    console.print(f"\n[bold magenta]📈 Analisis Forensik Digital: Uji Distribusi Benford's Law[/]")
    console.print(f"Target: [bold white]{p.name}[/] | Total Angka: {total_nums} | Sampel Digit: {analyzed}")
    console.print(f"Status Kesesuaian: [bold {'green' if 'acceptable' in status or 'close' in status else 'red'}]{status.upper()}[/] | Skor MAD: {mad:.4f} | Chi-Square: {chi_sq:.2f}\n")

    table = Table(title="Sebaran Digit Pertama vs. Distribusi Standar Benford (Nigrini 2012)", border_style="magenta")
    table.add_column("Digit", justify="center", style="bold")
    table.add_column("Jumlah Aktual", justify="right")
    table.add_column("Aktual (%)", justify="right")
    table.add_column("Benford Ekspektasi (%)", justify="right")
    table.add_column("Selisih (%)", justify="right")
    table.add_column("Z-Score", justify="right")
    table.add_column("Status Forensik", justify="center")

    for d in dist:
        is_anom = d.digit in anomalies
        stat_label = "[bold red]ANOMALI[/]" if is_anom else "[green]Wajar[/]"
        table.add_row(
            str(d.digit),
            str(d.actual_count),
            f"{d.actual_pct:.1f}%",
            f"{d.expected_pct:.1f}%",
            f"{'+' if d.diff_pct > 0 else ''}{d.diff_pct:.1f}%",
            f"{d.z_score:.2f}",
            stat_label,
        )

    console.print(table)
    if anomalies:
        console.print(f"[bold red]⚠️ PERINGATAN FORENSIK:[/] Lonjakan deviasi signifikan terdeteksi pada digit: {anomalies}. Disarankan pengujian substantif 100%.")
    else:
        console.print("[bold green]✓ Distribusi angka transaksi berada dalam batas wajar alami.[/]")


@cli.command("terrain")
@click.argument("target_path", type=click.Path(exists=True))
def terrain_cmd(target_path: str) -> None:
    """Classify and inspect the operational audit terrain of a document dossier."""
    p = Path(target_path)
    documents = parse_path(p)
    detector = DomainTerrainDetector()
    profile = detector.detect(documents)

    console.print(f"\n[bold cyan]🌐 Klasifikasi Medan Audit (Terrain Detection)[/]")
    console.print(f"Target Dossier    : [bold white]{p.name}[/] ({len(documents)} berkas)")
    console.print(f"Medan Utama       : [bold green]{profile.primary_domain.upper()}[/] (Confidence: {profile.confidence*100:.0f}%)")
    console.print(f"Medan Terdeteksi  : [cyan]{', '.join(d.upper() for d in profile.detected_domains)}[/]")

    if profile.detected_regulations:
        console.print(f"Regulasi Terkait  : [yellow]{', '.join(profile.detected_regulations)}[/]")
    if profile.key_entities:
        console.print(f"Entitas Terdeteksi: [white]{', '.join(profile.key_entities)}[/]")

    console.print("\n[bold]Rekomendasi Prosedur Uji Spesifik Medan:[/]")
    for idx, check in enumerate(profile.recommended_checks, 1):
        console.print(f"  {idx}. {check}")


@cli.command("profiles")
def profiles_cmd() -> None:
    """List all supported audit domain terrains and their regulatory frameworks."""
    terrains = list_all_terrains()
    table = Table(title="Daftar Medan Audit Universal (Auditor Anything)", border_style="cyan")
    table.add_column("Domain / Terrain", style="bold green")
    table.add_column("Judul Program")
    table.add_column("Regulasi / Standar Acuan")
    table.add_column("Fokus Red Flags Utama")

    for t in terrains:
        table.add_row(
            t.domain.value.upper(),
            t.title,
            "; ".join(t.statutory_references[:2]),
            "; ".join(t.key_red_flags[:2]),
        )
    console.print(table)


@cli.command("saaipi")
@click.argument("target", type=click.Path(exists=True))
@click.option("--json", "json_mode", is_flag=True, help="Output SAAIPI evaluation in JSON format.")
def saaipi_cmd(target: str, json_mode: bool) -> None:
    """Evaluate compliance with PER-01/AAIPI/DPN/2021 Standar Audit Intern Pemerintah Indonesia (SAAIPI)."""
    p = Path(target)
    if p.suffix in [".yaml", ".yml"]:
        pack = AuditPack.from_yaml(p)
    elif p.suffix == ".json":
        pack = AuditPack.from_json(p)
    else:
        # Audit target with GOVERNMENT domain
        engine = AuditEngine()
        pack = engine.audit(p, domain=AuditDomain.GOVERNMENT)

    report = evaluate_saaipi_compliance(pack)

    if json_mode:
        click.echo(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
        return

    verdict_color = "green" if "MEMENUHI" in report.summary_verdict and "BELUM" not in report.summary_verdict else "yellow" if "SUBSTANSIAL" in report.summary_verdict else "red"
    summary_text = (
        f"[bold white]{report.standard_title}[/]\n"
        f"Dasar Regulasi : [bold cyan]{report.legal_basis}[/]\n"
        f"Auditi / Berkas: [white]{pack.title}[/] (`{pack.audit_ref}`)\n\n"
        f"• Skor Kepatuhan SAAIPI  : [bold {verdict_color}]{report.overall_compliance_score:.1f}%[/]\n"
        f"• Standar Atribut (1000) : [cyan]{report.attribute_standards_score:.1f}%[/]\n"
        f"• Standar Pelaksanaan(2000): [cyan]{report.performance_standards_score:.1f}%[/]\n"
        f"• Kepatuhan Kode Etik APIP: [green]{report.ethics_score:.1f}%[/]\n"
        f"• Keterpenuhan Unsur 5C   : [bold {'green' if report.five_c_rigor_score >= 90 else 'yellow'}]{report.five_c_rigor_score:.1f}%[/]\n"
        f"• Simpulan Dewan Penjamin: [{verdict_color}]{report.summary_verdict}[/]"
    )
    console.print(Panel(summary_text, title="🏛️ Evaluasi Kepatuhan SAAIPI (PER-01/AAIPI/DPN/2021)", border_style="cyan"))

    # 1. Ethics Table
    ethics_table = Table(title="1. Kode Etik Auditor Intern Pemerintah Indonesia (APIP)", border_style="blue")
    ethics_table.add_column("Prinsip Etika", style="bold")
    ethics_table.add_column("Status", justify="center")
    ethics_table.add_column("Skor", justify="right")
    ethics_table.add_column("Catatan Penilaian")

    for name, data in report.ethics_evaluations.items():
        st = data["status"]
        st_color = "green" if st == "Terpenuhi" else "yellow" if "Perlu" in st else "red"
        ethics_table.add_row(
            name,
            f"[{st_color}]{st}[/]",
            f"{data['score']:.0f}%",
            data["notes"],
        )
    console.print(ethics_table)

    # 2. Standards Table (1000 - 2500)
    std_table = Table(title="2. Evaluasi Standar Atribut & Standar Pelaksanaan SAAIPI", border_style="cyan")
    std_table.add_column("Kode", style="bold magenta", width=14)
    std_table.add_column("Seri", width=24)
    std_table.add_column("Judul Standar", style="bold")
    std_table.add_column("Status", justify="center", width=14)
    std_table.add_column("Skor", justify="right", width=8)
    std_table.add_column("Catatan Hasil Reviu")

    for ev in report.evaluations:
        status_label = (
            "[bold green]SESUAI[/]" if ev.status == "compliant"
            else "[bold yellow]SEBAGIAN[/]" if ev.status == "partial"
            else "[bold red]TIDAK SESUAI[/]"
        )
        std_table.add_row(
            ev.clause.code,
            ev.clause.series,
            ev.clause.title,
            status_label,
            f"{ev.score:.0f}%",
            ev.notes,
        )
    console.print(std_table)


# Register alias 'aipi' within skillaudit CLI group
cli.add_command(saaipi_cmd, name="aipi")


@click.command("aipi")
@click.argument("target", type=click.Path(exists=True))
@click.option("--json", "json_mode", is_flag=True, help="Output SAAIPI evaluation in JSON format.")
def aipi_standalone(target: str, json_mode: bool) -> None:
    """Standalone CLI shortcut for PER-01/AAIPI/DPN/2021 SAAIPI evaluation."""
    saaipi_cmd.callback(target=target, json_mode=json_mode)


# ======================================================================
# Internal Helpers
# ======================================================================



def _render_summary_panel(pack: AuditPack) -> None:
    crit = pack.metrics.findings_by_risk.get("critical", 0)
    high = pack.metrics.findings_by_risk.get("high", 0)
    med = pack.metrics.findings_by_risk.get("medium", 0)
    low = pack.metrics.findings_by_risk.get("low", 0)

    domain_str = pack.domain.value.upper()
    benford_status = pack.benford_analysis.conformity_status.replace("_", " ").title()

    summary_text = (
        f"[bold white]{pack.title}[/]  (Ref: `{pack.audit_ref}`)\n\n"
        f"• Medan / Domain Audit : [bold cyan]{domain_str}[/] (Confidence: {pack.terrain_profile.confidence*100:.0f}%)\n"
        f"• Forensik Benford     : [bold {'green' if 'Acceptable' in benford_status or 'Close' in benford_status else 'red'}]{benford_status}[/] (MAD: {pack.benford_analysis.mad_score:.4f})\n"
        f"• Total Dokumen Diuji  : [cyan]{len(pack.documents)} Berkas[/]\n"
        f"• Skor Kepatuhan       : [bold {'green' if pack.metrics.compliance_score >= 80 else 'red'}]{pack.metrics.compliance_score:.1f}%[/]\n"
        f"• Akurasi Aritmatika   : [bold {'green' if pack.metrics.arithmetic_accuracy >= 90 else 'yellow'}]{pack.metrics.arithmetic_accuracy:.1f}%[/]\n"
        f"• Bukti Terverifikasi  : [bold green]{pack.metrics.evidence_grounding_rate:.1f}%[/]\n"
        f"• Total Temuan         : [bold]{len(pack.findings)}[/] "
        f"([red]{crit} Kritis[/], [orange3]{high} Tinggi[/], [yellow]{med} Sedang[/], [green]{low} Rendah[/])"
    )
    console.print(Panel(summary_text, title="📊 Ringkasan Hasil Pemeriksaan Audit (Segala Medan)", border_style="blue"))


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

    if fmt in ["bundle", "all"]:
        bundle_zip = out / f"{slug}_evidence_bundle.zip"
        export_evidence_bundle_zip(pack, bundle_zip)
        console.print(f"  • Evidence Bundle : [yellow]{bundle_zip}[/]")



if __name__ == "__main__":
    cli()
