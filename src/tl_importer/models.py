"""Core data model of the import framework.

Pipeline data flow:
SourceDocument -> RawEntity -> NormalizedEntity -> ValidationReport -> ImportResult
"""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any


class EntityType(StrEnum):
    """Entity types supported by the import framework."""

    WEAPON = "Weapon"
    ARMOR = "Armor"
    ACCESSORY = "Accessory"
    SKILL = "Skill"
    SKILL_CORE = "SkillCore"
    TRAIT = "Trait"
    BUFF = "Buff"
    SET_BONUS = "SetBonus"
    MONSTER = "Monster"
    BOSS = "Boss"
    NPC = "Npc"


class Rarity(StrEnum):
    """Rarities in scope for this milestone."""

    EPIC = "Epic"
    HEROIC = "Heroic"


class Severity(StrEnum):
    """Validation issue severity."""

    ERROR = "error"
    WARNING = "warning"


class ImportStatus(StrEnum):
    """Outcome of an import run."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass(frozen=True)
class SourceDocument:
    """A document fetched from a provider, before parsing."""

    provider: str
    uri: str
    content_type: str
    content: str
    fetched_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RawEntity:
    """An entity extracted from a source document, in provider-specific shape."""

    entity_type: EntityType
    source: SourceDocument
    data: dict[str, Any]
    rarity: Rarity | None = None


@dataclass(frozen=True)
class NormalizedEntity:
    """An entity in canonical TL-AI shape, ready for validation and staging."""

    stable_id: str
    entity_type: EntityType
    rarity: Rarity
    name: str
    payload: dict[str, Any]
    references: tuple[str, ...]
    source: SourceDocument


@dataclass(frozen=True)
class ImportIssue:
    """A single validation finding for an imported entity."""

    severity: Severity
    code: str
    stable_id: str
    message: str


@dataclass
class ValidationReport:
    """Validation result for one normalized entity."""

    stable_id: str
    issues: list[ImportIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ImportIssue]:
        """Issues with error severity."""
        return [issue for issue in self.issues if issue.severity is Severity.ERROR]

    @property
    def warnings(self) -> list[ImportIssue]:
        """Issues with warning severity."""
        return [issue for issue in self.issues if issue.severity is Severity.WARNING]

    @property
    def is_valid(self) -> bool:
        """True when no errors were found."""
        return not self.errors


@dataclass(frozen=True)
class ImportJob:
    """A request to import entities of given types and rarities from one provider."""

    provider: str
    entity_types: tuple[EntityType, ...]
    rarities: tuple[Rarity, ...] = (Rarity.EPIC, Rarity.HEROIC)
    params: dict[str, Any] = field(default_factory=dict)
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class ImportContext:
    """Execution context shared by all pipeline stages."""

    job: ImportJob
    specs_dir: Path = Path("specifications")
    dry_run: bool = True
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImportResult:
    """Aggregated outcome of one pipeline run."""

    job_id: str
    status: ImportStatus = ImportStatus.SUCCESS
    documents_fetched: int = 0
    raw_entities: int = 0
    normalized_entities: int = 0
    valid_entities: int = 0
    imported_entities: int = 0
    reports: list[ValidationReport] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None
