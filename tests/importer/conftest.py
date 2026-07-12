"""Shared fixtures for importer tests."""

from pathlib import Path

import pytest

SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas"

VALID_TRAIT = """\
id: tl.trait.t009_trait
type: Trait
internalName: ImportTrait
displayName: Import Trait
description: An imported test trait.
rarity: Heroic
traitCategory: Offense
appliesTo:
  - Weapon
effects:
  - attribute: Hit
    modifier: Flat
    valuesByRarity:
      Heroic: 90
version: 2.0.0
patch: "1.0"
metadata:
  createdAt: "2026-07-09"
  status: validated
"""

VALID_WEAPON = """\
id: tl.weapon.t009_sword
type: Weapon
internalName: ImportSword
displayName: Import Sword
description: An imported test weapon.
rarity: Epic
weaponType: Sword
itemLevel: 60
baseStats:
  - attribute: MinDamage
    modifier: Flat
    value: 10
  - attribute: MaxDamage
    modifier: Flat
    value: 20
traitPool:
  - tl.trait.t009_trait
maxTraitSlots: 2
version: 2.0.0
patch: "1.0"
metadata:
  createdAt: "2026-07-09"
  status: validated
"""


@pytest.fixture
def schemas_dir() -> Path:
    """The real project schemas directory."""
    return SCHEMAS_DIR


@pytest.fixture
def specs_dir(tmp_path: Path) -> Path:
    """A temporary specifications tree with one valid weapon and one valid trait."""
    root = tmp_path / "specifications"
    (root / "items" / "weapons").mkdir(parents=True)
    (root / "traits").mkdir(parents=True)
    (root / "items" / "weapons" / "ImportSword.yaml").write_text(VALID_WEAPON, encoding="utf-8")
    (root / "traits" / "ImportTrait.yaml").write_text(VALID_TRAIT, encoding="utf-8")
    return root


@pytest.fixture
def empty_specs_dir(tmp_path: Path) -> Path:
    """An empty specifications tree."""
    root = tmp_path / "specifications"
    root.mkdir()
    return root
