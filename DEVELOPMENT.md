# Development Setup Guide

This guide helps maintain code quality and prevent formatting issues in the Spoticron project.

## Quick Setup

```bash
# Install development dependencies
make install-dev

# Setup pre-commit hooks (recommended)
make setup-pre-commit

# Format code before committing
make format

# Check formatting and linting
make lint
```

## Automated Tools

### 1. Pre-commit Hooks

Pre-commit hooks automatically run before each commit to check:

- Code formatting (Black)
- Import sorting (isort)
- Basic linting (flake8)
- Trailing whitespace removal
- YAML syntax checking

**Setup:**

```bash
pip install pre-commit
pre-commit install
```

### 2. VS Code Integration

VS Code is configured to:

- Auto-format on save with Black
- Auto-sort imports with isort
- Show linting errors inline
- Use the project's virtual environment

**Required Extensions:**

- Python (ms-python.python)
- Black Formatter (ms-python.black-formatter)
- isort (ms-python.isort)

### 3. Manual Commands

Format code:

```bash
black .
isort .
```

Check formatting:

```bash
black --check --diff .
isort --check-only --diff .
flake8 .
```

## Configuration Files

- `.pre-commit-config.yaml` - Pre-commit hook configuration
- `pyproject.toml` - Tool configurations (Black, isort, pytest, etc.)
- `.vscode/settings.json` - VS Code editor settings
- `requirements-dev.txt` - Development dependencies
- `Makefile` - Common development tasks

## CI/CD Integration

The project pipeline checks:

1. **Black formatting** - `black --check --diff .`
2. **Import sorting** - `isort --check-only --diff .`
3. **Linting** - `flake8 .`
4. **Type checking** - `pylance` (in IDE)

## Best Practices

1. **Always run pre-commit hooks**: `pre-commit run --all-files`
2. **Use make commands**: `make format` before committing
3. **Enable VS Code auto-format**: Formats on save automatically
4. **Check before pushing**: `make lint` to verify everything passes

## Troubleshooting

**Pre-commit fails on formatting:**

```bash
make format  # Auto-fix formatting
git add .    # Re-stage files
git commit   # Try commit again
```

**Import sorting issues:**

```bash
isort .      # Fix import order
black .      # Ensure formatting is still correct
```

**Line length violations:**

- All tools are configured for 88-character lines
- Black will automatically wrap long lines
- Manual wrapping may be needed for comments/strings

## Tool Versions

- Black: 25.9.0
- isort: 5.13.2
- flake8: 7.0.0
- pre-commit: 4.3.0

Keep these updated regularly for the latest features and bug fixes.
