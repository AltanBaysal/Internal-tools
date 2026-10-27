# Madde 124 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-29-queenagent-m124-cache-kimligi-uygulama-design.md](../specs/2026-08-29-queenagent-m124-cache-kimligi-uygulama-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `client.py`: `stream`'e `conversation_id=""`; `_request` boş olmayanı başlık yapar.

## B. `xai_engine.py` ve `ports.py`: imza + geçiş; port'a bir cümle docstring.

## C. `stream_answer.py`: çağrıya `conversation_id=chat_id`.

## D. İki komut koşulur; beklenen yeşil: dört yeni test dahil tamamı, defter çifti bilinen kırmızı.

## E. Yeşil commit.

## Bilerek yapılmayanlar: `complete` imzası, frontend, dist, defter ellenmez.
