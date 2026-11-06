"""A request's body (step 6, Body): JSON, only the fields its address takes, 4 MB at most."""

from pydantic import BaseModel, ConfigDict
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from core.errors import problem, respond

# The whole order of 20,000 frames is ~120 KB; nothing the API takes comes near this.
MAX_BYTES = 4 * 1024 * 1024


class RequestBody(BaseModel):
    """What every request body is built on: a field it does not declare is an error, never dropped.

    Pydantic drops an undeclared field silently by default, and the core drops nothing the agent
    sent (step 1). A test walks every body in the OpenAPI document for it.
    """

    model_config = ConfigDict(extra="forbid")


class BodyLimit:
    """Refuses a body over MAX_BYTES before any endpoint reads it.

    Counted as it arrives, so a chunked body with no Content-Length is held to it too: an endpoint
    holds its body whole in memory, and Colab's memory is the jobs'. At most MAX_BYTES and one chunk
    are read before the answer.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        chunks: list[bytes] = []
        size = 0
        more = True
        while more:
            message = await receive()
            if message["type"] != "http.request":
                return  # the caller left: no one to answer
            chunk: bytes = message.get("body", b"")
            size += len(chunk)
            if size > MAX_BYTES:
                await _too_large()(scope, receive, send)
                return
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


def _too_large() -> ASGIApp:
    megabytes = MAX_BYTES // (1024 * 1024)
    message = f"The body is over {megabytes} MB, the most one request takes."
    return respond(
        "invalid_request",
        message,
        {"problems": [problem("body", "out_of_range", message)]},
        f"Send at most {megabytes} MB in one request.",
    )
