"""Every error the API answers, in one shape of four fields (step 6, Errors; CODE-STANDARD).

A group raises `ApiError` with a code from `CODES`; FastAPI's own failures — validation, an unknown
address, a method the address lacks, an exception nobody caught — are turned into the same shape
here, so no answer leaves the API in FastAPI's `{"detail": ...}`.
"""

import json
from dataclasses import dataclass
from typing import Any, Literal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, ValidationException
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel, Field, ValidationError
from starlette.exceptions import HTTPException

from core.change import HEADERS_HINT


class Error(BaseModel):
    code: str = Field(description="What went wrong, as a fixed name to act on.")
    message: str = Field(
        description="What is wrong and why; a service's failure in the service's own words."
    )
    details: dict[str, Any] = Field(
        description="The ids the error is about. `problems` lists each problem, a field's as "
        "{field, code, message}."
    )
    hint: str | None = Field(
        description="The next step, when the core knows it for certain; otherwise null."
    )


@dataclass(frozen=True)
class Code:
    status: int
    # Whether the hint is always given — a rule's next step, or a service error's state and option —
    # or always null (step 6's Hint column). Checked on every error answer the tests receive.
    hint: bool


# Step 6's table, as far as the core raises it today; the item that raises a code adds its row.
CODES: dict[str, Code] = {
    "invalid_request": Code(400, hint=True),
    "unknown_endpoint": Code(404, hint=True),
    "method_not_allowed": Code(405, hint=True),
    "internal": Code(500, hint=False),
}

# What is wrong with one field of a 400 (step 6, Format).
FieldCode = Literal[
    "missing",
    "unknown",
    "wrong_type",
    "not_allowed",
    "out_of_range",
    "not_accepted",
    "not_supported",
    "name_rule",
    "duplicate",
    "bad_query",
]

# Every operation's error answer in the OpenAPI document; naming `default` also keeps FastAPI from
# adding its 422, which this API never answers.
RESPONSES: dict[int | str, dict[str, Any]] = {
    "default": {"model": Error, "description": "Any error, in its four fields."}
}


class ApiError(Exception):
    """An error a rule of the core raises; its status is its code's."""

    def __init__(
        self,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        hint: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status = CODES[code].status
        self.error = Error(code=code, message=message, details=details or {}, hint=hint)

    def response(self, headers: dict[str, str] | None = None) -> JSONResponse:
        return JSONResponse(self.error.model_dump(), status_code=self.status, headers=headers)


def respond(
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    hint: str | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return ApiError(code, message, details, hint).response(headers)


# What an error echoes is cut there, in bytes as the answer sends them: an address, a field's name
# or an exception's text can be any length, and the whole error is held to a budget of the agent's
# context (tests/budgets.py, ERROR_BYTES 2048). The rest stays in the log.
ADDRESS_BYTES = 200
MESSAGE_BYTES = 300
FIELD_BYTES = 48
PROBLEM_BYTES = 128
# Problems listed, each at most FIELD_BYTES + PROBLEM_BYTES and its keys (~220 B); the rest counted.
PROBLEMS_SHOWN = 6


def problem(field: str, code: FieldCode, message: str) -> dict[str, str]:
    return {"field": field, "code": code, "message": message}


# The API's root, where core/api/endpoints.py serves the index; called `/api`, as its hints name it.
INDEX = "/"


def unknown(address: str) -> ApiError:
    return ApiError(
        "unknown_endpoint",
        f"`{_cut(address, ADDRESS_BYTES)}` is not an address of this API.",
        hint="`GET /api` lists every address.",
    )


def handle(api: FastAPI) -> None:
    """Puts the four-field shape on every failure FastAPI and Starlette answer themselves.

    The handlers are `async`: they touch no store, so they need no worker thread of their own.
    """

    @api.exception_handler(ApiError)
    async def raised(request: Request, error: ApiError) -> JSONResponse:
        return error.response()

    @api.exception_handler(RequestValidationError)
    async def invalid(request: Request, error: RequestValidationError) -> JSONResponse:
        return _invalid(request, [_field_problem(found) for found in error.errors()])

    @api.exception_handler(HTTPException)
    async def routing(request: Request, error: HTTPException) -> JSONResponse:
        if error.status_code == 404:
            return unknown(_address(request)).response()
        if error.status_code == 405:
            return _method_not_allowed(api, request, error)
        # Starlette's and FastAPI's own; the core raises ApiError. A 4xx is a request it could not
        # read, such as a body cut off mid-read.
        if error.status_code < 500:
            message = f"`body` could not be read: {error.detail}."
            return _invalid(request, [problem("body", "wrong_type", message)])
        return respond("internal", f"{error.status_code}: {error.detail}")

    @api.exception_handler(Exception)
    async def failed(request: Request, error: Exception) -> JSONResponse:
        # Starlette raises the exception again once this is sent, so Uvicorn logs its traceback.
        return respond("internal", _failure(error))


def _sent(text: str) -> int:
    """Bytes of `text` as the answer sends it: a control character is six, `"` two, `ğ` two."""
    return len(json.dumps(text, ensure_ascii=False).encode("utf-8")) - 2


def _cut(text: str, most: int) -> str:
    if _sent(text) <= most:
        return text
    # Each character is at least a byte, so `most` characters are the most that may fit.
    text = text[:most]
    while _sent(text + "…") > most:
        text = text[:-1]
    return text + "…"


def _failure(error: Exception) -> str:
    # A validation error's text carries the values and the source line it failed on: the caller
    # gets its kind and count, the log the rest.
    if isinstance(error, ValidationException | ValidationError):
        count = len(error.errors())
        return f"{type(error).__name__}: {count} validation error{'' if count == 1 else 's'}"
    return _cut(f"{type(error).__name__}: {error}", MESSAGE_BYTES)


def _invalid(request: Request, problems: list[dict[str, str]]) -> JSONResponse:
    message = (
        problems[0]["message"]
        if len(problems) == 1
        else f"The request has {len(problems)} problems; nothing was done."
    )
    details: dict[str, Any] = {"problems": problems[:PROBLEMS_SHOWN]}
    if len(problems) > PROBLEMS_SHOWN:
        details["more"] = len(problems) - PROBLEMS_SHOWN
    places = {found["field"].split(".")[0] for found in problems}
    hints: list[str] = []
    if "header" in places:
        hints.append(HEADERS_HINT)
    if places - {"header"}:
        # Raised once a route is found: its address is the template the index writes.
        address = _template(request)
        hints.append(
            "`GET /api` takes only `path`, an address `GET /api` lists."
            if address == INDEX
            else f"`GET /api?path={address}` gives what this address takes."
        )
    return respond("invalid_request", message, details, " ".join(hints))


def _template(request: Request) -> str:
    # `path_format` drops a converter, `{name:path}` being `{name}`, as the OpenAPI document does.
    # A route that is no APIRoute, FastAPI's /openapi.json, may leave the mount in `scope["route"]`
    # or nothing: its address is the request's.
    route = request.scope.get("route")
    return route.path_format if isinstance(route, APIRoute) else _address(request)


def _address(request: Request) -> str:
    # The address as the index writes it, without the prefix the API is mounted at.
    return request.scope["path"].removeprefix(request.scope.get("root_path", ""))


def _method_not_allowed(api: FastAPI, request: Request, error: HTTPException) -> JSONResponse:
    # The router stops at the first route whose address matches: `scope["route"]` is that route and
    # `Allow` names its methods only, so an address served by a GET and a DELETE route would lose
    # one. The OpenAPI document, built once and kept, has them all.
    address = _template(request)
    item: dict[str, Any] | None = api.openapi()["paths"].get(address)
    if item is not None:
        methods = sorted(method.upper() for method in item)
        takes = ", ".join(methods)
        called = address
        hint = f"`{address}` takes {takes}; `GET /api?path={address}` describes it."
    else:
        # Outside the document — the index, FastAPI's /openapi.json — the address has one route,
        # so its own `Allow` is whole. No detail describes it: the hint names the call itself.
        allowed = (error.headers or {}).get("Allow", "")
        methods = sorted(method for method in allowed.split(", ") if method not in ("", "HEAD"))
        takes = ", ".join(methods)
        called = "/api" if address == INDEX else "/api" + address
        hint = (
            f"`GET {called}` is the only call at this address."
            if methods == ["GET"]
            else f"`{called}` takes {takes}."
        )
    return respond(
        "method_not_allowed",
        f"`{called}` does not take {request.method}.",
        {"methods": methods},
        hint,
        headers={"Allow": takes},
    )


# Pydantic's error types, said in our words. `{field}` is the field's path; the rest is pydantic's
# context for that type. A type not here keeps pydantic's own message, after the field.
_MESSAGES: dict[str, tuple[FieldCode, str]] = {
    "missing": ("missing", "`{field}` is missing."),
    "extra_forbidden": ("unknown", "`{field}` is not a field this address takes."),
    "literal_error": ("not_allowed", "`{field}` must be {expected}."),
    "enum": ("not_allowed", "`{field}` must be {expected}."),
    "string_pattern_mismatch": ("not_allowed", "`{field}` must match `{pattern}`."),
    "greater_than": ("out_of_range", "`{field}` must be more than {gt}."),
    "greater_than_equal": ("out_of_range", "`{field}` must be at least {ge}."),
    "less_than": ("out_of_range", "`{field}` must be less than {lt}."),
    "less_than_equal": ("out_of_range", "`{field}` must be at most {le}."),
    "string_too_short": ("out_of_range", "`{field}` must have at least {min_length} {characters}."),
    "string_too_long": ("out_of_range", "`{field}` must have at most {max_length} {characters}."),
    "too_short": ("out_of_range", "`{field}` must have at least {min_length} {items}."),
    "too_long": ("out_of_range", "`{field}` must have at most {max_length} {items}."),
    "string_type": ("wrong_type", "`{field}` must be a string."),
    "int_type": ("wrong_type", "`{field}` must be a whole number."),
    "int_parsing": ("wrong_type", "`{field}` must be a whole number."),
    "int_from_float": ("wrong_type", "`{field}` must be a whole number."),
    "float_type": ("wrong_type", "`{field}` must be a number."),
    "float_parsing": ("wrong_type", "`{field}` must be a number."),
    "bool_type": ("wrong_type", "`{field}` must be true or false."),
    "bool_parsing": ("wrong_type", "`{field}` must be true or false."),
    "dict_type": ("wrong_type", "`{field}` must be a JSON object."),
    "model_type": ("wrong_type", "`{field}` must be a JSON object."),
    "model_attributes_type": ("wrong_type", "`{field}` must be a JSON object."),
    "list_type": ("wrong_type", "`{field}` must be a list."),
    "json_invalid": ("wrong_type", "`{field}` is not JSON: {error}."),
}


def _field_problem(found: Any) -> dict[str, str]:
    kind: str = found["type"]
    # A JSON error's place ends in the character's position, which is no field: the body is.
    place = found["loc"][:1] if kind == "json_invalid" else found["loc"]
    # A name is the caller's, any length: cut, as is the message it is said in (`?=1` has none).
    field = _cut(".".join(str(part) or "(empty)" for part in place), FIELD_BYTES)
    context: dict[str, Any] = found.get("ctx", {})
    code, template = _MESSAGES.get(kind, ("wrong_type", "`{field}`: {msg}."))
    plural = context.get("min_length", context.get("max_length")) != 1
    message = template.format(
        field=field,
        msg=found["msg"],
        characters="characters" if plural else "character",
        items="items" if plural else "item",
        **context,
    )
    return problem(field, code, _cut(message, PROBLEM_BYTES))
