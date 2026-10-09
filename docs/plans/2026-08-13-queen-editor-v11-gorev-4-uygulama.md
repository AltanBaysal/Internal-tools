# v11 Görev 4 — seçim kalkınca halkalar da kalkar: İMPLEMENTASYON döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `29848c8`'deki iki kırmızı testi yeşile çevirmek.

**Architecture:** `selecting` durumu siliniyor; mod `selected.length > 0`'dan türetiliyor.

**Tech Stack:** React 18, vitest, Vite build.

**Tasarım:** [implementasyon spec'i](../specs/2026-08-13-queen-editor-v11-gorev-4-uygulama-design.md)

## Global Constraints

- **Testler değişmiyor.** `29848c8`'deki dört test sözleşme.
- Yorum ve commit mesajı **İngilizce**.
- **`dist/` aynı commit'te** yeniden derlenir.
- Commit mesajında **çift tırnak yok**.
- Komutlar: `npm test --prefix queen-editor/frontend` · `npm run build --prefix queen-editor/frontend`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/Gallery.jsx` | seçim ve modu | 1 durum silinir, 3 yer sadeleşir |
| `queen-editor/frontend/dist/` | Colab'ın servis ettiği paket | yeniden derlenir |

---

### Task 1: Mod seçimden türetilir

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`

**Interfaces:**
- Consumes: yok. Produces: yok (dışarıdan görünen arayüz aynı).

- [ ] **Step 1: Durumu sil, türet**

Mevcut:

```js
  const [selecting, setSelecting] = useState(false);
  const [selected, setSelected] = useState([]);
```

Yerine:

```js
  const [selected, setSelected] = useState([]);
  // The mode IS the selection: rings on the cards while there is one, none while there is not.
  // Derived rather than a flag of its own, because the two drifting apart is exactly what left a
  // gallery covered in rings after its bar had already gone.
  const selecting = selected.length > 0;
```

- [ ] **Step 2: `closeSelection`'ı sadeleştir**

```js
  function closeSelection() {
    setSelected([]);
  }
```

- [ ] **Step 3: `toggle`'dan mod satırını çıkar**

```js
  function toggle(fid) {
    setSelected((current) => (current.includes(fid)
      ? current.filter((chosen) => chosen !== fid)
      : [...current, fid]));
  }
```

- [ ] **Step 4: Çubuğun koşulundaki ikizi tekleştir**

```js
      {/* The bar belongs to a selection, not to a mode alongside it: there is only the selection
          now, so having one is the whole condition. */}
      {selecting && (
```

- [ ] **Step 5: Ön yüz takımı**

Run: `npm test --prefix queen-editor/frontend`
Expected: 318 geçen, 0 düşen.

---

### Task 2: Derle ve commit'le

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Commit**

```bash
git add queen-editor/frontend/src queen-editor/frontend/dist docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): end the selection mode with the selection

The two failing tests from the previous commit go green.

The gallery kept the mode in a flag of its own beside the list of chosen frames,
and only one of the two was cleared when the last card was let go: the bar read
the list and went, the rings read the flag and stayed. A gallery covered in
rings with nothing on screen saying a selection was open.

The flag is gone. The mode is the selection being non-empty, so the two cannot
disagree -- and the bar's condition, which used to ask both, now asks the one
thing there is.

What this costs, plainly: letting the last card go ends the mode, so the next
click on a card opens the photo instead of picking it. Picking up again goes
through the ring, which appears under the pointer -- the same way it worked
after Vazgeç. The click that empties the selection still does not navigate: the
link reads the mode as it was when the click began.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** türetme→Task 1 Step 1 · `closeSelection`→Step 2 · `toggle`→Step 3 · çubuğun
koşulu→Step 4 · `dist/`→Task 2. Eksik yok.

**Sözleşmeye uyum:** dört test de sınıfı okuyor; sınıf `selecting`ten yazılıyor, `selecting` artık
listeden türüyor. Modu tümden kaldırma riski, geçmekte olan iki test tarafından kapalı.

**Kontrol edilen yan etki:** `setSelecting` başka hiçbir yerde çağrılmıyor; Esc dinleyicisi ve alt
boşluk `selecting`i okuyor, ikisi de türetilmiş değerle aynı şekilde çalışıyor.
