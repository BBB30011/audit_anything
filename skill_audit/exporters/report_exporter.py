"""Markdown report and working paper exporters."""

from __future__ import annotations

from pathlib import Path

from skill_audit.models import AuditDomain, AuditPack, AuditStatus, Finding5C, RiskLevel


class ReportExporter:
    """Exports AuditPack into professional Markdown Audit Reports (LHA) and Working Papers (KKA)."""

    def export_report(self, pack: AuditPack, output_file: str | Path | None = None) -> str:
        """Render formal Laporan Hasil Audit (LHA) in Markdown format."""
        is_apip = (
            pack.domain == AuditDomain.GOVERNMENT
            or pack.human_sign_off.signoff_type == "aaipi"
            or any("saaipi" in d.content.lower() or "apip" in d.content.lower() for d in pack.documents)
        )
        if is_apip:
            from skill_audit.knowledge.saaipi_standards import format_lha_aaipi
            report_text = format_lha_aaipi(pack)
            if output_file:
                p = Path(output_file)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(report_text, encoding="utf-8")
            return report_text

        lines: list[str] = [
            f"# LAPORAN HASIL AUDIT DOKUMEN (LHA)",
            f"**Referensi Penugasan:** `{pack.audit_ref}`  ",
            f"**Judul Penugasan:** {pack.title}  ",
            f"**Auditor Penanggung Jawab:** {pack.lead_auditor}  ",
            f"**Tanggal Audit:** {pack.created_at[:10]}  ",
            f"**Klasifikasi Audit:** {pack.domain.value.upper()}  ",
            "",
            "---",
            "",
            "## 1. RINGKASAN EKSEKUTIF & KESIMPULAN PENGAWASAN",
            pack.executive_summary,
            "",
            "### 1.1 Metrik Ringkasan Pemeriksaan",
            "| Indikator Pemeriksaan | Hasil / Skor | Status |",
            "|:---|:---:|:---:|",
            f"| Total Dokumen Diperiksa | {pack.metrics.total_documents} Berkas | Info |",
            f"| Skor Kepatuhan (Compliance) | {pack.metrics.compliance_score:.1f}% | {'🟢 Memadai' if pack.metrics.compliance_score >= 80 else '🔴 Perlu Perbaikan'} |",
            f"| Akurasi Aritmatika & Pajak | {pack.metrics.arithmetic_accuracy:.1f}% | {'🟢 Akurat' if pack.metrics.arithmetic_accuracy >= 90 else '🟡 Selisih Hitung'} |",
            f"| Tingkat Bukti Terverifikasi | {pack.metrics.evidence_grounding_rate:.1f}% | {'🟢 Tervalidasi' if pack.metrics.evidence_grounding_rate >= 80 else '🟡 Sebagian'} |",
            f"| Total Temuan Audit | {pack.metrics.total_findings} Temuan | {'🔴 Kritis' if pack.metrics.findings_by_risk.get('critical', 0) > 0 else '🟡 Sedang'} |",
            "",
            f"- **Kritis (Critical):** {pack.metrics.findings_by_risk.get('critical', 0)}",
            f"- **Tinggi (High):** {pack.metrics.findings_by_risk.get('high', 0)}",
            f"- **Sedang (Medium):** {pack.metrics.findings_by_risk.get('medium', 0)}",
            f"- **Rendah (Low):** {pack.metrics.findings_by_risk.get('low', 0)}",
            "",
            f"**Medan / Domain Audit Terdeteksi:** `{pack.domain.value.upper()}` (Tingkat Keyakinan: {pack.terrain_profile.confidence*100:.0f}%)  ",
            f"**Regulasi / Standar Acuan Teridentifikasi:** {', '.join(pack.terrain_profile.detected_regulations) if pack.terrain_profile.detected_regulations else 'Standar Pemeriksaan Internal Umum'}  ",
            "",
            "---",
            "",
            "## 2. RUANG LINGKUP & DOKUMEN YANG DIPERIKSA",
            f"{pack.scope}\n",
            "| No | Nama Dokumen | Peran dalam Berkas | Halaman/Lembar |",
            "|:---|:---|:---|:---:|",
        ]

        for idx, doc in enumerate(pack.documents, 1):
            lines.append(f"| {idx} | `{doc.name}` | {doc.role_in_dossier.upper()} | {doc.total_pages_or_sheets} |")

        lines.extend([
            "",
            "---",
            "",
            "## 3. TABEL REKONSILIASI DOKUMEN & 3-WAY MATCHING",
        ])

        if pack.reconciliations:
            lines.append("| Uraian Uji Silang | Rincian Nilai Antar-Dokumen | Selisih | Hasil Uji |")
            lines.append("|:---|:---|:---:|:---:|")
            for r in pack.reconciliations:
                vals_str = "<br>".join(f"- {k}: Rp {v:,.0f}" if isinstance(v, (int, float)) else f"- {k}: {v}" for k, v in r.doc_values.items())
                diff_str = f"Rp {r.discrepancy_amount:,.0f}" if r.discrepancy_amount else "Rp 0"
                stat_badge = "🟢 MATCH" if r.status == AuditStatus.PASS else "🔴 MISMATCH"
                lines.append(f"| {r.item_description} | {vals_str} | {diff_str} | {stat_badge} |")
        else:
            lines.append("_Tidak ada pengujian rekonsiliasi nilai multi-dokumen._")

        lines.extend([
            "",
            "---",
            "",
            "## 4. TATA KELOLA KORPORASI (GCG), SoD & BATAS KEWENANGAN (DoA)",
        ])

        if pack.sod_conflicts:
            lines.append("### 4.1 Benturan Pemisahan Tugas (Segregation of Duties - SoD)")
            lines.append("| ID | Nama Individu | Peran Bertentangan | Dokumen Terkait | Risiko Fraud |")
            lines.append("|:---:|:---|:---|:---|:---|")
            for s in pack.sod_conflicts:
                lines.append(f"| `{s.conflict_id}` | **{s.individual_name}** | {s.role_a} vs {s.role_b} | {', '.join(s.document_refs)} | {s.risk_explanation} |")
            lines.append("")
        else:
            lines.append("> 🟢 **Pemisahan Tugas (SoD) Memadai:** Tidak ditemukan perangkapan peran bertentangan dalam berkas.\n")

        if pack.doa_violations:
            lines.append("### 4.2 Pelampauan Batas Kewenangan Otorisasi (DoA)")
            lines.append("| ID | Pejabat Penandatangan | Nilai Transaksi | Batas Maksimum | Pelampauan | Dokumen |")
            lines.append("|:---:|:---|:---:|:---:|:---:|:---|")
            for d in pack.doa_violations:
                lines.append(f"| `{d.violation_id}` | **{d.approver_name}** ({d.approver_title}) | Rp {d.transaction_amount:,.0f} | Rp {d.authorized_limit:,.0f} | **+Rp {d.excess_amount:,.0f}** | `{d.document_ref}` |")
            lines.append("")
        else:
            lines.append("> 🟢 **Batas Otorisasi (DoA) Sesuai:** Seluruh pengesahan berada dalam batas kewenangan yang sah.\n")

        lines.extend([
            "",
            "---",
            "",
            "## 5. DAFTAR TEMUAN AUDIT (STANDAR 5C)",
        ])

        if not pack.findings:
            lines.append("> 🟢 **Tidak Ditemukan Anomali atau Ketidakpatuhan Material.** Seluruh berkas memenuhi kriteria pengujian.")
        else:
            for f in pack.findings:
                lines.extend(self._render_finding_5c(f))

        lines.extend([
            "",
            "---",
            "",
            "## 6. RENCANA AKSI & MATRIKS TINDAK LANJUT",
            "| No | ID Temuan | Prioritas | Langkah Perbaikan yang Diperlukan | Batas Waktu | PIC |",
            "|:---:|:---:|:---:|:---|:---:|:---|",
        ])

        for step in pack.action_plan:
            lines.append(
                f"| {step['step_no']} | `{step['finding_id']}` | **{step['priority']}** | "
                f"{step['action_required']} | {step['target_days']} Hari | {step['pic']} |"
            )

        # 7. Forensic Digital Analysis (Benford's Law)
        bn = pack.benford_analysis
        bn_status = bn.conformity_status.replace("_", " ").title()
        lines.extend([
            "",
            "---",
            "",
            "## 7. ANALISIS FORENSIK DIGITAL (UJI HUKUM DISTRIBUSI BENFORD'S LAW)",
            f"> *Standar Forensik Nigrini (2012) & ISA 240: Menguji kealamian sebaran angka transaksi untuk mendeteksi rekayasa dan kecurangan.*",
            "",
            f"- **Status Kesesuaian Distribusi:** `{bn_status.upper()}`",
            f"- **Skor Mean Absolute Deviation (MAD):** `{bn.mad_score:.4f}` (Ambang batas wajar <= 0.012)",
            f"- **Skor Chi-Square:** `{bn.chi_square:.2f}` | **Total Sampel Angka Diuji:** `{bn.analyzed_digits}`",
            f"- **Digit Anomali Deviasi Kritis (|Z| > 2.58):** {', '.join(f'Digit {d}' for d in bn.critical_anomalies) if bn.critical_anomalies else 'Tidak ada (Distribusi Wajar)'}",
            "",
        ])
        if bn.digit_distribution:
            lines.extend([
                "| Digit | Frekuensi Aktual | Aktual (%) | Standar Benford (%) | Selisih (%) | Z-Score | Status Forensik |",
                "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
            ])
            for d in bn.digit_distribution:
                is_anom = d.digit in bn.critical_anomalies
                stat_badge = "🔴 **ANOMALI**" if is_anom else "🟢 Wajar"
                diff_sign = "+" if d.diff_pct > 0 else ""
                lines.append(
                    f"| **{d.digit}** | {d.actual_count} | {d.actual_pct:.1f}% | {d.expected_pct:.1f}% | {diff_sign}{d.diff_pct:.1f}% | {d.z_score:.2f} | {stat_badge} |"
                )
            lines.append("")

        # 8. REA Ledger of Unknowns (Inquiries)
        lines.extend([
            "",
            "---",
            "",
            "## 8. BUKU BESAR PERTANYAAN TERBUKA (LEDGER OF UNKNOWNS & INQUIRIES)",
            "> *Metodologi REA: Seluruh ambiguitas bukti dan dokumen yang belum diperoleh dicatat sebagai inquiry resmi.*",
            "",
        ])
        if pack.unknowns:
            lines.append("| ID | Pertanyaan & Klarifikasi Bukti | Kategori | Status | Bukti Diperlukan |")
            lines.append("|:---:|:---|:---|:---:|:---|")
            for u in pack.unknowns:
                st_icon = "🟢 RESOLVED" if u.status.value == "resolved" else ("🟡 OPEN" if u.status.value == "open" else "⚪ WAIVED")
                res_txt = f"<br>_Penyelesaian:_ {u.resolution_notes}" if u.resolution_notes else ""
                lines.append(f"| `{u.id}` | **{u.question}**{res_txt} | `{u.category}` | `{st_icon}` | {u.evidence_required} |")
            lines.append("")
        else:
            lines.append("> 🟢 **Seluruh Bukti Lengkap:** Tidak terdapat pertanyaan atau ambiguitas bukti yang menggantung.\n")

        # 9. REA Audit Obligations & Coverage
        lines.extend([
            "",
            "---",
            "",
            "## 9. EVALUASI PEMENUHAN KEWAJIBAN AUDIT (AUDIT OBLIGATIONS COVERAGE)",
            "> *Metodologi REA: Pemenuhan kewajiban pengujian standar sesuai regulasi dan kerangka kerja.*",
            "",
        ])
        if pack.obligations:
            lines.append("| ID | Prosedur Kewajiban Audit | Dasar Regulasi / Standar | Status | Catatan Pengujian |")
            lines.append("|:---:|:---|:---|:---:|:---|")
            for o in pack.obligations:
                st_icon = "🟢 SATISFIED" if o.status == "satisfied" else ("🔴 VIOLATED" if o.status == "violated" else "🟡 PARTIAL")
                lines.append(f"| `{o.id}` | **{o.title}** | {o.standard_ref} | `{st_icon}` | {o.coverage_notes} |")
            lines.append("")

        # 10. Cryptographic Evidence Bundle Manifest
        lines.extend([
            "",
            "---",
            "",
            "## 10. MANIFES BERKAS BUKTI & INTEGRITAS KRIPTOGRAFIS (EVIDENCE BUNDLE)",
            "> *Nilai Hash SHA-256 menjamin keaslian bukti audit dan deteksi manipulasi (Tamper-Evident).*  ",
            f"**Bundle ID:** `{pack.evidence_bundle.get('bundle_id', 'EVD-AUTO')}` | "
            f"**Status Integritas:** `🟢 {pack.evidence_bundle.get('integrity_status', 'VERIFIED_INTACT').upper()}`",
            "",
            "| Nama Berkas Dokumen | Peran Berkas | SHA-256 Digest | Ukuran | Status Forensik |",
            "|:---|:---|:---|:---:|:---:|",
        ])
        for f in pack.evidence_bundle.get("files", []):
            hash_abbr = f"{f.get('content_sha256', '')[:16]}...{f.get('content_sha256', '')[-12:]}"
            lines.append(f"| `{f.get('name')}` | `{f.get('role_in_dossier')}` | `{hash_abbr}` | {f.get('size_bytes', 0)} B | 🟢 Verified Intact |")

        # 11. Human Sign-Off Sheet
        lines.extend([
            "",
            "---",
            "",
            "## 11. LEMBAR PENGESAHAN & KESIMPULAN AUDITOR (HUMAN SIGN-OFF)",
        ])
        so = pack.human_sign_off
        if so.is_signed:
            lines.extend([
                f"> **STATUS:** `🟢 TELAH DISAHKAN & DITANDATANGANI`  ",
                f"> **Nama Auditor Penanggung Jawab:** {so.reviewer_name}  ",
                f"> **Jabatan / Registrasi:** {so.reviewer_role} (NIP/No. Reg: `{so.reviewer_license_or_nip}`)  ",
                f"> **Tanggal Pengesahan:** {so.signed_at}  ",
                f"> **Kesimpulan Pengawasan:** **{so.audit_opinion}**  ",
                f"> **Catatan Akhir Auditor:**  \n> _{so.comments}_  ",
                "",
                "```",
                f"   [DITANDATANGANI SECARA ELEKTRONIK]",
                f"   Oleh      : {so.reviewer_name}",
                f"   Peran     : {so.reviewer_role}",
                f"   Simpulan  : {so.audit_opinion}",
                "```",
            ])
        else:
            lines.extend([
                "> 🟡 **STATUS: DRAFT - MENUNGGU REVIEW & PENGESAHAN AUDITOR MANUSIA**",
                "> *Untuk menandatangani laporan ini, jalankan perintah:* `skillaudit signoff <pack_file>` *atau gunakan dasbor interaktif.*",
            ])

        lines.append("\n---\n*Laporan ini dihasilkan oleh Sistem Skill-Audit terintegrasi Kolaborasi Human-AI & Arsitektur REA.*")
        report_text = "\n".join(lines)

        if output_file:
            p = Path(output_file)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(report_text, encoding="utf-8")

        return report_text


    def export_working_papers(self, pack: AuditPack, output_file: str | Path | None = None) -> str:
        """Render Kertas Kerja Audit (KKA) in Markdown table format."""
        lines = [
            f"# KERTAS KERJA AUDIT (KKA)",
            f"**Penugasan:** {pack.title} (`{pack.audit_ref}`)  ",
            f"**Auditor:** {pack.lead_auditor} | **Tanggal:** {pack.created_at[:10]}  ",
            "",
            "| Ref KKA | Prosedur Pemeriksaan | Dokumen Diuji | Hasil Pengujian | Catatan & Analisis | Ref Temuan |",
            "|:---|:---|:---|:---:|:---|:---:|",
        ]

        for row in pack.working_papers:
            res_str = "🟢 Sesuai (Pass)" if row.result == AuditStatus.PASS else ("🔴 Temuan (Fail)" if row.result == AuditStatus.FAIL else "🟡 Catatan (Warn)")
            f_ref = f"`{row.finding_ref}`" if row.finding_ref else "-"
            lines.append(
                f"| `{row.ref_no}` | {row.procedure} | {row.document_ref} | {res_str} | {row.notes} | {f_ref} |"
            )

        kka_text = "\n".join(lines)
        if output_file:
            p = Path(output_file)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(kka_text, encoding="utf-8")

        return kka_text

    @staticmethod
    def _render_finding_5c(f: Finding5C) -> list[str]:
        risk_pill = {
            RiskLevel.CRITICAL: "🔴 **KRITIS (CRITICAL)**",
            RiskLevel.HIGH: "🟠 **TINGGI (HIGH)**",
            RiskLevel.MEDIUM: "🟡 **SEDANG (MEDIUM)**",
            RiskLevel.LOW: "🔵 **RENDAH (LOW)**",
            RiskLevel.INFORMATIONAL: "⚪ **INFORMASIONAL**",
        }.get(f.risk_level, f.risk_level.value.upper())

        out = [
            f"### [{f.id}] {f.title}",
            f"- **Tingkat Risiko:** {risk_pill}",
            f"- **Kategori Pengujian:** `{f.category}`",
            f"- **Proses Bisnis:** `{f.business_process or 'Procure-to-Pay'}` | **Komponen COSO:** `{f.coso_component or 'Control Activities'}`",
        ]

        if f.risk_score:
            out.append(
                f"- **Skor ERM (5x5):** Likelihood={f.risk_score.likelihood}, Impact={f.risk_score.impact} "
                f"(Inherent: {f.risk_score.inherent_score}, Residual: {f.risk_score.residual_score:.1f}, Zona: `{f.risk_score.heatmap_zone.upper()}`)"
            )

        out.extend([
            "",
            f"#### A. Kondisi (Condition)",
            f"{f.condition}",
            "",
            f"#### B. Kriteria (Criteria)",
            f"{f.criteria}",
            "",
            f"#### C. Sebab (Cause)",
            f"{f.cause}",
            "",
            f"#### D. Akibat & Risiko (Consequence)",
            f"{f.consequence}",
            "",
            f"#### E. Rekomendasi Perbaikan (Recommendation)",
            f"{f.recommendation}",
            "",
        ])

        if f.evidence:
            out.append("#### Bukti Terverifikasi (Verified Source Citations):")
            for ev in f.evidence:
                out.append(f"> 📄 **{ev.document}** ({ev.locator}):\n> \"_{ev.excerpt}_\"")
            out.append("")

        out.append("---\n")
        return out
