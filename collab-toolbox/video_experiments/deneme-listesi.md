# Video Generation — Deneme Listesi

Farklı video üretim yöntemlerini/workflow'larını test etmek için yapılacaklar listesi.
Branch: `video-generation`. Her madde test edildikçe durumu işaretle ve notunu yaz.

## Mevcut yapı (baseline — hepsi WAN)

| Araç | Model | Giriş türü | Notlar |
|---|---|---|---|
| `video_generator/imageToVideo.ipynb` | WAN 2.2 I2V (SmoothMix_I2V_v2, High+Low noise) | image-to-video, first+last frame | lightx2v 4-step hız LoRA, WAN_General_NSFW LoRA, RIFE interpolation gömülü |
| `loop_maker/comfy_ui.ipynb` | WAN 2.1 VACE 14B | video-to-video / loop | lightx2v step-distill LoRA |

## Hedef referanslar (yeniden oluşturulacak)

- [ ] **Civitai video #133122787** — bu videoyu yeniden oluşturmayı dene
  - Kaynak: https://civitai.red/images/133122787
  - Hedef: aynı/benzer sonucu üretebilecek model + workflow + prompt kombinasyonunu bulmak
  - Durum: bekliyor
  - Not: —

- [ ] **Civitai video #132599076** — bu videoyu yeniden oluşturmayı dene
  - Kaynak: https://civitai.red/images/132599076
  - Hedef: aynı/benzer sonucu üretebilecek model + workflow + prompt kombinasyonunu bulmak
  - Durum: bekliyor
  - Not: —

## Denenecek workflow'lar / modeller

- [ ] **LTX 2.3 I2V — "Eros" (mrxin)**
  - Kaynak: https://civitai.red/models/2488266/mrxin-ltx-23-i2v-eros-12gb-vram-and-32gb-ram-workflow
  - Model ailesi: **LTX-Video 2.3** (WAN dışı — yeni model ailesi)
  - Neden: düşük VRAM (12GB) / 32GB RAM ile çalışan I2V; mevcut WAN'a alternatif hız/donanım profili
  - Durum: bekliyor
  - Not: —

- [ ] **WAN 2.2 I2V — "PainterI2V" (Kenpechi)**
  - Kaynak: https://civitai.red/models/2409134/wan22-i2v-painteri2v-workflow-kenpechi
  - Model ailesi: WAN 2.2 I2V (farklı workflow varyantı)
  - Neden: mevcut SmoothMix workflow'una karşı farklı bir WAN 2.2 I2V workflow kıyası
  - Durum: bekliyor
  - Not: —

- [ ] **WAN 2.2 I2V — "All-in-One" (first/last frame + loop + upscale + interpolate)**
  - Kaynak: https://civitai.red/models/2404513/i2v-first-last-frame-loop-upscale-and-interpolate-or-all-in-one-wan-22-workflow
  - Model ailesi: WAN 2.2 I2V (tek workflow'da: first+last frame, loop, upscale, interpolate)
  - Neden: üretim + son-işlem (upscale/interpolate/loop) tek workflow'da birleşik — pipeline'ı sadeleştirebilir
  - Durum: bekliyor
  - Not: —

- [ ] **DASIWA — WAN 2.2 I2V 14B "Lightspeed" (model/checkpoint)**
  - Kaynak: https://civitai.red/models/1981116/dasiwa-wan-22-i2v-14b-or-lightspeed-or-safetensors
  - Model ailesi: WAN 2.2 I2V 14B (safetensors checkpoint — workflow değil, model)
  - Neden: mevcut SmoothMix_I2V_v2'ye alternatif WAN 2.2 I2V finetune; "Lightspeed" hız odaklı
  - Durum: bekliyor
  - Not: —

- [ ] **WAN 2.2 T2V — "Smooth Workflow v5.0" TEXT2VIDEO grubu (Digital Pastel)** → [wan22-smooth-t2v/](wan22-smooth-t2v/)
  - Kaynak: https://civitai.red/models/1995784/smooth-mix-wan-22-14b-i2vt2v
  - Model ailesi: WAN 2.2 **T2V**-A14B (SmoothMix T2V v3 High+Low — version 2768924 / 2768944)
  - Neden: listedeki ilk text-to-video denemesi — mevcut her şey I2V. `video_generator/imageToVideo.json` zaten bu grafiğin FIRST2LASTFRAME grubunun API export'u (node ID'leri birebir tutuyor); T2V grubu hep vardı, hiç açılmadı. Sampler/çözünürlük/süre/RIFE ayarları I2V ile aynı → kıyas temiz, değişen tek eksen I2V→T2V.
  - Durum: bekliyor
  - Not: —
