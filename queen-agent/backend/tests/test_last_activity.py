"""Madde 346: the project list says when each project was last used, and is ordered by it.

The moment is not stored anywhere: it is read off the chats, whose newest file was written the last
time anybody talked in the project (CODE-STANDARD, "no file repeats another's answer"). A project
with no chats was last used when it was made. The order is pinned first, in the order they were
pinned, then the most recently used -- the design's All projects (items 135 and 167).
"""
import os
from datetime import datetime, timezone

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import PROJECT_FILE, FileProjectStore
from backend.features.workspace.data.memory_permissions import MemoryPermissions
from backend.features.workspace.data.memory_stops import MemoryStops
from backend.features.workspace.domain.chat import Chat, Message
from backend.features.workspace.domain.project import Project
from backend.features.workspace.domain.prompt import APPROVED
from backend.features.workspace.domain.usecases.list_projects import list_projects
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.web.app import create_app

BORN = "2026-08-09T10:00:00.000+00:00"


def _iso(seconds):
    # The shape the server stamps everything with: UTC, to the millisecond.
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat(timespec="milliseconds")


def _at(day):
    return f"2026-08-{day:02d}T10:00:00.000+00:00"


def _born(tmp_path):
    store = FileProjectStore(Store(str(tmp_path)))
    store.add(Project(id="pabc", name="Thesis", created_at=BORN))
    return store


def _reopened(tmp_path):
    # A second instance reads from disk only, which is what a restart does.
    return FileProjectStore(Store(str(tmp_path))).get("pabc")


def _chat(chat_id):
    return Chat(
        id=chat_id,
        title="Hi",
        created_at=BORN,
        messages=(Message(role="user", at=BORN, text="Hi"),),
    )


def _touch(tmp_path, *parts, seconds):
    os.utime(os.path.join(str(tmp_path), *parts), (seconds, seconds))


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
    _born(tmp_path)
    assert _reopened(tmp_path).last_activity == BORN, (
        "Sohbeti olmayan projenin son kullanımı createdAt değil"
    )


def test_the_newest_chat_file_says_when_the_project_was_last_used(tmp_path):
    _born(tmp_path)
    raw = Store(str(tmp_path))
    before = raw.read_text(f"pabc/{PROJECT_FILE}")
    chats = FileChatStore(raw)
    chats.add("pabc", _chat("c1"))
    chats.add("pabc", _chat("c2"))
    _touch(tmp_path, "pabc", "chats", "c1.json", seconds=1_000_000_100)
    _touch(tmp_path, "pabc", "chats", "c2.json", seconds=1_000_000_000)
    assert _reopened(tmp_path).last_activity == _iso(1_000_000_100), (
        "Projenin son kullanımı en yeni sohbet dosyasının anı değil"
    )
    # Read, never written: the chats already say it, and a second copy is the one that goes stale.
    assert raw.list_dir("pabc") == ["chats", PROJECT_FILE], (
        "Son kullanım anı projenin klasörüne bir dosya olarak yazıldı"
    )
    assert raw.read_text(f"pabc/{PROJECT_FILE}") == before, (
        "Son kullanım anı project.json'a yazıldı"
    )


def test_the_pin_says_when_the_project_was_pinned(tmp_path):
    store = _born(tmp_path)
    project = _reopened(tmp_path)
    assert (project.pinned, project.pinned_at) == (False, ""), (
        "Sabitli olmayan projenin sabitlendiği bir an var"
    )
    store.set_pinned("pabc", True)
    _touch(tmp_path, "pabc", "pinned", seconds=1_000_000_000)
    project = _reopened(tmp_path)
    assert (project.pinned, project.pinned_at) == (True, _iso(1_000_000_000)), (
        "Sabitlendiği an pinned dosyasının anı değil"
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
    app = create_app(
        dist_dir=str(tmp_path),
        blueprints=(
            make_workspace_bp(
                FileProjectStore(store),
                FileChatStore(store),
                FileFileStore(store),
                FakeEngine(),
                MemoryStops(),
                MemoryPermissions(),
            ),
        ),
    )
    return app.test_client()


def _made_long_ago(tmp_path, *ids):
    # Born in 2000, a day apart, so nothing done in this test can land in the same millisecond as a
    # birth and leave the order to chance.
    store = FileProjectStore(Store(str(tmp_path)))
    for day, pid in enumerate(ids, start=1):
        store.add(Project(id=pid, name=pid, created_at=f"2000-01-{day:02d}T00:00:00.000+00:00"))


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


def test_a_pinned_project_leads_the_newer_ones(tmp_path):
    _made_long_ago(tmp_path, "pold", "pmid", "pnew")
    client = _client(tmp_path)
    client.patch("/api/projects/pmid", json={"pinned": True})
    assert _order(client) == ["pmid", "pnew", "pold"], (
        "Sabitlenen proje sabitli olmayan daha yenilerin önüne geçmedi"
    )
