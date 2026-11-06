# Madde 527 · İskelet ve ilk ekran, sürüm V1 — plan

[Tasarım](../specs/2026-11-06-queen-studio-m527-iskelet-design.md). Her adım önce düşen bir testle.

1. **Paketler.** `queen-studio/requirements.txt` (fastapi, uvicorn), `requirements-dev.txt` (üstüne
   pytest, httpx2, ruff, pyright), `.venv`'e kurmak. `pyproject.toml`: pytest (`pythonpath = .`, önbellek
   kapalı), ruff (3.12, satır 100), pyright (sıkı, 3.12). `queen-studio/.gitignore`: `!ui/dist/`,
   `ui/src/api/schema.d.ts`, `.ruff_cache/`.
2. **Ad ve health.** `tests/api/test_health.py` → `core/about.py`, `core/api/endpoints.py`,
   `core/server.py` (`create_api`).
3. **UI'ı sunmak.** `tests/test_server.py` → `core/server.py` (`serve`).
4. **Kimlik.** `tests/disk/test_identity.py` → `core/disk/identity.py`.
5. **Log.** `tests/test_log.py` → `core/log.py`.
6. **Başlangıç dosyası.** `tests/test_main.py` → `main.py` (`build`, sonra Uvicorn).
7. **OpenAPI dosyası.** `tests/test_openapi_file.py` → `write_openapi.py`; koşup
   `ui/src/api/openapi.json`'ı yazmak.
8. **Kontrol araçları.** `tests/test_checks.py`: ruff ve pyright temiz.
9. **UI.** `ui/package.json` (`types`, `pretest`, `test`, `prebuild`, `build`, `dev`), `tsconfig.json`,
   `eslint.config.js`, `vite.config.ts`, `index.html`; `src/about.test.ts` → `src/about.ts`;
   `src/Placeholder.test.tsx` → `src/Placeholder.tsx`; `src/main.tsx`. `npm ci`, `npm test`,
   `npm run build`.
10. **Elle.** Core'u açıp `/` ve `/api/health`'e bakmak; `core.log`'a bakmak.
11. **Belgeler.** CLAUDE.md'nin Commands'ı; CODE-STANDARD'ın başındaki cümle; FOUNDATION'ın 4. kararı.
