from pathlib import Path

import pytest
from fastapi import FastAPI

from tests.contract import checked_client

TESTS = Path(__file__).resolve().parent


def test_the_check_on_every_error_answer_bites() -> None:
    # FastAPI's own 404 is {"detail": "Not Found"}: the checked client refuses it.
    with pytest.raises(AssertionError):
        checked_client(FastAPI()).get("/nothing-here")


def test_no_test_builds_a_client_that_skips_the_check() -> None:
    # Split, so this file does not find itself.
    built = "TestClient" + "("
    found = [
        str(path.relative_to(TESTS))
        for path in TESTS.rglob("*.py")
        if path.name != "contract.py" and built in path.read_text(encoding="utf-8")
    ]

    assert found == [], "reach the API through tests.contract.checked_client"
