# Madde 246 · dynv2 sahneye göre ve en başta — test turunun tasarımı

**Tarih:** 19 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey. H3 talimatının metni 19 Eylül'de kullanıcıyla birlikte yazıldı *(uygulama turunun
tasarımında, olduğu gibi)*.

## Bugün ne oluyor

- H3 talimatı `dynv2`'yi her prompt'a zorunlu yazdırıyor, `[Shot 1] dynv2.` olarak.
- Üretici, gelen prompt'un önüne resim cümlesini koyuyor. `dynv2` modele giden prompt'un ilk
  kelimesi olmuyor.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | H3 talimatı fotoğrafın videonun ilk karesi olduğunu söylüyor | **kırmızı** |
| 2 | H3 talimatında `dynv2.` ilk satır, çoğu sahnede yazılıyor, sakin ya da durgun sahnede yazılmıyor; bölüm `[Shot 1] dynv2` demiyor | **kırmızı** |
| 3 | Üç bölüm talimatta duruyor | yeşil *(bekçi)* |
| 4 | `dynv2.` ile başlayan prompt: I2VA'da modele giden prompt `dynv2. <resim cümlesi>` ile başlıyor, geri kalanı ondan sonra | **kırmızı** |
| 5 | Aynısı FL2VA'da | **kırmızı** |
| 6 | `dynv2`'siz prompt bugünkü gibi resim cümlesiyle başlıyor | yeşil *(bekçi, mevcut test)* |

## Bu turda değişen

- `test_video_prompt_writer.py`: `test_the_h3_instruction_asks_for_the_trigger_and_the_three_sections`
  gidiyor. Yerine `test_the_h3_instruction_says_the_photo_is_the_first_frame` *(1)*,
  `test_the_h3_instruction_opens_with_dynv2_unless_the_scene_is_calm` *(2)*,
  `test_the_h3_instruction_asks_for_the_three_sections` *(3)*.
- `test_comfy_h3_video_generator.py`: `test_dynv2_goes_before_the_i2va_picture_sentence` *(4)*,
  `test_dynv2_goes_before_the_fl2va_picture_sentence` *(5)*.
