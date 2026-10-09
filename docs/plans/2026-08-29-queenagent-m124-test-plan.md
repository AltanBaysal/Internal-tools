# Madde 124 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-29-queenagent-m124-cache-kimligi-testler-design.md](../specs/2026-08-29-queenagent-m124-cache-kimligi-testler-design.md)
**Bu tur yalnız test dosyalarına dokunur.**
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. Fake'lere `conversation_id=""` parametresi: kaydeder, davranış değiştirmez.

## B. Tasarımdaki dört test yazılır.

## C. İki komut koşulur; beklenen: dört yeni kırmızı + bilinen defter çifti, başka kırmızı yok.

## D. Kırmızı commit.

## Bilerek yapılmayanlar: `skip`/`xfail` yok; client, engine, port, use case ellenmez.
