"""Manual import service: specifications/ -> tl_compiler -> IR -> PostgreSQL/SQLite."""

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tl_compiler.ir import build_ir
from tl_compiler.pipeline import run_validation
from tl_database.session import get_engine
from tl_importer.importers.database import DatabaseImporter, ImportStats
from tl_importer.models import EntityType, ImportContext, ImportJob
from tl_importer.providers.manual import LocalManualProvider

logger = logging.getLogger("tl_importer.service")


@dataclass(frozen=True)
class DatabaseTarget:
    """A database to import into."""

    name: str
    url: str


@dataclass
class ManualImportOutcome:
    """Result of one manual import run."""

    exit_code: int
    report: dict[str, Any]


class ManualImportService:
    """Runs the manual import: scan, validate, compile to IR, and upsert into databases."""

    def __init__(self, specs_dir: Path, schemas_dir: Path) -> None:
        self._specs_dir = specs_dir
        self._schemas_dir = schemas_dir

    def run(
        self,
        targets: tuple[DatabaseTarget, ...],
        report_path: Path,
        *,
        validate_only: bool = False,
    ) -> ManualImportOutcome:
        """Execute the import and write build/import_report.json. Returns the outcome."""
        job = ImportJob(provider="manual", entity_types=tuple(EntityType))
        context = ImportContext(job=job, specs_dir=self._specs_dir, dry_run=validate_only)
        provider = LocalManualProvider()
        documents = list(provider.fetch(context))
        logger.info("scanned %d document(s) in %s", len(documents), self._specs_dir)

        specs, validation = run_validation(self._specs_dir, self._schemas_dir)
        report: dict[str, Any] = {
            "generatedAt": datetime.now(UTC).isoformat(),
            "provider": provider.name,
            "jobId": job.job_id,
            "specificationsDir": str(self._specs_dir),
            "documentsScanned": len(documents),
            "validateOnly": validate_only,
            "validation": validation.to_dict(),
            "databases": [],
        }

        if not validation.is_valid:
            logger.error("validation failed with %d error(s)", len(validation.errors))
            self._write(report, report_path)
            return ManualImportOutcome(exit_code=1, report=report)

        ir = build_ir(specs)
        report["entityCount"] = len(ir.entities)
        logger.info("compiled %d entity(ies) to IR", len(ir.entities))

        if not validate_only:
            importer = DatabaseImporter()
            stats_list: list[ImportStats] = []
            for target in targets:
                logger.info("importing into %s", target.name)
                engine = get_engine(target.url)
                stats_list.append(importer.import_ir(ir.entities, engine, target.name))
                engine.dispose()
            report["databases"] = [stats.to_dict() for stats in stats_list]

        self._write(report, report_path)
        return ManualImportOutcome(exit_code=0, report=report)

    @staticmethod
    def _write(report: dict[str, Any], report_path: Path) -> None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        logger.info("import report written to %s", report_path)
