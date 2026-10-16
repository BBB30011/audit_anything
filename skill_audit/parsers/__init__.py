"""Document parsers package for Skill-Audit."""

from __future__ import annotations

from pathlib import Path

from skill_audit.models import AuditDocument
from skill_audit.parsers.base import BaseParser
from skill_audit.parsers.docx_parser import DocxParser
from skill_audit.parsers.dossier_parser import DossierParser
from skill_audit.parsers.excel_parser import ExcelParser
from skill_audit.parsers.pdf_parser import PDFParser
from skill_audit.parsers.text_parser import TextParser

ALL_PARSERS: list[BaseParser] = [
    PDFParser(),
    ExcelParser(),
    DocxParser(),
    TextParser(),
]


def parse_path(path: str | Path) -> list[AuditDocument]:
    """Parse a single file or an entire directory/zip dossier into AuditDocuments."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Source path not found: {p}")

    dossier_parser = DossierParser()
    if dossier_parser.can_parse(p):
        return dossier_parser.parse(p)

    for parser in ALL_PARSERS:
        if parser.can_parse(p):
            doc = parser.parse(p)
            doc.role_in_dossier = DossierParser.classify_document_role(doc)
            return [doc]

    # Fallback to TextParser
    text_p = TextParser()
    doc = text_p.parse(p)
    doc.role_in_dossier = DossierParser.classify_document_role(doc)
    return [doc]


__all__ = [
    "BaseParser",
    "PDFParser",
    "ExcelParser",
    "DocxParser",
    "TextParser",
    "DossierParser",
    "parse_path",
]
