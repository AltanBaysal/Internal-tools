import json
import re
from collections.abc import Iterator
from typing import Any, Literal

import pytest
from fastapi import FastAPI
from pydantic import BaseModel

from core.change import Change
from core.lists import listing
from core.lists.listing import Listing
from core.lists.parse import MOST_LIMIT
from tests.budgets import ERROR_BYTES, LIST_ITEM_BYTES, TEXT_SAMPLE_BYTES
from tests.contract import checked_client
from tests.sample import NOTES, Note, sample_api

CHANGE = {"Idempotency-Key": "bulk-1", "Actor": "agent"}


def note(id: int, position: int, **fields: Any) -> dict[str, Any]:
    look = {"status": "done", "prompt": "p", "seed": 1, "created": "2026-11-04T09:12:00Z"}
    return {
        "id": id,
        "position": position,
        "scene": f"scene {id}",
        "archived": False,
        "score": None,
        "updated": "2026-11-04T09:12:00Z",
        "photo": look,
        "video": None,
        "tags": [],
        "input": {},
        **fields,
    }


NOTES_GIVEN = [
    note(17, 1, scene="Yağmurda bir sokak"),
    note(4, 0, scene="IŞIK", video={**note(0, 0)["photo"], "status": "waiting"}),
    note(25, 2, archived=True),
]


def client(notes: list[dict[str, Any]] | None = None, changes: list[Change] | None = None) -> Any:
    return checked_client(sample_api(changes, NOTES_GIVEN if notes is None else notes))


def test_a_list_answers_its_default_fields_in_its_default_order() -> None:
    response = client().get("/notes")

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": 4,
                "position": 0,
                "scene": "IŞIK",
                "photo": {"status": "done"},
                "video": {"status": "waiting"},
            },
            {
                "id": 17,
                "position": 1,
                "scene": "Yağmurda bir sokak",
                "photo": {"status": "done"},
                "video": None,
            },
            {
                "id": 25,
                "position": 2,
                "scene": "scene 25",
                "photo": {"status": "done"},
                "video": None,
            },
        ],
        "total": 3,
        "offset": 0,
        "limit": 100,
    }


def test_a_list_takes_the_whole_query() -> None:
    response = client().get(
        "/notes?scene=ilike.ışık&archived=is.false&updated=gte.2026-11-04"
        "&order=id.desc&limit=5&select=id,video.status"
    )

    assert response.json() == {
        "items": [{"id": 4, "video": {"status": "waiting"}}],
        "total": 1,
        "offset": 0,
        "limit": 5,
    }


def test_a_wrong_query_names_the_lists_fields() -> None:
    response = client().get("/notes", params={"statsu": "eq.done"})

    assert response.status_code == 400
    assert response.json() == {
        "code": "invalid_request",
        "message": "`query.statsu` is not a field of this list.",
        "details": {
            "problems": [
                {
                    "field": "query.statsu",
                    "code": "unknown",
                    "message": "`query.statsu` is not a field of this list.",
                }
            ],
            "fields": list(NOTES.fields),
        },
        "hint": "`GET /api?path=/notes` gives what this address takes.",
    }


class Untouchable(list[dict[str, Any]]):
    def __iter__(self) -> Iterator[dict[str, Any]]:
        raise AssertionError("a record was read")


def test_a_page_past_its_byte_budget_is_refused_with_how_many_fit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Two default items and the page's frame fit in 300 bytes; the third does not.
    monkeypatch.setattr(listing, "PAGE_BYTES", 300)

    response = client().get("/notes")

    assert response.status_code == 400
    assert response.json() == {
        "code": "invalid_request",
        "message": "The page passes 300 bytes, the most an answer takes; 2 of its items fit.",
        "details": {
            "problems": [
                {
                    "field": "query.limit",
                    "code": "out_of_range",
                    "message": "The page passes 300 bytes, the most an answer takes; 2 of its "
                    "items fit.",
                }
            ],
            "fits": 2,
        },
        "hint": "Ask for at most 2 with `limit`, or for fewer fields with `select`.",
    }
    assert client().get("/notes", params={"limit": "2"}).status_code == 200


def test_one_thing_past_the_byte_budget_is_refused_too(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(listing, "PAGE_BYTES", 100)

    response = client().get("/notes/17")

    assert response.json()["hint"] == "Ask for fewer fields with `select`."
    assert client().get("/notes/17", params={"select": "id"}).json() == {"id": 17}


def test_a_wrong_query_reads_no_record() -> None:
    response = client(Untouchable()).get("/notes", params={"id": "eq.x"})

    assert response.json()["details"]["problems"][0]["field"] == "query.id"


def test_a_bulk_change_without_its_headers_names_them_and_does_nothing() -> None:
    changes: list[Change] = []

    response = client(changes=changes).delete("/notes", params={"id": "eq.4"})

    fields = [problem["field"] for problem in response.json()["details"]["problems"]]
    assert fields == ["header.Idempotency-Key", "header.Actor"]
    assert changes == []


def test_a_bulk_change_without_a_filter_is_refused() -> None:
    changes: list[Change] = []

    response = client(changes=changes).delete("/notes", headers=CHANGE)

    assert response.json()["details"]["problems"] == [
        {
            "field": "query",
            "code": "missing",
            "message": "A bulk change names what it acts on: filters, or `all=true` for every one.",
        }
    ]
    assert changes == []


def test_a_bulk_change_acts_on_what_the_lists_get_finds() -> None:
    found = client().get("/notes", params={"video": "is.null", "select": "id"}).json()["items"]

    response = client().delete("/notes", params={"video": "is.null"}, headers=CHANGE)

    assert response.json() == {"deleted": [17, 25]}
    assert [item["id"] for item in found] == [17, 25]


def test_a_bulk_change_with_all_true_acts_on_every_one() -> None:
    response = client().delete("/notes", params={"all": "true"}, headers=CHANGE)

    assert sorted(response.json()["deleted"]) == [4, 17, 25]


def test_a_bulk_change_refuses_a_page() -> None:
    response = client().delete("/notes", params={"all": "true", "limit": "1"}, headers=CHANGE)

    assert response.json()["details"]["problems"][0]["field"] == "query.limit"


def test_one_things_get_takes_select_and_answers_the_whole_by_default() -> None:
    whole = client().get("/notes/17").json()
    picked = client().get("/notes/17", params={"select": "scene,photo.seed"}).json()
    wrong = client().get("/notes/17", params={"scene": "eq.x"})

    assert whole == NOTES_GIVEN[0]
    assert picked == {"scene": "Yağmurda bir sokak", "photo": {"seed": 1}}
    assert wrong.json()["details"]["problems"][0]["code"] == "unknown"


def test_an_address_detail_gives_the_lists_defaults() -> None:
    detail = client().get("/", params={"path": "/notes"}).json()

    assert detail["GET"]["list"] == {
        "order": "position",
        "select": "id,position,scene,photo.status,video.status",
    }
    assert "query" not in detail["GET"]
    item = detail["GET"]["returns"]["fields"]["items"]["items"]["fields"]
    assert item.keys() == Note.model_fields.keys()
    # A time is told from text by its format: the agent filters it with a time or a day.
    assert item["updated"] == {
        "type": "string",
        "format": "date-time",
        "description": "When it last changed.",
    }


def test_a_list_declared_with_a_reserved_name_or_a_wrong_default_stops() -> None:
    class Ordered(BaseModel):
        order: int

    with pytest.raises(ValueError, match="order is a parameter of every list"):
        Listing(Ordered, default=("order",), order="order")
    with pytest.raises(ValueError, match="`nope`"):
        Listing(Note, default=("id", "nope"), order="id")
    with pytest.raises(ValueError, match="`photo`"):
        Listing(Note, default=("id",), order="photo")


def test_every_lists_worst_query_error_stays_within_its_budget() -> None:
    # Every problem as long as it may be shown, as many as are shown, and the list's fields; on
    # each list in the document, so a list with many fields is measured as it is added.
    params: list[tuple[str, str | int | float | bool | None]] = [
        (f"{number}" + "\x01" * 2000, "eq.1") for number in range(7)
    ]
    params += [("order", "\x01" * 2000), ("select", "\x01" * 2000)]
    api = sample_api()
    lists = [
        address
        for address, item in api.openapi()["paths"].items()
        if "x-list" in item.get("get", {})
    ]

    for address in lists:
        response = checked_client(api).get(re.sub(r"\{[^}]+\}", "x", address), params=params)

        assert response.status_code == 400, address
        assert len(response.content) <= ERROR_BYTES, (address, len(response.content))
    assert "/notes" in lists


# The size of a list's default fields (FOUNDATION 4), measured on its worst item: built from the
# item's schema in the document, so every list of the core is measured, today's and later ones.
SAMPLE_INT = 1_234_567
SAMPLE_TIME = "2026-11-04T09:12:00Z"


def sample(schema: dict[str, Any], doc: dict[str, Any]) -> Any:
    if "$ref" in schema:
        return sample(doc["components"]["schemas"][schema["$ref"].rsplit("/", 1)[1]], doc)
    options = [option for option in schema.get("anyOf", []) if option.get("type") != "null"]
    if options:
        return sample(options[0], doc)
    kind: str = schema.get("type", "object")
    if "enum" in schema:
        return max(schema["enum"], key=lambda value: len(str(value)))
    if kind == "object":
        properties: dict[str, Any] = schema.get("properties", {})
        return {name: sample(field, doc) for name, field in properties.items()}
    if kind == "array":
        return [sample(schema["items"], doc)]
    if kind == "string":
        if schema.get("format") == "date-time":
            return SAMPLE_TIME
        return "x" * schema.get("maxLength", TEXT_SAMPLE_BYTES)
    return {"integer": SAMPLE_INT, "number": 12345.678, "boolean": False}[kind]


def default_item(item: Any, select: str) -> Any:
    picked: dict[str, Any] = {}
    for name in select.split(","):
        *outer, last = name.split(".")
        source, target = item, picked
        for part in outer:
            source, target = source[part], target.setdefault(part, {})
        target[last] = source[last]
    return picked


def page_item_schema(operation: dict[str, Any], doc: dict[str, Any]) -> dict[str, Any] | None:
    schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    if "$ref" in schema:
        schema = doc["components"]["schemas"][schema["$ref"].rsplit("/", 1)[1]]
    properties: dict[str, Any] = schema.get("properties", {})
    if not {"items", "total", "offset", "limit"} <= properties.keys():
        return None
    return properties["items"]["items"]


def oversized(api: FastAPI) -> list[str]:
    """Each list whose default item is over its budget, or that answers a page with no `x-list`."""
    doc = api.openapi()
    found: list[str] = []
    for address, item in doc["paths"].items():
        for method, operation in item.items():
            schema = page_item_schema(operation, doc)
            if schema is None:
                continue
            if "x-list" not in operation:
                found.append(f"{method.upper()} {address}: no x-list")
                continue
            picked = default_item(sample(schema, doc), operation["x-list"]["select"])
            size = len(json.dumps(picked, ensure_ascii=False, separators=(",", ":")).encode())
            if size > LIST_ITEM_BYTES:
                found.append(f"{method.upper()} {address}: {size} B")
    return found


def test_every_lists_default_item_stays_within_its_budget() -> None:
    # The sample API carries the core's groups too: each list added later is measured here.
    assert oversized(sample_api()) == []


class Heavy(BaseModel):
    id: int
    prompt: str
    negative: str
    model_prompt: str
    status: Literal["waiting", "running"]


def test_the_walk_finds_a_list_too_heavy_or_unmarked() -> None:
    heavy = Listing(Heavy, default=("id", "prompt", "negative", "model_prompt"), order="id")
    api = sample_api()

    @api.get("/heavy", summary="Heavy", response_model=heavy.page, openapi_extra=heavy.extra)
    def every() -> None: ...

    @api.get("/unmarked", summary="Unmarked", response_model=heavy.page)
    def unmarked() -> None: ...

    found = oversized(api)

    assert found[0].startswith("GET /heavy: ")
    assert found[1:] == ["GET /unmarked: no x-list"]


def test_a_whole_page_of_the_samples_worst_items_fits_the_byte_budget() -> None:
    # The budget is an outer bound: a page of the most items, each whole and at its worst, fits.
    doc = sample_api().openapi()
    worst = sample(doc["components"]["schemas"]["Note"], doc)
    size = len(json.dumps(worst, ensure_ascii=False, separators=(",", ":")).encode())

    assert size * MOST_LIMIT <= listing.PAGE_BYTES, size
