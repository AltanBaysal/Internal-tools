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
