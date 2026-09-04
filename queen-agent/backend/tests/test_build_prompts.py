import ast

import pytest

from backend.features.workspace.domain.build_prompts import (
    DEFAULT_QUALITY,
    build_prompts,
    prompts_name,
    render_module,
)
from backend.features.workspace.domain.errors import BadStructure

# The code's own chain rather than one this file invents (Madde 150). Every prompt opens with it and
# nothing in a structure file can change that any more, so a test carrying its own would be testing
# a door that is closed. Written once here so the assertions below read the same as they always did.
QUALITY = DEFAULT_QUALITY
AYLIN = "1girl, long teal hair"
DENIZ = "1boy, short black hair"
BEDROOM = "sunlit bedroom, morning light"
GECELIK = "white nightgown"
GUNLUK = "black t-shirt"
TAKIM = "dark grey suit"
PEOPLE = "1girl, 1boy"
# What separates two character blocks. Written once: the node reading it splits on the literal
# string, so a typo here would be a typo in every assertion at the same time.
BREAK = " BREAK "
# An identity carrying no count of its own. AYLIN and DENIZ carry one, the way Madde 163 has the
# model write them; this one is the third character in a crowd, where the assertion is one exact
# string and a count would only be noise.
EDA = "freckles, green eyes"
# The tags half of a character written in the map form. None of them carries a count -- which is what
# makes them the fixture for asking whether a count appeared out of nowhere.
AYLIN_TAGS = "long teal hair, green eyes"
DENIZ_TAGS = "short black hair, stubble"
TAGS = {"aylin": AYLIN_TAGS, "deniz": DENIZ_TAGS}


def _kinds(**people):
    """A characters map in the map form: a kind beside the tags.

    What set_character wrote between Madde 154 and 163. It writes plain text again from 163 on, but
    the shape stays on the user's disk and the builder still has to read it -- so it stays here too.
    """
    return {name: {"kind": kind, "tags": TAGS[name]} for name, kind in people.items()}


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


def test_the_chain_always_comes_from_code():
    # Madde 110 moved the chain into code and left a door open; Madde 150 closed it. There is one
    # chain, it is the same in every scenario, and nothing on disk decides it.
    assert build_prompts(_structure()) == [
        f"{DEFAULT_QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"
    ]


def test_a_file_that_writes_its_own_quality_is_ignored():
    # The one behaviour this madde changes. A file carrying the field is not an error and is not
    # rewritten -- it is simply not read, so an old file goes on building and builds the same
    # prompt as a new one.
    built = build_prompts(_structure(quality="score_9_up, masterpiece"))[0]
    assert built.startswith(f"{DEFAULT_QUALITY}, ")
    assert "masterpiece, best quality" in built  # the code's chain, not the file's two tags
    assert not built.startswith("score_9_up, masterpiece,")


def test_the_quality_field_changes_nothing():
    # The whole of what the field means now, in one line: with it and without it are the same
    # prompt. Anything less than this leaves room for it to matter somewhere.
    assert build_prompts(_structure(quality="a wholly different chain")) == build_prompts(
        _structure()
    )


def test_loose_commas_and_spaces_are_tidied_away():
    # Measured on a frame's own field since Madde 150: quality is no longer something a file can
    # write, but the tidying it used to prove is _tags' and still holds.
    structure = _structure(frames=[_frame(action=" , sitting , ", camera=" ,, medium shot,")])
    assert build_prompts(structure) == [
        f"{QUALITY}, {AYLIN}, {BEDROOM}, sitting, medium shot"
    ]


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
        build_prompts({"characters": {}})


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


def test_a_character_written_with_a_kind_still_builds():
    # The shape set_character wrote between Madde 154 and 163, and files on the user's disk still
    # carry it. The tags come through exactly as written and the kind beside them changes nothing:
    # from 163 on it is a field nobody reads.
    structure = _structure(characters={"aylin": {"kind": "girl", "tags": AYLIN}})
    assert build_prompts(structure) == [
        f"{QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"
    ]


def test_a_character_written_as_plain_text_still_builds():
    # Every file on the user's disk carries this shape, and a rename cannot turn their work into
    # rubbish -- the rule the shots fallback has kept since it was written.
    assert build_prompts(_structure()) == [
        f"{QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"
    ]


def test_a_preview_reads_both_shapes_too():
    plain = _tried(_structure(), "aylin")
    with_kind = _tried(_structure(characters={"aylin": {"kind": "girl", "tags": AYLIN}}), "aylin")
    assert with_kind == plain


def test_a_frames_number_never_reaches_the_prompt():
    # The number is for the file's readers -- the user and the tools that address a frame by it
    # (Madde 153). An image model has no use for it, and a builder that carried it through would put
    # a bare 3 in front of every picture.
    assert build_prompts(_structure(frames=[_frame(frame=3)])) == build_prompts(_structure())


def test_the_people_tag_is_written_right_after_quality():
    built = build_prompts(_structure(frames=[_frame(people="1girl")]))
    assert built == [f"{QUALITY}, 1girl, {AYLIN}, {BEDROOM}, an action, a camera"]


def test_a_frame_without_a_people_tag_still_splits():
    # Files written before the field existed carry no count. What is missing is skipped -- the way a
    # missing quality is skipped -- and the order still opens up around the camera.
    built = build_prompts(_structure(frames=[_frame(characters={"aylin": [], "deniz": []})]))
    assert built == [f"{QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera{BREAK}{DENIZ}"]


def test_an_empty_people_tag_adds_nothing():
    # A count written blank must not leave a gap behind, the way an empty quality does not.
    built = build_prompts(_structure(frames=[_frame(people=" ")]))
    assert built == [f"{QUALITY}, {AYLIN}, {BEDROOM}, an action, a camera"]


def test_the_code_never_works_a_count_out_of_the_characters():
    # Madde 163. Two girls in one frame, and nothing in it says so: the prompt carries what the tags
    # carry and not one tag more. Madde 156 wrote 2girls here, from the kinds beside the tags.
    structure = _structure(
        characters=_kinds(aylin="girl", deniz="girl"),
        frames=[_frame(characters={"aylin": [], "deniz": []})],
    )
    built = build_prompts(structure)[0]
    assert built == f"{QUALITY}, {AYLIN_TAGS}, {BEDROOM}, an action, a camera{BREAK}{DENIZ_TAGS}"


def test_each_character_carries_its_own_count_into_its_own_block():
    # Where the count went instead. Madde 139 put a BREAK between character blocks, so each one is
    # its own chunk to the encoder -- and a count written into a character's tags lands inside the
    # chunk describing that character, which is the whole reason 156's aggregate is not needed.
    built = build_prompts(_structure(frames=[_frame(characters={"aylin": [], "deniz": []})]))[0]
    opening, behind = built.split(BREAK)
    assert "1girl" in opening and "1boy" not in opening
    assert "1boy" in behind and "1girl" not in behind


def test_the_kind_itself_never_reaches_the_prompt():
    # The one thing the map form must never do. girl beside a character's own 1girl would be the
    # same thing said twice, in a place where saying it twice weights it -- and these tags carry no
    # count of their own, so any girl in the prompt could only have come out of the field.
    built = build_prompts(_structure(characters=_kinds(aylin="girl")))[0]
    assert "girl" not in built


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
        f"{QUALITY}, {PEOPLE}, {AYLIN}, {BEDROOM}, an action, a camera{BREAK}{DENIZ}"
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


def test_the_two_behind_are_cut_off_from_each_other_too():
    # The cost the ordering fix accepted -- the two behind still bleeding into each other -- is not
    # worth accepting once a separator exists. One rule with no exception: every character block
    # gets a break, so the third is as separate from the second as the second is from the lead.
    structure = _structure(
        characters={"aylin": AYLIN, "deniz": DENIZ, "eda": EDA},
        frames=[_frame(people="2girls, 1boy", characters={"aylin": [], "deniz": [], "eda": []})],
    )
    assert build_prompts(structure)[0].endswith(f"{DENIZ}{BREAK}{EDA}")


def test_break_never_touches_a_comma():
    # The node reading the prompt splits on the literal string, so a BREAK written as one more tag
    # would leave every chunk opening and closing on a comma. Harmless to the model, unreadable to
    # whoever opens the file -- and the reason the blocks are joined rather than listed.
    frame = _frame(people=PEOPLE, characters={"aylin": ["gecelik"], "deniz": ["takim"]})
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


def test_a_try_ignores_the_files_own_quality():
    # The same rule as a frame's, because a look at one character has to show what a frame will
    # show -- a preview opening with a different chain would be a preview of nothing.
    structure = _structure(quality="a wholly different chain")
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
