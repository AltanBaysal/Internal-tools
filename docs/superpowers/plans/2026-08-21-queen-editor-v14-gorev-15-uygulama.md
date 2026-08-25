# v14 Görev 15 — Galeri kartının görsel hizalaması: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün bıraktığı 12 kırmızıyı yeşile döndürmek: karonun dört köşesi, hapın
kutusu, borcun listeye dönmesi ve perdenin tonu.

**Architecture:** Üç dosya. Konum haptan köşe kutusuna taşınıyor (paylaşılan), galeri karosu o
kutuyu ve yeni rozet satırını çiziyor, detay sayfası kendi etiketini aynı kutuyla sarıyor.

**Tech Stack:** React 18, vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-15-galeri-karti-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor.**
- Yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor.**
- Commit **yeşil gider**.
- Ölçü kalıbın, renk hâlin: zemin ve iç boşluk her hapta, ton yalnız bekleyen ve kuyruktakinde.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/frame_status.jsx` | köşe kutusu, kalıbın ölçüsü, bekleyenin tonu | dört değişiklik |
| `.../photo_generation/Gallery.jsx` | rozetler, borç listesi, perde, düğme zemini | altı değişiklik |
| `.../photo_generation/PhotoDetail.jsx` | kendi etiketini köşeyle sarıyor | iki satır |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Köşe kutusu ve hapın kalıbı

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/frame_status.jsx`

**Interfaces:**
- Produces: `Corner({ children })` — `data-corner`, sol üst, sütun.
- Produces: `StatusPills({ states })` — `[{layer, state}]` alıyor, boşsa hiçbir şey.
- `Pill` ve `StatusPill` adları duruyor; `Pill` yalnız kutucuğun kendisi.

- [ ] **Step 1: Bekleyen iki hâlin tonu**

```jsx
const STATE = {
  // The palette's second grey, not its brightest ink: at 9px over a photograph the third one is a
  // label nobody can read, but this is the tone the ownership badge in the opposite corner already
  // carries at exactly this size (Fark 65). The other two states carry meaning in their colour.
  pending: { word: "kuyrukta", color: "var(--ink-2)", alive: false },
  // The same debt, with the queue standing still: "kuyrukta" claims movement, and a run that
  // stopped has none. Same ink -- a frame nobody is working on is no less worth reading.
  waiting: { word: "bekliyor", color: "var(--ink-2)", alive: false },
  running: { word: "üretiliyor", color: "var(--accent)", alive: true },
  failed: { word: "hata", color: "var(--danger)", alive: false },
};
```

- [ ] **Step 2: Konumu kutuya taşı, kalıbı genişlet**

`PILL` sabiti ikiye ayrılıyor:

```jsx
// Top left, the corner the design gives it (madde 57). It sat at the bottom for a while because
// the select ring owned this corner and appeared under the pointer, so the pill had to jump out of
// the way -- movement inside a card the user only pointed at. The ring moved to the opposite
// corner instead, and nothing here has to move again.
//
// The corner is the box rather than the pill's own position: a frame can be waiting for two layers
// at once, and the second label reads under the first (Fark 64).
const CORNER = {
  position: "absolute", top: 6, left: 6, zIndex: 2,
  display: "flex", flexDirection: "column", alignItems: "flex-start", gap: 3,
  // The corner is part of the card: a label must not turn it into a dead spot for drag or click.
  pointerEvents: "none",
};

// One mould whatever the state says, and measure is the mould's half: two labels standing one under
// the other on different grounds would read as a mistake. Colour is the caller's (Fark 65).
const PILL = {
  display: "flex", alignItems: "center", gap: 4,
  // Dark enough to carry the words over any picture, bright or not.
  background: "rgba(10,8,7,.7)", borderRadius: 3, padding: "3px 7px",
  fontSize: 9, lineHeight: 1.4,
};
```

- [ ] **Step 3: `Corner`, ve `Pill`'den konumun kalkması**

```jsx
/** The corner the labels stand in: top left, one under another.
 *
 * Exported so a page with a single sentence of its own puts it in the same place rather than
 * wherever its own layout happens to drop it.
 */
export function Corner({ children }) {
  return <span data-corner style={CORNER}>{children}</span>;
}

/** The label itself, with whatever words the caller has.
 *
 * Exported so a page that has its own sentence to put in that corner gets the same label rather
 * than a second one that looks almost like it.
 */
export function Pill({ color, alive, children }) {
  return (
    <span data-pill className="qe-pill wf-mono" style={{ ...PILL, color }}>
      {alive && (
        <span aria-hidden="true" className="qe-dot qe-dot--alive"
              style={{ background: "currentColor", width: 5, height: 5 }} />
      )}
      {children}
    </span>
  );
}
```

- [ ] **Step 4: `StatusPills`**

`StatusPill`'in altına:

```jsx
/** Every label a frame's state has earned, in the corner they belong in.
 *
 * An empty list draws no corner at all: a produced frame with nothing owed has the photo itself for
 * an answer, and what it owns is said by the badges in the corner below.
 */
export function StatusPills({ states }) {
  if (!states.length) return null;
  return (
    <Corner>
      {states.map(({ layer, state }) => <StatusPill key={layer} layer={layer} state={state} />)}
    </Corner>
  );
}
```

`StatusPill`'in kendi gövdesi ve yorumu değişmiyor.

---

### Task 2: Karonun rozetleri, borcu ve perdesi

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`

**Interfaces:**
- Consumes: `StatusPills`, `Corner` (dolaylı).

- [ ] **Step 1: İkonların içe aktarımı kalkıyor**

`import { PlayGlyph, SoundGlyph } from "./glyphs.jsx";` satırı ve `GLYPH` sabiti siliniyor.
`import { Rendering, StatusPill } from "./frame_status.jsx";` → `StatusPills`.

`glyphs.jsx` değişmiyor: `PlayGlyph`'i detay sayfasının video sekmesi kullanıyor.

- [ ] **Step 2: Rozet satırı ve rozetin kendisi**

`OWNS` sabiti şununla değişiyor:

```jsx
// Madde 57's third plane: the order badge top right, the state pill top left, and what the frame
// owns bottom left -- the corner across from it is left empty on purpose, so no two of them ever
// land on each other (Fark 60). It says the layer is finished; an unfinished one is the pill's to
// tell.
const OWNS = { position: "absolute", bottom: 6, left: 6, display: "flex", alignItems: "center",
               gap: 4, zIndex: 1, pointerEvents: "none" };
// A box per layer rather than two words sharing one (Fark 62), and the word stands in it alone --
// no icon rides with it (Fark 61, karar 21). The layers themselves and their words live next door,
// in the module the delete confirms count with -- the tile and the window say the same thing.
const OWN = { background: "rgba(10,8,7,.75)", color: "var(--ink-2)", padding: "2px 5px",
              borderRadius: 3 };
```

`Tile` içindeki çizim:

```jsx
        {owns.length > 0 && (
          <span data-owns style={OWNS}>
            {owns.map(({ layer, word }) => (
              <Mono key={layer} size={9} data-own style={OWN}>{word}</Mono>
            ))}
          </span>
        )}
```

- [ ] **Step 3: Perde ve düğmenin zemini**

`VEIL`'in zemini:

```jsx
// A layer that blew up on a frame that still has its picture: the way back rides an overlay CSS
// only brings down under the pointer, so the photo is never hidden for good (madde 67). The app's
// own brown black rather than a pure one -- the tone every other label on this card already stands
// on (Fark 75). How much of the photo shows through does not change.
const VEIL = { position: "absolute", inset: 0, display: "flex", alignItems: "center",
               justifyContent: "center", background: "rgba(10,8,7,.55)",
               borderRadius: "var(--r-sm)", zIndex: 3 };
```

`RetryButton` bir zemin alıyor:

```jsx
/** The way back from a failed render.
 *
 * Pressed once: the queue has taken it and the card only changes on the next poll, so the button
 * says so itself rather than sitting there ready for a second press (madde 69).
 *
 * `ground` is what it stands on. Under the veil that is the card's own colour, so the button reads
 * as a button rather than as a hole cut in the overlay (Fark 75). In the middle of an empty red
 * card it is already standing on a card, and a second ground there would be a box inside a box --
 * which is why none is the default and the one that wants one says so.
 */
function RetryButton({ frame, sent, ground = "transparent", onRetry }) {
  return (
    <Btn sm disabled={sent}
         onClick={(e) => { e.preventDefault(); e.stopPropagation(); if (!sent) onRetry(frame); }}
         style={{ color: "var(--danger)", borderColor: "var(--danger)", background: ground }}>
      {sent ? "Kuyruğa eklendi" : <><Icon.Regen /> Tekrar dene</>}
    </Btn>
  );
}
```

Perdenin içindeki çağrı `ground="var(--bg-2)"` alıyor; kırmızı karonun ortasındaki olduğu gibi
kalıyor.

- [ ] **Step 4: Borç bir liste**

```jsx
/** Everything worth saying about a frame's state, in the order it is read.
 *
 * Running first, then what blew up, then what is still owed. Only the debt is ever more than one:
 * a frame's video and its sound can both be waiting, and the corner stacks them (Fark 64). What the
 * worker is holding is a single job, and a card naming it beside two more would bury the picture
 * under it.
 *
 * No ceiling is written here because the queue is one: a frame whose photo has not landed takes no
 * layer job at all (queue_layer.frames_in_scope), so a photo's debt and a layer's never meet on one
 * frame and two is as high as this list goes.
 *
 * `flowing` is the queue's own state, not this frame's: an owed layer reads as queued while the
 * worker is moving through the list and as waiting once it has stopped. The debt is the same
 * either way; only the promise differs.
 */
function statusOf(frame, rendering, flowing) {
  if (rendering) return [{ layer: rendering, state: "running" }];
  const failed = (frame.failed || [])[0];
  if (failed) return [{ layer: failed, state: "failed" }];
  return (frame.owed || []).map((layer) => ({ layer, state: flowing ? "pending" : "waiting" }));
}
```

`Tile`'a giden satır:

```jsx
                      pill={<StatusPills states={statusOf(frame, rendering, running)} />}
```

- [ ] **Step 5: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: Gallery'nin 11 kırmızısı yeşile döner; `PhotoDetail` hâlâ bir kırmızı taşıyor.

---

### Task 3: Detay sayfasının köşesi

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`

- [ ] **Step 1: İçe aktarma**

`import { Pill, Rendering, StatusPill } from "./frame_status.jsx";` →
`import { Corner, Pill, Rendering, StatusPill } from "./frame_status.jsx";`

- [ ] **Step 2: İki etiketi köşeyle sar**

```jsx
            {sent.length > 0 ? (
              <Corner><Pill color="var(--accent)">yeniden üretilecek — kuyrukta</Pill></Corner>
            ) : coming ? (
              /* What the frame is waiting for, in the gallery's own words. A copy frame's page is
                 full of its source's picture, and this is the only thing that says the video is
                 still coming (madde 81). A failed layer gets no pill: the stage says that across
                 its whole width. */
              <Corner>
                <StatusPill layer={coming} state={running ? "running" : "pending"} />
              </Corner>
            ) : null}
```

Üstündeki yorum olduğu gibi kalıyor.

- [ ] **Step 3: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil — 384 / 474 / 694 / 454.

---

### Task 4: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

15. maddenin **İş** hücresi ✅ ile başlar, sayaç `14/31` → `15/31`. Satırın sonuna kararların notu
düşülür: *(28–31. kararlar: sürükleme, hover'daki numara, bırakma anı ve karışık seçim onayı bugünkü
hâlinde kalıyor — v4 fark listesi.)*

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): four corners on the gallery card, none of them crowded

What a frame owns moves to the bottom left and the corner across from it is left empty, so
the pill, the number and the badges never land on each other. Each layer takes a box of its
own instead of two words sharing one, and the word stands in it alone -- the icons are gone,
which the brief had already given back to the design.

A frame waiting for both its video and its sound now says both, the second under the first.
That is what turned the pills' position into a box of its own: two labels cannot stack while
each one carries its own top and left. The detail page shows a single label in the same
corner and reads it from the same place. No ceiling is written for the stack because the
queue is one -- a frame whose photo has not landed takes no layer job, so a photo's debt and
a layer's never meet and two is as high as it goes.

The waiting label steps down one grey. The argument for the brightest ink was that a faint
tone is unreadable at 9px over a photograph, and it still holds for the palette's third
grey -- but the ownership badge across the card has been carrying the second one at this
size all along. Ground and padding change on every pill and the ink on only these two: the
mould's half is the measure, the state's half is the colour, and a stack of two showing two
different grounds would read as a mistake.

The veil over a failed layer turns the brown black the rest of the card already stands on,
and the way back under it gets the card's own ground so it reads as a button rather than a
hole cut in the overlay. The same button in the middle of an empty red card keeps none: it
is already standing on a card.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in beş bölümü Task 1 (1, 3), Task 2 (2, 4, 5), Task 3 (1'in detay
sayfasındaki yüzü).

**Tip tutarlılığı:** `statusOf` artık her yolda **dizi** dönüyor — üçünün de dizi olduğu tek tek
kontrol edildi; `StatusPills` `states.length` okuyor, yani `null` dönen bir yol kalırsa orada
patlar.

**Kontrol edilen tuzak:** `key={layer}`. Aynı katman listede iki kez doğamıyor: üretilen tek,
patlayan tek, borç ise zaten katman başına bir satır.

**Kontrol edilen tuzak 2:** `pointerEvents` haptan köşeye taşındı. Hapta bırakılsaydı köşe kutusu
kartın üstünde ölü bir dikdörtgen olurdu — sürükleme ve tıklama oradan geçemezdi.

**Kontrol edilen tuzak 3:** `Mono` kendi `className`'ini yazıp `...rest`'i sonra yayıyor, yani
`data-own` geçiyor ama bir `className` verilseydi `wf-mono`'yu ezerdi. Rozete className
verilmiyor.

**Kontrol edilen tuzak 4:** `PlayGlyph` siliniyor sanılabilir; detay sayfasının sekme listesi onu
kullanıyor. Kalkan yalnız galerinin içe aktarımı.

**Değişmeyen:** `app.css`, `layer_words.js`, `glyphs.jsx`. Rozetin kelimeleri ve hover kuralları bu
maddenin konusu değil.
