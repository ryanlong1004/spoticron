# Makefile for Spoticron development tasks

.PHONY: help install install-dev format lint test clean setup-pre-commit

# Default target
help:
	@echo "Available commands:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo "  format          Auto-format code with black and isort"
	@echo "  lint            Run linting checks"
	@echo "  test            Run tests"
	@echo "  setup-pre-commit Install and setup pre-commit hooks"
	@echo "  clean           Clean up temporary files"

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev: install
	pip install -r requirements-dev.txt

# Auto-format code
format:
	black .
	isort .

# Run linting checks
lint:
	black --check --diff .
	isort --check-only --diff .
	flake8 .

# Run tests
test:
	python -m pytest tests/ -v

# Setup pre-commit hooks
setup-pre-commit: install-dev
	pre-commit install
	pre-commit run --all-files

# Clean temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
