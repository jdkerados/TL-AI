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
    issues.extend(_validate_trait_pool(spec, index))
    return issues


def _validate_trait_pool(spec: SpecFile, index: dict[str, SpecFile]) -> list[Issue]:
    """Traits in an item's traitPool must declare the item kind in their appliesTo list."""
    if spec.data is None:
        return []
    item_type = spec.data.get("type")
    if item_type not in ("Weapon", "Armor", "Accessory"):
        return []
    trait_pool = spec.data.get("traitPool")
    if not isinstance(trait_pool, list):
        return []
    issues: list[Issue] = []
    for reference in trait_pool:
        target = index.get(reference) if isinstance(reference, str) else None
        if target is None or target.data is None:
            continue
        applies_to = target.data.get("appliesTo")
        if isinstance(applies_to, list) and item_type not in applies_to:
            issues.append(
                Issue(
                    Severity.ERROR,
                    "TRAIT_NOT_APPLICABLE",
                    spec.relative_path,
                    f"trait {reference!r} does not apply to {item_type} "
                    f"(appliesTo: {applies_to})",
                )
            )
    return issues
