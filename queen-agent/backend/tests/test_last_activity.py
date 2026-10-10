"""Madde 346: the project list says when each project was last used, and is ordered by it.

The moment is not stored: it is read off the project's chats -- since Madde 447, the newest
lastActivity among their rows in projects.json, which is when somebody last said something in one.
A project with no chats was last used when it was made. The order is pinned first, in the order
they were pinned, then the most recently used -- the design's All projects (items 135 and 167).
"""
import json

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import PROJECTS_FILE, FileProjectStore
from backend.features.workspace.data.live_turns import LiveTurns
from backend.features.workspace.domain.chat import Chat, Message
from backend.features.workspace.domain.project import Project
from backend.features.workspace.domain.prompt import APPROVED
from backend.features.workspace.domain.usecases.edit_project import edit_project
from backend.features.workspace.domain.usecases.list_projects import list_projects
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.web.app import create_app

BORN = "2026-08-09T10:00:00.000+00:00"


def _at(day):
    return f"2026-08-{day:02d}T10:00:00.000+00:00"


def _born(tmp_path):
    store = FileProjectStore(Store(str(tmp_path)))
    store.add(Project(id="pabc", name="Thesis", created_at=BORN))
    return store


def _reopened(store, tmp_path):
    # What a restart does: the writer finishes, and a new store reads the file.
    store.flush()
    return FileProjectStore(Store(str(tmp_path))).get("pabc")


def _chat(chat_id, said_at=BORN):
    return Chat(
        id=chat_id,
        title="Hi",
        created_at=BORN,
        messages=(Message(role="user", at=said_at, text="Hi"),),
    )


# ---- The project ----


def test_a_project_was_last_used_at_its_newest_chat_or_else_when_it_was_made():
    assert Project(id="p", name="p", created_at=BORN).last_activity == BORN, (
        "Sohbeti olmayan projenin son kullanımı doğduğu an değil"
    )
    assert Project(id="p", name="p", created_at=BORN, last_chat_at=_at(20)).last_activity == _at(20), (
        "Sohbeti olan projenin son kullanımı en yeni sohbetin anı değil"
    )


# ---- The store ----


def test_a_project_with_no_chats_was_last_used_when_it_was_made(tmp_path):
    assert _reopened(_born(tmp_path), tmp_path).last_activity == BORN, (
        "Sohbeti olmayan projenin son kullanımı createdAt değil"
    )


def test_the_newest_chat_says_when_the_project_was_last_used(tmp_path):
    store = _born(tmp_path)
    chats = FileChatStore(Store(str(tmp_path)), store)
    chats.add("pabc", _chat("c1", said_at=_at(20)))
    chats.add("pabc", _chat("c2", said_at=_at(12)))
    assert _reopened(store, tmp_path).last_activity == _at(20), (
        "Projenin son kullanımı en yeni sohbetin anı değil"
    )
    # Read off the chats' rows, never written as a field of its own: a second copy is the one that
    # goes stale.
    entry = json.loads(Store(str(tmp_path)).read_text(PROJECTS_FILE))["pabc"]
    assert "lastActivity" not in entry, "Son kullanım anı projenin kaydına yazıldı"


def test_the_pin_says_when_the_project_was_pinned(tmp_path):
    store = _born(tmp_path)
    project = _reopened(store, tmp_path)
    assert (project.pinned, project.pinned_at) == (False, ""), (
        "Sabitli olmayan projenin sabitlendiği bir an var"
    )
    edit_project(store, "pabc", _at(15), pinned=True)
    project = _reopened(store, tmp_path)
    assert (project.pinned, project.pinned_at) == (True, _at(15)), (
        "Sabitlendiği an sabitleme isteğinin anı değil"
    )


# ---- The use case, with a fake port ----


class FakeProjectStore:
    def __init__(self, projects):
        self.projects = projects

    def list_all(self):
        return list(self.projects)


def test_pinned_lead_in_the_order_they_were_pinned_then_the_most_recently_used():
    # Neither the ids nor the births explain the order: both run a to f.
    store = FakeProjectStore(
        [
            Project(id="a", name="a", created_at=_at(1), pinned_at=_at(20)),
            # Pinned first, and talked in recently -- the talk does not move it among the pinned.
            Project(id="b", name="b", created_at=_at(2), pinned_at=_at(10), last_chat_at=_at(25)),
            Project(id="c", name="c", created_at=_at(3)),
            Project(id="d", name="d", created_at=_at(4), last_chat_at=_at(15)),
            Project(id="e", name="e", created_at=_at(5), last_chat_at=_at(12)),
            # No chats: it was last used when it was made.
            Project(id="f", name="f", created_at=_at(14)),
        ]
    )
    assert [project.id for project in list_projects(store)] == ["b", "a", "d", "f", "e", "c"], (
        "Liste önce sabitlendikleri sırayla sabitlenenleri, sonra en son kullanılanı vermiyor"
    )


# ---- The API ----


class FakeEngine:
    def stream(self, messages, tools=None, on_open=None):
        yield {"text": "Done."}

    def stream_alone(self, system, text, on_open=None):
        yield {"text": APPROVED}


def _client(tmp_path):
    store = Store(str(tmp_path))
    projects = FileProjectStore(store)
    app = create_app(
        dist_dir=str(tmp_path),
        blueprints=(
            make_workspace_bp(
                projects,
                FileChatStore(store, projects),
                FileFileStore(store, projects),
                FakeEngine(),
                LiveTurns(),
            ),
        ),
    )
    return app.test_client()


def _made_long_ago(tmp_path, *ids):
    # Born in 2000, a day apart, so nothing done in this test can land in the same millisecond as a
    # birth and leave the order to chance. Written to disk before the app that reads them starts.
    store = FileProjectStore(Store(str(tmp_path)))
    for day, pid in enumerate(ids, start=1):
        store.add(Project(id=pid, name=pid, created_at=f"2000-01-{day:02d}T00:00:00.000+00:00"))
    store.flush()


def _order(client):
    return [row["id"] for row in client.get("/api/projects").get_json()]


def test_the_list_says_when_each_project_was_last_used(tmp_path):
    client = _client(tmp_path)
    created = client.post("/api/projects", json={"name": "Thesis"}).get_json()
    assert created["lastActivity"] == created["createdAt"], (
        "Yeni projenin son kullanımı doğduğu an değil"
    )
    assert client.get("/api/projects").get_json() == [created], (
        "Liste projenin son kullanımını oluşturmanın cevabı gibi söylemiyor"
    )


def test_talking_in_a_project_renews_its_moment_and_brings_it_up(tmp_path):
    _made_long_ago(tmp_path, "pold", "pnew")
    client = _client(tmp_path)
    assert _order(client) == ["pnew", "pold"], "En son kullanılan proje önde değil"
    client.post("/api/projects/pold/messages", json={"text": "Hi"}).get_data()
    rows = client.get("/api/projects").get_json()
    assert [row["id"] for row in rows] == ["pold", "pnew"], (
        "Sohbet edilen proje listenin önüne geçmedi"
    )
    assert rows[0]["lastActivity"] > "2000-01-02T00:00:00.000+00:00", (
        "Sohbet edilince projenin son kullanımı yenilenmedi"
    )


def test_talking_in_an_existing_chat_brings_its_project_and_the_chat_up(tmp_path):
    # Madde 452: test_talking_in_a_project_renews_its_moment_and_brings_it_up talks in a chat it
    # creates. Here the chat is already there -- the older of its project's two -- and the project is
    # the older of two; the times are from 2000, so nothing said in this test can tie with them.
    store = FileProjectStore(Store(str(tmp_path)))
    chats = FileChatStore(Store(str(tmp_path)), store)
    store.add(Project(id="pold", name="pold", created_at="2000-01-01T00:00:00.000+00:00"))
    store.add(Project(id="pnew", name="pnew", created_at="2000-01-02T00:00:00.000+00:00"))
    chats.add("pold", _chat("cold", said_at="2000-01-03T00:00:00.000+00:00"))
    chats.add("pold", _chat("cmid", said_at="2000-01-03T01:00:00.000+00:00"))
    chats.add("pnew", _chat("cnew", said_at="2000-01-04T00:00:00.000+00:00"))
    store.flush()
    client = _client(tmp_path)
    assert _order(client) == ["pnew", "pold"], "En son kullanılan proje önde değil"

    def chat_ids():
        return [row["id"] for row in client.get("/api/projects/pold/chats").get_json()]

    assert chat_ids() == ["cmid", "cold"], "En son kullanılan sohbet önde değil"

    client.post("/api/projects/pold/messages", json={"chat": "cold", "text": "Again"}).get_data()

    rows = client.get("/api/projects").get_json()
    assert [row["id"] for row in rows] == ["pold", "pnew"], (
        "Var olan sohbette konuşulan proje listenin önüne geçmedi"
    )
    assert rows[0]["lastActivity"] > "2000-01-04T00:00:00.000+00:00", (
        "Var olan sohbette konuşulunca projenin son kullanımı yenilenmedi"
    )
    assert chat_ids() == ["cold", "cmid"], (
        "Konuşulan sohbet kenar çubuğunun sırasında öne geçmedi"
    )


def test_a_pinned_project_leads_the_newer_ones(tmp_path):
    _made_long_ago(tmp_path, "pold", "pmid", "pnew")
    client = _client(tmp_path)
    client.patch("/api/projects/pmid", json={"pinned": True})
    assert _order(client) == ["pmid", "pnew", "pold"], (
        "Sabitlenen proje sabitli olmayan daha yenilerin önüne geçmedi"
    )
