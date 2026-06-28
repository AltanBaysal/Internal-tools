# DaSiWa (FastFidelity C-AiO) — Colab'da indirilecekler (workflow.json'dan çıkarıldı)

Etiketler: **✅** API'den doğrulandı · **📌** workflow.json'a gömülü (yazar verdi) · **📚** kanonik repo (yaygın, ping'lenmedi) · **❌** bulunamadı → kullanıcı verecek.

> Node URL'lerinin çoğu workflow içindeki Note node'unda yazar tarafından verilmiş 📌. Checkpoint'ler gated Civitai (version ID Civitai API ile çözüldü ✅).

## 1) Custom node'lar (8)

| # | Paket | git URL | Kaynak |
|---|---|---|---|
| 1 | ComfyUI-Manager | https://github.com/ltdrdata/ComfyUI-Manager | 📚 |
| 2 | ComfyUI-VideoHelperSuite | https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite | 📌 |
| 3 | rgthree-comfy | https://github.com/rgthree/rgthree-comfy | 📌 |
| 4 | comfyui-WhiteRabbit | https://github.com/Artificial-Sweetener/comfyui-WhiteRabbit | 📌 |
| 5 | ComfyUI-KJNodes | https://github.com/kijai/ComfyUI-KJNodes | 📌 |
| 6 | ComfyUI-GGUF | https://github.com/city96/ComfyUI-GGUF | 📌 |
| 7 | ComfyUI-DaSiWa-Nodes | https://github.com/darksidewalker/ComfyUI-DaSiWa-Nodes | 📌 |
| 8 | ComfyUI-LTXVideo | https://github.com/Lightricks/ComfyUI-LTXVideo | 📌 |

> `SageAttention` (thu-ml/SageAttention) opsiyonel — custom node değil, pip paketi (`pip install sageattention`).

## 2) Modeller — gated Civitai (version ID doğrulandı ✅, model 1981116)

| Hedef | Workflow placeholder | Version ID | İnen dosya | Durum |
|---|---|---|---|---|
| diffusion_models | DaSiWa_..._SnatchKiss_v11_HIGH_fp8_mixed.safetensors | **2953474** | DasiwaWAN22I2V14BLightspeed_snatchkissHighV11.safetensors | ✅ (UI'da seç) |
| diffusion_models | DaSiWa_..._SnatchKiss_v11_LOW_fp8_mixed.safetensors | **2953485** | DasiwaWAN22I2V14BLightspeed_snatchkissLowV11.safetensors | ✅ (UI'da seç) |

> **Config dosyası:** Bu version'da **ayrı config dosyası YOK** — version 2953474'te 2 Model varyantı var (full + pruned fp8). `api/download/models/2953474` primary'yi indirir. (Önceki "config indir" uyarısı bu checkpoint için geçerli değil.)

## 3) Modeller — HF

| Hedef | Dosya | Kaynak | Durum |
|---|---|---|---|
| vae | wan_2.1_vae.safetensors | Comfy-Org/Wan_2.2_ComfyUI_Repackaged | 📚 |
| text_encoders | umt5_xxl_fp8_e4m3fn_scaled.safetensors | Comfy-Org/Wan_2.2_ComfyUI_Repackaged | 📚 |
| upscale_models | 2x-AnimeSharpV4_RCAN.safetensors | `Kim2091/2x-AnimeSharpV4` | ⚠️ repo ✅ bulundu, tam dosya adı build'de teyit edilecek |

## 4) Kişisel/opsiyonel LoRA'lar

Base + hız checkpoint'leriyle çalışır; ekstra concept LoRA'yı kullanıcı kendi koleksiyonundan ekler.

## 5) Otomatik (manuel indirme yok)

| Dosya | Not |
|---|---|
| rife49.pt / rife_v4.26.safetensors | Frame interpolation — FrameInterpolationModelLoader / WhiteRabbit ilk kullanımda iner (Comfy-Org/frame_interpolation) |

## 6) Doğrulama (tam tarama)

Loader node'ları: `UNETLoader`, `UnetLoaderGGUF`, `CLIPLoader`, `VAELoader`, `UpscaleModelLoader`, `FrameInterpolationModelLoader`, `Power Lora Loader (rgthree)`, `LoadImage` → hepsi listeyle eşleşti.

**wav2vec teyidi:** `wav2vec2_large_english_fp16` workflow.json'da **yalnızca Note metninde** geçiyor (grep: tek eşleşme, loader yok) → C-AiO'da **yüklenmiyor, gerekmez** (S2V ayrı model 2151205). `clip_vision` referansı var (start/end image), loader yok → opsiyonel. `controlnet/ipadapter/onnx/embeddings` → yok.

**Açık kalan:** AnimeSharp upscaler tam dosya adı (repo bulundu, dosya build'de teyit) — ikincil/upscale, üretimi engellemez.
