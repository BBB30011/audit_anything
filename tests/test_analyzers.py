"""Tests for analyzers: MathChecker, CrossChecker, AnomalyDetector, ComplianceAnalyzer."""

from skill_audit.analyzers.anomaly import AnomalyDetector
from skill_audit.analyzers.compliance import ComplianceAnalyzer
from skill_audit.analyzers.cross_checker import CrossChecker
from skill_audit.analyzers.math_checker import MathChecker
from skill_audit.models import AuditDocument, DocType


def test_math_checker_calculation_error():
    content = "Rincian Barang:\n10 x Rp 50.000 = Rp 600.000"
    doc = AuditDocument(name="Invoice.txt", path="Invoice.txt", doc_type=DocType.TEXT, content=content)

    checker = MathChecker()
    findings = checker.analyze([doc])

    assert len(findings) >= 1
    f = findings[0]
    assert "FND-MATH" in f.id
    assert "600,000" in f.condition or "600.000" in f.condition
    assert "500,000" in f.condition or "500.000" in f.condition


def test_math_checker_tax_error():
    content = "Subtotal: Rp 100.000.000\nPPN 11%: Rp 15.000.000\nTotal: Rp 115.000.000"
    doc = AuditDocument(name="Invoice.txt", path="Invoice.txt", doc_type=DocType.TEXT, content=content)

    checker = MathChecker()
    findings = checker.analyze([doc])

    assert any("PPN" in f.title for f in findings)


def test_cross_checker_missing_bast():
    doc_inv = AuditDocument(
        name="Invoice.txt",
        path="Invoice.txt",
        doc_type=DocType.TEXT,
        role_in_dossier="invoice",
        content="Tagihan Invoice senilai Rp 50.000.000",
    )

    checker = CrossChecker()
    findings, reconciliations = checker.analyze([doc_inv])

    assert any("BAST" in f.title for f in findings)


def test_cross_checker_chronology_anomaly():
    doc_bast = AuditDocument(
        name="BAST.txt",
        path="BAST.txt",
        doc_type=DocType.TEXT,
        role_in_dossier="goods_receipt",
        content="Tanggal BAST: 25-09-2024. Telah diterima barang dengan baik.",
        entities={"dates": ["25-09-2024"]},
    )
    doc_inv = AuditDocument(
        name="Invoice.txt",
        path="Invoice.txt",
        doc_type=DocType.TEXT,
        role_in_dossier="invoice",
        content="Tanggal: 20-09-2024. Tagihan pengadaan.",
        entities={"dates": ["20-09-2024"]},
    )

    checker = CrossChecker()
    findings, _ = checker.analyze([doc_bast, doc_inv])

    assert any("Anomali Tanggal" in f.title for f in findings)


def test_anomaly_detector_missing_stamp():
    doc = AuditDocument(
        name="Kuitansi.txt",
        path="Kuitansi.txt",
        doc_type=DocType.TEXT,
        role_in_dossier="invoice",
        content="Total Pembayaran: Rp 15.000.000 (tidak ada kata m-a-t-e-r-a-i).",
        entities={"amounts": [{"raw": "Rp 15.000.000", "value": 15000000.0}]},
    )

    detector = AnomalyDetector()
    findings = detector.analyze([doc])

    assert any("Meterai" in f.title for f in findings)


def test_compliance_analyzer_checklist():
    doc_contract = AuditDocument(
        name="Kontrak.txt",
        path="Kontrak.txt",
        doc_type=DocType.TEXT,
        role_in_dossier="contract",
        content="Surat Perintah Kerja (SPK). Denda keterlambatan 1/1000 per hari. Penyelesaian perselisihan di Pengadilan Negeri.",
    )

    analyzer = ComplianceAnalyzer()
    findings, papers, score = analyzer.analyze([doc_contract])

    assert len(papers) >= 4
    assert score > 0.0
