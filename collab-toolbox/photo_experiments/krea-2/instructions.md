# Krea 2 — Talimatlar

Madde 485 *(v10 yol haritası)*. İki defter: `turbo.ipynb` (8 adım) ve `raw.ipynb` (52 adım, ya da Turbo
LoRA'sıyla 8). Grafikler Comfy-Org'un **resmî şablonları**, olduğu gibi. Hangi dosya neden iniyor:
[indirilecekler.md](indirilecekler.md).

## Çalıştırma

1. Colab 🔑 Secrets'a **`CIVITAI_COOKIE`** ekle (Civitai dosyaları için zorunlu): civitai.red → giriş →
   F12 → Application → Cookies → `__Secure-civ-token`, değere çift tıkla → Ctrl+A → Ctrl+C. `HF_TOKEN`
   isteğe bağlı.
2. Defteri Colab'a yükle (**File → Upload notebook**), **Runtime → Change runtime type → A100**,
   **Run all**. Her şey baştan iner. En alttaki linke gir.
3. Turbo: sol kenarda **Workflows** → bir workflow. RAW: sol kenarda **Templates** → Krea 2 → int8
   *Text to Image*; eksik model penceresini kapat (Turbo modeli bu defterde yok). Yaz → **Run**
   (Ctrl+Enter).

## Hangi şablon

- `image_krea2_turbo_t2i_int8`: prompt'tan resim; `prompt`'a yaz.
- `image_krea2_turbo_int8_image_style_reference`: referans resmin tarzında. Resmi bağlı `Load Image`'a
  yükle (`image1`); bir ya da iki referans, ikincisi için yeni bir `Load Image`'ı `image2`'ye bağla.
  Tetik yok: resim ve prompt.

## prompt_enhance

t2i şablonunda **açık** geliyor: metin kodlayıcı (Qwen3-VL) prompt'u bir talimatla düzyazıya yeniden
yazar. Bizim etiket listemizi olduğu gibi denemek için büyük node'da **kapat**.

## Model değiştirmek

Büyük node'da `unet_name`:
- Turbo defterinde: `krea2_turbo_int8_convrot`, `Wulver_v0.5_fp8_e4m3fn`, `sickOllie_krea2_3035266`,
  `moodyKrea2MixUncensoredV8FREEV8_v80BF16FP8_3213091`.
- RAW defterinde: `krea2_raw_int8_convrot`, `Wulver_v0.5_non_turbo_bf16`.

## Adım ve cfg

Dışa açık değiller: büyük node'un alt grafiğine gir, `KSampler`'ın `steps`'i ve `cfg`'si (stil
referansında `BasicScheduler`'ın `steps`'i ve `CFGGuider`'ın `cfg`'si). cfg 1'de negatif prompt hiçbir
şey yapmaz.

**cfg 3,5'te negatif** (RAW, ya da LoRA'sız Wulver Non-Turbo): şablonun negatifi `ConditioningZeroOut`;
Wulver'ın README'si cfg 1'in üstünde negatif olarak boş bir `CLIPTextEncode` istiyor. Alt grafiğe gir,
boş bir `CLIPTextEncode` ekle, `clip`'ini `CLIPLoader`'dan al, ve `KSampler`'ın `negative`'ine
`ConditioningZeroOut` yerine onu bağla.

- **Turbo:** 8 adım, cfg 1, `euler` / `simple` — şablon böyle açılıyor.
- **RAW:** 52 adım, cfg 3,5 (Krea'nın kartı). Sampler ve scheduler yazılı değil; şablonunki kalır.
- **RAW + Turbo LoRA** (`krea2_turbo_lora_rank_64_bf16`): güç 1,0, 8 adım, cfg 1; ya da güç 0,6, 14
  adım, cfg 1. Kaynak Wulver'ın README'si, RAW'ın bir ince ayarı için; çıplak RAW'da denenmemiş.
- **Wulver (Turbo):** 8 adım, cfg 1, `euler` / `simple`.
- **Wulver Non-Turbo:** LoRA'sız 52 adım, cfg 3,5 (negatif yukarıdaki gibi); ya da Turbo LoRA'sıyla
  1,0 / 8 adım / cfg 1 (0,6 / 14 adım da olur); `euler` / `simple`.
- **Sick Ollie:** Euler, Beta, cfg 1, 9 adım; yazarı en iyi 1440 × 1920 diyor.
- **Moody:** Euler A (`euler_ancestral`), Beta, 8 adım (ayrıntı için 12'ye kadar) — yazarın V6 notu;
  V8 için ayrıca bir ayar yazılı değil.

RAW defterinin özeti Krea'nın RAW int8'inde ComfyUI'nin niceleme işaretini bulamazsa uyarır: o modelde
resim bozuk çıkarsa sebep bu olabilir.

## LoRA eklemek

- **Tek LoRA, t2i'de:** şablonun kendi yuvası var. Büyük node'da `enable_lora`'yı aç, `lora_name`'den
  seç, `lora_strength`; `lora_trigger_word` prompt'un sonuna eklenir — tetiği olmayan LoRA'da boşalt
  (şablon tablodaki hiçbir LoRA'nın olmayan `muted minimalist sketch style` ile açılıyor).
- **Birden fazlası:** alt grafiğe gir, şablonun `LoraLoaderModelOnly`'si ile `Switch (Model)`'ın
  `on_true` girişi arasına yeni bir `LoraLoaderModelOnly` koy; `enable_lora` açık kalsın. Stil
  referansında: şablonun `LoraLoaderModelOnly`'si (`krea2_style_reference`) ile `ModelSamplingFlux`
  arasına.
- **RAW'da Turbo LoRA'sı** da böyle eklenir.

## Tetik sözcükleri

Krea'nın tarz LoRA'ları, güç 1,0:

- `krea2_darkbrush` — `monochrome ink wash style`
- `krea2_dotmatrix` — `monochrome stippling style`
- `krea2_kidsdrawing` — `naive expressive sketch style`
- `krea2_neondrip` — `textured abstract style`
- `krea2_rainywindow` — `rainy window style`
- `krea2_retroanime` — `purple retro anime style`
- `krea2_softwatercolor` — `art deco watercolor style`
- `krea2_sunsetblur` — `ethereal motion blur style`
- `krea2_vintagetarot` — `vintage tarot style`

`krea2_style_reference` ve SNOFS'ta tetik yok. SNOFS etiketle değil düzyazıyla eğitilmiş.

`krea2 sex` LoRA'larının tetik kelimeleri sayfasında:
[carry](https://civitai.red/models/2801881?modelVersionId=3170121) ·
[dog](https://civitai.red/models/2801881?modelVersionId=3158793) ·
[Mis](https://civitai.red/models/2801881?modelVersionId=3169965) ·
[CG](https://civitai.red/models/2801881?modelVersionId=3158775) ·
[spo](https://civitai.red/models/2801881?modelVersionId=3169634) ·
[BJ](https://civitai.red/models/2801881?modelVersionId=3158893).

## Wulver

Prompt sırası: önce bir rating etiketi, sonra varsa `@sanatçı`, sonra tarif — ör. `sfw, @sanatçı, A
digital painting of …`. `@sanatçı` 1.113 tarzdan biri ve
[ARTISTS.md](https://huggingface.co/Vaelico/Wulver/blob/main/ARTISTS.md)'deki adla birebir, `@` dahil.
Düzyazı en iyi çalışıyor, ama booru / e621 etiketleri de çalışıyor — bizim prompt'larımız etiket
listesi. Konusu anthro / furry, anime / kemono.

## Not

Moody V8 gerçekçi fotoğrafa yönelik (yazarı: *"RAW-style photography, skin texture"*). Civitai'nin öteki
NSFW LoRA'larının ve Sick Ollie'nin de gerçekçi fotoğraf tarzında olduğu doğrulanmadı.
