"""Enterprise Risk Management (ERM) scoring, 5x5 Heatmap generation, and COSO mapping engine."""

from __future__ import annotations

from typing import Any

from skill_audit.knowledge.risk_management import (
    calculate_risk_profile,
    generate_heatmap_matrix,
)
from skill_audit.models import (
    AuditStatus,
    ControlEvaluation,
    Finding5C,
    RiskLevel,
    RiskScore5x5,
)


class RiskEngine:
    """Enriches audit findings with 5x5 Likelihood x Impact scores, COSO mapping, and generates Heatmaps."""

    def evaluate_and_enrich(
        self,
        findings: list[Finding5C],
    ) -> tuple[dict[str, Any], list[ControlEvaluation]]:
        """Compute ERM risk profiles for all findings and generate COSO control evaluations."""
        control_evaluations: list[ControlEvaluation] = []

        for f in findings:
            if not f.risk_score:
                f.risk_score = self._compute_finding_risk_score(f)

            if not f.coso_component:
                f.coso_component = self._infer_coso_component(f)

            if not f.business_process:
                f.business_process = self._infer_business_process(f)

            # Generate corresponding COSO Control Evaluation
            control_evaluations.append(
                ControlEvaluation(
                    control_id=f"CTRL-{f.id}",
                    coso_component=f.coso_component,
                    control_title=f"Mitigasi Pengendalian atas: {f.title}",
                    control_nature="preventive" if f.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH] else "detective",
                    control_type="manual",
                    design_effectiveness=AuditStatus.FAIL if f.risk_level == RiskLevel.CRITICAL else AuditStatus.PASS,
                    operating_effectiveness=AuditStatus.FAIL,
                    deficiency_level="Material Weakness" if f.risk_level == RiskLevel.CRITICAL else ("Significant Deficiency" if f.risk_level == RiskLevel.HIGH else "Control Deficiency"),
                    notes=f"Kondisi: {f.condition[:120]}...",
                )
            )

        # Generate 5x5 Heatmap matrix
        heatmap = generate_heatmap_matrix(findings)
        return heatmap, control_evaluations

    @staticmethod
    def _compute_finding_risk_score(f: Finding5C) -> RiskScore5x5:
        r_val = f.risk_level.value
        cat_lower = f.category.lower()

        # Determine likelihood & impact based on risk level and category
        if r_val == "critical":
            likelihood = 4
            impact = 5
            eff = 0.2
        elif r_val == "high":
            likelihood = 4
            impact = 4
            eff = 0.4
        elif r_val == "medium":
            likelihood = 3
            impact = 3
            eff = 0.6
        elif r_val == "low":
            likelihood = 2
            impact = 2
            eff = 0.8
        else:
            likelihood = 1
            impact = 1
            eff = 0.9

        # Adjust for financial / fraud / SoD weight
        if "fraud" in cat_lower or "sod" in cat_lower or "rekonsiliasi" in cat_lower:
            impact = min(5, impact + 1)

        return calculate_risk_profile(likelihood, impact, eff)

    @staticmethod
    def _infer_coso_component(f: Finding5C) -> str:
        cat_lower = (f.category + " " + f.title).lower()
        if "sod" in cat_lower or "pemisahan tugas" in cat_lower or "aritmatika" in cat_lower or "3-way" in cat_lower or "bast" in cat_lower:
            return "Control Activities"
        elif "doa" in cat_lower or "kewenangan" in cat_lower or "etika" in cat_lower or "integritas" in cat_lower or "struktur" in cat_lower:
            return "Control Environment"
        elif "fraud" in cat_lower or "anomali" in cat_lower or "risiko" in cat_lower:
            return "Risk Assessment"
        elif "pelaporan" in cat_lower or "informasi" in cat_lower or "faktur" in cat_lower or "npwp" in cat_lower:
            return "Information & Communication"
        return "Monitoring Activities"

    @staticmethod
    def _infer_business_process(f: Finding5C) -> str:
        text = (f.title + " " + f.category + " " + f.condition).lower()
        if any(k in text for k in ["spk", "po", "pengadaan", "bast", "vendor", "tagihan", "invoice"]):
            return "Procure-to-Pay (P2P)"
        elif any(k in text for k in ["penjualan", "piutang", "surat jalan", "customer", "pelanggan"]):
            return "Order-to-Cash (O2C)"
        elif any(k in text for k in ["jurnal", "buku besar", "laporan keuangan", "neraca", "rekonsiliasi bank"]):
            return "Record-to-Report (R2R)"
        elif any(k in text for k in ["gaji", "payroll", "pegawai", "karyawan", "lembur", "hris"]):
            return "Hire-to-Retire (H2R)"
        return "Tata Kelola & Umum"
