"""Specification categories and validation patterns for the TL Compiler."""

import re
from dataclasses import dataclass
from pathlib import PurePosixPath

STABLE_ID_RE = re.compile(r"^tl\.[a-z_]+\.[a-z0-9_]+$")
PASCAL_CASE_RE = re.compile(r"^[A-Z][A-Za-z0-9]*$")

DEFAULT_SPECS_DIR = "specifications"
DEFAULT_SCHEMAS_DIR = "schemas"
DEFAULT_BUILD_DIR = "build"


@dataclass(frozen=True)
class Category:
    """A specification directory mapped to its schema and expected entity type."""

    directory: str
    schema_file: str
    entity_type: str
    id_category: str


CATEGORIES: tuple[Category, ...] = (
    Category("entities", "entity.schema.json", "Entity", "entity"),
    Category("items/weapons", "weapon.schema.json", "Weapon", "weapon"),
    Category("items/armor", "armor.schema.json", "Armor", "armor"),
    Category("items/accessories", "accessory.schema.json", "Accessory", "accessory"),
    Category("skills", "skill.schema.json", "Skill", "skill"),
    Category("skill_cores", "skill_core.schema.json", "SkillCore", "skill_core"),
    Category("traits", "trait.schema.json", "Trait", "trait"),
    Category("buffs", "buff.schema.json", "Buff", "buff"),
    Category("monsters", "monster.schema.json", "Monster", "monster"),
    Category("bosses", "boss.schema.json", "Boss", "boss"),
    Category("npc", "npc.schema.json", "Npc", "npc"),
    Category("sets", "set.schema.json", "SetBonus", "set"),
    Category("formulas", "formula.schema.json", "Formula", "formula"),
    Category("stats", "stat.schema.json", "Stat", "stat"),
    Category("events", "event.schema.json", "Event", "event"),
)

_CATEGORIES_BY_DIRECTORY = {category.directory: category for category in CATEGORIES}


def category_for(relative_path: str) -> Category | None:
    """Resolve the category of a specification file from its path relative to specifications/."""
    parent = str(PurePosixPath(relative_path).parent)
    return _CATEGORIES_BY_DIRECTORY.get(parent)
