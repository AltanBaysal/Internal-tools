# Madde 132 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-29-queenagent-m132-replace-all-testler-design.md](../specs/2026-08-29-queenagent-m132-replace-all-testler-design.md)
**Bu tur yalnız test dosyalarına dokunur.**
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `test_tools.py`: bayrağın işi, sayısı, ve tanımdaki yeri — dört kırmızı.

## B. `test_tools.py`: bayraksız ret, bulunamayan metin, tek geçiş — üç bekçi.

## C. İki komut koşulur; beklenen: dört kırmızı, üç bekçi yeşil, defter çifti bilinen kırmızı.

## D. Kırmızı commit.

## Bilerek yapılmayanlar: `skip`/`xfail` yok; kod ellenmez; `add_frames` yok.
