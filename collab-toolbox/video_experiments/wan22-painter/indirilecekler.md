# Painter — Colab'da indirilecekler (workflow.json'dan çıkarıldı)

Etiketler: **✅** API'den doğrulandı · **📌** workflow.json'a gömülü (yazar verdi) · **📚** kanonik repo (yaygın, bu turda ayrıca ping'lenmedi) · **❌** bulunamadı → kullanıcı verecek.

> **Doğrulama hatası yakaladı:** Workflow'daki `civitai 1585622@2337890` linki **FFGO değil**, lightx2v lightning LoRA. Painter'da **gated Civitai checkpoint YOK**.

## 1) Custom node'lar (12)

| # | Paket | git URL | Kaynak |
|---|---|---|---|
| 1 | ComfyUI-Manager | https://github.com/ltdrdata/ComfyUI-Manager | 📚 |
| 2 | rgthree-comfy | https://github.com/rgthree/rgthree-comfy | 📚 |
| 3 | ComfyUI-Custom-Scripts | https://github.com/pythongosssss/ComfyUI-Custom-Scripts | 📚 |
| 4 | ComfyUI-KJNodes | https://github.com/kijai/ComfyUI-KJNodes | 📚 |
| 5 | ComfyUI-Impact-Pack | https://github.com/ltdrdata/ComfyUI-Impact-Pack | 📚 |
| 6 | ComfyUI-GGUF | https://github.com/city96/ComfyUI-GGUF | 📚 |
| 7 | ComfyUI-VideoHelperSuite | https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite | 📚 |
| 8 | ComfyUI-Easy-Use | https://github.com/yolain/ComfyUI-Easy-Use | 📚 |
| 9 | ComfyUI-Frame-Interpolation | https://github.com/Fannovel16/ComfyUI-Frame-Interpolation | 📚 |
| 10 | ComfyUI-PainterI2V | https://github.com/princepainter/ComfyUI-PainterI2V | 📌 |
| 11 | ComfyUI-PainterI2Vadvanced | https://github.com/princepainter/ComfyUI-PainterI2Vadvanced | 📌 |
| 12 | FFGO-Video-Customization | https://github.com/zli12321/FFGO-Video-Customization | 📌 |

## 2) Modeller — HF (gated YOK)

| Hedef | Dosya | Kaynak | Durum |
|---|---|---|---|
| diffusion_models | wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors | Comfy-Org/Wan_2.2_ComfyUI_Repackaged | 📚 |
| diffusion_models | wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors | Comfy-Org/Wan_2.2_ComfyUI_Repackaged | 📚 |
| text_encoders | umt5_xxl_fp8_e4m3fn_scaled.safetensors | Comfy-Org/Wan_2.2_ComfyUI_Repackaged | 📚 |
| vae | wan_2.1_vae.safetensors | Comfy-Org/Wan_2.2_ComfyUI_Repackaged | 📚 |
| loras | Wan_2_2_I2V_A14B_HIGH_lightx2v_4step_lora_v1030_rank_64_bf16.safetensors | `Kijai/WanVideo_comfy → LoRAs/Wan22_Lightx2v/` | ✅ |
| loras | **Wan2.2_i2v_A14b_low_noise_lora_rank64_lightx2v_4step_1022.safetensors** | — | ❌ Kijai/WanVideo_comfy'de YOK → kullanıcı verecek |
| loras | high_noise_model.safetensors (FFGO HIGH) | `Video-Customization/FFGO-Lora-Adapter → merged_lora/` | ✅ (workflow adı `Wan2.2_FFGO-LoRA-HIGH_bf16` — UI'da seç) |
| loras | low_noise_model.safetensors (FFGO LOW) | `Video-Customization/FFGO-Lora-Adapter → merged_lora/` | ✅ (workflow adı `Wan22_FFGO-LoRA-LOW_bf16` — UI'da seç) |
| upscale_models | **RealESRGAN_x2plus.pt** | — | ❌ ai-forever/Real-ESRGAN'da yok (orada x2/x4/x8 var, x2plus yok) → kullanıcı verecek |

**Alternatif (GGUF, düşük VRAM):** `Wan2.2-I2V-A14B-HighNoise-Q8_0.gguf` / `LowNoise-Q8_0.gguf` → 📚 QuantStack/Wan2.2-I2V-A14B-GGUF (workflow GGUF loader'ı yüklü).
**Not (LOW lightx2v):** Kijai'de tam dosya yok ama LOW alternatifleri var (`Wan_2_2_I2V_A14B_LOW_lightx2v_4step_lora_260412_rank_64_fp16.safetensors`) → kullanıcı bunu substitüt seçebilir.

## 3) Modeller — gated Civitai

**Yok.**

## 4) Kişisel/opsiyonel concept LoRA'lar (~35) — ❌ URL'siz → kullanıcı verecek

Power Lora Loader'larda `HIGH\...` / `LOW\...` klasörlerinde kişisel NSFW concept LoRA'lar (BreastRub, Handjob, Titfuck-Paizuri, Deepthroat, Pov-insertion, PussyLoRA, big_breasts, Wan2_Undressing, F4c3spl4sh, M4crom4sti4, NSFW-22, Walk, Jiggle Tits, Body-Cumshot-Pullout). İndirme URL'si yok → kullanıcı kendi koleksiyonundan koyar veya loader'ı kapatır.
- İstisna: `DR34ML4Y_HIGH/LOW_V2` → Civitai 1811313 (HIGH 2553151, LOW 2553271) ✅; istenirse eklenir.

## 5) Otomatik (manuel indirme yok)

| Dosya | Not |
|---|---|
| rife49.pt | RIFE — ComfyUI-Frame-Interpolation ilk kullanımda iner |

## 6) Doğrulama (tam tarama)

Loader node'ları: `UNETLoader`, `UnetLoaderGGUF`, `CLIPLoader`, `VAELoader`, `LoraLoaderModelOnly`, `Power Lora Loader (rgthree)`, `UpscaleModelLoader`, `LoadImage` → hepsi listeyle eşleşti. `clip_vision` referansı var ama CLIPVisionLoader yok → opsiyonel input. `controlnet/ipadapter/wav2vec/onnx/embeddings` → yok.

**❌ kalanlar (kullanıcı verecek):** lightx2v LOW (`...4step_1022`), RealESRGAN_x2plus.pt, ~35 kişisel concept LoRA.
