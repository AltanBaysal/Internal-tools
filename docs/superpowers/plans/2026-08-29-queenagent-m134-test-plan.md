# Madde 134 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-29-queenagent-m134-plan-geri-okuma-testler-design.md](../specs/2026-08-29-queenagent-m134-plan-geri-okuma-testler-design.md)
**Bu tur yalnız test dosyalarına dokunur.**
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `test_skills.py`: akışın hangi planı okuyacağını söylemesi — bir kırmızı.

## B. Kelime tavanı ve mevcut plan pinleri bekçi olarak duruyor.

## C. İki komut koşulur; beklenen: bir kırmızı, defter çifti bilinen kırmızı.

## D. Kırmızı commit.

## Bilerek yapılmayanlar: `skip`/`xfail` yok; kod ellenmez; taban ve araç tanımları ellenmez.
