# v11 Görev 3 — duran üretim kuyrukta görünmez: İMPLEMENTASYON döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `1577dc3`'teki beş kırmızı testi yeşile çevirmek.

**Architecture:** Ekranın zaten hesapladığı "kuyruk bu projede akıyor mu" cevabı galeriye bir prop
olarak iniyor; galeri onu `statusOf`'a veriyor; `statusOf` borcun kelimesini ona göre seçiyor.

**Tech Stack:** React 18, vitest, Vite build.

**Tasarım:** [implementasyon spec'i](../specs/2026-08-13-queen-editor-v11-gorev-3-uygulama-design.md)

## Global Constraints

- **Testler değişmiyor.** `1577dc3`'teki beş test sözleşme.
- Yorum ve commit mesajı **İngilizce**; arayüz metni Türkçe.
- **`dist/` aynı commit'te** yeniden derlenir.
- Commit mesajında **çift tırnak yok**.
- Komutlar: `npm test --prefix queen-editor/frontend` · `npm run build --prefix queen-editor/frontend`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/frame_status.jsx` | durum → kelime eşlemesi | 1 satır eklenir |
| `.../photo_generation/Gallery.jsx` | kareye ne yazılacağı | prop + yeniden adlandırma |
| `.../photo_generation/ProjectScreen.jsx` | bilginin aşağı inmesi | 1 satır |
| `queen-editor/frontend/dist/` | Colab'ın servis ettiği paket | yeniden derlenir |

---

### Task 1: Sözlüğe bekleyen hâli eklenir

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/frame_status.jsx`

**Interfaces:**
- Produces: `STATE.waiting` — `statusOf`'un döndürebileceği yeni durum adı.

- [ ] **Step 1: `STATE`'e satırı ekle**

```js
const STATE = {
  // The brightest ink, not a quiet grey: 9px over a photograph, a dim tone is not a soft label but
  // an unreadable one. The other two carry meaning in their colour and are bright already.
  pending: { word: "kuyrukta", color: "var(--ink)", alive: false },
  // The same debt, with the queue standing still: "kuyrukta" claims movement, and a run that
  // stopped has none. Same ink -- a frame nobody is working on is no less worth reading.
  waiting: { word: "bekliyor", color: "var(--ink)", alive: false },
  running: { word: "üretiliyor", color: "var(--accent)", alive: true },
  failed: { word: "hata", color: "var(--danger)", alive: false },
};
```

`StatusPill` değişmiyor: tabloyu okuyor, tablo büyüdü.

---

### Task 2: Galeri kuyruğun hâlini öğrenir

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`

**Interfaces:**
- Consumes: yeni `running` prop'u (boolean).
- Produces: yok.

- [ ] **Step 1: `statusOf`'a üçüncü argümanı ekle**

```js
/** The one thing worth saying about a frame's state, or nothing at all.
 *
 * Running first, then what blew up, then what is still owed: a frame can be several of these at
 * once -- its photo failed while its video waits -- and two pills in one corner make the card
 * unreadable. The rest is the detail page's to show.
 *
 * `flowing` is the queue's own state, not this frame's: an owed layer reads as queued while the
 * worker is moving through the list and as waiting when it has stopped. The debt is the same
 * either way; only the promise differs.
 */
function statusOf(frame, rendering, flowing) {
  if (rendering) return { layer: rendering, state: "running" };
  const failed = (frame.failed || [])[0];
  if (failed) return { layer: failed, state: "failed" };
  const owed = (frame.owed || [])[0];
  if (owed) return { layer: owed, state: flowing ? "pending" : "waiting" };
  return null;
}
```

- [ ] **Step 2: Prop'u imzaya ekle**

```js
export default function Gallery({ project, frames, current, currentLayer, running, onReorder,
                                  onDelete, onRetry, onSelectionChange }) {
```

- [ ] **Step 3: Kare döngüsündeki yerel `running`'i `rendering` yap**

Üç kullanım, hepsi aynı döngüde:

```js
          // Which layer of this frame the worker is holding, if any -- not to be confused with
          // `running`, the prop above, which says whether the queue is moving at all.
          const rendering = frame.id === current ? (currentLayer || "photo") : null;
          const state = rendering === "photo" ? "running" : frame.status;
```

ve

```js
                      pill={<StatusPill {...(statusOf(frame, rendering, running) || {})} />}
```

- [ ] **Step 4: Galeri testlerini koş**

Run: `npm test --prefix queen-editor/frontend`
Expected: `Gallery.test.jsx` yeşil; `ProjectScreen.test.jsx`'te iki test hâlâ kırmızı (prop henüz
geçmiyor).

---

### Task 3: Ekran bildiğini galeriye söyler

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx`

**Interfaces:**
- Consumes: mevcut `running` değişkeni (satır 39).
- Produces: yok.

- [ ] **Step 1: Galeriye geçir**

```jsx
          <Gallery project={project} frames={frames} current={current} currentLayer={currentLayer}
                   running={running}
                   onReorder={reorder} onDelete={removePhotos} onRetry={retry}
                   onSelectionChange={setSelected} />
```

- [ ] **Step 2: Tam ön yüz takımı**

Run: `npm test --prefix queen-editor/frontend`
Expected: 314 geçen, 0 düşen.

---

### Task 4: Derle ve commit'le

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Commit**

```bash
git add queen-editor/frontend/src queen-editor/frontend/dist docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): stop a halted queue from promising movement

The five tests from the previous commit go green.

A frame with an owed layer said kuyrukta whatever the queue was doing, so a run
that stopped on a dead xAI key left a gallery full of frames announcing work
nobody was doing. The debt is real -- Devam et still produces those videos -- so
the fix is the word, not the state: an owed layer reads as bekliyor while the
queue stands still.

The gallery could not have picked that word before, because nothing told it
whether the queue was moving. The screen already knew -- it computes exactly
that to decide whether a batch is this project's -- and now says so.

The loop's local running is renamed to rendering, which is what it always meant:
the layer of this one frame that the worker holds. Left as it was it would have
shadowed the new prop, and both values look plausible in that spot.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** kelime tablosu→Task 1 · kararın `statusOf`'ta olması→Task 2 Step 1 · prop
threading→Task 2 Step 2 ve Task 3 · ad çakışması→Task 2 Step 3 · `dist/`→Task 4. Eksik yok.

**Sözleşmeye uyum:** galeri prop'u `running` — testlerin `renderGallery({ ..., running: true })`
ile çağırdığı ad. `statusOf`'un üçüncü parametresi `flowing` adını taşıyor ama o bileşenin içi;
testler onu görmüyor.

**Dikkat:** Task 2 Step 3 üç satırı birden değiştiriyor. İkisini değiştirip üçüncüsünü unutmak
`rendering is not defined` verir — sessiz bir hata değil, o yüzden risk düşük.
