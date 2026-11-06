"""A list's query, read against its fields (step 6, List query and Bulk selection). Pure.

PostgREST's syntax: `<field>=[not.]<operator>.<value>` filters, all of which must hold; `order`,
`limit`, `offset` and `select`. A filter's field may come twice — a date range names it so — but a
reserved parameter only once: which of two limits was meant is not ours to guess. Every problem is
counted, not only the first, and each value is read with its field's kind, so `status=eq.waitng` is
refused rather than answered with an empty list.

What a query may make the core do is bounded before it is done (CODE-STANDARD, Cost): two filters
a field, MOST_IN values in an `in`, each field once in `order` and `select`, a pattern of
MOST_CHARACTERS; the whole query by the core's QUERY_BYTES (core/query.py), refused before routing.
"""

import re
from collections.abc import Callable, Container, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal, cast, get_args

from core.errors import FIELD_BYTES, PROBLEM_BYTES, FieldCode, cut, problem
from core.lists.fields import Kind, ListField
from core.lists.pattern import MOST_CHARACTERS, Pattern, TooLong

Op = Literal["eq", "neq", "in", "gt", "gte", "lt", "lte", "like", "ilike", "is"]
_OPS = frozenset(get_args(Op))

# A field's kind as a message says it, and what it takes; `is.<value>` is one operator per value.
_KIND_WORDS: dict[Kind, str] = {
    "text": "text",
    "int": "a whole number",
    "number": "a number",
    "bool": "true or false",
    "time": "a time",
    "object": "an object",
    "list": "a list",
}
_ORDERED = ("eq", "neq", "in", "gt", "gte", "lt", "lte", "is.null")
_TAKES: dict[Kind, tuple[str, ...]] = {
    "text": ("eq", "neq", "in", "like", "ilike", "is.null"),
    "int": _ORDERED,
    "number": _ORDERED,
    "time": _ORDERED,
    "bool": ("eq", "neq", "in", "is.true", "is.false", "is.null"),
    "object": ("is.null",),
    "list": ("is.null",),
}
_IS_VALUES: dict[str, bool | None] = {"null": None, "true": True, "false": False}

# Parameters that are no field: a list may not name a field so (core/lists/listing.py).
RESERVED = ("select", "order", "limit", "offset", "all")
_PAGED = ("select", "order", "limit", "offset")
DEFAULT_LIMIT = 100
MOST_LIMIT = 1000
# A range is two filters on one field; a third says nothing a range does not.
FILTERS_PER_FIELD = 2
# The values of one `in`: as many as a page holds.
MOST_IN = MOST_LIMIT

# The literal forms are bounded too: 18 digits stay a machine-sized number.
_INT = re.compile(r"-?[0-9]{1,18}")
_NUMBER = re.compile(r"-?[0-9]{1,18}(\.[0-9]{1,18})?")
_DAY = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_TIME = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")

# What is selected: each name's own selection, or None for its whole value.
type Tree = dict[str, Tree | None]


@dataclass(frozen=True)
class Filter:
    field: ListField
    op: Op
    negate: bool
    # By operator: a value of the field's kind; a frozenset for `in`; a Pattern for `like` and
    # `ilike`; None, True or False for `is`.
    value: Any


@dataclass(frozen=True)
class Order:
    field: ListField
    descending: bool


@dataclass(frozen=True)
class Query:
    filters: tuple[Filter, ...]
    order: tuple[Order, ...]  # what was asked, then the list's default for ties
    limit: int
    offset: int
    select: Tree | None  # None: the whole record


class Refused(Exception):
    """The query's problems, each `{field, code, message}`, its message cut to PROBLEM_BYTES."""

    def __init__(self, problems: list[dict[str, str]]) -> None:
        super().__init__(f"{len(problems)} problems")
        self.problems = [
            {**found, "message": cut(found["message"], PROBLEM_BYTES)} for found in problems
        ]


class _Wrong(Exception):
    def __init__(self, code: FieldCode, message: str) -> None:
        super().__init__(message)
        self.code: FieldCode = code
        self.message = message


Pairs = Sequence[tuple[str, str]]
Fields = dict[str, ListField]


def parse_list(
    pairs: Pairs, fields: Fields, select: Tree | None, order: tuple[Order, ...]
) -> Query:
    """A list's GET; `select` and `order` are the list's defaults."""
    problems: list[dict[str, str]] = []
    given = _reserved(pairs, _PAGED, problems)
    filters = _filters(pairs, fields, problems, skipped=_PAGED, refused=())
    asked: tuple[Order, ...] = ()
    if "order" in given:
        asked = _caught(lambda: parse_order(given["order"], fields), problems) or ()
    if "select" in given:
        select = _caught(lambda: parse_select(given["select"], fields), problems)
    limit = _whole(given, "limit", DEFAULT_LIMIT, MOST_LIMIT, problems)
    offset = _whole(given, "offset", 0, None, problems)
    if problems:
        raise Refused(problems)
    named = {each.field.name for each in asked}
    ties = tuple(each for each in order if each.field.name not in named)
    return Query(filters, asked + ties, limit, offset, select)


def parse_bulk(pairs: Pairs, fields: Fields) -> tuple[Filter, ...]:
    """A bulk change's filters: its list's, or none with `all=true` for every one."""
    problems: list[dict[str, str]] = []
    given = _reserved(pairs, ("all",), problems)
    filters = _filters(pairs, fields, problems, skipped=("all",), refused=_PAGED)
    if given.get("all", "true") != "true":
        problems.append(problem("query.all", "not_allowed", "`query.all` must be true."))
    if not problems and not filters and "all" not in given:
        message = "A bulk change names what it acts on: filters, or `all=true` for every one."
        problems.append(problem("query", "missing", message))
    if problems:
        raise Refused(problems)
    return filters


def parse_one(pairs: Pairs, fields: Fields) -> Tree | None:
    """One thing's GET: `select` alone, the whole record by default."""
    problems: list[dict[str, str]] = []
    given = _reserved(pairs, ("select",), problems)
    for name, _ in pairs:
        if name != "select":
            at = _at(name)
            problems.append(problem(at, "unknown", f"`{at}` is not a field this address takes."))
    select = None
    if "select" in given:
        select = _caught(lambda: parse_select(given["select"], fields), problems)
    if problems:
        raise Refused(problems)
    return select


def parse_order(text: str, fields: Fields) -> tuple[Order, ...]:
    """`<field>[.asc|.desc],…`, each field once; a field's name may hold dots, so the direction is
    the last part."""
    found: dict[str, Order] = {}
    for item in (item.strip() for item in text.split(",")):
        name, _, direction = item.rpartition(".")
        if direction not in ("asc", "desc"):
            name, direction = item, "asc"
        field = _named(name, "order", fields, found)
        if field.kind in ("object", "list"):
            words = _KIND_WORDS[field.kind]
            message = f"`query.order` cannot order by `{field.name}`: it is {words}."
            raise Refused([problem("query.order", "bad_query", message)])
        found[name] = Order(field, descending=direction == "desc")
    return tuple(found.values())


def parse_select(text: str, fields: Fields) -> Tree | None:
    """None for `*`, the whole record; otherwise each name, once, nested in its objects."""
    names = [item.strip() for item in text.split(",")]
    if "*" in names:
        return None
    tree: Tree = {}
    seen: set[str] = set()
    for name in names:
        _named(name, "select", fields, seen)
        seen.add(name)
        node = tree
        *outer, last = name.split(".")
        for part in outer:
            inner = node.setdefault(part, {})
            if inner is None:
                break  # its object is selected whole
            node = inner
        else:
            node[last] = None
    return tree


def _reserved(
    pairs: Pairs, names: tuple[str, ...], problems: list[dict[str, str]]
) -> dict[str, str]:
    """Each reserved parameter given, by name; a second one is `duplicate`."""
    given: dict[str, str] = {}
    twice: set[str] = set()
    for name, value in pairs:
        if name not in names:
            continue
        if name not in given:
            given[name] = value
        elif name not in twice:
            twice.add(name)
            at = f"query.{name}"
            problems.append(problem(at, "duplicate", f"`{at}` is given twice; it takes one."))
    return given


def _filters(
    pairs: Pairs,
    fields: Fields,
    problems: list[dict[str, str]],
    skipped: tuple[str, ...],
    refused: tuple[str, ...],
) -> tuple[Filter, ...]:
    found: list[Filter] = []
    counted: dict[str, int] = {}
    for name, text in pairs:
        if name in skipped:
            continue
        at = _at(name)
        if name in refused:
            message = f"`{at}` is not taken by a bulk change: it acts on every match."
            problems.append(problem(at, "unknown", message))
        elif name not in fields:
            problems.append(problem(at, "unknown", f"`{at}` is not a field of this list."))
        else:
            counted[name] = counted.get(name, 0) + 1
            if counted[name] > FILTERS_PER_FIELD:
                # Said once a field, and the filter is not read: the bound comes before the work.
                if counted[name] == FILTERS_PER_FIELD + 1:
                    message = f"`{at}` takes at most {FILTERS_PER_FIELD} filters, a range's two."
                    problems.append(problem(at, "out_of_range", message))
                continue
            try:
                found.append(_filter(at, fields[name], text))
            except _Wrong as wrong:
                problems.append(problem(at, wrong.code, wrong.message))
    return tuple(found)


def _filter(at: str, field: ListField, text: str) -> Filter:
    negate = text.startswith("not.")
    op, dot, value = text.removeprefix("not.").partition(".")
    takes = _TAKES[field.kind]
    if not dot or op not in _OPS:
        message = f"`{at}` must be an operator and a value; it takes {', '.join(takes)}."
        raise _Wrong("bad_query", message)
    if (f"is.{value}" if op == "is" else op) not in takes:
        then = "; filter by one of its fields" if field.kind == "object" else ""
        message = f"`{at}` is {_KIND_WORDS[field.kind]}: it takes {', '.join(takes)}{then}."
        raise _Wrong("bad_query", message)
    if op == "is":
        return Filter(field, "is", negate, _IS_VALUES[value])
    if op == "in":
        return Filter(field, "in", negate, _in(at, field, value))
    if op in ("like", "ilike"):
        try:
            pattern = Pattern.read(value, folded=op == "ilike")
        except TooLong:
            message = f"`{at}`: a pattern has at most {MOST_CHARACTERS} characters."
            raise _Wrong("out_of_range", message) from None
        return Filter(field, cast(Op, op), negate, pattern)
    return Filter(field, cast(Op, op), negate, _value(at, field, value))


def _in(at: str, field: ListField, value: str) -> frozenset[Any]:
    if not (value.startswith("(") and value.endswith(")")):
        raise _Wrong("bad_query", f"`{at}` must list its values in parentheses, as in `in.(a,b)`.")
    # No quoting: a text holding a comma is found with `eq`.
    items = value[1:-1].split(",") if value != "()" else []
    if len(items) > MOST_IN:
        raise _Wrong("out_of_range", f"`{at}` takes at most {MOST_IN} values in `in`.")
    return frozenset(_value(at, field, item) for item in items)


def _value(at: str, field: ListField, text: str) -> Any:
    if field.allowed:
        if text not in field.allowed:
            raise _Wrong("not_allowed", f"`{at}` must be one of {', '.join(field.allowed)}.")
        return text
    match field.kind:
        case "int":
            if _INT.fullmatch(text):
                return int(text)
        case "number":
            # Digits and a point only: `nan` and `inf` never get this far.
            if _NUMBER.fullmatch(text):
                return float(text)
        case "bool":
            if text in ("true", "false"):
                return text == "true"
        case "time":
            found = _time(text)
            if found is not None:
                return found
            message = f"`{at}` must be a time, 2026-11-04T09:12:00Z, or a day, 2026-11-04."
            raise _Wrong("wrong_type", message)
        case _:
            return text
    raise _Wrong("wrong_type", f"`{at}` must be {_KIND_WORDS[field.kind]}.")


def _time(text: str) -> datetime | None:
    # Step 6: a time is UTC to the second; a day alone is its 00:00.
    try:
        if _DAY.fullmatch(text):
            return datetime.fromisoformat(text).replace(tzinfo=UTC)
        if _TIME.fullmatch(text):
            return datetime.fromisoformat(text)
    except ValueError:
        return None
    return None


def _whole(
    given: dict[str, str], name: str, default: int, most: int | None, problems: list[dict[str, str]]
) -> int:
    if name not in given:
        return default
    at = f"query.{name}"
    message = (
        f"`{at}` must be a whole number from 0 to {most}."
        if most is not None
        else f"`{at}` must be a whole number, 0 or more."
    )
    text = given[name]
    if not _INT.fullmatch(text):
        problems.append(problem(at, "wrong_type", message))
        return default
    number = int(text)
    if number < 0 or (most is not None and number > most):
        problems.append(problem(at, "out_of_range", message))
    return number


def _named(name: str, place: str, fields: Fields, seen: Container[str]) -> ListField:
    """The field `query.<place>` names; refused when unknown, empty, or named twice (`seen`)."""
    at = f"query.{place}"
    if not name:
        raise Refused([problem(at, "bad_query", f"`{at}` names an empty field.")])
    if name not in fields:
        message = f"`{at}` names `{cut(name, FIELD_BYTES)}`, not a field of this list."
        raise Refused([problem(at, "unknown", message)])
    if name in seen:
        raise Refused([problem(at, "duplicate", f"`{at}` names `{name}` twice.")])
    return fields[name]


def _caught[T](read: Callable[[], T], problems: list[dict[str, str]]) -> T | None:
    try:
        return read()
    except Refused as refused:
        problems.extend(refused.problems)
        return None


def _at(name: str) -> str:
    # A name is the caller's, any length; `?=1` has none.
    return cut(f"query.{name or '(empty)'}", FIELD_BYTES)
