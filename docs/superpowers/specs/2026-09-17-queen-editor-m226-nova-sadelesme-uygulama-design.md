# Madde 226 · Nova Orange ve Nova Anime kaldırılacak — uygulama turunun tasarımı

**Tarih:** 17 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Testler:** [test turu](2026-09-17-queen-editor-m226-nova-sadelesme-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Ne değişiyor

| Yer | Değişiklik |
|---|---|
| `domain/recipes.py` | İki satır gider. Yanına `RETIRED = {"novaorange": "nova3dcg", "novaanime": "nova3dcg"}`: kaldırılan bir adın hangi tarife düştüğü |
| `data/comfy_photo_generator.py` | `_recipe` kimliği önce `RETIRED`'dan geçiriyor. Bilinmeyen başka bir kimlik yine duruyor |
| Defter, CONFIG hücresi | `PHOTO_NOVAORANGE` ve `PHOTO_NOVAANIME` kutuları ve kontroldeki adları gider |
| Defter, model hücresi | `PHOTO_CHECKPOINTS`'ten ve `PHOTO_RECIPES`'ten iki satır gider |

**Neden `find` değil `_recipe`:** `find` panelin listesini de kuruyor. Takma adı orada çözmek, eski bir
kimliğin listeye Nova 3DCG'nin **ikinci bir satırı** olarak girmesi demek olurdu. Takma ad yalnız
render'ın sorusu: bu kare neyle üretilecek.

**Neden bir sözlük, bir `if` değil:** iki ad aynı yere düşüyor, ve 222 Slime'ın checkpoint'ini
değiştirirse bu tablo büyüyebilir. Yine de tek bir satır, ayrı bir katman değil.
