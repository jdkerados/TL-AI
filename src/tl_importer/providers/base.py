"""Provider interfaces. Providers fetch SourceDocuments; no fetching is implemented yet."""

from abc import ABC, abstractmethod
from collections.abc import Iterator

from tl_importer.models import EntityType, ImportContext, SourceDocument


class Provider(ABC):
    """Interface of every data source provider."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider name."""

    @abstractmethod
    def supports(self, entity_type: EntityType) -> bool:
        """Whether this provider can supply documents for the given entity type."""

    @abstractmethod
    def fetch(self, context: ImportContext) -> Iterator[SourceDocument]:
        """Fetch source documents for the job in the given context."""


class WikiProvider(Provider, ABC):
    """Interface for the Throne & Liberty wiki source."""


class QuestlogProvider(Provider, ABC):
    """Interface for the Questlog source."""


class MaxrollProvider(Provider, ABC):
    """Interface for the Maxroll source."""


class YoutubeProvider(Provider, ABC):
    """Interface for the YouTube source."""


class ManualProvider(Provider, ABC):
    """Interface for manually curated local documents."""
