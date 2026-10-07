# v14 Görev 17 — Panelin görsel hizalaması: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün bıraktığı 10 kırmızıyı yeşile döndürmek: satırın dairesi ve ölçüsü, model
kutusu, kapsam adı, kalkan Süre bloğu.

**Architecture:** Çizim `LayerPanel.jsx`'te. Kapsam adının anıldığı üç yorum — biri arka uçta, biri
arka uç testinde — kodla eşitleniyor.

**Tech Stack:** React 18, vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-17-panel-hizalamasi-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor** — arka uç testindeki **yorum** düzeltmesi dışında, ki o
  bir ölçüyü değil bir cümleyi değiştiriyor.
- Yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor.**
- Commit **yeşil gider**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/LayerPanel.jsx` | satır, daire, kutu, ad, blok | altı değişiklik |
| `backend/.../usecases/queue_layer.py` | kapsam adını anan yorum | bir satır |
| `backend/tests/test_photo_usecases.py` | aynı adı anan yorum | bir satır |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Satırın ortak kılığı ve dairesi

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`

**Interfaces:**
- Produces: `data-dot` — kapsam satırının başındaki daire.

- [ ] **Step 1: Ortak sabit ve daire**

`ScopeRow`'un üstüne:

```jsx
// What both row families share. One constant rather than the same object written twice: the design
// widened the row (Fark 31), and a measure given to only one of them would leave two heights in one
// panel -- ModeRow's own comment says it is drawn the way a scope row is drawn.
const ROW = { display: "flex", alignItems: "center", padding: "10px 12px", background: "none",
              width: "100%" };
// The radio the design puts at the head of a scope row: thick and accent-coloured on the chosen
// one, thin and grey on the other. Three long properties rather than the border shorthand, because
// a shorthand carrying var() cannot be read back out of the element again.
const DOT = { width: 12, height: 12, borderRadius: "50%", borderStyle: "solid", flexShrink: 0 };
```

- [ ] **Step 2: `ScopeRow`**

```jsx
function ScopeRow({ label, count, active, disabled, onPick }) {
  return (
    <button type="button" onClick={onPick} disabled={disabled}
            className="wf-stroke"
            style={{ ...ROW, justifyContent: "space-between", gap: 10,
                     cursor: disabled ? "default" : "pointer",
                     borderColor: active ? "var(--accent)" : "var(--border)",
                     opacity: disabled ? 0.4 : active ? 1 : 0.4 }}>
      <span style={{ display: "flex", alignItems: "center", gap: 10, minWidth: 0 }}>
        {/* The row's own dim state is what makes an unpicked circle faint -- no second fading
            here, or the two would drift the day one of them is changed. */}
        <span data-dot style={{ ...DOT, borderWidth: active ? 2 : 1,
                                borderColor: active ? "var(--accent)" : "var(--ink-3)" }} />
        <Note size={12} style={{ color: "var(--ink-2)" }}>{label}</Note>
      </span>
      <Mono size={12} style={{ color: active ? "var(--accent)" : "var(--ink-3)" }}>{count}</Mono>
    </button>
  );
}
```

- [ ] **Step 3: `ModeRow`**

```jsx
function ModeRow({ label, active, disabled, onPick }) {
  return (
    <button type="button" onClick={onPick} disabled={disabled}
            className="wf-stroke"
            style={{ ...ROW, cursor: disabled ? "default" : "pointer",
                     borderColor: active ? "var(--accent)" : "var(--border)",
                     // Closed first: a closed row must not stay bright just because it was picked.
                     opacity: disabled ? 0.4 : active ? 1 : 0.4 }}>
      <Note size={12} style={{ color: "var(--ink-2)" }}>{label}</Note>
    </button>
  );
}
```

Yorumun başındaki *"with nothing on the right"* cümlesi duruyor: sağdaki sayı hâlâ ikisini ayıran
şey.

---

### Task 2: Ad, model kutusu ve kalkan blok

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`

- [ ] **Step 1: Kapsam adı ve `note` alanının gidişi**

`WORDS.video` içinde:

```js
    missing: "Videosu olmayan kareler",
```

ve `note` satırı, yorumuyla birlikte, iki katmandan da siliniyor.

- [ ] **Step 2: İki yorumdaki kısa ad**

`LayerPanel.jsx` içindeki iki satır tam adı yazıyor:

```js
  // than the raw selection: Videosu olmayan kareler leaves those frames out by its own definition,
```

```js
  // Only on the selection's own scope: "Videosu olmayan kareler" is scattered by nature -- what
```

- [ ] **Step 3: Blok başlıkları ve model kutusu**

Dört `Mono size={11} style={LABEL}` başlığı `data-label` alıyor. Model bloğu:

```jsx
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Mono size={11} data-label style={LABEL}>Model</Mono>
        {/* The photo panel's own box, with the one option there is: a layer has a single model and
            the job that goes to the queue carries no model at all -- the engine picks it. The frame
            and the arrow are the design's (Fark 32); the choice is not invented, and the day a
            second model arrives the box is already here. */}
        <select className="wf-input" value={words.model} onChange={() => {}}
                style={{ fontSize: 12.5, color: "var(--ink)", cursor: "pointer" }}>
          <option value={words.model}>{words.model}</option>
        </select>
      </div>
```

- [ ] **Step 4: Süre bloğunu sil**

```jsx
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <Mono size={11} style={LABEL}>Süre</Mono>
        <Note size={12} style={{ color: "var(--ink-3)" }}>{words.note}</Note>
      </div>
```

Bu blok tümüyle gidiyor (karar 17).

---

### Task 3: Arka uçtaki iki yorum

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/usecases/queue_layer.py`
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`

- [ ] **Step 1: `frames_in_scope`'un açıklaması**

```python
    yet. A frame that already holds one is out of the None scope and inside a selection's: the
    panel's row is called "Videosu olmayan kareler", while picking a frame by hand says "this one"
    -- and that is the only way madde 25's "every variant of a frame that already has a video" can
    be asked for.
```

- [ ] **Step 2: Testin yorumu**

```python
    # The panel's row is called "Videosu olmayan kareler": with no selection it means exactly that.
```

Ölçülen şey değişmiyor; değişen, ekranda yazanı anan cümle.

- [ ] **Step 3: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil — 384 / 474 / 694 / 475.

---

### Task 4: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

17. maddenin **İş** hücresi ✅ ile başlar, sayaç `16/31` → `17/31`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the layer panel takes the shape it was drawn in

The scope row gets its full name back. This was a slip and not a choice -- the app's own
description wrote it out, the sound side kept it, and only the video side was shortened.
Three comments named the row by its short name and all three now say what the screen says.

Each scope row grows a circle at its head, thick and accent-coloured on the one that is
picked. The row's own dim state is what makes the other one faint; a second fading would be
two rules for one look. Both row families take the wider measure and now read it from one
constant, so the next change to a row cannot move one of them without the other.

The model becomes the box the photo panel already uses, holding the one option a layer has.
Nothing is invented by that: the job the queue takes carries no model, the engine picks it,
and what changes here is only that the fact is shown in a frame instead of a grey line. The
day a second model exists the box is already standing.

The length block is gone, which was decided when the differences were read: the rule lives
in a written document and does not need to hold a place in the panel. What is left carries a
name a test can read as a list -- Model, Kapsam, Üretim modu, Varyant.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in beş bölümü Task 1 (1, 2), Task 2 (3, 4, 5), Task 3 (4'ün arka uç yüzü).

**Tip tutarlılığı:** `ROW` yalnız ortak olanı taşıyor — `justifyContent` ve `gap` kapsam satırının
kendi eklemesi, çünkü sağdaki sayı yalnız onda var.

**Kontrol edilen tuzak:** `select` bir `onChange` almadan `value` taşıyamaz — React kontrollü alan
uyarısı verir. Tek seçenekli kutu hiçbir şey değiştiremiyor, ama boş bir işleyici alıyor.

**Kontrol edilen tuzak 2:** dairenin ölçüsü `borderWidth` olarak yazılıyor. `border: "2px solid
var(--accent)"` kısayolu jsdom'da geri okunamıyor ve testi sebepsiz kırmızı bırakırdı.

**Kontrol edilen tuzak 3:** `data-label` dört başlığın dördünde de olmalı — üçünde olsaydı test
listeyi eksik okur ve sessizce geçerdi.

**Değişmeyen:** `GeneratePanel.jsx`, `InstallCard.jsx`, 16. maddenin sebep kuralları.
