"""Nox configuration for automated quality checks, formatting, and testing.

This file automates:
- Clean: remove cache dirs (__pycache__, .pytest_cache, etc,but not .venv)
- Formatting: ruff format
- Linting: ruff check
- Type Checking: mypy + (optional) mypy-upgrade to silence newly introduced errors
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


nox.options.sessions = [
    "format_code",
    "lint",
    "typecheck",
    "security",
    "dependency_check",
    "coverage",
    "clean",
]

# path to the shared virtual environment
SHARED_VENV_DIR = Path(".venv") / "shared"

# define directories/files to check
LOCATIONS = ["."]


def ensure_shared_venv(session: nox.Session) -> None:
    """Ensure the shared virtual environment exists and is set up."""
    # create new isolated venv for consistent dependency
    if not SHARED_VENV_DIR.exists():
        session.log(f"Creating shared virtual environment at {SHARED_VENV_DIR}...")
        subprocess.run(  # nosec B603
            [sys.executable, "-m", "venv", str(SHARED_VENV_DIR)],
            check=True,
        )

    # determine pip executable path based on platform
    if sys.platform == "win32":
        pip_exe = SHARED_VENV_DIR / "Scripts" / "pip.exe"
    else:
        pip_exe = SHARED_VENV_DIR / "bin" / "pip"

    # install dependencies if not already installed
    result = subprocess.run(  # nosec B603
        [str(pip_exe), "install", "-r", "requirements.txt"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        session.error(f"Failed to install requirements.txt:\n{result.stderr}")

    # try to install the package in editable mode first, then regular if that fails
    result = subprocess.run(  # nosec B603
        [str(pip_exe), "install", "-e", "."],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        # if editable install fails, try regular install
        result = subprocess.run(  # nosec B603
            [str(pip_exe), "install", "."],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            # log the error but don't fail as package installation may not be critical
            session.log(f"Warning: Could not install package: {result.stderr}")
            session.log(
                "Continuing anyway - package may not be required for all sessions"
            )

    # set the session to use our shared venv
    if sys.platform == "win32":
        bin_dir = SHARED_VENV_DIR / "Scripts"
        path_sep = ";"
    else:
        bin_dir = SHARED_VENV_DIR / "bin"
        path_sep = ":"

    # update PATH to prioritize venv binaries
    current_path = session.env.get("PATH", "")
    session.env["VIRTUAL_ENV"] = str(SHARED_VENV_DIR)
    session.env["PATH"] = str(bin_dir) + path_sep + current_path


def get_venv_executable(name: str) -> str:
    """Get the path to an executable in the shared venv."""
    if sys.platform == "win32":
        exe_path = SHARED_VENV_DIR / "Scripts" / f"{name}.exe"
    else:
        exe_path = SHARED_VENV_DIR / "bin" / name

    return str(exe_path)


def install_dev_tools(session: nox.Session) -> None:
    """Install all development tools from requirements.txt."""
    # ensure shared venv exists and is set up
    ensure_shared_venv(session)


@nox.session(venv_backend="none")
def format_code(session: nox.Session) -> None:
    """Auto-format code using Ruff."""
    install_dev_tools(session)
    session.log(f"Running formatters on: {', '.join(LOCATIONS)}")

    # run the formatter
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
    install_dev_tools(session)
    session.log(f"Running linters on: {', '.join(LOCATIONS)}")

    session.run(get_venv_executable("ruff"), "check", *LOCATIONS)


@nox.session(venv_backend="none")
def typecheck(session: nox.Session) -> None:
    """Run mypy and use mypy-upgrade to silence new errors."""
    install_dev_tools(session)

    # filter out noxfile.py from mypy targets if present
    mypy_targets = [d for d in LOCATIONS if d != "noxfile.py"]
    session.log(f"Running mypy on: {', '.join(mypy_targets)}")

    with tempfile.NamedTemporaryFile(
        "w+", delete=False, encoding="utf-8", suffix=".txt"
    ) as report_file:
        report_path = Path(report_file.name)

        session.log("Step 1: Running mypy and capturing output...")
        session.run(
            get_venv_executable("mypy"),
            *mypy_targets,
            # allow mypy to 'fail' so we can process its output
            success_codes=[0, 1, 2],
            stdout=report_file,
            stderr=report_file,
        )

    output = report_path.read_text(encoding="utf-8")

    # exit early if mypy had a configuration error
    if "is not a valid Python package name" in output or "usage: mypy" in output:
        report_path.unlink(missing_ok=True)
        session.error(f"Mypy configuration error. Full output:\n{output}")

    # exit early if there are no type errors to fix
    has_type_errors = "error:" in output and "Found" in output
    if not has_type_errors:
        report_path.unlink(missing_ok=True)
        session.log("Mypy found no issues. Skipping upgrade.")
        return

    session.log("Step 2: Type errors found. Running mypy-upgrade...")
    session.run(
        get_venv_executable("mypy-upgrade"),
        "--report",
        str(report_path),
        success_codes=[0, 1],
    )
    report_path.unlink(missing_ok=True)

    session.log("Step 3: Verifying with a final mypy check...")
    # this run will fail the session if errors persist after the upgrade attempt
    session.run(get_venv_executable("mypy"), *mypy_targets)


@nox.session(venv_backend="none")
def security(session: nox.Session) -> None:
    """Scan for security vulnerabilities with Bandit."""
    install_dev_tools(session)
    session.log("Scanning for security vulnerabilities with Bandit...")
    # the '-r .' scans the entire repository recursively
    # use -ll to suppress manager/tester warnings about test names in comments
    bandit_args = ["-ll", "-r", "."]
    # only use config file if it exists
    if Path("pyproject.toml").exists():
        bandit_args.extend(["-c", "pyproject.toml"])
    session.run(
        get_venv_executable("bandit"),
        *bandit_args,
        success_codes=[0, 1],  # dont fail if only low severity issues found
    )


@nox.session(venv_backend="none")
def dependency_check(session: nox.Session) -> None:
    """Check dependencies for known vulnerabilities with pip-audit."""
    install_dev_tools(session)
    session.log("Checking dependencies for known vulnerabilities (pip-audit)...")
    session.run(get_venv_executable("pip-audit"), "-r", "requirements.txt")


@nox.session(venv_backend="none")
def coverage(session: nox.Session) -> None:
    """Generate a test coverage report."""
    install_dev_tools(session)

    # run pytest with coverage flags. Pytest will auto-discover tests if no path is specified
    test_path = "tests/" if Path("tests").exists() else "."
    session.run(
        get_venv_executable("pytest"),
        "-v",  # verbose: show each test name as it runs
        "--cov=.",
        "--cov-report=term-missing",
        test_path,
        success_codes=[0, 5],  # 5 = no tests collected
    )


# Cache dirs/files to remove (all in .gitignore, safe to regenerate). Skip .venv and .nox.
_CACHE_DIRS = ("__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache")
_CACHE_FILES = (".coverage",)
_SKIP_PREFIXES = (".venv", ".nox")


def _under_skip(path: Path, root: Path) -> bool:
    """True if path is under any _SKIP_PREFIXES dir."""
    try:
        rel = path.relative_to(root)
    except ValueError:
        return True
    parts = rel.parts
    return any(parts and parts[0] == prefix for prefix in _SKIP_PREFIXES)


@nox.session(venv_backend="none")
def clean(session: nox.Session) -> None:
    """Remove cache dirs (__pycache__, .pytest_cache, .ruff_cache, .mypy_cache, etc.)."""
    root = Path.cwd()
    for name in _CACHE_DIRS:
        for path in root.rglob(name):
            if path.is_dir() and not _under_skip(path, root):
                shutil.rmtree(path, ignore_errors=True)
    for name in _CACHE_FILES:
        for path in root.rglob(name):
            if path.is_file() and not _under_skip(path, root):
                path.unlink(missing_ok=True)
