import json

import pytest

from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.domain.naming import unique_name
from backend.features.workspace.domain.tools import (
    DEFAULT_NAME,
    MAX_ROUNDS,
    TOOL_SPECS,
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


def test_reading_gives_the_contents(tmp_path):
    files = _files(tmp_path)
    _call(files, "create_file", name="plan.md", content="the body")
    # Numbered since Madde 131: the contents are all still there, with the column in front of them.
    assert _call(files, "read_file", name="plan.md") == "     1\tthe body"


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
    # the rule add_frames keeps, and the same person opening the same file.
    files = _files(tmp_path)
    _call(files, "start_scenario", name="bar-scene")
    assert '\n  "characters": {}' in files.read("p1", "bar-scene.json")


# --- creating over a name that is taken (Madde 69) ------------------------------------------------
#
# It used to number: plan.md became plan-2.md and the project held two versions of one document. The
# way to change a file that exists is edit_file, and until now reaching for it was the model's own
# choice -- which is the kind of thing FOUNDATION 5 says code decides.


def test_creating_over_a_name_that_is_taken_writes_nothing(tmp_path):
    files = _with(tmp_path, "plan.md", "first")
    _call(files, "create_file", name="plan.md", content="second")
    # Asked of the store rather than through read_file: the subject here is what is on disk, and
    # since Madde 131 the tool hands back a numbered view of it rather than the document.
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


def test_the_schema_tool_hands_back_the_shape_and_the_rules(tmp_path):
    from backend.features.workspace.domain.schema import SCHEMA

    # No arguments at all: there is one shape, and asking which one would be a question with a
    # single answer.
    assert _call(_files(tmp_path), "read_prompt_structure_schema") == SCHEMA


def test_the_schema_tool_brings_no_file_into_being(tmp_path):
    assert run_tool(_files(tmp_path), "p1", "read_prompt_structure_schema", "{}").created is None


def test_the_schema_tool_says_what_it_answered_with(tmp_path):
    # A reader's line rather than the answer itself, like every other outcome.
    assert run_tool(_files(tmp_path), "p1", "read_prompt_structure_schema", "{}").outcome == "Schema"


def test_create_file_names_both_formats_a_file_can_take():
    # The param used to say ending in .md while the schema says a structure file is .json -- two
    # opposite instructions to the same model. Pinned so the contradiction cannot quietly return.
    spec = next(s for s in TOOL_SPECS if s["function"]["name"] == "create_file")
    said = spec["function"]["parameters"]["properties"]["name"]["description"]
    assert ".md for a document" in said
    assert ".json for a structure file" in said


def test_the_schema_tool_defines_the_term_it_hands_back():
    # The model meets the words structure file in three descriptions before any skill text
    # explains them. The definition has to ride with the name, or a skill-less chat reads a term
    # nothing anchors.
    spec = next(s for s in TOOL_SPECS if s["function"]["name"] == "read_prompt_structure_schema")
    said = spec["function"]["description"]
    assert "one JSON per scenario" in said
    assert "before writing or changing" in said


def test_the_listing_tool_is_gone():
    # Madde 127: the names ride in every request now, so there is nothing left for this tool to
    # answer -- and a tool that is still declared keeps being called. Taking it away is what makes
    # the call impossible rather than merely discouraged.
    assert "list_files" not in {spec["function"]["name"] for spec in TOOL_SPECS}


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
        # Seventh since Madde 96. The shape of a structure file stopped being a paragraph in a
        # skill's text; it is fetched when a file is about to be written. Renamed 28 Aug so the
        # name says whose schema it reads.
        "read_prompt_structure_schema",
        # Eighth since Madde 98: the same joining, one character at a time, so a character can be
        # looked at before it enters a frame.
        "build_character_prompts",
        # Madde 128. Appending to a JSON list through edit_file made the model quote the previous
        # frame back to reach the end of it; the end of a list is something code knows.
        "add_frames",
        # Madde 167. create_file writes a document, this writes a structure -- and it takes no
        # content, because the shape is the code's. It has to exist before Madde 171 shuts .json to
        # create_file, or the model would be left with no way to start a scenario at all.
        "start_scenario",
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
    _call(files, "edit_file", name="intro-frames.json", old="long teal hair", new="short red hair")
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
    # Empty rather than invented: the call really is about nothing in particular.
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


# --- a read that hands back line numbers (Madde 131) ----------------------------------------------
#
# The anchor an edit takes has to occur exactly once, and the model was judging that by eye over an
# unnumbered wall of near-identical frames. It judged wrong, `_edit` answered "appears 3 times", and
# the retry cost a whole round. Claude Code's Read hands back `cat -n`, and its Edit carries the
# same uniqueness rule -- what was missing here is not the rule but the column in front of it.


def test_a_read_hands_back_numbered_lines(tmp_path):
    files = _with(tmp_path, "plan.md", "alpha\nbeta\ngamma")
    assert _call(files, "read_file", name="plan.md") == (
        "     1\talpha\n     2\tbeta\n     3\tgamma"
    )


def test_the_numbers_are_right_aligned_so_the_text_starts_in_one_column(tmp_path):
    # Padding rather than a bare number: left-aligned, the text would step right at line 10 and the
    # model would be reading a ragged edge for the rest of the file.
    files = _with(tmp_path, "long.md", "\n".join(str(n) for n in range(1, 11)))
    lines = _call(files, "read_file", name="long.md").splitlines()
    assert lines[8] == "     9\t9"
    assert lines[9] == "    10\t10"
    assert lines[8].index("\t") == lines[9].index("\t")


def test_an_empty_file_reads_as_nothing_rather_than_a_first_line(tmp_path):
    # A guard, green before the change: a lone "1" would put a line in front of the model that the
    # file does not have, and an edit anchored on nothing is the next thing that happens.
    files = _with(tmp_path, "empty.md", "")
    assert _call(files, "read_file", name="empty.md") == ""


def test_the_outcome_still_counts_the_lines_it_read(tmp_path):
    # A guard: the outcome counts the file's lines, not the width of what was shown.
    files = _with(tmp_path, "plan.md", "alpha\nbeta\ngamma")
    assert _outcome(files, "read_file", name="plan.md") == "3 lines"


def test_the_schema_is_handed_back_unnumbered(tmp_path):
    # A guard, and the reason is the rule: numbers exist so an anchor can be picked, and no anchor
    # is ever written into the schema. It is one text for the whole app, not a file on disk.
    from backend.features.workspace.domain.schema import SCHEMA

    assert _call(_files(tmp_path), "read_prompt_structure_schema") == SCHEMA


def test_an_edit_matches_the_disk_and_not_the_numbered_view(tmp_path):
    # A guard on the seam: what the model was shown carries a column the file does not have, and
    # matching against the shown form would edit a file nobody has.
    files = _with(tmp_path, "plan.md", "alpha\nbeta")
    _call(files, "read_file", name="plan.md")
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


# --- adding frames without an anchor (Madde 128) --------------------------------------------------
#
# Appending to a JSON list is not an append: the list closes with a bracket and the new frame goes
# before it. So edit_file made the model quote the previous frame back word for word -- once in old
# and once in new, in the most expensive token class -- and near-identical frames made that anchor
# collide besides. Nothing here takes a position from the model, so there is no position to get
# wrong: the end of a list is a fact the code holds. NotebookEdit is the same shape for a
# structured file, and build_prompts already walks it here.

FRAME = {
    "characters": {"aylin": ["gecelik"]},
    "location": "bedroom",
    "action": "three",
    "camera": "wide",
}


def test_add_frames_appends_to_the_end_of_the_list(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "add_frames", name="scene.json", frames=[FRAME])
    frames = json.loads(files.read("p1", "scene.json"))["frames"]
    assert len(frames) == 3
    assert frames[2]["action"] == "three"
    # The two that were there stay where they were: the built list runs in the frames' order.
    assert [frame["action"] for frame in frames[:2]] == ["one", "two"]


def test_add_frames_says_how_many_it_added_and_how_many_there_are_now(tmp_path):
    # Two numbers rather than one. The model learns the state from the answer instead of reading
    # the file back, and the second number is what makes a doubled call visible.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    assert _call(files, "add_frames", name="scene.json", frames=[FRAME, FRAME]) == (
        "Added 2 frames to scene.json; it holds 4 now."
    )


def test_add_frames_says_on_the_card_how_many_it_added(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    assert _outcome(files, "add_frames", name="scene.json", frames=[FRAME]) == "1 frame"


def test_add_frames_leaves_the_maps_alone(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "add_frames", name="scene.json", frames=[FRAME])
    after = json.loads(files.read("p1", "scene.json"))
    before = json.loads(STRUCTURE)
    for key in ("quality", "characters", "outfits", "locations"):
        assert after[key] == before[key]


def test_add_frames_writes_readable_turkish_rather_than_escapes(tmp_path):
    # The user opens this file and fixes it by hand, and a wall of ı is a file they cannot
    # read. Their work is the first principle, and it includes being able to see it.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "add_frames", name="scene.json", frames=[{**FRAME, "action": "başını çeviriyor"}])
    assert "başını çeviriyor" in files.read("p1", "scene.json")


def test_add_frames_refuses_a_file_that_is_not_there(tmp_path):
    assert "no file by that name" in _call(
        _files(tmp_path), "add_frames", name="ghost.json", frames=[FRAME]
    )


def test_add_frames_carries_the_parsers_own_sentence_when_the_json_is_broken(tmp_path):
    # A guessed cause would send the model looking in the wrong place -- _build's rule.
    files = _with(tmp_path, "scene.json", "{ not json")
    answer = _call(files, "add_frames", name="scene.json", frames=[FRAME])
    assert "not valid JSON" in answer
    assert "Expecting" in answer


def test_add_frames_refuses_a_structure_with_no_frames_list(tmp_path):
    files = _with(tmp_path, "scene.json", json.dumps({"characters": {"aylin": "1girl"}}))
    assert "no frames list" in _call(files, "add_frames", name="scene.json", frames=[FRAME])


def test_add_frames_refuses_a_frames_argument_that_is_not_a_list(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    assert "list of frames" in _call(files, "add_frames", name="scene.json", frames="three")
    assert files.read("p1", "scene.json") == STRUCTURE


def test_adding_nothing_writes_nothing(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    assert "unchanged" in _call(files, "add_frames", name="scene.json", frames=[])
    assert files.read("p1", "scene.json") == STRUCTURE


def test_add_frames_brings_no_file_into_being(tmp_path):
    # No card: the file was already there. The rule edit_file follows.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    added = run_tool(
        files, "p1", "add_frames", json.dumps({"name": "scene.json", "frames": [FRAME]})
    )
    assert added.created is None


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


def test_calling_add_frames_twice_puts_the_frames_in_twice(tmp_path):
    # Appending is not idempotent, and pretending otherwise would have the tool guess which of two
    # identical frames was meant. Left visible instead, in the second number of the answer.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "add_frames", name="scene.json", frames=[FRAME])
    answer = _call(files, "add_frames", name="scene.json", frames=[FRAME])
    assert len(json.loads(files.read("p1", "scene.json"))["frames"]) == 4
    assert "holds 4 now" in answer
