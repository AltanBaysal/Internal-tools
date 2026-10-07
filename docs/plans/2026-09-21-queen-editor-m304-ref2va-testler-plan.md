# Madde 304 — REF2VA, test turunun planı

**Spec:** [m304 test turu](../specs/2026-09-21-queen-editor-m304-ref2va-testler-design.md)

İki test dosyası: `test_comfy_h3_video_generator.py`, `test_photo_usecases.py`. Kaynak koda
dokunulmuyor.

## Adımlar

1. **Üreticinin beş testi** — dosyanın kendi `FakeClient`'ı ve `director` kurgusuyla.
2. **Döngünün iki testi** — `FakeGenerator` artık `references`'ı da kaydediyor, ve `make_job` bir
   havuz çağrılabiliri alıyor.
3. **Dört test satırı koşulur.**

## Beklenen kırmızı

Yedi test: ne port alanı, ne üreticinin kipi, ne de döngünün havuzu var.
