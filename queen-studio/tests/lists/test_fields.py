from datetime import datetime
from typing import Annotated, Any, Literal

import pytest
from pydantic import BaseModel, Field

from core.lists.fields import ListField, fields_of


class Lora(BaseModel):
    id: str
    files: list[dict[str, Any]]


class Photo(BaseModel):
    status: Literal["waiting", "running", "done"]
    seed: int
    strength: float
    lora: Lora | None
    created: datetime


class Frame(BaseModel):
    id: int
    scene: Annotated[str, Field(max_length=500)]
    muted: bool
    photo: Photo
    video: Photo | None = None
    input: dict[str, Any]


def test_each_field_is_read_off_the_model_with_its_kind() -> None:
    assert fields_of(Frame) == {
        "id": ListField("id", "int"),
        "scene": ListField("scene", "text"),
        "muted": ListField("muted", "bool"),
        "photo": ListField("photo", "object"),
        "photo.status": ListField("photo.status", "text", ("waiting", "running", "done")),
        "photo.seed": ListField("photo.seed", "int"),
        "photo.strength": ListField("photo.strength", "number"),
        "photo.lora": ListField("photo.lora", "object"),
        "photo.lora.id": ListField("photo.lora.id", "text"),
        "photo.lora.files": ListField("photo.lora.files", "list"),
        "photo.created": ListField("photo.created", "time"),
        "video": ListField("video", "object"),
        "video.status": ListField("video.status", "text", ("waiting", "running", "done")),
        "video.seed": ListField("video.seed", "int"),
        "video.strength": ListField("video.strength", "number"),
        "video.lora": ListField("video.lora", "object"),
        "video.lora.id": ListField("video.lora.id", "text"),
        "video.lora.files": ListField("video.lora.files", "list"),
        "video.created": ListField("video.created", "time"),
        "input": ListField("input", "object"),
    }


def test_a_nullable_field_has_the_kind_of_what_it_holds() -> None:
    class Maybe(BaseModel):
        finished: datetime | None
        count: Annotated[int, Field(ge=0)] | None

    assert fields_of(Maybe) == {
        "finished": ListField("finished", "time"),
        "count": ListField("count", "int"),
    }


class Odd(BaseModel):
    either: int | str


class Numbers(BaseModel):
    level: Literal[1, 2]


def test_a_kind_the_query_cannot_read_stops_the_declaration() -> None:
    with pytest.raises(ValueError, match=r"Odd\.either"):
        fields_of(Odd)
    with pytest.raises(ValueError, match=r"Numbers\.level"):
        fields_of(Numbers)


def test_an_alias_stops_the_declaration() -> None:
    # A record is the model's JSON by its fields' own names: an alias would name another field.
    class Aliased(BaseModel):
        sort_by: str = Field(alias="sort-by")

    with pytest.raises(ValueError, match=r"Aliased\.sort_by"):
        fields_of(Aliased)
