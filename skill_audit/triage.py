"""Human-AI Collaborative Audit Triage and Sign-Off Module.

Enables seamless bi-directional collaboration between AI Agents and Human Lead Auditors:
1. AI proposes findings, evidence citations, and open unknowns.
2. Human Auditor reviews, exercises professional judgement, approves/rejects, resolves unknowns.
3. Formal Human Sign-Off with audit opinion (WTP/WDP/Adverse/Disclaimer).
4. Persists human feedback into AuditPack and updates audit deliverables.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from skill_audit.models import AuditPack, HumanSignOff, RiskLevel, UnknownItem, UnknownStatus

console = Console()


def display_triage_summary(pack: AuditPack) -> None:
    """Print high-level overview of items awaiting human auditor review."""
    table = Table(title="📋 Status Review Kolaborasi Human-AI", header_style="bold cyan")
    table.add_column("Komponen Audit", style="bold")
    table.add_column("Total Item", justify="center")
    table.add_column("Status Review", justify="center")

    approved_findings = sum(1 for f in pack.findings if f.human_status == "approved")
    rejected_findings = sum(1 for f in pack.findings if f.human_status == "rejected")
    pending_findings = sum(1 for f in pack.findings if f.human_status == "pending")

    table.add_row(
        "Temuan Audit (5C Findings)",
        str(len(pack.findings)),
        f"[green]{approved_findings} Disetujui[/] | [yellow]{pending_findings} Pending[/] | [red]{rejected_findings} Ditolak[/]",
    )

    open_unknowns = sum(1 for u in pack.unknowns if u.status == UnknownStatus.OPEN)
    resolved_unknowns = sum(1 for u in pack.unknowns if u.status == UnknownStatus.RESOLVED)
    table.add_row(
        "Ledger of Unknowns (Inquiries)",
        str(len(pack.unknowns)),
        f"[green]{resolved_unknowns} Selesai[/] | [yellow]{open_unknowns} Menunggu Klarifikasi[/]",
    )

    sign_off_status = "[green]✓ TELAH DITANDATANGANI[/]" if pack.human_sign_off.is_signed else "[yellow]MENUNGGU PENGESAHAN[/]"
    table.add_row("Pengesahan Auditor Manusia", "1 Lembar", sign_off_status)

    console.print(table)


def run_interactive_triage(pack_path: str | Path) -> AuditPack:
    """Run interactive terminal session for human auditor to review AI results."""
    p_path = Path(pack_path)
    pack = AuditPack.from_yaml(p_path)

    console.print(Panel(
        f"[bold cyan]Skill-Audit: Sesi Triage & Kolaborasi Human-AI[/]\n"
        f"Penugasan: [yellow]{pack.title}[/] (Ref: {pack.audit_ref})\n"
        f"Audit Berkas: {len(pack.documents)} dokumen | Temuan AI: {len(pack.findings)} temuan",
        border_style="cyan",
    ))

    display_triage_summary(pack)

    # 1. Review 5C Findings
    if pack.findings:
        if Confirm.ask("\nApakah Anda ingin mereview temuan audit (5C Findings)?", default=True):
            for idx, f in enumerate(pack.findings, 1):
                console.print(f"\n[bold yellow]─── Temuan {idx}/{len(pack.findings)}: [{f.id}] {f.title} ───[/]")
                console.print(f"• Kategori     : {f.category}")
                console.print(f"• Tingkat Risiko AI : [{f.risk_level.value.upper()}]")
                console.print(f"• Kondisi      : {f.condition}")
                console.print(f"• Rekomendasi  : {f.recommendation}")
                if f.evidence:
                    console.print(f"• Bukti Verbatim: \"{f.evidence[0].excerpt[:120]}...\" ({f.evidence[0].document})")

                choice = Prompt.ask(
                    "Tindakan Auditor",
                    choices=["a", "r", "m", "s"],
                    default="a",
                )
                # a: Approve, r: Reject (False positive), m: Modify note/risk, s: Skip
                if choice == "a":
                    f.human_status = "approved"
                    console.print("[green]✓ Temuan Disetujui (Approved).[/]")
                elif choice == "r":
                    f.human_status = "rejected"
                    f.human_notes = Prompt.ask("Alasan penolakan / False positive")
                    console.print("[red]✗ Temuan Ditolak (Rejected).[/]")
                elif choice == "m":
                    new_risk = Prompt.ask(
                        "Ubah Tingkat Risiko",
                        choices=["critical", "high", "medium", "low", "informational"],
                        default=f.risk_level.value,
                    )
                    f.risk_level = RiskLevel(new_risk)
                    f.human_notes = Prompt.ask("Catatan Auditor Manusia")
                    f.human_status = "adjusted"
                    console.print(f"[cyan]✓ Tingkat risiko diubah menjadi {new_risk.upper()}.[/]")

    # 2. Review Unknowns Ledger
    if pack.unknowns:
        if Confirm.ask("\nApakah Anda ingin memeriksa Ledger of Unknowns (Inquiries)?", default=True):
            for idx, u in enumerate(pack.unknowns, 1):
                console.print(f"\n[bold yellow]─── Inquiry {idx}/{len(pack.unknowns)}: [{u.id}] {u.question} ───[/]")
                console.print(f"• Status Saat Ini : [{u.status.value.upper()}]")
                console.print(f"• Bukti Diperlukan: {u.evidence_required}")

                if u.status == UnknownStatus.OPEN:
                    action = Prompt.ask(
                        "Tindakan Auditor",
                        choices=["resolve", "waive", "keep_open"],
                        default="resolve",
                    )
                    if action == "resolve":
                        notes = Prompt.ask("Keterangan Penyelesaian / Klarifikasi Bukti")
                        ref = Prompt.ask("Nomor Bukti / Dokumen Pendukung", default="")
                        auditor_name = Prompt.ask("Nama Auditor", default="Lead Auditor")
                        u.status = UnknownStatus.RESOLVED
                        u.resolution_notes = notes
                        u.evidence_ref = ref
                        u.resolved_by = auditor_name
                        console.print("[green]✓ Inquiry dinyatakan Selesai (Resolved).[/]")
                    elif action == "waive":
                        rationale = Prompt.ask("Alasan Pelepasan (Waiver Rationale)")
                        u.status = UnknownStatus.WAIVED
                        u.resolution_notes = f"[WAIVED]: {rationale}"
                        console.print("[yellow]⚠ Inquiry Diterima/Dilepas (Waived).[/]")

    # 3. Formal Human Sign-Off
    if Confirm.ask("\nApakah Anda ingin menandatangani pengesahan formal LHA (Human Sign-Off)?", default=True):
        name = Prompt.ask("Nama Auditor Penanggung Jawab", default="Drs. Bambang Wijaya, Ak., CA, CPA")
        role = Prompt.ask("Jabatan Auditor", default="Lead Internal Auditor")
        nip = Prompt.ask("Nomor Registrasi Akuntan / NIP", default="NIP-19850412-201001-1-003")
        opinion = Prompt.ask(
            "Opini / Kesimpulan Audit",
            choices=[
                "WTP (Wajar Tanpa Pengecualian)",
                "WDP (Wajar Dengan Pengecualian)",
                "Tidak Wajar (Adverse)",
                "Menolak Memberikan Opini (Disclaimer)",
            ],
            default="WDP (Wajar Dengan Pengecualian)",
        )
        comments = Prompt.ask(
            "Catatan Akhir Auditor",
            default="Pengendalian internal cukup memadai dengan catatan perbaikan kepatuhan kontrak dan administrasi perpajakan.",
        )

        pack.human_sign_off = HumanSignOff(
            reviewer_name=name,
            reviewer_role=role,
            reviewer_license_or_nip=nip,
            audit_opinion=opinion,
            signed_at=datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC"),
            comments=comments,
            is_signed=True,
        )
        console.print(f"[bold green]✓ Berhasil ditandatangani oleh {name} dengan opini: {opinion}[/]")

    # Save updated pack
    pack.to_yaml(p_path)
    console.print(f"\n[bold green]✓ Seluruh perubahan hasil triage telah disimpan ke:[/] {p_path}")
    return pack
