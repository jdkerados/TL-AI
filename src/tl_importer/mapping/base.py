"""Mapping interfaces: declarative field mappings from provider shape to canonical shape."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from tl_importer.models import EntityType, RawEntity


@dataclass(frozen=True)
class MappingRule:
    """One declarative field mapping from a provider field to a canonical field."""

    source_field: str
    target_field: str
    required: bool = False
    transform: str | None = None


class EntityMapper(ABC):
    """Interface of every entity field mapper."""

    @property
    @abstractmethod
    def entity_type(self) -> EntityType:
        """The entity type this mapper handles."""

    @property
    @abstractmethod
    def rules(self) -> tuple[MappingRule, ...]:
        """The declarative mapping rules of this mapper."""

    @abstractmethod
    def apply(self, raw: RawEntity) -> dict[str, Any]:
        """Apply the mapping rules to a raw entity, producing canonical fields."""
