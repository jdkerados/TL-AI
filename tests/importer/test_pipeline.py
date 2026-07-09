"""Architecture tests: the pipeline orchestrates injected interface implementations."""

from collections.abc import Iterator, Sequence

from tl_importer.importers import EntityImporter
from tl_importer.models import (
    EntityType,
    ImportContext,
    ImportIssue,
    ImportJob,
    ImportStatus,
    NormalizedEntity,
    Rarity,
    RawEntity,
    Severity,
    SourceDocument,
    ValidationReport,
)
from tl_importer.normalizers import Normalizer
from tl_importer.parsers import Parser
from tl_importer.pipeline import ImportPipeline
from tl_importer.providers import ManualProvider
from tl_importer.validators import ImportValidator


class FakeProvider(ManualProvider):
    """Test double emitting one in-memory document."""

    @property
    def name(self) -> str:
        return "fake"

    def supports(self, entity_type: EntityType) -> bool:
        return True

    def fetch(self, context: ImportContext) -> Iterator[SourceDocument]:
        yield SourceDocument(
            provider=self.name, uri="doc://weapons", content_type="text/plain", content="two"
        )


class FakeParser(Parser):
    """Test double producing two raw weapons per document."""

    def can_parse(self, document: SourceDocument) -> bool:
        return document.content_type == "text/plain"

    def parse(self, document: SourceDocument, context: ImportContext) -> Iterator[RawEntity]:
        yield RawEntity(EntityType.WEAPON, document, {"name": "GoodSword"}, Rarity.EPIC)
        yield RawEntity(EntityType.WEAPON, document, {"name": "BadSword"}, Rarity.HEROIC)


class FakeNormalizer(Normalizer):
    """Test double producing canonical entities."""

    @property
    def entity_type(self) -> EntityType:
        return EntityType.WEAPON

    def normalize(self, raw: RawEntity, context: ImportContext) -> NormalizedEntity:
        name = str(raw.data["name"])
        return NormalizedEntity(
            stable_id=f"tl.weapon.{name.lower()}",
            entity_type=raw.entity_type,
            rarity=raw.rarity or Rarity.EPIC,
            name=name,
            payload=dict(raw.data),
            references=(),
            source=raw.source,
        )


class FakeValidator(ImportValidator):
    """Test double rejecting entities named BadSword."""

    def validate(self, entity: NormalizedEntity, context: ImportContext) -> ValidationReport:
        report = ValidationReport(stable_id=entity.stable_id)
        if entity.name == "BadSword":
            report.issues.append(
                ImportIssue(Severity.ERROR, "BAD_NAME", entity.stable_id, "rejected")
            )
        return report


class FakeImporter(EntityImporter):
    """Test double recording persisted entities."""

    def __init__(self) -> None:
        self.persisted: list[NormalizedEntity] = []

    def persist(self, entities: Sequence[NormalizedEntity], context: ImportContext) -> int:
        self.persisted.extend(entities)
        return len(entities)


def _pipeline(importer: FakeImporter) -> ImportPipeline:
    return ImportPipeline(
        provider=FakeProvider(),
        parser=FakeParser(),
        normalizer=FakeNormalizer(),
        validator=FakeValidator(),
        importer=importer,
    )


def _context(*, dry_run: bool) -> ImportContext:
    job = ImportJob(provider="fake", entity_types=(EntityType.WEAPON,))
    return ImportContext(job=job, dry_run=dry_run)


def test_pipeline_runs_all_stages() -> None:
    importer = FakeImporter()
    result = _pipeline(importer).run(_context(dry_run=False))
    assert result.documents_fetched == 1
    assert result.raw_entities == 2
    assert result.normalized_entities == 2
    assert result.valid_entities == 1
    assert result.imported_entities == 1
    assert [entity.name for entity in importer.persisted] == ["GoodSword"]
    assert result.status is ImportStatus.PARTIAL
    assert result.finished_at is not None


def test_pipeline_dry_run_does_not_persist() -> None:
    importer = FakeImporter()
    result = _pipeline(importer).run(_context(dry_run=True))
    assert result.valid_entities == 1
    assert result.imported_entities == 0
    assert importer.persisted == []


def test_pipeline_reports_are_collected() -> None:
    result = _pipeline(FakeImporter()).run(_context(dry_run=True))
    assert len(result.reports) == 2
    assert sum(1 for report in result.reports if not report.is_valid) == 1
