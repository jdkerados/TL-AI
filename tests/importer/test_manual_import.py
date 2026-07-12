"""Tests for the manual import provider, service, and CLI."""

import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select

from tl_database.models import Entity, Weapon
from tl_database.session import DEFAULT_DATABASE_URL, create_session_factory
from tl_importer.cli.import_main import main
from tl_importer.models import EntityType, ImportContext, ImportJob
from tl_importer.providers.manual import LocalManualProvider
from tl_importer.service import DatabaseTarget, ManualImportService


def _context(specs_dir: Path) -> ImportContext:
    job = ImportJob(provider="manual", entity_types=tuple(EntityType))
    return ImportContext(job=job, specs_dir=specs_dir)


def _sqlite_target(tmp_path: Path) -> DatabaseTarget:
    return DatabaseTarget("sqlite", f"sqlite:///{(tmp_path / 'import.sqlite3').as_posix()}")


def _run(
    specs_dir: Path, schemas_dir: Path, tmp_path: Path, target: DatabaseTarget | None = None
) -> tuple[int, dict[str, object], DatabaseTarget]:
    target = target or _sqlite_target(tmp_path)
    service = ManualImportService(specs_dir, schemas_dir)
    report_path = tmp_path / "import_report.json"
    outcome = service.run((target,), report_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    return outcome.exit_code, report, target


def _weapon_version(url: str) -> str | None:
    engine = create_engine(url)
    with create_session_factory(engine)() as session:
        weapon = session.scalar(select(Weapon).where(Weapon.stable_id == "tl.weapon.t009_sword"))
        version = weapon.semantic_version if weapon else None
    engine.dispose()
    return version


def test_provider_scans_specifications(specs_dir: Path) -> None:
    provider = LocalManualProvider()
    documents = list(provider.fetch(_context(specs_dir)))
    assert [doc.uri for doc in documents] == [
        "items/weapons/ImportSword.yaml",
        "traits/ImportTrait.yaml",
    ]
    assert all(doc.provider == "manual" for doc in documents)
    assert all(doc.content for doc in documents)


def test_empty_specifications(empty_specs_dir: Path, schemas_dir: Path, tmp_path: Path) -> None:
    exit_code, report, _ = _run(empty_specs_dir, schemas_dir, tmp_path)
    assert exit_code == 0
    assert report["documentsScanned"] == 0
    assert report["entityCount"] == 0


def test_invalid_yaml_fails(specs_dir: Path, schemas_dir: Path, tmp_path: Path) -> None:
    (specs_dir / "traits" / "Broken.yaml").write_text("a: [unclosed", encoding="utf-8")
    exit_code, report, _ = _run(specs_dir, schemas_dir, tmp_path)
    assert exit_code == 1
    validation = report["validation"]
    assert isinstance(validation, dict)
    assert validation["valid"] is False
    assert report["databases"] == []
    assert not (tmp_path / "import.sqlite3").exists()


def test_invalid_reference_fails(specs_dir: Path, schemas_dir: Path, tmp_path: Path) -> None:
    (specs_dir / "traits" / "ImportTrait.yaml").unlink()
    exit_code, report, _ = _run(specs_dir, schemas_dir, tmp_path)
    assert exit_code == 1
    validation = report["validation"]
    assert isinstance(validation, dict)
    codes = {issue["code"] for issue in validation["issues"]}
    assert "REF_UNRESOLVED" in codes


def test_duplicate_stable_id_fails(specs_dir: Path, schemas_dir: Path, tmp_path: Path) -> None:
    content = (specs_dir / "traits" / "ImportTrait.yaml").read_text(encoding="utf-8")
    (specs_dir / "traits" / "ImportTraitCopy.yaml").write_text(
        content.replace("internalName: ImportTrait", "internalName: ImportTraitCopy"),
        encoding="utf-8",
    )
    exit_code, report, _ = _run(specs_dir, schemas_dir, tmp_path)
    assert exit_code == 1
    validation = report["validation"]
    assert isinstance(validation, dict)
    codes = {issue["code"] for issue in validation["issues"]}
    assert "ID_DUPLICATE" in codes


def test_valid_sqlite_import(specs_dir: Path, schemas_dir: Path, tmp_path: Path) -> None:
    exit_code, report, target = _run(specs_dir, schemas_dir, tmp_path)
    assert exit_code == 0
    databases = report["databases"]
    assert isinstance(databases, list)
    assert databases[0]["inserted"] == 2
    engine = create_engine(target.url)
    with create_session_factory(engine)() as session:
        weapon = session.scalar(select(Weapon).where(Weapon.stable_id == "tl.weapon.t009_sword"))
        assert weapon is not None
        assert weapon.is_validated is True
        assert weapon.semantic_version == "2.0.0"
        assert weapon.patch_version == "1.0"
        assert weapon.meta["specification"]["status"] == "validated"
        assert weapon.meta["references"] == ["tl.trait.t009_trait"]
    engine.dispose()


def test_reimport_same_version_skips(specs_dir: Path, schemas_dir: Path, tmp_path: Path) -> None:
    target = _sqlite_target(tmp_path)
    _run(specs_dir, schemas_dir, tmp_path, target)
    _, report, _ = _run(specs_dir, schemas_dir, tmp_path, target)
    databases = report["databases"]
    assert isinstance(databases, list)
    assert databases[0]["inserted"] == 0
    assert databases[0]["skipped"] == 2


def test_version_upgrade(specs_dir: Path, schemas_dir: Path, tmp_path: Path) -> None:
    target = _sqlite_target(tmp_path)
    _run(specs_dir, schemas_dir, tmp_path, target)
    weapon_file = specs_dir / "items" / "weapons" / "ImportSword.yaml"
    weapon_file.write_text(
        weapon_file.read_text(encoding="utf-8").replace("version: 2.0.0", "version: 2.1.0"),
        encoding="utf-8",
    )
    exit_code, report, _ = _run(specs_dir, schemas_dir, tmp_path, target)
    assert exit_code == 0
    databases = report["databases"]
    assert isinstance(databases, list)
    assert databases[0]["updated"] == 1
    assert _weapon_version(target.url) == "2.1.0"


def test_version_downgrade_rejected(specs_dir: Path, schemas_dir: Path, tmp_path: Path) -> None:
    target = _sqlite_target(tmp_path)
    weapon_file = specs_dir / "items" / "weapons" / "ImportSword.yaml"
    original = weapon_file.read_text(encoding="utf-8")
    weapon_file.write_text(original.replace("version: 2.0.0", "version: 3.0.0"), encoding="utf-8")
    _run(specs_dir, schemas_dir, tmp_path, target)
    weapon_file.write_text(original, encoding="utf-8")
    exit_code, report, _ = _run(specs_dir, schemas_dir, tmp_path, target)
    assert exit_code == 0
    databases = report["databases"]
    assert isinstance(databases, list)
    assert databases[0]["rejectedDowngrades"] == 1
    assert _weapon_version(target.url) == "3.0.0"


def test_validate_only_touches_no_database(
    specs_dir: Path, schemas_dir: Path, tmp_path: Path
) -> None:
    target = _sqlite_target(tmp_path)
    service = ManualImportService(specs_dir, schemas_dir)
    outcome = service.run((target,), tmp_path / "report.json", validate_only=True)
    assert outcome.exit_code == 0
    assert outcome.report["databases"] == []
    assert not Path(tmp_path / "import.sqlite3").exists()


def test_cli_sqlite_import(specs_dir: Path, schemas_dir: Path, tmp_path: Path) -> None:
    sqlite_url = f"sqlite:///{(tmp_path / 'cli.sqlite3').as_posix()}"
    report_path = tmp_path / "import_report.json"
    exit_code = main(
        [
            "--specs",
            str(specs_dir),
            "--schemas",
            str(schemas_dir),
            "--database",
            "sqlite",
            "--sqlite-url",
            sqlite_url,
            "--report",
            str(report_path),
        ]
    )
    assert exit_code == 0
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["databases"][0]["inserted"] == 2
    assert _weapon_version(sqlite_url) == "2.0.0"


def _postgres_available() -> bool:
    try:
        engine = create_engine(DEFAULT_DATABASE_URL, connect_args={"connect_timeout": 2})
        with engine.connect():
            pass
        engine.dispose()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _postgres_available(), reason="PostgreSQL is not reachable")
def test_postgres_import(specs_dir: Path, schemas_dir: Path, tmp_path: Path) -> None:
    target = DatabaseTarget("postgres", DEFAULT_DATABASE_URL)
    engine = create_engine(DEFAULT_DATABASE_URL)
    try:
        exit_code, report, _ = _run(specs_dir, schemas_dir, tmp_path, target)
        assert exit_code == 0
        databases = report["databases"]
        assert isinstance(databases, list)
        assert databases[0]["dialect"] == "postgresql"
        assert databases[0]["inserted"] == 2
        with create_session_factory(engine)() as session:
            weapon = session.scalar(
                select(Weapon).where(Weapon.stable_id == "tl.weapon.t009_sword")
            )
            assert weapon is not None
            assert weapon.is_validated is True
    finally:
        with create_session_factory(engine)() as session:
            for stable_id in ("tl.weapon.t009_sword", "tl.trait.t009_trait"):
                entity = session.scalar(select(Entity).where(Entity.stable_id == stable_id))
                if entity is not None:
                    session.delete(entity)
            session.commit()
        engine.dispose()
