# Madde 482 · Qwen Image 2.1 — nerede, nasıl denenir — araştırma

**Tarih:** 20 Ekim 2026 · **Madde:** [v10 yol haritası](../arsiv/roadmaps/2026-10-20-queen-editor-v10-roadmap.md),
482 · v10-4 · **Kod yok.** Kararları kullanıcı verir; deneme ve entegrasyon onlardan sonra başlar.

Kullanıcının sorusu *(20 Ekim)*: *"tamam şimdi qwen image geçelim comfy ui da yada nerede test edeceğiz
karar verelim ne öneriyorsun araştırıp yazar mısın mesela comfy ui da hazır workflow var mı vs vs gibi"*

İşaretler: **✅** resmî kaynaktan ya da koddan doğrulandı · **🗣️** üçüncü taraf ya da topluluk
kaynağı, resmî değil · **🧮** doğrulanmış sayılardan hesaplandı · **≈** tahmin, ölçülmedi.

## Öneri

1. **Önce bir lisans kararı gerekiyor.** Qwen-Image-2.1 açık ağırlıklı, ama lisansı Apache değil:
   **Qwen Research License**, yalnız ticari olmayan kullanım. Metin: *"FOR NON-COMMERCIAL PURPOSES
   ONLY"* ve *"You shall not use the Materials for any commercial purpose without obtaining a separate
   commercial license from us."* ✅ [LICENSE](https://huggingface.co/Qwen/Qwen-Image-2.1/blob/main/LICENSE)
   Kanallar gelir getiriyorsa bu bir engel. Seçenekler aşağıda, [Açık sorular](#açık-sorular) 1'de.
   Bunu bir hukuk görüşü olarak değil, lisansın kendi cümlesi olarak okuyun.
2. **İlk bakış için: ayrı, elle sürülen bir ComfyUI deneme defteri, Colab'da A100'de.** MiniMax H3 da
   böyle denenmişti: önce [video_experiments/minimax-h3/manual.ipynb](../../collab-toolbox/video_experiments/minimax-h3/manual.ipynb)
   (madde 213), sonra Queen Editor'e alındı (madde 243). Defter Comfy'nin **hazır resmî şablonunu**
   açar (`image_qwen_image_2_1_t2i.json`, Turbo'su da var) ve üç dosya indirir, toplam ~17,3 GB. Hepsi
   HF'te açık, Civitai'ye ve aynaya gerek yok. Uygulamanın koduna dokunulmaz. Bu defterde bir projeden
   alınmış gerçek prompt'lar denenir: bugünkü etiket listesiyle ve düzyazıya çevrilmiş hâliyle, üç
   boyutta, Turbo ve tam modelle.
   - İsteğe bağlı, kurulumdan önce 5 dakikalık bir ön bakış: resmî
     [HF Space](https://huggingface.co/spaces/Qwen/Qwen-Image-2.1). Yalnız tarza bakmak için, ve yalnız
     NSFW olmayan prompt'larla.
3. **Asıl entegrasyon için: Queen Editor'ün kendi defteri ve ikinci bir grafik.** Defterde yeni bir
   `PHOTO_QWEN` kutusu olur. `workflow_api.json`'ın yanına, ilk bakışta beğenilen ayarlardan export
   edilmiş ikinci bir grafik eklenir. Kare başına seçilen model hangi grafiğin kullanılacağını da
   belirler. Taslağı [Entegrasyon taslağı](#entegrasyon-taslağı) bölümünde.
4. **Boyut adayları.** Hepsi videonun oranını tam tutuyor ve 32'nin katı. Seçim ilk bakışta, gözle
   yapılır. 🧮

   | | Video (H3) | Aday 1 · ucuz | **Aday 2 · önerilen başlangıç** | Aday 3 · doğal 2K'ya yakın |
   |---|---|---|---|---|
   | Yatay 16:9 | 1024 × 576 | 1536 × 864 (×1,5) | **2048 × 1152 (×2)** | 2560 × 1440 (×2,5) |
   | Dikey 2:3 | 576 × 864 | 1024 × 1536 | **1280 × 1920** | 1664 × 2496 |

## 1. "Qwen Image 2.1" tam olarak ne?

**Bu adla bir model var, ve resmî.** Qwen ekibi (Alibaba) yayımladı. Ağırlıkları 20 Eylül 2026'da
açıldı. ✅ Kesin.

| Model | Tarih | Boyut | Metin kodlayıcı | Lisans | Kaynak |
|---|---|---|---|---|---|
| Qwen-Image | Ağustos 2025 | 20B | Qwen2.5-VL 7B | Apache-2.0 | ✅ [HF](https://huggingface.co/Qwen/Qwen-Image), [Comfy dosyaları](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI) |
| Qwen-Image-Edit-2509 / -2511 | Eylül / Aralık 2025 | (düzenleme modelleri) | — | Apache-2.0 | ✅ [HF Qwen listesi](https://huggingface.co/api/models?author=Qwen&search=Qwen-Image&limit=50&full=true) |
| Qwen-Image-2512 | Aralık 2025 | 20B | Qwen2.5-VL 7B | Apache-2.0 | ✅ [HF](https://huggingface.co/Qwen/Qwen-Image-2512) |
| Qwen-Image-2.0 (ve 2.0-Pro) | Şubat 2026 | — | — | ağırlık yok, yalnız API | 🗣️ [lilting.ch](https://lilting.ch/en/articles/qwen-image-2-pro-api-release). Qwen'in HF hesabında 2.0 deposu yok ✅ |
| **Qwen-Image-2.1** | **20 Eylül 2026** | **7B** (32 tek akışlı DiT katmanı) | **Qwen3-VL 8B** | **Qwen Research** (ticari değil) | ✅ [GitHub](https://github.com/QwenLM/Qwen-Image-2.1), [HF](https://huggingface.co/Qwen/Qwen-Image-2.1) |
| Qwen-Image-2.1-Turbo | 9 Ekim 2026 | 7B, 8 adımlık damıtılmış checkpoint | Qwen3-VL 8B | Qwen Research | ✅ [HF](https://huggingface.co/Qwen/Qwen-Image-2.1-Turbo), [GitHub haberleri](https://github.com/QwenLM/Qwen-Image-2.1) |

- **VAE:** 64 kanallı, 16 kat uzamsal sıkıştırmalı bir RGBA otokodlayıcı, yani saydamlığı doğal
  olarak üretebiliyor. ✅ [GitHub](https://github.com/QwenLM/Qwen-Image-2.1). ComfyUI'deki
  uygulaması Wan 2.2'nin VAE modülünü kullanıyor. ✅ [ComfyUI PR #16400](https://github.com/Comfy-Org/ComfyUI/pull/16400)
- **Üretim ve düzenleme tek modelde.** En fazla 10 referans resim alıyor (ComfyUI node'unda 16 yuva
  var). ✅ [docs.comfy.org](https://docs.comfy.org/tutorials/image/qwen/qwen-image-2-1)
- **"Pro" bir API adı.** GitHub sayfası: *"Qwen-Image-2.1 Pro and Turbo APIs are now officially
  live!"* ✅. Açık ağırlıklar yalnız `Qwen-Image-2.1` ve `Qwen-Image-2.1-Turbo`. Pro'nun açık 2.1'le
  aynı ağırlık olup olmadığını hiçbir kaynak söylemiyor, bu doğrulanamadı.
- **Ticari kullanım:** 2.1 ve Turbo'da yok. Lisansta *"Non-Commercial" shall mean for research or
  evaluation purposes only*, ticari lisans için de `model-business@notice.qwencloud.com` adresi
  veriliyor ✅ [LICENSE](https://huggingface.co/Qwen/Qwen-Image-2.1/blob/main/LICENSE). Comfy'nin
  sayfası da aynısını söylüyor ✅ [comfy.org](https://comfy.org/qwen-image-2.1/). Üretilen resimler
  için ayrı bir madde yok. Yasak "Materials"ı (model ve belgeleri) kullanmaya konuyor.
- **2.1 ile eski Qwen-Image aynı mimari değil.** Eskisi 20B ve Qwen2.5-VL kullanıyor, 2.1 ise 7B ve
  Qwen3-VL kullanıyor. Bu yüzden eski Qwen-Image LoRA'ları 2.1'e oturmaz. 🧮 *(Katman yapıları farklı.
  Ölçülmedi, ama bir LoRA'nın anahtarları başka bir mimarinin ağırlıklarını bulamaz.)*

## 2. ComfyUI'de yerleşik destek

- **ComfyUI'nin içinde, custom node gerekmiyor.** Destek [PR #16400](https://github.com/Comfy-Org/ComfyUI/pull/16400)
  ile geldi, 19 Eylül 2026'da birleştirildi ✅. Yeni node'lar `TextEncodeQwenImage21` ve
  `QwenImage21Cache` (`comfy_extras/nodes_qwen.py`). ✅
- **Sürüm:** Hangi sürümle geldiğini resmî bir kaynakta bulamadım. ComfyUI Wiki **0.37.0 ve üstü**
  diyor 🗣️ [comfyui-wiki](https://comfyui-wiki.com/en/news/2026-09-21-qwen-image-2-1). Bizim için
  fark etmez: defter ComfyUI'yi her koşuda `master`'dan çekiyor
  *([colab/comfy.py](../../queen-editor/colab/comfy.py), `install_comfy`: `git clone` + `git pull`)*. ✅
- **Hazır resmî şablonlar var** ✅ [docs.comfy.org](https://docs.comfy.org/tutorials/image/qwen/qwen-image-2-1),
  [workflow_templates](https://github.com/Comfy-Org/workflow_templates):
  - `image_qwen_image_2_1_t2i.json`: metinden resim, 25 adım, `cfg 1`, `euler` / `simple`
  - `image_qwen_image_2_1_turbo_t2i.json`: 8 adım, `ManualSigmas` + `SamplerCustomAdvanced`, `cfg 1`
  - `…_image_edit.json`, `…_turbo_image_edit.json`, `…_background_removal.json`

  Şablonlar ComfyUI'nin Template Library'sinde de "Qwen-Image-2.1" aranarak bulunuyor. Grafik bir
  **subgraph** içinde: `UNETLoader` → `CLIPLoader (type: qwen_image)` → `TextEncodeQwenImage21`
  (`prompt` ve `negative_prompt` girdileri var) → `EmptyLatentImage` → `KSampler` → `VAEDecode`.
  Boyutu dışarıdaki `ResolutionSelector` veriyor, varsayılanı 1 MP (1024 × 1024).
  ✅ [şablon JSON'u](https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/image_qwen_image_2_1_t2i.json)
- Şablonda bir de **prompt geliştirici** var: Qwen3.5 9B, `refine_prompt`. Varsayılanı kapalı ✅.
  Bizde prompt'u Queen AI ve QueenAgent yazdığı için bu kısım gerekmez, ve indirmesi 9,5 GB tutar.

### Dosyalar — [Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1)

Boyutlar HF API'sinin dosya listesinden okundu ✅ ([liste](https://huggingface.co/api/models/Comfy-Org/Qwen-Image-2.1/tree/main?recursive=true)).
Depodaki yollar `diffusion_models/…`, `text_encoders/…` ve böyle devam ediyor; `split_files/` yok.

| Klasör | Dosya | Boyut | Not |
|---|---|---|---|
| `diffusion_models/` | `qwen_image_2.1_int8_convrot.safetensors` | 7,26 GB | **Şablonun kullandığı** |
| `diffusion_models/` | `qwen_image_2.1_bf16.safetensors` | 14,23 GB | tam hassasiyet |
| `diffusion_models/` | `qwen_image_2.1_turbo_int8_convrot.safetensors` | 7,26 GB | Turbo şablonunun kullandığı |
| `diffusion_models/` | `qwen_image_2.1_turbo_bf16.safetensors` | 14,23 GB | |
| `text_encoders/` | `qwen3vl_8b_int8_convrot.safetensors` | 9,35 GB | **Şablonun kullandığı** |
| `text_encoders/` | `qwen3vl_8b_bf16.safetensors` / `qwen3vl_8b_w4a8.safetensors` | 17,53 / 6,31 GB | |
| `vae/` | `qwen_image_2.1_vae_bf16.safetensors` | 0,68 GB | **zorunlu** |
| `loras/` | `qwen_image_2.1_turbo_lora_avg_rank_178_bf16.safetensors` | 0,91 GB | Tam modelden çıkarılmış Turbo LoRA'sı: *"use 8 steps and cfg 1"* ✅ [README](https://huggingface.co/Comfy-Org/Qwen-Image-2.1/blob/main/README.md) |
| `text_encoders/` | `qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors` | 9,47 GB | prompt geliştirici, bizde gereksiz |
| `model_patches/` | `qwen_image_2.1_fun_controlnet_union_int8_convrot.safetensors` | 3,78 GB | ControlNet, şimdilik gereksiz |

**Bizim için asgari set:** int8 DiT + int8 metin kodlayıcı + VAE = **17,28 GB** 🧮. Turbo istenirse
bunun yanına ya Turbo DiT'i (+7,26 GB) ya da Turbo LoRA'sı (+0,91 GB) gelir.

### Başka hassasiyetler

- **fp8:** [unsloth/Qwen-Image-2.1-FP8](https://huggingface.co/unsloth/Qwen-Image-2.1-FP8) 🗣️. Ama
  fp8 A100'de yerel değil. Depo H3'te bu yüzden `int8_convrot`'u seçmişti
  *([deneme-listesi.md](../../collab-toolbox/video_experiments/deneme-listesi.md))*. Qwen'de de
  resmî int8 sürümü varken fp8'e gerek yok.
- **GGUF:** resmî bir GGUF yok. Topluluktan
  [unsloth/Qwen-Image-2.1-GGUF](https://huggingface.co/unsloth/Qwen-Image-2.1-GGUF) 🗣️: Q8_0
  7,64 GB, Q6_K 6,27 GB, Q4_K_M 4,20 GB, Q2_K 2,47 GB ✅ *([dosya listesi](https://huggingface.co/api/models/unsloth/Qwen-Image-2.1-GGUF/tree/main))*.
  GGUF için ComfyUI-GGUF gerekiyor. Bir model kartı, eski sürümlerin "Unknown model architecture!"
  hatası verdiğini ve leejet'in fork'unun kullanılmasını söylüyor 🗣️
  [abenzerps](https://huggingface.co/abenzerps/Qwen-Image-2.1-Uncensored-Quantized). A100'de buna
  gerek yok.
- **NVFP4** topluluk sürümleri var ([BennyDaBall](https://huggingface.co/BennyDaBall/Qwen-Image-2.1-NVFP4)) 🗣️.
  Yalnız Blackwell'de anlamlı, A100'de değil.
- **Nunchaku:** HF'te 20 Ekim'de en çok indirilen 60 "Qwen-Image-2.1" deposunun hiçbiri Nunchaku
  değil ✅ *([arama](https://huggingface.co/api/models?search=Qwen-Image-2.1&limit=60&sort=downloads))*.
  Var olmadığını kanıtlamaz, ama bulunamadı.

## 3. Hız ve VRAM — Colab'ın kartında

**Bizim kartlar.** Defter GPU'yu yalnızca `nvidia-smi` ile okuyor, belli bir kart istemiyor.
Assert mesajı T4'ü öneriyor *([queeneditor.ipynb](../../queen-editor/queeneditor.ipynb), hücre 1)*.
Depoda ölçülmüş iki kart var: **T4, 14,74 GiB** ve **A100, 39,56 GiB**
*([test_comfy_photo_generator.py](../../queen-editor/backend/tests/test_comfy_photo_generator.py))*.
H3 videosu A100'de koşuyor. ✅

- **A100 40 GB:** asgari set 17,3 GB. DiT (7,3 GB) ile metin kodlayıcı (9,4 GB) aynı anda bile karta
  sığar 🧮. Int8 ConvRot dosyaları bu depoda A100'de zaten çalışıyor: H3'ün DiT'i ve VAE'si de
  `int8_convrot` ✅ *([model_groups.py](../../queen-editor/backend/features/producers/domain/model_groups.py))*.
- **T4 15 GB:** DiT tek başına sığar. Metin kodlayıcıyla birlikte sığmaz, ComfyUI sırayla yükleyip
  boşaltmak zorunda kalır. T4'te bf16 donanım desteği de yok. Qwen 2.1'in T4'te çalıştığına dair bir
  kaynak bulamadım. **Denenmeden önerilmez.** ≈
- **VRAM rakamları birbirini tutmuyor**, hepsi üçüncü taraf:
  - 24 GB'lık RTX 3090'da int8 setinin çalıştığı doğrulanmış 🗣️ [alesha-pro/tools](https://github.com/alesha-pro/tools/tree/main/qwen-image-2.1)
  - bir incelemede "tam yüklü" ~27–29 GB, hassasiyeti yazılmadan 🗣️ [MindStudio](https://www.mindstudio.ai/blog/qwen-image-2-1-hands-on-review)
  - resmî sayfalarda VRAM sayısı yok. Yalnız *"Int8 … lower memory"* ve CPU offload önerisi var ✅
    [docs.comfy.org](https://docs.comfy.org/tutorials/image/qwen/qwen-image-2-1)
- **Süre.** Bulabildiğim tek düzgün ölçüm şu: RTX 3090, int8 set, **2048 × 1152, 50 adım, iş başına
  82–96 sn**. Model yükleme de bu sürenin içinde. 🗣️ [alesha-pro/tools](https://github.com/alesha-pro/tools/tree/main/qwen-image-2.1)
  A100 için bir ölçüm yok. Ölçekleyerek tahmin ≈, A100'ün 3090'dan yavaş olmadığı varsayımıyla:
  - 2048 × 1152, 25 adım (şablon): **≈ 30–45 sn**
  - 2048 × 1152, Turbo 8 adım: **≈ 10–20 sn**
  - 1536 × 864'te token sayısı 2048 × 1152'nin %56'sı 🧮, yani bunların kabaca yarısı ile üçte ikisi
    arası ≈.

  Gerçek sayıyı ilk bakış defteri gösterir.
- **Hızlandırıcılar:**
  - **Resmî Turbo** (8 adım, `cfg 1`). Kartında bir hız ya da kalite rakamı yok, yalnız *"other
    schedules have not been evaluated"* yazıyor. ✅ [HF](https://huggingface.co/Qwen/Qwen-Image-2.1-Turbo)
  - **Lightning LoRA** (4 adım): [lightx2v/Qwen-Image-2.1-Lightning](https://huggingface.co/lightx2v/Qwen-Image-2.1-Lightning),
    `pytorch_lora_weights.safetensors`, 67 MB ✅. Resmî değil, LightX2V ekibinin. 13 Ekim'de çıktı
    🗣️ [comfyui-wiki](https://comfyui-wiki.com/en/news/2026-10-13-qwen-image-2-1-lightning). Kalite
    kanıtı yalnız kartın kendi yan yana örnekleri, ve 40 adımlık taraf *"an earlier run"*den. Ölçüm
    yok, **güven düşük-orta.**
  - ComfyUI belgesi Lightning'i `LoraLoaderModelOnly` ile, 4 adım, `euler` / `simple` ile
    kullanmayı söylüyor ✅. Dosyanın adı jenerik; bizim `loras/` klasörüne yeni bir adla girmesi
    gerekir.

## 4. Boyutlar

**Resmî hazır boyutlar** ✅ [GitHub](https://github.com/QwenLM/Qwen-Image-2.1), [HF](https://huggingface.co/Qwen/Qwen-Image-2.1):
1:1 2048 × 2048 · 16:9 2752 × 1536 · 9:16 1536 × 2752 · 4:3 2400 × 1792 · 3:2 2528 × 1696 ·
2:3 1696 × 2528. Model **doğal 2K**, yani ~4 MP. ComfyUI şablonu ise 1 MP ile açılıyor, ve belge
2K'nın çok üstünde (4K) prompt'a uyumun düştüğünü yazıyor ✅ [docs.comfy.org](https://docs.comfy.org/tutorials/image/qwen/qwen-image-2-1).

**Izgara.** Latent her kenarı 16'ya bölüyor: `latent_h // 16, latent_w // 16`. Transformer'ın ek bir
yama katlaması yok, her latent noktası bir token ✅
*([nodes_qwen.py](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_qwen.py),
[qwen_image21/model.py](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/ldm/qwen_image21/model.py))*.
Yani yapısal alt sınır **16'nın katı**. Şablonun notu ise *"multiples of 32 where possible"* diyor, ve
referans resimler 32'ye yuvarlanıyor ✅. Bu yüzden 32'nin katları seçildi.

**Resmî boyutlar videonun oranını tam tutmuyor** 🧮:
- 2752 × 1536 = 1,7917, yani 16:9'dan **%0,78** farklı. Eski Qwen'in 1664 × 928'i ise %0,86 farklı.
- 1696 × 2528 = 0,6709, yani 2:3'ten **%0,63** farklı.

Depo %1'e kadar farka izin veriyor, ama 475 birebir oranı seçmişti, çünkü hiçbir şeye mal olmuyor
([475 araştırması](../arsiv/research/2026-10-20-queen-editor-m475-h3-16-9.md)).

**Tam 16:9 olan boyutlar** 🧮: boyut 16k × 9k olmalı.
- 16'nın katı olması için k'nin 16'nın katı olması gerekir: … 1280 × 720, 1536 × 864, 1792 × 1008,
  2048 × 1152, 2304 × 1296, 2560 × 1440 …
- 32'nin katı olması için k'nin 32'nin katı olması gerekir: **512 × 288, 1024 × 576, 1536 × 864,
  2048 × 1152, 2560 × 1440, 3072 × 1728**.
- 64'ün katı olması için k'nin 64'ün katı olması gerekir: yalnız 1024 × 576, 2048 × 1152, 3072 × 1728.

**Tam 2:3 olan boyutlar, 32'nin katı** 🧮: boyut 64m × 96m olmalı → 1024 × 1536, 1088 × 1632,
1152 × 1728, 1216 × 1824, **1280 × 1920**, … , 1664 × 2496, 1728 × 2592.

| Boyut | Oran | MP | Token (G/16 × Y/16) | Videoya göre | Değerlendirme |
|---|---|---|---|---|---|
| 1536 × 864 | tam 16:9 | 1,33 | 5.184 | ×1,5 | Bugünkü boyut, en ucuzu. Doğal 2K'nın üçte biri; ayrıntı kaybı olabilir ≈ |
| **2048 × 1152** | tam 16:9 | 2,36 | 9.216 | ×2 | **Başlangıç önerisi.** 64'ün de katı. Doğal 2K'nın token sayısının %56'sı. 3090 ölçümü de bu boyutta 🗣️ |
| 2560 × 1440 | tam 16:9 | 3,69 | 14.400 | ×2,5 | Doğal 2K alanına en yakın tam 16:9. 2048 × 1152'den ≈ 1,6–2,4 kat pahalı |
| 2752 × 1536 *(resmî)* | %0,78 farklı | 4,23 | 16.512 | — | Tam oran değil |
| 1024 × 1536 | tam 2:3 | 1,57 | 6.144 | ×1,78 | Bugünkü dikey boyut |
| **1280 × 1920** | tam 2:3 | 2,46 | 9.600 | ×2,22 | Dikey başlangıç önerisi, 64'ün de katı |
| 1664 × 2496 | tam 2:3 | 4,15 | 16.224 | ×2,89 | Resmî 1696 × 2528'e en yakın tam 2:3 |

Export bugün kareyi 1920 × 1080'e sığdırıyor. 2048 × 1152 ve üstü export'ta küçülür, büyümez. 🧮

## 5. Tarz ve içerik

- **Prompt dili düzyazı, etiket değil.** Metni bir LLM, Qwen3-VL 8B kodluyor ✅. Resmî örneklerin
  hepsi uzun, betimleyici cümleler. Şablonun prompt geliştiricisi de prompt'u *"tek bir betimleyici
  paragrafa"* çeviriyor ✅ [şablon](https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/image_qwen_image_2_1_t2i.json).
  Bir topluluk modelinin kartında açıkça şöyle yazıyor: *"Qwen Image 2.1 reads prose, not tag
  lists"* 🗣️ [Noct-Q README](https://huggingface.co/Noctaluna/Noct-Q-Uncensored-Qwen-Image-2.1/blob/main/README.md).
- **Bizim prompt'larımız Illustrious için yazılmış booru etiketleri.** QueenAgent'ın talimatı
  *"The image model is weak and draws every tag in the prompt"* diye başlıyor ve tüm senaryo için tek
  bir negatif liste yazdırıyor ✅
  *([queen-agent prompt.py](../../queen-agent/backend/features/workspace/domain/prompt.py))*.
  Grafikte de Illustrious'un kalite etiketleri var: `masterpiece, best quality, amazing quality,
  absurdres` *([workflow_api.json](../../queen-editor/assets/workflow_api.json), node 3)*.
  - Etiketler bir LLM'e kelime olarak yine anlam taşır. Ama kalite etiketleri, sanatçı ve karakter
    etiketleri Illustrious'taki işi görmez ≈.
  - Qwen tabanlı başka bir anime modeli için yapılmış bir incelemede *"Danbooru tags are not as
    effective as in Illustrious or Anima"* yazıyor 🗣️ [note.com, MOSS-Image](https://note.com/hirorohi03/n/n085c66f9f7fc?hl=en).
    Bu 2.1 değil, ama aynı yönü gösteriyor.
  - **Sonuç: yeniden yazmak büyük ihtimalle gerekiyor.** Ne kadar gerektiğini ilk bakışta aynı karenin
    iki prompt'u gösterir. ≈
- **Olası bir kazanç.** 479–481'in uğraştığı karakter karışmaları, CLIP'in etiketleri birbirine
  bulaştırmasından geliyor. Bir kullanıcı, Qwen kodlayıcılı bir anime modeline geçince bu tür CLIP
  yan etkilerinin büyük ölçüde kalktığını yazıyor 🗣️ [note.com, WAI-ANIMA](https://note.com/nonb0716/n/nc7644494c360?hl=en).
  Tek bir kişinin deneyimi; 2.1'de görülmedi.
- **Anime, illüstrasyon ve 3DCG tarzları.** Resmî sayfalarda anime iddiası yok. Örnekler gerçekçi
  portre, infografik, *"painterly concept art"* ve karakter sayfası ✅ [comfy.org](https://comfy.org/qwen-image-2.1/).
  ComfyUI Wiki tarzın metinle güvenilir şekilde değiştiğini söylüyor 🗣️ [comfyui-wiki](https://comfyui-wiki.com/en/news/2026-09-21-qwen-image-2-1).
  2.1 ile Illustrious'u karşılaştıran bir kaynak **bulamadım.** Anime tarzı Illustrious'un kendi
  alanı; Qwen'in onu ne kadar tuttuğu ancak denemede görülür.
- **LoRA'lar.** Ekosistem bir aylık.
  - Civitai'de **"Qwen 2.1"** adında ayrı bir taban model kategorisi var ✅
    [Civitai API](https://civitai.com/api/v1/models?baseModels=Qwen%202.1&types=LORA&limit=60&sort=Most%20Downloaded&nsfw=true).
    En çok indirilenler NSFW, gerçekçilik (Lenovo UltraReal), yüz değiştirme ve "Anime2Real".
  - **Bir anime ya da 3DCG tarz LoRA'sı bulamadım.**
  - HF'te [WarmBloodAban/Qwen-Image-2.1-LoRAs](https://huggingface.co/WarmBloodAban/Qwen-Image-2.1-LoRAs)
    var, bir anime karakter tutarlılığı LoRA'sı, düzenleme için 🗣️.
  - Tam bir ince ayar olarak "Noct Q" var, bir anime sürümüyle birlikte
    ([Civitai](https://civitai.com/models/2958896), [HF anime](https://huggingface.co/Noctaluna/Noct-Q-Anime-Uncensored-Qwen-Image-2.1)) 🗣️.
    Kartına göre bu bir *merge*. Lisansı yine Qwen Research.
- **NSFW.**
  - Resmî sayfalarda bir güvenlik filtresi ya da reddetme davranışından söz edilmiyor ✅ *(yokluğu
    okundu)*.
  - Bir ticari API sağlayıcısı kendi testinde 45 açık prompt'un 44'ünün yazıldığı gibi geldiğini, ve
    eğitim verisinin NSFW'den arındırıldığını yazıyor 🗣️ [spicyapi](https://spicyapi.ai/blog/qwen-image-2-1).
  - HF'te çok indirilen "Uncensored" sürümlerin ve NSFW LoRA'larının olması, tabanın açık içerikte
    zayıf kaldığına işaret ediyor ≈.
  - Backlog'daki *"her şeyi NSFW'ye çeviriyor"* sorunu açısından bu iyi haber olabilir: istenmeden
    NSFW'ye kayması beklenmez ≈. Öte yandan açık içerik isteyen kareler için bir LoRA ya da ince ayar
    gerekebilir. **İkisi de denemede görülür.**
- **Bilinen bir kusur.** madebyollin, damalı doku (*"checkerboard texture"*) için ayrı bir VAE
  yayımlamış ✅ [HF](https://huggingface.co/madebyollin/texture-fix-vae-for-qwen-image-2.1), ve
  ComfyUI belgesi de onu isteğe bağlı olarak listeliyor ✅. İlk bakışta bu dokuya da bakılmalı.

## 6. Nerede denenir

| Yol | Artısı | Eksisi |
|---|---|---|
| **(a) Ayrı manuel ComfyUI defteri, Colab A100** *(önerilen ilk bakış)* | Üretimin koşacağı makinenin aynısı, yani süre ve VRAM gerçek. Resmî şablon hazır geliyor. 17,3 GB açık HF dosyası, Civitai ya da cookie yok. ComfyUI arayüzünde adım, boyut, Turbo ve LoRA elle değiştirilebiliyor. NSFW de dahil her prompt denenebiliyor. H3'ün de emsali bu (madde 213). Uygulamaya dokunmuyor | Bir defter yazmak gerekiyor (H3 defteri kalıp olur). Colab kredisi harcıyor. İndirme ~10–15 dk ≈ |
| (a′) Queen Editor defterine bir deneme hücresi | Kurulu ComfyUI'yi kullanır | Üretim defterine deneme kodu girer. Uygulama Qwen'i henüz tanımadığı için ComfyUI'ye ayrı bir tünel gerekir. Depo bu ayrımı hep korudu |
| (b) Başka bir kiralık GPU'da ComfyUI (RunPod vb.) | 24–48 GB kartlar ucuz olabilir ≈ | Bizim Colab'ımızın sayılarını vermez. Yeni bir hesap ve kurulum. Bu araştırmada fiyatlara bakılmadı |
| (c) Hazır demo ya da API: [HF Space](https://huggingface.co/spaces/Qwen/Qwen-Image-2.1) (ZeroGPU, çalışıyor ✅), Alibaba Model Studio (Pro ~0,035–0,04 USD/resim ✅ [fiyat](https://www.alibabacloud.com/help/en/model-studio/qwen-image-2-1-pro)), üçüncü taraf API'ler (PiAPI Turbo 0,015 USD/resim 🗣️ [piapi](https://piapi.ai/qwen-image-2-1)) | Kurulumsuz, birkaç dakikada tarz hakkında bir fikir verir | Barındırılan servisler NSFW'yi büyük ihtimalle süzer ≈. Pro'nun açık 2.1'le aynı model olduğu doğrulanmadı. Space'in ayarları (boyut, adım, negatif) görülemedi. Süre ve VRAM hakkında bir şey söylemez |
| (d) Comfy Cloud | Şablonlar orada hazır ✅ [comfy.org](https://comfy.org/qwen-image-2.1/) | Ücretli ≈. İçerik politikası bilinmiyor. Yine bizim makinemiz değil |

**İlk bakış: (a).** İsterseniz önce (c)'nin HF Space'iyle beş dakikalık bir tarz ön bakışı.
**Asıl entegrasyon: Queen Editor defteri + ikinci grafik** (aşağıda).

İlk bakış defterinde bakılacaklar, bir öneri:
1. Gerçek bir projeden 4–6 kare, her biri bugünkü etiket prompt'uyla ve düzyazı hâliyle.
2. 1536 × 864, 2048 × 1152 ve 2560 × 1440'ta.
3. Tam model (25 adım), Turbo (8 adım) ve Lightning (4 adım).
4. Her birinin süresi, VRAM'i, yüzler, el ve damalı doku. Aynı karenin bugünkü Nova ya da DaSiWa
   çıktısıyla yan yana.

## Entegrasyon taslağı

Kod değil, yalnız şekli; spec, kod okunduktan sonra yazılır.

- **İkinci bir grafik asset'i.** Örneğin `queen-editor/assets/workflow_photo_qwen_api.json`.
  - İlk bakışta beğenilen şablondan alınır, subgraph'ı açıp düz hâle getirilir ve
    *Export (API)* ile kaydedilir ≈. Subgraph'lı bir API export'unda node id'lerinin nasıl göründüğü
    doğrulanmadı.
  - Bugünkü grafikteki gibi sabit id'li node'ları olur: Width / Height (`easy int`), POSITIVE ve
    NEGATIVE metni, Seed, Batch Size, UNETLoader ve bir LoRA yükleyicisi. Id'ler export'ta belli
    olur; `ComfyPhotoGenerator` bugün bunları dosyanın başında sabit olarak tutuyor
    *([comfy_photo_generator.py](../../queen-editor/backend/features/photo_generation/data/comfy_photo_generator.py))*.
- **Kare başına model, grafiği de seçer.**
  - Bugün `catalog.MODELS`'ın bir satırı `{"id", "label", "checkpoint"}`, ve `_graph` node 45'e
    `ckpt_name` yazıyor *([catalog.py](../../queen-editor/backend/features/photo_generation/domain/catalog.py))*.
  - Qwen satırı bunun yerine kendi grafiğini ve dosyalarını adlandırmalı. Grafiği ya üretici seçer
    ya da ayrı bir üretici sınıfı olur; hangisi olacağı spec'in kararı.
  - Ayrıca bugünkü `SIZES`, `WEIGHT_BYTES` (SDXL'in 2,6B'si) ve `PICTURE_BYTES` SDXL'e göre
    hesaplanmış. Qwen için kendi sayıları gerekir.
- **Kurulum.**
  - `model_groups.GROUPS["photo"]` bugün `checkpoints/*.safetensors` soruyor. Qwen'in dosyaları ise
    `diffusion_models/`, `text_encoders/` ve `vae/` altında.
  - Defterde bir `PHOTO_QWEN` kutusu ve `HF_PHOTO`'ya üç satır eklenir (Comfy-Org deposu, 17,3 GB).
    `QE_PHOTO_MODELS`'e de `qwen…` id'si girer.
  - H3'ün metin kodlayıcısı Qwen3-VL **32B**, Qwen Image'ınki **8B**. Paylaşılmazlar.
- **LoRA.**
  - USNR ve Slime SDXL LoRA'ları, Qwen'e yüklenmez.
  - Bugün LoRA kutusu her modelde aynı listeyi gösteriyor (madde 238). Liste modelin ailesine göre
    ayrılmalı: Qwen için "Boş", ve ileride Qwen 2.1 tarz LoRA'ları ya da Lightning.
  - Yükleyici olarak `LoraLoaderModelOnly` belgede yazıyor ✅. rgthree'nin Power Lora Loader'ı
    Qwen'de denenmedi.
- **Negatif prompt.**
  - Qwen 2.1 `cfg 1` ile koşuyor, ve **`cfg 1`'de negatif hiç uygulanmıyor** ✅ (*"negative_prompt:
    unused while cfg is 1"*, şablon notu).
  - `cfg 2` *"over-sharpened edges"*, `cfg 5` *"degrades quality badly"* ✅ [docs.comfy.org](https://docs.comfy.org/tutorials/image/qwen/qwen-image-2-1).
    `cfg > 1` her adımı iki kez çalıştırır, yani süre ~2 katına çıkar 🧮.
  - Diffusers'taki karşılığı `true_cfg_scale`; Lightning'in kartında 1.0 ✅.
  - Bizim senaryo başına negatif listemiz Qwen'de büyük ihtimalle düşer. QueenAgent'ın *"write the
    opposite tags instead"* yolu (olumlu yazmak) zaten var.
- **Yüz düzelticisi.**
  - Bugünkü grafikte FaceDetailer (node 31) SDXL'in modeli ve CLIP'iyle yeniden örnekliyor, ve
    Save Image ondan okuyor.
  - Impact Pack'in FaceDetailer'ının Qwen 2.1'in modeli ve koşullamasıyla çalıştığına dair bir kaynak
    bulamadım.
  - 2K'da yüzler büyük çıkacağından Qwen grafiği **detailer'sız başlamalı** ≈. Gerekip gerekmediğini
    ilk bakış gösterir.
- **Fotoğraf ile video aynı ComfyUI'de.**
  - Qwen ve H3 aynı karta sırayla yüklenir. Model değişimi her geçişte bir yükleme süresi demek ≈.
  - Diske de ek olarak 17,3 GB gelir; video 37 GiB, fotoğraf bugün iki modelle ~16 GiB
    *([queeneditor.ipynb](../../queen-editor/queeneditor.ipynb), `PHOTO_GIB`)*.

## Açık sorular

1. **Lisans.** Qwen-Image-2.1 ticari kullanıma kapalı. Hangisi?
   1. 2.1 ile denemeye devam, ticari kullanım için Qwen'den lisans istenir (`model-business@notice.qwencloud.com`).
   2. Apache-2.0 olan **Qwen-Image-2512** denenir. 20B, fp8'i 20,4 GB + metin kodlayıcı 9,4 GB ✅
      [dosyalar](https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI), negatifle `true_cfg_scale 4`
      ✅ [HF](https://huggingface.co/Qwen/Qwen-Image-2512). A100'de sığar 🧮, ama daha yavaş ≈.
      Tam 16:9 boyutu 1792 × 1008 (16'nın katı) 🧮.
   3. Kanallar bu açıdan ticari sayılmıyor.

   **Öneri: 1 ya da 2.** Karar sizin, hukuki bir değerlendirme değil.
2. **İlk bakış nerede?** **Öneri: ayrı manuel defter, Colab A100.** HF Space ön bakışı da istenir mi?
3. **Açık içerik.** Qwen'in çizdiği kareler açık içerik de içerecek mi? İçerecekse taban model yetmeyebilir,
   ve bir NSFW LoRA'sı ya da Noct Q gibi bir ince ayar denenir (o da Qwen Research lisanslı).
4. **Prompt'lar.** Qwen kareleri için QueenAgent ayrı, düzyazı bir prompt mu yazacak, yoksa etiketler
   olduğu gibi mi gidecek? İlk bakıştaki ikili deneme bunu gösterir; **öneri: denemeden sonra karar.**
5. **Hangi model, hangi hız.** Tam model (25 adım), Turbo (8) ya da Lightning (4). **Öneri: Turbo'yla
   başlamak**, resmî ve tek dosya. Kalite yetmezse tam model.
6. **Boyut.** **Öneri: 2048 × 1152 / 1280 × 1920 ile başlamak**, 1536 × 864 ve 2560 × 1440 ile
   karşılaştırarak.
7. **Kart.** Qwen fotoğrafları yalnız A100'de mi üretilecek? T4 doğrulanmadı.

## Doğrulanamayanlar

- Qwen 2.1'in A100'de süresi ve tepe VRAM'i. Hiçbir kaynak vermiyor; tek ölçüm RTX 3090'dan, üçüncü
  taraf.
- ComfyUI'nin desteği hangi sürümle getirdiği. 0.37.0 yalnız ComfyUI Wiki'de geçiyor.
- "Pro" API'sinin açık 2.1 ağırlıklarıyla aynı olup olmadığı.
- HF Space'in ayarları ve içerik süzgeci.
- Taban modelin NSFW davranışı (yalnız bir ticari sağlayıcının testi var) ve eğitim verisinin süzülüp
  süzülmediği.
- Anime, illüstrasyon ve 3DCG'de Illustrious'la doğrudan bir karşılaştırma. Bulunamadı.
- Lightning LoRA'sının kalitesi. Yalnız kartın kendi örnekleri var.
- Qwen 2.1'in T4'te çalışması; FaceDetailer'ın ve Power Lora Loader'ın Qwen 2.1'le çalışması.
- Nunchaku sürümü: bulunamadı.
