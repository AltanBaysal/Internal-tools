# Madde 107 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-29-queenagent-m107-ritual-testler-design.md](../specs/2026-08-29-queenagent-m107-ritual-testler-design.md)
**Bu tur yalnız test dosyalarına dokunur; metinler ikinci turun.**
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `test_prompt.py`'a Madde 107 bölümü: iki test, tasarımdaki pinlerle.

## B. `test_skills.py`'a Madde 107 bölümü: üç test, tasarımdaki pinlerle.

## C. İki komut koşulur; beklenen: beş yeni kırmızı + bilinen defter çifti, başka kırmızı yok.

## D. Kırmızı commit.

## Bilerek yapılmayanlar: `skip`/`xfail` yok; `prompt.py` ve `skills.py` ellenmez.
