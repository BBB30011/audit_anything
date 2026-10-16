"""Parser for PDF audit documents using pypdf."""

from __future__ import annotations

from pathlib import Path

from skill_audit.grounding import extract_key_entities
from skill_audit.models import AuditDocument, DocType, KnowledgeChunk
from skill_audit.parsers.base import BaseParser


class PDFParser(BaseParser):
    """Extracts text and page-by-page structure from PDF files."""

    def can_parse(self, path: Path) -> bool:
        return path.suffix.lower() == ".pdf"

    def parse(self, path: Path) -> AuditDocument:
        import pypdf

        reader = pypdf.PdfReader(str(path))
        page_count = len(reader.pages)

        page_texts: list[str] = []
        chunks: list[KnowledgeChunk] = []

        for idx, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                page_texts.append(f"--- [Halaman {idx}] ---\n{text}")
                chunks.append(
                    KnowledgeChunk(
                        content=text,
                        document_name=path.name,
                        locator=f"Halaman {idx}",
                        chunk_index=idx - 1,
                        metadata={"page": idx, "page_count": page_count},
                    )
                )

        full_content = "\n\n".join(page_texts)
        entities = extract_key_entities(full_content)

        return AuditDocument(
            name=path.name,
            path=str(path.resolve()),
            doc_type=DocType.PDF,
            total_pages_or_sheets=page_count,
            content=full_content,
            entities=entities,
            chunks=chunks,
        )
