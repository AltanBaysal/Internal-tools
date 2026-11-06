from typing import Annotated, Any

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

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


def test_a_route_that_parses_its_own_query_takes_any_parameter() -> None:
    response = checked_client(sample_api()).get("/samples", params={"status": "eq.waiting"})

    assert response.status_code == 200
    assert response.json() == {"status": "eq.waiting"}
