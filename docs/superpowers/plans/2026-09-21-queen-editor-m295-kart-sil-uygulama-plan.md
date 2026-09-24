# Madde 295 — Kartı sil, implementasyon turunun planı

**Spec:** [m295 implementasyon turu](../specs/2026-09-21-queen-editor-m295-kart-sil-uygulama-design.md)

İki dosya: `backend/.../usecases/remove_frames.py`, `frontend/.../PhotoDetail.jsx`. Testlere
dokunulmaz — turun testleri `b25a0f81`'de yazıldı.

## Adımlar

1. **`remove_frames`:** `removed` listesi kimlik yerine `(kimlik, borçlu katmanlar)` taşır, ve
   yazma döngüsü katman başına bir satır yazar. `layer_file` import edilir. Dönen cevabın şekli
   *(`{"deleted": [...], "removed": [...]}`)* kimlik listesi olarak kalır — bu cevabı ekran okuyor.

2. **Modül açıklaması:** *"not yet -> nothing to delete; the log says removed"* satırı hangi yuvaya
   yazıldığını söyler.

3. **`PhotoDetail`:** `holds` dalı iki düğmeye çıkar. Kartınki `setAsking("frame")` açar — fotoğraf
   sekmesindeki pencerenin aynısı, `lostLayers` cümlesiyle.

4. **Dört test satırı koşulur.**

5. **`npm run build --prefix queen-editor/frontend`**, ve `dist` aynı commit'e girer.

## Beklenen yeşil

Turun dört testi döner. Özellikle bakılacaklar: `test_a_frame_that_was_never_produced_only_leaves_-
the_queue`, `test_a_failed_frame_leaves_the_gallery_the_same_way`, ve detay sayfasının *"sekme başına
tek yıkıcı düğme"* testleri.
