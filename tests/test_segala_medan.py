"""Unit tests for Universal Multi-Terrain (Segala Medan) Auditing capabilities.

Tests:
- DomainTerrainDetector (Healthcare, Government, HR, Financial, Procurement)
- BenfordForensicAnalyzer (Nigrini 2012 MAD, Chi-Square, Z-Score, Anomaly Findings)
- Domain Terrain Profiles & Knowledge Base
- Domain-Adaptive Obligations & Unknowns
- CLI commands (audit, terrain, benford, profiles)
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest
from click.testing import CliRunner

from skill_audit.analyzers.benford_analyzer import BenfordForensicAnalyzer
from skill_audit.analyzers.obligation_engine import ObligationEngine
from skill_audit.analyzers.terrain_detector import DomainTerrainDetector
from skill_audit.analyzers.unknowns_engine import UnknownsEngine
from skill_audit.cli import cli
from skill_audit.engine import AuditEngine
from skill_audit.knowledge.domain_profiles import (
    DOMAIN_TERRAIN_PROFILES,
    get_terrain_profile,
    list_all_terrains,
)
from skill_audit.models import (
    AuditDocument,
    AuditDomain,
    AuditPack,
    DocType,
    Finding5C,
    RiskLevel,
)


def test_domain_profiles_completeness() -> None:
    """Verify that all 12+ audit terrains are properly defined with statutory rules."""
    terrains = list_all_terrains()
    assert len(terrains) >= 10

    domains_checked = [
        AuditDomain.FINANCIAL,
        AuditDomain.PROCUREMENT,
        AuditDomain.GOVERNMENT,
        AuditDomain.HEALTHCARE,
        AuditDomain.HR_PAYROLL,
        AuditDomain.SUPPLY_CHAIN,
        AuditDomain.FORENSIC_FRAUD,
        AuditDomain.IT_SECURITY,
        AuditDomain.TAX_CUSTOMS,
        AuditDomain.BANKING_FINTECH,
        AuditDomain.ESG_SUSTAINABILITY,
    ]

    for d in domains_checked:
        prog = get_terrain_profile(d)
        assert prog is not None
        assert prog.domain == d
        assert len(prog.statutory_references) > 0
        assert len(prog.mandatory_obligations) > 0
        assert len(prog.key_red_flags) > 0


def test_terrain_detector_healthcare() -> None:
    """Verify classification of healthcare hospital billing and clinical records."""
    doc = AuditDocument(
        name="Klaim_Rawat_Inap_Pasien_RSUD.txt",
        path="tests/fixtures/Klaim_Rawat_Inap_Pasien_RSUD.txt",
        doc_type=DocType.TEXT,
        content=(
            "RUMAH SAKIT UMUM DAERAH (RSUD) DR. SOETOMO\n"
            "Resume Medis Rawat Inap & Rincian Klaim BPJS Kesehatan\n"
            "Nama Pasien: Tn. Suparman | DPJP: dr. Hendra, Sp.B\n"
            "Diagnosa Utama: Appendicitis Akut (ICD-10 K35.8)\n"
            "Tindakan Bedah: Appendectomy (ICD-9-CM 47.0)\n"
            "Tarif INA-CBG: Rp 14.500.000\n"
            "Rincian Farmasi: Obat antibiotik dan analgesik resep dokter."
        ),
    )
    detector = DomainTerrainDetector()
    profile = detector.detect([doc])
    assert profile.primary_domain == "healthcare"
    assert "healthcare" in profile.detected_domains
    assert any("Permenkes" in reg or "Kesehatan" in reg or "Bpjs" in reg for reg in profile.detected_regulations) or len(profile.recommended_checks) > 0


def test_terrain_detector_government() -> None:
    """Verify classification of public sector government budget and SP2D records."""
    doc = AuditDocument(
        name="SP2D_Realisasi_Belanja_Modal_DPA.txt",
        path="tests/fixtures/SP2D.txt",
        doc_type=DocType.TEXT,
        content=(
            "PEMERINTAH KOTA SURABAYA - BADAN PENGELOLAAN KEUANGAN DAN ASET DAERAH\n"
            "Surat Perintah Pencairan Dana (SP2D) Beban APBD TA 2026\n"
            "Kode Satker: 1.02.01.01 | Kuasa Pengguna Anggaran (KPA): Ir. Bambang\n"
            "Dasar SPM No: 0045/SPM-LS/2026 | DPA SKPD No: DPA/A.1/1.02/2026\n"
            "Uraian: Pembayaran Pembangunan Gedung Puskesmas tahap II sesuai BAP.\n"
            "Realisasi Belanja Modal: Rp 1.250.000.000"
        ),
    )
    detector = DomainTerrainDetector()
    profile = detector.detect([doc])
    assert profile.primary_domain == "government"
    assert "government" in profile.detected_domains


def test_benford_analyzer_natural_distribution() -> None:
    """Verify Benford analyzer evaluates naturally distributed numbers correctly."""
    # Generate 100 numbers approximately conforming to Benford's first-digit distribution
    # 30 starting with 1, 18 with 2, 12 with 3, 10 with 4, 8 with 5, 7 with 6, 6 with 7, 5 with 8, 4 with 9
    sample_amounts = []
    distribution_counts = {1: 30, 2: 18, 3: 12, 4: 10, 5: 8, 6: 7, 7: 6, 8: 5, 9: 4}
    for digit, count in distribution_counts.items():
        for i in range(count):
            sample_amounts.append(float(digit * 1000 + i * 15))

    doc = AuditDocument(
        name="Laporan_Transaksi_Keuangan.txt",
        path="tests/fixtures/trans.txt",
        doc_type=DocType.TEXT,
        content="Transaksi: " + ", ".join(f"Rp {a:,.0f}" for a in sample_amounts),
        entities={"amounts": [{"value": a} for a in sample_amounts]},
    )

    analyzer = BenfordForensicAnalyzer(min_sample_size=15)
    result, findings = analyzer.analyze([doc])

    assert result.analyzed_digits == 100
    assert result.conformity_status in ["close_conformity", "acceptable_conformity"]
    assert result.mad_score < 0.012
    assert len(findings) == 0  # No anomaly finding because data is natural


def test_benford_analyzer_anomalous_fabrication() -> None:
    """Verify Benford analyzer flags human fabricated numbers (e.g., all starting with 7)."""
    # 30 numbers all starting with digit 7 (classic fraud / fabricated vouchers)
    sample_amounts = [float(7000 + i * 25) for i in range(30)]

    doc = AuditDocument(
        name="Voucher_Kas_Mencurigakan.txt",
        path="tests/fixtures/voucher.txt",
        doc_type=DocType.TEXT,
        content="Voucher: " + ", ".join(f"Rp {a:,.0f}" for a in sample_amounts),
        entities={"amounts": [{"value": a} for a in sample_amounts]},
    )

    analyzer = BenfordForensicAnalyzer(min_sample_size=15)
    result, findings = analyzer.analyze([doc])

    assert result.analyzed_digits == 30
    assert result.conformity_status == "non_conforming"
    assert result.mad_score > 0.015
    assert 7 in result.critical_anomalies
    assert len(findings) == 1
    assert "FND-BNF-001" in findings[0].id
    assert "Digit 7" in findings[0].title or "7" in findings[0].condition


def test_domain_adaptive_obligations_and_unknowns() -> None:
    """Verify ObligationEngine and UnknownsEngine dynamically adapt to terrain."""
    doc = AuditDocument(
        name="Rincian_Klaim_RSUD.txt",
        path="tests/fixtures/rsud.txt",
        doc_type=DocType.TEXT,
        content="Rumah Sakit Pasien Rawat Inap Billing BPJS Kesehatan",
        role_in_dossier="invoice",
    )

    # Test Obligation Engine with HEALTHCARE domain
    obl_engine = ObligationEngine()
    obligations, coverage = obl_engine.evaluate([doc], [], domain=AuditDomain.HEALTHCARE)
    obl_ids = [o.id for o in obligations]
    assert "OBL-HLT-001" in obl_ids
    assert "OBL-HLT-002" in obl_ids

    # Test Unknowns Engine with HEALTHCARE domain (missing resume medis)
    unk_engine = UnknownsEngine()
    unknowns = unk_engine.analyze([doc], [], domain=AuditDomain.HEALTHCARE)
    assert any("Resume Medis" in u.question for u in unknowns)


def test_universal_cli_commands(tmp_path: Path) -> None:
    """Test skillaudit CLI commands: profiles, terrain, benford, and audit."""
    runner = CliRunner()

    # 1. Test profiles
    res_prof = runner.invoke(cli, ["profiles"])
    assert res_prof.exit_code == 0
    assert "HEALTHCARE" in res_prof.output
    assert "GOVERNMENT" in res_prof.output

    # 2. Test terrain on procurement sample
    res_terrain = runner.invoke(cli, ["terrain", "examples/procurement_dossier"])
    assert res_terrain.exit_code == 0
    assert "PROCUREMENT" in res_terrain.output

    # 3. Test universal audit command
    out_dir = str(tmp_path / "universal_audit_out")
    res_audit = runner.invoke(cli, ["audit", "examples/procurement_dossier", "-o", out_dir, "-f", "pack"])
    assert res_audit.exit_code == 0
    assert "Audit Berkas Procurement Dossier" in res_audit.output

    # 4. Test benford on generated pack
    pack_file = next(Path(out_dir).glob("*.yaml"))
    res_bnf = runner.invoke(cli, ["benford", str(pack_file)])
    assert res_bnf.exit_code == 0
    assert "Benford's Law" in res_bnf.output
