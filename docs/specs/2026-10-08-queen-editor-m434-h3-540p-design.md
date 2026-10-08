# Madde 434 · H3 videosu 540p'de — tasarım

**Tarih:** 8 Ekim 2026 · **Madde:** [v9 yol haritası](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md),
434 · **Dal:** `feat/queen-editor-v9` · **Kurallar:** [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Kod için hiçbir şey; boyut 8 Ekim'de seçildi *(aşağıda)*. **Çıktıyı değiştirdiği için commit ve push
kullanıcının onayını bekler**, ve kullanıcı Colab'da dener — notebook dalı çektiği için push'tan sonra:
videonun 576 × 864 çıkıp çıkmadığı, esneyip esnemediği, ve 12 saniyelik videonun GPU'ya sığıp
sığmadığı orada görülür.

## Ne, neden

Kullanıcı H3 videosunu daha yüksek çözünürlükte istiyor *(8 Ekim — "abi çözünürlüğü arttırmak
istiyorum")*. Bugün iki H3 grafiğinin Director'ı (`"2730"`) 480p'de, oran `auto`: dikey 2:3 kareden
512 × 768. **Olacak:** 540p, 576 × 864, ve oran yine `auto`.

**Oran `auto` kalır.** Önceki bir denemede fotoğrafla videonun oranı farklıyken video yatayda esnedi
*(kullanıcı — "fotoğrafın oranı ile videonun oranı olmaaycın video yatayda esniyor")*; video
fotoğrafın oranını izler, kare ya da sabit bir oran yapılmaz.

**576 × 864 panelin hazır boyutu değil, bir hesap.** Kullanıcı ComfyUI'nin Director panelinde
"2:3 · 540p · 576 × 896 · 32px H3 grid"'i seçti. Panel iki kenarı 32px ızgaraya ayrı ayrı yuvarlıyor,
ve 576 × 896 tam 2:3 değil: 576 / 896 = 0.643, fotoğrafın 1024 × 1536'sı 0.667 — fark %3.6.
`test_workflow_asset.py`'nin `test_the_photo_and_the_h3_video_agree_on_the_shape_of_the_frame`'i
iki oranın %1'den fazla ayrılmasına izin vermiyor, çünkü fotoğrafı kendi boyutuna çeken bir grafik onu
sessizce esnetir. 576 × 864 tam 2:3 ve iki kenarı da ızgarada (576 = 18 × 32, 864 = 27 × 32).
Kullanıcı ikisinden bunu seçti *(8 Ekim — "bu olsun")*.

## Boyut nerede duruyor

Her iki grafikte de — `assets/workflow_video_h3_api.json` (I2VA) ve
`assets/workflow_video_h3_first_last_api.json` (FL2VA) — boyut iki yerde:

| Yer | Bugün | Olacak |
|---|---|---|
| Director'ın girdileri, `width` / `height` | 512 / 768 | **576 / 864** |
| `timeline_data`'nın `resolution.resolution`'ı | `"480p"` | **`"540p"`** |

Dokunulmayanlar, ve neden:

- `resolution.aspect` — `"auto"` kalır *(yukarıda)*.
- `resolution`'ın geri kalanı — `input_scaling` (`"Auto"`) ve `custom_*` alanları — kullanıcı
  yalnız boyutu seçti. `custom_*` adlarıyla özel oranın değerleri, ve oran `auto`.
- Timeline satırının `source_width` / `source_height`'ı (1024 × 1536) — örnek resmin boyutu, videonun
  değil; üretici bugün de dokunmuyor.
- İki `builder_state` kopyası — boyut taşımıyor.
- `"2737"` Model Preview Override'ın `max_resolution: 512`'si — örnekleme sırasında küçük VAE'den
  geçen önizlemenin boyutu, videonunki değil.
- `comfy_h3_video_generator.py` boyuta hiç dokunmuyor: ne `width`/`height`'ı ne `resolution`'ı
  yazıyor. Değişmez.

## Risk

H3 Director'ı ComfyUI'nin kendi düğümü, ve kaynağı bu depoda yok. Boyutu `width` / `height`'tan mı
okuyor, yoksa `540p` ve `auto`'dan kendisi mi hesaplıyor, bilinmiyor. Kendisi hesaplıyorsa bu sayıları
yok sayabilir ve panelin 576 × 896'sını üretebilir; kullanıcının Colab denemesi hangisi olduğunu
gösterir.

## Testler — `backend/tests/test_workflow_asset.py`

- **`test_both_h3_graphs_render_four_seconds_at_512_by_768`** bugünkü boyutu sabitliyor. Adı
  `test_both_h3_graphs_render_four_seconds_at_576_by_864` olur, docstring'i boyutun neden bu olduğunu
  söyler, ve iki grafikte de `(duration, width, height) == (4, 576, 864)`'ü, ve timeline'ın
  `resolution`'ında `(aspect, resolution) == ("auto", "540p")`'yi sorar. Grafikler değişmeden kırmızı.
- **`test_the_photo_and_the_h3_video_agree_on_the_shape_of_the_frame`** olduğu gibi kalır ve yeşil
  kalır: 576 / 864 fotoğrafın oranıyla aynı.
- `test_comfy_h3_video_generator.py`'nin sahte grafiği 512 × 768 diyor; o üreticinin testi için kurulmuş
  bir grafik, gönderilen grafiği sabitlemiyor. Değişmez. `480p`'yi hiçbir test sabitlemiyor.

## Sınırlar

- Yalnız iki H3 grafiğinin Director'ı ve `test_workflow_asset.py`'nin bir testi değişir.
- Süre, prompt, seed, model, LoRA ve öteki düğümler değişmez. WAN grafikleri ve fotoğraf grafiği
  değişmez.
- Frontend değişmez; `dist`'e dokunulmaz.

## Bitti sayılır

- İki H3 grafiğinde Director 576 × 864, timeline'ı `540p`, oranı `auto`.
- Yeni test grafikler değişmeden kırmızı, değişince yeşil; şekil testi baştan sona yeşil.
- Dört satır yeşil; sayılar değişmez, çünkü bir test yeniden adlandırıldı, eklenmedi.
- Colab'da: dikey 2:3 bir kareden üretilen H3 videosu 576 × 864, ve esnemiyor — kullanıcının
  denemesinde görülecek.
