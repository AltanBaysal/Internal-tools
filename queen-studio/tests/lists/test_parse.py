from datetime import UTC, datetime
from typing import Any, Literal

import pytest
from pydantic import BaseModel

from core.errors import FIELD_BYTES
from core.lists.fields import fields_of
from core.lists.parse import (
    Filter,
    Op,
    Order,
    Query,
    Refused,
    parse_bulk,
    parse_list,
    parse_one,
    parse_order,
    parse_select,
)
from core.lists.pattern import Pattern


class Look(BaseModel):
    status: Literal["waiting", "running", "done"]
    prompt: str | None


class Note(BaseModel):
    id: int
    scene: str
    score: float | None
    archived: bool
    updated: datetime
    photo: Look
    video: Look | None
    tags: list[str]


FIELDS = fields_of(Note)
DEFAULT_ORDER = (Order(FIELDS["id"], descending=False),)


def listed(*pairs: tuple[str, str]) -> Query:
    return parse_list(list(pairs), FIELDS, select=None, order=DEFAULT_ORDER)


def refused(*pairs: tuple[str, str]) -> list[dict[str, str]]:
    with pytest.raises(Refused) as caught:
        listed(*pairs)
    return caught.value.problems


def test_no_query_is_the_lists_defaults() -> None:
    assert listed() == Query(filters=(), order=DEFAULT_ORDER, limit=100, offset=0, select=None)


@pytest.mark.parametrize(
    ("name", "text", "op", "negate", "value"),
    [
        ("id", "eq.3", "eq", False, 3),
        ("id", "neq.-3", "neq", False, -3),
        ("id", "gt.3", "gt", False, 3),
        ("score", "gte.2.5", "gte", False, 2.5),
        ("score", "lt.2", "lt", False, 2.0),
        ("id", "lte.3", "lte", False, 3),
        ("scene", "eq.a.b", "eq", False, "a.b"),
        ("scene", "eq.", "eq", False, ""),
        ("photo.status", "eq.done", "eq", False, "done"),
        ("archived", "eq.true", "eq", False, True),
        ("archived", "is.false", "is", False, False),
        ("archived", "not.is.true", "is", True, True),
        ("video", "not.is.null", "is", True, None),
        ("tags", "is.null", "is", False, None),
        ("id", "in.(1,2)", "in", False, frozenset({1, 2})),
        ("photo.status", "not.in.(waiting,running)", "in", True, frozenset({"waiting", "running"})),
        ("id", "in.()", "in", False, frozenset[int]()),
        ("scene", "not.eq.x", "eq", True, "x"),
        ("updated", "gte.2026-11-04", "gte", False, datetime(2026, 11, 4, tzinfo=UTC)),
        (
            "updated",
            "lt.2026-11-04T09:12:00Z",
            "lt",
            False,
            datetime(2026, 11, 4, 9, 12, tzinfo=UTC),
        ),
    ],
)
def test_a_filter_is_read_with_its_fields_kind(
    name: str, text: str, op: Op, negate: bool, value: Any
) -> None:
    assert listed((name, text)).filters == (Filter(FIELDS[name], op, negate, value),)


@pytest.mark.parametrize(
    ("text", "op", "negate", "folded"),
    [
        ("like.*Rain*at NIGHT", "like", False, False),
        ("not.ilike.IşIk*YAĞMUR*", "ilike", True, True),
    ],
)
def test_like_and_ilike_read_their_pattern(text: str, op: Op, negate: bool, folded: bool) -> None:
    pattern = text.removeprefix("not.").partition(".")[2]

    assert listed(("scene", text)).filters == (
        Filter(FIELDS["scene"], op, negate, Pattern.read(pattern, folded)),
    )


def test_two_filters_on_one_field_both_hold() -> None:
    # A date range repeats its field (step 6).
    found = listed(("updated", "gte.2026-11-01"), ("updated", "lt.2026-11-08")).filters

    assert [(f.op, f.value.day) for f in found] == [("gte", 1), ("lt", 8)]


@pytest.mark.parametrize(
    ("name", "text", "code", "message"),
    [
        ("id", "eq.x", "wrong_type", "`query.id` must be a whole number."),
        ("id", "eq.1_000", "wrong_type", "`query.id` must be a whole number."),
        ("id", "in.(1,x)", "wrong_type", "`query.id` must be a whole number."),
        ("score", "gt.nan", "wrong_type", "`query.score` must be a number."),
        ("archived", "eq.yes", "wrong_type", "`query.archived` must be true or false."),
        (
            "updated",
            "gte.2026-13-01",
            "wrong_type",
            "`query.updated` must be a time, 2026-11-04T09:12:00Z, or a day, 2026-11-04.",
        ),
        (
            "updated",
            "gte.2026-11-04T09:12:00+03:00",
            "wrong_type",
            "`query.updated` must be a time, 2026-11-04T09:12:00Z, or a day, 2026-11-04.",
        ),
        (
            "photo.status",
            "eq.waitng",
            "not_allowed",
            "`query.photo.status` must be one of waiting, running, done.",
        ),
        (
            "id",
            "3",
            "bad_query",
            "`query.id` must be an operator and a value; it takes eq, neq, in, gt, gte, lt, lte, "
            "is.null.",
        ),
        (
            "scene",
            "match.rain",
            "bad_query",
            "`query.scene` must be an operator and a value; it takes eq, neq, in, like, ilike, "
            "is.null.",
        ),
        (
            "scene",
            "gt.a",
            "bad_query",
            "`query.scene` is text: it takes eq, neq, in, like, ilike, is.null.",
        ),
        (
            "id",
            "like.1*",
            "bad_query",
            "`query.id` is a whole number: it takes eq, neq, in, gt, gte, lt, lte, is.null.",
        ),
        (
            "scene",
            "is.true",
            "bad_query",
            "`query.scene` is text: it takes eq, neq, in, like, ilike, is.null.",
        ),
        (
            "archived",
            "is.maybe",
            "bad_query",
            "`query.archived` is true or false: it takes eq, neq, in, is.true, is.false, is.null.",
        ),
        (
            "photo",
            "eq.x",
            "bad_query",
            "`query.photo` is an object: it takes is.null; filter by one of its fields.",
        ),
        ("tags", "eq.x", "bad_query", "`query.tags` is a list: it takes is.null."),
        (
            "id",
            "in.1,2",
            "bad_query",
            "`query.id` must list its values in parentheses, as in `in.(a,b)`.",
        ),
        (
            "scene",
            "ilike." + "a" * 201,
            "out_of_range",
            "`query.scene`: a pattern has at most 200 characters.",
        ),
        ("statsu", "eq.x", "unknown", "`query.statsu` is not a field of this list."),
        ("all", "true", "unknown", "`query.all` is not a field of this list."),
        ("", "eq.x", "unknown", "`query.(empty)` is not a field of this list."),
    ],
)
def test_a_wrong_filter_is_refused_saying_why(
    name: str, text: str, code: str, message: str
) -> None:
    field = f"query.{name or '(empty)'}"

    assert refused((name, text)) == [{"field": field, "code": code, "message": message}]


def test_a_pattern_of_200_characters_is_taken() -> None:
    assert listed(("scene", "like." + "*a" * 100)).filters


def test_a_field_takes_two_filters_a_range_and_no_third() -> None:
    assert len(listed(("score", "gte.1"), ("score", "lt.2")).filters) == 2
    assert refused(
        ("score", "gte.1"), ("score", "lt.2"), ("score", "neq.x"), ("score", "eq.1")
    ) == [
        {
            "field": "query.score",
            "code": "out_of_range",
            "message": "`query.score` takes at most 2 filters, a range's two.",
        }
    ]


def test_an_in_takes_as_many_values_as_a_page_and_no_more() -> None:
    most = ",".join(str(number) for number in range(1000))

    assert len(listed(("id", f"in.({most})")).filters[0].value) == 1000
    assert refused(("id", f"in.({most},1000)")) == [
        {
            "field": "query.id",
            "code": "out_of_range",
            "message": "`query.id` takes at most 1000 values in `in`.",
        }
    ]


def test_a_long_unknown_name_is_cut_where_it_is_named() -> None:
    (found,) = refused(("ğ" * 500, "eq.1"))

    assert len(found["field"].encode()) <= FIELD_BYTES
    assert found["field"].endswith("…")


def test_every_problem_is_counted_not_only_the_first() -> None:
    found = refused(("id", "eq.x"), ("nope", "eq.1"), ("limit", "-1"))

    assert [problem["field"] for problem in found] == ["query.id", "query.nope", "query.limit"]


@pytest.mark.parametrize("name", ["select", "order", "limit", "offset"])
def test_a_reserved_parameter_given_twice_is_refused(name: str) -> None:
    value = {"select": "id", "order": "id", "limit": "1", "offset": "1"}[name]

    assert refused((name, value), (name, value)) == [
        {
            "field": f"query.{name}",
            "code": "duplicate",
            "message": f"`query.{name}` is given twice; it takes one.",
        }
    ]


def test_order_comes_first_and_the_default_breaks_ties() -> None:
    query = listed(("order", "photo.status.desc,scene.asc,updated"))

    assert query.order == (
        Order(FIELDS["photo.status"], descending=True),
        Order(FIELDS["scene"], descending=False),
        Order(FIELDS["updated"], descending=False),
        Order(FIELDS["id"], descending=False),
    )


def test_an_order_by_the_default_field_is_not_repeated() -> None:
    assert listed(("order", "id.desc")).order == (Order(FIELDS["id"], descending=True),)


@pytest.mark.parametrize(
    ("text", "code", "message"),
    [
        ("statsu", "unknown", "`query.order` names `statsu`, not a field of this list."),
        ("statsu.desc", "unknown", "`query.order` names `statsu`, not a field of this list."),
        ("photo", "bad_query", "`query.order` cannot order by `photo`: it is an object."),
        ("tags.desc", "bad_query", "`query.order` cannot order by `tags`: it is a list."),
        ("id,", "bad_query", "`query.order` names an empty field."),
        # Each field once: so an order has at most as many keys as the list has fields.
        ("scene,scene.desc", "duplicate", "`query.order` names `scene` twice."),
    ],
)
def test_a_wrong_order_is_refused(text: str, code: str, message: str) -> None:
    assert refused(("order", text)) == [{"field": "query.order", "code": code, "message": message}]


@pytest.mark.parametrize(("limit", "offset"), [("0", "0"), ("1000", "20000"), ("50", "100")])
def test_a_page_is_taken(limit: str, offset: str) -> None:
    query = listed(("limit", limit), ("offset", offset))

    assert (query.limit, query.offset) == (int(limit), int(offset))


@pytest.mark.parametrize(
    ("name", "value", "code", "message"),
    [
        ("limit", "1001", "out_of_range", "`query.limit` must be a whole number from 0 to 1000."),
        ("limit", "-1", "out_of_range", "`query.limit` must be a whole number from 0 to 1000."),
        ("limit", "ten", "wrong_type", "`query.limit` must be a whole number from 0 to 1000."),
        ("offset", "-1", "out_of_range", "`query.offset` must be a whole number, 0 or more."),
        ("offset", "1.5", "wrong_type", "`query.offset` must be a whole number, 0 or more."),
    ],
)
def test_a_wrong_page_is_refused(name: str, value: str, code: str, message: str) -> None:
    assert refused((name, value)) == [{"field": f"query.{name}", "code": code, "message": message}]


def test_select_names_the_fields_nested_in_their_objects() -> None:
    query = listed(("select", "photo.prompt, id,photo.status,video"))

    assert query.select == {"photo": {"prompt": None, "status": None}, "id": None, "video": None}


def test_an_object_selected_whole_takes_in_its_fields() -> None:
    assert parse_select("photo.status,photo", FIELDS) == {"photo": None}
    assert parse_select("photo,photo.status", FIELDS) == {"photo": None}


def test_a_star_selects_the_whole_record() -> None:
    assert listed(("select", "*")).select is None


@pytest.mark.parametrize(
    ("text", "code", "message"),
    [
        ("id,nope", "unknown", "`query.select` names `nope`, not a field of this list."),
        ("", "bad_query", "`query.select` names an empty field."),
        ("id,,scene", "bad_query", "`query.select` names an empty field."),
        ("id,scene,id", "duplicate", "`query.select` names `id` twice."),
    ],
)
def test_a_wrong_select_is_refused(text: str, code: str, message: str) -> None:
    assert refused(("select", text)) == [
        {"field": "query.select", "code": code, "message": message}
    ]


def test_the_default_order_and_select_are_read_as_the_query_reads_them() -> None:
    assert parse_order("updated.desc", FIELDS) == (Order(FIELDS["updated"], descending=True),)
    with pytest.raises(Refused):
        parse_order("nope", FIELDS)


def test_a_bulk_change_takes_the_lists_filters() -> None:
    assert parse_bulk([("id", "in.(1,2)")], FIELDS) == (
        Filter(FIELDS["id"], "in", False, frozenset({1, 2})),
    )


def test_a_bulk_change_takes_all_true_for_every_one() -> None:
    assert parse_bulk([("all", "true")], FIELDS) == ()
    assert parse_bulk([("all", "true"), ("id", "eq.1")], FIELDS) == (
        Filter(FIELDS["id"], "eq", False, 1),
    )


def bulk_refused(*pairs: tuple[str, str]) -> list[dict[str, str]]:
    with pytest.raises(Refused) as caught:
        parse_bulk(list(pairs), FIELDS)
    return caught.value.problems


def test_a_bulk_change_without_a_filter_is_refused() -> None:
    assert bulk_refused() == [
        {
            "field": "query",
            "code": "missing",
            "message": "A bulk change names what it acts on: filters, or `all=true` for every one.",
        }
    ]


@pytest.mark.parametrize("name", ["select", "order", "limit", "offset"])
def test_a_bulk_change_takes_no_page_order_or_select(name: str) -> None:
    assert bulk_refused(("all", "true"), (name, "1")) == [
        {
            "field": f"query.{name}",
            "code": "unknown",
            "message": f"`query.{name}` is not taken by a bulk change: it acts on every match.",
        }
    ]


def test_all_takes_only_true_once() -> None:
    assert bulk_refused(("all", "false")) == [
        {"field": "query.all", "code": "not_allowed", "message": "`query.all` must be true."}
    ]
    assert bulk_refused(("all", "true"), ("all", "true")) == [
        {
            "field": "query.all",
            "code": "duplicate",
            "message": "`query.all` is given twice; it takes one.",
        }
    ]


def test_one_things_get_takes_only_select() -> None:
    assert parse_one([], FIELDS) is None
    assert parse_one([("select", "id")], FIELDS) == {"id": None}
    with pytest.raises(Refused) as caught:
        parse_one([("id", "eq.1")], FIELDS)
    assert caught.value.problems == [
        {
            "field": "query.id",
            "code": "unknown",
            "message": "`query.id` is not a field this address takes.",
        }
    ]
