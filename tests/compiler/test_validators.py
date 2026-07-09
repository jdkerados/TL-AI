"""Tests for the validation pipeline."""

from pathlib import Path

from tl_compiler.pipeline import run_validation


def _codes(specs_dir: Path, schemas_dir: Path) -> set[str]:
    _, report = run_validation(specs_dir, schemas_dir)
    return {issue.code for issue in report.issues}


def test_valid_corpus_has_no_issues(specs_dir: Path, schemas_dir: Path) -> None:
    _, report = run_validation(specs_dir, schemas_dir)
    assert report.is_valid
    assert report.issues == []
    assert report.files_scanned == 2


def test_schema_violation_detected(specs_dir: Path, schemas_dir: Path) -> None:
    content = (specs_dir / "traits" / "TestTrait.yaml").read_text(encoding="utf-8")
    (specs_dir / "traits" / "TestTrait.yaml").write_text(
        content.replace("version: 1.0.0\n", ""), encoding="utf-8"
    )
    assert "SCHEMA_INVALID" in _codes(specs_dir, schemas_dir)


def test_unresolved_reference_detected(specs_dir: Path, schemas_dir: Path) -> None:
    (specs_dir / "traits" / "TestTrait.yaml").unlink()
    assert "REF_UNRESOLVED" in _codes(specs_dir, schemas_dir)


def test_id_category_mismatch_detected(specs_dir: Path, schemas_dir: Path) -> None:
    content = (specs_dir / "traits" / "TestTrait.yaml").read_text(encoding="utf-8")
    (specs_dir / "traits" / "TestTrait.yaml").write_text(
        content.replace("id: tl.trait.test_trait", "id: tl.buff.test_trait"),
        encoding="utf-8",
    )
    codes = _codes(specs_dir, schemas_dir)
    assert "ID_CATEGORY_MISMATCH" in codes


def test_duplicate_stable_id_detected(specs_dir: Path, schemas_dir: Path) -> None:
    content = (specs_dir / "traits" / "TestTrait.yaml").read_text(encoding="utf-8")
    (specs_dir / "traits" / "TestTraitCopy.yaml").write_text(
        content.replace("name: TestTrait", "name: TestTraitCopy"), encoding="utf-8"
    )
    assert "ID_DUPLICATE" in _codes(specs_dir, schemas_dir)


def test_type_mismatch_detected(specs_dir: Path, schemas_dir: Path) -> None:
    content = (specs_dir / "traits" / "TestTrait.yaml").read_text(encoding="utf-8")
    (specs_dir / "buffs").mkdir(exist_ok=True)
    (specs_dir / "traits" / "TestTrait.yaml").unlink()
    (specs_dir / "buffs" / "TestTrait.yaml").write_text(content, encoding="utf-8")
    codes = _codes(specs_dir, schemas_dir)
    assert "TYPE_MISMATCH" in codes


def test_filename_mismatch_detected(specs_dir: Path, schemas_dir: Path) -> None:
    trait = specs_dir / "traits" / "TestTrait.yaml"
    trait.rename(specs_dir / "traits" / "OtherName.yaml")
    assert "FILENAME_MISMATCH" in _codes(specs_dir, schemas_dir)


def test_uncategorized_directory_warns(specs_dir: Path, schemas_dir: Path) -> None:
    (specs_dir / "world").mkdir()
    (specs_dir / "world" / "Zone.yaml").write_text("name: Zone\n", encoding="utf-8")
    _, report = run_validation(specs_dir, schemas_dir)
    assert {issue.code for issue in report.warnings} == {"NO_SCHEMA"}
    assert report.is_valid
