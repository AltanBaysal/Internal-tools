# v11 Görev 6 — LLM açıklamaları kalkar: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** İki test; ikisi de kırmızı. Kod bu döngüde değişmiyor.

**Architecture:** Bir mevcut test tersine çevriliyor, ses paneline eşi yazılıyor.

**Tech Stack:** vitest + @testing-library/react, jsdom.

**Tasarım:** [test spec'i](../specs/2026-08-13-queen-editor-v11-gorev-6-testler-design.md)

## Global Constraints

- **Kod değişmiyor.** `LayerPanel.jsx` bu commit'te olduğu gibi kalır; `dist/` yeniden derlenmez.
- **Kırmızı bırakılır.**
- Test adları ve yorumlar **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- Test komutu: `npm test --prefix queen-editor/frontend`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/LayerPanel.test.jsx` | panelin ne söylediği | 1 test tersine çevrilir, 1 eklenir |

---

### Task 1: İki panelin de sustuğunu yaz

**Files:**
- Test: `queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx`

**Interfaces:**
- Consumes: `renderPanel()`, `renderSound()`.
- Produces: yok.

- [ ] **Step 1: Video testini tersine çevir**

Mevcut *"says who writes the prompt, since it never asks for one"* testinin yerine:

```js
  it("does not explain who writes the prompt -- the frame's own page does", () => {
    // The sentence was read once and then took up room at the foot of the panel on every open.
    // Where a prompt is actually read -- the frame's page -- an empty one still says that the
    // language model will write it when its turn comes.
    renderPanel();

    expect(screen.queryByText(/LLM/)).toBeNull();
  });
```

- [ ] **Step 2: Ses paneline eşini ekle**

`LayerPanel — sound` describe'ının sonuna:

```js
  it("does not explain who writes the prompt either", () => {
    // Both panels are one component and the design asks for them to be identical; leaving the
    // sentence on one of them would part them where nothing else does.
    renderSound();

    expect(screen.queryByText(/LLM/)).toBeNull();
  });
```

- [ ] **Step 3: İkisinin de düştüğünü gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: 2 düşen — ikisi de `expected ... not to be null` benzeri, yani cümle hâlâ ekranda.

---

### Task 2: Kırmızıyı doğrula ve commit'le

- [ ] **Step 1: Tam ön yüz takımı**

Run: `npm test --prefix queen-editor/frontend`
Expected: 322 + 1 = 323; 2 düşen, 321 geçen.

- [ ] **Step 2: Kaynak koda dokunulmadığını doğrula**

Run: `git status --short`
Expected: yalnız `LayerPanel.test.jsx` ve `docs/superpowers`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): stop the layer panels explaining who writes the prompt

THESE TWO TESTS FAIL ON PURPOSE. The fix is the next commit.

The sentence at the foot of the video and sound panels says a language model
writes the prompt. It is read once and then occupies the panel on every open,
and where a prompt is actually read -- the frame's own page -- an empty one
already says the model will write it when its turn comes.

One of these tests is the old one turned around: it used to look for the
sentence. The other is new, because the sound panel never had one, and the two
panels are a single component that the design asks to be identical -- a rule
written for only one of them is how they drift.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** K1→Task 1 Step 1 · K2→Step 2. Eksik yok.

**Seçici notu:** `queryByText(/LLM/)` cümlenin tam metnini değil, ondan söz eden herhangi bir satırı
arıyor. Metin ileride yeniden yazılırsa test yine tutar — aranan şey bir cümle değil, o bilginin
panelde olmaması.
