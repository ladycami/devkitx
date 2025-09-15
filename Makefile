# Makefile for devtools-py package

.PHONY: help install install-dev clean lint test build validate version-current version-bump-patch version-bump-minor version-bump-major

# Default target
help:
	@echo "Available targets:"
	@echo "  install          Install package in development mode"
	@echo "  install-dev      Install package with development dependencies"
	@echo "  clean           Clean build artifacts"
	@echo "  lint            Run linting checks (ruff, black, mypy)"
	@echo "  test            Run test suite with coverage"
	@echo "  validate        Run full validation checks"
	@echo "  build           Build package (with validation)"
	@echo "  build-skip-validation  Build package (skip validation)"
	@echo "  version-current Show current version"
	@echo "  version-bump-patch     Bump patch version"
	@echo "  version-bump-minor     Bump minor version"
	@echo "  version-bump-major     Bump major version"

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Cleaning
clean:
	rm -rf dist/ build/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Code quality
lint:
	python -m ruff check src/devtools_py tests
	python -m black --check src/devtools_py tests
	python -m mypy src/devtools_py

format:
	python -m ruff check --fix src/devtools_py tests
	python -m black src/devtools_py tests

# Testing
test:
	python -m pytest --cov=devtools_py --cov-report=term-missing

test-verbose:
	python -m pytest -v --cov=devtools_py --cov-report=term-missing --cov-report=html

# Validation and building
validate:
	python scripts/build_validate.py

build:
	python scripts/build.py --clean

build-skip-validation:
	python scripts/build.py --clean --skip-validation

# Version management
version-current:
	python scripts/version_manager.py current

version-bump-patch:
	python scripts/version_manager.py bump patch

version-bump-minor:
	python scripts/version_manager.py bump minor

version-bump-major:
	python scripts/version_manager.py bump major

# Release workflow
release-patch: version-bump-patch build
	@echo "Patch release ready for deployment"

release-minor: version-bump-minor build
	@echo "Minor release ready for deployment"

release-major: version-bump-major build
	@echo "Major release ready for deployment"