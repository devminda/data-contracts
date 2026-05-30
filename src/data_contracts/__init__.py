from data_contracts.contracts import ContractBase, contract
from data_contracts.diff import SchemaDiff, MigrationReport, FieldChange, ChangeType
from data_contracts.validation import ValidationResult, ValidationError, Severity
from data_contracts.registry import SchemaRegistry, SchemaVersion
from data_contracts.notifications import NotificationBus, Consumer

__version__ = "1.0.0"

__all__ = [
    "ContractBase", "contract",
    "SchemaDiff", "MigrationReport", "FieldChange", "ChangeType",
    "ValidationResult", "ValidationError", "Severity",
    "SchemaRegistry", "SchemaVersion",
    "NotificationBus", "Consumer",
]
