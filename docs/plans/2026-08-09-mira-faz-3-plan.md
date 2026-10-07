# Mira Faz 3 (Proje ekranı) — Uygulama Planı

**Hedef:** Proje ekranı (Madde 6) ve adın/açıklamanın değiştirilmesi (Madde 7).

**Mimari:** Ekran kendi verisini Faz 2'nin çektiği listeden bulur — yeni bir `GET` yok. Düzenleme tek
bir kısmi uç noktadan geçer (`PATCH /api/projects/<id>`); doğrulama domain'de, HTTP kodu rotada.
Composer kabuğu iki ekranda ortak bir bileşene çıkar.

**Kaynak spec:** [Faz 3](../specs/2026-08-09-mira-faz-3-proje-ekrani-design.md)

## Global Kısıtlar

- Boş ad reddi **sunucuda**; tarayıcının iptali kolaylıktır, güvence değil.
- Gönderilmeyen alan değişmez; `hue` ve `createdAt` bu uç noktadan hiç değişmez.
- Domain HTTP kodu bilmez: `ProjectNotFound` → 404, `InvalidProjectName` → 400 çevirisi rotada.
- Komutlar sabit: `python -m pytest d:\code\github\internal-tools\mira -q` ·
  `npm --prefix d:\code\github\internal-tools\mira\frontend test` ·
  `npm --prefix d:\code\github\internal-tools\mira\frontend run build`

---

### Task 1: Düzenleme use case'i ve deposu

**Dosyalar:**
- Oluştur: `mira/backend/features/workspace/domain/usecases/edit_project.py`
- Değiştir: `mira/backend/features/workspace/domain/ports.py`,
  `mira/backend/features/workspace/data/file_project_store.py`
- Test: `mira/backend/tests/test_edit_project.py`

**Arayüzler:**
- Üretir: `edit_project(store, project_id, name=None, desc=None) -> Project` · `ProjectNotFound` ·
  `InvalidProjectName` · `ProjectStore.get(project_id)` · `ProjectStore.replace(project)`

- [ ] **Adım 1: Başarısız testleri yaz** — `test_edit_project.py`:

```python
import pytest

from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.project import Project
from backend.features.workspace.domain.usecases.edit_project import (
    InvalidProjectName,
    ProjectNotFound,
    edit_project,
)
from backend.services.store.store import Store


def _store(tmp_path):
    store = FileProjectStore(Store(str(tmp_path)))
    store.add(
        Project(
            id="pabc",
            name="Thesis",
            desc="Click to add a description.",
            hue=94,
            created_at="2026-08-09T10:00:00+00:00",
        )
    )
    return store


def test_the_name_changes_and_stays_changed(tmp_path):
    edit_project(_store(tmp_path), "pabc", name="Thesis research")
    assert FileProjectStore(Store(str(tmp_path))).get("pabc").name == "Thesis research"


def test_sending_only_a_description_leaves_the_name_alone(tmp_path):
    edited = edit_project(_store(tmp_path), "pabc", desc="Source summaries.")
    assert edited.name == "Thesis"
    assert edited.desc == "Source summaries."


def test_sending_only_a_name_leaves_the_description_alone(tmp_path):
    edited = edit_project(_store(tmp_path), "pabc", name="Renamed")
    assert edited.desc == "Click to add a description."


@pytest.mark.parametrize("bad", ["", "   ", "\n"])
def test_an_empty_name_is_rejected_and_the_old_one_survives(tmp_path, bad):
    store = _store(tmp_path)
    with pytest.raises(InvalidProjectName):
        edit_project(store, "pabc", name=bad)
    assert store.get("pabc").name == "Thesis"


def test_an_unknown_project_is_reported(tmp_path):
    with pytest.raises(ProjectNotFound):
        edit_project(_store(tmp_path), "nope", name="x")


def test_both_fields_are_trimmed(tmp_path):
    edited = edit_project(_store(tmp_path), "pabc", name="  Thesis  ", desc="  Notes.  ")
    assert (edited.name, edited.desc) == ("Thesis", "Notes.")


def test_the_hue_and_the_creation_time_are_never_touched(tmp_path):
    edited = edit_project(_store(tmp_path), "pabc", name="Renamed")
    assert edited.hue == 94
    assert edited.created_at == "2026-08-09T10:00:00+00:00"
```

- [ ] **Adım 2:** `python -m pytest d:\code\github\internal-tools\mira -q` → FAIL (`edit_project` yok)

- [ ] **Adım 3: Yaz**

`domain/usecases/edit_project.py`:

```python
"""Edit a project -- a partial update: whatever is not sent stays as it is."""
from dataclasses import replace

from backend.features.workspace.domain.project import Project


class ProjectNotFound(Exception):
    """No project carries this id."""


class InvalidProjectName(Exception):
    """A project cannot be left without a name."""


def edit_project(store, project_id, name=None, desc=None) -> Project:
    current = store.get(project_id)
    if current is None:
        raise ProjectNotFound(project_id)

    changes = {}
    if name is not None:
        trimmed = name.strip()
        # The browser cancels on an empty prompt, but that is a convenience; the rule lives here.
        if not trimmed:
            raise InvalidProjectName(name)
        changes["name"] = trimmed
    if desc is not None:
        changes["desc"] = desc.strip()

    # hue and created_at are never in `changes`: one is part of the project's identity, the other is
    # its history.
    edited = replace(current, **changes)
    store.replace(edited)
    return edited
```

`ports.py` — `ProjectStore` protokolüne iki metot eklenir:

```python
    def get(self, project_id: str) -> Project | None:
        """The project with this id, or None."""

    def replace(self, project: Project) -> None:
        """Overwrite an existing project's stored fields."""
```

`file_project_store.py` — iki metot eklenir:

```python
    def get(self, project_id):
        for project in self.list_all():
            if project.id == project_id:
                return project
        return None

    def replace(self, project):
        # Only the stored fields are written; the counts are derived and never persisted.
        self._store.write_text(
            f"{project.id}/{PROJECT_FILE}",
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
```

`add` ve `replace` aynı gövdeyi paylaşıyor; ortak kısmı `_write(project)` özel metoduna alınır ve
`add` yalnız "varsa reddet" kontrolünü ekler.

- [ ] **Adım 4:** `python -m pytest d:\code\github\internal-tools\mira -q` → 39 test PASS

---

### Task 2: PATCH uç noktası

**Dosyalar:** Değiştir `presentation/routes.py` · Test `mira/backend/tests/test_projects_api.py`

- [ ] **Adım 1: Testleri ekle**

```python
def test_patch_renames_a_project(tmp_path):
    client = _client(tmp_path)
    created = client.post("/api/projects").get_json()
    resp = client.patch(f"/api/projects/{created['id']}", json={"name": "Thesis"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Thesis"
    assert client.get("/api/projects").get_json()[0]["name"] == "Thesis"


def test_patch_rejects_an_empty_name(tmp_path):
    client = _client(tmp_path)
    created = client.post("/api/projects").get_json()
    assert client.patch(f"/api/projects/{created['id']}", json={"name": "  "}).status_code == 400


def test_patch_on_an_unknown_project_is_404(tmp_path):
    assert _client(tmp_path).patch("/api/projects/nope", json={"name": "x"}).status_code == 404


def test_patch_keeps_the_counts_in_the_answer(tmp_path):
    client = _client(tmp_path)
    created = client.post("/api/projects").get_json()
    body = client.patch(f"/api/projects/{created['id']}", json={"desc": "Notes."}).get_json()
    assert body["chats"] == 0 and body["files"] == 0
```

- [ ] **Adım 2:** koş → FAIL (405/404)

- [ ] **Adım 3: Rotayı ekle** — `routes.py` içine:

```python
    @workspace_bp.patch("/api/projects/<project_id>")
    def patch_project(project_id):
        payload = request.get_json(silent=True) or {}
        try:
            project = edit_project(
                project_store,
                project_id,
                name=payload.get("name"),
                desc=payload.get("desc"),
            )
        except ProjectNotFound:
            return jsonify({"error": "project not found"}), 404
        except InvalidProjectName:
            return jsonify({"error": "a project needs a name"}), 400
        # Re-read so the counts in the answer come from the directories, exactly like the list does.
        return jsonify(_as_json(project_store.get(project_id)))
```

`from flask import Blueprint, jsonify, request` ve `edit_project` ithalleri eklenir.

- [ ] **Adım 4:** koş → 43 test PASS

---

### Task 3: Proje ekranı

**Dosyalar:**
- Oluştur: `mira/frontend/src/features/workspace/ComposerShell.jsx`,
  `mira/frontend/src/features/workspace/ProjectScreen.jsx`
- Değiştir: `HomeScreen.jsx` (kabuğu kullanır), `workspace.css`, `App.jsx`
- Test: `mira/frontend/src/features/workspace/ProjectScreen.test.jsx`

**Arayüzler:**
- Üretir: `<ComposerShell rows placeholder note action />` ·
  `<ProjectScreen project onBack onRename onDescribe />`

- [ ] **Adım 1: Test yaz**

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import ProjectScreen from "./ProjectScreen.jsx";

const PROJECT = {
  id: "p1",
  name: "Thesis research",
  desc: "Source summaries.",
  hue: 45,
  chats: 0,
  files: 0,
};

test("the title, the description and both column headings are drawn", () => {
  render(<ProjectScreen project={PROJECT} />);
  expect(screen.getByRole("heading", { level: 1 }).textContent).toBe("Thesis research");
  expect(screen.getByText("Source summaries.")).toBeTruthy();
  expect(screen.getByText("Chats")).toBeTruthy();
  expect(screen.getByText("Files Mira created")).toBeTruthy();
});

test("an empty file column teaches instead of sitting blank", () => {
  render(<ProjectScreen project={PROJECT} />);
  expect(screen.getByText(/No files yet/)).toBeTruthy();
});

test("a project that does not exist says so instead of crashing", () => {
  render(<ProjectScreen project={null} />);
  expect(screen.getByText("That project does not exist.")).toBeTruthy();
});

test("Rename asks for a new name", () => {
  const onRename = vi.fn();
  render(<ProjectScreen project={PROJECT} onRename={onRename} />);
  fireEvent.click(screen.getByRole("button", { name: "Rename" }));
  expect(onRename).toHaveBeenCalled();
});

test("clicking the description asks to change it", () => {
  const onDescribe = vi.fn();
  render(<ProjectScreen project={PROJECT} onDescribe={onDescribe} />);
  fireEvent.click(screen.getByText("Source summaries."));
  expect(onDescribe).toHaveBeenCalled();
});
```

- [ ] **Adım 2:** `npm --prefix ... test` → FAIL

- [ ] **Adım 3: Yaz**

`ComposerShell.jsx`:

```jsx
// The composer's frame, shared by home and the project screen. It has no behaviour yet: the draft
// rules are Madde 8 and sending is Faz 5.
export default function ComposerShell({ rows, placeholder, note, action }) {
  return (
    <div className="composer">
      <textarea className="composer__input" rows={rows} placeholder={placeholder} />
      <div className="composer__foot">
        {note ? <span className="composer__note">{note}</span> : null}
        <button type="button" className="composer__send" disabled>
          {action}
        </button>
      </div>
    </div>
  );
}
```

`ProjectScreen.jsx`:

```jsx
import ComposerShell from "./ComposerShell.jsx";

export default function ProjectScreen({ project, onBack, onRename, onDescribe }) {
  if (!project) {
    return (
      <div className="screen">
        <div className="screen__column">
          <button type="button" className="back" onClick={onBack}>
            ← back
          </button>
          <p className="screen__missing">That project does not exist.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="screen">
      <div className="screen__column">
        <button type="button" className="back" onClick={onBack}>
          ← back
        </button>

        <div className="screen__title-row">
          <h1 className="screen__title">{project.name}</h1>
          <button type="button" className="ghost" onClick={onRename}>
            Rename
          </button>
        </div>

        {/* The prototype writes "Click to add a description." into every new project, so clicking
            has to do something -- otherwise the app instructs the user and then ignores them. */}
        <p className="screen__desc" onClick={onDescribe}>
          {project.desc}
        </p>

        <ComposerShell
          rows={2}
          placeholder="Start a new chat in this project..."
          note="the answer is saved as a file"
          action="Start"
        />

        <div className="project-grid">
          <div>
            <h2 className="column__title">Chats</h2>
          </div>
          <div>
            <h2 className="column__title">Files Mira created</h2>
            <div className="file-list">
              <p className="file-list__empty">
                No files yet — start a chat and Mira will create one.
              </p>
            </div>
            <p className="file-list__note">
              Chats create the files; you just open and read them.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
```

`HomeScreen.jsx` içindeki composer bloğu `<ComposerShell rows={3} placeholder="Ask anything — Mira
saves the answer to your project as a file." action="Send" />` ile değiştirilir. `note` verilmez —
Home'un mono hedef etiketi Madde 11'in kararı.

- [ ] **Adım 4:** `npm --prefix ... test` → PASS

---

### Task 4: Bağlama ve stil

**Dosyalar:** Değiştir `useProjects.js`, `App.jsx`, `workspace.css` · Test `App.test.jsx` (ekleme)

- [ ] **Adım 1: Test ekle** — `App.test.jsx`:

```jsx
test("a renamed project shows the new name in both places at once", async () => {
  const project = { id: "p1", name: "Old", desc: "d", hue: 45, chats: 0, files: 0 };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (options?.method === "PATCH") {
      return Promise.resolve({ ok: true, status: 200, json: async () => ({ ...project, name: "New" }) });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [project] });
  });
  vi.stubGlobal("fetch", fetch);
  vi.stubGlobal("prompt", vi.fn().mockReturnValue("New"));
  window.history.pushState(null, "", "/p/p1");

  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: "Rename" })).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: "Rename" }));
  await waitFor(() => expect(screen.getAllByText("New").length).toBe(2));
});

test("an empty prompt sends nothing", async () => {
  const project = { id: "p1", name: "Old", desc: "d", hue: 45, chats: 0, files: 0 };
  const fetch = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => [project] });
  vi.stubGlobal("fetch", fetch);
  vi.stubGlobal("prompt", vi.fn().mockReturnValue(""));
  window.history.pushState(null, "", "/p/p1");

  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: "Rename" })).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: "Rename" }));
  expect(fetch.mock.calls.every(([, options]) => options?.method !== "PATCH")).toBe(true);
});
```

`fireEvent` ithali `App.test.jsx`'e eklenir.

- [ ] **Adım 2:** koş → FAIL

- [ ] **Adım 3: `useProjects.js`'e düzenleme ekle**

```js
  const editProject = useCallback(async (id, changes) => {
    try {
      const edited = await patchJson(`/api/projects/${id}`, changes);
      setProjects((current) => current.map((p) => (p.id === id ? edited : p)));
      return edited;
    } catch (failure) {
      setError(failure.message);
      return null;
    }
  }, []);
```

`shared/api.js`'e `patchJson` eklenir; `postJson` ile ortak gövde `sendJson(method, path, body)`
haline gelir.

- [ ] **Adım 4: `App.jsx`'i bağla**

```jsx
  const project = projects.find((candidate) => candidate.id === route.projectId) ?? null;

  const ask = (question, current, field) => {
    const answer = window.prompt(question, current);
    // An empty prompt cancels -- the design's rule, and the server refuses an empty name anyway.
    if (answer && answer.trim()) editProject(route.projectId, { [field]: answer });
  };
```

ve `route.view === "project"` dalında `<ProjectScreen … />` çizilir.

- [ ] **Adım 5: `workspace.css`'e ekran stilleri**

`.screen`, `.screen__column` (max-width 920px, padding 48px 0 60px, `riseIn`), `.back`,
`.screen__title-row`, `.screen__title` (Newsreader 36px), `.screen__desc` (cursor pointer),
`.screen__missing`, `.project-grid` (`minmax(0,1fr) 320px`, gap 40px), `.column__title`,
`.file-list`, `.file-list__empty`, `.file-list__note`, `.composer__note`.

- [ ] **Adım 6:** `npm --prefix ... test` → PASS · `npm --prefix ... run build`

---

## Öz-denetim

**Spec kapsaması.** On bir cümle: 1-2 Task 1 (`test_the_name_changes…`, iki "yalnız şu alan" testi) ·
3 `test_an_empty_name_is_rejected…` + Task 2 400 testi · 4 Task 2 404 testi · 5
`test_both_fields_are_trimmed` · 6 `test_the_hue_and_the_creation_time…` · 7-9 Task 3'ün üç testi ·
10-11 Task 4'ün iki testi.

**Ad tutarlılığı.** `edit_project(store, project_id, name, desc)` Task 1'de tanımlı; Task 2 aynı
adlarla çağırıyor. Ön yüzdeki `editProject(id, changes)` gövdeyi `{name}` / `{desc}` olarak
gönderiyor, sunucunun beklediği anahtarlarla aynı. `ComposerShell` prop'ları (`rows`, `placeholder`,
`note`, `action`) iki çağrı yerinde de aynı.

**Risk.** `App.test.jsx` `window.prompt`'u sahteliyor; jsdom'da `prompt` tanımsız olduğu için
`vi.stubGlobal` şart, ve `afterEach`'teki `unstubAllGlobals` onu da temizliyor.
