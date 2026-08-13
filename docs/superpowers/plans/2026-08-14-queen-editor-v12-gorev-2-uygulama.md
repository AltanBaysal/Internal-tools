# v12 Görev 2 — Sürükleme: İMPLEMENTASYON döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `20f7528`'deki beş kırmızı testi yeşile çevirmek ve v12'yi kapatmak.

**Architecture:** Tek dosyadan bir mekanizma siliniyor; `draggable` bir koşula iniyor.

**Tech Stack:** React 18, vitest, Vite build.

**Tasarım:** [implementasyon spec'i](../specs/2026-08-14-queen-editor-v12-gorev-2-uygulama-design.md)

## Global Constraints

- **Testler değişmiyor.** `20f7528`'deki altı test sözleşme.
- Yorum ve commit mesajı **İngilizce**.
- **`dist/` aynı commit'te** yeniden derlenir.
- Commit mesajında **çift tırnak yok**.
- Komutlar: `npm test --prefix queen-editor/frontend` · `npm run build --prefix queen-editor/frontend`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/Gallery.jsx` | galerinin davranışı | tutuş mekanizması silinir |
| `queen-editor/frontend/dist/` | Colab'ın servis ettiği paket | yeniden derlenir |

---

### Task 1: Tutuş mekanizması silinir

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`

- [ ] **Step 1: `HOLD_MS` sabitini ve yorumunu sil**

```js
// Long enough that a press-and-slide does not become a drag, short enough that a deliberate hold
// does not feel stuck. The design asks for a hold; the number is ours.
const HOLD_MS = 250;
```

tümüyle çıkar.

- [ ] **Step 2: `armed` durumu ve `hold` referansını sil**

```js
  // A tile can only be picked up after it has been held: this is the one that is armed.
  const [armed, setArmed] = useState(null);
```

ve

```js
  const hold = useRef(null);
```

çıkar.

- [ ] **Step 3: Zamanlayıcıyı temizleyen efekti sil**

```js
  useEffect(() => () => clearTimeout(hold.current), []);
```

çıkar.

- [ ] **Step 4: `press` ve `release` fonksiyonlarını sil**

Yorumlarıyla birlikte:

```js
  // Every card can be picked up, whatever became of it: the sequence a drag makes is the sequence
  // the queue produces in, so a frame with no pixels yet is exactly the one worth moving.
  function press(fid) {
    clearTimeout(hold.current);
    hold.current = setTimeout(() => setArmed(fid), HOLD_MS);
  }

  function release() {
    clearTimeout(hold.current);
    setArmed(null);
  }
```

çıkar. Sildiği cümle kaybolmuyor — bir sonraki adımda `draggable`'ın yanına iniyor.

- [ ] **Step 5: `useRef` import'unu sil**

`hold` bu dosyanın tek referansıydı:

```js
import { useEffect, useState } from "react";
```

- [ ] **Step 6: Karo hep sürüklenebilir olsun**

Karo `<div>`'ünde şu dört satır:

```jsx
              draggable={armed === frame.id && !selecting}
              onMouseDown={() => !selecting && press(frame.id)}
              onMouseUp={release}
              onMouseLeave={release}
```

şununla değişir:

```jsx
              // Draggable from the start, not after a hold: the browser decides at mousedown
              // whether a press may become a drag, so a tile armed 250 ms later was never a drag
              // source at all -- the gallery simply could not be reordered. Every card can be
              // picked up whatever became of it, because the sequence a drag makes is the
              // sequence the queue produces in.
              draggable={!selecting}
```

- [ ] **Step 7: `onDragEnd` artık bırakacak bir şey bulmuyor**

```jsx
              onDragEnd={() => { setDragIndex(null); setOverIndex(null); release(); }}
```

→

```jsx
              onDragEnd={() => { setDragIndex(null); setOverIndex(null); }}
```

- [ ] **Step 8: Ön yüz takımı**

Run: `npm test --prefix queen-editor/frontend`
Expected: 324 geçen, 0 düşen.

---

### Task 2: Derle, yol haritasını kapat, commit'le

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasının durumunu güncelle**

`docs/superpowers/plans/2026-08-14-queen-editor-v12-roadmap.md` başlığındaki
`**Durum:** 0/2` → `**Durum:** 2/2 — bitti, Colab turu bekliyor`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor/frontend/src queen-editor/frontend/dist docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): let a tile be dragged the moment it is pressed

The five tests from the previous commit go green, and v12 closes.

A tile became draggable 250 ms after it was pressed. The browser decides at
mousedown whether a press may become a drag, so by the time the attribute
arrived the press had already been read as a text selection -- and the gallery
could not be reordered at all, however deliberately it was held.

The hold goes with it: the state, the timer, the ref, the two functions and
the three mouse handlers that fed them. Keeping it would have meant writing a
drag of our own, and the thing it guarded against -- a slide becoming a drag
-- is what the browser is already threshold for.

What a tile loses is that its file name can no longer be selected with the
mouse, which is what being draggable costs. The name is still selectable on
the frame s own page.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** mekanizmanın silinmesi → Step 1-5, 7 · `draggable` → Step 6 · `dist/` → Task 2.
Eksik yok.

**Kontrol edilen bağ:** `selecting` hâlâ kullanılıyor (sınıf adı, `onClick`, alt çubuk), yani
Step 6 onu öksüz bırakmıyor.

**Kontrol edilen import:** `useEffect` iki efekt için duruyor (seçim yankısı, Escape tuşu);
`useState` beş durum için duruyor. Yalnız `useRef` öksüz kalıyor ve Step 5 onu alıyor.

**Kontrol edilen kayıp:** silinen yorumun söylediği şey ("her kart kalkar, çünkü sürüklemenin
kurduğu sıra üretimin sırasıdır") Step 6'nın yorumunda korunuyor — kural kodda kalırken gerekçesi
kaybolmasın.
