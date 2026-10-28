# Madde 319 — Havuzun sırası, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `d111c390`'ın dört kırmızı testi yeşile dönüyor.

**Spec:** [m319 uygulama turu](../specs/2026-09-24-queen-editor-m319-havuz-sirasi-uygulama-design.md)

## Her yere geçerli kurallar

- Yorum **İngilizce**. Testlere dokunulmaz. Kaynakla `dist/` aynı commit'te.

---

## Görev 1: `glyphs.jsx` — `PlusGlyph`

```jsx
// A plus: what the design puts in front of Ekle on a reference row's last card.
export const PlusGlyph = ({ size }) => (
  <Glyph name="plus" size={size}>
    <path d="M7 2v10M2 7h10" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
  </Glyph>
);
```

## Görev 2: `ReferencePanel.jsx` — ölçüler, numara, kart

```jsx
const PANEL = { padding: "24px 32px 48px", display: "flex", flexDirection: "column", gap: 28 };

const TILES = { display: "flex", flexWrap: "wrap", gap: 12 };
const TILE = { position: "relative", width: 144, display: "flex", flexDirection: "column", gap: 4 };
const FRAME = { width: 144, height: 108, objectFit: "cover", background: "var(--bg-2)",
                border: "1px solid var(--border)", borderRadius: "var(--r-sm)",
                boxSizing: "border-box", display: "block" };
const BIN = { position: "absolute", top: 6, right: 6, width: 18, height: 18, lineHeight: "16px",
              padding: 0, fontSize: 12, background: "var(--bg)", border: "1px solid var(--border)",
              color: "var(--ink-2)", cursor: "pointer", borderRadius: 3 };
// The slot number is the one a prompt calls the reference by, so it sits on the picture.
const SEQ = { position: "absolute", top: 6, left: 6, background: "rgba(10, 8, 7, .75)" };
const HOLE = { width: 144, height: 108, border: "1px dashed var(--border)",
               background: "var(--bg-2)", borderRadius: "var(--r-sm)", boxSizing: "border-box" };
// The card after a row's last reference is where a file goes in: dashed, because nothing is
// there yet.
const ADD = { ...HOLE, display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
              fontSize: 12, color: "var(--ink-3)" };
```

`Tile`'da `×`'in önüne:

```jsx
      {/* wf-seq's own look, not the kit's Seq: that one pads to 001, and a prompt says <Picture 1>. */}
      <span className="wf-seq" style={SEQ}>{row.slot}</span>
```

Ad ve süre `Note size={11}`. Ses kutusunun yüzü `FRAME`'in ölçüsünde.

Sıra: başlık 12 px, sıranın içi 12 px aralık; kutulardan sonra, sıra dolu değilse:

```jsx
              {rows.length < (pool.limits[kind] ?? 0) && (
                // The way in: after the last reference, until the row holds all it may. What a
                // press on it does is madde 320's.
                <div data-add={kind} style={ADD}><PlusGlyph size={14} /> Ekle</div>
              )}
```

## Görev 3: Koşu, dist ve yeşil commit

- [ ] Dört satır yeşil. - [ ] `npm run build --prefix queen-editor/frontend`. - [ ] `feat(m319): …`.
