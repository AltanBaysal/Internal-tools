# WAN 2.2 Smooth T2V — deneme ortamı (tasarım)

**Tarih:** 2026-07-17 · **Durum:** onaylandı, implementasyon planı bekliyor

## Amaç

**Soru: text-to-video işe yarıyor mu?** Prompt'tan doğrudan video üretmek kaliteli/kullanışlı mı, mevcut image-to-video'ya gerçek bir alternatif mi. Çıktı: ComfyUI UI'ında elle çalıştırılıp **gözle** değerlendirilen bir deneme. İşe yararsa batch'e taşımak ayrı bir iş.

Bu bir üretim aracı değil — `video_generator/imageToVideo.ipynb`'nin T2V kardeşini yapmıyoruz.

## Bağlam — neden bu kadar kolay

Kullanıcı `WAN 2.2 Smooth Workflow v5.0` grafiğini repoya bıraktı. Analiz iki şey ortaya çıkardı:

1. Dosya bir "T2V workflow" değil; yazarın (Digital Pastel) **tam UI grafiği**, içinde dört grup: `TEXT2VIDEO`, `IMAGE2VIDEO`, `FIRST2LASTFRAME`, `AUDIO2VIDEO`. Hepsi `mode:4` (bypass) gelir; UI'daki *Fast Groups Bypasser* ("Choose Your Workflow") ile grup seçilir.
2. **`video_generator/imageToVideo.json` bu grafiğin FIRST2LASTFRAME grubunun API export'u** — node ID'leri birebir tutuyor (315/316, 338/342, 343, 350–352, `333:291`). Yani T2V hep oradaydı, hiç açılmamış.

T2V grubunun teknik farkı dar: ayrı bir T2V node'u yok — `WanImageToVideo` (node 50) `start_image` bağlanmadan kullanılmış (WAN'ın bilinen boş-latent numarası). Sampler / shift / çözünürlük / süre / RIFE / VHS ayarları I2V ile **birebir aynı** → kıyas temiz, değişen tek eksen I2V→T2V.

## Kararlar

| Karar | Gerekçe |
|---|---|
| **Workflow'a dokunulmaz** | Kullanıcı kararı. Yazar yeni sürüm çıkarınca diff'lenebilir; 169 KB'lık UI JSON'unda node/link ameliyatı riskli. |
| **Sadece ortam kurulur, workflow elle yüklenir** | `video_experiments/`'in tanımı bu; `ltx23-eros` birebir böyle çalışıyor. |
| **Tam grafik (4 grup) yüklenir, sadece T2V modelleri iner** | Yazarın tasarladığı kullanım. Diğer gruplar grafikte durur; açılırsa model bulunamaz hatası verir (dökümante edilir). |
| **NSFW LoRA I2V olmasına rağmen indirilir** | Kullanıcı kararı: UI'da deneyecek. Tutmayabilir — aşağıdaki riske bak. |
| **Notebook hibrit kopyalanır** | Doğrulama+indirme (`check_safetensors` + `fetch`) `imageToVideo`'dan; Civitai auth/probe + tünel `ltx23-eros`'tan. Gerekçe aşağıda. |

## Mimari

Yeni klasör: `collab-toolbox/video_experiments/wan22-smooth-t2v/`

| Dosya | İçerik |
|---|---|
| `workflow.json` | Repo kökündeki `WAN 2.2 Smooth Workflow v5.0 (1).json` taşınır — **değiştirilmez** |
| `instructions.md` | Kaynak özeti + UI adımları + model ekleme (Türkçe) |
| `indirilecekler.md` | İndirme manifesti, ✅/📌/📚/❌ etiketleriyle (Türkçe) |
| `wan22-smooth-t2v.ipynb` | Colab: ComfyUI + custom node + model + tünel |

Ayrıca `video_experiments/deneme-listesi.md`'ye 6. madde — listedeki **ilk T2V girdisi** (mevcut beşi de I2V).

### Notebook yapısı

Hücre sırası `ltx23-eros` kalıbı: **1)** CONFIG (Civitai cookie; Drive yok) → **2)** helpers → **3)** ComfyUI + Manager + custom node'lar → **4)** modeller (önce gated probe, sonra indir) → **5)** başlat + cloudflared tüneli.

**İçerik hibrit — hangi parça nereden:**

| Parça | Kaynak | Neden |
|---|---|---|
| `log` / `human` / `head_text` / `run` / **`check_safetensors`** | `video_generator/imageToVideo.ipynb` c5 | `NOTEBOOK-STANDARD.md` §3 standardı: üç durumlu (`ok`/`partial`/`invalid`), beklenen boyutu safetensors header'ındaki `data_offsets`'ten hesaplar. |
| **`fetch(url, dir, filename, label, *, parallel, headers)`** | `imageToVideo.ipynb` c9 | §3 standart imzası. `parallel=False` = yalnız curl → Civitai/B2 sorununu `ltx23-eros`'un `curl_first`'ü kadar çözer, ekstra parametre gerekmez. |
| Custom node listesi (16) | `imageToVideo.ipynb` c7 | Aynı grafiğin F2LF grubunu çalıştıran **kanıtlanmış** liste. |
| `civitai_url` / `cookie_header` / `civitai_probe` | `ltx23-eros` c3 | §4 referansı: doğru auth (`civitai.red` + `__Secure-civ-token`) + ağır indirmeden önce fail-fast probe. |
| Başlat + cloudflared + `--enable-manager` + `tail -f` | `ltx23-eros` c6 | `imageToVideo`'da tünel yok (API modu); `video_experiments` UI istiyor. |

**`ltx23-eros`'un `is_valid_safetensors()`'ı KULLANILMAZ** — yalnızca "dosya > 1 MB + header magic" bakar; 13.5 GiB'lık yarım inmiş bir checkpoint'i "valid" sayar. 27 GiB checkpoint indirirken bu fark kritik.

- Civitai auth **yeni** desenle: `civitai.red` + `__Secure-civ-token`. `imageToVideo`'nunki eski/kırık (`__Secure-civitai-token` + `civitai.com`) — **kopyalanmayacak**.
- `--enable-manager` açık: workflow elle yüklendiği için eksik node çok olası.
- Başlatma hücresi `tail -f` ile ön planda bloklu kalır (Colab idle kesmesin).

### Custom node'lar

`imageToVideo.ipynb`'nin 16'lık listesi **aynen** alınır — tahmin değil, aynı grafiğin F2LF grubunu çalıştıran kanıtlanmış liste. Tam grafiği yüklediğimiz için hepsi şart: bypass'lı grupların node class'ı yoksa UI "missing node" verir.

## Model manifesti (~37 GiB)

T2V grubunun ihtiyaç duyduğu her şey + kullanıcının denemek istediği NSFW LoRA. Her satır API'den doğrulandı; ✅ = doğrulandı, ⚠️ = bilinen risk.

Boyutlar API'nin verdiği ham değerden; Civitai `sizeKB`'ı KiB varsayıldı (14,207,481.8 KB → 13.55 GiB), HF byte veriyor.

| Hedef | Kaydedilecek ad | Kaynak | Boyut | Durum |
|---|---|---|---|---|
| diffusion_models | `SmoothMix_T2V_High_v3.safetensors` | Civitai **2768924** | ~13.5 GiB | ✅ "T2V High v3.0", base `Wan Video 2.2 T2V-A14B`, model 1995784 |
| diffusion_models | `SmoothMix_T2V_Low_v3.safetensors` | Civitai **2768944** | ~13.5 GiB | ✅ "T2V Low v3.0", aynı base |
| text_encoders | `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | HF Comfy-Org Wan2.1 repackaged | ~6.3 GiB | ✅ imageToVideo'da çalışan indirme (boyut yaklaşık — API'ye sorulmadı) |
| vae | `Wan2_1_VAE_fp32.safetensors` | HF Comfy-Org `wan_2.1_vae.safetensors` | ~250 MB | ✅ imageToVideo deseni (indir + rename) |
| loras | `wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors` | HF Comfy-Org Wan2.2 repackaged | 1.14 GiB | ✅ HF API (1,226,977,424 B) |
| loras | `wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors` | HF Comfy-Org Wan2.2 repackaged | 1.14 GiB | ✅ HF API (1,226,977,424 B) |
| loras | `WAN_General_NSFW_HIGH.safetensors` | Civitai **2073605** | ~0.57 GiB | ⚠️ base `Wan Video 2.2 **I2V**-A14B`; gerçek ad `NSFW-22-H-e8.safetensors` |
| loras | `WAN_General_NSFW_LOW.safetensors` | Civitai **2083303** | ~0.57 GiB | ⚠️ base `Wan Video 2.2 **I2V**-A14B` |

**Ad değişimi şart:** Civitai'nin verdiği gerçek ad `smoothMixWan2214BI2V_t2vHighV30.safetensors`; workflow `SmoothMix_T2V_High_v3.safetensors` bekliyor. `fetch()` hedef adla kaydeder (imageToVideo I2V'de aynısını yapıyor). Yapılmazsa workflow modelleri bulamaz.

**Upscale modeli yok:** yazarın "Upscale by 2"si `ImageScaleBy` lanczos — algoritmik, dosya inmez. (Grafikte `UpscaleModelLoader` yok.)

### Başka creator'ın modelini kullanmak

`CIVITAI_MODELS` bilinçli genişletme noktasıdır: tek satır `(version_id, subfolder, filename, label, curl_first)` eklenir, dosya UI'daki dropdown'da görünür — workflow'a dokunulmaz.

**Kısıt:** WAN 2.2 A14B bir MoE; grafikte iki `UNETLoader` olmasının sebebi bu. Alternatif model de (a) `Wan Video 2.2 T2V-A14B` base olmalı — I2V değil, (b) **high/low noise çifti** halinde gelmeli. Tek dosyalık model, WAN 2.1 veya LTX bu grafiğe düşmez. `instructions.md` bunu yazar.

## Riskler / açık uçlar

1. **LoRA loader'ları boş geliyor — en kolay atlanacak adım.** Yazar Power Lora Loader 109/110'u boş bırakmış ama sampler **6 step / cfg 1**'e ayarlı; bu ancak distill (lightx2v) LoRA ile çalışır. Notebook LoRA'ları indirir, **kullanıcı UI'da loader'a eklemek zorundadır** — yoksa çıktı çöp olur ve "T2V kötü" sanılır. `instructions.md`'nin en üstünde durur.
2. **NSFW LoRA I2V için eğitilmiş** (`I2V-A14B`, T2V sürümü yok — model 1307155'in dört sürümü de I2V). Tutmazsa "T2V mi kötü, LoRA mı uyumsuz" karışır; sorun çıkarsa önce onu bypass et.
3. **`flownet.pkl` (RIFE) — doğrulanmadı.** MTB node'u otomatik mi indiriyor, manuel mi gerekiyor bilinmiyor. Build sırasında çözülecek; küçük dosya, fail-loud yakalar.
4. **VAE fp32 adlandırması.** Comfy-Org'un `wan_2.1_vae.safetensors`'ı gerçekten fp32 mi belirsiz; yazar calcuis/wan-gguf'u linkliyor. Ad yalnızca loader'ın arama anahtarı olduğu için çalışır — imageToVideo bunu aylardır böyle yapıyor.
5. **Prompt boş geliyor** (`PromptGenerator` 230:229) — beklenen, kullanıcı yazacak.

## Doğrulama

Kabul kriteri: **UI'da TEXT2VIDEO grubuyla bir video üretilir.**

1. Notebook'u A100 runtime'da Run all → hata yok, `trycloudflare` linki basılır.
2. Link açılır, `workflow.json` yüklenir → **"missing node" hatası yok** (16 custom node yeterli mi — bu listeyi doğrular).
3. Model dropdown'larında `SmoothMix_T2V_High_v3` / `_Low_v3` görünür (rename doğru çalıştı mı).
4. TEXT2VIDEO grubu açılır, lightx2v LoRA'ları loader'a eklenir, prompt yazılır → Run.
5. 480×720, 5 sn, 32 fps mp4 çıkar. Çöp değilse T2V çalışıyor demektir.
6. Ek: NSFW LoRA eklenip tutuyor mu bakılır (risk 2).

Sonuç `deneme-listesi.md`'deki maddeye `Durum` + `Not` olarak yazılır.
