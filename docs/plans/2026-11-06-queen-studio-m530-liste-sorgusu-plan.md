# Madde 530 · Liste sorgusu — plan

[Tasarım](../specs/2026-11-06-queen-studio-m530-liste-sorgusu-design.md). Her adım önce düşen bir testle.

1. **Bağımlılık yok.** İlk yapılışta `regex` paketi eklenmişti; regex'in kaldırılmasıyla (adım 12)
   `requirements.txt`'ten çıktı, `.venv`'den kaldırıldı.
2. **Alanlar.** `tests/lists/test_fields.py` → `core/lists/fields.py` (`Kind`, `Field`, `fields_of`).
3. **Ayrıştırıcı.** `tests/lists/test_parse.py` → `core/lists/parse.py` (`Filter`, `Order`, `Query`,
   `Refused`, `parse_list`, `parse_bulk`, `parse_one`, `parse_order`, `parse_select`); sorunlar
   `errors.problem`'la, adlar `errors.cut`'la.
4. **Değerlendirici.** `tests/lists/test_run.py` → `core/lists/run.py` (`page`, `filtered`,
   `ordered`, `pick`, `value_of`, `liked`); `ilike`'ın katlaması (`parse.fold`).
5. **m529'un yardımcıları.** `core/errors.py`: `_cut` → `cut`, `_template` → `template`,
   `_invalid`'in `ApiError` kuran yarısı `invalid(address, problems, details)`; var olan testler
   yeşil kalır.
6. **Listing.** `tests/sample.py`'ye `/notes` (`GET` liste, `DELETE` toplu, `GET /notes/{id}`);
   `tests/lists/test_listing.py` → `core/lists/listing.py` (`Listing`, `Page`,
   `Selection`); `errors.py`'nin pydantic tablosuna `given_twice`.
7. **Ayrıntı ve dizin.** `tests/api/test_discovery.py` (`list` ayrıntıda, `rules` sorguyu söyler) →
   `core/api/discovery.py` (`x-list` → `list`, `RULES`).
8. **Yinelenen parametre.** `tests/test_query.py` → `core/query.py` (`known_query` tek değerli
   parametrenin yinelenmesini `duplicate` sayar).
9. **Boy.** `tests/budgets.py`'ye `LIST_ITEM_BYTES`, `TEXT_SAMPLE_BYTES`; `tests/lists/test_listing.py`'de
   belgenin yürüyüşü; en kötü sorgu hatası `ERROR_BYTES`'ta.
10. **Belgeler.** CODE-STANDARD, Düzen (`core/lists/`); 6. adımın desen satırı; kararlar,
    Sapmalar (ana agent yazar).
11. **Kontrol.** `write_openapi.py` (belge değişmemeli); ruff, pyright; iki suite, sırayla.
12. **Regex'in kaldırılması** (kullanıcıyla verilen karar, 6 Kasım). Önce testler: `test_parse.py`
    (`like`/`ilike` parçaları ve katlaması, `match` bilinmeyen işleç), `test_run.py` (`liked`,
    `ilike`'ın i'leri ve `casefold`'u, geç düşen desen; süre bütçesinin testleri silindi),
    `test_listing.py` (süre bütçesinin testi silindi); sonra `parse.py` (`fold`, `_pattern`),
    `run.py` (`liked`; `TooSlow` ve süre gitti), `listing.py` (`Asked`, `REGEX_SECONDS` gitti),
    `discovery.RULES`, `requirements.txt`, 6. adım.
13. **Review'un bulguları: sınırlar** (CODE-STANDARD, Maliyet'in yeni kuralı). Önce testler:
    `test_parse.py` (alan başına iki süzgeç, `in`'in 1000 değeri, `order`'da ve `select`'te iki
    kez anılan alan), `test_pattern.py` (yeni: `Pattern`, ortadaki parçası düşen desen),
    `test_run.py` ve `test_listing.py` (sayfanın bayt bütçesi, düşük ayarla), `test_query.py`
    (`list[str] | None`), `test_main.py` (h11 ve baş sınırı); sonra `core/lists/pattern.py`
    (yeni), `parse.py` (`FILTERS_PER_FIELD`, `MOST_IN`, tekrar eden alan, `_OPS`, `_KIND_WORDS`),
    `fields.py` (`ListField`), `run.py` (`page` bayt yazar, `TooLarge`), `listing.py`
    (`PAGE_BYTES`), `core/query.py` (`_repeats`), `main.py` (`SERVER`, `HEAD_BYTES`).
14. **QA'nın bulguları.** h11'in baş sınırı tek okumada gelen başı tutmuyor: `core/query.py`'ye
    `QueryLimit` ve `QUERY_BYTES` (16 KiB), `create_api`'de `BodyLimit`'in yanında; testi
    `test_query.py`'de, sınır küçültülerek. `main.py`'nin ve `parse.py`'nin açıklaması,
    `test_main.py`'nin h11 testi yalnız gösterdiğini söyler. `discovery._KEPT`'e `format`
    (zamanın `date-time`'ı); bilinmeyen işleç alanın işleçlerini sayar; `pattern.py`'nin ve spec'in
    katlanmış parça cümlesi.
