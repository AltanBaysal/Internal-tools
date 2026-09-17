# Madde 231 · Galeride Shift ile aralık, Ctrl ile tek tek seçim — test turunun planı

**Spec:** [test turu](../specs/2026-09-17-queen-editor-m231-shift-ctrl-secim-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar.

## Adımlar

**1 · `Gallery.test.jsx`.** Yeni bir `describe`, beş karelik galeride. Seçim `onSelectionChange`'in
son çağrısından okunuyor, sıralanarak, çünkü sıra bu maddenin sorusu değil.

| Test | Olgu |
|---|---|
| `selects every card between the anchor and a shift-press, top to bottom` | 1, 7 |
| `selects the same run bottom to top` | 2 |
| `starts the run from the last plain press and keeps what was chosen before` | 3 |
| `leaves the frame the worker holds out of the run` | 4 |
| `starts a selection with a shift-press instead of opening the frame` | 5 |
| `adds a card with ctrl and takes it out again, without opening it` | 6 |

**2 · Takım koşulur**, dördü de. Beklenen: yalnız **queen-editor'ün ön yüzü kırmızı**.

**3 · Kırmızı commit'lenir.**
