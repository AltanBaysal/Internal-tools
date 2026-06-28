# LTX Eros — Colab'da indirilecekler (workflow.json'dan çıkarıldı)

`workflow.json` baştan sona tarandı (node `cnr_id`/`aux_id` + tüm model loader yolları). ✅ = URL kesin, ⚠️ = doğrulanmalı (cnr_id'yi ComfyUI-Manager birebir çözer → UI'da "Install Missing Custom Nodes" yedek).

## 1) Custom node'lar (16)

| # | cnr_id / aux_id | git URL | Durum |
|---|---|---|---|
| 1 | ComfyUI-Manager | https://github.com/ltdrdata/ComfyUI-Manager | ✅ |
| 2 | comfyui-kjnodes | https://github.com/kijai/ComfyUI-KJNodes | ✅ |
| 3 | rgthree-comfy | https://github.com/rgthree/rgthree-comfy | ✅ |
| 4 | comfyui-easy-use | https://github.com/yolain/ComfyUI-Easy-Use | ✅ |
| 5 | comfyui-mxtoolkit | https://github.com/Smirnov75/ComfyUI-mxToolkit | ✅ |
| 6 | comfyui-videohelpersuite | https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite | ✅ |
| 7 | ComfyUI-LTXVideo | https://github.com/Lightricks/ComfyUI-LTXVideo | ✅ |
| 8 | comfyui-impact-pack | https://github.com/ltdrdata/ComfyUI-Impact-Pack | ✅ |
| 9 | ComfyUI-VFI (GACLove/ComfyUI-VFI) | https://github.com/GACLove/ComfyUI-VFI | ✅ |
| 10 | RES4LYF | https://github.com/ClownsharkBatwing/RES4LYF | ✅ |
| 11 | comfyui-custom-scripts | https://github.com/pythongosssss/ComfyUI-Custom-Scripts | ✅ |
| 12 | ComfyLiterals | https://github.com/M1kep/ComfyLiterals | ✅ |
| 13 | comfyui_memory_cleanup | https://github.com/LAOGOU-666/Comfyui-Memory_Cleanup | ✅ (registry) |
| 14 | controlaltai-nodes | https://github.com/gseth/ControlAltAI-Nodes | ✅ (registry) |
| 15 | comfyui-int-and-float (danTheMonk/comfyui-int-and-float) | https://github.com/danTheMonk/comfyui-int-and-float | ✅ (GitHub) |
| 16 | comfyui_nvidia_rtx_nodes | https://github.com/Comfy-Org/Nvidia_RTX_Nodes_ComfyUI | ✅ (registry, resmi) |

> **16 URL'in hepsi doğrulandı** (ComfyUI registry API / GitHub). Notebook'taki ilk hali **10 node** içeriyordu; eksik 6'sı: RES4LYF, comfyui-custom-scripts, ComfyLiterals, comfyui-int-and-float, comfyui_nvidia_rtx_nodes (+ memory_cleanup vardı).
>
> **İki URL'im yanlıştı, düzeltildi:** `comfyui_memory_cleanup` (SeniorPikachu ❌ → LAOGOU-666 ✅), `controlaltai-nodes` (gabe-init ❌ → gseth ✅).

## 2) Modeller — gerekli (URL'ler workflow "Model Links" node'undan)

| Hedef klasör | Dosya | Kaynak | Durum |
|---|---|---|---|
| diffusion_models | ltx2310eros_v1_FP8.safetensors | **Civitai 2892069** (gated, cookie) | ✅ |
| diffusion_models | ltx-2.3-22b-distilled_transformer_only_fp8_input_scaled_v3.safetensors | HF Kijai/LTX2.3_comfy | ✅ |
| text_encoders | gemma_3_12B_it_fp8_e4m3fn.safetensors | HF GitMylo/LTX-2-comfy_gemma_fp8_e4m3fn | ✅ |
| clip | ltx-2.3_text_projection_bf16.safetensors | HF Kijai/LTX2.3_comfy | ✅ |
| vae | LTX23_video_vae_bf16.safetensors | HF Kijai/LTX2.3_comfy | ✅ |
| vae | LTX23_audio_vae_bf16.safetensors | HF Kijai/LTX2.3_comfy | ✅ |
| vae | taeltx2_3.safetensors | GitHub madebyollin/taehv | ✅ |
| latent_upscale_models | ltx-2.3-spatial-upscaler-x2-1.1.safetensors | HF Lightricks/LTX-2.3 | ✅ (loader'da x2-1.0 yazıyor, link x2-1.1 — UI'da seç) |
| upscale_models | nmkdSiaxCX_200k.safetensors | **Civitai 164677** (gated, cookie) | ✅ |
| loras | ltx-2.3-22b-distilled-lora-1.1_fro90_ceil72_condsafe.safetensors | HF TenStrip | ✅ (First pass) |
| loras | ltx-2.3-22b-distilled-lora-384-1.1.safetensors | HF Lightricks/LTX-2.3 | ✅ (Final pass) |

## 3) Concept LoRA'lar — Civitai (gated, version ID doğrulandı)

Workflow Power Lora Loader'larındaki concept LoRA'lar. Model Links node'unda yoktu; kullanıcının verdiği Civitai linklerinden **public API ile version ID + dosya adı doğrulandı** → notebook gated indirir (cookie).

| Dosya (workflow) | Civitai model | Version ID | İnen dosya | Durum |
|---|---|---|---|---|
| DR34ML4Y_LTXXX_V2.safetensors | models/1811313 | **2950842** | DR34ML4Y_LTXXX_V2.safetensors | ✅ birebir |
| Penile_Praxis_V4.safetensors | models/2332473 | **2772932** (v4.0 LTX2.3) | Penile_Praxis_V4.safetensors | ✅ birebir |
| LTX2.3_Physics_V2_000002000.safetensors | models/2668916 | **2996907** | DaSiWa_LTX23_NSFW_Bodyphysics_Fluid_Motion_Enhancer_v01.safetensors | ⚠️ doğru konsept, **farklı dosya adı** (tek sürüm v1.0; UI'da Physics loader'ında seç) |

## 4) Otomatik (manuel indirme yok)

| Dosya | Not |
|---|---|
| flownet.pkl | RIFE modeli — ComfyUI-VFI ilk kullanımda kendi indirir |

---

**Notebook'a uygulanacak:** Bölüm 1'deki 16 node (notebook'ta 10 vardı → 6 ekle), Bölüm 2'deki 11 model (notebook ile aynı). Bölüm 3 LoRA'lar Hücre 7 notunda "kullanıcı sağlar" olarak belirtilir. ⚠️ node'larda clone hatası notebook'u durdurmasın → tolerant (warn + Manager).

## Doğrulama (tam tarama)

Workflow'daki **tüm model loader node'ları** tek tek kontrol edildi → hepsi yukarıdaki listeyle eşleşiyor, karşılıksız loader yok:
`DiffusionModelLoaderKJ`, `UNETLoader`, `DualCLIPLoader` (gemma + text_projection), `VAELoaderKJ` ×2 (video+audio VAE), `VAELoader` (taeltx2_3), `LatentUpscaleModelLoader`, `UpscaleModelLoader`, `Power Lora Loader (rgthree)` ×3.

**Başka model türü yok:** `clip_vision`, `controlnet`, `ipadapter`, `wav2vec`, `embeddings`, `.onnx`, `.ckpt` arandı → **hiç eşleşme yok**. Liste eksiksiz.
