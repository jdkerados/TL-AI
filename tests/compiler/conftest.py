"""Shared fixtures for compiler tests: a minimal valid specification corpus."""

from pathlib import Path

import pytest

SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas"

VALID_TRAIT = """\
id: tl.trait.test_trait
type: Trait
name: TestTrait
version: 1.0.0
patch: "1.0"
metadata:
  createdAt: "2026-07-09"
  status: staging
"""

VALID_WEAPON = """\
id: tl.weapon.test_sword
type: Weapon
name: TestSword
description: A test weapon.
version: 1.0.0
patch: "1.0"
metadata:
  createdAt: "2026-07-09"
  status: staging
traits:
  - tl.trait.test_trait
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
