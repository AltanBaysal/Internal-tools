# WAN 2.2 T2V — "Smooth Workflow v5.0" TEXT2VIDEO (Digital Pastel) — Talimatlar

- **Kaynak model:** https://civitai.red/models/1995784/smooth-mix-wan-22-14b-i2vt2v
- **Sürüm:** v5.0 — grafik yazarın orijinali, **değiştirilmedi**
- **Model ailesi:** WAN 2.2 T2V-A14B (SmoothMix T2V v3 High+Low)
- **Grafik:** 4 grup içerir (TEXT2VIDEO / IMAGE2VIDEO / FIRST2LASTFRAME / AUDIO2VIDEO); biz **TEXT2VIDEO**'yu kullanırız

## Bu klasörde ne var

İki notebook, aynı grafiğin iki kullanım şekli:

| Dosya | Ne yapar |
|---|---|
| **[manual.ipynb](manual.ipynb)** | ComfyUI'yi tünelle açar, grafiği **elle** sürersin. Ayar denemek, prompt kurcalamak için. |
| **[workflow_manual.json](workflow_manual.json)** | `manual.ipynb`'de UI'a yüklediğin graf (**UI formatı**) |
| **[api.ipynb](api.ipynb)** | UI açmaz. PROMPTS hücresine prompt listeni yazarsın, her prompt için bir video Drive'a düşer. Üretim için. |
| **[workflow_api.json](workflow_api.json)** | `api.ipynb`'nin okuduğu graf (**API formatı**, `Export (API)` çıktısı) |

İkisi birbirini tamamlar: **`manual` ile ayarı bul → `Export (API)` → `api` ile üret.** İki workflow dosyası aynı grafiktir, farklı formatlarda — API kodu UI formatını okuyamaz.

> ⚠️ **Distill/hız LoRA'sı EKLEME.** Yazar Power Lora Loader'ları (**109** / **110**) boş bırakmış ve sampler **6 step / cfg 1**'e ayarlı — bu ikisi çelişmiyor: SmoothMix T2V v3'te lightx2v checkpoint'e **merge edilmiş** (model sayfası: *"Just as T2V v2.0 it has light2xv baked in it"*). Elle bir distill LoRA daha eklersen iki kez uygulanır ve çıktı bozulur. 18 Tem 2026'da UI'da doğrulandı: **hız LoRA'sı olmadan** en iyi sonuç alınıyor.
>
> Bu yasak **stil/hareket LoRA'larını kapsamıyor** — 109/110 tam da onlar için duruyor. `loras/` klasörüne inen SmoothMix Animations seti oraya takılabilir (bkz. Kullanım adım 6).

## Ne yapar

Prompt'tan doğrudan video: 480×720, 5 sn, RIFE ile 16→32 fps, `ImageScaleBy` ile 2× upscale, h264-mp4 (crf 19).

Görsel girdi yok: `WanImageToVideo` (node **50**) `start_image` bağlanmadan kullanılıyor — WAN'ın bilinen boş-latent numarası. Core ComfyUI'da Wan için ayrı bir T2V conditioning node'u yok.

## Kullanım

1. Runtime → Change runtime type → **A100 GPU** (Colab Pro gerekli).
2. `manual.ipynb`'yi yükle → CONFIG'de Civitai cookie'yi kontrol et → **Run all**. (~35.3 GiB iner.)
3. Son hücrenin bastığı `trycloudflare` linkine gir. **O hücreyi kapatma** — kapanırsa Colab runtime'ı idle sayıp tüneli öldürür.
4. UI'da bu klasördeki **`workflow_manual.json`**'u yükle (Workflow → Open, ya da dosyayı tarayıcıya sürükle).
5. **"Choose Your Workflow"** (Fast Groups Bypasser) → **TEXT2VIDEO**'yu aç. Grafik tamamen bypass'lı gelir; hiçbir grup açık değildir.
6. **Power Lora Loader 109/110** — hız LoRA'sı ekleme (yukarıdaki uyarı). Stil denemek istersen `loras/`ten seç: **High → 109**, **Low → 110**, aynı setten çift olarak, strength **0.5**'ten başla — ve prompt'a trigger word yaz (`SmoothMixAnime` / `SmoothMixRealism`; Futanari çifti kendi kelimeleriyle). Trigger word olmadan LoRA sessizce etkisiz kalır.
7. **PromptGenerator** (node **230:229**) boş gelir — prompt'unu yaz.
8. UNETLoader **37**/**56** dropdown'larında `SmoothMix_T2V_High_v3` / `_Low_v3` seçili mi bak.
9. **Run**.

## Notlar / bilinen sorunlar

- **Sadece TEXT2VIDEO çalışır.** Diğer 3 grubun modelleri inmez (bkz. [dependencies.md](dependencies.md) §6); açarsan model bulunamaz hatası alırsın.
- **İnen LoRA'lar T2V-native** (SmoothMix Animations, model 2040641) — eski `WAN_General_NSFW` çifti I2V tabanlı olduğu için 2026-07-21'de çıkarıldı. Yine de **çıktıya etkisi UI'da henüz ölçülmedi**: bozuk sonuç görürsen önce LoRA'ları bypass edip karşılaştır.
- Eksik custom node çıkarsa: UI'da **Manager → Install Missing Custom Nodes** → Restart. Notebook `--enable-manager` ile başlar; bu flag olmadan Manager kapalıdır.
- Cookie `exp` ~30 gün. Dolduysa gated probe ilk saniyelerde HTTP 401/403 + Civitai'nin gerçek yanıtıyla durur → `civitai.red`'de yeniden login, CONFIG'i güncelle.
- Modeller Drive'a değil Colab'ın geçici diskine iner; her oturumda yeniden iner.

## Başka creator'ın modelini kullanmak

Notebook'taki `CIVITAI_MODELS` listesine tek satır ekle:

```python
(version_id, DIFF, "İstediğin_Ad.safetensors", "Etiket"),
```

Dosya UI'daki UNETLoader dropdown'ında görünür — **workflow'a dokunmana gerek yok**.

**Kısıt:** WAN 2.2 A14B bir MoE (high-noise + low-noise uzman çifti); grafikte iki `UNETLoader` olmasının sebebi bu. Alternatif model de:

1. **`Wan Video 2.2 T2V-A14B`** base olmalı — I2V değil. (Civitai'de model version sayfasındaki `baseModel` alanına bak; NSFW LoRA'da tam bu tuzağa düştük.)
2. **high/low noise çifti** halinde gelmeli.

Tek dosyalık model, WAN 2.1 veya LTX bu grafiğe düşmez. LoRA'lar için de aynı kısıt geçerli.

## API modu — UI'a girmeden üretmek

[api.ipynb](api.ipynb) aynı grafiği ComfyUI'nin HTTP API'si üzerinden çalıştırır: prompt listeni yaz, çalıştır, her prompt için bir video insin. UI açılmaz, tünel yok.

**Drive kurulumu (bir kez):**

```
MyDrive/TextToVideo/
├── workflow_api.json   ← bu klasördeki workflow_api.json'un kopyası
└── output/             ← otomatik oluşur
```

**Kullanım:**

1. Runtime → **A100 GPU**
2. `api.ipynb` → **PROMPTS** hücresine prompt'larını yaz (her biri üç tırnak arasında, eksiksiz bir metin) → **Run all** (~35.3 GiB iner)
3. Her prompt için bir video: `PROMPTS[0]` → `output/01.mp4`, `PROMPTS[1]` → `02.mp4`, …
4. **Yeni video:** listeye **sondan** ekle, **2. ve 7. hücreyi** çalıştır — üretilmiş videolar atlanır, sadece yenisi üretilir

**Prompt'u tek parça, akan cümlelerle yaz.** WAN metni UMT5 ile kodluyor: uzun bağlam alan, düz cümlelerle eğitilmiş bir encoder. Prompt'u alanlara (karakter/mekân/kamera/stil) bölüp noktayla birleştirmek **denendi ve bırakıldı** — 2026-07-20'de A100'de koşuldu, çıktı kötü çıktı; model bağlaçsız öbek dizisini iyi okumuyor. `masterpiece, best quality, 8k` gibi Danbooru tag'leri de SDXL/CLIP konvansiyonu, burada karşılığı yok.

> ⚠️ **Sıra çıktı adını belirliyor.** Ortaya eleman eklemek veya sırayı değiştirmek altındaki eşleşmeleri kaydırır: `05.mp4` başka bir prompt'a ait olur ama dosya var diye atlanır. **Bir numarayı kapatmak için silme, prompt'unu boş bırak** — liste kaymaz, o numara atlanır.

**Grafiği değiştirmek:** `manual.ipynb`'yi çalıştır, UI'da düzenle, **Workflow → Export (API)** → Drive'daki `workflow_api.json`'un üzerine yaz. Notebook'a dokunma.

Notebook grafiğe yalnızca prompt'u ve seed'i basar (`PromptGenerator` **230:229**, `Seed` **82**); çözünürlük, süre, step/cfg, RIFE ayarları grafikte ne yazıyorsa odur. Düğüm yerinde durduğu için wildcard sözdizimi (`{ a | b }`) prompt'un içinde çalışır.

**Seed:** `SEED` tüm listeye uygulanır (PROMPTS hücresinde). Aynı listeyi tekrar çalıştırmak aynı videoları verir.

**Neden iki notebook:** UI'lı olan ayarı bulmak, API'li olan üretmek için. İkisi aynı grafiği kullanır; API'li olanın gördüğü graf Drive'daki export'tur.
