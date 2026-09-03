import json
import threading
import time

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


def test_the_schema_tool_is_gone(tmp_path):
    # Madde 159. Half of what it handed back described the file's shape, and that half died as the
    # tools took the shape over -- the model was reading a JSON example of a form it can no longer
    # write. What did not die is craft, and craft moved into the descriptions of the tools that
    # write values.
    assert "read_prompt_structure_schema" not in {s["function"]["name"] for s in TOOL_SPECS}
    assert "no tool called" in _call(_files(tmp_path), "read_prompt_structure_schema").lower()


def test_the_module_that_held_the_schema_is_gone():
    # Imported inside, like everything else in this file that asks about a module: a bare import at
    # the top of a test file is a collection error, and then no red in the turn is visible.
    with pytest.raises(ImportError):
        from backend.features.workspace.domain import schema  # noqa: F401


def test_create_file_no_longer_offers_the_structure_extension():
    # This param once named both formats, because the tool could write both. Since Madde 151 it
    # cannot, and an example still offering .json would walk the model into a refusal -- the same
    # contradiction as before, pointing the other way.
    spec = next(s for s in TOOL_SPECS if s["function"]["name"] == "create_file")
    said = spec["function"]["parameters"]["properties"]["name"]["description"]
    assert ".json" not in said
    assert ".md" in said


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
        # read_prompt_structure_schema stood here from Madde 96 until 159 retired it. The half of it
        # that described the file's shape died as the tools took the shape over, and the half that
        # was craft moved into the descriptions of the tools that write values.
        # Eighth since Madde 98: the same joining, one character at a time, so a character can be
        # looked at before it enters a frame.
        "build_character_prompts",
        # Madde 154. One tool per part of a structure file, now that create_file and edit_file
        # cannot touch one. Three set_ rather than one taking a map: three resources, and each
        # carries a rule the others do not -- read where the model is using it.
        "create_structure",
        "set_character",
        "set_outfit",
        "set_location",
        # Madde 155. add_frames became these two: one opens frames from their sentences, the other
        # goes round the empty ones and writes each from a request of its own.
        "add_scene",
        "write_frame_prompt",
        # Madde 157. Four rather than one taking a map, for the reason the set_ tools are four: a
        # single remove_entry would have the model remembering which of them wants to be told where
        # to look. Removal is its own tool rather than a set_ with nothing in it -- an empty value
        # meaning delete would let a model that failed to fill a field wipe the entry in silence.
        "remove_character",
        "remove_outfit",
        "remove_location",
        "remove_frame",
        # Madde 158, and the last of the holes Madde 151 opened: correcting a frame that is already
        # written. Apart from write_frame_prompt so that the intent is in the call rather than in
        # what the tool finds when it gets there.
        "update_frame",
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


# Madde 151. What the model may write to a structure file used to be a list of rules it was asked to
# hold; from here it is a door. These hold the door shut, and the ones after them hold it from
# closing on anything else.


def test_create_file_refuses_a_structure_file(tmp_path):
    said = _call(_files(tmp_path), "create_file", name="scene.json", content="{}")
    assert "structure file" in said
    assert "as text" in said


def test_create_file_writes_nothing_when_it_refuses(tmp_path):
    # Two things, and this is the one that matters: saying no is not the same as not writing.
    files = _files(tmp_path)
    _call(files, "create_file", name="scene.json", content="{}")
    assert files.read("p1", "scene.json") is None


def test_create_file_refuses_a_structure_file_before_looking_at_the_name(tmp_path):
    # Ahead of the taken-name check on purpose. If a taken name answered differently, the model
    # would read that as a door which opens for a name nobody has used yet.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    said = _call(files, "create_file", name="scene.json", content="{}")
    assert "structure file" in said
    assert "already" not in said.lower()
    assert files.read("p1", "scene.json") == STRUCTURE


def test_the_door_does_not_care_about_letter_case(tmp_path):
    # A door a model can walk around by shouting the extension is not a door, and this is exactly
    # the kind of gap it finds while looking for one.
    said = _call(_files(tmp_path), "create_file", name="SCENE.JSON", content="{}")
    assert "structure file" in said


def test_a_refused_structure_write_says_refused(tmp_path):
    assert _outcome(_files(tmp_path), "create_file", name="scene.json", content="{}") == "Refused"


def test_edit_file_refuses_a_structure_file(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    said = _call(files, "edit_file", name="scene.json", old="wide", new="close")
    assert "structure file" in said
    assert "as text" in said


def test_edit_file_leaves_the_structure_untouched_when_it_refuses(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "edit_file", name="scene.json", old="wide", new="close")
    assert files.read("p1", "scene.json") == STRUCTURE


def test_edit_file_still_repairs_a_broken_structure_file(tmp_path):
    # The one way in, and it has to stay open. A file the user broke by hand fails every structural
    # tool at json.loads; if text editing were shut too, nothing could put the comma back.
    files = _with(tmp_path, "scene.json", '{"frames": [,]}')
    _call(files, "edit_file", name="scene.json", old="[,]", new="[]")
    assert files.read("p1", "scene.json") == '{"frames": []}'


def test_read_file_still_opens_a_structure_file(tmp_path):
    # Reading breaks nothing, and a model that cannot see the file is blind rather than safe
    # (kullanıcı kararı, 3 Eylül).
    files = _with(tmp_path, "scene.json", STRUCTURE)
    assert "aylin" in _call(files, "read_file", name="scene.json")


def test_the_door_is_not_in_front_of_the_structural_tools(tmp_path):
    # add_scene writes the same file and must go on writing it: the door is about the model
    # writing JSON by hand, not about the tools that own the shape.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "add_scene", file="scene.json", scenes=["bir"])
    assert len(json.loads(files.read("p1", "scene.json"))["frames"]) == 3


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
    # Written straight to the store rather than through edit_file, which Madde 151 shut on this
    # file. What is being measured is the build overwriting its own output, and how the structure
    # came to change in between is not part of it.
    files.write("p1", "intro-frames.json", STRUCTURE.replace("long teal hair", "short red hair"))
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
    # Empty rather than invented: the call really is about nothing in particular. Asked of a name
    # nobody knows since Madde 159 took the schema reader away -- it was the one tool that ran and
    # named no file, and this claim is about the empty target rather than about that tool.
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


# --- the SDXL prompt rules, and the one place they live (Madde 159) -------------------------------
#
# The schema tool handed back two halves. The shape half died as the tools took the shape over --
# create_file cannot write a structure file, set_ and update_ build it, and the model can read the
# result with read_file. What is left is the rules: how a value is written for an image model. They
# sit in the descriptions of the tools that write values, where the model reads them while choosing
# the tool rather than at the top of a long context, and no round is spent fetching them. Named for
# what they are (4 Sep): CRAFT said nothing to whoever met the word cold.


def _rules():
    from backend.features.workspace.domain.tools import SDXL_PROMPT_RULES

    return SDXL_PROMPT_RULES


def _description(tool):
    return next(s for s in TOOL_SPECS if s["function"]["name"] == tool)["function"]["description"]


@pytest.mark.parametrize(
    "tool", ["set_character", "set_outfit", "set_location", "update_frame"]
)
def test_every_tool_that_writes_a_value_carries_the_prompt_rules(tool):
    # One text, not split by tool (user decision, 3 Sep). set_character sees the frame rules too:
    # harmless, and being one source it cannot go stale against itself.
    assert _rules() in _description(tool)


@pytest.mark.parametrize("tool", ["add_scene", "write_frame_prompt", "build_prompts"])
def test_a_tool_that_writes_no_value_does_not_carry_it(tool):
    # add_scene writes the user's own sentence and it never reaches a prompt; write_frame_prompt
    # takes no fields at all. A rule carried where it cannot apply is a rule read where it cannot
    # be used.
    assert _rules() not in _description(tool)


def test_the_sub_model_is_told_the_same_thing(tmp_path):
    from backend.features.workspace.domain.tools import WRITING

    # Madde 155 wrote this text a second time on purpose, with the schema still standing. One source
    # now, so the two cannot drift into telling one model something the other was never told.
    assert _rules() in WRITING


def test_the_prompt_rules_teach_the_form_of_a_value():
    said = _rules().lower()
    assert "tags" in said and "sentence" in said
    # The two the trials actually produced: a narrated action, and a value hedging between two.
    assert "no or" in said
    assert "frozen instant" in said


def test_the_prompt_rules_teach_what_a_camera_is():
    said = _rules().lower()
    # Two decisions, both from the given lists, because a camera written as one leaves the other
    # to the image model.
    assert "close-up" in said and "from above" in said


def test_the_prompt_rules_say_who_opens_a_prompt():
    assert "first" in _rules().lower()


def test_the_prompt_rules_leave_the_count_and_the_quality_to_code():
    said = _rules().lower()
    assert "quality" in said and "count" in said


def test_the_prompt_rules_say_nothing_about_the_shape_of_the_file():
    # The half that died. A JSON example here would be the schema coming back in a place the model
    # reads every turn, and it would describe a file it is no longer allowed to write by hand.
    said = _rules()
    assert "{" not in said and "}" not in said
    assert '"frames"' not in said and "json" not in said.lower()


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


# --- a frame is born from its scene (Madde 155) ---------------------------------------------------
#
# Two calls where there was one. add_scene opens frames carrying nothing but the sentence they are
# for; write_frame_prompt goes round the empty ones and fills each from its own small request. What
# splits them is that a frame can be planned without knowing what its picture holds -- and the
# scenes used to live in a second file, matched to frames by position, which is a pairing nobody
# could see go wrong.

FRAME = {
    "frame": 3,
    "characters": {"aylin": ["gecelik"]},
    "location": "bedroom",
    "action": "three",
    "camera": "wide",
}

# What the writer answers with: the fields update_frame takes, and nothing else. One shape for both
# roads into a frame (Madde 155).
WRITTEN = json.dumps(
    {
        "characters": {"aylin": ["gecelik"]},
        "location": "bedroom",
        "action": "sitting on edge of bed, looking down",
        "camera": "medium shot, from above",
    }
)


def _scened(tmp_path, *scenes):
    """A structure whose frames carry a sentence each and no prompt at all."""
    structure = json.loads(STRUCTURE)
    structure["frames"] = [
        {"frame": place, "scene": scene} for place, scene in enumerate(scenes, start=1)
    ]
    return _with(tmp_path, "scene.json", json.dumps(structure))


def _frames_of(files, name="scene.json"):
    return json.loads(files.read("p1", name))["frames"]


class ScriptedWriter:
    """Stands in for the model write_frame_prompt asks, one frame at a time.

    Answers in the order it is called. A None in the script is a request that fell over, which is
    the case the tool has to survive without losing the frames around it.

    It also counts how many calls are in the air at once, because that is the only thing about the
    waves that can be seen from outside: how long they take is not something a test should measure.
    """

    def __init__(self, answers, usage=None):
        self.answers = list(answers)
        self.seen = []
        self.at_once = 0
        self.seen_when_first_finished = None
        self._live = 0
        self._lock = threading.Lock()
        self._usage = usage

    def write_once(self, system, user, model=""):
        with self._lock:
            self._live += 1
            self.at_once = max(self.at_once, self._live)
            place = len(self.seen)
            self.seen.append({"system": system, "user": user, "model": model})
        # Long enough that a second request would overlap this one if it were allowed to.
        time.sleep(0.01)
        with self._lock:
            self._live -= 1
            if place == 0:
                # Evidence of the warm-up: nobody else had started while the first was out.
                self.seen_when_first_finished = len(self.seen)
        answer = self.answers[place] if place < len(self.answers) else self.answers[-1]
        if answer is None:
            raise RuntimeError("the connection dropped")
        return {"text": answer, "usage": self._usage}


def _write(files, writer, name="scene.json"):
    return run_tool(
        files, "p1", "write_frame_prompt", json.dumps({"file": name}), engine=writer
    )


def test_add_scene_opens_a_frame_for_each_sentence(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "add_scene", file="scene.json", scenes=["Aylin mektubu okuyor", "Deniz kapıda"])
    assert [frame.get("scene") for frame in _frames_of(files)[2:]] == [
        "Aylin mektubu okuyor",
        "Deniz kapıda",
    ]


def test_a_scene_frame_carries_no_prompt_fields(tmp_path):
    # Born with the brief and its number, nothing else. What the picture holds is a separate act,
    # and a frame half-filled by whoever wrote the sentence is the pairing this madde takes apart.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "add_scene", file="scene.json", scenes=["Aylin mektubu okuyor"])
    assert set(_frames_of(files)[2]) == {"frame", "scene"}


def test_add_scene_appends_and_renumbers(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "add_scene", file="scene.json", scenes=["bir", "iki"])
    assert [frame["frame"] for frame in _frames_of(files)] == [1, 2, 3, 4]


def test_add_scene_says_which_numbers_the_scenes_got(tmp_path):
    # The model addresses a frame by number from here on, and this answer is where it learns them.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    said = _call(files, "add_scene", file="scene.json", scenes=["bir", "iki"])
    assert "3" in said and "4" in said


def test_add_scene_refuses_an_empty_list(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    assert "scene" in _call(files, "add_scene", file="scene.json", scenes=[])
    assert files.read("p1", "scene.json") == STRUCTURE


def test_add_scene_refuses_a_list_that_is_not_one(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    assert "list" in _call(files, "add_scene", file="scene.json", scenes="bir")
    assert files.read("p1", "scene.json") == STRUCTURE


def test_add_scene_refuses_something_that_is_not_a_sentence(tmp_path):
    # All or nothing, as everywhere else: one bad element and no frame is opened, rather than a
    # file left holding some of what was asked for.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    assert "sentence" in _call(files, "add_scene", file="scene.json", scenes=["bir", 7])
    assert files.read("p1", "scene.json") == STRUCTURE


def test_add_scene_refuses_a_file_that_is_not_there(tmp_path):
    assert "no file by that name" in _call(
        _files(tmp_path), "add_scene", file="ghost.json", scenes=["bir"]
    )


# --- the prompt is written one frame at a time (Madde 155) ----------------------------------------
#
# The tool is a loop, and each turn of it is a request of its own: this frame's sentence, the file's
# maps, and a system prompt about writing prompts. Nothing else -- not the conversation, not the
# other frames, not the previous camera. Sixteen rounds in the main chat could never have carried
# forty frames, and each of those rounds would have re-sent the whole conversation to write one.


def test_an_empty_frame_is_filled_from_its_scene(tmp_path):
    files = _scened(tmp_path, "Aylin mektubu okuyor")
    _write(files, ScriptedWriter([WRITTEN]))
    written = _frames_of(files)[0]
    assert written["action"] == "sitting on edge of bed, looking down"
    assert written["scene"] == "Aylin mektubu okuyor"  # the brief stays where it was


def test_a_frame_that_is_already_written_is_left_alone(tmp_path):
    # Which is what lets the call be made again: it fills the empty ones and passes over the rest,
    # so a run that lost three frames is finished by running it once more.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    writer = ScriptedWriter([WRITTEN])
    _write(files, writer)
    assert writer.seen == []


def test_a_frame_without_a_scene_is_left_alone(tmp_path):
    # Nothing to write from. A request carrying no brief would be the model inventing a frame.
    structure = json.loads(STRUCTURE)
    structure["frames"] = [{"frame": 1}]
    files = _with(tmp_path, "scene.json", json.dumps(structure))
    writer = ScriptedWriter([WRITTEN])
    _write(files, writer)
    assert writer.seen == []


def test_the_request_carries_the_scene_and_the_maps(tmp_path):
    # And the maps because the writer picks from them: it names a character, not describes one.
    files = _scened(tmp_path, "Aylin mektubu okuyor")
    writer = ScriptedWriter([WRITTEN])
    _write(files, writer)
    asked = writer.seen[0]["user"]
    assert "Aylin mektubu okuyor" in asked
    assert "aylin" in asked and "gecelik" in asked and "bedroom" in asked


def test_the_request_carries_nothing_of_the_other_frames(tmp_path):
    # The whole saving, and the whole of the focus: two frames are two small questions rather than
    # one growing one.
    files = _scened(tmp_path, "birinci sahne", "ikinci sahne")
    writer = ScriptedWriter([WRITTEN, WRITTEN])
    _write(files, writer)
    assert "ikinci sahne" not in writer.seen[0]["user"]


def test_a_name_the_writer_invented_leaves_that_frame_empty(tmp_path):
    # The same check add_frames used to make, on the same road in: a name no map knows does not
    # reach the file, whoever offered it. The frames around it are not punished for it.
    invented = json.dumps({"characters": {"lara": []}, "action": "a", "camera": "b"})
    files = _scened(tmp_path, "birinci", "ikinci")
    _write(files, ScriptedWriter([invented, WRITTEN]))
    frames = _frames_of(files)
    assert "action" not in frames[0]
    assert frames[1]["action"] == "sitting on edge of bed, looking down"


def test_an_answer_that_is_not_json_leaves_that_frame_empty(tmp_path):
    files = _scened(tmp_path, "birinci", "ikinci")
    _write(files, ScriptedWriter(["I am afraid I cannot", WRITTEN]))
    frames = _frames_of(files)
    assert "action" not in frames[0]
    assert "action" in frames[1]


def test_a_request_that_fell_over_leaves_that_frame_empty(tmp_path):
    files = _scened(tmp_path, "birinci", "ikinci")
    _write(files, ScriptedWriter([None, WRITTEN]))
    assert "action" not in _frames_of(files)[0]
    assert "action" in _frames_of(files)[1]


def test_the_report_counts_what_was_written_and_what_was_left(tmp_path):
    # Nothing is retried. The model is told what stands so it can decide -- run again, change the
    # model in the composer, or fix the scene that keeps failing.
    files = _scened(tmp_path, "birinci", "ikinci")
    said = _write(files, ScriptedWriter([None, WRITTEN])).text
    assert "1" in said and "empty" in said.lower()


def test_running_again_fills_only_the_empty_ones(tmp_path):
    files = _scened(tmp_path, "birinci", "ikinci")
    _write(files, ScriptedWriter([None, WRITTEN]))
    second = ScriptedWriter([WRITTEN])
    _write(files, second)
    assert len(second.seen) == 1
    assert all("action" in frame for frame in _frames_of(files))


def test_no_more_than_five_requests_are_in_the_air(tmp_path):
    # The provider answers a full pool with a 429 and this app does not retry, so a dropped request
    # is a dropped frame. Five is fast without going near it.
    files = _scened(tmp_path, *[f"sahne {n}" for n in range(12)])
    writer = ScriptedWriter([WRITTEN])
    _write(files, writer)
    assert writer.at_once <= 5
    assert len(writer.seen) == 12


def test_the_first_request_goes_alone(tmp_path):
    # It warms the provider's prefix cache -- instruction and maps are the same in all of them, and
    # if they all left together none would find it warm.
    files = _scened(tmp_path, *[f"sahne {n}" for n in range(12)])
    writer = ScriptedWriter([WRITTEN])
    _write(files, writer)
    assert writer.seen_when_first_finished == 1


def test_it_stops_at_a_hundred_requests(tmp_path):
    files = _scened(tmp_path, *[f"sahne {n}" for n in range(105)])
    writer = ScriptedWriter([WRITTEN])
    said = _write(files, writer).text
    assert len(writer.seen) == 100
    assert "5" in said


def test_what_the_sub_requests_spent_is_reported(tmp_path):
    # Otherwise this tool spends from somewhere the bill cannot see.
    files = _scened(tmp_path, "birinci", "ikinci")
    writer = ScriptedWriter([WRITTEN], usage={"sent": 10, "cached": 2, "answered": 5})
    assert _write(files, writer).spent == {"sent": 20, "cached": 4, "answered": 10}


def test_without_an_engine_the_tool_refuses(tmp_path):
    # An answer rather than a crash, the rule every miss in this module follows.
    files = _scened(tmp_path, "birinci")
    said = run_tool(files, "p1", "write_frame_prompt", json.dumps({"file": "scene.json"})).text
    assert "cannot" in said.lower() or "no" in said.lower()


def test_write_frame_prompt_refuses_a_file_that_is_not_there(tmp_path):
    said = _write(_files(tmp_path), ScriptedWriter([WRITTEN]), name="ghost.json").text
    assert "no file by that name" in said


# --- the file is born and the maps are filled by tools of their own (Madde 154) -------------------
#
# Madde 151 shut create_file and edit_file on a structure file; from here every part of one has a
# tool. Three set_ tools rather than a single one with a map parameter, because each map carries a
# different rule -- and the rules move out of the fourteen-item list into the description of the
# tool they apply to, where the model reads them at the moment it is using them.


def _map_of(files, name, which):
    return json.loads(files.read("p1", name))[which]


def test_create_structure_writes_an_empty_skeleton(tmp_path):
    files = _files(tmp_path)
    _call(files, "create_structure", file="bar-scene.json")
    assert json.loads(files.read("p1", "bar-scene.json")) == {
        "characters": {},
        "outfits": {},
        "locations": {},
        "frames": [],
    }


def test_create_structure_forces_the_json_extension(tmp_path):
    # safe_name gives an extensionless name .md, which would leave a structure file that is not one
    # -- and every structural tool would then refuse it. The tool bends the name to its own rule,
    # the way write_plan does.
    files = _files(tmp_path)
    _call(files, "create_structure", file="bar-scene")
    assert files.read("p1", "bar-scene.json") is not None


def test_create_structure_refuses_a_name_that_is_taken(tmp_path):
    # Overwriting would delete a scenario the user built, without a word.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    said = _call(files, "create_structure", file="scene.json")
    assert "already" in said.lower()
    assert files.read("p1", "scene.json") == STRUCTURE


def test_create_structure_draws_a_card(tmp_path):
    born = run_tool(_files(tmp_path), "p1", "create_structure", json.dumps({"file": "s.json"}))
    assert born.created == "s.json"


def test_set_character_adds_a_new_one(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "set_character", file="scene.json", name="lara", kind="girl", tags="red hair")
    assert _map_of(files, "scene.json", "characters")["lara"] == {
        "kind": "girl",
        "tags": "red hair",
    }


def test_set_character_changes_the_one_that_is_there(tmp_path):
    # One entry per name, whichever way it was written. A second aylin would leave two answers to
    # the question of what she looks like.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "set_character", file="scene.json", name="aylin", kind="girl", tags="short red")
    characters = _map_of(files, "scene.json", "characters")
    assert list(characters) == ["aylin"]
    assert characters["aylin"]["tags"] == "short red"


def test_set_character_says_whether_it_added_or_changed(tmp_path):
    # set does both, so the answer has to say which -- otherwise a name written twice looks like a
    # name written once.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    born = _call(files, "set_character", file="scene.json", name="lara", kind="girl", tags="red")
    again = _call(files, "set_character", file="scene.json", name="lara", kind="girl", tags="blue")
    assert "Added" in born
    assert "Changed" in again


def test_changing_a_character_says_how_many_frames_name_it(tmp_path):
    # Why the maps exist: one edit reaches every frame that names the entry. The model cannot see
    # how far it just reached unless the answer says so.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    said = _call(files, "set_character", file="scene.json", name="aylin", kind="girl", tags="new")
    assert "2 frames" in said


def test_a_kind_that_is_neither_girl_nor_boy_is_refused(tmp_path):
    # Free text here would break Madde 156's counting quietly, a scenario at a time. A closed set
    # shows the mistake where it is made.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    said = _call(files, "set_character", file="scene.json", name="lara", kind="robot", tags="x")
    assert "girl" in said and "boy" in said
    assert "lara" not in _map_of(files, "scene.json", "characters")


def test_set_character_refuses_a_file_that_is_not_there(tmp_path):
    # And brings none into being. bar-scene.json mistyped as barscene.json would otherwise start a
    # second scenario in silence, and nobody would find out until the prompts came out short.
    files = _files(tmp_path)
    assert "no file by that name" in _call(
        files, "set_character", file="ghost.json", name="lara", kind="girl", tags="red"
    )
    assert files.read("p1", "ghost.json") is None


def test_set_outfit_adds_and_changes(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "set_outfit", file="scene.json", name="palto", tags="long coat")
    assert _map_of(files, "scene.json", "outfits")["palto"] == "long coat"
    _call(files, "set_outfit", file="scene.json", name="palto", tags="short coat")
    assert _map_of(files, "scene.json", "outfits")["palto"] == "short coat"


def test_set_location_adds_and_changes(tmp_path):
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "set_location", file="scene.json", name="rooftop", tags="night, city lights")
    assert _map_of(files, "scene.json", "locations")["rooftop"] == "night, city lights"


def test_only_a_character_carries_a_kind():
    # A parameter the model can see is one it will fill, and an outfit has no kind to give.
    asked = {
        spec["function"]["name"]: spec["function"]["parameters"]["properties"]
        for spec in TOOL_SPECS
    }
    assert "kind" in asked["set_character"]
    assert "kind" not in asked["set_outfit"]
    assert "kind" not in asked["set_location"]


def test_the_character_tool_says_clothing_belongs_elsewhere():
    # Rule 2 of the fourteen, moved to where it is used. In a list carried every turn it was one
    # line among many; here the model meets it while writing the entry it is about.
    said = next(s for s in TOOL_SPECS if s["function"]["name"] == "set_character")
    assert "outfit" in said["function"]["description"].lower()


def test_the_outfit_tool_says_one_entry_dresses_one_person():
    # Rules 8 and 14. One entry covering both put the man in the dress and the woman in the
    # trousers, because whoever names it is handed the whole text.
    said = next(s for s in TOOL_SPECS if s["function"]["name"] == "set_outfit")
    assert "one person" in said["function"]["description"].lower()


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
    # identical sentences was meant. Left visible instead, in the numbers the answer names.
    files = _with(tmp_path, "scene.json", STRUCTURE)
    _call(files, "add_scene", file="scene.json", scenes=["bir"])
    answer = _call(files, "add_scene", file="scene.json", scenes=["bir"])
    assert len(json.loads(files.read("p1", "scene.json"))["frames"]) == 4
    assert "4" in answer


# --- removing what a structure file holds (Madde 157) ---------------------------------------------
#
# A file with something used and something spare in every map, because removal is a question about
# both at once: the used name is refused with its frames named, the spare one goes. Frame 2 is open
# and unwritten, so the middle of the list is a frame rather than a hole.
CROWDED = json.dumps(
    {
        "characters": {
            "aylin": {"kind": "girl", "tags": "long teal hair"},
            "lara": {"kind": "girl", "tags": "red hair"},
        },
        "outfits": {"gecelik": "white nightgown", "palto": "long coat"},
        "locations": {"bedroom": "sunlit bedroom", "rooftop": "night, city lights"},
        "frames": [
            {
                "frame": 1,
                "scene": "bir",
                "characters": {"aylin": ["gecelik"]},
                "location": "bedroom",
                "action": "one",
                "camera": "wide",
            },
            {"frame": 2, "scene": "iki"},
            {
                "frame": 3,
                "scene": "uc",
                "characters": {"aylin": ["gecelik"]},
                "location": "bedroom",
                "action": "three",
                "camera": "close",
            },
        ],
    }
)

REMOVERS = ("remove_character", "remove_outfit", "remove_location", "remove_frame")


@pytest.mark.parametrize(
    "tool,which,name",
    [
        ("remove_character", "characters", "lara"),
        ("remove_outfit", "outfits", "palto"),
        ("remove_location", "locations", "rooftop"),
    ],
)
def test_a_name_no_frame_uses_is_removed(tmp_path, tool, which, name):
    files = _with(tmp_path, "scene.json", CROWDED)
    said = _call(files, tool, file="scene.json", name=name)
    assert name not in _map_of(files, "scene.json", which)
    assert name in said


@pytest.mark.parametrize(
    "tool,which",
    [
        ("remove_character", "characters"),
        ("remove_outfit", "outfits"),
        ("remove_location", "locations"),
    ],
)
def test_removing_a_name_nobody_has_is_refused(tmp_path, tool, which):
    # Silent success is a model believing it deleted something. The sentence is the one
    # build_prompts gives, so a name that is not there reads the same wherever it is met.
    files = _with(tmp_path, "scene.json", CROWDED)
    said = _call(files, tool, file="scene.json", name="ghost")
    assert "ghost" in said and which in said
    assert len(_map_of(files, "scene.json", which)) == 2


@pytest.mark.parametrize(
    "tool,which,name,verb",
    [
        ("remove_character", "characters", "aylin", "in"),
        ("remove_outfit", "outfits", "gecelik", "worn"),
        ("remove_location", "locations", "bedroom", "place"),
    ],
)
def test_a_name_a_frame_uses_is_refused_and_its_frames_named(tmp_path, tool, which, name, verb):
    # Rule 5 of the fourteen, and now the code's answer rather than a line in a list carried every
    # turn. The numbers are the useful half: the model's next move is to fix those frames.
    files = _with(tmp_path, "scene.json", CROWDED)
    said = _call(files, tool, file="scene.json", name=name)
    assert verb in said
    assert "1, 3" in said
    assert name in _map_of(files, "scene.json", which)


@pytest.mark.parametrize("tool", REMOVERS)
def test_removing_from_a_file_that_is_not_there_is_an_answer(tmp_path, tool):
    files = _files(tmp_path)
    said = _call(files, tool, file="ghost.json", name="lara", frame=1)
    assert "no file by that name" in said.lower()


@pytest.mark.parametrize("tool", REMOVERS)
def test_removing_from_a_broken_file_says_what_the_parser_said(tmp_path, tool):
    # A guessed cause sends the model somewhere else, and a broken file is the one case the
    # structural tools cannot repair -- so the sentence has to be the parser's own.
    files = _with(tmp_path, "scene.json", "{ not json")
    said = _call(files, tool, file="scene.json", name="lara", frame=1)
    assert "not valid json" in said.lower()


def test_removing_an_outfit_leaves_a_character_of_the_same_name_alone(tmp_path):
    # Names may repeat across maps: they are keys in different places, and nothing stops a scenario
    # from having a character and a garment called the same thing.
    same = json.loads(CROWDED)
    same["outfits"]["lara"] = "a coat named after nobody"
    files = _with(tmp_path, "scene.json", json.dumps(same))
    _call(files, "remove_outfit", file="scene.json", name="lara")
    assert "lara" not in _map_of(files, "scene.json", "outfits")
    assert "lara" in _map_of(files, "scene.json", "characters")


def test_removing_a_frame_renumbers_the_ones_left(tmp_path):
    files = _with(tmp_path, "scene.json", CROWDED)
    _call(files, "remove_frame", file="scene.json", frame=2)
    frames = _frames_of(files)
    assert [frame["frame"] for frame in frames] == [1, 2]
    # And the one that went is the one that was named. Numbers moving up must not move a different
    # frame into the gap -- which is exactly what a test on the numbers alone would miss.
    assert [frame["scene"] for frame in frames] == ["bir", "uc"]


def test_the_answer_says_how_many_frames_are_left(tmp_path):
    # The model names a frame by its number in the next breath, and this sentence is the only place
    # it can learn that everything after the gap has moved.
    files = _with(tmp_path, "scene.json", CROWDED)
    assert "2 frames" in _call(files, "remove_frame", file="scene.json", frame=1)


def test_removing_a_frame_that_is_not_there_says_how_many_there_are(tmp_path):
    files = _with(tmp_path, "scene.json", CROWDED)
    said = _call(files, "remove_frame", file="scene.json", frame=9)
    assert "3" in said and "9" in said
    assert len(_frames_of(files)) == 3


@pytest.mark.parametrize("number", [0, -1])
def test_a_frame_number_below_one_is_refused(tmp_path, number):
    # The one that would pass unnoticed: frames[-1] is legal Python, and it would quietly take the
    # last frame away when nothing of the sort was meant.
    files = _with(tmp_path, "scene.json", CROWDED)
    said = _call(files, "remove_frame", file="scene.json", frame=number)
    assert len(_frames_of(files)) == 3
    # The number back in the sentence, so the refusal is about what was asked for rather than a
    # general complaint -- and so this test cannot pass on a tool that does not exist yet.
    assert str(number) in said


def test_a_frame_number_written_as_digits_is_taken(tmp_path):
    # Models send "2" for 2 often enough that refusing it would be a refusal about typing rather
    # than about the file, and there is only one way to read it.
    files = _with(tmp_path, "scene.json", CROWDED)
    _call(files, "remove_frame", file="scene.json", frame="2")
    assert [frame["scene"] for frame in _frames_of(files)] == ["bir", "uc"]


@pytest.mark.parametrize("number", ["iki", None, 1.5, ""])
def test_something_that_is_not_a_frame_number_is_refused(tmp_path, number):
    # 1.5 among them on purpose: int() would round it down and take frame 1 away, which is the
    # quietest way there is to lose somebody's work.
    files = _with(tmp_path, "scene.json", CROWDED)
    said = _call(files, "remove_frame", file="scene.json", frame=number)
    assert len(_frames_of(files)) == 3
    assert "number" in said.lower()


def test_removing_the_last_frame_leaves_the_file_with_none(tmp_path):
    one = json.loads(CROWDED)
    one["frames"] = one["frames"][:1]
    files = _with(tmp_path, "scene.json", json.dumps(one))
    said = _call(files, "remove_frame", file="scene.json", frame=1)
    assert _frames_of(files) == []
    assert "no frames" in said.lower()


def test_a_frame_that_is_already_written_is_removed_too(tmp_path):
    # No guard on a written frame. Removing one is not an accident to be caught, it is the ordinary
    # thing to do with a beat that left the scenario.
    files = _with(tmp_path, "scene.json", CROWDED)
    _call(files, "remove_frame", file="scene.json", frame=1)
    assert [frame["scene"] for frame in _frames_of(files)] == ["iki", "uc"]


def test_removing_never_draws_a_card(tmp_path):
    # A card announces a file that was born. Nothing is born here, and one drawn on a removal would
    # put the scenario's name on the screen as though it had just started.
    files = _with(tmp_path, "scene.json", CROWDED)
    for tool, arguments in (
        ("remove_character", {"file": "scene.json", "name": "lara"}),
        ("remove_outfit", {"file": "scene.json", "name": "palto"}),
        ("remove_location", {"file": "scene.json", "name": "rooftop"}),
        ("remove_frame", {"file": "scene.json", "frame": 1}),
    ):
        ran = run_tool(files, "p1", tool, json.dumps(arguments))
        assert ran.created is None
        # Asked as well, because created is None for a tool nobody knows too -- and this claim is
        # about a removal that happened, not about a name run_tool did not recognise.
        assert ran.outcome != "Unknown tool"


# --- correcting a frame that is already written (Madde 158) ---------------------------------------
#
# The last of the holes Madde 151 opened. CROWDED serves it whole: frames 1 and 3 are written, frame
# 2 carries a scene and nothing else, so what may be updated and what may not are both already there.


def _frame_at(files, number, name="scene.json"):
    return _frames_of(files, name)[number - 1]


def test_updating_one_field_leaves_the_rest_of_the_frame_alone(tmp_path):
    # The whole of the tool in one line, and the half a test can miss: proving the camera changed
    # says nothing about whether the action survived.
    files = _with(tmp_path, "scene.json", CROWDED)
    _call(files, "update_frame", file="scene.json", frame=1, camera="close-up, from below")
    frame = _frame_at(files, 1)
    assert frame["camera"] == "close-up, from below"
    assert frame["action"] == "one"
    assert frame["location"] == "bedroom"
    assert frame["characters"] == {"aylin": ["gecelik"]}
    assert frame["scene"] == "bir"


def test_several_fields_change_in_one_call(tmp_path):
    files = _with(tmp_path, "scene.json", CROWDED)
    _call(files, "update_frame", file="scene.json", frame=1, action="standing", camera="full body")
    frame = _frame_at(files, 1)
    assert frame["action"] == "standing" and frame["camera"] == "full body"


def test_the_scene_is_corrected_by_the_same_tool(tmp_path):
    # No update_scene. Updating is one action on a frame whatever field it lands on, and a fifth
    # tool would teach the model nothing it does not already know.
    files = _with(tmp_path, "scene.json", CROWDED)
    _call(files, "update_frame", file="scene.json", frame=1, scene="bambaska bir an")
    frame = _frame_at(files, 1)
    assert frame["scene"] == "bambaska bir an"
    assert frame["action"] == "one"


def test_who_is_in_the_frame_can_be_changed(tmp_path):
    files = _with(tmp_path, "scene.json", CROWDED)
    _call(files, "update_frame", file="scene.json", frame=1, characters={"lara": ["palto"]})
    assert _frame_at(files, 1)["characters"] == {"lara": ["palto"]}


def test_a_frame_with_no_prompt_yet_is_refused(tmp_path):
    # write, not update. The two being separate is what keeps the intent in every call and stops a
    # frame nobody has written from being half-filled by hand.
    files = _with(tmp_path, "scene.json", CROWDED)
    said = _call(files, "update_frame", file="scene.json", frame=2, camera="close")
    assert "write_frame_prompt" in said
    assert "camera" not in _frame_at(files, 2)


def test_a_call_that_changes_nothing_is_refused(tmp_path):
    # Silent success is a model believing it did something. A call carrying only the file and the
    # number is asking for nothing.
    files = _with(tmp_path, "scene.json", CROWDED)
    said = _call(files, "update_frame", file="scene.json", frame=1)
    assert "nothing" in said.lower()
    assert _frame_at(files, 1)["action"] == "one"


def test_one_field_nobody_knows_refuses_the_whole_call(tmp_path):
    # Madde 152's rule, kept. Writing the known half and dropping the rest would have the model
    # believing it wrote a frame that does not exist.
    files = _with(tmp_path, "scene.json", CROWDED)
    said = _call(files, "update_frame", file="scene.json", frame=1, camera="close", mood="tense")
    assert "mood" in said
    assert _frame_at(files, 1)["camera"] == "wide"


def test_a_character_no_map_knows_is_refused_before_anything_is_written(tmp_path):
    files = _with(tmp_path, "scene.json", CROWDED)
    said = _call(files, "update_frame", file="scene.json", frame=1, characters={"ghost": []})
    assert "ghost" in said and "aylin" in said
    assert _frame_at(files, 1)["characters"] == {"aylin": ["gecelik"]}


def test_an_outfit_no_map_knows_is_refused_the_same_way(tmp_path):
    files = _with(tmp_path, "scene.json", CROWDED)
    said = _call(files, "update_frame", file="scene.json", frame=1, characters={"lara": ["yok"]})
    assert "yok" in said and "gecelik" in said
    assert _frame_at(files, 1)["characters"] == {"aylin": ["gecelik"]}


def test_a_character_wearing_nothing_is_not_a_mistake(tmp_path):
    # The schema's own rule since outfits existed: a name with no outfit is an empty list. What is
    # refused is a name that does not exist, never the absence of one.
    files = _with(tmp_path, "scene.json", CROWDED)
    _call(files, "update_frame", file="scene.json", frame=1, characters={"lara": []})
    assert _frame_at(files, 1)["characters"] == {"lara": []}


def test_updating_a_frame_that_is_not_there_says_how_many_there_are(tmp_path):
    files = _with(tmp_path, "scene.json", CROWDED)
    said = _call(files, "update_frame", file="scene.json", frame=9, camera="close")
    assert "3" in said and "9" in said


@pytest.mark.parametrize("number", [0, -1])
def test_updating_a_frame_below_one_is_refused(tmp_path, number):
    # frames[-1] again, and it would rewrite the last frame rather than remove it -- quieter still.
    files = _with(tmp_path, "scene.json", CROWDED)
    said = _call(files, "update_frame", file="scene.json", frame=number, camera="from behind")
    assert str(number) in said
    # The last frame specifically, because that is the one frames[-1] would have reached.
    assert _frame_at(files, 3)["camera"] == "close"


def test_a_frame_number_written_as_digits_is_taken_by_update_too(tmp_path):
    files = _with(tmp_path, "scene.json", CROWDED)
    _call(files, "update_frame", file="scene.json", frame="3", camera="from behind")
    assert _frame_at(files, 3)["camera"] == "from behind"


def test_updating_in_a_file_that_is_not_there_is_an_answer(tmp_path):
    said = _call(_files(tmp_path), "update_frame", file="ghost.json", frame=1, camera="close")
    assert "no file by that name" in said.lower()


def test_updating_in_a_broken_file_says_what_the_parser_said(tmp_path):
    files = _with(tmp_path, "scene.json", "{ not json")
    said = _call(files, "update_frame", file="scene.json", frame=1, camera="close")
    assert "not valid json" in said.lower()


def test_an_update_leaves_the_frames_own_number_where_it_was(tmp_path):
    # The stamp is the code's (Madde 153) and an update is not a place for it to move or vanish.
    files = _with(tmp_path, "scene.json", CROWDED)
    _call(files, "update_frame", file="scene.json", frame=3, camera="from behind")
    # The change asked for as well, or the numbers would be right on a file nothing had touched.
    assert _frame_at(files, 3)["camera"] == "from behind"
    assert [frame["frame"] for frame in _frames_of(files)] == [1, 2, 3]


def test_updating_never_draws_a_card(tmp_path):
    files = _with(tmp_path, "scene.json", CROWDED)
    ran = run_tool(
        files, "p1", "update_frame", json.dumps({"file": "scene.json", "frame": 1, "camera": "c"})
    )
    assert ran.created is None
    assert ran.outcome != "Unknown tool"
