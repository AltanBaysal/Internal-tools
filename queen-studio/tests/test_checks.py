"""The checks run with the tests (CODE-STANDARD, Checks): a change is done once none reports."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check(*command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", *command], cwd=ROOT, capture_output=True, text=True, check=False
    )


def test_ruff_finds_nothing() -> None:
    found = check("ruff", "check", ".")

    assert found.returncode == 0, found.stdout + found.stderr


def test_ruff_would_reformat_nothing() -> None:
    found = check("ruff", "format", "--check", ".")

    assert found.returncode == 0, found.stdout + found.stderr


def test_pyright_strict_finds_nothing() -> None:
    # Told which Python to read the packages from, so it checks against what the suite runs on.
    found = check("pyright", "--pythonpath", sys.executable)

    assert found.returncode == 0, found.stdout + found.stderr
