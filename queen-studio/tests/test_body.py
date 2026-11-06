import asyncio
import threading
from collections.abc import Iterator
from typing import Annotated, Any, cast

import pytest
from pydantic import BaseModel, Field
from starlette.types import Message, Receive, Scope, Send

import core.body
from core.body import BodyLimit, RequestBody
from core.change import Change
from tests.contract import checked_client
from tests.sample import sample_api

CHANGE = {"Idempotency-Key": "list-1", "Actor": "agent", "Content-Type": "application/json"}

# The bound set small, so no test sends a body of megabytes.
SMALL = 1024


@pytest.fixture
def small(monkeypatch: pytest.MonkeyPatch) -> int:
    monkeypatch.setattr(core.body, "MAX_BYTES", SMALL)
    return SMALL


def padded(size: int) -> bytes:
    """A JSON body of exactly `size` bytes."""
    head, tail = b'{"name": "a", "pad": "', b'"}'
    return head + b" " * (size - len(head) - len(tail)) + tail


def test_the_body_limit_is_1_mib() -> None:
    # About 3.5 times the largest body the API takes, an edit's `replace` of 5000 places
    # (~250–300 KB, step 6).
    assert core.body.MAX_BYTES == 1024 * 1024


def test_the_bodies_held_at_once_are_8_mib() -> None:
    assert core.body.HELD_BYTES == 8 * 1024 * 1024


class Held(RequestBody):
    text: str = Field(max_length=200, description="Any text.")


def test_a_body_past_the_bodies_held_at_once_is_refused_unread(
    small: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Set small: a request held inside its endpoint keeps its body counted until it is answered.
    held_body = b'{"text": "' + b"x" * 50 + b'"}'
    sent = b'{"name": "a"}'
    monkeypatch.setattr(core.body, "HELD_BYTES", len(held_body) + len(sent) - 1)
    changes: list[Change] = []
    api = sample_api(changes)
    holding, release = threading.Event(), threading.Event()

    @api.post("/hold", summary="Hold a body")
    def hold(held: Held) -> None:
        holding.set()
        release.wait(5)

    with checked_client(api) as client:
        holder = threading.Thread(
            target=client.post,
            args=("/hold",),
            kwargs={"content": held_body, "headers": {"Content-Type": "application/json"}},
        )
        holder.start()
        assert holding.wait(5)

        refused = client.post("/samples/1", content=sent, headers=CHANGE)
        health = client.get("/health")
        release.set()
        holder.join(5)
        taken = client.post("/samples/1", content=sent, headers=CHANGE)

    assert refused.status_code == 503
    assert refused.json()["code"] == "busy"
    assert health.status_code == 200
    assert taken.status_code == 200
    assert len(changes) == 1


async def endpoint(scope: Scope, receive: Receive, send: Send) -> None:
    await receive()
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b""})


def through(limit: BodyLimit, messages: list[Message]) -> int:
    """The status `limit` answers a request whose body arrives as `messages`; 0 for none."""
    arriving = iter(messages)
    statuses: list[int] = []

    async def receive() -> Message:
        return next(arriving)

    async def send(message: Message) -> None:
        if message["type"] == "http.response.start":
            statuses.append(message["status"])

    asyncio.run(limit({"type": "http", "path": "/"}, receive, send))
    return statuses[0] if statuses else 0


def chunk(size: int, more: bool) -> Message:
    return {"type": "http.request", "body": b"x" * size, "more_body": more}


@pytest.mark.parametrize(
    ("messages", "status"),
    [
        ([chunk(512, True), chunk(513, False)], 400),
        ([chunk(512, True), {"type": "http.disconnect"}], 0),
        ([chunk(512, False)], 200),
    ],
    ids=["too-large", "caller-left", "answered"],
)
def test_a_body_leaves_nothing_held_however_it_ends(
    small: int, messages: list[Message], status: int
) -> None:
    # Driven directly: the test client sends a body as one message, and these end mid-body.
    limit = BodyLimit(endpoint)

    assert through(limit, messages) == status
    assert limit.held == 0


def test_a_body_over_the_limit_is_refused_before_the_endpoint_reads_it(small: int) -> None:
    changes: list[Change] = []

    response = checked_client(sample_api(changes)).post(
        "/samples/1", content=padded(small + 1), headers=CHANGE
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": "invalid_request",
        "message": "The body is over 1,024 bytes, the most one request takes.",
        "details": {
            "problems": [
                {
                    "field": "body",
                    "code": "out_of_range",
                    "message": "The body is over 1,024 bytes, the most one request takes.",
                }
            ]
        },
        "hint": "Send at most 1,024 bytes of body in one request.",
    }
    assert changes == []


def test_a_chunked_body_is_counted_as_it_arrives(small: int) -> None:
    # No Content-Length to trust: the body is counted chunk by chunk.
    def chunks() -> Iterator[bytes]:
        sent = padded(small + 1)
        for start in range(0, len(sent), 256):
            yield sent[start : start + 256]

    response = checked_client(sample_api()).post("/samples/1", content=chunks(), headers=CHANGE)

    assert response.json()["details"]["problems"][0]["field"] == "body"


def test_a_body_at_the_limit_reaches_the_endpoint_whole(small: int) -> None:
    # The pad is an unknown field, so the endpoint's validation answers: it read the whole body.
    response = checked_client(sample_api()).post(
        "/samples/1", content=padded(small), headers=CHANGE
    )

    assert response.json()["details"]["problems"] == [
        {
            "field": "body.pad",
            "code": "unknown",
            "message": "`body.pad` is not a field this address takes.",
        }
    ]


def unbounded(doc: dict[str, Any]) -> list[str]:
    """Each place in the document's request bodies that takes an unknown field or has no maximum.

    Bodies inherit core.body.RequestBody, so an object of named fields refuses any other; a list
    needs `maxItems`, a text `maxLength` (an enum or a constant is bounded already), a map
    `maxProperties`, and a field takes no `Any` (CODE-STANDARD, Cost). Each model is walked once.
    """
    schemas: dict[str, Any] = doc["components"]["schemas"]
    found: list[str] = []
    seen: set[str] = set()

    def walk(schema: dict[str, Any], place: str) -> None:
        if "$ref" in schema:
            name: str = schema["$ref"].rsplit("/", 1)[1]
            if name not in seen:
                seen.add(name)
                walk(schemas[name], name)
            return
        kind = schema.get("type")
        options = [*schema.get("anyOf", []), *schema.get("oneOf", []), *schema.get("allOf", [])]
        if "properties" in schema:
            if schema.get("additionalProperties") is not False:
                found.append(f"{place}: takes unknown fields")
            for field, inner in schema["properties"].items():
                walk(inner, f"{place}.{field}")
        elif kind == "object":
            if "maxProperties" not in schema:
                found.append(f"{place}: no maxProperties")
            extra = schema.get("additionalProperties")
            if isinstance(extra, dict):
                walk(cast(dict[str, Any], extra), f"{place}.*")
        elif kind == "array":
            if "maxItems" not in schema:
                found.append(f"{place}: no maxItems")
            for item in [schema.get("items", {}), *schema.get("prefixItems", [])]:
                walk(item, f"{place}[]")
        elif kind == "string":
            if not {"maxLength", "enum", "const"} & schema.keys():
                found.append(f"{place}: no maxLength")
        elif kind is None and not options and not {"enum", "const"} & schema.keys():
            found.append(f"{place}: takes anything")
        for option in options:
            walk(option, place)

    for path, item in doc["paths"].items():
        for method, operation in item.items():
            if "requestBody" in operation:
                body = operation["requestBody"]["content"]["application/json"]["schema"]
                walk(body, f"{method.upper()} {path}")
    return found


def test_every_body_bounds_its_size_and_refuses_unknown_fields() -> None:
    doc = sample_api().openapi()

    assert "Sample" in doc["components"]["schemas"], "the sample API has a body to check"
    assert unbounded(doc) == []


class Loose(BaseModel):
    note: str = Field(description="Not RequestBody's.")


class Open(RequestBody):
    tags: list[str] = Field(max_length=3, description="Texts of no length.")
    names: list[Annotated[str, Field(max_length=5)]] = Field(description="No count.")
    scores: dict[str, int] = Field(description="A map of no size.")
    loose: Loose = Field(description="Takes any field.")
    anything: Any = Field(description="Anything.")


def test_a_body_that_forgets_a_bound_is_found() -> None:
    api = sample_api()

    @api.post("/open", summary="Takes too much")
    def take(open: Open) -> None:
        pass

    assert unbounded(api.openapi()) == [
        "Open.tags[]: no maxLength",
        "Open.names: no maxItems",
        "Open.scores: no maxProperties",
        "Loose: takes unknown fields",
        "Loose.note: no maxLength",
        "Open.anything: takes anything",
    ]
