# Mira Faz 1 (Disk) — Uygulama Planı

> **Ajan işçiler için:** Bu plan `superpowers:executing-plans` ile madde madde uygulanır. Adımlar
> takip için kutucuk (`- [ ]`) sözdizimindedir.

**Hedef:** Diskteki gerçeği kurmak — tek kökün altında çalışan bir dosya servisi (Madde 2) ve
`workspace` feature'ının proje oluşturma/listeleme yeteneği, uç noktalarıyla (Madde 3).

**Mimari:** `store/` servisi kök hapishanesinin arkasında metin ve dizin seviyesinde konuşur, JSON
bilmez. `workspace` feature'ı üç katmandır: `domain/` saf kuralları ve `ProjectStore` protokolünü
tutar (dış ithal yok), `data/` bu protokolü `store/` üzerinden gerçekler ve `project.json` şemasını
bilen tek yerdir, `presentation/` yalnız HTTP çevirisi yapar. Somut sınıflar `main.py`'de bağlanır.

**Yığın:** Python 3 · Flask · pytest

**Kaynak spec:** [Faz 1 — Disk](../specs/2026-08-09-mira-faz-1-disk-design.md)

## Global Kısıtlar

- Kod, yorum, docstring ve test adı **İngilizce**.
- `domain/` hiçbir dış şey ithal etmez: ne `flask`, ne `os`, ne `json`, ne dosya adı. Id ve "şimdi"
  use case'e **parametre** olarak geçer — testler sahte saatle ve sabit id ile çalışır.
- `service ↛ feature`, `feature ↛ feature`, `service ↛ service`. Somut sınıflar yalnız `main.py`'de.
- Kök dışına çıkan hiçbir yol kabul edilmez.
- Var olan bir şeyin üstüne sessizce yazılmaz.
- **Commit adımı yoktur** — commit'ler koşunun sonunda topluca.
- Test komutu her seferinde aynı: `python -m pytest d:\code\github\internal-tools\mira -q`

---

### Task 1: `store/` servisi

**Dosyalar:**
- Oluştur: `mira/backend/services/store/__init__.py`, `mira/backend/services/store/store.py`
- Test: `mira/backend/tests/test_store.py`

**Arayüzler:**
- Üretir: `Store(root)` · `read_text(rel)` · `write_text(rel, text)` · `list_dir(rel)` ·
  `exists(rel)` · `mtime(rel)` · `move(src_rel, dst_rel)` · `PathOutsideRoot`

- [ ] **Adım 1: Başarısız testleri yaz**

`mira/backend/tests/test_store.py`:

```python
import os

import pytest

from backend.services.store.store import PathOutsideRoot, Store


@pytest.mark.parametrize("rel", ["../escape.txt", "a/../../escape.txt", "/etc/passwd", "C:\\Windows\\x"])
def test_paths_escaping_the_root_are_rejected(tmp_path, rel):
    store = Store(str(tmp_path))
    with pytest.raises(PathOutsideRoot):
        store.write_text(rel, "no")


def test_write_creates_missing_parent_directories(tmp_path):
    store = Store(str(tmp_path))
    store.write_text("a/b/c.txt", "hello")
    assert store.read_text("a/b/c.txt") == "hello"


def test_missing_directory_lists_as_empty(tmp_path):
    assert Store(str(tmp_path)).list_dir("nothing/here") == []


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        Store(str(tmp_path)).read_text("nothing.txt")


def test_move_keeps_the_content_and_clears_the_old_place(tmp_path):
    store = Store(str(tmp_path))
    store.write_text("files/note.md", "body")
    store.move("files/note.md", "trash/note.md")
    assert store.read_text("trash/note.md") == "body"
    assert not store.exists("files/note.md")


def test_root_is_created_on_first_write_not_on_construction(tmp_path):
    root = tmp_path / "mira-root"
    store = Store(str(root))
    assert not os.path.exists(root)
    store.write_text("a.txt", "x")
    assert os.path.exists(root)
```

- [ ] **Adım 2: Testleri koş, başarısız olduklarını gör**

`python -m pytest d:\code\github\internal-tools\mira -q`
Beklenen: FAIL — `ModuleNotFoundError: No module named 'backend.services.store'`

- [ ] **Adım 3: Servisi yaz**

`mira/backend/services/store/__init__.py` — boş.

`mira/backend/services/store/store.py`:

```python
"""Store -- file access under one root. Knows no project, chat or file concept."""
import os


class PathOutsideRoot(Exception):
    """A relative path would have escaped the store's root."""


class Store:
    def __init__(self, root):
        self._root = os.path.abspath(root)

    def _full(self, rel):
        # The root is a jail. Today every caller is our own code, so this catches a bug; from Faz 8
        # on a filename comes from the model, and then the same rule catches an attack.
        if os.path.isabs(rel) or os.path.splitdrive(rel)[0]:
            raise PathOutsideRoot(rel)
        full = os.path.abspath(os.path.join(self._root, rel))
        if full != self._root and not full.startswith(self._root + os.sep):
            raise PathOutsideRoot(rel)
        return full

    def read_text(self, rel):
        with open(self._full(rel), encoding="utf-8") as handle:
            return handle.read()

    def write_text(self, rel, text):
        full = self._full(rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def list_dir(self, rel):
        # An empty directory is a normal state -- every screen starts with "nothing here yet" -- so
        # a missing one answers with the same emptiness instead of making every caller guard it.
        # A missing *file*, in contrast, is the caller's mistake and read_text lets it raise.
        try:
            return sorted(os.listdir(self._full(rel)))
        except FileNotFoundError:
            return []

    def exists(self, rel):
        return os.path.exists(self._full(rel))

    def mtime(self, rel):
        return os.path.getmtime(self._full(rel))

    def move(self, src_rel, dst_rel):
        destination = self._full(dst_rel)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        os.replace(self._full(src_rel), destination)
```

- [ ] **Adım 4: Testleri koş, geçtiklerini gör**

`python -m pytest d:\code\github\internal-tools\mira -q`
Beklenen: 14 test PASS (Faz 0'ın 5'i + bu 9'u).

---

### Task 2: Proje domain'i ve use case'leri

**Dosyalar:**
- Oluştur: `mira/backend/features/workspace/__init__.py`,
  `mira/backend/features/workspace/domain/__init__.py`,
  `mira/backend/features/workspace/domain/project.py`,
  `mira/backend/features/workspace/domain/ports.py`,
  `mira/backend/features/workspace/domain/usecases/__init__.py`,
  `mira/backend/features/workspace/domain/usecases/create_project.py`,
  `mira/backend/features/workspace/domain/usecases/list_projects.py`
- Test: `mira/backend/tests/test_project_usecases.py`

**Arayüzler:**
- Üretir: `Project(id, name, desc, hue, created_at)` · `ProjectStore` protokolü (`add`, `list_all`) ·
  `create_project(store, new_id, now) -> Project` · `list_projects(store) -> list[Project]` ·
  `NEW_PROJECT_NAME`, `NEW_PROJECT_DESC`, `HUE_STEP`

- [ ] **Adım 1: Başarısız testleri yaz**

`mira/backend/tests/test_project_usecases.py`:

```python
from backend.features.workspace.domain.project import Project
from backend.features.workspace.domain.usecases.create_project import (
    HUE_STEP,
    NEW_PROJECT_DESC,
    NEW_PROJECT_NAME,
    create_project,
)
from backend.features.workspace.domain.usecases.list_projects import list_projects


class FakeProjectStore:
    """A stand-in port: the use cases are tested with no disk and no clock."""

    def __init__(self, projects=()):
        self.projects = list(projects)

    def add(self, project):
        self.projects.append(project)

    def list_all(self):
        return list(self.projects)


def _project(pid, created_at):
    return Project(id=pid, name=pid, desc="", hue=0, created_at=created_at)


def test_new_project_is_born_with_the_default_name_and_description():
    store = FakeProjectStore()
    project = create_project(store, new_id="pabc", now="2026-08-09T10:00:00+00:00")
    assert project.name == NEW_PROJECT_NAME
    assert project.desc == NEW_PROJECT_DESC
    assert project.id == "pabc"
    assert project.created_at == "2026-08-09T10:00:00+00:00"


def test_created_project_is_handed_to_the_store():
    store = FakeProjectStore()
    project = create_project(store, new_id="pabc", now="2026-08-09T10:00:00+00:00")
    assert store.projects == [project]


def test_hue_steps_with_the_number_of_existing_projects():
    store = FakeProjectStore([_project("p1", "2026-08-01T00:00:00+00:00")])
    project = create_project(store, new_id="p2", now="2026-08-09T10:00:00+00:00")
    assert project.hue == HUE_STEP


def test_hue_wraps_around_the_colour_wheel():
    existing = [_project(f"p{i}", "2026-08-01T00:00:00+00:00") for i in range(8)]
    project = create_project(FakeProjectStore(existing), new_id="p9", now="2026-08-09T10:00:00+00:00")
    assert 0 <= project.hue < 360


def test_projects_come_back_oldest_first():
    store = FakeProjectStore([
        _project("zzz", "2026-08-05T00:00:00+00:00"),
        _project("aaa", "2026-08-01T00:00:00+00:00"),
    ])
    assert [p.id for p in list_projects(store)] == ["aaa", "zzz"]
```

Son test bilerek id'leri ters alfabetik seçiyor: sıranın dizin adından değil `createdAt`'ten geldiğini
kanıtlamanın tek yolu bu.

- [ ] **Adım 2: Testleri koş, başarısız olduklarını gör**

`python -m pytest d:\code\github\internal-tools\mira -q`
Beklenen: FAIL — `ModuleNotFoundError: No module named 'backend.features.workspace'`

- [ ] **Adım 3: Domain'i yaz**

Boş dosyalar: `workspace/__init__.py`, `workspace/domain/__init__.py`,
`workspace/domain/usecases/__init__.py`.

`project.py`:

```python
"""Project -- the workspace that owns a set of chats and a set of files."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    id: str
    name: str
    desc: str
    hue: int
    created_at: str
```

`ports.py`:

```python
"""Ports the workspace domain depends on. Implementations live in data/."""
from typing import Protocol

from backend.features.workspace.domain.project import Project


class ProjectStore(Protocol):
    def add(self, project: Project) -> None:
        """Persist a new project. Raises if its id is already taken."""

    def list_all(self) -> list[Project]:
        """Every project, in no particular order."""
```

`usecases/create_project.py`:

```python
"""Create a project -- the defaults a new project is born with."""
from backend.features.workspace.domain.project import Project

# The design never asks for a name up front: the project is born named and renamed afterwards.
NEW_PROJECT_NAME = "New project"
NEW_PROJECT_DESC = "Click to add a description."
# Successive projects step around the colour wheel instead of repeating a hue.
HUE_STEP = 47


def create_project(store, new_id, now):
    # The hue is decided once and stored: deleting a neighbour later must not recolour the card.
    hue = (len(store.list_all()) * HUE_STEP) % 360
    project = Project(
        id=new_id,
        name=NEW_PROJECT_NAME,
        desc=NEW_PROJECT_DESC,
        hue=hue,
        created_at=now,
    )
    store.add(project)
    return project
```

`usecases/list_projects.py`:

```python
"""List projects oldest first -- the order both the sidebar and the home cards show."""


def list_projects(store):
    # The id is opaque, so it says nothing about age; createdAt is the only thing that does. The id
    # is the tie-break so two projects created in the same second still come back in a fixed order.
    return sorted(store.list_all(), key=lambda project: (project.created_at, project.id))
```

- [ ] **Adım 4: Testleri koş, geçtiklerini gör**

`python -m pytest d:\code\github\internal-tools\mira -q`
Beklenen: 19 test PASS.

---

### Task 3: `project.json` deposu

**Dosyalar:**
- Oluştur: `mira/backend/features/workspace/data/__init__.py`,
  `mira/backend/features/workspace/data/file_project_store.py`
- Test: `mira/backend/tests/test_file_project_store.py`

**Arayüzler:**
- Tüketir: `Store`, `Project`
- Üretir: `FileProjectStore(store)` — `ProjectStore` protokolünü gerçekler · `ProjectIdTaken` ·
  `PROJECT_FILE`

- [ ] **Adım 1: Başarısız testleri yaz**

`mira/backend/tests/test_file_project_store.py`:

```python
import pytest

from backend.features.workspace.data.file_project_store import (
    PROJECT_FILE,
    FileProjectStore,
    ProjectIdTaken,
)
from backend.features.workspace.domain.project import Project
from backend.services.store.store import Store


def _store(tmp_path):
    return FileProjectStore(Store(str(tmp_path)))


def _project(pid="pabc", name="Thesis", created_at="2026-08-09T10:00:00+00:00"):
    return Project(id=pid, name=name, desc="Notes.", hue=94, created_at=created_at)


def test_project_survives_a_new_store_instance(tmp_path):
    _store(tmp_path).add(_project())
    # A second instance reads from disk only -- this is what "the app rebuilds itself from files"
    # means, and it is what a server restart does.
    assert _store(tmp_path).list_all() == [_project()]


def test_existing_id_is_not_overwritten(tmp_path):
    store = _store(tmp_path)
    store.add(_project(name="First"))
    with pytest.raises(ProjectIdTaken):
        store.add(_project(name="Second"))
    assert store.list_all()[0].name == "First"


def test_entries_without_a_project_file_are_ignored(tmp_path):
    raw = Store(str(tmp_path))
    raw.write_text("stray/notes.txt", "not a project")
    FileProjectStore(raw).add(_project())
    assert [p.id for p in FileProjectStore(raw).list_all()] == ["pabc"]


def test_empty_root_lists_nothing(tmp_path):
    assert _store(tmp_path).list_all() == []


def test_the_id_is_the_directory_name_and_is_not_repeated_in_the_file(tmp_path):
    raw = Store(str(tmp_path))
    FileProjectStore(raw).add(_project())
    assert "pabc" not in raw.read_text(f"pabc/{PROJECT_FILE}")
```

- [ ] **Adım 2: Testleri koş, başarısız olduklarını gör**

`python -m pytest d:\code\github\internal-tools\mira -q`
Beklenen: FAIL — `No module named 'backend.features.workspace.data'`

- [ ] **Adım 3: Depoyu yaz**

`data/__init__.py` — boş.

`data/file_project_store.py`:

```python
"""FileProjectStore -- the only place that knows the project.json schema."""
import json

from backend.features.workspace.domain.project import Project

PROJECT_FILE = "project.json"


class ProjectIdTaken(Exception):
    """A project directory already exists -- the user's work is never overwritten."""


class FileProjectStore:
    def __init__(self, store):
        self._store = store

    def add(self, project):
        path = f"{project.id}/{PROJECT_FILE}"
        if self._store.exists(path):
            raise ProjectIdTaken(project.id)
        # The id is the directory name, so it is not written into the file: no artifact repeats an
        # answer another one already gives.
        self._store.write_text(
            path,
            json.dumps(
                {
                    "name": project.name,
                    "desc": project.desc,
                    "hue": project.hue,
                    "createdAt": project.created_at,
                },
                ensure_ascii=False,
                indent=2,
            ),
        )

    def list_all(self):
        projects = []
        for entry in self._store.list_dir(""):
            path = f"{entry}/{PROJECT_FILE}"
            if not self._store.exists(path):
                continue  # anything else living under the root is not ours to read
            raw = json.loads(self._store.read_text(path))
            projects.append(
                Project(
                    id=entry,
                    name=raw["name"],
                    desc=raw["desc"],
                    hue=raw["hue"],
                    created_at=raw["createdAt"],
                )
            )
        return projects
```

- [ ] **Adım 4: Testleri koş, geçtiklerini gör**

`python -m pytest d:\code\github\internal-tools\mira -q`
Beklenen: 24 test PASS.

---

### Task 4: Uç noktalar ve bağlama

**Dosyalar:**
- Oluştur: `mira/backend/features/workspace/presentation/__init__.py`,
  `mira/backend/features/workspace/presentation/routes.py`
- Değiştir: `mira/main.py`
- Test: `mira/backend/tests/test_projects_api.py`

**Arayüzler:**
- Tüketir: `create_app(dist_dir, blueprints)`, `FileProjectStore`, `Store`, use case'ler
- Üretir: `make_workspace_bp(project_store) -> Blueprint` · `GET /api/projects` ·
  `POST /api/projects`

- [ ] **Adım 1: Başarısız testleri yaz**

`mira/backend/tests/test_projects_api.py`:

```python
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.web.app import create_app


def _client(tmp_path):
    project_store = FileProjectStore(Store(str(tmp_path)))
    return create_app(dist_dir=str(tmp_path), blueprints=(make_workspace_bp(project_store),)).test_client()


def test_empty_root_returns_an_empty_list(tmp_path):
    resp = _client(tmp_path).get("/api/projects")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_created_project_appears_in_the_list(tmp_path):
    client = _client(tmp_path)
    created = client.post("/api/projects")
    assert created.status_code == 201
    body = created.get_json()
    assert body["name"] == "New project"
    assert body["id"].startswith("p")
    assert client.get("/api/projects").get_json() == [body]


def test_projects_survive_a_fresh_app(tmp_path):
    _client(tmp_path).post("/api/projects")
    assert len(_client(tmp_path).get("/api/projects").get_json()) == 1


def test_two_projects_get_different_ids_and_hues(tmp_path):
    client = _client(tmp_path)
    first = client.post("/api/projects").get_json()
    second = client.post("/api/projects").get_json()
    assert first["id"] != second["id"]
    assert first["hue"] != second["hue"]
```

- [ ] **Adım 2: Testleri koş, başarısız olduklarını gör**

`python -m pytest d:\code\github\internal-tools\mira -q`
Beklenen: FAIL — `No module named 'backend.features.workspace.presentation'`

- [ ] **Adım 3: Rotaları yaz**

`presentation/__init__.py` — boş.

`presentation/routes.py`:

```python
"""Workspace HTTP routes -- request/response translation only, no business rules."""
import uuid
from datetime import datetime, timezone

from flask import Blueprint, jsonify

from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.list_projects import list_projects


def make_workspace_bp(project_store):
    workspace_bp = Blueprint("workspace", __name__)

    @workspace_bp.get("/api/projects")
    def get_projects():
        return jsonify([_as_json(project) for project in list_projects(project_store)])

    @workspace_bp.post("/api/projects")
    def post_project():
        # Creating takes no input: the design never asks for a name up front.
        project = create_project(project_store, new_id=_new_id(), now=_now())
        return jsonify(_as_json(project)), 201

    return workspace_bp


def _new_id():
    # Opaque and immutable: renaming a project must not move its directory or break a link.
    return "p" + uuid.uuid4().hex[:12]


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _as_json(project):
    return {
        "id": project.id,
        "name": project.name,
        "desc": project.desc,
        "hue": project.hue,
        "createdAt": project.created_at,
    }
```

- [ ] **Adım 4: `main.py`'yi bağla**

```python
"""Composition root -- the only place that wires concrete classes together."""
from backend import config
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.web.app import create_app

app = create_app(blueprints=(make_workspace_bp(FileProjectStore(Store(config.ROOT))),))

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT)
```

- [ ] **Adım 5: Testleri koş, geçtiklerini gör**

`python -m pytest d:\code\github\internal-tools\mira -q`
Beklenen: 28 test PASS.

---

## Öz-denetim

**Spec kapsaması.** Faz 1 spec'inin sekiz kanıtlanacak cümlesi: (1) kök dışı yol → Task 1
`test_paths_escaping_the_root_are_rejected` · (2) olmayan dizin/dosya → Task 1
`test_missing_directory_lists_as_empty`, `test_missing_file_raises` · (3) taşıma → Task 1
`test_move_keeps_the_content_and_clears_the_old_place` · (4) yeniden kurulunca aynı liste → Task 3
`test_project_survives_a_new_store_instance`, Task 4 `test_projects_survive_a_fresh_app` · (5) sıra
`createdAt`'ten → Task 2 `test_projects_come_back_oldest_first` · (6) üstüne yazılmıyor → Task 3
`test_existing_id_is_not_overwritten` · (7) hue → Task 2 iki test · (8) boş kök → Task 4
`test_empty_root_returns_an_empty_list`. Spec'in "alt dizinler bu fazda açılmaz" kararı Task 3'te
uygulanıyor: `add` yalnız `project.json` yazıyor.

**Ad tutarlılığı.** `Project(id, name, desc, hue, created_at)` Task 2'de tanımlanıyor; Task 3 ve 4
aynı alan adlarını kullanıyor. Diskteki ve HTTP'deki alan adı `createdAt`, Python tarafındaki
`created_at` — çeviri yalnız iki yerde (`file_project_store.py`, `routes.py`) yapılıyor ve ikisi de
sınır katmanı. `ProjectStore` protokolünün `add`/`list_all` adları hem sahte hem gerçek uygulamada
aynı.

**Yer tutucu yok.** Bütün adımlarda gerçek kod var; hiçbir adım "uygun hata yönetimi ekle" demiyor.
