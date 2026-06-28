# WAN 2.2 I2V — "All-in-One" (fatberg_slim) — Talimatlar

- **Kaynak:** https://civitai.red/models/2404513/i2v-first-last-frame-loop-upscale-and-interpolate-or-all-in-one-wan-22-workflow
- **Sürüm:** Güncelleme: 2026-05-11
- **Model ailesi:** WAN 2.2 (I2V / FLF / Loop), lisans: Apache 2.0
- **Workflow arşivi:** 22.44 KB (Civitai'den indirilip bu klasöre `workflow.json` olarak konacak)

> **Önemli:** Tam kurulum talimatları, önerilen LoRA ağırlıkları ve **tüm indirme linkleri workflow'un İÇİNDE bir markdown guide node'unda.** Yani kesin model/dosya listesi `workflow.json` gelince oradan çıkarılacak.

## Ne yapar (3-in-1 + son-işlem)

Tek workflow, merkezi "Control Center"dan şube seçilir:

- 🖼️ **Image to Video (I2V)** — ana mod; tek görsel + prompt. **Batch Image Loader** ile bir klasördeki tüm görselleri sırayla işler (manuel yükleme yok).
- 🔁 **First Last Frame (FLF)** — başlangıç ve bitiş karesi verilir, ara hareketi model üretir (kontrollü geçiş/sinematik).
- 🔄 **Loop** — FLF gibi ama başlangıç=bitiş aynı görsel → kesintisiz döngü.
- ⬆️ **Upscale & Interpolate** — bağımsız aç/kapa (Fast Groups Bypasser); biri, ikisi veya hiçbiri.
- 💾 **Save Last Frame** — videonun son karesini kaydeder, sonraki üretime zincirlemek için (uzun video üretiminin anahtarı).

## Öne çıkan özellikler

- 🎛️ **Central Control Center** — model, VAE, CLIP, çözünürlük, step ve Speed LoRA'lar **bir kez** ayarlanır, tüm şubelerde kullanılır.
- ⚡ **Lightning LoRA** desteği (Lightx2v High + Low) — dual-step sampler ile hızlı render.
- 🔀 **Dynamic Prompts** (wildcard) desteği.
- 🧩 **Power LoRA Loader** her şube için bağımsız.
- 📦 **FP8 scaled, model merge ve GGUF** varyantları destekli.

## Model klasör yapısı

Kaynak yalnızca klasör eşlemesi veriyor (kesin dosya adları workflow guide node'unda):

```
ComfyUI/models/
├── diffusion_models/   → WAN 2.2 model dosyaları
├── LoRAs/              → Speed LoRA'lar + concept LoRA'lar
├── vae/                → VAE
└── text_encoders/      → CLIP / text encoder
```

⚠️ Workflow yüklendikten sonra her model loader'a tıklayıp dosyaları dropdown'dan **elle seç** — yollar otomatik çözülmüyor.

## Notlar (notebook için)

- Kesin model/LoRA/VAE/CLIP dosyaları ve indirme linkleri **workflow.json içindeki markdown guide node**'undan alınacak. JSON gelince oradaki listeyi bu md'ye işleyip indirme hücrelerini doldururuz.
- Custom node'lar sayfada listelenmemiş; en az rgthree (Fast Groups Bypasser, Power LoRA Loader), Dynamic Prompts, RIFE/interpolation, batch loader gerekir — kesin liste JSON'dan netleşir.
