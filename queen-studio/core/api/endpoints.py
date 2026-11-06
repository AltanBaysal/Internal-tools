"""The `api` group's endpoints: health today, the discovery index from v1-5."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from core.about import NAME, VERSION


class Health(BaseModel):
    app: str = Field(
        description="Always the app's name: an address that answers otherwise is not ours."
    )
    core: str = Field(
        description="This core's identity. It stays while the machine lives, restarts included."
    )
    version: str = Field(description="The core's version.")


def router(core_id: str) -> APIRouter:
    endpoints = APIRouter()

    @endpoints.get(
        "/health",
        summary="Which app and which core answer here",
        description="Checks the address is this app's core. Calls no other service.",
    )
    def health() -> Health:
        return Health(app=NAME, core=core_id, version=VERSION)

    return endpoints
