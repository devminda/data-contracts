import inspect
from typing import Any, get_type_hints

from data_contracts.registry import SchemaRegistry, SchemaVersion
from data_contracts.validation import ValidationResult, validate_data


class ContractMeta(type):
    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> "ContractMeta":
        cls = super().__new__(mcs, name, bases, namespace)

        if name == "ContractBase":
            return cls

        annotations: dict[str, Any] = {}
        for base in reversed(cls.__mro__):
            annotations.update(getattr(base, "__annotations__", {}))

        try:
            resolved = get_type_hints(cls)
        except Exception:
            resolved = annotations

        schema_fields = {k: v for k, v in resolved.items() if not k.startswith("_")}

        cls._schema_fields = schema_fields  # type: ignore[attr-defined]
        cls._schema_name = name  # type: ignore[attr-defined]
        cls._schema_version = getattr(cls, "__version__", "1.0.0")  # type: ignore[attr-defined]

        SchemaRegistry.register(SchemaVersion(
            name=name,
            version=cls._schema_version,  # type: ignore[attr-defined]
            fields=schema_fields,
        ))

        def _validate(data: dict) -> ValidationResult:
            return validate_data(schema_fields, data)

        cls.validate = staticmethod(_validate)  # type: ignore[attr-defined]
        return cls


class ContractBase(metaclass=ContractMeta):
    """Inherit from this to opt into the data contracts framework."""
    pass


def contract(version: Any = "1.0.0"):
    def _decorator(cls: type) -> type:
        try:
            resolved = get_type_hints(cls)
        except Exception:
            resolved = getattr(cls, "__annotations__", {})

        schema_fields = {k: v for k, v in resolved.items() if not k.startswith("_")}
        cls._schema_fields = schema_fields  # type: ignore[attr-defined]
        cls._schema_name = cls.__name__  # type: ignore[attr-defined]
        cls._schema_version = version  # type: ignore[attr-defined]

        SchemaRegistry.register(SchemaVersion(
            name=cls.__name__, version=version, fields=schema_fields,
        ))

        def _validate(data: dict) -> ValidationResult:
            return validate_data(schema_fields, data)

        cls.validate = staticmethod(_validate)  # type: ignore[attr-defined]
        return cls

    if inspect.isclass(version):
        cls, version = version, "1.0.0"
        return _decorator(cls)

    return _decorator
