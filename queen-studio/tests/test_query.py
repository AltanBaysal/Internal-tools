from typing import Annotated, Any

import pytest
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from core import query
from core.change import Change
from core.server import create_api
from tests.contract import checked_client
from tests.sample import sample_api

CHANGE = {"Idempotency-Key": "list-1", "Actor": "agent"}


def test_a_query_parameter_the_route_does_not_declare_is_refused() -> None:
    response = checked_client(sample_api()).get("/samples/1", params={"zz": "1", "yy": "2"})

    assert response.status_code == 400
    assert response.json() == {
        "code": "invalid_request",
        "message": "The request has 2 problems; nothing was done.",
        "details": {
            "problems": [
                {
                    "field": "query.zz",
                    "code": "unknown",
                    "message": "`query.zz` is not a field this address takes.",
                },
                {
                    "field": "query.yy",
                    "code": "unknown",
                    "message": "`query.yy` is not a field this address takes.",
                },
            ]
        },
        "hint": "`GET /api?path=/samples/{id}` gives what this address takes.",
    }


def test_a_change_with_an_unknown_query_parameter_is_not_made() -> None:
    changes: list[Change] = []

    response = checked_client(sample_api(changes)).post(
        "/samples/1", params={"lod": "true"}, json={"name": "a"}, headers=CHANGE
    )

    assert response.json()["details"]["problems"][0]["field"] == "query.lod"
    assert changes == []


def test_a_declared_query_parameter_is_taken() -> None:
    response = checked_client(sample_api()).post(
        "/samples/1", params={"loud": "true"}, json={"name": "a"}, headers=CHANGE
    )

    assert response.status_code == 200


def test_a_mistyped_index_query_is_refused_rather_than_answered_with_the_index() -> None:
    response = checked_client(create_api(core_id="k3v9q2mz7a")).get("/", params={"paht": "/health"})

    assert response.json()["details"]["problems"][0]["field"] == "query.paht"


def test_a_parameter_without_a_name_is_named_as_empty() -> None:
    response = checked_client(sample_api()).get("/samples/1?=1")

    assert response.json()["details"]["problems"][0] == {
        "field": "query.(empty)",
        "code": "unknown",
        "message": "`query.(empty)` is not a field this address takes.",
    }


class Filter(BaseModel):
    limit: int = 10
    sort_by: str = Field("a", alias="sort-by")


def with_query_model() -> FastAPI:
    api = sample_api()

    @api.get("/listed", summary="A query model")
    def listed(found: Annotated[Filter, Query()]) -> list[Any]:
        return [found.limit, found.sort_by]

    return api


def test_the_fields_of_a_query_model_are_declared() -> None:
    response = checked_client(with_query_model()).get(
        "/listed", params={"limit": "3", "sort-by": "b"}
    )

    assert response.json() == [3, "b"]


def test_a_query_model_still_refuses_what_it_lacks() -> None:
    response = checked_client(with_query_model()).get("/listed", params={"zz": "1"})

    assert response.json()["details"]["problems"][0]["field"] == "query.zz"


def test_a_parameter_given_twice_is_refused_rather_than_one_dropped() -> None:
    # FastAPI keeps the last of two and drops the first without a word.
    changes: list[Change] = []

    response = checked_client(sample_api(changes)).post(
        "/samples/1?loud=true&loud=false", json={"name": "a"}, headers=CHANGE
    )

    assert response.json()["details"]["problems"] == [
        {
            "field": "query.loud",
            "code": "duplicate",
            "message": "`query.loud` is given twice; it takes one.",
        }
    ]
    assert changes == []


def test_the_index_refuses_two_paths() -> None:
    response = checked_client(create_api(core_id="k3v9q2mz7a")).get("/?path=/health&path=/x")

    assert response.json()["details"]["problems"][0]["code"] == "duplicate"


def test_a_list_parameter_may_repeat() -> None:
    api = sample_api()

    @api.get("/tagged", summary="Tagged")
    def tagged(tag: Annotated[list[str], Query()]) -> list[str]:
        return tag

    @api.get("/maybe", summary="Maybe tagged")
    def maybe(tag: Annotated[list[str] | None, Query()] = None) -> list[str]:
        return tag or []

    assert checked_client(api).get("/tagged?tag=a&tag=b").json() == ["a", "b"]
    assert checked_client(api).get("/maybe?tag=a&tag=b").json() == ["a", "b"]


def test_a_query_past_its_bound_is_refused_before_any_route(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Set small here; whatever the server lets through, the core holds the query to it.
    monkeypatch.setattr(query, "QUERY_BYTES", 32)
    changes: list[Change] = []
    checked = checked_client(sample_api(changes))

    taken = checked.post("/samples/1?loud=true", json={"name": "a"}, headers=CHANGE)
    refused = checked.post("/samples/1?loud=true&x=" + "x" * 30, json={"name": "a"}, headers=CHANGE)

    assert taken.status_code == 200
    assert refused.json() == {
        "code": "invalid_request",
        "message": "The query is over 32 bytes, the most one request takes.",
        "details": {
            "problems": [
                {
                    "field": "query",
                    "code": "out_of_range",
                    "message": "The query is over 32 bytes, the most one request takes.",
                }
            ]
        },
        "hint": "Send at most 32 bytes of query in one request.",
    }
    assert len(changes) == 1


def test_a_query_at_its_bound_is_read(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(query, "QUERY_BYTES", len("status=eq.waiting"))

    response = checked_client(sample_api()).get("/samples", params={"status": "eq.waiting"})

    assert response.json() == {"status": "eq.waiting"}


def test_a_route_that_parses_its_own_query_takes_any_parameter() -> None:
    response = checked_client(sample_api()).get("/samples", params={"status": "eq.waiting"})

    assert response.status_code == 200
    assert response.json() == {"status": "eq.waiting"}
