# Madde 255 · Export ekranı disclaimer adımını söyleyecek — test turunun planı

**Spec:** [test turu](../specs/2026-09-21-queen-editor-m255-disclaimer-adimi-testler-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · Bugünkü `..._joining_the_pieces_...` testi** 1-4. olguların testine dönüşüyor:
`Disclaimer ekleniyor…` var, `birleştiriliyor…` ve `22 / 22 yazıldı…` yok, düğme basılamıyor,
diğer mod basılabilir.

**2 · 5. olgunun testi:** ayrı export koşarken ekranda `Disclaimer` geçen hiçbir şey yok.

**3 · Takım:** dört satır paralel, verbatim. Kırmızı yalnız queen-editor ön yüzünde.

**4 · Commit** (kırmızı). `dist/` bu turda build'lenmiyor — build, kodun değiştiği turun işi.
