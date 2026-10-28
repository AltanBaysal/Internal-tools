# v13 Görev 1 — Galeri resim kuyruğu: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aynı anda en fazla iki karo resminin uçmasını ve her yolun slotu geri vermesini sınayan
testleri yazmak, ve takımı kırmızı commit'lemek.

**Architecture:** İki yeni dosya, iki ayrı sorumluluk. `image_queue.js` tavanın bütün kurallarını
tutar ve DOM bilmez — saf JavaScript olarak sınanır. `TileImage.jsx` yalnız protokolü uygular (sor,
verilince çiz, bitince bırak) ve kuyruğu sahtesiyle değiştirilerek sınanır. Bu döngüde ikisi de
yalnız imzalarıyla açılıyor.

**Tech Stack:** React 18, vitest, jsdom, @testing-library/react.

**Tasarım:** [test spec'i](../specs/2026-08-14-queen-editor-v13-gorev-1-testler-design.md)

## Global Constraints

- **Bu döngüde mantık yazılmıyor.** Yeni iki kaynak dosyası yalnız imzalarıyla açılır: dönüş tipi
  doğru, içi boş, tek bir kural/sayı/koşul yok. Var olan hiçbir dosya değişmiyor.
- `Gallery.jsx` bu döngüde **hiç** değişmiyor — `TileImage` yazılıyor ama kullanılmıyor.
- Test adları ve yorumlar **İngilizce**; kullanıcıya görünen metin yok.
- Commit mesajında **çift tırnak yok**.
- Komut: `npm test --prefix queen-editor/frontend`
- `dist/` **derlenmiyor** — çalışan ön yüz davranışı değişmedi.
- Commit **kırmızı gider**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `frontend/src/shared/image_queue.js` | tavan, sıra, slot iadesi — DOM bilmez | yaratılır (iskelet) |
| `frontend/src/shared/image_queue.test.js` | kuyruğun kuralları | yaratılır |
| `frontend/src/features/photo_generation/TileImage.jsx` | karonun kuyrukla konuşması | yaratılır (iskelet) |
| `frontend/src/features/photo_generation/TileImage.test.jsx` | protokol | yaratılır |

---

### Task 1: Kuyruk — iskelet ve kuralların testleri

**Files:**
- Create: `queen-editor/frontend/src/shared/image_queue.js`
- Create: `queen-editor/frontend/src/shared/image_queue.test.js`

**Interfaces:**
- Produces: `createQueue(limit)` → `{ ask(grant) }`; `ask` bir bilet döndürür: `{ done() }`.
  `grant` argümansız çağrılır. `done()` slotu bırakır, sırasını bekleyen bir bilette ise onu
  sıradan düşürür. `imageQueue` uygulamanın paylaştığı örnektir, tavanı 2.
  Task 2 ve implementasyon döngüsü bu isimlere dayanıyor.

- [ ] **Step 1: İskeleti yaz**

`queen-editor/frontend/src/shared/image_queue.js`:

```js
// Skeleton only -- the rules land in the implementation cycle. Signatures exist so the tests next
// door can run and fail on what they assert rather than on a missing import.
export function createQueue(limit) {
  return { ask: () => ({ done: () => {} }) };
}

export const imageQueue = createQueue(2);
```

- [ ] **Step 2: Kuralların testlerini yaz**

`queen-editor/frontend/src/shared/image_queue.test.js`:

```js
import { describe, expect, it } from "vitest";

import { createQueue, imageQueue } from "./image_queue.js";

// Every test reads one list: who was granted, in the order it happened. A queue that hands slots
// out in the wrong order or loses one shows up as a different list, not as a different count.
describe("image queue", () => {
  it("grants the first askers up to the limit", () => {
    const queue = createQueue(2);
    const granted = [];

    queue.ask(() => granted.push("a"));
    queue.ask(() => granted.push("b"));

    expect(granted).toEqual(["a", "b"]);
  });

  it("makes an asker past the limit wait", () => {
    const queue = createQueue(2);
    const granted = [];

    queue.ask(() => granted.push("a"));
    queue.ask(() => granted.push("b"));
    queue.ask(() => granted.push("c"));

    expect(granted).toEqual(["a", "b"]);
  });

  it("hands a freed slot to the asker that has waited longest", () => {
    const queue = createQueue(2);
    const granted = [];
    const first = queue.ask(() => granted.push("a"));
    queue.ask(() => granted.push("b"));
    queue.ask(() => granted.push("c"));
    queue.ask(() => granted.push("d"));

    first.done();

    // c asked before d, so the slot is c's. Without an order, a gallery that is scrolled through
    // leaves its oldest waiters at the back for as long as new ones keep arriving.
    expect(granted).toEqual(["a", "b", "c"]);
  });

  it("skips an asker that gave up and grants the one behind it", () => {
    const queue = createQueue(2);
    const granted = [];
    const first = queue.ask(() => granted.push("a"));
    queue.ask(() => granted.push("b"));
    const leaving = queue.ask(() => granted.push("c"));
    queue.ask(() => granted.push("d"));

    leaving.done();
    first.done();

    // Two things at once: the one that left is never drawn, and its place does not swallow the
    // slot. Only the second half says the queue goes on -- one tile scrolled past must not stall
    // every tile behind it.
    expect(granted).toEqual(["a", "b", "d"]);
  });

  it("frees one slot however many times done is called", () => {
    const queue = createQueue(2);
    const granted = [];
    const first = queue.ask(() => granted.push("a"));
    queue.ask(() => granted.push("b"));
    queue.ask(() => granted.push("c"));
    queue.ask(() => granted.push("d"));

    first.done();
    first.done();

    // A tile that loads and is then taken off the screen releases twice. The second release must
    // not hand out a slot the queue never got back.
    expect(granted).toEqual(["a", "b", "c"]);
  });

  it("keeps a freed slot for the next asker when no one is waiting", () => {
    const queue = createQueue(1);
    const granted = [];
    const first = queue.ask(() => granted.push("a"));

    first.done();
    queue.ask(() => granted.push("b"));

    expect(granted).toEqual(["a", "b"]);
  });

  it("shares one queue of two slots for the gallery", () => {
    const granted = [];

    imageQueue.ask(() => granted.push("a"));
    imageQueue.ask(() => granted.push("b"));
    imageQueue.ask(() => granted.push("c"));

    // The number the whole task exists for. Tested on the shared instance because that is the one
    // the gallery uses -- createQueue could be right while the app shipped a different ceiling.
    // Nothing is released here on purpose: this test is last, and no other test reads this queue.
    expect(granted).toEqual(["a", "b"]);
  });
});
```

- [ ] **Step 3: Yalnız bu dosyayı koştur**

Run: `npm test --prefix queen-editor/frontend -- image_queue`
Expected: 7 test, 7'si de düşüyor. Hepsi aynı sebeple: `ask` hiçbir `grant`'i çağırmıyor, dolayısıyla
`granted` her testte `[]` kalıyor.

---

### Task 2: Karo — iskelet ve protokolün testleri

**Files:**
- Create: `queen-editor/frontend/src/features/photo_generation/TileImage.jsx`
- Create: `queen-editor/frontend/src/features/photo_generation/TileImage.test.jsx`

**Interfaces:**
- Consumes: Task 1'in `imageQueue`'su (`ask(grant)` → `{ done() }`), ve `shared/api.js`'ten
  `fileUrl(project, file)`.
- Produces: `TileImage({ project, file, ...rest })` — bir `<img>` çizer, `alt` dosya adıdır, kalan
  öznitelikler olduğu gibi geçer. `Gallery.jsx` implementasyon döngüsünde bunu kullanacak.

- [ ] **Step 1: İskeleti yaz**

`queen-editor/frontend/src/features/photo_generation/TileImage.jsx`:

```jsx
// Skeleton only -- asking the queue, drawing on a grant and releasing land in the implementation
// cycle. The signature exists so the tests next door run and fail on their assertions.
export function TileImage({ project, file, ...rest }) {
  return <img alt={file} {...rest} />;
}
```

- [ ] **Step 2: Protokolün testlerini yaz**

`queen-editor/frontend/src/features/photo_generation/TileImage.test.jsx`:

```jsx
import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { fileUrl } from "../../shared/api.js";
import { TileImage } from "./TileImage.jsx";

// The queue's own rules are tested next door. What is tested here is the protocol -- ask, draw
// when granted, release when finished -- so the queue is a fake the test holds the grant of.
// vi.hoisted because vi.mock is lifted above the imports and cannot see an ordinary const.
const queue = vi.hoisted(() => {
  const waiting = [];
  return {
    waiting,
    ask(grant) {
      const ticket = { grant, released: 0, done: () => { ticket.released += 1; } };
      waiting.push(ticket);
      return ticket;
    },
    forget: () => { waiting.length = 0; },
  };
});

vi.mock("../../shared/image_queue.js", () => ({ imageQueue: queue }));

// jsdom has no layout and therefore no IntersectionObserver; the test supplies one and drives it
// by hand, the same way this suite supplies a clipboard and a video duration.
function stubObserver() {
  const made = [];
  vi.stubGlobal("IntersectionObserver", class {
    constructor(callback) { this.callback = callback; made.push(this); }
    observe() {}
    disconnect() {}
  });
  // Optional call for the same reason as grant below: a component that never observes leaves this
  // empty, and a helper that throws would hide the assertion the test is actually about.
  const fire = (isIntersecting) =>
    act(() => made[made.length - 1]?.callback([{ isIntersecting }]));
  return { near: () => fire(true), away: () => fire(false) };
}

const picture = () => screen.getByRole("img");
const sourceOf = () => picture().getAttribute("src");
// Optional call on purpose: while the skeleton never asks, this helper must leave the assertion to
// do the failing rather than throw on an empty queue.
const grant = () => act(() => queue.waiting[0]?.grant());
const releases = () => queue.waiting.map((ticket) => ticket.released);

beforeEach(() => queue.forget());
afterEach(() => vi.unstubAllGlobals());

describe("TileImage", () => {
  it("draws no picture before the tile comes near", () => {
    stubObserver();

    render(<TileImage project="düğün" file="1_a.png" />);

    expect(sourceOf()).toBeNull();
  });

  it("asks for the picture once the tile comes near", () => {
    const view = stubObserver();
    render(<TileImage project="düğün" file="1_a.png" />);

    view.near();

    expect(queue.waiting).toHaveLength(1);
  });

  it("draws no picture until the queue grants a slot", () => {
    const view = stubObserver();
    render(<TileImage project="düğün" file="1_a.png" />);

    view.near();

    // The ceiling is only a ceiling if being in the queue is not enough to be drawn.
    expect(sourceOf()).toBeNull();
  });

  it("draws the picture once the queue grants a slot", () => {
    const view = stubObserver();
    render(<TileImage project="düğün" file="1_a.png" />);
    view.near();

    grant();

    expect(sourceOf()).toBe(fileUrl("düğün", "1_a.png"));
  });

  it("frees its slot once the picture has loaded", () => {
    const view = stubObserver();
    render(<TileImage project="düğün" file="1_a.png" />);
    view.near();
    grant();

    fireEvent.load(picture());

    expect(releases()).toEqual([1]);
  });

  it("frees its slot when the picture fails", () => {
    const view = stubObserver();
    render(<TileImage project="düğün" file="1_a.png" />);
    view.near();
    grant();

    fireEvent.error(picture());

    // A file that cannot be drawn must not hold a slot: one broken photo would otherwise take a
    // permanent bite out of a ceiling of two.
    expect(releases()).toEqual([1]);
  });

  it("frees its slot when the tile leaves before its turn", () => {
    const view = stubObserver();
    render(<TileImage project="düğün" file="1_a.png" />);
    view.near();

    view.away();

    // Scrolled past while still waiting: it drops out of the queue, so what is on screen is not
    // stuck behind what no longer is.
    expect(releases()).toEqual([1]);
  });

  it("frees its slot when the tile is taken off the screen", () => {
    const view = stubObserver();
    const { unmount } = render(<TileImage project="düğün" file="1_a.png" />);
    view.near();
    grant();

    unmount();

    expect(releases()).toEqual([1]);
  });

  it("draws the picture at once when the browser has no observer", () => {
    // Without this the gallery does not degrade, it dies: calling new on an absent constructor
    // throws where it stands. jsdom is one such browser, which is what keeps Gallery.test.jsx up.
    vi.stubGlobal("IntersectionObserver", undefined);

    render(<TileImage project="düğün" file="1_a.png" />);
    grant();

    expect(sourceOf()).toBe(fileUrl("düğün", "1_a.png"));
  });
});
```

- [ ] **Step 3: Yalnız bu dosyayı koştur**

Run: `npm test --prefix queen-editor/frontend -- TileImage`
Expected: 9 test, 7'si düşüyor. Geçen ikisi `draws no picture before the tile comes near` ve
`draws no picture until the queue grants a slot` — iskelet zaten hiç `src` yazmıyor.

- [ ] **Step 4: Bütün takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: 14 düşen test (7 kuyruk + 7 karo). Geri kalan takım — `Gallery.test.jsx` dahil — yeşil:
var olan hiçbir dosyaya dokunulmadı.

---

### Task 3: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): ask how many tile pictures may fly at once

Red on purpose -- the implementation cycle turns these green.

The gallery has never limited how many tile pictures are in flight, so the
poll's request waits behind them and the ten second abort fires. There was no
test to miss it: with nothing deciding, there was no behaviour to ask about.
These tests put the question in writing first.

Two files open with their signatures only, no rule inside either, so every test
runs and fails on its assertion rather than on a missing import.

Seven queue tests fail because ask grants nobody. Seven tile tests fail because
the tile neither asks nor releases. Two tile tests pass today for the wrong
reason -- a skeleton that draws nothing satisfies both -- and become guards once
the rest go green: they are what stops draw always from passing.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in 16 testinin 16'sı planda kodlu. 1-7 → Task 1 Step 2; 8-16 → Task 2
Step 2. Spec'in "iskelet" bölümü → Task 1 Step 1 ve Task 2 Step 1. "Gallery.jsx bu döngüde
değişmiyor" → Global Constraints ve Task 2 Step 4'ün beklentisi.

**Tip tutarlılığı:** `ask(grant)` → `{ done() }` her yerde aynı. Sahte kuyruk aynı şekli taşıyor
(`ask` bir bilet döndürüyor, biletin `done`'u sayıyor), yani `TileImage` gerçek kuyrukla da aynı
protokolü konuşuyor. `imageQueue` adı iskelette, sahtede ve `vi.mock` yolunda aynı.

**Kontrol edilen tuzak:** `vi.mock`'un fabrikası import'ların üstüne kaldırılıyor, dolayısıyla sıradan
bir `const queue` fabrikanın içinden görünmez ve test "Cannot access before initialization" ile
patlar. `vi.hoisted` tam olarak bunun için.

**Kontrol edilen tuzak 2:** `grant()` yardımcısı `?.` kullanıyor. İskelet hiç sormadığından kuyruk
boş; `?.` olmasa test bir `TypeError` ile düşerdi ve kırmızı "iddia yanlış" değil "yardımcı patladı"
demek olurdu — bu döngünün bütün amacı iddianın kendisini görmek.

**Kontrol edilen tuzak 3:** `imageQueue` modül durumu taşıyor ve `shares one queue of two slots`
onu doldurup bırakıyor. Bu yüzden dosyanın **son** testi, ve başka hiçbir test paylaşılan örneğe
bakmıyor — `TileImage.test.jsx` modülü zaten tümüyle sahtesiyle değiştiriyor.

**Kontrol edilen kapsam:** `Gallery.test.jsx`, `fileUrl`'ü mock'luyor ve hiçbir yerde `img src`'ye
bakmıyor; `Tile` yerel bir bileşen ve `children` alıyor. Bu döngüde ona dokunulmuyor, dolayısıyla
yeşil kalması bekleniyor — ve implementasyon döngüsünde de kırılmaması bekleniyor.
