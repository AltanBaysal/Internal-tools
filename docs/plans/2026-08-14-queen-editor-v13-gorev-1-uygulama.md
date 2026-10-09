# v13 Görev 1 — Galeri resim kuyruğu: İMPLEMENTASYON döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** On dört kırmızı testi yeşile çevirmek: kuyruğa kurallarını, karoya protokolünü vermek ve
galeriyi ona bağlamak.

**Architecture:** İki iskelet dolduruluyor, bir çağrı yeri değişiyor. Kuyruk bir sayaç ve bir
sıradan ibaret, DOM bilmiyor. Karo üç sinyali bağlıyor (gözlemci, kuyruk, `<img>`) ve bileti bir
referansta tutuyor çünkü onu bırakan dört yol var.

**Tech Stack:** React 18, vitest, jsdom, Vite.

**Tasarım:** [uygulama spec'i](../specs/2026-08-14-queen-editor-v13-gorev-1-uygulama-design.md)

## Global Constraints

- Testler **değişmiyor**. Bir test yanlışsa durulur ve konuşulur; yeşile boyanmaz.
- Yorumlar **İngilizce**, ve yalnız NEDEN'i söylüyor.
- Commit mesajında **çift tırnak yok**.
- Komut: `npm test --prefix queen-editor/frontend`
- `dist/` **aynı commit'te** yeniden derlenir — `frontend/src/` değişiyor.
- Commit **yeşil** gider.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `frontend/src/shared/image_queue.js` | tavan, sıra, slot iadesi | iskelet dolar |
| `frontend/src/features/photo_generation/TileImage.jsx` | gözlemci + bilet + bırakma | iskelet dolar |
| `frontend/src/features/photo_generation/Gallery.jsx` | karoyu çizen dal | `<img>` → `<TileImage>` |

---

### Task 1: Kuyruğa kurallarını ver

**Files:**
- Modify: `queen-editor/frontend/src/shared/image_queue.js`

**Interfaces:**
- Produces: `createQueue(limit)` → `{ ask(grant) }`, `ask` → `{ done() }`. `imageQueue` tavanı 2
  olan paylaşılan örnek. Task 2 bunu import ediyor.

- [ ] **Step 1: Dosyanın tamamını değiştir**

```js
// The gallery draws every tile as its own request through the same tunnel, and nothing used to
// count them: the poll's request waited behind a screenful of photos until the ten second abort in
// api.js fired. Two at a time leaves the pipe open for the API without making the gallery crawl.
const GALLERY_SLOTS = 2;

export function createQueue(limit) {
  const waiting = [];
  let flying = 0;

  function pour() {
    while (flying < limit && waiting.length) {
      const ticket = waiting.shift();
      // Skip rather than stop: a tile scrolled past while in line must not hold up the ones behind
      // it, which is the whole reason the queue is worth having.
      if (ticket.spent) continue;
      flying += 1;
      ticket.holding = true;
      ticket.grant();
    }
  }

  return {
    ask(grant) {
      const ticket = {
        grant,
        holding: false,
        spent: false,
        done() {
          // One ticket frees one slot however often it is released. A tile that loads and is then
          // taken off the screen releases twice, and the second must not invent a slot.
          if (ticket.spent) return;
          ticket.spent = true;
          if (!ticket.holding) return;
          flying -= 1;
          pour();
        },
      };
      waiting.push(ticket);
      pour();
      return ticket;
    },
  };
}

export const imageQueue = createQueue(GALLERY_SLOTS);
```

- [ ] **Step 2: Kuyruğun testlerini koştur**

Run: `npm test --prefix queen-editor/frontend -- image_queue`
Expected: 7 test, 7'si de geçiyor.

---

### Task 2: Karoya protokolünü ver

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/TileImage.jsx`

**Interfaces:**
- Consumes: `imageQueue` (Task 1), `fileUrl(project, file)`.
- Produces: `TileImage({ project, file, ...rest })`. Task 3 bunu çiziyor.

- [ ] **Step 1: Dosyanın tamamını değiştir**

```jsx
import { useEffect, useRef, useState } from "react";

import { fileUrl } from "../../shared/api.js";
import { imageQueue } from "../../shared/image_queue.js";

// How far ahead of the viewport a tile starts asking. Judgement, not measurement: too narrow and a
// tile shows up empty before it fills, too wide and pictures nobody scrolled to eat the ceiling.
const MARGIN = "300px";

export function TileImage({ project, file, ...rest }) {
  // A browser with no observer cannot be asked, and calling new on an absent constructor throws
  // where it stands and takes the gallery with it. Near is what the browser assumed before the
  // queue existed, so it is the safe answer. jsdom is one such browser.
  const [near, setNear] = useState(() => typeof IntersectionObserver === "undefined");
  const [granted, setGranted] = useState(false);
  const picture = useRef(null);
  const ticket = useRef(null);

  useEffect(() => {
    if (typeof IntersectionObserver === "undefined") return undefined;
    const watcher = new IntersectionObserver(
      (entries) => setNear(entries[entries.length - 1].isIntersecting),
      { rootMargin: MARGIN });
    watcher.observe(picture.current);
    return () => watcher.disconnect();
  }, []);

  useEffect(() => {
    if (!near) return undefined;
    ticket.current = imageQueue.ask(() => setGranted(true));
    // Scrolling away and being unmounted are the same answer to the queue: this tile is done
    // waiting. The ticket takes a second release without giving back a second slot.
    return () => ticket.current.done();
  }, [near]);

  // Loaded and failed are also the same answer: the slot is what is being returned, not a verdict
  // on the file. One broken photo must not take a permanent bite out of a ceiling of two.
  const release = () => ticket.current?.done();

  return (
    <img ref={picture} alt={file}
         src={granted ? fileUrl(project, file) : undefined}
         onLoad={release} onError={release}
         {...rest} />
  );
}
```

- [ ] **Step 2: Karonun testlerini koştur**

Run: `npm test --prefix queen-editor/frontend -- TileImage`
Expected: 9 test, 9'u da geçiyor.

---

### Task 3: Galeriyi karoya bağla

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`

- [ ] **Step 1: Import ekle**

Dosya import'ları büyük/küçük harf duyarsız alfabetik sıralıyor (`api` → `ConfirmModal` →
`router`), dolayısıyla yerel grubun **sonuna**:

```jsx
import { TileImage } from "./TileImage.jsx";
```

- [ ] **Step 2: `state === "done"` dalındaki `<img>`'i değiştir**

Bugün:

```jsx
                    {state === "done" ? (
                      <img src={fileUrl(project, frame.file)} alt={frame.file}
                           loading="lazy" decoding="async" draggable={false}
                           style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover",
                                    border: "1px solid var(--border)", borderRadius: "var(--r-sm)",
                                    display: "block" }} />
                    ) : state === "running" ? (
```

Şununla:

```jsx
                    {state === "done" ? (
                      /* The picture asks a queue before it downloads: every tile is a request
                         through the same tunnel, and unlimited tiles starved the poll until it
                         timed out. loading=lazy is gone with it -- the queue is the gate now, and
                         the tile only asks once it is near. */
                      <TileImage project={project} file={frame.file}
                                 decoding="async" draggable={false}
                                 style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover",
                                          border: "1px solid var(--border)",
                                          borderRadius: "var(--r-sm)", display: "block" }} />
                    ) : state === "running" ? (
```

- [ ] **Step 3: `fileUrl` hâlâ kullanılıyor mu, bak**

`Gallery.jsx` içinde `fileUrl` başka bir yerde kullanılmıyorsa import'tan çıkarılır; kullanılıyorsa
kalır. Grep ile bakılır, tahminle değil.

- [ ] **Step 4: Bütün takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: 353 geçen, 0 düşen.

---

### Task 4: Derle ve yeşil commit

- [ ] **Step 1: `dist/` derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Commit**

```bash
git add queen-editor/frontend/src queen-editor/frontend/dist docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): let two tile pictures fly at a time

The gallery drew every tile at once through the same tunnel, and the poll's
request waited behind them until the ten second abort fired. Two at a time
leaves the pipe open for the API.

Which contention starved it -- connection slots or bandwidth -- is still
unmeasured, and one ceiling answers both.

A tile asks only once it is near, and drops out of the line if it leaves before
its turn, so scrolling does not queue a gallery nobody looked at. Every way of
being finished returns the slot the same way: loaded, failed, scrolled away,
unmounted.

A browser without an observer draws at once rather than dying on a constructor
that is not there.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** "Ne geliyor"un dört paragrafı → Task 1 (sayaç ve sıra), Task 2 (üç sinyal ve
bilet, gözlemcisiz hâl), Task 3 (`<img>` → `<TileImage>`, `loading=lazy` gidiyor). "Değişen yerler"
tablosunun dört satırı → Task 1, 2, 3 ve Task 4 Step 1.

**Tip tutarlılığı:** `ask(grant)` → `{ done() }` üç dosyada da aynı. `TileImage`'ın props'u
(`project`, `file`, `...rest`) testteki çağrıyla ve Task 3'teki çağrıyla birebir.

**Kontrol edilen tuzak:** `release` `?.` kullanıyor ama efektin temizliği kullanmıyor — çünkü
temizlik ancak bilet kurulduktan sonra çalışabilir, `release` ise ilk boyamada `load` gelirse
biletten önce çağrılabilir. İki farklı durum, iki farklı yazım; ikisi de kasıtlı.

**Kontrol edilen tuzak 2:** `src={granted ? … : undefined}` — `undefined` React'e özniteliği hiç
yazdırmaz, `null` da öyle, ama boş string `src=""` yazar ve tarayıcı onu **sayfanın kendi URL'si**
sanıp indirmeye kalkar. Testler `getAttribute("src")` `null` bekliyor; boş string bunu da geçemezdi.

**Kontrol edilen tuzak 3:** gözlemci efekti `[]` bağımlılığıyla bir kez kuruluyor, bilet efekti
`[near]` ile. İkisi tek efekte konsaydı her yaklaşma gözlemciyi yeniden yaratırdı.
