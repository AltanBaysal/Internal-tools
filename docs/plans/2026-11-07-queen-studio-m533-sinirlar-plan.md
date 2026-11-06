# Madde 533 · Yapılmış kodun sınırları — plan

[Tasarım](../specs/2026-11-07-queen-studio-m533-sinirlar-design.md). Her adım önce düşen bir testle.

1. **Health.** `tests/api/test_health.py` (işçi sınırı 1, bir route onu tutarken health cevap
   verir) → `core/api/endpoints.py`'de `health` `async def`; FOUNDATION 2'ye kuralı.
2. **Bir gövde.** `tests/test_body.py` (sınır 1 MiB; testler `MAX_BYTES`'ı 1024'e kurar, hata
   baytla) → `core/body.py`'de `MAX_BYTES = 1024 * 1024`, `_too_large` baytla; 6. adımın Gövde satırı.
3. **Tutulan gövdeler.** `tests/test_body.py` (tutulan route'un yanında ikinci gövde `busy`, health
   200, bırakılınca geçer; `BodyLimit` doğrudan sürülerek üç çıkışta `held` 0) → `core/body.py`'de
   `HELD_BYTES`, `BodyLimit.held`, `_busy`; `core/errors.py`'de `busy` 503; 6. adımın tablosunda satırı.
4. **Hata.** `tests/test_errors.py` (yalnız gösterilenler `problem`'dan geçer, `more` doğru;
   gösterilmeyen başlık sorunu hint'i korur) → `core/errors.py`'de doğrulama handler'ı ilk
   `PROBLEMS_SHOWN`'u biçimler; `invalid` eski imzasıyla `_invalid`'e bırakır, yer `_places`'tan;
   `_failure`'da `error_count()`.
5. **Şema yürüyüşü.** `tests/test_body.py`: `unbounded(doc)`; örnek API'de boş, eksik sınırlı
   modelde her eksik adıyla.
6. **CODE-STANDARD, Cost:** sunucunun kendi korumalarının istisnası.
7. **Ölçüm.** `tmp/m533/`'te küçük denemeler (pydantic'in `max_length`'i ve `FailFast`'ı, hata
   başına süre ve bellek, ayrıştırılmış gövdenin boyu); sonra silinir.
8. **Suite'ler.** `queen-studio/.venv/Scripts/python -m pytest queen-studio -q`, sonra
   `npm test --prefix queen-studio/ui`. API'nin yüzeyi değişmedi: `openapi.json` ve `dist` aynı.
