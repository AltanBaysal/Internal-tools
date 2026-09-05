import json

import pytest

from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.domain.naming import unique_name
from backend.features.workspace.domain.tools import (
    DEFAULT_NAME,
    MAX_ROUNDS,
    TOOL_SPECS,
    numbered,
    run_tool,
    safe_name,
)
from backend.services.store.store import Store

STRUCTURE = json.dumps(
    {
        "quality": "score_9_up",
        "characters": {"aylin": "1girl, long teal hair"},
        "outfits": {"gecelik": "white nightgown"},
        "locations": {"bedroom": "sunlit bedroom"},
        "frames": [
            {
                "characters": {"aylin": ["gecelik"]},
                "location": "bedroom",
                "action": "one",
                "camera": "wide",
            },
            {
                "characters": {"aylin": ["gecelik"]},
                "location": "bedroom",
                "action": "two",
                "camera": "close",
            },
        ],
    }
)


def _files(tmp_path):
    return FileFileStore(Store(str(tmp_path)))


def _call(files, tool, **arguments):
    return run_tool(files, "p1", tool, json.dumps(arguments)).text


def _with(tmp_path, name, content):
    files = _files(tmp_path)
    files.write("p1", name, content)
    return files


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("plan.md", "plan.md"),
        ("notes/plan.md", "plan.md"),
        ("..\\..\\etc\\passwd", "passwd.md"),
        ("Chapter 2 intro", "Chapter-2-intro.md"),
        ("...", DEFAULT_NAME),
        ("", DEFAULT_NAME),
        (None, DEFAULT_NAME),
    ],
)
def test_a_name_from_the_model_is_cleaned(raw, expected):
    assert safe_name(raw) == expected


def test_a_taken_name_gets_a_number_rather_than_overwriting():
    assert unique_name(["plan.md"], "plan.md") == "plan-2.md"
    assert unique_name(["plan.md", "plan-2.md"], "plan.md") == "plan-3.md"


def test_a_name_with_no_extension_is_numbered_the_same_way():
    # A project id is a directory name, not a filename, and the trash numbers it by the same rule.
    # Splitting on a dot that is not there used to turn p1 into -2.p1.
    assert unique_name(["p1"], "p1") == "p1-2"
    assert unique_name(["p1", "p1-2"], "p1") == "p1-3"


def test_what_was_written_is_what_a_read_finds(tmp_path):
    files = _files(tmp_path)
    _call(files, "create_file", name="plan.md", content="the body")
    # The receipt rather than the document since Madde 179 -- the contents ride in the context box.
    # What this asks is the seam between the two tools: a file written is a file the next read
    # opens, and the line count is the nearest thing the answer says about what is in it.
    assert _call(files, "read_file", name="plan.md") == "plan.md, 1 line; it is in your opened files."


def test_reading_a_file_that_is_not_there_is_an_answer_not_a_crash(tmp_path):
    assert "no file by that name" in _call(_files(tmp_path), "read_file", name="ghost.md")


# --- the tool that gives birth to a structure file (Madde 167) ------------------------------------
#
# create_file writes a document, this writes a structure -- and its whole shape is four empty maps
# the code knows, so the tool takes no content at all. A tool with nothing to fill in is a model
# that never sees the shape, which is this run's binding rule.
#
# It has to exist before Madde 171 closes .json to create_file: a door shut with no other way
# through leaves the model unable to start anything.


def _started(files, name="bar-scene"):
    return json.loads(files.read("p1", run_tool(files, "p1", "start_scenario", json.dumps({"name": name})).target))


def test_start_scenario_writes_the_empty_maps_and_no_frames(tmp_path):
    # Exactly these four, and every one of them empty. A fifth key would be a shape the model never
    # asked for, and a missing one would have the first add_ call inventing it.
    files = _files(tmp_path)
    assert _started(files) == {"characters": {}, "outfits": {}, "locations": {}, "frames": []}


@pytest.mark.parametrize("asked", ["bar-scene", "bar-scene.md", "bar scene"])
def test_start_scenario_names_the_file_after_the_scenario(tmp_path, asked):
    # The extension is the tool's, the way a plan's is (plan_name). Madde 171 shuts the door on
    # .json, so the tool that opens one has to land on the same extension -- two that disagreed
    # would leave the door guarding a file nothing writes.
    files = _files(tmp_path)
    assert run_tool(files, "p1", "start_scenario", json.dumps({"name": asked})).target == (
        "bar-scene.json"
    )


def test_start_scenario_refuses_a_name_that_is_taken(tmp_path):
    # Madde 69's rule on this path too, with its own way out: a scenario is opened and added to,
    # never born a second time. Saying only that one exists would leave the next move to a guess.
    files = _with(tmp_path, "bar-scene.json", STRUCTURE)
    said = _call(files, "start_scenario", name="bar-scene")
    assert "There is already a file called bar-scene.json." in said
    assert "Open it and add to it, or pick another name for a new scenario." in said
    # And the scenario that was there is untouched -- the refusal is a refusal, not a rewrite.
    assert files.read("p1", "bar-scene.json") == STRUCTURE


def test_start_scenario_says_what_it_started(tmp_path):
    # One call, both halves read off it. Calling twice over the same tmp_path would meet the
    # scenario the first call wrote, and the second answer would be the refusal.
    made = run_tool(_files(tmp_path), "p1", "start_scenario", json.dumps({"name": "bar-scene"}))
    assert made.text == "Started bar-scene.json."
    assert made.outcome == "Started"


def test_start_scenario_hands_the_name_back_so_a_card_is_drawn(tmp_path):
    from backend.features.workspace.domain.tools import WRITES_FILES

    files = _files(tmp_path)
    assert run_tool(files, "p1", "start_scenario", json.dumps({"name": "bar"})).created == "bar.json"
    assert "start_scenario" in WRITES_FILES


def test_start_scenario_writes_the_file_for_a_person_to_read(tmp_path):
    # The user opens this file and fixes it by hand, so it is indented rather than one long line --
    # the rule every write to a structure keeps, and the same person opening the same file.
    files = _files(tmp_path)
    _call(files, "start_scenario", name="bar-scene")
    assert '\n  "characters": {}' in files.read("p1", "bar-scene.json")


# --- character management (Madde 168) -------------------------------------------------------------
#
# Three tools rather than one, by the rule create_file already keeps: add refuses a name that is
# there, update refuses one that is not, and so overwriting in silence stops being possible. The
# file's parameter is `file` and the entry's is `name` -- the subject of these sentences is the
# character, and the file is only where it lives.
#
# The shared opener and cast_of are born here too. Maddes 169 to 174 repeat this shape exactly, so
# what is nailed below is as much the pattern as the character.

CAST = json.dumps(
    {
        "characters": {
            "aylin": "1girl, long teal hair",
            "deniz": "1boy, short black hair",
            # In no frame at all: the one entry that can actually be removed.
            "eda": "1girl, freckles",
        },
        "outfits": {
            "gecelik": "white nightgown",
            "takim": "dark grey suit",
            # Worn in no frame at all: the one outfit that can actually be removed.
            "atki": "red knit scarf",
        },
        "locations": {
            "bedroom": "sunlit bedroom",
            # Nobody's place: the one location that can actually be removed.
            "kapi_onu": "apartment doorway, daytime",
        },
        "frames": [
            {"characters": {"aylin": ["gecelik"]}, "location": "bedroom", "action": "one"},
            {"characters": {"deniz": ["takim"]}, "location": "bedroom", "action": "two"},
            {
                "characters": {"aylin": ["gecelik"], "deniz": []},
                "location": "bedroom",
                "action": "three",
            },
        ],
    }
)


def _cast(tmp_path):
    return _with(tmp_path, "bar-scene.json", CAST)


def _read_back(files, key="characters"):
    return json.loads(files.read("p1", "bar-scene.json"))[key]


def test_add_character_writes_the_name_and_its_tags(tmp_path):
    files = _cast(tmp_path)
    _call(files, "add_character", file="bar-scene.json", name="lara", tags="1girl, red hair")
    assert _read_back(files)["lara"] == "1girl, red hair"


def test_add_character_says_what_it_added(tmp_path):
    files = _cast(tmp_path)
    made = run_tool(
        files,
        "p1",
        "add_character",
        json.dumps({"file": "bar-scene.json", "name": "lara", "tags": "1girl"}),
    )
    assert made.text == "Added lara to characters."
    assert made.outcome == "Added"


def test_add_character_refuses_a_name_that_is_already_there(tmp_path):
    # Madde 69's rule, one level down. A second aylin would silently replace the first, and every
    # frame naming her would change without anybody asking for it.
    files = _cast(tmp_path)
    said = _call(files, "add_character", file="bar-scene.json", name="aylin", tags="1girl, new")
    assert said == "There is already a character called aylin."
    assert _read_back(files)["aylin"] == "1girl, long teal hair"


def test_add_character_needs_a_name(tmp_path):
    files = _cast(tmp_path)
    assert _call(files, "add_character", file="bar-scene.json", tags="1girl") == (
        "A character needs a name."
    )


def test_add_character_needs_tags(tmp_path):
    # An entry with no text is an entry every frame naming it builds nothing from. Refused at birth
    # rather than found in the prompt.
    files = _cast(tmp_path)
    assert _call(files, "add_character", file="bar-scene.json", name="lara") == (
        "A new character needs tags."
    )


def test_add_character_leaves_the_other_maps_alone(tmp_path):
    files = _cast(tmp_path)
    _call(files, "add_character", file="bar-scene.json", name="lara", tags="1girl")
    # Asserted first, and not for company: without it everything below is vacuously true on a call
    # that did nothing at all.
    assert "lara" in _read_back(files)
    before = json.loads(CAST)
    for key in ("outfits", "locations", "frames"):
        assert _read_back(files, key) == before[key]


def test_update_character_changes_the_tags(tmp_path):
    files = _cast(tmp_path)
    _call(files, "update_character", file="bar-scene.json", name="aylin", tags="1girl, red hair")
    assert _read_back(files)["aylin"] == "1girl, red hair"


def test_update_character_refuses_a_name_nobody_knows(tmp_path):
    # _looked_up's sentence, so a name that is not there reads the same wherever it is met.
    files = _cast(tmp_path)
    said = _call(files, "update_character", file="bar-scene.json", name="lara", tags="1girl")
    assert said == "lara is not in characters; known: aylin, deniz, eda."


def test_update_character_renames_and_the_frames_follow(tmp_path):
    # The whole reason renaming lives in this tool rather than in one of its own: a name changed in
    # the map and left alone in the frames is a structure that will not build.
    files = _cast(tmp_path)
    _call(files, "update_character", file="bar-scene.json", name="aylin", new_name="ayla")
    assert "aylin" not in _read_back(files)
    assert _read_back(files)["ayla"] == "1girl, long teal hair"
    frames = _read_back(files, "frames")
    assert frames[0]["characters"] == {"ayla": ["gecelik"]}
    # And the one behind her keeps their place and their clothes.
    assert frames[2]["characters"] == {"ayla": ["gecelik"], "deniz": []}


def test_update_character_says_how_many_frames_followed(tmp_path):
    files = _cast(tmp_path)
    said = _call(files, "update_character", file="bar-scene.json", name="aylin", new_name="ayla")
    assert said == "Renamed aylin to ayla in characters; 2 frames followed."


def test_update_character_can_do_both_at_once(tmp_path):
    files = _cast(tmp_path)
    said = _call(
        files,
        "update_character",
        file="bar-scene.json",
        name="aylin",
        new_name="ayla",
        tags="1girl, red hair",
    )
    assert said == "Renamed aylin to ayla in characters and changed its text; 2 frames followed."
    assert _read_back(files)["ayla"] == "1girl, red hair"


def test_update_character_refuses_a_name_that_is_taken(tmp_path):
    # Two entries folded into one is the one thing here that cannot be undone by calling again.
    files = _cast(tmp_path)
    said = _call(files, "update_character", file="bar-scene.json", name="aylin", new_name="deniz")
    assert said == "There is already a character called deniz."
    assert _read_back(files)["deniz"] == "1boy, short black hair"


def test_update_character_needs_something_to_change(tmp_path):
    # No silent success. A model told nothing happened moves on believing it did.
    files = _cast(tmp_path)
    assert _call(files, "update_character", file="bar-scene.json", name="aylin") == (
        "Nothing was given to change about aylin."
    )


def test_update_character_refuses_renaming_to_the_same_name(tmp_path):
    files = _cast(tmp_path)
    assert _call(
        files, "update_character", file="bar-scene.json", name="aylin", new_name="aylin"
    ) == "aylin is already called that."


def test_update_character_reads_the_old_list_form_when_it_renames(tmp_path):
    # Files written before outfits existed carry a plain list of names, and a rename cannot turn
    # what is already on the user's disk into rubbish.
    old = json.loads(CAST)
    old["frames"] = [{"characters": ["aylin", "deniz"], "location": "bedroom", "action": "one"}]
    files = _with(tmp_path, "bar-scene.json", json.dumps(old))
    _call(files, "update_character", file="bar-scene.json", name="aylin", new_name="ayla")
    assert _read_back(files, "frames")[0]["characters"] == ["ayla", "deniz"]


def test_remove_character_takes_the_name_out(tmp_path):
    files = _cast(tmp_path)
    said = _call(files, "remove_character", file="bar-scene.json", name="eda")
    assert said == "Removed eda from characters."
    assert "eda" not in _read_back(files)


def test_remove_character_refuses_while_a_frame_names_it(tmp_path):
    # The frames are the answer to whether anything stands on this entry, which is why removing
    # opens the file where adding could have worked on the map alone.
    files = _cast(tmp_path)
    said = _call(files, "remove_character", file="bar-scene.json", name="aylin")
    assert said == "aylin is still in frames 1, 3. Nothing was removed."
    assert "aylin" in _read_back(files)


def test_remove_character_refuses_a_name_nobody_knows(tmp_path):
    files = _cast(tmp_path)
    assert _call(files, "remove_character", file="bar-scene.json", name="lara") == (
        "lara is not in characters; known: aylin, deniz, eda."
    )


def test_remove_character_leaves_the_frames_alone(tmp_path):
    files = _cast(tmp_path)
    _call(files, "remove_character", file="bar-scene.json", name="eda")
    # First, or the line below is vacuously true on a call that removed nothing.
    assert "eda" not in _read_back(files)
    assert _read_back(files, "frames") == json.loads(CAST)["frames"]


CHARACTER_TOOLS = ("add_character", "update_character", "remove_character")


@pytest.mark.parametrize("tool", CHARACTER_TOOLS)
def test_a_character_tool_says_when_the_file_is_not_there(tmp_path, tool):
    files = _files(tmp_path)
    assert _call(files, tool, file="ghost.json", name="aylin", tags="1girl") == (
        "There is no file by that name."
    )


@pytest.mark.parametrize("tool", CHARACTER_TOOLS)
def test_a_character_tool_says_when_the_file_is_not_json(tmp_path, tool):
    # The parser's own sentence. A guessed cause sends the model somewhere else entirely.
    files = _with(tmp_path, "bar-scene.json", "not json at all")
    said = _call(files, tool, file="bar-scene.json", name="aylin", tags="1girl")
    assert said.startswith("bar-scene.json is not valid JSON:")


@pytest.mark.parametrize("tool", CHARACTER_TOOLS)
def test_a_character_tool_says_when_the_file_has_no_frames_list(tmp_path, tool):
    # Asked of every one of them, not only of the two that read the frames. Removing asks whether
    # anything stands on the entry and renaming rewrites what does -- so a file with no list cannot
    # do this work, and saying so while adding beats crashing while removing.
    files = _with(tmp_path, "bar-scene.json", json.dumps({"characters": {}}))
    said = _call(files, tool, file="bar-scene.json", name="aylin", tags="1girl")
    assert said == "bar-scene.json has no frames list to add to; a structure file carries one."


def test_the_cast_of_a_frame_is_read_the_same_way_everywhere():
    # One reading of a frame's cast, not two. build_prompts held it privately and these tools need
    # the same two shapes; a copy would part from it on the first change to either.
    from backend.features.workspace.domain.build_prompts import cast_of

    assert cast_of({"characters": {"aylin": ["gecelik"], "deniz": []}}) == [
        ("aylin", ["gecelik"]),
        ("deniz", []),
    ]
    # What files written before outfits existed carry.
    assert cast_of({"characters": ["aylin", "deniz"]}) == [("aylin", []), ("deniz", [])]
    # One outfit written without its list is that one name, not its letters.
    assert cast_of({"characters": {"aylin": "gecelik"}}) == [("aylin", ["gecelik"])]


# --- outfit management (Madde 169) ----------------------------------------------------------------
#
# The same three tools over a second map, and the shared bodies carry most of it. What does not come
# free is everything touching a frame: a character is a key in the frame's cast, an outfit is a name
# inside that key's list. So "which frames stand on this" and "carry the rename through" both need
# their own answer here -- and so does the refusal's verb, because an outfit is worn rather than
# merely present.


def test_add_outfit_writes_the_name_and_its_tags(tmp_path):
    files = _cast(tmp_path)
    _call(files, "add_outfit", file="bar-scene.json", name="palto", tags="long wool coat")
    assert _read_back(files, "outfits")["palto"] == "long wool coat"


def test_add_outfit_says_what_it_added(tmp_path):
    files = _cast(tmp_path)
    assert _call(files, "add_outfit", file="bar-scene.json", name="palto", tags="coat") == (
        "Added palto to outfits."
    )


def test_add_outfit_refuses_a_name_that_is_already_there(tmp_path):
    files = _cast(tmp_path)
    said = _call(files, "add_outfit", file="bar-scene.json", name="gecelik", tags="something")
    assert said == "There is already an outfit called gecelik."
    assert _read_back(files, "outfits")["gecelik"] == "white nightgown"


def test_add_outfit_needs_a_name(tmp_path):
    # The singular comes off the plural, so one sentence serves three maps. This is where that is
    # measured on a second one.
    files = _cast(tmp_path)
    assert _call(files, "add_outfit", file="bar-scene.json", tags="coat") == (
        "An outfit needs a name."
    )


def test_add_outfit_needs_tags(tmp_path):
    files = _cast(tmp_path)
    assert _call(files, "add_outfit", file="bar-scene.json", name="palto") == (
        "A new outfit needs tags."
    )


def test_update_outfit_changes_the_tags(tmp_path):
    files = _cast(tmp_path)
    _call(files, "update_outfit", file="bar-scene.json", name="gecelik", tags="black slip")
    assert _read_back(files, "outfits")["gecelik"] == "black slip"


def test_update_outfit_refuses_a_name_nobody_knows(tmp_path):
    # This map's names only. A character's name is no help to somebody looking for an outfit.
    files = _cast(tmp_path)
    assert _call(files, "update_outfit", file="bar-scene.json", name="palto", tags="coat") == (
        "palto is not in outfits; known: atki, gecelik, takim."
    )


def test_update_outfit_renames_and_the_frames_follow(tmp_path):
    # An outfit lives inside a character's list, not as a key of the cast. The rename has to reach
    # in there and leave the character's own name exactly where it was.
    files = _cast(tmp_path)
    _call(files, "update_outfit", file="bar-scene.json", name="gecelik", new_name="pijama")
    frames = _read_back(files, "frames")
    assert frames[0]["characters"] == {"aylin": ["pijama"]}
    assert frames[2]["characters"] == {"aylin": ["pijama"], "deniz": []}
    # And the outfit nobody renamed is untouched.
    assert frames[1]["characters"] == {"deniz": ["takim"]}


def test_update_outfit_says_how_many_frames_followed(tmp_path):
    files = _cast(tmp_path)
    assert _call(
        files, "update_outfit", file="bar-scene.json", name="gecelik", new_name="pijama"
    ) == "Renamed gecelik to pijama in outfits; 2 frames followed."


def test_update_outfit_renames_inside_the_short_form_too(tmp_path):
    # One outfit written without its list is still that outfit, and a rename that skipped it would
    # leave a frame naming something the map no longer has.
    short = json.loads(CAST)
    short["frames"] = [{"characters": {"aylin": "gecelik"}, "location": "bedroom", "action": "one"}]
    files = _with(tmp_path, "bar-scene.json", json.dumps(short))
    _call(files, "update_outfit", file="bar-scene.json", name="gecelik", new_name="pijama")
    assert _read_back(files, "frames")[0]["characters"] == {"aylin": "pijama"}


def test_remove_outfit_takes_the_name_out(tmp_path):
    files = _cast(tmp_path)
    assert _call(files, "remove_outfit", file="bar-scene.json", name="atki") == (
        "Removed atki from outfits."
    )
    assert "atki" not in _read_back(files, "outfits")


def test_remove_outfit_refuses_while_a_frame_wears_it(tmp_path):
    # Its own verb. An outfit is worn by somebody; saying it is "in" a frame would read as a thing
    # lying there with nobody in it.
    files = _cast(tmp_path)
    said = _call(files, "remove_outfit", file="bar-scene.json", name="gecelik")
    assert said == "gecelik is still worn in frames 1, 3. Nothing was removed."
    assert "gecelik" in _read_back(files, "outfits")


def test_remove_outfit_leaves_the_characters_alone(tmp_path):
    files = _cast(tmp_path)
    _call(files, "remove_outfit", file="bar-scene.json", name="atki")
    # First, or the line below is vacuously true on a call that removed nothing.
    assert "atki" not in _read_back(files, "outfits")
    assert _read_back(files) == json.loads(CAST)["characters"]


OUTFIT_TOOLS = ("add_outfit", "update_outfit", "remove_outfit")


@pytest.mark.parametrize("tool", OUTFIT_TOOLS)
def test_an_outfit_tool_opens_the_file_the_same_way(tmp_path, tool):
    # The shared opener, measured on a second map: one missing file reads the same wherever it is
    # met, and that is the whole reason those four lines live in one place.
    assert _call(_files(tmp_path), tool, file="ghost.json", name="gecelik", tags="x") == (
        "There is no file by that name."
    )
    broken = _with(tmp_path, "bar-scene.json", "not json at all")
    assert _call(broken, tool, file="bar-scene.json", name="gecelik", tags="x").startswith(
        "bar-scene.json is not valid JSON:"
    )
    listless = _with(tmp_path, "listless.json", json.dumps({"outfits": {}}))
    assert _call(listless, tool, file="listless.json", name="gecelik", tags="x") == (
        "listless.json has no frames list to add to; a structure file carries one."
    )


# --- location management (Madde 170) --------------------------------------------------------------
#
# The third and last map, and the narrowest. A character is a key of the frame's cast and an outfit
# is a name inside it, so both are read through cast_of; a location is not there at all. It is the
# frame's own field, there is exactly one of it, and it is always a plain string -- no second shape
# on disk to forgive.
#
# Which makes this the measure of whether the shared bodies are really shared: a third map should
# arrive as a branch and a row, not as another loosening of the middle.


def test_add_location_writes_the_name_and_its_tags(tmp_path):
    files = _cast(tmp_path)
    _call(files, "add_location", file="bar-scene.json", name="balkon", tags="balcony, night")
    assert _read_back(files, "locations")["balkon"] == "balcony, night"


def test_add_location_says_what_it_added(tmp_path):
    files = _cast(tmp_path)
    assert _call(files, "add_location", file="bar-scene.json", name="balkon", tags="balcony") == (
        "Added balkon to locations."
    )


def test_add_location_refuses_a_name_that_is_already_there(tmp_path):
    # The article goes back to "a" here: one rule over three singulars, and this is the third.
    files = _cast(tmp_path)
    said = _call(files, "add_location", file="bar-scene.json", name="bedroom", tags="something")
    assert said == "There is already a location called bedroom."
    assert _read_back(files, "locations")["bedroom"] == "sunlit bedroom"


def test_add_location_needs_a_name(tmp_path):
    files = _cast(tmp_path)
    assert _call(files, "add_location", file="bar-scene.json", tags="balcony") == (
        "A location needs a name."
    )


def test_update_location_changes_the_tags(tmp_path):
    files = _cast(tmp_path)
    _call(files, "update_location", file="bar-scene.json", name="bedroom", tags="dark bedroom")
    assert _read_back(files, "locations")["bedroom"] == "dark bedroom"


def test_update_location_refuses_a_name_nobody_knows(tmp_path):
    files = _cast(tmp_path)
    assert _call(files, "update_location", file="bar-scene.json", name="balkon", tags="x") == (
        "balkon is not in locations; known: bedroom, kapi_onu."
    )


def test_update_location_renames_and_the_frames_follow(tmp_path):
    # A frame names its place in a field of its own, so the rename writes there and leaves the cast
    # entirely alone.
    files = _cast(tmp_path)
    _call(files, "update_location", file="bar-scene.json", name="bedroom", new_name="yatak")
    frames = _read_back(files, "frames")
    assert [frame["location"] for frame in frames] == ["yatak", "yatak", "yatak"]
    assert frames[0]["characters"] == {"aylin": ["gecelik"]}


def test_update_location_says_how_many_frames_followed(tmp_path):
    files = _cast(tmp_path)
    assert _call(
        files, "update_location", file="bar-scene.json", name="bedroom", new_name="yatak"
    ) == "Renamed bedroom to yatak in locations; 3 frames followed."


def test_remove_location_takes_the_name_out(tmp_path):
    files = _cast(tmp_path)
    assert _call(files, "remove_location", file="bar-scene.json", name="kapi_onu") == (
        "Removed kapi_onu from locations."
    )
    assert "kapi_onu" not in _read_back(files, "locations")


def test_remove_location_refuses_while_it_is_a_frames_place(tmp_path):
    # Its own verb, and the row written in 169 that has not run until now. A place is not something
    # standing in a frame; it is what the frame is set in.
    files = _cast(tmp_path)
    said = _call(files, "remove_location", file="bar-scene.json", name="bedroom")
    assert said == "bedroom is still the place in frames 1, 2, 3. Nothing was removed."
    assert "bedroom" in _read_back(files, "locations")


def test_remove_location_leaves_the_frames_alone(tmp_path):
    files = _cast(tmp_path)
    _call(files, "remove_location", file="bar-scene.json", name="kapi_onu")
    # First, or the line below is vacuously true on a call that removed nothing.
    assert "kapi_onu" not in _read_back(files, "locations")
    assert _read_back(files, "frames") == json.loads(CAST)["frames"]


LOCATION_TOOLS = ("add_location", "update_location", "remove_location")


@pytest.mark.parametrize("tool", LOCATION_TOOLS)
def test_a_location_tool_opens_the_file_the_same_way(tmp_path, tool):
    assert _call(_files(tmp_path), tool, file="ghost.json", name="bedroom", tags="x") == (
        "There is no file by that name."
    )
    broken = _with(tmp_path, "bar-scene.json", "not json at all")
    assert _call(broken, tool, file="bar-scene.json", name="bedroom", tags="x").startswith(
        "bar-scene.json is not valid JSON:"
    )
    listless = _with(tmp_path, "listless.json", json.dumps({"locations": {}}))
    assert _call(listless, tool, file="listless.json", name="bedroom", tags="x") == (
        "listless.json has no frames list to add to; a structure file carries one."
    )


def test_the_three_maps_are_managed_by_the_same_nine_tools():
    # The one place that says the pattern is a pattern. A later madde adding a parameter to one of
    # the nine, or naming a tenth differently, is caught here rather than by a reader noticing.
    declared = {spec["function"]["name"]: spec["function"] for spec in TOOL_SPECS}
    for which in ("character", "outfit", "location"):
        assert set(declared[f"add_{which}"]["parameters"]["required"]) == {"file", "name", "tags"}
        assert set(declared[f"update_{which}"]["parameters"]["required"]) == {"file", "name"}
        assert set(declared[f"update_{which}"]["parameters"]["properties"]) == {
            "file",
            "name",
            "tags",
            "new_name",
        }
        assert set(declared[f"remove_{which}"]["parameters"]["properties"]) == {"file", "name"}


# --- the door on a structure file (Madde 171) -----------------------------------------------------
#
# Shut only now, and not a madde earlier. A door with nothing behind it leaves the model unable to
# start anything at all; by here there is start_scenario and there are nine map tools, so a scenario
# can be opened, filled, corrected and emptied without one line of JSON being typed.
#
# No exception, by the user's decision of 5 Sep. A broken structure file cannot have come from these
# tools -- they refuse to open one -- so it came from somebody editing by hand, and handing that
# back to the model as text is handing it a guess. The model says the file is broken and where; the
# user fixes it.

SHUT = (
    "bar-scene.json is a structure file; it is not written or changed as text. Use start_scenario "
    "to open one, and the add_, update_ and remove_ tools to change it."
)


def test_create_file_refuses_a_structure_file(tmp_path):
    files = _files(tmp_path)
    assert _call(files, "create_file", name="bar-scene.json", content="{}") == SHUT
    # And nothing was born: a refusal that still wrote the file would be the worst of both.
    assert files.list_names("p1") == []


def test_edit_file_refuses_a_structure_file(tmp_path):
    files = _cast(tmp_path)
    assert _call(files, "edit_file", name="bar-scene.json", old="aylin", new="ayla") == SHUT
    assert files.read("p1", "bar-scene.json") == CAST


def test_the_door_is_shut_whatever_the_case_of_the_extension(tmp_path):
    # Windows opens BAR.JSON and bar.json as one file, so a door that read the case would be a door
    # standing beside its own frame.
    files = _files(tmp_path)
    said = _call(files, "create_file", name="BAR.JSON", content="{}")
    assert said.startswith("BAR.JSON is a structure file;")
    assert files.list_names("p1") == []


def test_the_door_is_shut_even_on_a_broken_structure_file(tmp_path):
    # The exception the archive kept, and the user closed on 5 Sep. The tools refuse to open a
    # broken file, so a broken file came from a hand rather than from here -- and repairing what a
    # person wrote by letting the model guess at it is not a repair.
    files = _with(tmp_path, "bar-scene.json", "{ not json")
    assert _call(files, "edit_file", name="bar-scene.json", old="not", new="also not") == SHUT
    assert files.read("p1", "bar-scene.json") == "{ not json"


def test_create_file_still_writes_a_document(tmp_path):
    files = _files(tmp_path)
    assert _call(files, "create_file", name="notes.md", content="the body") == "Saved as notes.md."


def test_edit_file_still_changes_a_document(tmp_path):
    files = _with(tmp_path, "notes.md", "the body")
    assert _call(files, "edit_file", name="notes.md", old="body", new="text") == "Edited notes.md."


def test_the_tool_that_opens_a_scenario_lands_where_the_door_is(tmp_path):
    # 167 named the file .json whatever it was asked for, and gave this as the reason. Measured
    # here: the one tool that may open a structure lands behind the door that shuts on everything
    # else, so the door never stands in front of a file nothing can write.
    files = _files(tmp_path)
    born = run_tool(files, "p1", "start_scenario", json.dumps({"name": "bar-scene.md"}))
    assert born.target.endswith(".json")
    assert _call(files, "edit_file", name=born.target, old="{", new="[").endswith(
        "it is not written or changed as text. Use start_scenario to open one, and the add_, "
        "update_ and remove_ tools to change it."
    )


# --- creating over a name that is taken (Madde 69) ------------------------------------------------
#
# It used to number: plan.md became plan-2.md and the project held two versions of one document. The
# way to change a file that exists is edit_file, and until now reaching for it was the model's own
# choice -- which is the kind of thing FOUNDATION 5 says code decides.


def test_creating_over_a_name_that_is_taken_writes_nothing(tmp_path):
    files = _with(tmp_path, "plan.md", "first")
    _call(files, "create_file", name="plan.md", content="second")
    # Asked of the store rather than through read_file: the subject here is what is on disk, and
    # since Madde 179 the tool hands back a receipt rather than the document.
    assert files.read("p1", "plan.md") == "first"
    # And no copy beside it: refusing means one document, which was the whole point.
    assert files.list_names("p1") == ["plan.md"]


def test_a_refused_create_points_at_the_tool_that_can_do_it(tmp_path):
    # The tool result is the instruction. Saying only "there is already one" would leave the model
    # to guess the next move, and guessing is what put it here.
    files = _with(tmp_path, "plan.md", "first")
    assert "edit_file" in _call(files, "create_file", name="plan.md", content="second")


def test_a_refused_create_brings_no_file_into_being(tmp_path):
    # No card: nothing was born. The same rule edit_file follows.
    files = _with(tmp_path, "plan.md", "first")
    refused = run_tool(files, "p1", "create_file", json.dumps({"name": "plan.md", "content": "x"}))
    assert refused.created is None


def test_a_refused_create_names_the_file_that_was_in_the_way(tmp_path):
    # The call was about that file, and the card says which. It used to name plan-2.md -- a file
    # that only existed because of the numbering this item took away.
    files = _with(tmp_path, "plan.md", "first")
    assert _target(files, "create_file", name="plan.md", content="second") == "plan.md"


def test_a_refused_create_does_not_say_it_saved(tmp_path):
    files = _with(tmp_path, "plan.md", "first")
    assert _outcome(files, "create_file", name="plan.md", content="second") == "Already there"


# --- the plan tool (Madde 91) --------------------------------------------------------------------


def test_a_plan_is_written_under_a_name_that_says_it_is_one(tmp_path):
    # Two jobs in one rule: a plan is recognisable on disk, and the tool cannot be turned into a way
    # of writing the very deliverable it was supposed to be planning.
    files = _files(tmp_path)
    assert "bar-scene-plan.md" in _call(files, "write_plan", name="bar-scene.md", content="1. ...")
    assert files.read("p1", "bar-scene-plan.md") == "1. ..."
    # A name that already says it is a plan is not made to say it twice.
    assert "bar-scene-plan.md" in _call(files, "write_plan", name="bar-scene-plan.md", content="x")


def test_writing_a_plan_again_replaces_it(tmp_path):
    # Unlike create_file, which never overwrites. A second plan sitting in bar-scene-plan-2.md would
    # lose which of the two is the one to follow.
    files = _files(tmp_path)
    _call(files, "write_plan", name="bar-scene", content="first")
    _call(files, "write_plan", name="bar-scene", content="second")
    assert files.read("p1", "bar-scene-plan.md") == "second"
    assert files.list_names("p1") == ["bar-scene-plan.md"]


def test_only_the_first_plan_reports_a_born_file(tmp_path):
    # The card says a file came into being. A second write changes one that was already there --
    # the same rule edit_file follows.
    files = _files(tmp_path)
    born = run_tool(files, "p1", "write_plan", json.dumps({"name": "a", "content": "x"}))
    again = run_tool(files, "p1", "write_plan", json.dumps({"name": "a", "content": "y"}))
    assert born.created == "a-plan.md"
    assert again.created is None


def test_an_unknown_tool_does_not_bring_the_loop_down(tmp_path):
    assert "no tool called" in run_tool(_files(tmp_path), "p1", "delete_everything", "{}").text


def test_broken_arguments_are_answered_not_raised(tmp_path):
    assert "not valid JSON" in run_tool(_files(tmp_path), "p1", "read_file", "{oops").text


def test_only_creating_reports_a_born_file(tmp_path):
    files = _files(tmp_path)
    created = run_tool(files, "p1", "create_file", json.dumps({"name": "a", "content": "x"}))
    read = run_tool(files, "p1", "read_file", json.dumps({"name": "a.md"}))
    # What the model is told and whether a file was born are two questions, so they travel apart.
    assert created.created == "a.md"
    assert read.created is None


def test_the_build_tool_tells_the_model_it_assembles_frames():
    # The model reads this before it reaches for the tool, so the word has to be the same one the
    # instruction and the structure file use.
    built = next(spec for spec in TOOL_SPECS if spec["function"]["name"] == "build_prompts")
    said = built["function"]["description"].lower()
    assert "frame" in said and "shot" not in said


# --- the schema tool is gone, and the rules ride with the parameters (Madde 172) ------------------
#
# It taught the model the file's shape: the JSON example, which field goes where, how a map is
# written. Maddes 167 to 171 took that shape into the tools -- the model calls a function now -- so
# the schema was teaching a form it is no longer allowed to type. That is m127's list_files mistake,
# and that one cost a trial.
#
# Half of it had to live. The shape became the code's; the tag text is still the model's, and no
# signature can make it leave the quality chain out or put the count in the right entry. That half
# splits by author: what goes into a map entry is Queen's and rides with these six tools; what goes
# into a frame's action is Grok's and rides with write_frame_prompt (Madde 176).

TAG_TOOLS = (
    "add_character",
    "update_character",
    "add_outfit",
    "update_outfit",
    "add_location",
    "update_location",
)


def _rules():
    from backend.features.workspace.domain.tools import SDXL_PROMPT_RULES

    return SDXL_PROMPT_RULES


def test_the_schema_tool_is_gone(tmp_path):
    assert "read_prompt_structure_schema" not in {
        spec["function"]["name"] for spec in TOOL_SPECS
    }
    # And a record written before this madde can still carry the name, so the runner answers rather
    # than crashes -- the road every deleted tool has taken.
    said = run_tool(_files(tmp_path), "p1", "read_prompt_structure_schema", "{}").text
    assert "no tool called" in said


@pytest.mark.parametrize("tool", TAG_TOOLS)
def test_the_rules_ride_with_every_tool_that_takes_tags(tool):
    spec = next(s for s in TOOL_SPECS if s["function"]["name"] == tool)
    assert _rules() in spec["function"]["description"]


def test_the_rules_ride_with_nothing_else():
    # Six copies is what this costs on every request. A seventh, on a tool that writes no tags,
    # would be paid for and read by nobody.
    carrying = {
        spec["function"]["name"]
        for spec in TOOL_SPECS
        if _rules() in spec["function"]["description"]
    }
    assert carrying == set(TAG_TOOLS)


def test_the_rules_put_the_count_in_the_characters_own_entry():
    # Madde 166 inverted the schema's sixth rule: the count used to belong to the frame's people
    # field, and that field is gone. This is the only place the new home is written down.
    said = _rules()
    assert "1girl" in said
    assert "count" in said.lower()


def test_the_rules_keep_solo_out_of_a_character():
    # The count travels with the person; solo does not. The same character stands alone in one frame
    # and beside somebody in the next, so an entry claiming solo is wrong in half of them.
    assert "solo" in _rules()


def test_the_rules_keep_clothes_out_of_a_character_and_name_them_by_the_garment():
    said = _rules()
    assert "clothes" in said.lower() or "clothing" in said.lower()
    # An outfit named after its wearer cannot be worn by the other one, which is the whole reason
    # outfits are their own map.
    assert "garment" in said.lower()


def test_the_rules_keep_people_out_of_a_location():
    said = _rules()
    assert "nobody" in said.lower() or "no people" in said.lower()


def test_the_rules_forbid_a_quality_chain():
    # Code puts it at the front of every prompt, so one written here is printed twice.
    said = _rules()
    assert "quality" in said.lower()
    assert "twice" in said.lower()


def test_the_rules_forbid_an_or():
    # One picture, and an or is a coin it cannot toss.
    said = _rules()
    assert " or " in said
    assert "coin" in said.lower()


def test_the_rules_ask_for_tags_rather_than_sentences():
    said = _rules()
    assert "tags" in said.lower() and "sentence" in said.lower()
    # An article is not a tag: the density is the thing a weak model gets wrong first.
    assert "article" in said.lower()


def test_the_rules_say_nothing_about_a_frames_action():
    # The other half of the schema, and it belongs to whoever writes an action -- write_frame_prompt,
    # in Madde 176. Carried here it would ride on six tools that never write one, six times per
    # request, read by nobody.
    said = _rules().lower()
    assert "action" not in said
    assert "camera" not in said


def test_create_file_no_longer_offers_to_write_a_structure():
    # It used to offer both formats, because for a while it really could write either. Madde 171
    # shut that, and a description still offering .json would be telling the model to make a call
    # that comes back refused -- m127's list_files mistake, which cost a whole trial.
    spec = next(s for s in TOOL_SPECS if s["function"]["name"] == "create_file")
    said = spec["function"]["parameters"]["properties"]["name"]["description"]
    assert ".json" not in said
    # And the way out rides in the tool's own description, where a model choosing between them reads
    # it: not in a skill text a chat may never have selected.
    assert "start_scenario opens those" in spec["function"]["description"]


def test_the_term_structure_file_is_still_anchored_somewhere():
    # The schema tool used to define it, and the model meets the words in several descriptions
    # before any skill text explains them. With that tool gone the definition has to ride with the
    # one tool that brings a structure into being, or a skill-less chat reads a term nothing
    # anchors.
    spec = next(s for s in TOOL_SPECS if s["function"]["name"] == "start_scenario")
    assert "structure file" in spec["function"]["description"]


def test_the_listing_tool_is_gone():
    # Madde 127: the names ride in every request now, so there is nothing left for this tool to
    # answer -- and a tool that is still declared keeps being called. Taking it away is what makes
    # the call impossible rather than merely discouraged.
    assert "list_files" not in {spec["function"]["name"] for spec in TOOL_SPECS}


def test_the_runner_takes_an_engine_and_the_tools_that_do_not_need_one_carry_on(tmp_path):
    # Madde 175. Every tool here answers out of the file store; one of them is about to answer out
    # of a model as well, and the engine has to reach it without the other seventeen noticing.
    files = _with(tmp_path, "plan.md", "one\ntwo")
    answered = run_tool(files, "p1", "read_file", json.dumps({"name": "plan.md"}), engine=object())
    assert answered.outcome == "2 lines"


def test_a_result_carries_no_spending_unless_the_tool_says_so(tmp_path):
    # The field is born here and filled in Madde 176. None rather than zeroes: a tool that spent
    # nothing and a tool that cannot spend are the same thing to the stamp, and neither should add
    # a row of noughts to it.
    files = _with(tmp_path, "plan.md", "one")
    assert run_tool(files, "p1", "read_file", json.dumps({"name": "plan.md"})).spent is None


def test_the_listing_tool_is_unknown_to_the_runner(tmp_path):
    # The other half: a record written before this madde can still carry the name, and the turn
    # that replays it must get an answer rather than a crash.
    assert "no tool called" in run_tool(_files(tmp_path), "p1", "list_files", "{}").text


def test_every_tool_is_declared_to_the_model():
    assert {spec["function"]["name"] for spec in TOOL_SPECS} == {
        "read_file",
        "create_file",
        "edit_file",
        "build_prompts",
        # Sixth since Madde 91, and declared here with the rest: which modes offer it is a separate
        # question, asked in modes.py.
        "write_plan",
        # Madde 98: the same joining, one character at a time, so a character can be
        # looked at before it enters a frame.
        "build_character_prompts",
        # Madde 128 for the position -- the end of a list is something code knows, so the model
        # never quotes a frame back to reach it -- and Madde 173 for the frame itself: the fields
        # are in the signature, and every name in them is looked for in the maps before it lands.
        "add_scene",
        # Madde 167. create_file writes a document, this writes a structure -- and it takes no
        # content, because the shape is the code's. It has to exist before Madde 171 shuts .json to
        # create_file, or the model would be left with no way to start a scenario at all.
        "start_scenario",
        # Madde 168. Three rather than one: add refuses a name that is there, update refuses one
        # that is not, and remove refuses while a frame stands on it. Overwriting in silence is not
        # a thing the signatures allow.
        "add_character",
        "update_character",
        "remove_character",
        # Madde 169. The same three over a second map. What is not the same is everything touching
        # a frame: an outfit lives inside a character's list, and it is worn rather than present.
        "add_outfit",
        "update_outfit",
        "remove_outfit",
        # Madde 170. The third and narrowest map: a frame names its place in a field of its own,
        # there is one of it, and it is always a plain string.
        "add_location",
        "update_location",
        "remove_location",
        # Madde 174. The frame's own two, which complete the three every map has. Between 171 and
        # here a frame already in the file could not be touched at all.
        "update_frame",
        "remove_frame",
        # Madde 176. The one tool that answers out of a model rather than out of the file store:
        # the border between the agent that builds a scenario and the model that writes its
        # sentences.
        "write_frame_prompt",
    }


# --- the reads the descriptions used to demand (Madde 125) ---------------------------------------
#
# Madde 107 told the base never to read back your own writing, and the trial that followed did it
# anyway -- because these two descriptions ride inside the very call the model is about to make and
# ordered it in so many words. A rule the tool contradicts is a rule the tool wins.


def _said_by(tool):
    return next(spec for spec in TOOL_SPECS if spec["function"]["name"] == tool)["function"][
        "description"
    ]


def test_the_edit_tool_asks_for_a_read_only_when_the_turn_has_not_seen_the_file():
    said = _said_by("edit_file")
    assert "if this turn has not seen it" in said
    assert "already in front of you" in said
    # The unconditional order, which is what produced create_file -> read_file -> edit_file.
    assert "so read the file first" not in said


def test_the_plan_tool_does_not_demand_a_read_of_what_the_turn_just_wrote():
    # One step closing cost three plan writes in the trial: write_plan, edit_file, write_plan.
    said = _said_by("write_plan")
    assert "if this turn has not seen it" in said
    assert "so read it first" not in said


def test_write_plan_ends_only_the_turn_that_was_asked_to_plan():
    # Madde 103. The server ends the turn after write_plan in plan mode alone (Madde 97), and the
    # flow writes a plan as its first step and asks its first question in the same turn. The model
    # never sees the mode, so the description binds the ending to the ask instead: a turn asked
    # only to plan ends, a plan that is step one of a larger job carries on.
    plan = next(spec for spec in TOOL_SPECS if spec["function"]["name"] == "write_plan")
    said = plan["function"]["description"]
    assert "asked only to plan" in said
    assert "carry on" in said


def test_the_round_limit_carries_the_longest_chain():
    # list, read, a skeleton, several batches of frames, a self-check and the build. Pinned,
    # because a limit that quietly cuts the chain short looks like a model that gave up.
    assert MAX_ROUNDS == 16


def test_editing_changes_the_one_match_and_leaves_the_rest(tmp_path):
    files = _with(tmp_path, "plan.md", "alpha\nbeta\ngamma")
    assert "plan.md" in _call(files, "edit_file", name="plan.md", old="beta", new="BETA")
    assert files.read("p1", "plan.md") == "alpha\nBETA\ngamma"


def test_an_edit_can_take_text_out(tmp_path):
    files = _with(tmp_path, "plan.md", "alpha, beta")
    _call(files, "edit_file", name="plan.md", old=", beta", new="")
    assert files.read("p1", "plan.md") == "alpha"


def test_editing_a_file_that_is_not_there_is_an_answer_not_a_crash(tmp_path):
    said = _call(_files(tmp_path), "edit_file", name="ghost.md", old="a", new="b")
    assert "no file by that name" in said


def test_an_edit_with_nothing_to_replace_is_refused(tmp_path):
    files = _with(tmp_path, "plan.md", "alpha")
    assert "text to replace" in _call(files, "edit_file", name="plan.md", old="", new="x")
    assert files.read("p1", "plan.md") == "alpha"


def test_text_that_is_not_in_the_file_changes_nothing(tmp_path):
    files = _with(tmp_path, "plan.md", "alpha")
    assert "not in plan.md" in _call(files, "edit_file", name="plan.md", old="beta", new="x")
    assert files.read("p1", "plan.md") == "alpha"


def test_text_that_appears_twice_is_refused_and_says_how_many(tmp_path):
    files = _with(tmp_path, "plan.md", "beta and beta")
    # Uniqueness is the safety: with two matches, which one was meant is a guess.
    assert "2 times" in _call(files, "edit_file", name="plan.md", old="beta", new="x")
    assert files.read("p1", "plan.md") == "beta and beta"


def test_an_edit_does_not_report_a_born_file(tmp_path):
    files = _with(tmp_path, "plan.md", "alpha")
    edited = run_tool(files, "p1", "edit_file", json.dumps({"name": "plan.md", "old": "a", "new": "b"}))
    assert edited.created is None


def test_building_writes_a_file_named_after_the_source(tmp_path):
    files = _with(tmp_path, "intro-frames.json", STRUCTURE)
    said = _call(files, "build_prompts", name="intro-frames.json")
    assert "intro-frames.py" in said and "2" in said
    assert "PROMPTS" in files.read("p1", "intro-frames.py")
    assert "long teal hair" in files.read("p1", "intro-frames.py")


def test_building_reports_a_born_file(tmp_path):
    files = _with(tmp_path, "intro-frames.json", STRUCTURE)
    built = run_tool(files, "p1", "build_prompts", json.dumps({"name": "intro-frames.json"}))
    assert built.created == "intro-frames.py"


def test_trying_a_character_writes_a_file_named_after_both(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "build_character_prompts", name="scene.json", character="aylin")
    assert "scene-aylin.py" in files.list_names("p1")


def test_trying_a_character_reports_a_born_file(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    result = run_tool(
        files,
        "p1",
        "build_character_prompts",
        json.dumps({"name": "scene.json", "character": "aylin"}),
    )
    assert result.created == "scene-aylin.py"


def test_trying_a_character_nobody_knows_writes_nothing(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    said = _call(files, "build_character_prompts", name="scene.json", character="ghost")
    assert "ghost" in said
    assert files.list_names("p1") == ["scene.json"]


def test_a_character_try_says_how_many_prompts_it_wrote(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    result = run_tool(
        files,
        "p1",
        "build_character_prompts",
        json.dumps({"name": "scene.json", "character": "aylin"}),
    )
    # One outfit in this structure, so the singular is the answer -- counted() decides that.
    assert result.outcome == "1 prompt"


def test_building_again_writes_over_its_own_output(tmp_path):
    files = _with(tmp_path, "intro-frames.json", STRUCTURE)
    _call(files, "build_prompts", name="intro-frames.json")
    # Through the map tool since Madde 171: the structure is no longer changed as text, and this
    # test was reaching for the door that closed. The claim it makes is untouched -- what changes is
    # the only way left to change a character.
    _call(
        files,
        "update_character",
        file="intro-frames.json",
        name="aylin",
        tags="1girl, short red hair",
    )
    _call(files, "build_prompts", name="intro-frames.json")
    # A derived file: regenerating it is the point, so numbering would only hide which one is now.
    assert sorted(files.list_names("p1")) == ["intro-frames.json", "intro-frames.py"]
    assert "teal" not in files.read("p1", "intro-frames.py")


def test_building_from_a_file_that_is_not_there_is_an_answer(tmp_path):
    assert "no file by that name" in _call(_files(tmp_path), "build_prompts", name="ghost.json")


def test_broken_json_is_reported_in_the_parsers_own_words(tmp_path):
    files = _with(tmp_path, "frames.json", "{oops")
    said = _call(files, "build_prompts", name="frames.json")
    # Never a guessed cause: whatever the parser said is what the model is told.
    assert "frames.json" in said and "Expecting" in said
    assert files.list_names("p1") == ["frames.json"]


def test_an_unknown_name_writes_no_file(tmp_path):
    broken = STRUCTURE.replace('{"aylin": ["gecelik"]}', '{"aylinn": ["gecelik"]}', 1)
    files = _with(tmp_path, "frames.json", broken)
    said = _call(files, "build_prompts", name="frames.json")
    assert "aylinn" in said and "aylin" in said
    assert files.list_names("p1") == ["frames.json"]


def test_a_python_source_is_refused_so_it_is_not_written_over(tmp_path):
    files = _with(tmp_path, "frames.py", STRUCTURE)
    assert "frames.py" in _call(files, "build_prompts", name="frames.py")
    assert files.read("p1", "frames.py") == STRUCTURE


# --- what a call reports about itself (Madde 66) -------------------------------------------------
#
# The chat draws a line per call, and the line needs the file the call was about. The name is asked
# for here rather than worked out by the caller: cleaning a name and settling a clash are this
# module's rules, and a second copy of them would drift on the first change to either.


def _target(files, tool, **arguments):
    return run_tool(files, "p1", tool, json.dumps(arguments)).target


def test_a_read_reports_the_cleaned_name_rather_than_the_asked_one(tmp_path):
    files = _with(tmp_path, "plan.md", "body")
    assert _target(files, "read_file", name="notes/plan.md") == "plan.md"


def test_a_call_about_no_file_has_no_target_to_report(tmp_path):
    # Empty rather than invented: the call really is about nothing in particular. Asked of an
    # unknown name since Madde 172 took the last argument-free tool away.
    assert _target(_files(tmp_path), "read_prompt_structure_schema") == ""


def test_an_edit_reports_the_file_it_changed(tmp_path):
    files = _with(tmp_path, "plan.md", "one two")
    assert _target(files, "edit_file", name="plan.md", old="one", new="1") == "plan.md"


def test_a_build_reports_the_structure_it_built_from(tmp_path):
    # The source rather than the output: the file card already names what was written, and the line
    # saying the same thing twice would carry nothing.
    files = _with(tmp_path, "frames.json", STRUCTURE)
    assert _target(files, "build_prompts", name="frames.json") == "frames.json"


def test_a_call_that_missed_still_reports_its_target(tmp_path):
    # A miss is a step that happened. Whether it succeeded is the answer's story, not the line's.
    assert _target(_files(tmp_path), "read_file", name="gone.md") == "gone.md"


# --- how the call went, in a few words (Madde 78) ------------------------------------------------
#
# The line under the call. Written by the tool because the tool is what knows, and never the result
# itself: what a read returned is the file, and that is already on disk.


def _outcome(files, tool, **arguments):
    return run_tool(files, "p1", tool, json.dumps(arguments)).outcome


def test_reading_says_how_much_was_read(tmp_path):
    files = _with(tmp_path, "plan.md", "one\ntwo\nthree")
    assert _outcome(files, "read_file", name="plan.md") == "3 lines"


def test_creating_says_it_was_saved(tmp_path):
    # Not the name: the line above already carries it, and a second copy would go stale on the
    # first change to either.
    assert _outcome(_files(tmp_path), "create_file", name="plan.md", content="a") == "Saved"


def test_an_edit_says_it_changed_the_file(tmp_path):
    files = _with(tmp_path, "plan.md", "one two")
    assert _outcome(files, "edit_file", name="plan.md", old="one", new="1") == "Edited"


def test_a_build_says_how_many_prompts_it_wrote(tmp_path):
    files = _with(tmp_path, "frames.json", STRUCTURE)
    assert _outcome(files, "build_prompts", name="frames.json") == "2 prompts"


def test_a_call_that_was_refused_says_why(tmp_path):
    # Reading a file that is not there is something the turn really did, and hiding it would make
    # the record read as though the answer had what it asked for.
    assert _outcome(_files(tmp_path), "read_file", name="gone.md") == "No file by that name"


# --- a read opens a file rather than printing it (Madde 179) --------------------------------------
#
# Madde 129 killed a staleness: a read's result froze where it was written while the file moved on,
# so the model read the same file three times in one trial. The box holds names and reads the
# contents from disk, and there is one entry that cannot go stale.
#
# Inside a single turn it survived. The tool answered with the whole file, and that answer sits in
# the conversation until the turn ends -- so every round after a read carried the file twice: once
# frozen in the conversation, once fresh in the box. A file edited in the same turn made the two
# disagree, and the model had to decide which of them to believe.
#
# The line numbers of Madde 131 stay. They moved with the contents: the box is the one place a file
# is shown now, so its numbers are the only ones there are.


def test_a_read_hands_back_a_receipt_rather_than_the_file(tmp_path):
    files = _with(tmp_path, "plan.md", "alpha\nbeta\ngamma")
    assert _call(files, "read_file", name="plan.md") == (
        "plan.md, 3 lines; it is in your opened files."
    )


def test_what_was_read_is_not_in_the_answer(tmp_path):
    # The whole item in one line. Left here, this copy rides every later round of the turn beside
    # the box's own, and the two part company the moment anything writes to the file.
    files = _with(tmp_path, "plan.md", "alpha\nbeta\ngamma")
    assert "alpha" not in _call(files, "read_file", name="plan.md")


def test_a_file_that_is_not_there_still_says_so(tmp_path):
    # Unchanged, and it has to be: files_opened skips a read that missed, so this sentence is what
    # keeps a name out of the box (context_box._MISSED).
    assert _call(_files(tmp_path), "read_file", name="ghost.md") == "There is no file by that name."


def test_the_outcome_still_counts_the_lines_it_read(tmp_path):
    # A guard: the card counts the file's lines, which is now also what the answer says.
    files = _with(tmp_path, "plan.md", "alpha\nbeta\ngamma")
    assert _outcome(files, "read_file", name="plan.md") == "3 lines"


def test_a_file_is_still_shown_with_numbered_lines():
    # Madde 131, asked of the function rather than of the tool: the anchor an edit takes has to
    # occur exactly once, and the model was judging that by eye over an unnumbered wall of
    # near-identical frames. It judged wrong, _edit answered "appears 3 times", and the retry cost
    # a round.
    assert numbered("alpha\nbeta\ngamma") == "     1\talpha\n     2\tbeta\n     3\tgamma"


def test_the_numbers_are_right_aligned_so_the_text_starts_in_one_column():
    # Padding rather than a bare number: left-aligned, the text would step right at line 10 and the
    # model would be reading a ragged edge for the rest of the file.
    lines = numbered("\n".join(str(n) for n in range(1, 11))).splitlines()
    assert lines[8] == "     9\t9"
    assert lines[9] == "    10\t10"
    assert lines[8].index("\t") == lines[9].index("\t")


def test_an_empty_file_shows_as_nothing_rather_than_a_first_line():
    # A lone "1" would put a line in front of the model that the file does not have, and an edit
    # anchored on nothing is the next thing that happens.
    assert numbered("") == ""


def test_an_edit_matches_the_disk_and_not_the_numbered_view(tmp_path):
    # A guard on the seam: what the model is shown carries a column the file does not have, and
    # matching against the shown form would edit a file nobody has.
    files = _with(tmp_path, "plan.md", "alpha\nbeta")
    assert "not in plan.md" in _call(files, "edit_file", name="plan.md", old="     2\tbeta", new="x")
    assert "Edited plan.md" in _call(files, "edit_file", name="plan.md", old="beta", new="delta")
    assert files.read("p1", "plan.md") == "alpha\ndelta"


def test_the_edit_tool_tells_the_model_to_drop_the_numbers():
    # The bridge between a numbered read and an unnumbered match lives in the description, not in
    # the code -- the same place Claude Code's Edit puts it.
    said = _said_by("edit_file")
    assert "without the line numbers" in said


# --- an edit that can take every match (Madde 132) ------------------------------------------------
#
# A repeating anchor left one way out: grow it and start again, which is a whole round and a fatter
# anchor. Claude Code offers the other one -- "or sets replace_all: true to replace them all" -- and
# the job it is for is already in the run: a map entry's name repeats through every frame that
# calls on it (Madde 113). The refusal stays the default, because replacing more than was meant is
# the user's file quietly saying something else (FOUNDATION 1).


def test_replace_all_changes_every_occurrence(tmp_path):
    files = _with(tmp_path, "plan.md", "aylin here, aylin there, aylin everywhere")
    _call(files, "edit_file", name="plan.md", old="aylin", new="deniz", replace_all=True)
    assert files.read("p1", "plan.md") == "deniz here, deniz there, deniz everywhere"


def test_replace_all_says_how_many_places_it_changed(tmp_path):
    # The model learns the count from the answer rather than by reading the file back, which is the
    # habit Madde 129 and 131 have been taking away one reason at a time.
    files = _with(tmp_path, "plan.md", "one one one")
    assert _outcome(files, "edit_file", name="plan.md", old="one", new="two", replace_all=True) == (
        "Edited 3 places"
    )


def test_the_flag_on_a_single_occurrence_reads_like_an_ordinary_edit(tmp_path):
    # A guard: asking for all of something there is one of is not a different event, and a card
    # saying "1 place" would make it look like one.
    files = _with(tmp_path, "plan.md", "only here")
    assert _outcome(files, "edit_file", name="plan.md", old="only", new="just", replace_all=True) == (
        "Edited"
    )


def test_without_the_flag_a_text_that_repeats_is_still_refused(tmp_path):
    # A guard, and the decision itself: the default stays the refusal.
    files = _with(tmp_path, "plan.md", "one one one")
    assert "appears 3 times" in _call(files, "edit_file", name="plan.md", old="one", new="two")
    assert files.read("p1", "plan.md") == "one one one"


def test_the_flag_does_not_rescue_a_text_that_is_not_there(tmp_path):
    # A guard: the flag multiplies a match, it does not conjure one.
    files = _with(tmp_path, "plan.md", "one one one")
    answer = _call(files, "edit_file", name="plan.md", old="seven", new="two", replace_all=True)
    assert "not in plan.md" in answer


def test_the_edit_tool_takes_the_flag_as_a_parameter():
    spec = next(s for s in TOOL_SPECS if s["function"]["name"] == "edit_file")
    flag = spec["function"]["parameters"]["properties"]["replace_all"]
    assert flag["type"] == "boolean"
    # Not required: the default is the refusal, and a required flag would make the model state an
    # intent on every ordinary edit.
    assert "replace_all" not in spec["function"]["parameters"]["required"]


def test_the_edit_tool_tells_the_model_the_flag_is_there():
    # A parameter the description never mentions is a parameter a weak model does not reach for --
    # 108 and 118 both showed it going around what it was not shown.
    said = _said_by("edit_file")
    assert "replace_all" in said


# --- a frame is born with its scene and its cast (Madde 173) --------------------------------------
#
# Madde 128 took the position out of the model's hands: appending to a JSON list is not an append,
# and edit_file made it quote the previous frame back word for word to reach the end. That much
# holds. What did not is the frame itself -- add_frames took a list of objects and looked inside
# none of them, so a frame naming a character nobody had written reached the disk in silence and
# surfaced rounds later, in build_prompts, as a miss in a file nobody was editing any more. The
# shape was something the model had to know, and since Madde 172 there is nowhere left to learn it.
#
# add_scene puts the fields in the signature: the model knows a tool's signature, never the file's
# shape. Every name it is handed is looked for in the maps before anything at all is written.

SCENE = {
    "scene": "she turns her head",
    "characters": {"aylin": ["gecelik"]},
    "location": "bedroom",
}


def test_add_scene_appends_to_the_end_of_the_frames_list(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "add_scene", file="scene.json", scenes=[SCENE])
    frames = json.loads(files.read("p1", "scene.json"))["frames"]
    assert len(frames) == 3
    assert frames[2]["scene"] == "she turns her head"
    # The two that were there stay where they were: the built list runs in the frames' order.
    assert [frame["action"] for frame in frames[:2]] == ["one", "two"]


def test_add_scene_gives_each_frame_the_number_of_its_place(tmp_path):
    # The place rather than a counter. build_prompts and _frames_naming already count frames by
    # where they sit, and a second source of truth would part from this one on the first removal.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "add_scene", file="scene.json", scenes=[SCENE, SCENE])
    frames = json.loads(files.read("p1", "scene.json"))["frames"]
    assert [frame["number"] for frame in frames[2:]] == [3, 4]


def test_add_scene_says_which_frames_it_made(tmp_path):
    # The numbers rather than a total: the model's next move is write_frame_prompt on each of them,
    # and a count would send it reading the file back to learn what to name.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    assert _call(files, "add_scene", file="scene.json", scenes=[SCENE, SCENE, SCENE]) == (
        "Added 3 scenes to scene.json as frames 3-5."
    )


def test_one_scene_is_one_frame_and_the_answer_reads_like_one(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    assert _call(files, "add_scene", file="scene.json", scenes=[SCENE]) == (
        "Added 1 scene to scene.json as frame 3."
    )


def test_add_scene_counts_the_scenes_on_the_card(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    assert _outcome(files, "add_scene", file="scene.json", scenes=[SCENE]) == "1 scene"


def test_add_scene_writes_the_three_fields_and_no_action(tmp_path):
    # The action is Madde 176's, and the prompt model writes it. A frame born without one is not
    # broken but half finished -- where an empty string would read as an action somebody wrote.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "add_scene", file="scene.json", scenes=[SCENE])
    born = json.loads(files.read("p1", "scene.json"))["frames"][2]
    assert born["scene"] == "she turns her head"
    assert born["characters"] == {"aylin": ["gecelik"]}
    assert born["location"] == "bedroom"
    assert "action" not in born


def test_a_scene_with_nothing_but_its_sentence_is_a_frame(tmp_path):
    # The user's decision of 5 Sep: a landscape has no cast, and a close-up may name no place. A
    # field that was not given is left out rather than emptied -- build_prompts drops an empty
    # location, but a key sitting there says somebody chose it.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    answer = _call(files, "add_scene", file="scene.json", scenes=[{"scene": "the empty room"}])
    born = json.loads(files.read("p1", "scene.json"))["frames"][2]
    assert born == {"number": 3, "scene": "the empty room"}
    assert "Added 1 scene" in answer


def test_one_outfit_written_without_its_list_is_written_down_as_a_list(tmp_path):
    # cast_of forgives this slip on the way out, so it is forgiven on the way in too -- and
    # straightened as it lands. Reading puts up with two shapes because both are already on disk;
    # writing has no such excuse, and the tool picks which one the file gets.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(
        files,
        "add_scene",
        file="scene.json",
        scenes=[{"scene": "s", "characters": {"aylin": "gecelik"}}],
    )
    born = json.loads(files.read("p1", "scene.json"))["frames"][2]
    assert born["characters"] == {"aylin": ["gecelik"]}


def test_add_scene_writes_readable_turkish_rather_than_escapes(tmp_path):
    # The user opens this file and fixes it by hand, and a wall of ı is a file they cannot
    # read. Their work is the first principle, and it includes being able to see it.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "add_scene", file="scene.json", scenes=[{"scene": "başını çeviriyor"}])
    assert "başını çeviriyor" in files.read("p1", "scene.json")


def test_add_scene_leaves_the_maps_alone(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "add_scene", file="scene.json", scenes=[SCENE])
    after = json.loads(files.read("p1", "scene.json"))
    before = json.loads(STRUCTURE)
    # The work happened first: without this the loop below passes on a file nothing touched.
    assert len(after["frames"]) == 3
    for key in ("characters", "outfits", "locations"):
        assert after[key] == before[key]


def test_add_scene_brings_no_file_into_being(tmp_path):
    # No card: the file was already there. The rule edit_file follows.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    added = run_tool(
        files, "p1", "add_scene", json.dumps({"file": "scene.json", "scenes": [SCENE]})
    )
    # The work first: created is None for a tool that did nothing at all, so without this the test
    # is green on the day add_scene stops existing.
    assert len(json.loads(files.read("p1", "scene.json"))["frames"]) == 3
    assert added.created is None


def test_a_frame_add_scene_wrote_is_a_frame_build_prompts_can_build(tmp_path):
    # The two halves of one shape, put together in the only place that can see both. A tool writing
    # a frame the builder cannot read would pass every test above and fail in front of the user.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "add_scene", file="scene.json", scenes=[SCENE])
    assert "3 prompts" in _call(files, "build_prompts", name="scene.json")


def test_add_scene_refuses_a_character_nobody_wrote(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    answer = _call(
        files,
        "add_scene",
        file="scene.json",
        scenes=[{"scene": "s", "characters": {"deniz": []}}],
    )
    assert "frame 3: deniz is not in characters; known: aylin." in answer
    assert files.read("p1", "scene.json") == STRUCTURE


def test_add_scene_refuses_an_outfit_nobody_wrote(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    answer = _call(
        files,
        "add_scene",
        file="scene.json",
        scenes=[{"scene": "s", "characters": {"aylin": ["palto"]}}],
    )
    assert "frame 3: palto is not in outfits; known: gecelik." in answer
    assert files.read("p1", "scene.json") == STRUCTURE


def test_add_scene_refuses_a_place_nobody_wrote(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    answer = _call(files, "add_scene", file="scene.json", scenes=[{"scene": "s", "location": "bar"}])
    assert "frame 3: bar is not in locations; known: bedroom." in answer
    assert files.read("p1", "scene.json") == STRUCTURE


def test_every_name_nobody_knows_comes_back_at_once(tmp_path):
    # build_prompts' rule, one step earlier: one pass fixes them all. Answering with the first miss
    # would spend a round on each of them, and every one of those rounds carries the whole chat.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    answer = _call(
        files,
        "add_scene",
        file="scene.json",
        scenes=[
            {"scene": "s", "characters": {"deniz": []}},
            {"scene": "s", "location": "bar"},
        ],
    )
    assert "frame 3: deniz is not in characters" in answer
    assert "frame 4: bar is not in locations" in answer
    # Neither of them landed, not even the frame whose own names were all fine.
    assert "Nothing was added." in answer
    assert files.read("p1", "scene.json") == STRUCTURE


def test_a_scene_needs_its_sentence(tmp_path):
    # The one field that is required. A frame with a cast and no scene is a frame the prompt model
    # has nothing to write from, and Madde 176 would refuse it one round later.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    answer = _call(
        files, "add_scene", file="scene.json", scenes=[{"characters": {"aylin": []}}]
    )
    assert "frame 3: a scene needs a sentence saying what happens." in answer
    # Blank is the same as missing: a space is not a brief.
    assert "frame 3: a scene needs" in _call(
        files, "add_scene", file="scene.json", scenes=[{"scene": "   "}]
    )
    assert files.read("p1", "scene.json") == STRUCTURE


def test_a_cast_that_is_not_a_map_is_refused_with_the_shape_it_wanted(tmp_path):
    # The run's rule: a wrong shape is refused with a sentence saying what was expected. A plain
    # list of names is what files written before outfits carry and reading still forgives it --
    # but nothing new is written in a shape that cannot say who is wearing what.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    answer = _call(
        files, "add_scene", file="scene.json", scenes=[{"scene": "s", "characters": ["aylin"]}]
    )
    assert "frame 3: characters is a map from a name to the outfits they wear." in answer
    assert files.read("p1", "scene.json") == STRUCTURE


def test_a_scene_that_is_not_an_object_is_one_problem_rather_than_four(tmp_path):
    # Nothing can be looked for inside it, so it says so once and the walk moves on. Counting the
    # same mistake four times would bury whatever else in the batch is genuinely wrong.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    answer = _call(files, "add_scene", file="scene.json", scenes=["she turns her head"])
    assert "a scene is an object with scene, characters and location." in answer
    assert answer.count("frame 3") == 1


def test_add_scene_refuses_a_scenes_argument_that_is_not_a_list(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    assert "list of scenes" in _call(files, "add_scene", file="scene.json", scenes=SCENE)
    assert files.read("p1", "scene.json") == STRUCTURE


def test_adding_no_scenes_writes_nothing(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    assert "unchanged" in _call(files, "add_scene", file="scene.json", scenes=[])
    assert files.read("p1", "scene.json") == STRUCTURE


def test_add_scene_refuses_a_file_that_is_not_there(tmp_path):
    assert "no file by that name" in _call(
        _files(tmp_path), "add_scene", file="ghost.json", scenes=[SCENE]
    )


def test_add_scene_carries_the_parsers_own_sentence_when_the_json_is_broken(tmp_path):
    # A guessed cause would send the model looking in the wrong place -- _build's rule.
    files = _with(tmp_path, "scene.json", "{ not json")
    answer = _call(files, "add_scene", file="scene.json", scenes=[SCENE])
    assert "not valid JSON" in answer
    assert "Expecting" in answer


def test_add_scene_refuses_a_structure_with_no_frames_list(tmp_path):
    files = _with(tmp_path, "scene.json", json.dumps({"characters": {"aylin": "1girl"}}))
    assert "no frames list" in _call(files, "add_scene", file="scene.json", scenes=[SCENE])


def test_only_the_sentence_is_required_of_a_scene():
    # The user's decision of 5 Sep, in the one place the model reads it. Requiring a cast would
    # make a landscape impossible to write, and requiring a place would do it to a close-up.
    spec = next(s for s in TOOL_SPECS if s["function"]["name"] == "add_scene")
    assert spec["function"]["parameters"]["properties"]["scenes"]["items"]["required"] == ["scene"]


def test_add_frames_is_no_longer_a_tool(tmp_path):
    # The road every deleted tool goes down: a record written before this madde can still name it,
    # and the turn that replays it has to get an answer rather than a crash.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    assert "no tool called add_frames" in run_tool(
        files, "p1", "add_frames", json.dumps({"name": "scene.json", "frames": [SCENE]})
    ).text


# --- changing a frame and taking one out (Madde 174) ----------------------------------------------
#
# 171 shut .json to edit_file and 173 retired add_frames, which between them left a gap: a frame
# already in the file could not be touched at all. The model wanting the third frame's place fixed
# had one move left -- build the scenario again.
#
# The three tools a map has, now over frames. What update_frame will not touch is the action: that
# is Madde 176's field, written by the prompt model, and a hand-written one here would be the way
# round the quality gate. Nor the number, which is the frame's place -- and the only thing that
# moves a place is a removal, which is why remove_frame renumbers what is left.

WITH_ACTION = json.dumps(
    {
        "characters": {"aylin": "1girl, long teal hair"},
        "outfits": {"gecelik": "white nightgown", "palto": "long coat"},
        "locations": {"bedroom": "sunlit bedroom", "balcony": "night balcony"},
        "frames": [
            {"number": 1, "scene": "one", "characters": {"aylin": ["gecelik"]}, "location": "bedroom"},
            {
                "number": 2,
                "scene": "two",
                "characters": {"aylin": ["gecelik"]},
                "location": "bedroom",
                "action": "she turns her head, close-up",
            },
            {"number": 3, "scene": "three", "location": "bedroom"},
        ],
    },
    indent=2,
)


def _frames(files):
    return json.loads(files.read("p1", "scene.json"))["frames"]


def test_update_frame_changes_the_scene_and_leaves_the_rest_where_it_was(tmp_path):
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    _call(files, "update_frame", file="scene.json", frame=1, scene="she wakes")
    changed = _frames(files)[0]
    assert changed["scene"] == "she wakes"
    assert changed["characters"] == {"aylin": ["gecelik"]}
    assert changed["location"] == "bedroom"


def test_update_frame_changes_the_cast(tmp_path):
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    _call(files, "update_frame", file="scene.json", frame=1, characters={"aylin": ["palto"]})
    assert _frames(files)[0]["characters"] == {"aylin": ["palto"]}
    assert _frames(files)[0]["scene"] == "one"


def test_update_frame_changes_the_place(tmp_path):
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    _call(files, "update_frame", file="scene.json", frame=1, location="balcony")
    assert _frames(files)[0]["location"] == "balcony"


def test_update_frame_changes_several_fields_in_one_call(tmp_path):
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    _call(files, "update_frame", file="scene.json", frame=1, scene="she wakes", location="balcony")
    changed = _frames(files)[0]
    assert (changed["scene"], changed["location"]) == ("she wakes", "balcony")


def test_update_frame_does_not_touch_the_action(tmp_path):
    # Madde 176's field, and the whole point of it is that a model with a restriction did not write
    # it. A hand-written action here would be the way round the tool that exists to write one.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    _call(files, "update_frame", file="scene.json", frame=2, scene="she looks away")
    changed = _frames(files)[1]
    assert changed["scene"] == "she looks away"
    assert changed["action"] == "she turns her head, close-up"


def test_update_frame_keeps_the_frames_number(tmp_path):
    # The number is the frame's place, and an update moves nothing.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    _call(files, "update_frame", file="scene.json", frame=2, scene="she looks away")
    # The work first: the numbers are already 1, 2, 3 on disk, so without this the test is green
    # on a call that did nothing at all.
    assert _frames(files)[1]["scene"] == "she looks away"
    assert [frame["number"] for frame in _frames(files)] == [1, 2, 3]


def test_update_frame_names_what_it_changed(tmp_path):
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    assert _call(
        files, "update_frame", file="scene.json", frame=1, scene="she wakes", location="balcony"
    ) == "Changed scene and location of frame 1 in scene.json."


def test_an_empty_place_takes_the_field_off_the_frame(tmp_path):
    # A frame that shows no place of its own is a frame written without the field (Madde 173), so
    # clearing one has to arrive at the same shape: two roads to one frame, or the file grows two
    # ways of saying nothing.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    _call(files, "update_frame", file="scene.json", frame=1, location="")
    assert "location" not in _frames(files)[0]
    assert _frames(files)[0]["scene"] == "one"


def test_an_empty_cast_takes_the_field_off_the_frame(tmp_path):
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    _call(files, "update_frame", file="scene.json", frame=1, characters={})
    assert "characters" not in _frames(files)[0]


def test_update_frame_straightens_a_lone_outfit_the_way_add_scene_does(tmp_path):
    # Both roads write the same shape, or a frame born one way and changed the other holds two.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    _call(files, "update_frame", file="scene.json", frame=1, characters={"aylin": "palto"})
    assert _frames(files)[0]["characters"] == {"aylin": ["palto"]}


def test_update_frame_refuses_when_nothing_was_given(tmp_path):
    # No silent success: a model told nothing happened moves on believing it did. _update_entry's
    # sentence, one level along.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    assert "Nothing was given to change about frame 1." in _call(
        files, "update_frame", file="scene.json", frame=1
    )


def test_update_frame_refuses_a_frame_that_is_not_there(tmp_path):
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    assert "scene.json has 3 frames; there is no frame 9." in _call(
        files, "update_frame", file="scene.json", frame=9, scene="s"
    )


def test_a_frame_is_named_by_its_number(tmp_path):
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    assert "counting from 1" in _call(
        files, "update_frame", file="scene.json", frame="the last one", scene="s"
    )
    # Zero and below are not places in a list the model counts from 1.
    assert "counting from 1" in _call(files, "update_frame", file="scene.json", frame=0, scene="s")
    # True is an int in Python, and taking it would quietly mean frame 1.
    assert "counting from 1" in _call(
        files, "update_frame", file="scene.json", frame=True, scene="s"
    )


def test_a_number_written_as_a_string_is_forgiven(tmp_path):
    # 173's lone outfit, again: a small slip costs a round to send back, and there is exactly one
    # thing "3" can mean here.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    _call(files, "update_frame", file="scene.json", frame="3", scene="she leaves")
    assert _frames(files)[2]["scene"] == "she leaves"


def test_update_frame_refuses_a_name_nobody_wrote(tmp_path):
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    answer = _call(files, "update_frame", file="scene.json", frame=1, location="bar")
    assert "frame 1: bar is not in locations; known: balcony, bedroom." in answer
    assert _frames(files)[0]["location"] == "bedroom"


def test_update_frame_refuses_a_cast_that_is_not_a_map(tmp_path):
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    answer = _call(files, "update_frame", file="scene.json", frame=1, characters=["aylin"])
    assert "frame 1: characters is a map from a name to the outfits they wear." in answer
    assert _frames(files)[0]["characters"] == {"aylin": ["gecelik"]}


def test_a_frames_scene_cannot_be_emptied(tmp_path):
    # Required at birth, so it cannot be cleared later: the two would leave a frame that add_scene
    # would refuse to write sitting in the file anyway.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    answer = _call(files, "update_frame", file="scene.json", frame=1, scene="   ")
    assert "frame 1: a scene needs a sentence saying what happens." in answer
    assert _frames(files)[0]["scene"] == "one"


def test_update_frame_refuses_a_file_that_is_not_there(tmp_path):
    # The shared road: _opened answers for every tool that opens a structure.
    assert "no file by that name" in _call(
        _files(tmp_path), "update_frame", file="ghost.json", frame=1, scene="s"
    )


def test_remove_frame_takes_the_frame_out(tmp_path):
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    _call(files, "remove_frame", file="scene.json", frame=2)
    assert [frame["scene"] for frame in _frames(files)] == ["one", "three"]


def test_remove_frame_renumbers_what_is_left_from_one(tmp_path):
    # The number is the frame's place, and a removal is the one thing that moves places. A number
    # left where it was would part from build_prompts, which counts frames by where they sit.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    _call(files, "remove_frame", file="scene.json", frame=1)
    assert [frame["number"] for frame in _frames(files)] == [1, 2]
    assert [frame["scene"] for frame in _frames(files)] == ["two", "three"]


def test_remove_frame_says_what_is_left(tmp_path):
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    assert _call(files, "remove_frame", file="scene.json", frame=2) == (
        "Removed frame 2 from scene.json; 2 frames left, renumbered from 1."
    )


def test_removing_the_last_frame_says_nothing_about_renumbering(tmp_path):
    # There is nothing left to renumber, and a sentence saying otherwise is a sentence about work
    # that did not happen.
    files = _with(tmp_path, "scene.json", json.dumps({"frames": [{"number": 1, "scene": "one"}]}))
    assert _call(files, "remove_frame", file="scene.json", frame=1) == (
        "Removed frame 1 from scene.json; no frames left."
    )
    assert _frames(files) == []


def test_remove_frame_refuses_a_frame_that_is_not_there(tmp_path):
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    assert "scene.json has 3 frames; there is no frame 9." in _call(
        files, "remove_frame", file="scene.json", frame=9
    )
    assert len(_frames(files)) == 3


def test_remove_frame_leaves_the_maps_alone(tmp_path):
    # The user's decision of 5 Sep: nothing here deletes on the model's behalf. A character left in
    # no frame at all stays in the map, and removing it is the user's to ask for.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    _call(files, "remove_frame", file="scene.json", frame=1)
    after = json.loads(files.read("p1", "scene.json"))
    before = json.loads(WITH_ACTION)
    assert len(after["frames"]) == 2
    for key in ("characters", "outfits", "locations"):
        assert after[key] == before[key]


def test_a_removal_gives_an_older_files_frames_the_numbers_they_never_had(tmp_path):
    # Frames written before Madde 173 carry no number at all. Renumbering counts places rather than
    # reading what is there, so it repairs them on the way past.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "remove_frame", file="scene.json", frame=1)
    assert [frame["number"] for frame in _frames(files)] == [1]


# --- the frame's action, written by the model that writes those (Madde 176) -----------------------
#
# The whole reason this run is shaped the way it is. The main agent builds the scenario -- who is
# there, what they wear, where, in what order -- and it is good at that and bad at the one sentence
# a frame turns on: its restriction makes it write around the thing rather than at it. The prompt
# model is the other way round, strong on exactly that sentence and unable to carry the rest.
#
# This tool is the whole of the border between them. The main agent says which frame and, if it has
# something to add, why; the prompt model writes the sentence and nothing else. The camera lives in
# that sentence too (the user's decision, 5 Sep): a model splitting one shot across two fields is a
# model doing bookkeeping instead of writing.


class FakeWriter:
    """An engine that only writes once, which is all this tool ever asks of one."""

    def __init__(self, text="she turns her head, close-up", spent=None, blow_up=None):
        self.text = text
        self.spent = spent or {"sent": 120, "cached": 0, "answered": 24}
        self.blow_up = blow_up
        self.system = None
        self.user = None

    def write_once(self, system, user):
        self.system, self.user = system, user
        if self.blow_up:
            raise RuntimeError(self.blow_up)
        return {"text": self.text, "spent": self.spent}


def _wrote(files, engine, **arguments):
    return run_tool(
        files, "p1", "write_frame_prompt", json.dumps(arguments), engine=engine
    )


def test_the_prompt_writers_system_prompt_carries_the_rules_a_map_entry_is_written_by():
    # One text, two readers. Madde 172 put the entry rules beside the tools that take tags; the
    # model writing an action reads the same ones, because it is writing into the same prompt.
    from backend.features.workspace.domain.tools import (
        SDXL_PROMPT_RULES,
        WRITE_FRAME_SYSTEM_PROMPT,
    )

    assert SDXL_PROMPT_RULES in WRITE_FRAME_SYSTEM_PROMPT


def test_the_prompt_writer_is_told_about_the_action_and_the_camera():
    # The other half of the dead schema (Madde 172), and this is where it landed: the half about
    # what happens in a frame and how it is shot, read by the one model that writes it.
    from backend.features.workspace.domain.tools import WRITE_FRAME_SYSTEM_PROMPT

    said = WRITE_FRAME_SYSTEM_PROMPT.lower()
    assert "action" in said
    # Since Madde 166 there is no camera field: the shot is part of the sentence, so the model has
    # to be told that it is.
    assert "camera" in said or "shot" in said


def test_the_prompt_writer_is_not_told_what_queenagent_tells_its_agent():
    # SYSTEM_PROMPT is a page about tools, files, chats and how to talk to a user. The model here
    # has none of those and one sentence to write.
    from backend.features.workspace.domain.prompt import SYSTEM_PROMPT
    from backend.features.workspace.domain.tools import WRITE_FRAME_SYSTEM_PROMPT

    assert SYSTEM_PROMPT not in WRITE_FRAME_SYSTEM_PROMPT


def test_the_writer_is_handed_the_scene_the_cast_and_the_place(tmp_path):
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    writer = FakeWriter()
    _wrote(files, writer, file="scene.json", frame=1)
    said = writer.user
    assert "one" in said                       # the scene sentence, which is the brief
    assert "aylin" in said                     # the name, so a note that uses it can be matched
    assert "1girl, long teal hair" in said     # and the tags, which are what the prompt is made of
    assert "white nightgown" in said           # the outfit's tags, not just its name
    assert "bedroom" in said and "sunlit bedroom" in said


def test_the_writer_is_handed_the_note_when_there_is_one(tmp_path):
    # The main agent's voice. A user saying "this one is flat" reaches the writer as a note, and
    # calling the same frame again with one is what a retry is here.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    writer = FakeWriter()
    _wrote(files, writer, file="scene.json", frame=1, note="make it tenser, she is afraid")
    assert "make it tenser, she is afraid" in writer.user


def test_the_writer_is_handed_this_frame_and_no_other(tmp_path):
    # The user's decision of 5 Sep, and the reason this request is cheap. A file of forty frames
    # would otherwise send forty casts to write one sentence.
    files = _with(
        tmp_path,
        "scene.json",
        json.dumps(
            {
                "characters": {"aylin": "1girl", "deniz": "1boy, dark hair"},
                "outfits": {"gecelik": "white nightgown", "palto": "long coat"},
                "locations": {"bedroom": "sunlit bedroom", "balcony": "night balcony"},
                "frames": [
                    {"number": 1, "scene": "one", "characters": {"aylin": ["gecelik"]},
                     "location": "bedroom"},
                    {"number": 2, "scene": "two", "characters": {"deniz": ["palto"]},
                     "location": "balcony"},
                ],
            }
        ),
    )
    writer = FakeWriter()
    _wrote(files, writer, file="scene.json", frame=1)
    assert "aylin" in writer.user
    assert "deniz" not in writer.user
    assert "long coat" not in writer.user
    assert "night balcony" not in writer.user


def test_what_comes_back_is_written_to_the_frames_action(tmp_path):
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    _wrote(files, FakeWriter("she turns her head, close-up"), file="scene.json", frame=1)
    assert _frames(files)[0]["action"] == "she turns her head, close-up"


def test_an_action_that_is_already_there_is_written_over(tmp_path):
    # Always, and on purpose: a second call with a note is a correction, and a correction that left
    # the old sentence behind would be an argument rather than a fix.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    _wrote(files, FakeWriter("she looks away"), file="scene.json", frame=2, note="softer")
    assert _frames(files)[1]["action"] == "she looks away"


def test_the_answer_is_a_receipt_rather_than_the_prompt(tmp_path):
    # Madde 130's rule, one road along: what was built goes in the file, not back into the chat.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    answer = _wrote(files, FakeWriter("she turns her head"), file="scene.json", frame=1)
    assert answer.text == "Wrote frame 1 of scene.json."
    assert "turns her head" not in answer.text
    # No card: the file was already there.
    assert answer.created is None


def test_the_tools_own_spending_comes_back_with_its_answer(tmp_path):
    # The user pays for this request, so somebody has to be able to find it. The tool is the only
    # place that knows it happened.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    answer = _wrote(
        files,
        FakeWriter(spent={"sent": 300, "cached": 0, "answered": 60}),
        file="scene.json",
        frame=1,
    )
    assert answer.spent == {"sent": 300, "cached": 0, "answered": 60}


def test_a_frame_with_no_scene_has_nothing_to_write_from(tmp_path):
    files = _with(
        tmp_path, "scene.json", json.dumps({"frames": [{"number": 1, "characters": {}}]})
    )
    writer = FakeWriter()
    answer = _wrote(files, writer, file="scene.json", frame=1)
    assert "Frame 1 has no scene to write from." in answer.text
    # Refused before the request, not after it: nothing is paid to be told this.
    assert writer.user is None


def test_writing_refuses_a_frame_that_is_not_there(tmp_path):
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    assert "there is no frame 9" in _wrote(
        files, FakeWriter(), file="scene.json", frame=9
    ).text


def test_writing_without_a_model_says_so_rather_than_crashing(tmp_path):
    # run_tool's engine is optional, and every other tool ignores it. This one cannot.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    answer = run_tool(
        files, "p1", "write_frame_prompt", json.dumps({"file": "scene.json", "frame": 1})
    )
    assert "no model to write with" in answer.text
    assert "action" not in _frames(files)[0]


def test_a_request_that_falls_over_leaves_the_frame_as_it_was(tmp_path):
    # The service's own words, and no retry: calling the same frame again is what a retry is here,
    # and a loop inside the tool would pay twice without anybody seeing it happen.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    answer = _wrote(
        files, FakeWriter(blow_up="503 upstream is busy"), file="scene.json", frame=1
    )
    assert "503 upstream is busy" in answer.text
    assert "action" not in _frames(files)[0]


def test_an_empty_answer_is_not_written_down(tmp_path):
    # An empty action builds into a prompt with a gap where the sentence should be, and nothing
    # downstream would ever say which frame it came from.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    answer = _wrote(files, FakeWriter("   "), file="scene.json", frame=1)
    assert "answered with nothing" in answer.text
    assert "action" not in _frames(files)[0]


def test_the_two_frame_tools_point_at_the_one_that_writes_an_action():
    # Madde 173 and 174 both stayed silent about the action because the tool that writes one did
    # not exist yet, and naming a tool the model cannot call is m127's mistake. It exists now.
    assert "write_frame_prompt" in _said_by("add_scene")
    assert "write_frame_prompt" in _said_by("update_frame")


# --- a look that hands back what there is to look at (Madde 135) ---------------------------------
#
# The preview said "Wrote 1 prompts to ...-lara.py" and stopped there, so the model read the file
# back to show the user the thing they had asked to see. Madde 98 called this tool a look; a look
# that returns nothing to look at costs a round every time it is taken.


def test_a_character_preview_hands_back_the_prompts_it_built(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    answer = _call(files, "build_character_prompts", name="scene.json", character="aylin")
    assert "long teal hair" in answer
    assert "white nightgown" in answer


def test_a_character_preview_counts_one_prompt_as_one(tmp_path):
    # counted() rather than a bare number, which is what the outcome has used all along -- the
    # sentence was the one place still saying "1 prompts".
    files = _with(tmp_path, "scene.json", STRUCTURE)
    answer = _call(files, "build_character_prompts", name="scene.json", character="aylin")
    assert "1 prompt " in answer
    assert "1 prompts" not in answer


def test_a_character_preview_still_writes_its_file(tmp_path):
    # A guard. Handing the prompts back is in addition to the file, not instead of it: the card
    # names it and the user finds it in the project afterwards.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    built = run_tool(
        files,
        "p1",
        "build_character_prompts",
        json.dumps({"name": "scene.json", "character": "aylin"}),
    )
    assert built.created == "scene-aylin.py"
    assert files.read("p1", "scene-aylin.py")


def test_a_build_of_one_frame_counts_it_as_one(tmp_path):
    # Madde 136. The sentence printed a bare number beside a fixed plural, so a one-frame scenario
    # read "Wrote 1 prompts" -- while the outcome one line below it said "1 prompt", because that
    # one goes through counted(). One result, two grammars.
    one = json.loads(STRUCTURE)
    one["frames"] = one["frames"][:1]
    files = _with(tmp_path, "one.json", json.dumps(one))
    answer = _call(files, "build_prompts", name="one.json")
    assert "1 prompt " in answer
    assert "1 prompts" not in answer


def test_a_build_of_more_than_one_still_says_prompts(tmp_path):
    # A guard: counted() is not a rewrite of the sentence, only of the number in it.
    files = _with(tmp_path, "frames.json", STRUCTURE)
    assert "2 prompts" in _call(files, "build_prompts", name="frames.json")


def test_the_scene_builder_still_does_not_hand_back_its_prompts(tmp_path):
    # A guard, and the limit of this item. Madde 130 says the built prompts are never printed back,
    # and twenty-five of them inside a tool answer is the invitation to print them. A preview is
    # there to be looked at; a built list is there to sit in the file.
    files = _with(tmp_path, "frames.json", STRUCTURE)
    answer = _call(files, "build_prompts", name="frames.json")
    assert "frames.py" in answer
    assert "long teal hair" not in answer


def test_calling_add_scene_twice_puts_the_scenes_in_twice(tmp_path):
    # Appending is not idempotent, and pretending otherwise would have the tool guess which of two
    # identical scenes was meant. Left visible instead, in the numbers the second answer names.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "add_scene", file="scene.json", scenes=[SCENE])
    answer = _call(files, "add_scene", file="scene.json", scenes=[SCENE])
    assert len(json.loads(files.read("p1", "scene.json"))["frames"]) == 4
    assert "as frame 4." in answer
