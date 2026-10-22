"""A Krea scenario's shape and its build (Madde 492).

A Krea scenario is a style and frames of a scene and a prompt each, and the name says it is one:
plaj.krea.json. Content that does not fit is refused, saying what does not fit -- it is never read
as the other kind (the user, 22 October: "hayır kontrol böyle yapılmamalı bu çok kötü bir tasarım").
"""
import pytest

from backend.features.workspace.domain.errors import BadStructure
from backend.features.workspace.domain.krea_prompts import build_krea_prompts, krea_problems

SOURCE = "plaj.krea.json"


def _scenario(**changes):
    scenario = {
        "style": "A photorealistic photo taken on a phone.",
        "frames": [
            {"scene": "She walks in.", "prompt": "A woman walks into a bar."},
            {"scene": "He waves.", "prompt": "A man waves from the counter."},
        ],
    }
    scenario.update(changes)
    return scenario


def test_a_scenario_of_the_right_shape_has_no_problems():
    assert krea_problems(SOURCE, _scenario()) == []
    assert krea_problems(SOURCE, {"style": "x", "frames": []}) == []


def test_something_that_is_not_an_object_is_one_problem():
    assert krea_problems(SOURCE, ["a", "list"]) == [
        "plaj.krea.json: a Krea scenario is a JSON object with style and frames."
    ]


def test_every_problem_comes_back_at_once():
    # One pass fixes them all, which is build_prompts' rule too: the model is not sent back once for
    # each of them.
    scenario = {
        "characters": {},
        "frames": [
            {"scene": "x", "prompt": "y", "characters": {"aylin": []}},
            {"scene": "x"},
            "not a frame",
            {"scene": 3, "prompt": "y"},
        ],
    }
    assert krea_problems(SOURCE, scenario) == [
        "plaj.krea.json has no style; a Krea scenario has style and frames.",
        "plaj.krea.json has characters; a Krea scenario has style and frames.",
        "plaj.krea.json: frame 1 has characters; a Krea frame has scene and prompt.",
        "plaj.krea.json: frame 2 has no prompt; a Krea frame has scene and prompt.",
        "plaj.krea.json: frame 3 is not an object with scene and prompt.",
        "plaj.krea.json: frame 4's scene is not text.",
    ]


def test_a_style_that_is_not_text_and_frames_that_are_not_a_list_are_named():
    assert krea_problems(SOURCE, {"style": ["x"], "frames": {}}) == [
        "plaj.krea.json: the style is not text.",
        "plaj.krea.json: frames is not a list.",
    ]


def test_a_frame_carries_no_number():
    # The user, 22 October: a Krea frame is counted by its place, and carries no number.
    scenario = _scenario(frames=[{"scene": "x", "prompt": "y", "number": 1}])
    assert krea_problems(SOURCE, scenario) == [
        "plaj.krea.json: frame 1 has number; a Krea frame has scene and prompt."
    ]


def test_each_frame_is_built_as_the_style_then_its_prompt():
    assert build_krea_prompts(SOURCE, _scenario()) == [
        {
            "scene": "She walks in.",
            "photo": "A photorealistic photo taken on a phone. A woman walks into a bar.",
        },
        {
            "scene": "He waves.",
            "photo": "A photorealistic photo taken on a phone. A man waves from the counter.",
        },
    ]


def test_the_edges_are_trimmed_so_one_space_joins_the_two():
    scenario = _scenario(style="  A photo.\n", frames=[{"scene": "x", "prompt": "\nA dog. "}])
    assert build_krea_prompts(SOURCE, scenario)[0]["photo"] == "A photo. A dog."


def test_a_shape_that_does_not_fit_is_not_built():
    with pytest.raises(BadStructure) as refused:
        build_krea_prompts(SOURCE, {"frames": []})
    assert str(refused.value) == (
        "plaj.krea.json has no style; a Krea scenario has style and frames."
    )


def test_an_empty_style_and_every_empty_prompt_are_refused_at_once():
    scenario = _scenario(
        style=" ",
        frames=[
            {"scene": "x", "prompt": ""},
            {"scene": "x", "prompt": "fine"},
            {"scene": "x", "prompt": "  "},
        ],
    )
    with pytest.raises(BadStructure) as refused:
        build_krea_prompts(SOURCE, scenario)
    assert str(refused.value) == "\n".join(
        [
            "plaj.krea.json has an empty style.",
            "plaj.krea.json: frame 1 has an empty prompt.",
            "plaj.krea.json: frame 3 has an empty prompt.",
        ]
    )


def test_a_scenario_without_frames_builds_nothing():
    with pytest.raises(BadStructure) as refused:
        build_krea_prompts(SOURCE, _scenario(frames=[]))
    assert str(refused.value) == "That file has no frames to build from."
