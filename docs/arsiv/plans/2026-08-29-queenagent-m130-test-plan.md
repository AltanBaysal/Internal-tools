# Madde 130 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-29-queenagent-m130-kapanis-testler-design.md](../specs/2026-08-29-queenagent-m130-kapanis-testler-design.md)
**Bu tur yalnız test dosyalarına dokunur.**
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `test_skills.py`: prompt+ kendi kapanışını söyler — bir kırmızı.

## B. Kelime tavanı testi bekçi olarak duruyor; asıl kısıt o.

## C. İki komut koşulur; beklenen: bir kırmızı, defter çifti bilinen kırmızı.

## D. Kırmızı commit.

## Bilerek yapılmayanlar: `skip`/`xfail` yok; kod ellenmez; taban ve akış metni ellenmez.
