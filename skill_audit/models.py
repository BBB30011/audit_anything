"""Core data models for Skill-Audit.

Defines the data structures flowing through the audit pipeline:
  Source Documents / Dossiers -> Extracted Chunks -> Verification & Reconciliation ->
  AuditPack (5C Findings, Working Papers, Reconciliations, Metrics, Action Plan)
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"

    @property
    def score_weight(self) -> int:
        weights = {
            "critical": 25,
            "high": 15,
            "medium": 7,
            "low": 2,
            "informational": 0,
        }
        return weights.get(self.value, 0)


class AuditDomain(str, Enum):
    PROCUREMENT = "procurement"
    FINANCIAL = "financial"
    LEGAL_CONTRACT = "legal_contract"
    COMPLIANCE = "compliance"
    IT_SECURITY = "it_security"
    INTERNAL_CONTROL = "internal_control"
    HEALTHCARE = "healthcare"
    GOVERNMENT = "government"
    HR_PAYROLL = "hr_payroll"
    SUPPLY_CHAIN = "supply_chain"
    FORENSIC_FRAUD = "forensic_fraud"
    TAX_CUSTOMS = "tax_customs"
    BANKING_FINTECH = "banking_fintech"
    ESG_SUSTAINABILITY = "esg_sustainability"
    GENERAL = "general"
    AUTO = "auto"


class DocType(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    DOCX = "docx"
    TEXT = "text"
    DOSSIER = "dossier"


class AuditStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    INCONCLUSIVE = "inconclusive"


class UnknownStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    WAIVED = "waived"


def slugify(text: str) -> str:
    """Convert arbitrary title into safe filesystem & URL slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-") or "audit-pack"


# ======================================================================
# Evidence & Grounding Models
# ======================================================================


@dataclass(frozen=True)
class EvidenceCitation:
    """Verbatim quote from a source document proving an audit finding or paper."""

    document: str
    locator: str  # e.g., 'Page 4', 'Row 15', 'Pasal 3.2'
    excerpt: str  # verbatim text quote
    char_offset: int | None = None
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "document": self.document,
            "locator": self.locator,
            "excerpt": self.excerpt,
        }
        if self.char_offset is not None:
            d["char_offset"] = self.char_offset
        if self.confidence < 1.0:
            d["confidence"] = round(self.confidence, 2)
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvidenceCitation:
        return cls(
            document=str(data.get("document", "")),
            locator=str(data.get("locator", "")),
            excerpt=str(data.get("excerpt", "")),
            char_offset=data.get("char_offset"),
            confidence=float(data.get("confidence", 1.0)),
        )

    @property
    def label(self) -> str:
        return f"[{self.document} · {self.locator}]"


@dataclass
class KnowledgeChunk:
    """Atomic content chunk extracted from an audit document."""

    content: str
    document_name: str = ""
    section: str = ""
    locator: str = ""
    chunk_index: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "document_name": self.document_name,
            "section": self.section,
            "locator": self.locator,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeChunk:
        return cls(
            content=str(data.get("content", "")),
            document_name=str(data.get("document_name", "")),
            section=str(data.get("section", "")),
            locator=str(data.get("locator", "")),
            chunk_index=int(data.get("chunk_index", 0)),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Section:
    """Coherent structural unit (e.g. Chapter, Sheet, Clause, Page)."""

    id: str
    title: str
    locator: str
    content: str = ""
    chunks: list[KnowledgeChunk] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# ======================================================================
# Enterprise Governance, Risk & Internal Control Models
# ======================================================================


@dataclass
class RiskScore5x5:
    """Enterprise Risk Management (ISO 31000 / COSO ERM) 5x5 Likelihood x Impact scoring."""

    likelihood: int = 3  # 1 to 5
    impact: int = 3  # 1 to 5
    control_effectiveness: float = 0.5  # 0.0 (None) to 1.0 (Flawless)

    @property
    def inherent_score(self) -> int:
        return self.likelihood * self.impact

    @property
    def residual_score(self) -> float:
        eff = max(0.0, min(1.0, self.control_effectiveness))
        return round(self.inherent_score * (1.0 - (eff * 0.7)), 1)

    @property
    def heatmap_zone(self) -> str:
        score = self.residual_score
        if score >= 15.0:
            return "critical_red"
        elif score >= 10.0:
            return "high_amber"
        elif score >= 5.0:
            return "medium_yellow"
        else:
            return "low_green"

    def to_dict(self) -> dict[str, Any]:
        return {
            "likelihood": self.likelihood,
            "impact": self.impact,
            "inherent_score": self.inherent_score,
            "control_effectiveness": self.control_effectiveness,
            "residual_score": self.residual_score,
            "heatmap_zone": self.heatmap_zone,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RiskScore5x5:
        return cls(
            likelihood=int(data.get("likelihood", 3)),
            impact=int(data.get("impact", 3)),
            control_effectiveness=float(data.get("control_effectiveness", 0.5)),
        )


@dataclass
class SoDConflict:
    """Segregation of Duties (SoD) violation across business processes."""

    conflict_id: str
    individual_name: str
    role_a: str
    role_b: str
    document_refs: list[str] = field(default_factory=list)
    risk_explanation: str = ""
    recommendation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "individual_name": self.individual_name,
            "role_a": self.role_a,
            "role_b": self.role_b,
            "document_refs": self.document_refs,
            "risk_explanation": self.risk_explanation,
            "recommendation": self.recommendation,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SoDConflict:
        return cls(
            conflict_id=str(data.get("conflict_id", "")),
            individual_name=str(data.get("individual_name", "")),
            role_a=str(data.get("role_a", "")),
            role_b=str(data.get("role_b", "")),
            document_refs=list(data.get("document_refs", [])),
            risk_explanation=str(data.get("risk_explanation", "")),
            recommendation=str(data.get("recommendation", "")),
        )


@dataclass
class DoAViolation:
    """Delegation of Authority (DoA) limit exceedance or improper authorization."""

    violation_id: str
    approver_name: str
    approver_title: str
    transaction_amount: float
    authorized_limit: float
    document_ref: str
    notes: str = ""

    @property
    def excess_amount(self) -> float:
        return max(0.0, self.transaction_amount - self.authorized_limit)

    def to_dict(self) -> dict[str, Any]:
        return {
            "violation_id": self.violation_id,
            "approver_name": self.approver_name,
            "approver_title": self.approver_title,
            "transaction_amount": self.transaction_amount,
            "authorized_limit": self.authorized_limit,
            "excess_amount": self.excess_amount,
            "document_ref": self.document_ref,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DoAViolation:
        return cls(
            violation_id=str(data.get("violation_id", "")),
            approver_name=str(data.get("approver_name", "")),
            approver_title=str(data.get("approver_title", "")),
            transaction_amount=float(data.get("transaction_amount", 0.0)),
            authorized_limit=float(data.get("authorized_limit", 0.0)),
            document_ref=str(data.get("document_ref", "")),
            notes=str(data.get("notes", "")),
        )


@dataclass
class ControlEvaluation:
    """COSO Internal Control testing row (Test of Design & Test of Operating Effectiveness)."""

    control_id: str
    coso_component: str  # e.g., "Control Activities", "Control Environment"
    control_title: str
    control_nature: str = "preventive"  # preventive, detective, corrective
    control_type: str = "manual"  # manual, automated, it_dependent_manual
    design_effectiveness: AuditStatus = AuditStatus.PASS
    operating_effectiveness: AuditStatus = AuditStatus.PASS
    deficiency_level: str = "None"  # None, Control Deficiency, Significant Deficiency, Material Weakness
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "control_id": self.control_id,
            "coso_component": self.coso_component,
            "control_title": self.control_title,
            "control_nature": self.control_nature,
            "control_type": self.control_type,
            "design_effectiveness": self.design_effectiveness.value,
            "operating_effectiveness": self.operating_effectiveness.value,
            "deficiency_level": self.deficiency_level,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ControlEvaluation:
        return cls(
            control_id=str(data.get("control_id", "")),
            coso_component=str(data.get("coso_component", "")),
            control_title=str(data.get("control_title", "")),
            control_nature=str(data.get("control_nature", "preventive")),
            control_type=str(data.get("control_type", "manual")),
            design_effectiveness=AuditStatus(data.get("design_effectiveness", "pass")),
            operating_effectiveness=AuditStatus(data.get("operating_effectiveness", "pass")),
            deficiency_level=str(data.get("deficiency_level", "None")),
            notes=str(data.get("notes", "")),
        )


# ======================================================================
# REA-Inspired Audit Ledger Models (Unknowns, Obligations, Bundle, Sign-Off)
# ======================================================================


@dataclass
class UnknownItem:
    """Audit Inquiries & Unknowns Ledger (inspired by REA unknowns protocol).

    Captures open questions, missing documentation, and evidentiary ambiguities.
    An audit cannot be marked clean without resolving or formally waiving unknowns.
    """

    id: str
    question: str
    category: str = "General"  # Financial, Documentary, Legal, Compliance, Technical
    status: UnknownStatus = UnknownStatus.OPEN
    impact: str = ""
    evidence_required: str = ""
    resolution_notes: str = ""
    resolved_by: str = ""
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "question": self.question,
            "category": self.category,
            "status": self.status.value,
            "impact": self.impact,
            "evidence_required": self.evidence_required,
            "resolution_notes": self.resolution_notes,
            "resolved_by": self.resolved_by,
            "evidence_ref": self.evidence_ref,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UnknownItem:
        return cls(
            id=str(data.get("id", "")),
            question=str(data.get("question", "")),
            category=str(data.get("category", "General")),
            status=UnknownStatus(data.get("status", "open")),
            impact=str(data.get("impact", "")),
            evidence_required=str(data.get("evidence_required", "")),
            resolution_notes=str(data.get("resolution_notes", "")),
            resolved_by=str(data.get("resolved_by", "")),
            evidence_ref=str(data.get("evidence_ref", "")),
        )


@dataclass
class AuditObligation:
    """Mandatory Audit Obligation / Criteria Ledger.

    Tracks required audit tests and compliance standards across the engagement.
    """

    id: str
    title: str
    standard_ref: str
    status: str = "satisfied"  # satisfied, violated, partial, untested
    coverage_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "standard_ref": self.standard_ref,
            "status": self.status,
            "coverage_notes": self.coverage_notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuditObligation:
        return cls(
            id=str(data.get("id", "")),
            title=str(data.get("title", "")),
            standard_ref=str(data.get("standard_ref", "")),
            status=str(data.get("status", "satisfied")),
            coverage_notes=str(data.get("coverage_notes", "")),
        )


@dataclass
class EvidenceBundleManifest:
    """Cryptographic Evidence Bundle Manifest (inspired by REA evidence bundles).

    Contains cryptographic SHA-256 digests and provenance metadata of all audited artifacts.
    """

    bundle_id: str
    created_at: str
    files: list[dict[str, Any]] = field(default_factory=list)
    total_files: int = 0
    integrity_status: str = "verified_intact"  # verified_intact, compromised

    def to_dict(self) -> dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "created_at": self.created_at,
            "files": self.files,
            "total_files": self.total_files,
            "integrity_status": self.integrity_status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvidenceBundleManifest:
        return cls(
            bundle_id=str(data.get("bundle_id", "")),
            created_at=str(data.get("created_at", "")),
            files=list(data.get("files", [])),
            total_files=int(data.get("total_files", 0)),
            integrity_status=str(data.get("integrity_status", "verified_intact")),
        )


@dataclass
class HumanSignOff:
    """Formal Human Auditor Sign-Off and Professional Judgement Opinion."""

    reviewer_name: str = ""
    reviewer_role: str = ""
    reviewer_license_or_nip: str = ""
    audit_opinion: str = "WTP (Wajar Tanpa Pengecualian)"  # WTP, WDP, Tidak Wajar, Disclaimer
    signed_at: str = ""
    comments: str = ""
    is_signed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "reviewer_name": self.reviewer_name,
            "reviewer_role": self.reviewer_role,
            "reviewer_license_or_nip": self.reviewer_license_or_nip,
            "audit_opinion": self.audit_opinion,
            "signed_at": self.signed_at,
            "comments": self.comments,
            "is_signed": self.is_signed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HumanSignOff:
        return cls(
            reviewer_name=str(data.get("reviewer_name", "")),
            reviewer_role=str(data.get("reviewer_role", "")),
            reviewer_license_or_nip=str(data.get("reviewer_license_or_nip", "")),
            audit_opinion=str(data.get("audit_opinion", "WTP (Wajar Tanpa Pengecualian)")),
            signed_at=str(data.get("signed_at", "")),
            comments=str(data.get("comments", "")),
            is_signed=bool(data.get("is_signed", False)),
        )


@dataclass
class TerrainProfile:
    """Multi-terrain domain classification and framework detection."""

    primary_domain: str = "general"
    detected_domains: list[str] = field(default_factory=list)
    confidence: float = 1.0
    detected_regulations: list[str] = field(default_factory=list)
    key_entities: list[str] = field(default_factory=list)
    recommended_checks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "primary_domain": self.primary_domain,
            "detected_domains": self.detected_domains,
            "confidence": round(self.confidence, 2),
            "detected_regulations": self.detected_regulations,
            "key_entities": self.key_entities,
            "recommended_checks": self.recommended_checks,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TerrainProfile:
        return cls(
            primary_domain=str(data.get("primary_domain", "general")),
            detected_domains=list(data.get("detected_domains", [])),
            confidence=float(data.get("confidence", 1.0)),
            detected_regulations=list(data.get("detected_regulations", [])),
            key_entities=list(data.get("key_entities", [])),
            recommended_checks=list(data.get("recommended_checks", [])),
        )


@dataclass
class BenfordDigitStat:
    """Statistical deviation of a single leading digit in Benford analysis."""

    digit: int
    actual_count: int
    actual_pct: float
    expected_pct: float
    diff_pct: float
    z_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "digit": self.digit,
            "actual_count": self.actual_count,
            "actual_pct": round(self.actual_pct, 2),
            "expected_pct": round(self.expected_pct, 2),
            "diff_pct": round(self.diff_pct, 2),
            "z_score": round(self.z_score, 2),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BenfordDigitStat:
        return cls(
            digit=int(data.get("digit", 0)),
            actual_count=int(data.get("actual_count", 0)),
            actual_pct=float(data.get("actual_pct", 0.0)),
            expected_pct=float(data.get("expected_pct", 0.0)),
            diff_pct=float(data.get("diff_pct", 0.0)),
            z_score=float(data.get("z_score", 0.0)),
        )


@dataclass
class BenfordAnalysisResult:
    """Forensic Benford's Law distribution analysis across extracted numeric figures."""

    total_numbers: int = 0
    analyzed_digits: int = 0
    conformity_status: str = "acceptable"  # close, acceptable, marginally_acceptable, non_conforming
    mad_score: float = 0.0  # Mean Absolute Deviation
    chi_square: float = 0.0
    critical_anomalies: list[int] = field(default_factory=list)
    digit_distribution: list[BenfordDigitStat] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_numbers": self.total_numbers,
            "analyzed_digits": self.analyzed_digits,
            "conformity_status": self.conformity_status,
            "mad_score": round(self.mad_score, 4),
            "chi_square": round(self.chi_square, 2),
            "critical_anomalies": self.critical_anomalies,
            "digit_distribution": [d.to_dict() for d in self.digit_distribution],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BenfordAnalysisResult:
        return cls(
            total_numbers=int(data.get("total_numbers", 0)),
            analyzed_digits=int(data.get("analyzed_digits", 0)),
            conformity_status=str(data.get("conformity_status", "acceptable")),
            mad_score=float(data.get("mad_score", 0.0)),
            chi_square=float(data.get("chi_square", 0.0)),
            critical_anomalies=list(data.get("critical_anomalies", [])),
            digit_distribution=[BenfordDigitStat.from_dict(d) for d in data.get("digit_distribution", [])],
        )


# ======================================================================
# Findings & Audit Records (5C Standard)
# ======================================================================


@dataclass
class Finding5C:
    """Standard 5C Audit Finding structure (Condition, Criteria, Cause, Consequence, Correction)."""

    id: str
    title: str
    risk_level: RiskLevel
    category: str
    condition: str
    criteria: str
    cause: str
    consequence: str
    recommendation: str
    evidence: list[EvidenceCitation] = field(default_factory=list)
    management_response: str = ""
    remediation_deadline_days: int = 30
    tags: list[str] = field(default_factory=list)
    risk_score: RiskScore5x5 | None = None
    coso_component: str = ""
    business_process: str = ""
    human_status: str = "pending"  # pending, approved, rejected, adjusted
    human_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "title": self.title,
            "risk_level": self.risk_level.value,
            "category": self.category,
            "condition": self.condition,
            "criteria": self.criteria,
            "cause": self.cause,
            "consequence": self.consequence,
            "recommendation": self.recommendation,
            "evidence": [e.to_dict() for e in self.evidence],
            "management_response": self.management_response,
            "remediation_deadline_days": self.remediation_deadline_days,
            "tags": self.tags,
            "coso_component": self.coso_component,
            "business_process": self.business_process,
            "human_status": self.human_status,
            "human_notes": self.human_notes,
        }
        if self.risk_score:
            d["risk_score"] = self.risk_score.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Finding5C:
        f = cls(
            id=str(data.get("id", "")),
            title=str(data.get("title", "")),
            risk_level=RiskLevel(data.get("risk_level", "medium")),
            category=str(data.get("category", "General")),
            condition=str(data.get("condition", "")),
            criteria=str(data.get("criteria", "")),
            cause=str(data.get("cause", "")),
            consequence=str(data.get("consequence", "")),
            recommendation=str(data.get("recommendation", "")),
            evidence=[EvidenceCitation.from_dict(e) for e in data.get("evidence", [])],
            management_response=str(data.get("management_response", "")),
            remediation_deadline_days=int(data.get("remediation_deadline_days", 30)),
            tags=list(data.get("tags", [])),
            coso_component=str(data.get("coso_component", "")),
            business_process=str(data.get("business_process", "")),
            human_status=str(data.get("human_status", "pending")),
            human_notes=str(data.get("human_notes", "")),
        )
        if data.get("risk_score"):
            f.risk_score = RiskScore5x5.from_dict(data["risk_score"])
        return f


@dataclass
class WorkingPaperRow:
    """Kertas Kerja Audit (KKA) / Audit Working Paper entry."""

    ref_no: str
    procedure: str
    document_ref: str
    test_performed: str
    result: AuditStatus
    notes: str
    evidence: list[EvidenceCitation] = field(default_factory=list)
    finding_ref: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "ref_no": self.ref_no,
            "procedure": self.procedure,
            "document_ref": self.document_ref,
            "test_performed": self.test_performed,
            "result": self.result.value,
            "notes": self.notes,
            "evidence": [e.to_dict() for e in self.evidence],
        }
        if self.finding_ref:
            d["finding_ref"] = self.finding_ref
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkingPaperRow:
        return cls(
            ref_no=str(data.get("ref_no", "")),
            procedure=str(data.get("procedure", "")),
            document_ref=str(data.get("document_ref", "")),
            test_performed=str(data.get("test_performed", "")),
            result=AuditStatus(data.get("result", "pass")),
            notes=str(data.get("notes", "")),
            evidence=[EvidenceCitation.from_dict(e) for e in data.get("evidence", [])],
            finding_ref=data.get("finding_ref"),
        )


@dataclass
class ReconciliationItem:
    """Cross-document reconciliation item (e.g. 3-Way Matching)."""

    item_description: str
    doc_values: dict[str, Any]  # e.g., {'Contract': 50000000, 'Invoice': 55000000}
    status: AuditStatus
    discrepancy_amount: float | None = None
    discrepancy_details: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "item_description": self.item_description,
            "doc_values": self.doc_values,
            "status": self.status.value,
            "discrepancy_details": self.discrepancy_details,
        }
        if self.discrepancy_amount is not None:
            d["discrepancy_amount"] = self.discrepancy_amount
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReconciliationItem:
        return cls(
            item_description=str(data.get("item_description", "")),
            doc_values=dict(data.get("doc_values", {})),
            status=AuditStatus(data.get("status", "pass")),
            discrepancy_amount=data.get("discrepancy_amount"),
            discrepancy_details=str(data.get("discrepancy_details", "")),
        )


# ======================================================================
# Ingested Document Models
# ======================================================================


@dataclass
class AuditDocument:
    """Representation of an ingested document or audit evidence file."""

    name: str
    path: str
    doc_type: DocType
    role_in_dossier: str = "general"
    total_pages_or_sheets: int = 1
    content: str = ""
    entities: dict[str, Any] = field(default_factory=dict)
    chunks: list[KnowledgeChunk] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "doc_type": self.doc_type.value,
            "role_in_dossier": self.role_in_dossier,
            "total_pages_or_sheets": self.total_pages_or_sheets,
            "content": self.content,
            "entities": self.entities,
            "chunks_count": len(self.chunks),
            "content_length": len(self.content),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuditDocument:
        return cls(
            name=str(data.get("name", "")),
            path=str(data.get("path", "")),
            doc_type=DocType(data.get("doc_type", "text")),
            role_in_dossier=str(data.get("role_in_dossier", "general")),
            total_pages_or_sheets=int(data.get("total_pages_or_sheets", 1)),
            content=str(data.get("content", "")),
            entities=dict(data.get("entities", {})),
            chunks=[KnowledgeChunk.from_dict(c) for c in data.get("chunks", [])],
        )


# ======================================================================
# Metrics & Complete Audit Pack
# ======================================================================


@dataclass
class AuditMetric:
    """Quantitative scoring & summary metrics of the audit."""

    total_documents: int = 0
    total_findings: int = 0
    findings_by_risk: dict[str, int] = field(default_factory=dict)
    compliance_score: float = 100.0  # Percentage (0 - 100)
    arithmetic_accuracy: float = 100.0  # Percentage (0 - 100)
    evidence_grounding_rate: float = 100.0  # Percentage of findings with verified source quotes

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_documents": self.total_documents,
            "total_findings": self.total_findings,
            "findings_by_risk": self.findings_by_risk,
            "compliance_score": round(self.compliance_score, 1),
            "arithmetic_accuracy": round(self.arithmetic_accuracy, 1),
            "evidence_grounding_rate": round(self.evidence_grounding_rate, 1),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuditMetric:
        return cls(
            total_documents=int(data.get("total_documents", 0)),
            total_findings=int(data.get("total_findings", 0)),
            findings_by_risk=dict(data.get("findings_by_risk", {})),
            compliance_score=float(data.get("compliance_score", 100.0)),
            arithmetic_accuracy=float(data.get("arithmetic_accuracy", 100.0)),
            evidence_grounding_rate=float(data.get("evidence_grounding_rate", 100.0)),
        )


@dataclass
class AuditPack:
    """The master deliverable: complete, standalone audit pack.

    Contains all documents, verified 5C findings, working papers (KKA),
    reconciliation matrices, metrics, and actionable remediation steps.
    """

    title: str
    audit_ref: str
    lead_auditor: str = "Skill-Audit System"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    domain: AuditDomain = AuditDomain.GENERAL
    executive_summary: str = ""
    scope: str = ""
    methodology: str = "Standard 5C Audit Methodology with 3-Way Reconciliation & Deterministic Evidence Grounding"
    documents: list[AuditDocument] = field(default_factory=list)
    findings: list[Finding5C] = field(default_factory=list)
    working_papers: list[WorkingPaperRow] = field(default_factory=list)
    reconciliations: list[ReconciliationItem] = field(default_factory=list)
    metrics: AuditMetric = field(default_factory=AuditMetric)
    action_plan: list[dict[str, Any]] = field(default_factory=list)
    sod_conflicts: list[SoDConflict] = field(default_factory=list)
    doa_violations: list[DoAViolation] = field(default_factory=list)
    control_evaluations: list[ControlEvaluation] = field(default_factory=list)
    risk_heatmap: dict[str, Any] = field(default_factory=dict)
    governance_score: float = 100.0
    unknowns: list[UnknownItem] = field(default_factory=list)
    obligations: list[AuditObligation] = field(default_factory=list)
    evidence_bundle: dict[str, Any] = field(default_factory=dict)
    human_sign_off: HumanSignOff = field(default_factory=HumanSignOff)
    terrain_profile: TerrainProfile = field(default_factory=TerrainProfile)
    benford_analysis: BenfordAnalysisResult = field(default_factory=BenfordAnalysisResult)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "audit_ref": self.audit_ref,
            "lead_auditor": self.lead_auditor,
            "created_at": self.created_at,
            "domain": self.domain.value,
            "executive_summary": self.executive_summary,
            "scope": self.scope,
            "methodology": self.methodology,
            "documents": [doc.to_dict() for doc in self.documents],
            "findings": [f.to_dict() for f in self.findings],
            "working_papers": [w.to_dict() for w in self.working_papers],
            "reconciliations": [r.to_dict() for r in self.reconciliations],
            "metrics": self.metrics.to_dict(),
            "action_plan": self.action_plan,
            "sod_conflicts": [s.to_dict() for s in self.sod_conflicts],
            "doa_violations": [d.to_dict() for d in self.doa_violations],
            "control_evaluations": [c.to_dict() for c in self.control_evaluations],
            "risk_heatmap": self.risk_heatmap,
            "governance_score": round(self.governance_score, 1),
            "unknowns": [u.to_dict() for u in self.unknowns],
            "obligations": [o.to_dict() for o in self.obligations],
            "evidence_bundle": self.evidence_bundle,
            "human_sign_off": self.human_sign_off.to_dict(),
            "terrain_profile": self.terrain_profile.to_dict(),
            "benford_analysis": self.benford_analysis.to_dict(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuditPack:
        pack = cls(
            title=str(data.get("title", "Untitled Audit")),
            audit_ref=str(data.get("audit_ref", "AUD-001")),
            lead_auditor=str(data.get("lead_auditor", "Skill-Audit")),
            created_at=str(data.get("created_at", datetime.now(timezone.utc).isoformat())),
            domain=AuditDomain(data.get("domain", "general")),
            executive_summary=str(data.get("executive_summary", "")),
            scope=str(data.get("scope", "")),
            methodology=str(data.get("methodology", "")),
            documents=[AuditDocument.from_dict(d) for d in data.get("documents", [])],
            findings=[Finding5C.from_dict(f) for f in data.get("findings", [])],
            working_papers=[WorkingPaperRow.from_dict(w) for w in data.get("working_papers", [])],
            reconciliations=[ReconciliationItem.from_dict(r) for r in data.get("reconciliations", [])],
            metrics=AuditMetric.from_dict(data.get("metrics", {})),
            action_plan=list(data.get("action_plan", [])),
            sod_conflicts=[SoDConflict.from_dict(s) for s in data.get("sod_conflicts", [])],
            doa_violations=[DoAViolation.from_dict(d) for d in data.get("doa_violations", [])],
            control_evaluations=[ControlEvaluation.from_dict(c) for c in data.get("control_evaluations", [])],
            risk_heatmap=dict(data.get("risk_heatmap", {})),
            governance_score=float(data.get("governance_score", 100.0)),
            unknowns=[UnknownItem.from_dict(u) for u in data.get("unknowns", [])],
            obligations=[AuditObligation.from_dict(o) for o in data.get("obligations", [])],
            evidence_bundle=dict(data.get("evidence_bundle", {})),
            human_sign_off=HumanSignOff.from_dict(data.get("human_sign_off", {})),
            terrain_profile=TerrainProfile.from_dict(data.get("terrain_profile", {})),
            benford_analysis=BenfordAnalysisResult.from_dict(data.get("benford_analysis", {})),
            metadata=dict(data.get("metadata", {})),
        )
        return pack

    def to_yaml(self, path: str | Path | None = None) -> str:
        """Serialize pack to YAML string, optionally writing to file."""
        dumped = yaml.safe_dump(self.to_dict(), sort_keys=False, allow_unicode=True)
        if path:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(dumped, encoding="utf-8")
        return dumped

    @classmethod
    def from_yaml(cls, source: str | Path) -> AuditPack:
        """Load AuditPack from YAML file or raw string."""
        if isinstance(source, Path) or (isinstance(source, str) and "\n" not in source and Path(source).exists()):
            content = Path(source).read_text(encoding="utf-8")
        else:
            content = source
        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            raise ValueError("YAML content does not represent a valid AuditPack dictionary.")
        return cls.from_dict(data)

    def to_json(self, path: str | Path | None = None, indent: int = 2) -> str:
        """Serialize pack to JSON string, optionally writing to file."""
        dumped = json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
        if path:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(dumped, encoding="utf-8")
        return dumped

    @classmethod
    def from_json(cls, source: str | Path) -> AuditPack:
        """Load AuditPack from JSON file or raw string."""
        if isinstance(source, Path) or (isinstance(source, str) and "\n" not in source and Path(source).exists()):
            content = Path(source).read_text(encoding="utf-8")
        else:
            content = source
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError("JSON content does not represent a valid AuditPack dictionary.")
        return cls.from_dict(data)
