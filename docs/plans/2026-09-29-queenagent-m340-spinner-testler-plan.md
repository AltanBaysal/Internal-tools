# Madde 340 — Yüklenirken spinner, önce dosya listesinde · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dosya listesi yüklenirken iskeletin yerine tasarımın spinner'ının döndüğünü tutan testler,
kırmızı.

**Architecture:** Üç test dosyası: yeni `Spinner.test.jsx` halkanın kendisini, `FileRail.test.jsx`
listenin yüklenişini, `workspace.css.test.js` tasarımın ölçülerini tutar. Halka
`data-testid="spinner"` ile bulunur.

**Tech Stack:** vitest + jsdom, Testing Library.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m340-spinner-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce.
- Bu turda `Spinner.jsx`, `FileRail.jsx` ve `workspace.css` yazılmaz; `Skeleton.jsx` ve testleri hiç
  değişmez.
- `dist` derlenmez. Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Spinner'ın, listenin ve ölçülerin testleri, kırmızı

**Files:**
- Create: `queen-agent/frontend/src/features/workspace/Spinner.test.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/FileRail.test.jsx` — *a rail still loading says neither* testinin yerine üç test
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css.test.js` — iskeletin iki testinin altına iki test

**Interfaces:**
- Produces: uygulama turunun karşılayacakları — `Spinner.jsx`'in varsayılan dışa aktarımı,
  `<span className="spinner" aria-hidden="true" data-testid="spinner" />` çizer; FileRail yüklenirken
  `.file-list` içinde `<div className="file-list__spinner">` ve içinde Spinner; `workspace.css`'te
  satır başında `.spinner {` ve `.file-list__spinner {` kuralları.

- [ ] **Step 1: `Spinner.test.jsx`'i yaz**

```jsx
import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import Spinner from "./Spinner.jsx";

// Madde 340, the design's items 173 and 181: one small turning ring. Every place that waits puts the
// same ring in a box of its own, so the ring is all this draws.
test("it is the design's ring", () => {
  render(<Spinner />);
  expect(screen.getByTestId("spinner").className).toBe("spinner");
});

test("the ring says nothing", () => {
  // The heading and the buttons standing around it already say what is loading.
  render(<Spinner />);
  const ring = screen.getByTestId("spinner");
  expect(ring.getAttribute("aria-hidden")).toBe("true");
  expect(ring.textContent).toBe("");
});
```

- [ ] **Step 2: `FileRail.test.jsx`'te yükleniş testini değiştir**

Bugünkü test:

```jsx
test("a rail still loading says neither", () => {
  render(<FileRail files={[]} loading />);
  expect(screen.queryByText(/No files yet/)).toBeNull();
  expect(screen.getByTestId("skeleton")).toBeTruthy();
});
```

yerine:

```jsx
// Madde 340: while the list loads, a small turning ring stands where the rows will be, instead of
// the shimmering blocks (the design's items 173 and 181).
test("a rail still loading says neither, and turns a spinner where the rows will be", () => {
  const { container } = render(<FileRail files={[]} loading />);
  expect(screen.queryByText(/No files yet/)).toBeNull();
  const spinner = screen.getByTestId("spinner");
  expect(spinner.parentElement.className).toBe("file-list__spinner");
  expect(container.querySelector(".file-list").contains(spinner)).toBe(true);
  expect(screen.queryByTestId("skeleton")).toBeNull();
});

test("while the spinner turns, the heading and Refresh stand where they are", () => {
  render(<FileRail files={[]} loading onRefresh={vi.fn()} />);
  expect(screen.getByTestId("spinner")).toBeTruthy();
  expect(screen.getByRole("button", { name: /Project files/ })).toBeTruthy();
  expect(screen.getByRole("button", { name: "Refresh" })).toBeTruthy();
});

test("once the list has come, the spinner is gone and the rows are there", () => {
  render(<FileRail files={FILES} />);
  expect(screen.getByText("outline.md")).toBeTruthy();
  expect(screen.queryByTestId("spinner")).toBeNull();
});
```

- [ ] **Step 3: `workspace.css.test.js`'e iki test ekle**, *the blocks blink at the design's speed* testinin altına:

```js
// Madde 340: the design's spinner (items 173, 181) is the live stamp's ring at twice the size, on
// the turn that ring already has, so no animation is invented for it.
test("the spinner is the live stamp's ring at 20px", () => {
  const ring = rule(".spinner");
  expect(ring).toContain("width: 20px");
  expect(ring).toContain("height: 20px");
  expect(ring).toContain("border: 1.5px solid var(--line)");
  expect(ring).toContain("border-top-color: var(--accent)");
  expect(ring).toContain("border-radius: 50%");
  expect(ring).toContain("animation: msg-spin 0.8s linear infinite");
});

test("in the file list the spinner stands centred where the rows will be", () => {
  const spot = rule(".file-list__spinner");
  expect(spot).toContain("display: flex");
  expect(spot).toContain("justify-content: center");
  expect(spot).toContain("padding: 24px 12px");
});
```

- [ ] **Step 4: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `npm test --prefix queen-agent/frontend` kırmızı — `Spinner.test.jsx` `./Spinner.jsx`'i
bulamadığı için yüklenemez; FileRail'in ilk iki yeni testi `spinner`'ı bulamaz; CSS'in iki testi
kuralı bulamaz. *Once the list has come* yeşil. `python -m pytest queen-editor -q` 377'nin bilinen iki
kırmızısı; öteki iki süit yeşil.

- [ ] **Step 5: Kırmızıyı commit'le**

```powershell
git add queen-agent/frontend/src/features/workspace/Spinner.test.jsx queen-agent/frontend/src/features/workspace/FileRail.test.jsx queen-agent/frontend/src/features/workspace/workspace.css.test.js docs/specs/2026-09-29-queenagent-m340-spinner-testler-design.md docs/plans/2026-09-29-queenagent-m340-spinner-testler-plan.md
git commit -m @'
test(queen-agent): Madde 340 red -- the file list turns the design's spinner while it loads, not the skeleton

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
