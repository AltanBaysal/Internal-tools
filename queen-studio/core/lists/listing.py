"""A list, declared once beside its group's rules, and joined to FastAPI (step 6, List query).

    FRAMES = Listing(Frame, default=("id", "position", "scene"), order="position")

    @frames.get("/projects/{p}/frames", response_model=FRAMES.page, openapi_extra=FRAMES.extra)
    def every(query: Annotated[Query, Depends(FRAMES.query)]) -> Response:
        return FRAMES.answer(records, query)

The query is read before the endpoint runs, so a wrong one loads no record. The dependencies are
`async`: they read the query only, never the store.
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import Depends, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field
from starlette.datastructures import QueryParams

from core.change import Change, change
from core.errors import ApiError, invalid, problem, template
from core.lists.fields import fields_of
from core.lists.parse import (
    RESERVED,
    Filter,
    Query,
    Refused,
    Tree,
    parse_bulk,
    parse_list,
    parse_one,
    parse_order,
    parse_select,
)
from core.lists.run import Record, TooLarge, filtered, json_bytes, page, pick
from core.query import own_query

# The most one list's answer takes, whatever its `limit` and `select`: an outer bound for the
# core's memory and the tunnel, not the agent's context, which the defaults keep (a page of 100 at
# LIST_ITEM_BYTES is ~25 KB). A whole page of the sample's worst items (MOST_LIMIT × ~0.8 KB) fits;
# a page of 1000 whole frames with long prompts does not, and is told to ask for fewer.
PAGE_BYTES = 1024 * 1024


# A list's answer as the OpenAPI document gives it; the answer itself is sent as it is built. No
# docstring: it would reach the API as the model's description.
class Page[Item: BaseModel](BaseModel):
    items: list[Item] = Field(
        description="This page of the matches, in order; each has only the fields `select` names."
    )
    total: int = Field(description="How many records match the filters, on every page.")
    offset: int = Field(description="Where this page starts among the matches.")
    limit: int = Field(description="The most items a page has; 0 gives the total alone.")


@dataclass(frozen=True)
class Selection:
    """What a bulk change acts on, and the change itself (core/change.py)."""

    filters: tuple[Filter, ...]
    change: Change


class Listing:
    """A list of `item`s: its fields read off the model, its default fields and order.

    Raises ValueError for a field the query cannot read, a field named as a reserved parameter, or a
    default that names no field: met when the group is imported.
    """

    def __init__(self, item: type[BaseModel], default: Sequence[str], order: str) -> None:
        self.fields = fields_of(item)
        clash = sorted({name.split(".")[0] for name in self.fields} & set(RESERVED))
        if clash:
            raise ValueError(f"{item.__name__}: {', '.join(clash)} is a parameter of every list.")
        try:
            self.select = parse_select(",".join(default), self.fields)
            self.order = parse_order(order, self.fields)
        except Refused as refused:
            found = "; ".join(each["message"] for each in refused.problems)
            raise ValueError(f"{item.__name__}'s defaults: {found}") from None
        self.page: type[BaseModel] = Page[item]
        # The address's detail gives these as `list` (core/api/discovery.py); the size test of the
        # default fields finds every list by them.
        self.extra: dict[str, Any] = {"x-list": {"order": order, "select": ",".join(default)}}
        self._names = list(self.fields)

    async def query(
        self, request: Request, params: Annotated[QueryParams, Depends(own_query)]
    ) -> Query:
        """The dependency of the list's GET."""
        try:
            return parse_list(params.multi_items(), self.fields, self.select, self.order)
        except Refused as refused:
            raise self._refused(request, refused.problems) from None

    async def selection(
        self,
        request: Request,
        params: Annotated[QueryParams, Depends(own_query)],
        made: Annotated[Change, Depends(change)],
    ) -> Selection:
        """The dependency of a bulk change (step 6, Bulk selection).

        `change` is its own: without the two headers FastAPI never calls this, and the answer names
        the headers; the query's problems come once they are right.
        """
        try:
            return Selection(parse_bulk(params.multi_items(), self.fields), made)
        except Refused as refused:
            raise self._refused(request, refused.problems) from None

    async def one(
        self, request: Request, params: Annotated[QueryParams, Depends(own_query)]
    ) -> Tree | None:
        """The dependency of one thing's GET: its `select`, the whole record by default."""
        try:
            return parse_one(params.multi_items(), self.fields)
        except Refused as refused:
            raise self._refused(request, refused.problems) from None

    def answer(self, records: Iterable[Record], query: Query) -> Response:
        """The page, sent as built: FastAPI would hold a partial item against the whole model.

        Refused past PAGE_BYTES, never cut short: the caller is told how many items fit.
        """
        try:
            body = page(records, query, PAGE_BYTES)
        except TooLarge as large:
            message = (
                f"The page passes {PAGE_BYTES:,} bytes, the most an answer takes; "
                f"{large.fits} of its items fit."
            )
            hint = (
                f"Ask for at most {large.fits} with `limit`, or for fewer fields with `select`."
                if large.fits
                else "Ask for fewer fields with `select`."
            )
            details = {"problems": [problem("query.limit", "out_of_range", message)]}
            raise ApiError(
                "invalid_request", message, {**details, "fits": large.fits}, hint
            ) from None
        return Response(body, media_type="application/json")

    def matches(self, records: Iterable[Record], selection: Selection) -> list[Record]:
        """The records a bulk change acts on; all-or-nothing is the change's own (step 2)."""
        return filtered(records, selection.filters)

    def answer_one(self, record: Record, select: Tree | None) -> Response:
        """The record's selected fields, held to PAGE_BYTES as a page is."""
        body = json_bytes(pick(record, select))
        if len(body) > PAGE_BYTES:
            message = f"The answer passes {PAGE_BYTES:,} bytes, the most an answer takes."
            details = {"problems": [problem("query.select", "out_of_range", message)]}
            raise ApiError(
                "invalid_request", message, details, "Ask for fewer fields with `select`."
            )
        return Response(body, media_type="application/json")

    def _refused(self, request: Request, problems: list[dict[str, str]]) -> ApiError:
        # Step 6: the error names the list's fields; their kinds are in the address's detail.
        return invalid(template(request), problems, {"fields": self._names})
