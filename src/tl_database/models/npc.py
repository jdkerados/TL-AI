"""Npc model."""

import uuid

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from tl_database.models.entity import Entity


class Npc(Entity):
    """NPC (joined-table inheritance from Entity)."""

    __tablename__ = "npcs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True
    )

    __mapper_args__ = {"polymorphic_identity": "npc"}
