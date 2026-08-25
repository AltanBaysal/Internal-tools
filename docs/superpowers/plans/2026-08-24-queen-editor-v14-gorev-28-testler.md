# v14 Görev 28 — Galerinin indirme sırası: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Üç test dosyasını maddenin sözleşmesine çevirmek. Yedi test kırmızı kalır; kod bu döngüde
değişmez.

**Architecture:** Kuyruğun paylaşılan tavanı bir sayı. Karonun protokolü — sıraya gir, izin gelince
çiz, bitince bırak — kendi dosyasında, kuyruk taklitle. Galerinin karoları hangi sırada kurduğu ise
yalnız galeride görülebiliyor, o yüzden oraya tek test giriyor ve o dosya da kuyruğu taklit etmeye
başlıyor.

**Tech Stack:** Vitest, @testing-library/react, jsdom.

**Spec:** [v14 Görev 28 test spec'i](../specs/2026-08-24-queen-editor-v14-gorev-28-testler-design.md)

## Global Constraints

- **Kod değişmiyor.** `TileImage.jsx`, `image_queue.js`, `Gallery.jsx` bu commit'te olduğu gibi
  kalır. Değişen yalnız `*.test.*` dosyaları.
- **Kırmızı bırakılır.** `skip`/`xfail` yok; testler düpedüz düşer ve commit mesajı bunu söyler.
- **`dist` derlenmiyor** — kaynak değişmediği için derlenecek bir şey yok.
- Dil: test adları ve yorumlar **İngilizce**; commit mesajı **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- Test komutu (depo kökünden, `cd` yok): `npm test --prefix queen-editor/frontend`
- Süre sabiti **30000 ms**. Testler bu sayıyı doğrudan yazar; koddan okumaz.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/frontend/src/shared/image_queue.test.js` | kuyruğun kuralları ve paylaşılan tavanı | tek testin sayısı ve adı |
| `queen-editor/frontend/src/features/photo_generation/TileImage.test.jsx` | karonun protokolü ve ne gösterdiği | baştan yazılır |
| `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx` | galerinin bütünü | kuyruk taklidi + tek test |

Üç ayrı görev, çünkü üçü ayrı ayrı reddedilebilir: tavan sayısı, karonun sözleşmesi, galerinin
sırası.

---

### Task 1: Paylaşılan kuyruğun tavanı 1 olur

**Files:**
- Test: `queen-editor/frontend/src/shared/image_queue.test.js`

**Interfaces:**
- Consumes: `imageQueue` — modülün paylaşılan tekili.
- Produces: implementasyon döngüsünün uyacağı sayı — `GALLERY_SLOTS = 1`.

- [ ] **Step 1: Dosyanın son testini değiştir**

Bugünkü hâli:

```js
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
```

Yerine:

```js
  it("shares one queue of a single slot for the gallery", () => {
    const granted = [];

    imageQueue.ask(() => granted.push("a"));
    imageQueue.ask(() => granted.push("b"));
    imageQueue.ask(() => granted.push("c"));

    // One at a time: the picture downloads, and only when it is in does the next request leave.
    // Tested on the shared instance because that is the one the gallery uses -- createQueue could
    // be right while the app shipped a different ceiling. Nothing is released here on purpose:
    // this test is last, and no other test reads this queue.
    expect(granted).toEqual(["a"]);
  });
```

`createQueue`'nun kendi testlerine **dokunulmuyor** — kendi tavanlarını veriyorlar, ve FIFO, atlama
ile "bir bilet bir slot" kuralları değişmiyor.

- [ ] **Step 2: Yalnız bu testin düştüğünü gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: `image_queue.test.js` içinde **1 failed** — *shares one queue of a single slot for the
gallery*, `["a","b"]` alıp `["a"]` beklediği için. Aynı dosyanın diğer altı testi yeşil.

---

### Task 2: Karonun sözleşmesi baştan yazılır

**Files:**
- Test: `queen-editor/frontend/src/features/photo_generation/TileImage.test.jsx`

**Interfaces:**
- Consumes: `TileImage({ project, file, ...rest })`, `shownPictures`, taklit `imageQueue`.
- Produces: implementasyon döngüsünün uyacağı sözleşme — karo mount olunca sıraya girer; fotoğraf
  gelene kadar `<img>` `display: none` durur; bekleyen karo `.wf-img`, inen karo ayrıca
  `.wf-spinner` gösterir; bilet yükleme, hata, ekrandan silinme ve 30 saniyede bırakılır.

- [ ] **Step 1: Dosyayı baştan yaz**

Bugünkü dosyanın gözlemci taklidi (`stubObserver`) ve onu süren beş testi tümüyle gidiyor. Yeni
hâli:

```jsx
import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { fileUrl } from "../../shared/api.js";
import { shownPictures } from "../../shared/shown_pictures.js";
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

// How long the tile waits before it lets the queue move on. Written out rather than imported: a
// test that reads the number from the code cannot say the number is wrong.
const PATIENCE = 30000;

// Found by its alt rather than its role: a picture that has not arrived is hidden, and testing
// library leaves a hidden element out of the accessibility tree altogether.
const picture = () => screen.getByAltText("1_a.png");
const sourceOf = () => picture().getAttribute("src");
const seen = () => picture().style.display !== "none";
const holder = () => document.querySelector(".wf-img");
const turning = () => document.querySelector(".wf-spinner");
// Optional call on purpose: a tile that never asks must leave the assertion to do the failing
// rather than throw on an empty queue.
const grant = () => act(() => queue.waiting[0]?.grant());
const releases = () => queue.waiting.map((ticket) => ticket.released);

beforeEach(() => {
  queue.forget();
  // A picture that has been on screen once is remembered for the session, so a suite whose tests
  // all name the same file has to start each of them from nothing.
  shownPictures.clear();
});
afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

describe("TileImage — asking", () => {
  it("asks for the picture as soon as the tile is built", () => {
    render(<TileImage project="düğün" file="1_a.png" />);

    // Nothing was scrolled and nothing came into view: the tile asks because it exists. That is
    // what makes the gallery fill in frame order instead of in the order the page was scrolled.
    expect(queue.waiting).toHaveLength(1);
  });

  it("asks even where the browser could tell it is out of sight", () => {
    // The gate this task removes only exists where there is an observer to run it, and jsdom has
    // none -- so an observer is put here for the tile to ignore. Without this test the removal
    // could not be seen from a test at all.
    vi.stubGlobal("IntersectionObserver", class {
      observe() {}
      disconnect() {}
    });

    render(<TileImage project="düğün" file="1_a.png" />);

    expect(queue.waiting).toHaveLength(1);
  });

  it("draws no picture until the queue grants a slot", () => {
    render(<TileImage project="düğün" file="1_a.png" />);

    // The ceiling is only a ceiling if being in the queue is not enough to be drawn.
    expect(sourceOf()).toBeNull();
  });

  it("draws the picture once the queue grants a slot", () => {
    render(<TileImage project="düğün" file="1_a.png" />);

    grant();

    expect(sourceOf()).toBe(fileUrl("düğün", "1_a.png"));
  });

  it("skips the queue for a picture it has already shown", () => {
    const first = render(<TileImage project="düğün" file="1_a.png" />);
    grant();
    fireEvent.load(picture());
    first.unmount();

    render(<TileImage project="düğün" file="1_a.png" />);

    // No second wait, and no second ticket: the bytes are in the browser's cache, so what waiting
    // again would cost is the picture blinking off the screen (İstek 1.2). Not even a holder for
    // an instant -- a holder is what the blink looks like.
    expect(queue.waiting).toHaveLength(1);
    expect(sourceOf()).toBe(fileUrl("düğün", "1_a.png"));
    expect(seen()).toBe(true);
    expect(holder()).toBeNull();
  });

  it("does not remember a picture that never arrived", () => {
    const first = render(<TileImage project="düğün" file="1_a.png" />);
    grant();
    fireEvent.error(picture());
    first.unmount();

    render(<TileImage project="düğün" file="1_a.png" />);

    expect(sourceOf()).toBeNull();
  });
});

describe("TileImage — what the tile shows", () => {
  it("shows a plain holder while it waits its turn", () => {
    render(<TileImage project="düğün" file="1_a.png" />);

    // Every tile is in the queue from the moment it is built, so a ring on each of them would be
    // ninety rings turning at once. That is not information.
    expect(holder()).toBeTruthy();
    expect(turning()).toBeNull();
  });

  it("shows a turning holder while the picture is coming", () => {
    render(<TileImage project="düğün" file="1_a.png" />);

    grant();

    // With a ceiling of one there is exactly one of these on the screen: the gallery's answer to
    // what is downloading right now.
    expect(turning()).toBeTruthy();
  });

  it("keeps the picture out of sight until it arrives", () => {
    render(<TileImage project="düğün" file="1_a.png" />);

    grant();

    // The complaint this started from: an img with nothing to draw writes its alt text on the
    // screen, and the alt text is the file name.
    expect(seen()).toBe(false);
  });

  it("shows the picture and drops the holder once it arrives", () => {
    render(<TileImage project="düğün" file="1_a.png" />);
    grant();

    fireEvent.load(picture());

    expect(seen()).toBe(true);
    expect(holder()).toBeNull();
  });

  it("leaves a quiet holder where a picture never arrived", () => {
    render(<TileImage project="düğün" file="1_a.png" />);
    grant();

    fireEvent.error(picture());

    // A broken image icon and a file name is what this replaces. The ring goes with it: nothing
    // is coming any more, and a ring that turns forever says the opposite.
    expect(holder()).toBeTruthy();
    expect(turning()).toBeNull();
    expect(seen()).toBe(false);
  });
});

describe("TileImage — giving the slot back", () => {
  it("frees its slot once the picture has loaded", () => {
    render(<TileImage project="düğün" file="1_a.png" />);
    grant();

    fireEvent.load(picture());

    expect(releases()).toEqual([1]);
  });

  it("frees its slot when the picture fails", () => {
    render(<TileImage project="düğün" file="1_a.png" />);
    grant();

    fireEvent.error(picture());

    // Loaded and failed are the same answer: the slot is what is being returned, not a verdict on
    // the file. One broken photo must not take a permanent bite out of the ceiling.
    expect(releases()).toEqual([1]);
  });

  it("frees its slot when the tile is taken off the screen", () => {
    const { unmount } = render(<TileImage project="düğün" file="1_a.png" />);
    grant();

    unmount();

    // Opening a frame's page, deleting it, dragging it elsewhere: the tile stops being, and the
    // queue must not go on holding a slot for it.
    expect(releases()).toEqual([1]);
  });

  it("frees its slot when the picture takes too long", () => {
    vi.useFakeTimers();
    render(<TileImage project="düğün" file="1_a.png" />);
    grant();

    act(() => vi.advanceTimersByTime(PATIENCE));

    // An img download has no timeout of its own -- the ten second abort in api.js belongs to
    // fetch. A request that hangs answers neither load nor error, and with a ceiling of one a
    // ticket held forever is the whole gallery stopped behind it.
    expect(releases()).toEqual([1]);
  });

  it("draws a picture that arrives after its slot was given up", () => {
    vi.useFakeTimers();
    render(<TileImage project="düğün" file="1_a.png" />);
    grant();
    act(() => vi.advanceTimersByTime(PATIENCE));

    fireEvent.load(picture());

    // Letting the queue move on is not cancelling the download. The bytes were already on their
    // way, and a picture is what the tile is for.
    expect(seen()).toBe(true);
    expect(shownPictures.has(fileUrl("düğün", "1_a.png"))).toBe(true);
  });
});
```

- [ ] **Step 2: Altı testin düştüğünü gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: `TileImage.test.jsx` içinde **6 failed**:

| Test | Bugün neden düşüyor |
|---|---|
| asks even where the browser could tell it is out of sight | Gözlemci var, karo görüş alanına girmeden sıraya girmiyor |
| shows a plain holder while it waits its turn | Kutu diye bir şey yok |
| shows a turning holder while the picture is coming | Halka diye bir şey yok |
| keeps the picture out of sight until it arrives | `<img>` her zaman görünür |
| leaves a quiet holder where a picture never arrived | Aynı, kutu yok |
| frees its slot when the picture takes too long | Süre diye bir şey yok |

Geri kalanı **yeşil doğuyor ve öyle kalıyor** — jsdom'da `IntersectionObserver` hiç yok, dolayısıyla
bugünkü karo da mount olunca sıraya giriyor. Bunlar kanıt değil, bekçi: implementasyon turunda
silinmemesi gereken davranışlar.

Düşenler `AssertionError` ile düşmeli. `TypeError` ya da `null` üstünde patlama varsa yazım hatası
vardır — özellikle `picture()` bir şey bulamıyorsa `alt` metni değişmiş demektir.

---

### Task 3: Galeri karoları kare sırasıyla kuruyor

**Files:**
- Test: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

**Interfaces:**
- Consumes: dosyanın mevcut `renderGallery` ve `FRAMES` yardımcıları
  (`[done("2_a.png"), done("1_a.png"), done("0_a.png")]`).
- Produces: yok — bu test bir sözleşme üretmiyor, var olan sırayı sabitliyor.

- [ ] **Step 1: Dosyaya kuyruk taklidini ekle**

Mevcut iki `vi.mock` çağrısının hemen altına (15. satırdan sonra):

```jsx
// The tiles ask a shared queue before they download, and jsdom never loads a picture -- with the
// real one the first tile would hold the only slot for the whole file. The fake grants nothing by
// itself, and the order of its list is the order the tiles asked in.
const queue = vi.hoisted(() => {
  const waiting = [];
  return {
    waiting,
    ask(grant) {
      const ticket = { grant, done: () => {} };
      waiting.push(ticket);
      return ticket;
    },
    forget: () => { waiting.length = 0; },
  };
});

vi.mock("../../shared/image_queue.js", () => ({ imageQueue: queue }));
```

Ve mevcut `beforeEach`:

```jsx
beforeEach(() => {
  vi.clearAllMocks();
  queue.forget();
});
```

- [ ] **Step 2: Testi `Gallery ordering` bölümüne ekle**

`describe("Gallery ordering", ...)` içine, son testin ardına:

```jsx
  it("puts the tiles in the queue in the order the frames are in", () => {
    renderGallery();

    act(() => queue.waiting[0].grant());

    // The item's own promise: the gallery fills from the first frame to the last, whichever way
    // the page was scrolled. FIFO is the queue's own test and asking at build is the tile's; what
    // only this can say is that the first ticket belongs to the first frame.
    expect(screen.getByAltText("2_a.png").getAttribute("src")).toBeTruthy();
    expect(screen.getByAltText("1_a.png").getAttribute("src")).toBeNull();

    act(() => queue.waiting[1].grant());

    expect(screen.getByAltText("1_a.png").getAttribute("src")).toBeTruthy();
  });
```

- [ ] **Step 3: Dosyanın tamamının yeşil kaldığını gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: `Gallery.test.jsx` **0 failed**. Yeni test de yeşil doğuyor — galeri karoları zaten kare
sırasıyla kuruyor; bu test o sırayı bundan sonra kimse bozamasın diye var.

Taklidin dosyanın geri kalanını bozmaması gerekiyor: mevcut testler fotoğrafı `getByAltText` ile
buluyor, `src`'sine bakmıyor. Bir test düşerse taklit yanlış yere konmuştur — `vi.mock` çağrıları
dosyanın tepesinde, `describe`'ların dışında olmalı.

---

### Task 4: Kırmızıyı doğrula ve commit'le

- [ ] **Step 1: Yalnız testlerin değiştiğini doğrula**

Run: `git status --short`
Expected: üç test dosyası ve `docs/superpowers`. `TileImage.jsx`, `image_queue.js`, `Gallery.jsx`
ve `frontend/dist` bu listede **olmamalı** — varsa kod yanlışlıkla değişmiştir, geri alınır.

- [ ] **Step 2: Toplamı bir kez daha gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: **7 failed** — Task 1'in bir tanesi ve Task 2'nin altısı. Başka düşen olmamalı.

- [ ] **Step 3: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): red for a gallery that downloads in frame order

SEVEN OF THESE TESTS FAIL ON PURPOSE. The code is the next commit.

The gallery asked for its pictures in whatever order the viewport reached them
and let two download at once -- and a tile that scrolled away handed its slot
back while its own download carried on, so the number really in flight was
larger than the ceiling said. A tile with nothing to draw yet wrote its alt
text across the card, which is the file name.

What these pin: the tile asks the moment it is built rather than when it comes
near, so frame order is download order and scrolling decides nothing; the
shared ceiling is one, which is the whole of what the user asked for -- one
goes, it lands, the next leaves; a tile waiting its turn shows a plain holder
while the one downloading shows a turning one; the picture stays out of sight
until it arrives and a picture that never arrives leaves a quiet holder rather
than a broken icon and a file name; and a request that hangs gives its slot up
after thirty seconds, because an img download has no timeout of its own and
with a ceiling of one a ticket held forever is the whole gallery stopped.

Not all of them are red. jsdom has no IntersectionObserver, so a tile there
already asks at mount and the tests that say so are green on arrival -- they
are guards, not proof. The one that proves the gate is gone puts an observer
in the tile's way and expects it to ask anyway.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** A1 → Task 1 · A2 → Task 2'nin ilk iki testi · A3, A4 → sonraki ikisi · A5 →
*skips the queue for a picture it has already shown* · A6–A10 → *what the tile shows* bölümü ·
A11–A13 → *giving the slot back* bölümünün ilk üçü · A14 → *takes too long* · A15 → *arrives after
its slot was given up* · A16 → Task 3. Spec'te olup planda karşılığı olmayan madde yok. Spec'in
"yeni testi yok, bilerek" dediği davranış da planda yok — kuyruğun mevcut testi taşıyor.

**Ad tutarlılığı:** Testlerin okuduğu üç şey — `.wf-img`, `.wf-spinner` ve `<img>`'in
`style.display`'i — implementasyon döngüsünün uyacağı sözleşme. İlk ikisi uygulamada zaten var
(`Rendering` ve kit'in kendi sınıfı), üçüncüsü bu maddede doğuyor.

**Bilerek dışarıda:** taklit kuyruğun `done` çağrı sayısını okuyan bir test. Süresi dolmuş bir karo
fotoğrafı gelince bileti ikinci kez bırakır; o bırakışın slot üretmemesi kuyruğun kuralı ve kuyruğun
kendi testi bunu tutuyor. Karo tarafında sınamak kodun kendi içini sınamak olurdu.

**Yakalanan tuzak:** `getByRole("img")`. Bugünkü dosya karoyu böyle buluyor, ama gizlenen bir `<img>`
erişilebilirlik ağacından da çıkıyor ve sorgu boş dönüyor. Yeni dosya baştan `getByAltText`
kullanıyor; `Gallery.test.jsx` zaten öyle yapıyordu, o dosya bundan etkilenmiyor.

**Dürüstlük notu:** yedi kırmızının hepsi davranış testi, ama *"gözlemci gitti"*yi kanıtlayan tek
test yapay bir gözlemci kuruyor. jsdom'da o kapı zaten yok; kapının kaldırıldığını başka türlü
görmenin yolu da yok.
