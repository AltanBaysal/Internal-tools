# DaSiWa WAN 2.2 Workflows (Darksidewalker) — Talimatlar

- **Workflow koleksiyonu:** "DaSiWa Wan2.2 Workflows | I2V | SVI 2.0 | FLF2V" — Güncelleme: 2026-06-10
- **Checkpoint (ayrı):** https://civitai.red/models/1981116/dasiwa-wan-22-i2v-14b-or-lightspeed-or-safetensors
- **Base model:** Wan Video 2.2 I2V-A14B, lisans: Apache 2.0 (AIR: `civitai:1823089@2712329`)
- **Arşiv:** 245.57 KB **Config** — checkpoint ile **aynı klasöre** config dosyası da konmalı.
- Civitai'den indirilip bu klasöre `workflow.json` olarak konacak (koleksiyon 5 parça; muhtemelen **FastFidelity C-AiO** kullanılır).

> Yazar: "Workflow'lar kendi checkpoint'lerime göre optimize." Yani DASIWA checkpoint + bu workflow birlikte kullanılır.

## Custom node gereksinimleri (sayfadaki "Requirements")

- `ComfyUI-VideoHelperSuite`
- `rgthree-comfy`
- `Comfyui-WhiteRabbit`
- `+ packaging, torchlanc` (python paketleri)
- `ComfyUI-KJNodes`
- `ComfyUI-GGUF`
- `ComfyUI-DaSiWa-Nodes`
- `ffmpeg`
- `Sage Attention` (opsiyonel)

## Koleksiyondaki workflow türleri

- **FastFidelity C-AiO** — 🖼️ I2V + FLF2V; otomatik aspect-ratio/çözünürlük, çoklu upscaler (Torchlanc / Upscale with Model / RTX Super Resolution), length automation, watermark, color match, MiniMeme (gif), **NAG (CFG1)**, interpolation, **perfect loop**, last frame extraction, bookmark kısayolları.
- **FastFidelity C-SVI** — 🖼️ SVI (SVI 2.0, 10 sampler'a kadar); torchlanc/model upscale, resolution matching, length automation, watermark, interpolation.
- **Swarm Basic** — SwarmUI preset (video için ComfyUI önerilir, bu değil).
- **Backend Test** — sağlık testi: örnek videoyu üretmezse ComfyUI backend bozuk demektir.

## Son değişiklikler

Tiled VAE opsiyonu, optimize last frame extraction, optimize MiniMeme, native color transfer node, **DaSiWa RTX Upscale & Refiner**, watermark overlay değişti, eksik bağlantı düzeltildi.

## Önemli notlar / bilinen sorunlar (notebook için)

- ⚠️ ComfyUI **"Nodes 2.0 beta"** ile KULLANMA — bozar.
- Bazı WAN 2.2 sürümleri **high+low** checkpoint kullanır; S2V tek checkpoint — açıklamaları oku, doğru checkpoint'i kullan.
- **ffmpeg** kurulu olmalı.
- ComfyUI + custom_nodes güncel olmalı; **pytorch 2.9+cu128** veya üzeri.
- VHS node bazı workflow'larda **webp av1** encoding kullanır; sürücü yoksa H265/H264'e geç.
- Model/clip/vae **dosya yollarının** sisteme (Linux/Windows) uyduğundan emin ol → Colab'da Linux yolları.
- `ComfyUI-DD-Translation` eklentisi node bağlantılarını bozabilir — kullanma.
- Eski sürümler yazarın GitHub repo'sunda.
