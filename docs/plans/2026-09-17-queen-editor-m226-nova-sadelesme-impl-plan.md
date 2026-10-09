# Madde 226 · Nova Orange ve Nova Anime kaldırılacak — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-17-queen-editor-m226-nova-sadelesme-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Adımlar

**1 · `recipes.py`.** İki satır gider, `RETIRED` gelir, belge ve yorumlar iki tarife göre düzelir.

**2 · `comfy_photo_generator._recipe`.** `recipes.RETIRED.get(recipe_id, recipe_id)`.

**3 · Defter.** CONFIG hücresinden iki kutu ve kontroldeki adları, model hücresinden iki checkpoint ve
iki tarif satırı.

**4 · Takım koşulur**, dördü de. Beklenen: dördü yeşil.

**5 · Commit**, madde işaretlenir. Ön yüz değişmiyor.
