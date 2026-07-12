"""Tests for the IR builder."""

from pathlib import Path

from tl_compiler.ir import build_ir
from tl_compiler.parser import load_specifications


def test_ir_contains_all_entities(specs_dir: Path) -> None:
    ir = build_ir(load_specifications(specs_dir))
    assert len(ir.entities) == 2
    index = ir.by_id()
    assert set(index) == {"tl.weapon.test_sword", "tl.trait.test_trait"}


def test_ir_entity_fields(specs_dir: Path) -> None:
    ir = build_ir(load_specifications(specs_dir))
    weapon = ir.by_id()["tl.weapon.test_sword"]
    assert weapon.entity_type == "Weapon"
    assert weapon.internal_name == "TestSword"
    assert weapon.display_name == "Test Sword"
    assert weapon.rarity == "Epic"
    assert weapon.version == "2.0.0"
    assert weapon.patch == "1.0"
    assert weapon.status == "staging"
    assert weapon.source_path == "items/weapons/TestSword.yaml"
    assert weapon.references == ("tl.trait.test_trait",)
    assert weapon.payload["id"] == "tl.weapon.test_sword"


def test_ir_is_sorted_by_stable_id(specs_dir: Path) -> None:
    ir = build_ir(load_specifications(specs_dir))
    ids = [entity.stable_id for entity in ir.entities]
    assert ids == sorted(ids)
