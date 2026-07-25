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


def test_unreadable_text_reports_pythons_own_error():
    with pytest.raises(InvalidPrompts) as exc:
        parse_prompts('["a", ')
    assert "Python listesi bekleniyor" in str(exc.value)
    assert "[\"ilk prompt\"" in str(exc.value)      # shows an example


def test_bare_string_is_rejected():
    with pytest.raises(InvalidPrompts) as exc:
        parse_prompts('"tek prompt"')
    assert "köşeli parantez" in str(exc.value)


def test_non_list_is_rejected_with_its_type():
    with pytest.raises(InvalidPrompts) as exc:
        parse_prompts("42")
    assert "int" in str(exc.value)


def test_non_string_item_is_rejected():
    with pytest.raises(InvalidPrompts) as exc:
        parse_prompts('["a", 3]')
    assert "metin" in str(exc.value)


def test_list_of_only_empty_items_is_rejected():
    with pytest.raises(InvalidPrompts) as exc:
        parse_prompts('["", "   "]')
    assert str(exc.value) == "Listede dolu prompt yok."
