# Madde 123 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-29-queenagent-m123-persona-uygulama-design.md](../specs/2026-08-29-queenagent-m123-persona-uygulama-design.md)
**Testler kırmızı commit'te**; bu tur yalnız `skills.py`'a dokunur.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. İki metin tasarımdaki iskeletle yeniden yazılır; eski pin cümleleri aynen taşınır.

## B. Tavan aşılırsa kelime kırpılır, pin cümlesi asla.

## C. Docstring'e Madde 123 cümlesi.

## Beklenen yeşil: `test_skills.py` tamamı; defter çifti bilinen kırmızı.

## Bilerek yapılmayanlar: taban yönerge, şema, defter ellenmez; `dist` derlenmez.
