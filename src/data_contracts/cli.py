import importlib.util
import json
import sys
from pathlib import Path

import click

from data_contracts.diff import SchemaDiff
from data_contracts.registry import SchemaRegistry


def _load_module(path: str) -> None:
    p = Path(path).resolve()
    spec = importlib.util.spec_from_file_location(p.stem, p)
    if spec is None or spec.loader is None:
        raise click.ClickException(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]


@click.group()
def main() -> None:
    """data-contracts — schema evolution and validation toolkit."""


@main.command()
@click.argument("old_schema", metavar="OLD_SCHEMA.py")
@click.argument("new_schema", metavar="NEW_SCHEMA.py")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
def diff(old_schema: str, new_schema: str, fmt: str) -> None:
    """Diff two schema files and report breaking changes."""
    SchemaRegistry.clear()
    _load_module(old_schema)
    old_schemas = SchemaRegistry.list_schemas()
    _load_module(new_schema)

    if not old_schemas:
        raise click.ClickException(f"No schemas found in {old_schema}")

    all_schemas = SchemaRegistry.list_schemas()
    new_schemas = [s for s in all_schemas if s not in old_schemas]
    if not new_schemas:
        raise click.ClickException(f"No new schemas found in {new_schema}")

    old_sv = SchemaRegistry.get_latest(old_schemas[0])
    new_sv = SchemaRegistry.get_latest(new_schemas[0])

    if old_sv is None or new_sv is None:
        raise click.ClickException("Could not retrieve schema versions")

    report = SchemaDiff(old_sv, new_sv).generate_report()

    if fmt == "json":
        click.echo(report.to_json())
    else:
        report.print_report()

    sys.exit(1 if report.is_breaking else 0)


@main.command()
@click.argument("schema_file", metavar="SCHEMA.py")
@click.option("--data", "data_file", required=True, help="JSON file with a single data row")
def validate(schema_file: str, data_file: str) -> None:
    """Validate a JSON data row against a schema file."""
    SchemaRegistry.clear()
    _load_module(schema_file)
    schemas = SchemaRegistry.list_schemas()
    if not schemas:
        raise click.ClickException(f"No schemas found in {schema_file}")
    sv = SchemaRegistry.get_latest(schemas[0])
    if sv is None:
        raise click.ClickException("Could not retrieve schema")
    with open(data_file) as f:
        data = json.load(f)
    from data_contracts.validation import validate_data
    result = validate_data(sv.fields, data)
    click.echo(result.summary())
    sys.exit(0 if result.is_valid else 1)
