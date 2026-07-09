"""Item models: Item base plus Weapon, Armor, and Accessory subtypes."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tl_database.models.associations import item_traits, set_bonus_items
from tl_database.models.entity import Entity

if TYPE_CHECKING:
    from tl_database.models.set_bonus import SetBonus
    from tl_database.models.trait import Trait


class Item(Entity):
    """Base item (joined-table inheritance from Entity)."""

    __tablename__ = "items"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True
    )

    traits: Mapped[list["Trait"]] = relationship(
        secondary=item_traits, back_populates="items", passive_deletes=True
    )
    set_bonuses: Mapped[list["SetBonus"]] = relationship(
        secondary=set_bonus_items, back_populates="items", passive_deletes=True
    )

    __mapper_args__ = {"polymorphic_identity": "item"}


class Weapon(Item):
    """Weapon item."""

    __tablename__ = "weapons"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True
    )

    __mapper_args__ = {"polymorphic_identity": "weapon"}


class Armor(Item):
    """Armor item."""

    __tablename__ = "armor"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True
    )

    __mapper_args__ = {"polymorphic_identity": "armor"}


class Accessory(Item):
    """Accessory item."""

    __tablename__ = "accessories"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True
    )

    __mapper_args__ = {"polymorphic_identity": "accessory"}
