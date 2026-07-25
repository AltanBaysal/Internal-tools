# Queen Editor — Bölüm 3: Proje · Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Projeler ekranı çalışsın: Drive'da `MyDrive/queenEditor/<ad>/` klasörü oluşturulsun, kartlar listelensin (en son değişen üstte), geçersiz/çakışan adda sunucunun Türkçe mesajı modalda görünsün.

**Architecture:** İlk gerçek feature iskeleti. `services/drive/storage.py` yalnız dosya sistemi konuşur; `features/projects` üç katman (`domain` saf kural + port + use case, `data` port gerçeklemesi, `presentation` Flask route). Bağlama yalnız `main.py`'de (`functools.partial` ile use case'ler store'a bağlanır, blueprint `create_app`'e enjekte edilir) — `web/` hiçbir feature'ı import etmez. Frontend aynı düzende: `vendor/kit.jsx` tasarımdan kopya, `features/projects` bileşenleri + `useProjects` hook'u, `shared/` fetch sarmalayıcı ve tarih biçimleyici.

**Tech Stack:** Python 3 · Flask · pytest · React 18 · Vite 5 (build-time) · Google Colab (Drive mount) · cloudflared

**Spec:** [2026-07-25-queen-editor-b3-proje-design.md](../specs/2026-07-25-queen-editor-b3-proje-design.md) · **Şemsiye:** [2026-07-24-queen-editor-v1-design.md](../specs/2026-07-24-queen-editor-v1-design.md)

## Global Constraints

- **Dil ayrımı:** kod yorumları, docstring, commit mesajları **İngilizce**; kullanıcıya görünen UI metni ve notebook markdown/`print`/`assert` **Türkçe**.
- **Katman yasakları:** `feature ↛ feature`, `servis ↛ feature`, `servis ↛ servis`. `domain/` hiçbir dış şey import etmez (`flask`, `os`, `requests` yok). `data/` düzeni/şemayı bilen tek yer. `presentation/` iş kuralı içermez. Somut bağlama yalnız `backend/main.py`.
- **Ad kuralları tek yerde:** `domain/name_rules.py`. Tarayıcıda kural kopyası **yasak** — mesajlar sunucudan gelir.
- **Hata metni uydurulmaz:** `OSError` yakalandığında gövdeye `str(exc)` yazılır (repo kuralı: servisin/işletim sisteminin kendi çıktısı).
- **Drive kökünü backend oluşturmaz.** Kök yoksa istisna yukarı çıkar → 500 + gerçek metin. Kökü notebook oluşturur.
- **Vendor dokunulmazlığı:** `frontend/src/vendor/` tasarımdan birebir; **yalnız ihracat sınırı** uyarlanır (`Object.assign(window, …)` → `export {…}`). Gövdeler ve `styles.css` elle düzenlenmez — gereken CSS düzeltmesi `shared/app.css`'e yazılır.
- **Derleme (ComfyUI deseni):** `queen-editor/frontend/` içinde `npm run build`; `dist/` commit'lenir, `node_modules/` commit'lenmez. Colab derlemez.
- **Test komutu:** `queen-editor/` içinden `pytest` — Drive, ComfyUI, tünel gerektirmez. Bölüm 2'nin 4 testi bozulmadan geçmeli.
- **Commit politikası:** Kullanıcı Colab'da doğrulayıp "commit" demeden **hiçbir şey commit edilmez** (spec dosyası dahil). Son task bunu kapı olarak taşır.
- **Kapsam dışı (bu bölümde yok):** proje ekranı / kart tıklama · `prompts.json` · silme-yeniden adlandırma · foto sayısı/kapak · ComfyUI.

---

### Task 1: Drive servisi + `config.DRIVE_ROOT`

**Files:**
- Modify: `queen-editor/backend/config.py`
- Create: `queen-editor/backend/services/__init__.py` (boş)
- Create: `queen-editor/backend/services/drive/__init__.py` (boş)
- Create: `queen-editor/backend/services/drive/storage.py`
- Test: `queen-editor/backend/tests/test_drive_storage.py`

**Interfaces:**
- Consumes: (yok)
- Produces: `config.DRIVE_ROOT` (str) · `DriveStorage(root)` — `list_dirs() -> list[tuple[str, float]]`, `make_dir(name) -> float | None` (`None` = zaten var).

- [ ] **Step 1: Failing test yaz** — `queen-editor/backend/tests/test_drive_storage.py`

```python
import pytest

from backend.services.drive.storage import DriveStorage


def test_make_dir_creates_folder_and_returns_mtime(tmp_path):
    storage = DriveStorage(str(tmp_path))
    mtime = storage.make_dir("düğün")
    assert mtime is not None and mtime > 0
    assert (tmp_path / "düğün").is_dir()


def test_make_dir_returns_none_when_name_taken(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.make_dir("düğün")
    assert storage.make_dir("düğün") is None


def test_list_dirs_returns_name_and_mtime(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.make_dir("düğün")
    storage.make_dir("kapak çekimi")
    entries = storage.list_dirs()
    assert sorted(name for name, _ in entries) == ["düğün", "kapak çekimi"]
    assert all(mtime > 0 for _, mtime in entries)


def test_list_dirs_skips_files(tmp_path):
    (tmp_path / "not-a-project.txt").write_text("x", encoding="utf-8")
    assert DriveStorage(str(tmp_path)).list_dirs() == []


def test_list_dirs_raises_when_root_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        DriveStorage(str(tmp_path / "yok")).list_dirs()
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && pytest backend/tests/test_drive_storage.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'backend.services'`.

- [ ] **Step 3: Boş `__init__.py` dosyalarını yaz**

`queen-editor/backend/services/__init__.py` ve `queen-editor/backend/services/drive/__init__.py` — ikisi de boş (paket işaretleyici).

- [ ] **Step 4: `backend/services/drive/storage.py` yaz**

```python
"""Folder operations under one root -- knows no project, no JSON, no schema.

On Colab `root` sits inside the mounted Drive (see app.ipynb); locally it is any folder.
A missing root is NOT created here: that would silently write to Colab's local disk when the
Drive mount failed, so the error must reach the caller.
"""
import os


class DriveStorage:
    def __init__(self, root):
        self.root = root

    def list_dirs(self):
        """[(name, mtime)] for every direct subfolder of root. Files are skipped."""
        with os.scandir(self.root) as entries:
            return [(e.name, e.stat().st_mtime) for e in entries if e.is_dir()]

    def make_dir(self, name):
        """Create root/name. Returns its mtime, or None when the name is already taken."""
        path = os.path.join(self.root, name)
        try:
            os.mkdir(path)
        except FileExistsError:
            return None
        return os.stat(path).st_mtime
```

- [ ] **Step 5: `backend/config.py`'ye `DRIVE_ROOT` ekle**

`PORT = 8000` satırının altına:

```python
# Every project is a folder under this root. Colab mounts Drive and passes the real path in
# QE_DRIVE_ROOT (app.ipynb); the default is only a sane guess for a Colab runtime.
DRIVE_ROOT = os.environ.get("QE_DRIVE_ROOT", "/content/drive/MyDrive/queenEditor")
```

- [ ] **Step 6: Testi çalıştır, geçsin**

Run: `cd queen-editor && pytest -q`
Expected: PASS (Bölüm 2'nin 4 testi + 5 yeni test = 9).

---

### Task 2: Ad kuralları (saf domain)

**Files:**
- Create: `queen-editor/backend/features/__init__.py` (boş)
- Create: `queen-editor/backend/features/projects/__init__.py` (boş)
- Create: `queen-editor/backend/features/projects/domain/__init__.py` (boş)
- Create: `queen-editor/backend/features/projects/domain/name_rules.py`
- Test: `queen-editor/backend/tests/test_name_rules.py`

**Interfaces:**
- Consumes: (yok — saf fonksiyon)
- Produces: `name_rules.validate(name) -> str | None` — Türkçe hata mesajı, geçerliyse `None`. `name_rules.MAX_LENGTH = 64`.

- [ ] **Step 1: Failing test yaz** — `queen-editor/backend/tests/test_name_rules.py`

```python
import pytest

from backend.features.projects.domain import name_rules

FORBIDDEN_MESSAGE = 'Proje adında şu karakterler kullanılamaz: / \\ : * ? " < > |'


@pytest.mark.parametrize(
    "name",
    ["düğün", "kapak çekimi", "lookbook-mayıs", "test_2", "a", "ü" * 64],
)
def test_valid_names_return_none(name):
    assert name_rules.validate(name) is None


@pytest.mark.parametrize(
    "name, expected",
    [
        ("", "Proje adı boş olamaz."),
        ("   ", "Proje adı boş olamaz."),
        (" düğün", "Proje adı boşlukla başlayamaz veya bitemez."),
        ("düğün ", "Proje adı boşlukla başlayamaz veya bitemez."),
        ("ü" * 65, "Proje adı en fazla 64 karakter olabilir."),
        ("foto/deneme", FORBIDDEN_MESSAGE),
        ("C:\\yol", FORBIDDEN_MESSAGE),
        ("a\tb", FORBIDDEN_MESSAGE),
        (".gizli", "Proje adı nokta ile başlayamaz veya bitemez."),
        ("düğün.", "Proje adı nokta ile başlayamaz veya bitemez."),
        ("..", "Proje adı nokta ile başlayamaz veya bitemez."),
    ],
)
def test_invalid_names_return_message(name, expected):
    assert name_rules.validate(name) == expected
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && pytest backend/tests/test_name_rules.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'backend.features'`.

- [ ] **Step 3: Boş `__init__.py` dosyalarını yaz**

`backend/features/__init__.py`, `backend/features/projects/__init__.py`, `backend/features/projects/domain/__init__.py` — üçü de boş.

- [ ] **Step 4: `backend/features/projects/domain/name_rules.py` yaz**

```python
"""Project name validation -- the single source of truth for the rules.

Pure: no filesystem, no Flask, no schema knowledge. The name becomes a Drive folder name, so the
rules are the filesystem's plus a length cap. Turkish letters, spaces, dashes and underscores are
allowed on purpose ("kapak çekimi"). Messages are user-facing, so they are Turkish; the frontend
prints them verbatim and keeps no copy of the rules.
"""

MAX_LENGTH = 64
FORBIDDEN_CHARS = '/\\:*?"<>|'


def validate(name):
    """Return a Turkish error message, or None when the name is usable."""
    if not isinstance(name, str) or not name.strip():
        return "Proje adı boş olamaz."
    if name != name.strip():
        return "Proje adı boşlukla başlayamaz veya bitemez."
    if len(name) > MAX_LENGTH:
        return f"Proje adı en fazla {MAX_LENGTH} karakter olabilir."
    # Control characters break folder names as badly as the reserved punctuation does.
    if any(ch in FORBIDDEN_CHARS or ord(ch) < 32 for ch in name):
        return 'Proje adında şu karakterler kullanılamaz: / \\ : * ? " < > |'
    if name.startswith(".") or name.endswith("."):
        return "Proje adı nokta ile başlayamaz veya bitemez."
    return None
```

- [ ] **Step 5: Testi çalıştır, geçsin**

Run: `cd queen-editor && pytest -q`
Expected: PASS (9 + 17 = 26 test).

---

### Task 3: `Project` + port + use case'ler

**Files:**
- Create: `queen-editor/backend/features/projects/domain/project.py`
- Create: `queen-editor/backend/features/projects/domain/ports.py`
- Create: `queen-editor/backend/features/projects/domain/usecases/__init__.py` (boş)
- Create: `queen-editor/backend/features/projects/domain/usecases/list_projects.py`
- Create: `queen-editor/backend/features/projects/domain/usecases/create_project.py`
- Test: `queen-editor/backend/tests/test_project_usecases.py`

**Interfaces:**
- Consumes: `name_rules.validate` (Task 2)
- Produces:
  - `Project(name: str, modified_at: float)` — frozen dataclass
  - `ProjectStore` Protocol: `list() -> list[Project]`, `create(name) -> Project | None`
  - `list_projects(store) -> list[Project]` — `modified_at` azalan
  - `create_project(store, name) -> Project`; `InvalidName` / `NameTaken` istisnaları (mesajları Türkçe, doğrudan kullanıcıya gider)

- [ ] **Step 1: Failing test yaz** — `queen-editor/backend/tests/test_project_usecases.py`

```python
import pytest

from backend.features.projects.domain.project import Project
from backend.features.projects.domain.usecases.create_project import (
    InvalidName,
    NameTaken,
    create_project,
)
from backend.features.projects.domain.usecases.list_projects import list_projects


class FakeStore:
    """In-memory ProjectStore -- no Drive, no filesystem."""

    def __init__(self, projects=()):
        self.projects = list(projects)

    def list(self):
        return list(self.projects)

    def create(self, name):
        if any(p.name == name for p in self.projects):
            return None
        project = Project(name, 100.0)
        self.projects.append(project)
        return project


def test_list_projects_newest_change_first():
    store = FakeStore([Project("eski", 100.0), Project("yeni", 300.0), Project("orta", 200.0)])
    assert [p.name for p in list_projects(store)] == ["yeni", "orta", "eski"]


def test_list_projects_returns_empty_list():
    assert list_projects(FakeStore()) == []


def test_create_project_returns_created_project():
    store = FakeStore()
    project = create_project(store, "kapak çekimi")
    assert project.name == "kapak çekimi"
    assert [p.name for p in store.list()] == ["kapak çekimi"]


def test_create_project_rejects_invalid_name_without_touching_store():
    store = FakeStore()
    with pytest.raises(InvalidName) as exc:
        create_project(store, "foto/deneme")
    assert "kullanılamaz" in str(exc.value)
    assert store.list() == []


def test_create_project_raises_when_name_taken():
    store = FakeStore([Project("düğün", 100.0)])
    with pytest.raises(NameTaken) as exc:
        create_project(store, "düğün")
    assert str(exc.value) == "Bu ad zaten kullanılıyor. Başka bir ad dene."
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && pytest backend/tests/test_project_usecases.py -q`
Expected: FAIL — `ModuleNotFoundError: ...domain.project`.

- [ ] **Step 3: `domain/project.py` yaz**

```python
"""The project entity: a name and when its folder last changed."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    name: str
    modified_at: float
```

- [ ] **Step 4: `domain/ports.py` yaz**

```python
"""Ports this feature needs. Implemented in data/, faked in tests -- domain stays pure."""
from typing import Protocol

from backend.features.projects.domain.project import Project


class ProjectStore(Protocol):
    def list(self) -> list[Project]:
        """Every project. Order is not guaranteed -- the use case sorts."""
        ...

    def create(self, name: str) -> Project | None:
        """Create the project; None means the name is already taken."""
        ...
```

- [ ] **Step 5: `domain/usecases/__init__.py` (boş) ve `usecases/list_projects.py` yaz**

```python
"""Every project, newest change first -- the order the projects screen shows."""


def list_projects(store):
    return sorted(store.list(), key=lambda p: p.modified_at, reverse=True)
```

- [ ] **Step 6: `domain/usecases/create_project.py` yaz**

```python
"""Create one project: validate the name, then let the store settle the conflict.

Both exception messages are user-facing Turkish -- presentation forwards them untouched, so the
rules and their wording live in exactly one place.
"""
from backend.features.projects.domain import name_rules


class InvalidName(Exception):
    """The name broke a rule (message is the user-facing text)."""


class NameTaken(Exception):
    """A project with this name already exists."""


def create_project(store, name):
    error = name_rules.validate(name)
    if error:
        raise InvalidName(error)
    project = store.create(name)
    if project is None:
        raise NameTaken("Bu ad zaten kullanılıyor. Başka bir ad dene.")
    return project
```

- [ ] **Step 7: Testi çalıştır, geçsin**

Run: `cd queen-editor && pytest -q`
Expected: PASS (26 + 5 = 31 test).

---

### Task 4: `data/project_store.py` (portun gerçeklemesi)

**Files:**
- Create: `queen-editor/backend/features/projects/data/__init__.py` (boş)
- Create: `queen-editor/backend/features/projects/data/project_store.py`
- Test: `queen-editor/backend/tests/test_project_store.py`

**Interfaces:**
- Consumes: `DriveStorage` (Task 1) · `Project` (Task 3)
- Produces: `DriveProjectStore(storage)` — `ProjectStore` portunu gerçekler (`list()`, `create(name)`).

- [ ] **Step 1: Failing test yaz** — `queen-editor/backend/tests/test_project_store.py`

```python
from backend.features.projects.data.project_store import DriveProjectStore
from backend.services.drive.storage import DriveStorage


def store_at(path):
    return DriveProjectStore(DriveStorage(str(path)))


def test_create_makes_folder_and_returns_project(tmp_path):
    created = store_at(tmp_path).create("kapak çekimi")
    assert created.name == "kapak çekimi"
    assert created.modified_at > 0
    assert (tmp_path / "kapak çekimi").is_dir()


def test_create_returns_none_when_folder_exists(tmp_path):
    store = store_at(tmp_path)
    store.create("düğün")
    assert store.create("düğün") is None


def test_list_returns_projects_for_every_folder(tmp_path):
    store = store_at(tmp_path)
    store.create("düğün")
    store.create("test")
    assert sorted(p.name for p in store.list()) == ["düğün", "test"]
    assert all(p.modified_at > 0 for p in store.list())
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && pytest backend/tests/test_project_store.py -q`
Expected: FAIL — `ModuleNotFoundError: ...data.project_store`.

- [ ] **Step 3: `data/__init__.py` (boş) ve `data/project_store.py` yaz**

```python
"""ProjectStore over DriveStorage -- the only place that knows a project IS a folder under the
Drive root (queenEditor/<name>/). The domain never learns where a project lives."""
from backend.features.projects.domain.project import Project


class DriveProjectStore:
    def __init__(self, storage):
        self.storage = storage

    def list(self):
        return [Project(name, mtime) for name, mtime in self.storage.list_dirs()]

    def create(self, name):
        mtime = self.storage.make_dir(name)
        if mtime is None:
            return None
        return Project(name, mtime)
```

- [ ] **Step 4: Testi çalıştır, geçsin**

Run: `cd queen-editor && pytest -q`
Expected: PASS (31 + 3 = 34 test).

---

### Task 5: Route'lar + `create_app` enjeksiyonu + composition root

**Files:**
- Create: `queen-editor/backend/features/projects/presentation/__init__.py` (boş)
- Create: `queen-editor/backend/features/projects/presentation/routes.py`
- Modify: `queen-editor/backend/web/app.py`
- Modify: `queen-editor/backend/main.py`
- Test: `queen-editor/backend/tests/test_projects_routes.py`

**Interfaces:**
- Consumes: `create_project` / `list_projects` use case'leri (Task 3) · `DriveProjectStore` (Task 4) · `create_app` (Bölüm 2)
- Produces: `make_projects_blueprint(list_projects, create_project) -> Blueprint` (argümanlar store'a **bağlanmış** çağrılabilirler) · `create_app(dist_dir=…, blueprints=())` · `GET /api/projects` · `POST /api/projects`.

- [ ] **Step 1: Failing test yaz** — `queen-editor/backend/tests/test_projects_routes.py`

```python
import os
from functools import partial

from backend.features.projects.data.project_store import DriveProjectStore
from backend.features.projects.domain.usecases.create_project import create_project
from backend.features.projects.domain.usecases.list_projects import list_projects
from backend.features.projects.presentation.routes import make_projects_blueprint
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app


def client_for(drive_root, dist_dir):
    """Wire the feature by hand -- the same wiring main.py does, but over a temp folder."""
    store = DriveProjectStore(DriveStorage(str(drive_root)))
    blueprint = make_projects_blueprint(
        list_projects=partial(list_projects, store),
        create_project=partial(create_project, store),
    )
    return create_app(dist_dir=str(dist_dir), blueprints=[blueprint]).test_client()


def make_client(tmp_path):
    drive = tmp_path / "drive"
    drive.mkdir()
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("x", encoding="utf-8")
    return client_for(drive, dist), drive


def test_get_projects_empty(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.get("/api/projects")
    assert resp.status_code == 200
    assert resp.get_json() == {"projects": []}


def test_post_creates_folder_and_returns_201(tmp_path):
    client, drive = make_client(tmp_path)
    resp = client.post("/api/projects", json={"name": "kapak çekimi"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["name"] == "kapak çekimi"
    assert isinstance(body["modifiedAt"], int)
    assert (drive / "kapak çekimi").is_dir()


def test_get_projects_newest_change_first(tmp_path):
    client, drive = make_client(tmp_path)
    client.post("/api/projects", json={"name": "eski"})
    client.post("/api/projects", json={"name": "yeni"})
    os.utime(drive / "eski", (1000, 1000))
    os.utime(drive / "yeni", (2000, 2000))
    names = [p["name"] for p in client.get("/api/projects").get_json()["projects"]]
    assert names == ["yeni", "eski"]


def test_post_invalid_name_returns_400(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.post("/api/projects", json={"name": "foto/deneme"})
    assert resp.status_code == 400
    assert "kullanılamaz" in resp.get_json()["error"]


def test_post_duplicate_name_returns_409(tmp_path):
    client, _ = make_client(tmp_path)
    client.post("/api/projects", json={"name": "düğün"})
    resp = client.post("/api/projects", json={"name": "düğün"})
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "Bu ad zaten kullanılıyor. Başka bir ad dene."


def test_post_without_name_returns_400(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.post("/api/projects", json={})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Proje adı boş olamaz."


def test_get_projects_reports_the_real_error_when_root_missing(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("x", encoding="utf-8")
    client = client_for(tmp_path / "olmayan-kok", dist)
    resp = client.get("/api/projects")
    assert resp.status_code == 500
    assert "olmayan-kok" in resp.get_json()["error"]


def test_health_still_works(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/health").get_json() == {"status": "ok"}
```

- [ ] **Step 2: Testi çalıştır, fail gör**

Run: `cd queen-editor && pytest backend/tests/test_projects_routes.py -q`
Expected: FAIL — `ModuleNotFoundError: ...presentation.routes`.

- [ ] **Step 3: `presentation/__init__.py` (boş) ve `presentation/routes.py` yaz**

```python
"""/api/projects -- request/response translation only. No rules, no filesystem knowledge."""
from flask import Blueprint, jsonify, request

from backend.features.projects.domain.usecases.create_project import InvalidName, NameTaken


def make_projects_blueprint(list_projects, create_project):
    """Both arguments are use cases already bound to a store (see main.py)."""
    bp = Blueprint("projects", __name__)

    def payload(project):
        # The UI shows whole seconds; the float's precision means nothing to it.
        return {"name": project.name, "modifiedAt": int(project.modified_at)}

    @bp.get("/api/projects")
    def get_projects():
        try:
            projects = list_projects()
        except OSError as exc:
            # The operating system's own words -- never guess the cause (missing mount, no
            # permission and a wrong path all land here with different messages).
            return jsonify({"error": str(exc)}), 500
        return jsonify({"projects": [payload(p) for p in projects]})

    @bp.post("/api/projects")
    def post_project():
        name = (request.get_json(silent=True) or {}).get("name", "")
        try:
            project = create_project(name)
        except InvalidName as exc:
            return jsonify({"error": str(exc)}), 400
        except NameTaken as exc:
            return jsonify({"error": str(exc)}), 409
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500
        return jsonify(payload(project)), 201

    return bp
```

- [ ] **Step 4: `backend/web/app.py`'yi blueprint enjeksiyonuna açacak şekilde değiştir**

`create_app` imzası ve blueprint kaydı (dosyanın kalanı — statik servis — aynı kalır):

```python
def create_app(dist_dir=config.DIST_DIR, blueprints=()):
    app = Flask(__name__, static_folder=None)  # dist is served by our own routes
    app.config["DIST_DIR"] = dist_dir
    app.register_blueprint(health_bp)
    # Features are injected by the composition root: this infrastructure layer must not import
    # any feature (CODE-STANDARD.md).
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
```

- [ ] **Step 5: `backend/main.py`'yi composition root olarak yaz**

```python
"""Composition root -- build services, wire them into features, start Flask.
Run as: python -m backend.main"""
from functools import partial

from backend import config
from backend.features.projects.data.project_store import DriveProjectStore
from backend.features.projects.domain.usecases.create_project import create_project
from backend.features.projects.domain.usecases.list_projects import list_projects
from backend.features.projects.presentation.routes import make_projects_blueprint
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app

_project_store = DriveProjectStore(DriveStorage(config.DRIVE_ROOT))
_projects_bp = make_projects_blueprint(
    list_projects=partial(list_projects, _project_store),
    create_project=partial(create_project, _project_store),
)

app = create_app(blueprints=[_projects_bp])

if __name__ == "__main__":
    print(f"Proje kökü: {config.DRIVE_ROOT}")
    app.run(host=config.HOST, port=config.PORT)
```

- [ ] **Step 6: Bütün testleri çalıştır**

Run: `cd queen-editor && pytest -q`
Expected: PASS (34 + 8 = 42 test; Bölüm 2'nin health + statik testleri dahil).

---

### Task 6: `vendor/kit.jsx` (tasarımdan) + CODE-STANDARD vendor kuralı

**Files:**
- Create: `queen-editor/frontend/src/vendor/kit.jsx`
- Modify: `queen-editor/CODE-STANDARD.md`

**Interfaces:**
- Consumes: (yok)
- Produces: `Hand · Note · Mono · HL · Btn · Seq · Grip · Segment · ImgPH · Status · Pill · Icon · Arrow` — `vendor/kit.jsx`'ten ESM ihracatı. Task 8 bunlardan `Hand`, `Mono`, `Note`, `Btn`, `Icon` kullanır.

- [ ] **Step 1: Tasarımdan kit dosyasını çek**

DesignSync `get_file`, projectId `efad1f83-69d3-4e07-89fa-3783839c81c3`, path `wireframe-kit.jsx` → içeriği `queen-editor/frontend/src/vendor/kit.jsx`'e **birebir** yaz (bileşen gövdelerine, SVG'lere, yorumlara dokunma).

- [ ] **Step 2: Yalnız ihracat sınırını ESM'e çevir**

Dosyanın sonundaki

```js
// Export to window
Object.assign(window, {
  Hand, Note, Mono, HL, Btn, Seq, Grip, Segment, ImgPH, Status, Pill, Icon, Arrow,
});
```

bloğunu şununla değiştir (dosyadaki **tek** değişiklik budur):

```js
// Adapted for ESM -- the ONLY change from the design copy; component bodies are verbatim.
export { Hand, Note, Mono, HL, Btn, Seq, Grip, Segment, ImgPH, Status, Pill, Icon, Arrow };
```

Not: `import React` satırı gerekmez — Vite'ın React eklentisi otomatik JSX runtime kullanır. Şimdilik kullanılmayan primitifler (`ImgPH`, `Status`, `Pill`, `Seq`, `Grip`, `Segment`, `Arrow`, `HL`) dosyada kalır: Bölüm 5 galeriyi onlarla kuracak ve Vite kullanılmayan ihracatları derlemeden eler.

- [ ] **Step 3: `CODE-STANDARD.md`'deki vendor kuralını genişlet**

`## Frontend (frontend/src/)` bölümündeki vendor maddesini şununla değiştir:

```markdown
- **vendor/** is copied from the claude.ai/design project and never hand-edited. One exception,
  mechanical and reviewable: a file may be adapted **at its export boundary only** — the design
  project writes to globals (`Object.assign(window, {…})`), which no ES module can import, so that
  last block becomes `export {…}`. Component bodies, styles and comments stay verbatim, and
  re-pulling a file is still a one-line change. Anything the design copy gets wrong for our app
  (e.g. `.wf-scrim` being `position: absolute` because artboards are framed) is fixed in
  `shared/app.css`, never in `vendor/`.
```

- [ ] **Step 4: Dosyanın derlendiğini doğrula**

Run: `cd queen-editor/frontend && npm run build`
Expected: hata yok (kit henüz kimse tarafından import edilmediği için çıktı Bölüm 2'nin aynısı olur; amaç sözdiziminin geçtiğini görmek).

---

### Task 7: `shared/api.js` · `shared/date.js` · `shared/app.css`

**Files:**
- Modify: `queen-editor/frontend/src/shared/api.js`
- Create: `queen-editor/frontend/src/shared/date.js`
- Create: `queen-editor/frontend/src/shared/app.css`
- Modify: `queen-editor/frontend/src/main.jsx`

**Interfaces:**
- Consumes: `GET /api/projects`, `POST /api/projects` (Task 5)
- Produces: `listProjects() -> Promise<[{name, modifiedAt}]>` · `createProject(name) -> Promise<{name, modifiedAt}>` (hata durumunda `Error(sunucu mesajı)` fırlatır) · `formatModified(epochSeconds) -> "22 Tem 2026 · 14:32"`.

- [ ] **Step 1: `shared/api.js`'yi yeniden yaz**

```js
// Single fetch wrapper -- same-origin "/api", so no base URL and no CORS.
// On failure it throws the server's own message: the rules (and their Turkish wording) live in the
// backend, and the UI prints whatever comes back.
async function request(path, options) {
  const resp = await fetch(path, options);
  let body = null;
  try {
    body = await resp.json();
  } catch {
    body = null; // empty or non-JSON body (e.g. a tunnel error page)
  }
  if (!resp.ok) throw new Error(body?.error || `${resp.status} ${resp.statusText}`);
  return body;
}

export async function listProjects() {
  const body = await request("/api/projects");
  return body.projects;
}

export async function createProject(name) {
  return request("/api/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
}
```

(`getHealth` kaldırılır — UI'da bağlantı göstergesi yok. **`/api/health` ucu backend'de kalır**: `app.ipynb`'nin serve hücresi Flask'ın ayağa kalkmasını onunla bekliyor.)

- [ ] **Step 2: `shared/date.js` yaz**

```js
// "22 Tem 2026 · 14:32" -- month names come from the browser, so no hand-kept Turkish table.
const DAY = new Intl.DateTimeFormat("tr-TR", { day: "numeric", month: "short", year: "numeric" });
const TIME = new Intl.DateTimeFormat("tr-TR", { hour: "2-digit", minute: "2-digit" });

export function formatModified(epochSeconds) {
  const date = new Date(epochSeconds * 1000);
  return `${DAY.format(date)} · ${TIME.format(date)}`;
}
```

- [ ] **Step 3: `shared/app.css` yaz**

```css
/* The app's own styles. vendor/styles.css is never edited -- corrections land here. */

/* The design copy scrims an artboard, which is a positioned frame; our modal must cover the
   whole viewport. */
.wf-scrim {
  position: fixed;
}
```

- [ ] **Step 4: `main.jsx`'e app.css import'unu ekle**

`import "./vendor/styles.css";` satırının **altına** (sıra önemli: uygulamanın düzeltmesi vendor'ı geçersiz kılar):

```jsx
import "./shared/app.css";
```

- [ ] **Step 5: Derlemenin geçtiğini doğrula**

Run: `cd queen-editor/frontend && npm run build`
Expected: hata yok. (`App.jsx` hâlâ `getHealth`'i import ediyorsa build **kırılır** — bu beklenen; Task 8 `App.jsx`'i değiştiriyor. Kırılırsa Task 8'e geç, sonra buraya dönüp derlemeyi tekrar çalıştır.)

---

### Task 8: Projeler ekranı (frontend feature) + derleme

**Files:**
- Create: `queen-editor/frontend/src/features/projects/useProjects.js`
- Create: `queen-editor/frontend/src/features/projects/ProjectCard.jsx`
- Create: `queen-editor/frontend/src/features/projects/NewProjectModal.jsx`
- Create: `queen-editor/frontend/src/features/projects/ProjectsScreen.jsx`
- Modify: `queen-editor/frontend/src/App.jsx`
- Regenerate + commit: `queen-editor/frontend/dist/`

**Interfaces:**
- Consumes: `listProjects` / `createProject` (Task 7) · `formatModified` (Task 7) · `Hand · Mono · Note · Btn · Icon` (Task 6)
- Produces: `<ProjectsScreen />` — Bölüm 4 bunun içine proje ekranı geçişini ekleyecek.

- [ ] **Step 1: `features/projects/useProjects.js` yaz**

```js
import { useCallback, useEffect, useState } from "react";

import { listProjects } from "../../shared/api.js";

// The screen's data lives here: loading | ready | error(server message). Drive is the single
// source of truth, so every change ends with a reload instead of patching local state.
export function useProjects() {
  const [state, setState] = useState({ status: "loading", projects: [], error: null });

  const reload = useCallback(() => {
    setState({ status: "loading", projects: [], error: null });
    return listProjects()
      .then((projects) => setState({ status: "ready", projects, error: null }))
      .catch((err) => setState({ status: "error", projects: [], error: err.message }));
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  return { ...state, reload };
}
```

- [ ] **Step 2: `features/projects/ProjectCard.jsx` yaz**

```jsx
import { formatModified } from "../../shared/date.js";
import { Hand, Mono } from "../../vendor/kit.jsx";

// Deliberately NOT clickable: the project screen lands in Part 4, so nothing here promises a
// click (no pointer cursor, no hover lift). Part 4 adds one onClick.
export default function ProjectCard({ name, modifiedAt }) {
  return (
    <div
      className="wf-card"
      style={{
        aspectRatio: "4/3",
        padding: 14,
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        boxSizing: "border-box",
      }}
    >
      <Hand size={16} style={{ alignSelf: "flex-start" }}>{name}</Hand>
      <Mono size={11} style={{ color: "var(--ink-3)", alignSelf: "flex-end" }}>
        {formatModified(modifiedAt)}
      </Mono>
    </div>
  );
}
```

- [ ] **Step 3: `features/projects/NewProjectModal.jsx` yaz**

```jsx
import { useEffect, useState } from "react";

import { Btn, Hand, Mono, Note } from "../../vendor/kit.jsx";

// The server owns the name rules; this modal only forwards the message it gets back, so no rule
// is duplicated here. "Oluştur" is disabled while the box is empty or a request is in flight
// (Drive can take a moment over FUSE -- no double create).
export default function NewProjectModal({ onCancel, onCreate }) {
  const [name, setName] = useState("");
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "Escape") onCancel();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel]);

  function submit() {
    setBusy(true);
    setError(null);
    onCreate(name).catch((err) => {
      setError(err.message);
      setBusy(false);
    });
  }

  return (
    <div className="wf-scrim" onClick={onCancel}>
      <div
        className="wf-card wf-card--shadow"
        onClick={(e) => e.stopPropagation()}
        style={{ width: 380, padding: 20, display: "flex", flexDirection: "column", gap: 12 }}
      >
        <Hand size={17}>Yeni proje</Hand>
        <Mono
          size={11}
          style={{ color: "var(--ink-2)", letterSpacing: ".08em", textTransform: "uppercase" }}
        >
          Proje adı
        </Mono>
        <input
          className="wf-input"
          autoFocus
          value={name}
          onChange={(e) => {
            setName(e.target.value);
            setError(null);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && name && !busy) submit();
          }}
          style={error ? { borderColor: "var(--danger)" } : undefined}
        />
        {error && <Note size={12} style={{ color: "var(--danger)" }}>{error}</Note>}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 4 }}>
          <Btn ghost onClick={onCancel} disabled={busy}>Vazgeç</Btn>
          <Btn hl onClick={submit} disabled={!name || busy}>
            {busy ? "Oluşturuluyor…" : "Oluştur"}
          </Btn>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: `features/projects/ProjectsScreen.jsx` yaz**

```jsx
import { useState } from "react";

import { createProject } from "../../shared/api.js";
import { Btn, Hand, Icon, Mono, Note } from "../../vendor/kit.jsx";
import NewProjectModal from "./NewProjectModal.jsx";
import ProjectCard from "./ProjectCard.jsx";
import { useProjects } from "./useProjects.js";

const CENTERED = {
  minHeight: "60vh",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  gap: 10,
};

export default function ProjectsScreen() {
  const { status, projects, error, reload } = useProjects();
  const [modalOpen, setModalOpen] = useState(false);

  // Drive is the single source of truth: after a create we re-read the list instead of guessing
  // the new card, so the date on screen is the folder's own.
  async function handleCreate(name) {
    await createProject(name);
    setModalOpen(false);
    await reload();
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr auto 1fr",
          alignItems: "center",
          padding: "14px 32px",
          background: "var(--bg-2)",
          borderBottom: "1px solid var(--border)",
        }}
      >
        <Hand size={20}><span className="wf-hl">Queen Editor</span></Hand>
        <Hand size={20}>Projeler</Hand>
        <Btn hl style={{ justifySelf: "end" }} onClick={() => setModalOpen(true)}>
          <Icon.Plus /> Yeni proje
        </Btn>
      </div>

      <div style={{ flex: 1, padding: "24px 32px" }}>
        {status === "error" ? (
          <div style={CENTERED}>
            <span style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--danger)" }}>
              <Icon.Warn />
              <Note size={14} style={{ color: "var(--danger)", fontWeight: 500 }}>
                Projeler yüklenemedi
              </Note>
            </span>
            {/* The server's raw message -- we never guess the cause. */}
            <Mono
              size={11}
              style={{
                color: "var(--ink-3)",
                background: "var(--bg)",
                border: "1px solid var(--border)",
                borderRadius: 3,
                padding: "6px 8px",
                maxWidth: 640,
                wordBreak: "break-word",
              }}
            >
              {error}
            </Mono>
            <Btn onClick={reload}><Icon.Regen /> Tekrar dene</Btn>
          </div>
        ) : status === "loading" ? null : projects.length === 0 ? (
          <div style={CENTERED}>
            <Mono size={12} style={{ color: "var(--ink-3)" }}>henüz proje yok</Mono>
            <Note size={13} style={{ color: "var(--ink-3)" }}>
              İlk projeni oluştur, fotoğrafların burada toplansın
            </Note>
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
            {projects.map((p) => (
              <ProjectCard key={p.name} name={p.name} modifiedAt={p.modifiedAt} />
            ))}
          </div>
        )}
      </div>

      {modalOpen && (
        <NewProjectModal onCancel={() => setModalOpen(false)} onCreate={handleCreate} />
      )}
    </div>
  );
}
```

- [ ] **Step 5: `App.jsx`'i tek ekrana indir**

Dosyanın tamamı (Bölüm 2'nin bağlantı göstergesi kalkar — bağlantının kanıtı artık listenin kendisi):

```jsx
import ProjectsScreen from "./features/projects/ProjectsScreen.jsx";

// Part 3 has one screen; routing to the project screen lands in Part 4.
export default function App() {
  return <ProjectsScreen />;
}
```

- [ ] **Step 6: Derle**

Run: `cd queen-editor/frontend && npm run build`
Expected: `dist/index.html` + `dist/assets/*` yeniden üretilir, hata/uyarı yok. (`dist/` commit'e girecek — CLAUDE.md'deki "build before commit" kuralı.)

- [ ] **Step 7: Backend testleri hâlâ geçiyor mu**

Run: `cd queen-editor && pytest -q`
Expected: PASS (42 test) — frontend değişikliği backend'i etkilemez, bu bir kontrol.

---

### Task 9: Notebook — Drive mount + `QE_DRIVE_ROOT`

**Files:**
- Modify: `queen-editor/app.ipynb` (NotebookEdit ile: markdown hücresi, CONFIG hücresi, yeni mount hücresi, serve hücresi)
- Modify: `queen-editor/README.md`

**Interfaces:**
- Consumes: `config.DRIVE_ROOT`'un `QE_DRIVE_ROOT` ile geçersiz kılınması (Task 1) · `python -m backend.main` (Task 5)
- Produces: Colab'da mount edilmiş Drive + `MyDrive/queenEditor` kökü + doğru kökle çalışan Flask.

- [ ] **Step 1: Başlık markdown hücresini güncelle** (`cell-0`)

```markdown
# Queen Editor — Proje (Bölüm 3)

Drive'ı bağlar → repoyu klonlar → **Flask** derlenmiş arayüzü ve `/api/projects` ucunu servis eder
→ **cloudflared** linki basar. Açılan sayfada **Projeler** ekranı: **+ Yeni proje** ile
`MyDrive/queenEditor/<ad>/` klasörü oluşur, kartlar en son değişen en üstte listelenir.
ComfyUI ve foto üretimi bu bölümde yok.

Arayüz repoya **derlenmiş** gelir (ComfyUI deseni); Colab'da npm/build çalışmaz.

## Kullanım
1. Bu `app.ipynb`'yi Colab'a yükle (**File → Upload notebook**).
2. Colab'ın **🔑 Secrets** panelinde `GITHUB_TOKEN` ekli olmalı (fine-grained, yalnız bu repo,
   `Contents: read` — kurulum için `README.md`).
3. **Runtime → Run all** → Drive erişim penceresi çıkar, **izin ver** → en alttaki linke gir.
```

- [ ] **Step 2: CONFIG hücresine `DRIVE_FOLDER` ekle** (`cell-1`)

`APP_PORT  = 8000` satırının altına:

```python
DRIVE_FOLDER = "queenEditor"               # MyDrive altındaki proje kökü (Drive klasörü)
```

- [ ] **Step 3: CONFIG'in son çıktı satırını genişlet** (`cell-1`)

```python
print(f"✓ Dal: {BRANCH}  |  Repo: {REPO}  |  Hedef: {CLONE_DIR}")
print(f"✓ Proje kökü: MyDrive/{DRIVE_FOLDER}")
```

- [ ] **Step 4: Yeni mount hücresini CONFIG ile klon hücresi arasına ekle**

```python
# === Mount Google Drive ===
# Projects ARE Drive folders, so the mount must succeed before the server starts: writing under
# /content/drive without a mount silently lands on Colab's local disk, and those folders die with
# the runtime. The first run opens a Google permission window -- grant it.
import os
from google.colab import drive

drive.mount("/content/drive")

DRIVE_ROOT = f"/content/drive/MyDrive/{DRIVE_FOLDER}"
os.makedirs(DRIVE_ROOT, exist_ok=True)   # first run creates it; later runs reuse it
assert os.path.isdir(DRIVE_ROOT), f"❌ Proje kökü oluşmadı: {DRIVE_ROOT}"
print(f"✓ Drive bağlı — proje kökü: {DRIVE_ROOT}")
```

- [ ] **Step 5: Serve hücresinde Flask'a `QE_DRIVE_ROOT`'u geçir**

`logf = open(FLASK_LOG, "w")` satırından sonraki `subprocess.Popen([...])` çağrısını şununla değiştir:

```python
logf = open(FLASK_LOG, "w")
# The backend reads its Drive root from the environment (backend/config.py) -- the path is decided
# here, in the mount cell, not hardcoded in the app.
flask_env = {**os.environ, "QE_DRIVE_ROOT": DRIVE_ROOT}
subprocess.Popen(["python", "-m", "backend.main"], cwd=APP_DIR, env=flask_env,
                 stdout=logf, stderr=subprocess.STDOUT)
```

- [ ] **Step 6: Serve hücresinin link mesajını güncelle**

```python
print(f"\n🔗 Queen Editor: {link}\n")
print("⬆️  Linke gir → Projeler ekranı açılır, '+ Yeni proje' ile proje oluştur.\n")
```

- [ ] **Step 7: `README.md`'yi güncelle** (İngilizce — geliştirici metni; token kurulum bölümü 1-2 değişmez)

`So far:` paragrafını (satır 8-9) şununla değiştir:

```markdown
So far: **Part 1** proved the private repo clones on Colab; **Part 2** serves the pre-built frontend
with Flask and opens a tunnel; **Part 3** adds the projects screen — create a project, get a folder
under `MyDrive/queenEditor/`. No ComfyUI, no photo generation yet.
```

`## Run on Colab` altındaki ilk paragrafı (satır 13-15) şununla değiştir:

```markdown
`app.ipynb` mounts Google Drive, clones this repo (the built `frontend/dist/` ships with it), starts
the Flask server, and prints a cloudflared link. Colab never builds — it only serves.
```

`### 3. Run` bölümünü şununla değiştir:

```markdown
**Runtime → Run all.** The notebook mounts Drive (**grant access in the popup** — projects are Drive
folders, so this must succeed), clones the repo, starts Flask (which serves the pre-built
`frontend/dist/`), and prints a cloudflared link. Open it — the projects screen appears; **+ Yeni
proje** creates a folder under `MyDrive/queenEditor/`. The token is read from Secrets and never
appears in any output or in the notebook source.
```

(Son "Developer note" paragrafı olduğu gibi kalır.)

- [ ] **Step 8: Notebook'un geçerli JSON olduğunu ve hücre sırasını doğrula**

Read ile `queen-editor/app.ipynb` açılır; sıra **markdown → CONFIG → mount → klon → serve** olmalı ve her hücre düzgün ayrışmalı. (Gerçek testi Colab'da — Task 10.)

---

### Task 10: Colab doğrulaması + commit (kullanıcı kapısı)

**Files:** (yok — doğrulama + commit)

**Interfaces:**
- Consumes: Task 1-9
- Produces: Bölüm 3'ün kapanışı.

- [ ] **Step 1: Yerel tam test turu**

Run: `cd queen-editor && pytest -q`
Expected: PASS (42 test).
Run: `cd queen-editor/frontend && npm run build`
Expected: hata yok, `dist/` güncel (kaynak değiştiyse yeniden derlenmiş olmalı — aksi hâlde Colab eski arayüzü servis eder).

- [ ] **Step 2: Kullanıcı Colab doğrulaması**

Kullanıcı `app.ipynb`'yi Colab'a yükler, **Run all**. Beklenen (spec'in doğrulama listesi):

1. Drive izni verilir → `✓ Drive bağlı — proje kökü: /content/drive/MyDrive/queenEditor`.
2. Klon + Flask + cloudflared linki basılır.
3. Linke gir → **Projeler** ekranı, `henüz proje yok`.
4. **+ Yeni proje** → `kapak çekimi` → **Oluştur** → modal kapanır, kart belirir (sol üst ad, sağ alt tarih); Drive'da `MyDrive/queenEditor/kapak çekimi/` görünür.
5. Aynı adı tekrar dene → kutu kırmızı, altında `Bu ad zaten kullanılıyor. Başka bir ad dene.`
6. `foto/deneme` → yasak karakter mesajı aynı yerde.
7. İkinci proje → yeni kart **en üstte**.
8. Sayfayı yenile → projeler duruyor.
9. Karta tıkla → hiçbir şey olmaz (beklenen).
10. (Negatif) Flask'ı durdur, sayfayı yenile → kırmızı **Projeler yüklenemedi** + gerçek hata metni + **Tekrar dene**.

- [ ] **Step 3: Kullanıcı onayıyla commit**

Kullanıcı "çalışıyor, commit" dedikten sonra, **açık pathspec** ile iki commit + push (aynı dalda başka bir oturum çalışıyor olabilir — `git add` + çıplak `git commit` yasak):

```bash
# docs
git commit -m "docs(queen-editor): Bölüm 3 — proje spec + plan" -- \
  docs/superpowers/specs/2026-07-25-queen-editor-b3-proje-design.md \
  docs/superpowers/plans/2026-07-25-queen-editor-b3-proje.md
# feat (backend + frontend kaynağı + derlenmiş dist + notebook/README/standart)
git add -- queen-editor/backend queen-editor/frontend/src queen-editor/frontend/dist \
  queen-editor/app.ipynb queen-editor/README.md queen-editor/CODE-STANDARD.md
git commit -m "feat(queen-editor): Bölüm 3 — proje oluştur + listele (Drive)" -- \
  queen-editor/backend queen-editor/frontend/src queen-editor/frontend/dist \
  queen-editor/app.ipynb queen-editor/README.md queen-editor/CODE-STANDARD.md
git push origin feat/queen-editor-v1
```

(Yeni docs dosyaları izlenmiyorsa ilk commit'ten önce `git add -- <iki yol>`. `node_modules/` `.gitignore`'da.)

---

## Doğrulama özeti

| Ne | Nasıl |
|---|---|
| Drive servisi | `pytest backend/tests/test_drive_storage.py` → 5 test |
| Ad kuralları | `pytest backend/tests/test_name_rules.py` → 17 test (6 geçerli + 11 geçersiz) |
| Use case'ler (sahte port) | `pytest backend/tests/test_project_usecases.py` → 5 test |
| Store (tmp_path) | `pytest backend/tests/test_project_store.py` → 3 test |
| Uçlar | `pytest backend/tests/test_projects_routes.py` → 8 test (200 · 201 · sıra · 400 · 409 · boş ad · 500 gerçek metin · health) |
| Bölüm 2 bozulmadı | `pytest` toplam 42 test |
| Arayüz derleniyor | `cd frontend && npm run build` → `dist/` güncel |
| Uçtan uca | Colab Run all → proje oluştur → Drive'da klasör + ekranda kart |
| Bölüm 3 kapanır | Kullanıcı doğrular → docs + feat commit'leri + push |
