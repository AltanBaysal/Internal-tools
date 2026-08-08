import pytest

from backend.features.photo_generation.domain.prompt_list import InvalidPrompts, parse_prompts


def test_parses_a_python_list():
    assert parse_prompts('["kraliçe tahtta", "kraliçe bahçede"]') == ["kraliçe tahtta", "kraliçe bahçede"]


def test_strips_a_leading_assignment():
    # The list is pasted straight out of a notebook cell.
    assert parse_prompts('PROMPTS = ["a", "b"]') == ["a", "b"]


def test_multiline_items_survive_and_are_stripped():
    assert parse_prompts('["""\n  kraliçe\n"""]') == ["kraliçe"]


def test_empty_items_are_dropped():
    # nova-3dcg's contract: an empty item is a deliberate "skip this line" switch.
    assert parse_prompts('["a", "", "  ", "b"]') == ["a", "b"]


def test_empty_text_is_rejected():
    with pytest.raises(InvalidPrompts) as exc:
        parse_prompts("   ")
    assert str(exc.value) == "Prompt listesi boş."


@pytest.mark.parametrize("text", ['["a", ', '"tek prompt"', "42", '["a", 3]', "{'a': 1}"])
def test_every_unreadable_shape_gets_the_same_one_line(text):
    with pytest.raises(InvalidPrompts) as exc:
        parse_prompts(text)
    assert str(exc.value) == "Format hatası — liste okunamadı"


def test_the_format_error_gives_no_detail():
    # The design's rule: no expected shape, no example, no line or column, no Python message.
    with pytest.raises(InvalidPrompts) as exc:
        parse_prompts('["a", ')
    message = str(exc.value)
    assert "örnek" not in message.lower()
    assert "ilk prompt" not in message
    assert "\n" not in message


def test_a_list_of_only_empty_items_reads_as_an_empty_list():
    with pytest.raises(InvalidPrompts) as exc:
        parse_prompts('["", "   "]')
    assert str(exc.value) == "Prompt listesi boş."
