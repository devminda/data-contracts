from data_contracts.diff import ChangeType, SchemaDiff
from data_contracts.registry import SchemaVersion
import json


def sv(name: str, version: str, fields: dict) -> SchemaVersion:
    return SchemaVersion(name=name, version=version, fields=fields)


class TestFieldAdded:
    def test_is_safe(self):
        report = SchemaDiff(sv("S","1.0",{"symbol":str}), sv("S","2.0",{"symbol":str,"volume":int})).generate_report()
        assert not report.is_breaking
        assert any(c.change_type == ChangeType.FIELD_ADDED for c in report.changes)


class TestFieldRemoved:
    def test_is_breaking(self):
        report = SchemaDiff(sv("S","1.0",{"symbol":str,"price":float}), sv("S","2.0",{"symbol":str})).generate_report()
        assert report.is_breaking
        assert any(c.change_type == ChangeType.FIELD_REMOVED and c.field_name == "price" for c in report.breaking_changes)


class TestTypeChanged:
    def test_is_breaking(self):
        report = SchemaDiff(sv("S","1.0",{"value":int}), sv("S","2.0",{"value":str})).generate_report()
        assert report.is_breaking
        change = next(c for c in report.changes if c.field_name == "value")
        assert change.change_type == ChangeType.TYPE_CHANGED
        assert change.old_value == "int" and change.new_value == "str"


class TestRenameHeuristic:
    def test_rename_detected(self):
        report = SchemaDiff(sv("S","1.0",{"price":float,"symbol":str}), sv("S","2.0",{"close_price":float,"symbol":str})).generate_report()
        assert report.is_breaking
        rename = next(c for c in report.changes if c.change_type == ChangeType.FIELD_RENAMED)
        assert rename.old_value == "price" and rename.new_value == "close_price"

    def test_ambiguous_types_no_rename(self):
        report = SchemaDiff(sv("S","1.0",{"a":float,"b":float}), sv("S","2.0",{"c":float,"d":float})).generate_report()
        assert ChangeType.FIELD_RENAMED not in {c.change_type for c in report.changes}

    def test_no_changes_identical(self):
        fields = {"symbol": str, "price": float}
        report = SchemaDiff(sv("S","1.0",fields), sv("S","2.0",fields)).generate_report()
        assert not report.is_breaking and len(report.changes) == 0


class TestMigrationReport:
    def test_to_json_valid(self):
        report = SchemaDiff(sv("S","1.0",{"x":str}), sv("S","2.0",{"y":str})).generate_report()
        assert json.loads(report.to_json())["is_breaking"] is True

    def test_breaking_safe_split(self):
        report = SchemaDiff(sv("S","1.0",{"keep":str,"remove":int}), sv("S","2.0",{"keep":str,"added":bool})).generate_report()
        assert len(report.breaking_changes) == 1 and len(report.safe_changes) == 1
