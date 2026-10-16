"""Tests for Click CLI commands."""

from click.testing import CliRunner
from skill_audit.cli import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Skill-Audit" in result.output
    assert "doc" in result.output
    assert "dossier" in result.output
    assert "cross-check" in result.output
    assert "verify" in result.output


def test_cli_audit_doc(tmp_path):
    f = tmp_path / "test_doc.txt"
    f.write_text("SURAT PERINTAH KERJA No 01. Total: Rp 10.000.000. Denda: 1/1000.", encoding="utf-8")

    out_dir = tmp_path / "output"
    runner = CliRunner()
    result = runner.invoke(cli, ["doc", str(f), "-o", str(out_dir), "-f", "all"])

    assert result.exit_code == 0
    assert out_dir.exists()
    assert any(out_dir.glob("*_pack.yaml"))


def test_cli_audit_dossier():
    runner = CliRunner()
    result = runner.invoke(cli, ["dossier", "examples/procurement_dossier", "-f", "all"])
    assert result.exit_code == 0
    assert "Ringkasan Hasil Pemeriksaan Audit" in result.output


def test_cli_verify(tmp_path):
    runner = CliRunner()
    out_dir = tmp_path / "output_test"
    runner.invoke(cli, ["dossier", "examples/procurement_dossier", "-o", str(out_dir)])

    pack_files = list(out_dir.glob("*_pack.yaml"))
    assert len(pack_files) > 0
    res = runner.invoke(cli, ["verify", str(pack_files[0])])
    assert res.exit_code == 0

