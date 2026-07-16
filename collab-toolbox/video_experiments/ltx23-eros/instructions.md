# LTX 2.3 I2V — "Eros" (MrXin) — Talimatlar

- **Kaynak:** https://civitai.red/models/2488266/mrxin-ltx-23-i2v-eros-12gb-vram-and-32gb-ram-workflow
- **Sürüm:** EROS V6 — Güncelleme: 2026-05-21
- **Model ailesi:** LTX-Video 2.3 (WAN dışı), lisans: LTXV2
- **Workflow arşivi:** 27.55 KB (Civitai'den indirilip bu klasöre `workflow.json` olarak konacak)

> Kaynak sayfadan birebir aktarılmış referans. Notebook'un indirme/kurulum hücreleri buna göre doldurulacak. Kesin dosya adları workflow JSON gelince doğrulanacak (aşağıda "Required Models" ile "Folder Structure" arasında küçük ad farkları var — not düşüldü).

## Ne yapar / öne çıkanlar

- Dual-pass (First Pass + Final Pass) LTX 2.3 I2V; güçlü ve tutarlı hareket.
- 24 FPS video + senkron ses (audio).
- Gömülü Video Editor: RTX Super Resolution + `nmkdSiaxCX` upscaler + RIFE (48/60 FPS).
- Model değişimi: **10Eros V1 FP8** ↔ **Distilled 22B**.
- V6: First/Final pass'te **LTX2 NAG** (Negative Attention Guidance), VAELoader KJ node'ları, esnek sigma sistemi (Manual 8 step / LTXVScheduler+Sigmoid 12 step), `LTXVImgToVideoInplaceKJ` ile görsel conditioning.
- Hedef donanım: 16GB VRAM + 32GB RAM (12GB kartlar için OOM ayarları var).

## Gerekli modeller + hedef klasör

Kaynaktaki **Folder Structure** (notebook indirmeleri bunu temel alır):

```
ComfyUI/models/
├── diffusion_models/
│   ├── ltx2310eros_beta.safetensors
│   └── ltx-2.3-22b-distilled_transformer_only_fp8_input_scaled_v3.safetensors
├── text_encoders/
│   └── gemma_3_12B_it_fp8_e4m3fn.safetensors
├── clip/
│   └── ltx-2.3_text_projection_bf16.safetensors
├── VAE/
│   ├── LTX23_video_vae_bf16.safetensors
│   ├── LTX23_audio_vae_bf16.safetensors
│   └── taeltx2_3.safetensors          # preview VAE
├── latent_upscale_models/
│   └── ltx-2.3-spatial-upscaler-x2-1.1.safetensors
├── upscale_models/
│   └── nmkdSiaxCX_200k.safetensors
└── Lora/
    ├── ltx-2.3-22b-distilled-lora-1.1_fro90_ceil72_condsafe.safetensors
    └── ltx-2.3-22b-distilled-lora-384-1.1.safetensors
```

**Not — "Required Models" listesindeki ad farkları** (JSON gelince netleşecek):
- Ana checkpoint: "10Eros V1 FP8 → `ltx2310eros_v1_FP8.safetensors`" yazıyor ama folder tree'de `ltx2310eros_beta.safetensors`.
- Spatial upscaler: required'da `x2-1.0`, tree'de `x2-1.1`.
- Distilled LoRA'lar (First & Second Pass) required listede adsız; tree'deki iki LoRA bunlar.

## Custom node'lar

- `ComfyUI-KJNodes`
- `rgthree-comfy`
- `ComfyUI-easy-use`
- `ComfyUI-mxToolkit`
- `ComfyUI-VideoHelperSuite`
- `ComfyUI-LTXVideo`
- `controlaltai-nodes`
- `comfyui_nvidia_rtx_nodes`
- `GACLove/ComfyUI-VFI` (RIFE için)
- `comfyui_memory_cleanup` + `comfyui-impact-pack`

## Çalıştırma flag'leri (low VRAM)

Kaynak Windows `.bat` için şunu öneriyor:

```
main.py --lowvram --reserve-vram 6 --preview-method none --disable-xformers --disable-smart-memory
```

> **Colab notu:** Bu flag'ler 12GB kartlar için. Colab Pro A100 (40GB) üzerinde muhtemelen gerekmez; ilk denemede sade çalıştırıp OOM olursa `--lowvram`/`--reserve-vram` eklenir. Sayfadaki Windows swap-file (virtual memory) adımı Colab'da geçersiz.

## Kullanım ipuçları

- En iyi sonuç için **10Eros V1 FP8** + önerilen trigger word'ler.
- OOM/yüz bozulması olursa: ComfyUI güncelle → Manager → "Install Missing Custom Nodes" → restart; sonra düşük VRAM flag'leri.
- İlk test: **Longer Side 1024**, **Video Length 20s**.

## Disclaimer

Kaynak: yalnızca eğlence/sanatsal/yaratıcı amaç; yasa dışı/zararlı/rıza dışı kullanım yok.
