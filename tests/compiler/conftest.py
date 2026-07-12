"""Shared fixtures for compiler tests: a minimal valid specification corpus."""

from pathlib import Path

import pytest

SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas"

VALID_TRAIT = """\
id: tl.trait.test_trait
type: Trait
internalName: TestTrait
displayName: Test Trait
description: A test trait.
rarity: Epic
traitCategory: Offense
appliesTo:
  - Weapon
effects:
  - attribute: CriticalChance
    modifier: Flat
    valuesByRarity:
      Epic: 110
version: 2.0.0
patch: "1.0"
metadata:
  createdAt: "2026-07-09"
  status: staging
"""

VALID_WEAPON = """\
id: tl.weapon.test_sword
type: Weapon
internalName: TestSword
displayName: Test Sword
description: A test weapon.
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
  - tl.trait.test_trait
maxTraitSlots: 2
version: 2.0.0
patch: "1.0"
metadata:
  createdAt: "2026-07-09"
  status: staging
"""


@pytest.fixture
def schemas_dir() -> Path:
    """The real project schemas directory."""
    return SCHEMAS_DIR


@pytest.fixture
def specs_dir(tmp_path: Path) -> Path:
    """A temporary specifications tree containing one valid weapon and one valid trait."""
    root = tmp_path / "specifications"
    (root / "items" / "weapons").mkdir(parents=True)
    (root / "traits").mkdir(parents=True)
    (root / "items" / "weapons" / "TestSword.yaml").write_text(VALID_WEAPON, encoding="utf-8")
    (root / "traits" / "TestTrait.yaml").write_text(VALID_TRAIT, encoding="utf-8")
    return root
