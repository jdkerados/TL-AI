"""Manual provider: local YAML specification files. The only provider of Milestone M1."""

import logging
from collections.abc import Iterator

from tl_importer.models import EntityType, ImportContext, SourceDocument
from tl_importer.providers.base import ManualProvider

logger = logging.getLogger("tl_importer.manual")


class LocalManualProvider(ManualProvider):
    """Fetches specification documents from the local specifications/ tree."""

    @property
    def name(self) -> str:
        """Unique provider name."""
        return "manual"

    def supports(self, entity_type: EntityType) -> bool:
        """The manual provider supplies every entity type."""
        return True

    def fetch(self, context: ImportContext) -> Iterator[SourceDocument]:
        """Yield one document per YAML file under the specifications directory."""
        specs_dir = context.specs_dir
        for path in sorted(specs_dir.rglob("*.yaml")):
            relative = path.relative_to(specs_dir).as_posix()
            logger.debug("fetched document %s", relative)
            yield SourceDocument(
                provider=self.name,
                uri=relative,
                content_type="application/yaml",
                content=path.read_text(encoding="utf-8"),
            )
