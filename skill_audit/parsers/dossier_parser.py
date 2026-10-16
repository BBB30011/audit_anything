"""Dossier and multi-document parser for comprehensive audit engagements."""

from __future__ import annotations

import re
import tempfile
import zipfile
from pathlib import Path
from typing import Callable

from skill_audit.models import AuditDocument, DocType
from skill_audit.parsers.docx_parser import DocxParser
from skill_audit.parsers.excel_parser import ExcelParser
from skill_audit.parsers.pdf_parser import PDFParser
from skill_audit.parsers.text_parser import TextParser


class DossierParser:
    """Parses an entire folder or ZIP archive of audit files and classifies their roles."""

    def __init__(self) -> None:
        self.parsers = [
            PDFParser(),
            ExcelParser(),
            DocxParser(),
            TextParser(),
        ]

    def can_parse(self, path: Path) -> bool:
        return path.is_dir() or path.suffix.lower() == ".zip"

    def parse(self, path: Path) -> list[AuditDocument]:
        """Parse directory or zip archive into a list of classified AuditDocuments."""
        target_dir = path
        temp_dir_obj = None

        if path.is_file() and path.suffix.lower() == ".zip":
            temp_dir_obj = tempfile.TemporaryDirectory(prefix="skillaudit_zip_")
            target_dir = Path(temp_dir_obj.name)
            with zipfile.ZipFile(str(path), "r") as z:
                z.extractall(target_dir)

        docs: list[AuditDocument] = []
        files = sorted([f for f in target_dir.rglob("*") if f.is_file() and not f.name.startswith((".", "~$"))])

        for file_path in files:
            doc = self._parse_single_file(file_path)
            if doc:
                doc.role_in_dossier = self.classify_document_role(doc)
                docs.append(doc)

        if temp_dir_obj:
            temp_dir_obj.cleanup()

        return docs

    def _parse_single_file(self, file_path: Path) -> AuditDocument | None:
        for parser in self.parsers:
            if parser.can_parse(file_path):
                try:
                    return parser.parse(file_path)
                except Exception as e:
                    # Return minimal fallback doc on parse failure
                    return AuditDocument(
                        name=file_path.name,
                        path=str(file_path.resolve()),
                        doc_type=DocType.TEXT,
                        content=f"[Error parsing file {file_path.name}: {e}]",
                    )
        return None

    @staticmethod
    def classify_document_role(doc: AuditDocument) -> str:
        """Classify document role based on filename and header semantics."""
        text = (doc.name + " " + doc.content[:1000]).lower()

        if any(k in text for k in ["spk", "kontrak", "perjanjian", "purchase order", " po ", "surat pesanan"]):
            return "contract"
        elif any(k in text for k in ["bast", "berita acara serah terima", "surat jalan", "delivery note", "goods receipt", "packing list"]):
            return "goods_receipt"
        elif any(k in text for k in ["invoice", "tagihan", "kwitansi", "billing"]):
            return "invoice"
        elif any(k in text for k in ["faktur pajak", "bukti potong", "pajak", "ppn", "pph", "tax invoice"]):
            return "tax_document"
        elif any(k in text for k in ["bukti transfer", "rekening koran", "bank statement", "payment proof", "kuitansi pembayaran"]):
            return "payment_proof"
        elif any(k in text for k in ["sop", "kebijakan", "policy", "pedoman", "standar", "peraturan", "uu ", "pp "]):
            return "policy"
        elif any(k in text for k in ["buku besar", "general ledger", "jurnal", "trial balance", "neraca", "kertas kerja"]):
            return "working_paper"

        return "general"
