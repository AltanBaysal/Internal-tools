# Madde 253 · Kodlama GPU'ya geçecek — test turunun planı

**Spec:** [test turu](../specs/2026-09-21-queen-editor-m253-gpu-kodlama-testler-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `FakeRun`:** `-encoders` sorusuna cevap veren `encoders` alanı, varsayılanı boş. Yanına
kodlayıcı sorularını süzen bir yardımcı.

**2 · `NVENC` sabiti:** beklenen kodlayıcı argümanları, `ENCODE`'un yanında.

**3 · Testler:** olgu 1, 2, 3 ve 5 — dört test.

**4 · Takım:** dört satır paralel. Beklenen: yalnız bu dört test kırmızı; 249 ile 250'nin
`libx264`'lü testleri yeşil kalıyor.

**5 · Commit** (kırmızı). Ardından uygulama turu.
