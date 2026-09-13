# DaSiWa MiniMax H3 — MythicAlchemy (cMMH3 V19) — Talimatlar

- **Workflow:** "DaSiWa MiniMax H3 Workflows | T2V/A | FL2V/A | Ref2V/A" — bu klasörde `workflow.json`
  (Civitai'den inen adı `DasiwaMinimaxH3WorkflowsT2VA_cMMH3V19.json`, arayüz formatı; API export'u değil).
- **Checkpoint (ayrı):** https://civitai.red/models/2877206/dasiwa-minimax-h3
- **Model ailesi:** MiniMax H3 — WAN değil, **yeni bir aile**. Ağırlıklar HuggingFace'te açık
  (`Comfy-Org/MiniMax-H3`); DaSiWa'nın kendi turbo finetune'u Civitai'de, login-gated.
- Yazar: Darksidewalker — `wan22-dasiwa` denemesindeki WAN workflow'larıyla aynı kişi, aynı node seti.

## Tek dosya, beş mod

Civitai'deki ad "T2V/A" diyor ama dosyanın içi bunu yalanlıyor. Grafiğin kendi notu:

> *"All MiniMax H3 modes — T2VA, I2VA, FLF2VA, REF2VA in one workflow"* · *"Ships in **I2VA**. All five
> MiniMax H3 modes are one click away on the Director pills: T2VA · I2VA · FL2VA · L2VA · REF2VA."*

Mod, Director node'undaki **pill**'lerden seçiliyor; grafik değişmiyor. **Açılışta I2VA geliyor** —
queen-editor'ün video kuyruğunun verdiği şeyin ta kendisi: bir kare fotoğrafı + prompt.

| Mod | Girdi | Bizim tarafta karşılığı |
|---|---|---|
| **I2VA** | tek fotoğraf + prompt | kuyruğun standart video işi |
| **FL2VA** | ilk + son kare | loop ve bağlı video (`workflow_video_first_last_api.json`'un yaptığı) |
| T2VA | yalnız prompt | kuyrukta karşılığı yok — her video işi bir fotoğrafla geliyor |
| L2VA | son kareden uzatma | — |
| REF2VA | referans medya havuzu | ayrı UNET ister (+21 GB) |

**A = Audio.** H3 videoyu ve sesi birlikte üretiyor; ses ayrı bir geçiş değil. Bu, ilerde
queen-editor'ün ayrı ses katmanıyla (MMAudio) çakışan bir konu — ama denemeyi ilgilendirmiyor.

## Custom node gereksinimleri (grafiğin kendi "Requirements" notu)

| Paket | git URL |
|---|---|
| rgthree-comfy | https://github.com/rgthree/rgthree-comfy |
| ComfyUI-KJNodes | https://github.com/kijai/ComfyUI-KJNodes |
| ComfyUI-GGUF | https://github.com/city96/ComfyUI-GGUF |
| ComfyUI-DaSiWa-Nodes | https://github.com/darksidewalker/ComfyUI-DaSiWa-Nodes |
| Comfyui-MMH3-UltimateUpscale | https://github.com/bbaudio-2025/Comfyui-MMH3-UltimateUpscale |
| ffmpeg | apt |

`MiniMaxH3Director`, `MiniMaxH3Cache`, `MiniMaxH3SigmaShift`, `MiniMaxChunkFeedForward`,
`MiniMaxH3DirectorGuide` node'ları bu listenin hiçbirinde **adı geçmiyor**: grafiğin notu
*"routes to the native H3 backend automatically"* diyor, yani güncel ComfyUI'nin kendi H3 desteği
olması bekleniyor. Bu yüzden defter **ComfyUI-Manager**'ı da kuruyor ve UI'da eksik node çıkarsa
**Manager → Install Missing Custom Nodes** ile kapatılıyor. Hangi paketten geldikleri denemede
öğrenilecek ve buraya yazılacak.

## Sampler ayarları (grafiğin kendi tablosu)

| | Normal | Turbo |
|---|---|---|
| Sampler | `res_multistep` | `euler` |
| Scheduler | `simple` | `simple` |
| Steps | **25** | **4–8** |
| Shift Video | 10–12 | 6–8 |
| Shift Audio | 3–5 | 4–5 |

Turbo, DaSiWa'nın Civitai'deki kendi checkpoint'ine ait. 21 GB'lık bir video modelinde 25 adım ile
6 adım arasındaki fark denemenin süresini belirler — ilk koşu HF'in düz modeliyle yapılırsa **25
adım** demektir.

## Çıktı boru hattı — hepsi kapalı geliyor

Frame interpolation (RIFE ×2), post resize, model ile upscale (`2x-AnimeSharpV4_RCAN`), RTX
Upscaler, latent upscale, watermark: **altısı da OFF**. Kapalıyken grup tümden bypass, yani
modelleri inmese de grafik koşar. Bu yüzden ilk indirmede yoklar.

## Bilinen tuzaklar

- ⚠️ **`nvfp4` dosyalarını Colab'da alma.** fp4 yalnız Blackwell'de (RTX 50xx / B200) yerel; A100
  Ampere. Aynı sebeple `fp8_scaled` de A100'de yerel değil. Doğru aile **`int8_convrot`** (UNET) ve
  **`int4_convrot`** (CLIP) — grafiğin kendi varsayılanı da bu.
- ⚠️ **VRAM sırayla yetiyor, aynı anda yetmiyor.** UNET 21 GB + metin kodlayıcı 15 GB = 36 GB; A100
  40 GB'da ancak ComfyUI kodlayıcıyı encode'dan sonra bellekten atarsa geçer. Sığmazsa grafiğin
  **⚙️ Chunking** (MiniMax H3 Chunk FeedForward) anahtarı bunun için duruyor — varsayılanı OFF.
- ⚠️ **ComfyUI "Nodes 2.0 beta" ile kullanma** — DaSiWa'nın WAN workflow'larında bozulmaya yol
  açıyordu, aynı node seti burada da var.
- Grafik **subgraph** kullanıyor (node tipi olarak UUID geçen yerler) — eski ComfyUI ön yüzü açamaz,
  güncel sürüm şart.
- 🧺 **MiniMax H3 Cache** hız kazandırıyor ama grafiğin kendi uyarısı: *"can ghost/morph"*. İlk
  denemede açma; yoksa modelin mi cache'in mi suçu olduğu ayrılamaz.
- `ComfyUI-DD-Translation` eklentisi node bağlantılarını bozuyor — kurma.

## Sıra

1. `manual.ipynb` → **Run all** → en alttaki linkten ComfyUI.
2. `workflow.json`'u UI'a sürükle, **I2VA** pill'i seçili gelir, bir fotoğraf ver, prompt yaz, Run.
3. Çıkan videoya bak. Beğenilirse: klasör `video_experiments/`'ten `video_generator/`'a taşınır
   *(`wan22-smooth-t2v` bunu yaptı)* ve **Workflow → Export (API)** ile alınan dosya queen-editor'e
   girecek olan şeydir — madde 213.
