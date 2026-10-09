# Madde 295 — Kartı sil, test turunun planı

**Spec:** [m295 test turu](../specs/2026-09-21-queen-editor-m295-kart-sil-testler-design.md)

İki test dosyası: `backend/tests/test_photo_usecases.py`,
`frontend/src/features/photo_generation/PhotoDetail.test.jsx`. Kaynak koda dokunulmuyor.

## Adımlar

1. **Backend testleri**, `remove_frames`'in bugünkü testlerinin yanına. Kart 292'nin
   `planned_layers` yardımcısıyla kurulur — plan hangi katmanı borçlandığını zaten taşıyor.

2. **Frontend testleri**, `PhotoDetail.test.jsx`'in silme bölümüne. Dosyanın kendi kurgu yardımcıları
   kullanılır; video sekmesine geçiş oradaki testlerin yaptığı gibi sekmeye basılarak yapılır.

3. **Dört test satırı koşulur.**

## Beklenen kırmızı

Backend'de iki, frontend'de iki. Bekçi testleri *(3 ve 6)* yeşil geçer.

## Bu turda yapılmayacaklar

Kod yok, `dist` yok.
