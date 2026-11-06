# Yeni editör — 5. Backend yığını

Core'un ve UI'ın neyle yazılacağı.

queen-editor'ın yığını kalır; bu kez baştan düzenli, basit ve yatay kurulur. Değişenler: Flask
yerine FastAPI ve onunla gelenler, UI'da JavaScript yerine TypeScript.

| Parça | Seçim |
|---|---|
| Dil | Python |
| Web sunucusu | FastAPI, Uvicorn'la çalışır |
| Alanlar ve kontrolleri | Pydantic (FastAPI'yle gelir) |
| ComfyUI'ye istek | httpx |
| Depo | Drive API'nin resmi Python kütüphanesi |
| Üretim | ComfyUI |
| Video işleme | ffmpeg |
| UI | React, Vite, TypeScript |
| MCP adaptörü | Python, MCP'nin Python SDK'sı |
| Testler | pytest (core ve adaptör), Vitest (UI), Playwright (uçtan uca) |

## FastAPI

- `GET /api`'nin iskeleti (endpoint'ler, aldıkları alanlar, alanların türü) koddan kendiliğinden
  çıkar; kod değişince o da değişir.
- Açıklamaları biz yazarız: her endpoint'in ve her alanın açıklaması, agent'a yazar gibi.
- Hata mesajlarını biz yazarız. FastAPI'nin kendi kuru mesajları kapatılır; her hata neyin eksik ya
  da yanlış olduğunu ve nedenini söyler. Ör. "`prompt` eksik. `t2i` prompt olmadan fotoğraf
  üretemez; sahnede ne olduğunu yaz." Gerçek mesajlar İngilizcedir (11. adım).
- Endpoint'ler async yazılmaz. Drive'a gitmek gibi yavaş işler sunucuyu dondurmaz.

## UI'da TypeScript

- UI, agent'la aynı endpoint'leri kullanır. Endpoint'lerin tanımı FastAPI'nin tam OpenAPI'sinden
  (`/api/openapi.json`) UI'ın TypeScript türlerine kendiliğinden geçer; `GET /api` agent içindir
  (6. adım).
- Core'da bir endpoint değişip UI ona uymazsa hata UI derlenirken görünür, çalışırken değil.
