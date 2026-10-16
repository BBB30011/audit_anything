"""Evidence grounding and entity extraction helpers for Skill-Audit.

Audit findings must be anchored by verifiable evidence. This module enforces
zero-hallucination trust boundaries: an evidence quote is valid only when it
can be found verbatim within the ingested source document chunks.
"""

from __future__ import annotations

import re
from typing import Any

from skill_audit.models import AuditDocument, EvidenceCitation, KnowledgeChunk


def normalize_evidence(text: str) -> str:
    """Normalize whitespace and formatting for robust quote verification."""
    return " ".join(str(text).split()).strip()


def verify_citation(
    documents: list[AuditDocument],
    excerpt: str,
    target_doc_name: str | None = None,
    min_length: int = 6,
    max_length: int = 600,
) -> EvidenceCitation | None:
    """Verify that an excerpt exists verbatim in the ingested audit documents.

    Returns an EvidenceCitation with document name, locator, and offset if verified,
    or None if the quote is absent (unsupported claim / hallucination).
    """
    if not isinstance(excerpt, str):
        return None

    clean_quote = normalize_evidence(excerpt)
    if len(clean_quote) < min_length or len(clean_quote) > max_length:
        return None

    target_docs = documents
    if target_doc_name:
        target_docs = [d for d in documents if d.name.lower() == target_doc_name.lower()] or documents

    quote_cf = clean_quote.casefold()

    for doc in target_docs:
        doc_normalized = normalize_evidence(doc.content)
        if quote_cf in doc_normalized.casefold():
            # Find specific chunk and locator
            matched_chunk: KnowledgeChunk | None = None
            for chunk in doc.chunks:
                chunk_normalized = normalize_evidence(chunk.content)
                if quote_cf in chunk_normalized.casefold():
                    matched_chunk = chunk
                    break

            locator = matched_chunk.locator if matched_chunk else "General"
            offset = doc.content.casefold().find(quote_cf[:40]) if len(quote_cf) >= 40 else None

            return EvidenceCitation(
                document=doc.name,
                locator=locator,
                excerpt=clean_quote,
                char_offset=offset if offset != -1 else None,
                confidence=1.0,
            )

    return None


def extract_key_entities(text: str) -> dict[str, Any]:
    """Extract standard audit entities from document text.

    Detects:
    - Monetary amounts (Rupiah, USD, generic currencies)
    - Dates (ISO, Indonesian format, English format)
    - Document reference numbers (SPK, PO, BAST, Invoice, Surat)
    - Tax numbers (NPWP / Tax ID)
    - Signatories, Approvals & Stamp markers
    """
    entities: dict[str, Any] = {
        "amounts": [],
        "dates": [],
        "doc_numbers": [],
        "tax_ids": [],
        "parties": [],
        "signatures_detected": [],
    }

    # 1. Amounts (e.g., Rp 150.000.000, Rp. 1.250.000,00, $50,000.00, IDR 75,000,000)
    amount_patterns = [
        r"(?:Rp\.?|IDR)\s*([0-9]{1,3}(?:\.[0-9]{3})+(?:,[0-9]{2})?)",
        r"(?:Rp\.?|IDR)\s*([0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{2})?)",
        r"\$\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)",
        r"(?:Total|Jumlah|Subtotal|Nilai|Tagihan)[:\s]+(?:Rp\.?|IDR)?\s*([0-9\.\,]+)",
    ]
    for pattern in amount_patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            raw_val = match.group(1).strip()
            # Parse numerical float
            cleaned = raw_val.replace(".", "").replace(",", ".") if "." in raw_val and "," in raw_val else raw_val
            # Handle Indonesian standard (dot as thousand separator)
            if "." in raw_val and "," not in raw_val:
                cleaned = raw_val.replace(".", "")
            elif "," in raw_val and "." not in raw_val:
                cleaned = raw_val.replace(",", "")
            try:
                num = float(cleaned)
                if num > 0 and num not in [a["value"] for a in entities["amounts"]]:
                    entities["amounts"].append({"raw": match.group(0).strip(), "value": num})
            except ValueError:
                pass

    # 2. Dates
    date_patterns = [
        # YYYY-MM-DD
        r"\b\d{4}-\d{2}-\d{2}\b",
        # DD/MM/YYYY or DD-MM-YYYY
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",
        # Indonesian textual date (e.g., 14 Oktober 2024, 05 Januari 2025)
        r"\b\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b",
    ]
    for pattern in date_patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            d_str = match.group(0).strip()
            if d_str not in entities["dates"]:
                entities["dates"].append(d_str)

    # 3. Document numbers
    doc_num_patterns = [
        r"(?:Nomor|No|Ref|Invoice|SPK|PO|BAST|Faktur)[\s.:]+([A-Z0-9\/\.\-_]{4,40})",
    ]
    for pattern in doc_num_patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            doc_no = match.group(1).strip().rstrip(".,;")
            if len(doc_no) >= 4 and doc_no not in entities["doc_numbers"]:
                entities["doc_numbers"].append(doc_no)

    # 4. Tax IDs (e.g., NPWP: 01.234.567.8-901.000)
    npwp_pattern = r"\b\d{2}\.\d{3}\.\d{3}\.\d{1}-\d{3}\.\d{3}\b"
    for match in re.finditer(npwp_pattern, text):
        val = match.group(0).strip()
        if val not in entities["tax_ids"]:
            entities["tax_ids"].append(val)

    # 5. Signatures, Stamped, Approved
    sig_patterns = [
        r"(?:Tanda Tangan|Ditandatangani oleh|Disetujui oleh|Mengetahui|Pemberi Tugas|Penerima Tugas|Pejabat Pembuat Komitmen|PPK|Direktur Utama|Manager Keuangan)[:\s]+([^\n\r,]{3,50})",
        r"(?:Meterai|Bea Meterai|Lunas|Cap Stempel)",
    ]
    for pattern in sig_patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            sig_txt = match.group(0).strip()
            if sig_txt not in entities["signatures_detected"]:
                entities["signatures_detected"].append(sig_txt)

    # 6. Corporate parties (PT, CV, Badan, Dinas, Yayasan)
    party_pattern = r"\b(?:PT\.?|CV\.?|Badan|Dinas|Kementerian|Yayasan)\s+[A-Za-z0-9\s.,&-]{3,40}"
    for match in re.finditer(party_pattern, text):
        party_name = normalize_evidence(match.group(0).strip()).rstrip(".,")
        if party_name not in entities["parties"]:
            entities["parties"].append(party_name)

    return entities


def split_into_audit_chunks(
    text: str,
    document_name: str,
    max_chunk_chars: int = 1200,
    overlap_chars: int = 150,
) -> list[KnowledgeChunk]:
    """Split long audit text into bounded KnowledgeChunks preserving line/section locators."""
    if not text.strip():
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text.strip()]

    chunks: list[KnowledgeChunk] = []
    current_content: list[str] = []
    current_len = 0
    chunk_idx = 0
    start_para_idx = 1

    for p_idx, para in enumerate(paragraphs, 1):
        p_len = len(para)
        if current_len + p_len > max_chunk_chars and current_content:
            chunk_text = "\n\n".join(current_content)
            locator = f"Paragraphs {start_para_idx}-{p_idx - 1}" if start_para_idx != p_idx - 1 else f"Paragraph {start_para_idx}"
            chunks.append(
                KnowledgeChunk(
                    content=chunk_text,
                    document_name=document_name,
                    locator=locator,
                    chunk_index=chunk_idx,
                    metadata={"para_start": start_para_idx, "para_end": p_idx - 1},
                )
            )
            chunk_idx += 1
            # Retain overlap if desired
            current_content = [para]
            current_len = p_len
            start_para_idx = p_idx
        else:
            current_content.append(para)
            current_len += p_len + 2

    if current_content:
        chunk_text = "\n\n".join(current_content)
        locator = f"Paragraphs {start_para_idx}-{len(paragraphs)}" if start_para_idx != len(paragraphs) else f"Paragraph {start_para_idx}"
        chunks.append(
            KnowledgeChunk(
                content=chunk_text,
                document_name=document_name,
                locator=locator,
                chunk_index=chunk_idx,
                metadata={"para_start": start_para_idx, "para_end": len(paragraphs)},
            )
        )

    return chunks
