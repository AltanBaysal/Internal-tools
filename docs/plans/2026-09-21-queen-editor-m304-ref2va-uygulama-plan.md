# Madde 304 — REF2VA, implementasyon turunun planı

**Spec:** [m304 implementasyon turu](../specs/2026-09-21-queen-editor-m304-ref2va-uygulama-design.md)

Testlere dokunulmaz — turun testleri `c1b55ad8`'de yazıldı.

## Adımlar

1. **Port ve dört üretici** imzayı alır.
2. **`reference_files`** senaryosu.
3. **`run_loop`** referans işine havuzu veriyor; yedi kapı taşıyor.
4. **H3 üreticisi** REF2VA'yı koşuyor.
5. **`main.py`** bağlar.
6. **Dört test satırı koşulur.**

## Beklenen yeşil

Turun yedi testi, ve üreticinin bugünkü bütün testleri.
