# Nova 3DCG foto üretimi — manual notebook (tasarım)

**Tarih:** 2026-07-21 · **Durum:** onay bekliyor

## Amaç

`imageToVideoV2` batch'i numaralı fotoğraf istiyor; o fotoğrafları üretecek sistem yok. Kullanıcının sevdiği creator'ın modelleriyle (Nova 3DCG XL + USNR STYLE LoRA + Remacri) fotoğraf üreten bir ComfyUI kurulumu yapılır. Bu tur **sadece manual aşama**: kullanıcı UI'da ayarları bulur, beğendiği ayarla Export (API) verir; `api.ipynb` (batch, `PROMPTS` listesi, varyantlar, `photoGenV2` Drive klasörü) **sonraki turda** o export üzerine yazılır — arbuzai'de kanıtlanmış sıra.

## Kararlar

| Karar | Gerekçe |
|---|---|
| Workflow = `Basic_V37.json` birebir kopya, tek byte değişmez | Kullanıcı kararı: "creator'ın kullandığını düz çalıştırayım". Grafik Illustrious hedefli; üç model de grafiğin öngördüğü yerlere oturuyor (checkpoint slotu, boş Power Lora Loader, `4x_foolhardy_Remacri.pth` zaten grafikte yazılı). arbuzai'deki workflow-dokunulmaz kuralının aynısı. |
| Bu tur sadece `manual.ipynb` | Kullanıcı kararı ("Önce manual"). Export görülmeden api node id'lerine güvenilmez. |
| Model seti sabit: Nova 3DCG XL IL v9.0 + USNR_STYLE_ILL_V1.0 (0.8) + Remacri | Kullanıcı kararı. LoRA ağırlığı 0.8'i kullanıcı UI'da girer — Power Lora Loader grafikte boş geliyor, notebook grafiğe dokunmaz. |
| + `face_yolov9c.pt` + `sam_vit_b_01ec64.pth` indirilir | Grafiğin default-açık FaceDetailer dalı bu ikisini yükler; dosya yoksa loader patlar. |
| Drive klasörü `MyDrive/photoGenV2` | Kullanıcı kararı. Bu turda tek kullanımı export edilen `workflow_api.json`'ın konacağı yer olması; batch çıktı düzeni api turunda tanımlanır. |
| Donanım: normal Colab GPU (T4 yeter) | SDXL sınıfı model; A100 gerekmez. WAN notebook'larından ayrışan tek donanım satırı. |

## Mimari

```
collab-toolbox/photo_generator/nova-3dcg/
├── manual.ipynb           ← wan22-arbuzai/manual.ipynb kopyalanıp uyarlanır
└── workflow_manual.json   ← comfyuiImage_v37/Basic_V37.json birebir kopya (sha256 doğrulanır)
```

`manual.ipynb` = arbuzai `manual.ipynb` deseni: helper'lar (`fetch`, `check_safetensors`, `civitai_probe`) → custom node kurulumu → model indirme → ComfyUI + cloudflared tunnel → kullanıcı UI'da çalışır. Drive mount yok — Export (API) tarayıcıya iner, kullanıcı `photoGenV2`'ye elle koyar. Değişen bölgeler:

**CUSTOM_NODES — Basic_V37'nin künyesinden (cnr_id/aux_id), 7 paket:**
`rgthree-comfy`, `ComfyUI-Impact-Pack`, `ComfyUI-Impact-Subpack`, `ComfyUI-Easy-Use`, `ComfyUI-Custom-Scripts` (pysssss), `ComfyUI_UltimateSDUpscale` (git submodule — `--recursive` klonlanır), `ComfyUI-KJNodes`. Grafikteki kalan her node comfy-core.

**MODELS — 5 dosya:**

| Dosya | Hedef | Kaynak |
|---|---|---|
| `nova3DCGXL_ilV90.safetensors` (~6.5 GiB) | `checkpoints/` | Civitai version **2744564** |
| `USNR_STYLE_ILL_V1_lokr3-000024.safetensors` | `loras/` | Civitai version **1552087** |
| `4x_foolhardy_Remacri.pth` | `upscale_models/` | HF `FacehugmanIII/4x_foolhardy_Remacri` (açık repo) |
| `face_yolov9c.pt` | `ultralytics/bbox/` | HF (adres implementasyonda teyit edilir) |
| `sam_vit_b_01ec64.pth` | `sams/` | Meta segment-anything yayın adresi (implementasyonda teyit edilir) |

Civitai indirmeleri arbuzai'deki kanıtlı yolla: `civitai.red` + `__Secure-civ-token` cookie + curl (`parallel=False`), `check_safetensors` doğrulaması. Dosya adları grafiğin `widgets_values`'ında geçen adlarla birebir aynı tutulur — kullanıcının UI'da tek yapacağı şey listeden seçmek.

**Markdown yönergeleri (Türkçe):** checkpoint'i `nova3DCGXL_ilV90` seç → Power Lora Loader'a USNR 0.8 ekle → prompt'ları POSITIVE/NEGATIVE wildcard kutularına yaz → istersen Control Center'dan kapalı dalları (Ultimate SD Upscale/Remacri, hires fix, el/göz detailer) aç → beğenince **Export (API)** → `MyDrive/photoGenV2/workflow_api.json`.

## Grafik hakkında bilinenler (implementasyonu bağlayan tespitler)

- 74 node'un 37'si default bypass (`mode: 4`). Açık yol: checkpoint → CLIPSetLastLayer → Power Lora Loader → wildcard prompt zinciri → DifferentialDiffusion → KSampler → VAEDecode → FaceDetailer (yalnız yüz) → SaveImage.
- Bypass'lı node'ların da **paketi kurulu olmalı** — UI grafiği yüklerken eksik node tipi kırmızı düşer.
- `UpscaleModelLoader` bypass'lı ama widget'ında `4x_foolhardy_Remacri.pth` yazılı; kullanıcı dalı açtığında dosya hazır olmalı.
- Prompt'lar `CLIPTextEncode`'a doğrudan değil `ImpactWildcardProcessor` → `RegexReplace` zincirinden gidiyor; KSampler'ın kendi step/cfg/seed widget'ları ölü (primitive node'lardan link geliyor). Bu, api turunda enjeksiyon noktalarını belirleyecek.

## Kullanılmayan varyantlar (kayıt)

Grafik, Civitai'de **model 1386234 — "ComfyUI Image Workflows" (Legendaer)** koleksiyonunun bir parçası. V37 sürümünde altı dosya var; repoya yalnız `Basic_V37` girdi, kalanlar indirilip incelendikten sonra silindi (hepsi Civitai'den yeniden inebilir):

| Dosya | Neden alınmadı |
|---|---|
| `Standard_V37` | Basic'in üstüne ek dallar; ihtiyaç doğmadı |
| `Advanced_V37` | Daha fazla custom node + model |
| `Advanced_Gemma_V37` | Prompt üretimi için **Gemma** görsel-dil modeli ister |
| `Advanced_QwenVL_V37` | Prompt üretimi için **Qwen-VL** görsel-dil modeli ister |
| `Detailer_V37` | Yalnız detailer zinciri; Basic'te FaceDetailer zaten default açık |

İleride biri gerekirse: Civitai model 1386234 → sürüm V37 → zip. Yeni varyant bu notebook'un custom node listesini ve model setini büyütür; kurulum süresi ona göre artar.

## Doğrulama (kullanıcı, Colab)

1. T4 runtime'da Run all → 7 paket kurulur, 5 model iner, tunnel URL basılır.
2. UI'da workflow açılır — kırmızı (eksik) node yok.
3. Checkpoint listesinde `nova3DCGXL_ilV90`, LoRA listesinde USNR, upscaler listesinde Remacri görünür.
4. Prompt yazıp Queue → görsel üretilir; FaceDetailer karşılaştırma panelinde yüz düzeltmesi görünür.
5. Export (API) alınıp `photoGenV2`'ye konur → api turunun girdisi.

## Kapsam dışı

`api.ipynb` (batch, `PROMPTS`, `VARIANTS`, çıktı adlandırması, resume), `workflow_api.json`, `photoGenV2/output` düzeni, `instructions.md`. Hepsi export geldikten sonraki turda.
