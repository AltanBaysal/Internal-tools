# Madde 303 — Referans işi kart doğuruyor, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m303 test turu](2026-09-21-queen-editor-m303-kart-doguruyor-testler-design.md),
`a0e0007f` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## `queue_references` bir koşu oluyor

302'de beş kontroldü; şimdi `start_batch`'in şeklini alıyor: runner, kayıt, plan, sıra, üretici,
tohum, saat. Kontroller aynen duruyor ve önce koşuyor — hiçbir şey yazılmadan reddetmek 302'nin
kuralıydı.

Sonra:

1. **Kartlar planlanıyor** — `plan_reference_cards(start, prompts, variants, new_seed)`:
   `plan_frames`'in ikizi, iki farkla *(iş tipi video, satırda `mode: reference`)*. Ayrı bir
   fonksiyon, çünkü `plan_frames`'e tip ve kip parametreleri eklemek onu iki işin ortak paydası
   yapardı; ikisi de kısa ve ikisi de kendi cümlesini söylüyor.
2. **Plan'a ekleniyor**, sonra **kuyruk çalıştırılıyor** — `start_batch`'in kendi sırası: ölen bir
   koşu yapacağı işi arkasında bırakır.

`next_number` numarayı veriyor: projenin kuralı, fotoğrafın değil.

## Üretici bugün ne yapıyor

H3'ün referans kipi **304**'te. Bugün iş kuyruğa giriyor ve bugünkü video üreticisine gidiyor —
kaynak fotoğrafı olmadığı için gerçek H3 bunu reddeder ve kart kırmızı olur. Doğru davranış: kart
doğdu, üretim başarısız, ve *Tekrar dene* 304 geldiğinde çalışır.

## Kapı ve `main.py`

Uç aynı; bağlanan şey uzuyor. Kanca ve panel hiç değişmiyor — 302'de yazıldılar.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil.
