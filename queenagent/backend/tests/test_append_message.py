import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.errors import ChatNotFound, EmptyMessage
from backend.features.workspace.domain.usecases.append_message import append_message
from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.list_chats import list_chats
from backend.features.workspace.domain.usecases.start_chat import start_chat
from backend.services.store.store import Store


def _stores(tmp_path):
    store = Store(str(tmp_path))
    return FileProjectStore(store), FileChatStore(store)


def _chat(projects, chats, project_id, chat_id, text, now):
    # A chat always lives in a project, so the project is made first.
    create_project(projects, new_id=project_id, now=now)
    return start_chat(chats, projects, project_id, text, chat_id, now)


def _seeded(tmp_path):
    projects, chats = _stores(tmp_path)
    _chat(projects, chats, "p1", "c1", "Write the intro", "2026-08-09T11:04:00.000+00:00")
    return projects, chats


def test_a_message_lands_at_the_end_and_the_title_stays(tmp_path):
    _, chats = _seeded(tmp_path)
    chat = append_message(chats, "p1", "c1", "and a second one", "2026-08-09T11:06:00.000+00:00")
    assert [m.text for m in chat.messages] == ["Write the intro", "and a second one"]
    assert chat.title == "Write the intro"


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


def test_an_unknown_chat_is_reported(tmp_path):
    _, chats = _seeded(tmp_path)
    with pytest.raises(ChatNotFound):
        append_message(chats, "p1", "nope", "hi", "2026-08-09T11:06:00.000+00:00")


def test_a_later_message_lifts_its_chat_to_the_top(tmp_path):
    projects, chats = _stores(tmp_path)
    create_project(projects, new_id="p1", now="2026-08-09T10:00:00.000+00:00")
    start_chat(chats, projects, "p1", "older", "c1", "2026-08-09T10:00:00.000+00:00")
    start_chat(chats, projects, "p1", "newer", "c2", "2026-08-09T12:00:00.000+00:00")
    append_message(chats, "p1", "c1", "still here", "2026-08-09T13:00:00.000+00:00")
    assert [chat.id for chat in list_chats(chats, "p1")] == ["c1", "c2"]


def test_starting_a_chat_needs_its_project_to_exist(tmp_path):
    projects, chats = _stores(tmp_path)
    with pytest.raises(Exception):
        start_chat(chats, projects, "ghost", "hi", "c1", "2026-08-09T11:04:00.000+00:00")
