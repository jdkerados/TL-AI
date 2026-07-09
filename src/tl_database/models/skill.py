"""Skill and SkillCore models."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tl_database.models.associations import skill_buffs, skill_core_skills
from tl_database.models.entity import Entity

if TYPE_CHECKING:
    from tl_database.models.buff import Buff


class Skill(Entity):
    """Skill (joined-table inheritance from Entity)."""

    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True
    )

    buffs: Mapped[list["Buff"]] = relationship(
        secondary=skill_buffs, back_populates="skills", passive_deletes=True
    )
    skill_cores: Mapped[list["SkillCore"]] = relationship(
        secondary=skill_core_skills, back_populates="skills", passive_deletes=True
    )

    __mapper_args__ = {"polymorphic_identity": "skill"}


class SkillCore(Entity):
    """Skill core (joined-table inheritance from Entity)."""

    __tablename__ = "skill_cores"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True
    )

    skills: Mapped[list[Skill]] = relationship(
        secondary=skill_core_skills, back_populates="skill_cores", passive_deletes=True
    )

    __mapper_args__ = {"polymorphic_identity": "skill_core"}
