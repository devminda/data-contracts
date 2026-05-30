import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from data_contracts.registry import SchemaRegistry, SchemaVersion


class ChangeType(Enum):
    FIELD_ADDED = "FIELD_ADDED"
    FIELD_REMOVED = "FIELD_REMOVED"
    TYPE_CHANGED = "TYPE_CHANGED"
    FIELD_RENAMED = "FIELD_RENAMED"


@dataclass
class FieldChange:
    change_type: ChangeType
    field_name: str
    old_value: str | None = None
    new_value: str | None = None
    is_breaking: bool = False
    description: str = ""

    def __post_init__(self) -> None:
        self.is_breaking = self.change_type in (
            ChangeType.FIELD_REMOVED, ChangeType.TYPE_CHANGED, ChangeType.FIELD_RENAMED,
        )


@dataclass
class MigrationReport:
    schema_name: str
    old_version: str
    new_version: str
    changes: list[FieldChange] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    breaking_changes: list[FieldChange] = field(default_factory=list)
    safe_changes: list[FieldChange] = field(default_factory=list)
    is_breaking: bool = False

    def __post_init__(self) -> None:
        self.breaking_changes = [c for c in self.changes if c.is_breaking]
        self.safe_changes = [c for c in self.changes if not c.is_breaking]
        self.is_breaking = len(self.breaking_changes) > 0

    def to_dict(self) -> dict:
        return {
            "schema": self.schema_name,
            "from_version": self.old_version,
            "to_version": self.new_version,
            "is_breaking": self.is_breaking,
            "breaking_changes": [
                {"field": c.field_name, "type": c.change_type.value, "description": c.description}
                for c in self.breaking_changes
            ],
            "safe_changes": [
                {"field": c.field_name, "type": c.change_type.value, "description": c.description}
                for c in self.safe_changes
            ],
            "generated_at": self.generated_at.isoformat(),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def print_report(self) -> None:
        print(f"\n{'='*60}")
        print(f"  Schema migration report: {self.schema_name}")
        print(f"  {self.old_version}  ->  {self.new_version}")
        print(f"{'='*60}")
        status = "BREAKING" if self.is_breaking else "SAFE"
        print(f"\n  Status:   {status}")
        print(f"  Changes:  {len(self.changes)}  "
              f"(breaking: {len(self.breaking_changes)}, safe: {len(self.safe_changes)})")
        if self.breaking_changes:
            print(f"\n  Breaking changes:")
            for c in self.breaking_changes:
                print(f"     [{c.change_type.value}] {c.field_name}")
                print(f"       {c.description}")
        if self.safe_changes:
            print(f"\n  Safe changes:")
            for c in self.safe_changes:
                print(f"     [{c.change_type.value}] {c.field_name}")
                print(f"       {c.description}")
        if not self.changes:
            print("\n  No changes detected.")
        print(f"\n{'='*60}\n")


class SchemaDiff:
    def __init__(self, old: SchemaVersion, new: SchemaVersion) -> None:
        self.old = old
        self.new = new

    @classmethod
    def from_registry(cls, old_name: str, new_name: str) -> "SchemaDiff":
        old = SchemaRegistry.get_latest(old_name)
        new = SchemaRegistry.get_latest(new_name)
        if old is None:
            raise KeyError(f"Schema '{old_name}' not found in registry")
        if new is None:
            raise KeyError(f"Schema '{new_name}' not found in registry")
        return cls(old, new)

    def _detect_renames(
        self,
        removed: set[str],
        added: set[str],
        old_fields: dict[str, type],
        new_fields: dict[str, type],
    ) -> list[FieldChange]:
        renames: list[FieldChange] = []
        matched_added: set[str] = set()
        for old_f in list(removed):
            old_type = old_fields[old_f]
            candidates = [
                f for f in added
                if f not in matched_added and new_fields[f] == old_type
            ]
            if len(candidates) == 1:
                new_f = candidates[0]
                renames.append(FieldChange(
                    change_type=ChangeType.FIELD_RENAMED,
                    field_name=old_f,
                    old_value=old_f,
                    new_value=new_f,
                    description=(
                        f"'{old_f}' -> '{new_f}' (type: {old_type.__name__}). "
                        f"Update all consumers to use '{new_f}'."
                    ),
                ))
                matched_added.add(new_f)
        return renames

    def generate_report(self) -> MigrationReport:
        old_fields = self.old.fields
        new_fields = self.new.fields
        changes: list[FieldChange] = []

        old_keys = set(old_fields.keys())
        new_keys = set(new_fields.keys())
        removed = old_keys - new_keys
        added = new_keys - old_keys
        common = old_keys & new_keys

        renames = self._detect_renames(removed, added, old_fields, new_fields)
        renamed_old = {c.old_value for c in renames}
        renamed_new = {c.new_value for c in renames}
        changes.extend(renames)

        for f in removed - renamed_old:  # type: ignore[operator]
            changes.append(FieldChange(
                change_type=ChangeType.FIELD_REMOVED, field_name=f,
                old_value=old_fields[f].__name__,
                description=f"Field '{f}' removed. Consumers reading it will fail.",
            ))

        for f in added - renamed_new:  # type: ignore[operator]
            changes.append(FieldChange(
                change_type=ChangeType.FIELD_ADDED, field_name=f,
                new_value=new_fields[f].__name__,
                description=f"New field '{f}' added. Consumers unaffected (additive).",
            ))

        for f in common:
            if old_fields[f] != new_fields[f]:
                changes.append(FieldChange(
                    change_type=ChangeType.TYPE_CHANGED, field_name=f,
                    old_value=old_fields[f].__name__,
                    new_value=new_fields[f].__name__,
                    description=(
                        f"Type of '{f}': {old_fields[f].__name__} -> {new_fields[f].__name__}. "
                        f"May cause runtime errors."
                    ),
                ))

        return MigrationReport(
            schema_name=self.old.name,
            old_version=self.old.version,
            new_version=self.new.version,
            changes=changes,
        )
