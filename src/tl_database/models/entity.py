"""Polymorphic base entity model. All game-domain models extend Entity."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tl_database.base import Base, embedding_type, json_type
from tl_database.models.source import Source


class Entity(Base):
    """Base table for all game-domain entities (joined-table inheritance)."""

    __tablename__ = "entities"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    stable_id: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    display_name: Mapped[str | None] = mapped_column(String(200), index=True)
    rarity: Mapped[str | None] = mapped_column(String(20), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    semantic_version: Mapped[str] = mapped_column(String(50))
    patch_version: Mapped[str] = mapped_column(String(50), index=True)
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    meta: Mapped[dict[str, Any]] = mapped_column("metadata", json_type(), default=dict)
    payload: Mapped[dict[str, Any] | None] = mapped_column(json_type())
    embedding: Mapped[Any | None] = mapped_column(embedding_type())
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("sources.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    source: Mapped[Source | None] = relationship(back_populates="entities")

    __table_args__ = (
        CheckConstraint("stable_id LIKE 'tl.%'", name="stable_id_format"),
        CheckConstraint("semantic_version <> ''", name="semantic_version_not_empty"),
        CheckConstraint("patch_version <> ''", name="patch_version_not_empty"),
        Index("ix_entities_type_validated", "entity_type", "is_validated"),
    )

    __mapper_args__ = {
        "polymorphic_identity": "entity",
        "polymorphic_on": "entity_type",
    }
