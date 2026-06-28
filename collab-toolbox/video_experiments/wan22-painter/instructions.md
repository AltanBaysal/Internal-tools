# WAN 2.2 I2V — "PainterI2V" (kenpechi) — Talimatlar

- **Kaynak:** https://civitai.red/models/2409134/wan22-i2v-painteri2v-workflow-kenpechi
- **Sürüm:** v2.4 — Güncelleme: 2026-05-05
- **Model ailesi:** WAN 2.2 I2V, lisans: Apache 2.0
- **Workflow arşivi:** 28.46 KB (Civitai'den indirilip bu klasöre `workflow.json` olarak konacak)

> Kaynak sayfadan birebir aktarılmış referans. Yazarın notu: kendisi AI üretiminde uzman olmadığını, bazı bilgilerin yanlış olabileceğini belirtiyor.

## Amaç / öne çıkanlar

- Tekrarlı üretimde **kompakt operasyon**: prompt girişi, görsel seçimi, süre/step/çözünürlük ve özellikle **LoRA seçimi** sırasında ekran kaydırmayı azaltır.
- Tüm node'lar sabitlenmiş (istemsiz kayma yok), kullanılabilirlik artırılmış.
- **İki video birleştirme:** ilk üretimin son karesi ikinci üretimin başlangıç görseli olur. SVI'dan farklı olarak 5-frame overlap yok; ilk görselin içeriği korunmaz (yüz/geçiş bozulabilir). Pratik sınır: **2 video**.
- v2.1: **GGUF model loader** standart; FPS sabit 16'dan değiştirilebilir hale geldi; **RIFE-VFI** çarpanı input alanından ayarlanabilir.
- Seed node: **Seed (rgthree)** (eski "CR Seed" sorunluydu).

## Temel WAN 2.2 modelleri (HuggingFace)

Kaynak yalnızca base CLIP + VAE linki veriyor; diffusion checkpoint kullanıcının seçtiği WAN 2.2 I2V modeli (GGUF loader mevcut).

- **CLIP (text encoders):** https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/tree/main/split_files/text_encoders
- **VAE:** https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/tree/main/split_files/vae

## Workflow'a özel LoRA + custom node'lar

- **PainterI2V** (node): https://github.com/princepainter/ComfyUI-PainterI2V
- **PainterI2V Advanced** (node): https://github.com/princepainter/ComfyUI-PainterI2Vadvanced
- **FFGO** (node): https://github.com/zli12321/FFGO-Video-Customization
- **FFGO LoRA (merged):** https://huggingface.co/Video-Customization/FFGO-Lora-Adapter/tree/main/merged_lora
- **RIFE-VFI** (frame interpolation — node adı kaynakta belirtilmemiş; ComfyUI-VFI / Frame-Interpolation)
- **rgthree** (Seed (rgthree) için)

## Kullanım notları

- **PainterI2V:** slow motion'ı iyileştirir + **kamera hareketini** güçlendirir; yazarın workflow'unda kamera hareketi için elzem.
- **FFGO:** input görselinin (özellikle kadın karakterlerde **yüz tutarlılığı**) korunmasını sağlar. Ağırlık **0.3** ayarlı; yükseltilebilir ama çok yüksek değer hareketi bozar.
- İki-video birleştirmede geçiş kareleri doğal olmayabilir; ilk üretimde yüz net görünüyorsa ikinci üretimde kişi değişmez. 3+ video pratikte kullanılmaz hale geliyor.
- SVI yerine bu workflow: dinamik ama doğal hareket için daha uygun (SVI aynı hareketi üretmekte zorlanıyor).
