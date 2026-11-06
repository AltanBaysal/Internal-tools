import json
from typing import Any

from fastapi import APIRouter

from core.about import NAME, VERSION
from core.api.discovery import RULES, index
from core.errors import CODES
from core.server import create_api
from tests.budgets import DETAIL_BYTES, INDEX_BYTES, INDEX_LINE_BYTES
from tests.contract import checked_client
from tests.sample import SECTION, sample_api


def compact(value: Any) -> int:
    """Bytes of `value` as the API sends it."""
    return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def test_the_index_names_the_app_the_rules_and_each_section_with_its_lines() -> None:
    response = checked_client(create_api(core_id="k3v9q2mz7a")).get("/")

    assert response.status_code == 200
    assert response.json() == {
        "app": NAME,
        "version": VERSION,
        "rules": RULES,
        "sections": [
            {
                "name": "Discovery",
                "about": "How to learn this API, and to check that the address answers with "
                "this app's core.",
                "endpoints": ["GET /health: Which app and which core answer here"],
            }
        ],
    }


def test_an_endpoint_added_grows_the_index_by_its_one_line() -> None:
    before = checked_client(create_api(core_id="k3v9q2mz7a")).get("/").json()
    api = create_api(core_id="k3v9q2mz7a")
    added = APIRouter(tags=["Discovery"])

    @added.get("/ping", summary="Answers pong", description="A long description stays out.")
    def ping() -> str:
        return "pong"

    api.include_router(added)

    after = checked_client(api).get("/").json()
    before["sections"][0]["endpoints"].append("GET /ping: Answers pong")
    assert after == before


def test_every_operation_is_one_line_of_its_section() -> None:
    body = checked_client(sample_api()).get("/").json()

    lines = {
        (section["name"], line.split(":")[0])
        for section in body["sections"]
        for line in section["endpoints"]
    }
    assert lines == {
        ("Discovery", "GET /health"),
        ("Samples", "POST /samples/{id}"),
        ("Samples", "GET /samples/{id}"),
        ("Samples", "DELETE /samples/{id}"),
        ("Samples", "GET /boom"),
        ("Samples", "GET /samples"),
    }
    assert body["sections"][1] == {**body["sections"][1], "about": SECTION["description"]}


def test_an_operation_in_no_section_stops_the_index_rather_than_vanish_from_it() -> None:
    api = create_api(core_id="k3v9q2mz7a")

    @api.get("/stray", summary="In no section")
    def stray() -> None: ...

    try:
        index(api.openapi())
    except ValueError as missing:
        assert "GET /stray" in str(missing)
    else:
        raise AssertionError("an operation in no section was left out silently")


def test_the_index_stays_within_its_budget() -> None:
    response = checked_client(sample_api()).get("/")

    assert len(response.content) <= INDEX_BYTES, len(response.content)
    for section in response.json()["sections"]:
        for line in section["endpoints"]:
            assert compact(line) <= INDEX_LINE_BYTES, line


def test_an_address_detail_gives_each_method_its_fields_answer_and_errors() -> None:
    response = checked_client(sample_api()).get("/", params={"path": "/samples/{id}"})

    assert response.status_code == 200
    detail = response.json()
    assert detail.keys() == {"POST", "GET", "DELETE"}
    assert detail["POST"] == {
        "description": "Makes the sample.",
        "path": {"id": {"type": "integer", "required": True, "description": "The sample's id."}},
        "query": {
            "loud": {
                "type": "boolean",
                "required": False,
                "description": "Say it loudly.",
                "default": False,
            }
        },
        "body": {
            "type": "object",
            "fields": {
                "name": {
                    "type": "string",
                    "required": True,
                    "description": "The sample's name.",
                    "minLength": 1,
                    "maxLength": 20,
                },
                "kind": {
                    "type": "string",
                    "required": False,
                    "description": "Its kind.",
                    "enum": ["a", "b"],
                    "default": "a",
                },
                "count": {
                    "type": "integer",
                    "required": False,
                    "description": "How many to make.",
                    "default": 1,
                    "minimum": 1,
                    "maximum": 9,
                },
                "place": {
                    "type": "object | null",
                    "required": False,
                    "description": "Where it goes.",
                    "fields": {
                        "frame": {
                            "type": "integer",
                            "required": True,
                            "description": "The frame it stands on.",
                        }
                    },
                },
            },
        },
        "returns": {
            "type": "object",
            "fields": {
                "id": {"type": "integer", "description": "The sample's id."},
                "name": {"type": "string", "description": "Its name."},
            },
        },
        "errors": ["unknown_endpoint"],
    }


def test_the_headers_the_caller_adds_stay_out_of_the_detail() -> None:
    # The MCP tool and the UI add Idempotency-Key and Actor; the agent never writes them (step 6).
    detail = checked_client(sample_api()).get("/", params={"path": "/samples/{id}"}).json()

    assert "header" not in detail["DELETE"]
    assert "Idempotency-Key" not in json.dumps(detail)


def test_an_unknown_address_has_no_detail() -> None:
    response = checked_client(create_api(core_id="k3v9q2mz7a")).get(
        "/", params={"path": "/nothing"}
    )

    assert response.status_code == 404
    assert response.json()["message"] == "`/nothing` is not an address of this API."


def test_every_address_detail_stays_within_its_budget() -> None:
    api_client = checked_client(sample_api())

    for path in sample_api().openapi()["paths"]:
        response = api_client.get("/", params={"path": path})
        assert len(response.content) <= DETAIL_BYTES, (path, len(response.content))


def test_every_operation_names_only_errors_the_core_has() -> None:
    doc = sample_api().openapi()

    for item in doc["paths"].values():
        for operation in item.values():
            assert set(operation.get("x-errors", [])) <= CODES.keys(), operation["summary"]
