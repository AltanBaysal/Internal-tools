# WAN 2.2 Smooth T2V — Bağımlılıklar (workflow_manual.json'dan çıkarıldı)

Bu klasördeki iki notebook'un Colab'da neye ihtiyaç duyduğu: custom node'lar, modeller, otomatik inenler ve **bilerek inmeyenler**. Notebook'ların nasıl kullanılacağı [instructions.md](instructions.md)'de.

Etiketler: **✅** API'den doğrulandı · **📌** grafiğe gömülü (yazar verdi) · **📚** kanonik repo (yaygın, ping'lenmedi) · **⚠️** bilinen risk.

**Hangi notebook neyi indirir:** ikisi de **aynı seti**, ~35.3 GiB. Bu bilinçli bir kural — listeler hizalı tutulur ki UI'da LoRA'lı bir graf export edildiğinde `api.ipynb` notebook'a dokunmadan çalışsın.

> `api.ipynb` LoRA'ları indirir ama **kullanmaz**: API grafiğinin Power Lora Loader'ları boş. Etki etmeleri için `manual.ipynb`'de UI'da takılıp **Workflow → Export (API)** ile Drive'daki graf güncellenmeli.

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

## 2) Modeller — gated Civitai (version ID'ler API ile doğrulandı ✅)

İki ayrı Civitai modelinden geliyor, ikisi de aynı yazarın: checkpoint'ler **1995784**'ten (SmoothMix WAN 2.2), LoRA'lar **2040641**'den (SmoothMix Animations WAN 2.2).

| Hedef | Kaydedilecek ad | Version ID | Civitai'nin verdiği ad | Boyut | Durum |
|---|---|---|---|---|---|
| diffusion_models | `SmoothMix_T2V_High_v3.safetensors` | **2768924** | smoothMixWan2214BI2V_t2vHighV30.safetensors | ~13.5 GiB | ✅ "T2V High v3.0", base `Wan Video 2.2 T2V-A14B` |
| diffusion_models | `SmoothMix_T2V_Low_v3.safetensors` | **2768944** | smoothMixWan2214BI2V_t2vLowV30.safetensors | ~13.5 GiB | ✅ "T2V Low v3.0", aynı base |
| loras | `SmoothMix_Style_High.safetensors` | **2318650** | (sürüm: Style High) | ~0.3 GiB | ✅ base `Wan Video 2.2 T2V-A14B` |
| loras | `SmoothMix_Style_Low.safetensors` | **2318707** | SmoothMixStyle_Low.safetensors | ~0.3 GiB | ✅ base `Wan Video 2.2 T2V-A14B` |
| loras | `SmoothMix_Animation_High.safetensors` | **2309690** | (sürüm: Animation High) | ~0.3 GiB | ✅ base `Wan Video 2.2 T2V-A14B` |
| loras | `SmoothMix_Animation_Low.safetensors` | **2309689** | (sürüm: Animation Low) | ~0.3 GiB | ✅ base `Wan Video 2.2 T2V-A14B` |
| loras | `SmoothMix_Futanari_High.safetensors` | **2476982** | (sürüm: Futanaris and Males High) | ~0.3 GiB | ✅ base `Wan Video 2.2 T2V-A14B` |
| loras | `SmoothMix_Futanari_Low.safetensors` | **2474616** | (sürüm: Futanaris and Males Low) | ~0.3 GiB | ✅ base `Wan Video 2.2 T2V-A14B` |

> **Ad değişimi şart (checkpoint'ler).** Civitai dosyayı `smoothMixWan2214BI2V_t2v*V30.safetensors` olarak veriyor; grafiğin UNETLoader **37**/**56**'sı `SmoothMix_T2V_*_v3.safetensors` istiyor. `fetch()` hedef adla kaydeder — yapılmazsa dropdown'da model görünmez. LoRA'larda böyle bir zorunluluk yok (loader'lar boş gelir), adlar okunabilirlik için seçildi.
>
> Parantezli hücreler Civitai'nin sürüm adı: yalnız **2318707**'nin gerçek dosya adı API'den teyit edildi, diğerleri indirme anında görülür.

> **LoRA kullanımı.** Altısı da T2V-A14B tabanlı, yani grafiğin base'iyle uyumlu — I2V tuzağı bu sette yok. Ama **takmak yetmez, trigger word şart**: Style ve Animation için prompt'ta `SmoothMixAnime` ya da `SmoothMixRealism` geçmeli, Futanari çifti kendi kelimeleriyle (`futanari`, `flaccid`, `erect`, …). Yazarın önerdiği strength **0.5–1.0**; High → Power Lora Loader **109**, Low → **110**, hep aynı setten çift olarak.
>
> **Setin XXX Animations çifti (2376136 / 2376143) bilerek inmiyor:** koleksiyondaki tek I2V-A14B tabanlı çift, yani aşağıda ayıklanan uyumsuzluğun aynısı.
>
> Önceki `WAN_General_NSFW` çifti (model 1307155, I2V tabanlı) 2026-07-21'de bu listeden çıkarıldı. `video_generator/imageToVideo.ipynb`'de **duruyor** — o araç I2V, LoRA orada base'iyle uyumlu.

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

Hangi grubu açarsan onun satırındakiler eksik olur. Dağılım §7'deki loader taramasından geliyor — her dosya her gruba gerekmiyor:

| Grup | Eksik olan |
|---|---|
| IMAGE2VIDEO | `SmoothMix_I2V_v2_High/Low` (2513182 / 2513186) |
| FIRST2LASTFRAME | yukarıdaki I2V çifti **+** `clip_vision_h.safetensors` |
| AUDIO2VIDEO | MMAudio 4 dosya: `mmaudio_large_44k_v2_fp16`, `mmaudio_vae_44k_fp16`, `mmaudio_synchformer_fp16`, `apple_DFN5B-CLIP-ViT-H-14-384_fp16` |

`clip_vision_h.safetensors` **yalnız FIRST2LASTFRAME'in** ihtiyacı: grafikteki tek `CLIPVisionLoader` (id **351**) o kutunun içinde. IMAGE2VIDEO'yu açmak onu gerektirmez.

## 7) Doğrulama (tam tarama)

Grafikteki loader node'ları: `UNETLoader` ×6, `UnetLoaderGGUF` ×6 (hepsi `unet_name: null` — boş, kullanılmıyor), `CLIPLoader` ×3, `VAELoader` ×3, `CLIPVisionLoader` ×1 (yalnız F2LF), `Power Lora Loader (rgthree)` ×6 (hepsi **boş**), `MMAudioModelLoader` / `MMAudioFeatureUtilsLoader` ×4 (yalnız audio), `LoadImage` ×3 (I2V/F2LF), `RIFEInterpolation` ×4.

`UpscaleModelLoader` → **yok**. `controlnet` / `ipadapter` / `onnx` / `embeddings` → **yok**.

**TEXT2VIDEO grubunun (x: 524→3750, y: −61→1980) kullandığı loader'lar:** UNETLoader **37**/**56**, CLIPLoader **38**, VAELoader **39**, Power Lora Loader **109**/**110** (boş), RIFEInterpolation **160** → hepsi yukarıdaki listeyle eşleşti. Latent: `WanImageToVideo` **50**, `start_image` bağlanmadan (WAN'ın boş-latent numarası). Prompt: `PromptGenerator` **230:229** (boş gelir).
