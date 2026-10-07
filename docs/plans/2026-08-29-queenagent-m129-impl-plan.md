# Madde 129 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-29-queenagent-m129-baglam-kabi-uygulama-design.md](../specs/2026-08-29-queenagent-m129-baglam-kabi-uygulama-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `domain/context_box.py` doğar: `BOX_LIMIT`, `files_opened`, `schema_was_read`.

## B. `stream_answer.py`: kap metne çevrilir ve isteğin kuyruğuna, adların ardına konur.

## C. İki komut koşulur; beklenen yeşil: on yedi yeni test dahil tamamı, defter çifti bilinen kırmızı.

## D. Yeşil commit.

## Bilerek yapılmayanlar: disk şeması, `tool` mesajları, yazma araçları ellenmez.
