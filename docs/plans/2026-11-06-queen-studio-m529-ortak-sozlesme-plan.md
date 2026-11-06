# Madde 529 · Ortak sözleşme: hatalar, başlıklar, `GET /api` — plan

[Tasarım](../specs/2026-11-06-queen-studio-m529-ortak-sozlesme-design.md). Her adım önce düşen bir testle.

1. **Testin yardımcıları.** `tests/budgets.py` (dört sınır), `tests/contract.py` (`checked_client`,
   `check_error`), `tests/sample.py` (yalnız testte açılan grup: `POST`, `GET`, `DELETE
   /samples/{id}`, `GET /boom`; `sample_api`).
2. **Hata.** `tests/test_errors.py` → `core/errors.py` (`Error`, `CODES`, `FieldCode`, `RESPONSES`,
   `ApiError`, `respond`, `problem`, `unknown`, `handle`); `core/server.py`'de `redirect_slashes=False`,
   `responses=errors.RESPONSES`, `errors.handle(api)`.
3. **Gövde.** `tests/test_body.py` → `core/body.py` (`RequestBody`, `MAX_BYTES`, `BodyLimit`);
   `create_api`'de `api.add_middleware(BodyLimit)`.
4. **Başlıklar.** `tests/test_change.py` → `core/change.py` (`Actor`, `Change`, `change`).
4b. **Sorgu.** `tests/test_query.py` (örnek gruba `GET /samples`, `own_query`'yle) → `core/query.py`
   (`own_query`, `known_query`); `create_api`'de `dependencies=[Depends(known_query)]`.
5. **Dizin ve ayrıntı.** `tests/api/test_discovery.py` → `core/api/discovery.py` (`RULES`, `index`,
   `detail`; satır `"<fiil> <adres>: <özet>"`); `core/api/endpoints.py`'de `SECTION` ve `GET /` (`?path=`); `create_api`'de
   `openapi_tags=[endpoints.SECTION]`.
6. **Var olan testler.** `tests/test_server.py` (çıplak `/api` dizin, `?path=/health` ayrıntı,
   `unknown_endpoint`), `tests/api/test_health.py`, `tests/test_main.py`: hepsi `contract.checked_client`'la.
7. **OpenAPI dosyası.** `write_openapi.py`'yi koşmak; `ui/src/api/openapi.json` `Error`'u taşır.
8. **UI.** `npm test`, `npm run build`; `dist` değişmedi mi bakmak.
9. **Elle.** Örnek API'yi Uvicorn'la açıp `/api/boom`'un `internal` döndüğüne ve izinin `core.log`'a
   düştüğüne, `/api/health/`'in yönlendirilmediğine bakmak (`tmp/m529/run_fail.py`).
10. **Kontrol araçları.** ruff ve pyright temiz; iki suite yeşil.
11. **Reviewer'ın bulguları.** Önce testler: `tests/test_errors.py` (dizinin kendi hint'i ve adı,
    hint'lerin andığı çağrılar 200, kesilen `internal` ve adres, doğrulama hatasının türü ve sayısı,
    `{name:path}`, FastAPI'nin `4xx`'i), `tests/test_query.py` (sorgu modeli), `tests/test_contract.py`
    (`TestClient(` taraması); sonra `core/errors.py`, `core/query.py`, `core/change.py`,
    `core/api/endpoints.py` (`async`), `Body` → `RequestBody`, `contract.client` → `checked_client`.
12. **QA'nın bulguları.** Önce testler: `tests/test_errors.py` (`/openapi.json`'ın 405'i, adların
    baytla kesilmesi, ilk altı sorun ve kalanın sayısı, en kötü boy), `tests/test_change.py`
    (başlık sorununun hint'i), `tests/test_query.py` (`query.(empty)`); sonra `core/errors.py`
    (`_sent`, `_cut`, `*_BYTES`, `PROBLEMS_SHOWN`, 405'in belge dışı yolu) ve `core/change.py`
    (`HEADERS_HINT`).
