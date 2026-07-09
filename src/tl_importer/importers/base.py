"""Importer interface: hands validated entities to the compiler/database stage."""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from tl_importer.models import ImportContext, NormalizedEntity


class EntityImporter(ABC):
    """Interface of the final pipeline stage.

    Implementations will stage validated entities as YAML specifications for the
    TL Compiler (AD-15/AD-21) and persist compiled results to the database.
    The runtime never reads YAML (AD-20).
    """

    @abstractmethod
    def persist(self, entities: Sequence[NormalizedEntity], context: ImportContext) -> int:
        """Persist validated entities. Returns the number of entities imported."""
