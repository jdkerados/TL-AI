"""Stat model."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tl_database.models.associations import buff_stats, trait_stats
from tl_database.models.entity import Entity

if TYPE_CHECKING:
    from tl_database.models.buff import Buff
    from tl_database.models.trait import Trait


class Stat(Entity):
    """Stat definition (joined-table inheritance from Entity)."""

    __tablename__ = "stats"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True
    )

    traits: Mapped[list["Trait"]] = relationship(
        secondary=trait_stats, back_populates="stats", passive_deletes=True
    )
    buffs: Mapped[list["Buff"]] = relationship(
        secondary=buff_stats, back_populates="stats", passive_deletes=True
    )

    __mapper_args__ = {"polymorphic_identity": "stat"}
