"""Validation report model."""

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tl_compiler import COMPILER_VERSION
from tl_compiler.validator.issues import Issue, Severity


@dataclass
class ValidationReport:
    """Aggregated result of a validation run."""

    specs_dir: str
    schemas_dir: str
    files_scanned: int
    issues: list[Issue] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def errors(self) -> list[Issue]:
        """Issues with error severity."""
        return [issue for issue in self.issues if issue.severity is Severity.ERROR]

    @property
    def warnings(self) -> list[Issue]:
        """Issues with warning severity."""
        return [issue for issue in self.issues if issue.severity is Severity.WARNING]

    @property
    def is_valid(self) -> bool:
        """True when no errors were found."""
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        """Serialize the report."""
        return {
            "compilerVersion": COMPILER_VERSION,
            "generatedAt": self.generated_at,
            "specificationsDir": self.specs_dir,
            "schemasDir": self.schemas_dir,
            "filesScanned": self.files_scanned,
            "valid": self.is_valid,
            "errorCount": len(self.errors),
            "warningCount": len(self.warnings),
            "issues": [issue.to_dict() for issue in self.issues],
        }

    def write(self, path: Path) -> None:
        """Write the report as JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")
