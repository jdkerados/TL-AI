"""Tests for the YAML loader."""

from pathlib import Path

from tl_compiler.parser import load_specifications


def test_loads_valid_corpus(specs_dir: Path) -> None:
    specs = load_specifications(specs_dir)
    assert len(specs) == 2
    assert all(spec.error is None for spec in specs)
    assert all(spec.data is not None for spec in specs)


def test_categories_resolved(specs_dir: Path) -> None:
    specs = {spec.relative_path: spec for spec in load_specifications(specs_dir)}
    weapon = specs["items/weapons/TestSword.yaml"]
    trait = specs["traits/TestTrait.yaml"]
    assert weapon.category is not None and weapon.category.entity_type == "Weapon"
    assert trait.category is not None and trait.category.entity_type == "Trait"


def test_invalid_yaml_reports_error(specs_dir: Path) -> None:
    (specs_dir / "traits" / "Broken.yaml").write_text("a: [unclosed", encoding="utf-8")
    specs = {spec.relative_path: spec for spec in load_specifications(specs_dir)}
    assert specs["traits/Broken.yaml"].error is not None


def test_non_mapping_reports_error(specs_dir: Path) -> None:
    (specs_dir / "traits" / "List.yaml").write_text("- a\n- b\n", encoding="utf-8")
    specs = {spec.relative_path: spec for spec in load_specifications(specs_dir)}
    assert specs["traits/List.yaml"].error is not None


def test_yml_extension_rejected(specs_dir: Path) -> None:
    (specs_dir / "traits" / "Wrong.yml").write_text("id: tl.trait.wrong\n", encoding="utf-8")
    specs = {spec.relative_path: spec for spec in load_specifications(specs_dir)}
    assert ".yaml extension" in str(specs["traits/Wrong.yml"].error)
