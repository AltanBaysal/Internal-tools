import json

import pytest

from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.domain.naming import unique_name
from backend.features.workspace.domain.tools import (
    DEFAULT_NAME,
    TOOL_SPECS,
    run_tool,
    safe_name,
)
from backend.services.store.store import Store


def _files(tmp_path):
    return FileFileStore(Store(str(tmp_path)))


def _call(files, tool, **arguments):
    return run_tool(files, "p1", tool, json.dumps(arguments)).text


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


def test_creating_reports_the_name_actually_used(tmp_path):
    files = _files(tmp_path)
    _call(files, "create_file", name="plan.md", content="first")
    assert "plan-2.md" in _call(files, "create_file", name="plan.md", content="second")
    # Nothing was overwritten: both are still there.
    assert _call(files, "read_file", name="plan.md") == "first"


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


def test_every_tool_is_declared_to_the_model():
    assert {spec["function"]["name"] for spec in TOOL_SPECS} == {
        "list_files",
        "read_file",
        "create_file",
    }
