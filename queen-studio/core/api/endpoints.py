"""The `api` group's endpoints: the discovery index and health."""

from typing import Annotated, Any

from fastapi import APIRouter, FastAPI, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from core.about import NAME, VERSION
from core.api import discovery
from core.errors import INDEX, unknown

# The index's section for this group; each group names its own beside its router.
SECTION = {
    "name": "Discovery",
    "description": "How to learn this API, and to check that the address answers with this app's "
    "core.",
}


class Health(BaseModel):
    app: str = Field(
        description="Always the app's name: an address that answers otherwise is not ours."
    )
    core: str = Field(
        description="This core's identity. It stays while the machine lives, restarts included."
    )
    version: str = Field(description="The core's version.")


def router(core_id: str) -> APIRouter:
    endpoints = APIRouter(tags=[SECTION["name"]])

    # Out of the OpenAPI document: it is the document's reading, not one of its addresses, so it
    # is no line of its own index; the rules name it. At `errors.INDEX`, whose errors name it
    # `/api`. `async`, unlike FOUNDATION 2's endpoints: it reads memory only, never the store.
    @endpoints.get(INDEX, include_in_schema=False)
    async def index(
        request: Request,
        path: Annotated[str | None, Query(description="An address as the index writes it.")] = None,
    ) -> JSONResponse:
        # FastAPI builds the document once and keeps it; each answer reads it from memory.
        api: FastAPI = request.app
        doc: dict[str, Any] = api.openapi()
        if path is None:
            return JSONResponse(discovery.index(doc))
        found = discovery.detail(doc, path)
        if found is None:
            raise unknown(path)
        return JSONResponse(found)

    @endpoints.get(
        "/health",
        summary="Which app and which core answer here",
        description="Checks the address is this app's core. Calls no other service.",
    )
    def health() -> Health:
        return Health(app=NAME, core=core_id, version=VERSION)

    return endpoints
