# Madde 302 — Üretimin reddi, test turunun planı

**Spec:** [m302 test turu](../specs/2026-09-21-queen-editor-m302-uretimin-reddi-testler-design.md)

Üç test dosyası, hepsi var: `test_reference_usecases.py`, `test_reference_routes.py`,
`useGeneration.test.jsx`. Kaynak koda dokunulmuyor.

## Adımlar

1. **Altı kullanım senaryosu testi** — `queue_references(store, pool, orders, project, prompts,
   variants, has_h3)` çağrısıyla; havuz sahteleri 297'den geliyor.
2. **İki kapı testi** — `POST …/references/produce`, gerçek diskle.
3. **Bir kanca testi** — referans kipi hangi çağrıya gidiyor.
4. **Dört test satırı koşulur.**

## Beklenen kırmızı

`queue_references` ve ucu yok; kanca referans kipini tanımıyor.
