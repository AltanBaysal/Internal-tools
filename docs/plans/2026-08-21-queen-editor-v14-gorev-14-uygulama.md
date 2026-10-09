# v14 Görev 14 — Detaydan dönünce galerinin yerinde durması: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün bıraktığı altı testi yeşile döndürmek: kayma yeri ziyaretler arasında
dursun, bir kez gelmiş resim beklemesin.

**Architecture:** İki yeni küçük modül ve onları takan iki dosya. İki konu birbirinden bağımsız,
o yüzden ayrı turlar.

**Tech Stack:** React 18, vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-14-galerinin-yeri-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor.**
- Yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor.**
- Commit **yeşil gider**.
- İki bellek de **yalnız oturum**: modül düzeyinde, diske yazılmıyor, yenilenince unutuluyor.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `frontend/src/shared/shown_pictures.js` | ekrana gelmiş resimler | **yeni** |
| `.../photo_generation/useKeptScroll.js` | kayma yerinin belleği | **yeni** |
| `.../photo_generation/TileImage.jsx` | iki kapıyı atlama | üç değişiklik |
| `.../photo_generation/ProjectScreen.jsx` | kancanın takılması | iki satır |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Kayma yeri

**Files:**
- Create: `queen-editor/frontend/src/features/photo_generation/useKeptScroll.js`
- Modify: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx`

**Interfaces:**
- Produces: `useKeptScroll(project) -> ref`.

- [ ] **Step 1: Kancayı yaz**

```js
import { useLayoutEffect, useRef } from "react";

// Where each project's gallery was left, by project. Opening a frame's page replaces the whole
// project screen, so the scroll box is built again on every step in and out -- and a box built
// again starts at the top, which is where the pictures the user was looking at go missing
// (İstek 1.2).
//
// Memory only: what is wanted is standing still inside one visit, not a property of the project. A
// reload opens the gallery at the top, the same as opening it for the first time.
const KEPT = new Map();

/** The ref for the gallery's scroll box; attaching it is the whole contract.
 *
 * A layout effect rather than an ordinary one: the restore has to land before the browser paints,
 * or the gallery is drawn at the top for one frame and then jumps. The node is captured in the
 * effect's body, so the cleanup holds one whether or not React has cleared the ref by then -- and
 * the place is read on the way out rather than on every scroll event, which is one write a visit.
 */
export function useKeptScroll(project) {
  const box = useRef(null);
  useLayoutEffect(() => {
    const node = box.current;
    node.scrollTop = KEPT.get(project) || 0;
    return () => KEPT.set(project, node.scrollTop);
  }, [project]);
  return box;
}
```

- [ ] **Step 2: Kutuya tak**

`ProjectScreen.jsx`, `useProducers` satırının altına:

```jsx
  // The gallery's own scroll box, kept across the steps in and out of a frame's page.
  const box = useKeptScroll(project);
```

ve kutunun kendisi:

```jsx
        <div data-scroll ref={box} style={{ flex: 1, minWidth: 0, overflowY: "auto" }}>
```

İçe aktarma: `import { useKeptScroll } from "./useKeptScroll.js";`

- [ ] **Step 3: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: `useKeptScroll.test.jsx`'in üçü ve `ProjectScreen`'in biri yeşile döner;
`TileImage.test.jsx` hâlâ toplanamıyor.

---

### Task 2: Bir kez gelmiş resim

**Files:**
- Create: `queen-editor/frontend/src/shared/shown_pictures.js`
- Modify: `queen-editor/frontend/src/features/photo_generation/TileImage.jsx`

**Interfaces:**
- Produces: `shownPictures` — URL'lerden oluşan bir `Set`.

- [ ] **Step 1: Kümeyi yaz**

```js
// Which pictures this session has already put on screen. Opening a frame's page builds the whole
// gallery again, and a tile that starts empty waits for the viewport and then for a queue slot --
// that waiting is what the user sees as their photos disappearing (İstek 1.2). The bytes are in the
// browser's cache either way; what is kept here is that the waiting is already over.
//
// Beside the queue rather than inside it: one is a ceiling on what may be in flight, the other a
// note of what has already landed.
//
// URLs, and a session's worth of short strings -- nothing is evicted because nothing grows.
export const shownPictures = new Set();
```

- [ ] **Step 2: Karoyu düzelt**

```jsx
export function TileImage({ project, file, ...rest }) {
  const url = fileUrl(project, file);
  // Has this picture been on screen already? Read once, when the tile is built: a tile coming back
  // to a gallery it was already in skips both gates below, because that waiting is exactly what
  // coming back must not do twice (İstek 1.2).
  const [held] = useState(() => shownPictures.has(url));
  // A browser with no observer cannot be asked, and calling new on an absent constructor throws
  // where it stands and takes the gallery with it. Near is what the browser assumed before the
  // queue existed, so it is the safe answer. jsdom is one such browser.
  const [near, setNear] = useState(() => held || typeof IntersectionObserver === "undefined");
  const [granted, setGranted] = useState(held);
  const picture = useRef(null);
  const ticket = useRef(null);

  useEffect(() => {
    if (held || typeof IntersectionObserver === "undefined") return undefined;
    const watcher = new IntersectionObserver(
      (entries) => setNear(entries[entries.length - 1].isIntersecting),
      { rootMargin: MARGIN });
    watcher.observe(picture.current);
    return () => watcher.disconnect();
  }, [held]);

  useEffect(() => {
    if (held || !near) return undefined;
    ticket.current = imageQueue.ask(() => setGranted(true));
    // Scrolling away and being unmounted are the same answer to the queue: this tile is done
    // waiting. The ticket takes a second release without giving back a second slot.
    return () => ticket.current.done();
  }, [held, near]);

  // Loaded and failed are also the same answer: the slot is what is being returned, not a verdict
  // on the file. One broken photo must not take a permanent bite out of a ceiling of two.
  const release = () => ticket.current?.done();

  return (
    <img ref={picture} alt={file}
         src={granted ? url : undefined}
         // Only a picture that really arrived is remembered: a broken one has nothing to keep, and
         // the next tile that asks for it should get to try again.
         onLoad={() => { shownPictures.add(url); release(); }}
         onError={release}
         {...rest} />
  );
}
```

İçe aktarma: `import { shownPictures } from "../../shared/shown_pictures.js";`

- [ ] **Step 3: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil — 384 / 474 / 694 / 444.

---

### Task 3: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

14. maddenin **İş** hücresi ✅ ile başlar, sayaç `13/31` → `14/31`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the gallery keeps its place and its pictures

Where the gallery was scrolled to is kept per project and put back before the browser
paints, so stepping into a frame's page and back leaves the screen exactly where it was. It
is read on the way out rather than on every scroll event, and it lives in memory only: a
reload opens at the top, the same as a first visit.

A tile whose picture has already been on screen this session draws it at once. Neither gate
is used again -- no observer is built and no ticket is taken -- because the ticket is the
part that would matter: a tile drawn without waiting that still stood in the queue would
eat the turn of one that really is waiting. The bytes are in the browser's cache either
way; what the second wait cost was the photos blinking off the screen.

A picture that never arrived is not remembered. There is nothing to keep, and the next tile
that asks for it should get to try again.

The gallery's list was already remembered across mounts. These two are the other half of
standing still, which is what the user asked for.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in üç parçası Task 1 (1, 3) ve Task 2 (2).

**Tip tutarlılığı:** `useKeptScroll` bir ref döndürüyor ve doğrudan bir düğüme takılıyor;
`shownPictures` her yerde `Set` ve anahtarı `fileUrl`'ün verdiği URL.

**Kontrol edilen tuzak:** `held` bir `useState` başlangıcı, yani kurulduğu andaki cevabı tutuyor.
Kümeyi her render'da okumak, yükleme bittiği anda bileti olan bir karonun kendini "beklememiş"
sanmasına yol açardı.

**Kontrol edilen tuzak 2:** gözlemci de `held` ile kapanıyor. Yalnız kuyruk kapansaydı, geri gelen
her karo hiçbir işe yaramayan bir gözlemci kurardı.

**Kontrol edilen tuzak 3:** `onError` kümeye yazmıyor. Tek bir `release` iki olayı da karşılasaydı
patlamış bir resim "gösterilmiş" sayılırdı.

**Kontrol edilen tuzak 4:** kanca `project` bağımlılığı taşıyor. Aynı ekran proje değiştirdiğinde
eskinin yeri yazılıp yeninin yeri okunuyor — `useGeneration` galeriyi zaten böyle değiştiriyor.

**Değişmeyen:** `image_queue.js` ve kuyruğun kuralları. Bu madde kuyruğa kimin girdiğini
değiştiriyor, kuyruğun kendisini değil.
