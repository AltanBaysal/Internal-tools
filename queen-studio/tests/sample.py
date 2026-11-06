"""A test-only group: the contract is tried on it before the groups that use it exist."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, FastAPI, Path, Query
from pydantic import BaseModel, Field
from starlette.datastructures import QueryParams

from core.body import RequestBody
from core.change import Change, change
from core.errors import ApiError
from core.query import own_query
from core.server import create_api

SECTION = {"name": "Samples", "description": "Test-only addresses."}


class Place(RequestBody):
    frame: int = Field(description="The frame it stands on.")


class Sample(RequestBody):
    name: str = Field(min_length=1, max_length=20, description="The sample's name.")
    kind: Literal["a", "b"] = Field(default="a", description="Its kind.")
    count: int = Field(default=1, ge=1, le=9, description="How many to make.")
    place: Place | None = Field(default=None, description="Where it goes.")


class Made(BaseModel):
    id: int = Field(description="The sample's id.")
    name: str = Field(description="Its name.")


def router(changes: list[Change]) -> APIRouter:
    samples = APIRouter(tags=[SECTION["name"]])

    @samples.post(
        "/samples/{id}",
        summary="Make a sample",
        description="Makes the sample.",
        openapi_extra={"x-errors": ["unknown_endpoint"]},
    )
    def make(
        id: Annotated[int, Path(description="The sample's id.")],
        sample: Sample,
        made: Annotated[Change, Depends(change)],
        loud: Annotated[bool, Query(description="Say it loudly.")] = False,
    ) -> Made:
        changes.append(made)
        return Made(id=id, name=sample.name)

    @samples.get("/samples/{id}", summary="One sample")
    def one(id: int) -> Made:
        if id == 0:
            raise ApiError("unknown_endpoint", "There is no sample 0.", {"id": 0}, "Ask for 1.")
        return Made(id=id, name="one")

    @samples.delete("/samples/{id}", summary="Remove a sample")
    def remove(id: int, made: Annotated[Change, Depends(change)]) -> Made:
        changes.append(made)
        return Made(id=id, name="gone")

    @samples.get("/boom", summary="Fail inside")
    def boom() -> Made:
        raise RuntimeError("the sample broke")

    # As v1-6's lists will: the query is the route's own to parse.
    @samples.get("/samples", summary="Every sample")
    def every(query: Annotated[QueryParams, Depends(own_query)]) -> dict[str, str]:
        return dict(query)

    return samples


def sample_api(changes: list[Change] | None = None) -> FastAPI:
    """The core's API with the samples beside its own groups."""
    api = create_api(core_id="k3v9q2mz7a")
    assert api.openapi_tags is not None
    api.openapi_tags.append(SECTION)
    api.include_router(router([] if changes is None else changes))
    return api
