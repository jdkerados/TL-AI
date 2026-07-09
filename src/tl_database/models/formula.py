"""Formula model (consumed by the Mathematical Engine)."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tl_database.models.associations import formula_inputs, formula_outputs
from tl_database.models.entity import Entity

if TYPE_CHECKING:
    from tl_database.models.stat import Stat


class Formula(Entity):
    """Mathematical formula (joined-table inheritance from Entity)."""

    __tablename__ = "formulas"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True
    )

    inputs: Mapped[list["Stat"]] = relationship(secondary=formula_inputs, passive_deletes=True)
    outputs: Mapped[list["Stat"]] = relationship(secondary=formula_outputs, passive_deletes=True)

    __mapper_args__ = {"polymorphic_identity": "formula"}
