"""Patch model: Throne & Liberty game patch records."""

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import CheckConstraint, Date, DateTime, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from tl_database.base import Base, json_type


class Patch(Base):
    """Game patch record (standalone table, not a game-domain entity)."""

    __tablename__ = "patches"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    stable_id: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    version: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(200))
    released_at: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    meta: Mapped[dict[str, Any]] = mapped_column("metadata", json_type(), default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint("stable_id LIKE 'tl.%'", name="stable_id_format"),
        CheckConstraint("version <> ''", name="version_not_empty"),
    )
