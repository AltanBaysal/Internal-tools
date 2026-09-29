# Madde 339 — Proje sabitlenir ve arşivlenir, sunucu · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sunucunun projeyi sabitleyip bıraktığını, arşive alıp geri getirdiğini, listenin ikisini de
söylediğini ve ikisinin de yeniden açılışta kaldığını tutan testler, kırmızı.

**Architecture:** Yeni bir test dosyası, `queen-agent/backend/tests/test_pin_archive.py`: depo
katmanı gerçek `Store`'la, use case sahte portla, API Flask'ın test istemcisiyle, ve CODE-STANDARD'ın
tablosu. `test_projects_api.py`'de satırın alan kümesini tutan test genişler.

**Tech Stack:** pytest, Flask test client.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m339-sabitle-arsivle-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce; hata cümlesi Türkçe.
- İşaret dosyalarının adları testte düz yazılır: `pinned`, `archived`.
- Bu turda üretim kodu ve CODE-STANDARD.md değişmez; ön uç değişmez, `dist` derlenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Testler, kırmızı

**Files:**
- Create: `queen-agent/backend/tests/test_pin_archive.py`
- Modify: `queen-agent/backend/tests/test_projects_api.py` — `test_the_answer_carries_neither_a_description_nor_a_colour`

**Interfaces:**
- Produces (uygulama turunun karşılayacağı):
  - `Project.pinned: bool = False`, `Project.archived: bool = False` — okunurken diskten.
  - `FileProjectStore.set_pinned(project_id: str, pinned: bool) -> None`,
    `FileProjectStore.set_archived(project_id: str, archived: bool) -> None`; projenin klasöründe
    `pinned` / `archived` dosyası; aynı cevabı ikinci kez istemek diske dokunmaz.
  - `edit_project(store, project_id, name=None, pinned=None, archived=None)` — `None` gönderilmemiş
    demek; yalnız `name` gelince `store.replace` çağrılır.
  - `PATCH /api/projects/<id>` gövdesinde `pinned` / `archived`; proje JSON'ında `"pinned"` ve
    `"archived"`.
  - CODE-STANDARD'ın tablosunda `` | `pinned` | `` ve `` | `archived` | `` ile başlayan satırlar.

- [ ] **Step 1: `test_pin_archive.py`'yi yaz**

```python
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


def test_the_archive_leaves_the_pin_alone(tmp_path):
    # Two questions, two files: a pinned project comes back from the archive where it stood.
    store = _born(tmp_path)
    store.set_pinned("pabc", True)
    store.set_archived("pabc", True)
    assert _reopened(tmp_path).pinned, "Arşiv sabitlemeyi kaldırdı"
    store.set_archived("pabc", False)
    assert _reopened(tmp_path).pinned, "Arşivden dönen proje sabitlemesini kaybetti"


# ---- The use case, with a fake port ----


class FakeProjectStore:
    def __init__(self):
        self.project = Project(id="pabc", name="Thesis", created_at="2026-08-09T10:00:00+00:00")
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


# ---- The API ----


class FakeEngine:
    def stream(self, messages, tools=None, on_open=None, conversation_id=""):
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
    pid = client.post("/api/projects").get_json()["id"]
    pinned = client.patch(f"/api/projects/{pid}", json={"pinned": True}).get_json()
    assert pinned["pinned"] is True, "PATCH projeyi sabitlemedi"
    unpinned = client.patch(f"/api/projects/{pid}", json={"pinned": False}).get_json()
    assert unpinned["pinned"] is False, "PATCH sabitlemeyi bırakmadı"


def test_patch_archives_and_the_archived_project_stays_listed(tmp_path):
    # The row says it is archived; which tab shows it is the screen's to decide (v9-2t).
    client = _client(tmp_path)
    pid = client.post("/api/projects").get_json()["id"]
    archived = client.patch(f"/api/projects/{pid}", json={"archived": True}).get_json()
    assert archived["archived"] is True, "PATCH projeyi arşive almadı"
    assert client.get("/api/projects").get_json() == [archived], (
        "Arşivdeki proje listede kendi satırıyla durmuyor"
    )
    back = client.patch(f"/api/projects/{pid}", json={"archived": False}).get_json()
    assert back["archived"] is False, "PATCH projeyi arşivden geri getirmedi"


def test_the_list_says_both_and_a_fresh_app_says_the_same(tmp_path):
    client = _client(tmp_path)
    first = client.post("/api/projects").get_json()["id"]
    second = client.post("/api/projects").get_json()["id"]
    client.patch(f"/api/projects/{first}", json={"pinned": True})
    client.patch(f"/api/projects/{second}", json={"archived": True})
    rows = {
        row["id"]: (row["pinned"], row["archived"])
        for row in _client(tmp_path).get("/api/projects").get_json()
    }
    assert rows == {first: (True, False), second: (False, True)}, (
        "Liste yeniden açılınca sabitlemeyi ve arşivi söylemiyor"
    )


# ---- The standard ----


def test_the_standard_names_both_new_files():
    # The row asks for it (v9-2b): a new artifact in the store is a new row in the table that says
    # which question each one answers.
    with open(CODE_STANDARD, encoding="utf-8") as handle:
        named = {line.split("`")[1] for line in handle if line.startswith("| `")}
    assert {"pinned", "archived"} <= named, "CODE-STANDARD'ın tablosu yeni dosyaları söylemiyor"
```

- [ ] **Step 2: Satırın alan kümesini genişlet**

`test_projects_api.py`'de:

```python
def test_the_answer_carries_neither_a_description_nor_a_colour(tmp_path):
    created = _client(tmp_path).post("/api/projects").get_json()
    # Madde 339 added the pin and the archive; neither a description nor a colour came back with them.
    assert set(created) == {"id", "name", "createdAt", "chats", "files", "pinned", "archived"}
```

- [ ] **Step 3: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `python -m pytest queen-agent -q` yeni dosyanın on üç testinde ve genişleyen testte
kırmızı — depo testleri `AttributeError` (`pinned`/`set_pinned` yok), use case testleri `TypeError`
(`pinned` diye bir argüman yok), API testleri `KeyError`, belge testi iddianın kendisi: 14 kırmızı,
932 yeşil — genişleyen test bugünkü 933'ün biri. queen-editor'ün arka ucu 377'nin bilinen iki kırmızısı; iki ön uç yeşil.

- [ ] **Step 4: Kırmızıyı commit'le**

```powershell
git add queen-agent/backend/tests/test_pin_archive.py queen-agent/backend/tests/test_projects_api.py docs/superpowers/specs/2026-09-29-queenagent-m339-sabitle-arsivle-testler-design.md docs/superpowers/plans/2026-09-29-queenagent-m339-sabitle-arsivle-testler-plan.md
git commit -m @'
test(queen-agent): Madde 339 red -- a project is pinned and archived in files of its own, and the list says both

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
