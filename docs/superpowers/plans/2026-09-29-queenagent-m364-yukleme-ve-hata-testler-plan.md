# Madde 364 — Yüklenirken ve yüklenemeyince · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Madde 364'ün testlerini yazmak — yalnız testleri —, dört satırı koşup yenilerin kırmızı
olduğunu görmek ve kırmızı hâliyle commit'lemek.

**Architecture:** Ön uçta iki ekran (`AllProjectsScreen`, `NameProjectScreen`) yüklenme ve hata
hâllerini tasarımın 172 ve 173'ü gibi çizer; `useProjects` listenin hatasını (`error`) yazmanın
reddinden (`writeError`) ayırır, oluşturmanın reddi çağırana gider; Try again `retryProjects`'tir.
Bu tur yalnız bunları anlatan testleri yazar. Sunucu değişmez.

**Tech Stack:** vitest + jsdom + Testing Library.

**Spec:** [2026-09-29-queenagent-m364-yukleme-ve-hata-testler-design.md](../specs/2026-09-29-queenagent-m364-yukleme-ve-hata-testler-design.md)

## Global Constraints

- Testler İngilizce, yorumlar NEDEN'i söyler; `skip`, `xfail`, `.skip`, `.todo` yok.
- Testler yalnız CLAUDE.md'nin dört satırıyla koşar, paralel, olduğu gibi.
- Commit mesajında çift tırnak yok, amend yok; sonu `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Ekran sözleri tasarımdaki gibi: `Couldn't load projects.`, `Try again`, `Copy`, `Copied`,
  `Could not copy`.
- Sınıflar: `.all-projects__spinner`, `.empty__error`, `.empty__actions`, `.failure__retry`,
  `ghost empty__copy`, `.list-error`, `.empty__refused`.

---

### Task 1: İki ekranın testleri

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/AllProjectsScreen.test.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/NameProjectScreen.test.jsx`

**Interfaces:**
- Produces (uygulama turuna):
  `<AllProjectsScreen … loading error writeError onRetry />` — `loading` önce gelir; `error` ekranı
  hata ekranına çevirir; `writeError` listenin üstünde `.list-error`.
  `<NameProjectScreen first loading error onRetry onCreate />` — `onCreate(name)` reddeden bir söz
  döndürürse ekran kalır, sözün `message`'ı `.empty__refused`'da.

- [ ] **Step 1:** `AllProjectsScreen.test.jsx`'ten *a list that could not be read says what the server
  said, and nothing else* silinir; dosyanın sonuna:

```js
// --- Madde 364: while the list loads, and when it cannot be read (the design's 172, 173) ---------

// jsdom ships no clipboard, so the test supplies one and watches what it is handed.
function stubClipboard(answer) {
  const writeText = vi.fn(() => answer);
  Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
  return writeText;
}

// What failure.js makes of a Flask 500 page: the code and the body, as they came.
const RAW = "HTTP 500: <!doctype html>\n<title>500 Internal Server Error</title>";

test("while the list loads a spinner turns where the list will be", () => {
  const { container } = render(<AllProjectsScreen projects={[]} loading />);
  const spot = container.querySelector(".all-projects__tools").nextElementSibling;
  expect(spot.className).toBe("all-projects__spinner");
  expect(spot.querySelector("[data-testid=spinner]")).toBeTruthy();
});

test("a list that could not be read says so in one sentence, and nothing else stands", () => {
  const { container } = render(<AllProjectsScreen projects={[]} error={RAW} />);
  expect(container.querySelector(".empty > .empty__error").textContent).toBe(
    "Couldn't load projects.",
  );
  expect(screen.queryByText(/HTTP 500/)).toBeNull();
  expect(screen.queryByText("All projects")).toBeNull();
  expect(screen.queryByRole("textbox", { name: "Search projects" })).toBeNull();
  expect(screen.queryByText("No projects yet.")).toBeNull();
});

test("under the sentence stand Try again and Copy, and Try again asks for the list again", () => {
  const onRetry = vi.fn();
  const { container } = render(<AllProjectsScreen projects={[]} error={RAW} onRetry={onRetry} />);
  const buttons = [...container.querySelectorAll(".empty > .empty__actions > button")];
  expect(buttons.map((one) => one.textContent)).toEqual(["Try again", "Copy"]);
  expect(buttons[0].className).toBe("failure__retry");
  expect(buttons[1].className).toBe("ghost empty__copy");
  fireEvent.click(buttons[0]);
  expect(onRetry).toHaveBeenCalled();
});

test("Copy puts the error on the clipboard exactly as it came, and says it landed", async () => {
  const writeText = stubClipboard(Promise.resolve());
  render(<AllProjectsScreen projects={[]} error={RAW} />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  expect(writeText).toHaveBeenCalledWith(RAW);
  expect(await screen.findByRole("button", { name: "Copied" })).toBeTruthy();
});

test("a copy that did not land says so in Copy's place", async () => {
  stubClipboard(Promise.reject(new Error("denied")));
  render(<AllProjectsScreen projects={[]} error={RAW} />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  expect(await screen.findByRole("button", { name: "Could not copy" })).toBeTruthy();
});

test("while Try again reads the list, the frame and its spinner stand again", () => {
  const { container } = render(<AllProjectsScreen projects={[]} loading error={RAW} />);
  expect(screen.getByText("All projects", { selector: ".screen__title" })).toBeTruthy();
  expect(container.querySelector(".all-projects__spinner")).toBeTruthy();
  expect(screen.queryByText("Couldn't load projects.")).toBeNull();
});

test("a write the server refused leaves the list standing, with the server's words over it", () => {
  const { container } = render(
    <AllProjectsScreen projects={[PINNED, RECENT]} writeError="the store is unreachable" />,
  );
  const line = screen.getByText("the store is unreachable");
  expect(line.className).toBe("list-error");
  expect(line.previousElementSibling.className).toBe("all-projects__tools");
  expect(names(container)).toEqual(["Harbour at dusk", "Night market"]);
  expect(screen.queryByText("Couldn't load projects.")).toBeNull();
});
```

- [ ] **Step 2:** `NameProjectScreen.test.jsx`'te *while the list loads, nothing is asked yet* ve *a
  failure says what the server said, and nothing else* şunlarla değişir:

```js
test("while the list loads, the spinner stands alone and nothing is asked yet", () => {
  const { container } = render(<NameProjectScreen loading onCreate={vi.fn()} />);
  const empty = container.querySelector(".empty");
  expect(empty.children.length).toBe(1);
  expect(empty.firstElementChild.dataset.testid).toBe("spinner");
  expect(screen.queryByPlaceholderText("Project name")).toBeNull();
  expect(screen.queryByText(/Name your/)).toBeNull();
});

const RAW = "HTTP 500: <!doctype html>\n<title>500 Internal Server Error</title>";

test("a list that could not be read says so, with Try again and Copy, and asks nothing", () => {
  const onRetry = vi.fn();
  render(<NameProjectScreen error={RAW} onRetry={onRetry} onCreate={vi.fn()} />);
  expect(screen.getByText("Couldn't load projects.").className).toBe("empty__error");
  expect(screen.queryByText(/HTTP 500/)).toBeNull();
  expect(screen.queryByPlaceholderText("Project name")).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  expect(onRetry).toHaveBeenCalled();
});

test("its Copy puts the error on the clipboard exactly as it came", () => {
  const writeText = vi.fn(() => Promise.resolve());
  Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
  render(<NameProjectScreen error={RAW} onCreate={vi.fn()} />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  expect(writeText).toHaveBeenCalledWith(RAW);
});

test("a project the server will not make keeps the name typed, and says what the server said", async () => {
  const onCreate = vi.fn().mockRejectedValue(new Error("a project needs a name"));
  render(<NameProjectScreen onCreate={onCreate} />);
  type("Harbour");
  fireEvent.keyDown(field(), { key: "Enter" });
  const said = await screen.findByText("a project needs a name");
  expect(said.className).toBe("empty__refused");
  expect(said.previousElementSibling.className).toBe("empty__row");
  expect(field().value).toBe("Harbour");
});
```

### Task 2: App'in testleri

**Files:**
- Modify: `queen-agent/frontend/src/App.test.jsx`

**Interfaces:**
- Consumes: Task 1'in iki ekranı; `serverForRows`, `ROWS`, `sections`, `actionsFor`,
  `onAllProjects`, `nameField`, `barExit`, `ok`, `THESIS` dosyada zaten var.

- [ ] **Step 1:** *a list that fails to load says so instead of claiming there are none* `Couldn't load
  projects.`'i bekler ve `/HTTP 500/`'ün ekranda olmadığını söyler.
- [ ] **Step 2:** *a project the server will not make says what the server said* sonunda
  `expect((await nameField()).value).toBe("Harbour")`.
- [ ] **Step 3:** Delete bölümünden sonra yeni bölüm:

```js
// --- Madde 364: the list that did not come, and a write the server refused ------------------------

const FAILED = { ok: false, status: 500, text: async () => "" };

// The first read of the list fails; the next one waits until the test answers it.
function listFailingOnce(projects) {
  let reads = 0;
  let answer;
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path) => {
      if (path !== "/api/projects") return ok([]);
      reads += 1;
      if (reads === 1) return Promise.resolve(FAILED);
      return new Promise((resolve) => {
        answer = () => resolve({ ok: true, status: 200, json: async () => projects });
      });
    }),
  );
  return () => answer();
}

test("Try again reads the list again, with the spinner while it waits", async () => {
  const answer = listFailingOnce([THESIS]);
  render(<App />);
  fireEvent.click(await screen.findByRole("button", { name: "Try again" }));
  expect(await screen.findByText("All projects", { selector: ".screen__title" })).toBeTruthy();
  expect(document.querySelector(".all-projects__spinner [data-testid=spinner]")).toBeTruthy();
  await act(async () => {
    answer();
  });
  expect(await screen.findByText("Thesis", { selector: ".all-projects__row-name" })).toBeTruthy();
  expect(screen.queryByText("Couldn't load projects.")).toBeNull();
});

test("on the naming screen a list that did not come offers Try again, and no way back", async () => {
  const answer = listFailingOnce([THESIS]);
  window.history.pushState(null, "", "/new");
  render(<App />);
  expect(await screen.findByText("Couldn't load projects.")).toBeTruthy();
  expect(barExit()).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  await act(async () => {
    answer();
  });
  expect(await screen.findByLabelText("Name your project")).toBe(await nameField());
});

// serverForRows, with its first rename, pin or delete refused in the server's own words.
function refusingFirstWrite(projects) {
  const fetch = serverForRows(projects);
  const keep = fetch.getMockImplementation();
  let refused = false;
  fetch.mockImplementation((path, options) => {
    if (!refused && ["PATCH", "DELETE"].includes(options?.method)) {
      refused = true;
      return Promise.resolve({
        ok: false,
        status: 500,
        text: async () => JSON.stringify({ error: "the store is unreachable" }),
      });
    }
    return keep(path, options);
  });
  return fetch;
}

const renameTo = (from, to) => {
  actionsFor(from);
  fireEvent.click(screen.getByRole("button", { name: "Rename" }));
  const field = screen.getByRole("textbox", { name: "Project name" });
  fireEvent.change(field, { target: { value: to } });
  fireEvent.keyDown(field, { key: "Enter" });
};

test("a rename the server refuses leaves All projects standing, with the server's words", async () => {
  refusingFirstWrite(ROWS);
  const { container } = render(<App />);
  await onAllProjects();
  renameTo("Thesis", "Dissertation");
  expect((await screen.findByText("the store is unreachable")).className).toBe("list-error");
  expect(sections(container)).toEqual({ Recent: ["Thesis", "Notes"] });
  expect(screen.queryByText("Couldn't load projects.")).toBeNull();
});

test("a delete the server refuses leaves the project where it was", async () => {
  refusingFirstWrite(ROWS);
  const { container } = render(<App />);
  await onAllProjects();
  actionsFor("Notes");
  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  fireEvent.click(screen.getByRole("button", { name: "Delete" }));
  expect((await screen.findByText("the store is unreachable")).className).toBe("list-error");
  expect(sections(container)).toEqual({ Recent: ["Thesis", "Notes"] });
});

test("the next write that lands takes the refusal's line away", async () => {
  refusingFirstWrite(ROWS);
  const { container } = render(<App />);
  await onAllProjects();
  renameTo("Thesis", "Dissertation");
  await screen.findByText("the store is unreachable");
  actionsFor("Notes");
  fireEvent.click(screen.getByRole("button", { name: "Pin" }));
  await waitFor(() =>
    expect(sections(container)).toEqual({ Pinned: ["Notes"], Recent: ["Thesis"] }),
  );
  expect(screen.queryByText("the store is unreachable")).toBeNull();
});
```

### Task 3: Stil testleri

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css.test.js`

- [ ] **Step 1:** Dosyanın sonuna:

```js
// --- Madde 364: the wait and the list that did not come (the design's 172, 173, kit.css) ----------

test("on All projects the spinner stands centred where the list will be", () => {
  const spot = rule(".all-projects__spinner");
  expect(spot).toContain("display: flex");
  expect(spot).toContain("justify-content: center");
  expect(spot).toContain("padding: 40px 12px");
});

test("Try again and Copy stand side by side under the sentence", () => {
  const actions = rule(".empty__actions");
  expect(actions).toContain("display: flex");
  expect(actions).toContain("gap: 10px");
  expect(actions).toContain("margin-top: 16px");
});

test("the failure's Copy answers in Copy's own colours", () => {
  expect(rule('.empty__copy[data-said="yes"]')).toContain("color: var(--accent)");
  expect(rule('.empty__copy[data-said="no"]')).toContain("color: var(--destructive)");
});

test("a refused project's words are the server's, in the failure's own voice", () => {
  const said = rule(".empty__refused");
  expect(said).toContain("font-family: var(--font-mono)");
  expect(said).toContain("font-size: 11.5px");
  expect(said).toContain("color: #a4735a");
  expect(said).toContain("overflow-wrap: anywhere");
});
```

### Task 4: Kırmızıyı görmek ve commit

- [ ] **Step 1:** Dört satır, paralel:
  `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
  `python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`.
  Beklenen: yalnız `npm test --prefix queen-agent/frontend` kırmızı, yalnız yukarıdaki yeni ve
  değişen testlerde; öteki üçü yeşil.
- [ ] **Step 2:** Commit:

```
git add docs/superpowers/specs/2026-09-29-queenagent-m364-yukleme-ve-hata-testler-design.md docs/superpowers/plans/2026-09-29-queenagent-m364-yukleme-ve-hata-testler-plan.md queen-agent/frontend/src
git commit -m "test(queen-agent): Madde 364 red -- the wait, the list that did not come, and a refused write"
```
