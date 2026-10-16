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
from skill_audit.models import AuditDomain, AuditPack, HumanSignOff, RiskLevel, UnknownStatus
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
@click.option("--name", required=True, help="Full name of Lead Auditor.")
@click.option("--role", default="Lead Internal Auditor", help="Professional role or title.")
@click.option("--nip", default="", help="Registration / NIP / CPA license number.")
@click.option(
    "--opinion",
    type=click.Choice([
        "WTP (Wajar Tanpa Pengecualian)",
        "WDP (Wajar Dengan Pengecualian)",
        "Tidak Wajar (Adverse)",
        "Menolak Memberikan Opini (Disclaimer)",
    ]),
    default="WDP (Wajar Dengan Pengecualian)",
    help="Official audit conclusion opinion.",
)
@click.option("--notes", default="", help="Auditor final comments or professional judgement.")
def signoff_cmd(pack_file: str, name: str, role: str, nip: str, opinion: str, notes: str) -> None:
    """Formally sign-off on an audit pack with professional auditor opinion."""
    from datetime import datetime, timezone

    p = Path(pack_file)
    pack = AuditPack.from_yaml(p)

    pack.human_sign_off = HumanSignOff(
        reviewer_name=name,
        reviewer_role=role,
        reviewer_license_or_nip=nip,
        audit_opinion=opinion,
        signed_at=datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC"),
        comments=notes or "Pengesahan formal diterbitkan setelah pengujian kepatuhan dan rekonsiliasi dokumen.",
        is_signed=True,
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
    console.print(f"  • Penanggung Jawab : [bold white]{name}[/] ({role})")
    console.print(f"  • NIP / Lisensi    : {nip or '-'}")
    console.print(f"  • Opini Audit      : [bold cyan]{opinion}[/]")
    console.print(f"  • Disimpan ke      : [green]{p}[/]")



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

    if fmt in ["bundle", "all"]:
        bundle_zip = out / f"{slug}_evidence_bundle.zip"
        export_evidence_bundle_zip(pack, bundle_zip)
        console.print(f"  • Evidence Bundle : [yellow]{bundle_zip}[/]")



if __name__ == "__main__":
    cli()
