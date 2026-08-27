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


def test_listing_an_empty_project_says_so_in_words(tmp_path):
    assert "no files yet" in _call(_files(tmp_path), "list_files")


def test_listing_names_the_files(tmp_path):
    files = _files(tmp_path)
    _call(files, "create_file", name="plan.md", content="a")
    assert _call(files, "list_files") == "plan.md"


def test_reading_gives_the_contents(tmp_path):
    files = _files(tmp_path)
    _call(files, "create_file", name="plan.md", content="the body")
    assert _call(files, "read_file", name="plan.md") == "the body"


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
    assert _call(files, "read_file", name="plan.md") == "first"
    # And no copy beside it: refusing means one document, which was the whole point.
    assert _call(files, "list_files") == "plan.md"


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
    assert _call(files, "read_file", name="bar-scene-plan.md") == "1. ..."
    # A name that already says it is a plan is not made to say it twice.
    assert "bar-scene-plan.md" in _call(files, "write_plan", name="bar-scene-plan.md", content="x")


def test_writing_a_plan_again_replaces_it(tmp_path):
    # Unlike create_file, which never overwrites. A second plan sitting in bar-scene-plan-2.md would
    # lose which of the two is the one to follow.
    files = _files(tmp_path)
    _call(files, "write_plan", name="bar-scene", content="first")
    _call(files, "write_plan", name="bar-scene", content="second")
    assert _call(files, "read_file", name="bar-scene-plan.md") == "second"
    assert _call(files, "list_files") == "bar-scene-plan.md"


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
    assert "not valid JSON" in run_tool(_files(tmp_path), "p1", "list_files", "{oops").text


def test_only_creating_reports_a_born_file(tmp_path):
    files = _files(tmp_path)
    created = run_tool(files, "p1", "create_file", json.dumps({"name": "a", "content": "x"}))
    listed = run_tool(files, "p1", "list_files", "{}")
    # What the model is told and whether a file was born are two questions, so they travel apart.
    assert created.created == "a.md"
    assert listed.created is None


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
    assert _call(_files(tmp_path), "read_schema") == SCHEMA


def test_the_schema_tool_brings_no_file_into_being(tmp_path):
    assert run_tool(_files(tmp_path), "p1", "read_schema", "{}").created is None


def test_the_schema_tool_says_what_it_answered_with(tmp_path):
    # A reader's line rather than the answer itself, like every other outcome.
    assert run_tool(_files(tmp_path), "p1", "read_schema", "{}").outcome == "Schema"


def test_every_tool_is_declared_to_the_model():
    assert {spec["function"]["name"] for spec in TOOL_SPECS} == {
        "list_files",
        "read_file",
        "create_file",
        "edit_file",
        "build_prompts",
        # Sixth since Madde 91, and declared here with the rest: which modes offer it is a separate
        # question, asked in modes.py.
        "write_plan",
        # Seventh since Madde 96. The shape of a structure file stopped being a paragraph in a
        # skill's text; it is fetched when a file is about to be written.
        "read_schema",
    }


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


def test_listing_has_no_target_to_report(tmp_path):
    # Empty rather than invented: the call really is about nothing in particular.
    assert _target(_files(tmp_path), "list_files") == ""


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


def test_listing_says_how_many_files_there_are(tmp_path):
    files = _files(tmp_path)
    _call(files, "create_file", name="plan.md", content="a")
    _call(files, "create_file", name="notes.md", content="b")
    assert _outcome(files, "list_files") == "2 files"


def test_listing_nothing_says_so_rather_than_counting_to_zero(tmp_path):
    assert _outcome(_files(tmp_path), "list_files") == "No files"


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
