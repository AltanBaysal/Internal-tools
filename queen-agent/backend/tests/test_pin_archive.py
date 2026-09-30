"""Madde 339: a project can be pinned and archived, and the project list says which.

Each answer is a file of its own in the project's directory -- `pinned` and `archived`, there or not
there -- because project.json answers only what the project is called and since when (CODE-STANDARD,
Separation of concerns). The two names are written out here rather than imported: what is held is
the shape on disk.
"""
import os

import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import PROJECT_FILE, FileProjectStore
from backend.features.workspace.data.memory_permissions import MemoryPermissions
from backend.features.workspace.data.memory_stops import MemoryStops
from backend.features.workspace.domain.errors import ProjectNotFound
from backend.features.workspace.domain.project import Project
from backend.features.workspace.domain.usecases.edit_project import edit_project
from backend.features.workspace.domain.usecases.list_projects import list_projects
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.web.app import create_app

CODE_STANDARD = os.path.join(
    os.path.dirname(                                  # queen-agent
        os.path.dirname(                              # backend
            os.path.dirname(os.path.abspath(__file__)))),  # tests
    "CODE-STANDARD.md",
)


def _born(tmp_path):
    store = FileProjectStore(Store(str(tmp_path)))
    store.add(Project(id="pabc", name="Thesis", created_at="2026-08-09T10:00:00+00:00"))
    return store


def _reopened(tmp_path):
    # A second instance reads from disk only, which is what a restart does.
    return FileProjectStore(Store(str(tmp_path))).get("pabc")


# ---- The store ----


def test_a_new_project_is_neither_pinned_nor_archived(tmp_path):
    _born(tmp_path)
    project = _reopened(tmp_path)
    assert (project.pinned, project.archived) == (False, False), (
        "Yeni proje sabitli ya da arşivde doğdu"
    )


def test_a_pin_outlives_the_app_and_goes_when_unpinned(tmp_path):
    store = _born(tmp_path)
    store.set_pinned("pabc", True)
    assert _reopened(tmp_path).pinned, "Sabitleme yeniden açılınca kalmadı"
    store.set_pinned("pabc", False)
    assert not _reopened(tmp_path).pinned, "Bırakılan proje hâlâ sabitli"


def test_an_archive_outlives_the_app_and_goes_when_unarchived(tmp_path):
    store = _born(tmp_path)
    store.set_archived("pabc", True)
    assert _reopened(tmp_path).archived, "Arşiv yeniden açılınca kalmadı"
    store.set_archived("pabc", False)
    assert not _reopened(tmp_path).archived, "Geri getirilen proje hâlâ arşivde"


def test_each_answer_is_a_file_of_its_own(tmp_path):
    store = _born(tmp_path)
    raw = Store(str(tmp_path))
    store.set_pinned("pabc", True)
    store.set_archived("pabc", True)
    assert raw.exists("pabc/pinned") and raw.exists("pabc/archived"), (
        "Sabitleme ve arşiv projenin klasöründe kendi dosyalarında durmuyor"
    )
    store.set_pinned("pabc", False)
    store.set_archived("pabc", False)
    assert not raw.exists("pabc/pinned") and not raw.exists("pabc/archived"), (
        "Bırakınca ve geri getirince dosyalar klasörde kaldı"
    )


def test_pinning_and_archiving_leave_project_json_alone(tmp_path):
    store = _born(tmp_path)
    raw = Store(str(tmp_path))
    before = raw.read_text(f"pabc/{PROJECT_FILE}")
    store.set_pinned("pabc", True)
    store.set_archived("pabc", True)
    assert raw.read_text(f"pabc/{PROJECT_FILE}") == before, (
        "project.json sabitleme ya da arşiv yüzünden değişti"
    )


def test_asking_for_what_already_stands_changes_nothing(tmp_path):
    store = _born(tmp_path)
    # Never pinned, never archived: there is nothing to take away, and that is not an error.
    store.set_pinned("pabc", False)
    store.set_archived("pabc", False)
    store.set_pinned("pabc", True)
    # The pin's mtime is when the project was pinned; a second pin must not move it.
    pinned = os.path.join(str(tmp_path), "pabc", "pinned")
    os.utime(pinned, (1_000_000_000, 1_000_000_000))
    store.set_pinned("pabc", True)
    assert os.path.getmtime(pinned) == 1_000_000_000, "İkinci sabitleme sabitlendiği anı kaydırdı"


def test_a_pin_left_beside_an_archived_project_does_not_read_as_pinned(tmp_path):
    # Madde 384: an archive takes the pin with it, but one made under the rule before (363, 382)
    # left the file on disk. An archived project never reads as pinned all the same.
    store = _born(tmp_path)
    store.set_pinned("pabc", True)
    store.set_archived("pabc", True)
    assert not _reopened(tmp_path).pinned, "Arşivdeki proje sabitli okunuyor"


# ---- The use cases, with a fake port ----


def _day(day):
    return f"2026-08-{day:02d}T10:00:00.000+00:00"


class FakeProjectStore:
    def __init__(self, **fields):
        self.project = Project(
            id="pabc", name="Thesis", created_at="2026-08-09T10:00:00+00:00", **fields
        )
        self.replaced = []
        self.marked = []

    def get(self, project_id):
        return self.project if project_id == self.project.id else None

    def replace(self, project):
        self.replaced.append(project)

    def set_pinned(self, project_id, pinned):
        self.marked.append(("pinned", project_id, pinned))

    def set_archived(self, project_id, archived):
        self.marked.append(("archived", project_id, archived))


def test_pinning_does_not_rewrite_the_project_file():
    # project.json is written on create and on rename (CODE-STANDARD); a pin is neither.
    store = FakeProjectStore()
    edit_project(store, "pabc", pinned=True, archived=False)
    assert store.replaced == [], "Sabitlemek project.json'ı yeniden yazdı"
    assert store.marked == [("pinned", "pabc", True), ("archived", "pabc", False)], (
        "İstenen sabitleme ve arşiv depoya gitmedi"
    )


def test_an_unknown_project_cannot_be_pinned():
    store = FakeProjectStore()
    with pytest.raises(ProjectNotFound):
        edit_project(store, "nope", pinned=True)
    assert store.marked == [], "Olmayan bir proje için işaret yazıldı"


def test_archiving_lets_the_pin_go():
    # Madde 384: the archive takes the pin with it, on the server -- the browser sends none.
    store = FakeProjectStore(pinned_at=_day(10))
    edit_project(store, "pabc", archived=True)
    assert ("pinned", "pabc", False) in store.marked, "Arşiv sabitlemeyi silmedi"


def test_unarchiving_lets_the_pin_go():
    # Unarchive brings the project back into Recent, never into Pinned -- also one whose pin an
    # archive made before Madde 384 left on disk.
    store = FakeProjectStore(pinned_at=_day(10), archived=True)
    edit_project(store, "pabc", archived=False)
    assert ("pinned", "pabc", False) in store.marked, "Unarchive sabitlemeyi bırakmadı"


def test_bringing_back_what_is_not_archived_leaves_the_pin():
    # Asking for what already stands changes nothing (Madde 339).
    store = FakeProjectStore(pinned_at=_day(10))
    edit_project(store, "pabc", archived=False)
    assert ("pinned", "pabc", False) not in store.marked, (
        "Arşivde olmayan projeye gelen archived=False sabitlemeyi bıraktı"
    )


class FakeListStore:
    def __init__(self, projects):
        self.projects = projects

    def list_all(self):
        return list(self.projects)


def test_the_archived_are_listed_by_last_use_alone():
    # Madde 384: nothing archived stands among the pins -- not even one whose pin an older archive
    # left on disk -- so the Archived tab, which keeps the server's order, is by last use alone.
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
    client = _client(tmp_path)
    first = client.post("/api/projects", json={"name": "Thesis"}).get_json()["id"]
    second = client.post("/api/projects", json={"name": "Thesis"}).get_json()["id"]
    client.patch(f"/api/projects/{first}", json={"pinned": True})
    client.patch(f"/api/projects/{second}", json={"archived": True})
    rows = {
        row["id"]: (row["pinned"], row["archived"])
        for row in _client(tmp_path).get("/api/projects").get_json()
    }
    assert rows == {first: (True, False), second: (False, True)}, (
        "Liste yeniden açılınca sabitlemeyi ve arşivi söylemiyor"
    )


def test_archive_deletes_the_pin_and_unarchive_does_not_bring_it_back(tmp_path):
    # Madde 384: the archive takes the pin with it on the server, and Unarchive brings the project
    # back into Recent.
    client = _client(tmp_path)
    pid = client.post("/api/projects", json={"name": "Thesis"}).get_json()["id"]
    client.patch(f"/api/projects/{pid}", json={"pinned": True})
    archived = client.patch(f"/api/projects/{pid}", json={"archived": True}).get_json()
    assert (archived["pinned"], archived["archived"]) == (False, True), (
        "Arşive alınan proje sabitli kaldı"
    )
    assert not Store(str(tmp_path)).exists(f"{pid}/pinned"), "Arşivden sonra pinned dosyası duruyor"
    listed = _client(tmp_path).get("/api/projects").get_json()[0]
    assert listed["pinned"] is False, "Yeniden açılınca arşivdeki proje sabitli"
    back = client.patch(f"/api/projects/{pid}", json={"archived": False}).get_json()
    assert back["pinned"] is False, "Unarchive projeyi sabitlemesiyle geri getirdi"
    listed = _client(tmp_path).get("/api/projects").get_json()[0]
    assert (listed["pinned"], listed["archived"]) == (False, False), (
        "Yeniden açılınca arşivden dönen proje sabitli ya da arşivde"
    )


def test_undo_brings_a_pinned_project_back_into_recent_unpinned(tmp_path):
    # Madde 384, the owner's choice over the design's restoreProject: Undo only takes the archive
    # back. The pin went with the archive, so the project -- and its Undo line before it -- stands
    # in Recent, where its own last use puts it.
    projects = FileProjectStore(Store(str(tmp_path)))
    for day, pid in enumerate(("pa", "pb", "pc"), start=1):
        projects.add(Project(id=pid, name=pid, created_at=f"2000-01-{day:02d}T00:00:00.000+00:00"))
    projects.set_pinned("pa", True)
    projects.set_pinned("pb", True)
    client = _client(tmp_path)
    client.patch("/api/projects/pa", json={"archived": True})
    rows = client.get("/api/projects").get_json()
    assert [row["id"] for row in rows] == ["pb", "pc", "pa"], (
        "Arşivdeki proje son kullanımının yerinde değil"
    )
    assert rows[2]["pinned"] is False, "Arşivdeki proje listede sabitli"
    back = client.patch("/api/projects/pa", json={"archived": False}).get_json()
    assert (back["pinned"], back["archived"]) == (False, False), (
        "Undo projeyi sabitli ya da arşivde bıraktı"
    )
    assert [row["id"] for row in client.get("/api/projects").get_json()] == ["pb", "pc", "pa"], (
        "Undo'dan sonra proje Recent'te son kullanımının yerinde değil"
    )
    assert not Store(str(tmp_path)).exists("pa/pinned"), "Undo'dan sonra pinned dosyası duruyor"


def test_a_pin_an_older_archive_left_neither_orders_nor_survives_unarchive(tmp_path):
    # An archive made before Madde 384 left the pin file on disk. The list reads past it and
    # Unarchive clears it, so no migration is needed.
    projects = FileProjectStore(Store(str(tmp_path)))
    projects.add(Project(id="pa", name="pa", created_at="2000-01-01T00:00:00.000+00:00"))
    projects.add(Project(id="pb", name="pb", created_at="2000-01-02T00:00:00.000+00:00"))
    projects.set_pinned("pa", True)
    projects.set_archived("pa", True)
    projects.set_archived("pb", True)
    client = _client(tmp_path)
    rows = client.get("/api/projects").get_json()
    assert [(row["id"], row["pinned"]) for row in rows] == [("pb", False), ("pa", False)], (
        "Eski arşivin bıraktığı sabitleme arşivdeki projeyi öne dizdi ya da sabitli gösterdi"
    )
    back = client.patch("/api/projects/pa", json={"archived": False}).get_json()
    assert back["pinned"] is False, "Unarchive eski sabitlemeyi geri getirdi"
    assert not Store(str(tmp_path)).exists("pa/pinned"), "Unarchive eski pinned dosyasını silmedi"


# ---- The standard ----


def test_the_standard_names_both_new_files():
    # The row asks for it (v9-2b): a new artifact in the store is a new row in the table that says
    # which question each one answers.
    with open(CODE_STANDARD, encoding="utf-8") as handle:
        named = {line.split("`")[1] for line in handle if line.startswith("| `")}
    assert {"pinned", "archived"} <= named, "CODE-STANDARD'ın tablosu yeni dosyaları söylemiyor"
