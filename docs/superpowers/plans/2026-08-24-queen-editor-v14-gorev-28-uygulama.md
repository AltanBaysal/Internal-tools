# v14 Görev 28 — Galerinin indirme sırası: İMPLEMENTASYON döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Yedi kırmızı testi yeşile döndürmek — galeri kareleri baştan sona, tek tek indirsin ve
inmemiş karo dosya adı yerine tutucu göstersin.

**Architecture:** Kuyrukta bir sayı ve gerekçesi değişiyor. Karo baştan yazılıyor: görünürlük kapısı
çıkıyor, üç durumlu bir hâl, bir süre ve bir tutucu giriyor. Galeride bir yorum bugüne uyuyor.
Ardından ön yüz derleniyor ve `dist` aynı commit'e giriyor.

**Tech Stack:** React, Vite, Vitest.

**Spec:** [v14 Görev 28 implementasyon spec'i](../specs/2026-08-24-queen-editor-v14-gorev-28-uygulama-design.md)

## Global Constraints

- **Test dosyalarına dokunulmuyor.** Kırmızı commit'te ne yazıldıysa o kalır; testi koda uydurmak
  turun anlamını yok eder.
- Süre sabiti **30000**, testin yazdığı sayı.
- Tutucunun sınıfı **`wf-img`**, halkanınki **`wf-spinner`** — testler bu iki adı arıyor.
- Gizleme **`display: "none"`** ile; testler `style.display` okuyor.
- Dil: kod ve yorumlar **İngilizce**, commit mesajı **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- **`dist` kaynakla aynı commit'e girer.**
- Test komutları (depo kökünden, `cd` yok):
  `npm test --prefix queen-editor/frontend` · `python -m pytest queen-editor -q`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/frontend/src/shared/image_queue.js` | aynı anda kaç indirme olabileceği | sabit + yorum |
| `queen-editor/frontend/src/features/photo_generation/TileImage.jsx` | bir karonun fotoğrafını ne zaman ve nasıl çizdiği | baştan yazılır |
| `queen-editor/frontend/src/features/photo_generation/Gallery.jsx` | galerinin bütünü | tek yorum |
| `queen-editor/frontend/dist/**` | defterin çalıştırdığı ön yüz | yeniden derlenir |

---

### Task 1: Kuyruğun tavanı 1 olur

**Files:**
- Modify: `queen-editor/frontend/src/shared/image_queue.js`

**Interfaces:**
- Consumes: yok.
- Produces: `imageQueue` — tavanı 1 olan paylaşılan tekil.

- [ ] **Step 1: Sabiti ve yorumunu değiştir**

Dosyanın ilk dört satırı bugün şöyle:

```js
// The gallery draws every tile as its own request through the same tunnel, and nothing used to
// count them: the poll's request waited behind a screenful of photos until the ten second abort in
// api.js fired. Two at a time leaves the pipe open for the API without making the gallery crawl.
const GALLERY_SLOTS = 2;
```

Yerine:

```js
// One at a time, in the order the tiles were built. Every tile is its own request through the same
// tunnel and the status poll shares it, so a ceiling is what keeps the API's request from waiting
// behind a project's worth of photos. One rather than more: on a full gallery the difference is
// seconds, and a pipe with one thing in it is the pipe nobody has to reason about.
const GALLERY_SLOTS = 1;
```

Dosyanın geri kalanına — `createQueue`, `pour`, bilet — **dokunulmuyor.**

- [ ] **Step 2: O testin yeşile döndüğünü gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: `image_queue.test.js` **7 passed**. Toplam hâlâ kırmızı; kalan altısı Task 2'nin.

---

### Task 2: Karo baştan yazılır

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/TileImage.jsx`

**Interfaces:**
- Consumes: `imageQueue.ask(grant) -> ticket`, `ticket.done()`, `shownPictures`, `fileUrl`,
  `Rendering({ style })`.
- Produces: `TileImage({ project, file, style, ...rest })` — galerinin bugün çağırdığı imzanın
  aynısı; `style` artık adıyla alınıyor.

- [ ] **Step 1: Dosyayı baştan yaz**

```jsx
import { useEffect, useRef, useState } from "react";

import { fileUrl } from "../../shared/api.js";
import { imageQueue } from "../../shared/image_queue.js";
import { shownPictures } from "../../shared/shown_pictures.js";
import { Rendering } from "./frame_status.jsx";

// How long a tile waits for its picture before it lets the queue move on. An img download has no
// timeout of its own -- the ten second abort in api.js belongs to fetch -- so a request that hangs
// answers neither load nor error, and with a single slot that is the whole gallery stopped behind
// it. Judgement rather than measurement: long enough that a slow photo is never given up on early.
const PATIENCE = 30000;

// The picture is in the page from the start, because a hidden image is downloaded and an absent one
// is not. Hidden rather than merely empty: an img with nothing to draw writes its alt text across
// the card, and the alt text is the file name.
const HIDDEN = { display: "none" };

export function TileImage({ project, file, style, ...rest }) {
  const url = fileUrl(project, file);
  // Has this picture been on screen already? Read once, when the tile is built: a tile coming back
  // to a gallery it was already in draws at once, because that waiting is exactly what coming back
  // must not do twice (İstek 1.2).
  const [held] = useState(() => shownPictures.has(url));
  const [granted, setGranted] = useState(held);
  // waiting until the browser answers, then here or gone. A picture that never arrived keeps the
  // holder and loses the ring: nothing is coming, and a ring that turns forever says otherwise.
  const [state, setState] = useState(held ? "here" : "waiting");
  const ticket = useRef(null);

  useEffect(() => {
    if (held) return undefined;
    // No viewport to wait for: every tile asks as soon as it is built, so the order the gallery
    // downloads in is the order its frames are in, whichever way the page is scrolled.
    ticket.current = imageQueue.ask(() => setGranted(true));
    // Being taken off the screen is an answer to the queue: this tile is done waiting. The ticket
    // takes a second release without giving back a second slot.
    return () => ticket.current.done();
  }, [held]);

  useEffect(() => {
    if (!granted || state !== "waiting") return undefined;
    const timer = setTimeout(() => ticket.current?.done(), PATIENCE);
    return () => clearTimeout(timer);
  }, [granted, state]);

  // Loaded and failed are the same answer to the queue: what is being returned is the slot, not a
  // verdict on the file. One broken photo must not take a permanent bite out of a ceiling of one.
  const settle = (how) => {
    setState(how);
    ticket.current?.done();
  };

  return (
    <>
      {state !== "here" && (granted && state === "waiting"
        // Only the tile that holds the slot turns. Every tile is in the queue from the moment it
        // is built, so a ring on each of them would be a gallery of rings saying nothing.
        ? <Rendering style={style} />
        : <div className="wf-img" style={style} />)}
      <img alt={file} src={granted ? url : undefined}
           style={state === "here" ? style : HIDDEN}
           // Only a picture that really arrived is remembered: a broken one has nothing to keep,
           // and the next tile that asks for it should get to try again.
           onLoad={() => { shownPictures.add(url); settle("here"); }}
           onError={() => settle("gone")}
           {...rest} />
    </>
  );
}
```

- [ ] **Step 2: Karonun altı testinin de yeşile döndüğünü gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: **553 passed.**

Düşen kalırsa:

| Düşen | Bak |
|---|---|
| `shows a plain holder…` | Kutunun sınıfı `wf-img` mi |
| `shows a turning holder…` | `Rendering` içeri alındı mı, koşul `granted && state === "waiting"` mi |
| `keeps the picture out of sight…` | `style` prop'u `rest`'ten ayrıldı mı — ayrılmadıysa `{...rest}` gizlemeyi eziyor |
| `frees its slot when the picture takes too long` | Süre etkisinin bağımlılıkları `[granted, state]` mi |
| `asks even where…` | Dosyada `IntersectionObserver` kaldı mı |
| Galeri ya da detay testlerinden biri | Fotoğrafın `alt`'ı hâlâ `file` mi |

---

### Task 3: Galerinin yorumu bugüne uyar

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`

**Interfaces:**
- Consumes: yok.
- Produces: yok.

- [ ] **Step 1: `TileImage`'ın üstündeki yorumu değiştir**

Bugünkü hâli:

```jsx
{/* The picture asks a queue before it downloads: every tile is a request
    through the same tunnel, and unlimited tiles starved the poll until it
    timed out. loading=lazy is gone with it -- the queue is the gate now, and
    the tile only asks once it is near. */}
```

Yerine:

```jsx
{/* The picture asks a queue before it downloads: every tile is a request
    through the same tunnel, and one at a time keeps the poll's own request
    from waiting behind a project's worth of photos. Every tile asks as soon
    as it is drawn, so the gallery fills in frame order however the page is
    scrolled. */}
```

Son cümle *"karo yalnız yaklaşınca ister"* diyordu ve artık doğru değil; depo kuralı, çelişkide
yorumun koda uydurulmasını söylüyor.

- [ ] **Step 2: Takımın yeşil kaldığını gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: **553 passed.** Yorum hiçbir testi etkilemez; bu adım yazım hatası içindir.

---

### Task 4: Ön yüz derlenir ve commit'lenir

- [ ] **Step 1: Python tarafının da yeşil olduğunu gör**

Run: `python -m pytest queen-editor -q`
Expected: **711 passed.**

- [ ] **Step 2: Derle**

Run: `npm run build --prefix queen-editor/frontend`
Expected: hatasız biter ve `queen-editor/frontend/dist` yenilenir.

- [ ] **Step 3: Test dosyalarının değişmediğini doğrula**

Run: `git status --short`
Expected: üç kaynak dosya ve `dist`. `*.test.*` bu listede **olmamalı** — varsa test koda
uydurulmuştur, geri alınır ve Task 2'ye dönülür.

- [ ] **Step 4: Commit**

```bash
git add queen-editor/frontend docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the gallery downloads one picture at a time, in frame order

Green. Three gates became two: the tile no longer waits for the viewport, so
it asks the moment it is built and the gallery fills from the first frame to
the last however the page is scrolled. The ceiling is one -- a picture goes,
it lands, the next leaves -- which is what was asked for in the first place
and is also the simplest thing the queue can be.

The leak went with the gate. A granted tile that scrolled away used to hand
its slot back while its own download carried on, so more was in flight than
the ceiling said; a tile that never leaves the queue by scrolling cannot do
that.

A tile with nothing to draw was writing its alt text across the card, which is
the file name. It now shows the app's own image holder -- plain while it waits
its turn, turning while it downloads, plain again and quiet where a picture
never arrived. The picture stays hidden rather than absent, because a hidden
image is still downloaded.

One slot has a hazard two never had: an img download has no timeout of its
own, so a request that hangs answers neither load nor error and holds the only
slot forever. The tile gives its ticket up after thirty seconds. The download
is not cancelled -- if the picture arrives late it is still drawn.

The queue's comment justified its number with a starvation that belonged to
the tunnel, and the tunnel was fixed yesterday. It says what is true now.
EOF
git log --oneline -1
```

---

### Task 5: Yol haritasında maddeyi işaretle

- [ ] **Step 1: Maddeyi ✅ yap, sayacı ilerlet**

`docs/superpowers/plans/2026-08-20-queen-editor-v14-roadmap.md`:
- 28. maddenin **İş** hücresi `✅ **Galerinin indirme sırası.**` diye başlar.
- Başlıktaki sayaç `27/30` → `28/30`.

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/plans/2026-08-20-queen-editor-v14-roadmap.md
git commit -F - <<'EOF'
docs(queen-editor): the download order item is done in code, and waits for the tour

Both tours are in and the suite is green. What the tour still has to say is
whether a gallery of a hundred frames filling one picture at a time reads as
fast to a person -- the order is now certain, the patience is not.
EOF
```

## Self-Review

**Spec kapsamı:** K1 → Task 1 · K2 → Task 2'nin silinen gözlemcisi · K3, K4 → Task 2'nin çizim
bloğu · K5 → `HIDDEN` ve ayrılan `style` · K6 → `settle("gone")` ve tutucunun koşulu · K7 → süre
etkisi. Spec'in "Ön yüz derleniyor" bölümü → Task 4 Step 2. Spec'te olup planda karşılığı olmayan
madde yok.

**Ad tutarlılığı:** Testlerin okuduğu üç ad — `.wf-img`, `.wf-spinner`, `style.display` — planda
birebir aynı biçimde yazılıyor. `Rendering` halkayı kendi getiriyor, plan onu yeniden tarif
etmiyor.

**Yakalanan tuzak:** `style`. Bugün `rest`'in içinde geliyor ve `{...rest}` en sonda duruyor —
ayrılmazsa galerinin gönderdiği `display: block`, gizlemeyi sessizce ezerdi. Test düşer ama sebebi
görünmez, o yüzden Step 2'nin tablosunda adıyla yazılı.

**Bilerek dışarıda:** indirmenin iptali. Süre dolunca `src` kaldırılabilirdi; kaldırılmıyor, çünkü
yolda olan baytları çöpe atmak hiçbir şey kazandırmıyor ve testlerden biri geç gelen fotoğrafın
yine çizilmesini istiyor.
