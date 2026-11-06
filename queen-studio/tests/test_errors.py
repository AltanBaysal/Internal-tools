import json
import re
from pathlib import Path
from typing import Annotated, Any

import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient

from core import errors
from core.change import HEADERS_HINT, Change, change
from core.errors import ADDRESS_BYTES, FIELD_BYTES, MESSAGE_BYTES, PROBLEMS_SHOWN, FieldCode
from core.server import create_api, serve
from tests.budgets import ERROR_BYTES
from tests.contract import checked_client
from tests.sample import Made, sample_api

CHANGE = {"Idempotency-Key": "list-1", "Actor": "agent"}


def problems(body: Any) -> list[tuple[str, str]]:
    return [(problem["field"], problem["code"]) for problem in body["details"]["problems"]]


def test_an_error_the_core_raises_comes_with_its_four_fields_and_its_codes_status() -> None:
    response = checked_client(sample_api()).get("/samples/0")

    assert response.status_code == 404
    assert response.json() == {
        "code": "unknown_endpoint",
        "message": "There is no sample 0.",
        "details": {"id": 0},
        "hint": "Ask for 1.",
    }


def test_fastapis_validation_error_is_a_400_naming_each_field() -> None:
    response = checked_client(sample_api()).post(
        "/samples/x", json={"name": 7, "kind": "c", "count": 10, "extra": 1}, headers=CHANGE
    )

    assert response.status_code == 400
    body = response.json()
    assert body["code"] == "invalid_request"
    assert problems(body) == [
        ("path.id", "wrong_type"),
        ("body.name", "wrong_type"),
        ("body.kind", "not_allowed"),
        ("body.count", "out_of_range"),
        ("body.extra", "unknown"),
    ]
    assert body["message"] == "The request has 5 problems; nothing was done."
    assert body["hint"] == "`GET /api?path=/samples/{id}` gives what this address takes."


@pytest.mark.parametrize(
    ("sent", "field", "message"),
    [
        ({}, "body.name", "`body.name` is missing."),
        (
            {"name": "a", "extra": 1},
            "body.extra",
            "`body.extra` is not a field this address takes.",
        ),
        ({"name": 7}, "body.name", "`body.name` must be a string."),
        ({"name": "a", "count": "many"}, "body.count", "`body.count` must be a whole number."),
        ({"name": "a", "kind": "c"}, "body.kind", "`body.kind` must be 'a' or 'b'."),
        ({"name": "a", "count": 0}, "body.count", "`body.count` must be at least 1."),
        ({"name": "a", "count": 10}, "body.count", "`body.count` must be at most 9."),
        ({"name": ""}, "body.name", "`body.name` must have at least 1 character."),
        ({"name": "a" * 21}, "body.name", "`body.name` must have at most 20 characters."),
        ({"name": "a", "place": 3}, "body.place", "`body.place` must be a JSON object."),
        ({"name": "a", "place": {}}, "body.place.frame", "`body.place.frame` is missing."),
        ([], "body", "`body` must be a JSON object."),
    ],
)
def test_one_problem_is_the_whole_message(sent: Any, field: str, message: str) -> None:
    response = checked_client(sample_api()).post("/samples/1", json=sent, headers=CHANGE)

    body = response.json()
    assert body["details"]["problems"] == [
        {"field": field, "code": body["details"]["problems"][0]["code"], "message": message}
    ]
    assert body["message"] == message


def test_a_body_that_is_not_json_says_what_the_parser_said() -> None:
    response = checked_client(sample_api()).post(
        "/samples/1", content=b"{name", headers={**CHANGE, "Content-Type": "application/json"}
    )

    body = response.json()
    assert problems(body) == [("body", "wrong_type")]
    assert body["message"].startswith("`body` is not JSON: Expecting property name")


def test_a_missing_body_is_named() -> None:
    response = checked_client(sample_api()).post("/samples/1", headers=CHANGE)

    assert response.json()["details"]["problems"] == [
        {"field": "body", "code": "missing", "message": "`body` is missing."}
    ]


@pytest.mark.parametrize("path", ["/nothing-here", "/health/"])
def test_an_unknown_address_is_unknown_endpoint_and_points_at_the_index(path: str) -> None:
    # A stray slash is not redirected: FastAPI's redirect names an absolute http:// address, which
    # behind the tunnel's https is the wrong one.
    response = checked_client(create_api(core_id="k3v9q2mz7a")).get(path)

    assert response.status_code == 404
    assert "location" not in response.headers
    assert response.json() == {
        "code": "unknown_endpoint",
        "message": f"`{path}` is not an address of this API.",
        "details": {},
        "hint": "`GET /api` lists every address.",
    }


def test_a_method_the_address_lacks_names_every_method_it_has() -> None:
    # GET, POST and DELETE at /samples/{id} are three routes; the router stops at the first.
    response = checked_client(sample_api()).patch("/samples/1")

    assert response.status_code == 405
    assert response.headers["allow"] == "DELETE, GET, POST"
    assert response.json() == {
        "code": "method_not_allowed",
        "message": "`/samples/{id}` does not take PATCH.",
        "details": {"methods": ["DELETE", "GET", "POST"]},
        "hint": "`/samples/{id}` takes DELETE, GET, POST; "
        "`GET /api?path=/samples/{id}` describes it.",
    }


def test_a_method_the_index_lacks_names_the_index_by_its_address() -> None:
    # The index is the API's root: called `/api`, not `/`.
    response = checked_client(create_api(core_id="k3v9q2mz7a")).post("/")

    assert response.status_code == 405
    assert response.json() == {
        "code": "method_not_allowed",
        "message": "`/api` does not take POST.",
        "details": {"methods": ["GET"]},
        "hint": "`GET /api` is the only call at this address.",
    }


def test_a_query_the_index_does_not_take_has_the_indexs_own_hint() -> None:
    response = checked_client(create_api(core_id="k3v9q2mz7a")).get("/", params={"paht": "/x"})

    assert response.json()["hint"] == ("`GET /api` takes only `path`, an address `GET /api` lists.")


@pytest.fixture
def mounted(tmp_path: Path) -> TestClient:
    """The core as it is served: the API at /api, where the hints' calls are made."""
    ui = tmp_path / "dist"
    ui.mkdir()
    (ui / "index.html").write_text("<p>the page</p>", encoding="utf-8")
    return checked_client(serve(sample_api(), ui), api="/api")


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/api?paht=/health"),
        ("POST", "/api"),
        ("GET", "/api?path=/nothing"),
        ("GET", "/api/nothing"),
        ("PATCH", "/api/samples/1"),
        ("GET", "/api/samples/x"),
        ("GET", "/api/samples/1?zz=1"),
        ("POST", "/api/openapi.json"),
    ],
)
def test_every_call_a_hint_names_answers(mounted: TestClient, method: str, path: str) -> None:
    hint: str = mounted.request(method, path).json()["hint"]

    calls = re.findall(r"`GET (/api[^`]*)`", hint)
    assert calls, hint
    for call in calls:
        assert mounted.get(call).status_code == 200, (hint, call)


def odd_api() -> FastAPI:
    """Routes that fail in the ways a real endpoint may, outside any section of the index."""
    api = sample_api()

    @api.get("/long", summary="A long failure")
    def long() -> None:
        raise RuntimeError("x" * 5000)

    @api.get("/answer", summary="A wrong answer")
    def answer() -> int:
        wrong: Any = "not a number"
        return wrong

    @api.get("/model", summary="A model built wrong")
    def model() -> Made:
        return Made.model_validate({"id": "x"})

    @api.get("/files/{name:path}", summary="A file")
    def file(name: str) -> str:
        return name

    @api.post("/parse", summary="A body FastAPI could not read")
    def parse() -> None:
        raise HTTPException(400, "There was an error parsing the body")

    @api.get("/down", summary="A service status")
    def down() -> None:
        raise HTTPException(503, "Service Unavailable")

    return api


def test_a_long_failure_is_cut_in_the_answer() -> None:
    message = (
        checked_client(odd_api(), raise_server_exceptions=False).get("/long").json()["message"]
    )

    # Cut by bytes as sent: "…" is three.
    assert message == "RuntimeError: " + "x" * (MESSAGE_BYTES - len("RuntimeError: ") - 3) + "…"


@pytest.mark.parametrize(
    ("path", "message"),
    [
        ("/answer", "ResponseValidationError: 1 validation error"),
        ("/model", "ValidationError: 2 validation errors"),
    ],
)
def test_a_validation_failure_inside_says_only_its_type_and_count(path: str, message: str) -> None:
    # Its text carries the value and the source line: those stay in the log.
    body = checked_client(odd_api(), raise_server_exceptions=False).get(path).json()

    assert (body["code"], body["message"]) == ("internal", message)


def test_a_path_converter_is_written_as_the_index_writes_the_address() -> None:
    client = checked_client(odd_api())

    refused = client.patch("/files/a/b").json()
    assert refused["details"] == {"methods": ["GET"]}
    assert (
        refused["hint"] == "`/files/{name}` takes GET; `GET /api?path=/files/{name}` describes it."
    )
    assert client.get("/files/a", params={"zz": "1"}).json()["hint"] == (
        "`GET /api?path=/files/{name}` gives what this address takes."
    )


def test_a_long_unknown_address_is_cut_in_the_message() -> None:
    message = checked_client(create_api(core_id="")).get("/" + "a" * 300).json()["message"]

    assert message == f"`/{'a' * (ADDRESS_BYTES - 4)}…` is not an address of this API."


@pytest.mark.parametrize(
    "name",
    ["n" * 5000, "ğ" * 2000, "\x01" * 2000, '"' * 2000],
    ids=["long", "two-byte", "escaped", "quoted"],
)
def test_a_long_unknown_name_is_cut_by_the_bytes_it_is_sent_in(name: str) -> None:
    # A control character is six bytes in JSON, `"` two, `ğ` two: the cut counts what is sent.
    client = checked_client(sample_api())

    for response in [
        client.get("/samples/1", params={name: "1"}),
        client.post("/samples/1", json={"name": "a", name: 1}, headers=CHANGE),
    ]:
        assert response.status_code == 400
        field = response.json()["details"]["problems"][0]["field"]
        assert len(json.dumps(field, ensure_ascii=False).encode()) - 2 <= FIELD_BYTES
        assert len(response.content) <= ERROR_BYTES


def test_many_problems_list_the_first_and_count_the_rest() -> None:
    params = {f"unknown{number}": "1" for number in range(300)}

    response = checked_client(sample_api()).get("/samples/1", params=params)

    body = response.json()
    assert body["message"] == "The request has 300 problems; nothing was done."
    assert len(body["details"]["problems"]) == PROBLEMS_SHOWN
    assert body["details"]["more"] == 300 - PROBLEMS_SHOWN
    assert len(response.content) <= ERROR_BYTES


def test_only_the_problems_shown_are_said_in_words(monkeypatch: pytest.MonkeyPatch) -> None:
    # A body of many unknown keys brings an error for each; set small, the bound shows. Each problem
    # said in words passes through `problem`.
    monkeypatch.setattr(errors, "PROBLEMS_SHOWN", 2)
    said: list[str] = []
    real = errors.problem

    def counted(field: str, code: FieldCode, message: str) -> dict[str, str]:
        said.append(field)
        return real(field, code, message)

    monkeypatch.setattr(errors, "problem", counted)
    sent = {"name": "a", **{f"k{number:02}": 0 for number in range(20)}}

    body = checked_client(sample_api()).post("/samples/1", json=sent, headers=CHANGE).json()

    assert said == ["body.k00", "body.k01"]
    assert problems(body) == [("body.k00", "unknown"), ("body.k01", "unknown")]
    assert body["details"]["more"] == 18
    assert body["message"] == "The request has 20 problems; nothing was done."


def test_a_header_problem_past_the_shown_ones_keeps_the_headers_hint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The hint is of every problem, the counted ones too: here the headers come last.
    monkeypatch.setattr(errors, "PROBLEMS_SHOWN", 2)
    api = sample_api()

    def numbers(a: int, b: int, c: int) -> int:
        return a + b + c

    @api.post("/late", summary="Headers last")
    def late(
        total: Annotated[int, Depends(numbers)], made: Annotated[Change, Depends(change)]
    ) -> int:
        return total

    body = checked_client(api).post("/late").json()

    assert problems(body) == [("query.a", "missing"), ("query.b", "missing")]
    assert body["details"]["more"] == 3
    assert body["hint"] == f"{HEADERS_HINT} `GET /api?path=/late` gives what this address takes."


def test_the_longest_problems_still_fit_the_budget() -> None:
    # Every name as long as it may be shown, and as many as are shown.
    params = {f"{number:03}" + "\x01" * 2000: "1" for number in range(PROBLEMS_SHOWN + 1)}

    response = checked_client(sample_api()).get("/samples/1", params=params)

    assert len(response.content) <= ERROR_BYTES, len(response.content)


def test_a_method_outside_the_document_names_what_its_route_takes() -> None:
    # FastAPI's own /openapi.json is no APIRoute and no address of the document.
    response = checked_client(create_api(core_id="")).post("/openapi.json")

    assert response.status_code == 405
    assert response.json() == {
        "code": "method_not_allowed",
        "message": "`/api/openapi.json` does not take POST.",
        "details": {"methods": ["GET"]},
        "hint": "`GET /api/openapi.json` is the only call at this address.",
    }


def test_another_4xx_of_fastapis_is_a_problem_with_the_body() -> None:
    response = checked_client(odd_api()).post("/parse")

    assert response.status_code == 400
    assert response.json() == {
        "code": "invalid_request",
        "message": "`body` could not be read: There was an error parsing the body.",
        "details": {
            "problems": [
                {
                    "field": "body",
                    "code": "wrong_type",
                    "message": "`body` could not be read: There was an error parsing the body.",
                }
            ]
        },
        "hint": "`GET /api?path=/parse` gives what this address takes.",
    }


def test_another_5xx_of_fastapis_is_internal() -> None:
    response = checked_client(odd_api()).get("/down")

    assert response.json()["message"] == "503: Service Unavailable"


def test_the_cores_own_failure_is_internal_with_the_exceptions_words() -> None:
    response = checked_client(sample_api(), raise_server_exceptions=False).get("/boom")

    assert response.status_code == 500
    assert response.json() == {
        "code": "internal",
        "message": "RuntimeError: the sample broke",
        "details": {},
        "hint": None,
    }


def test_the_failure_still_reaches_the_server_which_logs_it() -> None:
    # Uvicorn writes the traceback to the log ("Exception in ASGI application"): only an exception
    # the app lets out reaches it.
    with pytest.raises(RuntimeError, match="the sample broke"):
        checked_client(sample_api()).get("/boom")


def test_every_operation_answers_its_errors_with_the_error_model() -> None:
    doc = sample_api().openapi()

    for item in doc["paths"].values():
        for operation in item.values():
            responses = operation["responses"]
            assert responses["default"]["content"]["application/json"]["schema"] == {
                "$ref": "#/components/schemas/Error"
            }
            assert "422" not in responses
    assert "HTTPValidationError" not in doc["components"]["schemas"]


def test_the_error_model_is_typed_for_the_ui() -> None:
    error = create_api(core_id="").openapi()["components"]["schemas"]["Error"]

    assert set(error["required"]) == {"code", "message", "details", "hint"}
    assert error["properties"]["details"]["type"] == "object"
    assert error["properties"]["hint"]["anyOf"] == [{"type": "string"}, {"type": "null"}]
    assert all(field["description"] for field in error["properties"].values())


def test_every_success_is_200() -> None:
    # Step 6: one success status, so a repeat answers as the first did; 201, 202 and 204 are unused.
    doc = sample_api().openapi()

    for item in doc["paths"].values():
        for operation in item.values():
            statuses = {status for status in operation["responses"] if status != "default"}
            assert statuses == {"200"}
