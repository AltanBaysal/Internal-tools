import ast

import pytest

from backend.features.workspace.domain.build_prompts import (
    build_prompts,
    prompts_name,
    render_module,
)
from backend.features.workspace.domain.errors import BadStructure

QUALITY = "score_9_up, masterpiece"
AYLIN = "1girl, long teal hair"
DENIZ = "1boy, short black hair"
ECE = "1girl, blonde bob"
BEDROOM = "sunlit bedroom, morning light"
GECELIK = "white nightgown"
GUNLUK = "black t-shirt"
TAKIM = "dark grey suit"


def _frame(**changes):
    frame = {
        "characters": {"aylin": []},
        "location": "bedroom",
        "action": "an action",
        "camera": "a camera",
    }
    frame.update(changes)
    return frame


def _structure(**changes):
    structure = {
        "quality": QUALITY,
        "characters": {"aylin": AYLIN, "deniz": DENIZ, "ece": ECE},
        "outfits": {"gecelik": GECELIK, "gunluk": GUNLUK, "takim": TAKIM},
        "locations": {"bedroom": BEDROOM},
        "frames": [_frame()],
    }
    structure.update(changes)
    return structure


def _prompts_of(module_text):
    # Parsed rather than run: what matters is that the file the user copies out is valid Python and
    # says what it was meant to say.
    return ast.literal_eval(ast.parse(module_text).body[0].value)


def test_a_frame_is_built_in_the_fixed_order():
    assert build_prompts(_structure()) == [
        f"{QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"
    ]


def test_the_character_text_is_the_same_in_every_frame():
    built = build_prompts(_structure(frames=[_frame(action="one"), _frame(action="two")]))
    # The whole point of the structure: no copy, so no drift.
    assert AYLIN in built[0] and AYLIN in built[1]


def test_one_edit_in_the_map_turns_every_frame():
    structure = _structure(frames=[_frame(action="one"), _frame(action="two")])
    structure["characters"]["aylin"] = "1girl, short red hair"
    built = build_prompts(structure)
    assert all("short red hair" in prompt for prompt in built)
    assert not any("teal" in prompt for prompt in built)


def test_two_characters_keep_the_frames_own_order():
    built = build_prompts(_structure(frames=[_frame(characters={"deniz": [], "aylin": []})]))
    assert built[0].index(DENIZ) < built[0].index(AYLIN)


def test_a_frame_without_a_character_or_a_place_still_builds():
    built = build_prompts(_structure(frames=[_frame(characters={}, location="")]))
    assert built == [f"{QUALITY}, an action, a camera"]


def test_a_frames_outfit_follows_its_character():
    built = build_prompts(_structure(frames=[_frame(characters={"aylin": ["gecelik"]})]))
    assert built == [f"{QUALITY}, {AYLIN}, {GECELIK}, {BEDROOM}, an action, a camera"]


def test_two_outfits_keep_the_order_they_were_written_in():
    built = build_prompts(_structure(frames=[_frame(characters={"aylin": ["gunluk", "gecelik"]})]))
    assert built[0].index(GUNLUK) < built[0].index(GECELIK)


def test_each_characters_block_stays_together():
    # An image model has to be able to tell whose clothes are whose, and the only thing saying so
    # is that the identity and its outfits are neighbours.
    frame = _frame(characters={"aylin": ["gunluk"], "deniz": ["takim"]})
    built = build_prompts(_structure(frames=[frame]))[0]
    assert built.index(AYLIN) < built.index(GUNLUK) < built.index(DENIZ) < built.index(TAKIM)


# --- more than one person in a frame (Madde 70) ---------------------------------------------------
#
# They used to be built side by side, and an image model cannot tell two neighbouring descriptions
# apart -- whose hair is whose stops being answerable. The fix is distance: the main character stays
# at the front and everyone else goes after the camera, with the place and the action in between.


def test_a_frame_puts_everyone_after_the_first_at_the_end():
    frame = _frame(characters={"aylin": ["gunluk"], "deniz": ["takim"]})
    assert build_prompts(_structure(frames=[frame])) == [
        f"{QUALITY}, {AYLIN}, {GUNLUK}, {BEDROOM}, an action, a camera, {DENIZ}, {TAKIM}"
    ]


def test_three_characters_leave_only_the_first_at_the_front():
    # The second and third stay neighbours at the end, and the same bleeding is possible between
    # them. Known and accepted: the one that has to come out clean is the main character.
    frame = _frame(characters={"aylin": [], "deniz": [], "ece": []})
    assert build_prompts(_structure(frames=[frame])) == [
        f"{QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera, {DENIZ}, {ECE}"
    ]


def test_one_character_is_built_exactly_as_it_was():
    # The half that must not move. A frame with one person has nothing to separate, and a change
    # there would be this item breaking what it was not asked to touch.
    built = build_prompts(_structure(frames=[_frame(characters={"aylin": ["gecelik"]})]))
    assert built == [f"{QUALITY}, {AYLIN}, {GECELIK}, {BEDROOM}, an action, a camera"]


def test_the_main_character_stays_in_front_of_the_place():
    # The other half of the rule: everyone else moves, the first one does not.
    frame = _frame(characters={"aylin": [], "deniz": []})
    built = build_prompts(_structure(frames=[frame]))[0]
    assert built.index(AYLIN) < built.index(BEDROOM)


def test_a_character_with_no_outfit_is_just_the_identity():
    built = build_prompts(_structure(frames=[_frame(characters={"aylin": []})]))
    assert built == [f"{QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"]


def test_the_old_list_of_names_is_read_as_names_without_outfits():
    # Files written before outfits existed carry a plain list, and they keep building.
    built = build_prompts(_structure(frames=[_frame(characters=["aylin"])]))
    assert built == [f"{QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"]


def test_a_single_outfit_written_without_a_list_is_read_as_one():
    # The instruction asks for a list; a model that writes one name plainly still means one name,
    # and reading it letter by letter would answer with nonsense.
    built = build_prompts(_structure(frames=[_frame(characters={"aylin": "gecelik"})]))
    assert built == [f"{QUALITY}, {AYLIN}, {GECELIK}, {BEDROOM}, an action, a camera"]


def test_an_unknown_outfit_names_the_frame_and_what_is_known():
    with pytest.raises(BadStructure) as refused:
        build_prompts(_structure(frames=[_frame(characters={"aylin": ["gecelikk"]})]))
    said = str(refused.value)
    assert "frame 1" in said and "gecelikk" in said and "outfits" in said
    assert "gecelik" in said and "takim" in said


def test_an_unknown_character_in_the_map_form_is_reported_too():
    with pytest.raises(BadStructure) as refused:
        build_prompts(_structure(frames=[_frame(characters={"aylinn": []})]))
    said = str(refused.value)
    assert "frame 1" in said and "aylinn" in said and "characters" in said


def test_a_structure_with_no_outfits_map_still_builds():
    structure = _structure()
    del structure["outfits"]
    assert build_prompts(structure) == [f"{QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"]


def test_a_structure_without_quality_still_builds():
    structure = _structure()
    del structure["quality"]
    assert build_prompts(structure) == [f"{AYLIN}, {BEDROOM}, an action, a camera"]


def test_loose_commas_and_spaces_are_tidied_away():
    structure = _structure(
        quality=" score_9_up , ",
        frames=[_frame(action="", camera=" ,, medium shot,")],
    )
    assert build_prompts(structure) == [f"score_9_up, {AYLIN}, {BEDROOM}, medium shot"]


def test_a_repeated_solo_tag_is_left_exactly_as_written():
    structure = _structure(frames=[_frame(characters={"aylin": [], "deniz": []})])
    structure["characters"] = {"aylin": "1girl, solo", "deniz": "1boy, solo"}
    # Out of scope by decision: the tool carries the entries through as written, and a wrong count
    # is seen on the screen rather than silently guessed at here.
    assert build_prompts(structure)[0].count("solo") == 2


def test_an_old_structure_still_reads_its_list_from_shots():
    # A rename cannot turn what is already on the user's disk into rubbish.
    structure = _structure()
    structure["shots"] = structure.pop("frames")
    assert build_prompts(structure) == [f"{QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"]


def test_a_structure_carrying_both_lists_uses_frames():
    structure = _structure(frames=[_frame(action="the new one")])
    structure["shots"] = [_frame(action="the old one")]
    assert "the new one" in build_prompts(structure)[0]


def test_an_unknown_character_names_the_frame_the_name_and_what_is_known():
    with pytest.raises(BadStructure) as refused:
        build_prompts(_structure(frames=[_frame(characters=["aylinn"])]))
    said = str(refused.value)
    assert "frame 1" in said
    assert "aylinn" in said
    assert "aylin" in said and "deniz" in said
    # Place names are no help to someone looking for a character.
    assert "bedroom" not in said


def test_an_unknown_place_is_reported_the_same_way():
    with pytest.raises(BadStructure) as refused:
        build_prompts(_structure(frames=[_frame(location="rooftop")]))
    said = str(refused.value)
    assert "frame 1" in said and "rooftop" in said and "bedroom" in said


def test_every_miss_is_reported_at_once():
    structure = _structure(frames=[_frame(characters=["ghost"]), _frame(location="rooftop")])
    with pytest.raises(BadStructure) as refused:
        build_prompts(structure)
    said = str(refused.value)
    # One pass, one fix: stopping at the first miss would cost a round per mistake.
    assert "frame 1" in said and "frame 2" in said
    assert "ghost" in said and "rooftop" in said


def test_a_structure_with_no_frames_says_so():
    with pytest.raises(BadStructure) as empty:
        build_prompts(_structure(frames=[]))
    assert "frame" in str(empty.value).lower()
    with pytest.raises(BadStructure):
        build_prompts({"quality": QUALITY})


def test_something_that_is_not_a_structure_at_all_is_refused():
    # Valid JSON is not the same as a structure, and the answer is words rather than a crash.
    with pytest.raises(BadStructure):
        build_prompts(["a list"])


def test_the_written_module_is_valid_python_and_holds_the_prompts():
    assert _prompts_of(render_module(["one, two", "three"])) == ["one, two", "three"]


def test_the_module_uses_triple_quotes_and_a_trailing_comma():
    assert '    """one""",' in render_module(["one"])
    assert render_module(["one"]).rstrip().endswith("]")


def test_a_prompt_with_quotes_or_a_backslash_still_parses():
    tricky = ['a """quoted""" tag', "a back\\slash", 'ends with a quote"']
    assert _prompts_of(render_module(tricky)) == tricky


@pytest.mark.parametrize(
    "source,expected",
    [
        ("intro-frames.json", "intro-frames.py"),
        ("scene.json", "scene.py"),
        ("noextension", "noextension.py"),
    ],
)
def test_the_output_is_named_after_the_source(source, expected):
    assert prompts_name(source) == expected
