"""Stable-ID validator: pattern, category prefix, and uniqueness."""

from tl_compiler.config import STABLE_ID_RE
from tl_compiler.parser import SpecFile
from tl_compiler.validator.issues import Issue, Severity


def validate_stable_id(spec: SpecFile) -> list[Issue]:
    """Validate the stable ID of one specification file."""
    if spec.data is None or spec.category is None:
        return []
    issues: list[Issue] = []
    stable_id = spec.data.get("id")
    if not isinstance(stable_id, str) or not STABLE_ID_RE.match(stable_id):
        issues.append(
            Issue(
                Severity.ERROR,
                "ID_PATTERN",
                spec.relative_path,
                f"id {stable_id!r} does not match the stable-ID pattern "
                "tl.<category>.<identifier>",
            )
        )
        return issues
    if spec.category is not None:
        expected_prefix = f"tl.{spec.category.id_category}."
        if not stable_id.startswith(expected_prefix):
            issues.append(
                Issue(
                    Severity.ERROR,
                    "ID_CATEGORY_MISMATCH",
                    spec.relative_path,
                    f"id {stable_id!r} must start with {expected_prefix!r} "
                    f"for files in {spec.category.directory}/",
                )
            )
    return issues


def validate_unique_ids(duplicates: dict[str, list[SpecFile]]) -> list[Issue]:
    """Report duplicate stable IDs across the corpus."""
    issues: list[Issue] = []
    for stable_id, specs in sorted(duplicates.items()):
        files = ", ".join(spec.relative_path for spec in specs)
        for spec in specs[1:]:
            issues.append(
                Issue(
                    Severity.ERROR,
                    "ID_DUPLICATE",
                    spec.relative_path,
                    f"duplicate stable ID {stable_id!r} (defined in: {files})",
                )
            )
    return issues
