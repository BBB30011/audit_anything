"""Base parser interface for audit documents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from skill_audit.models import AuditDocument, DocType


class BaseParser(ABC):
    """Abstract interface for all document parsers."""

    @abstractmethod
    def can_parse(self, path: Path) -> bool:
        """Check if this parser can handle the given file."""
        pass

    @abstractmethod
    def parse(self, path: Path) -> AuditDocument:
        """Extract content, structure, and entities from file into an AuditDocument."""
        pass
