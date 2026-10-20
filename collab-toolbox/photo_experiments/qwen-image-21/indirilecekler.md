# Qwen Image 2.1 (normal + Turbo) — indirilecekler

Kaynak, Comfy-Org'un iki resmî şablonu: her yükleyici node'un kendi `models` listesi dosyanın adını,
klasörünü ve adresini veriyor. Şablonlar 20 Ekim'de okundu, ve iki defter de şablonu koymadan önce
bu listeyi diskteki dosyalarla yeniden karşılaştırıyor.

| Şablon | Kaynak |
|---|---|
| `image_qwen_image_2_1_t2i` | https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_qwen_image_2_1_t2i.json |
| `image_qwen_image_2_1_turbo_t2i` | https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_qwen_image_2_1_turbo_t2i.json |

Boyutlar bayt olarak HF'in dosya listesinden ✅
([Comfy-Org](https://huggingface.co/api/models/Comfy-Org/Qwen-Image-2.1/tree/main?recursive=true));
defterler her indirmeyi bu sayıya tutuyor.

Custom node yok: şablonların bütün node'ları ComfyUI'nin kendinde
([PR #16400](https://github.com/Comfy-Org/ComfyUI/pull/16400)).

---

## 1) Defterin kendi modeli

| Defter | Klasör | Dosya | Bayt | Adres |
|---|---|---|---|---|
| `normal.ipynb` | `diffusion_models/` | `qwen_image_2.1_int8_convrot.safetensors` | 7.256.783.064 | https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/diffusion_models/qwen_image_2.1_int8_convrot.safetensors |
| `turbo.ipynb` | `diffusion_models/` | `qwen_image_2.1_turbo_int8_convrot.safetensors` | 7.256.787.829 | https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/diffusion_models/qwen_image_2.1_turbo_int8_convrot.safetensors |

## 2) İkisinde de

| Klasör | Dosya | Bayt | Adres |
|---|---|---|---|
| `text_encoders/` | `qwen3vl_8b_int8_convrot.safetensors` | 9.350.798.360 | https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/text_encoders/qwen3vl_8b_int8_convrot.safetensors |
| `vae/` | `qwen_image_2.1_vae_bf16.safetensors` | 675.509.688 | https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/vae/qwen_image_2.1_vae_bf16.safetensors |
| `text_encoders/` | `qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors` | 9.471.072.252 | https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/text_encoders/qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors |

**Defter başına toplam: 26.754.163.364 B ≈ 26,8 GB** *(Turbo'nunki 4.765 bayt fazla)*.

### Prompt geliştirici neden iniyor

Araştırma onu gereksiz saymıştı: prompt'u bizde Queen AI ve QueenAgent yazıyor, şablon da onu kapalı
açıyor (`refine_prompt: false`). Kapalıyken **yüklenmiyor** da: geliştiricinin çıktısı tembel bir
anahtardan (`ComfySwitchNode`, girdileri `lazy=True`) geçiyor, ve anahtar yalnız seçili dalı istiyor.

Ama ComfyUI bir işi çalıştırmadan önce çıktıya giden **her** node'un girdisini doğruluyor —
`execution.py`'nin `validate_inputs`'u bağlı node'lara iniyor ve tembel girdilere bakmıyor. Seçili
dosya listede yoksa `value_not_in_list` dönüyor ve iş hiç başlamıyor. Yani dosyası olmayan şablon
**Run**'da durur. İnmesinin tek sebebi şablonun dokunulmadan çalışması.

Dosyasız yolu da var, ama elle: büyük node'daki `PE_model` kutusunda listedeki herhangi bir metin
kodlayıcı seçilir (kapalıyken hiç yüklenmediği için hangisi olduğu fark etmez). Defter bunu yapmıyor:
şablona dokunmuyor.

---

## 3) İnmeyenler

| Dosya | Boyut | Neden inmiyor |
|---|---|---|
| `qwen_image_2.1_bf16` / `qwen_image_2.1_turbo_bf16` | 14,23 GB | Tam hassasiyet; şablonlar `int8_convrot`'u yüklüyor. Turbo şablonunun "Model Links" notu bf16'yı da sayıyor, ama hiçbir yükleyici onu istemiyor |
| `qwen3vl_8b_bf16` / `qwen3vl_8b_w4a8` | 17,53 / 6,31 GB | Şablonlar int8'i yüklüyor |
| `qwen_image_2.1_turbo_lora_avg_rank_178_bf16` | 0,91 GB | Tam modelden çıkarılmış Turbo LoRA'sı; resmî Turbo şablonu onun yerine ayrı Turbo modelini yüklüyor |
| `qwen3.5_9b_qwen_image_2.1_pe_i2i…` | 9,47 GB | Düzenleme (i2i) şablonlarının geliştiricisi |
| `qwen_image_2.1_fun_controlnet_union…` | 3,78 GB | ControlNet, şablonlarda yok |
| Lightning LoRA *(lightx2v, 4 adım)* | 67 MB | Resmî değil; ilk bakış resmî iki şablonla sınırlı |

`fp8`, `nvfp4` ve GGUF sürümleri de inmiyor: fp8 ve fp4 A100'de (Ampere) yerel değil, GGUF için ayrı
bir custom node gerekiyor, ve resmî int8 sürümü varken hiçbiri gerekmiyor
*(araştırma, "Başka hassasiyetler")*.

---

## 4) Klasör düzeni

```
ComfyUI/
├── models/
│   ├── diffusion_models/   qwen_image_2.1_int8_convrot.safetensors        (normal)
│   │                       qwen_image_2.1_turbo_int8_convrot.safetensors  (turbo)
│   ├── text_encoders/      qwen3vl_8b_int8_convrot.safetensors
│   │                       qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors
│   └── vae/                qwen_image_2.1_vae_bf16.safetensors
└── user/default/workflows/ image_qwen_image_2_1_t2i.json        (normal, resmî şablon olduğu gibi)
                            image_qwen_image_2_1_turbo_t2i.json  (turbo, resmî şablon olduğu gibi)
```

Alt klasör yok: şablonların yükleyicileri dosyaları kendi klasörlerinin kökünde arıyor.
