"""tl-import CLI: manual import of specifications into PostgreSQL and/or SQLite."""

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

from tl_compiler.config import DEFAULT_BUILD_DIR, DEFAULT_SCHEMAS_DIR, DEFAULT_SPECS_DIR
from tl_database.session import get_database_url
from tl_importer.service import DatabaseTarget, ManualImportOutcome, ManualImportService

DEFAULT_SQLITE_URL = f"sqlite:///{DEFAULT_BUILD_DIR}/tl-ai.sqlite3"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tl-import",
        description="Import validated YAML specifications into the TL-AI databases",
    )
    parser.add_argument(
        "--specs",
        type=Path,
        default=Path(DEFAULT_SPECS_DIR),
        help="specifications directory (default: specifications/)",
    )
    parser.add_argument(
        "--schemas",
        type=Path,
        default=Path(DEFAULT_SCHEMAS_DIR),
        help="JSON Schemas directory (default: schemas/)",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="validate and compile only; do not touch any database",
    )
    parser.add_argument(
        "--database",
        choices=("postgres", "sqlite", "both"),
        default="both",
        help="target database(s) (default: both)",
    )
    parser.add_argument(
        "--postgres-url",
        default=None,
        help="PostgreSQL URL (default: TL_DATABASE_URL env var or local dev default)",
    )
    parser.add_argument(
        "--sqlite-url",
        default=DEFAULT_SQLITE_URL,
        help=f"SQLite URL (default: {DEFAULT_SQLITE_URL})",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path(DEFAULT_BUILD_DIR) / "import_report.json",
        help="import report output path (default: build/import_report.json)",
    )
    return parser


def _targets(args: argparse.Namespace) -> tuple[DatabaseTarget, ...]:
    postgres = DatabaseTarget("postgres", args.postgres_url or get_database_url())
    sqlite = DatabaseTarget("sqlite", args.sqlite_url)
    if args.database == "postgres":
        return (postgres,)
    if args.database == "sqlite":
        return (sqlite,)
    return (postgres, sqlite)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns the process exit code."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = _build_parser().parse_args(argv)
    service = ManualImportService(args.specs, args.schemas)
    outcome: ManualImportOutcome = service.run(
        _targets(args), args.report, validate_only=args.validate_only
    )
    return outcome.exit_code


def run() -> None:
    """Console-script wrapper."""
    raise SystemExit(main())
