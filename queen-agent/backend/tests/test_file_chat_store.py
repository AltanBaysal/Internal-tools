import json
from dataclasses import replace

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.chat import Chat, ChatSummary, Message, ToolCall, Usage
from backend.features.workspace.domain.project import Project
from backend.services.store.store import Store

BORN = "2026-08-09T11:04:00+00:00"


def _chat(chat_id="c1", text="Hello"):
    return Chat(
        id=chat_id,
        title=text,
        created_at=BORN,
        messages=(Message(role="user", at=BORN, text=text),),
    )


def _wired(tmp_path):
    """The raw store and a chat store over a root holding one project, p1."""
    raw = Store(str(tmp_path))
    projects = FileProjectStore(raw)
    projects.add(Project(id="p1", name="Thesis", created_at=BORN))
    return raw, FileChatStore(raw, projects), projects


def _round_trip(tmp_path, chat):
    # Written, then read by a store built afresh on the same root -- what a restart does.
    raw, chats, projects = _wired(tmp_path)
    chats.add("p1", chat)
    projects.flush()
    return FileChatStore(raw, FileProjectStore(raw)).get("p1", chat.id)


def _hand_written(tmp_path, text, chat_id="old"):
    """A chat file an older version left on disk, with its row in projects.json."""
    raw, chats, projects = _wired(tmp_path)
    raw.write_text(f"p1/chats/{chat_id}.json", text)
    projects.put_chat("p1", Chat(id=chat_id, title="Old", created_at=BORN))
    return chats


def test_a_chat_survives_a_new_store_instance(tmp_path):
    assert _round_trip(tmp_path, _chat()) == _chat()


def test_the_id_is_the_file_name_and_is_not_repeated_inside(tmp_path):
    raw, chats, _ = _wired(tmp_path)
    chats.add("p1", _chat())
    assert "c1" not in raw.read_text("p1/chats/c1.json")


def test_a_chat_that_still_carries_a_skill_on_disk_is_read_without_it(tmp_path):
    # Madde 86 took the field out. Every chat written before it has a skill key sitting in its
    # JSON; nothing reads it, and nothing puts one back -- the same shape Madde 82 left behind.
    chats = _hand_written(
        tmp_path,
        '{"title": "Old", "createdAt": "2026-08-09T11:04:00+00:00", "skill": "verify-prompts",'
        ' "messages": [{"role": "user", "at": "2026-08-09T11:04:00+00:00", "text": "hi",'
        ' "skill": "verify-prompts"}]}',
    )
    old = chats.get("p1", "old")
    assert not hasattr(old, "skill")
    # A different field with the same name, and this one is still read.
    assert old.messages[0].skill == "verify-prompts"


def test_the_skill_a_message_was_sent_with_survives_the_disk(tmp_path):
    written = replace(
        _chat(),
        messages=(Message(role="user", at=BORN, text="hi", skill="verify"),),
    )
    assert _round_trip(tmp_path, written).messages[0].skill == "verify"


def test_a_message_with_no_skill_writes_no_field(tmp_path):
    raw, chats, _ = _wired(tmp_path)
    chats.add("p1", _chat())
    assert "skill" not in raw.read_text("p1/chats/c1.json")


def test_the_model_a_message_was_sent_with_survives_the_disk(tmp_path):
    # Written by Madde 146 to 357, and kept since 358 as a record: a chat written again after a new
    # message must not strip its older turns of the model that answered them.
    written = replace(
        _chat(),
        messages=(Message(role="user", at=BORN, text="hi", model="deepseek-v4-pro"),),
    )
    assert _round_trip(tmp_path, written).messages[0].model == "deepseek-v4-pro"


def test_a_message_with_no_model_writes_no_field(tmp_path):
    # Every message written before Madde 146 has none, and so does every one since Madde 358.
    raw, chats, _ = _wired(tmp_path)
    chats.add("p1", _chat())
    assert "model" not in raw.read_text("p1/chats/c1.json")


def test_the_two_model_fields_are_not_the_same_field(tmp_path):
    # The pair that keeps Madde 146 honest. Madde 82 took `model` off the CHAT and that stays gone;
    # this madde put one on the MESSAGE. They share a name and nothing else, and a record carrying
    # both must lose the first and keep the second -- exactly what the skill pair above does.
    chats = _hand_written(
        tmp_path,
        '{"title": "Old", "createdAt": "2026-08-09T11:04:00+00:00", "model": "deepseek-v4-pro",'
        ' "messages": [{"role": "user", "at": "2026-08-09T11:04:00+00:00", "text": "hi",'
        ' "model": "deepseek-v4-flash"}]}',
    )
    old = chats.get("p1", "old")
    assert not hasattr(old, "model")
    assert old.messages[0].model == "deepseek-v4-flash"


def test_a_chat_written_before_skills_existed_still_reads(tmp_path):
    # There are records on disk already. They have no such field and must not need a migration.
    chats = _hand_written(
        tmp_path,
        '{"title": "Old", "createdAt": "2026-08-09T11:04:00+00:00",'
        ' "messages": [{"role": "user", "at": "2026-08-09T11:04:00+00:00", "text": "hi"}]}',
    )
    assert chats.get("p1", "old").messages[0].skill == ""


def test_a_chat_that_still_carries_a_model_on_disk_is_read_without_it(tmp_path):
    # Madde 82 took the field out. Every chat written before it has a model key sitting in its
    # JSON, and reading one must not fail over a word nothing asks about any more -- it simply
    # drops the next time the chat is written.
    chats = _hand_written(
        tmp_path,
        '{"title": "Old", "createdAt": "2026-08-09T11:04:00+00:00", "messages": [],'
        ' "model": "deepseek-v4-pro"}',
    )
    old = chats.get("p1", "old")
    assert old.title == "Old"
    assert not hasattr(old, "model")


# --- what projects.json knows of a chat (Madde 447) ----------------------------------------------


def test_an_unknown_chat_is_none_without_going_to_the_disk(tmp_path):
    # A chat id from the address becomes a path only once projects.json names it.
    raw, chats, _ = _wired(tmp_path)
    raw.write_text("p1/chats/stray.json", "not a chat at all")
    assert chats.get("p1", "nope") is None
    assert chats.get("p1", "stray") is None, "projects.json'da olmayan bir sohbet diskten okundu"
    assert chats.get("p9", "c1") is None


def test_a_row_whose_chat_file_is_gone_reads_as_none(tmp_path):
    raw, chats, _ = _wired(tmp_path)
    chats.add("p1", _chat())
    raw.move("p1/chats/c1.json", "elsewhere/c1.json")
    assert chats.get("p1", "c1") is None, "Dosyası gitmiş sohbet bulunmadı yerine çöktü"


def test_a_project_without_chats_lists_nothing(tmp_path):
    _, chats, _ = _wired(tmp_path)
    assert chats.list_for("p1") == []
    assert chats.list_for("p9") == []


def test_writing_a_chat_puts_its_row(tmp_path):
    raw, chats, _ = _wired(tmp_path)
    chats.add("p1", _chat())
    later = replace(_chat(), messages=_chat().messages + (Message("ai", "2026-08-09T11:09:00+00:00", "Hi"),))
    chats.replace("p1", later)
    assert chats.list_for("p1") == [
        ChatSummary("c1", "Hello", BORN, "2026-08-09T11:09:00+00:00")
    ], "Sohbetin satırı yazınca gelmedi ya da yenilenmedi"


def test_a_chats_mode_is_its_row_s_and_never_its_file_s(tmp_path):
    # Madde 463: a setting of the chat, held where its list is -- not in what it said.
    raw, chats, _ = _wired(tmp_path)
    chats.add("p1", _chat())
    assert chats.mode_of("p1", "c1") == "edit"
    assert chats.set_mode("p1", "c1", "ask") is True
    assert chats.mode_of("p1", "c1") == "ask"
    assert "mode" not in json.loads(raw.read_text("p1/chats/c1.json")), "Mod sohbet dosyasına yazıldı"
    assert chats.mode_of("p1", "ghost") is None and chats.set_mode("p1", "ghost", "ask") is False


def test_the_list_opens_no_chat(tmp_path):
    raw, chats, _ = _wired(tmp_path)
    chats.add("p1", _chat())
    # The file can say anything now: the list is answered from projects.json.
    raw.write_text("p1/chats/c1.json", "not json")
    assert [chat.id for chat in chats.list_for("p1")] == ["c1"]


def test_the_chat_is_written_before_its_row(tmp_path):
    raw = Store(str(tmp_path))
    projects = FileProjectStore(raw)
    projects.add(Project(id="p1", name="Thesis", created_at=BORN))
    seen = []

    class Watching:
        def put_chat(self, project_id, chat):
            seen.append(raw.list_dir(f"{project_id}/chats"))
            projects.put_chat(project_id, chat)

    FileChatStore(raw, Watching()).add("p1", _chat())
    assert seen == [["c1.json"]], "Sohbetin satırı içeriğinden önce yazıldı"


# --- the calls a message carries (Madde 66) ------------------------------------------------------


def _answered(*calls):
    return replace(
        _chat(),
        messages=(
            Message(role="ai", at="2026-08-09T11:05:00+00:00", text="Read it.", calls=calls),
        ),
    )


def test_the_calls_an_answer_made_survive_a_round_trip(tmp_path):
    chat = _answered(ToolCall("read_file", "plan.md"), ToolCall("list_files", ""))
    assert _round_trip(tmp_path, chat) == chat


def test_a_message_that_called_nothing_writes_no_field(tmp_path):
    # An empty list is noise on disk, exactly as an empty file list is.
    raw, chats, _ = _wired(tmp_path)
    chats.add("p1", _chat())
    assert "calls" not in raw.read_text("p1/chats/c1.json")


def test_a_call_with_no_target_writes_no_target(tmp_path):
    raw, chats, _ = _wired(tmp_path)
    chats.add("p1", _answered(ToolCall("list_files", "")))
    assert "target" not in raw.read_text("p1/chats/c1.json")


def test_how_a_call_went_survives_a_round_trip(tmp_path):
    chat = _answered(ToolCall("read_file", "plan.md", "45 lines"))
    assert _round_trip(tmp_path, chat) == chat


def test_a_call_with_nothing_to_say_writes_no_outcome(tmp_path):
    # The same rule one field over: a call recorded before this existed carries none.
    raw, chats, _ = _wired(tmp_path)
    chats.add("p1", _answered(ToolCall("list_files", "")))
    assert "outcome" not in raw.read_text("p1/chats/c1.json")


def test_a_stopped_answer_survives_a_round_trip(tmp_path):
    chat = replace(
        _chat(),
        messages=(
            Message(role="ai", at="2026-08-09T11:05:00+00:00", text="Half a", stopped=True),
        ),
    )
    assert _round_trip(tmp_path, chat) == chat


def test_an_answer_that_was_not_stopped_writes_no_field(tmp_path):
    raw, chats, _ = _wired(tmp_path)
    chats.add("p1", _chat())
    assert "stopped" not in raw.read_text("p1/chats/c1.json")


def test_a_chat_written_before_calls_existed_reads_back_empty(tmp_path):
    # No migration: the field is absent, and absent is what empty means.
    chats = _hand_written(
        tmp_path,
        json.dumps(
            {
                "title": "Hello",
                "createdAt": BORN,
                "messages": [{"role": "ai", "at": BORN, "text": "hi"}],
            }
        ),
        chat_id="c1",
    )
    assert chats.get("p1", "c1").messages[0].calls == ()
    # The same absence, one field over: nothing written before today was ever stopped.
    assert chats.get("p1", "c1").messages[0].stopped is False
    # And one more: nothing written before today was ever measured.
    assert chats.get("p1", "c1").messages[0].usage == Usage()


# --- what the answer spent (Madde 68) ------------------------------------------------------------


def _spent():
    return replace(
        _chat(),
        messages=(
            Message(
                role="ai",
                at="2026-08-09T11:05:00+00:00",
                text="Here it is.",
                usage=Usage(sent=12400, cached=9100, answered=842),
            ),
        ),
    )


def test_what_an_answer_spent_survives_a_round_trip(tmp_path):
    assert _round_trip(tmp_path, _spent()) == _spent()


def test_what_an_answer_spent_is_written_as_three_numbers(tmp_path):
    # Madde 337: the ceiling reads the messages now, and nothing reads the last round's size.
    raw, chats, _ = _wired(tmp_path)
    chats.add("p1", _spent())
    stored = json.loads(raw.read_text("p1/chats/c1.json"))["messages"][0]["usage"]
    assert stored == {"sent": 12400, "cached": 9100, "answered": 842}


def test_a_chat_written_with_the_last_rounds_size_still_reads(tmp_path):
    # Every chat answered between Madde 133 and 337 carries the key. No migration: it is ignored,
    # and it drops the next time the chat is written.
    chats = _hand_written(
        tmp_path,
        '{"title": "Old", "createdAt": "2026-08-09T11:04:00+00:00", "messages": ['
        '{"role": "ai", "at": "2026-08-09T11:05:00+00:00", "text": "hi",'
        ' "usage": {"sent": 12400, "cached": 9100, "answered": 842, "context": 11400}}]}',
    )
    assert chats.get("p1", "old").messages[0].usage == Usage(12400, 9100, 842)


def test_an_answer_nobody_measured_writes_no_field(tmp_path):
    # An all-zero object is noise on disk, exactly as an empty file list is.
    raw, chats, _ = _wired(tmp_path)
    chats.add("p1", _chat())
    assert "usage" not in raw.read_text("p1/chats/c1.json")


# --- the lines a chat holds (Madde 195) ----------------------------------------------------------


def _versioned():
    from backend.features.workspace.domain.chat import Version

    return replace(
        _chat(),
        versions=(
            Version(id="l2", parent="", at=1, messages=(Message(role="user", at=BORN, text="again"),)),
        ),
        active="l2",
    )


def test_the_lines_a_chat_holds_survive_the_disk(tmp_path):
    assert _round_trip(tmp_path, _versioned()) == _versioned()


def test_a_version_writes_where_it_split_and_what_it_said(tmp_path):
    # The prefix is deliberately not among them: it belongs to the line the version grew out of, and
    # a copy of it here is the second place for one conversation to be written down.
    raw, chats, _ = _wired(tmp_path)
    chats.add("p1", _versioned())
    stored = json.loads(raw.read_text("p1/chats/c1.json"))
    assert stored["active"] == "l2"
    assert stored["versions"] == [
        {
            "id": "l2",
            "parent": "",
            "at": 1,
            "messages": [{"role": "user", "at": BORN, "text": "again"}],
        }
    ]


def test_a_chat_that_never_branched_writes_neither_field(tmp_path):
    # The rule every other field on this record keeps: what is empty is not written down.
    raw, chats, _ = _wired(tmp_path)
    chats.add("p1", _chat())
    written = raw.read_text("p1/chats/c1.json")
    assert "versions" not in written
    assert "active" not in written


def test_a_chat_written_before_this_reads_as_one_line(tmp_path):
    # Every chat on disk today. No migration is owed: the fields fill themselves the first time
    # somebody edits a message.
    chats = _hand_written(
        tmp_path,
        '{"title": "Old", "createdAt": "2026-08-09T11:04:00+00:00",'
        ' "messages": [{"role": "user", "at": "2026-08-09T11:04:00+00:00", "text": "hi"}]}',
    )
    old = chats.get("p1", "old")
    assert old.versions == ()
    assert old.active == ""


# --- the trim (Madde 345) ------------------------------------------------------------------------


def _trimmed(count):
    return replace(
        _chat(),
        messages=(
            Message(role="ai", at="2026-08-09T11:05:00+00:00", text="Here it is.", trimmed=count),
        ),
    )


def test_a_trim_survives_a_round_trip(tmp_path):
    assert _round_trip(tmp_path, _trimmed(4)) == _trimmed(4)
    raw = Store(str(tmp_path))
    assert json.loads(raw.read_text("p1/chats/c1.json"))["messages"][0]["trimmed"] == 4


def test_a_message_that_trimmed_nothing_writes_no_field_and_reads_zero(tmp_path):
    # The rule every other field on the record keeps, and no migration: every chat on disk today
    # reads as untrimmed.
    raw, chats, _ = _wired(tmp_path)
    chats.add("p1", _chat())
    assert "trimmed" not in raw.read_text("p1/chats/c1.json")
    assert chats.get("p1", "c1").messages[0].trimmed == 0


# --- the failed answer (Madde 440) ---------------------------------------------------------------


def _failed():
    return replace(
        _chat(),
        messages=(
            Message(role="ai", at="2026-08-09T11:05:00+00:00", text="HTTP 502", failed="technical"),
        ),
    )


def test_a_failed_answer_survives_a_round_trip(tmp_path):
    # On disk so the card stays on a reload and when the chat is opened again.
    assert _round_trip(tmp_path, _failed()) == _failed()
    raw = Store(str(tmp_path))
    assert json.loads(raw.read_text("p1/chats/c1.json"))["messages"][0]["failed"] == "technical"


def test_a_real_answer_writes_no_failed_field_and_reads_empty(tmp_path):
    raw, chats, _ = _wired(tmp_path)
    chats.add("p1", _chat())
    assert "failed" not in raw.read_text("p1/chats/c1.json")
    assert chats.get("p1", "c1").messages[0].failed == ""
