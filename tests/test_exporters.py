"""Tests for exporters: ReportExporter, WebExporter, CSVExporter, SkillExporter."""

from pathlib import Path

from skill_audit.exporters import (
    CSVExporter,
    ReportExporter,
    SkillExporter,
    WebExporter,
)
from skill_audit.models import AuditPack, EvidenceCitation, Finding5C, RiskLevel


def _make_dummy_pack() -> AuditPack:
    return AuditPack(
        title="Audit Pengadaan Komputer",
        audit_ref="AUD-PC-01",
        executive_summary="Ringkasan eksekutif pengadaan komputer.",
        findings=[
            Finding5C(
                id="FND-001",
                title="Keterlambatan Penyerahan Barang",
                risk_level=RiskLevel.MEDIUM,
                category="Klausul Kontrak",
                condition="Barang diserahkan terlambat 5 hari kalender.",
                criteria="Pasal 3 SPK: Batas waktu penyerahan 20 September.",
                cause="Kendala logistik vendor.",
                consequence="Keterlambatan operasional divisi TI.",
                recommendation="Kenakan denda keterlambatan 1/1000 per hari.",
                evidence=[EvidenceCitation(document="SPK.txt", locator="Pasal 3", excerpt="20 September")],
            )
        ],
    )


def test_report_exporter(tmp_path):
    pack = _make_dummy_pack()
    exp = ReportExporter()

    rep_file = tmp_path / "lha.md"
    rep_text = exp.export_report(pack, rep_file)
    assert rep_file.exists()
    assert "LAPORAN HASIL AUDIT" in rep_text
    assert "FND-001" in rep_text


def test_web_exporter(tmp_path):
    pack = _make_dummy_pack()
    exp = WebExporter()

    html_file = tmp_path / "dashboard.html"
    exp.export(pack, html_file)
    assert html_file.exists()
    content = html_file.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "Audit Pengadaan Komputer" in content
    assert "FND-001" in content


def test_csv_exporter(tmp_path):
    pack = _make_dummy_pack()
    exp = CSVExporter()

    csv_file = tmp_path / "findings.csv"
    exp.export_findings(pack, csv_file)
    assert csv_file.exists()
    content = csv_file.read_text(encoding="utf-8")
    assert "ID Temuan" in content
    assert "FND-001" in content


def test_skill_exporter(tmp_path):
    pack = _make_dummy_pack()
    exp = SkillExporter()

    skill_dir = exp.export(pack, tmp_path)
    assert skill_dir.exists()
    assert (skill_dir / "SKILL.md").exists()
    assert (skill_dir / "references").exists()
    assert (skill_dir / "assets" / "audit_pack.yaml").exists()
    assert (skill_dir / "scripts" / "run_audit.py").exists()
