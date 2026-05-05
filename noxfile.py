"""Nox configuration for automated quality checks, formatting, and testing.

This file automates:
- Clean: remove cache dirs and build artifacts (including .egg-info)
- Formatting: ruff format
- Linting: ruff check
- Type Checking: mypy + mypy-upgrade
- Security Scanning: bandit (code), pip-audit (dependencies)
- Testing: pytest
- Test Coverage: coverage reporting
"""

import shutil
import subprocess  # nosec B404
import sys
import tempfile
from pathlib import Path

import nox


# --- CONFIGURATION ---
nox.options.sessions = [
    "format_code",
    "lint",
    "typecheck",
    "security",
    "dependency_check",
    "coverage",
    "clean",
]

# Path to the shared virtual environment
SHARED_VENV_DIR = Path(".venv") / "shared"
LOCATIONS = ["."]

# Cache dirs/files to remove (Safe to regenerate).
# Added build, dist, and *.egg-info for a truly clean state.
_CACHE_DIRS = (
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "build",
    "dist",
    "*.egg-info",
    ".coverage",
)
_CACHE_FILES = (".coverage", "coverage.xml")
_SKIP_PREFIXES = (".venv", ".nox")

# --- HELPERS ---


def ensure_shared_venv(session: nox.Session) -> None:
    """Ensure the shared virtual environment exists and is set up."""
    if not SHARED_VENV_DIR.exists():
        session.log(f"Creating shared virtual environment at {SHARED_VENV_DIR}...")
        # Use sys.executable to ensure we use the same Python version
        subprocess.run(
            [sys.executable, "-m", "venv", str(SHARED_VENV_DIR)],
            check=True,
        )

    pip_exe = get_venv_executable("pip")

    # Universal check for requirements.txt
    if Path("requirements.txt").exists():
        session.run(
            pip_exe, "install", "-r", "requirements.txt", external=True, silent=True
        )

    # Attempt to install the package itself
    # We use success_codes=[0, 1] because linting can often happen without a full install
    session.log("Installing project package...")
    session.run(
        pip_exe, "install", "-e", ".", external=True, silent=True, success_codes=[0, 1]
    )

    # Update session environment to use the shared venv
    bin_dir = "Scripts" if sys.platform == "win32" else "bin"
    path_sep = ";" if sys.platform == "win32" else ":"

    venv_bin_path = SHARED_VENV_DIR / bin_dir
    session.env["VIRTUAL_ENV"] = str(SHARED_VENV_DIR)
    session.env["PATH"] = f"{venv_bin_path}{path_sep}{session.env.get('PATH', '')}"


def get_venv_executable(name: str) -> str:
    """Get the path to an executable in the shared venv."""
    bin_dir = "Scripts" if sys.platform == "win32" else "bin"
    suffix = ".exe" if sys.platform == "win32" else ""
    return str(SHARED_VENV_DIR / bin_dir / f"{name}{suffix}")


def _under_skip(path: Path, root: Path) -> bool:
    """True if path is under any _SKIP_PREFIXES dir."""
    try:
        rel = path.relative_to(root)
        parts = rel.parts
        return any(parts and parts[0] == prefix for prefix in _SKIP_PREFIXES)
    except ValueError:
        return True


# --- SESSIONS ---


@nox.session(venv_backend="none")
def format_code(session: nox.Session) -> None:
    """Auto-format code using Ruff."""
    ensure_shared_venv(session)
    session.run(get_venv_executable("ruff"), "format", *LOCATIONS)
    session.run(
        get_venv_executable("ruff"),
        "check",
        "--fix",
        "--unsafe-fixes",
        *LOCATIONS,
        success_codes=[0, 1],
    )


@nox.session(venv_backend="none")
def lint(session: nox.Session) -> None:
    """Lint code using Ruff."""
    ensure_shared_venv(session)
    session.run(get_venv_executable("ruff"), "check", *LOCATIONS)


@nox.session(venv_backend="none")
def typecheck(session: nox.Session) -> None:
    """Run mypy and use mypy-upgrade to silence new errors."""
    ensure_shared_venv(session)

    mypy_targets = [d for d in LOCATIONS if d != "noxfile.py"]

    with tempfile.NamedTemporaryFile(
        "w+", delete=False, encoding="utf-8", suffix=".txt"
    ) as report_file:
        report_path = Path(report_file.name)
        session.run(
            get_venv_executable("mypy"),
            *mypy_targets,
            success_codes=[0, 1, 2],
            stdout=report_file,
            stderr=report_file,
        )

    output = report_path.read_text(encoding="utf-8")

    if "error:" in output and "Found" in output:
        session.log("Type errors found. Running mypy-upgrade...")
        session.run(
            get_venv_executable("mypy-upgrade"),
            "--report",
            str(report_path),
            success_codes=[0, 1],
        )
        report_path.unlink(missing_ok=True)
        # Final verification
        session.run(get_venv_executable("mypy"), *mypy_targets)
    else:
        report_path.unlink(missing_ok=True)
        session.log("Mypy found no issues.")


@nox.session(venv_backend="none")
def security(session: nox.Session) -> None:
    """Scan for security vulnerabilities with Bandit."""
    ensure_shared_venv(session)
    bandit_args = ["-ll", "-r", "."]
    if Path("pyproject.toml").exists():
        bandit_args.extend(["-c", "pyproject.toml"])
    session.run(get_venv_executable("bandit"), *bandit_args, success_codes=[0, 1])


@nox.session(venv_backend="none")
def dependency_check(session: nox.Session) -> None:
    """Check dependencies for known vulnerabilities with pip-audit."""
    ensure_shared_venv(session)
    if Path("requirements.txt").exists():
        session.run(get_venv_executable("pip-audit"), "-r", "requirements.txt")
    else:
        session.run(get_venv_executable("pip-audit"))


@nox.session(venv_backend="none")
def coverage(session: nox.Session) -> None:
    """Generate a test coverage report."""
    ensure_shared_venv(session)
    test_path = "tests/" if Path("tests").exists() else "."
    session.run(
        get_venv_executable("pytest"),
        "-v",
        "--cov=.",
        "--cov-report=term-missing",
        test_path,
        success_codes=[0, 5],
    )


@nox.session(venv_backend="none")
def clean(session: nox.Session) -> None:
    """Remove cache dirs, build artifacts, and egg-info."""
    root = Path.cwd()
    for pattern in _CACHE_DIRS:
        for path in root.rglob(pattern):
            if _under_skip(path, root):
                continue

            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
                session.log(f"Removed directory: {path.relative_to(root)}")
            elif path.is_file():
                path.unlink(missing_ok=True)
                session.log(f"Removed file: {path.relative_to(root)}")
