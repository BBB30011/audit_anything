"""Parser for plain text, markdown, and structured text files."""

from __future__ import annotations

from pathlib import Path

from skill_audit.grounding import extract_key_entities, split_into_audit_chunks
from skill_audit.models import AuditDocument, DocType
from skill_audit.parsers.base import BaseParser


class TextParser(BaseParser):
    """Parses .txt, .md, .json, .yaml files into AuditDocument."""

    SUPPORTED_EXTS = {".txt", ".md", ".markdown", ".json", ".yaml", ".yml", ".log"}

    def can_parse(self, path: Path) -> bool:
        return path.suffix.lower() in self.SUPPORTED_EXTS

    def parse(self, path: Path) -> AuditDocument:
        content = path.read_text(encoding="utf-8", errors="replace")
        entities = extract_key_entities(content)
        chunks = split_into_audit_chunks(content, document_name=path.name)

        return AuditDocument(
            name=path.name,
            path=str(path.resolve()),
            doc_type=DocType.TEXT,
            total_pages_or_sheets=max(1, len(content) // 2000),
            content=content,
            entities=entities,
            chunks=chunks,
        )
