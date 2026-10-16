"""Tests for validation module and CI/CD strict gate."""

from skill_audit.models import AuditPack, EvidenceCitation, Finding5C, RiskLevel
from skill_audit.validation import validate_audit_pack


def test_validate_valid_pack():
    pack = AuditPack(
        title="Audit Uji Sah",
        audit_ref="AUD-VAL-01",
        executive_summary="Ringkasan valid.",
        findings=[
            Finding5C(
                id="FND-001",
                title="Temuan Sah",
                risk_level=RiskLevel.MEDIUM,
                category="Kepatuhan",
                condition="Kondisi riil ditemukan.",
                criteria="Standar SOP Bagian 3.",
                cause="Akar penyebab.",
                consequence="Dampak risiko finansial.",
                recommendation="Lakukan langkah perbaikan.",
                evidence=[EvidenceCitation(document="Doc1.txt", locator="Halaman 1", excerpt="Kutipan bukti")],
            )
        ],
    )

    report = validate_audit_pack(pack, strict=True)
    assert report.ok is True
    assert len(report.errors) == 0


def test_validate_strict_fails_on_uncited():
    pack = AuditPack(
        title="Audit Uji Tanpa Bukti",
        audit_ref="AUD-VAL-02",
        executive_summary="Ringkasan eksekutif.",
        findings=[
            Finding5C(
                id="FND-001",
                title="Klaim Tanpa Kutipan",
                risk_level=RiskLevel.HIGH,
                category="Uji",
                condition="Kondisi",
                criteria="Kriteria",
                cause="Sebab",
                consequence="Akibat",
                recommendation="Rekomendasi",
                evidence=[],  # No evidence!
            )
        ],
    )

    # In non-strict mode: warning
    report_soft = validate_audit_pack(pack, strict=False)
    assert report_soft.ok is True
    assert len(report_soft.warnings) >= 1

    # In strict mode: error (CI/CD gate fails!)
    report_strict = validate_audit_pack(pack, strict=True)
    assert report_strict.ok is False
    assert len(report_strict.errors) >= 1
    assert any("uncited" in err.code for err in report_strict.errors)
