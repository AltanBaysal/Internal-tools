# WAN 2.2 Smooth T2V — Colab'da indirilecekler (workflow_manual.json'dan çıkarıldı)

Etiketler: **✅** API'den doğrulandı · **📌** grafiğe gömülü (yazar verdi) · **📚** kanonik repo (yaygın, ping'lenmedi) · **⚠️** bilinen risk.

Bu liste `manual.ipynb` içindir. `api.ipynb` aynı listeden **NSFW LoRA'ları indirmez** (API grafiğinde LoRA loader'ları boş, yerleri yok) — orada ~33.5 GiB iner.

> Grafiğin **TEXT2VIDEO** grubunun ihtiyacı iner. Diğer 3 grup (IMAGE2VIDEO / FIRST2LASTFRAME / AUDIO2VIDEO) grafikte durur ama modelleri **inmez** — açarsan model bulunamaz hatası verir (bkz. §6).

## 1) Custom node'lar (16)

`video_generator/imageToVideo.ipynb`'nin listesi birebir — aynı grafiğin FIRST2LASTFRAME grubunu çalıştıran kanıtlanmış liste. Tam grafik yüklendiği için **hepsi** şart: bypass'lı grubun node class'ı yoksa UI "missing node" verir.

| # | Paket | git URL | Sağladığı |
|---|---|---|---|
| 1 | ComfyUI-Manager | https://github.com/ltdrdata/ComfyUI-Manager.git | eksik node tespiti (UI) |
| 2 | rgthree-comfy | https://github.com/rgthree/rgthree-comfy.git | Power Lora Loader, Seed, Fast Groups Bypasser, Label |
| 3 | comfy_mtb | https://github.com/melMass/comfy_mtb.git | Note Plus, Pick From Batch, RIFEInterpolation |
| 4 | ComfyUI-VideoHelperSuite | https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git | VHS_VideoCombine |
| 5 | ComfyUI-MMAudio | https://github.com/kijai/ComfyUI-MMAudio.git | AUDIO2VIDEO grubu (modelleri inmez) |
| 6 | ComfyUI-WanVideoWrapper | https://github.com/kijai/ComfyUI-WanVideoWrapper.git | Wan video node'ları |
| 7 | ComfyUI-GGUF | https://github.com/city96/ComfyUI-GGUF.git | UnetLoaderGGUF (grafikte var ama boş) |
| 8 | ComfyUI-KJNodes | https://github.com/kijai/ComfyUI-KJNodes.git | ImageResizeKJv2, ColorMatch |
| 9 | ComfyMath | https://github.com/evanspearman/ComfyMath.git | ComfyMathExpression (süre → kare: `a*16+1`) |
| 10 | ComfyUI-Frame-Interpolation | https://github.com/Fannovel16/ComfyUI-Frame-Interpolation.git | RIFE |
| 11 | ComfyUI-VFI | https://github.com/GACLove/ComfyUI-VFI.git | frame interpolation |
| 12 | ComfyUI_Comfyroll_CustomNodes | https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git | CR Float To Integer |
| 13 | ComfyUI-Easy-Use | https://github.com/yolain/ComfyUI-Easy-Use.git | easy cleanGpuUsed |
| 14 | ComfyUI-mxToolkit | https://github.com/Smirnov75/ComfyUI-mxToolkit.git | mxSlider2D (çözünürlük) |
| 15 | ComfyUI-NAG | https://github.com/scottmudge/ComfyUI-NAG.git | KSamplerWithNAG (Advanced) |
| 16 | comfyui-adaptiveprompts | https://github.com/Alectriciti/comfyui-adaptiveprompts.git | PromptGenerator |

## 2) Modeller — gated Civitai (model 1995784, version ID'ler API ile doğrulandı ✅)

| Hedef | Kaydedilecek ad | Version ID | Civitai'nin verdiği ad | Boyut | Durum |
|---|---|---|---|---|---|
| diffusion_models | `SmoothMix_T2V_High_v3.safetensors` | **2768924** | smoothMixWan2214BI2V_t2vHighV30.safetensors | ~13.5 GiB | ✅ "T2V High v3.0", base `Wan Video 2.2 T2V-A14B` |
| diffusion_models | `SmoothMix_T2V_Low_v3.safetensors` | **2768944** | smoothMixWan2214BI2V_t2vLowV30.safetensors | ~13.5 GiB | ✅ "T2V Low v3.0", aynı base |
| loras | `WAN_General_NSFW_HIGH.safetensors` | **2073605** | NSFW-22-H-e8.safetensors | ~0.57 GiB | ⚠️ base `Wan Video 2.2 **I2V**-A14B` |
| loras | `WAN_General_NSFW_LOW.safetensors` | **2083303** | (2.2 LOW v0.08a nightly) | ~0.57 GiB | ⚠️ base `Wan Video 2.2 **I2V**-A14B` |

> **Ad değişimi şart.** Civitai dosyayı `smoothMixWan2214BI2V_t2v*V30.safetensors` olarak veriyor; grafiğin UNETLoader **37**/**56**'sı `SmoothMix_T2V_*_v3.safetensors` istiyor. `fetch()` hedef adla kaydeder — yapılmazsa dropdown'da model görünmez.

> **NSFW LoRA riski.** Model 1307155'in dört sürümü de I2V-A14B; T2V sürümü **yok**. Kullanıcı isteğiyle iniyor. Çıktı bozuksa **önce bunu bypass et** — yoksa "T2V mi kötü, LoRA mı uyumsuz" ayrışmaz.

## 3) Modeller — HuggingFace

| Hedef | Kaydedilecek ad | Kaynak | Boyut | Durum |
|---|---|---|---|---|
| text_encoders | `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | Comfy-Org/Wan_2.1_ComfyUI_repackaged → `split_files/text_encoders/` | ~6.3 GiB | 📚 imageToVideo'da çalışan indirme |
| vae | **`Wan2_1_VAE_fp32.safetensors`** ← `wan_2.1_vae.safetensors` | Comfy-Org/Wan_2.1_ComfyUI_repackaged → `split_files/vae/` | ~250 MB | 📚 imageToVideo deseni (indir + rename) |

> **lightx2v LoRA'sı gerekmiyor — inmez.** Yazar Power Lora Loader **109**/**110**'u boş bırakmış ve sampler 6 step / cfg 1; bu bir çelişki değil: T2V v3'te distill LoRA checkpoint'e **merge edilmiş** (model sayfası: *"Just as T2V v2.0 it has light2xv baked in it"*). Elle eklemek iki kez uygular ve çıktıyı bozar. 18 Tem 2026'da UI'da doğrulandı — sıfır LoRA en iyi sonucu veriyor; `wan2.2_t2v_lightx2v_4steps_lora_v1.1_*` (2×1.14 GiB) manifestten çıkarıldı.

## 4) Upscale modeli — YOK

Yazarın "Upscale by 2"si `ImageScaleBy` (lanczos) — algoritmik, dosya inmez. Grafikte `UpscaleModelLoader` yok (grep: **0 eşleşme**).

## 5) Otomatik (manuel indirme yok)

| Dosya | Not |
|---|---|
| `flownet.pkl` | `RIFEInterpolation` (comfy_mtb) ilk kullanımda indirir. ✅ Notebook'un model listesine **eklenmesi gerekmiyor**: kurulum log'unda hiç geçmiyor (setup'ta inmiyor), ama RIFE node **160** TEXT2VIDEO zincirinde ve üretim sorunsuz çalıştı → dosyayı node kendi indirmiş. |

## 6) İnmeyen (diğer gruplar için — bilerek atlandı)

`SmoothMix_I2V_v2_High/Low` (2513182 / 2513186), `clip_vision_h.safetensors`, MMAudio 4 dosya (`mmaudio_large_44k_v2_fp16`, `mmaudio_vae_44k_fp16`, `mmaudio_synchformer_fp16`, `apple_DFN5B-CLIP-ViT-H-14-384_fp16`). IMAGE2VIDEO / FIRST2LASTFRAME / AUDIO2VIDEO gruplarını açarsan bunlar eksik olur.

## 7) Doğrulama (tam tarama)

Grafikteki loader node'ları: `UNETLoader` ×6, `UnetLoaderGGUF` ×6 (hepsi `unet_name: null` — boş, kullanılmıyor), `CLIPLoader` ×3, `VAELoader` ×3, `CLIPVisionLoader` ×1 (yalnız F2LF), `Power Lora Loader (rgthree)` ×6 (hepsi **boş**), `MMAudioModelLoader` / `MMAudioFeatureUtilsLoader` ×4 (yalnız audio), `LoadImage` ×3 (I2V/F2LF), `RIFEInterpolation` ×4.

`UpscaleModelLoader` → **yok**. `controlnet` / `ipadapter` / `onnx` / `embeddings` → **yok**.

**TEXT2VIDEO grubunun (x: 524→3750, y: −61→1980) kullandığı loader'lar:** UNETLoader **37**/**56**, CLIPLoader **38**, VAELoader **39**, Power Lora Loader **109**/**110** (boş), RIFEInterpolation **160** → hepsi yukarıdaki listeyle eşleşti. Latent: `WanImageToVideo` **50**, `start_image` bağlanmadan (WAN'ın boş-latent numarası). Prompt: `PromptGenerator` **230:229** (boş gelir).
