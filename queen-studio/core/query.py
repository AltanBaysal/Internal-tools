"""A request's query (step 6, Body: nothing sent is dropped): only the parameters its route reads.

FastAPI leaves an undeclared query parameter unread, so `?paht=/health` would answer as if it were
not there. `known_query` runs before every endpoint and refuses such a parameter with
`invalid_request`. A route that parses its own query — the lists' PostgREST query (v1-6) — takes
`own_query` instead, and the check leaves it to that parser.

Both are `async`: they touch no store, so they need no worker thread of their own.
"""

from typing import Any

from fastapi import Request
from fastapi.dependencies.models import Dependant
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from starlette.datastructures import QueryParams


async def own_query(request: Request) -> QueryParams:
    """The query, whole, for a route that parses its own, as the list endpoints do (v1-6)."""
    return request.query_params


async def known_query(request: Request) -> None:
    # Runs as the app's dependency, before the route's own parameters are read: an unknown
    # parameter is answered alone, the route's other problems on the next try.
    route: Any = request.scope["route"]
    declared = _declared(route.dependant)
    if declared is None:
        return
    unknown = [name for name in request.query_params if name not in declared]
    if unknown:
        raise RequestValidationError(
            [
                {"type": "extra_forbidden", "loc": ("query", name), "msg": "Not declared"}
                for name in unknown
            ]
        )


def _declared(dependant: Dependant) -> set[str] | None:
    """The query parameters a route and its dependencies read; None when it parses its own."""
    if dependant.call is own_query:
        return None
    names: set[str] = set()
    for parameter in dependant.query_params:
        kind = parameter.field_info.annotation
        if isinstance(kind, type) and issubclass(kind, BaseModel):
            # `Annotated[Filter, Query()]`: the query's parameters are the model's fields.
            names |= {field.alias or name for name, field in kind.model_fields.items()}
        else:
            names.add(parameter.alias)
    for dependency in dependant.dependencies:
        found = _declared(dependency)
        if found is None:
            return None
        names |= found
    return names
