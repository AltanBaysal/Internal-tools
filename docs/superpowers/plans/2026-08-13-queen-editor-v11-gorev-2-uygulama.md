# v11 Görev 2 — seçili kare sayısı: İMPLEMENTASYON döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `03c5f77`'deki beş kırmızı testi yeşile çevirmek.

**Architecture:** Video/ses paneli, galerinin seçimini karenin kimliğiyle eşler; kuyruğa gönderdiği
şey eskisi gibi dosya adı kalır.

**Tech Stack:** React 18, vitest, Vite build.

**Tasarım:** [implementasyon spec'i](../specs/2026-08-13-queen-editor-v11-gorev-2-uygulama-design.md)

## Global Constraints

- **Testler değişmiyor.** `03c5f77`'deki beş test sözleşme.
- Yorum ve commit mesajı **İngilizce**; arayüz metni Türkçe (bu görevde arayüz metni değişmiyor).
- **`dist/` aynı commit'te** yeniden derlenir — Colab derlenmiş arayüzü olduğu gibi servis ediyor.
- Commit mesajında **çift tırnak yok**.
- Komutlar: `npm test --prefix queen-editor/frontend` · `npm run build --prefix queen-editor/frontend`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx` | seçimin hangi anahtarla eşleştiği | 1 satır + yorum |
| `queen-editor/frontend/dist/` | Colab'ın servis ettiği paket | yeniden derlenir |

---

### Task 1: Panel seçimi kimlikle eşler

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`

**Interfaces:**
- Consumes: `selected` (kimlik listesi, `ProjectScreen` → `SidePanel` üzerinden galeriden gelir),
  `frames`.
- Produces: `onQueue(files, variants)` — dosya adları, değişmiyor.

- [ ] **Step 1: `inSelection`'ı kimliğe çevir**

Mevcut:

```js
  const inSelection = can.filter((frame) => chosen.includes(frame.file));
```

Yerine:

```js
  // By identity, not by file name: asking for a second video makes a copy frame, and the copy
  // shows the same photo -- so a file name cannot tell two frames apart and the gallery keeps its
  // selection as identities for exactly that reason. What goes to the queue below is still the
  // file name; the two are three lines apart so neither can be changed without seeing the other.
  const inSelection = can.filter((frame) => chosen.includes(frame.id));
```

- [ ] **Step 2: Ön yüz takımını koş**

Run: `npm test --prefix queen-editor/frontend`
Expected: 309 geçen, 0 düşen.

---

### Task 2: Derle ve commit'le

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`
Expected: `dist/` yeniden yazılır (JS hash'i değişir).

- [ ] **Step 2: Commit**

```bash
git add queen-editor/frontend/src queen-editor/frontend/dist docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): count the frames the gallery actually picked

The five tests from the previous commit go green.

The gallery keeps its selection as frame identities, deliberately: asking for a
second video makes a copy frame showing the same photo, and a file name cannot
tell those two apart. The video panel was comparing that selection against file
names, so the count never left zero and the row stayed out of reach.

The panel now matches on identity and still sends file names to the queue --
three lines apart, so neither can be changed without seeing the other. The
gallery is untouched: closing this from its end would have traded a visible
wrong count for a silent one.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** kimlikle eşleme→Task 1 · dosya adının korunması→değişmeyen satır, yorumla
bağlandı · `dist/`→Task 2. Spec'te olup planda olmayan madde yok.

**Sözleşmeye uyum:** beş testin beşi de bu tek satırla yeşile döner — dördü panelin sayısını, biri
ekranın dikişini okuyor, hepsi aynı filtreden geçiyor. Testlere dokunulmuyor.

**Gözden geçirilen alternatif:** galerinin dosya adı yayınlaması. Reddedildi, sebebi spec'te; ikiz
kare testi zaten o yolu geçirmez.
