"""The shape every error answer keeps, checked on each one a test receives (step 12).

Tests reach the API through `checked_client`, so no error answer goes unchecked: the four fields,
the code's status, the hint rule and the size budget. `test_contract.py` finds any other client.
"""

from typing import Any, get_args

import httpx2
from fastapi.testclient import TestClient
from starlette.types import ASGIApp

from core.errors import CODES, FieldCode
from tests.budgets import ERROR_BYTES

FIELD_PLACES = {"body", "query", "header", "path"}


def checked_client(app: ASGIApp, api: str = "", raise_server_exceptions: bool = True) -> TestClient:
    """A test client checking every error answer from an address under `api`, the API's prefix.

    `serve`'s app also serves the UI, whose 404 is the static files', not the API's: `api="/api"`.
    """
    checked = TestClient(app, raise_server_exceptions=raise_server_exceptions)

    def check(response: httpx2.Response) -> None:
        if response.status_code >= 400 and response.request.url.path.startswith(api):
            response.read()
            check_error(response)

    checked.event_hooks = {"request": [], "response": [check]}
    return checked


def check_error(response: httpx2.Response) -> None:
    assert len(response.content) <= ERROR_BYTES, f"{len(response.content)} B: {response.text}"
    body: dict[str, Any] = response.json()
    assert isinstance(body, dict), body
    assert body.keys() == {"code", "message", "details", "hint"}, body
    code = CODES[body["code"]]
    assert response.status_code == code.status, body
    assert isinstance(body["message"], str) and body["message"], body
    details: dict[str, Any] = body["details"]
    assert isinstance(details, dict), body
    if code.hint:
        assert isinstance(body["hint"], str) and body["hint"], body
    else:
        assert body["hint"] is None, body
    problems: list[dict[str, Any]] = details.get("problems", [])
    for problem in problems:
        assert problem.keys() == {"field", "code", "message"}, problem
        assert problem["field"].split(".")[0] in FIELD_PLACES, problem
        assert problem["code"] in get_args(FieldCode), problem
        assert isinstance(problem["message"], str) and problem["message"], problem
