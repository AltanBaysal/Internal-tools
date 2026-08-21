# v14 Görev 13 — Seçim barının görünümü: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün bıraktığı üç testi yeşile döndürmek: bar sıkışsın, yazılar bölünmesin,
bekleyen kare varsa katman düğmeleri doğmasın.

**Architecture:** Tek dosya, iki değişiklik. Biri bir biçim sabiti, öbürü bir koşul.

**Tech Stack:** React 18, vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-13-secim-bari-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor.**
- Yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor.**
- Commit **yeşil gider**.
- **Barın konumu değişmiyor** — `BAR_RAIL`'in `bottom: 28`'i ve yorumu olduğu gibi kalıyor.
- **Kopyala'nın koşulu değişmiyor**: karışık seçimde duruyor (Fark 79).

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `frontend/src/features/photo_generation/Gallery.jsx` | bar | `BAR`, katman düğmelerinin koşulu |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Barın biçimi

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`

- [ ] **Step 1: `BAR`'ı düzelt**

```jsx
// 10, not 14: the bar was designed with three buttons and carries six now (Fark 83). Nothing may
// break in two -- nowrap keeps a label on one line, and with it a flex item cannot shrink below its
// own text either. The other half of never wrapping, items falling to a second row, is what flex
// already does by default.
const BAR = { display: "flex", alignItems: "center", gap: 10, padding: "10px 18px",
              borderColor: "var(--accent)", pointerEvents: "auto", whiteSpace: "nowrap" };
```

- [ ] **Step 2: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: iki test yeşile döner; katman düğmelerinin testi kırmızı kalır.

---

### Task 2: Katman düğmelerinin koşulu

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`

- [ ] **Step 1: Koşulu ekle**

Bardaki `LAYER_ACTIONS.map` bloğu, yorumuyla birlikte:

```jsx
            {/* One per layer, to the right of Sil and dressed like it. Two conditions: nothing in
                the selection may still be waiting -- what these take off is a finished stack, and
                the queue is still writing into that one (Fark 82) -- and something has to carry the
                layer, because a window asking about no frames at all is not a window (Fark 80). */}
            {chosenQueued.length === 0
              && LAYER_ACTIONS.map(({ layer, label }) => holding(layer).length > 0 && (
                <Btn key={layer} sm onClick={() => setConfirming(layer)} style={DANGER}>
                  <Icon.Trash /> {label}
                </Btn>
              ))}
```

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil — 384 / 474 / 694 / 438.

---

### Task 3: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

13. maddenin **İş** hücresi ✅ ile başlar, sayaç `12/31` → `13/31`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the bar drops the layer buttons while anything is still waiting

Videolari sil and Sesleri sil now need two things, not one: something in the selection has
to carry the layer, and nothing in it may still be waiting to be produced. What they take
off is a finished stack, and the queue is still writing into a pending frame. A selection
of nothing but pending frames is left with the three buttons every selection has. Kopyala
keeps its own rule and stays in a mixed selection.

The question is asked once for the whole selection rather than once per layer, and it is
asked of a list the bar already had -- the same one the delete window splits its three
shapes by.

The space between the bar's items is 10 now: it was drawn for three buttons and carries
six. Nothing in it may break in two either, which also stops a button shrinking below its
own words. Items falling to a second row is what flex already prevents, so no line says so.

The bar's position is untouched, and why is in the spec: 28 is the answer to the user's own
finding, and 20 is the value that finding was about.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in iki parçası Task 1 ve Task 2.

**Tip tutarlılığı:** `chosenQueued` bir kimlik dizisi ve zaten hesaplanıyor; `holding(layer)` de
öyle. İkisi de aynı `selected` listesinden çıkıyor.

**Kontrol edilen tuzak:** koşul `map`'in dışında. İçeride olsaydı aynı cevap iki kez yazılırdı, ve
iki düğme farklı sebeplerle kaybolabilirdi.

**Kontrol edilen tuzak 2:** `chosenQueued` erken dönüşlerin üstünde hesaplanıyor (11. maddede oraya
taşındı), yani bar çizilirken tanımlı.

**Değişmeyen:** `BAR_RAIL`, Kopyala'nın koşulu, ve pencerelerin sözleri.
