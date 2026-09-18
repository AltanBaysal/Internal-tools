# MiniMax H3 — DaSiWa "MythicAlchemy" cMMH3 V19 — Talimatlar

- **Workflow:** bu klasörde `workflow.json` — Civitai'den inen adı
  `DasiwaMinimaxH3WorkflowsT2VA_cMMH3V19.json`, **arayüz** formatı *(API export'u değil)*.
  Kaynak: https://civitai.red/models/2831978/dasiwa-minimax-h3-workflows-or-t2va-or-fl2va-or-ref2va
- **Checkpoint (ayrı):** https://civitai.red/models/2877206/dasiwa-minimax-h3
- **Model ailesi:** **MiniMax H3** — WAN değil, yeni bir aile. Ağırlıklar HuggingFace'te açık
  (`Comfy-Org/MiniMax-H3`); DaSiWa'nın kendi finetune'u Civitai'de, login-gated.
- Yazar: Darksidewalker — `wan22-dasiwa` denemesindeki WAN workflow'larıyla aynı kişi, aynı node
  seti.

## Tek dosya, beş mod

Civitai'deki ad "T2V/A" diyor; dosyanın içi bunu yalanlıyor. Grafiğin kendi notları:

> *"All MiniMax H3 modes — T2VA, I2VA, FLF2VA, REF2VA in one workflow"* ·
> *"**Ships in I2VA.** All five MiniMax H3 modes are one click away on the Director pills:
> T2VA · I2VA · FL2VA · L2VA · REF2VA."*

Mod, Director node'undaki **pill**'lerden seçiliyor; grafik değişmiyor. **Açılışta I2VA geliyor** —
queen-editor'ün video kuyruğunun bir üreticiye verdiği şeyin ta kendisi: bir kare fotoğrafı + prompt.

| Mod | Girdi | Bizim tarafta karşılığı |
|---|---|---|
| **I2VA** | tek fotoğraf + prompt | kuyruğun standart video işi |
| **FL2VA** | ilk + son kare | loop ve bağlı video — `workflow_video_first_last_api.json`'un yaptığı |
| T2VA | yalnız prompt | kuyrukta karşılığı yok: her video işi bir fotoğrafla geliyor |
| L2VA | son kareden uzatma | — |
| REF2VA | referans medya havuzu | ayrı UNET ister (+21 GB) |

**A = Audio.** H3 videoyu ve sesi **birlikte** üretiyor; ses ayrı bir geçiş değil. Bu, queen-editor'ün
ayrı ses katmanıyla (MMAudio) çakışan bir konu — denemeyi ilgilendirmiyor, 213'ün kararını
ilgilendiriyor.

## Dosya turbo ayarlarıyla geliyor

Grafiğin Settings alt-grafiği şu an şunu taşıyor: sampler `euler`, **8 adım**, shift video 6,
shift audio 3. Bunlar **turbo** sütunu — ve her iki UNET yuvasında da yazarın kendi turbo
checkpoint'i seçili. `manual.ipynb` tam o checkpoint'i indiriyor, yani **ayarlara dokunmadan**
çalışması gerekiyor.

| | Normal | **Turbo (kurulu olan)** |
|---|---|---|
| Sampler | `res_multistep` | **`euler`** |
| Scheduler | `simple` | `simple` |
| Steps | 25 | **8** |
| Shift Video | 10–12 | **6** |
| Shift Audio | 3–5 | **3** |

Açık HF checkpoint'ine *(`minimax_h3_fl2va_pruned_int8_convrot`)* geçersen bu tablonun **sol**
sütununa dönmen gerekir — turbo olmayan bir modeli 8 adımda koşturmak bozuk çıktı verir.

## Modeller nerede duruyor

**`MiniMaxH3/` bir alt klasör, ad öneki değil.** Grafik loader'ına `MiniMaxH3/<dosya>` diyor;
ComfyUI da `models/diffusion_models/MiniMaxH3/` ve `models/vae/MiniMaxH3/` altına bakıyor. Metin
kodlayıcı ve `taeh3` kendi klasörlerinin kökünde. Hangi dosya, hangi adres, kaç GB:
[indirilecekler.md](indirilecekler.md).

## Çıktı boru hattı — altısı da kapalı geliyor

Frame interpolation (RIFE ×2), post resize, model ile upscale (`2x-AnimeSharpV4_RCAN`), RTX
Upscaler, latent upscale, watermark. Grafikte hepsinin node'u `mode: 4`, yani bypass: kapalıyken
grup tümden devre dışı, modelleri inmese de grafik koşar. `manual.ipynb` bu yüzden onları
indirmiyor.

## Bilinen tuzaklar

- ⚠️ **`nvfp4` / `fp8` dosyalarını seçme.** fp4 yalnız Blackwell'de (RTX 50xx / B200), fp8
  Ada/Hopper'da yerel; Colab'ın büyük kartı A100, yani Ampere. Doğru aile **`int8_convrot`** (UNET)
  ve **`int4_convrot`** (CLIP) — grafiğin kendi varsayılanı da bu.
- ⚠️ **VRAM sırayla yetiyor, aynı anda yetmiyor.** UNET 21 GB + metin kodlayıcı 15 GB = 36 GB; 40
  GB'lık A100'de ancak ComfyUI kodlayıcıyı encode'dan sonra bellekten atarsa geçer. Sığmazsa
  Director'deki **⚙️ Chunking** (MiniMax H3 Chunk FeedForward) anahtarı bunun için duruyor —
  varsayılanı OFF.
- 🧺 **MiniMax H3 Cache'i ilk denemede açma.** Hız kazandırıyor ama grafiğin kendi uyarısı:
  *"can ghost/morph"*. Açıkken bozuk çıktının suçlusu model mi cache mi ayrılamaz.
- ⚠️ **Dosyalar damgalı geliyor.** Bu nicelemeleri üreten araç, son tensörden sonra bir satır ASCII
  bırakıyor: `L2P_bypass_<kaynak dosya>_<unix zaman>`. ComfyUI'nin kendi okuyucusu *(DynamicVRAM
  açıkken)* görmez, Rust `safetensors` reddeder — yani aynı dosya ayara göre yükleniyor
  *([ComfyUI #15602](https://github.com/Comfy-Org/ComfyUI/issues/15602))*. Reddin cümlesi de
  gerçekten kesik bir dosyanınkiyle aynı: *"incomplete metadata, file not fully covered"*.
  `manual.ipynb` bu kuyruğu **basıp kesiyor**, o yüzden defterden geçen dosyalarda sorun çıkmaz —
  ama modeli elle indirirsen bu duvara çarparsın.
- ⚠️ **ComfyUI "Nodes 2.0 beta" ile kullanma** — DaSiWa'nın WAN workflow'larında bozulmaya yol
  açıyordu, aynı node seti burada da var.
- Grafik **subgraph** kullanıyor (node tipi olarak UUID geçen yerler) — eski ComfyUI ön yüzü açamaz.
- `ComfyUI-DD-Translation` eklentisi node bağlantılarını bozuyor — kurma.
- ⚠️ **T4 bu modeli koşturmuyor.** 16 GB VRAM yetmiyor ve makinenin sistem RAM'i de yetmiyor;
  *"Not enough GPU memory"* ile duruyor. Çalışan koşu **80 GB**'lık kartta oldu. Runtime'ı **A100**
  seç — ve runtime tipini değiştirmek makineyi sıfırladığı için 40,1 GB yeniden iner.
- ✅ `MiniMaxH3*` node'ları hiçbir custom node paketinde adı geçmiyor çünkü **ComfyUI'nin kendinde**:
  grafik yüklendiğinde tek bir "missing node" uyarısı çıkmadı *(14 Eylül)*. Model 3 Ağustos 2026'da
  açık ağırlıklarla yayınlandığında ComfyUI desteği aynı gün girmiş.

## Sıra

1. `manual.ipynb` → Colab, **A100** → **Run all** → en alttaki link.
2. `workflow.json`'u UI'a sürükle-bırak. **I2VA** açılışta seçili gelir; Director'e bir fotoğraf ver,
   prompt'u yaz, **Queue Prompt**.
3. Çıkan videoya bak.
4. Beğenilirse: klasör `video_experiments/`'ten `video_generator/`'a taşınır — `wan22-smooth-t2v`
   bunu yaptı — ve **Workflow → Export (API)** ile alınan dosya queen-editor'e girecek olan şeydir
   *(v5 yol haritası, madde 213)*.
