import ast

import pytest

from backend.features.workspace.domain.build_prompts import (
    DEFAULT_QUALITY,
    build_prompts,
    prompts_name,
    render_module,
)
from backend.features.workspace.domain.errors import BadStructure

# A chain no scenario gets to use (Madde 166). It appears in one test only -- the one proving a file
# that writes its own is ignored -- and every other expectation opens with DEFAULT_QUALITY.
QUALITY = "score_9_up, masterpiece"
AYLIN = "1girl, long teal hair"
DENIZ = "1boy, short black hair"
BEDROOM = "sunlit bedroom, morning light"
GECELIK = "white nightgown"
GUNLUK = "black t-shirt"
TAKIM = "dark grey suit"
# What separates two character blocks. Written once: the node reading it splits on the literal
# string, so a typo here would be a typo in every assertion at the same time.
BREAK = " BREAK "
# A second woman, and no count inside her entry: the count rides in whoever's entry needs it, and
# this one is only ever behind someone else.
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
    # No quality field: since Madde 166 the chain is the code's in every scenario, and a fixture
    # carrying one would be testing a door that is closed.
    structure = {
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
        f"{DEFAULT_QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"
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
    assert built == [f"{DEFAULT_QUALITY}, an action, a camera"]


def test_a_frames_outfit_follows_its_character():
    built = build_prompts(_structure(frames=[_frame(characters={"aylin": ["gecelik"]})]))
    assert built == [f"{DEFAULT_QUALITY}, {AYLIN}, {GECELIK}, {BEDROOM}, an action, a camera"]


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
    assert built == [f"{DEFAULT_QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"]


def test_the_old_list_of_names_is_read_as_names_without_outfits():
    # Files written before outfits existed carry a plain list, and they keep building.
    built = build_prompts(_structure(frames=[_frame(characters=["aylin"])]))
    assert built == [f"{DEFAULT_QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"]


def test_a_single_outfit_written_without_a_list_is_read_as_one():
    # The instruction asks for a list; a model that writes one name plainly still means one name,
    # and reading it letter by letter would answer with nonsense.
    built = build_prompts(_structure(frames=[_frame(characters={"aylin": "gecelik"})]))
    assert built == [f"{DEFAULT_QUALITY}, {AYLIN}, {GECELIK}, {BEDROOM}, an action, a camera"]


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
    assert build_prompts(structure) == [f"{DEFAULT_QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"]


def test_the_quality_chain_always_comes_from_code():
    # Madde 110 put the chain in code and left a door open for a file that wanted another one.
    # Madde 166 closes it: the chain is the same in every scenario, and one place saying so cannot
    # disagree with itself.
    assert build_prompts(_structure()) == [
        f"{DEFAULT_QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"
    ]


def test_a_files_own_quality_chain_is_ignored():
    # The door Madde 110 left open, now shut. A chain written into the file was a chain a model had
    # copied out of the schema example -- which is how one mixing two model families reached a real
    # file. The field may still sit there; nothing reads it.
    built = build_prompts(_structure(quality=QUALITY))[0]
    assert built.startswith(f"{DEFAULT_QUALITY}, ")
    assert "masterpiece" not in built


def test_a_frames_people_field_is_ignored():
    # Madde 166. The count rides in whoever's entry needs it, and a frame-level field was a second
    # place saying how many people there are -- two places that can disagree, and a model doing
    # arithmetic it has no reason to be doing.
    built = build_prompts(_structure(frames=[_frame(people="1girl, 1boy")]))
    assert built == [f"{DEFAULT_QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"]


def test_the_count_rides_in_the_characters_own_tags():
    # Where it lives now that the frame has no field for it. The one place that says so: with
    # `people` gone, nothing else in this file would.
    assert build_prompts(_structure())[0].count("1girl") == 1


def test_an_old_frames_camera_is_still_read():
    # No tool writes this field after Madde 173, but files on disk carry it and a rename cannot
    # turn what is already there into rubbish -- the rule the `shots` fallback keeps.
    built = build_prompts(_structure(frames=[_frame(camera="upper body, from side")]))
    assert built[0].endswith("an action, upper body, from side")


def test_loose_commas_and_spaces_are_tidied_away():
    structure = _structure(frames=[_frame(action="", camera=" ,, medium shot,")])
    assert build_prompts(structure) == [f"{DEFAULT_QUALITY}, {AYLIN}, {BEDROOM}, medium shot"]


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
    assert build_prompts(structure) == [f"{DEFAULT_QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"]


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


def test_two_characters_split_around_the_camera():
    # The order opens up around the camera: the lead in front of it, everyone else behind.
    built = build_prompts(_structure(frames=[_frame(characters={"aylin": [], "deniz": []})]))
    assert built == [f"{DEFAULT_QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera{BREAK}{DENIZ}"]


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
    frame = _frame(characters={"aylin": [], "deniz": []})
    assert build_prompts(_structure(frames=[frame])) == [
        f"{DEFAULT_QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera{BREAK}{DENIZ}"
    ]


def test_the_leading_characters_outfit_comes_before_the_place():
    # The whole front half in one chain: identity, its outfit, then the place -- and whoever is left
    # is nowhere near them.
    frame = _frame(characters={"aylin": ["gecelik"], "deniz": []})
    built = build_prompts(_structure(frames=[frame]))[0]
    assert (
        built.index(AYLIN)
        < built.index(GECELIK)
        < built.index(BEDROOM)
        < built.index("a camera")
        < built.index(DENIZ)
    )


def test_the_outfit_of_whoever_comes_last_follows_them_past_the_camera():
    frame = _frame(characters={"aylin": [], "deniz": ["takim"]})
    built = build_prompts(_structure(frames=[frame]))[0]
    assert built.index("a camera") < built.index(DENIZ) < built.index(TAKIM)


def test_the_two_behind_are_cut_off_from_each_other_too():
    # The cost the ordering fix accepted -- the two behind still bleeding into each other -- is not
    # worth accepting once a separator exists. One rule with no exception: every character block
    # gets a break, so the third is as separate from the second as the second is from the lead.
    structure = _structure(
        characters={"aylin": AYLIN, "deniz": DENIZ, "eda": EDA},
        frames=[_frame(characters={"aylin": [], "deniz": [], "eda": []})],
    )
    assert build_prompts(structure)[0].endswith(f"{DENIZ}{BREAK}{EDA}")


def test_break_never_touches_a_comma():
    # The node reading the prompt splits on the literal string, so a BREAK written as one more tag
    # would leave every chunk opening and closing on a comma. Harmless to the model, unreadable to
    # whoever opens the file -- and the reason the blocks are joined rather than listed.
    frame = _frame(characters={"aylin": ["gecelik"], "deniz": ["takim"]})
    built = build_prompts(_structure(frames=[frame]))[0]

    # Asserted first, and not only for company: without it the two below are vacuously true on a
    # prompt that carries no BREAK at all, which is exactly what this file held before the item.
    assert BREAK in built
    assert ", BREAK" not in built
    assert "BREAK," not in built


def test_a_single_character_frame_carries_no_break():
    # Nothing to separate: one block is one block.
    assert "BREAK" not in build_prompts(_structure())[0]


def test_a_character_tried_alone_carries_no_break():
    # The try path builds one character on their own, so a second block never exists.
    assert all("BREAK" not in prompt for prompt in _tried(_structure(), "aylin"))


def test_the_old_list_form_makes_its_first_name_the_leading_character():
    built = build_prompts(_structure(frames=[_frame(characters=["aylin", "deniz"])]))[0]
    assert built.index(AYLIN) < built.index("a camera") < built.index(DENIZ)


def test_a_frame_with_nobody_in_it_still_builds():
    # A landscape has no cast, and nothing about it is a miss: the empty block is dropped and the
    # place, the action and the camera carry the frame on their own.
    built = build_prompts(_structure(frames=[_frame(characters={})]))
    assert built == [f"{DEFAULT_QUALITY}, {BEDROOM}, an action, a camera"]


def test_a_character_is_tried_once_for_every_outfit():
    # Character times outfits, in the order the map wrote them. No model in it: the same joining
    # that builds a frame builds this, so what is seen here is what a frame will show.
    assert _tried(_structure(), "aylin") == [
        f"{DEFAULT_QUALITY}, {AYLIN}, {GECELIK}",
        f"{DEFAULT_QUALITY}, {AYLIN}, {GUNLUK}",
        f"{DEFAULT_QUALITY}, {AYLIN}, {TAKIM}",
    ]


def test_a_file_with_no_outfits_gives_the_identity_once():
    structure = _structure()
    del structure["outfits"]
    assert _tried(structure, "aylin") == [f"{DEFAULT_QUALITY}, {AYLIN}"]


def test_a_try_always_gets_the_chain_from_code():
    assert _tried(_structure(), "aylin")[0] == f"{DEFAULT_QUALITY}, {AYLIN}, {GECELIK}"


def test_a_try_ignores_the_files_own_quality():
    # The same door, closed on the other path (Madde 166). A look at one character has to show what
    # a frame will show, and a chain that held here but not there would make the look a lie.
    tried = _tried(_structure(quality=QUALITY), "aylin")[0]
    assert tried.startswith(f"{DEFAULT_QUALITY}, ")
    assert "masterpiece" not in tried


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
