"""Validation pipeline: load, validate, and report on the specification corpus."""

from pathlib import Path

from tl_compiler.parser import SpecFile, load_specifications
from tl_compiler.resolver import build_index
from tl_compiler.validator import (
    Issue,
    SchemaValidator,
    Severity,
    ValidationReport,
    validate_references,
    validate_semantics,
    validate_stable_id,
    validate_unique_ids,
)


def run_validation(specs_dir: Path, schemas_dir: Path) -> tuple[list[SpecFile], ValidationReport]:
    """Run the full validation pipeline and return loaded specs plus the report."""
    specs = load_specifications(specs_dir)
    schema_validator = SchemaValidator(schemas_dir)
    index, duplicates = build_index(specs)

    issues: list[Issue] = []
    for spec in specs:
        if spec.error is not None:
            issues.append(Issue(Severity.ERROR, "PARSE_ERROR", spec.relative_path, spec.error))
            continue
        issues.extend(schema_validator.validate(spec))
        issues.extend(validate_stable_id(spec))
        issues.extend(validate_semantics(spec))
        issues.extend(validate_references(spec, index))
    issues.extend(validate_unique_ids(duplicates))

    report = ValidationReport(
        specs_dir=str(specs_dir),
        schemas_dir=str(schemas_dir),
        files_scanned=len(specs),
        issues=issues,
    )
    return specs, report
