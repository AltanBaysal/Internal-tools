# v11 Görev 5 — kare köşeleri yeniden dağıtılır: İMPLEMENTASYON döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `527393a`'daki beş kırmızı testi yeşile çevirmek.

**Architecture:** İki satır içi konum yer değiştiriyor, rozet CSS'in tutunacağı bir sınıf kazanıyor
ve satır içi opaklığını CSS'e bırakıyor.

**Tech Stack:** React 18, CSS, vitest, Vite build.

**Tasarım:** [implementasyon spec'i](../specs/2026-08-13-queen-editor-v11-gorev-5-uygulama-design.md)

## Global Constraints

- **Testler değişmiyor.** `527393a`'daki beş test sözleşme.
- Yorum ve commit mesajı **İngilizce**.
- **`vendor/` elle düzenlenmez** — `Mono`'nun `className` davranışı çağrı yerinde karşılanır.
- **`dist/` aynı commit'te** yeniden derlenir.
- Commit mesajında **çift tırnak yok**.
- Komutlar: `npm test --prefix queen-editor/frontend` · `npm run build --prefix queen-editor/frontend`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/frame_status.jsx` | etiketin köşesi | `PILL` konumu + yorum |
| `.../photo_generation/Gallery.jsx` | halkanın köşesi, rozetin sınıfı | `CHECK` konumu, rozet elemanı |
| `.../shared/app.css` | rozetin görünürlüğü | 3 kural |
| `queen-editor/frontend/dist/` | Colab'ın servis ettiği paket | yeniden derlenir |

---

### Task 1: Etiket sol üste

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/frame_status.jsx`

- [ ] **Step 1: `PILL`'i taşı ve yorumu düzelt**

```js
// Top left, the corner the design gives it (madde 57). It sat at the bottom for a while because
// the select ring owned this corner and appeared under the pointer, so the pill had to jump out of
// the way -- movement inside a card the user only pointed at. The ring moved to the opposite
// corner instead, and nothing here has to move again.
const PILL = {
  position: "absolute", top: 6, left: 6, zIndex: 2,
```

Geri kalanı aynı.

---

### Task 2: Halka sağ üste, rozet CSS'e tutunur

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`

- [ ] **Step 1: `CHECK`'i taşı**

```js
// The ✓ ring sits where the order badge is, and the badge steps aside for it (see app.css): while
// frames are being picked, what is looked at is the pictures, not the numbering. Its visibility is
// CSS's job -- it appears on hover while browsing, and stays on for every tile once the mode is
// open.
const CHECK = { position: "absolute", top: 6, right: 6, width: 18, height: 18, borderRadius: "50%",
```

- [ ] **Step 2: `BADGE`'ten satır içi opaklığı çıkar, sınıfı ver**

Mevcut:

```jsx
        {badge != null && (
          <Mono size={10} style={muted ? { ...BADGE, opacity: 0.5 } : BADGE}>{badge}</Mono>
        )}
```

Yerine:

```jsx
        {/* wf-mono is repeated on purpose: the kit's Mono writes its own className before spreading
            the rest, so a className passed in replaces it rather than joining it -- and vendor/ is
            not ours to edit. The dim tone for a frame with no photo yet is a class rather than an
            inline style, because an inline opacity would beat the rule in app.css that takes the
            number away when the ring arrives. */}
        {badge != null && (
          <Mono size={10} className={muted ? "wf-mono qe-badge qe-badge--muted" : "wf-mono qe-badge"}
                style={BADGE}>{badge}</Mono>
        )}
```

---

### Task 3: Rozet halkanın belirdiği yerde çekilir

**Files:**
- Modify: `queen-editor/frontend/src/shared/app.css`

- [ ] **Step 1: `.qe-check` kurallarının hemen altına ekle**

```css
/* The order badge shares the top right corner with the ✓ ring, so it steps aside in exactly the
   two states where the ring steps in. Its dim tone for a frame that is not a photo yet lives here
   too: as an inline style it would outrank these rules and the number would never leave. */
.qe-badge {
  transition: opacity 0.12s;
}

.qe-badge--muted {
  opacity: 0.5;
}

.qe-tile:hover .qe-badge,
.qe-tile--selecting .qe-badge {
  opacity: 0;
}
```

- [ ] **Step 2: Ön yüz takımı**

Run: `npm test --prefix queen-editor/frontend`
Expected: 322 geçen, 0 düşen.

---

### Task 4: Derle ve commit'le

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`
Expected: `dist/` yeniden yazılır — bu kez CSS hash'i de değişir.

- [ ] **Step 2: Commit**

```bash
git add queen-editor/frontend/src queen-editor/frontend/dist docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): give the state pill the corner the design asks for

The five tests from the previous commit go green.

The pill goes to the top left and the select ring to the top right, opposite it.
The ring used to own the top left and appear under the pointer, which is why the
pill had been pushed to the bottom: two things in one corner meant one of them
jumped whenever a card was pointed at.

The order badge already lives in the top right, so it steps aside wherever the
ring steps in -- the same two states, hover and selection mode, mirrored in
app.css. Nothing moves: a number leaving is not a label sliding.

Two things had to be handled for that to work at all. The kit's Mono writes its
own className before spreading the rest, so the badge names both classes itself;
vendor is not ours to edit. And the badge's dim tone moved out of the inline
style, because an inline opacity outranks a stylesheet rule -- the number would
have stayed put under the ring, with every position test passing.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** etiket→Task 1 · halka→Task 2 Step 1 · rozetin sınıfı ve opaklığı→Task 2 Step 2 ·
CSS→Task 3 · `dist/`→Task 4. Eksik yok.

**Belirginlik kontrolü:** `.qe-tile:hover .qe-badge` (0,2,0) ile `.qe-badge--muted` (0,1,0) —
gizleme kazanıyor, sönük ton yalnız kimse bakmıyorken geçerli. Doğru sıra.

**Sözleşmeye uyum:** testler `.qe-badge` seçicisini, `top/right/left` satır içi değerlerini ve
`app.css`'te iki seçiciyi arıyor; dördü de bu planda birebir yazılı.
