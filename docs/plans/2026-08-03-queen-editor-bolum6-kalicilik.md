# Bölüm 6 — Kalıcılık + iz · Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Panelin içeriği ve her fotoğrafın hangi prompt'tan üretildiği Drive'a yazılsın; sayfa yenilenince kutular dolu gelsin, galeri diski değil kaydı okusun.

**Architecture:** Proje klasörüne üç dosya girer — `settings.json` (panelin içeriği, sahibi `projects`), `plan.json` (üretimin kuyruğu) ve `photos.jsonl` (var olan fotoğraflar + metadata), son ikisinin sahibi `photo_generation`. Plan ölü bir kayıt değil, işçinin sırayla okuduğu kuyruktur; seed plan yazılırken belirlenir. Kayıt satırı her fotoğraf diske düştükten hemen sonra eklenir ve kendi kendine yeter.

**Tech Stack:** Python 3 · Flask · pytest · React 18 · Vite

**Spec:** [2026-08-03-queen-editor-bolum6-kalicilik-design.md](../specs/2026-08-03-queen-editor-bolum6-kalicilik-design.md)

## Global Constraints

- **Dil:** kod yorumları, docstring'ler ve commit mesajları **İngilizce**; kullanıcıya görünen arayüz metinleri ve hata mesajları **Türkçe**.
- **Katman kuralı:** `presentation → domain ← data → services`. Yasaklar: `feature ↛ feature`, `service ↛ feature`, `service ↛ service`. Somut sınıflar yalnız `backend/main.py`'da bağlanır.
- **domain saflığı:** `domain/` altındaki hiçbir dosya `flask`, `requests`, dosya yolu veya dosya şeması bilmez. Zaman ve rastgelelik dışarıdan enjekte edilir.
- **Şema sahipliği:** bir dosya şemasını bilen tek yer o feature'ın `data/` katmanıdır. `<numara>_<harf>.png` şemasını bilen tek yer `photo_store.py`'dır.
- **Testler:** `queen-editor/` dizininden `pytest`. Domain ve use case testleri sahte portlarla — ComfyUI yok, Drive yok. Route testleri gerçek depoları geçici klasöre bağlar (dosyalardaki mevcut desen).
- **Tek commit:** görevler arasında commit atılmaz. Bir görev, kendi testleri geçtiğinde tamamlanmış sayılır; bütün bölüm bittikten sonra (Task 6, Step 10) **tek** commit atılır.
- **Frontend derlemesi:** `frontend/src/` altında herhangi bir değişiklikten sonra `queen-editor/frontend/` içinde `npm run build` çalıştırılır ve üretilen `dist/` o commit'e dahil edilir; yoksa Colab eski arayüzü servis eder.
- **Hata metni:** hiçbir yerde sebep uydurulmaz — sunucunun/işletim sisteminin kendi mesajı olduğu gibi taşınır.
- **Colab testi:** her doğrulama öncesi commit **ve push** gerekir; notebook repoyu klonluyor.

---

### Task 1: Drive metin ilkelleri

`DriveStorage` bugün yalnız bayt yazabiliyor ve dosya adı listeleyebiliyor. Üç dosyanın da ihtiyacı olan metin okuma/yazma ve satır ekleme ilkelleri servise girer. Servis hiçbir şema bilmez: JSON'u çağıran çözer.

**Files:**
- Modify: `queen-editor/backend/services/drive/storage.py`
- Test: `queen-editor/backend/tests/test_drive_storage.py`

**Interfaces:**
- Consumes: mevcut `DriveStorage(root)`
- Produces:
  - `DriveStorage.read_text(subdir, name) -> str | None`
  - `DriveStorage.write_text(subdir, name, text) -> None`
  - `DriveStorage.append_line(subdir, name, line) -> None`
  - `DriveStorage.read_lines(subdir, name) -> list[str]`

- [ ] **Step 1: Write the failing tests**

`queen-editor/backend/tests/test_drive_storage.py` dosyasının **sonuna** ekle:

```python
def test_read_text_returns_none_when_the_file_is_not_there(tmp_path):
    assert DriveStorage(str(tmp_path)).read_text("düğün", "settings.json") is None


def test_write_text_creates_the_folder_and_round_trips(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.write_text("düğün", "settings.json", '{"negatif": "bulanık"}')
    assert storage.read_text("düğün", "settings.json") == '{"negatif": "bulanık"}'


def test_write_text_replaces_what_was_there(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.write_text("düğün", "settings.json", "eski")
    storage.write_text("düğün", "settings.json", "yeni")
    assert storage.read_text("düğün", "settings.json") == "yeni"


def test_append_line_creates_the_file_and_keeps_earlier_lines(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.append_line("düğün", "photos.jsonl", '{"file": "0_a.png"}')
    storage.append_line("düğün", "photos.jsonl", '{"file": "0_b.png"}')
    assert storage.read_lines("düğün", "photos.jsonl") == [
        '{"file": "0_a.png"}', '{"file": "0_b.png"}']


def test_read_lines_is_empty_when_the_file_is_not_there(tmp_path):
    assert DriveStorage(str(tmp_path)).read_lines("düğün", "photos.jsonl") == []


def test_read_lines_skips_blank_lines(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.write_text("düğün", "photos.jsonl", "ilk\n\n   \nikinci\n")
    assert storage.read_lines("düğün", "photos.jsonl") == ["ilk", "ikinci"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest backend/tests/test_drive_storage.py -v`
Expected: FAIL — `AttributeError: 'DriveStorage' object has no attribute 'read_text'`

- [ ] **Step 3: Implement the primitives**

`queen-editor/backend/services/drive/storage.py` içinde `write_bytes`'ın altına ekle:

```python
    def read_text(self, subdir, name):
        """Contents of root/subdir/name, or None when it is not there.

        Missing is not an error: a project that was never saved and one whose file was removed are
        the same answer to the caller -- there is nothing to read.
        """
        path = os.path.join(self.root, subdir, name)
        if not os.path.isfile(path):
            return None
        with open(path, encoding="utf-8") as f:
            return f.read()

    def write_text(self, subdir, name, text):
        """Write root/subdir/name, creating the folder if needed. Replaces the whole file."""
        path = os.path.join(self.root, subdir)
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, name), "w", encoding="utf-8") as f:
            f.write(text)

    def append_line(self, subdir, name, line):
        """Add one line to the end of root/subdir/name, creating it if needed.

        Nothing already written is rewritten, so a session that dies mid-write can lose at most the
        line it was adding.
        """
        path = os.path.join(self.root, subdir)
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, name), "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def read_lines(self, subdir, name):
        """Non-blank lines of root/subdir/name; [] when it is not there."""
        text = self.read_text(subdir, name)
        if text is None:
            return []
        return [line for line in text.splitlines() if line.strip()]
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest backend/tests/test_drive_storage.py -v`
Expected: PASS (yeni 6 test dahil hepsi)

---

### Task 2: Ayarlar — depo, use case'ler, uçlar

`settings.json` şemasını bilen tek yer `projects/data/settings_store.py` olur. Dosya doğrulanmaz: tek işi kutuları geri doldurmaktır, sunucunun reddettiği bir liste de kullanıcının yazdığı şeydir.

**Files:**
- Create: `queen-editor/backend/features/projects/data/settings_store.py`
- Create: `queen-editor/backend/features/projects/domain/usecases/get_settings.py`
- Create: `queen-editor/backend/features/projects/domain/usecases/save_settings.py`
- Modify: `queen-editor/backend/features/projects/domain/ports.py`
- Modify: `queen-editor/backend/features/projects/presentation/routes.py`
- Modify: `queen-editor/backend/main.py`
- Create: `queen-editor/backend/tests/test_settings_store.py`
- Test: `queen-editor/backend/tests/test_project_usecases.py`, `queen-editor/backend/tests/test_projects_routes.py`

**Interfaces:**
- Consumes: `DriveStorage.read_text`, `DriveStorage.write_text`, `DriveStorage.dir_exists` (Task 1 + mevcut)
- Produces:
  - `DriveSettingsStore(storage)` — `project_exists(project) -> bool`, `read(project) -> dict`, `write(project, settings) -> None`
  - `get_settings(store, project) -> dict` (`{"prompts": str, "negative": str, "variants": int | None}`), `ProjectMissing` fırlatır
  - `save_settings(store, project, prompts, negative, variants) -> None`
  - `GET /api/projects/<project>/settings` → 200 ayarlar · 404 proje yok
  - `PUT /api/projects/<project>/settings` → 204 · 404 proje yok
  - `make_projects_blueprint(list_projects, create_project, get_settings, save_settings)`

- [ ] **Step 1: Write the failing store tests**

`queen-editor/backend/tests/test_settings_store.py` oluştur:

```python
from backend.features.projects.data.settings_store import DriveSettingsStore
from backend.services.drive.storage import DriveStorage

EMPTY = {"prompts": "", "negative": "", "variants": None}


def store_at(path):
    return DriveSettingsStore(DriveStorage(str(path)))


def test_reading_a_project_that_never_saved_gives_empty_settings(tmp_path):
    (tmp_path / "düğün").mkdir()
    assert store_at(tmp_path).read("düğün") == EMPTY


def test_write_then_read_round_trips(tmp_path):
    (tmp_path / "düğün").mkdir()
    store = store_at(tmp_path)
    settings = {"prompts": '["kraliçe tahtta"]', "negative": "bulanık", "variants": 4}
    store.write("düğün", settings)
    assert store.read("düğün") == settings


def test_the_prompt_text_is_stored_exactly_as_written(tmp_path):
    (tmp_path / "düğün").mkdir()
    store = store_at(tmp_path)
    typed = '[\n  "kraliçe tahtta",\n]'          # trailing comma and line breaks survive
    store.write("düğün", {"prompts": typed, "negative": "", "variants": 4})
    assert store.read("düğün")["prompts"] == typed


def test_an_unreadable_file_reads_as_empty_settings(tmp_path):
    (tmp_path / "düğün").mkdir()
    (tmp_path / "düğün" / "settings.json").write_text("{ yarım", encoding="utf-8")
    assert store_at(tmp_path).read("düğün") == EMPTY


def test_fields_of_the_wrong_type_read_as_empty(tmp_path):
    (tmp_path / "düğün").mkdir()
    (tmp_path / "düğün" / "settings.json").write_text(
        '{"prompts": 5, "negative": null, "variants": true}', encoding="utf-8")
    assert store_at(tmp_path).read("düğün") == EMPTY


def test_project_exists_follows_the_folder(tmp_path):
    (tmp_path / "düğün").mkdir()
    store = store_at(tmp_path)
    assert store.project_exists("düğün") is True
    assert store.project_exists("yok") is False
```

- [ ] **Step 2: Run the store tests to verify they fail**

Run: `pytest backend/tests/test_settings_store.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'backend.features.projects.data.settings_store'`

- [ ] **Step 3: Implement the settings store**

`queen-editor/backend/features/projects/data/settings_store.py` oluştur:

```python
"""SettingsStore over DriveStorage -- the only place that knows the settings file's name and shape.

The prompt text is kept exactly as it was typed. A parsed list would come back reformatted, and the
panel has to reopen looking the way the user left it.

Nothing here validates: this file's only job is to refill the boxes, so anything unreadable reads as
empty settings rather than making the project impossible to open.
"""
import json

FILE = "settings.json"


def _empty():
    return {"prompts": "", "negative": "", "variants": None}


def _text(value):
    return value if isinstance(value, str) else ""


def _count(value):
    # bool is an int in Python, and True would silently become "1 variant".
    return value if isinstance(value, int) and not isinstance(value, bool) else None


class DriveSettingsStore:
    def __init__(self, storage):
        self._storage = storage

    def project_exists(self, project):
        return self._storage.dir_exists(project)

    def read(self, project):
        raw = self._storage.read_text(project, FILE)
        if raw is None:
            return _empty()
        try:
            data = json.loads(raw)
        except ValueError:
            return _empty()
        if not isinstance(data, dict):
            return _empty()
        return {"prompts": _text(data.get("prompts")),
                "negative": _text(data.get("negative")),
                "variants": _count(data.get("variants"))}

    def write(self, project, settings):
        self._storage.write_text(
            project, FILE, json.dumps(settings, ensure_ascii=False, indent=2))
```

- [ ] **Step 4: Run the store tests to verify they pass**

Run: `pytest backend/tests/test_settings_store.py -v`
Expected: PASS (6 test)

- [ ] **Step 5: Write the failing use case tests**

`queen-editor/backend/tests/test_project_usecases.py` dosyasının **sonuna** ekle (dosyanın başında `import pytest` yoksa onu da ekle):

```python
from backend.features.projects.domain.usecases.get_settings import ProjectMissing, get_settings
from backend.features.projects.domain.usecases.save_settings import save_settings


class FakeSettingsStore:
    def __init__(self, projects=("düğün",)):
        self.projects = list(projects)
        self.saved = {}

    def project_exists(self, project):
        return project in self.projects

    def read(self, project):
        return self.saved.get(project, {"prompts": "", "negative": "", "variants": None})

    def write(self, project, settings):
        self.saved[project] = settings


def test_get_settings_passes_the_store_through():
    store = FakeSettingsStore()
    store.saved["düğün"] = {"prompts": '["a"]', "negative": "neg", "variants": 4}
    assert get_settings(store, "düğün") == {"prompts": '["a"]', "negative": "neg", "variants": 4}


def test_get_settings_rejects_a_missing_project():
    with pytest.raises(ProjectMissing) as exc:
        get_settings(FakeSettingsStore(), "yok")
    assert str(exc.value) == "Proje yok: yok"


def test_save_settings_stores_what_it_was_given():
    store = FakeSettingsStore()
    save_settings(store, "düğün", '["a"]', "neg", 4)
    assert store.saved["düğün"] == {"prompts": '["a"]', "negative": "neg", "variants": 4}


def test_save_settings_keeps_text_the_server_would_reject():
    # A list that fails to parse is still what the user typed; losing it would punish the mistake
    # twice.
    store = FakeSettingsStore()
    save_settings(store, "düğün", "[ yarım", "", None)
    assert store.saved["düğün"]["prompts"] == "[ yarım"


def test_save_settings_rejects_a_missing_project():
    store = FakeSettingsStore()
    with pytest.raises(ProjectMissing):
        save_settings(store, "yok", '["a"]', "", 4)
    assert store.saved == {}
```

- [ ] **Step 6: Run the use case tests to verify they fail**

Run: `pytest backend/tests/test_project_usecases.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'backend.features.projects.domain.usecases.get_settings'`

- [ ] **Step 7: Implement the use cases and the port**

`queen-editor/backend/features/projects/domain/usecases/get_settings.py` oluştur:

```python
"""What the panel shows when the project opens.

The message is user-facing Turkish; presentation forwards it untouched.
"""


class ProjectMissing(Exception):
    """No such project folder (message is the user-facing text)."""


def get_settings(store, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    return store.read(project)
```

`queen-editor/backend/features/projects/domain/usecases/save_settings.py` oluştur:

```python
"""Store the panel's content as it was submitted.

Deliberately unvalidated: the file exists to refill the boxes, and text the generator rejected is
still what the user typed. The project folder must already exist -- writing would otherwise create
one, and every folder under the root counts as a project.
"""
from backend.features.projects.domain.usecases.get_settings import ProjectMissing


def save_settings(store, project, prompts, negative, variants):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    store.write(project, {"prompts": prompts, "negative": negative, "variants": variants})
```

`queen-editor/backend/features/projects/domain/ports.py` dosyasının sonuna ekle:

```python
class SettingsStore(Protocol):
    def project_exists(self, project: str) -> bool:
        ...

    def read(self, project: str) -> dict:
        """{"prompts": str, "negative": str, "variants": int | None} -- empty when never saved."""
        ...

    def write(self, project: str, settings: dict) -> None:
        """Replace the stored settings with this dict."""
        ...
```

- [ ] **Step 8: Run the use case tests to verify they pass**

Run: `pytest backend/tests/test_project_usecases.py -v`
Expected: PASS

- [ ] **Step 9: Extend the route test wiring and write the failing route tests**

`queen-editor/backend/tests/test_projects_routes.py`: importlara ekle

```python
from backend.features.projects.data.settings_store import DriveSettingsStore
from backend.features.projects.domain.usecases.get_settings import get_settings
from backend.features.projects.domain.usecases.save_settings import save_settings
```

`client_for` içindeki blueprint kurulumunu şununla değiştir (dosya gerçek depoları geçici klasöre bağlıyor — aynı deseni sürdür):

```python
def client_for(drive_root, dist_dir):
    """Wire the feature by hand -- the same wiring main.py does, but over a temp folder."""
    storage = DriveStorage(str(drive_root))
    store = DriveProjectStore(storage)
    settings_store = DriveSettingsStore(storage)
    blueprint = make_projects_blueprint(
        list_projects=partial(list_projects, store),
        create_project=partial(create_project, store),
        get_settings=partial(get_settings, settings_store),
        save_settings=partial(save_settings, settings_store),
    )
    return create_app(dist_dir=str(dist_dir), blueprints=[blueprint]).test_client()
```

Dosyanın sonuna ekle:

```python
def test_settings_start_empty_for_a_new_project(tmp_path):
    client, _ = make_client(tmp_path)
    client.post("/api/projects", json={"name": "düğün"})
    assert client.get("/api/projects/düğün/settings").get_json() == {
        "prompts": "", "negative": "", "variants": None}


def test_settings_survive_a_put_and_come_back(tmp_path):
    client, _ = make_client(tmp_path)
    client.post("/api/projects", json={"name": "düğün"})
    resp = client.put("/api/projects/düğün/settings",
                      json={"prompts": '["a"]', "negative": "neg", "variants": 4})
    assert resp.status_code == 204
    assert client.get("/api/projects/düğün/settings").get_json() == {
        "prompts": '["a"]', "negative": "neg", "variants": 4}


def test_settings_of_an_unknown_project_return_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/projects/yok/settings").status_code == 404
    assert client.put("/api/projects/yok/settings", json={"prompts": "x"}).status_code == 404


def test_putting_settings_never_creates_a_project(tmp_path):
    # Every folder under the root is a project: a settings write to an unknown name must not
    # conjure one.
    client, drive = make_client(tmp_path)
    client.put("/api/projects/yok/settings", json={"prompts": "x"})
    assert not (drive / "yok").exists()
    assert client.get("/api/projects").get_json() == {"projects": []}


def test_settings_of_the_wrong_type_are_coerced(tmp_path):
    client, _ = make_client(tmp_path)
    client.post("/api/projects", json={"name": "düğün"})
    client.put("/api/projects/düğün/settings",
               json={"prompts": 5, "negative": None, "variants": "4"})
    assert client.get("/api/projects/düğün/settings").get_json() == {
        "prompts": "", "negative": "", "variants": None}
```

- [ ] **Step 10: Run the route tests to verify they fail**

Run: `pytest backend/tests/test_projects_routes.py -v`
Expected: FAIL — `TypeError: make_projects_blueprint() got an unexpected keyword argument 'get_settings'`

- [ ] **Step 11: Add the routes**

`queen-editor/backend/features/projects/presentation/routes.py`: importa ekle

```python
from backend.features.projects.domain.usecases.get_settings import ProjectMissing
```

imzayı değiştir

```python
def make_projects_blueprint(list_projects, create_project, get_settings, save_settings):
```

ve `return bp` satırından hemen önce ekle:

```python
    @bp.get("/api/projects/<project>/settings")
    def get_project_settings(project):
        try:
            return jsonify(get_settings(project))
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500

    @bp.put("/api/projects/<project>/settings")
    def put_project_settings(project):
        body = request.get_json(silent=True) or {}
        prompts, negative, variants = (body.get("prompts"), body.get("negative"),
                                       body.get("variants"))
        try:
            save_settings(
                project,
                prompts if isinstance(prompts, str) else "",
                negative if isinstance(negative, str) else "",
                # bool is an int in Python, and True would silently mean "1 variant".
                variants if isinstance(variants, int) and not isinstance(variants, bool) else None,
            )
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500
        # 204: the client already has what it sent; there is nothing to send back.
        return "", 204
```

- [ ] **Step 12: Wire the store in the composition root**

`queen-editor/backend/main.py`: importlara ekle

```python
from backend.features.projects.data.settings_store import DriveSettingsStore
from backend.features.projects.domain.usecases.get_settings import get_settings
from backend.features.projects.domain.usecases.save_settings import save_settings
```

ve `_projects_bp = make_projects_blueprint(...)` bloğunu şununla değiştir:

```python
_settings_store = DriveSettingsStore(_storage)
_projects_bp = make_projects_blueprint(
    list_projects=partial(list_projects, _project_store),
    create_project=partial(create_project, _project_store),
    get_settings=partial(get_settings, _settings_store),
    save_settings=partial(save_settings, _settings_store),
)
```

- [ ] **Step 13: Run the whole suite**

Run: `pytest`
Expected: PASS

---

### Task 3: Ayarlar paneli (frontend)

Bu görevin sonunda **görünür sonuç** var: prompt/negatif/varyant yaz, Üret'e bas, sayfayı yenile — kutular dolu gelir. Ayarlar `projects` feature'ının hook'uyla okunur, proje ekranına `App.jsx` üzerinden geçer; iki feature birbirini import etmez.

**Files:**
- Modify: `queen-editor/frontend/src/shared/api.js`
- Create: `queen-editor/frontend/src/features/projects/useProjectSettings.js`
- Modify: `queen-editor/frontend/src/App.jsx`
- Modify: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx`
- Modify: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx`

**Interfaces:**
- Consumes: `GET/PUT /api/projects/<project>/settings` (Task 2)
- Produces:
  - `getSettings(project) -> Promise<{prompts, negative, variants}>`, `saveSettings(project, settings) -> Promise`
  - `useProjectSettings(project) -> {status, settings, error, save}`
  - `ProjectScreen` props: `{project, settings, settingsError, onSaveSettings}`
  - `GeneratePanel` props: `{job, error, busyElsewhere, settings, onGenerate, onStop}`

- [ ] **Step 1: Add the two API calls**

`queen-editor/frontend/src/shared/api.js` — `createProject`'in altına ekle:

```javascript
export async function getSettings(project) {
  return request(`/api/projects/${encodeURIComponent(project)}/settings`);
}

export async function saveSettings(project, { prompts, negative, variants }) {
  return request(`/api/projects/${encodeURIComponent(project)}/settings`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompts, negative, variants }),
  });
}
```

- [ ] **Step 2: Write the settings hook**

`queen-editor/frontend/src/features/projects/useProjectSettings.js` oluştur:

```javascript
import { useCallback, useEffect, useState } from "react";

import { getSettings, saveSettings } from "../../shared/api.js";

// The panel's content belongs to the project, not to the tab: loading | ready | error(server text).
// Saving does not touch this state -- what is on screen is already what was sent.
export function useProjectSettings(project) {
  const [state, setState] = useState({ status: "loading", settings: null, error: null });

  useEffect(() => {
    let cancelled = false;
    setState({ status: "loading", settings: null, error: null });
    getSettings(project)
      .then((settings) => {
        if (!cancelled) setState({ status: "ready", settings, error: null });
      })
      .catch((err) => {
        if (!cancelled) setState({ status: "error", settings: null, error: err.message });
      });
    return () => {
      cancelled = true;
    };
  }, [project]);

  const save = useCallback((settings) => saveSettings(project, settings), [project]);

  return { ...state, save };
}
```

- [ ] **Step 3: Join the two features in the composition root**

`queen-editor/frontend/src/App.jsx` dosyasının tamamını şununla değiştir:

```javascript
import ProjectScreen from "./features/photo_generation/ProjectScreen.jsx";
import ProjectsScreen from "./features/projects/ProjectsScreen.jsx";
import { useProjectSettings } from "./features/projects/useProjectSettings.js";
import { projectFromPath, useRoute } from "./shared/router.js";

const EMPTY_SETTINGS = { prompts: "", negative: "", variants: null };

// The join lives here: settings belong to the projects feature, the gallery and the batch to
// photo_generation, and neither imports the other.
// Rendering waits for the settings so the panel's fields can start from them -- mounting empty and
// filling in afterwards would overwrite whatever the user had begun typing.
function ProjectRoute({ project }) {
  const { status, settings, error, save } = useProjectSettings(project);
  if (status === "loading") return null;
  return (
    <ProjectScreen
      project={project}
      settings={settings || EMPTY_SETTINGS}
      settingsError={error}
      onSaveSettings={save}
    />
  );
}

export default function App() {
  const project = projectFromPath(useRoute());
  return project ? <ProjectRoute project={project} /> : <ProjectsScreen />;
}
```

- [ ] **Step 4: Sequence save-then-generate in the project screen**

`queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx`: en üste `useState` importunu ekle

```javascript
import { useState } from "react";
```

bileşenin imzasını ve gövdesinin başını şununla değiştir:

```javascript
export default function ProjectScreen({ project, settings, settingsError, onSaveSettings }) {
  const { job, photos, error, generate, stop } = useGeneration(project);
  const [saveError, setSaveError] = useState(settingsError);
  // The worker is global: a batch started from another project blocks this one (the server 409s).
  const busyElsewhere = job.status === "running" && job.project !== project;
  const running = job.status === "running" && !busyElsewhere;

  // Pressing Üret persists the panel first, whether or not the batch is accepted -- text the
  // server rejects is still what the user typed. Both writes land in the same folder, so settings
  // that cannot be written mean the photos could not be either: say so and do not start.
  async function handleGenerate(form) {
    setSaveError(null);
    try {
      await onSaveSettings({
        prompts: form.prompts, negative: form.negative, variants: form.variants,
      });
    } catch (err) {
      setSaveError(err.message);
      return;
    }
    await generate(form);
  }
```

ve `GeneratePanel` çağrısını şununla değiştir:

```javascript
        <GeneratePanel job={job} error={saveError || error} busyElsewhere={busyElsewhere}
                       settings={settings} onGenerate={handleGenerate} onStop={stop} />
```

- [ ] **Step 5: Start the panel's fields from the stored settings**

`queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx`: imzayı ve üç `useState` satırını şununla değiştir:

```javascript
export default function GeneratePanel({ job, error, busyElsewhere, settings, onGenerate, onStop }) {
  // Initial values only: the screen mounts after the settings have loaded, so there is nothing to
  // sync afterwards and typing is never overwritten.
  const [prompts, setPrompts] = useState(settings.prompts);
  const [negative, setNegative] = useState(settings.negative);
  // Text, not a number: the field has to survive being cleared while typing. Whatever is not a
  // whole number goes to the server as null and comes back with the server's own message.
  const [variants, setVariants] = useState(
    settings.variants === null ? "4" : String(settings.variants),
  );
```

- [ ] **Step 6: Build the frontend**

Run: `cd queen-editor/frontend && npm run build`
Expected: `dist/` yeniden üretilir, hata yok.

- [ ] **Step 7: Run the backend suite (nothing should have moved)**

Run: `pytest` (from `queen-editor/`)
Expected: PASS

---

### Task 4: Plan ve kayıt depoları

İki dosyanın şemasını bilen iki ayrı depo. Henüz kimse çağırmıyor — Task 5 bağlayacak.

**Files:**
- Create: `queen-editor/backend/features/photo_generation/data/plan_store.py`
- Create: `queen-editor/backend/features/photo_generation/data/photo_record.py`
- Modify: `queen-editor/backend/features/photo_generation/domain/ports.py`
- Create: `queen-editor/backend/tests/test_plan_store.py`
- Create: `queen-editor/backend/tests/test_photo_record.py`

**Interfaces:**
- Consumes: `DriveStorage.write_text/read_text/append_line/read_lines` (Task 1)
- Produces:
  - `DrivePlanStore(storage)` — `write(project, negative, frames)`, `read(project) -> {"negative": str, "frames": list[dict]}`, `max_number(project) -> int | None`
  - `DrivePhotoRecord(storage)` — `append(project, entry)`, `list(project) -> list[dict]` (en yeni başta)
  - Kare biçimi: `{"number": int, "letter": str, "prompt": str, "seed": int}`
  - Kayıt satırı: `{"file": str, "prompt": str, "negative": str, "seed": int, "createdAt": str}`

- [ ] **Step 1: Write the failing plan store tests**

`queen-editor/backend/tests/test_plan_store.py` oluştur:

```python
from backend.features.photo_generation.data.plan_store import DrivePlanStore
from backend.services.drive.storage import DriveStorage

FRAMES = [
    {"number": 3, "letter": "a", "prompt": "kraliçe tahtta", "seed": 11},
    {"number": 4, "letter": "a", "prompt": "kraliçe balkonda", "seed": 22},
]


def store_at(path):
    return DrivePlanStore(DriveStorage(str(path)))


def test_write_then_read_round_trips(tmp_path):
    store = store_at(tmp_path)
    store.write("düğün", "bulanık", FRAMES)
    assert store.read("düğün") == {"negative": "bulanık", "frames": FRAMES}


def test_reading_a_project_without_a_plan_gives_no_frames(tmp_path):
    assert store_at(tmp_path).read("düğün") == {"negative": "", "frames": []}


def test_a_new_plan_replaces_the_previous_one(tmp_path):
    store = store_at(tmp_path)
    store.write("düğün", "eski", FRAMES)
    store.write("düğün", "yeni", [{"number": 9, "letter": "a", "prompt": "x", "seed": 1}])
    assert store.read("düğün")["frames"] == [
        {"number": 9, "letter": "a", "prompt": "x", "seed": 1}]


def test_max_number_is_the_highest_the_plan_reserved(tmp_path):
    store = store_at(tmp_path)
    store.write("düğün", "", FRAMES)
    assert store.max_number("düğün") == 4


def test_max_number_is_none_without_a_plan(tmp_path):
    assert store_at(tmp_path).max_number("düğün") is None


def test_an_unreadable_plan_reserves_nothing(tmp_path):
    (tmp_path / "düğün").mkdir()
    (tmp_path / "düğün" / "plan.json").write_text("{ yarım", encoding="utf-8")
    store = store_at(tmp_path)
    assert store.read("düğün") == {"negative": "", "frames": []}
    assert store.max_number("düğün") is None
```

- [ ] **Step 2: Run them to verify they fail**

Run: `pytest backend/tests/test_plan_store.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'backend.features.photo_generation.data.plan_store'`

- [ ] **Step 3: Implement the plan store**

`queen-editor/backend/features/photo_generation/data/plan_store.py` oluştur:

```python
"""PlanStore over DriveStorage -- the only place that knows the plan file's name and shape.

The plan is the queue a run works through, not a log of it: it is written once when a batch is
submitted and replaced by the next batch's plan. What a frame actually produced belongs to the
photo record.

A frame carries its number and letter, not a file name: the "<number>_<letter>.png" scheme is
photo_store's to know, and repeating it here would give it a second owner.
"""
import json

FILE = "plan.json"


def _empty():
    return {"negative": "", "frames": []}


class DrivePlanStore:
    def __init__(self, storage):
        self._storage = storage

    def write(self, project, negative, frames):
        """frames: [{"number", "letter", "prompt", "seed"}] in the order they will render."""
        self._storage.write_text(project, FILE, json.dumps(
            {"negative": negative, "frames": frames}, ensure_ascii=False, indent=2))

    def read(self, project):
        raw = self._storage.read_text(project, FILE)
        if raw is None:
            return _empty()
        try:
            data = json.loads(raw)
        except ValueError:
            # A half-written or hand-edited plan must not make the project unopenable.
            return _empty()
        if not isinstance(data, dict) or not isinstance(data.get("frames"), list):
            return _empty()
        negative = data.get("negative")
        return {"negative": negative if isinstance(negative, str) else "",
                "frames": [f for f in data["frames"]
                           if isinstance(f, dict) and isinstance(f.get("number"), int)]}

    def max_number(self, project):
        """Highest number this plan reserved, or None when there is no plan to honour."""
        numbers = [frame["number"] for frame in self.read(project)["frames"]]
        return max(numbers) if numbers else None
```

- [ ] **Step 4: Run them to verify they pass**

Run: `pytest backend/tests/test_plan_store.py -v`
Expected: PASS (6 test)

- [ ] **Step 5: Write the failing photo record tests**

`queen-editor/backend/tests/test_photo_record.py` oluştur:

```python
from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.services.drive.storage import DriveStorage


def record_at(path):
    return DrivePhotoRecord(DriveStorage(str(path)))


def entry(file, prompt="kraliçe tahtta"):
    return {"file": file, "prompt": prompt, "negative": "bulanık", "seed": 11,
            "createdAt": "2026-08-03T14:32:11+00:00"}


def test_a_project_without_a_record_lists_nothing(tmp_path):
    assert record_at(tmp_path).list("düğün") == []


def test_appended_photos_come_back_newest_first(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", entry("0_a.png"))
    record.append("düğün", entry("0_b.png"))
    assert [row["file"] for row in record.list("düğün")] == ["0_b.png", "0_a.png"]


def test_a_row_keeps_every_field_it_was_given(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", entry("0_a.png"))
    assert record.list("düğün")[0] == entry("0_a.png")


def test_turkish_text_survives_the_round_trip(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", entry("0_a.png", prompt="kraliçe bahçede, şövalyeler"))
    assert record.list("düğün")[0]["prompt"] == "kraliçe bahçede, şövalyeler"


def test_a_half_written_last_line_does_not_hide_the_rest(tmp_path):
    # What a session death leaves behind: the line being appended is cut off.
    record = record_at(tmp_path)
    record.append("düğün", entry("0_a.png"))
    with open(tmp_path / "düğün" / "photos.jsonl", "a", encoding="utf-8") as f:
        f.write('{"file": "0_b.pn')
    assert [row["file"] for row in record.list("düğün")] == ["0_a.png"]


def test_rows_without_a_file_name_are_skipped(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", {"prompt": "adı yok"})
    record.append("düğün", entry("0_a.png"))
    assert [row["file"] for row in record.list("düğün")] == ["0_a.png"]
```

- [ ] **Step 6: Run them to verify they fail**

Run: `pytest backend/tests/test_photo_record.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'backend.features.photo_generation.data.photo_record'`

- [ ] **Step 7: Implement the photo record**

`queen-editor/backend/features/photo_generation/data/photo_record.py` oluştur:

```python
"""PhotoRecord over DriveStorage -- the only place that knows the record file's name and shape.

This is the gallery's list: one JSON object per line, appended right after the photo itself is
written, never rewritten. Append-only is the point -- a session that dies mid-write loses at most
the line it was adding, where rewriting the whole file could lose every earlier one.
"""
import json

FILE = "photos.jsonl"


class DrivePhotoRecord:
    def __init__(self, storage):
        self._storage = storage

    def append(self, project, entry):
        """entry: {"file", "prompt", "negative", "seed", "createdAt"}."""
        self._storage.append_line(project, FILE, json.dumps(entry, ensure_ascii=False))

    def list(self, project):
        """Every recorded photo, newest first.

        A line that will not parse is skipped rather than raised on: the last one can be
        half-written after a session death, and one bad line must not hide the photos before it.
        """
        rows = []
        for line in self._storage.read_lines(project, FILE):
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if isinstance(row, dict) and isinstance(row.get("file"), str):
                rows.append(row)
        rows.reverse()
        return rows
```

- [ ] **Step 8: Add the two ports**

`queen-editor/backend/features/photo_generation/domain/ports.py` dosyasının sonuna ekle:

```python
class PlanStore(Protocol):
    def write(self, project: str, negative: str, frames: list) -> None:
        """Replace the project's plan with this run's frames, in render order."""
        ...

    def max_number(self, project: str) -> int | None:
        """Highest number the stored plan reserved; None when there is no plan."""
        ...


class PhotoRecord(Protocol):
    def append(self, project: str, entry: dict) -> None:
        """Add one produced photo's row."""
        ...

    def list(self, project: str) -> list:
        """Every recorded photo, newest first."""
        ...
```

- [ ] **Step 9: Run the whole suite**

Run: `pytest`
Expected: PASS

---

### Task 5: Üretim planı yazar, kaydı doldurur

`start_batch` artık kuyruğu diske yazıyor, seed'leri plan anında çekiyor, her başarılı karede kayda satır ekliyor ve numarayı hem diske hem plana bakarak seçiyor.

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/usecases/start_batch.py`
- Modify: `queen-editor/backend/main.py`
- Test: `queen-editor/backend/tests/test_photo_usecases.py`, `queen-editor/backend/tests/test_photo_routes.py`

**Interfaces:**
- Consumes: `DrivePlanStore`, `DrivePhotoRecord` (Task 4); mevcut `PhotoStore.next_number/save/project_exists`
- Produces:
  - `plan_frames(start, prompts, variants, new_seed) -> list[dict]`
  - `next_number(store, plan_store, project) -> int`
  - `start_batch(runner, store, record, plan_store, generator, new_seed, now, project, text, negative, variants)`

- [ ] **Step 1: Update the fakes and write the failing tests**

`queen-editor/backend/tests/test_photo_usecases.py`: `FakeGenerator`'ın altına iki sahte ekle

```python
class FakePlanStore:
    def __init__(self, reserved=None):
        self.reserved = reserved          # highest number an earlier plan reserved, or None
        self.written = None               # (negative, frames) of the last write

    def write(self, project, negative, frames):
        self.written = (negative, frames)

    def max_number(self, project):
        return self.reserved


class FakeRecord:
    def __init__(self):
        self.rows = []

    def append(self, project, entry):
        self.rows.append(entry)

    def list(self, project):
        return list(reversed(self.rows))
```

`run_batch` yardımcısını şununla değiştir

```python
def run_batch(runner, store, generator, project="düğün", text='["a", "b"]', negative="neg",
              variants=2, seed=42, record=None, plan_store=None):
    return start_batch(runner, store, record or FakeRecord(), plan_store or FakePlanStore(),
                       generator, lambda: seed, lambda: "2026-08-03T14:32:11+00:00",
                       project, text, negative, variants)
```

mevcut iki testi yeni kare biçimine göre değiştir

```python
def test_plan_frames_is_prompt_major():
    seeds = iter([11, 22, 33, 44])
    assert plan_frames(3, ["ilk", "ikinci"], 2, lambda: next(seeds)) == [
        {"number": 3, "letter": "a", "prompt": "ilk", "seed": 11},
        {"number": 3, "letter": "b", "prompt": "ilk", "seed": 22},
        {"number": 4, "letter": "a", "prompt": "ikinci", "seed": 33},
        {"number": 4, "letter": "b", "prompt": "ikinci", "seed": 44},
    ]


def test_every_frame_gets_prompt_negative_and_a_fresh_seed():
    store, generator, runner = FakeStore(), FakeGenerator(), sync_runner()
    seeds = iter([11, 22, 33, 44])
    start_batch(runner, store, FakeRecord(), FakePlanStore(), generator, lambda: next(seeds),
                lambda: "2026-08-03T14:32:11+00:00", "düğün", '["a", "b"]', "neg", 2)
    assert generator.calls == [("a", "neg", 11), ("a", "neg", 22),
                               ("b", "neg", 33), ("b", "neg", 44)]
```

`test_progress_is_reported_before_each_frame` içindeki `current` beklentisini şununla değiştir (rapor artık kareyi olduğu gibi taşıyor, seed dahil)

```python
    assert seen[0]["current"] == {"number": 0, "letter": "a", "prompt": "a", "seed": 42}
```

ve dosyanın sonuna yeni testleri ekle

```python
def test_the_plan_is_written_before_the_first_frame_renders():
    plan_store, runner = FakePlanStore(), sync_runner()

    class ChecksThePlan:
        def generate(self, prompt, negative, seed):
            assert plan_store.written is not None, "plan yazılmadan üretim başladı"
            return b"PNG"

    run_batch(runner, FakeStore(), ChecksThePlan(), text='["a"]', variants=2,
              plan_store=plan_store)
    negative, frames = plan_store.written
    assert negative == "neg"
    assert frames == [{"number": 0, "letter": "a", "prompt": "a", "seed": 42},
                      {"number": 0, "letter": "b", "prompt": "a", "seed": 42}]


def test_each_produced_photo_gets_a_record_row():
    record = FakeRecord()
    run_batch(sync_runner(), FakeStore(), FakeGenerator(), text='["a"]', variants=2, record=record)
    assert record.rows == [
        {"file": "0_a.png", "prompt": "a", "negative": "neg", "seed": 42,
         "createdAt": "2026-08-03T14:32:11+00:00"},
        {"file": "0_b.png", "prompt": "a", "negative": "neg", "seed": 42,
         "createdAt": "2026-08-03T14:32:11+00:00"},
    ]


def test_a_failed_frame_leaves_no_record_row():
    class FailsFirstFrame:
        def __init__(self):
            self.calls = 0

        def generate(self, prompt, negative, seed):
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("node 41: OOM")
            return b"PNG"

    record = FakeRecord()
    run_batch(sync_runner(), FakeStore(), FailsFirstFrame(), text='["a"]', variants=2,
              record=record)
    assert [row["file"] for row in record.rows] == ["0_b.png"]


def test_numbering_skips_what_an_unfinished_plan_reserved():
    # Disk stopped at 4 because the run died, but the plan had reserved through 11.
    store = FakeStore(next_no=5)
    run_batch(sync_runner(), store, FakeGenerator(), text='["a"]', variants=1,
              plan_store=FakePlanStore(reserved=11))
    assert [(n, letter) for n, letter, _d in store.saved] == [(12, "a")]


def test_numbering_follows_disk_when_it_is_ahead_of_the_plan():
    store = FakeStore(next_no=20)
    run_batch(sync_runner(), store, FakeGenerator(), text='["a"]', variants=1,
              plan_store=FakePlanStore(reserved=11))
    assert [(n, letter) for n, letter, _d in store.saved] == [(20, "a")]


def test_a_rejected_batch_writes_no_plan():
    plan_store = FakePlanStore()
    with pytest.raises(InvalidPrompts):
        run_batch(sync_runner(), FakeStore(), FakeGenerator(), text="42", plan_store=plan_store)
    assert plan_store.written is None
```

- [ ] **Step 2: Run them to verify they fail**

Run: `pytest backend/tests/test_photo_usecases.py -v`
Expected: FAIL — `TypeError: start_batch() missing ... required positional argument`

- [ ] **Step 3: Rewrite start_batch**

`queen-editor/backend/features/photo_generation/domain/usecases/start_batch.py`: dosyanın üst kısmı (docstring, importlar, `LETTERS`, üç exception sınıfı) aynı kalır; `plan_frames`'ten sonrasını şununla değiştir:

```python
def plan_frames(start, prompts, variants, new_seed):
    """[{"number", "letter", "prompt", "seed"}] in prompt-major order: 0_a 0_b … 1_a.

    Number = prompt, letter = variant -- nova-3dcg's meaning, kept so a photo's name still says
    which prompt produced it.

    Seeds are drawn here, when the run is planned, rather than when a frame renders: the plan is
    what a resumed run reads back, so a frame has to produce the image it was planned to produce.
    """
    return [{"number": start + index, "letter": LETTERS[variant], "prompt": prompt,
             "seed": new_seed()}
            for index, prompt in enumerate(prompts)
            for variant in range(variants)]


def next_number(store, plan_store, project):
    """The first number a new run may use.

    Two things can claim a number: a file already on disk, and a frame an earlier plan reserved but
    never produced. Both are honoured -- reusing a number would bind one file name to two prompts
    and break what the record means. The record needs no separate check: a row is appended only
    after its photo is written, so it can hold no number disk does not.
    """
    on_disk = store.next_number(project)
    reserved = plan_store.max_number(project)
    return on_disk if reserved is None else max(on_disk, reserved + 1)


def start_batch(runner, store, record, plan_store, generator, new_seed, now,
                project, text, negative, variants):
    prompts = parse_prompts(text)          # raises InvalidPrompts
    # bool is an int in Python, and True would silently mean "1 variant".
    if isinstance(variants, bool) or not isinstance(variants, int) \
            or not 1 <= variants <= len(LETTERS):
        raise InvalidVariants(f"Varyant sayısı 1-{len(LETTERS)} arası bir tam sayı olmalı.")
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")

    frames = plan_frames(next_number(store, plan_store, project), prompts, variants, new_seed)
    # Written before the first render, so a run that dies leaves behind what it meant to make.
    plan_store.write(project, negative, frames)
    total = len(frames)

    def job():
        done = failed = consecutive = 0
        for frame in frames:
            if runner.stop_requested():
                return {"status": "stopped", "done": done, "failed": failed, "total": total}
            runner.report({"done": done, "failed": failed, "total": total, "current": frame})
            try:
                data = generator.generate(frame["prompt"], negative, frame["seed"])
            except Exception as exc:
                failed += 1
                consecutive += 1
                # getattr, not isinstance: domain must not import the ComfyUI service.
                reason = policy.stop_reason(consecutive, getattr(exc, "infra", False))
                if reason:
                    return {"status": "error", "error": f"{reason}\n{exc}",
                            "done": done, "failed": failed, "total": total}
                continue
            filename = store.save(project, frame["number"], frame["letter"], data)
            # Only after the photo exists: the row is what "this photo is here" means.
            record.append(project, {"file": filename, "prompt": frame["prompt"],
                                    "negative": negative, "seed": frame["seed"],
                                    "createdAt": now()})
            done += 1
            consecutive = 0
        return {"status": "done", "done": done, "failed": failed, "total": total}

    if not runner.start(project, job):
        raise Busy("Zaten bir üretim sürüyor.")
```

- [ ] **Step 4: Run the use case tests to verify they pass**

Run: `pytest backend/tests/test_photo_usecases.py -v`
Expected: PASS

- [ ] **Step 5: Update the route test wiring**

`queen-editor/backend/tests/test_photo_routes.py`: importlara ekle

```python
from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.features.photo_generation.data.plan_store import DrivePlanStore
```

`make_client` içindeki depo kurulumunu ve `start_batch` bağlamasını şununla değiştir:

```python
    storage = DriveStorage(str(drive))
    store = DrivePhotoStore(storage)
    record = DrivePhotoRecord(storage)
    plan_store = DrivePlanStore(storage)
    runner = runner or PhotoRunner(spawn=lambda fn: fn())
    blueprint = make_photo_generation_blueprint(
        start_batch=partial(start_batch, runner, store, record, plan_store,
                            generator or FakeGenerator(), lambda: 42,
                            lambda: "2026-08-03T14:32:11+00:00"),
        get_status=partial(get_status, runner),
        stop_generation=partial(stop_generation, runner),
        list_photos=partial(list_photos, store),
        photo_dir=store.photo_dir,
    )
```

`test_generate_returns_202_and_writes_every_frame` artık klasörde iki JSON dosyası daha bulacak; iddiayı yalnız PNG'lere daralt:

```python
    assert sorted(p.name for p in (drive / "düğün").glob("*.png")) == [
        "0_a.png", "0_b.png", "1_a.png", "1_b.png"]
```

- [ ] **Step 6: Wire the new stores in the composition root**

`queen-editor/backend/main.py`: importlara ekle

```python
from datetime import datetime, timezone

from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.features.photo_generation.data.plan_store import DrivePlanStore
```

`_photo_runner = PhotoRunner()` satırının altına ekle

```python
_photo_record = DrivePhotoRecord(_storage)
_plan_store = DrivePlanStore(_storage)
```

ve `start_batch` bağlamasını şununla değiştir

```python
    start_batch=partial(start_batch, _photo_runner, _photo_store, _photo_record, _plan_store,
                        _photo_generator, lambda: random.randint(0, 2**31 - 1),
                        lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")),
```

- [ ] **Step 7: Run the whole suite**

Run: `pytest`
Expected: PASS

---

### Task 6: Galeri kayıttan okur

Son adım: galerinin listesi klasör taraması olmaktan çıkıp kayıt dosyası olur. Diskten listeleme yolu tamamen kaldırılır — aynı soruya cevap veren iki yol bırakmak, standardın *Separation of concerns* bölümünün yasakladığı şeydir. Bu görev bitince Bölüm 6'nın tamamı Colab'da denenebilir.

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/usecases/list_photos.py`
- Modify: `queen-editor/backend/features/photo_generation/data/photo_store.py`
- Modify: `queen-editor/backend/features/photo_generation/domain/ports.py`
- Modify: `queen-editor/backend/main.py`
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`
- Test: `queen-editor/backend/tests/test_photo_usecases.py`, `queen-editor/backend/tests/test_photo_routes.py`, `queen-editor/backend/tests/test_photo_store.py`

**Interfaces:**
- Consumes: `DrivePhotoRecord.list` (Task 4)
- Produces: `list_photos(record, store, project) -> list[dict]`; `GET /api/projects/<p>/photos` → `{"photos": [{"file", "prompt", "negative", "seed", "createdAt"}]}`

- [ ] **Step 1: Update the failing use case tests**

`queen-editor/backend/tests/test_photo_usecases.py`: mevcut iki `list_photos` testini şununla değiştir

```python
def test_list_photos_comes_from_the_record():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "prompt": "a"})
    record.append("düğün", {"file": "0_b.png", "prompt": "a"})
    assert list_photos(record, FakeStore(), "düğün") == [
        {"file": "0_b.png", "prompt": "a"}, {"file": "0_a.png", "prompt": "a"}]


def test_list_photos_rejects_a_missing_project():
    with pytest.raises(ProjectMissing):
        list_photos(FakeRecord(), FakeStore(), "yok")
```

`FakeStore`'dan artık kullanılmayan `list_photos` metodunu ve `photos` parametresini sil:

```python
class FakeStore:
    def __init__(self, projects=("düğün",), next_no=0):
        self.projects = list(projects)
        self.next_no = next_no
        self.saved = []

    def project_exists(self, project):
        return project in self.projects

    def next_number(self, project):
        return self.next_no

    def save(self, project, number, letter, data):
        self.saved.append((number, letter, data))
        return f"{number}_{letter}.png"

    def photo_dir(self, project):
        return f"/fake/{project}"
```

- [ ] **Step 2: Run them to verify they fail**

Run: `pytest backend/tests/test_photo_usecases.py -k list_photos -v`
Expected: FAIL — `TypeError: list_photos() takes 2 positional arguments but 3 were given`

- [ ] **Step 3: Read the gallery's list from the record**

`queen-editor/backend/features/photo_generation/domain/usecases/list_photos.py` dosyasının tamamını şununla değiştir:

```python
"""The gallery's list: the photos the record says exist, newest first.

The folder is not scanned. A row is appended only after its photo is written, so the record is the
list -- and it carries the metadata the gallery's later features (order, export, detail) need,
which a directory listing cannot.
"""
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def list_photos(record, store, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    return record.list(project)
```

- [ ] **Step 4: Remove the disk-listing path**

`queen-editor/backend/features/photo_generation/data/photo_store.py`: `list_photos` metodunu sil. `_number_of` kalır — `next_number` onu kullanmaya devam ediyor. Sınıfın docstring'ini de gerçeğe uydur:

```python
"""PhotoStore over DriveStorage -- the only place that knows photos are named "<n>_<letter>.png"
inside the project folder.

Numbering never reuses a number: the next one is the highest on disk plus one, so a second run
appends instead of overwriting. Files that do not match the scheme (notes, the project's JSON
files) are ignored rather than guessed at.

Listing the folder is deliberately not offered: which photos a project has is the photo record's
answer, and two ways to ask it would be two ways to disagree.
"""
```

`queen-editor/backend/features/photo_generation/domain/ports.py`: `PhotoStore` protokolünden `list_photos` girdisini sil.

`queen-editor/backend/tests/test_photo_store.py`: diskten listelemeye ait dört testi sil — `test_list_photos_newest_number_first`, `test_list_photos_letters_ascend_within_a_number`, `test_list_photos_ignores_files_outside_the_scheme`, `test_list_photos_is_empty_for_a_project_without_photos`.

- [ ] **Step 5: Rebind the use case**

`queen-editor/backend/main.py`: `list_photos` bağlamasını şununla değiştir

```python
    list_photos=partial(list_photos, _photo_record, _photo_store),
```

- [ ] **Step 6: Update the route tests**

`queen-editor/backend/tests/test_photo_routes.py`: `make_client` içindeki bağlamayı şununla değiştir

```python
        list_photos=partial(list_photos, record, store),
```

ve `test_photos_are_listed_newest_first` testini şu üçüyle değiştir:

```python
def test_photos_are_listed_newest_first(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)
    files = [row["file"] for row in
             client.get("/api/projects/düğün/photos").get_json()["photos"]]
    assert files == ["1_a.png", "0_a.png"]


def test_files_without_a_record_row_are_not_listed(tmp_path):
    # The record is the gallery's list: a file no run produced is not part of the project.
    client, drive = make_client(tmp_path)
    (drive / "düğün" / "9_a.png").write_bytes(b"x")
    assert client.get("/api/projects/düğün/photos").get_json() == {"photos": []}


def test_a_listed_photo_carries_the_prompt_that_made_it(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["kraliçe tahtta"]', variants=1)
    row = client.get("/api/projects/düğün/photos").get_json()["photos"][0]
    assert row["file"] == "0_a.png" and row["prompt"] == "kraliçe tahtta"
```

- [ ] **Step 7: Run the whole suite**

Run: `pytest`
Expected: PASS

- [ ] **Step 8: Read the file name out of each row in the gallery**

`queen-editor/frontend/src/features/photo_generation/Gallery.jsx`: dosyanın başındaki yorumu gerçeğe uydur

```javascript
// Artboard 03/04: five columns, newest first (the record's own order). The frame being rendered
// sits at the front as a spinner tile, so the grid shows what is happening, not just what landed.
```

ve `photos.map` bloğunu şununla değiştir

```javascript
        {photos.map((photo) => (
          <Tile key={photo.file} name={photo.file}>
            {/* New tab on click -- the gesture the design gives every tile. */}
            <a href={photoUrl(project, photo.file)} target="_blank" rel="noreferrer">
              <img src={photoUrl(project, photo.file)} alt={photo.file}
                   style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover",
                            border: "1px solid var(--border)", borderRadius: 3, display: "block" }} />
            </a>
          </Tile>
        ))}
```

- [ ] **Step 9: Build the frontend**

Run: `cd queen-editor/frontend && npm run build`
Expected: hata yok

- [ ] **Step 10: Commit the whole bölüm as one commit**

Görevler arasında commit atılmadı; hepsi burada tek commit olarak girer.

```bash
git add queen-editor
git commit -m "feat(queen-editor): Bölüm 6 — kalıcılık + iz"
```

- [ ] **Step 11: Push, then verify on Colab**

```bash
git push
```

Notebook repoyu klonluyor: push edilmemiş iş Colab'da görünmez. Bu yüzden commit doğrulamadan **önce** gelmek zorunda — Colab kodu repodan çekiyor, çalışma ağacından değil.

Colab'da `app.ipynb` → Run all → tünel linkini aç ve spec'in doğrulama listesini uygula:

1. Projeye gir → prompt listesi, negatif, varyant yaz → **Üret**.
2. Sayfayı yenile → üç kutu da dolu geliyor. Projeden çık-gir, başka sekmede aç → yine dolu.
3. Drive'da proje klasöründe `settings.json`, `plan.json`, `photos.jsonl` duruyor. Kayıt dosyasını aç → her satırda dosya adı, prompt, negatif, seed ve zaman var; galerideki fotolarla birebir aynı.
4. Plan dosyasını aç → o üretimin bütün kareleri, sırasıyla ve seed'leriyle duruyor.
5. Bozuk bir liste yapıştır → Üret → hata; sayfayı yenile → bozuk metin kutuda duruyor.
6. Üretimi yarıda **Durdur** → tekrar **Üret** → yeni numaralar, durdurulan üretimin ayırdığı en büyük numaranın üstünden başlıyor; eski kayıt satırları değişmemiş.

**Not (Bölüm 5'ten kalan fotolar):** bu proje daha önce foto üretmişse o fotolar galeriden kaybolur — kayıt satırları yok. Beklenen davranış, migration yazılmıyor (kullanıcı kararı: sistem kullanılmadı, yalnız test edildi). Temiz bir doğrulama için yeni bir proje aç.
