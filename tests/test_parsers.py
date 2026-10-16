"""Tests for document parsers."""

from pathlib import Path

from skill_audit.parsers.dossier_parser import DossierParser
from skill_audit.parsers.excel_parser import ExcelParser
from skill_audit.parsers.text_parser import TextParser


def test_text_parser(tmp_path):
    f = tmp_path / "sample_sop.md"
    f.write_text("# SOP Pengeluaran Kas\nSetiap pengeluaran kas di atas Rp 1.000.000 harus disetujui Manager.", encoding="utf-8")

    parser = TextParser()
    assert parser.can_parse(f) is True

    doc = parser.parse(f)
    assert doc.name == "sample_sop.md"
    assert "SOP Pengeluaran Kas" in doc.content
    assert len(doc.chunks) >= 1
    assert any(a["value"] == 1000000.0 for a in doc.entities["amounts"])


def test_csv_parser(tmp_path):
    f = tmp_path / "kas.csv"
    f.write_text("No,Tanggal,Keterangan,Nilai\n1,2024-09-01,ATK,Rp 500.000\n2,2024-09-02,Sewa,Rp 2.000.000\n", encoding="utf-8")

    parser = ExcelParser()
    assert parser.can_parse(f) is True

    doc = parser.parse(f)
    assert doc.name == "kas.csv"
    assert "Baris 2:" in doc.content
    assert len(doc.chunks) >= 1


def test_dossier_parser_role_classification(tmp_path):
    f_spk = tmp_path / "01_SPK_Kontrak.txt"
    f_spk.write_text("SURAT PERINTAH KERJA No 01", encoding="utf-8")

    f_bast = tmp_path / "02_BAST_Serah_Terima.txt"
    f_bast.write_text("BERITA ACARA SERAH TERIMA", encoding="utf-8")

    f_inv = tmp_path / "03_Invoice_Tagihan.txt"
    f_inv.write_text("INVOICE TAGIHAN No 99", encoding="utf-8")

    parser = DossierParser()
    docs = parser.parse(tmp_path)

    roles = {d.name: d.role_in_dossier for d in docs}
    assert roles["01_SPK_Kontrak.txt"] == "contract"
    assert roles["02_BAST_Serah_Terima.txt"] == "goods_receipt"
    assert roles["03_Invoice_Tagihan.txt"] == "invoice"
