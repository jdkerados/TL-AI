"""tl-importer CLI skeleton. No import execution: the framework has no providers yet."""

import argparse
from collections.abc import Sequence

from tl_importer import IMPORTER_VERSION
from tl_importer.models import EntityType, Rarity

PROVIDER_INTERFACES = (
    "WikiProvider",
    "QuestlogProvider",
    "MaxrollProvider",
    "YoutubeProvider",
    "ManualProvider",
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tl-importer", description="TL-AI data import framework")
    parser.add_argument("--version", action="version", version=f"tl-importer {IMPORTER_VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("info", help="show supported entity types, rarities, and providers")
    return parser


def _cmd_info() -> int:
    print(f"tl-importer {IMPORTER_VERSION} (framework only, no concrete providers)")
    print("Entity types: " + ", ".join(entity_type.value for entity_type in EntityType))
    print("Rarities: " + ", ".join(rarity.value for rarity in Rarity))
    print("Provider interfaces: " + ", ".join(PROVIDER_INTERFACES))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns the process exit code."""
    _build_parser().parse_args(argv)
    return _cmd_info()


def run() -> None:
    """Console-script wrapper."""
    raise SystemExit(main())
