# Femboy ve futa LoRA'ları — indirilecekler

Madde 501 · v11-4. Defter Queen Editor'ün Nova 3DCG ve DaSiWa'da kullandığı fotoğraf grafiğini kurar ve
altı aday LoRA'yı — üç femboy, üç futa — onun üstünde dener: gereken her şey Queen Editor'ün indirdiğinin
bir alt kümesi, artı adaylar. Her şey baştan iner; doldurulacak seçenek yok.

Civitai'deki boyutlar API'nin `sizeKB × 1024`'ü (27 Ekim). Dosyanın boyunu safetensors header'ı zaten
kanıtlıyor; API'nin sayısı yalnız boş disk toplamında.

## Workflow'lar — defter kurar, Workflows paneline

Aday başına bir tane, adı adayın kaydedilen dosya adı: `femboysXL_v1`, `femboy_illustrious_v1_3`,
`femboy_new_tos_il`, `futa_flaccid_v3`, `futa_on_female_il_v2`, `futa_on_male_il_v2`. İki grafikten
kurulur; ikisi de bu reponun `main`'inden, GitHub'dan okunur — Secrets'ta `GITHUB_TOKEN` varsa GitHub'ın
API'sinden, yoksa açık `raw.githubusercontent.com` adresinden (repo bugün açık):

- [`queen-editor/assets/workflow_api.json`](../../../queen-editor/assets/workflow_api.json) — Queen
  Editor'ün fotoğraf grafiği, API biçiminde.
- [`collab-toolbox/photo_generator/nova-3dcg/workflow_manual.json`](../../photo_generator/nova-3dcg/workflow_manual.json)
  — aynı grafiğin arayüz biçimi, nova-3dcg denemesinden; Queen Editor'ünki bundan export edildi.

Defter önce ikisinin aynı şeyi çizdiğini karşılaştırır, sonra arayüz grafiğine Queen Editor'ün bir
kareye yazdıklarını yazar (`instructions.md` ve defterin 5. bölümü). Repo bir gün kapanırsa açık adres
404 döner ve hücre GitHub'ın cevabıyla durur; `GITHUB_TOKEN` eklenince API'den iner.

## Custom node'lar — 8

Arayüz grafiğinin node'larının geldiği paketler: rgthree-comfy (`main` dalı), ComfyUI-Impact-Pack,
ComfyUI-Impact-Subpack, ComfyUI-Easy-Use, ComfyUI-ppm (`CLIPTextEncodeBREAK`); ve yalnız grafiğin kapalı
dallarında duranlar için ComfyUI-Custom-Scripts, ComfyUI_UltimateSDUpscale, ComfyUI-KJNodes. Queen
Editor'ün on paketinden ComfyUI-Manager ve ComfyUI-DaSiWa-Nodes kurulmuyor.

---

## 1) Queen Editor'ün checkpoint'leri — Civitai, `checkpoints/`

Queen Editor'ün indirdiği sürümler, aynı adlarla (`queeneditor.ipynb`, `PHOTO_CHECKPOINTS`).

| Model · sürüm | Dosya | Bayt *(API)* | Adres |
|---|---|---|---|
| [Nova 3DCG XL](https://civitai.com/models/715287) · IL v9.0 (2744564) | `nova3DCGXL_ilV90.safetensors` | 6.938.530.484 | https://civitai.red/api/download/models/2744564 |
| [DaSiWa Illustrious](https://civitai.com/models/1034922) · EpitaphEcstasy (3012006) | `DasiwaIllustriousAnime_epitaphecstasy.safetensors` | 6.938.115.222 | https://civitai.red/api/download/models/3012006 |

## 2) Adaylar — Civitai, `loras/`

Kendi adlarıyla kaydedilir: Civitai'deki adları (`last-000008`, `Femboy`, `Futa_on_male-000055`, …)
yükleyicinin listesinde ayırt edilmiyor ya da grubunu söylemiyor.

| Grup | Model · sürüm | Kaydedilen ad *(Civitai'deki)* | Bayt *(API)* | Adres |
|---|---|---|---|---|
| femboy | [femboysXL](https://civitai.com/models/289006) · v1.0 (324974) | `femboysXL_v1.safetensors` *(last-000008)* | 489.722.956 | https://civitai.red/api/download/models/324974 |
| femboy | [Femboy illustrious](https://civitai.com/models/1738161) · v1.3 (2693790) | `femboy_illustrious_v1_3.safetensors` *(Femboy)* | 228.456.460 | https://civitai.red/api/download/models/2693790 |
| femboy | [Femboy, Sissy, Feminine Male](https://civitai.com/models/1922853) · IL (2176350) | `femboy_new_tos_il.safetensors` *(Femboy_new_ToS_tags_PonyIL)* | 228.476.020 | https://civitai.red/api/download/models/2176350 |
| futa | [Flaccid Futa](https://civitai.com/models/2063309) · v3.0 IL (2698395) | `futa_flaccid_v3.safetensors` *(Flaccid_Futa_v3.0)* | 228.460.108 | https://civitai.red/api/download/models/2698395 |
| futa | [Futa on Female](https://civitai.com/models/1107758) · Illustrious v2 (1457484) | `futa_on_female_il_v2.safetensors` *(Futa_on_Female_illustrious-000053)* | 228.479.108 | https://civitai.red/api/download/models/1457484 |
| futa | [Futa on Male / Futadom 2](https://civitai.com/models/891832) · Illustrious v2 (2066157) | `futa_on_male_il_v2.safetensors` *(Futa_on_male-000055)* | 228.482.300 | https://civitai.red/api/download/models/2066157 |

**femboysXL** dosyasının header'ı: `ss_sd_model_name = cagliostrolab/animagine-xl-3.0`, 92 dim, 8.
epoch; açıklamalarının etiket sayımı boş. Girişsiz iniyor. Öteki beşi ve DaSiWa girişe bağlı (girişsiz
istek `401 "The creator of this asset requires you to be logged in to download it"`), yani header'ları
ancak defterde, inince okunuyor.

**Civitai girişi gerekiyor.** Defter çerezi Colab Secrets'tan **`CIVITAI_COOKIE`** adıyla okuyor
(queen-editor'ün adı), `civitai.red`'e `__Secure-civ-token` çereziyle gidiyor, önce her dosyanın ilk
1 KB'ını deniyor, sonra tek bağlantılı `curl` ile indiriyor. Ayna yok: denemedeki dosyalar aynaya
konmuyor (queen-editor, madde 327).

## 3) Yüz düzeltmesi — grafiğin FaceDetailer'ı açık

| Klasör | Dosya | Boyut | Adres |
|---|---|---|---|
| `ultralytics/bbox/` | `face_yolov9c.pt` | 51.648.019 B *(HF listesi)* | https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov9c.pt |
| `sams/` | `sam_vit_b_01ec64.pth` | ~375 MB | https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth |

Queen Editor'ün indirdiği iki dosya. `.pt` / `.pth` kendi boyunu söylemiyor: başı bir hata sayfası
değil mi ve Queen Editor'ün taban boyunu (40 MB / 300 MB) geçiyor mu, ona bakılır.

## Toplam

**Civitai: 15.508.722.658 B ≈ 15,5 GB** (checkpoint'ler 13,9 GB, altı aday 1,6 GB), yüz düzeltmesiyle
**≈ 15,9 GB**. Boş disk kontrolü henüz yerinde olmayan dosyaları toplar ve 5 GiB pay ister.

---

## 4) İnmeyenler

| Dosya | Neden inmiyor |
|---|---|
| `USNR_STYLE_ILL_V1_lokr3-000024` | Queen Editor'de bir LoRA seçilince USNR kapanır; adaylar onsuz çizilir |
| `translucent_penetration_v5` (Slime) | Denemenin konusu değil |
| `4x_foolhardy_Remacri.pth` | Yalnız grafiğin kapalı upscale dalı okur |
| femboysXL "MULTI-LoRA" base (128 dim) ve extra (64 dim) | Birlikte kullanılmak için iki dosya; tek dosyalık 92 dim'lik olan alındı |
| Femboy illustrious v1.2, V1; Flaccid Futa v2.0, V1.0; Futa on Male'in ilk Illustrious sürümü | Her adayın en yeni Illustrious sürümü alındı |
| Futa on Female ve Futa on Male'in Pony sürümleri | Pony başka bir taban |
| Öteki femboy ve futa LoRA'ları | `instructions.md`, iki "Seçilmeyenler" listesi |

## 5) Klasör düzeni

```
ComfyUI/
├── models/
│   ├── checkpoints/        nova3DCGXL_ilV90.safetensors
│   │                       DasiwaIllustriousAnime_epitaphecstasy.safetensors
│   ├── loras/              femboysXL_v1.safetensors
│   │                       femboy_illustrious_v1_3.safetensors
│   │                       femboy_new_tos_il.safetensors
│   │                       futa_flaccid_v3.safetensors
│   │                       futa_on_female_il_v2.safetensors
│   │                       futa_on_male_il_v2.safetensors
│   ├── ultralytics/bbox/   face_yolov9c.pt
│   └── sams/               sam_vit_b_01ec64.pth
└── user/default/workflows/ femboysXL_v1.json, femboy_illustrious_v1_3.json, femboy_new_tos_il.json,
                            futa_flaccid_v3.json, futa_on_female_il_v2.json, futa_on_male_il_v2.json
```
