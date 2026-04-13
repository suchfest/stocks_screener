# CI/CD Quality Checks

Universal Nox configuration for automated code quality checks, formatting, and testing.

## Quick Start

```bash
nox
```

This runs all quality checks: formatting, linting, type checking, security scanning, dependency checks, test coverage, and clean.

## Available Sessions

- `format_code` - Auto-format code using Ruff
- `lint` - Lint code using Ruff
- `typecheck` - Type checking with Mypy
- `security` - Security scanning with Bandit (code)
- `dependency_check` - Check dependencies for known vulnerabilities (pip-audit)
- `coverage` - Test coverage reporting with pytest
- `clean` - Remove cache dirs (e.g. `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`)

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run all sessions:
```bash
nox
```

Run a specific session:
```bash
nox -s format_code
nox -s lint
nox -s typecheck
nox -s security
nox -s dependency_check
nox -s coverage
nox -s clean
```

## Pre-commit (optional)

To run the same checks (except `clean`) automatically on every `git commit`:

```bash
pip install -r requirements.txt   # or run nox once to create the venv
pre-commit install
```

After that, each commit runs: format_code, lint, typecheck, security, dependency_check, coverage. If any fail, the commit is blocked.
