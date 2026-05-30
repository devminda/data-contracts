# Changelog

All notable changes to this project will be documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [1.0.0] - 2026-05-29
### Added
- `ContractBase` metaclass for automatic schema registration
- `@contract` decorator as alternative API
- `SchemaDiff` engine with rename heuristic detection
- `ValidationResult` with errors and warnings
- `NotificationBus` for consumer alerting
- `SchemaSourceInspector` for AST-based static analysis
- CLI: `data-contracts diff` and `data-contracts validate`
