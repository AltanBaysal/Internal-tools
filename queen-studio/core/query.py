"""A request's query (step 6, Body: nothing sent is dropped): only the parameters its route reads.

FastAPI leaves an undeclared query parameter unread, so `?paht=/health` would answer as if it were
not there, and of a parameter given twice keeps the last. `known_query` runs before every endpoint
and refuses both with `invalid_request`. A route that parses its own query — a list's PostgREST
query (core/lists), where a filter's field may repeat — takes `own_query` instead, and the check
leaves it to that parser.

Both are `async`: they touch no store, so they need no worker thread of their own.

`QueryLimit` comes before either, before routing: a query over QUERY_BYTES is refused unread. It
is the core's own bound, whatever the server in front of it lets through.
"""

from collections import Counter
from types import NoneType, UnionType
from typing import Annotated, Any, Union, get_args, get_origin

from fastapi import Request
from fastapi.dependencies.models import Dependant
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from starlette.datastructures import QueryParams
from starlette.types import ASGIApp, Receive, Scope, Send

from core.errors import problem, respond

# The most a request's query takes, in bytes as sent. Every count a list's query can drive rests on
# it (core/lists). The largest a list needs: an `in` of 1000 seven-digit ids with its commas sent
# as %2C, ~10 KB, beside a few other filters.
QUERY_BYTES = 16 * 1024


class QueryLimit:
    """Refuses a query over QUERY_BYTES before any route reads it."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        query: bytes = scope.get("query_string", b"")
        if scope["type"] == "http" and len(query) > QUERY_BYTES:
            message = f"The query is over {QUERY_BYTES:,} bytes, the most one request takes."
            await respond(
                "invalid_request",
                message,
                {"problems": [problem("query", "out_of_range", message)]},
                f"Send at most {QUERY_BYTES:,} bytes of query in one request.",
            )(scope, receive, send)
            return
        await self.app(scope, receive, send)


async def own_query(request: Request) -> QueryParams:
    """The query, whole, for a route that parses its own, as the list endpoints do (v1-6)."""
    return request.query_params


async def known_query(request: Request) -> None:
    # Runs as the app's dependency, before the route's own parameters are read: an unknown or
    # repeated parameter is answered alone, the route's other problems on the next try.
    route: Any = request.scope["route"]
    declared = _declared(route.dependant)
    if declared is None:
        return
    given = Counter(name for name, _ in request.query_params.multi_items())
    unknown = [name for name in given if name not in declared]
    # FastAPI keeps the last of two values and drops the first: which was meant is not ours to
    # guess. A parameter that is a list takes each.
    twice = [name for name in given if given[name] > 1 and declared.get(name) is False]
    if unknown or twice:
        raise RequestValidationError(
            [
                {"type": "extra_forbidden", "loc": ("query", name), "msg": "Not declared"}
                for name in unknown
            ]
            + [{"type": "given_twice", "loc": ("query", name), "msg": "Twice"} for name in twice]
        )


def _declared(dependant: Dependant) -> dict[str, bool] | None:
    """The query parameters a route and its dependencies read, each with whether it may repeat;
    None when the route parses its own."""
    if dependant.call is own_query:
        return None
    names: dict[str, bool] = {}
    for parameter in dependant.query_params:
        kind = parameter.field_info.annotation
        if isinstance(kind, type) and issubclass(kind, BaseModel):
            # `Annotated[Filter, Query()]`: the query's parameters are the model's fields.
            for name, field in kind.model_fields.items():
                names[field.alias or name] = _repeats(field.annotation)
        else:
            names[parameter.alias] = _repeats(kind)
    for dependency in dependant.dependencies:
        found = _declared(dependency)
        if found is None:
            return None
        names |= found
    return names


def _repeats(kind: Any) -> bool:
    """Whether a parameter is a list: `list[str]`, `list[str] | None`, `Annotated[list[str], …]`."""
    if get_origin(kind) is Annotated:
        return _repeats(get_args(kind)[0])
    if get_origin(kind) in (Union, UnionType):
        return any(_repeats(part) for part in get_args(kind) if part is not NoneType)
    return get_origin(kind) in (list, tuple, set) or kind in (list, tuple, set)
