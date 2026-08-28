# Madde 129 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-29-queenagent-m129-baglam-kabi-testler-design.md](../specs/2026-08-29-queenagent-m129-baglam-kabi-testler-design.md)
**Bu tur yalnız test dosyalarına dokunur.**
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `test_context_box.py` doğar: kabın kendi kuralları, yedi test.

## B. `test_stream_answer.py`: kabın isteğe nasıl bindiği, beş test.

## C. İki komut koşulur; beklenen: on iki yeni kırmızı + bilinen defter çifti.

## D. Kırmızı commit.

## Bilerek yapılmayanlar: `skip`/`xfail` yok; kod ellenmez.
