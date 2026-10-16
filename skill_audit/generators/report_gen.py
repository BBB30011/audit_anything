"""Report and executive summary generator with dual-engine (LLM + offline heuristic)."""

from __future__ import annotations

from typing import Any

from skill_audit.generators.llm_client import LLMClient
from skill_audit.models import AuditDocument, AuditMetric, Finding5C, RiskLevel


class ReportGenerator:
    """Generates executive summaries, audit opinions, and corrective action plans."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm = llm_client or LLMClient()

    def generate_executive_summary(
        self,
        title: str,
        documents: list[AuditDocument],
        findings: list[Finding5C],
        metrics: AuditMetric,
    ) -> str:
        """Generate high-level executive summary and audit opinion."""
        if self.llm.is_available:
            try:
                return self._generate_summary_llm(title, documents, findings, metrics)
            except Exception:
                # Fallback to deterministic synthesis on API error
                pass

        return self._generate_summary_deterministic(title, documents, findings, metrics)

    def generate_action_plan(self, findings: list[Finding5C]) -> list[dict[str, Any]]:
        """Generate prioritized remediation action plan from findings."""
        plan: list[dict[str, Any]] = []

        # Sort findings by risk severity (Critical -> High -> Medium -> Low)
        order = {RiskLevel.CRITICAL: 1, RiskLevel.HIGH: 2, RiskLevel.MEDIUM: 3, RiskLevel.LOW: 4, RiskLevel.INFORMATIONAL: 5}
        sorted_findings = sorted(findings, key=lambda f: order.get(f.risk_level, 99))

        for idx, f in enumerate(sorted_findings, 1):
            plan.append({
                "step_no": idx,
                "finding_id": f.id,
                "title": f.title,
                "priority": f.risk_level.value.upper(),
                "action_required": f.recommendation,
                "target_days": f.remediation_deadline_days,
                "pic": self._infer_pic(f.category),
            })

        return plan

    def _generate_summary_deterministic(
        self,
        title: str,
        documents: list[AuditDocument],
        findings: list[Finding5C],
        metrics: AuditMetric,
    ) -> str:
        doc_count = len(documents)
        f_count = len(findings)
        crit_count = metrics.findings_by_risk.get("critical", 0)
        high_count = metrics.findings_by_risk.get("high", 0)
        med_count = metrics.findings_by_risk.get("medium", 0)

        # Determine overall audit opinion
        if crit_count > 0:
            opinion = "TIDAK MEMADAI (Adverse / Unsatisfactory) dengan temuan risiko kritis yang memerlukan tindakan perbaikan segera."
        elif high_count > 0 or metrics.compliance_score < 75.0:
            opinion = "MEMERLUKAN PERBAIKAN SIGNIFIKAN (Qualified / Needs Improvement) terkait kontrol kepatuhan dan konsistensi transaksi."
        elif med_count > 0 or metrics.compliance_score < 90.0:
            opinion = "CUKUP MEMADAI DENGAN CATATAN (Satisfactory with Exceptions) dengan kepatuhan umum yang baik."
        else:
            opinion = "MEMADAI (Unqualified / Satisfactory) di mana seluruh dokumen memenuhi standar administratif dan substansi yang diuji."

        doc_names = ", ".join(d.name for d in documents[:5])
        if len(documents) > 5:
            doc_names += f" dan {len(documents) - 5} dokumen lainnya"

        summary = (
            f"### Ringkasan Eksekutif Audit Dokumen\n\n"
            f"Pemeriksaan kepatuhan dan keabsahan dokumen atas **{title}** mencakup analisis terhadap {doc_count} dokumen "
            f"({doc_names}). Pengujian mencakup uji kelengkapan administratif, uji perhitungan aritmatika dan perpajakan, "
            f"rekonsiliasi silang 3-Way Matching (Kontrak - BAST - Invoice - Bukti Pembayaran), serta kepatuhan klausul standar.\n\n"
            f"**Opini / Kesimpulan Pemeriksaan:**\n"
            f"> Status Pengendalian Internal: **{opinion}**\n\n"
            f"**Sorotan Hasil Pemeriksaan:**\n"
            f"- Total Temuan Audit: **{f_count}** temuan (Kritis: {crit_count}, Tinggi: {high_count}, Sedang: {med_count}).\n"
            f"- Skor Kepatuhan (Compliance Score): **{metrics.compliance_score:.1f}%**.\n"
            f"- Akurasi Aritmatika & Pajak: **{metrics.arithmetic_accuracy:.1f}%**.\n"
            f"- Tingkat Bukti Terverifikasi (Grounding Rate): **{metrics.evidence_grounding_rate:.1f}%**.\n"
        )
        return summary

    def _generate_summary_llm(
        self,
        title: str,
        documents: list[AuditDocument],
        findings: list[Finding5C],
        metrics: AuditMetric,
    ) -> str:
        system_prompt = (
            "Anda adalah Senior Lead Auditor bersertifikasi CIA, CISA, dan QIA. "
            "Tugas Anda adalah menyusun Ringkasan Eksekutif (Executive Summary) formal, berbobot, objektif, "
            "dan berlandaskan data temuan empiris. Gunakan bahasa Indonesia formal audit (Bahasa Baku)."
        )
        finding_summaries = "\n".join(
            f"- [{f.id}][{f.risk_level.value.upper()}] {f.title}: {f.condition}"
            for f in findings[:10]
        )
        user_prompt = (
            f"Judul Audit: {title}\n"
            f"Jumlah Dokumen: {len(documents)}\n"
            f"Daftar Dokumen: {', '.join(d.name for d in documents)}\n"
            f"Skor Kepatuhan: {metrics.compliance_score:.1f}%\n"
            f"Statistik Risiko: {metrics.findings_by_risk}\n"
            f"Ringkasan Temuan:\n{finding_summaries}\n\n"
            f"Susunlah Ringkasan Eksekutif mencakup:\n"
            f"1. Latar Belakang & Ruang Lingkup Pengujian\n"
            f"2. Opini / Kesimpulan Efektivitas Kontrol Dokumen\n"
            f"3. Sorotan Temuan Utama & Dampak Potensial\n"
            f"4. Arah Rekomendasi Strategis"
        )
        return self.llm.complete(system_prompt, user_prompt, temperature=0.2)

    @staticmethod
    def _infer_pic(category: str) -> str:
        cat_lower = category.lower()
        if "pajak" in cat_lower or "aritmatika" in cat_lower or "keuangan" in cat_lower:
            return "Bagian Keuangan & Perpajakan"
        elif "pengadaan" in cat_lower or "kontrak" in cat_lower or "bast" in cat_lower:
            return "Pejabat Pengadaan / Divisi Pengadaan (Procurement)"
        elif "hukum" in cat_lower or "legal" in cat_lower:
            return "Divisi Legal & Kepatuhan (Compliance)"
        elif "security" in cat_lower or "it" in cat_lower:
            return "Divisi IT & Keamanan Informasi"
        return "Unit Pemilik Proses (Process Owner)"
