import re
from typing import Any

import pytest
from fastapi import FastAPI

from core.change import HEADERS_HINT, Change
from core.server import create_api
from tests.contract import checked_client
from tests.sample import sample_api

CHANGING = {"POST", "PATCH", "DELETE"}


def test_a_changing_request_without_its_headers_is_not_made() -> None:
    changes: list[Change] = []

    response = checked_client(sample_api(changes)).post("/samples/1", json={"name": "a"})

    assert response.status_code == 400
    assert response.json()["details"]["problems"] == [
        {
            "field": "header.Idempotency-Key",
            "code": "missing",
            "message": "`header.Idempotency-Key` is missing.",
        },
        {"field": "header.Actor", "code": "missing", "message": "`header.Actor` is missing."},
    ]
    assert changes == []


def test_a_header_problem_is_hinted_with_the_headers_rule() -> None:
    # The address's detail leaves the headers out (the agent never writes them): the hint says them.
    response = checked_client(sample_api()).post("/samples/1", json={"name": "a"})

    assert response.json()["hint"] == HEADERS_HINT


def test_header_and_body_problems_are_hinted_with_both() -> None:
    response = checked_client(sample_api()).post("/samples/1", json={})

    assert response.json()["hint"] == (
        f"{HEADERS_HINT} `GET /api?path=/samples/{{id}}` gives what this address takes."
    )


@pytest.mark.parametrize(
    ("headers", "field", "code"),
    [
        ({"Idempotency-Key": "", "Actor": "ui"}, "header.Idempotency-Key", "not_allowed"),
        ({"Idempotency-Key": "k" * 129, "Actor": "ui"}, "header.Idempotency-Key", "out_of_range"),
        (
            {"Idempotency-Key": "k\xe9".encode("latin-1"), "Actor": "ui"},
            "header.Idempotency-Key",
            "not_allowed",
        ),
        ({"Idempotency-Key": "list-1", "Actor": "core"}, "header.Actor", "not_allowed"),
    ],
)
def test_a_header_out_of_its_rule_is_not_made(
    headers: dict[str, Any], field: str, code: str
) -> None:
    # `core` is only the core's own history records' actor (step 6).
    changes: list[Change] = []

    response = checked_client(sample_api(changes)).post(
        "/samples/1", json={"name": "a"}, headers=headers
    )

    assert [(p["field"], p["code"]) for p in response.json()["details"]["problems"]] == [
        (field, code)
    ]
    assert changes == []


def test_the_endpoint_receives_the_key_and_the_actor() -> None:
    changes: list[Change] = []
    key = "".join(chr(code) for code in range(0x20, 0x7F))[:128].strip()

    response = checked_client(sample_api(changes)).post(
        "/samples/1", json={"name": "a"}, headers={"Idempotency-Key": key, "Actor": "ui"}
    )

    assert response.status_code == 200
    assert changes == [Change(key=key, actor="ui")]


def test_a_read_takes_neither_header() -> None:
    assert checked_client(sample_api()).get("/samples/1").status_code == 200


def unguarded(api: FastAPI) -> list[str]:
    """Each changing route that does not refuse a request without the two headers."""
    # Walked in the OpenAPI document, where every included router's operations are.
    found: list[str] = []
    checked = checked_client(api)
    paths: dict[str, Any] = api.openapi()["paths"]
    for address, item in paths.items():
        for method in (method.upper() for method in item):
            if method not in CHANGING:
                continue
            # Each path parameter filled with a word: whatever else is wrong, the headers are named.
            path = re.sub(r"\{[^}]+\}", "x", address)
            response = checked.request(method, path)
            body: Any = response.json() if response.status_code == 400 else {"details": {}}
            fields = {problem["field"] for problem in body["details"].get("problems", [])}
            if not {"header.Idempotency-Key", "header.Actor"} <= fields:
                found.append(f"{method} {address}")
    return found


def test_every_changing_route_refuses_a_request_without_the_headers() -> None:
    # The sample API carries the core's own routes too, so each new changing endpoint is tried here.
    assert unguarded(sample_api()) == []


def test_the_walk_finds_a_changing_route_that_forgot_them() -> None:
    api = create_api(core_id="k3v9q2mz7a")

    @api.post("/careless", summary="Change without the headers")
    def careless() -> None: ...

    assert unguarded(api) == ["POST /careless"]


def test_the_ui_types_carry_both_headers_on_a_changing_operation() -> None:
    parameters = sample_api().openapi()["paths"]["/samples/{id}"]["post"]["parameters"]
    headers = {p["name"]: p for p in parameters if p["in"] == "header"}

    assert headers.keys() == {"Idempotency-Key", "Actor"}
    assert all(header["required"] for header in headers.values())
    assert headers["Actor"]["schema"]["enum"] == ["agent", "ui"]
    assert all(header["description"] for header in headers.values())
