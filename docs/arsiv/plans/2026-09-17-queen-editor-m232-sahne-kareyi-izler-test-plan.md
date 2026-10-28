# Madde 232 · Kare değişince sahnede eski karenin dosyası kalmayacak — test turunun planı

**Spec:** [test turu](../specs/2026-09-17-queen-editor-m232-sahne-kareyi-izler-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar. jsdom medya yüklemiyor, bu yüzden testler `load`, `loadeddata` ve
`error` olaylarını kendileri ateşliyor.

## Adımlar

**1 · `PhotoDetail.test.jsx`.** Yeni bir `describe` bloğu, madde 232. Bir yardımcı iki kareyi açıp
`rerender`'ı döndürüyor. `SECOND_SOUND` fikstürü sesli ikinci kare.

| Test | Olgu |
|---|---|
| `throws the old picture away when the frame changes` | 1 |
| `says it is loading until the new picture arrives` | 2 |
| `says so when the picture does not come, and which one` | 3 |
| `throws the old video away when the frame changes` | 4 |
| `throws the old sound away when the frame changes` | 5 |
| `says it is loading until the video arrives` | 6 |
| `says so when the video does not come, and which one` | 7 |

**2 · Takım koşulur**, dördü de. Beklenen: yalnız **queen-editor'ün ön yüzü kırmızı**.

**3 · Kırmızı commit'lenir.**
