# Madde 136 · Tur 1 (test) — Plan

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](2026-08-25-queenagent-v5-roadmap.md) · Madde 136
**Bu tur yalnız test dosyalarına dokunur.**
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## Sorun

`_build`'ın cevabı `f"Wrote {len(prompts)} prompts to ..."` — ham sayı, sabit çoğul. Tek kareli
senaryoda `Wrote 1 prompts`. Bir satır altındaki `outcome` aynı sayıyı `counted()` ile doğru
söylüyor.

Spec ayrı bir belge almıyor: sorun tek cümle, yol ve karar yol haritasının maddesinde yazılı, ve
bir tasarım belgesi onu üçüncü kez kopyalardı *(bir doku kodun söylediğini tekrarlamaz)*.

## A. `test_tools.py`: tek kareli yapıdan `1 prompt` — bir kırmızı.

## B. `test_tools.py`: iki kareli yapı `2 prompts` demeye devam eder — bir bekçi.

## C. İki komut koşulur; beklenen: bir kırmızı, bir bekçi yeşil, defter çifti bilinen kırmızı.

## D. Kırmızı commit.

## Bilerek yapılmayanlar: `skip`/`xfail` yok; kod ellenmez; `build_prompts`'un promptları geri vermemesi ellenmez.
