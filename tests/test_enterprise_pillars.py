"""Tests for Enterprise Pillars:
1. Business Processes & Knowledge
2. Technical Audit & ITGC (SHA-256 integrity, audit trail)
3. Governance & DoA (Delegation of Authority, Anti-Bribery)
4. Internal Controls & SoD (COSO 2013 17 Principles, Segregation of Duties)
5. ISO 31000 ERM & 5x5 Risk Heatmap
"""

from pathlib import Path
from click.testing import CliRunner
from skill_audit.analyzers.governance_checker import GovernanceChecker
from skill_audit.analyzers.risk_engine import RiskEngine
from skill_audit.analyzers.sod_checker import SoDChecker
from skill_audit.cli import cli
from skill_audit.engine import AuditEngine
from skill_audit.knowledge.business_processes import BUSINESS_PROCESSES, get_process_info
from skill_audit.knowledge.governance import DEFAULT_DOA_MATRIX, GCG_PRINCIPLES, evaluate_doa_limit
from skill_audit.knowledge.internal_controls import COSO_17_PRINCIPLES, SOD_RULES
from skill_audit.knowledge.risk_management import (
    IMPACT_SCALE,
    LIKELIHOOD_SCALE,
    calculate_risk_profile,
    generate_heatmap_matrix,
)
from skill_audit.knowledge.technical_audit import ITGC_DOMAINS, compute_file_sha256, verify_audit_trail_integrity
from skill_audit.models import AuditDocument, DocType, Finding5C, RiskLevel, RiskScore5x5, SoDConflict


def test_business_processes_knowledge():
    assert "P2P" in BUSINESS_PROCESSES
    assert "O2C" in BUSINESS_PROCESSES
    assert "R2R" in BUSINESS_PROCESSES
    assert "H2R" in BUSINESS_PROCESSES

    p2p = get_process_info("P2P")
    assert p2p is not None
    assert "Procure-to-Pay" in p2p["name"]
    assert len(p2p["key_controls"]) >= 4


def test_technical_audit_sha256(tmp_path):
    test_file = tmp_path / "sample.txt"
    test_file.write_text("Audit Trail Line 1\nAudit Trail Line 2", encoding="utf-8")

    digest = compute_file_sha256(str(test_file))
    assert len(digest) == 64
    assert isinstance(digest, str)


def test_technical_audit_trail_integrity():
    events = [
        "2024-09-01T10:00:00 [USER:alice] CREATE_PO",
        "2024-09-01T11:00:00 [USER:bob] APPROVE_PO",
    ]
    is_valid, issues = verify_audit_trail_integrity(events)
    assert is_valid is True
    assert len(issues) == 0

    # Out of order timestamps
    bad_events = [
        "2024-09-01T12:00:00 [USER:alice] CREATE_PO",
        "2024-09-01T10:00:00 [USER:bob] APPROVE_PO",
    ]
    is_valid_bad, bad_issues = verify_audit_trail_integrity(bad_events)
    assert is_valid_bad is False
    assert len(bad_issues) > 0


def test_coso_and_sod_knowledge():
    assert len(COSO_17_PRINCIPLES) == 17
    assert len(SOD_RULES) >= 5
    assert any(rule["code"] == "SOD-01" for rule in SOD_RULES)


def test_sod_checker_conflict_detection():
    # Same person approves PO and signs goods receipt (BAST)
    doc_po = AuditDocument(
        name="PO-001.txt",
        path="PO-001.txt",
        doc_type=DocType.TEXT,
        role_in_dossier="purchase_order",
        content="Disetujui oleh: Budi Santoso\nJabatan: Pejabat Pengadaan (Buyer)",
        entities={"signatures": ["Budi Santoso"]},
    )
    doc_bast = AuditDocument(
        name="BAST-001.txt",
        path="BAST-001.txt",
        doc_type=DocType.TEXT,
        role_in_dossier="goods_receipt",
        content="Penerima: Budi Santoso\nSebagai: Tim Penerima Barang (Receiving BAST)",
        entities={"signatures": ["Budi Santoso"]},
    )

    checker = SoDChecker()
    findings, conflicts = checker.analyze([doc_po, doc_bast])

    assert len(conflicts) >= 1
    assert any("Budi Santoso" in c.individual_name for c in conflicts)
    assert any(f.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] for f in findings)


def test_governance_doa_limit_evaluation():
    # Department Manager limit is 100,000,000
    is_ok, limit, msg = evaluate_doa_limit(75_000_000.0, "Department Manager")
    assert is_ok is True
    assert limit == 100_000_000.0

    # Over limit
    is_ok_over, limit_over, msg_over = evaluate_doa_limit(150_000_000.0, "Department Manager")
    assert is_ok_over is False
    assert limit_over == 100_000_000.0


def test_governance_checker_violation():
    doc = AuditDocument(
        name="PO-HighValue.txt",
        path="PO-HighValue.txt",
        doc_type=DocType.TEXT,
        role_in_dossier="purchase_order",
        content="Total Nilai Pengadaan: Rp 150.000.000\nDisetujui oleh: Hendra Wijaya\nJabatan: Manager Operasional",
        entities={"amounts": [{"raw": "Rp 150.000.000", "value": 150_000_000.0}]},
    )

    checker = GovernanceChecker()
    findings, violations, gov_score = checker.analyze([doc])

    assert len(violations) >= 1
    v = violations[0]
    assert v.approver_name == "Hendra Wijaya"
    assert v.approver_title == "Manager Operasional"
    assert v.transaction_amount == 150_000_000.0
    assert any("DoA" in f.title or "Kewenangan" in f.title for f in findings)


def test_risk_management_5x5_scoring():
    # Likelihood 4 x Impact 5 with control effectiveness 0.5
    score = calculate_risk_profile(4, 5, control_effectiveness=0.5)
    assert score.inherent_score == 20
    assert score.residual_score == 13.0
    assert score.heatmap_zone == "high_amber"


def test_risk_heatmap_matrix_generation():
    findings = [
        Finding5C(
            id="FND-01",
            title="Finding High",
            risk_level=RiskLevel.HIGH,
            category="Operational",
            condition="Test cond",
            criteria="Test crit",
            cause="Test cause",
            consequence="Test cons",
            recommendation="Test corr",
            risk_score=RiskScore5x5(likelihood=4, impact=4, control_effectiveness=0.2),
        ),
        Finding5C(
            id="FND-02",
            title="Finding Low",
            risk_level=RiskLevel.LOW,
            category="Operational",
            condition="Test cond",
            criteria="Test crit",
            cause="Test cause",
            consequence="Test cons",
            recommendation="Test corr",
            risk_score=RiskScore5x5(likelihood=1, impact=2, control_effectiveness=0.8),
        ),
    ]

    heatmap = generate_heatmap_matrix(findings)
    assert len(heatmap["grid"]) == 25
    assert heatmap["total_assessed"] == 2
    assert "zone_counts" in heatmap


def test_risk_engine_enrichment():
    fnd = Finding5C(
        id="FND-TAX",
        title="Selisih Perhitungan PPN Faktur Pajak",
        risk_level=RiskLevel.MEDIUM,
        category="Taxation",
        condition="PPN tertera Rp 15.000.000",
        criteria="PPN 11%",
        cause="Kesalahan rumus hitung",
        consequence="Kekurangan bayar pajak",
        recommendation="Koreksi faktur pajak",
    )

    engine = RiskEngine()
    heatmap, control_evals = engine.evaluate_and_enrich([fnd])
    assert fnd.risk_score is not None
    assert fnd.risk_score.inherent_score > 0
    assert len(control_evals) == 1
    assert "grid" in heatmap


def test_dossier_engine_with_enterprise_pillars(tmp_path):
    # Test end-to-end engine execution on procurement dossier
    engine = AuditEngine(checklist_config="coso_internal_controls")
    pack = engine.audit(target_path="examples/procurement_dossier")

    assert len(pack.documents) >= 3
    assert len(pack.findings) >= 1
    assert pack.risk_heatmap is not None
    assert pack.governance_score >= 0.0
    assert isinstance(pack.sod_conflicts, list)
    assert isinstance(pack.doa_violations, list)


def test_cli_pillar_commands(tmp_path):
    runner = CliRunner()

    # Test framework list
    res_fw = runner.invoke(cli, ["framework", "list"])
    assert res_fw.exit_code == 0
    assert "COSO-2013" in res_fw.output
    assert "ISO-31000" in res_fw.output
    assert "ITGC" in res_fw.output

    # Test dossier audit producing pack
    out_dir = tmp_path / "out"
    res_dossier = runner.invoke(
        cli, ["dossier", "examples/procurement_dossier", "-f", "all", "-o", str(out_dir)]
    )
    assert res_dossier.exit_code == 0

    pack_files = list(out_dir.glob("*_pack.yaml"))
    assert len(pack_files) > 0
    pack_path = str(pack_files[0])

    # Test risk command
    res_risk = runner.invoke(cli, ["risk", pack_path])
    assert res_risk.exit_code == 0
    assert "ISO 31000" in res_risk.output or "Heatmap" in res_risk.output or "Matrix" in res_risk.output

    # Test sod command
    res_sod = runner.invoke(cli, ["sod", pack_path])
    assert res_sod.exit_code == 0

    # Test governance command
    res_gov = runner.invoke(cli, ["governance", pack_path])
    assert res_gov.exit_code == 0
    assert "Tata Kelola" in res_gov.output or "GCG" in res_gov.output

