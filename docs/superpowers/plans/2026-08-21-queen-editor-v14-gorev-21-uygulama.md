# v14 Görev 21 — Sağ panelin düzeni: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün bıraktığı 12 kırmızıyı yeşile döndürmek: katmanını söyleyen etiketler,
sabit yükseklikli kutular, kopyala ikonu, iki grup ve tek dikey ritim.

**Architecture:** İki dosya. `glyphs.jsx`'e bir ikon, `PhotoDetail.jsx`'e iki küçük bileşen ve
sütunun yeniden düzenlenmesi.

**Tech Stack:** React 18, vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-21-panel-duzeni-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor.**
- Yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor.**
- Commit **yeşil gider**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/glyphs.jsx` | ekranın kendi ikonları | `CopyGlyph` eklenir |
| `.../photo_generation/PhotoDetail.jsx` | detay sayfası | iki bileşen, iki sabit, sütun |
| `frontend/dist/` | not defterinin okuduğu çıktı | derlenir |

---

### Task 1: Kopya ikonu

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/glyphs.jsx`

**Interfaces:**
- Produces: `CopyGlyph({ size })` — `data-glyph="copy"`.

- [ ] **Step 1: Dosyanın sonuna**

```jsx
// Two sheets, one behind the other. The front one is whole; the back one shows only the edge the
// front does not cover, which is what makes the pair read as a copy rather than two boxes.
export const CopyGlyph = ({ size }) => (
  <Glyph name="copy" size={size}>
    <rect x="4.6" y="1.9" width="7.5" height="7.5" rx="1.3" stroke="currentColor"
          strokeWidth="1.4" />
    <path d="M9.4 12.1H3.2a1.3 1.3 0 0 1-1.3-1.3V4.6" stroke="currentColor" strokeWidth="1.4"
          strokeLinecap="round" strokeLinejoin="round" />
  </Glyph>
);
```

---

### Task 2: Kopya düğmesi ve başlık satırı

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`

**Interfaces:**
- Consumes: `CopyGlyph`.
- Produces: `BoxLabel({ label, text })` — iki prompt kutusunun başlık satırı.

- [ ] **Step 1: `useRef` ve `CopyGlyph` içeri alınıyor**

```jsx
import { useEffect, useRef, useState } from "react";
```

```jsx
import { CopyGlyph, PlayGlyph, SoundGlyph } from "./glyphs.jsx";
```

- [ ] **Step 2: `Field`'ın hemen üstüne iki bileşen**

```jsx
// Long enough to be read without looking away, short enough that the icon is an icon again before
// it is next needed. RawOutput's own measure -- the same answer to the same question.
const SAID_MS = 2500;

// Fark 90: one press puts the box's text on the clipboard. The icon answers in its own name and
// its colour and adds no line to the panel -- a word appearing beside the heading would push the
// box under it down, which is the very thing Fark 89 is about (karar 33).
function CopyButton({ label, text }) {
  const [said, setSaid] = useState(null);
  const fade = useRef(null);

  useEffect(() => () => clearTimeout(fade.current), []);

  function copy() {
    clearTimeout(fade.current);
    // Written straight from the press, not from a microtask after it: the clipboard is granted to
    // a user gesture and a browser may refuse a write that arrives even a tick late. The try is
    // for the other half -- with no clipboard object at all the call throws where it stands, while
    // a refused permission rejects instead, and the user needs the same answer either way.
    let landing;
    try {
      landing = navigator.clipboard.writeText(text);
    } catch (absent) {
      landing = Promise.reject(absent);
    }
    Promise.resolve(landing)
      .then(() => setSaid("Kopyalandı"))
      .catch(() => setSaid("Kopyalanamadı"))
      .finally(() => { fade.current = setTimeout(() => setSaid(null), SAID_MS); });
  }

  return (
    // An empty box has nothing to copy, and a button that copies nothing and says it did is a lie.
    // Dimmed rather than gone: an icon that came and went as the user typed would make the heading
    // twitch (karar 34).
    <button type="button" onClick={copy} disabled={!text}
            aria-label={said || `${label} — kopyala`}
            style={{ background: "none", border: "none", padding: 0, lineHeight: 0,
                     cursor: text ? "pointer" : "default", opacity: text ? 1 : 0.35,
                     color: said === "Kopyalandı" ? "var(--accent)"
                       : said === "Kopyalanamadı" ? "var(--danger)" : "var(--ink-3)" }}>
      <CopyGlyph size={12} />
    </button>
  );
}

// A box's heading: what it holds on the left, and on the right the one thing that can be done to it
// without opening it. Both prompt boxes are drawn from here, so the row is described once.
function BoxLabel({ label, text }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
      <Mono size={10} style={LABEL}>{label}</Mono>
      <CopyButton label={label} text={text} />
    </div>
  );
}
```

---

### Task 3: Kutular kendi ölçüsünü alıyor

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`

**Interfaces:**
- Produces: `data-box` — metnin durduğu kutu; yüksekliği buradan okunuyor.

- [ ] **Step 1: `LABEL`'ın altına iki sabit**

```js
// Fark 89: each box takes its own measure instead of sharing whatever the window leaves over -- a
// short window used to squeeze both at once. The photo's is the tallest, being the one prompt
// written from nothing; the negative is the shortest, a list of words rather than a sentence.
const PROMPT_HEIGHT = { photo: 162, video: 150, audio: 150 };
const NEGATIVE_HEIGHT = 96;
```

- [ ] **Step 2: `TextBlock`**

```jsx
// Prompt and negative are the same block twice, each at its own height and each scrolling inside
// itself so a long text folds rather than growing the panel (Fark 89).
//
// `hint` is what an empty box says when the emptiness has a reason -- a layer nobody has written
// the words for yet (madde 81). It is centred while a real prompt is not: a prompt is read from the
// left, an absence is a notice and stands in the middle of the box (Fark 92). Without a hint an
// empty box says "—", because an empty negative is an answer of its own.
function TextBlock({ label, text, hint, height }) {
  const empty = !text;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <BoxLabel label={label} text={text} />
      {/* border-box, or the padding would add itself to the design's measure: this repo has no
          global box-sizing reset and the stroke class does not carry one. */}
      <div data-box className="wf-stroke"
           style={{ height, overflowY: "auto", padding: 10, boxSizing: "border-box" }}>
        {/* The box is drawn even with nothing in it: a box that came and went with the frame would
            make the column jump between frames -- and an empty one reads as a prompt somebody
            deleted, which is the whole reason the hint exists. */}
        <Note size={12} style={{ color: empty ? "var(--ink-4)" : "var(--ink-2)", display: "block",
                                 lineHeight: 1.6,
                                 ...(empty && hint ? { textAlign: "center" } : {}) }}>
          {empty ? (hint || "—") : text}
        </Note>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: `PromptBox`**

```jsx
// The open layer's own prompt, in the user's hands. Only this one box is writable: what is sent is
// the open layer's prompt alone, and a box under it that changed nothing would be a lie.
//
// Nothing is saved. The words live on screen until they are made into a frame or the frame is left
// (madde 76) -- a stored draft is a concept the design never asked for.
function PromptBox({ label, value, changed, height, onChange }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <BoxLabel label={label} text={value} />
      <textarea data-box className="wf-stroke wf-note" value={value}
                onChange={(e) => onChange(e.target.value)}
                style={{ height, overflowY: "auto", padding: 10, resize: "none",
                         boxSizing: "border-box", background: "transparent", color: "var(--ink-2)",
                         fontSize: 12, lineHeight: 1.6,
                         // The accent says one thing: pressing now makes a NEW prompt rather than
                         // another variant of this one. Space around the words is not that.
                         borderColor: changed ? "var(--accent)" : undefined }} />
    </div>
  );
}
```

---

### Task 4: Sütunun iki grubu ve ritmi

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`

**Interfaces:**
- Produces: `data-side`, `data-group` (`info`, `production`).

- [ ] **Step 1: `SIDE`**

```js
// Fark 91: one vertical rhythm down the column -- 16 between blocks. And with every box at a fixed
// height the column has a fixed total, so a window shorter than that scrolls the panel rather than
// putting the delete button somewhere nobody can reach (karar 35).
const SIDE = {
  width: 300, flexShrink: 0, borderLeft: "1px solid var(--border)", padding: 16,
  display: "flex", flexDirection: "column", gap: 16, boxSizing: "border-box", minHeight: 0,
  overflowY: "auto",
};
```

- [ ] **Step 2: `Field`'ın iç boşluğu**

```jsx
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
```

- [ ] **Step 3: Sütun iki gruba sarılıyor**

`<div style={SIDE}>` → `<div data-side style={SIDE}>`.

Bilgi grubunun açılışı:

```jsx
            {/* What the frame is. No group heading and no rule under it: the split from what can be
                made of it is where the eye rests, not a line it reads (Fark 91). */}
            <div data-group="info"
                 style={{ display: "flex", flexWrap: "wrap", columnGap: 24, rowGap: 16 }}>
```

Bilgi grubu `Üretim modu` alanından sonra kapanıyor, ve üretim grubu hemen orada açılıyor:

```jsx
            </div>

            {/* What can be made of it. */}
            <div data-group="production"
                 style={{ display: "flex", flexDirection: "column", gap: 16 }}>
```

Üretim grubu silme düğmesinden sonra kapanıyor — `</div>` sütunun kendi `</div>`'inden önce.
Aradaki her şey (prompt kutuları, yeni mod, üret, açıklama satırı, tekrar dene, hata kartları, sil)
olduğu gibi bu grubun içinde kalıyor, girinti bir seviye artıyor.

- [ ] **Step 4: Prompt kutularının etiketi ve yüksekliği**

```jsx
              {/* The open layer's own prompt, and nothing under it: what a layer was made from is
                  no longer this page's to show (madde 87). The heading says whose words these are,
                  in the tab's own word so a layer cannot be called two things (Fark 88). */}
              {holds ? (
                <PromptBox label={`${LAYER_LABEL[open]} prompt'u`} value={typed} changed={changed}
                           height={PROMPT_HEIGHT[open]}
                           onChange={(text) => setWords((kept) => ({ ...kept, [open]: text }))} />
              ) : (
                <TextBlock label={`${LAYER_LABEL[open]} prompt'u`} height={PROMPT_HEIGHT[open]}
                           text={(frame.prompts || {})[open]
                                 ?? (open === "photo" ? frame.prompt : "")}
                           // A layer still in the queue has no words yet, and nobody typed the
                           // missing ones. Not the photo's: those words are the user's own, so a
                           // notice about a prompt nobody has written would be false there.
                           hint={openState === "pending" && open !== "photo"
                             ? "Prompt yok — üretim sırası geldiğinde eklenecek."
                             : null} />
              )}
              {/* The negative belongs to the photo alone: video and sound jobs carry none. It stays
                  read-only: the design gives the user the prompt, not the whole submission. */}
              {open === "photo" && (
                <TextBlock label={`${LAYER_LABEL.photo} negatif prompt'u`}
                           height={NEGATIVE_HEIGHT} text={frame.negative} />
              )}
```

- [ ] **Step 5: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil — 384 / 474 / 694 / 494.

---

### Task 5: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

21. maddenin **İş** hücresi ✅ ile başlar, sayaç `20/31` → `21/31`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the right column takes its own measure

The headings name their layer now, in the tab's own word rather than a second list, so a
layer cannot be called one thing on its tab and another over its box.

The boxes stop sharing what the window leaves and take their own heights. They carry
box-sizing with them: this repo has no global reset, and without it the ten pixels of
padding would add themselves to the design's measure. With the column at a fixed total the
panel scrolls inside itself -- a window shorter than the column would otherwise leave the
delete button somewhere nobody could reach.

Each heading gained a copy icon, and the icon answers in its own accessible name: copied,
or could not copy, for two and a half seconds, in accent or in red. The words and the wait
are the raw output panel's, which answers the same question. It gains no line, because a
word appearing beside a heading would push the box under it down and that is the thing this
item is about. Over an empty box it dims rather than leaves: copying nothing and saying it
worked is a lie, and an icon that came and went as the user typed would make the heading
twitch.

The column is two groups now -- what the frame is, then what can be made of it -- with no
heading and no rule between them, and one vertical measure down the whole of it.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in dört bölümü Task 1+2 (1), Task 3 (2), Task 4 Step 4 (3), Task 4
Step 1–3 (4).

**Tip tutarlılığı:** `BoxLabel` iki kutudan da `label` ve `text` alıyor; `CopyButton`'ın adı
`${label} — kopyala`, testin aradığıyla birebir aynı tire ve boşluk.

**Kontrol edilen tuzak:** `boxSizing` unutulursa testler yine yeşil geçer — jsdom yerleşim
hesaplamıyor, `style.height` yazılan değeri döndürür. Yani bunu yakalayacak tek şey bu satırın
kendisi; Colab turunda kutular 20 piksel uzun çıkardı.

**Kontrol edilen tuzak 2:** `Yeni mod` etiketi `BoxLabel` almıyor — o bir prompt kutusu değil, ve
bir seçicinin kopyalanacak metni yok.

**Kontrol edilen tuzak 3:** `data-field` yalnız bilgi grubunun etiketlerinde. `BoxLabel` düz `Mono`
kullanıyor, yoksa 19. maddenin "üst grupta başka satır yok" testi prompt başlıklarını da sayardı.

**Kontrol edilen tuzak 4:** `SAID_MS` zaman aşımı bileşen sökülürken temizleniyor — kullanıcı
kopyaladıktan hemen sonra oklarla başka kareye geçebilir.

**Koşuda çıkan tuzak 5:** 494 test yeşil geçti ve koşu yine de 1 ile çıktı. Sebep uygulama değil,
kırmızı turda yazdığım pano taklidiydi: reddedilen sözü testin en başında yaratıyordum, oysa
basıştan önce bir sayfanın açılması gerekiyor. Kimsenin beklemediği bir ret o tikler boyunca
"yakalanmamış" sayılıyor ve vitest bunun için bütün koşuyu düşürüyor — testlerin hepsi yeşilken.
`RawOutput`'un aynı yardımcısı bu tuzağa düşmüyor çünkü orada stub ile basış arasında `await` yok.

Yardımcı düzeltildi: cevap artık çağrı anında üretiliyor, yani ret doğduğu tikte zaten ele
alınıyor. **Uygulama turunda bir test dosyasına dokunmanın tek meşru sebebi bu** — testin ölçtüğü
şey değişmedi, kendi kusuru düzeldi.

**Değişmeyen:** kutuların içindekiler, negatifin salt okunurluğu, sahne, sekme şeridi, oynatıcı,
onay pencereleri.
