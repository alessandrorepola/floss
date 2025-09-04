# Makefile for PyFault development
.PHONY: help install install-dev format lint test quality clean

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install package in development mode"
	@echo "  install-dev  - Install package with development dependencies"
	@echo "  format       - Format code with black and isort"
	@echo "  lint         - Run all linting checks (black, isort, flake8, mypy)"
	@echo "  test         - Run tests with pytest"
	@echo "  quality      - Run all quality checks (lint + test)"
	@echo "  clean        - Remove build artifacts and cache files"
	@echo "  pre-commit   - Install and run pre-commit hooks"

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e .[dev]

# Code formatting
format:
	isort pyfault/
	black pyfault/

# Linting and type checking
lint:
	@echo "🔍 Running code quality checks..."
	black --check --diff pyfault/
	isort --check-only --diff pyfault/
	flake8 pyfault/
	mypy pyfault/

# Testing
test:
	pytest tests/ -v

# Run all quality checks
quality: lint test
	@echo "✅ All quality checks passed!"

# Pre-commit hooks
pre-commit:
	pre-commit install
	pre-commit run --all-files

# Clean up
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
