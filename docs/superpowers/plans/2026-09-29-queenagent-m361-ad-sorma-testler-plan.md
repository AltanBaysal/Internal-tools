# Madde 361 — Ad sorma ekranı · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Madde 361'in testlerini yazmak — yalnız testleri —, dört satırı koşup yenilerin kırmızı
olduğunu görmek ve kırmızı hâliyle commit'lemek.

**Architecture:** Sunucuda `create_project` bir ad alır ve numaralama gider; ön uçta `/new` adresi,
yeni `NameProjectScreen.jsx`, `Bar`'ın `exit`'i ve App'in oluşturma yolları. Bu tur yalnız bunları
anlatan testleri yazar.

**Tech Stack:** pytest + Flask test client; vitest + jsdom + Testing Library.

**Spec:** [2026-09-29-queenagent-m361-ad-sorma-testler-design.md](../specs/2026-09-29-queenagent-m361-ad-sorma-testler-design.md)

## Global Constraints

- Testler İngilizce, yorumlar NEDEN'i söyler; `skip`, `xfail`, `.skip`, `.todo` yok.
- Testler yalnız CLAUDE.md'nin dört satırıyla koşar, paralel, olduğu gibi.
- Commit mesajında çift tırnak yok, amend yok; sonu `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Ekran sözleri tasarımdaki gibi: `Name your project`, `Name your first project`,
  `Chats live inside a project, and the files they create stay there.`, `Project name`,
  `Create project`, `Cancel`; sunucunun sözü `a project needs a name`.

---

### Task 1: Sunucunun testleri

**Files:**
- Modify: `queen-agent/backend/tests/test_project_usecases.py`
- Modify: `queen-agent/backend/tests/test_projects_api.py`
- Modify: `queen-agent/backend/tests/test_append_message.py`, `test_delete_project.py`, `test_stream_answer.py` (yalnız `create_project(...)` çağrılarına `name=`)

**Interfaces:**
- Produces (uygulama turuna): `create_project(store, new_id, name, now) -> Project`; ad kırpılır,
  boş/`None` → `InvalidProjectName`, depoya yazılmaz. `NEW_PROJECT_NAME` modülde yok.
  `POST /api/projects` `{"name"}` → 201; ad yok/boş → 400 `{"error": "a project needs a name"}`.

- [ ] **Step 1:** `test_project_usecases.py`'de `NEW_PROJECT_NAME` importu ve numaralamanın yedi testi
  silinir; `_born(store, pid="pabc", name="Harbour")` ada geçer; yeniler:

```python
def test_a_new_project_is_born_with_the_name_it_was_given():
    # Madde 361: every + New project asks for the name first, so the project is born with it --
    # trimmed, as a rename trims it.
    store = FakeProjectStore()
    project = _born(store, name="  Harbour at dusk  ")
    assert project.name == "Harbour at dusk"
    assert project.id == "pabc"
    assert project.created_at == "2026-08-09T10:00:00+00:00"


def test_a_project_is_not_born_without_a_name():
    # The screen sends nothing for a blank field, but that is a convenience; the rule lives here.
    store = FakeProjectStore()
    for blank in ("", "   ", None):
        with pytest.raises(InvalidProjectName):
            _born(store, name=blank)
    assert store.projects == []


def test_the_numbering_is_gone():
    # Madde 191 numbered a project born with no name. No road makes one any more.
    assert not hasattr(create_project_module, "NEW_PROJECT_NAME")
```

- [ ] **Step 2:** `test_projects_api.py`'de `_create(client, name="Thesis")` yardımcısı
  (`client.post("/api/projects", json={"name": name})`); her `client.post("/api/projects")` ona geçer;
  *projects opened one after another…* silinir; *created project appears in the list* `Harbour`'la
  yeniden yazılır; yeni:

```python
def test_a_project_needs_a_name_to_be_born(tmp_path):
    client = _client(tmp_path)
    for asked in (client.post("/api/projects"),
                  client.post("/api/projects", json={}),
                  client.post("/api/projects", json={"name": "  "})):
        assert asked.status_code == 400
        assert asked.get_json() == {"error": "a project needs a name"}
    assert client.get("/api/projects").get_json() == []
```

- [ ] **Step 3:** Öteki üç dosyada `create_project(projects, new_id=…, now=…)` →
  `create_project(projects, new_id=…, name="Thesis", now=…)`.

### Task 2: Ön ucun testleri

**Files:**
- Modify: `queen-agent/frontend/src/shared/useRoute.test.js` (R1)
- Modify: `queen-agent/frontend/src/features/workspace/Bar.test.jsx` (B1)
- Create: `queen-agent/frontend/src/features/workspace/NameProjectScreen.test.jsx` (N1–N8)
- Modify: `queen-agent/frontend/src/App.test.jsx` (A1–A9; 353'ün *+ New project makes a project…*'i silinir; `serverWithProjects`'in POST'u gövdedeki adı doğurur)
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css.test.js` (C1–C5; "gone" listesinden iki sınıf çıkar)

**Interfaces:**
- Produces: `parsePath("/new")` → `{ view: "new", projectId: null, chatId: null }`.
  `<Bar project exit onExit />` — `exit` düğmenin adı; verilmezse `project ? "Exit project" : null`.
  `<NameProjectScreen first loading error onCreate />` — `onCreate(name)` kırpılmış adla çağrılır ve
  bir söz döndürebilir; söz bitene kadar ikinci basış çağırmaz.

- [ ] **Step 1:** R1:

```js
test("the naming screen has an address of its own", () => {
  expect(parsePath("/new")).toEqual({ view: "new", projectId: null, chatId: null });
});
```

- [ ] **Step 2:** B1:

```js
test("on the naming screen the right holds Cancel, in Exit project's place and look", () => {
  const onExit = vi.fn();
  const { container } = render(<Bar project={null} exit="Cancel" onExit={onExit} />);
  expect(container.querySelector(".bar__project")).toBeNull();
  const cancel = screen.getByRole("button", { name: "Cancel" });
  expect(cancel.className).toBe("ghost bar__exit");
  fireEvent.click(cancel);
  expect(onExit).toHaveBeenCalled();
});
```

- [ ] **Step 3:** `NameProjectScreen.test.jsx` — N1–N8 (tam kod dosyada): etiket `getByLabelText`,
  `.empty > .empty__box`, cümle, placeholder, `.empty__action`; `first`; `document.activeElement`;
  Enter ve düğme `onCreate("Harbour")`; boş, boşluk ve Shift + Enter çağırmaz; bitmeyen sözle ikinci
  basış çağırmaz; `loading` ve `error`.
- [ ] **Step 4:** `App.test.jsx` — A1–A9 (tam kod dosyada). POST'u sayan yardımcı:
  `posts(fetch)` = `method === "POST"` ve yol `/api/projects` olan çağrılar.
- [ ] **Step 5:** `workspace.css.test.js` — C1–C5 `rule()` ile.

### Task 3: Kırmızıyı görmek ve commit

- [ ] **Step 1:** Dört satır, paralel:
  `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
  `python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`.
  Beklenen: queen-agent'ın iki süiti yalnız yukarıdaki testlerde kırmızı (sunucuda `create_project`'e
  `name=` verenler `TypeError`, `NameProjectScreen.test.jsx` dosya bulunamadığı için); queen-editor'ün
  ikisi yeşil.
- [ ] **Step 2:** Commit:

```
git add docs/superpowers/specs/2026-09-29-queenagent-m361-ad-sorma-testler-design.md docs/superpowers/plans/2026-09-29-queenagent-m361-ad-sorma-testler-plan.md queen-agent/backend/tests queen-agent/frontend/src
git commit -m "test(queen-agent): Madde 361 red -- the naming screen, and a project born with its name"
```
