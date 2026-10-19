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

from skill_audit.models import (
    APIPConclusion,
    AuditDomain,
    AuditPack,
    HumanSignOff,
    RiskLevel,
    UnknownItem,
    UnknownStatus,
)

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
    is_apip = (
        pack.domain == AuditDomain.GOVERNMENT
        or pack.human_sign_off.signoff_type == "aaipi"
        or bool(pack.human_sign_off.apip_conclusion)
        or any("saaipi" in str(r).lower() or "apip" in str(r).lower() for r in pack.terrain_profile.detected_regulations)
        or any("saaipi" in d.content.lower() or "apip" in d.content.lower() for d in pack.documents)
    )

    if Confirm.ask("\nApakah Anda ingin menandatangani pengesahan formal LHA (Human Sign-Off)?", default=True):
        if is_apip:
            console.print(Panel(
                "[bold cyan]Pengesahan Pengawasan Intern APIP (Standar SAAIPI PER-01/AAIPI/DPN/2021)[/]\n"
                "• Peran: [bold]Mitra Strategis & Early Warning System[/]\n"
                "• Menghasilkan: [bold]Simpulan Efektivitas 3 Pilar SPIP (Tata Kelola, Risiko, Kontrol)[/]\n"
                "• [dim]*Catatan: Bukan opini judisial eksternal BPK RI (WTP/WDP/TW/TMP)*[/]",
                border_style="cyan",
            ))
            conclusion = Prompt.ask(
                "Simpulan Pengawasan APIP (SAAIPI 2400 / PP 60/2008 SPIP)",
                choices=[
                    "Sangat Efektif (Tata Kelola, Risiko, & SPIP Berjalan Prima)",
                    "Cukup Efektif dengan Catatan (SPIP Memadai, Rekomendasi Bersifat Perbaikan)",
                    "Kurang Efektif (Memerlukan Perbaikan Signifikan pada Tata Kelola/Pengendalian)",
                    "Tidak Efektif (Berisiko Kritis, Pengendalian Intern Gagal Mengatasi Risiko)",
                    "Pernyataan Telah Direviu (Reviu LK / Negative Assurance)",
                    "Advis Strategis Tata Kelola (Consulting Advisory)",
                ],
                default="Cukup Efektif dengan Catatan (SPIP Memadai, Rekomendasi Bersifat Perbaikan)",
            )
            at = Prompt.ask("Nama & NIP Anggota Tim (AT)", default=pack.human_sign_off.anggota_tim or "Tim Auditor Pertama / Muda")
            kt = Prompt.ask("Nama & NIP Ketua Tim (KT)", default=pack.human_sign_off.ketua_tim or "Drs. Bambang Wijaya, Ak., CA, CRMO (NIP 19820514 200801 1 008)")
            dalnis = Prompt.ask("Nama & NIP Pengendali Teknis (Dalnis)", default=pack.human_sign_off.pengendali_teknis or "Dr. Suryadi, Ak., M.Ak, CIA, CGCAE (NIP 19760910 200003 1 002)")
            pm = Prompt.ask("Nama & NIP Pengendali Mutu / Irban (PM)", default=pack.human_sign_off.pengendali_mutu or "Hj. Ratna Sari, SE., M.Si, QGIA (NIP 19741201 199903 2 001)")
            inspektur = Prompt.ask("Nama & NIP Inspektur (Pimpinan APIP)", default=pack.human_sign_off.inspektur or "Ir. Mochammad Hidayat, M.M., CRGP (NIP 19680315 199303 1 005)")
            comments = Prompt.ask(
                "Catatan & Arahan Supervisi Pengawasan Intern",
                default="Pengendalian intern dan tata kelola pengadaan dinilai cukup memadai dengan rekomendasi percepatan pengenaan sanksi denda dan tertib administrasi.",
            )

            pack.human_sign_off = HumanSignOff(
                reviewer_name=kt,
                reviewer_role="Ketua Tim Pengawasan Intern APIP",
                reviewer_license_or_nip="",
                audit_opinion=conclusion,
                signed_at=datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC"),
                comments=comments,
                is_signed=True,
                signoff_type="aaipi",
                apip_conclusion=conclusion,
                anggota_tim=at,
                ketua_tim=kt,
                pengendali_teknis=dalnis,
                pengendali_mutu=pm,
                inspektur=inspektur,
            )
            console.print(f"[bold green]✓ LHA APIP berhasil disahkan oleh {kt} dengan simpulan: {conclusion}[/]")
        else:
            name = Prompt.ask("Nama Auditor Penanggung Jawab", default="Drs. Bambang Wijaya, Ak., CA, CPA")
            role = Prompt.ask("Jabatan Auditor", default="Lead Internal Auditor")
            nip = Prompt.ask("Nomor Registrasi Akuntan / Lisensi", default="NIP-19850412-201001-1-003")
            opinion = Prompt.ask(
                "Simpulan Pengendalian Internal",
                choices=[
                    "Adequate / Satisfactory (Pengendalian Internal Efektif)",
                    "Adequate with Improvements (Memadai dengan Catatan)",
                    "Needs Significant Improvement (Perlu Perbaikan Signifikan)",
                    "Unsatisfactory (Tidak Memadai)",
                ],
                default="Adequate with Improvements (Memadai dengan Catatan)",
            )
            comments = Prompt.ask(
                "Catatan Akhir Auditor",
                default="Pengendalian internal cukup memadai dengan beberapa catatan koreksi administratif.",
            )

            pack.human_sign_off = HumanSignOff(
                reviewer_name=name,
                reviewer_role=role,
                reviewer_license_or_nip=nip,
                audit_opinion=opinion,
                signed_at=datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC"),
                comments=comments,
                is_signed=True,
                signoff_type="general",
            )
            console.print(f"[bold green]✓ Berhasil ditandatangani oleh {name} dengan simpulan: {opinion}[/]")

    # Save updated pack
    pack.to_yaml(p_path)
    console.print(f"\n[bold green]✓ Seluruh perubahan hasil triage telah disimpan ke:[/] {p_path}")
    return pack
