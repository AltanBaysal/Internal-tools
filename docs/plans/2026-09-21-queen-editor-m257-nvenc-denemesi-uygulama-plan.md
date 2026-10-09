# Madde 257 · NVENC'in derlenmiş olması kullanılabilir olması değil — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-21-queen-editor-m257-nvenc-denemesi-uygulama-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `_encoder()`:** `-encoders` listesi yerine deneme kodlaması; dönen kod sıfırsa GPU, değilse
CPU. Olgu 1, 2, 3, 4.

**2 · Takım:** dört satır paralel. Beklenen: onbir kırmızının hepsi yeşil.

**3 · Commit** (yeşil).
