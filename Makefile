.PHONY: install test lint typecheck all clean

install:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src/ tests/

typecheck:
	mypy src/

all: lint typecheck test

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
