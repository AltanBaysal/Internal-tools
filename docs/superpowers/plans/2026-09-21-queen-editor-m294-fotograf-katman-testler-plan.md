# Madde 294 — Fotoğraf katmanı, test turunun planı

**Spec:** [m294 test turu](../specs/2026-09-21-queen-editor-m294-fotograf-katman-testler-design.md)

İki test dosyası: `backend/tests/test_photo_usecases.py` ve `backend/tests/test_photo_routes.py`.
Kaynak koda bu turda dokunulmuyor.

## Adımlar

1. **Galeri testleri** — 292'nin bıraktığı yerin hemen ardına, `test_a_video_born_frames_planned_-
   prompt_is_the_videos`'tan sonra. Beşi de mevcut `planned_layers` yardımcısını kullanıyor; yeni
   yardımcı gerekmiyor.

2. **`file` testi kopya kartla yazılır.** `photo_file("0_a")` zaten `0_a.png` olduğu için, fotoğrafı
   kendi adını taşıyan bir kartta iki cevap ayırt edilemez. Kopya kart *(`C1_0_a`, kaynağının
   resmini tutar)* ikisini ayırır: silinmiş dosya `0_a.png`, kartın kendi adı `C1_0_a.png`.

3. **Boş kutu testine ikinci bir kart konur** — galeri zaten boş dönerse test yanlış sebepten yeşil
   olur.

4. **`test_photo_routes.py`:** bugünkü `test_the_photo_layer_is_not_deleted_this_way` **yerini**
   `test_the_photo_is_a_layer_that_can_be_deleted`'a bırakır. Koruduğu kural kalkıyor; iki testi yan
   yana bırakmak takımın kendi kendisiyle çelişmesi olurdu.

5. **Dört test satırı koşulur.**

## Beklenen kırmızı

Dört kırmızı: fotoğrafı silinmiş kartın galeride durması *(iki test)*, hâlâ işi olan kartın durması,
ve kapının açılması. Boş kutu ve sıra testleri yeşil geçer.

## Bu turda yapılmayacaklar

Kod yok. Ekran yok — fotoğraf silme düğmesi bu maddenin işi değil.
