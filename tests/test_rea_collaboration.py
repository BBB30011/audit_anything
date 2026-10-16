"""Tests for REA architecture integration & Human-AI Collaboration:
1. Evidence Bundle & Forensic SHA-256 integrity verification
2. Unknowns & Inquiries Ledger (identifying gaps, resolving unknowns)
3. Audit Obligations & Standards Coverage evaluation
4. Human Sign-Off and Professional Judgement Opinion
5. REA CLI commands: unknowns, resolve-unknown, obligations, bundle, verify-bundle, signoff
"""

from pathlib import Path
from click.testing import CliRunner

from skill_audit.analyzers.obligation_engine import ObligationEngine
from skill_audit.analyzers.unknowns_engine import UnknownsEngine
from skill_audit.cli import cli
from skill_audit.engine import AuditEngine
from skill_audit.evidence_bundle import (
    create_evidence_bundle,
    export_evidence_bundle_zip,
    verify_evidence_bundle,
)
from skill_audit.models import (
    AuditDocument,
    DocType,
    Finding5C,
    HumanSignOff,
    RiskLevel,
    UnknownItem,
    UnknownStatus,
)


def test_evidence_bundle_creation_and_tamper_detection(tmp_path):
    doc1 = AuditDocument(name="SPK.txt", path="SPK.txt", doc_type=DocType.TEXT, content="Kontrak Pengadaan Server senilai Rp 50.000.000")
    doc2 = AuditDocument(name="BAST.txt", path="BAST.txt", doc_type=DocType.TEXT, content="Serah terima barang telah selesai 100%")

    manifest = create_evidence_bundle([doc1, doc2], "EVD-TEST-01")
    assert manifest.bundle_id == "EVD-TEST-01"
    assert manifest.total_files == 2
    assert manifest.integrity_status == "verified_intact"

    # Verify against intact documents
    res_intact = verify_evidence_bundle(manifest, [doc1, doc2])
    assert res_intact["verified_intact"] is True
    assert res_intact["tampered_count"] == 0

    # Modify doc1 content to simulate tampering
    tampered_doc1 = AuditDocument(name="SPK.txt", path="SPK.txt", doc_type=DocType.TEXT, content="Kontrak Pengadaan Server senilai Rp 999.000.000 (ALTERED!)")
    res_tampered = verify_evidence_bundle(manifest, [tampered_doc1, doc2])
    assert res_tampered["verified_intact"] is False
    assert res_tampered["tampered_count"] == 1


def test_unknowns_engine_gap_detection():
    # Only invoice, missing bank payment proof
    doc_inv = AuditDocument(
        name="Invoice.txt",
        path="Invoice.txt",
        doc_type=DocType.TEXT,
        role_in_dossier="invoice",
        content="Tagihan termin 1 sebesar Rp 50.000.000",
    )
    engine = UnknownsEngine()
    unknowns = engine.analyze([doc_inv], [])

    assert len(unknowns) >= 1
    # Check that missing payment unknown was logged
    assert any("dilunasi" in u.question or "kas/bank" in u.question for u in unknowns)

    # Test resolving the unknown
    target_u = unknowns[0]
    engine.resolve_unknown(
        target_u,
        notes="Telah diverifikasi terhadap rekening koran Bank Mandiri tanggal 25 Sept 2024",
        resolved_by="Senior Auditor",
        evidence_ref="Rekening_Koran_Sept2024.pdf",
    )
    assert target_u.status == UnknownStatus.RESOLVED
    assert "Bank Mandiri" in target_u.resolution_notes


def test_obligation_engine_coverage():
    docs = [
        AuditDocument(name="SPK.txt", path="SPK.txt", doc_type=DocType.TEXT, role_in_dossier="contract", content="SPK Pengadaan"),
        AuditDocument(name="BAST.txt", path="BAST.txt", doc_type=DocType.TEXT, role_in_dossier="goods_receipt", content="BAST Penerimaan"),
        AuditDocument(name="INV.txt", path="INV.txt", doc_type=DocType.TEXT, role_in_dossier="invoice", content="Invoice Tagihan"),
    ]
    findings = [
        Finding5C(
            id="FND-001",
            title="Ketiadaan Bea Meterai",
            risk_level=RiskLevel.MEDIUM,
            category="Compliance",
            condition="Meterai belum lunas",
            criteria="UU Bea Meterai",
            cause="Kelalaian",
            consequence="Denda",
            recommendation="Lakukan pemeteraian kemudian",
            tags=["stamp_duty", "compliance"],
        )
    ]

    engine = ObligationEngine()
    obligations, cov_pct = engine.evaluate(docs, findings)

    assert len(obligations) == 7
    assert cov_pct == 100.0
    # OBL-03 (Bea Meterai) should be violated due to finding
    obl_meterai = next(o for o in obligations if o.id == "OBL-03")
    assert obl_meterai.status == "violated"


def test_cli_rea_commands(tmp_path):
    runner = CliRunner()
    out_dir = tmp_path / "rea_out"

    # 1. Run dossier audit
    res_audit = runner.invoke(
        cli, ["dossier", "examples/procurement_dossier", "-f", "all", "-o", str(out_dir)]
    )
    assert res_audit.exit_code == 0

    pack_files = list(out_dir.glob("*_pack.yaml"))
    assert len(pack_files) > 0
    pack_path = str(pack_files[0])

    # 2. Inspect unknowns
    res_unk = runner.invoke(cli, ["unknowns", pack_path])
    assert res_unk.exit_code == 0
    assert "Ledger of Unknowns" in res_unk.output or "Inquiry" in res_unk.output

    # 3. Resolve an unknown
    res_resolve = runner.invoke(cli, [
        "resolve-unknown",
        pack_path,
        "--id", "UNK-01",
        "--notes", "Klarifikasi lisan dan rekening koran terkonfirmasi klir.",
        "--evidence", "Rekening_Koran_Mandiri.pdf",
    ])
    assert res_resolve.exit_code == 0
    assert "Berhasil menyelesaikan UNK-01" in res_resolve.output

    # 4. Inspect obligations
    res_obl = runner.invoke(cli, ["obligations", pack_path])
    assert res_obl.exit_code == 0
    assert "Kewajiban Audit" in res_obl.output

    # 5. Export and verify evidence bundle
    bundle_zip = out_dir / "test_bundle.zip"
    res_bundle = runner.invoke(cli, ["bundle", pack_path, "-o", str(bundle_zip)])
    assert res_bundle.exit_code == 0
    assert bundle_zip.exists()

    res_verify_b = runner.invoke(cli, ["verify-bundle", pack_path])
    assert res_verify_b.exit_code == 0
    assert "VERIFIED_INTACT" in res_verify_b.output

    # 6. Formal human sign-off
    res_sign = runner.invoke(cli, [
        "signoff",
        pack_path,
        "--name", "Drs. Hendro Wibowo, Ak., CA, CPA",
        "--role", "Audit Partner",
        "--nip", "CPA-ID-998822",
        "--opinion", "WDP (Wajar Dengan Pengecualian)",
        "--notes", "Opini WDP diterbitkan karena ketiadaan pakta integritas rekanan.",
    ])
    assert res_sign.exit_code == 0
    assert "Berhasil mengesahkan AuditPack" in res_sign.output
