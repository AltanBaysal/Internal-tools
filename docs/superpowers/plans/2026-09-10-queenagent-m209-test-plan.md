# Madde 209 · Tur 1 (testler) — Plan

**Tasarım:** [2026-09-10-queenagent-m209-surum-testler-design.md](../specs/2026-09-10-queenagent-m209-surum-testler-design.md)
**Kaynak:** [yol haritasının Madde 209'u](2026-09-06-queenagent-v8-roadmap.md).

**Bu turda kaynak kod yazılmaz.** Dört test kırmızıya döner.

**Komutlar** *(sabit satırlar, kuyruk eklenmez)*:

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Yürüten:** bu oturum, tek başına.

---

## Bağlayıcı kurallar

- **Değer test edilmez, biçim edilir.** `VERSION === "V8"` bir kararı iki yere yazar; koşu
  başlarken ikisini birden değiştirmek gerekir ve biri unutulunca süit kendini korur.
- **Ekrandaki iddia sabitle kurulur** — `getByText(VERSION)` — ki V9 geldiğinde test değişmesin.
- **`dist` bu turda derlenmez:** ön uç **kaynağı** değişmiyor, yalnız testler.
- Commit mesajında çift tırnak yok; amend yok.

## Değişen dosyalar

| Dosya | Ne oluyor |
|---|---|
| `queen-agent/frontend/src/shared/version.test.js` | yeni — sabitin biçimi |
| `queen-agent/frontend/src/features/workspace/Sidebar.test.jsx` | iki test doğar |
| `queen-agent/frontend/src/features/workspace/workspace.css.test.js` | bir test doğar |

**Kırmızının sebebi:** `shared/version.js` henüz yok, yani onu içeri alan üç dosya **çözümlenmeden**
kırmızı verir; CSS testi de olmayan bir kuralı arar.

---

## Görev 1 · Sabitin biçimi

**Dosya:** `queen-agent/frontend/src/shared/version.test.js` *(yeni)*

- [ ] **1.1**

```js
import { expect, test } from "vitest";

import { VERSION } from "./version.js";

test("the version reads as a run number", () => {
  // The value itself is a decision, not a behaviour: it is written by hand when a run opens and by
  // nothing else, so pinning "V8" here would put one decision in two places and let the suite pass
  // on the day only one of them moved. What is held is the shape the madde asked for -- the run
  // number, in capitals -- so v8, 8, V8.1 and V8-beta are all caught.
  expect(VERSION).toMatch(/^V\d+$/);
});
```

---

## Görev 2 · Çubuk sürümü gösterir

**Dosya:** `queen-agent/frontend/src/features/workspace/Sidebar.test.jsx`

- [ ] **2.1 — içeri alma**

Dosyanın başındaki `import Sidebar from "./Sidebar.jsx";` satırının altına:

```js
import { VERSION } from "../../shared/version.js";
```

- [ ] **2.2 — marka bloğunda çiziliyor**

`test("there is no logo mark beside the wordmark", ...)`'ın hemen altına:

```jsx
test("the sidebar says which run this is", () => {
  // We jump from run to run -- V6, V7, V8 -- and nothing on screen said which one was running.
  // Asked of the constant rather than of "V8": the value moves when a run opens, and this claim is
  // that it reaches the screen, not what it says.
  const { container } = render(<Sidebar projects={PROJECTS} activeProjectId="p1" />);
  expect(screen.getByText(VERSION)).toBeTruthy();
  expect(container.querySelector(".sidebar__brand").textContent).toContain(VERSION);
});
```

- [ ] **2.3 — katlanınca gidiyor**

`test("folded, nothing is left but the way back", ...)`'ın hemen altına:

```jsx
test("folded, the version folds with the name", () => {
  // It opens no room of its own: folded, the sidebar is the button that brings it back and nothing
  // else. True today because the collapsed branch returns early -- and written down so that moving
  // the brand block into that branch cannot quietly bring the version along.
  render(<Sidebar projects={PROJECTS} activeProjectId="p1" collapsed onToggle={vi.fn()} />);
  expect(screen.queryByText(VERSION)).toBeNull();
});
```

---

## Görev 3 · Ad ile sürüm alt alta

**Dosya:** `queen-agent/frontend/src/features/workspace/workspace.css.test.js`

Bu dosya `rule(selector)` ile bir kuralın gövdesini okuyor; `test("the sidebar's menu is the
design's own width", ...)`'ın altına:

- [ ] **3.1**

```js
test("the version sits under the name and reads as a note", () => {
  // The madde puts it under the wordmark, and the brand block is a row -- so the name and the
  // version need a column of their own or the version lands beside the name instead.
  expect(rule(".sidebar__name")).toContain("flex-direction: column");
  // The repo's note voice, the same variable the stamp and a call's head use: it is the wordmark's
  // footnote, not a second name.
  const version = rule(".sidebar__version");
  expect(version).toContain("color: var(--muted)");
  expect(version).toContain("font-size: 11px");
});
```

---

## Görev 4 · Süit ve kırmızı commit

- [ ] **4.1 — ön uç:** `npm test --prefix queen-agent/frontend`

Beklenen: **dört kırmızı** — 1.1, 2.2, 2.3, 3.1. İlk üçü `version.js` çözümlenmediği için, ve
`Sidebar.test.jsx`'in **tamamı** o içeri alma yüzünden düşerse sayı bu dosyanın bütün testleri
kadar olur; o hâlde de kırmızının sebebi tektir ve uygulama turu ikisini birden yeşile çevirir.

- [ ] **4.2 — arka uç:** `python -m pytest queen-agent -q` → 923 yeşil, dokunulmadı.

- [ ] **4.3 — commit.**

```
test(m209): red asks the sidebar which run this is
```

---

## Kendi kontrolü

- **Spec'in dört iddiası bir göreve düşüyor mu?** 1 → Görev 1; 2 ve 3 → Görev 2; 4 → Görev 3.
- **Yer tutucu var mı?** Yok.
- **Ad tutarlılığı:** `VERSION`, `.sidebar__name`, `.sidebar__version`, `.sidebar__brand` — ilk üçü
  uygulama turunun yazacağı adlar, sonuncusu bugün var. `PROJECTS`, `render`, `screen`, `vi`,
  `rule` — hepsi ilgili dosyada zaten kurulu.
- **`dist` gerekiyor mu?** Hayır: bu tur kaynağa dokunmuyor. Uygulama turunda gerekecek.
