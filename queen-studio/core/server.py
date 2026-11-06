"""The core's two halves at one address: `/api` is the core's, every other address the UI's."""

from pathlib import Path

from fastapi import Depends, FastAPI
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.types import ASGIApp, Receive, Scope, Send

from core import errors
from core.about import NAME, VERSION
from core.api import endpoints
from core.body import BodyLimit
from core.query import known_query


def create_api(core_id: str) -> FastAPI:
    """The API, its addresses written without `/api` as step 6 writes them.

    FastAPI's /docs pages stay off: the agent learns the API from `GET /api`, and those addresses
    belong to the UI. Each group's section of that index is one of `openapi_tags`.
    """
    api = FastAPI(
        title=NAME,
        version=VERSION,
        docs_url=None,
        redoc_url=None,
        # FastAPI's redirect for a stray slash names an absolute http:// address, the wrong one
        # behind the tunnel's https: such an address is unknown_endpoint instead.
        redirect_slashes=False,
        openapi_tags=[endpoints.SECTION],
        responses=errors.RESPONSES,
        dependencies=[Depends(known_query)],
    )
    errors.handle(api)
    api.add_middleware(BodyLimit)
    api.include_router(endpoints.router(core_id))
    return api


def serve(api: FastAPI, ui: Path) -> ASGIApp:
    """Mounts the API at `/api` and the built UI beside it.

    The API is its own app, so an address under `/api` that it lacks is its 404, never the UI's;
    bare `/api` is its root, the index. `html=True` serves index.html at `/`, and
    StaticFiles keeps every request inside `ui`.
    """
    app = Starlette(
        routes=[
            Mount("/api", app=api),
            Mount("/", app=StaticFiles(directory=ui, html=True)),
        ]
    )

    async def rooted(scope: Scope, receive: Receive, send: Send) -> None:
        # A Mount matches `/api/...` only, so `/api` would reach the UI. Rewritten here rather than
        # redirected: the agent's call answers in one round trip, and the query string is untouched.
        if scope["type"] == "http" and scope["path"] == "/api":
            scope = {**scope, "path": "/api/", "raw_path": b"/api/"}
        await app(scope, receive, send)

    return rooted
