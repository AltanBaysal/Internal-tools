"""The core's two halves at one address: `/api` is the core's, every other address the UI's."""

from pathlib import Path

from fastapi import FastAPI
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.types import ASGIApp, Receive, Scope, Send

from core.about import NAME, VERSION
from core.api import endpoints


def create_api(core_id: str) -> FastAPI:
    """The API, its addresses written without `/api` as step 6 writes them.

    FastAPI's /docs pages stay off: the agent learns the API from `GET /api` (v1-5), and those
    addresses belong to the UI.
    """
    api = FastAPI(title=NAME, version=VERSION, docs_url=None, redoc_url=None)
    api.include_router(endpoints.router(core_id))
    return api


def serve(api: FastAPI, ui: Path) -> ASGIApp:
    """Mounts the API at `/api` and the built UI beside it.

    The API is its own app, so an address under `/api` that it lacks is its 404, never the UI's;
    bare `/api` is its root, where v1-5 puts the index. `html=True` serves index.html at `/`, and
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
