# Madde 305 — Video ve ses referansı, test turunun planı

**Spec:** [m305 test turu](../specs/2026-09-21-queen-editor-m305-video-ses-referansi-testler-design.md)

Tek test dosyası: `backend/tests/test_comfy_h3_video_generator.py`. Kaynak koda dokunulmuyor.

## Adımlar

1. Üç tipli bir havuz kurgusu, ve beş test.
2. **Dört test satırı koşulur.**

## Beklenen kırmızı

Beş test: bugün üretici havuzun **yalnız** fotoğraflarını yazıyor, tipi sormadan hepsine `image`
diyor, ve `media_mode` diye bir alan tanımıyor.
