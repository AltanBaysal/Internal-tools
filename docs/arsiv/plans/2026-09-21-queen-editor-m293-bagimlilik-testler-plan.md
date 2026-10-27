# Madde 293 — Bağımlılık, test turunun planı

**Spec:** [m293 test turu](../specs/2026-09-21-queen-editor-m293-bagimlilik-testler-design.md)

İki dosya, yalnız test: `backend/tests/test_layers.py` ve
`backend/tests/test_photo_usecases.py`. Kaynak koda bu turda dokunulmuyor.

## Adımlar

1. **`test_layers.py`** — `can_produce` testlerinin hemen ardına, `cell` yardımcısından önce üç test:
   `NEEDS` tablosu, `falls_with(VIDEO)`/`falls_with(AUDIO)`, ve `falls_with(PHOTO)`. Kuralın kendi
   testleri kuralın kendi dosyasında duruyor.

2. **`test_photo_usecases.py` — silme.** `test_deleting_a_sound_leaves_the_video_alone`'un ardına
   iki test. İkisi de mevcut `layered_project()` kurgusunu kullanıyor *(fotoğraf + video + ses)*;
   yeni yardımcı gerekmiyor. Beşinci test bugünkü `test_deleting_a_video_takes_the_sound_over_it`'in
   söylediğini tekrar etmez — o duruyor; bu turun beşinci maddesi onun yerine **fotoğraf silinirken**
   videonun düşmediğini söyleyen dördüncü testin ikizi olarak yazılmaz. *(Spec'teki 5, bugünkü
   testtir: yeniden yazılmıyor, yerinde bırakılıyor ve implementasyon turunda yeşil kalması
   beklenir.)*

3. **`test_photo_usecases.py` — kapsam.** `test_audio_skips_a_frame_that_has_no_video`'nun ardına iki
   test, komşuları gibi düz galeri sözlükleriyle: fotoğrafsız kart video kapsamında, ve ses hâlâ video
   istiyor.

4. **Dört test satırı koşulur.**

## Beklenen kırmızı

- `test_layers.py`: üç test, `AttributeError` — `NEEDS` ve `falls_with` yok.
- `test_photo_usecases.py`: `test_deleting_the_photo_leaves_the_video_alone` düşer; bugün fotoğrafla
  birlikte video ve ses de siliniyor.

**Dört kırmızı.** Kapsam testleri ve bugünkü silme testleri yeşil geçer. Başka bir testin düşmesi bu
turun hatasıdır, maddenin değil.

## Bu turda yapılmayacaklar

Kod yok: `layers.py`, `remove_layer.py` ve `queue_layer.py` implementasyon turunda değişir.
