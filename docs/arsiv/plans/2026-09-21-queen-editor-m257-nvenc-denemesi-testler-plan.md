# Madde 257 · NVENC'in derlenmiş olması kullanılabilir olması değil — test turunun planı

**Spec:** [test turu](../specs/2026-09-21-queen-editor-m257-nvenc-denemesi-testler-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `FakeRun`:** `encoders` → `nvenc` *(deneme dönüyor mu, varsayılan `False`)*, ve süzgeç deneme
çağrısına bakıyor.

**2 · 253'ün dört testi:** yeni ikize göre, `nvenc=True` ile.

**3 · İki yeni test:** olgu 1 ve 3.

**4 · Takım:** dört satır paralel. Beklenen: dört test kırmızı.

**5 · Commit** (kırmızı). Ardından uygulama turu.
