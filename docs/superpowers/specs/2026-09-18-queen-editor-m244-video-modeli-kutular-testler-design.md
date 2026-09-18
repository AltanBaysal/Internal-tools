# Madde 244 · Defterde video yine bir kutu, modeli altında — test turunun tasarımı

**Tarih:** 18 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey. Tasarım 18 Eylül'de kullanıcıyla kararlaştı *(maddenin satırında)*. H3'ün T4 bilgisi
formdan çıkıyor.

## Bugün ne oluyor

243'ten beri CONFIG'de video bir açılır liste: `VIDEO_MODEL = "Yok"  #@param ["Yok", "WAN", "H3"]`.
`INSTALL_VIDEO` ondan türüyor. İndirme listeleri `VIDEO_MODEL == "WAN"` / `"H3"` arkasında. Formun
Üreticiler satırı H3'ün T4'te koşmadığını söylüyor.

## Ne olacak

- **`INSTALL_VIDEO` yeniden bir kutu**, öteki iki üretici gibi kapalı geliyor.
- **Formda yeni bir bölüm.** Fotoğraf modellerinin altında `#@markdown ---` ve
  `#@markdown ### Video modelleri`, içinde iki kutu: `VIDEO_WAN` ve `VIDEO_H3`, ikisi de kapalı.
  Bölüm, fotoğrafınki gibi, başlığından ibaret.
- **İki kontrol**, fotoğrafınkinin yanında:
  - `assert not INSTALL_VIDEO or VIDEO_WAN or VIDEO_H3`: video var, model yok.
  - `assert not (VIDEO_WAN and VIDEO_H3)`: iki model birden.
- **Seçim tek bir addan okunuyor:** `VIDEO_MODEL`, kutulardan türeyen `wan`, `h3` ya da boş. Listeler
  `VIDEO_MODEL == "wan"` / `"h3"` arkasında. Disk hesabı ve `QE_VIDEO_MODEL` da bu addan okuyor.
  Uygulamanın gördüğü değer değişmiyor.
- **H3'ün T4 bilgisi formdan çıkıyor.**

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Üç üretici de kapalı gelen bir kutu | **kırmızı** |
| 2 | `VIDEO_WAN` ve `VIDEO_H3` kapalı gelen kutular | **kırmızı** |
| 3 | Form: fotoğraf bölümünden sonra bir ayraç ve **Video modelleri** başlığı, ikisi de video kutularının önünde; model bölümleri başlıklarından ibaret | **kırmızı** |
| 4 | Video işaretli, model yok → CONFIG'de duruyor | **kırmızı** |
| 5 | İki video modeli birden → CONFIG'de duruyor | **kırmızı** |
| 6 | WAN'ın ve H3'ün listeleri `VIDEO_MODEL == "wan"` / `"h3"` arkasında; H3'ün HF dosyaları tek bağlantıyla | **kırmızı** |
| 7 | Disk hesabı H3'ü `VIDEO_MODEL == "h3"` iken sayıyor | **kırmızı** |
| 8 | Defter `QE_VIDEO_MODEL`'i geçiyor | yeşil *(bekçi)* |

## Bu turda değişen

Yalnız `test_notebook_installs_the_producer_groups.py`:
- `test_photo_and_sound_each_have_a_checkbox_of_their_own` yeniden üç üreticiyi soruyor. Adı
  eskisine dönüyor: `test_every_producer_has_a_checkbox_of_its_own`.
- `test_video_is_one_pick_among_none_wan_and_h3` gidiyor. Yerine olgu 2, 4 ve 5'in testleri
  giriyor.
- `test_the_form_leaves_the_model_section_at_its_heading` iki bölümü soruyor.
- `test_the_form_gives_video_models_a_section_of_their_own` yeni.
- Listelerin, tek bağlantının ve disk hesabının testleri küçük harfli değerleri arıyor.
- `test_the_form_says_h3_does_not_run_on_a_t4` gidiyor *(kullanıcı kararı)*.
