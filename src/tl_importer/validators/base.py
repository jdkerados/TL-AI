"""Validator interface: NormalizedEntity -> ValidationReport."""

from abc import ABC, abstractmethod

from tl_importer.models import ImportContext, NormalizedEntity, ValidationReport


class ImportValidator(ABC):
    """Interface of every import validator."""

    @abstractmethod
    def validate(self, entity: NormalizedEntity, context: ImportContext) -> ValidationReport:
        """Validate a normalized entity before it is staged."""
