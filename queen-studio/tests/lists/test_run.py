import json
from typing import Any

import pytest

from core.lists.fields import fields_of
from core.lists.parse import parse_list, parse_order
from core.lists.run import TooLarge, page, pick
from tests.lists.test_parse import Note

FIELDS = fields_of(Note)
ROOMY = 1024 * 1024


def note(id: int, **fields: Any) -> dict[str, Any]:
    return {
        "id": id,
        "scene": f"scene {id}",
        "score": None,
        "archived": False,
        "updated": "2026-11-04T09:12:00Z",
        "photo": {"status": "done", "prompt": None},
        "video": None,
        "tags": [],
        **fields,
    }


def answered(
    records: list[dict[str, Any]], *pairs: tuple[str, str], most_bytes: int = ROOMY
) -> dict[str, Any]:
    query = parse_list(list(pairs), FIELDS, select={"id": None}, order=parse_order("id", FIELDS))
    return json.loads(page(records, query, most_bytes))


def ids(records: list[dict[str, Any]], *pairs: tuple[str, str]) -> list[int]:
    return [item["id"] for item in answered(records, *pairs, ("limit", "1000"))["items"]]


def test_every_filter_must_hold() -> None:
    records = [note(1, archived=True), note(2, archived=True, score=3.0), note(3, score=3.0)]

    assert ids(records, ("archived", "is.true"), ("score", "gte.3")) == [2]


def test_a_date_range_holds_both_ends() -> None:
    records = [
        note(1, updated="2026-10-31T23:59:59Z"),
        note(2, updated="2026-11-01T00:00:00Z"),
        note(3, updated="2026-11-07T23:59:59Z"),
        note(4, updated="2026-11-08T00:00:00Z"),
    ]

    assert ids(records, ("updated", "gte.2026-11-01"), ("updated", "lt.2026-11-08")) == [2, 3]


def test_a_time_is_compared_as_a_time_not_as_text() -> None:
    # As text, `.5Z` sorts before `Z`; as a time it is half a second later.
    records = [note(1, updated="2026-11-04T09:12:00.500000Z"), note(2)]

    assert ids(records, ("updated", "gt.2026-11-04T09:12:00Z")) == [1]
    assert ids(records, ("order", "updated.desc")) == [1, 2]


@pytest.mark.parametrize(
    ("text", "found"),
    [
        ("eq.3", [2]),
        ("neq.3", [3]),
        ("not.eq.3", [3]),
        ("gt.0", [2, 3]),
        ("in.(3,5)", [2]),
        ("not.in.(3)", [3]),
        ("is.null", [1]),
        ("not.is.null", [2, 3]),
    ],
)
def test_a_null_matches_only_is_null(text: str, found: list[int]) -> None:
    # As in SQL, and so in PostgREST: a comparison with null holds neither way.
    records = [note(1), note(2, score=3.0), note(3, score=4.0)]

    assert ids(records, ("score", text)) == found


def test_the_fields_of_a_null_object_are_null() -> None:
    records = [note(1), note(2, video={"status": "waiting", "prompt": "p"})]

    assert ids(records, ("video.status", "is.null")) == [1]
    assert ids(records, ("video.status", "not.eq.done")) == [2]


def test_a_field_the_record_lacks_is_null() -> None:
    records = [{"id": 1}, note(2, score=1.0)]

    assert ids(records, ("score", "is.null")) == [1]


def test_is_true_and_is_false_see_null_as_neither() -> None:
    records = [note(1, archived=True), note(2), note(3, archived=None)]

    assert ids(records, ("archived", "is.true")) == [1]
    assert ids(records, ("archived", "not.is.true")) == [2, 3]


def test_like_minds_case() -> None:
    records = [note(1, scene="Rain at night"), note(2, scene="rain")]

    assert ids(records, ("scene", "like.Rain*")) == [1]
    assert ids(records, ("scene", "not.like.Rain*")) == [2]


@pytest.mark.parametrize(
    ("pattern", "scenes"),
    [
        ("yağmur", ["YAĞMUR", "Yağmur", "yağmur"]),
        ("ışık", ["IŞIK", "Işık", "ışık", "işik"]),
        ("İSTANBUL", ["istanbul", "ıstanbul", "Istanbul", "İstanbul"]),
        ("rain", ["RAIN", "Raın", "raİn"]),
    ],
)
def test_ilike_finds_turkish_and_english_is_together(pattern: str, scenes: list[str]) -> None:
    records = [note(number, scene=f"a {scene} b") for number, scene in enumerate(scenes, 1)]
    records.append(note(99, scene="something else"))

    assert ids(records, ("scene", f"ilike.*{pattern}*")) == list(range(1, len(scenes) + 1))


def test_ilike_folds_beyond_ascii() -> None:
    records = [note(1, scene="STRASSE"), note(2, scene="Çiçek")]

    assert ids(records, ("scene", "ilike.straße")) == [1]
    assert ids(records, ("scene", "ilike.ÇİÇEK")) == [2]


def test_order_puts_nulls_last_either_way_and_ties_in_the_default_order() -> None:
    records = [note(1, score=2.0), note(2), note(3, score=1.0), note(4, score=2.0), note(5)]

    assert ids(records, ("order", "score")) == [3, 1, 4, 2, 5]
    assert ids(records, ("order", "score.desc")) == [1, 4, 3, 2, 5]


def test_order_by_several_fields_the_first_first() -> None:
    records = [
        note(1, archived=True, scene="b"),
        note(2, archived=False, scene="a"),
        note(3, archived=True, scene="a"),
    ]

    assert ids(records, ("order", "archived.desc,scene")) == [3, 1, 2]


def test_a_page_counts_every_match_and_answers_its_part() -> None:
    records = [note(number) for number in range(1, 11)]

    assert answered(records, ("limit", "3"), ("offset", "4"), ("id", "gt.1")) == {
        "items": [{"id": 6}, {"id": 7}, {"id": 8}],
        "total": 9,
        "offset": 4,
        "limit": 3,
    }


def test_limit_0_gives_only_the_total() -> None:
    assert answered([note(1), note(2)], ("limit", "0")) == {
        "items": [],
        "total": 2,
        "offset": 0,
        "limit": 0,
    }


def test_an_offset_past_the_end_gives_no_items() -> None:
    assert answered([note(1)], ("offset", "5"))["items"] == []


def page_of(records: list[dict[str, Any]], most_bytes: int) -> bytes:
    query = parse_list([], FIELDS, select={"id": None}, order=parse_order("id", FIELDS))
    return page(records, query, most_bytes)


def test_a_page_is_its_json_as_written_and_takes_its_budget_exactly() -> None:
    records = [note(1), note(2)]
    body = b'{"items":[{"id":1},{"id":2}],"total":2,"offset":0,"limit":100}'

    assert page_of(records, len(body)) == body


def test_a_page_past_its_budget_is_refused_saying_how_many_fit_never_cut() -> None:
    records = [note(1), note(2), note(3)]
    one_short = len(b'{"items":[{"id":1},{"id":2},{"id":3}],"total":3,"offset":0,"limit":100}') - 1

    with pytest.raises(TooLarge) as caught:
        page_of(records, one_short)
    assert caught.value.fits == 2


def test_select_picks_nested_fields_and_a_null_object_whole() -> None:
    record = note(1, photo={"status": "done", "prompt": "p"})

    assert pick(record, {"photo": {"prompt": None}, "video": {"status": None}, "id": None}) == {
        "photo": {"prompt": "p"},
        "video": None,
        "id": 1,
    }
    assert pick(record, None) == record


def test_the_records_are_not_changed() -> None:
    records = [note(2), note(1)]
    before = [dict(record) for record in records]

    answered(records, ("order", "id.desc"), ("select", "*"))

    assert records == before
