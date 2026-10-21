# Krea 2 (Turbo + RAW) — indirilecekler

Madde 485. Comfy-Org'un dosyalarının kaynağı resmî şablonlar: her yükleyici node'un kendi `models`
listesi dosyanın adını, klasörünü ve adresini veriyor. Şablonlar 21 Ekim'de okundu, ve Turbo defteri bir
workflow'u koymadan önce bu listeyi diskteki dosyalarla yeniden karşılaştırıyor. Her şey baştan iner;
doldurulacak seçenek yok.

HF'teki boyutlar bayt olarak HF'in dosya listesinden
([Comfy-Org/Krea-2](https://huggingface.co/api/models/Comfy-Org/Krea-2/tree/main?recursive=true),
[Vaelico/Wulver](https://huggingface.co/api/models/Vaelico/Wulver/tree/main?recursive=true); ikisi de
açık); defterler her HF indirmesini bu sayıya tutuyor.

## Workflow'lar — olduğu gibi, Workflows paneline

| Defter | Workflow | Bayt | Kaynak |
|---|---|---|---|
| `turbo.ipynb` | `image_krea2_turbo_t2i_int8` | 60.684 | https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_krea2_turbo_t2i_int8.json |
| `turbo.ipynb` | `image_krea2_turbo_int8_image_style_reference` | 62.999 | https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_krea2_turbo_int8_image_style_reference.json |

İkisinin `models` listesi: `krea2_turbo_int8_convrot`, `qwen3vl_4b_fp8_scaled`, `qwen_image_vae`, ve
t2i'de `krea2_darkbrush`, stil referansında `krea2_style_reference`.

**RAW defterinde şablon yok.** Krea'nın üç şablonu da Turbo için; resmî RAW şablonu yok
([docs.comfy.org](https://docs.comfy.org/tutorials/image/krea/krea-2)). Turbo şablonlarının `models`
listesi RAW defterinde inmeyen Turbo DiT'ini istiyor; şablon ComfyUI'nin kendi **Templates** listesinden
açılır ve `unet_name` RAW'a çevrilir.

Custom node yok: bütün node'lar ComfyUI'nin kendinde (`CLIPLoader`'ın `krea2` türü, `ResolutionSelector`,
`TextGenerate`, `TextEncodeQwenImageEditPlus`, …). Stil referansı LoRA'sının kartı ostris'in custom
node'unu gösteriyor; resmî şablon aynı işi çekirdek node'larla yapıyor, o yüzden inmiyor.

---

## 1) Defterin kendi modeli — Hugging Face

| Defter | Klasör | Dosya | Bayt | Adres |
|---|---|---|---|---|
| `turbo.ipynb` | `diffusion_models/` | `krea2_turbo_int8_convrot.safetensors` | 13.492.686.496 | https://huggingface.co/Comfy-Org/Krea-2/resolve/main/diffusion_models/krea2_turbo_int8_convrot.safetensors |
| `turbo.ipynb` | `diffusion_models/` | `Wulver_v0.5_fp8_e4m3fn.safetensors` | 12.821.599.836 | https://huggingface.co/Vaelico/Wulver/resolve/main/Wulver_v0.5_fp8_e4m3fn.safetensors |
| `raw.ipynb` | `diffusion_models/` | `krea2_raw_int8_convrot.safetensors` | 13.492.686.496 | https://huggingface.co/Comfy-Org/Krea-2/resolve/main/diffusion_models/krea2_raw_int8_convrot.safetensors |
| `raw.ipynb` | `loras/` | `krea2_turbo_lora_rank_64_bf16.safetensors` | 469.423.778 | https://huggingface.co/Comfy-Org/Krea-2/resolve/main/loras/krea2_turbo_lora_rank_64_bf16.safetensors |
| `raw.ipynb` | `diffusion_models/` | `Wulver_v0.5_non_turbo_bf16.safetensors` | 25.640.191.128 | https://huggingface.co/Vaelico/Wulver/resolve/main/Wulver_v0.5_non_turbo_bf16.safetensors |

**Krea'nın DiT'i neden int8.** fp8 ve fp4 A100'de (Ampere) yerel değil. Resmî int8 şablonlar Comfy-Org'un
int8 dosyalarını yüklüyor, yani ComfyUI'nin niceleme işaretini taşımaları beklenir; bunu görmedik. RAW
defterinin özeti RAW int8'inin header'ına bakar ve işaret yoksa uyarır.

**Turbo LoRA'sı.** Comfy-Org'un README'si ne işe yaradığını yazmıyor. Krea: RAW damıtılmamış temel model,
52 adım, cfg 3,5, *"not recommended for inference"* — ince ayar ve LoRA eğitimi için
([krea/Krea-2-Raw](https://huggingface.co/krea/Krea-2-Raw)). Wulver'ın README'si, RAW'ın bir ince ayarı
için, bu LoRA'yı güç 1,0 / 8 adım / cfg 1 ya da 0,6 / 14 adım / cfg 1 ile kullanıyor; çıplak RAW'da
denenmemiş.

## 2) İkisinde de — Hugging Face

| Klasör | Dosya | Bayt | Adres |
|---|---|---|---|
| `text_encoders/` | `qwen3vl_4b_fp8_scaled.safetensors` | 5.242.467.968 | https://huggingface.co/Comfy-Org/Krea-2/resolve/main/text_encoders/qwen3vl_4b_fp8_scaled.safetensors |
| `vae/` | `qwen_image_vae.safetensors` | 253.806.246 | https://huggingface.co/Comfy-Org/Krea-2/resolve/main/vae/qwen_image_vae.safetensors |
| `loras/` | `krea2_darkbrush`, `krea2_dotmatrix`, `krea2_kidsdrawing`, `krea2_neondrip`, `krea2_rainywindow`, `krea2_retroanime`, `krea2_softwatercolor`, `krea2_sunsetblur`, `krea2_vintagetarot` (`.safetensors`) | 9 × 469.291.992 | https://huggingface.co/Comfy-Org/Krea-2/resolve/main/loras/krea2_<ad>.safetensors |
| `loras/` | `krea2_style_reference.safetensors` | 457.111.760 | https://huggingface.co/Comfy-Org/Krea-2/resolve/main/loras/krea2_style_reference.safetensors |

**Metin kodlayıcı neden fp8.** İki int8 şablon da `qwen3vl_4b_fp8_scaled`'i istiyor, `int8_convrot`'u
değil; şablon dokunulmadan çalışsın diye o iner. ComfyUI fp8 ağırlıkları A100'de bf16'ya çevirip
hesaplar: doğru, yerel fp8'den yavaş.

**Stil referansı** ([ostris/krea2_turbo_style_reference](https://huggingface.co/ostris/krea2_turbo_style_reference)):
Turbo'yu bir referans resmin tarzında koşturur; bir ya da iki resim, tetik yok. Kendi şablonu var,
t2i'de resim girişi yok.

## 3) Wulver

[Civitai 2881657](https://civitai.com/models/2881657), v0.5 (3361227), tabanı "Krea 2 Turbo" ·
[HF](https://huggingface.co/Vaelico/Wulver). Yazara göre *"Full fine-tune of Krea 2 Raw"*; Turbo
dosyalarına resmî Turbo LoRA'sı 1,0 güçle katılmış. Konusu anthro / furry, anime / kemono. Metin
kodlayıcı ve VAE Krea'nınkiler, *"stock ComfyUI loaders"*.

Civitai'deki dosyalar, HF'teki karşılıkları SHA256'yla eşlendi:

| Civitai dosyası | Ne | HF'teki adı |
|---|---|---|
| 3249021 *(birincil)*, 12,52 GB | fp8 e4m3fn, Turbo — yazarın ComfyUI için önerdiği | `Wulver_v0.5_fp8_e4m3fn` ← **turbo** |
| 3249141, 13,18 GB | int8 ConvRot, Turbo — yazara göre *"forge-neo and other int8 runtimes"* | `Wulver_v0.5_int8_convrot` |
| 3249022, 13,18 GB | düz int8, açıklaması yok | `Wulver_v0.5_int8` (yalnız SHA listesinde) |
| 3249389, 7,50 GB (Civitai "int8" diyor) | W4A8 ConvRot; ComfyUI ≥ 0.31 ve PyTorch cu130 ister | `Wulver_v0.5_w4a8-convrot` |
| 3249146 | GGUF; custom node ister | yalnız Civitai |
| 3249012 `wulverKrea2_v05.json`, 2.974 B | config değil, yazarın ComfyUI workflow'u | `Wulver_workflow.json` |
| — | Non-Turbo, int8 ConvRot, 13,49 GB | `Wulver_v0.5_non_turbo_int8-convrot` |
| — | Non-Turbo, bf16, 25,64 GB | `Wulver_v0.5_non_turbo_bf16` ← **raw** |

**Turbo'da fp8, HF'ten:** yazarın ComfyUI için önerdiği dosya; ComfyUI int8'i ancak kendi niceleme
işaretinden tanıdığı için başka araçlara yapılmış bir int8'i sessizce yanlış okuyabilir. HF'teki dosya
Civitai'nin birincil dosyasının aynısı, ve çerez gerekmiyor. **RAW'da Non-Turbo bf16:** Non-Turbo'nun
fp8'i yok; int8 ConvRot'u yazarı ComfyUI dışındaki araçlara veriyor. bf16'yı ComfyUI kesin doğru okur;
bedeli iki kat disk. `.json` inmiyor: yalnız resmî şablonlar.

## 4) Civitai — çerezle

[Civitai API](https://civitai.com/api/v1/models/2801881)'sinden, 21 Ekim. Hepsinin taban modeli **"Krea
2"**. Bayt sayıları API'nin `sizeKB × 1024`'ü.

| Defter | Klasör | Model · sürüm | Dosya | Bayt *(API)* | Adres |
|---|---|---|---|---|---|
| ikisi | `loras/` | [SNOFS](https://civitai.com/models/1972981) · Krea 2 v1.5 (3390681) | `snofs_krea_v1_5.safetensors` | 1.562.410.216 | https://civitai.red/api/download/models/3390681 |
| ikisi | `loras/` | [krea2 sex](https://civitai.com/models/2801881) · carry (3170121) | `krea2 standing and carry.safetensors` | 228.587.744 | https://civitai.red/api/download/models/3170121 |
| ikisi | `loras/` | krea2 sex · dog (3158793) | `krea doggy.safetensors` | 228.587.720 | https://civitai.red/api/download/models/3158793 |
| ikisi | `loras/` | krea2 sex · Mis (3169965) | `krea missionary.safetensors` | 228.587.728 | https://civitai.red/api/download/models/3169965 |
| ikisi | `loras/` | krea2 sex · CG (3158775) | `krea cowgirl.safetensors` | 228.587.720 | https://civitai.red/api/download/models/3158775 |
| ikisi | `loras/` | krea2 sex · spo (3169634) | `kea2 spooning.safetensors` | 228.587.720 | https://civitai.red/api/download/models/3169634 |
| ikisi | `loras/` | krea2 sex · BJ (3158893) | `kreablowjob.safetensors` | 228.587.720 | https://civitai.red/api/download/models/3158893 |
| turbo | `diffusion_models/` | [Sick Ollie](https://civitai.com/models/2676616) · Krea2 (3154408), fp8, dosya 3035266 | `sickOllie_krea2_3035266.safetensors` | 12.821.587.640 | https://civitai.red/api/download/models/3154408?fileId=3035266 |
| turbo | `diffusion_models/` | [Moody Krea2 Mix](https://civitai.com/models/2731187) · V8.0 BF16 & FP8 (3327123), fp8_scaled, dosya 3213091 | `moodyKrea2MixUncensoredV8FREEV8_v80BF16FP8_3213091.safetensors` | 13.141.769.512 | https://civitai.red/api/download/models/3327123?fileId=3213091 |

**SNOFS:** en yeni Krea 2 sürümü v1.5; tek dosya, bf16. Yazar: etiketle değil düzyazıyla eğitilmiş.

**krea2 sex:** 34 sürümün her biri bir pozisyon LoRA'sı. Genel olanlardan indirme sayısı en yüksek altı
alındı (carry 5.352, dog 4.652, Mis 4.485, CG 4.475, spo 4.252, BJ 4.100). Daha yeni BJ2 (3401693) ve
SP2 (3398592) alınmadı. Tetik kelimeleri her sürümün sayfasında (`instructions.md`'de bağlantılar).

**Checkpoint'ler `diffusion_models/`'a:** yalnız DiT taşıyorlar — bf16'ları 25,6 – 26,3 GB, Krea'nın
bf16 DiT'i (26,28 GB) kadar; metin kodlayıcı ve VAE ayrı. `Load Diffusion Model` onları orada arar. İkisi de yalnız
Turbo defterinde: yazarları onları Turbo gibi koşuyor (aşağıda); RAW'dan mı Turbo'dan mı türedikleri
yazılı değil.

- **Sick Ollie:** sürümde bf16 (birincil), int8, nf4, mxfp8 ve fp8 var; yazarın verdiği fp8 alındı
  (Civitai türü "Diffusion Model"). Ayarları: Euler, Beta, cfg 1, 9 adım, en iyi 1440 × 1920.
- **Moody V8.0:** V8.0'ın 3327244 girdisinde int4, nvfp4 ve int8 var; fp8'ler kardeş girdisi
  *"V8.0 BF16 & FP8"*'de (3327123), o da int4, nvfp4 ve int8'i taşıyor, ayrıca `fp8` (birincil,
  13.782.043.152 B), **`fp8_scaled`** (alınan) ve bf16. fp8_scaled'in boyu Comfy-Org'un
  `krea2_turbo_fp8_scaled`'inden (13.141.730.784 B) yalnız 38 KB farklı, yani büyük olasılıkla
  ComfyUI'nin okuduğu aynı biçim; birincil `fp8`'in biçimi yazılı değil. Ayarları yazarın V6 notunda:
  Euler A, Beta, 8 adım (12'ye kadar); V8 için ayrıca yazılı değil. V8 gerçekçi fotoğrafa yönelik
  (*"RAW-style photography, skin texture"*); öteki Civitai dosyalarının tarzı doğrulanmadı.

**Civitai girişi gerekiyor.** Defter çerezi Colab Secrets'tan **`CIVITAI_COOKIE`** adıyla okuyor
(queen-editor'ün adı), `civitai.red`'e `__Secure-civ-token` çereziyle gidiyor, önce her sürümün çıplak
adresinden ilk 1 KB'ı deniyor (seçicili adres probe'da 401 veriyor), sonra tek bağlantılı `curl` ile,
gerekirse `?fileId=` ile indiriyor. Ayna yok: denemedeki dosyalar aynaya konmuyor (queen-editor, madde
327).

Dosyanın boyunu safetensors header'ı zaten kanıtlıyor. `fileId` ile seçilen iki checkpoint ayrıca API'nin
bayt sayısına tutuluyor: gelenin istenen dosya olduğunu, sürümün birincil dosyası olmadığını o gösterir.
Ötekilerde API'nin sayısı (`sizeKB`) yalnız boş disk toplamında. Civitai indirmesinin toplam süre sınırı
yok: hız 5 dakika boyunca 1 MiB/s'in altında kalırsa durur (üst sınır 4 saat).

## 5) Stil referansı şablonunun örnek resmi — `ComfyUI/input/`, ikisinde de

| Dosya | Bayt | Adres |
|---|---|---|
| `krea2_reference_image.png` | 1.497.458 | https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/input/krea2_reference_image.png |

Şablonun `Load Image` node'u onu adıyla istiyor; yoksa **Run** resmi yükleyemez ve durur.

## Toplam (model dosyaları)

- **`turbo.ipynb`: 65.388.593.954 B ≈ 65,4 GB (60,9 GiB)**
- **`raw.ipynb`: 52.713.251.872 B ≈ 52,7 GB (49,1 GiB)**

Workflow'lar ve resim bunun dışında (turbo 1.621.141 B, raw 1.497.458 B). Boş disk kontrolü henüz
yerinde olmayan her model dosyasını toplar ve 5 GiB pay ister.

---

## 6) İnmeyenler

| Dosya | Boyut | Neden inmiyor |
|---|---|---|
| `krea2_turbo_bf16` / `krea2_raw_bf16` | 26,28 GB | Tam hassasiyet; int8 yetiyor |
| `krea2_turbo_fp8_scaled` / `krea2_raw_fp8_scaled`, `krea2_turbo_mxfp8`, `krea2_turbo_nvfp4` | 7,7 – 13,5 GB | fp8 ve fp4 A100'de yerel değil |
| `image_krea2_turbo_t2i` şablonu | 59.709 B | Aynı grafik, fp8 DiT'le; int8 kardeşi iniyor |
| `qwen3vl_4b_int8_convrot` / `qwen3vl_4b_bf16` | 4,86 / 8,88 GB | Şablonlar fp8_scaled'i istiyor |
| Wulver'ın int8 ConvRot (Turbo), düz int8, W4A8, GGUF, `.json`'u, Non-Turbo int8 ConvRot | 7,7 – 13,5 GB | 3. bölüm |
| Sick Ollie'nin bf16, int8, nf4, mxfp8'i | 7,7 – 25,6 GB | Yazarın fp8'i alındı |
| Moody V8.0'ın int8, int4, nvfp4, birincil `fp8`, bf16'sı | 7,5 – 26,3 GB | fp8_scaled alındı |
| ostris'in `ComfyUI-Krea2-Ostris-Edit` custom node'u | — | Resmî şablon çekirdek node'larla yapıyor |

---

## 7) Klasör düzeni

```
ComfyUI/
├── models/
│   ├── diffusion_models/   krea2_turbo_int8_convrot.safetensors              (turbo)
│   │                       Wulver_v0.5_fp8_e4m3fn.safetensors                (turbo)
│   │                       sickOllie_krea2_3035266.safetensors               (turbo)
│   │                       moodyKrea2MixUncensoredV8FREEV8_v80BF16FP8_3213091.safetensors  (turbo)
│   │                       krea2_raw_int8_convrot.safetensors                (raw)
│   │                       Wulver_v0.5_non_turbo_bf16.safetensors            (raw)
│   ├── text_encoders/      qwen3vl_4b_fp8_scaled.safetensors
│   ├── vae/                qwen_image_vae.safetensors
│   └── loras/              dokuz tarz LoRA'sı, krea2_style_reference, SNOFS, altı pozisyon LoRA'sı
│                           krea2_turbo_lora_rank_64_bf16.safetensors         (raw)
├── input/                  krea2_reference_image.png
└── user/default/workflows/ image_krea2_turbo_t2i_int8.json,
                            image_krea2_turbo_int8_image_style_reference.json (turbo)
```

Alt klasör yok: yükleyiciler dosyaları kendi klasörlerinin kökünde arıyor.
