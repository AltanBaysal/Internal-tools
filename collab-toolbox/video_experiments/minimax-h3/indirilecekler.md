# MiniMax H3 (DaSiWa cMMH3 V19) — Colab'da indirilecekler (`workflow.json`'dan çıkarıldı)

Etiketler: **✅** HF dosya listesinden doğrulandı · **📌** `workflow.json`'daki Note node'unda yazar
verdi · **📚** kanonik repo · **⚠️** teyit edilmedi.

> Adreslerin tamamı grafiğin **"Note: Model Links"** ve **"Model links Extra"** node'larından geliyor
> 📌; boyutlar HuggingFace dosya listesinden okundu ✅.

## 1) Custom node'lar (6 + Manager)

| # | Paket | git URL | Kaynak |
|---|---|---|---|
| 1 | ComfyUI-Manager | https://github.com/ltdrdata/ComfyUI-Manager | 📚 |
| 2 | rgthree-comfy | https://github.com/rgthree/rgthree-comfy | 📌 |
| 3 | ComfyUI-KJNodes | https://github.com/kijai/ComfyUI-KJNodes | 📌 |
| 4 | ComfyUI-GGUF | https://github.com/city96/ComfyUI-GGUF | 📌 |
| 5 | ComfyUI-DaSiWa-Nodes | https://github.com/darksidewalker/ComfyUI-DaSiWa-Nodes | 📌 |
| 6 | Comfyui-MMH3-UltimateUpscale | https://github.com/bbaudio-2025/Comfyui-MMH3-UltimateUpscale | 📌 |

`ffmpeg` apt'den. `MiniMaxH3*` node'ları bu listede yok — güncel ComfyUI'nin kendi H3 desteğinden
gelmesi bekleniyor; eksik çıkarsa Manager kapatır (bkz. `instructions.md`).

## 2) Modeller — ilk koşu (I2VA), hepsi HuggingFace, gated değil

Grafiğin "Settings" tablosunun seçtiği dosyalar. **Toplam ≈ 41,8 GB.**

| Hedef klasör | Dosya | Boyut | Kaynak |
|---|---|---|---|
| `diffusion_models` | `minimax_h3_fl2va_pruned_int8_convrot.safetensors` | **21 GB** ✅ | `Comfy-Org/MiniMax-H3/diffusion_models/` |
| `text_encoders` | `qwen3vl_32b_minimax_h3_int4_convrot.safetensors` | **15 GB** ✅ | `Abiray/MiniMax-H3-GGUF/text_encoders/` |
| `vae` | `minimax_h3_video_vae_fp16.safetensors` | **5,21 GB** ✅ | `Comfy-Org/MiniMax-H3/vae/` |
| `vae` | `minimax_h3_audio_vae_fp32.safetensors` | **605 MB** ✅ | `Comfy-Org/MiniMax-H3/vae/` |
| `vae_approx` | `taeh3.safetensors` | küçük ⚠️ | `Kijai/MiniMax-H3-TAE/vae_approx/` |

**FL2VA UNET'i T2VA, I2VA, FL2VA ve L2VA modlarının dördünü birden koşturuyor** — ayrı UNET yalnız
REF2VA istiyor. İlk deneme I2VA olduğu için bu tek dosya yetiyor.

Metin kodlayıcı **Qwen3-VL 32B**. Dosyanın üç sürümü var ve seçim donanıma bağlı:

| Dosya | Boyut | Colab A100'de |
|---|---|---|
| `qwen3vl_32b_minimax_h3_int4_convrot` (Abiray) | 15 GB ✅ | **bu** — grafiğin varsayılanı |
| `qwen3vl_32b_minimax_h3_int8_convrot` (Comfy-Org) | 27,1 GB ✅ | çalışır, 12 GB daha büyük |
| `qwen3vl_32b_minimax_h3_nvfp4_awq` | 15,7 GB ✅ | **hayır** — fp4 yalnız Blackwell'de yerel |

UNET tarafında da aynı ayrım: `pruned_bf16` 40,2 GB, `pruned_fp8_scaled` 21 GB *(fp8 A100'de yerel
değil)*, `int8_convrot` 21 GB. Kırpılmamış `bf16` 66,3 GB — Colab diskini tek başına tüketir.

## 3) İkinci koşuya bırakılanlar

| Ne | Nereden | Boyut | Neden şimdi değil |
|---|---|---|---|
| `minimax_h3_ref2va_pruned_int8_convrot.safetensors` | `Comfy-Org/MiniMax-H3/diffusion_models/` | 21 GB ✅ | yalnız REF2VA modu için |
| `dasiwa_minimax_h3_ref2va_v2_..._turbo_...safetensors` | Civitai model **2877206**, login-gated | ⚠️ | yazarın kendi turbo finetune'u; REF2VA tabanlı, 4–8 adım. Cookie ister *(NOTEBOOK-STANDARD §4)* |
| `2x-AnimeSharpV4_RCAN.safetensors` | `Kim2091/2x-AnimeSharpV4` | ⚠️ | "Upscale /w Model" anahtarı kapalı geliyor |
| `minimax_h3_latent_upscaler_3d_bf16.safetensors` | `LBH-123-AI/Minimax_h3_latent_Upscaler` | ⚠️ | "Latent Upscale" anahtarı kapalı geliyor |
| `minimax_h3_video_vae_int8_convrot.safetensors` | `Kijai/MiniMax-H3-experimental` | ⚠️ | fp16 VAE'nin alternatifi; ikisinden biri yeter |

## 4) Otomatik (manuel indirme yok)

| Dosya | Not |
|---|---|
| `rife_v4.26.safetensors` | Frame interpolation — anahtar kapalı; açılırsa loader ilk kullanımda kendi indirir *(`Comfy-Org/frame_interpolation`)* |

## 5) Klasör düzeni (grafiğin kendi notundan)

```
ComfyUI/models/
├── diffusion_models/   minimax_h3_fl2va_pruned_int8_convrot.safetensors
├── text_encoders/      qwen3vl_32b_minimax_h3_int4_convrot.safetensors
├── vae/                minimax_h3_video_vae_fp16.safetensors
│                       minimax_h3_audio_vae_fp32.safetensors
├── vae_approx/         taeh3.safetensors
├── upscale_models/     (opsiyonel)
└── latent_upscale_models/ (opsiyonel)
```

## 6) Doğrulama

Grafikteki loader node'ları: `UNETLoader` ×2, `CLIPLoader`, `VAELoader` ×2, `UpscaleModelLoader`,
`FrameInterpolationModelLoader`, `MMH3LatentUpscaleWithModelParams` → yukarıdaki listeyle eşleşti.
`LoraLoader` / `Power Lora Loader` **yok**: bu grafik LoRA yüklemiyor, hız kazancı checkpoint'in
kendisinden geliyor.

**Açık kalan:** `taeh3.safetensors` boyutu (HF 429 verdi; defter indirirken gerçek boyutu basar) ve
`MiniMaxH3*` node'larının hangi paketten geldiği.
