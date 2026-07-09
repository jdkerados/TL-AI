"""Buff model."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tl_database.models.associations import buff_stats, skill_buffs
from tl_database.models.entity import Entity

if TYPE_CHECKING:
    from tl_database.models.skill import Skill
    from tl_database.models.stat import Stat


class Buff(Entity):
    """Buff or debuff (joined-table inheritance from Entity)."""

    __tablename__ = "buffs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True
    )

    skills: Mapped[list["Skill"]] = relationship(
        secondary=skill_buffs, back_populates="buffs", passive_deletes=True
    )
    stats: Mapped[list["Stat"]] = relationship(
        secondary=buff_stats, back_populates="buffs", passive_deletes=True
    )

    __mapper_args__ = {"polymorphic_identity": "buff"}
