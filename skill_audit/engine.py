"""Central orchestrator for document and dossier audits."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from skill_audit.analyzers.anomaly import AnomalyDetector
from skill_audit.analyzers.compliance import ComplianceAnalyzer
from skill_audit.analyzers.cross_checker import CrossChecker
from skill_audit.analyzers.governance_checker import GovernanceChecker
from skill_audit.analyzers.math_checker import MathChecker
from skill_audit.analyzers.obligation_engine import ObligationEngine
from skill_audit.analyzers.risk_engine import RiskEngine
from skill_audit.analyzers.sod_checker import SoDChecker
from skill_audit.analyzers.unknowns_engine import UnknownsEngine
from skill_audit.evidence_bundle import create_evidence_bundle
from skill_audit.generators.llm_client import LLMClient
from skill_audit.generators.report_gen import ReportGenerator
from skill_audit.models import (
    AuditDomain,
    AuditMetric,
    AuditObligation,
    AuditPack,
    ControlEvaluation,
    DoAViolation,
    Finding5C,
    ReconciliationItem,
    RiskLevel,
    SoDConflict,
    UnknownItem,
    WorkingPaperRow,
)
from skill_audit.parsers import parse_path


class AuditEngine:
    """End-to-end engine for analyzing documents, performing cross-checks, and building AuditPacks."""

    def __init__(
        self,
        checklist_config: dict[str, Any] | str | Path | None = None,
        llm_client: LLMClient | None = None,
        lead_auditor: str = "Skill-Audit System",
    ) -> None:
        self.checklist_config = checklist_config
        self.llm = llm_client or LLMClient()
        self.report_gen = ReportGenerator(self.llm)
        self.lead_auditor = lead_auditor

        # Specialized enterprise analyzers
        self.math_checker = MathChecker()
        self.cross_checker = CrossChecker()
        self.anomaly_detector = AnomalyDetector()
        self.compliance_analyzer = ComplianceAnalyzer()
        self.sod_checker = SoDChecker()
        self.governance_checker = GovernanceChecker()
        self.risk_engine = RiskEngine()
        self.unknowns_engine = UnknownsEngine()
        self.obligation_engine = ObligationEngine()

    def audit(
        self,
        target_path: str | Path,
        title: str | None = None,
        domain: AuditDomain = AuditDomain.GENERAL,
        audit_ref: str | None = None,
    ) -> AuditPack:
        """Run full audit pipeline on a single document or an entire dossier."""
        path_obj = Path(target_path)
        documents = parse_path(path_obj)
        if not documents:
            raise ValueError(f"No parseable audit documents found in: {target_path}")

        audit_title = title or f"Audit Berkas {path_obj.stem.replace('_', ' ').title()}"
        ref_code = audit_ref or f"AUD-{path_obj.stem.upper()[:6]}-01"

        all_findings: list[Finding5C] = []
        all_working_papers: list[WorkingPaperRow] = []
        all_reconciliations: list[ReconciliationItem] = []

        # 1. Arithmetic & Tax Checks
        math_findings = self.math_checker.analyze(documents)
        all_findings.extend(math_findings)

        # 2. 3-Way Matching & Cross-Document Reconciliation
        x_findings, reconciliations = self.cross_checker.analyze(documents)
        all_findings.extend(x_findings)
        all_reconciliations.extend(reconciliations)

        # 3. Fraud Red Flags & Anomaly Detection
        anom_findings = self.anomaly_detector.analyze(documents)
        all_findings.extend(anom_findings)

        # 4. Framework Checklist Compliance Check
        comp_findings, comp_papers, comp_score = self.compliance_analyzer.analyze(
            documents, self.checklist_config
        )
        all_findings.extend(comp_findings)
        all_working_papers.extend(comp_papers)

        # 5. Segregation of Duties (SoD) Conflicts
        sod_findings, sod_conflicts = self.sod_checker.analyze(documents)
        all_findings.extend(sod_findings)

        # 6. Corporate Governance & Delegation of Authority (DoA) Limits
        gov_findings, doa_violations, gov_score = self.governance_checker.analyze(documents)
        all_findings.extend(gov_findings)

        # 7. Normalize Finding IDs sequentially
        for idx, finding in enumerate(all_findings, 1):
            finding.id = f"FND-{idx:03d}"

        # 8. Enterprise Risk Management (ERM) 5x5 Heatmap & COSO Mapping
        heatmap, control_evaluations = self.risk_engine.evaluate_and_enrich(all_findings)

        # 9. Compute Quantitative Metrics
        metrics = self._calculate_metrics(documents, all_findings, comp_score, math_findings)

        # 10. Executive Summary & Action Plan
        exec_summary = self.report_gen.generate_executive_summary(
            audit_title, documents, all_findings, metrics
        )
        action_plan = self.report_gen.generate_action_plan(all_findings)

        # 11. REA Unknowns & Inquiries Ledger
        unknowns = self.unknowns_engine.analyze(documents, all_findings)

        # 12. REA Reconstruction & Audit Obligations Ledger
        obligations, coverage_pct = self.obligation_engine.evaluate(documents, all_findings)

        # 13. Cryptographic Evidence Bundle (SHA-256 digests and provenance)
        evidence_bundle = create_evidence_bundle(documents, f"EVD-{ref_code}").to_dict()

        return AuditPack(
            title=audit_title,
            audit_ref=ref_code,
            lead_auditor=self.lead_auditor,
            domain=domain,
            executive_summary=exec_summary,
            scope=f"Pemeriksaan komprehensif atas {len(documents)} dokumen pada {path_obj.name}.",
            documents=documents,
            findings=all_findings,
            working_papers=all_working_papers,
            reconciliations=all_reconciliations,
            sod_conflicts=sod_conflicts,
            doa_violations=doa_violations,
            control_evaluations=control_evaluations,
            risk_heatmap=heatmap,
            governance_score=gov_score,
            unknowns=unknowns,
            obligations=obligations,
            evidence_bundle=evidence_bundle,
            metrics=metrics,
            action_plan=action_plan,
            metadata={"source_path": str(path_obj.resolve())},
        )

    def cross_check_files(
        self,
        file_paths: list[str | Path],
        title: str = "Uji Silang Dokumen (Cross-Check)",
    ) -> AuditPack:
        """Explicitly run 3-way matching and reconciliation across a list of distinct files."""
        documents = []
        for fp in file_paths:
            documents.extend(parse_path(Path(fp)))

        all_findings, reconciliations = self.cross_checker.analyze(documents)
        math_findings = self.math_checker.analyze(documents)
        all_findings.extend(math_findings)

        for idx, finding in enumerate(all_findings, 1):
            finding.id = f"FND-X-{idx:03d}"

        metrics = self._calculate_metrics(documents, all_findings, 100.0, math_findings)
        exec_summary = self.report_gen.generate_executive_summary(title, documents, all_findings, metrics)
        action_plan = self.report_gen.generate_action_plan(all_findings)

        return AuditPack(
            title=title,
            audit_ref="AUD-CROSS-01",
            lead_auditor=self.lead_auditor,
            domain=AuditDomain.PROCUREMENT,
            executive_summary=exec_summary,
            scope=f"Uji silang dan rekonsiliasi antara {len(documents)} dokumen terpilih.",
            documents=documents,
            findings=all_findings,
            reconciliations=reconciliations,
            metrics=metrics,
            action_plan=action_plan,
        )

    @staticmethod
    def _calculate_metrics(
        documents: list[Any],
        findings: list[Finding5C],
        compliance_score: float,
        math_findings: list[Finding5C],
    ) -> AuditMetric:
        risk_counts: dict[str, int] = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "informational": 0,
        }
        grounded_count = 0

        for f in findings:
            r_val = f.risk_level.value
            risk_counts[r_val] = risk_counts.get(r_val, 0) + 1
            if f.evidence and any(e.excerpt.strip() for e in f.evidence):
                grounded_count += 1

        total_f = len(findings)
        grounding_rate = (grounded_count / total_f * 100.0) if total_f > 0 else 100.0
        arith_acc = max(0.0, 100.0 - (len(math_findings) * 20.0))

        return AuditMetric(
            total_documents=len(documents),
            total_findings=total_f,
            findings_by_risk=risk_counts,
            compliance_score=compliance_score,
            arithmetic_accuracy=arith_acc,
            evidence_grounding_rate=grounding_rate,
        )
