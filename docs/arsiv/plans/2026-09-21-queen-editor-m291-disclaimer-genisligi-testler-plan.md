# Madde 291 · Disclaimer tuvalin %80'i olacak — test turunun planı

**Spec:** [test turu](../specs/2026-09-21-queen-editor-m291-disclaimer-genisligi-testler-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `STAMP` ayarlanıyor.** Beklenen zincirde `[1:v]scale=1920:-1[d]` → `[1:v]scale=1536:-1[d]`,
ve üstündeki yorum bugün doğru olanı söylüyor.

**2 · Genişlik testi yeniden yazılıyor.** `test_the_disclaimer_fills_the_canvas_width` gidiyor;
yerine iki yanında boşluk bırakan hâli geliyor: `scale=1536:-1` var, `scale=1920:-1` yok,
`H-h-43` duruyor. Olgu 1, 2, 3.

**3 · Takım:** dört satır paralel. Kırmızı yalnız queen-editor arka ucunda.

**4 · Commit** (kırmızı).
