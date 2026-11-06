from collections.abc import Iterator
from typing import Any

from core.body import MAX_BYTES
from core.change import Change
from tests.contract import checked_client
from tests.sample import sample_api

CHANGE = {"Idempotency-Key": "list-1", "Actor": "agent", "Content-Type": "application/json"}


def padded(size: int) -> bytes:
    """A JSON body of exactly `size` bytes."""
    head, tail = b'{"name": "a", "pad": "', b'"}'
    return head + b" " * (size - len(head) - len(tail)) + tail


def test_a_body_over_the_limit_is_refused_before_the_endpoint_reads_it() -> None:
    changes: list[Change] = []

    response = checked_client(sample_api(changes)).post(
        "/samples/1", content=padded(MAX_BYTES + 1), headers=CHANGE
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": "invalid_request",
        "message": "The body is over 4 MB, the most one request takes.",
        "details": {
            "problems": [
                {
                    "field": "body",
                    "code": "out_of_range",
                    "message": "The body is over 4 MB, the most one request takes.",
                }
            ]
        },
        "hint": "Send at most 4 MB in one request.",
    }
    assert changes == []


def test_a_chunked_body_is_counted_as_it_arrives() -> None:
    # No Content-Length to trust: the body is counted chunk by chunk.
    def chunks() -> Iterator[bytes]:
        body = padded(MAX_BYTES + 1)
        for start in range(0, len(body), 65536):
            yield body[start : start + 65536]

    response = checked_client(sample_api()).post("/samples/1", content=chunks(), headers=CHANGE)

    assert response.json()["details"]["problems"][0]["field"] == "body"


def test_a_body_at_the_limit_reaches_the_endpoint_whole() -> None:
    # The pad is an unknown field, so the endpoint's validation answers: it read the whole body.
    response = checked_client(sample_api()).post(
        "/samples/1", content=padded(MAX_BYTES), headers=CHANGE
    )

    assert response.json()["details"]["problems"] == [
        {
            "field": "body.pad",
            "code": "unknown",
            "message": "`body.pad` is not a field this address takes.",
        }
    ]


def test_every_body_model_refuses_a_field_it_does_not_take() -> None:
    # Bodies inherit core.body.RequestBody; one that does not would drop an unknown field silently.
    doc = sample_api().openapi()
    schemas: dict[str, Any] = doc["components"]["schemas"]

    def objects(schema: Any) -> Iterator[Any]:
        if "$ref" in schema:
            schema = schemas[schema["$ref"].rsplit("/", 1)[1]]
        if "properties" in schema:
            yield schema
            for field in schema["properties"].values():
                yield from objects(field)
        for option in schema.get("anyOf", []):
            yield from objects(option)
        if "items" in schema:
            yield from objects(schema["items"])

    bodies = [
        operation["requestBody"]["content"]["application/json"]["schema"]
        for item in doc["paths"].values()
        for operation in item.values()
        if "requestBody" in operation
    ]
    assert bodies, "the sample API has a body to check"
    for body in bodies:
        for found in objects(body):
            assert found.get("additionalProperties") is False, found["title"]
