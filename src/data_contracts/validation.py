from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationError:
    field_name: str
    expected: str
    received: Any
    severity: Severity = Severity.ERROR
    message: str = ""

    def __post_init__(self) -> None:
        if not self.message:
            self.message = (
                f"Field '{self.field_name}': expected {self.expected}, "
                f"got {type(self.received).__name__} = {self.received!r}"
            )


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.is_valid

    def summary(self) -> str:
        if self.is_valid:
            return "✅ Validation passed"
        lines = [f"❌ Validation failed ({len(self.errors)} error(s)):"]
        for e in self.errors:
            lines.append(f"   • {e.message}")
        return "\n".join(lines)


def validate_data(schema_fields: dict[str, type], data: dict) -> ValidationResult:
    errors: list[ValidationError] = []
    warnings: list[ValidationError] = []

    schema_keys = set(schema_fields.keys())
    data_keys = set(data.keys())

    for f in schema_keys - data_keys:
        errors.append(ValidationError(
            field_name=f, expected=schema_fields[f].__name__, received=None,
            message=f"Missing required field: '{f}'",
        ))

    for f in data_keys - schema_keys:
        warnings.append(ValidationError(
            field_name=f, expected="(not in schema)", received=data[f],
            severity=Severity.WARNING,
            message=f"Unknown field '{f}' — may indicate a schema addition",
        ))

    for f in schema_keys & data_keys:
        expected_type = schema_fields[f]
        value = data[f]
        if expected_type is float and isinstance(value, int):
            continue
        if not isinstance(value, expected_type):
            errors.append(ValidationError(
                field_name=f, expected=expected_type.__name__, received=value,
            ))

    return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
