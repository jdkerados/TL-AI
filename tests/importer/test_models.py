"""Architecture tests for the import framework data model."""

from tl_importer.models import (
    EntityType,
    ImportContext,
    ImportIssue,
    ImportJob,
    ImportResult,
    ImportStatus,
    NormalizedEntity,
    Rarity,
    RawEntity,
    Severity,
    SourceDocument,
    ValidationReport,
)


def test_supported_entity_types() -> None:
    assert {entity_type.value for entity_type in EntityType} == {
        "Weapon",
        "Armor",
        "Accessory",
        "Skill",
        "SkillCore",
        "Trait",
        "Buff",
        "SetBonus",
        "Monster",
        "Boss",
        "Npc",
    }


def test_supported_rarities() -> None:
    assert {rarity.value for rarity in Rarity} == {"Epic", "Heroic"}


def test_job_defaults_to_both_rarities() -> None:
    job = ImportJob(provider="manual", entity_types=(EntityType.WEAPON,))
    assert job.rarities == (Rarity.EPIC, Rarity.HEROIC)
    assert job.job_id


def test_context_defaults_to_dry_run() -> None:
    job = ImportJob(provider="manual", entity_types=(EntityType.WEAPON,))
    context = ImportContext(job=job)
    assert context.dry_run is True


def test_validation_report_severity_logic() -> None:
    report = ValidationReport(stable_id="tl.weapon.test")
    assert report.is_valid
    report.issues.append(ImportIssue(Severity.WARNING, "W", "tl.weapon.test", "warn"))
    assert report.is_valid
    report.issues.append(ImportIssue(Severity.ERROR, "E", "tl.weapon.test", "err"))
    assert not report.is_valid
    assert len(report.warnings) == 1
    assert len(report.errors) == 1


def test_dataflow_models_are_immutable() -> None:
    document = SourceDocument(provider="manual", uri="doc://x", content_type="text", content="")
    raw = RawEntity(entity_type=EntityType.WEAPON, source=document, data={})
    normalized = NormalizedEntity(
        stable_id="tl.weapon.x",
        entity_type=EntityType.WEAPON,
        rarity=Rarity.EPIC,
        name="X",
        payload={},
        references=(),
        source=document,
    )
    for frozen in (document, raw, normalized):
        try:
            frozen.provider = "other"  # type: ignore[misc, union-attr]
        except AttributeError:
            continue
        raise AssertionError(f"{type(frozen).__name__} is not frozen")


def test_import_result_defaults() -> None:
    result = ImportResult(job_id="j1")
    assert result.status is ImportStatus.SUCCESS
    assert result.documents_fetched == 0
    assert result.finished_at is None
