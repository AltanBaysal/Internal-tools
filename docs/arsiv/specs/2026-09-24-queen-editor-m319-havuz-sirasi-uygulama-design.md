# Madde 319 — Havuzun sırası ne gösteriyor, uygulama turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m319 test turu](2026-09-24-queen-editor-m319-havuz-sirasi-testler-design.md),
`d111c390`.

## Değişen — `ReferencePanel.jsx`

Ölçüler tasarımın `.rv-*` kurallarından *(proje-ekrani-tam/index.html)*:

- **Kutu** 144 px genişlik, 4 px aralık; **yüz** 144 × 108, köşe `var(--r-sm)`; **boşluk** aynı ölçüde.
- **Yuva numarası** sol üstte, 6 px içeride: `wf-seq` sınıfıyla, koyu yarı saydam zeminde
  *(`rgba(10, 8, 7, .75)`)*. `Seq` bileşeni değil — o sayıyı üç haneye dolduruyor *(`001`)*, oysa
  prompt'un `<Picture 1>`'i düz sayı.
- **`×`** 18 × 18, sağ üstte 6 px içeride; **ad** ve **süre** 11 px.
- **`+ Ekle` kartı** `data-add="<tip>"`, 144 × 108, kesikli kenar; artı glifi `glyphs.jsx`'e
  `PlusGlyph` olarak giriyor *(tasarımın `g.plus`'ı)*. Bu maddede tıklaması yok.
- **Sıralar** arası 28 px, sıranın içi 12 px; başlık 12 px; kutular arası 12 px.

Bugünkü ortak `Ekle` 320'ye kadar duruyor.

## Dist

`npm run build --prefix queen-editor/frontend`; `dist/` kodla aynı commit'te.

## Bitti sayılır

Dört test satırı yeşil; kod, dist, spec ve plan tek commit.
