# WAN 2.2 T2V — API modu (tasarım)

**Tarih:** 2026-07-18 · **Durum:** onaylandı, implementasyon planı bekliyor

## Amaç

**Prompt yaz → Run → video Drive'a düşsün. UI'a hiç girmeden.**

Kullanım döngüsü: CONFIG'deki `PROMPT`'u doldur, render hücresini çalıştır, video Drive'a iner. Sonraki prompt için prompt'u değiştirip **aynı hücreyi** tekrar çalıştır — modeller inmiş, ComfyUI ayakta, tekrar kurulum yok.

**Batch değil.** Prompt listesi, klasör tarama, kuyruk yok. Her run tek video üretir. Kullanıcı bunu açıkça istedi: "ben prompt girip run edeceğim, o çalışıp Drive'a koyacak, başka prompt gireceğim, bir daha run edeceğim."

## Bağlam

`wan22-smooth-t2v` UI'lı notebook'u Colab'da doğrulandı ve çalışıyor. Kullanıcı UI'da çok sayıda konfigürasyon denedi ve **sıfır LoRA ile en iyi sonucu aldı.**

Bu tesadüf değil, açıklaması var: creator'ın (DigitalPastel) model sayfası SmoothMix T2V v3.0 için *"Just as T2V v2.0 it has **light2xv baked in** it"* diyor. Distill LoRA zaten checkpoint'e merge edilmiş; Power Lora Loader'dan bir kez daha eklenince **iki kez uygulanıyor**.

Export bunu bağımsız olarak doğruluyor: `workflow_api.json`'da hiç LoRA yok ama sampler (`235:57`) **6 step / cfg 1** — bu ayar ancak distill merged'sa çalışır.

**Sonuç:** `wan2.2_t2v_lightx2v_4steps_lora_v1.1_*` (2×1.14 GiB) indirmesi gereksiz. Yeni notebook onları indirmez.

### API export hazır

Kullanıcı UI'da `Export (API)` yaptı → `collab-toolbox/video_generator/wan22-smooth-t2v/workflow_api.json` (32 node, API formatı).

İlk export'ta node `375` (`PreviewImage`, girdisi bağlanmamış) vardı. `PreviewImage` bir **output node**'dur; ComfyUI çalıştırmadan önce tüm output node'ları doğrular ve zorunlu girdisi eksik olanda `POST /prompt`'u komple reddeder. Kullanıcı o node'u UI'da silip yeniden export etti; şimdiki dosyada `"inputs": {}` hiç geçmiyor.

Kalan iki `UnetLoaderGGUF` (`354`/`355`, `unet_name: null`) **zararsız**: output node değiller ve onlara referans veren hiçbir node yok, ComfyUI'nin çalıştırma grafiği onları budar.

## Kararlar

| Karar | Gerekçe |
|---|---|
| **Yeni notebook, mevcut klasörün içinde** | `wan22-smooth-t2v/` altında iki notebook: UI'lı olan ayar bulmak için, API'li olan üretim için. Aynı işin iki ucu, grafik ve dokümanlar zaten orada. |
| **Referans `loop_maker/comfy_ui.ipynb`** | `NOTEBOOK-STANDARD.md`'nin ilan ettiği referans. `imageToVideo.ipynb` standardın 4 maddesini ihlal ediyor (aşağıda) — ondan kopyalanmaz. |
| **lightx2v indirilmez** | v3'te baked in; ikinci kez uygulamak çıktıyı bozuyor. ~2.28 GiB tasarruf. |
| **Tünel/UI yok** | API modu. Amaç UI'a girmemek. |
| **Çıktı adı zaman damgası** | Kullanıcı kararı. Art arda run'lar birbirini ezmez. |
| **Seed python'dan basılır** | Export'ta `82.inputs.seed = -1`. rgthree'nin `-1` randomizasyonu frontend widget'ında olur; API modunda frontend yok, davranış garanti değil. Notebook açık bir rastgele seed basar ve **ekrana yazar** — beğenilen çıktı tekrar üretilebilsin. |

### `imageToVideo.ipynb` neden referans değil

| Standart | İhlal |
|---|---|
| §1 CONFIG | Drive mount CONFIG'den **sonraki** hücrede — auth istemi 40 dakikalık indirmenin ortasında çıkıyor |
| §4 Civitai | Eski/kırık auth: `__Secure-civitai-token` + `civitai.com` + `?token=` API key |
| §5 Batch | `wait()`'te **timeout yok** — asılan bir prompt notebook'u sonsuza kadar bekletir. Hata sınıflandırması yok. |
| §6 Disk | ComfyUI'nin çıktı kopyası diskte bırakılıyor |

`loop_maker` bunların hepsini doğru yapıyor: `TIMEOUT_PER_VIDEO`, `describe_comfy_error()`, `os.remove(local_out)`, ilk satırda Drive mount.

## Mimari

**Yeni dosya:** `collab-toolbox/video_generator/wan22-smooth-t2v/textToVideo.ipynb`

| # | Hücre | İçerik |
|---|---|---|
| 1 | **CONFIG** | **İlk satırda Drive mount** (§1). `PROMPT`, `DRIVE_BASE`, `COOKIE_VALUE`, `COMFY_PORT` |
| 2 | Helpers | `log` / `human` / `head_text` / `run` / `check_safetensors` — UI'lı notebook'tan birebir |
| 3 | ComfyUI + 16 custom node | UI'lı notebook'tan birebir |
| 4 | Modeller | `SmoothMix_T2V_High/Low_v3` (Civitai, gated probe önce) + umt5 + VAE. **lightx2v yok** |
| 5 | ComfyUI'yi başlat | API modu, `/system_stats` ile hazır olma kontrolü. **Tünel yok**, hücre bloklamaz |
| 6 | **Render** | Prompt'u grafiğe bas → kuyruğa at → bekle → videoyu Drive'a yaz. **Tekrar çalıştırılabilir hücre budur** |

**Drive:** `MyDrive/TextToVideo/output/20260718_1930.mp4`

`workflow_api.json` notebook'a **gömülmez**, `DRIVE_BASE`'den okunur — `imageToVideo` deseni: kullanıcı export'u Drive'a koyar. Böylece grafiği değiştirmek için notebook'u düzenlemek gerekmez, UI'da yeniden export edip Drive'daki dosyayı değiştirmek yeter. Repodaki kopya referans/versiyon kaydıdır.

### Parametre basma

`imageToVideo`'nun deseni: node id sabitleri + alan başına bir setter, her run'da `copy.deepcopy` üzerinde.

```
PROMPT_NODE = "230:229"   # PromptGenerator, inputs.prompt
SEED_NODE   = "82"        # Seed (rgthree), inputs.seed
```

Grafiğin sabit kalan ayarları (export'tan): çözünürlük 480×720 (`97` mxSlider2D), süre 5 sn (`130` PrimitiveFloat → `220` `a*16+1` → 81 kare), sampler 6 step / cfg 1 euler+simple (`235:57`), RIFE 16→32 fps (`160`), `ImageScaleBy` 2× (`79`). Bunlar **patch'lenmez** — değiştirmek istersen UI'da değiştirip yeniden export edersin.

Node id'leri **opak string** olarak ele alınır: `"230:229"` ve `"235:57"` subgraph-flatten edilmiş id'ler, sayı değil.

### Çıktı alma

`VHS_VideoCombine` `save_output: true` ile çalışıyor, yani video ComfyUI'nin `output/` klasörüne yazılıyor. Notebook `/history/{id}`'den çıktı kaydını okur, `/view` ile indirir, Drive'a `YYYYMMDD_HHMM.mp4` adıyla yazar, sonra ComfyUI'nin yerel kopyasını **siler** (§6).

Grafik ayrıca son kareyi `SaveImage` (`81`) ile kaydediyor. Bu bir yan çıktı; notebook yalnızca videoyu alır, `.png`'yi Drive'a taşımaz.

## Model manifesti (~33.5 GiB)

| Hedef | Dosya | Kaynak |
|---|---|---|
| diffusion_models | `SmoothMix_T2V_High_v3.safetensors` | Civitai **2768924** |
| diffusion_models | `SmoothMix_T2V_Low_v3.safetensors` | Civitai **2768944** |
| text_encoders | `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | HF Comfy-Org Wan2.1 |
| vae | `Wan2_1_VAE_fp32.safetensors` ← `wan_2.1_vae.safetensors` | HF Comfy-Org Wan2.1 |

**İnmeyen:** lightx2v çifti (baked in), `WAN_General_NSFW_*` (I2V için eğitilmiş, UI'lı notebook'ta deneme amaçlıydı; API grafiğinde LoRA loader'ları boş, yerleri yok).

`flownet.pkl` (RIFE) kurulumda inmez, node ilk çalıştığında kendi indirir — UI'lı notebook'un run'ında doğrulandı.

## Hata politikası

`NOTEBOOK-STANDARD.md` §2: hatalar **gürültülü**, mesaj **ham** basılır, sebep uydurulmaz.

- `POST /prompt` → `node_errors` varsa `RuntimeError`, ComfyUI'nin kendi gövdesiyle
- `wait()` → **timeout'lu** (`loop_maker`'ın `TIMEOUT_PER_VIDEO` deseni). `imageToVideo`'daki sonsuz döngü kopyalanmaz
- Çalıştırma hatası → `describe_comfy_error()` ile node tipi + traceback ham basılır
- Video çıktısı bulunamazsa → `RuntimeError`, `/history` kaydıyla

Tek video üretildiği için `loop_maker`'ın batch'e özel mantığı (ardışık hata sayacı, infra-vs-item ayrımı, skip) **taşınmaz** — YAGNI.

## Yan iş: yanlış LoRA yönergesi

Sıfır-LoRA bulgusu, mevcut dokümanları yanlış duruma düşürdü. **9 yerde** "Power Lora Loader 109/110'a lightx2v ekle, yoksa çıktı çöp olur" yazıyor; T2V v3 için bu yanlış:

- `instructions.md` — satır 8 (üstteki uyarı blockquote'u), satır 23 (Kullanım adım 6)
- `wan22-smooth-t2v.ipynb` — hücre 0 markdown ×2, hücre 8 `HF_MODELS` yorumu + 2 indirme satırı, hücre 10 runtime `print`
- `indirilecekler.md` — satır 47-48 (manifest satırları), satır 52 (blockquote), satır 74 (grup envanteri)

Ayrıca `indirilecekler.md` satır 47'de HF yolunun ortasına yanlışlıkla bir `vscode-webview://` adresi yapışmış — o satırdaki repo adresi şu an bozuk.

**Bu ayrı bir commit'tir**, yeni notebook'un çalışmasına engel değil. Ama düzeltilmezse bir sonraki kullanıcı 2.28 GiB gereksiz indirip çıktısını bozar.

## Riskler / açık uçlar

1. **rgthree Seed `-1` davranışı.** Export'ta `-1` duruyor; API modunda randomize edilip edilmediği belirsiz. Notebook açık seed bastığı için sorun yaşanmaz, ama patch'lemeyi atlarsak her run aynı videoyu üretebilir.
2. **`PromptGenerator` bir wildcard node'u.** `comfyui-adaptiveprompts`'tan geliyor ve kendi `seed`'i var (`230:229.inputs.seed`). Düz metin prompt'la sorun çıkarmaz, ama prompt'ta `{a|b}` gibi sözdizimi varsa node onu genişletir — beklenmedik çıktı sebebi olabilir.
3. **Model indirmeleri UI'lı notebook'la aynı diski paylaşmaz.** Her Colab oturumu sıfırdan ~33.5 GiB indirir (≈6 dk, ölçüldü). Drive'a model koymak hızlandırmaz — Drive I/O daha yavaş.
4. **`workflow_api.json` Drive'da yaşar.** Repodaki kopya referans; kullanıcı Drive'dakini güncellemeyi unutursa eski grafik çalışır. `instructions.md`'de yazılacak.

## Doğrulama

Kabul kriteri: **CONFIG'e prompt yaz → Run all → Drive'da video var.**

1. Run all → hata yok, gated probe geçer, ~33.5 GiB iner, ComfyUI ayağa kalkar
2. Render hücresi biter, `MyDrive/TextToVideo/output/` altında zaman damgalı `.mp4` görünür
3. Video açılır, prompt'la alakalı ve 480×720 / 5 sn / 32 fps
4. **Tekrar kullanım:** `PROMPT` değiştirilir, **sadece render hücresi** çalıştırılır → ikinci video iner, birincisi durur
5. Aynı prompt'la tekrar → seed farklı olduğu için farklı video, ikisi de kalır

Basılan seed not edilir; beğenilen çıktı tekrar üretilmek istenirse CONFIG'e yazılabilir.
