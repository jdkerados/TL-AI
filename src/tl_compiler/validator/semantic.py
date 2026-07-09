"""Semantic validator: conventions that go beyond JSON Schema."""

from pathlib import PurePosixPath

from tl_compiler.config import PASCAL_CASE_RE
from tl_compiler.parser import SpecFile
from tl_compiler.validator.issues import Issue, Severity


def validate_semantics(spec: SpecFile) -> list[Issue]:
    """Validate naming and typing conventions for one specification file."""
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
    name = spec.data.get("name")
    if isinstance(name, str) and PASCAL_CASE_RE.match(name):
        stem = PurePosixPath(spec.relative_path).stem
        if stem != name:
            issues.append(
                Issue(
                    Severity.ERROR,
                    "FILENAME_MISMATCH",
                    spec.relative_path,
                    f"file name {stem!r} does not match entity name {name!r} "
                    "(expected one entity per file, named <Name>.yaml)",
                )
            )
    return issues
