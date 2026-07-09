"""YAML loader: reads every specification file under specifications/."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from tl_compiler.config import Category, category_for


@dataclass(frozen=True)
class SpecFile:
    """A loaded specification file."""

    path: Path
    relative_path: str
    category: Category | None
    data: dict[str, Any] | None
    error: str | None = None


def _load_file(path: Path, relative_path: str) -> SpecFile:
    category = category_for(relative_path)
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        return SpecFile(path, relative_path, category, None, f"cannot read file: {exc}")
    try:
        documents = list(yaml.safe_load_all(raw))
    except yaml.YAMLError as exc:
        return SpecFile(path, relative_path, category, None, f"invalid YAML: {exc}")
    if len(documents) != 1:
        return SpecFile(
            path,
            relative_path,
            category,
            None,
            f"expected exactly one YAML document, found {len(documents)}",
        )
    data = documents[0]
    if not isinstance(data, dict):
        return SpecFile(
            path,
            relative_path,
            category,
            None,
            f"expected a mapping at the top level, found {type(data).__name__}",
        )
    return SpecFile(path, relative_path, category, data)


def load_specifications(specs_dir: Path) -> list[SpecFile]:
    """Load every .yaml/.yml file under specs_dir, sorted by relative path."""
    specs: list[SpecFile] = []
    for pattern in ("*.yaml", "*.yml"):
        for path in specs_dir.rglob(pattern):
            relative_path = path.relative_to(specs_dir).as_posix()
            spec = _load_file(path, relative_path)
            if path.suffix == ".yml":
                spec = SpecFile(
                    path,
                    relative_path,
                    spec.category,
                    None,
                    "files must use the .yaml extension, not .yml",
                )
            specs.append(spec)
    specs.sort(key=lambda spec: spec.relative_path)
    return specs
