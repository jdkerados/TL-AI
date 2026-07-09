"""Normalizer interface: RawEntity -> NormalizedEntity."""

from abc import ABC, abstractmethod

from tl_importer.models import EntityType, ImportContext, NormalizedEntity, RawEntity


class Normalizer(ABC):
    """Interface of every entity normalizer."""

    @property
    @abstractmethod
    def entity_type(self) -> EntityType:
        """The entity type this normalizer produces."""

    @abstractmethod
    def normalize(self, raw: RawEntity, context: ImportContext) -> NormalizedEntity:
        """Transform a provider-specific raw entity into canonical TL-AI shape."""
