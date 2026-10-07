# Madde 290 · Ekran açılışta koşan export'u görecek — test turunun planı

**Spec:** [test turu](../specs/2026-09-21-queen-editor-m290-yenilemeye-dayanan-ekran-testler-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · Açılışta soruluyor.** `open()` sonrası `getExportState`'in çağrıldığı, hiçbir basış olmadan.
Olgu 1.

**2 · Koşan benimseniyor.** Sunucu birleşik modu `merging` ve biten adımlarıyla veriyor; ekran
basılmadan adımın cümlesini, kapalı düğmeyi ve süreleri gösteriyor. Olgu 2.

**3 · Bitmiş benimsenmiyor.** `done` veren bir durumda yeşil kart yok, düğme basılabilir. Olgu 3.

**4 · Hata benimsenmiyor.** `error` veren bir durumda kırmızı kart yok. Olgu 4.

**5 · Altı mevcut test ayarlanıyor:** koşan bir duruma basarak gelenler artık `open()` ile
geliyor. Soruları değişmiyor.

**6 · Takım:** dört satır paralel. Kırmızı yalnız queen-editor ön yüzünde.

**7 · Commit** (kırmızı). `dist` bu turda build'lenmiyor — ön yüz kaynağı değişmedi.
