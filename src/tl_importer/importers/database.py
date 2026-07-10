"""Database importer: upserts compiled IR entities into PostgreSQL or SQLite.

Behavior:
- UPSERT by stable ID.
- Update only if the semantic version is strictly newer; downgrades are rejected.
- Imported entities are marked IsValidated = true.
- Specification metadata, patch version, and semantic version are stored.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from tl_compiler.ir import IREntity
from tl_database.base import Base
from tl_database.models import (
    Accessory,
    Armor,
    Boss,
    Buff,
    Entity,
    Formula,
    Monster,
    Npc,
    SetBonus,
    Skill,
    SkillCore,
    Stat,
    Trait,
    Weapon,
)
from tl_database.session import create_session_factory

logger = logging.getLogger("tl_importer.database")

MODEL_BY_TYPE: dict[str, type[Entity]] = {
    "Entity": Entity,
    "Weapon": Weapon,
    "Armor": Armor,
    "Accessory": Accessory,
    "Skill": Skill,
    "SkillCore": SkillCore,
    "Trait": Trait,
    "Buff": Buff,
    "Set": SetBonus,
    "SetBonus": SetBonus,
    "Monster": Monster,
    "Boss": Boss,
    "Npc": Npc,
    "Stat": Stat,
    "Formula": Formula,
}


def parse_version(version: str) -> tuple[int, ...]:
    """Parse a semantic version into a comparable tuple."""
    return tuple(int(part) for part in version.split("."))


@dataclass(frozen=True)
class EntityAction:
    """The action taken for one entity during an import."""

    stable_id: str
    action: str
    from_version: str | None = None
    to_version: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize for the import report."""
        return {
            "stableId": self.stable_id,
            "action": self.action,
            "fromVersion": self.from_version,
            "toVersion": self.to_version,
        }


@dataclass
class ImportStats:
    """Outcome of importing the IR into one database."""

    database: str
    dialect: str
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    rejected_downgrades: int = 0
    unsupported: int = 0
    actions: list[EntityAction] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for the import report."""
        return {
            "database": self.database,
            "dialect": self.dialect,
            "inserted": self.inserted,
            "updated": self.updated,
            "skipped": self.skipped,
            "rejectedDowngrades": self.rejected_downgrades,
            "unsupported": self.unsupported,
            "errors": self.errors,
            "entities": [action.to_dict() for action in self.actions],
        }


class DatabaseImporter:
    """Imports compiled IR entities into a database engine."""

    def import_ir(self, entities: tuple[IREntity, ...], engine: Engine, name: str) -> ImportStats:
        """Upsert every IR entity into the given engine. Returns import statistics."""
        Base.metadata.create_all(engine)
        stats = ImportStats(database=name, dialect=engine.dialect.name)
        factory = create_session_factory(engine)
        with factory() as session:
            for entity in entities:
                self._upsert(session, entity, stats)
            session.commit()
        logger.info(
            "[%s] import finished: %d inserted, %d updated, %d skipped, "
            "%d downgrade(s) rejected, %d unsupported",
            name,
            stats.inserted,
            stats.updated,
            stats.skipped,
            stats.rejected_downgrades,
            stats.unsupported,
        )
        return stats

    def _upsert(self, session: Session, entity: IREntity, stats: ImportStats) -> None:
        model = MODEL_BY_TYPE.get(entity.entity_type)
        if model is None:
            stats.unsupported += 1
            stats.actions.append(EntityAction(entity.stable_id, "unsupported"))
            logger.warning(
                "[%s] %s: no database model for type %s, skipped",
                stats.database,
                entity.stable_id,
                entity.entity_type,
            )
            return
        meta = {
            "specification": entity.payload.get("metadata", {}),
            "references": list(entity.references),
        }
        existing = session.scalar(select(Entity).where(Entity.stable_id == entity.stable_id))
        if existing is None:
            session.add(
                model(
                    stable_id=entity.stable_id,
                    name=entity.name,
                    description=entity.payload.get("description"),
                    semantic_version=entity.version,
                    patch_version=entity.patch,
                    is_validated=True,
                    meta=meta,
                )
            )
            stats.inserted += 1
            stats.actions.append(EntityAction(entity.stable_id, "inserted", None, entity.version))
            logger.info("[%s] %s: inserted %s", stats.database, entity.stable_id, entity.version)
            return
        if type(existing) is not model:
            stats.errors.append(
                f"{entity.stable_id}: entity type changed from "
                f"{existing.entity_type!r} to {entity.entity_type!r}, rejected"
            )
            stats.actions.append(EntityAction(entity.stable_id, "type_change_rejected"))
            logger.error("[%s] %s: entity type change rejected", stats.database, entity.stable_id)
            return
        old_version = existing.semantic_version
        if parse_version(entity.version) > parse_version(old_version):
            existing.name = entity.name
            existing.description = entity.payload.get("description")
            existing.semantic_version = entity.version
            existing.patch_version = entity.patch
            existing.is_validated = True
            existing.meta = meta
            stats.updated += 1
            stats.actions.append(
                EntityAction(entity.stable_id, "updated", old_version, entity.version)
            )
            logger.info(
                "[%s] %s: updated %s -> %s",
                stats.database,
                entity.stable_id,
                old_version,
                entity.version,
            )
        elif parse_version(entity.version) == parse_version(old_version):
            stats.skipped += 1
            stats.actions.append(
                EntityAction(entity.stable_id, "skipped", old_version, entity.version)
            )
            logger.info(
                "[%s] %s: version %s unchanged, skipped",
                stats.database,
                entity.stable_id,
                old_version,
            )
        else:
            stats.rejected_downgrades += 1
            stats.actions.append(
                EntityAction(entity.stable_id, "downgrade_rejected", old_version, entity.version)
            )
            logger.warning(
                "[%s] %s: downgrade %s -> %s rejected",
                stats.database,
                entity.stable_id,
                old_version,
                entity.version,
            )
