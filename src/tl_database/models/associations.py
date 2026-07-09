"""Association tables for many-to-many relationships between entities."""

from sqlalchemy import Column, ForeignKey, Table, Uuid

from tl_database.base import Base

item_traits = Table(
    "item_traits",
    Base.metadata,
    Column("item_id", Uuid, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True),
    Column("trait_id", Uuid, ForeignKey("traits.id", ondelete="CASCADE"), primary_key=True),
)

set_bonus_items = Table(
    "set_bonus_items",
    Base.metadata,
    Column(
        "set_bonus_id", Uuid, ForeignKey("set_bonuses.id", ondelete="CASCADE"), primary_key=True
    ),
    Column("item_id", Uuid, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True),
)

skill_buffs = Table(
    "skill_buffs",
    Base.metadata,
    Column("skill_id", Uuid, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
    Column("buff_id", Uuid, ForeignKey("buffs.id", ondelete="CASCADE"), primary_key=True),
)

skill_core_skills = Table(
    "skill_core_skills",
    Base.metadata,
    Column(
        "skill_core_id", Uuid, ForeignKey("skill_cores.id", ondelete="CASCADE"), primary_key=True
    ),
    Column("skill_id", Uuid, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
)

monster_skills = Table(
    "monster_skills",
    Base.metadata,
    Column("monster_id", Uuid, ForeignKey("monsters.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", Uuid, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
)

trait_stats = Table(
    "trait_stats",
    Base.metadata,
    Column("trait_id", Uuid, ForeignKey("traits.id", ondelete="CASCADE"), primary_key=True),
    Column("stat_id", Uuid, ForeignKey("stats.id", ondelete="CASCADE"), primary_key=True),
)

buff_stats = Table(
    "buff_stats",
    Base.metadata,
    Column("buff_id", Uuid, ForeignKey("buffs.id", ondelete="CASCADE"), primary_key=True),
    Column("stat_id", Uuid, ForeignKey("stats.id", ondelete="CASCADE"), primary_key=True),
)

formula_inputs = Table(
    "formula_inputs",
    Base.metadata,
    Column("formula_id", Uuid, ForeignKey("formulas.id", ondelete="CASCADE"), primary_key=True),
    Column("stat_id", Uuid, ForeignKey("stats.id", ondelete="CASCADE"), primary_key=True),
)

formula_outputs = Table(
    "formula_outputs",
    Base.metadata,
    Column("formula_id", Uuid, ForeignKey("formulas.id", ondelete="CASCADE"), primary_key=True),
    Column("stat_id", Uuid, ForeignKey("stats.id", ondelete="CASCADE"), primary_key=True),
)
