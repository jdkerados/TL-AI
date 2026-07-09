"""Source model: provenance of ingested data."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, DateTime, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tl_database.base import Base, json_type

if TYPE_CHECKING:
    from tl_database.models.entity import Entity


class Source(Base):
    """Data source record (standalone table, not a game-domain entity)."""

    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    stable_id: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    url: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    meta: Mapped[dict[str, Any]] = mapped_column("metadata", json_type(), default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    entities: Mapped[list["Entity"]] = relationship(back_populates="source")

    __table_args__ = (
        CheckConstraint("stable_id LIKE 'tl.%'", name="stable_id_format"),
        CheckConstraint("name <> ''", name="name_not_empty"),
    )
