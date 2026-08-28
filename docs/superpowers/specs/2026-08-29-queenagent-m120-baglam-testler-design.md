# Madde 120 — İşin bağlamı skillere ve plana iner · Tur 1 (testler) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 120 —
kullanıcının kendi cümlesi: *"modele ne yaptığımızın contextini vermezsek nereden bilecek?"*

## Kök neden

119 olguyu şemaya yazdı, ama şema yalnız dosya yazılırken çekiliyor; skill metinleri her turda
gidiyor ve ikisi de işin ne olduğunu söylemeden başlıyor — akış neye doğru yürüdüğünü, prompt+
promptun neye gittiğini söylemiyor. Plan da taşımıyor: taze sohbet planı okuyunca adımları
devralıyor, işi değil.

## Kural

1. İki skill metni de işi söyleyerek açılır — ortak çekirdek cümle aynı: hikâye, SDXL ailesinden
   bir görüntü modeli için promptlara çevriliyor, her prompt tek bir donmuş kare.
2. Akışın yazdığı plan bir bağlam satırıyla açılır — ne yapılıyor, ne için — ki planı okuyan taze
   sohbet adımları değil işi devralsın.

## Test — `test_skills.py`, iki yeni

| Test | Aradığı |
|---|---|
| her skill işini söyler *(ALL_SKILLS üstünde parametrik)* | `prompts for an SDXL-family image model` her iki metinde |
| plan bağlamı taşır | `opens with one line of context` ve `inherits the work` akış metninde |

## Beklenen kırmızı

`test_skills.py` 3 *(parametrik test iki skill'de ayrı ayrı + plan testi)*. Defter çifti bilinen
kırmızı.

## Bilerek yapılmayanlar

- **`skills.py` açılmaz** — tur 2.
- **Taban yönerge ellenmez** — bağlam işin skill'inde; skill'siz sohbetin belli bir işi yok.
- **`dist` derlenmez.**
