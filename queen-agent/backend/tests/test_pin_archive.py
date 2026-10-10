"""Madde 339: a project can be pinned and archived, and the project list says which.

Since Madde 447 both are written in the project's entry in projects.json -- `pinnedAt` while it is
pinned, `archived` while it is archived -- and nowhere else.
"""
import json

import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import PROJECTS_FILE, FileProjectStore
from backend.features.workspace.data.live_turns import LiveTurns
from backend.features.workspace.domain.errors import ProjectNotFound
from backend.features.workspace.domain.project import Project
from backend.features.workspace.domain.prompt import APPROVED
from backend.features.workspace.domain.usecases.edit_project import edit_project
from backend.features.workspace.domain.usecases.list_projects import list_projects
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.web.app import create_app


def _day(day):
    return f"2026-08-{day:02d}T10:00:00.000+00:00"


NOW = _day(20)


def _born(tmp_path):
    store = FileProjectStore(Store(str(tmp_path)))
    store.add(Project(id="pabc", name="Thesis", created_at="2026-08-09T10:00:00+00:00"))
    return store


def _reopened(store, tmp_path):
    # What a restart does: the writer finishes, and a new store reads the file.
    store.flush()
    return FileProjectStore(Store(str(tmp_path))).get("pabc")


# ---- The store ----


def test_a_new_project_is_neither_pinned_nor_archived(tmp_path):
    project = _reopened(_born(tmp_path), tmp_path)
    assert (project.pinned, project.archived) == (False, False), (
        "Yeni proje sabitli ya da arşivde doğdu"
    )


def test_a_pin_outlives_the_app_and_goes_when_unpinned(tmp_path):
    store = _born(tmp_path)
    edit_project(store, "pabc", NOW, pinned=True)
    assert _reopened(store, tmp_path).pinned_at == NOW, "Sabitleme yeniden açılınca kalmadı"
    edit_project(store, "pabc", NOW, pinned=False)
    assert not _reopened(store, tmp_path).pinned, "Bırakılan proje hâlâ sabitli"


def test_an_archive_outlives_the_app_and_goes_when_unarchived(tmp_path):
    store = _born(tmp_path)
    edit_project(store, "pabc", NOW, archived=True)
    assert _reopened(store, tmp_path).archived, "Arşiv yeniden açılınca kalmadı"
    edit_project(store, "pabc", NOW, archived=False)
    assert not _reopened(store, tmp_path).archived, "Geri getirilen proje hâlâ arşivde"


def test_pin_and_archive_live_in_projects_json_alone(tmp_path):
    store = _born(tmp_path)
    edit_project(store, "pabc", NOW, pinned=True)
    store.flush()
    raw = Store(str(tmp_path))
    assert json.loads(raw.read_text(PROJECTS_FILE))["pabc"]["pinnedAt"] == NOW
    edit_project(store, "pabc", NOW, archived=True)
    store.flush()
    assert json.loads(raw.read_text(PROJECTS_FILE))["pabc"]["archived"] is True
    assert raw.list_dir("pabc") == [], "Sabitleme ya da arşiv projenin klasörüne bir dosya yazdı"


def test_asking_for_what_already_stands_writes_nothing(tmp_path, monkeypatch):
    raw = Store(str(tmp_path))
    store = FileProjectStore(raw)
    store.add(Project(id="pabc", name="Thesis", created_at="2026-08-09T10:00:00+00:00"))
    store.flush()
    writes = []
    monkeypatch.setattr(raw, "write_text", lambda rel, text: writes.append(rel))
    # Never pinned, never archived: there is nothing to take away, and that is not an error.
    edit_project(store, "pabc", NOW, pinned=False, archived=False)
    store.flush()
    assert writes == [], "Hiçbir şeyi değiştirmeyen istek diske yazdı"


def test_an_archived_project_never_reads_as_pinned():
    # Madde 384: an archive takes the pin with it, and whatever an entry says, an archived project
    # is not listed among the pins.
    assert not Project(id="p", name="p", created_at=_day(1), pinned_at=_day(2), archived=True).pinned


# ---- The use cases, with a fake port ----


class FakeProjectStore:
    """The port with one project, applying the change it is handed the way the real store does."""

    def __init__(self, **fields):
        self.project = Project(
            id="pabc", name="Thesis", created_at="2026-08-09T10:00:00+00:00", **fields
        )
        self.changes = 0

    def get(self, project_id):
        return self.project if project_id == self.project.id else None

    def update(self, project_id, change):
        if project_id != self.project.id:
            return None
        self.changes += 1
        self.project = change(self.project)
        return self.project


def test_pinning_stamps_the_moment():
    store = FakeProjectStore()
    pinned = edit_project(store, "pabc", NOW, pinned=True)
    assert (pinned.pinned, pinned.pinned_at) == (True, NOW), "Sabitleme anı yazılmadı"


def test_pinning_twice_does_not_move_the_moment():
    # The order of the pinned is the order they were pinned in (Madde 339).
    store = FakeProjectStore(pinned_at=_day(10))
    assert edit_project(store, "pabc", NOW, pinned=True).pinned_at == _day(10), (
        "İkinci sabitleme sabitlendiği anı kaydırdı"
    )


def test_unpinning_lets_the_pin_go():
    store = FakeProjectStore(pinned_at=_day(10))
    assert edit_project(store, "pabc", NOW, pinned=False).pinned_at == "", "Sabitleme bırakılmadı"


def test_an_unknown_project_cannot_be_pinned():
    store = FakeProjectStore()
    with pytest.raises(ProjectNotFound):
        edit_project(store, "nope", NOW, pinned=True)
    assert store.project.pinned_at == "", "Olmayan bir proje için sabitleme yazıldı"


def test_archiving_lets_the_pin_go():
    # Madde 384: the archive takes the pin with it, on the server -- the browser sends none.
    store = FakeProjectStore(pinned_at=_day(10))
    archived = edit_project(store, "pabc", NOW, archived=True)
    assert (archived.archived, archived.pinned_at) == (True, ""), "Arşiv sabitlemeyi silmedi"


def test_unarchiving_lets_the_pin_go():
    # Unarchive brings the project back into Recent, never into Pinned -- also one pinned while it
    # stood in the archive.
    store = FakeProjectStore(pinned_at=_day(10), archived=True)
    back = edit_project(store, "pabc", NOW, archived=False)
    assert (back.archived, back.pinned_at) == (False, ""), "Unarchive sabitlemeyi bırakmadı"


def test_bringing_back_what_is_not_archived_leaves_the_pin():
    # Asking for what already stands changes nothing (Madde 339).
    store = FakeProjectStore(pinned_at=_day(10))
    assert edit_project(store, "pabc", NOW, archived=False).pinned_at == _day(10), (
        "Arşivde olmayan projeye gelen archived=False sabitlemeyi bıraktı"
    )


def test_pin_archive_and_name_are_one_change():
    # One request, one change: the store hears of it once, and the writer writes once.
    store = FakeProjectStore()
    edit_project(store, "pabc", NOW, name="Renamed", pinned=True)
    assert store.changes == 1, "Bir istek depoya birden çok değişiklik gönderdi"
    assert (store.project.name, store.project.pinned_at) == ("Renamed", NOW)


class FakeListStore:
    def __init__(self, projects):
        self.projects = projects

    def list_all(self):
        return list(self.projects)


def test_the_archived_are_listed_by_last_use_alone():
    # Madde 384: nothing archived stands among the pins, so the Archived tab, which keeps the
    # server's order, is by last use alone.
    store = FakeListStore(
        [
            Project(id="a", name="a", created_at=_day(1), pinned_at=_day(10)),
            Project(id="b", name="b", created_at=_day(2), pinned_at=_day(5), archived=True),
            Project(id="c", name="c", created_at=_day(3)),
            Project(id="d", name="d", created_at=_day(4), archived=True),
        ]
    )
    projects = list_projects(store)
    assert [project.id for project in projects] == ["a", "d", "c", "b"], (
        "Arşivdeki projeler yalnız son kullanıma göre sıralı değil"
    )
    assert not any(project.pinned for project in projects if project.archived), (
        "Arşivdeki bir proje listede sabitli"
    )


# ---- The API ----


class FakeEngine:
    def stream(self, messages, tools=None, on_open=None):
        yield {"text": "Done."}

    def stream_alone(self, system, text, on_open=None):
        yield {"text": APPROVED}


def _wired(tmp_path):
    store = Store(str(tmp_path))
    projects = FileProjectStore(store)
    files = FileFileStore(store, projects)
    app = create_app(
        dist_dir=str(tmp_path),
        blueprints=(
            make_workspace_bp(
                projects,
                FileChatStore(store, projects),
                files,
                FakeEngine(),
                LiveTurns(),
            ),
        ),
    )
    return app.test_client(), projects, files


def _client(tmp_path):
    return _wired(tmp_path)[0]


def _fresh(projects, tmp_path):
    # A second app on the same root, once the first has written everything: a restart.
    projects.flush()
    return _client(tmp_path)


def test_patch_pins_and_unpins(tmp_path):
    client = _client(tmp_path)
    pid = client.post("/api/projects", json={"name": "Thesis"}).get_json()["id"]
    pinned = client.patch(f"/api/projects/{pid}", json={"pinned": True}).get_json()
    assert pinned["pinned"] is True, "PATCH projeyi sabitlemedi"
    unpinned = client.patch(f"/api/projects/{pid}", json={"pinned": False}).get_json()
    assert unpinned["pinned"] is False, "PATCH sabitlemeyi bırakmadı"


def test_patch_archives_and_the_archived_project_stays_listed(tmp_path):
    # The row says it is archived; which tab shows it is the screen's to decide (v9-2t).
    client = _client(tmp_path)
    pid = client.post("/api/projects", json={"name": "Thesis"}).get_json()["id"]
    archived = client.patch(f"/api/projects/{pid}", json={"archived": True}).get_json()
    assert archived["archived"] is True, "PATCH projeyi arşive almadı"
    assert client.get("/api/projects").get_json() == [archived], (
        "Arşivdeki proje listede kendi satırıyla durmuyor"
    )
    back = client.patch(f"/api/projects/{pid}", json={"archived": False}).get_json()
    assert back["archived"] is False, "PATCH projeyi arşivden geri getirmedi"


def test_the_list_says_both_and_a_fresh_app_says_the_same(tmp_path):
    client, projects, _ = _wired(tmp_path)
    first = client.post("/api/projects", json={"name": "Thesis"}).get_json()["id"]
    second = client.post("/api/projects", json={"name": "Thesis"}).get_json()["id"]
    client.patch(f"/api/projects/{first}", json={"pinned": True})
    client.patch(f"/api/projects/{second}", json={"archived": True})
    rows = {
        row["id"]: (row["pinned"], row["archived"])
        for row in _fresh(projects, tmp_path).get("/api/projects").get_json()
    }
    assert rows == {first: (True, False), second: (False, True)}, (
        "Liste yeniden açılınca sabitlemeyi ve arşivi söylemiyor"
    )


def test_archive_deletes_the_pin_and_unarchive_does_not_bring_it_back(tmp_path):
    # Madde 384: the archive takes the pin with it on the server, and Unarchive brings the project
    # back into Recent.
    client, projects, _ = _wired(tmp_path)
    pid = client.post("/api/projects", json={"name": "Thesis"}).get_json()["id"]
    client.patch(f"/api/projects/{pid}", json={"pinned": True})
    archived = client.patch(f"/api/projects/{pid}", json={"archived": True}).get_json()
    assert (archived["pinned"], archived["archived"]) == (False, True), (
        "Arşive alınan proje sabitli kaldı"
    )
    listed = _fresh(projects, tmp_path).get("/api/projects").get_json()[0]
    assert listed["pinned"] is False, "Yeniden açılınca arşivdeki proje sabitli"
    back = client.patch(f"/api/projects/{pid}", json={"archived": False}).get_json()
    assert back["pinned"] is False, "Unarchive projeyi sabitlemesiyle geri getirdi"
    listed = _fresh(projects, tmp_path).get("/api/projects").get_json()[0]
    assert (listed["pinned"], listed["archived"]) == (False, False), (
        "Yeniden açılınca arşivden dönen proje sabitli ya da arşivde"
    )


def test_unarchive_brings_a_pinned_project_back_into_recent_unpinned(tmp_path):
    # Madde 384, the owner's choice over the design's restoreProject: Unarchive only takes the
    # archive back. The pin went with the archive, so the project stands in Recent, where its own
    # last use puts it (the design's 217).
    client, projects, _ = _wired(tmp_path)
    for day, pid in enumerate(("pa", "pb", "pc"), start=1):
        projects.add(Project(id=pid, name=pid, created_at=f"2000-01-{day:02d}T00:00:00.000+00:00"))
    client.patch("/api/projects/pa", json={"pinned": True})
    client.patch("/api/projects/pb", json={"pinned": True})
    client.patch("/api/projects/pa", json={"archived": True})
    rows = client.get("/api/projects").get_json()
    assert [row["id"] for row in rows] == ["pb", "pc", "pa"], (
        "Arşivdeki proje son kullanımının yerinde değil"
    )
    assert rows[2]["pinned"] is False, "Arşivdeki proje listede sabitli"
    back = client.patch("/api/projects/pa", json={"archived": False}).get_json()
    assert (back["pinned"], back["archived"]) == (False, False), (
        "Unarchive projeyi sabitli ya da arşivde bıraktı"
    )
    assert [row["id"] for row in client.get("/api/projects").get_json()] == ["pb", "pc", "pa"], (
        "Unarchive'dan sonra proje Recent'te son kullanımının yerinde değil"
    )


def test_an_archived_project_is_used_as_any_other_and_stays_archived(tmp_path):
    # Madde 443, the owner's words: the only difference between an archived project and another is
    # the list it stands in. Nothing on the server reads the mark but the list's order and the pin,
    # so an archived project is talked in and read like any other -- and using it does not unarchive.
    client, _, files = _wired(tmp_path)
    pid = client.post("/api/projects", json={"name": "Thesis"}).get_json()["id"]
    files.write(pid, "plan.md", "the body")
    client.patch(f"/api/projects/{pid}", json={"archived": True})

    sent = client.post(f"/api/projects/{pid}/messages", json={"text": "hello"})
    assert sent.status_code == 200, "Arşivdeki projede mesaj reddedildi"
    sent.get_data()
    chats = client.get(f"/api/projects/{pid}/chats").get_json()
    assert len(chats) == 1, "Arşivdeki projenin sohbeti listelenmedi"
    record = client.get(f"/api/projects/{pid}/chats/{chats[0]['id']}").get_json()
    assert [m["text"] for m in record["messages"]] == ["hello", "Done."], (
        "Arşivdeki projede mesaj ya da cevabı kayda yazılmadı"
    )
    assert [f["name"] for f in client.get(f"/api/projects/{pid}/files").get_json()] == ["plan.md"], (
        "Arşivdeki projenin dosyası listelenmedi"
    )
    assert client.get(f"/api/projects/{pid}/files/plan.md").get_json()["text"] == "the body", (
        "Arşivdeki projenin dosyası okunmadı"
    )
    assert client.get("/api/projects").get_json()[0]["archived"] is True, (
        "Arşivdeki projeyi kullanmak onu arşivden çıkardı"
    )
