# MiniMax H3 (DaSiWa cMMH3 V19) — indirilecekler

`workflow.json` taranarak çıkarıldı: loader node'larının **seçili** değerleri, grafiğin kendi Note
node'larındaki adresler, ve node'ların açık/bypass durumu (`mode: 0` açık, `mode: 4` bypass).

**Kaynak etiketi — her satır bu üçünden biri:**

| | Anlamı |
|---|---|
| 📌 | Adresi **workflow'un kendi notu** veriyor |
| 🔁 | Workflow adres vermiyor; **depodaki başka bir denemede** aynı dosya kullanılıyor, adres oradan |
| 🔒 | Workflow adres vermiyor; Civitai'de ve **login-gated** — sürümü kullanıcı gösterdi, § 6 |
| ❌ | Adres yok, emsal yok, bulunamadı — *şu an böyle bir satır yok* |

Boyutlar ✅ ile işaretliyse HuggingFace / Civitai dosya listesinden okundu.

---

## 1) Custom node'lar

İlk beşi ve ffmpeg grafiğin **"📋 Features & Requirements"** notundan, adresleriyle 📌. Manager o
listede yok: onu biz ekliyoruz, deponun öteki deneme defterlerinde olduğu gibi 🔁.

| Paket | git URL | |
|---|---|---|
| rgthree-comfy | https://github.com/rgthree/rgthree-comfy | 📌 |
| ComfyUI-KJNodes | https://github.com/kijai/ComfyUI-KJNodes | 📌 |
| ComfyUI-GGUF | https://github.com/city96/ComfyUI-GGUF | 📌 |
| ComfyUI-DaSiWa-Nodes | https://github.com/darksidewalker/ComfyUI-DaSiWa-Nodes | 📌 |
| Comfyui-MMH3-UltimateUpscale | https://github.com/bbaudio-2025/Comfyui-MMH3-UltimateUpscale | 📌 |
| ffmpeg | apt (`apt-get install ffmpeg`) | 📌 |
| ComfyUI-Manager | https://github.com/ltdrdata/ComfyUI-Manager | 🔁 |

`MiniMaxH3Director`, `MiniMaxH3Cache`, `MiniMaxH3SigmaShift`, `MiniMaxChunkFeedForward`,
`MiniMaxH3DirectorGuide` node'ları grafiğin saydığı beşinin hiçbirinde adı geçmiyor. Grafiğin Quick Start notu
*"routes to the **native** H3 backend automatically"* diyor — yani güncel ComfyUI'nin kendinden
gelmesi bekleniyor. **Doğrulandı** *(14 Eylül)*: grafik yüklendiğinde tek bir "missing node" uyarısı
çıkmadı. H3 desteği ComfyUI çekirdeğinde — model 3 Ağustos 2026'da açıldığında aynı gün girmiş.

---

## 2) Grafiğin **şu an seçtiği** dosyalar

Bunlar `workflow.json`'u açtığında ComfyUI'nin arayacağı dosyalar (Settings alt-grafiğinin canlı
değerleri, satır 1135–1140). Not'lardaki listeyle **aynı değil** — yazar kendi checkpoint'ini seçili
bırakmış.

| Klasör | Dosya | Boyut | Kaynak |
|---|---|---|---|
| `diffusion_models/MiniMaxH3/` | `dasiwa_minimax_h3_ref2va_v2_pruned_hybrid_turbo_int8_row-wise_convrot_runtime_mixed.safetensors` | 20.967.669.168 B ✅ | 🔒 Civitai sürüm **3314686** — § 6 |
| `text_encoders/` | `qwen3vl_32b_minimax_h3_int4_convrot.safetensors` | 14.952.506.709 B ✅ | 📌 https://huggingface.co/Abiray/MiniMax-H3-GGUF/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_int4_convrot.safetensors |
| `vae/MiniMaxH3/` | `minimax_h3_video_vae_int8_convrot.safetensors` | 3.171.670.912 B ✅ | 📌 https://huggingface.co/Kijai/MiniMax-H3-experimental/resolve/main/minimax_h3_video_vae_int8_convrot.safetensors |
| `vae/MiniMaxH3/` | `minimax_h3_audio_vae_fp32.safetensors` | 605 MB ✅ | 📌 https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors |
| `vae_approx/` | `taeh3.safetensors` | 9.791.388 B ✅ | 📌 https://huggingface.co/Kijai/MiniMax-H3-TAE/resolve/main/vae_approx/taeh3.safetensors |

**`MiniMaxH3/` bir alt klasör.** Grafik dosyayı `diffusion_models/MiniMaxH3/...` ve
`vae/MiniMaxH3/...` altında arıyor; metin kodlayıcı ile `taeh3` alt klasörsüz, kök klasörde.

`taeh3`, `ModelPreviewOverrideKJ` node'unda ve **açık** (`mode: 0`) — üretim sırasındaki hızlı
önizleme onunla çiziliyor. 9,8 MB.

**Toplam ≈ 39,7 GB.**

---

## 3) Açık (gated olmayan) karşılıkları

DaSiWa'nın Civitai checkpoint'i olmadan da koşar: alt-grafiğin **tanım varsayılanları** bunlar, yani
yazar seçimini üstlerine yazmadan önce orada duran dosyalar. UI'da Settings panelinden seçilir.

| Klasör | Dosya | Boyut | Kaynak |
|---|---|---|---|
| `diffusion_models/MiniMaxH3/` | `minimax_h3_fl2va_pruned_int8_convrot.safetensors` | 21 GB ✅ | 📌 https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors |
| `diffusion_models/MiniMaxH3/` | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` | 21 GB ✅ | 📌 aynı klasör, `.../minimax_h3_ref2va_pruned_int8_convrot.safetensors` |
| `vae/MiniMaxH3/` | `minimax_h3_video_vae_fp16.safetensors` | 5,21 GB ✅ | 📌 https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_fp16.safetensors |

`fl2va` **T2VA, I2VA, FL2VA ve L2VA modlarının dördünü birden** koşturuyor; ayrı `ref2va` yalnız
REF2VA için. Yani açık yoldan ilk deneme için tek UNET yetiyor: **21 GB**.

**Ama adım sayısı değişir.** Dosya şu an turbo ayarlarıyla geliyor — `euler`, **8 adım**, shift
video 6 / audio 3 — ve o ayarlar DaSiWa'nın turbo checkpoint'ine ait. Açık `fl2va` turbo değil:
grafiğin kendi tablosu onun için `res_multistep`, **25 adım**, shift video 10–12 / audio 3–5 diyor.

### Metin kodlayıcının üç sürümü

Hepsi aynı ağırlık, farklı niceleme. Seçim donanıma bağlı:

| Dosya | Boyut | Nerede |
|---|---|---|
| `qwen3vl_32b_minimax_h3_int4_convrot` | 14.952.506.709 B ✅ | Abiray — **grafiğin seçtiği** |
| `qwen3vl_32b_minimax_h3_int8_convrot` | 27,1 GB ✅ | Comfy-Org |
| `qwen3vl_32b_minimax_h3_nvfp4_awq` | 15,7 GB ✅ | Comfy-Org 📌 — *fp4 yalnız Blackwell'de yerel* |

Aynı ayrım UNET'te de var: `pruned_fp8_scaled` 21 GB ama fp8 Ada/Hopper'da yerel;
`pruned_bf16` 40,2 GB; niceleme yapılmamış `bf16` 66,3 GB.

---

## 4) Bypass'lı — grafikte kapalı geliyor, inmese de koşar

Beşinin de node'u `mode: 4`.

| Klasör | Dosya | Boyut | Kaynak |
|---|---|---|---|
| `upscale_models/` | `2x-AnimeSharpV4_RCAN.safetensors` | 31.053.198 B ✅ | 🔁 workflow yalnız *"Upscale model → openmodeldb.info (optional)"* diyor, dosyayı adlandırmıyor. Aynı dosya [wan22-dasiwa/indirilecekler.md](../wan22-dasiwa/indirilecekler.md)'de `Kim2091/2x-AnimeSharpV4` olarak duruyor; repo doğrulandı: https://huggingface.co/Kim2091/2x-AnimeSharpV4/resolve/main/2x-AnimeSharpV4_RCAN.safetensors |
| `latent_upscale_models/` | `minimax_h3_latent_upscaler_3d_bf16.safetensors` | 690.592.992 B ✅ | 📌 https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler/resolve/main/minimax_h3_latent_upscaler_3d_bf16.safetensors |
| `frame_interpolation/` | `rife_v4.26.safetensors` | — | 🔁 workflow klasörü veriyor *(`Comfy-Org/frame_interpolation`, "optional")*, dosyayı değil. wan22-dasiwa'da not düşülmüş: **loader ilk kullanımda kendi indiriyor**, elle indirme yok |

Watermark açık gelmiyor ve resmi `#Watermark-Darksidewalker-Emblem.png` — yazarın kendi amblemi,
grafikte adres yok. Gerekmiyor.

---

## 5) Klasör düzeni

```
ComfyUI/models/
├── diffusion_models/
│   └── MiniMaxH3/      <- alt klasör: grafik dosyayı burada arıyor
│       └── *.safetensors
├── text_encoders/      qwen3vl_32b_minimax_h3_int4_convrot.safetensors
├── vae/
│   └── MiniMaxH3/      <- burada da alt klasör
│       ├── minimax_h3_video_vae_int8_convrot.safetensors
│       └── minimax_h3_audio_vae_fp32.safetensors
├── vae_approx/         taeh3.safetensors
├── upscale_models/         (bypass)
├── latent_upscale_models/  (bypass)
└── frame_interpolation/    (bypass, kendi iniyor)
```

---

## 6) 🔒 DaSiWa'nın kendi checkpoint'i — hangi sürüm, hangi dosya

Grafiğin **iki UNET yuvasında da** seçili olan dosya:

```
MiniMaxH3/dasiwa_minimax_h3_ref2va_v2_pruned_hybrid_turbo_int8_row-wise_convrot_runtime_mixed.safetensors
```

`workflow.json` bu dosya için **hiçbir adres vermiyor** ve depoda emsali yok. Civitai'de model
`2877206` altında, beş sürümle:

| Sürüm | ID | Dosyaları |
|---|---|---|
| DaSiWa Hybrid v2 | 3314675 | int8 ~21 GB · w4a8 ~12,5 GB |
| **DaSiWa Hybrid Turbo v2** | **3314686** | **int8 20.967.669.168 B ✅ *(primary — aranan)*** · int4 ~12,5 GB |
| DaSiWa Hybrid v1 | 3251526 | ~21 GB · ~12,5 GB |
| DaSiWa Hybrid 8Turbo v1 | 3275408 | ~21 GB · ~12,5 GB |
| DaSiWa Hybrid 4Turbo v1 | 3272675 | ~21 GB *(tek dosya)* |

**Sürümü ayıran şey adın içindeki `turbo`.** Civitai indirilen dosyayı sürümün adına göre yeniden
adlandırıyor, ve bu 3314675'in sayfasında görüldü: orada int8'in karşılığı
`..._pruned_hybrid_int8_row-wise_convrot_runtime_mixed`, int4'ünki `..._pruned_hybrid_w4a8` — ikisinde
de `turbo` **yok**. Grafiğin istediği adda `turbo` **var**, o da yalnız *Hybrid Turbo v2*'de.

`int8` / `int4` bundan **ayrı bir eksen**: dosyanın nicelemesi ve boyutu, turbo olup olmamasıyla
ilgisi yok. Aranan, turbo sürümün **int8**'i.

Sürümün açıklaması da uyuyor: *"Hybrid (REF2VA + FL2VA compatible) … distillation blend optimized
for 4-8 steps"* — grafiğin `euler` + **8 adım** ayarıyla birebir. Yazarın aynı dosyayı hem T2V+I2V
hem R2V yuvasına koyabilmesinin sebebi de bu: tek checkpoint ikisiyle de uyumlu.

**İndirme login-gated.** Cookie kuralları ve tuzakları
[NOTEBOOK-STANDARD.md § 4](../../NOTEBOOK-STANDARD.md)'te — özetle: host **`civitai.red`** *(`.com`
değil, cookie orada same-origin)*, cookie adı **`__Secure-civ-token`**, `?token=` API anahtarı
**kullanılmaz** *(gated dosya 401 döner)*, ve ağır indirmeden önce ilk 1 KB'lık probe. Adres:

```
https://civitai.red/api/download/models/3314686
```

Bu, sürümün **primary** dosyasını indirir — yani istenen int8'i. Dosya `diffusion_models/MiniMaxH3/`
altına, grafiğin aradığı adla konur.

**Bu dosya olmadan da deneme yapılabilir:** § 3'teki açık `fl2va` ile, 25 adımda.
