# Madde 292 — Kutu kimliği, test turunun planı

**Spec:** [m292 test turu](../specs/2026-09-21-queen-editor-m292-kutu-kimligi-testler-design.md)

Tek dosya değişiyor: `queen-editor/backend/tests/test_photo_usecases.py`. Üretim kodu bu turda
**hiç** ellenmiyor.

## Adımlar

1. **Plana video işi koyabilen bir yardımcı ekle.** Bugünkü `planned(*frames)` yalnız fotoğraf işi
   üretiyor *(`frame(n, letter, prompt)`)*. Yanına, bir kimliğe istenen tipte iş yazan küçük bir
   yardımcı gelir; ikisi de aynı `FakePlanStore`'u döndürür. Var olan `planned` değişmez — değişirse
   onu kullanan onlarca test bu maddenin kapsamına girerdi.

2. **Altı testi galeri bölümüne yaz**, spec'teki adlarla ve o sırayla:
   - `test_a_frame_planned_only_as_video_is_in_the_gallery`
   - `test_a_video_born_frames_status_comes_from_its_video`
   - `test_a_video_born_frame_keeps_its_name`
   - `test_a_frame_that_has_a_photo_job_still_opens_with_it`
   - `test_a_video_born_frame_leaves_the_gallery_when_its_video_is_deleted`
   - `test_a_video_born_frames_planned_prompt_is_the_videos`

   Her biri `list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")` çağırır ve
   dönen listeye bakar — bugünkü galeri testlerinin şekli budur.

3. **Dördüncü test bugünkü davranışı çiviliyor.** Fotoğraf ve video işi birlikte planlanan kartın
   tek satır açması ve durumunu fotoğrafından alması: bu test **bugün de yeşil** olmalı. Kırmızı
   çıkarsa yardımcı yanlış yazılmış demektir, madde değil.

4. **Takımı koş, kırmızıyı gör, kırmızıyı commit'le.** Dört satırın dördü de koşulur; kırmızı olması
   beklenen yalnız `python -m pytest queen-editor -q`, ve orada da yalnız bu beş yeni test.

## Beklenen kırmızı

1, 2, 3, 5, 6 düşer — bugünkü `list_frames` fotoğraf işi olmayan kimliği hiç satır saymıyor, yani
galeri boş döner. 4 yeşil kalır.

## Bu turda yapılmayacaklar

- `list_frames.py`'a ve başka hiçbir üretim dosyasına dokunulmaz.
- Silme kuralının genelleştirilmesi *(son katman gidince kutu gider)* — 294.
- Fotoğrafsız kartın ekranda ne çizdiği — 296, ve frontend tarafı.
