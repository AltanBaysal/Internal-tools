# Madde 135 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-29-queenagent-m135-onizleme-testler-design.md](../specs/2026-08-29-queenagent-m135-onizleme-testler-design.md)
**Bu tur yalnız test dosyalarına dokunur.**
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `test_tools.py`: önizlemenin promptu ve tekili — iki kırmızı.

## B. `test_tools.py`: `build_prompts`'un promptları geri vermemesi ve dosyanın yine yazılması — iki bekçi.

## C. İki komut koşulur; beklenen: iki kırmızı, iki bekçi yeşil, defter çifti bilinen kırmızı.

## D. Kırmızı commit.

## Bilerek yapılmayanlar: `skip`/`xfail` yok; kod ellenmez; `build_prompts`'un cevabı ellenmez.
