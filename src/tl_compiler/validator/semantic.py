"""Semantic validator: Entity Model V2 conventions that go beyond JSON Schema."""

from pathlib import PurePosixPath
from typing import Any

from tl_compiler.config import PASCAL_CASE_RE
from tl_compiler.parser import SpecFile
from tl_compiler.validator.issues import Issue, Severity


def validate_semantics(spec: SpecFile) -> list[Issue]:
    """Validate naming, typing, and V2 structural conventions for one specification file."""
    if spec.data is None or spec.category is None:
        return []
    issues: list[Issue] = []
    entity_type = spec.data.get("type")
    if entity_type != spec.category.entity_type:
        issues.append(
            Issue(
                Severity.ERROR,
                "TYPE_MISMATCH",
                spec.relative_path,
                f"type {entity_type!r} does not match expected type "
                f"{spec.category.entity_type!r} for files in {spec.category.directory}/",
            )
        )
    internal_name = spec.data.get("internalName")
    if isinstance(internal_name, str) and PASCAL_CASE_RE.match(internal_name):
        stem = PurePosixPath(spec.relative_path).stem
        if stem != internal_name:
            issues.append(
                Issue(
                    Severity.ERROR,
                    "FILENAME_MISMATCH",
                    spec.relative_path,
                    f"file name {stem!r} does not match internalName {internal_name!r} "
                    "(expected one entity per file, named <InternalName>.yaml)",
                )
            )
    issues.extend(_validate_set_bonus(spec))
    issues.extend(_validate_drops(spec))
    return issues


def _validate_set_bonus(spec: SpecFile) -> list[Issue]:
    """Piece counts must be strictly increasing and never exceed the member count."""
    if spec.data is None or spec.data.get("type") != "SetBonus":
        return []
    members = spec.data.get("members")
    bonuses = spec.data.get("bonuses")
    if not isinstance(members, list) or not isinstance(bonuses, list):
        return []
    issues: list[Issue] = []
    pieces = [b.get("pieces") for b in bonuses if isinstance(b, dict)]
    numeric = [p for p in pieces if isinstance(p, int)]
    if any(p > len(members) for p in numeric):
        issues.append(
            Issue(
                Severity.ERROR,
                "SET_PIECES_EXCEED_MEMBERS",
                spec.relative_path,
                f"piece counts {numeric} exceed the number of set members ({len(members)})",
            )
        )
    if numeric != sorted(set(numeric)):
        issues.append(
            Issue(
                Severity.ERROR,
                "SET_PIECES_NOT_INCREASING",
                spec.relative_path,
                f"piece counts {numeric} must be strictly increasing",
            )
        )
    return issues


def _validate_drops(spec: SpecFile) -> list[Issue]:
    """Monster/boss drops must have quantityMin <= quantityMax."""
    if spec.data is None:
        return []
    drops: Any = spec.data.get("drops")
    if not isinstance(drops, list):
        return []
    issues: list[Issue] = []
    for drop in drops:
        if not isinstance(drop, dict):
            continue
        minimum = drop.get("quantityMin")
        maximum = drop.get("quantityMax")
        if isinstance(minimum, int) and isinstance(maximum, int) and minimum > maximum:
            issues.append(
                Issue(
                    Severity.ERROR,
                    "DROP_QUANTITY_INVALID",
                    spec.relative_path,
                    f"drop {drop.get('item')!r}: quantityMin {minimum} > quantityMax {maximum}",
                )
            )
    return issues
