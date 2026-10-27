# WAN 2.2 arbuzai I2V — deneme ortamı (tasarım)

**Tarih:** 2026-07-18 · **Durum:** onaylandı, implementasyon planı bekliyor

## Amaç

**Soru: arbuzai'nin çıktılarındaki görünümü kendi görselim ve kendi prompt'umla yeniden üretebilir miyim?**

Çıktı: ComfyUI UI'ında elle çalıştırılıp **gözle** değerlendirilen bir deneme ortamı, artı öğrenilen ayarların biriktiği bir preset dokümanı. Bir üretim aracı değil; toplu üretim (Drive in/out) bu işin kapsamı dışında — ayarlar oturursa ayrı bir iş olarak `imageToVideo.ipynb` kalıbıyla yapılır.

## Bağlam

Kullanıcı arbuzai adlı creator'ın bir postundaki generation data'yı paylaştı:

```
Checkpoint : Smooth Mix Wan 2.2 14B (I2V/T2V) → I2V v2.0 High
LoRA       : SmoothMix Animations WAN 2.2 → XXX Animations High
LoRA       : SmoothMix Animations WAN 2.2 → XXX Animations Low
Prompt     : External Generator
```

Bundan üç şey çıktı:

1. **Çıktı image-to-video, text-to-video değil.** Kullanıcının ilk varsayımı T2V'ydi; checkpoint `I2V v2.0` olduğu için yanlış. Kardeş klasör `wan22-smooth-t2v`'nin TEXT2VIDEO grubuyla bu görünüm yakalanamaz — girdi tipi farklı.
2. **Checkpoint bizim zaten bildiğimiz model.** Aynı Civitai modeli (1995784), farklı sürüm dalı.
3. **arbuzai grafik paylaşmıyor.** Elimizde yalnızca kaynak listesi var. Çalıştıracağımız graf, yazarın (DigitalPastel) v5.0 grafiğinin **IMAGE2VIDEO** grubu.

### Grafikten çıkarılanlar (doğrulandı)

IMAGE2VIDEO grubunun sınırları `x: −5248 → −1480`, `y: −55 → 1979`. Bu kutunun içindeki loader'lar:

| Node | Tip | İstediği dosya |
|---|---|---|
| **197** | UNETLoader | `SmoothMix_I2V_v2_High.safetensors` |
| **186** | UNETLoader | `SmoothMix_I2V_v2_Low.safetensors` |
| **192** | CLIPLoader | `umt5_xxl_fp8_e4m3fn_scaled.safetensors` |
| **191** | VAELoader | `Wan2_1_VAE_fp32.safetensors` |
| **287** | LoadImage | kullanıcının girdi görseli |
| **201** / **200** | Power Lora Loader (rgthree) | **boş gelir** |

- **Text encoder ve VAE T2V ile birebir aynı dosya.** Değişen tek şey iki checkpoint.
- **`clip_vision_h.safetensors` GEREKMİYOR.** Grafikteki tek `CLIPVisionLoader` (id **351**, `pos [−242, 2434]`) FIRST2LASTFRAME kutusunun içinde. `video_generator/wan22-smooth-t2v/indirilecekler.md` §6 onu I2V'ye de gerekliymiş gibi listeliyor — o satır gevşek yazılmış; §7 doğrusunu söylüyor.

`201` / `200`'ün HIGH/LOW eşleşmesi **konum tahmini**: T2V'de soldaki (109, x≈1382) HIGH, sağdaki (110, x≈1831) LOW. Aynı simetriyle 201 (x≈−4400) HIGH, 200 (x≈−3954) LOW. UI'da teyit edilecek, koda gömülmeyecek.

### Repoda zaten çözülmüş olanlar

`video_generator/imageToVideo.ipynb` **şu anda** bu işin yarısını yapıyor — yeniden icat edilmeyecek, kopyalanacak:

- `2513182` / `2513186`'yı indiriyor ve **`SmoothMix_I2V_v2_High/Low.safetensors` adıyla kaydediyor** — ad değişimi kanıtlanmış
- `wan2.2_i2v_lightx2v_4steps_lora_v1_high/low_noise.safetensors` indiriyor — bizim ihtiyacımız olan distill çifti
- `wan_2.1_vae.safetensors` → `Wan2_1_VAE_fp32.safetensors` rename'i

## Kararlar

| Karar | Gerekçe |
|---|---|
| **Tamamen izole yeni klasör** (`wan22-arbuzai`) | Kullanıcı kararı. Kaynak klasör (`wan22-smooth-t2v`) doğrulandı ve deneme aşamasından çıktı; çalışan kurulumu oynatmak paralel çalışmayı bozar. Yeni klasör o klasörden hiçbir dosya okumaz, sadece kopyalar. |
| **Grafik birebir kopyalanır, DEĞİŞTİRİLMEZ** | Kullanıcı kararı. Kopya `collab-toolbox/video_generator/wan22-smooth-t2v/workflow.json` ile aynı (sha256 `9feefc6f…`). İleride özelleştirme ihtimali açık ama bu işin kapsamında değil. |
| **Klasör adı `wan22-arbuzai`** | Mevcut adlandırmaya uyar (`wan22-dasiwa`, `wan22-painter` de creator adı taşıyor). |
| **İnteraktif kullanım, Drive yok** | `video_experiments/`'in tanımı. Ayarlar bilinmezken toplu üretim, 20 videoyu yanlış ayarla üretmek demek. |
| **Notebook self-contained kopyalanır** | Repo pratiği. Kaynak `wan22-smooth-t2v.ipynb`; değişen tek şey model listeleri ve UI yönergeleri. |

## Mimari

Yeni klasör: `collab-toolbox/video_experiments/wan22-arbuzai/`

| Dosya | İçerik |
|---|---|
| `workflow.json` | `collab-toolbox/video_generator/wan22-smooth-t2v/workflow.json`'un birebir kopyası |
| `wan22-arbuzai.ipynb` | Colab: ComfyUI + custom node + model + tünel |

> **Kaynak klasörün yolu değişti.** `wan22-smooth-t2v` artık `video_experiments/` altında değil, doğrulandıktan sonra `collab-toolbox/video_generator/wan22-smooth-t2v/`'ye taşındı. Kopyalanacak `workflow.json` ve örnek alınacak `wan22-smooth-t2v.ipynb` oradadır.

Notebook hücre sırası kardeşiyle aynı: **1)** CONFIG (Civitai cookie; Drive yok) → **2)** helpers → **3)** ComfyUI + Manager + custom node'lar (16) → **4)** modeller (önce gated probe, sonra indir) → **5)** başlat + cloudflared tüneli.

Kardeş notebook'tan **birebir** alınanlar: `log` / `human` / `head_text` / `run` / `check_safetensors`, `fetch(url, dir, filename, label, *, parallel, headers)`, `civitai_url` / `cookie_header` / `civitai_probe`, 16'lık `CUSTOM_NODES` listesi, başlatma + `--enable-manager` + `tail -f` hücresi.

Değişen: **`CIVITAI_MODELS` / `HF_MODELS` içerikleri** ve markdown/print'lerdeki UI yönergeleri (IMAGE2VIDEO, node 287/201/200).

Korunan kurallar: üç durumlu `check_safetensors` (`NOTEBOOK-STANDARD.md` §3). Civitai auth yeni desen (`civitai.red` + `__Secure-civ-token`, `?token=` yok). Civitai indirmeleri `parallel=False` (curl) — aria2c cookie'yi B2'ye forward edip 403 yiyor. Fail-loud: hata mesajı servisin **ham çıktısını** basar.

> `instructions.md` / `indirilecekler.md` bu turda yazılmıyor. Kullanıcının UI'da ihtiyaç duyduğu her ayar notebook'un markdown hücrelerine ve son hücrenin print'lerine konuyor — okunacağı yer orası.

## Model manifesti (~36 GiB)

| Hedef | Kaydedilecek ad | Kaynak |
|---|---|---|
| diffusion_models | `SmoothMix_I2V_v2_High.safetensors` | Civitai **2513182** (model 1995784) |
| diffusion_models | `SmoothMix_I2V_v2_Low.safetensors` | Civitai **2513186** |
| loras | `SmoothMix_Animations_XXX_High.safetensors` | Civitai **2376136** (model 2040641) |
| loras | `SmoothMix_Animations_XXX_Low.safetensors` | Civitai **2376143** |
| loras | `wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors` | HF Comfy-Org Wan2.2 repackaged |
| loras | `wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors` | HF Comfy-Org Wan2.2 repackaged |
| text_encoders | `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | HF Comfy-Org Wan2.1 repackaged |
| vae | `Wan2_1_VAE_fp32.safetensors` ← `wan_2.1_vae.safetensors` | HF Comfy-Org Wan2.1 repackaged |

**Ad değişimi şart — sıra ters.** Civitai checkpoint'i `SmoothMix_I2V_High_v2.safetensors` olarak veriyor (model sayfasındaki dosya adı), grafiğin UNETLoader 197/186'sı `SmoothMix_I2V_v2_High.safetensors` istiyor: `_High_v2` ↔ `_v2_High`. `imageToVideo.ipynb` bunu zaten doğru yapıyor.

**Animations LoRA'sında doğru dal seçilmeli.** Model 2040641'in **sekiz** sürümü var: Animation, Futanaris and Males, XXX Animations, Style — her biri High+Low. arbuzai **XXX Animations** çiftini kullanıyor.

**İnmeyen (bilerek):** T2V checkpoint'leri, `clip_vision_h.safetensors`, MMAudio 4 dosya. TEXT2VIDEO / FIRST2LASTFRAME / AUDIO2VIDEO gruplarını açarsan bunlar eksik olur.

## arbuzai preset

Creator'ın (DigitalPastel) model sayfalarından aktarıldı — **yazarın beyanı, bizim ölçümümüz değil.**

| Ayar | Değer | Kaynak |
|---|---|---|
| Checkpoint | SmoothMix I2V v2.0 High + Low | ✅ generation data (Low çıkarım — MoE çift gerektiriyor) |
| XXX Animations LoRA | **1.0 / 1.0** (High → node 201, Low → node 200) | ✅ model sayfası: "High and Low Showcases are all using weight 1.0 on both Loras" (Img2Vid) |
| Distill LoRA | **High 3.0 / Low 1.5** | ✅ model sayfası, I2V v2.0 showcase'leri |
| Steps / CFG | **4-6 step / cfg 1** | ✅ yazarın önerdiği ayarlar |
| Sampler / Scheduler | **Euler a/Normal** ya da **UniPC/Simple** | ✅ aynı |
| Çözünürlük | 480×720–720×480 (orta sistem); I2V v2.0 showcase'leri **900×600** | ✅ aynı |
| Trigger word | `SmoothMixAnime` / `SmoothMixRealism` | ✅ model sayfası |
| Prompt | — | ❌ "External Generator"; kullanıcı kendi prompt'unu yazar |
| Seed | — | ❌ paylaşılmamış |

Kullanıcı test ettikçe bu tablo gerçek gözlemle güncellenir.

## Riskler / açık uçlar

1. **Distill LoRA — çelişki çözüldü, ama LoRA'lar aynı değil.** Model sayfası açıkça diyor ki I2V v2.0'da **lightx2v merged DEĞİL** ("Lightx2v Lora is NOT merged this time"), yani 6 step / cfg 1 için distill LoRA gerçekten şart — notebook'un onu indirmesi doğru. **Ama** yazarın showcase'lerinde kullandığı `lightx2v_I2V_14B_480p_cfg_step_distill_rank128_bf16` (WAN 2.1 dönemi, rank128); bizim indirdiğimiz `wan2.2_i2v_lightx2v_4steps_lora_v1_*` (WAN 2.2, 4 step). **Farklı LoRA'lar** — 3.0/1.5 ağırlıkları birebir taşınmayabilir. Önce repodakiyle 3.0/1.5 dene; hareket aşırı/eksikse ağırlığı oynat, sonra yazarınkine geç.
2. **XXX Animations dataset'i yalnız NSFW poz kapsıyor.** Yazarın notu: pozlar prompt'a bağlı değil, genel prompt'lar çalışır. Beklenen görünüm ancak uygun içerikte ortaya çıkar; nötr bir sahnede LoRA'nın etkisi görünmeyebilir ve "LoRA çalışmıyor" sanılır.
3. **T2V v2.0/v3.0'da lightx2v baked in, I2V v2.0'da değil.** İki sürüm arasında geçiş yaparken distill LoRA'yı çıkarmayı/eklemeyi unutmak bozuk çıktının en olası sebebi.
4. **Hiper-gerçekçi içerik morph olabilir.** Yazarın notu: I2V v2.0 "SmoothMix Animations" stiline çekiyor. Gerçekçi hedefliyorsan realizme iten prompt gerekir.
5. **Erkek anatomisi güvenilir üretilmiyor** (yazarın notu) — ayrı LoRA gerektirir, bu kapsamda yok.
6. **201/200'ün HIGH/LOW eşleşmesi tahmin** — UI'da teyit edilecek.
7. **`flownet.pkl` (RIFE)** — T2V run'ında otomatik iniyor mu görülecek; sonuç oradan taşınır, burada ayrıca tahmin edilmez.

## Doğrulama

Kabul kriteri: **UI'da IMAGE2VIDEO grubuyla, kullanıcının kendi görselinden bir video üretilir.**

1. Notebook A100 runtime'da Run all → hata yok, gated probe 4 Civitai asset için geçer, `trycloudflare` linki basılır.
2. Link açılır, klasörün `workflow.json`'u yüklenir → **"missing node" hatası yok**.
3. UNETLoader **197**/**186** dropdown'larında `SmoothMix_I2V_v2_High` / `_Low` görünür (rename doğru çalıştı mı).
4. "Choose Your Workflow" → **IMAGE2VIDEO**. LoadImage **287**'ye görsel. Power Lora Loader **201**: lightx2v_high 3.0 + Animations_XXX_High 1.0; **200**: lightx2v_low 1.5 + Animations_XXX_Low 1.0. Prompt → Run.
5. Video çıkar. arbuzai'nin çıktılarına benziyor mu — **gözle** değerlendirilir.
6. Benzemiyorsa sırayla: risk 1 (LoRA ağırlıkları / yazarın distill LoRA'sı), risk 2 (içerik uyumu), risk 4 (realizm morph'u).

Öğrenilen her değer preset tablosuna yazılır — tahmin değil, run'da ne olduysa o (drift yasağı).
