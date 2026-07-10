"""Tests for the database statistics generator."""

import json
from pathlib import Path

from tl_importer.service import DatabaseTarget, ManualImportService
from tl_importer.statistics import generate_statistics


def test_statistics_counts(specs_dir: Path, schemas_dir: Path, tmp_path: Path) -> None:
    target = DatabaseTarget("sqlite", f"sqlite:///{(tmp_path / 'stats.sqlite3').as_posix()}")
    service = ManualImportService(specs_dir, schemas_dir)
    outcome = service.run((target,), tmp_path / "import_report.json")
    assert outcome.exit_code == 0

    output_path = tmp_path / "database_statistics.json"
    report = generate_statistics((target,), output_path)
    assert output_path.is_file()
    assert report == json.loads(output_path.read_text(encoding="utf-8"))

    database = report["databases"][0]
    assert database["database"] == "sqlite"
    assert database["totalEntities"] == 2
    assert database["weaponCount"] == 1
    assert database["traitCount"] == 1
    assert database["armorCount"] == 0
    assert database["accessoryCount"] == 0
    assert database["skillCount"] == 0
    assert database["skillCoreCount"] == 0
    assert database["setBonusCount"] == 0
