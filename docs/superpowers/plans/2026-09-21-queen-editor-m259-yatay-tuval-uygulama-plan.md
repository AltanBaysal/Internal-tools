# Madde 259 · Birleşik export yatay tuvale geçiyor — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-21-queen-editor-m259-yatay-tuval-uygulama-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · Sabitler:** `MERGED_WIDTH` ve `MERGED_HEIGHT` geliyor, `DISCLAIMER_WIDTH` gidiyor,
`DISCLAIMER_MARGIN`'ın yorumu tuvali söylüyor.

**2 · `_stamp()`:** argümansız, sığdırma + bant + tam genişlikte bindirme. Olgu 1, 2, 3, 5, 6.

**3 · `merge()`:** ölçüyü söken satır gitti, çağrı `self._stamp()` diyor. Olgu 4.

**4 · Farklı ölçü mesajı:** gerekçe `concat`'in kendisine döndü. Olgu 9.

**5 · Yorumlar:** modül başlığı ve `ffprobe`'un satırı artık doğruyu söylüyor.

**6 · Takım:** dört satır paralel, verbatim. Beklenen: beş kırmızının hepsi yeşil.

**7 · Commit** (yeşil). Ardından 255 — koşunun son maddesi.
