"""Tests for the tl-ai CLI."""

import json
from pathlib import Path

from tl_compiler.cli import main


def test_validate_success(specs_dir: Path, schemas_dir: Path, tmp_path: Path) -> None:
    report_path = tmp_path / "report.json"
    exit_code = main(
        [
            "validate",
            "--specs",
            str(specs_dir),
            "--schemas",
            str(schemas_dir),
            "--report",
            str(report_path),
        ]
    )
    assert exit_code == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["valid"] is True
    assert report["filesScanned"] == 2


def test_validate_failure_exit_code(specs_dir: Path, schemas_dir: Path, tmp_path: Path) -> None:
    (specs_dir / "traits" / "TestTrait.yaml").unlink()
    exit_code = main(
        [
            "validate",
            "--specs",
            str(specs_dir),
            "--schemas",
            str(schemas_dir),
            "--report",
            str(tmp_path / "report.json"),
        ]
    )
    assert exit_code == 1


def test_compile_generates_artifacts(specs_dir: Path, schemas_dir: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "build"
    exit_code = main(
        [
            "compile",
            "--specs",
            str(specs_dir),
            "--schemas",
            str(schemas_dir),
            "--output",
            str(output_dir),
        ]
    )
    assert exit_code == 0
    assert (output_dir / "ir.json").is_file()
    assert (output_dir / "build_manifest.json").is_file()


def test_compile_aborts_on_validation_error(
    specs_dir: Path, schemas_dir: Path, tmp_path: Path
) -> None:
    (specs_dir / "traits" / "TestTrait.yaml").unlink()
    output_dir = tmp_path / "build"
    exit_code = main(
        [
            "compile",
            "--specs",
            str(specs_dir),
            "--schemas",
            str(schemas_dir),
            "--output",
            str(output_dir),
        ]
    )
    assert exit_code == 1
    assert not (output_dir / "build_manifest.json").exists()
