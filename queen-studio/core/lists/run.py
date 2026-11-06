"""A parsed query run over a list's records, in memory: never on Drive (step 6, List query). Pure.

Records are JSON-shaped, as `model_dump(mode="json")` gives them. The cost, for N records, F filters
and M matches: the filters O(N·F), a `like` O(N·L·m) for texts of L characters and pieces of
m ≤ 200 (≤ 600 once `ilike` casefolds), linear in L; the order a stable sort per key, O(M log M)
and about O(M) for records that come in order; the page's selection O(limit), its bytes held to a
budget as they are written. `limit=0` neither orders nor selects.
"""

import json
import operator
from collections.abc import Callable, Iterable, Mapping
from datetime import datetime
from typing import Any

from core.lists.fields import Kind
from core.lists.parse import Filter, Order, Query, Tree

Record = Mapping[str, Any]

_COMPARE: dict[str, Callable[[Any, Any], bool]] = {
    "eq": operator.eq,
    "neq": operator.ne,
    "gt": operator.gt,
    "gte": operator.ge,
    "lt": operator.lt,
    "lte": operator.le,
}


class TooLarge(Exception):
    """The page would pass its byte budget; `fits` items would not."""

    def __init__(self, fits: int) -> None:
        super().__init__(f"{fits} items fit")
        self.fits = fits


def page(records: Iterable[Record], query: Query, most_bytes: int) -> bytes:
    """The list's answer (step 6, Body) as JSON: this page of the matches, and how many match.

    Written item by item and counted as it goes: past `most_bytes` it raises TooLarge, never a page
    cut short.
    """
    matched = filtered(records, query.filters)
    head = b'{"items":['
    tail = f'],"total":{len(matched)},"offset":{query.offset},"limit":{query.limit}}}'.encode()
    size = len(head) + len(tail)
    items: list[bytes] = []
    if query.limit and query.offset < len(matched):
        for record in ordered(matched, query.order)[query.offset : query.offset + query.limit]:
            item = json_bytes(pick(record, query.select))
            size += len(item) + (1 if items else 0)
            if size > most_bytes:
                raise TooLarge(len(items))
            items.append(item)
    return head + b",".join(items) + tail


def json_bytes(value: Any) -> bytes:
    """As Starlette's JSONResponse writes it."""
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode()


def filtered(records: Iterable[Record], filters: Iterable[Filter]) -> list[Record]:
    """The records every filter holds for."""
    tests = [_test(each) for each in filters]
    return [record for record in records if all(test(record) for test in tests)]


def ordered(records: list[Record], order: Iterable[Order]) -> list[Record]:
    """Sorted by each key, the first first: one stable sort per key, the last key first."""
    found = list(records)
    for each in reversed(tuple(order)):
        found.sort(key=_rank(each), reverse=each.descending)
    return found


def _rank(each: Order) -> Callable[[Record], tuple[bool, Any]]:
    name, key, down = each.field.name, _key(each.field.kind), each.descending

    def rank(record: Record) -> tuple[bool, Any]:
        # A null goes last either way: under `reverse` the flag that puts it last flips.
        value = value_of(record, name)
        return (not down, None) if value is None else (down, key(value))

    return rank


def pick(record: Record, select: Tree | None) -> Any:
    """The selected fields, nested as the record nests them; None selects the whole record."""
    if select is None:
        return record
    picked: dict[str, Any] = {}
    for name, inner in select.items():
        value: Any = record.get(name)
        picked[name] = pick(value, inner) if inner is not None and _is_object(value) else value
    return picked


def value_of(record: Record, name: str) -> Any:
    """A dotted field's value; null when the record, or an object on the way, lacks it."""
    value: Any = record
    for part in name.split("."):
        if not _is_object(value):
            return None
        value = value.get(part)
    return value


def _is_object(value: Any) -> bool:
    return isinstance(value, Mapping)


def _test(each: Filter) -> Callable[[Record], bool]:
    name = each.field.name
    if each.op == "is":
        # `is` alone sees null, and holds or not either way (SQL's IS).
        return lambda record: (value_of(record, name) is each.value) != each.negate
    check = _check(each)
    key = _key(each.field.kind)

    def test(record: Record) -> bool:
        # As in SQL: any other comparison with null is never true, `not.` included.
        value = value_of(record, name)
        return value is not None and check(key(value)) != each.negate

    return test


def _check(each: Filter) -> Callable[[Any], bool]:
    wanted = each.value
    if each.op == "in":
        return lambda value: value in wanted
    if each.op in ("like", "ilike"):
        return wanted.matches
    compare = _COMPARE[each.op]
    return lambda value: compare(value, wanted)


def _key(kind: Kind) -> Callable[[Any], Any]:
    # A record's time is text (step 6, Time); read as a time, a fraction of a second sorts right.
    return datetime.fromisoformat if kind == "time" else _same


def _same(value: Any) -> Any:
    return value
