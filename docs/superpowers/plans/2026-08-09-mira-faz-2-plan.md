# Mira Faz 2 (Kabuk) — Uygulama Planı

> **Ajan işçiler için:** Bu plan `superpowers:executing-plans` ile madde madde uygulanır.

**Hedef:** İlk gerçek ekranlar — 280px sabit sidebar (Madde 4) ve Home: selamlama, composer kabuğu,
öneriler, proje kartları ve çalışan `New project` (Madde 5).

**Mimari:** Adres çubuğu hangi ekranın açık olduğunun tek kaynağıdır (`useRoute`, History API, kütüphane
yok). Bütün istekler `shared/api.js`'ten geçer. Sidebar ve Home kartları **aynı diziyi** okur, ayrı ayrı
çekmez. Kart sayıları sunucudan gelir: `list_dir` olmayan dizinde boş liste döndürdüğü için sayım
"dizin var mı" sorusu bile sormaz.

**Yığın:** Python 3 · Flask · pytest · React 18 · Vitest · Testing Library

**Kaynak spec:** [Faz 2 — Kabuk](../specs/2026-08-09-mira-faz-2-kabuk-design.md)

## Global Kısıtlar

- Arayüz metni ve kod **İngilizce**.
- Bileşen `fetch`'i doğrudan çağırmaz; `resp.ok` kontrolü yalnız `api.js`'te.
- Renk, yarıçap ve odak halkası `shared/app.css`'ten gelir; bileşen kendi odak stilini yazmaz.
- Vurgu rengi yalnız birincil eylemde (`New chat` butonu). Başka hiçbir yerde dolu vurgu yok.
- Sayılar diske **yazılmaz**; `project.json` şeması değişmez.
- Testlerde `fetch` sahte, saat sahte; hiçbir test gerçek saniye beklemez.
- Komutlar sabit:
  `python -m pytest d:\code\github\internal-tools\mira -q` ·
  `npm --prefix d:\code\github\internal-tools\mira\frontend test` ·
  `npm --prefix d:\code\github\internal-tools\mira\frontend run build`

---

### Task 1: Kart sayıları sunucudan

**Dosyalar:**
- Değiştir: `mira/backend/features/workspace/domain/project.py`,
  `mira/backend/features/workspace/data/file_project_store.py`,
  `mira/backend/features/workspace/presentation/routes.py`
- Test: `mira/backend/tests/test_file_project_store.py` (ekleme),
  `mira/backend/tests/test_projects_api.py` (ekleme)

**Arayüzler:**
- Üretir: `Project(..., chat_count=0, file_count=0)` · `GET /api/projects` yanıtında `chats`, `files`

- [ ] **Adım 1: Başarısız testleri yaz**

`test_file_project_store.py` sonuna:

```python
def test_counts_are_zero_when_the_subdirectories_do_not_exist(tmp_path):
    _store(tmp_path).add(_project())
    listed = _store(tmp_path).list_all()[0]
    assert (listed.chat_count, listed.file_count) == (0, 0)


def test_counts_come_from_the_directories(tmp_path):
    raw = Store(str(tmp_path))
    FileProjectStore(raw).add(_project())
    raw.write_text("pabc/chats/c1.json", "{}")
    raw.write_text("pabc/files/a.md", "a")
    raw.write_text("pabc/files/b.md", "b")
    listed = FileProjectStore(raw).list_all()[0]
    assert (listed.chat_count, listed.file_count) == (1, 2)


def test_counts_are_not_written_into_the_project_file(tmp_path):
    raw = Store(str(tmp_path))
    FileProjectStore(raw).add(_project())
    stored = raw.read_text(f"pabc/{PROJECT_FILE}")
    # A derived answer is never stored: the directory already answers it.
    assert "chat" not in stored and "file" not in stored
```

`test_projects_api.py` sonuna:

```python
def test_project_payload_carries_zero_counts_before_anything_exists(tmp_path):
    body = _client(tmp_path).post("/api/projects").get_json()
    assert body["chats"] == 0
    assert body["files"] == 0
```

- [ ] **Adım 2: Testleri koş, başarısız olduklarını gör**

`python -m pytest d:\code\github\internal-tools\mira -q`
Beklenen: FAIL — `Project` nesnesinin `chat_count` alanı yok, yanıt sözlüğünde `chats` anahtarı yok.

- [ ] **Adım 3: Üç dosyayı değiştir**

`project.py` — iki alan eklenir, ikisi de varsayılanlı:

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
    # Derived from the directories at read time and never written back: the counts are the
    # directory's own answer, so storing them would be a second copy that can go stale.
    chat_count: int = 0
    file_count: int = 0
```

`file_project_store.py` — `list_all` içindeki `Project(...)` çağrısına iki satır eklenir:

```python
            projects.append(
                Project(
                    id=entry,
                    name=raw["name"],
                    desc=raw["desc"],
                    hue=raw["hue"],
                    created_at=raw["createdAt"],
                    chat_count=len(self._store.list_dir(f"{entry}/{CHATS_DIR}")),
                    file_count=len(self._store.list_dir(f"{entry}/{FILES_DIR}")),
                )
            )
```

ve dosyanın başına iki sabit:

```python
CHATS_DIR = "chats"
FILES_DIR = "files"
```

`routes.py` — `_as_json` iki anahtar kazanır:

```python
def _as_json(project):
    return {
        "id": project.id,
        "name": project.name,
        "desc": project.desc,
        "hue": project.hue,
        "createdAt": project.created_at,
        "chats": project.chat_count,
        "files": project.file_count,
    }
```

- [ ] **Adım 4: Testleri koş**

`python -m pytest d:\code\github\internal-tools\mira -q`
Beklenen: 32 test PASS.

---

### Task 2: Veri erişimi ve adres

**Dosyalar:**
- Oluştur: `mira/frontend/src/shared/api.js`, `mira/frontend/src/shared/useRoute.js`
- Test: `mira/frontend/src/shared/api.test.js`, `mira/frontend/src/shared/useRoute.test.js`

**Arayüzler:**
- Üretir: `getJson(path)` · `postJson(path, body?)` · `parsePath(pathname) -> {view, projectId, chatId}` ·
  `useRoute() -> {route, navigate}`

- [ ] **Adım 1: Başarısız testleri yaz**

`api.test.js`:

```js
import { afterEach, expect, test, vi } from "vitest";

import { getJson, postJson } from "./api.js";

afterEach(() => vi.unstubAllGlobals());

function stubFetch(response) {
  const fetch = vi.fn().mockResolvedValue(response);
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

test("getJson returns the parsed body", async () => {
  stubFetch({ ok: true, status: 200, json: async () => [{ id: "p1" }] });
  await expect(getJson("/api/projects")).resolves.toEqual([{ id: "p1" }]);
});

test("a failing response throws instead of returning it", async () => {
  stubFetch({ ok: false, status: 500, json: async () => ({}) });
  await expect(getJson("/api/projects")).rejects.toThrow("500");
});

test("postJson sends POST and needs no body", async () => {
  const fetch = stubFetch({ ok: true, status: 201, json: async () => ({ id: "p1" }) });
  await postJson("/api/projects");
  expect(fetch.mock.calls[0][1].method).toBe("POST");
  expect(fetch.mock.calls[0][1].body).toBeUndefined();
});
```

`useRoute.test.js`:

```js
import { expect, test } from "vitest";

import { parsePath } from "./useRoute.js";

test("the root is home", () => {
  expect(parsePath("/")).toEqual({ view: "home", projectId: null, chatId: null });
});

test("a project path carries its id", () => {
  expect(parsePath("/p/pabc")).toEqual({ view: "project", projectId: "pabc", chatId: null });
});

test("a chat path carries both ids", () => {
  expect(parsePath("/p/pabc/c/c1")).toEqual({ view: "chat", projectId: "pabc", chatId: "c1" });
});

test("anything unrecognised falls back to home", () => {
  expect(parsePath("/nonsense/deep").view).toBe("home");
});
```

- [ ] **Adım 2: Testleri koş, başarısız olduklarını gör**

`npm --prefix d:\code\github\internal-tools\mira\frontend test`
Beklenen: FAIL — `Failed to resolve import "./api.js"`

- [ ] **Adım 3: İkisini yaz**

`shared/api.js`:

```js
// Every request goes through here: a component never calls fetch itself and no caller checks
// resp.ok on its own, so "the server said no" has exactly one meaning across the app.
async function request(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    throw new Error(`${options?.method ?? "GET"} ${path} failed with ${response.status}`);
  }
  return response.json();
}

export function getJson(path) {
  return request(path);
}

export function postJson(path, body) {
  const options = { method: "POST" };
  if (body !== undefined) {
    options.headers = { "Content-Type": "application/json" };
    options.body = JSON.stringify(body);
  }
  return request(path, options);
}
```

`shared/useRoute.js`:

```js
import { useCallback, useEffect, useState } from "react";

// The address bar is the source of truth for which screen is open: a reload must not lose the
// user's place, and the search results of Faz 13 need somewhere to jump to. Three shapes are all we
// have, so this stays a hook rather than a routing dependency.
export function parsePath(pathname) {
  const parts = pathname.split("/").filter(Boolean);
  if (parts[0] === "p" && parts[1]) {
    if (parts[2] === "c" && parts[3]) {
      return { view: "chat", projectId: parts[1], chatId: parts[3] };
    }
    return { view: "project", projectId: parts[1], chatId: null };
  }
  return { view: "home", projectId: null, chatId: null };
}

export function useRoute() {
  const [pathname, setPathname] = useState(() => window.location.pathname);

  useEffect(() => {
    const onPop = () => setPathname(window.location.pathname);
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  const navigate = useCallback((next) => {
    window.history.pushState(null, "", next);
    setPathname(next);
  }, []);

  return { route: parsePath(pathname), navigate };
}
```

- [ ] **Adım 4: Testleri koş**

`npm --prefix d:\code\github\internal-tools\mira\frontend test`
Beklenen: 8 test PASS.

---

### Task 3: Projeler kancası ve sidebar

**Dosyalar:**
- Oluştur: `mira/frontend/src/features/workspace/useProjects.js`,
  `mira/frontend/src/features/workspace/ProjectDot.jsx`,
  `mira/frontend/src/features/workspace/Sidebar.jsx`
- Test: `mira/frontend/src/features/workspace/Sidebar.test.jsx`

**Arayüzler:**
- Tüketir: `getJson`, `postJson`
- Üretir: `useProjects() -> {projects, error, createProject}` · `<ProjectDot hue size />` ·
  `<Sidebar projects activeProjectId onNewChat onNewProject onOpenProject />`

- [ ] **Adım 1: Başarısız testi yaz**

`Sidebar.test.jsx`:

```jsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, test, vi } from "vitest";

import Sidebar from "./Sidebar.jsx";

const PROJECTS = [
  { id: "p1", name: "Thesis research", desc: "", hue: 45, chats: 3, files: 3 },
  { id: "p2", name: "Product notes", desc: "", hue: 150, chats: 2, files: 2 },
];

test("both section headings are there with no projects at all", () => {
  render(<Sidebar projects={[]} activeProjectId={null} />);
  expect(screen.getByText("Projects")).toBeTruthy();
  expect(screen.getByText("Recent chats")).toBeTruthy();
});

test("projects are listed by name", () => {
  render(<Sidebar projects={PROJECTS} activeProjectId={null} />);
  expect(screen.getByText("Thesis research")).toBeTruthy();
  expect(screen.getByText("Product notes")).toBeTruthy();
});

test("clicking a project asks to open it", async () => {
  const onOpenProject = vi.fn();
  render(<Sidebar projects={PROJECTS} activeProjectId={null} onOpenProject={onOpenProject} />);
  await userEvent.click(screen.getByText("Thesis research"));
  expect(onOpenProject).toHaveBeenCalledWith("p1");
});
```

Tıklamalar `@testing-library/react`'in `fireEvent`'iyle yapılır. `user-event` **eklenmez**: bu testler
gerçek bir kullanıcının tuş tuş yazışını taklit etmeye ihtiyaç duymuyor, tek istedikleri bir tıklama —
bunun için zaten kurulu olan pakete bir bağımlılık daha eklemek karşılıksız olurdu.

- [ ] **Adım 2: Testi koş, başarısız olduğunu gör**

`npm --prefix d:\code\github\internal-tools\mira\frontend test`
Beklenen: FAIL — `Failed to resolve import "./Sidebar.jsx"`

- [ ] **Adım 3: Üçünü yaz**

`useProjects.js`:

```js
import { useCallback, useEffect, useState } from "react";

import { getJson, postJson } from "../../shared/api.js";

// One array feeds both lists on screen -- the sidebar and the home cards -- so a new project shows
// up in both without a second round trip and without them ever disagreeing.
export function useProjects() {
  const [projects, setProjects] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    getJson("/api/projects")
      .then((loaded) => {
        if (!cancelled) setProjects(loaded);
      })
      .catch((failure) => {
        if (!cancelled) setError(failure.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const createProject = useCallback(async () => {
    try {
      const created = await postJson("/api/projects");
      // Appended, not prepended: the server lists projects oldest first.
      setProjects((current) => [...current, created]);
      return created;
    } catch (failure) {
      setError(failure.message);
      return null;
    }
  }, []);

  return { projects, error, createProject };
}
```

`ProjectDot.jsx`:

```jsx
// The design's formula. The hue is stored with the project, so adding or removing a neighbour never
// recolours an existing card.
export default function ProjectDot({ hue, size = 9 }) {
  return (
    <span
      className="dot"
      style={{
        width: size,
        height: size,
        borderRadius: size / 3,
        background: `oklch(0.72 0.09 ${hue})`,
      }}
    />
  );
}
```

`Sidebar.jsx`:

```jsx
import ProjectDot from "./ProjectDot.jsx";

export default function Sidebar({ projects, activeProjectId, onNewChat, onNewProject, onOpenProject }) {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <span className="sidebar__mark" />
        <span className="sidebar__wordmark">Mira</span>
      </div>

      {/* Opens nothing yet -- the search panel is Madde 28. */}
      <button type="button" className="sidebar__search">
        <span className="sidebar__search-label">Search</span>
        <span className="sidebar__shortcut">⌘K</span>
      </button>

      <button type="button" className="sidebar__new-chat" onClick={onNewChat}>
        <span className="sidebar__plus">+</span>
        New chat
      </button>

      <div className="sidebar__projects">
        <div className="sidebar__head">
          <span className="sidebar__label">Projects</span>
          <button type="button" className="sidebar__add" onClick={onNewProject} aria-label="New project">
            +
          </button>
        </div>
        {projects.map((project) => (
          <button
            key={project.id}
            type="button"
            className={
              project.id === activeProjectId ? "sidebar__row sidebar__row--active" : "sidebar__row"
            }
            onClick={() => onOpenProject(project.id)}
          >
            <ProjectDot hue={project.hue} />
            <span className="sidebar__row-name">{project.name}</span>
            <span className="sidebar__row-badge">{project.files || ""}</span>
          </button>
        ))}
      </div>

      <div className="sidebar__chats">
        <span className="sidebar__label">Recent chats</span>
      </div>
    </aside>
  );
}
```

- [ ] **Adım 4: Testleri koş**

`npm --prefix d:\code\github\internal-tools\mira\frontend test`
Beklenen: 11 test PASS.

---

### Task 4: Home ekranı, kartlar ve stil

**Dosyalar:**
- Oluştur: `mira/frontend/src/features/workspace/ProjectCard.jsx`,
  `mira/frontend/src/features/workspace/HomeScreen.jsx`,
  `mira/frontend/src/features/workspace/workspace.css`
- Değiştir: `mira/frontend/src/App.jsx`, `mira/frontend/src/App.test.jsx`
- Test: `mira/frontend/src/features/workspace/HomeScreen.test.jsx`

**Arayüzler:**
- Tüketir: `useRoute`, `useProjects`, `Sidebar`, `ProjectDot`
- Üretir: `<ProjectCard project onOpen />` · `<HomeScreen projects error onNewProject onOpenProject />`

Stil dosyası feature'ın yanında durur: birlikte değişen şeyler birlikte yaşar. `shared/app.css` yalnız
uygulama geneli olan şeyi tutar — renkler, odak halkası, kare-dizileri.

- [ ] **Adım 1: Başarısız testleri yaz**

`HomeScreen.test.jsx`:

```jsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, test, vi } from "vitest";

import HomeScreen from "./HomeScreen.jsx";

const ONE = [{ id: "p1", name: "Thesis", desc: "Summaries.", hue: 45, chats: 1, files: 1 }];
const MANY = [{ id: "p2", name: "Notes", desc: "Records.", hue: 150, chats: 2, files: 0 }];

test("the greeting carries no name", () => {
  render(<HomeScreen projects={[]} error={null} />);
  expect(screen.getByRole("heading", { level: 1 }).textContent).toBe("Hi");
});

test("the send button is disabled in this phase", () => {
  render(<HomeScreen projects={[]} error={null} />);
  expect(screen.getByRole("button", { name: "Send" }).disabled).toBe(true);
});

test("a single chat and file are written in the singular", () => {
  render(<HomeScreen projects={ONE} error={null} />);
  expect(screen.getByText("1 chat · 1 file")).toBeTruthy();
});

test("two chats and no files are written in the plural", () => {
  render(<HomeScreen projects={MANY} error={null} />);
  expect(screen.getByText("2 chats · 0 files")).toBeTruthy();
});

test("New project asks for one", async () => {
  const onNewProject = vi.fn();
  render(<HomeScreen projects={[]} error={null} onNewProject={onNewProject} />);
  await userEvent.click(screen.getByRole("button", { name: "New project" }));
  expect(onNewProject).toHaveBeenCalled();
});

test("a load failure is shown instead of an empty screen", () => {
  render(<HomeScreen projects={[]} error="GET /api/projects failed with 500" />);
  expect(screen.getByText(/failed with 500/)).toBeTruthy();
});
```

`App.test.jsx` yeniden yazılır:

```jsx
import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import App from "./App.jsx";

afterEach(() => vi.unstubAllGlobals());

function stubProjects(projects) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => projects }),
  );
}

test("the shell renders", () => {
  stubProjects([]);
  render(<App />);
  expect(screen.getByTestId("app-shell")).toBeTruthy();
});

test("loaded projects reach both the sidebar and the cards", async () => {
  stubProjects([{ id: "p1", name: "Thesis", desc: "Summaries.", hue: 45, chats: 0, files: 0 }]);
  render(<App />);
  await waitFor(() => expect(screen.getAllByText("Thesis").length).toBe(2));
});

test("a project address does not draw home", async () => {
  stubProjects([]);
  window.history.pushState(null, "", "/p/pabc");
  render(<App />);
  await waitFor(() => expect(screen.queryByRole("heading", { level: 1 })).toBeNull());
  window.history.pushState(null, "", "/");
});
```

- [ ] **Adım 2: Testleri koş, başarısız olduklarını gör**

`npm --prefix d:\code\github\internal-tools\mira\frontend test`
Beklenen: FAIL — `Failed to resolve import "./HomeScreen.jsx"`

- [ ] **Adım 3: Kart ve ekranı yaz**

`ProjectCard.jsx`:

```jsx
import ProjectDot from "./ProjectDot.jsx";

function counted(value, singular) {
  return `${value} ${value === 1 ? singular : `${singular}s`}`;
}

export default function ProjectCard({ project, onOpen }) {
  return (
    <button type="button" className="card" onClick={onOpen}>
      <ProjectDot hue={project.hue} />
      <span className="card__name">{project.name}</span>
      <span className="card__desc">{project.desc}</span>
      <span className="card__meta">
        {counted(project.chats, "chat")} · {counted(project.files, "file")}
      </span>
    </button>
  );
}
```

`HomeScreen.jsx`:

```jsx
import ProjectCard from "./ProjectCard.jsx";

// The design's three prompts. They only fill the draft, and that wiring is Madde 8.
const SUGGESTIONS = [
  "Summarize this week's notes",
  "Draft a meeting agenda",
  "Turn my sources into a table",
];

export default function HomeScreen({ projects, error, onNewProject, onOpenProject }) {
  return (
    <div className="home">
      <div className="home__column">
        <h1 className="home__greeting">Hi</h1>

        <div className="composer">
          <textarea
            className="composer__input"
            rows={3}
            placeholder="Ask anything — Mira saves the answer to your project as a file."
          />
          <div className="composer__foot">
            {/* Permanently disabled here: "an empty draft disables Send" is a rule, and its home is
                Madde 8. Half of it written twice would be half of it wrong once. */}
            <button type="button" className="composer__send" disabled>
              Send
            </button>
          </div>
        </div>

        <div className="home__suggestions">
          {SUGGESTIONS.map((label) => (
            <button key={label} type="button" className="pill">
              {label}
            </button>
          ))}
        </div>

        <div className="home__head">
          <h2 className="home__section">Projects</h2>
          <button type="button" className="ghost" onClick={onNewProject}>
            New project
          </button>
        </div>

        {error ? <p className="home__error">{error}</p> : null}

        <div className="home__grid">
          {projects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onOpen={() => onOpenProject(project.id)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Adım 4: `App.jsx`'i bağla**

```jsx
import "./shared/app.css";
import "./features/workspace/workspace.css";

import HomeScreen from "./features/workspace/HomeScreen.jsx";
import Sidebar from "./features/workspace/Sidebar.jsx";
import { useProjects } from "./features/workspace/useProjects.js";
import { useRoute } from "./shared/useRoute.js";

export default function App() {
  const { route, navigate } = useRoute();
  const { projects, error, createProject } = useProjects();

  const openProject = (id) => navigate(`/p/${id}`);

  return (
    <div className="app-shell" data-testid="app-shell">
      <Sidebar
        projects={projects}
        activeProjectId={route.projectId}
        onNewChat={() => navigate("/")}
        onNewProject={createProject}
        onOpenProject={openProject}
      />
      <main className="main">
        {route.view === "home" ? (
          <HomeScreen
            projects={projects}
            error={error}
            onNewProject={createProject}
            onOpenProject={openProject}
          />
        ) : null}
      </main>
    </div>
  );
}
```

`createProject` doğrudan bağlanıyor: yeni proje kurulduktan sonra **Home'da kalınır**, projenin
ekranına atlamak Madde 6'nın işi.

- [ ] **Adım 5: `workspace.css`'i yaz**

```css
.main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

/* --- sidebar ------------------------------------------------------------ */

.sidebar {
  width: 280px;
  flex: none;
  background: var(--sidebar);
  border-right: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  padding: 18px 14px;
  gap: 18px;
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 2px 6px;
}

.sidebar__mark {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  background: var(--accent);
}

.sidebar__wordmark {
  font-family: var(--font-heading);
  font-size: 21px;
  letter-spacing: 0.2px;
}

.sidebar__search {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 8px 12px;
  border: 1px solid var(--line);
  border-radius: 9px;
  background: var(--canvas);
  color: var(--muted);
  font-family: inherit;
  font-size: 13px;
  cursor: pointer;
  text-align: left;
}

.sidebar__search:hover {
  border-color: #c9bfb2;
  color: #3a342e;
}

.sidebar__search-label {
  flex: 1;
}

.sidebar__shortcut {
  font-family: var(--font-mono);
  font-size: 11px;
}

.sidebar__new-chat {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border: none;
  border-radius: 9px;
  background: var(--accent);
  color: #fdfbf8;
  font-family: inherit;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  text-align: left;
}

.sidebar__new-chat:hover {
  background: #9e5232;
}

.sidebar__plus {
  font-size: 16px;
  line-height: 1;
  margin-top: -2px;
}

/* Projects take at most 40% and scroll inside themselves; Recent chats fills the rest. */
.sidebar__projects {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: none;
  max-height: 40%;
  overflow-y: auto;
}

.sidebar__chats {
  display: flex;
  flex-direction: column;
  gap: 2px;
  border-top: 1px solid var(--line);
  padding-top: 10px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.sidebar__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 12px 8px;
}

.sidebar__label {
  font-size: 11px;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: var(--muted);
  padding: 2px 12px 6px;
}

.sidebar__head .sidebar__label {
  padding: 0;
}

.sidebar__add {
  border: none;
  background: none;
  color: var(--muted);
  font-size: 15px;
  cursor: pointer;
  padding: 0 2px;
  line-height: 1;
}

.sidebar__add:hover {
  color: var(--ink);
}

.sidebar__row {
  display: flex;
  align-items: center;
  gap: 9px;
  width: 100%;
  padding: 8px 12px;
  border: none;
  border-radius: 9px;
  cursor: pointer;
  font-family: inherit;
  font-size: 13.5px;
  text-align: left;
  color: #3a342e;
  background: transparent;
}

.sidebar__row:hover {
  background: #e5dfd5;
}

.sidebar__row--active {
  background: #e5dfd5;
}

.sidebar__row-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar__row-badge {
  font-size: 11px;
  font-family: var(--font-mono);
  color: #96795f;
}

/* --- home --------------------------------------------------------------- */

.home {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 32px;
}

.home__column {
  width: 100%;
  max-width: 720px;
  padding-top: 14vh;
  animation: riseIn 0.4s ease both;
}

.home__greeting {
  font-family: var(--font-heading);
  font-weight: 400;
  font-size: 42px;
  margin: 0 0 28px;
  letter-spacing: -0.01em;
}

.composer {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 16px 16px 12px;
  box-shadow: 0 1px 2px rgba(60, 50, 40, 0.04);
}

.composer__input {
  width: 100%;
  border: none;
  outline: none;
  resize: none;
  background: transparent;
  font-family: inherit;
  font-size: 15.5px;
  line-height: 1.6;
  color: var(--ink);
}

.composer__foot {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 6px;
}

.composer__send {
  border: none;
  border-radius: 9px;
  padding: 8px 16px;
  font-family: inherit;
  font-size: 13.5px;
  font-weight: 500;
  background: #e5dfd5;
  color: #a79e93;
  cursor: not-allowed;
}

.home__suggestions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 14px;
}

.pill {
  border: 1px solid var(--line);
  background: var(--surface);
  border-radius: var(--radius-pill);
  padding: 7px 14px;
  font-family: inherit;
  font-size: 12.5px;
  color: #6b6259;
  cursor: pointer;
}

.pill:hover {
  border-color: #c9bfb2;
  color: var(--ink);
}

.home__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin: 44px 0 14px;
}

.home__section {
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0;
}

.ghost {
  border: 1px solid var(--line);
  background: var(--surface);
  border-radius: var(--radius-control);
  padding: 5px 11px;
  font-family: inherit;
  font-size: 12.5px;
  color: #6b6259;
  cursor: pointer;
}

.ghost:hover {
  border-color: #c9bfb2;
}

.home__error {
  font-size: 13px;
  color: #8a5237;
  margin: 0 0 12px;
}

.home__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  padding-bottom: 60px;
}

.card {
  text-align: left;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 16px 16px 14px;
  cursor: pointer;
  font-family: inherit;
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.card:hover {
  border-color: #c9bfb2;
}

.card__name {
  font-size: 15px;
  font-weight: 500;
  color: var(--ink);
}

.card__desc {
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
  text-wrap: pretty;
}

.card__meta {
  font-size: 11.5px;
  color: #a79e93;
  font-family: var(--font-mono);
  margin-top: 4px;
}

.dot {
  display: block;
  flex: none;
}
```

- [ ] **Adım 6: Testleri koş ve derle**

`npm --prefix d:\code\github\internal-tools\mira\frontend test` → 20 test PASS
`npm --prefix d:\code\github\internal-tools\mira\frontend run build` → `dist/` üretilir

---

## Öz-denetim

**Spec kapsaması.** Dokuz kanıtlanacak cümle: (1) `Sidebar.test.jsx` boş liste testi · (2)
`App.test.jsx` "iki yerde birden" · (3) `useProjects.createProject` yeniden çekmiyor, `App.test.jsx`
ve `HomeScreen.test.jsx` birlikte örtüyor · (4) `HomeScreen.test.jsx` tekil/çoğul iki testi · (5)
`HomeScreen.test.jsx` hata testi · (6) `App.test.jsx` `/p/<id>` testi · (7) `useRoute.test.js` ·
(8-9) Task 1'in dört arka uç testi. Spec'in "hedef etiketi bu fazda yok" ve "proje kurulunca Home'da
kalınır" kararları Task 4'te uygulanıyor.

**Ad tutarlılığı.** Sunucunun döndürdüğü anahtarlar `chats`/`files`; ön yüz her yerde bunları
kullanıyor (`project.chats`, `project.files`), Python tarafındaki `chat_count`/`file_count` yalnız
`_as_json` sınırında çevriliyor. `useRoute` `{view, projectId, chatId}` döndürüyor ve `App.jsx` aynı
adları okuyor. `ProjectDot` hem `Sidebar` hem `ProjectCard` tarafından aynı prop adlarıyla
çağrılıyor.

**Yer tutucu yok.** Bütün adımlarda gerçek kod var.

**Bir risk yazılı olsun.** `App.test.jsx`'in `/p/<id>` testi `window.history` durumunu değiştiriyor ve
sonunda geri alıyor; jsdom testleri aynı belgeyi paylaştığı için bu geri alma şart.
