# WAN 2.2 T2V — "Smooth Workflow v5.0" TEXT2VIDEO (Digital Pastel) — Talimatlar

- **Kaynak model:** https://civitai.red/models/1995784/smooth-mix-wan-22-14b-i2vt2v
- **Sürüm:** v5.0 — grafik yazarın orijinali, **değiştirilmedi**
- **Model ailesi:** WAN 2.2 T2V-A14B (SmoothMix T2V v3 High+Low)
- **Grafik:** 4 grup içerir (TEXT2VIDEO / IMAGE2VIDEO / FIRST2LASTFRAME / AUDIO2VIDEO); biz **TEXT2VIDEO**'yu kullanırız

> ⚠️ **En kritik adım — atlanırsa çıktı çöp olur.** Yazar Power Lora Loader'ları (**109** / **110**) BOŞ bırakmış, ama sampler **6 step / cfg 1**'e ayarlı. Bu ancak distill LoRA ile çalışır. Notebook `wan2.2_t2v_lightx2v_4steps_lora_v1.1_high/low_noise` dosyalarını indirir — **UI'da loader'lara elle eklemen gerekir.** Eklemezsen model kötü değil, ayar eksiktir.

## Ne yapar

Prompt'tan doğrudan video: 480×720, 5 sn, RIFE ile 16→32 fps, `ImageScaleBy` ile 2× upscale, h264-mp4 (crf 19).

Görsel girdi yok: `WanImageToVideo` (node **50**) `start_image` bağlanmadan kullanılıyor — WAN'ın bilinen boş-latent numarası. Core ComfyUI'da Wan için ayrı bir T2V conditioning node'u yok.

## Kullanım

1. Runtime → Change runtime type → **A100 GPU** (Colab Pro gerekli).
2. `wan22-smooth-t2v.ipynb`'yi yükle → CONFIG'de Civitai cookie'yi kontrol et → **Run all**. (~37 GiB iner, ~25-40 dk.)
3. Son hücrenin bastığı `trycloudflare` linkine gir. **O hücreyi kapatma** — kapanırsa Colab runtime'ı idle sayıp tüneli öldürür.
4. UI'da bu klasördeki **`workflow.json`**'u yükle (Workflow → Open, ya da dosyayı tarayıcıya sürükle).
5. **"Choose Your Workflow"** (Fast Groups Bypasser) → **TEXT2VIDEO**'yu aç. Grafik tamamen bypass'lı gelir; hiçbir grup açık değildir.
6. **Power Lora Loader'lara lightx2v LoRA'larını ekle** (yukarıdaki uyarı): **109** → `..._high_noise`, **110** → `..._low_noise`, strength 1.0.
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
