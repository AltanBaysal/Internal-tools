# Madde 125 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-29-queenagent-m125-arac-tanimlari-testler-design.md](../specs/2026-08-29-queenagent-m125-arac-tanimlari-testler-design.md)
**Bu tur yalnız `test_tools.py`'a dokunur.**
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `test_tools.py`'a Madde 125 bölümü: tasarımdaki iki test, pinleriyle.

## B. İki komut koşulur; beklenen: iki yeni kırmızı + bilinen defter çifti, başka kırmızı yok.

## C. Kırmızı commit.

## Bilerek yapılmayanlar: `skip`/`xfail` yok; `tools.py` ellenmez.
