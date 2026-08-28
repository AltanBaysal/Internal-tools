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
BEDROOM = "sunlit bedroom, morning light"
GECELIK = "white nightgown"
GUNLUK = "black t-shirt"
TAKIM = "dark grey suit"
PEOPLE = "1girl, 1boy"
# No count inside the identity: where the count belongs is the frame's own field, and this one is
# written the way the maps are meant to read from Madde 95 on.
EDA = "freckles, green eyes"


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
        "characters": {"aylin": AYLIN, "deniz": DENIZ},
        "outfits": {"gecelik": GECELIK, "gunluk": GUNLUK, "takim": TAKIM},
        "locations": {"bedroom": BEDROOM},
        "frames": [_frame()],
    }
    structure.update(changes)
    return structure


def _tried(structure, character):
    # Imported inside rather than at the top: a name that does not exist yet fails this whole
    # file's collection, and a collection error stops the suite before any other red is seen.
    from backend.features.workspace.domain.build_prompts import build_character_prompts

    return build_character_prompts(structure, character)


def _try_name(source, character):
    from backend.features.workspace.domain.build_prompts import character_prompts_name

    return character_prompts_name(source, character)


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


def test_a_structure_without_quality_gets_the_chain_from_code():
    # Madde 110: the chain is the same in every scenario, so the file no longer carries it -- and
    # a model that never writes it cannot write a wrong one.
    from backend.features.workspace.domain.build_prompts import DEFAULT_QUALITY

    structure = _structure()
    del structure["quality"]
    assert build_prompts(structure) == [
        f"{DEFAULT_QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"
    ]


def test_a_file_that_writes_its_own_quality_keeps_it():
    # The door left open: a scenario that needs another chain writes the field, and code steps
    # aside rather than adding a second one.
    from backend.features.workspace.domain.build_prompts import DEFAULT_QUALITY

    built = build_prompts(_structure())[0]
    assert built.startswith(f"{QUALITY}, ")
    assert DEFAULT_QUALITY not in built


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


def test_the_people_tag_is_written_right_after_quality():
    built = build_prompts(_structure(frames=[_frame(people="1girl")]))
    assert built == [f"{QUALITY}, 1girl, {AYLIN}, {BEDROOM}, an action, a camera"]


def test_a_frame_without_a_people_tag_still_splits():
    # Files written before the field existed carry no count. What is missing is skipped -- the way a
    # missing quality is skipped -- and the order still opens up around the camera.
    built = build_prompts(_structure(frames=[_frame(characters={"aylin": [], "deniz": []})]))
    assert built == [f"{QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera, {DENIZ}"]


def test_an_empty_people_tag_adds_nothing():
    # A count written blank must not leave a gap behind, the way an empty quality does not.
    built = build_prompts(_structure(frames=[_frame(people=" ")]))
    assert built == [f"{QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"]


def test_who_leads_is_decided_frame_by_frame():
    # The same two people can be in front in one frame and behind in the next: what decides is the
    # order this frame wrote them in, nothing carried over from the maps.
    frames = [
        _frame(characters={"aylin": [], "deniz": []}),
        _frame(characters={"deniz": [], "aylin": []}),
    ]
    built = build_prompts(_structure(frames=frames))
    assert built[0].index(AYLIN) < built[0].index("a camera") < built[0].index(DENIZ)
    assert built[1].index(DENIZ) < built[1].index("a camera") < built[1].index(AYLIN)


def test_the_second_character_lands_past_the_camera():
    frame = _frame(people=PEOPLE, characters={"aylin": [], "deniz": []})
    assert build_prompts(_structure(frames=[frame])) == [
        f"{QUALITY}, {PEOPLE}, {AYLIN}, {BEDROOM}, an action, a camera, {DENIZ}"
    ]


def test_the_leading_characters_outfit_comes_before_the_place():
    # The whole front half in one chain: identity, its outfit, then the place -- and whoever is left
    # is nowhere near them.
    frame = _frame(people=PEOPLE, characters={"aylin": ["gecelik"], "deniz": []})
    built = build_prompts(_structure(frames=[frame]))[0]
    assert (
        built.index(AYLIN)
        < built.index(GECELIK)
        < built.index(BEDROOM)
        < built.index("a camera")
        < built.index(DENIZ)
    )


def test_the_outfit_of_whoever_comes_last_follows_them_past_the_camera():
    frame = _frame(people=PEOPLE, characters={"aylin": [], "deniz": ["takim"]})
    built = build_prompts(_structure(frames=[frame]))[0]
    assert built.index("a camera") < built.index(DENIZ) < built.index(TAKIM)


def test_the_second_and_third_stay_side_by_side_at_the_end():
    # The accepted cost of the new order: the two behind can still bleed into each other. What the
    # order protects is the one in front.
    structure = _structure(
        characters={"aylin": AYLIN, "deniz": DENIZ, "eda": EDA},
        frames=[_frame(people="2girls, 1boy", characters={"aylin": [], "deniz": [], "eda": []})],
    )
    assert build_prompts(structure)[0].endswith(f"{DENIZ}, {EDA}")


def test_the_old_list_form_makes_its_first_name_the_leading_character():
    built = build_prompts(_structure(frames=[_frame(characters=["aylin", "deniz"])]))[0]
    assert built.index(AYLIN) < built.index("a camera") < built.index(DENIZ)


def test_a_frame_with_nobody_in_it_still_says_how_many():
    built = build_prompts(_structure(frames=[_frame(people="no humans", characters={})]))
    assert built == [f"{QUALITY}, no humans, {BEDROOM}, an action, a camera"]


def test_a_character_is_tried_once_for_every_outfit():
    # Character times outfits, in the order the map wrote them. No model in it: the same joining
    # that builds a frame builds this, so what is seen here is what a frame will show.
    assert _tried(_structure(), "aylin") == [
        f"{QUALITY}, {AYLIN}, {GECELIK}",
        f"{QUALITY}, {AYLIN}, {GUNLUK}",
        f"{QUALITY}, {AYLIN}, {TAKIM}",
    ]


def test_a_file_with_no_outfits_gives_the_identity_once():
    structure = _structure()
    del structure["outfits"]
    assert _tried(structure, "aylin") == [f"{QUALITY}, {AYLIN}"]


def test_a_try_without_quality_gets_the_chain_from_code():
    from backend.features.workspace.domain.build_prompts import DEFAULT_QUALITY

    structure = _structure()
    del structure["quality"]
    assert _tried(structure, "aylin")[0] == f"{DEFAULT_QUALITY}, {AYLIN}, {GECELIK}"


def test_trying_a_character_nobody_knows_names_what_is_known():
    # The same sentence a frame gets, minus the frame number: there is no frame here.
    with pytest.raises(BadStructure) as refused:
        _tried(_structure(), "aylinn")
    said = str(refused.value)
    assert "aylinn" in said and "aylin" in said and "deniz" in said
    assert "frame" not in said


@pytest.mark.parametrize(
    "source,character,expected",
    [
        ("bar-scene.json", "aylin", "bar-scene-aylin.py"),
        ("intro-frames.json", "deniz", "intro-frames-deniz.py"),
        ("noextension", "aylin", "noextension-aylin.py"),
    ],
)
def test_the_try_is_named_after_the_source_and_the_character(source, character, expected):
    assert _try_name(source, character) == expected


def test_a_character_name_with_spaces_still_makes_a_clean_file_name():
    # The name comes from the model like every other one, and a file name is not the place to find
    # out what it did with it.
    assert _try_name("bar-scene.json", "yan karakter") == "bar-scene-yan-karakter.py"


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
