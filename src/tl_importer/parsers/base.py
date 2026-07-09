"""Parser interface: SourceDocument -> RawEntity."""

from abc import ABC, abstractmethod
from collections.abc import Iterator

from tl_importer.models import ImportContext, RawEntity, SourceDocument


class Parser(ABC):
    """Interface of every source document parser."""

    @abstractmethod
    def can_parse(self, document: SourceDocument) -> bool:
        """Whether this parser understands the given document."""

    @abstractmethod
    def parse(self, document: SourceDocument, context: ImportContext) -> Iterator[RawEntity]:
        """Extract raw entities from the document."""
