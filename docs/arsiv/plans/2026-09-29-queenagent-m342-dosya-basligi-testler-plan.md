# Madde 342 — Açık dosyanın başlığı · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Açık dosyanın iki satırlı başlığını — solda çerçeveli `←`, sağda yazılı `Refresh` ve
`Copy`, altta ad, Download yok — ve `←`'nün satırın ortasında durmasını tutan testler, kırmızı.

**Architecture:** Dört test dosyası: `FilePanel.test.jsx` başlığın yapısını ve `Copy`'nin sözünü,
`useFile.test.jsx` ve `FileRail.test.jsx` Download'ın gidişini, `workspace.css.test.js` stil
dosyasının kilidini tutar.

**Tech Stack:** vitest + jsdom, Testing Library.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m342-dosya-basligi-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Test adı ve yorum İngilizce, UI metni İngilizce.
- Bu turda kod ve stil dosyası değişmez; `dist` derlenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Başlığın testleri, kırmızı

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/FilePanel.test.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/useFile.test.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/FileRail.test.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css.test.js`

**Interfaces:**
- Produces (uygulama turunun karşılayacağı): `.reader__head` > `.reader__bar` (ilk çocuk `←` ya da
  `×`, sonra `.reader__tools` > `Refresh`, `Copy` — ikisi de `ghost`) ve çubuğun dışında
  `.reader__name`; `Copy`'nin yazısı `Copied` / `Could not copy`, 2500 ms sonra `Copy`;
  `useFile(...).download` yok; CSS'te `.reader__head`, `.reader__bar`, `.back.back--inline`,
  `.reader__bar > .back`, `.reader__bar > button, .reader__tools > button`, `.reader__copy` kuralları.

- [ ] **Step 1: `FilePanel.test.jsx`**

İçe aktarma `act`'i de alır. Download'ın dört testi silinir. "Refresh says nothing while it runs"
ve Madde 193'ün yorumundaki Download cümleleri çıkar. "the answer is the icon's own name…" şuna
dönüşür, ve yanına:

```jsx
test("the answer is the button's own word and adds no line to the panel", async () => {
  stubClipboard(Promise.resolve());
  render(<FilePanel name="plan.md" file={FILE} />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  const said = await screen.findByRole("button", { name: "Copied" });
  expect(said.textContent).toBe("Copied");
  expect(screen.getAllByText("Copied").length).toBe(1);
});

test("a copy that did not land says so in the same place", async () => {
  stubClipboard(Promise.reject(new Error("denied")));
  render(<FilePanel name="plan.md" file={FILE} />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  const said = await screen.findByRole("button", { name: "Could not copy" });
  expect(said.textContent).toBe("Could not copy");
});

test("after a moment the button is Copy again", async () => {
  vi.useFakeTimers();
  try {
    stubClipboard(Promise.resolve());
    render(<FilePanel name="plan.md" file={FILE} />);
    fireEvent.click(screen.getByRole("button", { name: "Copy" }));
    await act(() => vi.advanceTimersByTimeAsync(0));
    expect(screen.getByRole("button", { name: "Copied" }).textContent).toBe("Copied");
    await act(() => vi.advanceTimersByTimeAsync(2500));
    expect(screen.getByRole("button", { name: "Copy" }).textContent).toBe("Copy");
  } finally {
    vi.useRealTimers();
  }
});
```

Sona Madde 342'nin başlık testleri:

```jsx
test("the header carries no Download", () => {
  render(<FilePanel name="plan.md" file={FILE} back />);
  expect(screen.queryByRole("button", { name: "Download" })).toBeNull();
});

test("the bar holds the way back at one edge, and Refresh then Copy at the other", () => {
  const { container } = render(<FilePanel name="plan.md" file={FILE} back />);
  const bar = container.querySelector(".reader__head > .reader__bar");
  expect(bar.firstElementChild.textContent).toBe("←");
  const tools = [...bar.querySelectorAll(".reader__tools > button")].map((one) => one.textContent);
  expect(tools).toEqual(["Refresh", "Copy"]);
});

test("Refresh and Copy are framed buttons with words on them", () => {
  render(<FilePanel name="plan.md" file={FILE} back />);
  expect(screen.getByRole("button", { name: "Refresh" }).classList.contains("ghost")).toBe(true);
  expect(screen.getByRole("button", { name: "Copy" }).classList.contains("ghost")).toBe(true);
});

test("the name stands under the bar, on a row of its own", () => {
  const { container } = render(<FilePanel name="plan.md" file={FILE} back />);
  const head = container.querySelector(".reader__head");
  expect(head.firstElementChild.className).toBe("reader__bar");
  expect(head.lastElementChild.className).toBe("reader__name");
  expect(head.lastElementChild.textContent).toBe("plan.md");
});

test("until the project screen goes, its × stands where the rail's ← does", () => {
  const { container } = render(<FilePanel name="plan.md" file={FILE} onClose={vi.fn()} />);
  expect(container.querySelector(".reader__bar").firstElementChild.textContent).toBe("×");
});
```

- [ ] **Step 2: `useFile.test.jsx`**

`beforeEach`'in nesne URL'si ve bağlantı tıklaması sahteleri, `Host`'un `save` düğmesi, ve kaydetmenin
iki testi (`saving reads the file again…`, `the saved file keeps the name…`) silinir; `beforeEach`
içe aktarmadan çıkar. Sona:

```jsx
test("the open file offers no download", () => {
  let reading;
  function Probe() {
    reading = useFile("p1");
    return null;
  }
  render(<Probe />);
  expect(reading.download).toBeUndefined();
});
```

- [ ] **Step 3: `FileRail.test.jsx`** — "the rail's reader is come back from…" testinin altına:

```jsx
test("while reading, the rail offers no Download", () => {
  render(<FileRail files={FILES} reading={{ name: "outline.md", file: OPEN_FILE }} />);
  expect(screen.queryByRole("button", { name: "Download" })).toBeNull();
});
```

- [ ] **Step 4: `workspace.css.test.js`** — "the room around the document belongs to the document"
testinin altına:

```js
// Every rule that selects the element, comments taken out first so that a sentence about a class
// is not read as a selector.
function rulesSelecting(names) {
  const bare = CSS.replace(/\/\*[\s\S]*?\*\//g, "");
  return [...bare.matchAll(/([^{}]+)\{([^}]*)\}/g)]
    .map(([, selectors, body]) => ({ selectors: selectors.split(",").map((one) => one.trim()), body }))
    .filter(({ selectors }) => selectors.some((one) => names.some((name) => one.includes(name))));
}

test("the reader's head is the bar above the name, closed by a line", () => {
  const head = rule(".reader__head");
  expect(head).toContain("flex-direction: column");
  expect(head).toContain("border-bottom: 1px solid var(--line)");
});

test("the way back and the two tools stand at the bar's two edges", () => {
  const bar = rule(".reader__bar");
  expect(bar).toContain("justify-content: space-between");
  expect(bar).toContain("align-items: center");
});

test("a way back inside a row outweighs the way back's own margin", () => {
  // APP-BUGS 48: one class lost to .back's 18 by source order, and the arrow stood 9 above the
  // middle of its row. Two classes win wherever the rule is written.
  expect(rule(".back.back--inline")).toContain("margin-bottom: 0");
  expect(CSS).not.toContain("\n.back--inline {");
});

test("the reader's way back is framed like Refresh and Copy", () => {
  const back = rule(".reader__bar > .back");
  expect(back).toContain("border: 1px solid var(--line)");
  expect(back).toContain("background: var(--surface)");
  expect(back).toContain("border-radius: var(--radius-control)");
  expect(back).toContain("padding: 5px 11px");
});

test("the three buttons in the bar are one height", () => {
  expect(grouped(".reader__bar > button,")).toContain("line-height: 20px");
});

test("Copy is wide enough for Could not copy, and Download is gone", () => {
  expect(rule(".reader__copy")).toContain("min-width: 116px");
  expect(CSS).not.toContain(".reader__download");
});

test("no rule takes the ghost's frame off Refresh or Copy", () => {
  const theirs = rulesSelecting([".reader__refresh", ".reader__copy"]);
  expect(theirs.length).toBeGreaterThan(0);
  for (const { selectors, body } of theirs) {
    expect(body).not.toContain("border: none");
    expect(body).not.toContain("background: transparent");
    expect(selectors).not.toContain(".reader__refresh:hover");
    expect(selectors).not.toContain(".reader__copy:hover");
  }
});
```

- [ ] **Step 5: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: QueenAgent'ın ön ucunda yeni testler kırmızı — Download hâlâ var, başlık tek satır,
`Copy`'nin yazısı `⧉`, stil dosyasında yeni kurallar yok. Öteki üç süit taban çizgisinde
(queen-editor'ün arka ucu 377'nin iki kırmızısıyla).

- [ ] **Step 6: Kırmızıyı commit'le**

```powershell
git add queen-agent/frontend/src/features/workspace/FilePanel.test.jsx queen-agent/frontend/src/features/workspace/useFile.test.jsx queen-agent/frontend/src/features/workspace/FileRail.test.jsx queen-agent/frontend/src/features/workspace/workspace.css.test.js docs/specs/2026-09-29-queenagent-m342-dosya-basligi-testler-design.md docs/plans/2026-09-29-queenagent-m342-dosya-basligi-testler-plan.md
git commit -m @'
test(queen-agent): Madde 342 red -- the open file's head is a framed back, Refresh and Copy above the name, with no Download

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
