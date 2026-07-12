"""IR data model."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IREntity:
    """One compiled entity."""

    stable_id: str
    entity_type: str
    internal_name: str
    display_name: str
    rarity: str | None
    version: str
    patch: str
    status: str
    source_path: str
    references: tuple[str, ...]
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Serialize for IR output."""
        return {
            "stableId": self.stable_id,
            "type": self.entity_type,
            "internalName": self.internal_name,
            "displayName": self.display_name,
            "rarity": self.rarity,
            "version": self.version,
            "patch": self.patch,
            "status": self.status,
            "sourcePath": self.source_path,
            "references": list(self.references),
            "payload": self.payload,
        }


@dataclass(frozen=True)
class BuildIR:
    """The full IR of one compilation run."""

    entities: tuple[IREntity, ...]

    def by_id(self) -> dict[str, IREntity]:
        """Index entities by stable ID."""
        return {entity.stable_id: entity for entity in self.entities}

    def to_dict(self) -> dict[str, Any]:
        """Serialize for IR output."""
        return {"entities": [entity.to_dict() for entity in self.entities]}
