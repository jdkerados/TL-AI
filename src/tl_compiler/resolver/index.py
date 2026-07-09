"""Stable-ID index and reference collection.

Reference rule (explicit, zero magic): any string value anywhere in a specification
document that matches the stable-ID pattern is a reference to another entity.
The entity's own top-level "id" value is not a reference.
"""

from typing import Any

from tl_compiler.config import STABLE_ID_RE
from tl_compiler.parser import SpecFile


def collect_references(data: dict[str, Any]) -> tuple[str, ...]:
    """Collect all stable-ID references from a specification document."""
    found: set[str] = set()

    def _walk(value: Any) -> None:
        if isinstance(value, str):
            if STABLE_ID_RE.match(value):
                found.add(value)
        elif isinstance(value, dict):
            for child in value.values():
                _walk(child)
        elif isinstance(value, list):
            for child in value:
                _walk(child)

    _walk(data)
    own_id = data.get("id")
    if isinstance(own_id, str):
        found.discard(own_id)
    return tuple(sorted(found))


def build_index(specs: list[SpecFile]) -> tuple[dict[str, SpecFile], dict[str, list[SpecFile]]]:
    """Build a stable-ID index. Returns (index, duplicates by stable ID)."""
    index: dict[str, SpecFile] = {}
    duplicates: dict[str, list[SpecFile]] = {}
    for spec in specs:
        if spec.data is None:
            continue
        stable_id = spec.data.get("id")
        if not isinstance(stable_id, str):
            continue
        if stable_id in index:
            duplicates.setdefault(stable_id, [index[stable_id]]).append(spec)
        else:
            index[stable_id] = spec
    return index, duplicates
