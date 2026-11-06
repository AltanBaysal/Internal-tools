import pytest

from core.lists.pattern import MOST_CHARACTERS, Pattern, TooLong, fold


@pytest.mark.parametrize(
    ("pattern", "text", "found"),
    [
        ("rain", "rain", True),
        ("rain", "rain at night", False),
        ("*rain*", "a rain at night", True),
        ("rain*", "rain at night", True),
        ("rain*", "a rain", False),
        ("*night", "rain at night", True),
        ("*night", "night falls", False),
        ("r*n", "rn", True),
        ("r*n", "rain", True),
        ("r*n", "r", False),
        ("a*a", "a", False),
        ("ab*ba", "aba", False),
        ("ab*ba", "abba", True),
        ("*a*b*c*", "xaxbxcx", True),
        ("*a*b*c*", "xcxbxax", False),
        ("*", "", True),
        ("**", "anything", True),
        ("", "", True),
        ("", "x", False),
        ("Rain*", "rain", False),
    ],
)
def test_like_is_the_whole_text_with_star_as_any_run(pattern: str, text: str, found: bool) -> None:
    assert Pattern.read(pattern, folded=False).matches(text) is found


def test_the_pattern_is_kept_as_its_pieces_between_stars() -> None:
    assert Pattern.read("*Rain*at NIGHT", folded=False).pieces == ("", "Rain", "at NIGHT")


def test_ilike_folds_the_pattern_and_the_text_with_the_four_is_as_one() -> None:
    pattern = Pattern.read("IşIk*YAĞMUR*İı", folded=True)

    assert pattern.pieces == ("işik", "yağmur", "ii")
    assert pattern.matches("Işık ve YAĞMUR, İı")


@pytest.mark.parametrize(
    ("text", "folded"),
    [("IŞIK", "işik"), ("İstanbul", "istanbul"), ("ıI", "ii"), ("STRASSE", "strasse"), ("ß", "ss")],
)
def test_fold_makes_the_four_is_one_and_casefolds_the_rest(text: str, folded: str) -> None:
    assert fold(text) == folded


def test_a_pattern_is_taken_up_to_its_bound_and_refused_past_it() -> None:
    assert Pattern.read("a" * MOST_CHARACTERS, folded=False)
    with pytest.raises(TooLong):
        Pattern.read("a" * (MOST_CHARACTERS + 1), folded=True)


def test_a_middle_piece_that_fails_late_is_one_find_not_a_backtrack() -> None:
    # The ends match a run of a's; the middle piece, ending in b, is not in it. A backtracking
    # engine tries each split of the run; here it is one find over it.
    pattern = Pattern.read("*" + "a" * 50 + "*" + "a" * 50 + "b" + "*", folded=False)

    assert pattern.matches("a" * 100_000) is False
