# Madde 136 · Tur 2 (uygulama) — Plan

**Testler:** [2026-08-29-queenagent-m136-test-plan.md](2026-08-29-queenagent-m136-test-plan.md)
**Kırmızı commit:** `d15d3d5`

## A. `tools.py` · `_build`'ın cümlesi `counted()` çağırır.

`f"Wrote {len(prompts)} prompts to {written}."` → `f"Wrote {counted(len(prompts), 'prompt')} to
{written}."` Bir satır altındaki `outcome` zaten aynı çağrıyı yapıyordu; şimdi ikisi aynı şeyi
söylüyor.

## B. İki komut koşuldu: **645 yeşil**, frontend 568 yeşil, defter çifti bilinen kırmızı.

## C. Yeşil commit.

## Bilerek yapılmayanlar

`build_prompts`'un promptları geri vermemesi *(130 ile 135'in sınırı)*, cevabın geri kalanı, ön
yüz, `dist`. Okuma kopyası da değişmiyor: bu cümle bir araç **tanımı** değil, aracın koşarken
verdiği cevap, ve belge tanımları taşıyor.
