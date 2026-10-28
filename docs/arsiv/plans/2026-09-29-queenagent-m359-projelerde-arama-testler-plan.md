# Madde 359 — Projelerde arama · test planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Amaç:** 359'un testlerini yazmak ve kırmızı hâliyle commit etmek; kod yazılmaz.

**Mimari:** Arama yalnız ön uçta, `AllProjectsScreen`'in kendi durumu (FOUNDATION, Karar 4). Testler
bileşenin testine ve `workspace.css.test.js`'in kilidine eklenir; sunucu değişmez.

**Teknoloji:** vitest + jsdom + Testing Library.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m359-projelerde-arama-testler-design.md)

## Genel kısıtlar

- Kutunun adı ve yazısı tam olarak `Search projects`; eşleşme yoksa tam olarak `No projects match "<kırpılmış arama>".`
- Sınıflar tasarımın: `all-projects__tools`, `all-projects__search`, `all-projects__empty`.
- Test adları ve yorumlar İngilizce; hiçbir test `skip` / `todo` değil.
- Testler yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi koşulur.

---

### Görev 1: Bileşenin testleri (D1–D9, A9)

**Dosyalar:**
- Değişir: `queen-agent/frontend/src/features/workspace/AllProjectsScreen.test.jsx`

- [ ] **Adım 1: A9'dan arama yarısını çıkar.** Son test *no row carries a menu yet* olur, yalnız
  `.all-projects__row-more`'un yokluğunu tutar; yorumu `// The row's ⋯ is Madde 360's.`

- [ ] **Adım 2: Dosyanın sonuna D1–D9'u ekle.**

```jsx
// --- Madde 359: the search (the design's items 135, 142, 167) ------------------------------------

const search = () => screen.getByRole("textbox", { name: "Search projects" });
const type = (text) => fireEvent.change(search(), { target: { value: text } });

test("the search stands under the head, named Search projects", () => {
  render(<AllProjectsScreen projects={[PINNED, RECENT]} />);
  const box = search();
  expect(box.getAttribute("placeholder")).toBe("Search projects");
  expect(box.classList.contains("all-projects__search")).toBe(true);
  // The tabs join this row with Madde 363.
  const tools = box.closest(".all-projects__tools");
  expect(tools.previousElementSibling.classList.contains("all-projects__head")).toBe(true);
});

test("the search has the focus when the screen opens", () => {
  render(<AllProjectsScreen projects={[PINNED, RECENT]} />);
  expect(document.activeElement).toBe(search());
});

test("while the list loads the search already stands, and has the focus", () => {
  // Given when the screen opens, not when the list comes: by then the user may be elsewhere.
  render(<AllProjectsScreen projects={[]} loading />);
  expect(document.activeElement).toBe(search());
});

test("typing narrows the list by name, and a section left empty goes", () => {
  const { container } = render(<AllProjectsScreen projects={[PINNED, RECENT, OLDER]} />);
  type("night");
  expect(names(container)).toEqual(["Night market"]);
  expect(labels(container)).toEqual(["Recent"]);
});

test("the search ignores case, accents and the spaces around it", () => {
  const CAFE = { ...OLDER, id: "p4", name: "Café noir" };
  const { container } = render(<AllProjectsScreen projects={[PINNED, RECENT, OLDER, CAFE]} />);
  type("HARBOUR");
  expect(names(container)).toEqual(["Harbour at dusk"]);
  type("cafe");
  expect(names(container)).toEqual(["Café noir"]);
  type("  pier  ");
  expect(names(container)).toEqual(["Old pier"]);
});

test("only the name is searched", () => {
  const { container } = render(<AllProjectsScreen projects={[PINNED, RECENT, OLDER]} />);
  type("chats");
  expect(names(container)).toEqual([]);
  type("2h");
  expect(names(container)).toEqual([]);
});

test("with no match the screen says so, with what was typed", () => {
  const { container } = render(<AllProjectsScreen projects={[PINNED, RECENT]} />);
  type("  zzz ");
  expect(screen.getByText('No projects match "zzz".', { selector: ".all-projects__empty" })).toBeTruthy();
  expect(container.querySelector(".all-projects__row")).toBeNull();
  expect(screen.queryByText("No projects yet.")).toBeNull();
});

test("emptying the box brings the whole list back", () => {
  const { container } = render(<AllProjectsScreen projects={[PINNED, RECENT, OLDER]} />);
  type("zzz");
  type("");
  expect(labels(container)).toEqual(["Pinned", "Recent"]);
  expect(names(container)).toEqual(["Harbour at dusk", "Night market", "Old pier"]);
});

test("with no projects at all a search still says there are none", () => {
  // Not a match that failed: there is nothing to match.
  render(<AllProjectsScreen projects={[]} />);
  type("zzz");
  expect(screen.getByText("No projects yet.")).toBeTruthy();
  expect(screen.queryByText(/No projects match/)).toBeNull();
});
```

### Görev 2: Stil kilidi (C7, C8)

**Dosyalar:**
- Değişir: `queen-agent/frontend/src/features/workspace/workspace.css.test.js` — *No projects yet. is
  the design's quiet line* testinin altına.

- [ ] **Adım 1: C7 ve C8'i ekle.**

```js
test("the search's row stands under the head, as the design spaces it", () => {
  const tools = rule(".all-projects__tools");
  expect(tools).toContain("display: flex");
  expect(tools).toContain("margin: 0 0 28px");
});

test("the search box is the design's field", () => {
  const box = rule(".all-projects__search");
  expect(box).toContain("flex: 1");
  expect(box).toContain("border: 1px solid var(--line)");
  expect(box).toContain("border-radius: var(--radius-control)");
  expect(box).toContain("padding: 8px 12px");
  expect(box).toContain("background: var(--surface)");
  expect(box).toContain("font-size: 13.5px");
});
```

### Görev 3: Kırmızıyı gör ve commit et

- [ ] **Adım 1: Dört satırı paralel koş.** `npm test --prefix queen-agent/frontend` D1–D9, C7, C8'de
  kırmızı (kutu yok; `rule` `-1` bulur); A9 yeşil. Öteki üç süit yeşil.
- [ ] **Adım 2: Commit.** Spec, bu plan ve iki test dosyası:
  `test(queen-agent): Madde 359 red -- Search projects narrows All projects by name, focused on open`
