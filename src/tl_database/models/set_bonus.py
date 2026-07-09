"""SetBonus model."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tl_database.models.associations import set_bonus_items
from tl_database.models.entity import Entity

if TYPE_CHECKING:
    from tl_database.models.item import Item


class SetBonus(Entity):
    """Item set bonus (joined-table inheritance from Entity)."""

    __tablename__ = "set_bonuses"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True
    )

    items: Mapped[list["Item"]] = relationship(
        secondary=set_bonus_items, back_populates="set_bonuses", passive_deletes=True
    )

    __mapper_args__ = {"polymorphic_identity": "set_bonus"}
