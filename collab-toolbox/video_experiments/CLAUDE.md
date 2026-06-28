# video_experiments

Farklı video üretim workflow'larını Colab Pro'da **görsel** denemek için bağımsız ComfyUI notebook'ları. Her notebook ComfyUI + Manager + custom node'lar + modelleri kaynaktan indirir, `cloudflared` ile bir UI linki verir; kullanıcı `workflow.json`'u UI'a elle yükleyip çalıştırır. **Drive kullanılmaz.**

## Denemeler

| Klasör | Workflow | Model ailesi |
|---|---|---|
| [ltx23-eros/](ltx23-eros/) | MrXin LTX 2.3 I2V "Eros" V6 | LTX-Video 2.3 |
| [wan22-painter/](wan22-painter/) | PainterI2V (kenpechi) v2.4 | WAN 2.2 I2V |
| [wan22-allinone/](wan22-allinone/) | All-in-One I2V/FLF/Loop (fatberg_slim) | WAN 2.2 I2V |
| [wan22-dasiwa/](wan22-dasiwa/) | DaSiWa FastFidelity C-AiO | WAN 2.2 I2V-A14B |

Her klasörde: `<deneme>.ipynb` + `workflow.json` (ComfyUI workflow) + `instructions.md` (Civitai sayfası özeti).

## Ortak kalıp

- **Base:** [comfyui_colab_with_manager.ipynb](comfyui_colab_with_manager.ipynb) (ComfyUI'nin resmi Manager'lı Colab notebook'u, referans).
- Tek CONFIG hücresi (Civitai `__Secure-civitai-token` cookie), Drive kapalı (`USE_GOOGLE_DRIVE=False`).
- **Civitai gated indirme:** `civitai.com/api/download/models/{version_id}` + **sadece cookie** (`?token=` API key yok — gated asset 401 verir). Video generator (`imageToVideo.ipynb`) ile birebir aynı kanıtlı kalıp.
- **Fail-fast:** inmeme ihtimali en yüksek gated modeller önce **probe** (ilk 1 KB) edilip indirilir, sonra HF `aria2c`.
- **Fail-loud:** bozuk indirme `is_valid_safetensors` → RuntimeError; ComfyUI 90 sn'de kalkmazsa RuntimeError.
- **Verbose log:** her hücre `banner()` ile başlar; GPU, node clone sonuçları, her model boyut+süre, indirme özeti, ComfyUI başlangıç log tail'i basılır (kolay debug).

## Kullanım

1. Colab → notebook'u yükle → Runtime **A100** → CONFIG'e Civitai cookie → **Run all**.
2. Çıkan `trycloudflare` linkine gir → `workflow.json`'u yükle → modelleri seç → Run.

> Kişisel/NSFW concept LoRA'lar (Painter, DaSiWa) URL'siz; kullanıcı kendi koleksiyonundan ekler.
