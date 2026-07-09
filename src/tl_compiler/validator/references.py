"""Cross-reference validator: every referenced stable ID must exist."""

from tl_compiler.parser import SpecFile
from tl_compiler.resolver import collect_references
from tl_compiler.validator.issues import Issue, Severity


def validate_references(spec: SpecFile, index: dict[str, SpecFile]) -> list[Issue]:
    """Validate that every stable-ID reference in the file resolves to a known entity."""
    if spec.data is None:
        return []
    issues: list[Issue] = []
    for reference in collect_references(spec.data):
        if reference not in index:
            issues.append(
                Issue(
                    Severity.ERROR,
                    "REF_UNRESOLVED",
                    spec.relative_path,
                    f"reference {reference!r} does not resolve to any known entity",
                )
            )
    return issues
