# v14 Görev 10 — Toplu kart taşıma: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün kırmızı bıraktığı altı testi yeşile döndürmek: seçim sürüklemeye katılsın,
blok olarak insin, ve ekrana hiçbir şey eklenmesin.

**Architecture:** Tek dosya, dört değişiklik. "Kim taşınıyor" sorusunun tek bir cevabı var ve hem
bırakma hem görünüm onu okuyor.

**Tech Stack:** React 18, vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-10-toplu-tasima-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor — bir silme dışında.** `lets nothing be dragged while a
  selection is open`, bu maddenin bilerek tersine çevirdiği cümleyi tutuyor. Silinmesi test turunun
  işiydi; atlanmış, burada tamamlanıyor. Yerini test turunun 6. testi alıyor ve aynı özniteliğe
  bakıp tersini söylüyor — yani kural nöbetsiz kalmıyor.
- Yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor.**
- Commit **yeşil gider**.
- **Tek kartın davranışı değişmiyor.** `Gallery ordering` bloğunun iki sürükleme testi bunun
  nöbeti; kırılırlarsa genelleme yanlış.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `frontend/src/features/photo_generation/Gallery.jsx` | sürükleme | `moving`, `handleDrop`, `dragging`, `draggable` |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Kim taşınıyor

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`

**Interfaces:**
- Produces: `moving` — taşınan kimliklerin galeri sırasındaki listesi, sürükleme yokken boş. Task 2
  ve Task 3 okuyor.

- [ ] **Step 1: Listeyi hesapla**

`handleDrop`'un tanımının üstüne, `confirm` hesabının altına:

```jsx
  // Who is moving, as one answer for the whole drag: a selected card takes the selection with it,
  // an unselected one goes alone. In the gallery's own order rather than the selection's, because
  // the selection is a list of presses -- picking a block from the bottom up would otherwise turn
  // it over on landing.
  const dragged = dragIndex === null ? null : frames[dragIndex].id;
  const moving = dragged === null
    ? []
    : selected.includes(dragged)
      ? frames.map((frame) => frame.id).filter((fid) => selected.includes(fid))
      : [dragged];
```

- [ ] **Step 2: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: altı kırmızı duruyor — listeyi henüz kimse okumuyor.

---

### Task 2: Blok iniyor

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`

**Interfaces:**
- Consumes: Task 1'in `moving`'i.

- [ ] **Step 1: `handleDrop`'u yaz**

```jsx
  function handleDrop() {
    const to = overIndex;
    const block = moving;
    setDragIndex(null);
    setOverIndex(null);
    if (to === null || !block.length) return;
    const ids = frames.map((frame) => frame.id);
    // Everything moving comes out, then goes back in starting at the slot's index. One card is this
    // rule with a single element, which is why dragging one has not changed.
    const next = ids.filter((fid) => !block.includes(fid));
    next.splice(to, 0, ...block);
    // Compared, not counted: dropping the second card of a block on its first leaves the sequence
    // exactly as it was while the two indices still differ.
    if (next.every((fid, index) => fid === ids[index])) return;
    // The whole sequence is sent, pending frames included: the order covers them too now.
    onReorder(next);
  }
```

- [ ] **Step 2: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: dört test yeşile döner (1, 2, 3, 9). 6 ve 7 kırmızı kalır. `Gallery ordering`'in iki
sürükleme testi hâlâ yeşil.

---

### Task 3: Blok sürüklenen gibi görünüyor ve seçim sürüklemeyi kapatmıyor

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`

**Interfaces:**
- Consumes: Task 1'in `moving`'i.

- [ ] **Step 1: `dragging`'i genişlet**

Karo döngüsü içinde:

```jsx
          const dragging = moving.includes(frame.id);
```

`isSlot` satırı olduğu gibi kalıyor: `!dragging` artık bloğun tamamını kapsıyor, ve yuva
göstergesinin kendisi değişmiyor.

- [ ] **Step 2: `draggable`'ı aç**

```jsx
              // Draggable from the start, not after a hold: the browser decides at mousedown
              // whether a press may become a drag, so a tile armed 250 ms later was never a drag
              // source at all -- the gallery simply could not be reordered. Every card can be
              // picked up whatever became of it, because the sequence a drag makes is the sequence
              // the queue produces in. A selection does not close this: a completed drag never ends
              // in a click, so a press can still mean a selection without the two colliding.
              draggable
```

- [ ] **Step 3: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil.

---

### Task 4: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

10. maddenin **İş** hücresi ✅ ile başlar, sayaç `9/31` → `10/31`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the selection travels with the card that is dragged

Picking up a selected card now moves every selected card, as one block, in the gallery's
own order. A scattered selection lands side by side where it was dropped and the cards
between it close the gap. An unselected card still goes alone and leaves the selection
where it is.

Dragging is no longer switched off while frames are selected. That was the whole reason
a sequence could only be moved a card at a time, losing its own order on the way. A
press can still be a selection: a completed drag never ends in a click.

The block is the single card's rule with more than one element -- everything moving is
lifted out, then put back starting at the slot's index -- so dragging one card behaves
exactly as it did.

Who is moving is worked out once per drag and read by both the drop and the look. The
dragged effect spreads over the block and nothing else appears: no count, no stack, no
ghost, and the slot indicator is the one that was already there.

Whether to write the order is decided by comparing the sequence rather than the indices.
Dropping a block's second card on its first leaves everything where it was, and the two
indices still differ.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in dört parçası sırayla Task 1, 2, 3, 3.

**Tip tutarlılığı:** `moving` her yerde kimlik dizisi; `handleDrop` ve `dragging` aynı değeri
okuyor, yani "kim taşınıyor" iki kez hesaplanmıyor.

**Kontrol edilen tuzak:** `handleDrop` `moving`'i yerel bir değişkene alıyor (`const block = moving`)
**önce**, `setDragIndex(null)` sonra. Durum güncellemeleri toplu olduğu için bu render'da `moving`
zaten sabit; yerel kopya, sırayı okuyan birinin bunu doğrulamak zorunda kalmaması için.

**Kontrol edilen tuzak 2:** `from` artık hiç kullanılmıyor. `dragIndex`'i `moving`'in içinde
tükettik; bırakma noktası yalnız `to`. Eski `from === to` korumasını bırakmak, dizi
karşılaştırmasıyla değiştirildiği için güvenli.

**Kontrol edilen tuzak 3:** `!block.length` koruması, sürükleme hiç başlamadan bir `drop` gelirse
diziyi bozmuyor — bugünkü `from === null` korumasının karşılığı.

**Kontrol edilen tuzak 4:** dizi karşılaştırması uzunluk kontrolü içermiyor, çünkü `next` her zaman
`ids` ile aynı uzunlukta: çıkarılan ve geri konan aynı küme.

**Değişmeyen:** `Gallery ordering`'in iki sürükleme testi. Task 2'den sonra hâlâ yeşil olmaları,
genellemenin tek kartı bozmadığının kanıtı.