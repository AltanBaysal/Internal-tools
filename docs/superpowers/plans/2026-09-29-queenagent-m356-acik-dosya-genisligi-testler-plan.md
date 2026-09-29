# Madde 356 — Açık dosya da çekilerek genişler · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Listeyle açık dosyanın tek genişlik olduğunu, açık dosyanın kenarının da çekildiğini ve
tutma yerinin okuyucunun üstünde durduğunu tutan testler, kırmızı.

**Architecture:** Üç test dosyası: `FileRail.test.jsx` panelin okurken genişliğini, tutma yerini ve
sınıfını; `App.test.jsx` genişliğin liste ile dosya arasında geçmesini; `workspace.css.test.js`
`.rail--open`'ın kendi genişliği olmadığını ve tutma yerinin `z-index`'ini tutar.

**Tech Stack:** vitest + jsdom, Testing Library.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m356-acik-dosya-genisligi-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce.
- Bu turda `FileRail.jsx`, `railWidth.js` ve `workspace.css` yazılmaz.
- Tersini söyleyen iki test silinir, susturulmaz.
- `dist` derlenmez. Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Tek genişliğin testleri, kırmızı

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/FileRail.test.jsx` — *a rail showing a document has no grip* silinir, yerine beş test
- Modify: `queen-agent/frontend/src/App.test.jsx` — *dragging it past its minimum folds it instead of leaving a sliver*'ın altına üç test
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css.test.js` — *while reading, the rail is the document at the design's widest* yerine bir test; *the grip is on the rail's left edge…*'in altına bir test; Madde 63 başlık yorumu düzelir
- Modify: `queen-agent/frontend/src/features/workspace/railWidth.test.js` — yalnız 12–13. satırın yorumu

**Interfaces:**
- Produces: uygulama turunun karşılayacakları — `FileRail` okurken (`reading.name`) `width`
  verildiyse, katlı olsun olmasın, `style.width` `${width}px`; `onResize` verildiyse okurken de
  `role="separator"` tutma yeri, listeninkiyle aynı hesap (`width + (başlangıç x - şimdiki x)`);
  çekerken sınıf `rail rail--open rail--dragging`, bırakınca `rail rail--open`.
  `workspace.css`'te `.rail--open {`'da `width:` yok, `display: flex` var; `.rail__grip {`'te
  `z-index: 1`.

- [ ] **Step 1: `FileRail.test.jsx`** — *a rail showing a document has no grip* testinin yerine:

```jsx
// Madde 356 (the design's items 158 and 177): the list and the open file are one width. A file opens
// at the width the list was left at, its own edge is pulled the same way, and the width it is pulled
// to is the list's once it closes.
const READING = {
  name: "outline.md",
  file: { name: "outline.md", text: "body", modifiedAt: NOW_ISO },
};

test("while reading, the rail is drawn at the width it is handed", () => {
  render(<FileRail files={FILES} width={420} reading={READING} />);
  expect(screen.getByTestId("file-rail").style.width).toBe("420px");
});

test("while reading, the held width stands even if the list is folded", () => {
  // Pulled under 220 while reading, the rail folds -- but the fold only shows once the file closes.
  render(<FileRail files={FILES} collapsed width={420} reading={READING} />);
  expect(screen.getByTestId("file-rail").style.width).toBe("420px");
});

test("a rail showing a document carries the grip too", () => {
  render(<FileRail files={FILES} width={320} onResize={vi.fn()} reading={READING} />);
  expect(screen.getByRole("separator")).toBeTruthy();
});

test("pulling the reader's grip leftwards asks for a wider rail, as the list's does", () => {
  const onResize = vi.fn();
  render(<FileRail files={FILES} width={320} onResize={onResize} reading={READING} />);
  fireEvent.mouseDown(screen.getByRole("separator"), { clientX: 500 });
  fireEvent.mouseMove(window, { clientX: 420 });
  expect(onResize).toHaveBeenCalledWith(400);
});

test("while the reader's edge is being pulled the rail says so", () => {
  // The design's own rule: a rail following the pointer arrives with it, so the easing is off.
  render(<FileRail files={FILES} width={320} onResize={vi.fn()} reading={READING} />);
  const rail = screen.getByTestId("file-rail");
  fireEvent.mouseDown(screen.getByRole("separator"), { clientX: 500 });
  expect(rail.className).toBe("rail rail--open rail--dragging");
  fireEvent.mouseUp(window);
  expect(rail.className).toBe("rail rail--open");
});
```

- [ ] **Step 2: `App.test.jsx`** — *dragging it past its minimum folds it instead of leaving a
  sliver*'ın altına:

```jsx
// Madde 356 (the design's items 158 and 177): the list and the open file are one width, held in App.
test("a file opens at the width the list was dragged to", async () => {
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());

  fireEvent.mouseDown(screen.getByRole("separator"), { clientX: 600 });
  fireEvent.mouseMove(window, { clientX: 520 });
  fireEvent.mouseUp(window);
  fireEvent.click(screen.getByText("plan.md"));
  await waitFor(() => expect(screen.getByText("body")).toBeTruthy());
  const rail = screen.getByTestId("file-rail");
  expect(rail.className).toContain("rail--open");
  expect(rail.style.width).toBe("400px");
});

test("the open file's edge is pulled too, and the list keeps that width once it closes", async () => {
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
  fireEvent.click(screen.getByText("plan.md"));
  await waitFor(() => expect(screen.getByText("body")).toBeTruthy());

  fireEvent.mouseDown(screen.getByRole("separator"), { clientX: 600 });
  fireEvent.mouseMove(window, { clientX: 520 });
  fireEvent.mouseUp(window);
  await waitFor(() => expect(screen.getByTestId("file-rail").style.width).toBe("400px"));

  fireEvent.click(screen.getByRole("button", { name: "←" }));
  await waitFor(() => expect(screen.getByText("Project files")).toBeTruthy());
  expect(screen.getByTestId("file-rail").style.width).toBe("400px");
});

test("pulled past its minimum while reading, the file stays and the fold shows once it closes", async () => {
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByText("plan.md")).toBeTruthy());
  fireEvent.click(screen.getByText("plan.md"));
  await waitFor(() => expect(screen.getByText("body")).toBeTruthy());

  // 320 - 200 is under the 220 the rail needs: the rail folds, but what is being read stays.
  fireEvent.mouseDown(screen.getByRole("separator"), { clientX: 400 });
  fireEvent.mouseMove(window, { clientX: 600 });
  fireEvent.mouseUp(window);
  expect(screen.getByText("body")).toBeTruthy();
  expect(screen.getByTestId("file-rail").style.width).toBe("320px");

  fireEvent.click(screen.getByRole("button", { name: "←" }));
  await waitFor(() =>
    expect(screen.getByTestId("file-rail").className).toContain("rail--collapsed"),
  );
});
```

- [ ] **Step 3: `workspace.css.test.js`**

Madde 63'ün başlık yorumu: `// Madde 63: reading empties the rail rather than splitting it.`
(`The document takes all 560.` düşer.)

*while reading, the rail is the document at the design's widest*'in yerine:

```js
test("while reading, the rail has no width of its own", () => {
  // Madde 356 (the design's item 158): the list and the open file are one width. The app writes it
  // inline, and until anything is dragged .rail's 320 holds for both.
  expect(rule(".rail--open")).not.toMatch(/[\s;{]width:/);
  // Still flex with one child: the reader claims the space with flex: 1 rather than a width.
  expect(rule(".rail--open")).toContain("display: flex");
});
```

*the grip is on the rail's left edge and says it can be pulled*'in altına:

```js
test("the grip stands above the reader", () => {
  // Madde 356 (the design's item 177): the reader's fadeIn lifts it into the grip's paint layer, and
  // as the later sibling it would cover the grip, so the pointer never reached the edge.
  expect(rule(".rail__grip")).toContain("z-index: 1");
});
```

- [ ] **Step 4: `railWidth.test.js`**, 12–13. satırın yorumu:

```js
  // 560 is the widest the rail goes, list and open file alike: they are one width (Madde 356).
```

- [ ] **Step 5: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `npm test --prefix queen-agent/frontend` kırmızı — FileRail'in beşi (okurken `style.width`
boş, okurken `separator` yok), App'in üçü (açık dosyada `style.width` boş; okurken `separator` yok),
CSS'in ikisi (`.rail--open`'da `width: 560px`; `.rail__grip`'te `z-index` yok). Öteki üç süit yeşil.

- [ ] **Step 6: Kırmızıyı commit'le**

```powershell
git add queen-agent/frontend/src/features/workspace/FileRail.test.jsx queen-agent/frontend/src/App.test.jsx queen-agent/frontend/src/features/workspace/workspace.css.test.js queen-agent/frontend/src/features/workspace/railWidth.test.js docs/superpowers/specs/2026-09-29-queenagent-m356-acik-dosya-genisligi-testler-design.md docs/superpowers/plans/2026-09-29-queenagent-m356-acik-dosya-genisligi-testler-plan.md
git commit -m @'
test(queen-agent): Madde 356 red -- the open file is the list's width, and its edge is pulled too

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
