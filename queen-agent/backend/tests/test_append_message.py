import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.errors import ChatNotFound, EmptyMessage
from backend.features.workspace.domain.usecases.append_message import append_message
from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.list_chats import list_chats
from backend.services.store.store import Store


def _stores(tmp_path):
    store = Store(str(tmp_path))
    return FileProjectStore(store), FileChatStore(store)


def _made(projects, chats, project_id, chat_id, text, now):
    # Making a chat goes through the rule itself since Madde 87: naming no chat is what asks for
    # one, and the id it is handed is the id it gets.
    return append_message(
        chats, project_id, "", text, now, project_store=projects, new_id=chat_id
    )


def _chat(projects, chats, project_id, chat_id, text, now):
    # A chat always lives in a project, so the project is made first.
    create_project(projects, new_id=project_id, now=now)
    return _made(projects, chats, project_id, chat_id, text, now)


def _seeded(tmp_path):
    projects, chats = _stores(tmp_path)
    _chat(projects, chats, "p1", "c1", "Write the intro", "2026-08-09T11:04:00.000+00:00")
    return projects, chats


def test_with_no_chat_named_the_rule_creates_one(tmp_path):
    # Madde 87: start_chat's job moved here. A message with no chat to land in makes the chat, and
    # the id it is given is the id it gets -- minting one is the route's job, not this rule's.
    projects, chats = _stores(tmp_path)
    create_project(projects, new_id="p1", now="2026-08-09T11:04:00.000+00:00")
    chat = append_message(
        chats,
        "p1",
        "",
        "Write the intro",
        "2026-08-09T11:04:00.000+00:00",
        skill="create-scenario",
        project_store=projects,
        new_id="c9",
    )
    assert chat.id == "c9"
    assert chat.title == "Write the intro"
    assert [(m.role, m.text, m.skill) for m in chat.messages] == [
        ("user", "Write the intro", "create-scenario")
    ]
    # And it is on disk, not only in what came back.
    assert [c.id for c in list_chats(chats, "p1")] == ["c9"]


def test_with_no_chat_named_an_empty_message_is_still_refused(tmp_path):
    projects, chats = _stores(tmp_path)
    create_project(projects, new_id="p1", now="2026-08-09T11:04:00.000+00:00")
    with pytest.raises(EmptyMessage):
        append_message(
            chats,
            "p1",
            "",
            "   ",
            "2026-08-09T11:04:00.000+00:00",
            project_store=projects,
            new_id="c9",
        )
    assert list_chats(chats, "p1") == []


def test_a_message_lands_at_the_end_and_the_title_stays(tmp_path):
    _, chats = _seeded(tmp_path)
    chat = append_message(chats, "p1", "c1", "and a second one", "2026-08-09T11:06:00.000+00:00")
    assert [m.text for m in chat.messages] == ["Write the intro", "and a second one"]
    assert chat.title == "Write the intro"


def test_a_message_remembers_which_skill_sent_it(tmp_path):
    # The record has to stay honest: changing the selection later must not make it look as though
    # an older turn was governed by the new one.
    _, chats = _seeded(tmp_path)
    chat = append_message(
        chats, "p1", "c1", "and a second one", "2026-08-09T11:06:00.000+00:00", skill="split-shots"
    )
    assert chat.messages[-1].skill == "split-shots"


def test_a_message_sent_with_no_skill_says_so(tmp_path):
    _, chats = _seeded(tmp_path)
    chat = append_message(chats, "p1", "c1", "plain", "2026-08-09T11:06:00.000+00:00")
    assert chat.messages[-1].skill == ""


def test_the_role_can_be_the_answer(tmp_path):
    # Faz 6 appends the reply through this very call.
    _, chats = _seeded(tmp_path)
    chat = append_message(chats, "p1", "c1", "Done.", "2026-08-09T11:06:00.000+00:00", role="ai")
    assert chat.messages[-1].role == "ai"


@pytest.mark.parametrize("blank", ["", "  "])
def test_an_empty_message_is_refused_and_the_chat_is_untouched(tmp_path, blank):
    _, chats = _seeded(tmp_path)
    with pytest.raises(EmptyMessage):
        append_message(chats, "p1", "c1", blank, "2026-08-09T11:06:00.000+00:00")
    assert len(chats.get("p1", "c1").messages) == 1


def test_a_stopped_answer_may_carry_nothing(tmp_path):
    # A message has to carry something, and a stop is something: it happened, and what happened gets
    # written down. The user's own message never carries this flag, so the empty one they type is
    # still refused -- the test above proves that and stays where it is.
    _, chats = _seeded(tmp_path)
    chat = append_message(
        chats, "p1", "c1", "", "2026-08-09T11:06:00.000+00:00", role="ai", stopped=True
    )
    assert chat.messages[-1].text == ""
    assert chat.messages[-1].stopped is True


def test_an_unknown_chat_is_reported(tmp_path):
    _, chats = _seeded(tmp_path)
    with pytest.raises(ChatNotFound):
        append_message(chats, "p1", "nope", "hi", "2026-08-09T11:06:00.000+00:00")


def test_a_later_message_lifts_its_chat_to_the_top(tmp_path):
    projects, chats = _stores(tmp_path)
    create_project(projects, new_id="p1", now="2026-08-09T10:00:00.000+00:00")
    _made(projects, chats, "p1", "c1", "older", "2026-08-09T10:00:00.000+00:00")
    _made(projects, chats, "p1", "c2", "newer", "2026-08-09T12:00:00.000+00:00")
    append_message(chats, "p1", "c1", "still here", "2026-08-09T13:00:00.000+00:00")
    assert [chat.id for chat in list_chats(chats, "p1")] == ["c1", "c2"]


def test_starting_a_chat_needs_its_project_to_exist(tmp_path):
    projects, chats = _stores(tmp_path)
    with pytest.raises(Exception):
        _made(projects, chats, "ghost", "c1", "hi", "2026-08-09T11:04:00.000+00:00")


# --- editing a message opens a version (Madde 195) -----------------------------------------------

LATER = "2026-08-09T12:00:00.000+00:00"


def _answered(tmp_path):
    """A chat of two turns: asked, answered, asked again, answered again."""
    projects, chats = _seeded(tmp_path)
    append_message(chats, "p1", "c1", "Done.", LATER, role="ai")
    append_message(chats, "p1", "c1", "Write the ending", LATER)
    append_message(chats, "p1", "c1", "Done twice.", LATER, role="ai")
    return projects, chats


def test_editing_a_message_opens_a_version_where_it_stood(tmp_path):
    # The index is how much of the open line the new one keeps, so a message edited at 2 keeps the
    # two before it and nothing after.
    _, chats = _answered(tmp_path)
    chat = append_message(
        chats, "p1", "c1", "Write a shorter ending", LATER, branch_at=2, line_id="l2"
    )
    assert [(v.id, v.parent, v.at) for v in chat.versions] == [("l2", "", 2)]
    assert [m.text for m in chat.versions[0].messages] == ["Write a shorter ending"]


def test_the_new_version_is_the_one_that_is_open(tmp_path):
    from backend.features.workspace.domain.chat import active_messages

    _, chats = _answered(tmp_path)
    chat = append_message(
        chats, "p1", "c1", "Write a shorter ending", LATER, branch_at=2, line_id="l2"
    )
    assert chat.active == "l2"
    assert [m.text for m in active_messages(chat)] == [
        "Write the intro",
        "Done.",
        "Write a shorter ending",
    ]


def test_the_message_that_was_edited_is_not_carried_over(tmp_path):
    # The point of the whole madde: the sentence the user changed their mind about does not travel
    # into the line they changed it on.
    from backend.features.workspace.domain.chat import active_messages

    _, chats = _answered(tmp_path)
    chat = append_message(
        chats, "p1", "c1", "Write a shorter ending", LATER, branch_at=2, line_id="l2"
    )
    assert "Write the ending" not in [m.text for m in active_messages(chat)]


def test_the_line_that_was_left_keeps_everything_it_had(tmp_path):
    # FOUNDATION 1: opening a version is not cutting the old turns off. They are still there, and
    # the arrows are what reach them.
    _, chats = _answered(tmp_path)
    append_message(chats, "p1", "c1", "Write a shorter ending", LATER, branch_at=2, line_id="l2")
    kept = chats.get("p1", "c1")
    assert [m.text for m in kept.messages] == [
        "Write the intro",
        "Done.",
        "Write the ending",
        "Done twice.",
    ]


def test_a_version_of_a_version_splits_from_the_open_one(tmp_path):
    # Whichever line the user is standing on is the one that branches -- not the first line, which
    # they may have walked away from several edits ago.
    _, chats = _answered(tmp_path)
    append_message(chats, "p1", "c1", "Write a shorter ending", LATER, branch_at=2, line_id="l2")
    append_message(chats, "p1", "c1", "Done shortly.", LATER, role="ai")
    chat = append_message(chats, "p1", "c1", "Shorter still", LATER, branch_at=2, line_id="l3")
    assert [(v.id, v.parent, v.at) for v in chat.versions] == [("l2", "", 2), ("l3", "l2", 2)]


def test_a_message_with_no_index_lands_on_the_open_line(tmp_path):
    # The answer to a version's question belongs to that version. Appending to the first line here
    # would answer a question nobody asked and leave the open one waiting for ever.
    from backend.features.workspace.domain.chat import active_messages

    _, chats = _answered(tmp_path)
    append_message(chats, "p1", "c1", "Write a shorter ending", LATER, branch_at=2, line_id="l2")
    chat = append_message(chats, "p1", "c1", "Done shortly.", LATER, role="ai")
    assert [m.text for m in chat.versions[0].messages] == [
        "Write a shorter ending",
        "Done shortly.",
    ]
    assert [m.text for m in active_messages(chat)][-1] == "Done shortly."
    assert len(chat.messages) == 4


def test_an_empty_sentence_is_refused_on_a_version_too(tmp_path):
    _, chats = _answered(tmp_path)
    with pytest.raises(EmptyMessage):
        append_message(chats, "p1", "c1", "   ", LATER, branch_at=2, line_id="l2")
    # And nothing was opened on the way to refusing it.
    assert chats.get("p1", "c1").versions == ()


def test_editing_in_a_chat_that_does_not_exist_is_refused(tmp_path):
    _, chats = _seeded(tmp_path)
    with pytest.raises(ChatNotFound):
        append_message(chats, "p1", "ghost", "hi", LATER, branch_at=0, line_id="l2")
