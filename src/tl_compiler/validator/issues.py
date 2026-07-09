"""Validation issue model."""

from dataclasses import dataclass
from enum import StrEnum


class Severity(StrEnum):
    """Issue severity."""

    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Issue:
    """A single validation finding."""

    severity: Severity
    code: str
    file: str
    message: str

    def to_dict(self) -> dict[str, str]:
        """Serialize for the validation report."""
        return {
            "severity": self.severity.value,
            "code": self.code,
            "file": self.file,
            "message": self.message,
        }
