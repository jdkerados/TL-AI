"""JSON Schema validator (Draft 2020-12) for specification files."""

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from tl_compiler.parser import SpecFile
from tl_compiler.validator.issues import Issue, Severity


class SchemaValidator:
    """Validates specification documents against the JSON Schemas in schemas/."""

    def __init__(self, schemas_dir: Path) -> None:
        self._schemas: dict[str, dict[str, Any]] = {}
        resources: list[tuple[str, Resource[Any]]] = []
        for path in sorted(schemas_dir.glob("*.schema.json")):
            schema = json.loads(path.read_text(encoding="utf-8"))
            self._schemas[path.name] = schema
            schema_id = schema.get("$id", path.name)
            resources.append((schema_id, Resource.from_contents(schema)))
        registry: Registry[Any] = Registry().with_resources(resources)
        self._validators: dict[str, Draft202012Validator] = {
            name: Draft202012Validator(schema, registry=registry)
            for name, schema in self._schemas.items()
        }

    @property
    def schema_names(self) -> tuple[str, ...]:
        """Names of the loaded schema files."""
        return tuple(self._schemas)

    def validate(self, spec: SpecFile) -> list[Issue]:
        """Validate one specification file against the schema of its category."""
        if spec.data is None:
            return []
        if spec.category is None:
            return [
                Issue(
                    Severity.WARNING,
                    "NO_SCHEMA",
                    spec.relative_path,
                    "no schema is defined for this directory; file was not schema-validated",
                )
            ]
        validator = self._validators.get(spec.category.schema_file)
        if validator is None:
            return [
                Issue(
                    Severity.ERROR,
                    "SCHEMA_MISSING",
                    spec.relative_path,
                    f"schema file not found: {spec.category.schema_file}",
                )
            ]
        issues = []
        for error in sorted(validator.iter_errors(spec.data), key=lambda e: e.json_path):
            issues.append(
                Issue(
                    Severity.ERROR,
                    "SCHEMA_INVALID",
                    spec.relative_path,
                    f"{error.json_path}: {error.message}",
                )
            )
        return issues
