# All-in-One — Colab'da indirilecekler (workflow.json'dan çıkarıldı)

Etiketler: **✅** API'den doğrulandı · **📌** workflow.json'a gömülü (yazar verdi) · **📚** kanonik repo (yaygın, ping'lenmedi) · **❌** bulunamadı → kullanıcı verecek.

> Model linkleri workflow içindeki **guide node'da** verilmiş (hepsi HF). **Gated Civitai YOK.** Kişisel LoRA yok — Control Center'da kullanıcı seçer.

## 1) Custom node'lar (11)

| # | Paket | git URL | Kaynak |
|---|---|---|---|
| 1 | ComfyUI-Manager | https://github.com/ltdrdata/ComfyUI-Manager | 📚 |
| 2 | ComfyUI_essentials | https://github.com/cubiq/ComfyUI_essentials | 📚 |
| 3 | ComfyUI-KJNodes | https://github.com/kijai/ComfyUI-KJNodes | 📚 |
| 4 | Derfuu_ComfyUI_ModdedNodes | https://github.com/Derfuu/Derfuu_ComfyUI_ModdedNodes | 📚 |
| 5 | rgthree-comfy | https://github.com/rgthree/rgthree-comfy | 📚 |
| 6 | ComfyUI-Easy-Use | https://github.com/yolain/ComfyUI-Easy-Use | 📚 |
| 7 | ComfyUI-Frame-Interpolation | https://github.com/Fannovel16/ComfyUI-Frame-Interpolation | 📚 |
| 8 | ComfyUI-Image-Selector | https://github.com/SLAPaper/ComfyUI-Image-Selector | ✅ registry |
| 9 | ComfyUI-GGUF | https://github.com/city96/ComfyUI-GGUF | 📚 |
| 10 | ComfyUI-VideoHelperSuite | https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite | 📚 |
| 11 | ComfyUI_Swwan | https://github.com/aining2022/ComfyUI_Swwan | ✅ GitHub |

> Dynamic Prompts (wildcard) için gömülü referans `adieyal/sd-dynamic-prompts` (A1111). ComfyUI tarafında ayrı cnr_id görünmüyor → gerekirse UI'da Manager → Install Missing Custom Nodes (opsiyonel).

## 2) Modeller — HF (gated YOK)

| Hedef | Dosya | Kaynak | Durum |
|---|---|---|---|
| diffusion_models | Wan2_2-I2V-A14B-HIGH_fp8_e4m3fn_scaled_KJ.safetensors | Kijai/WanVideo_comfy_fp8_scaled (I2V) | 📌 guide |
| diffusion_models | Wan2_2-I2V-A14B-LOW_fp8_e4m3fn_scaled_KJ.safetensors | Kijai/WanVideo_comfy_fp8_scaled (I2V) | 📌 guide |
| text_encoders | nsfw_wan_umt5-xxl_fp8_scaled.safetensors | `NSFW-API/NSFW-Wan-UMT5-XXL` | ✅ (workflow CLIPLoader'ı bunu istiyor — Comfy-Org umt5 DEĞİL) |
| vae | wan_2.1_vae.safetensors | Comfy-Org/Wan_2.2_ComfyUI_Repackaged | 📚 |
| loras | Wan_2_2_I2V_A14B_HIGH_lightx2v_MoE_distill_lora_rank_64_bf16.safetensors | Kijai/WanVideo_comfy (LoRAs/Wan22_Lightx2v) | 📌 guide |
| loras | Wan21_I2V_14B_lightx2v_cfg_step_distill_lora_rank64.safetensors | lightx2v/Wan2.1-I2V-14B-480P-StepDistill-CfgDistill-Lightx2v (loras) | 📌 guide |

**Alternatifler (workflow GGUF loader'ları da var → guide node'da):**
- GGUF base → 📌 QuantStack/Wan2.2-I2V-A14B-GGUF (HighNoise / LowNoise) · dosya: `wan22I2VA14BGGUF_a14bHigh/Low.gguf`
- GGUF CLIP → 📌 city96/umt5-xxl-encoder-gguf · dosya: `umt5-xxl-encoder-Q8_0.gguf`

## 3) Modeller — gated Civitai

**Yok.**

## 4) Kişisel/opsiyonel LoRA'lar

**Yok** — base + hız LoRA'larıyla çalışır; ek concept LoRA'yı kullanıcı Control Center'dan ekler.

## 5) Otomatik (manuel indirme yok)

| Dosya | Not |
|---|---|
| rife49.pt | RIFE — ComfyUI-Frame-Interpolation ilk kullanımda iner |

## 6) Doğrulama (tam tarama)

Loader node'ları: `CLIPLoader`, `CLIPLoaderGGUF`, `VAELoader`, `UNETLoader`, `UnetLoaderGGUF`, `Power Lora Loader (rgthree)`, `LoadImage`, `LoadImagesFromFolderKJ` → hepsi listeyle eşleşti. `clip_vision` referansı var ama loader yok → opsiyonel. `controlnet/ipadapter/wav2vec/onnx/embeddings` → yok.

**❌ kalan:** yok — tüm gerekli modeller HF'de doğrulanabilir kaynaklarda (fp8 yolları guide node'dan 📌, CLIP ✅).
