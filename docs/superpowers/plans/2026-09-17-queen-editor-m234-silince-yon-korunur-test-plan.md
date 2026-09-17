# Madde 234 · Detayda silinen kareden sonra gidilen yönde kalınır — test turunun planı

**Spec:** [test turu](../specs/2026-09-17-queen-editor-m234-silince-yon-korunur-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar.

## Adımlar

**1 · `PhotoDetail.test.jsx`.** Yeni bir `describe`, beş karelik bir dizide. Sayfa bir kez render
edilir, ok basılır, ve router'ın yaptığı gibi aynı sayfa `rerender` ile yeni kareye geçirilir.
Silmenin cevabı kimlikleri döndürür, böylece hook silinen kareyi kendi listesinden çıkarır ve ikinci
silme gerçek komşulara bakar.

| Test | Olgu |
|---|---|
| `after the back arrow, deleting opens the frame before it` | 1 |
| `after the left key, deleting opens the frame before it` | 2 |
| `after the forward arrow, deleting opens the frame after it` | 3 |
| `a second deletion keeps walking backwards` | 4 |
| `walking backwards off the end, deleting falls to the frame after it` | 5 |

**2 · Takım koşulur**, dördü de. Beklenen: yalnız **queen-editor'ün ön yüzü kırmızı**.

**3 · Kırmızı commit'lenir.**
