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
| **[api.ipynb](api.ipynb)** | UI açmaz. CONFIG'e prompt yazarsın, video Drive'a düşer. Üretim için. |
| **[workflow_api.json](workflow_api.json)** | `api.ipynb`'nin okuduğu graf (**API formatı**, `Export (API)` çıktısı) |

İkisi birbirini tamamlar: **`manual` ile ayarı bul → `Export (API)` → `api` ile üret.** İki workflow dosyası aynı grafiktir, farklı formatlarda — API kodu UI formatını okuyamaz.

> ⚠️ **LoRA EKLEME.** Yazar Power Lora Loader'ları (**109** / **110**) boş bırakmış ve sampler **6 step / cfg 1**'e ayarlı — bu ikisi çelişmiyor: SmoothMix T2V v3'te lightx2v checkpoint'e **merge edilmiş** (model sayfası: *"Just as T2V v2.0 it has light2xv baked in it"*). Elle bir distill LoRA daha eklersen iki kez uygulanır ve çıktı bozulur. **Boş bırak** — 18 Tem 2026'da UI'da doğrulandı, sıfır LoRA en iyi sonucu veriyor.

## Ne yapar

Prompt'tan doğrudan video: 480×720, 5 sn, RIFE ile 16→32 fps, `ImageScaleBy` ile 2× upscale, h264-mp4 (crf 19).

Görsel girdi yok: `WanImageToVideo` (node **50**) `start_image` bağlanmadan kullanılıyor — WAN'ın bilinen boş-latent numarası. Core ComfyUI'da Wan için ayrı bir T2V conditioning node'u yok.

## Kullanım

1. Runtime → Change runtime type → **A100 GPU** (Colab Pro gerekli).
2. `manual.ipynb`'yi yükle → CONFIG'de Civitai cookie'yi kontrol et → **Run all**. (~35 GiB iner.)
3. Son hücrenin bastığı `trycloudflare` linkine gir. **O hücreyi kapatma** — kapanırsa Colab runtime'ı idle sayıp tüneli öldürür.
4. UI'da bu klasördeki **`workflow_manual.json`**'u yükle (Workflow → Open, ya da dosyayı tarayıcıya sürükle).
5. **"Choose Your Workflow"** (Fast Groups Bypasser) → **TEXT2VIDEO**'yu aç. Grafik tamamen bypass'lı gelir; hiçbir grup açık değildir.
6. **Power Lora Loader 109/110'a dokunma** — boş kalacaklar (yukarıdaki uyarı).
7. **PromptGenerator** (node **230:229**) boş gelir — prompt'unu yaz.
8. UNETLoader **37**/**56** dropdown'larında `SmoothMix_T2V_High_v3` / `_Low_v3` seçili mi bak.
9. **Run**.

## Notlar / bilinen sorunlar

- **Sadece TEXT2VIDEO çalışır.** Diğer 3 grubun modelleri inmez (bkz. [indirilecekler.md](indirilecekler.md) §6); açarsan model bulunamaz hatası alırsın.
- **NSFW LoRA I2V için eğitilmiş** (`Wan Video 2.2 I2V-A14B`; T2V sürümü yok). İniyor ama garantisi yok — çıktı bozuksa **önce onu bypass et**, sonra T2V'yi yargıla.
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

[api.ipynb](api.ipynb) aynı grafiği ComfyUI'nin HTTP API'si üzerinden çalıştırır: prompt yaz, çalıştır, video Drive'a insin. UI açılmaz, tünel yok.

**Drive kurulumu (bir kez):**

```
MyDrive/TextToVideo/
├── workflow_api.json   ← bu klasördeki workflow_api.json'un kopyası
└── output/             ← otomatik oluşur
```

**Kullanım:**

1. Runtime → **A100 GPU**
2. `api.ipynb` → CONFIG'de `PROMPT`'u doldur → **Run all** (~33.5 GiB iner)
3. Video `output/YYYYAAGG_SSDDSS.mp4` olarak Drive'a düşer
4. **Yeni prompt:** `PROMPT`'u değiştir, **sadece 6. hücreyi** çalıştır — modeller inmiş, ComfyUI ayakta

**Grafiği değiştirmek:** `manual.ipynb`'yi çalıştır, UI'da düzenle, **Workflow → Export (API)** → Drive'daki `workflow_api.json`'un üzerine yaz. Notebook'a dokunma.

Notebook grafiğe yalnızca `PROMPT` ve seed'i basar (`PromptGenerator` **230:229**, `Seed` **82**); çözünürlük, süre, step/cfg, RIFE ayarları grafikte ne yazıyorsa odur.

**Seed:** her çalıştırmada rastgele ve ekrana basılır. Beğendiğin çıktıyı tekrarlamak için `generate(PROMPT, seed=123456)`.

**Neden iki notebook:** UI'lı olan ayarı bulmak, API'li olan üretmek için. İkisi aynı grafiği kullanır; API'li olanın gördüğü graf Drive'daki export'tur.
