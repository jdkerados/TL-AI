"""Monster and Boss models."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tl_database.models.associations import monster_skills
from tl_database.models.entity import Entity

if TYPE_CHECKING:
    from tl_database.models.skill import Skill


class Monster(Entity):
    """Monster (joined-table inheritance from Entity)."""

    __tablename__ = "monsters"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True
    )

    skills: Mapped[list["Skill"]] = relationship(secondary=monster_skills, passive_deletes=True)

    __mapper_args__ = {"polymorphic_identity": "monster"}


class Boss(Monster):
    """Boss (joined-table inheritance from Monster)."""

    __tablename__ = "bosses"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("monsters.id", ondelete="CASCADE"), primary_key=True
    )

    __mapper_args__ = {"polymorphic_identity": "boss"}
