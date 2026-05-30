# data-contracts

Schema evolution framework for Python data pipelines — detects breaking changes before they break your consumers.

## The problem

Your 50 pipelines consume an API that returns:
```json
{ "price": 100 }
```
One day it silently changes to:
```json
{ "close_price": 100 }
```
Everything breaks. This framework detects that automatically.

## Quick start

```python
from data_contracts import ContractBase, SchemaDiff

class TradeSchemaV1(ContractBase):
    __version__ = "1.0.0"
    symbol: str
    price: float       # <- this field will be renamed
    volume: int

class TradeSchemaV2(ContractBase):
    __version__ = "2.0.0"
    symbol: str
    close_price: float  # <- breaking: renamed from price
    volume: int
    timestamp: str      # <- safe: additive

report = SchemaDiff.from_registry("TradeSchemaV1", "TradeSchemaV2").generate_report()
report.print_report()
# 🔴 BREAKING — [FIELD_RENAMED] price → close_price
```

## Installation

```bash
pip install data-contracts
# or from source:
git clone https://github.com/yourname/data-contracts
cd data-contracts && make install
```

## CLI

```bash
data-contracts diff schema_v1.py schema_v2.py
data-contracts diff schema_v1.py schema_v2.py --format json
data-contracts validate schema.py --data row.json
```

## Features

- **Auto-registration** — schemas register themselves on class definition via metaclass
- **Breaking change detection** — field removed, renamed, type changed
- **Rename heuristic** — detects `price → close_price` as a rename, not remove+add
- **Consumer notifications** — notify downstream teams when breaking changes land
- **AST inspection** — analyse schema source without importing it
- **CLI** — diff any two schema files from the terminal

## Advanced Python concepts demonstrated

`metaclasses` · `decorators` · `dataclasses` · `type hints` · `inspect` · `AST` · `observer pattern`

## Project structure

```
src/data_contracts/
├── contracts.py      # ContractMeta metaclass + @contract decorator
├── diff.py           # SchemaDiff engine + MigrationReport
├── validation.py     # ValidationResult + type-checking engine
├── registry.py       # SchemaRegistry + SchemaVersion
├── notifications.py  # NotificationBus + Consumer
└── cli.py            # Click CLI
```

## Running tests

```bash
make test        # pytest + coverage
make lint        # ruff
make typecheck   # mypy
make all         # everything
```

## Background

Data contracts are how companies like Airbnb, Netflix, and Uber enforce reliability across hundreds of pipelines. This framework implements the core primitive: a schema that knows its own version history and can detect breaking changes between versions.
