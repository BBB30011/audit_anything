"""Deterministic quality and provenance validation for AuditPacks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from skill_audit.grounding import normalize_evidence
from skill_audit.models import AuditPack


@dataclass(frozen=True)
class ValidationIssue:
    severity: str  # 'error' or 'warning'
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"severity": self.severity, "code": self.code, "message": self.message}


@dataclass
class PackValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "metrics": self.metrics,
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "issues": [i.to_dict() for i in self.issues],
        }


def validate_audit_pack(pack: AuditPack, strict: bool = False) -> PackValidationReport:
    """Validate an AuditPack for structural integrity, 5C completeness, and evidence grounding.

    Strict mode fails if any finding lacks a verified source excerpt citation.
    """
    report = PackValidationReport()

    def _add(severity: str, code: str, msg: str) -> None:
        report.issues.append(ValidationIssue(severity=severity, code=code, message=msg))

    # 1. Header checks
    if not pack.title.strip():
        _add("error", "missing-title", "AuditPack title is empty.")
    if not pack.audit_ref.strip():
        _add("error", "missing-audit-ref", "AuditPack reference code is empty.")
    if not pack.executive_summary.strip():
        _add("warning", "missing-executive-summary", "Executive summary is missing.")

    # 2. Findings checks (5C validation)
    seen_titles: set[str] = set()
    cited_count = 0

    for idx, f in enumerate(pack.findings, 1):
        f_title_norm = normalize_evidence(f.title).casefold()
        if f_title_norm in seen_titles:
            _add("warning", "duplicate-finding", f"Temuan duplikat terdeteksi pada item {idx}: '{f.title}'.")
        seen_titles.add(f_title_norm)

        # Check 5C fields
        if not f.condition.strip():
            _add("error", "missing-condition", f"Temuan {f.id} ({f.title}) tidak memiliki elemen Kondisi (Condition).")
        if not f.criteria.strip():
            _add("error", "missing-criteria", f"Temuan {f.id} ({f.title}) tidak memiliki elemen Kriteria (Criteria).")
        if not f.cause.strip():
            _add("warning", "missing-cause", f"Temuan {f.id} ({f.title}) tidak memiliki analisis Sebab (Cause).")
        if not f.consequence.strip():
            _add("error", "missing-consequence", f"Temuan {f.id} ({f.title}) tidak memiliki uraian Akibat/Risiko (Consequence).")
        if not f.recommendation.strip():
            _add("error", "missing-recommendation", f"Temuan {f.id} ({f.title}) tidak memiliki Rekomendasi (Recommendation).")

        # Grounding / evidence check
        has_evidence = False
        if f.evidence:
            for ev in f.evidence:
                if ev.excerpt.strip():
                    has_evidence = True
                    break

        if has_evidence:
            cited_count += 1
        else:
            sev = "error" if strict else "warning"
            _add(sev, "uncited-finding", f"Temuan {f.id} ({f.title}) tidak memiliki kutipan bukti dokumen sumber (uncited).")

    # 3. Metrics sanity
    total_f = len(pack.findings)
    if pack.metrics.total_findings != total_f:
        _add("warning", "metric-mismatch", f"Metrics total_findings ({pack.metrics.total_findings}) != len(findings) ({total_f}).")

    report.metrics = {
        "total_documents": len(pack.documents),
        "total_findings": total_f,
        "cited_findings": cited_count,
        "grounding_percentage": round((cited_count / total_f * 100.0) if total_f > 0 else 100.0, 1),
        "total_working_papers": len(pack.working_papers),
        "total_reconciliations": len(pack.reconciliations),
    }

    return report
