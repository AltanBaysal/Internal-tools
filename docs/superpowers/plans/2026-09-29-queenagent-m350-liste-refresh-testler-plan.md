# Madde 350 — Dosya listesinde yazılı Refresh, başlığın satırında · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Listenin `Refresh`'inin yazılı, çerçeveli ve başlığın satırında durduğunu, kutunun ilk
dosyayla başladığını tutan testler, kırmızı.

**Architecture:** Üç test dosyası: `FileRail.test.jsx` satırı ve kutuyu, `ProjectScreen.test.jsx`
proje ekranının düğmesini, `workspace.css.test.js` tasarımın satır kurallarını tutar.

**Tech Stack:** vitest + jsdom, Testing Library.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m350-liste-refresh-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce.
- Bu turda `FileRail.jsx`, `ProjectScreen.jsx` ve `workspace.css` yazılmaz.
- `dist` derlenmez. Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Satırın, kutunun ve kuralların testleri, kırmızı

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/FileRail.test.jsx` — *folded, there is no Refresh either* testinin altına dört test; `within` içe aktarılır
- Modify: `queen-agent/frontend/src/features/workspace/ProjectScreen.test.jsx` — *with the panel open the Refresh travels into it* testinin altına bir test
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css.test.js` — *no rule takes the ghost's frame off Refresh or Copy* testinin altına üç test

**Interfaces:**
- Produces: uygulama turunun karşılayacakları — FileRail açıkken `<aside>`'ın içinde
  `<div className="rail__bar">`, içinde önce `rail__head`, sonra
  `<button className="ghost file-list__refresh">Refresh</button>`; `.file-list`'in ilk çocuğu ilk
  `FileRow` ya da yüklenirken `file-list__spinner`; proje ekranının `Refresh`'i de yazılı ve `ghost`;
  `workspace.css`'te satır başında `.rail__bar {` kuralı, `.rail__head {`'de `flex: 1`.

- [ ] **Step 1: `FileRail.test.jsx`**

İçe aktarma: `import { fireEvent, render, screen, within } from "@testing-library/react";`

*folded, there is no Refresh either* testinin altına:

```jsx
// Madde 350 (the design's items 154 and 175): Refresh is a written, framed button, like the reader's,
// and it stands on the heading's row to the right of PROJECT FILES 5 ›. The list's box starts with
// what it holds.
test("Refresh stands on the heading's row, to the right of the heading", () => {
  render(<FileRail files={FILES} onRefresh={vi.fn()} />);
  const head = screen.getByRole("button", { name: /Project files/ });
  const refresh = screen.getByRole("button", { name: "Refresh" });
  expect(refresh.parentElement.className).toBe("rail__bar");
  expect(head.nextElementSibling).toBe(refresh);
});

test("Refresh is a word in a frame, as the reader's is", () => {
  render(<FileRail files={FILES} onRefresh={vi.fn()} />);
  const refresh = screen.getByRole("button", { name: "Refresh" });
  expect(refresh.textContent).toBe("Refresh");
  expect(refresh.classList.contains("ghost")).toBe(true);
});

test("the list's box starts with the first file", () => {
  const { container } = render(<FileRail files={FILES} onRefresh={vi.fn()} />);
  const box = container.querySelector(".file-list");
  expect(box.firstElementChild.textContent).toContain("outline.md");
  expect(within(box).queryByRole("button", { name: "Refresh" })).toBeNull();
});

test("while the list loads, the box starts with the spinner", () => {
  const { container } = render(<FileRail files={[]} loading onRefresh={vi.fn()} />);
  expect(container.querySelector(".file-list").firstElementChild.className).toBe(
    "file-list__spinner",
  );
});
```

- [ ] **Step 2: `ProjectScreen.test.jsx`**, *with the panel open the Refresh travels into it*'in altına:

```jsx
test("the file column's Refresh is written and framed, as the rail's is", () => {
  // Madde 350: the two screens share one button, and this screen goes in v9-2n, so it follows the
  // rail rather than keeping a ↻ of its own.
  const files = [{ name: "outline.md", ext: "md", modifiedAt: new Date().toISOString() }];
  render(<ProjectScreen project={PROJECT} files={files} onRefresh={vi.fn()} />);
  const refresh = screen.getByRole("button", { name: "Refresh" });
  expect(refresh.textContent).toBe("Refresh");
  expect(refresh.classList.contains("ghost")).toBe(true);
});
```

- [ ] **Step 3: `workspace.css.test.js`**, *no rule takes the ghost's frame off Refresh or Copy*'nin altına:

```js
// Madde 350 (the design's item 175): the heading and Refresh share one row, and the 12 under the
// heading is the row's now.
test("the heading's row lays the heading and Refresh side by side", () => {
  const row = rule(".rail__bar");
  expect(row).toContain("display: flex");
  expect(row).toContain("align-items: center");
  expect(row).toContain("margin-bottom: 12px");
});

test("the heading takes what Refresh leaves of the row", () => {
  const head = rule(".rail__head");
  expect(head).toContain("flex: 1");
  expect(head).not.toContain("width: 100%");
  expect(head).not.toContain("margin-bottom");
  expect(rule(".rail__head--still")).not.toContain("margin-bottom");
});

test("no rule takes the ghost's frame off the list's Refresh", () => {
  for (const { selectors, body } of rulesSelecting([".file-list__refresh"])) {
    expect(body).not.toContain("border: none");
    expect(body).not.toContain("background: transparent");
    expect(selectors).not.toContain(".file-list__refresh:hover");
  }
});
```

- [ ] **Step 4: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `npm test --prefix queen-agent/frontend` kırmızı — FileRail'in dört yeni testi (düğme
`file-list__bar`'da, `↻` yazılı, `ghost` yok, kutunun ilk çocuğu `file-list__bar`), proje ekranının
yenisi, CSS'in üçü (`.rail__bar` yok; `.rail__head`'de `width: 100%` ve `margin-bottom`;
`.file-list__refresh`'te `border: none`). Öteki üç süit yeşil.

- [ ] **Step 5: Kırmızıyı commit'le**

```powershell
git add queen-agent/frontend/src/features/workspace/FileRail.test.jsx queen-agent/frontend/src/features/workspace/ProjectScreen.test.jsx queen-agent/frontend/src/features/workspace/workspace.css.test.js docs/superpowers/specs/2026-09-29-queenagent-m350-liste-refresh-testler-design.md docs/superpowers/plans/2026-09-29-queenagent-m350-liste-refresh-testler-plan.md
git commit -m @'
test(queen-agent): Madde 350 red -- the file list's Refresh is a written ghost on the heading's row, and the box starts with the first file

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
