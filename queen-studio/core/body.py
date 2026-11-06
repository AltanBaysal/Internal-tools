"""A request's body (step 6, Body): JSON, only the fields its address takes, 1 MiB at most."""

from pydantic import BaseModel, ConfigDict
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from core.errors import problem, respond

# The largest body the API takes, an edit's `replace` of 5000 places, is ~250–300 KB: this is
# about 3.5 times that. Every count a body drives — its items, its unknown keys, their errors —
# rests on it.
MAX_BYTES = 1024 * 1024
# The bodies all requests hold at once, in bytes: parsed, a body grows up to ~23 times
# (`[{},{}…]`), and parsed bodies pile up while their endpoints wait for a worker thread. Counted
# in bytes, not bodies, so many small bodies are not refused as if each were the largest. Eight of
# the largest at once, ~190 MB parsed at worst; ~27 of the largest real ones.
HELD_BYTES = 8 * MAX_BYTES


class RequestBody(BaseModel):
    """What every request body is built on: a field it does not declare is an error, never dropped.

    Pydantic drops an undeclared field silently by default, and the core drops nothing the agent
    sent (step 1). A test walks every body in the OpenAPI document for it.
    """

    model_config = ConfigDict(extra="forbid")


class BodyLimit:
    """Refuses a body over MAX_BYTES, or one past HELD_BYTES with the others held, before any
    endpoint reads it.

    Counted as it arrives, so a chunked body with no Content-Length is held to it too: an endpoint
    holds its body whole in memory, and Colab's memory is the jobs'. At most MAX_BYTES and one chunk
    are read before the answer. A body counts as held until its request is answered; a request
    without one, a GET or health, is never refused here.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        # Bytes of the bodies being read or answered now. Checked and added with no `await`
        # between, so two requests on the event loop cannot both pass on the same room.
        self.held = 0

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        size = 0
        try:
            chunks: list[bytes] = []
            more = True
            while more:
                message = await receive()
                if message["type"] != "http.request":
                    return  # the caller left: no one to answer
                chunk: bytes = message.get("body", b"")
                if size + len(chunk) > MAX_BYTES:
                    await _too_large()(scope, receive, send)
                    return
                if self.held + len(chunk) > HELD_BYTES:
                    await _busy()(scope, receive, send)
                    return
                size += len(chunk)
                self.held += len(chunk)
                chunks.append(chunk)
                more = message.get("more_body", False)
            body = b"".join(chunks)
            given = False

            async def replay() -> Message:
                # The body once, whole; then the caller's own messages, such as its leaving.
                nonlocal given
                if given:
                    return await receive()
                given = True
                return {"type": "http.request", "body": body, "more_body": False}

            await self.app(scope, replay, send)
        finally:
            self.held -= size


def _busy() -> ASGIApp:
    return respond(
        "busy",
        f"This body would take the bodies held at once past {HELD_BYTES:,} bytes, the most the "
        "core holds; it was not read.",
        hint="Nothing was done; send it again once the requests before it are answered.",
    )


def _too_large() -> ASGIApp:
    message = f"The body is over {MAX_BYTES:,} bytes, the most one request takes."
    return respond(
        "invalid_request",
        message,
        {"problems": [problem("body", "out_of_range", message)]},
        f"Send at most {MAX_BYTES:,} bytes of body in one request.",
    )
