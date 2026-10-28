# Madde 353 — All projects ekranı · test turu planı

> **Ajan için:** Bu plan tek oturumda, satır satır uygulanır (`superpowers:executing-plans`). Adımlar
> `- [ ]` kutularıyla izlenir. Yalnız test yazılır; üretim koduna dokunulmaz.

**Hedef:** 353'ün davranışını — All projects açılışı, `/p/<id>`'nin son sohbete açılması, proje
ekranının ve sohbet silmenin kalkması — kırmızı testler olarak yazmak ve kırmızı hâliyle commit etmek.

**Mimari:** Sunucuda sohbet silmenin yokluğu üç testle; ön uçta yeni `AllProjectsScreen`'in kendi test
dosyası, App'in akış testleri ve CSS kilidi. Proje ekranında duran bugünkü testler aynı iddiayla boş
sohbete (`/p/p1/c/new`) taşınır; tuttukları şey kalkan testler silinir.

**Teknoloji:** pytest + Flask test client; vitest + jsdom + Testing Library.

**Spec:** [2026-09-29-queenagent-m353-all-projects-testler-design.md](../specs/2026-09-29-queenagent-m353-all-projects-testler-design.md)

## Genel kısıtlar

- Testler yalnız CLAUDE.md'deki dört satırla, aynen ve paralel koşulur; daraltılmaz, borulanmaz.
- `skip`, `xfail`, `.skip`, `.todo` yok. Kalkan davranışın testi silinir.
- Test adları ve yorumlar İngilizce; ekran metinleri tasarımın İngilizcesi: `All projects`,
  `+ New project`, `Pinned`, `Recent`, `No projects yet.`, `N chats · N files`.
- Yeni bileşenin adı ve imzası: `AllProjectsScreen({ projects, loading, error, onNewProject, onOpenProject })`,
  `features/workspace/AllProjectsScreen.jsx`, default export.
- Commit mesajında çift tırnak yok, amend yok, sonunda `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

---

### Görev 1: Sunucu — sohbet silinemez

**Dosyalar:**
- Değiştir: `queen-agent/backend/tests/test_chats_api.py` (sohbet silen üç test)
- Değiştir: `queen-agent/backend/tests/test_delete.py` (sohbet silen beş test ve `_seeded`)

- [ ] **Adım 1:** `test_chats_api.py`'de `test_a_chat_can_be_deleted_and_stops_being_listed`,
  `test_deleting_a_chat_leaves_the_project_its_files`, `test_deleting_a_chat_that_is_not_there_is_a_404`
  silinir, yerine:

```python
def test_a_chat_cannot_be_deleted(tmp_path):
    # Madde 353: its one place on screen was the project screen, and that screen is gone -- so is
    # the door. The address still answers GET, which is why a DELETE is refused rather than unknown.
    client = _client(tmp_path)
    pid, cid = _started(client, "hi")
    assert client.delete(f"/api/projects/{pid}/chats/{cid}").status_code == 405
    assert [row["id"] for row in client.get(f"/api/projects/{pid}/chats").get_json()] == [cid]
    assert client.get(f"/api/projects/{pid}/chats/{cid}").status_code == 200
```

- [ ] **Adım 2:** `test_delete.py`'de `_seeded` ve beş sohbet testi silinir; `ChatNotFound`,
  `delete_chat`, `create_project`, `append_message`, `FileProjectStore`, `FileChatStore` import'ları
  gerekmeyenler kalkar. Yerine:

```python
def test_the_delete_chat_use_case_is_gone():
    # Madde 353: nothing on screen deletes a chat any more, so the rule that did is dead code.
    with pytest.raises(ModuleNotFoundError):
        import backend.features.workspace.domain.usecases.delete_chat  # noqa: F401


def test_neither_the_chat_store_nor_its_port_can_delete():
    # Deleting the project still takes its chats, whole, with the directory (FileProjectStore).
    assert not hasattr(FileChatStore, "delete")
    assert not hasattr(ChatStore, "delete")
```

  (`from backend.features.workspace.data.file_chat_store import FileChatStore` ve
  `from backend.features.workspace.domain.ports import ChatStore` kalır / eklenir.)

### Görev 2: `AllProjectsScreen.test.jsx`

**Dosyalar:** Oluştur: `queen-agent/frontend/src/features/workspace/AllProjectsScreen.test.jsx`

- [ ] **Adım 1:** A1–A9:

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import AllProjectsScreen from "./AllProjectsScreen.jsx";

const HOUR = 3600_000;
const ago = (hours) => new Date(Date.now() - hours * HOUR).toISOString();

const PINNED = { id: "p1", name: "Harbour at dusk", chats: 3, files: 2, pinned: true, lastActivity: ago(2) };
const RECENT = { id: "p2", name: "Night market", chats: 1, files: 1, pinned: false, lastActivity: ago(5) };
const OLDER = { id: "p3", name: "Old pier", chats: 0, files: 0, pinned: false, lastActivity: ago(30) };

const labels = (container) =>
  [...container.querySelectorAll(".all-projects__label")].map((label) => label.textContent);
const names = (section) =>
  [...section.querySelectorAll(".all-projects__row-name")].map((name) => name.textContent);

test("the head carries the title and + New project", () => { ... });           // A1
test("the pinned stand under Pinned, the rest under Recent, in the server's order", ...); // A2
test("with nothing pinned there is no Pinned section", ...);                    // A3
test("a row says how many chats and files, and when it was last used", ...);    // A4
test("pressing a row opens that project", ...);                                  // A5
test("with no projects the screen says so", ...);                                // A6
test("while the list loads, the head stands and nothing claims the list is empty", ...); // A7
test("a list that could not be read says what the server said, and nothing else", ...); // A8
test("no row carries a menu and the screen carries no search yet", ...);         // A9
```

  Gövdeler spec'in tablosundaki iddiaları birebir sorar: A2 `labels` `["Pinned", "Recent"]` ve
  bölüm başına `names`; A4 `3 chats · 2 files`, `2h ago`, `1 chat · 1 file`, `0 chats · 0 files`;
  A5 `getByRole("button", { name: /Night market/ })` → `onOpenProject("p2")`; A7 `loading` ve
  `projects={[]}`; A8 `error="the store is unreachable"`; A9 `.all-projects__row-more` ve
  `Search projects` yok.

### Görev 3: `App.test.jsx`

**Dosya:** Değiştir: `queen-agent/frontend/src/App.test.jsx`

- [ ] **Adım 1 — yardımcılar:** `PROJECT`'in yanına:

```jsx
const NOW = new Date().toISOString();
const THESIS = { id: "p1", name: "Thesis", chats: 2, files: 0, pinned: false, lastActivity: NOW };
const ok = (body, status = 200) => Promise.resolve({ ok: true, status, json: async () => body });

// Madde 353: projects, each project's chats, a chat record for any id, and a POST that makes one
// the server then lists first -- where it puts a project nobody has used since it was born.
function serverWithProjects(projects, chatsOf = {}) {
  const live = [...projects];
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path === "/api/projects" && options?.method === "POST") {
      const born = { id: "p9", name: "New project 3", chats: 0, files: 0, pinned: false, lastActivity: NOW };
      live.unshift(born);
      return ok(born, 201);
    }
    if (path === "/api/projects") return ok([...live]);
    const list = path.match(/^\/api\/projects\/(\w+)\/chats$/);
    if (list) return ok(chatsOf[list[1]] ?? []);
    const record = path.match(/\/chats\/(\w+)$/);
    if (record) return ok({ id: record[1], title: record[1], messages: [] });
    return ok([]);
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}
```

- [ ] **Adım 2 — yeni testler B1–B13** (spec'in tablosu). Örnek, B5 ve B9:

```jsx
test("a row opens the project's latest chat", async () => {
  serverWithProjects([THESIS], {
    p1: [
      { id: "c2", title: "Newest", lastActivity: NOW },
      { id: "c1", title: "Older", lastActivity: NOW },
    ],
  });
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: /Thesis/ }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c2"));
});

test("leaving before the project's chats arrive stays where the user went", async () => {
  const waiting = [];
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path) => {
      if (path === "/api/projects/p1/chats") {
        return new Promise((resolve) => waiting.push(resolve));
      }
      if (path === "/api/projects") return ok([THESIS]);
      return ok([]);
    }),
  );
  window.history.pushState(null, "", "/p/p1");
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: "Exit project" }));
  await screen.findByText("All projects", { selector: ".screen__title" });
  await act(async () => {
    waiting.forEach((resolve) =>
      resolve({ ok: true, status: 200, json: async () => [{ id: "c1", title: "Late", lastActivity: NOW }] }),
    );
  });
  expect(window.location.pathname).toBe("/");
});
```

  Ötekiler: B1 `/`'de satır `.all-projects__row-name`, adres `/`, `.sidebar` yok; B2 cevapsız
  `fetch`'le çubuk ve gövde, `.sidebar` ve `skeleton` yok, `All projects` var, cevaptan sonra
  `No projects yet.`; B3; B4 `stubChatInSecondProject` + `Exit project` → `/` ve başlık; B6 boş
  sohbet listesi → `/p/p1/c/new`; B7 `pushState` çağrıları `["/p/p1"]`, `replaceState`'inkiler
  `["/p/p1/c/c2"]`; B8 elle `/p/p1` → `/p/p1/c/c1`; B10 `+ New project` → `/p/p9/c/new`, bir
  `POST /api/projects`, `Exit project`'ten sonra satırlar `["New project 3", "Thesis"]`; B11 menüden
  sil → `/` ve `Notes` satırı; B12 404 sohbet → `← back` → `/`; B13 `/settings` → `All projects`.

- [ ] **Adım 3 — silinenler:** *the bar stands above the sidebar and the screen while the first list
  loads*, *the first load is one skeleton and no screen at all*, *no screen is drawn while the list is
  still on its way* (üçünün yerine B2); *the fork asks the browser where we are…*; *the app opens on
  the first project's screen* (B1); *a skill can be picked before anything is typed*; *the draft chat
  is still reached from the sidebar*; *the fork is not written into the history* (B7); `withChats`,
  `CHAT_ROW` ve sohbet silen üç test; *opening a file unfolds the rail rather than hiding what was
  opened*; *deleting the project you are in moves to the first one left* (B11).

- [ ] **Adım 4 — taşınanlar** (iddia aynı, yer boş sohbet):
  - Proje silmenin testleri ve *Escape closes the menu first*: `pushState("/p/p1")` →
    `"/p/p1/c/new"`; bekleme `{ selector: ".screen__title" }` → `{ selector: ".sidebar__row-name" }`.
    *the sidebar menu and the header open the same question* → *the sidebar menu opens the question*
    (başlığın `Delete`'i gitti). *deleting another project leaves where you are alone*'da adres
    `/p/p1/c/new`. *deleting the last project leaves the empty screen* `No projects yet.` bekler.
  - *a renamed project…*: sahte sunucu yalnız `/api/projects`'e listeyi, ötekilere `[]` verir; Rename
    kenar çubuğunun menüsünden; `New` iki yerde. *an empty prompt sends nothing* aynı yoldan.
  - `withFile`, *a file is not deleted…*, *Refresh asks again…*, *Escape closes the reading panel*,
    *no row anywhere offers a rename*: `/p/p1/c/new`. Panel rayda `←` ile döner (`×` değil); projenin
    kendi `Rename`'i aranmaz.
  - *offline, the strip shows…*: `serverWithProjects([PROJECT])`, `/p/p1/c/new`, `Reply...`.
  - *a chat is born naming the model…*, *the first sentence goes through the one door…*:
    `/p/p1/c/new`, `Reply...`.
  - *the skill picked on the project screen…* → *the skill picked in a draft is what the chat is born
    with*: `/p/p1/c/new`, seçici, `Reply...`, `POST`'un `skill`'i `edit-prompts`.
  - *a skill picked in a chat does not ride into a chat born on the project screen* → *…born in the
    draft*: `Exit project` yerine `New chat`, `Reply...`.
  - *the sidebar folds away…*: `Exit project` yerine katlı sütunun `New chat`'i, adres `/p/p1/c/new`.
  - *Exit project goes back…*, */settings…*, *the app never asks the server for settings*, *with no
    projects…*, *nothing is asked of a workspace-wide chat address*: B-testleri ve `No projects yet.`.

### Görev 4: Öteki ön uç testleri

**Dosyalar:** `FilePanel.test.jsx`, `Skeleton.test.jsx`, `Composer.test.jsx`, `workspace.css.test.js`;
sil: `ProjectScreen.test.jsx`, `NoProjectsScreen.test.jsx`.

- [ ] **Adım 1 — FilePanel:** *the rail's panel comes back* `back` vermeden çizer ve adını *the panel
  is always come back from* yapar; *the project screen's panel closes…* ve *until the project screen
  goes…* silinir; öteki testlerden `back` kalkar.
- [ ] **Adım 2 — Skeleton:** `screen` varyantının testi silinir. **Composer:** *the project screen's
  button is the same arrow under another name* silinir.
- [ ] **Adım 3 — CSS kilidi:** spec'teki silinecek testler silinir, karışık olanlardan yalnız proje
  ekranının satırları çıkar. Yeni:

```js
// Madde 353: the project screen, the "No projects yet" screen and the reader's × went with the
// screens that drew them. Comments are taken out first, so a sentence about a class is not a rule.
test("the project screen and the empty screen left no rule behind", () => {
  const gone = [
    ".screen-layout", ".project-grid", ".chat-list", ".chat-row", ".column__title",
    ".screen__title-row", ".screen__delete", ".file-list__bar", ".panel", ".skeleton--screen",
    ".reader__close", ".empty__title", ".empty__line",
  ];
  const selectors = CSS.replace(/\/\*[\s\S]*?\*\//g, "")
    .split("\n")
    .filter((line) => line && !/^\s/.test(line));
  expect(selectors.filter((line) => gone.some((name) => line.includes(name)))).toEqual([]);
});

test("PINNED and RECENT are the design's label", () => {
  const label = rule(".all-projects__label");
  expect(label).toContain("font-size: 11px");
  expect(label).toContain("letter-spacing: 0.09em");
  expect(label).toContain("text-transform: uppercase");
  expect(label).toContain("color: #6b6259");
});

test("a project row is 48 tall between two hairlines", () => {
  expect(rule(".all-projects__row")).toContain("min-height: 48px");
  expect(rule(".all-projects__row")).toContain("border-bottom: 1px solid #e9e3da");
  expect(rule(".all-projects__list")).toContain("border-top: 1px solid #e9e3da");
});

test("the time is the row's one fixed column", () => {
  const when = rule(".all-projects__row-when");
  expect(when).toContain("width: 96px");
  expect(when).toContain("text-align: right");
  expect(when).toContain("font-family: var(--font-mono)");
});

test("the head puts the title and + New project at its two ends", () => {
  const head = rule(".all-projects__head");
  expect(head).toContain("display: flex");
  expect(head).toContain("justify-content: space-between");
  expect(head).toContain("margin: 0 0 24px");
});

test("No projects yet. is the design's quiet line", () => {
  const empty = rule(".all-projects__empty");
  expect(empty).toContain("padding: 18px 12px");
  expect(empty).toContain("color: #a79e93");
});
```

### Görev 5: Koş ve commit

- [ ] **Adım 1:** Dört satır, paralel:
  `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
  `python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`.
  Beklenen: queen-agent'ın iki süiti yalnız yeni ve kırmızıya dönen testlerde kırmızı
  (`AllProjectsScreen.jsx` yok, bu yüzden o dosya bütünüyle); queen-editor yeşil.
- [ ] **Adım 2:** Spec, plan ve testler commit:

```
test(queen-agent): Madde 353 red -- All projects opens the app, a project opens its latest chat, and no chat can be deleted
```
