"""Trait model."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tl_database.models.associations import item_traits, trait_stats
from tl_database.models.entity import Entity

if TYPE_CHECKING:
    from tl_database.models.item import Item
    from tl_database.models.stat import Stat


class Trait(Entity):
    """Trait (joined-table inheritance from Entity)."""

    __tablename__ = "traits"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True
    )

    items: Mapped[list["Item"]] = relationship(
        secondary=item_traits, back_populates="traits", passive_deletes=True
    )
    stats: Mapped[list["Stat"]] = relationship(
        secondary=trait_stats, back_populates="traits", passive_deletes=True
    )

    __mapper_args__ = {"polymorphic_identity": "trait"}
