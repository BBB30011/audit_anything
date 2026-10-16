"""Tests for Skill-Audit core data models."""

import pytest
from skill_audit.models import (
    AuditDomain,
    AuditMetric,
    AuditPack,
    AuditStatus,
    EvidenceCitation,
    Finding5C,
    ReconciliationItem,
    RiskLevel,
    WorkingPaperRow,
)


def test_evidence_citation():
    ev = EvidenceCitation(
        document="SPK-001.txt",
        locator="Pasal 2",
        excerpt="Total nilai pekerjaan adalah Rp 45.000.000",
        char_offset=120,
    )
    d = ev.to_dict()
    assert d["document"] == "SPK-001.txt"
    assert d["locator"] == "Pasal 2"
    assert "Rp 45.000.000" in d["excerpt"]
    assert d["char_offset"] == 120

    ev2 = EvidenceCitation.from_dict(d)
    assert ev2.document == ev.document
    assert ev2.locator == ev.locator
    assert ev2.excerpt == ev.excerpt


def test_finding_5c_roundtrip():
    finding = Finding5C(
        id="FND-001",
        title="Salah Perhitungan Pajak PPN",
        risk_level=RiskLevel.HIGH,
        category="Aritmatika & Pajak",
        condition="PPN tercantum Rp 5.500.000 padahal DPP Rp 45.000.000",
        criteria="UU HPP Pasal 7 ayat (1) PPN 11%",
        cause="Formula manual keliru",
        consequence="Kelebihan tagihan senilai Rp 550.000",
        recommendation="Terbitkan nota koreksi",
        evidence=[
            EvidenceCitation(
                document="Invoice.txt",
                locator="Tabel Pajak",
                excerpt="PPN 11%: Rp 5.500.000",
            )
        ],
        tags=["tax", "ppn"],
    )

    d = finding.to_dict()
    assert d["id"] == "FND-001"
    assert d["risk_level"] == "high"
    assert len(d["evidence"]) == 1

    f2 = Finding5C.from_dict(d)
    assert f2.id == finding.id
    assert f2.title == finding.title
    assert f2.risk_level == RiskLevel.HIGH
    assert len(f2.evidence) == 1
    assert f2.evidence[0].document == "Invoice.txt"


def test_audit_pack_yaml_serialization(tmp_path):
    pack = AuditPack(
        title="Audit Pengadaan IT",
        audit_ref="AUD-IT-001",
        domain=AuditDomain.PROCUREMENT,
        executive_summary="Audit pengadaan telah selesai.",
        metrics=AuditMetric(total_documents=3, total_findings=1),
        findings=[
            Finding5C(
                id="FND-001",
                title="Temuan Uji",
                risk_level=RiskLevel.MEDIUM,
                category="General",
                condition="Kondisi uji",
                criteria="Kriteria uji",
                cause="Sebab uji",
                consequence="Akibat uji",
                recommendation="Rekomendasi uji",
            )
        ],
    )

    yaml_file = tmp_path / "test_pack.yaml"
    pack.to_yaml(yaml_file)
    assert yaml_file.exists()

    loaded = AuditPack.from_yaml(yaml_file)
    assert loaded.title == "Audit Pengadaan IT"
    assert loaded.audit_ref == "AUD-IT-001"
    assert len(loaded.findings) == 1
    assert loaded.findings[0].id == "FND-001"


def test_audit_pack_json_serialization(tmp_path):
    pack = AuditPack(
        title="Audit Finansial",
        audit_ref="AUD-FIN-002",
        domain=AuditDomain.FINANCIAL,
        executive_summary="Ringkasan eksekutif finansial.",
    )

    json_file = tmp_path / "test_pack.json"
    pack.to_json(json_file)
    assert json_file.exists()

    loaded = AuditPack.from_json(json_file)
    assert loaded.title == "Audit Finansial"
    assert loaded.audit_ref == "AUD-FIN-002"
