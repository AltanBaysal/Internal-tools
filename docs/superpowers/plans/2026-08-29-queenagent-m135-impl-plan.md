# Madde 135 · Tur 2 (uygulama) — Plan

**Testler:** [2026-08-29-queenagent-m135-onizleme-testler-design.md](../specs/2026-08-29-queenagent-m135-onizleme-testler-design.md)
**Kırmızı commit:** `f25f127`

## A. `tools.py` · `_try_character` kurduğu promptları cevabında verir.

Cümle dosyayı adıyla söylemeye devam ediyor, ardından promptlar geliyor. Sayı `counted()` ile,
yani tek promptta *"1 prompt"*.

## B. `_build` ellenmiyor.

Madde 130'un kuralı: kurulan liste geri basılmaz. Ayrım bu maddenin sınırı, ve testi bekçi olarak
tutuyor.

## C. İki komut koşulur; beklenen yeşil: iki kırmızı döner, iki bekçi yeşil kalır.

## D. Yeşil commit, ardından okuma kopyası.

## Bilerek yapılmayanlar: `build_prompts`'un cevabı, `_build`'ın kendi tekil hatası, ön yüz, `dist`.
