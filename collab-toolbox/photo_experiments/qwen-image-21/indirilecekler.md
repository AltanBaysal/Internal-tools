# Qwen Image 2.1 (normal + Turbo) — indirilecekler

Madde 482 (ilk bakış) ve 484 (karakter referansı, NSFW LoRA'ları, Noct Q). Comfy-Org'un dosyalarının
kaynağı resmî şablonlar: her yükleyici node'un kendi `models` listesi dosyanın adını, klasörünü ve
adresini veriyor. Şablonlar 20 ve 21 Ekim'de okundu, ve iki defter de bir workflow'u koymadan önce bu
listeyi diskteki dosyalarla yeniden karşılaştırıyor. Her şey baştan iner; doldurulacak seçenek yok.

## Workflow'lar — olduğu gibi, Workflows paneline

| Defter | Workflow | Kaynak |
|---|---|---|
| `normal.ipynb` | `image_qwen_image_2_1_t2i` | https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_qwen_image_2_1_t2i.json |
| `normal.ipynb` | `image_qwen_image_2_1_image_edit` | https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_qwen_image_2_1_image_edit.json |
| `normal.ipynb` | `NoctQ_V4_workflow` *(Noct Q'nun yazarının kendi workflow'u, 7.251 bayt)* | https://huggingface.co/Noctaluna/Noct-Q-Uncensored-Qwen-Image-2.1/blob/main/NoctQ_V4_workflow.json |
| `turbo.ipynb` | `image_qwen_image_2_1_turbo_t2i` | https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_qwen_image_2_1_turbo_t2i.json |
| `turbo.ipynb` | `image_qwen_image_2_1_turbo_image_edit` | https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_qwen_image_2_1_turbo_image_edit.json |

Custom node yok: bütün node'lar ComfyUI'nin kendinde
([PR #16400](https://github.com/Comfy-Org/ComfyUI/pull/16400)); Noct Q'nunki de yalnız çekirdek node'lar.

HF'teki boyutlar bayt olarak HF'in dosya listesinden ✅
([Comfy-Org](https://huggingface.co/api/models/Comfy-Org/Qwen-Image-2.1/tree/main?recursive=true),
[Noctaluna](https://huggingface.co/api/models/Noctaluna/Noct-Q-Uncensored-Qwen-Image-2.1/tree/main?recursive=true));
defterler her HF indirmesini bu sayıya tutuyor.

---

## 1) Defterin kendi modeli

| Defter | Klasör | Dosya | Bayt | Adres |
|---|---|---|---|---|
| `normal.ipynb` | `diffusion_models/` | `qwen_image_2.1_int8_convrot.safetensors` | 7.256.783.064 | https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/diffusion_models/qwen_image_2.1_int8_convrot.safetensors |
| `turbo.ipynb` | `diffusion_models/` | `qwen_image_2.1_turbo_int8_convrot.safetensors` | 7.256.787.829 | https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/diffusion_models/qwen_image_2.1_turbo_int8_convrot.safetensors |
| `turbo.ipynb` | `loras/` | `qwen_image_2.1_turbo_lora_avg_rank_178_bf16.safetensors` | 913.314.512 | https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/loras/qwen_image_2.1_turbo_lora_avg_rank_178_bf16.safetensors |

**Turbo LoRA'sı neden Turbo defterinde.** Noct Q V4'ün Turbo'su yok (aşağıda, 3). Comfy-Org'un
[README](https://huggingface.co/Comfy-Org/Qwen-Image-2.1/blob/main/README.md)'si: *"use either the full
Turbo model, or the Turbo LoRA extracted from the base model. Use 8 steps and cfg 1."* Noct Q Base'in bir
merge'ü, yani Turbo şablonunda Noct Q bu LoRA'yla denenir. **Bu ikiliyi hiçbir kaynak denemedi.**

## 2) İkisinde de — Hugging Face

| Klasör | Dosya | Bayt | Adres |
|---|---|---|---|
| `text_encoders/` | `qwen3vl_8b_int8_convrot.safetensors` | 9.350.798.360 | https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/text_encoders/qwen3vl_8b_int8_convrot.safetensors |
| `vae/` | `qwen_image_2.1_vae_bf16.safetensors` | 675.509.688 | https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/vae/qwen_image_2.1_vae_bf16.safetensors |
| `text_encoders/` | `qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors` | 9.471.072.252 | https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/text_encoders/qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors |
| `text_encoders/` | `qwen3.5_9b_qwen_image_2.1_pe_i2i.int8_convrot.safetensors` | 9.471.072.252 | https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/text_encoders/qwen3.5_9b_qwen_image_2.1_pe_i2i.int8_convrot.safetensors |
| `diffusion_models/` | `NoctQ_V4_int8_convrot.safetensors` | 7.256.784.368 | https://huggingface.co/Noctaluna/Noct-Q-Uncensored-Qwen-Image-2.1/resolve/main/NoctQ_V4_int8_convrot.safetensors |

### Prompt geliştiriciler neden iniyor

`pe_t2i` t2i şablonlarının, `pe_i2i` Edit şablonlarının. Araştırma onları gereksiz saymıştı: prompt'u
bizde Queen AI ve QueenAgent yazıyor, şablonlar da onları kapalı açıyor (`refine_prompt: false`).
Kapalıyken **yüklenmiyorlar** da: geliştiricinin çıktısı tembel bir anahtardan (`ComfySwitchNode`,
girdileri `lazy=True`) geçiyor, ve anahtar yalnız seçili dalı istiyor.

Ama ComfyUI bir işi çalıştırmadan önce çıktıya giden **her** node'un girdisini doğruluyor —
`execution.py`'nin `validate_inputs`'u bağlı node'lara iniyor ve tembel girdilere bakmıyor. Edit
şablonlarında da geliştiricinin yükleyicisi (`CLIPLoader`, node 477) etkin ve çıktıya bağlı. Seçili dosya
listede yoksa `value_not_in_list` dönüyor ve iş hiç başlamıyor. Yani dosyası olmayan şablon **Run**'da
durur. İnmelerinin tek sebebi şablonların dokunulmadan çalışması.

Dosyasız yolu da var, ama elle: büyük node'daki `PE_model` kutusunda listedeki herhangi bir metin
kodlayıcı seçilir (kapalıyken hiç yüklenmediği için hangisi olduğu fark etmez). Defter bunu yapmıyor:
şablona dokunmuyor.

## 3) Noct Q V4

[HF](https://huggingface.co/Noctaluna/Noct-Q-Uncensored-Qwen-Image-2.1) ·
[Civitai](https://civitai.com/models/2958896). Qwen 2.1'den türetilmiş sansürsüz bir *merge*, tek dosya;
metin kodlayıcısı ve VAE'si Comfy-Org'unkilerin aynısı (kartı). Yazara göre aynı dosyalarla Edit
şablonunda da çalışıyor. Ayarları 25 adım, `euler`, `simple`, **cfg 3** ve negatif prompt. V4 yalnız
**Base** olarak var: yazarın Turbo'su V3'te kaldı (*"V3.0 Turbo (Experimental)"*, 6 adım, yalnız
Civitai'de). Lisansı Qwen Research.

## 4) İkisinde de — Civitai, `loras/`

[Civitai API](https://civitai.com/api/v1/models?baseModels=Qwen%202.1&types=LORA&nsfw=true&sort=Most%20Downloaded)'sinden,
21 Ekim. Her birinin en son sürümünün taban modeli **"Qwen 2.1"**. Geniş NSFW olanlar seçildi; yalnız
tek bir bölgeye bakanlar, yüz değiştirme ve yalnız gerçekçilik LoRA'ları seçilmedi.

| Model | Sürüm | Dosya | Bayt *(API)* | Adres |
|---|---|---|---|---|
| [NSFW LORA \| Qwen Image 2.1](https://civitai.com/models/2958918) | v2.0 | `NSFW Qwen by TheseAlpacas V2.safetensors` | 79.744.352 | https://civitai.red/api/download/models/3357315 |
| [Qwen Image 2.1 - FemaledVaginus-NSFW](https://civitai.com/models/2986844) | v1.3b | `qwen2_1-femaledVaginus-nsfw-v1_3-fine_L22-31.safetensors` | 637.587.392 | https://civitai.red/api/download/models/3388157 |
| [NSFW UNLOCKED [LORA]](https://civitai.com/models/2063193) | Qwen2.1_V1 | `Qwen_2.1_Unlocked_V1.safetensors` | 50.390.941 | https://civitai.red/api/download/models/3392016 |
| [nsfw-posture-v3](https://civitai.com/models/2988215) | v1.0 | `nsfw-posture-v3.safetensors` | 83.943.880 | https://civitai.red/api/download/models/3388118 |

**Toplam: 851.666.565 B ≈ 0,85 GB.**

**Civitai girişi gerekiyor.** Dördünün de yazarı indirmeyi girişe bağlamış: girişsiz istek `401 "The
creator of this asset requires you to be logged in to download it"` dönüyor. Defter çerezi Colab
Secrets'tan **`CIVITAI_COOKIE`** adıyla okuyor (queen-editor'ün adı), `civitai.red`'e
`__Secure-civ-token` çereziyle gidiyor, önce her dosyanın ilk 1 KB'ını deniyor, sonra tek bağlantılı
`curl` ile indiriyor. Ayna yok: denemedeki dosyalar aynaya konmuyor (queen-editor, madde 327).

Dosyanın boyunu safetensors header'ı zaten kanıtlıyor; API'nin sayısı (`sizeKB`) yalnız boş disk
toplamında kullanılıyor.

Base'de eğitildiler; **resmî Turbo'da nasıl çalıştıkları bilinmiyor.** Turbo aynı mimari, yani
yüklenirler; etkisini anlatan bir kaynak yok.

## 5) Edit şablonlarının örnek resimleri — `ComfyUI/input/`

Şablonların `Load Image` node'ları bunları adıyla istiyor, ve şablonların *"Input Assets"* notu
adreslerini veriyor. Yoksa **Run** resmi yükleyemez ve durur.

| Defter | Dosya | Bayt | Adres |
|---|---|---|---|
| `normal.ipynb` | `portrait_model_denim.png` | 1.181.250 | https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/input/portrait_model_denim.png |
| `normal.ipynb` | `clothing_light_blue_denim_shirt.png` | 1.366.572 | https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/input/clothing_light_blue_denim_shirt.png |
| `turbo.ipynb` | `ballet_dancer_photography_minimalist_architecture.png` | 1.134.190 | https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/input/ballet_dancer_photography_minimalist_architecture.png |

## Toplam (model dosyaları)

- **`normal.ipynb`: 44.333.686.549 B ≈ 44,3 GB**
- **`turbo.ipynb`: 45.247.005.826 B ≈ 45,2 GB**

Workflow'lar ve resimler bunun dışında, ~3,9 MB. Boş disk kontrolü henüz yerinde olmayan her model
dosyasını toplar ve 5 GiB pay ister.

---

## 6) İnmeyenler

| Dosya | Boyut | Neden inmiyor |
|---|---|---|
| `qwen_image_2.1_bf16` / `qwen_image_2.1_turbo_bf16` | 14,23 GB | Tam hassasiyet; şablonlar `int8_convrot`'u yüklüyor. Şablonların "Model Links" notu bf16'yı da sayıyor, ama hiçbir yükleyici onu istemiyor |
| `qwen3vl_8b_bf16` / `qwen3vl_8b_w4a8` | 17,53 / 6,31 GB | Şablonlar int8'i yüklüyor |
| `qwen3.5_9b_…_pe_t2i_w4a8` / `…_pe_i2i_w4a8` | 6,72 GB | Şablonlar geliştiricilerin int8'ini yüklüyor |
| `qwen_image_2.1_fun_controlnet_union…` | 3,78 GB | ControlNet, şablonlarda yok |
| Noct Q'nun int4, fp8, bf16, fp16 dosyaları | 4,6 – 14,2 GB | Yalnız Civitai'de; HF'teki int8 ConvRot yetiyor |
| Lightning LoRA *(lightx2v, 4 adım)* | 67 MB | Resmî değil |

`fp8`, `nvfp4` ve GGUF sürümleri de inmiyor: fp8 ve fp4 A100'de (Ampere) yerel değil, GGUF için ayrı
bir custom node gerekiyor, ve resmî int8 sürümü varken hiçbiri gerekmiyor
*(482 araştırması, "Başka hassasiyetler")*.

---

## 7) Klasör düzeni

```
ComfyUI/
├── models/
│   ├── diffusion_models/   qwen_image_2.1_int8_convrot.safetensors        (normal)
│   │                       qwen_image_2.1_turbo_int8_convrot.safetensors  (turbo)
│   │                       NoctQ_V4_int8_convrot.safetensors
│   ├── text_encoders/      qwen3vl_8b_int8_convrot.safetensors
│   │                       qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors
│   │                       qwen3.5_9b_qwen_image_2.1_pe_i2i.int8_convrot.safetensors
│   ├── vae/                qwen_image_2.1_vae_bf16.safetensors
│   └── loras/              dört NSFW LoRA'sı
│                           qwen_image_2.1_turbo_lora_avg_rank_178_bf16.safetensors  (turbo)
├── input/                  Edit şablonlarının örnek resimleri
└── user/default/workflows/ image_qwen_image_2_1_t2i.json, image_qwen_image_2_1_image_edit.json,
                            NoctQ_V4_workflow.json                                  (normal)
                            image_qwen_image_2_1_turbo_t2i.json,
                            image_qwen_image_2_1_turbo_image_edit.json              (turbo)
```

Alt klasör yok: yükleyiciler dosyaları kendi klasörlerinin kökünde arıyor.
