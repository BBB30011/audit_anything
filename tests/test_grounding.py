"""Tests for grounding, citation verification, and entity extraction."""

from skill_audit.grounding import (
    extract_key_entities,
    normalize_evidence,
    split_into_audit_chunks,
    verify_citation,
)
from skill_audit.models import AuditDocument, DocType


def test_normalize_evidence():
    raw = "  Nilai   transaksi \n\n  adalah   Rp  10.000.000   "
    assert normalize_evidence(raw) == "Nilai transaksi adalah Rp 10.000.000"


def test_extract_key_entities():
    sample_text = """
    SURAT PERINTAH KERJA (SPK) Nomor: 042/SPK-TI/IX/2024
    Tanggal: 10 September 2024
    Pihak: PT Nusantara Jaya dan CV Mitra Teknologi
    NPWP: 02.456.789.1-012.000
    Total Nilai: Rp 45.000.000
    Disetujui oleh: Ir. Hendro Prabowo
    Meterai Tempel Rp 10.000
    """
    entities = extract_key_entities(sample_text)
    assert len(entities["amounts"]) >= 1
    assert any(a["value"] == 45000000.0 for a in entities["amounts"])
    assert "10 September 2024" in entities["dates"]
    assert "042/SPK-TI/IX/2024" in entities["doc_numbers"]
    assert "02.456.789.1-012.000" in entities["tax_ids"]
    assert any("Meterai" in s for s in entities["signatures_detected"])


def test_verify_citation_found():
    doc = AuditDocument(
        name="Kontrak.txt",
        path="/tmp/Kontrak.txt",
        doc_type=DocType.TEXT,
        content="Pasal 4: Denda keterlambatan sebesar 1/1000 untuk setiap hari keterlambatan.",
    )

    quote = "Denda keterlambatan sebesar 1/1000"
    citation = verify_citation([doc], quote)
    assert citation is not None
    assert citation.document == "Kontrak.txt"
    assert "1/1000" in citation.excerpt


def test_verify_citation_hallucination_rejected():
    doc = AuditDocument(
        name="Kontrak.txt",
        path="/tmp/Kontrak.txt",
        doc_type=DocType.TEXT,
        content="Pasal 4: Denda keterlambatan sebesar 1/1000.",
    )

    fake_quote = "Denda sebesar 50 persen dari nilai kontrak jika terjadi wanprestasi"
    citation = verify_citation([doc], fake_quote)
    assert citation is None
