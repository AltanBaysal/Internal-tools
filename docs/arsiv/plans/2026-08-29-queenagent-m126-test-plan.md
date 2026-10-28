# Madde 126 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-29-queenagent-m126-plan-isaretlemesi-testler-design.md](../specs/2026-08-29-queenagent-m126-plan-isaretlemesi-testler-design.md)
**Bu tur yalnız `test_skills.py`'a dokunur.**
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `test_skills.py`'a tek test: tasarımdaki iki pin.

## B. İki komut koşulur; beklenen: bir yeni kırmızı + bilinen defter çifti.

## C. Kırmızı commit.

## Bilerek yapılmayanlar: `skip`/`xfail` yok; `skills.py` ellenmez.
