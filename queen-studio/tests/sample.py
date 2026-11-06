"""A test-only group: the contract is tried on it before the groups that use it exist."""

from datetime import datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, FastAPI, Path, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field
from starlette.datastructures import QueryParams

from core.body import RequestBody
from core.change import Change, change
from core.errors import ApiError
from core.lists.listing import Listing, Selection
from core.lists.parse import Query as ListQuery
from core.lists.parse import Tree
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


class Look(BaseModel):
    status: Literal["waiting", "running", "done"] = Field(description="Where it is.")
    prompt: str | None = Field(description="What it shows.")
    seed: int = Field(description="Its seed.")
    created: datetime = Field(description="When it was made.")


# Shaped as a frame is (step 6, Frames): nested, nullable. A docstring would reach the API.
class Note(BaseModel):
    id: int = Field(description="The note's id.")
    position: int = Field(description="Its place.")
    scene: str = Field(description="Its scene.")
    archived: bool = Field(description="Whether it is put away.")
    score: float | None = Field(description="Its score.")
    updated: datetime = Field(description="When it last changed.")
    photo: Look = Field(description="Its photo.")
    video: Look | None = Field(description="Its video.")
    tags: list[str] = Field(description="Its tags.")
    input: dict[str, Any] = Field(description="What it was given.")


NOTES = Listing(
    Note, default=("id", "position", "scene", "photo.status", "video.status"), order="position"
)


class Gone(BaseModel):
    deleted: list[int] = Field(description="The notes the change would act on.")


def router(changes: list[Change], notes: list[dict[str, Any]]) -> APIRouter:
    samples = APIRouter(tags=[SECTION["name"]])

    # As each list of the core: declared once, its query read before the records are.
    @samples.get(
        "/notes",
        summary="Every note",
        description="The notes.",
        response_model=NOTES.page,
        openapi_extra=NOTES.extra,
    )
    def every_note(query: Annotated[ListQuery, Depends(NOTES.query)]) -> Response:
        return NOTES.answer(notes, query)

    @samples.delete("/notes", summary="Remove notes", response_model=Gone)
    def remove_notes(selected: Annotated[Selection, Depends(NOTES.selection)]) -> Gone:
        changes.append(selected.change)
        return Gone(deleted=[note["id"] for note in NOTES.matches(notes, selected)])

    @samples.get("/notes/{id}", summary="One note", response_model=Note)
    def one_note(id: int, select: Annotated[Tree | None, Depends(NOTES.one)]) -> Response:
        found = next((note for note in notes if note["id"] == id), None)
        if found is None:
            raise ApiError("unknown_endpoint", f"There is no note {id}.", {"id": id}, "Ask for 1.")
        return NOTES.answer_one(found, select)

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


def sample_api(
    changes: list[Change] | None = None, notes: list[dict[str, Any]] | None = None
) -> FastAPI:
    """The core's API with the samples beside its own groups."""
    api = create_api(core_id="k3v9q2mz7a")
    assert api.openapi_tags is not None
    api.openapi_tags.append(SECTION)
    api.include_router(router([] if changes is None else changes, [] if notes is None else notes))
    return api
