# Madde 124 · Tur 2 (uygulama) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 124
**Testler kırmızı commit'te (86502c1).**

## Yol

Kimlik yukarıdan aşağı bir parametre olarak iner; hiçbir katman onu üretmez, yalnız taşır:

- `stream_answer`: `engine.stream(..., conversation_id=chat_id)` — sohbetin id'si zaten eldedir.
- `ports.py` · `Engine.stream`: imzaya `conversation_id: str = ""` ve bir cümle docstring.
- `xai_engine.py` · `XaiEngine.stream`: client'a aynen geçirir; çeviri yapmaz.
- `client.py` · `XaiClient.stream`: `_request`'e geçirir; `_request` boş olmayan kimliği
  `x-grok-conv-id` başlığı yapar. `complete` `_request`'i kimliksiz çağırır, başlık göndermez.

## Bilerek yapılmayanlar

`complete` imzası değişmez (üretimde çağıranı yok); kimlik gövdeye değil başlığa gider
(cache anahtarı gövde prefix'idir, gövdeye giren kimlik prefix'i bozar); frontend, dist,
defter ellenmez.
