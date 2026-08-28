"""What the context box remembers (Madde 129).

The box is derived rather than stored: a chat's record already says which tool touched which file
(Madde 66 and 78), so the names come from there and the contents are read from disk at the moment
the request is built. Nothing is copied, so nothing can go stale.

The module is imported inside each test rather than at the top, for the reason test_modes.py gives:
a module that does not exist yet fails this whole file's collection, and then none of the turn's
other reds are visible anywhere in the suite.
"""
from backend.features.workspace.domain.chat import Chat, Message, ToolCall

NOW = "2026-08-09T11:04:00.000+00:00"


def _opened(chat, steps=()):
    from backend.features.workspace.domain.context_box import files_opened

    return files_opened(chat, steps)


def _chat(*turns):
    """A chat whose answers took the given steps -- one answer per argument."""
    return Chat(
        "c1",
        "t",
        NOW,
        tuple(Message("ai", NOW, "ok", calls=tuple(calls)) for calls in turns),
    )


def _read(name):
    return ToolCall("read_file", name, "5 lines")


def test_a_file_that_was_read_is_in_the_box():
    assert _opened(_chat([_read("plan.md")])) == ["plan.md"]


def test_the_newest_read_leads():
    # Newest first, because what falls off the end is what has been out of sight longest.
    assert _opened(_chat([_read("a.md"), _read("b.md")])) == ["b.md", "a.md"]


def test_the_same_file_read_twice_is_one_entry():
    # The whole point: the trial read one file three times and paid for it three times over.
    assert _opened(_chat([_read("a.md"), _read("b.md"), _read("a.md")])) == ["a.md", "b.md"]


def test_only_the_last_five_survive():
    from backend.features.workspace.domain.context_box import BOX_LIMIT

    reads = [_read(f"{number}.md") for number in range(1, 7)]
    assert BOX_LIMIT == 5
    # The oldest falls out rather than the newest: a chat that keeps working must not lose what it
    # is working on.
    assert _opened(_chat(reads)) == ["6.md", "5.md", "4.md", "3.md", "2.md"]


def test_a_write_alone_does_not_put_a_file_in_the_box():
    # Only the tools whose result carries meaning go in -- the user's own words, 29 Aug. A write
    # answers in one sentence, and one sentence needs no box.
    written = [
        ToolCall("create_file", "new.md", "Saved"),
        ToolCall("edit_file", "new.md", "Edited"),
        ToolCall("build_prompts", "frames.json", "12 prompts"),
    ]
    assert _opened(_chat(written)) == []


def test_a_file_that_was_written_after_being_read_stays():
    # And keeps its place: the box shows it as it is now, which is what makes the read-back
    # unnecessary.
    turn = [_read("plan.md"), ToolCall("edit_file", "plan.md", "Edited")]
    assert _opened(_chat(turn)) == ["plan.md"]


def test_this_turns_reads_are_in_the_box_before_the_record_is():
    # A turn's steps reach the record only when the answer is written. The next round is inside
    # the same turn, so the box has to hear about a read before that.
    assert _opened(_chat([]), steps=[_read("fresh.md")]) == ["fresh.md"]


def test_this_turns_reads_lead_the_older_ones():
    assert _opened(_chat([_read("old.md")]), steps=[_read("new.md")]) == ["new.md", "old.md"]


def test_a_chat_that_read_nothing_has_an_empty_box():
    assert _opened(_chat([])) == []
    assert _opened(Chat("c1", "t", NOW)) == []


def test_a_read_that_found_nothing_is_not_in_the_box():
    # The call happened, so the record keeps it -- but there is no file to put in front of the
    # model, and a name with nothing behind it would read as an empty file.
    assert _opened(_chat([ToolCall("read_file", "ghost.md", "No file by that name")])) == []


def _schema_read(chat, steps=()):
    from backend.features.workspace.domain.context_box import schema_was_read

    return schema_was_read(chat, steps)


def test_the_schema_is_remembered_separately():
    # It is not a project file: one text for the whole app, and no name to look up on disk.
    assert _schema_read(_chat([ToolCall("read_prompt_structure_schema", "", "Schema")]))
    assert not _schema_read(_chat([_read("plan.md")]))


def test_the_schema_is_remembered_from_this_turn_too():
    assert _schema_read(_chat([]), steps=[ToolCall("read_prompt_structure_schema", "", "Schema")])
