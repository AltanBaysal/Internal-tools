# Madde 326 — Referanstan'dan üretim sunucuda düşmüyor, uygulama turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m326 test turu](2026-09-24-queen-editor-m326-havuzdan-uretim-kapisi-testler-design.md),
`65dfed66`.

## Sunucu — yalnız `main.py`

- Havuzun üretim kapısının `partial`'ından `references=_reference_files` gidiyor. `queue_references`
  havuzu kuyruğa kendisi bağlıyor *(`partial(reference_files, store, pool, orders)`)*, çünkü havuzun
  deposu ve sırası zaten ona verilen argümanlar; ikinci bir yoldan vermek aynı şeyi iki yerde tutmak
  olurdu. Öteki kapıların `references=`'ı doğru — onların kullanım durumları havuzu bilmiyor ve o
  parametreyi alıyor.
- `queue_references`'ın imzası değişmiyor.

## Dist

Ekran değişmiyor; derlenecek bir şey yok.

## Bitti sayılır

Dört test satırı yeşil; kod, spec ve plan tek commit.
