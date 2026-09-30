import pytest

from backend.features.photo_generation.domain import prompt_list
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


# QueenAgent's list, in the shape its build_prompts.render_module writes: a record per frame, each
# value in triple quotes.
QUEEN_AGENT_LIST = '''PROMPTS = [
    {
        "scene": """Kraliçe tahtında oturuyor; salon boş ve karanlık.""",
        "photo": """score_9_up, 1girl, queen, crown BREAK sitting on a throne, throne room""",
    },
    {
        "scene": """Kraliçe gece bahçede yürüyor, fenerler yanıyor.""",
        "photo": """score_9_up, 1girl, queen BREAK walking, night garden, lanterns""",
    },
]
'''


def test_queen_agent_s_list_gives_each_frame_its_photo_prompt_and_scene():
    assert prompt_list.parse_photo_list(QUEEN_AGENT_LIST) == [
        {"prompt": "score_9_up, 1girl, queen, crown BREAK sitting on a throne, throne room",
         "scene": "Kraliçe tahtında oturuyor; salon boş ve karanlık."},
        {"prompt": "score_9_up, 1girl, queen BREAK walking, night garden, lanterns",
         "scene": "Kraliçe gece bahçede yürüyor, fenerler yanıyor."},
    ]


def test_the_flat_list_reads_as_it_does_today_and_carries_no_scene():
    assert prompt_list.parse_photo_list('PROMPTS = ["a", "", "b"]') == [{"prompt": "a"},
                                                                       {"prompt": "b"}]


@pytest.mark.parametrize("text", [
    '[{"photo": "a"}]',
    '[{"scene": "s"}]',
    '[{"scene": "s", "photo": 3}]',
    '["a", {"scene": "s", "photo": "p"}]',
    '{"scene": "s", "photo": "p"}',
])
def test_a_list_of_records_it_cannot_read_gets_the_same_one_line(text):
    with pytest.raises(InvalidPrompts) as exc:
        prompt_list.parse_photo_list(text)
    assert str(exc.value) == "Format hatası — liste okunamadı"


def test_a_record_with_a_blank_photo_is_left_out_like_a_blank_item():
    text = '[{"scene": "s", "photo": "a"}, {"scene": "t", "photo": "  "}]'
    assert prompt_list.parse_photo_list(text) == [{"prompt": "a", "scene": "s"}]
