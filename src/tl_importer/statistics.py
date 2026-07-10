"""Database statistics generator: entity counts per type and per database."""

import argparse
import json
import logging
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import func, select

from tl_compiler.config import DEFAULT_BUILD_DIR
from tl_database.models import Entity
from tl_database.session import create_session_factory, get_database_url, get_engine
from tl_importer.service import DatabaseTarget

logger = logging.getLogger("tl_importer.statistics")

DEFAULT_SQLITE_URL = f"sqlite:///{DEFAULT_BUILD_DIR}/tl-ai.sqlite3"

STATISTIC_KEYS: dict[str, str] = {
    "weapon": "weaponCount",
    "armor": "armorCount",
    "accessory": "accessoryCount",
    "skill": "skillCount",
    "skill_core": "skillCoreCount",
    "trait": "traitCount",
    "set_bonus": "setBonusCount",
}


def collect_statistics(target: DatabaseTarget) -> dict[str, Any]:
    """Collect entity counts per type from one database."""
    engine = get_engine(target.url)
    with create_session_factory(engine)() as session:
        rows = session.execute(
            select(Entity.entity_type, func.count()).group_by(Entity.entity_type)
        ).all()
    engine.dispose()
    counts: dict[str, int] = dict(rows)  # type: ignore[arg-type]
    statistics: dict[str, Any] = {
        "database": target.name,
        "totalEntities": sum(counts.values()),
    }
    for entity_type, key in STATISTIC_KEYS.items():
        statistics[key] = counts.get(entity_type, 0)
    other = {k: v for k, v in counts.items() if k not in STATISTIC_KEYS}
    if other:
        statistics["otherCounts"] = dict(sorted(other.items()))
    return statistics


def generate_statistics(targets: tuple[DatabaseTarget, ...], output_path: Path) -> dict[str, Any]:
    """Write build/database_statistics.json for the given database targets."""
    report: dict[str, Any] = {
        "generatedAt": datetime.now(UTC).isoformat(),
        "databases": [collect_statistics(target) for target in targets],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    logger.info("database statistics written to %s", output_path)
    return report


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns the process exit code."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(
        prog="tl-stats", description="Generate TL-AI database statistics"
    )
    parser.add_argument("--database", choices=("postgres", "sqlite", "both"), default="both")
    parser.add_argument("--postgres-url", default=None)
    parser.add_argument("--sqlite-url", default=DEFAULT_SQLITE_URL)
    parser.add_argument(
        "--output", type=Path, default=Path(DEFAULT_BUILD_DIR) / "database_statistics.json"
    )
    args = parser.parse_args(argv)
    postgres = DatabaseTarget("postgres", args.postgres_url or get_database_url())
    sqlite = DatabaseTarget("sqlite", args.sqlite_url)
    if args.database == "postgres":
        targets: tuple[DatabaseTarget, ...] = (postgres,)
    elif args.database == "sqlite":
        targets = (sqlite,)
    else:
        targets = (postgres, sqlite)
    report = generate_statistics(targets, args.output)
    for database in report["databases"]:
        logger.info("[%s] %d entities", database["database"], database["totalEntities"])
    return 0


def run() -> None:
    """Console-script wrapper."""
    raise SystemExit(main())
