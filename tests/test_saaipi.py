"""Unit tests for PER-01/AAIPI/DPN/2021 SAAIPI Standards Integration."""

from __future__ import annotations

import json
from pathlib import Path
from click.testing import CliRunner

from skill_audit.analyzers.obligation_engine import ObligationEngine
from skill_audit.analyzers.unknowns_engine import UnknownsEngine
from skill_audit.cli import cli
from skill_audit.knowledge.saaipi_standards import (
    SAAIPI_ETHICS_REGISTRY,
    SAAIPI_MANDATORY_OBLIGATIONS,
    SAAIPI_STANDARDS_REGISTRY,
    SAAIPIComplianceReport,
    SAAIPIEthicsPrinciple,
    evaluate_saaipi_compliance,
)
from skill_audit.models import (
    AuditDocument,
    AuditDomain,
    AuditMetric,
    AuditPack,
    DocType,
    EvidenceCitation,
    Finding5C,
    RiskLevel,
    WorkingPaperRow,
    AuditStatus,
)


def test_saaipi_registries() -> None:
    """Verify SAAIPI ethics principles and standards 1000-2500 codification."""
    # 6 Principles of Ethics
    assert len(SAAIPI_ETHICS_REGISTRY) == 6
    assert SAAIPIEthicsPrinciple.INTEGRITAS in SAAIPI_ETHICS_REGISTRY
    assert SAAIPIEthicsPrinciple.OBJEKTIVITAS in SAAIPI_ETHICS_REGISTRY
    assert SAAIPIEthicsPrinciple.KERAHASIAAN in SAAIPI_ETHICS_REGISTRY
    assert SAAIPIEthicsPrinciple.KOMPETENSI in SAAIPI_ETHICS_REGISTRY
    assert SAAIPIEthicsPrinciple.AKUNTABILITAS in SAAIPI_ETHICS_REGISTRY
    assert SAAIPIEthicsPrinciple.PERILAKU_PROFESIONAL in SAAIPI_ETHICS_REGISTRY

    # 10 Standards (Attribute 1000-1300, Performance 2000-2500)
    assert len(SAAIPI_STANDARDS_REGISTRY) == 10
    codes = [s.code for s in SAAIPI_STANDARDS_REGISTRY]
    assert "SAAIPI-1000" in codes  # Piagam Audit & Surat Tugas
    assert "SAAIPI-1100" in codes  # Independensi & Objektivitas
    assert "SAAIPI-1200" in codes  # Due Professional Care
    assert "SAAIPI-1300" in codes  # QAIP
    assert "SAAIPI-2000" in codes  # PKPT Berbasis Risiko
    assert "SAAIPI-2100" in codes  # GRC & SPIP
    assert "SAAIPI-2200" in codes  # Perencanaan & PKP
    assert "SAAIPI-2300" in codes  # Bukti Memadai & KKA
    assert "SAAIPI-2400" in codes  # LHA 5C
    assert "SAAIPI-2500" in codes  # TLRHP Monitoring

    # Mandatory Obligations
    assert len(SAAIPI_MANDATORY_OBLIGATIONS) == 7
    obl_codes = [o["code"] for o in SAAIPI_MANDATORY_OBLIGATIONS]
    assert "OBL-SAAIPI-1000" in obl_codes
    assert "OBL-SAAIPI-2500" in obl_codes


def test_evaluate_saaipi_compliance_full() -> None:
    """Test SAAIPI evaluation logic on a compliant pack."""
    doc = AuditDocument(
        name="surat_tugas_apip_dan_dpa.txt",
        path="surat_tugas_apip_dan_dpa.txt",
        doc_type=DocType.TEXT,
        role_in_dossier="surat_tugas",
        content=(
            "Surat Tugas Resmi Inspektorat Nomor ST-101/ITDA/2026. "
            "Piagam Audit Intern berlaku. Pakta Integritas bebas benturan kepentingan ditandatangani. "
            "Realisasi DPA Nomor 900/DPA-SKPD/2026. Tindak lanjut rekomendasi TLRHP."
        ),
    )
    citation = EvidenceCitation(
        document="surat_tugas_apip_dan_dpa.txt",
        locator="Baris 1",
        excerpt="Surat Tugas Resmi Inspektorat Nomor ST-101/ITDA/2026",
    )
    finding = Finding5C(
        id="FND-001",
        title="Kelebihan Pembayaran Uang Muka Tanpa Jaminan Pengembalian",
        risk_level=RiskLevel.HIGH,
        category="Public Sector Compliance",
        condition="Pembayaran uang muka sebesar Rp 50.000.000 dilakukan tanpa jaminan uang muka bank.",
        criteria="PER-01/AAIPI/DPN/2021 dan Perpres 16/2018 Pasal 61.",
        cause="Pejabat Pembuat Komitmen tidak memverifikasi keaslian surat jaminan.",
        consequence="Potensi kerugian keuangan daerah sebesar Rp 50.000.000 apabila penyedia wanprestasi.",
        recommendation="Menginstruksikan PPK menarik jaminan bank sah atau memotong pembayaran termin berikutnya.",
        evidence=[citation],
        management_response="PPK menerima temuan dan akan menagih jaminan bank dalam waktu 7 hari kerja.",
        remediation_deadline_days=14,
    )
    wp = WorkingPaperRow(
        ref_no="KKA-A.01",
        procedure="Uji keabsahan jaminan uang muka",
        document_ref="surat_tugas_apip_dan_dpa.txt",
        test_performed="Pemeriksaan fisik dokumen garansi bank",
        result=AuditStatus.FAIL,
        notes="Tidak ditemukan jaminan bank asli",
        evidence=[citation],
    )
    pack = AuditPack(
        title="Audit Kepatuhan Pelaksanaan Anggaran Dinas PU",
        audit_ref="AUD-APIP-001",
        domain=AuditDomain.GOVERNMENT,
        documents=[doc],
        findings=[finding],
        working_papers=[wp],
        action_plan=[{"action": "Penagihan jaminan uang muka", "deadline": "14 hari", "pic": "PPK"}],
    )

    report = evaluate_saaipi_compliance(pack)
    assert isinstance(report, SAAIPIComplianceReport)
    assert report.legal_basis == "Peraturan AAIPI Nomor: PER-01/AAIPI/DPN/2021"
    assert report.overall_compliance_score >= 85.0
    assert report.attribute_standards_score >= 80.0
    assert report.performance_standards_score >= 80.0
    assert report.five_c_rigor_score == 100.0
    assert "MEMENUHI STANDAR SAAIPI" in report.summary_verdict

    # Check AuditPack helper method
    helper_report = pack.get_saaipi_report()
    assert helper_report.overall_compliance_score == report.overall_compliance_score


def test_saaipi_obligations_in_engine() -> None:
    """Test that ObligationEngine evaluates SAAIPI obligations for government terrain."""
    doc = AuditDocument(
        name="dpa_dan_sp2d.txt",
        path="dpa_dan_sp2d.txt",
        doc_type=DocType.TEXT,
        content="Pengawasan APIP BPKP sesuai SAAIPI. Realisasi belanja DPA dan penerbitan SP2D.",
    )
    engine = ObligationEngine()
    obligations, coverage = engine.evaluate([doc], findings=[], domain=AuditDomain.GOVERNMENT)

    obl_ids = [o.id for o in obligations]
    assert "OBL-SAAIPI-1000" in obl_ids
    assert "OBL-SAAIPI-1100" in obl_ids
    assert "OBL-SAAIPI-1200" in obl_ids
    assert "OBL-SAAIPI-2300" in obl_ids
    assert "OBL-SAAIPI-2400" in obl_ids
    assert "OBL-SAAIPI-2500" in obl_ids
    assert coverage == 100.0


def test_saaipi_unknowns_in_engine() -> None:
    """Test that UnknownsEngine flags missing Surat Tugas APIP and missing TLRHP."""
    # Document has APIP keyword but no Surat Tugas or TLRHP
    doc = AuditDocument(
        name="laporan_realisasi_apbd.txt",
        path="laporan_realisasi_apbd.txt",
        doc_type=DocType.TEXT,
        content="Pengawasan APIP atas belanja modal peralatan mesin APBD 2026. LHA diterbitkan BPKP.",
    )
    engine = UnknownsEngine()
    unknowns = engine.analyze([doc], findings=[], domain=AuditDomain.GOVERNMENT)

    categories = [u.category for u in unknowns]
    assert "SAAIPI APIP Mandate" in categories
    assert "SAAIPI TLRHP Compliance" in categories


def test_cli_saaipi_command(tmp_path: Path) -> None:
    """Test Click CLI command 'skillaudit saaipi' with both table and JSON output."""
    runner = CliRunner()

    # Create dummy government dossier
    doc_file = tmp_path / "berkas_apip.txt"
    doc_file.write_text(
        "Inspektorat Daerah Provinsi. Surat Tugas ST-099/2026. Realisasi SP2D belanja barang APBD. SAAIPI compliance.",
        encoding="utf-8",
    )

    # Run CLI command
    result = runner.invoke(cli, ["saaipi", str(doc_file)])
    assert result.exit_code == 0
    assert "Evaluasi Kepatuhan SAAIPI" in result.output
    assert "PER-01/AAIPI/DPN/2021" in result.output
    assert "SAAIPI-1000" in result.output
    assert "SAAIPI-2500" in result.output

    # Run with --json
    result_json = runner.invoke(cli, ["saaipi", str(doc_file), "--json"])
    assert result_json.exit_code == 0
    data = json.loads(result_json.output)
    assert data["legal_basis"] == "Peraturan AAIPI Nomor: PER-01/AAIPI/DPN/2021"
    assert "overall_compliance_score" in data
    assert len(data["evaluations"]) == 10
