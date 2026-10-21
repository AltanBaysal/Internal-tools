# Madde 485 · Krea 2 — Colab deneme kurulumu — plan

**Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md), 485 · v10-9 ·
**Dal:** `feat/queen-editor-v10` · **Spec yok:** madde kullanıcıyla birlikte yapılıyor; bu plan onun
yerini tutar. **Kalıp:** 484'ün defterleri
([collab-toolbox/photo_experiments/qwen-image-21/](../../collab-toolbox/photo_experiments/qwen-image-21/))
ve [484'ün planı](2026-10-21-queen-editor-m484-qwen-trial-plan.md).

**Kullanıcının istediği (21 Ekim):** iki defter, `turbo.ipynb` ve `raw.ipynb`, yeni bir klasörde,
`collab-toolbox/photo_experiments/krea-2/`. **Her şey baştan iner;** sonradan yeni bir şey istenirse
ComfyUI yeniden başlatılır. Her defter: Krea 2'nin modeli ve parçaları (A100'de int8), Krea'nın bütün
resmî tarz LoRA'ları, Civitai'den NSFW LoRA'ları ve checkpoint'ler. **Workflow'u biz yazmayız ve
üretmeyiz:** yalnız Comfy-Org'un resmî şablonları, olduğu gibi. Kullanıcı sonradan bir checkpoint daha
ekledi: **Wulver** (model 2881657), tabanı "Krea 2 Turbo".

İşaretler: **✅** kaynaktan ya da dosyanın kendisinden doğrulandı · **≈** doğrulanmadı · **🧮** hesap.

---

## 0. Sorular — kararlaştı

**Ana ajan 21 Ekim'de onayladı**, ve cevapları:
- **S1:** curl yok. `instructions.md` her pozisyon sürümünün Civitai sayfasına bağlanır: "tetik
  kelimeleri sayfasında".
- **S2:** ComfyUI'nin sessizce yanlış okuyabileceği dosyaya kumar oynanmaz. Üçüncü kişilerin
  modellerinde yazarın ComfyUI için verdiği dosya alınır; **fp8 varsa fp8**, en doğrudan kaynaktan (HF,
  baytlar tutuyorsa; yoksa Civitai, `fileId` ile). ComfyUI fp8_scaled ağırlıkları A100'de bf16'ya çevirip
  doğru hesaplar, yerel fp8'den yavaş; şablonların kendi kodlayıcısı da zaten fp8_scaled. Yalnız int8
  varsa int8 kalır, ve `comfy_quant` yoksa özet uyarır. Comfy-Org'un int8 Krea dosyaları ve int8
  şablonlar kalır (onlar `comfy_quant` taşıyor).
- **S3:** yalnız fp8_scaled kodlayıcı.
- **S4:** Sick Ollie ve Moody yalnız Turbo defterinde.
- **S5:** Wulver Non-Turbo ham deftere, HF'ten, fp8'i varsa fp8. `instructions.md` ayarlarını verir:
  52 adım / cfg 3,5, ya da Turbo LoRA'sıyla 8 adım.
- **S6:** Wulver HF'ten. **S7:** Moody V8.0, fp8.

**Bu kararlarla seçilen dosyalar** (2.1 ve 2.2'nin tabloları buna göre düzeltildi):
- **Wulver Turbo:** `Wulver_v0.5_fp8_e4m3fn.safetensors`, HF, 12.821.599.836 B — Civitai'nin birincil
  dosyası 3249021'in aynısı (SHA256 `ef8b8e1c…`, `sizeKB × 1024` aynı bayt) ✅; yazarın *"ComfyUI — the
  one most people want"* dediği.
- **Wulver Non-Turbo:** HF'te fp8'i **yok** ✅; yalnız `non_turbo_bf16` (25.640.191.128 B) ve
  `non_turbo_int8-convrot` (13.491.966.712 B). Kural "yalnız int8 varsa int8": int8-convrot iner, özet
  `comfy_quant`'a bakar. bf16 ComfyUI'de kesin doğru okunur ama iki kat büyük; ana ajana not edildi.
- **Sick Ollie:** fp8, dosya 3035266, `sickOllie_krea2_3035266.safetensors`, 12.821.587.640 B, Civitai
  türü "Diffusion Model" ✅. HF'te yok; adres `…/3154408?fileId=3035266`.
- **Moody V8.0:** fp8, Civitai'de V8.0'ın kardeş girdisinde, **"V8.0 BF16 & FP8" (3327123)** ✅ — 3327244
  yalnız int4 / nvfp4 / int8 taşıyor. Orada iki fp8 var: `fp8` (3213080, birincil, 13.782.043.152 B) ve
  **`fp8_scaled` (3213091), 13.141.769.512 B** ✅. fp8_scaled seçildi: boyu Comfy-Org'un
  `krea2_turbo_fp8_scaled`'inden (13.141.730.784 B) yalnız 38 KB farklı, yani ComfyUI'nin tanıdığı aynı
  biçim 🧮; birincil `fp8`'in biçimi yazılı değil. Adres `…/3327123?fileId=3213091`, dosya
  `moodyKrea2MixUncensoredV8FREEV8_v80BF16FP8_3213091.safetensors`.

Aşağıdaki S1 – S7 onaydan önce sorulduğu hâliyle duruyor.

**S1. `krea2 sex` LoRA'larının tetik sözcükleri okunamadı.** WebFetch'in okuyucusu Civitai API'sinin
`trainedWords`'ünü açık cinsel terim olduğu için aktarmıyor; tek söylediği, CG sürümünün tek tetiğinin
*"kısa bir kod değil, uzun bir terim dizisi"* olduğu. Kullanıcının curl'ü reddettiği yerde
(*"tool kullan"*) README'yi WebFetch okuyabiliyordu; burada okuyamıyor.
1. **Önerilen:** API'nin açık JSON'u (`https://civitai.com/api/v1/model-versions/<id>`, dosya değil,
   girişsiz) altı sürüm için curl ile, `python -I` ile yalnız `trainedWords` basılarak okunur.
2. `instructions.md` tetik sözcüklerini yazmaz; her sürümün Civitai sayfasına bağlanır ("Trigger
   Words" kutusunda kopyala düğmesi var).

**S2. Wulver'ın, Sick Ollie'nin ve Moody'nin int8'i ComfyUI'nin kendi int8'i mi?** ComfyUI int8'i
katman başına bir `<katman>.comfy_quant` girdisinden tanıyor (biçim `int8_tensorwise`, `convrot: true`)
✅ ([comfy/ops.py](https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/ops.py)). Comfy-Org'un
dosyaları şablonlarda yükleniyor; ama Wulver'ın yazarı kendi `int8_convrot`'u için *"forge-neo and other
int8 runtimes"* diyor, ComfyUI için fp8'i öneriyor ✅. İşaret yoksa ComfyUI int8 baytlarını ölçeksiz
okur ve büyük olasılıkla sessizce bozuk resim verir ≈. Bunu şimdi bilmenin yolu dosyanın header'ı.
1. **Önerilen:** Wulver HF'te açık; header'ı tek bir range isteğiyle (ilk ~2 MB, model inmez) curl ile
   okunur ve `comfy_quant` aranır. Civitai'deki ikisi girişsiz okunamayabilir; onlar için defter
   indirdikten sonra bakar (2.2, adım 4).
2. Şimdi bakılmaz; yalnız defterin kendi kontrolü (2.2, adım 4) kullanıcıya söyler.

**S3. Metin kodlayıcı: şablonların adı fp8.** İki int8 şablon da (aşağıda, 1.1) metin kodlayıcı olarak
`qwen3vl_4b_fp8_scaled` istiyor, `int8_convrot`'u değil ✅. Brief'in kuralı *"download exactly what each
template names"*: **fp8_scaled iner** (5.242.467.968 B), `int8_convrot` (4.858.559.240 B) inmez. fp8
ağırlıkları A100'de yerel hesaplanmaz, ComfyUI onları bf16'ya çevirip koşar ≈; 4B'lik bir kodlayıcıda
fark küçük ≈. İstenirse int8 de iner ve `clip_name`'den seçilir (+4,86 GB). **Önerilen: yalnız fp8**,
kural böyle.

**S4. Sick Ollie ve Moody ham defterde de mi?** Brief "ikisinde de" diyor. İkisinin de yazarı onları
Turbo gibi koşuyor (Sick Ollie: 9 adım, cfg 1; Moody: 8 adım, cfg 1, örnek workflow'u bir Turbo
LoRA'sıyla) ✅, ama RAW'dan mı Turbo'dan mı türedikleri yazılı değil ≈. Ham defterde de aynı 8 – 9 adım,
cfg 1'le koşarlar, yani ham deftere bir şey katmıyorlar; Wulver için konan kural (*"yalnız kaynak ham
için de çalışıyor diyorsa"*) onlara da uyar.
1. **Önerilen:** yalnız Turbo defterinde. Ham defter 27,0 GB küçülür.
2. Brief'teki gibi ikisinde de.

**S5. Wulver ham defterde.** Civitai'deki dosyalar Turbo LoRA'sı içine katılmış Turbo dosyaları ✅. Ama
yazarın HF deposunda aynı sürümün **Non-Turbo** int8'i de var, ve README onu ham ayarlarla anlatıyor:
LoRA'sız 52 adım, cfg 3,5; ya da Turbo LoRA'sıyla 1,0 / 8 adım / cfg 1 ✅
([Vaelico/Wulver](https://huggingface.co/Vaelico/Wulver)).
1. **Önerilen:** ham deftere `Wulver_v0.5_non_turbo_int8-convrot.safetensors` (13.491.966.712 B, HF).
   Kullanıcının koşulu (*kaynak ham için çalışıyor diyorsa*) bu dosyada tutuyor.
2. Wulver yalnız Turbo defterinde.

**S6. Wulver nereden.** Civitai'deki seçilen dosya (3249141) HF'teki `Wulver_v0.5_int8_convrot`'un
**aynısı**: SHA256 ikisinde de `e3d89a4f…c7009877`, boy 13.491.966.712 B ✅. **Önerilen: HF'ten**
(`hf_hub_download`, çerez yok, Xet hızı, HF'in bayt sayısına tutulur). Civitai'den de olur:
`https://civitai.red/api/download/models/3361227?fileId=3249141`.

**S7. Moody'nin hangi sürümü.** "V8" adlı son sürüm **V8.0** (3327244, 15 Eylül) ✅. Ondan sonra iki
temalı özel sürüm var: *V8SE 古风萌妹* (3353829, 24 Eylül) ve *Gothic COS Halloween Sp* (3387411,
7 Ekim) ✅. **Önerilen: V8.0** — kullanıcının adını verdiği V8; SE'ler bir temaya ayarlı.

---

## 1. Kaynaklar

### 1.1 Resmî şablonlar ✅

[Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates/tree/main/templates)'te
Krea 2 için üç şablon var, üçü de Turbo; Comfy-Org'un
[README](https://huggingface.co/Comfy-Org/Krea-2/blob/main/README.md)'si ve
[docs.comfy.org](https://docs.comfy.org/tutorials/image/krea/krea-2) bu üçünü sayıyor. **RAW şablonu
yok** ✅.

| Şablon | Bayt | `models` listesi |
|---|---|---|
| `image_krea2_turbo_t2i_int8.json` | 60.684 | `krea2_turbo_int8_convrot`, `qwen3vl_4b_fp8_scaled`, `qwen_image_vae`, `krea2_darkbrush` |
| `image_krea2_turbo_int8_image_style_reference.json` | 62.999 | `krea2_turbo_int8_convrot`, `qwen3vl_4b_fp8_scaled`, `qwen_image_vae`, `krea2_style_reference` |
| `image_krea2_turbo_t2i.json` *(inmez)* | 59.709 | `krea2_turbo_fp8_scaled`, `qwen3vl_4b_fp8_scaled`, `qwen_image_vae`, `krea2_darkbrush` |

Ham adresler `https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/<ad>`;
baytlar GitHub contents API'sinden ✅. Brief'in andığı `image_krea2_turbo_t2i` fp8 DiT'i istiyor; A100
için int8'i yükleyen kardeşi `…_t2i_int8` iner.

**Grafik** (int8 t2i) ✅: üstte bir alt grafik node'u, *Text to Image (Krea-2 Turbo)*; dışa açık
girdileri `prompt`, `prompt_enhance` (**açık**), `LLM_max_token`, `LLM_thinking_mode`, `width`,
`height`, `seed`, `enable_lora` (kapalı), `lora_name`, `lora_strength`, `lora_trigger_word`,
`unet_name`, `clip_name`, `vae_name`. Adım ve cfg dışa açık değil: alt grafikteki `KSampler`'da, 8 adım,
cfg 1, `euler`, `simple`. Model hattı: `UNETLoader → LoraLoaderModelOnly → Switch (Model).on_true`,
ve `UNETLoader → Switch (Model).on_false`; anahtarı `enable_lora` seçiyor, çıkışı `KSampler`'a. Negatif
`ConditioningZeroOut`. `prompt_enhance` açıkken metin kodlayıcı (Qwen3-VL) prompt'u bir sistem
talimatıyla düzyazıya yeniden yazıyor (`TextGenerate`). Boyutu dışarıdaki `ResolutionSelector` veriyor.

**Stil referansı şablonu** ✅: alt grafik *Image Style Reference (Krea-2 Turbo)*; girdileri `image1`,
`image2`, `image3` (yalnız `image1` bağlı, `Load Image` → `krea2_reference_image.png`), `prompt`,
`prompt_enhance` (kapalı), `lora_name`, `lora_strength` (1), `unet_name`, `clip_name`, `vae_name`. Model
hattı `UNETLoader → LoraLoaderModelOnly (krea2_style_reference) → ModelSamplingFlux → CFGGuider /
BasicScheduler → SamplerCustomAdvanced`; resim `TextEncodeQwenImageEditPlus`'tan geçiyor. 8 adım
(`BasicScheduler`), cfg 1 (`CFGGuider`). Hepsi çekirdek node.

**Örnek resim** ✅: stil referansı şablonunun `Load Image`'ı `krea2_reference_image.png`'yi istiyor;
docs.comfy.org adresini veriyor:
`https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/input/krea2_reference_image.png`,
1.497.458 B. Yoksa **Run** durur (484'teki gibi). İki defterde de iner.

**Ham defter şablon dosyası almaz** (brief): kullanıcı Turbo şablonunu ComfyUI'nin kendi **Templates**
listesinden açar. ComfyUI master'ın `requirements.txt`'i `comfyui-workflow-templates==0.11.93`'ü
kuruyor, paket 20 Ekim'de yayımlandı ✅, Krea şablonları Haziran'dan beri depoda; yani listede olmaları
beklenir ≈ (paketin içi okunmadı). Açınca ComfyUI eksik Turbo DiT için bir "missing models" penceresi
gösterir; kapatılır, `unet_name` RAW'a çevrilir.

### 1.2 ComfyUI ✅

Krea 2 ComfyUI'nin kendinde: `CLIPLoader`'ın tür listesinde `"krea2"` var
([nodes.py](https://github.com/comfyanonymous/ComfyUI/blob/master/nodes.py)); `ResolutionSelector`
`comfy_extras/nodes_resolution.py`'de, `TextGenerate`, `ComfySwitchNode`, `StringConcatenate`,
`PrimitiveStringMultiline` de çekirdek eklerin listesinde. Comfy'nin blogu en az 0.26.0 istiyor
([blog](https://blog.comfy.org/p/krea-2-open-source-models-are-now)). Defter master'dan kurar ve
klonda `nodes.py`'de `"krea2"`'yi, `nodes_resolution.py`'de `ResolutionSelector`'ı arar; yoksa durur.

### 1.3 RAW ve Turbo ayarları

- **Turbo:** 8 adım, cfg 1 (ComfyUI'de "cfg yok" 1'dir; Krea'nın LoRA kartları `guidance_scale=0.0`),
  `euler`, `simple` — şablonun kendisi ✅.
- **RAW:** **52 adım, cfg 3,5** ✅ — Krea'nın kartındaki üç örneğin üçü de
  ([krea/Krea-2-Raw](https://huggingface.co/krea/Krea-2-Raw)). Kart RAW'ı *"not recommended for
  inference"* diye anlatıyor: ince ayar ve LoRA eğitimi için ✅. Sampler ve scheduler yazılı değil;
  şablonun `euler` / `simple`'ı kalır ≈.
- **RAW + Turbo LoRA** (`krea2_turbo_lora_rank_64_bf16`): Comfy-Org'un README'si ne işe yaradığını
  yazmıyor ✅. Wulver'ın README'si — RAW'ın bir ince ayarı — onu Non-Turbo dosyada şöyle kullanıyor:
  güç 1,0, 8 adım, cfg 1; ya da güç 0,6, 14 adım, cfg 1; `euler` / `simple` ✅. Çıplak RAW'da aynısı ≈.
  SNOFS'un yazarı da iki aşamalı sampler'ında ilk adımları *"Turbo LoRA'sız"* koşuyor ✅.

### 1.4 Tarz LoRA'ları ve tetik sözcükleri ✅

Comfy-Org README'si ve docs.comfy.org aynı tabloyu veriyor; `darkbrush`'ı Krea'nın kendi kartında da
okudum ([krea/Krea-2-LoRA-darkbrush](https://huggingface.co/krea/Krea-2-LoRA-darkbrush)): güç 1,0,
Turbo için, RAW'da eğitilmiş.

| LoRA | Tetik |
|---|---|
| `krea2_darkbrush` | `monochrome ink wash style` |
| `krea2_dotmatrix` | `monochrome stippling style` |
| `krea2_kidsdrawing` | `naive expressive sketch style` |
| `krea2_neondrip` | `textured abstract style` |
| `krea2_rainywindow` | `rainy window style` |
| `krea2_retroanime` | `purple retro anime style` |
| `krea2_softwatercolor` | `art deco watercolor style` |
| `krea2_sunsetblur` | `ethereal motion blur style` |
| `krea2_vintagetarot` | `vintage tarot style` |

Şablonun `lora_trigger_word` kutusu `muted minimalist sketch style` ile açılıyor — tablodaki hiçbir
LoRA'nın değil ✅; LoRA seçilince tetiği elle yazılır.

**`krea2_style_reference`** ✅: ostris'in LoRA'sı; *"inference on the Krea2 Turbo model in the style of a
reference image"*, bir ya da iki referans resim, **tetik yok** (*"just image and prompt"*)
([ostris/krea2_turbo_style_reference](https://huggingface.co/ostris/krea2_turbo_style_reference)).
Kartı ComfyUI için ostris'in custom node'unu gösteriyor; ama Comfy-Org'un resmî şablonu
(`…_int8_image_style_reference`) aynı işi çekirdek node'larla yapıyor ✅ — custom node inmez. Yani bu
LoRA bir `Load Image` girişi ve kendi şablonunu istiyor; t2i şablonunda resim girişi yok.

---

## 2. İnecek dosyalar

Boyutlar bayt. HF'tekiler HF API'sinin dosya listesinden ✅
([Comfy-Org/Krea-2](https://huggingface.co/api/models/Comfy-Org/Krea-2/tree/main?recursive=true),
`gated: false`; [Vaelico/Wulver](https://huggingface.co/api/models/Vaelico/Wulver/tree/main?recursive=true),
`gated: false`). Civitai'dekiler API'nin `sizeKB × 1024`'ü ✅ (her biri tam bir bayt sayısına çıkıyor),
yalnız disk toplamında; dosya kendi header'ıyla doğrulanır (484'teki gibi).

### 2.1 Hugging Face

| Defter | Klasör | Dosya | Bayt | Adres |
|---|---|---|---|---|
| turbo | `diffusion_models/` | `krea2_turbo_int8_convrot.safetensors` | 13.492.686.496 | https://huggingface.co/Comfy-Org/Krea-2/resolve/main/diffusion_models/krea2_turbo_int8_convrot.safetensors |
| raw | `diffusion_models/` | `krea2_raw_int8_convrot.safetensors` | 13.492.686.496 | https://huggingface.co/Comfy-Org/Krea-2/resolve/main/diffusion_models/krea2_raw_int8_convrot.safetensors |
| ikisi | `text_encoders/` | `qwen3vl_4b_fp8_scaled.safetensors` *(S3)* | 5.242.467.968 | https://huggingface.co/Comfy-Org/Krea-2/resolve/main/text_encoders/qwen3vl_4b_fp8_scaled.safetensors |
| ikisi | `vae/` | `qwen_image_vae.safetensors` | 253.806.246 | https://huggingface.co/Comfy-Org/Krea-2/resolve/main/vae/qwen_image_vae.safetensors |
| ikisi | `loras/` | dokuz tarz LoRA'sı, `krea2_<ad>.safetensors` (1.4) | 9 × 469.291.992 = 4.223.627.928 | https://huggingface.co/Comfy-Org/Krea-2/resolve/main/loras/krea2_<ad>.safetensors |
| ikisi | `loras/` | `krea2_style_reference.safetensors` | 457.111.760 | https://huggingface.co/Comfy-Org/Krea-2/resolve/main/loras/krea2_style_reference.safetensors |
| raw | `loras/` | `krea2_turbo_lora_rank_64_bf16.safetensors` | 469.423.778 | https://huggingface.co/Comfy-Org/Krea-2/resolve/main/loras/krea2_turbo_lora_rank_64_bf16.safetensors |
| turbo | `diffusion_models/` | `Wulver_v0.5_fp8_e4m3fn.safetensors` *(S2, S6)* | 12.821.599.836 | https://huggingface.co/Vaelico/Wulver/resolve/main/Wulver_v0.5_fp8_e4m3fn.safetensors |
| raw *(S5-1)* | `diffusion_models/` | `Wulver_v0.5_non_turbo_int8-convrot.safetensors` | 13.491.966.712 | https://huggingface.co/Vaelico/Wulver/resolve/main/Wulver_v0.5_non_turbo_int8-convrot.safetensors |

### 2.2 Civitai — çerezle, `civitai.red`

| Defter | Klasör | Model · sürüm | Dosya | Bayt *(API)* | İndirme adresi |
|---|---|---|---|---|---|
| ikisi | `loras/` | [SNOFS](https://civitai.com/models/1972981) · Krea 2 v1.5 (3390681) | `snofs_krea_v1_5.safetensors` | 1.562.410.216 | https://civitai.red/api/download/models/3390681 |
| ikisi | `loras/` | [krea2 sex](https://civitai.com/models/2801881) · carry (3170121) | `krea2 standing and carry.safetensors` | 228.587.744 | https://civitai.red/api/download/models/3170121 |
| ikisi | `loras/` | krea2 sex · dog (3158793) | `krea doggy.safetensors` | 228.587.720 | https://civitai.red/api/download/models/3158793 |
| ikisi | `loras/` | krea2 sex · Mis (3169965) | `krea missionary.safetensors` | 228.587.728 | https://civitai.red/api/download/models/3169965 |
| ikisi | `loras/` | krea2 sex · CG (3158775) | `krea cowgirl.safetensors` | 228.587.720 | https://civitai.red/api/download/models/3158775 |
| ikisi | `loras/` | krea2 sex · spo (3169634) | `kea2 spooning.safetensors` | 228.587.720 | https://civitai.red/api/download/models/3169634 |
| ikisi | `loras/` | krea2 sex · BJ (3158893) | `kreablowjob.safetensors` | 228.587.720 | https://civitai.red/api/download/models/3158893 |
| turbo | `diffusion_models/` | [Sick Ollie](https://civitai.com/models/2676616) · Krea2 (3154408), **fp8**, dosya 3035266 | `sickOllie_krea2_3035266.safetensors` | 12.821.587.640 | https://civitai.red/api/download/models/3154408?fileId=3035266 |
| turbo | `diffusion_models/` | [Moody Krea2 Mix](https://civitai.com/models/2731187) · V8.0 BF16 & FP8 (3327123), **fp8_scaled**, dosya 3213091 | `moodyKrea2MixUncensoredV8FREEV8_v80BF16FP8_3213091.safetensors` | 13.141.769.512 | https://civitai.red/api/download/models/3327123?fileId=3213091 |

*(Onaydan sonra, S2'nin kararıyla: yukarıdaki iki satır int8'ten fp8'e döndü. Onaydan önceki int8
seçimleri: Sick Ollie 3035672, 13.148.995.440 B; Moody 3213143, 13.789.287.384 B. Aşağıdaki iki
paragrafta int8 diye anılanlar o seçim.)*

**SNOFS** ✅: model sayfasındaki en yeni Krea 2 sürümü v1.5 (7 Ekim), tabanı "Krea 2", tek dosya, bf16,
1,56 GB. `trainedWords` boş; yazarı *"trained on natural language … not tags"* diyor ✅ — bizim etiket
listelerimizle zayıf kalabilir ≈.

**krea2 sex** ✅: 34 sürümün her biri bir pozisyon LoRA'sı, tek dosya, tabanı "Krea 2", her biri
~229 MB. Genel olanlardan indirme sayısı en yüksek altı seçildi: carry 5.352, dog 4.652, Mis 4.485,
CG 4.475, spo 4.252, BJ 4.100. Daha yeni iki v2 var — BJ2 (3401693), SP2 (3398592) — az indirilmiş
çünkü yeni; seçilmedi. Sürümlerin adları (CG, dog, …) kısa kodlar; **tetik sözcükleri ise uzun dizi
(S1)**.

**Sick Ollie** ✅: sürüm 3154408 "Krea2", tabanı "Krea 2", tür Checkpoint. Beş dosya: bf16 (birincil),
**int8** (3035672), nf4, mxfp8, fp8. Birincil olmadığı için adres `?fileId=3035672` taşır (API'nin kendi
`downloadUrl`'ü bu). Ayarları yazarın açıklamasında: **Euler, Beta, cfg 1, 9 adım**, en iyi
1440 × 1920 ✅. RAW'dan mı Turbo'dan mı türediği yazılı değil; ayarı Turbo'nunki gibi ≈ (S4).

**Moody Krea2 Mix V8.0** ✅: tabanı "Krea 2"; int8 dosyası birincil, adres seçicisiz. Yazar: *"INT8 is
CONVROT"*; ayarlar **Euler A + Beta, 8 adım** (ayrıntı için 12'ye kadar); cfg yazılı değil, örnek
workflow'u cfg 1 ve bir Turbo LoRA'sı kullanıyor ≈. V8 gerçekçi fotoğrafa yönelik (*"RAW-style
photography, skin texture"*) ✅. Aynı sürümde 7,36 GB'lık bir `int4` ve `nvfp4` de var; inmez.

**Wulver v0.5** ✅ — Civitai'deki dosyalar ve HF'teki karşılıkları, SHA256'yla eşlendi:

| Civitai dosyası | Ne | HF'teki adı |
|---|---|---|
| 3249021 *(birincil)* | fp8 e4m3fn, Turbo — yazarın ComfyUI için önerdiği | `Wulver_v0.5_fp8_e4m3fn` |
| **3249141** (13,18 GB) | **int8 ConvRot, Turbo** ← seçilen | `Wulver_v0.5_int8_convrot` (13.491.966.712) |
| 3249022 (13,18 GB) | düz int8, açıklaması yok | `Wulver_v0.5_int8` (13.491.946.328, yalnız SHA listesinde) |
| 3249389 (7,50 GB, Civitai "int8" diyor) | **W4A8** ConvRot; ComfyUI ≥ 0.31, PyTorch cu130 ister | `Wulver_v0.5_w4a8-convrot` (7.681.032.568) |
| 3249146 | GGUF; custom node ister | yalnız Civitai |
| 3249012 `wulverKrea2_v05.json` (2.974 B) | **config değil**, yazarın ComfyUI workflow'u (fp8, 8 adım) | `Wulver_workflow.json` (aynı SHA) |

A100 için **int8 ConvRot (3249141)**: ConvRot ComfyUI'nin tanıdığı int8 (S2'ye bakın); W4A8 Colab'ın
PyTorch'uyla yüklenmez ≈; düz int8'in hangi biçim olduğu yazılı değil. **`.json` gerekmiyor:** yazara
göre *"stock ComfyUI loaders"* yetiyor, ve dosya bir workflow — kullanıcının kuralı yalnız resmî şablon.
Wulver *"full fine-tune of Krea 2 Raw"*; Turbo dosyalarına resmî Turbo LoRA'sı 1,0 güçle katılmış ✅.
Ayarları **8 adım, cfg 1, `euler` / `simple`**, shift 1,15 (Krea'nın ComfyUI varsayılanı), 1024 ✅.
Prompt: *"Detailed descriptive prose works best; booru-style tag lists also work"*; açıklamada
booru / e621; başlık önce bir rating etiketiyle (`sfw, …`), sonra `@sanatçı` (ARTISTS.md'deki 1.113
addan biri, `@` dahil, birebir), sonra tarif ✅. Konusu *"anthro & furry, with strong anime / kemono
range"* ✅ — gerçekçi değil.

**Civitai girişi:** 484'teki yaklaşım, aynen: Secret `CIVITAI_COOKIE`, `__Secure-civ-token`, önce her
dosyaya 1 KB'lık probe. Standardın §4'ü: probe çıplak adresle — seçicili adres probe'da 401 verdi.
Sick Ollie'nin probe'u bu yüzden `…/3154408` (birincil bf16'nın ilk KB'ı; erişimi aynı sürüm için
dener), indirmesi `?fileId=3035266` ile (onaylanan fp8 dosyası; 0.).

---

## 3. Toplamlar 🧮

Ortak (ikisinde): kodlayıcı fp8 + VAE + 9 tarz + stil referansı + SNOFS + 6 pozisyon =
**13.110.950.470 B**.

**Onaylanan seçimle (0.):**

| Defter | Eklenenler | Toplam |
|---|---|---|
| turbo | Turbo DiT int8 + Wulver fp8 + Sick Ollie fp8 + Moody fp8_scaled | **65.388.593.954 B ≈ 65,4 GB (60,9 GiB)** |
| raw | RAW DiT int8 + Turbo LoRA + Wulver Non-Turbo **bf16** (4.7'nin 4'ü) | **52.713.251.872 B ≈ 52,7 GB (49,1 GiB)** |

Onaydan önce hesaplananlar (int8 checkpoint'lerle):

| Defter | Seçim | Toplam |
|---|---|---|
| turbo | + Turbo DiT + Wulver + Sick Ollie + Moody | 67.033.886.502 B ≈ 67,0 GB (62,4 GiB) |
| raw | (S4-1, S5-1): + RAW DiT + Turbo LoRA + Wulver Non-Turbo | 40.565.027.456 B ≈ 40,6 GB (37,8 GiB) |
| raw | S4-2, S5-1: yukarıdaki + Sick Ollie + Moody | 67.503.310.280 B ≈ 67,5 GB (62,9 GiB) |
| raw | S4-2, S5-2 (brief'teki gibi) | 54.011.343.568 B ≈ 54,0 GB (50,3 GiB) |
| raw | S4-1, S5-2 | 27.073.060.744 B ≈ 27,1 GB (25,2 GiB) |

S3'te int8 kodlayıcı da inerse her deftere +4.858.559.240 B. Şablonlar ve resim bunun dışında
(turbo 1.621.141 B, raw 1.497.458 B). Boş disk kontrolü 484'teki gibi: yerinde olmayan her dosyanın
baytı toplanır, +5 GiB pay.

---

## 4. Adımlar, dosya dosya

Her adım bitince burada işaretlenir. Kod 484'ün `turbo.ipynb`'sinden kopyalanır; değişen yalnız
aşağıdakiler. **Onaydan sonra (0.'ın kararları):** Turbo defterinde üçüncü kişilerin dosyaları fp8, yani
orada int8 olan üçüncü kişi dosyası kalmadı; `comfy_int8` yalnız RAW defterinde (Wulver Non-Turbo).

### 4.1 `collab-toolbox/photo_experiments/krea-2/turbo.ipynb` (yeni)

- [x] **Hücre 0 (başlık):** madde 485; Krea 2 Turbo, 8 adım; ne iner (Turbo DiT, tarz LoRA'ları, stil
  referansı, Civitai LoRA'ları, Wulver / Sick Ollie / Moody); ~65,4 GB; sırlar (`CIVITAI_COOKIE`
  zorunlu, `HF_TOKEN` isteğe bağlı); RAW'ın ayrı defterde olduğu.
- [x] **Hücre 1–2 (CONFIG):** 484'ün aynısı; çerez metni "LoRA'lar ve checkpoint'ler".
- [x] **Hücre 3–4 (yardımcılar):** 484'ün aynısı. `comfy_int8` burada yok (yukarıda).
- [x] **Hücre 5–6 (ComfyUI):** master'dan, 484'ün aynısı; Qwen kontrolü yerine `nodes.py`'de
  `"krea2"` ve `comfy_extras/nodes_resolution.py`'de `ResolutionSelector` aranır (1.2).
- [x] **Hücre 7–8 (modeller):**
  - `MODELS` (HF): Turbo DiT, fp8 kodlayıcı, VAE, dokuz tarz LoRA'sı, stil referansı (Comfy-Org);
    Wulver **fp8** (Vaelico). `hf_fetch` değişmez.
  - `CIVITAI` (yeni ad, LoRA'lardan fazlası var): `(sürüm, dosya id ya da None, dosya adı, klasör, bayt,
    etiket)` — SNOFS, altı pozisyon, Sick Ollie, Moody. `civitai_fetch` klasörü bu satırdan alır,
    indirme adresine `?fileId=` yalnız verilmişse eklenir; probe her zaman çıplak adresle.
  - Sıra 484'ün aynısı: boş disk → probe'lar → HF → Civitai → özet (bütün klasörler).
  - Markdown: iki tablo, Wulver'ın neden fp8 ve HF'ten indiği, kodlayıcının neden fp8 olduğu (şablon
    onu istiyor), Civitai notları 484'ün metniyle.
- [x] **Hücre 9–10 (workflow'lar):** `TEMPLATES` = `image_krea2_turbo_t2i_int8.json` ve
  `image_krea2_turbo_int8_image_style_reference.json`; `INPUT_IMAGES` = `krea2_reference_image.png`.
  `place_workflow` ve `place_image` 484'ün aynısı (JSON mu; `models` listesindeki her dosya diskte mi;
  hedefte varsa dokunulmaz).
- [x] **Hücre 11–12 (başlat):** 484'ün aynısı; son satırlar iki workflow'u, LoRA'ların ve
  checkpoint'lerin yerini ve `instructions.md`'yi anar.

### 4.2 `collab-toolbox/photo_experiments/krea-2/raw.ipynb` (yeni)

turbo'nun aynısı, farkları:
- [x] Başlık: RAW, 52 adım, cfg 3,5; ya da Turbo LoRA'sıyla 8 adım; toplam (S4/S5'in seçimine göre);
  şablon dosyası yok, Turbo şablonu ComfyUI'nin Templates listesinden açılır.
- [x] `MODELS`: Turbo DiT yerine RAW DiT; + `krea2_turbo_lora_rank_64_bf16`; Wulver yerine Wulver
  Non-Turbo int8 (fp8'i yok). `CIVITAI`: Sick Ollie ve Moody yok (S4-1); şekli Turbo'nunkiyle aynı.
- [x] Hücre 3–4: + `comfy_int8(path)` — header'da `.comfy_quant` ile biten bir anahtar var mı. Özetin
  sonunda `diffusion_models/`'taki her `*int8*` dosyası için çağrılır (Wulver Non-Turbo, ve
  karşılaştırma için Comfy-Org'un RAW'ı); header bir kez daha okunur (yerel disk, iki dosya). Yoksa
  uyarır, durmaz.
- [x] Hücre 9–10: `TEMPLATES` ve `place_workflow` yok (kullanılmayan kod yazılmaz); yalnız
  `place_image` ve `krea2_reference_image.png`. Markdown: neden şablon yok (resmî RAW şablonu yok;
  Turbo şablonunun DiT'i bu defterde inmiyor, `place_workflow`'un kontrolü onu ister).
- [x] Hücre 12: son satırlar Templates → Krea 2 → `unet_name` → RAW'ı söyler.

### 4.3 `collab-toolbox/photo_experiments/krea-2/indirilecekler.md` (yeni)

484'ünkinin düzeni: şablonlar (1.1), defterin kendi modeli, ikisinde de — HF, Civitai (2.2'nin
tabloları, çerez, bayt sayısının yalnız disk toplamında olduğu), Wulver'ın dosya eşlemesi, örnek resim,
toplamlar (3.), inmeyenler (bf16 / fp8 / mxfp8 / nvfp4 DiT'ler, int8 ve bf16 kodlayıcı, fp8 t2i şablonu,
Wulver'ın fp8 / düz int8 / W4A8 / GGUF / `.json`'u, Sick Ollie'nin ve Moody'nin öteki hassasiyetleri,
ostris'in custom node'u), klasör düzeni.
- [x] Yazıldı.

### 4.4 `collab-toolbox/photo_experiments/krea-2/instructions.md` (yeni)

Kısa, Türkçe, test planı yok.
- [x] **Çalıştırma:** Secrets'a `CIVITAI_COOKIE` (tek satır nasıl) → A100 → Run all → link.
- [x] **Hangi şablon:** `image_krea2_turbo_t2i_int8` — prompt'tan resim; `…_int8_image_style_reference`
  — referans resmin tarzında (`image1`'e resim, bir ya da iki; tetik yok). Ham defterde: sol kenarda
  **Templates** → Krea 2 → int8 *Text to Image*; eksik model penceresi kapatılır.
- [x] **`prompt_enhance`:** t2i'de açık geliyor; prompt'u Qwen3-VL düzyazıya yeniden yazar. Bizim
  prompt'umuzu olduğu gibi denemek için kapat.
- [x] **Model değiştirmek:** büyük node'da `unet_name` → RAW, Wulver, Sick Ollie, Moody.
- [x] **RAW ile Turbo:** Turbo 8 adım, cfg 1, `euler` / `simple`. RAW 52 adım, cfg 3,5. RAW + Turbo
  LoRA: güç 1,0, 8 adım, cfg 1 (ya da 0,6 / 14 adım / cfg 1). Adım ve cfg dışa açık değil: alt grafiğe
  gir, `KSampler` (stil referansında `BasicScheduler`'ın `steps`'i ve `CFGGuider`'ın `cfg`'si). cfg 1'de
  negatif hiçbir şey yapmaz.
- [x] **Checkpoint ayarları, birer satır:** Sick Ollie — Euler, Beta, cfg 1, 9 adım, 1440 × 1920;
  Moody — Euler A, Beta, 8 adım (12'ye kadar); Wulver — 8 adım, cfg 1, `euler` / `simple`. Wulver'da
  `sfw, @sanatçı, …` sırası; `@sanatçı` 1.113 tarzdan biri (ARTISTS.md, birebir); düzyazı en iyi, ama
  booru / e621 etiketleri de çalışıyor — bizim prompt'larımız etiket listesi. Wulver'ın konusu anthro /
  furry, anime / kemono.
- [x] **LoRA eklemek:** t2i şablonunun kendi tek LoRA yuvası var: `enable_lora`'yı aç, `lora_name`,
  `lora_strength`, `lora_trigger_word` (prompt'un sonuna eklenir; tetiği olmayanda boşalt). Birden
  fazlası için alt grafiğe gir, şablonun `LoraLoaderModelOnly`'si ile `Switch (Model)`'ın `on_true`'su
  arasına yeni `LoraLoaderModelOnly`, `enable_lora` açık. Stil referansında: şablonun
  `LoraLoaderModelOnly`'si (`krea2_style_reference`) ile `ModelSamplingFlux` arasına.
- [x] **Tetik sözcükleri:** dokuz tarz LoRA'sı (1.4), güç 1,0; stil referansında tetik yok; SNOFS'ta
  tetik yok, düzyazıyla eğitilmiş; pozisyon LoRA'larının tetikleri (S1'e göre).
- [x] **Tek satır:** Civitai'nin NSFW LoRA'ları ve checkpoint'leri gerçekçi fotoğraf tarzında (Wulver
  hariç, o anime / furry).

### 4.5 `collab-toolbox/README.md`

- [x] `photo_experiments/` satırına: `krea-2/` Krea 2'yi dener, Turbo ve RAW için birer defter, resmî
  ComfyUI şablonlarıyla.

### 4.6 Bitiş

- [x] İki defterin kod hücreleri yerelde `ast.parse` ile ayrıştırıldı, iki `.ipynb` geçerli JSON;
  iki şablonun `models` listesi (1.1) Turbo'nun `MODELS`'ında (eksik yok); `MODELS` + `CIVITAI`
  koddan toplandı: turbo 65.388.593.954 B, raw 40.565.027.456 B — 3.'tekiyle aynı. Colab'da koşmak
  kullanıcının işi.
- [x] Dört suite koşuldu (defterlere test yok; değişmediklerini gösterirler): queen-agent 1232 passed,
  queen-agent/frontend 931 passed, queen-editor 1909 passed, queen-editor/frontend 934 passed.
- [x] Yol haritasına dokunulmaz; commit ana ajanın.

### 4.7 Reviewer'ın düzeltmeleri *(21 Ekim; reviewer 485'i geçirdi, bunlar ana ajanın listesi)*

- [x] **1. cfg 3,5'te negatif.** t2i şablonunun negatifi `ConditioningZeroOut`; Wulver'ın README'si cfg
  1'in üstünde boş bir `CLIPTextEncode` istiyor. `instructions.md`'nin "Adım ve cfg"sine bir paragraf ve
  `raw.ipynb`'nin son çıktısına aynı not: alt grafikte boş bir `CLIPTextEncode`, `clip`'i
  `CLIPLoader`'dan, `KSampler`'ın `negative`'ine `ConditioningZeroOut` yerine. "LoRA'sız koşarken negatif
  boş kalır" çıktı.
- [x] **2. Tetik bağlantıları** `https://civitai.red/models/2801881?modelVersionId=<id>`.
- [x] **3. `comfy_int8`** `"_quantization_metadata" in (header.get("__metadata__") or {})`'yi de kabul
  ediyor; docstring ve hücre 3'ün markdown'u iki işareti de anıyor.
- [x] **4. Wulver Non-Turbo bf16** (ana ajanın kararı): `Wulver_v0.5_non_turbo_bf16.safetensors`,
  25.640.191.128 B, HF. `MODELS`, toplamlar (raw 52.713.251.872 B), defterin markdown'u, son çıktı,
  `instructions.md` ve `indirilecekler.md`. `comfy_int8` Comfy-Org'un RAW int8'i için kalıyor; özetin
  yorumu ve mesajı buna göre.
- [x] **5. Büyük Civitai dosyaları:** `--max-time 3600` yerine `--speed-limit 1048576 --speed-time 300`,
  `run`'ın süresi 4 saat. İki defterde de; markdown'larda ve `indirilecekler.md`'de bir cümle.
- [x] **6. `fileId`'li indirmede bayt kontrolü:** `civitai_fetch` artık `size` alıyor; `file_id` varsa
  dosya hem yerindeyken hem `.part`'tan sonra `settled(..., "Civitai API")` ile API'nin sayısına tutuluyor.
  `settled`'ın yeni `counted_by` argümanı mesajı söylüyor ("HF listesi" varsayılan). İki defterde de
  aynı yardımcılar.
- [x] **7. Belge doğruluğu:** `indirilecekler.md`'de 3327123'ün int4, nvfp4 ve int8'i de taşıdığı; Moody'nin
  ayarları V6'nın notu olarak; gerçekçilik notu yalnız Moody V8 için (kaynaklı), ötekiler doğrulanmadı;
  Comfy-Org int8'inin işareti "beklenir, görmedik — RAW'ın özeti bakıyor" (`indirilecekler.md`, raw
  hücre 7, turbo hücre 8'in yorumu); bu planda Sick Ollie'nin `fileId`'i 3035266.
- [x] Yerelde: iki defterin kod hücreleri `ast.parse`'tan geçti; `MODELS` + `CIVITAI` koddan: turbo
  65.388.593.954 B, raw 52.713.251.872 B.

---

## 5. Maliyet ve bozulabilecekler

- **İstekler:** her dosya bir kez iner; yerinde olan için ağa gidilmez. Civitai başına bir 1 KB probe +
  bir indirme; şablon ve resim başına bir istek, yalnız yoksa. N dosyada O(N).
- **Çerez yok ya da bayat:** CONFIG'de ya da probe'larda, ağır bir şey inmeden durur.
- **Yarım dosya:** HF `hf_stage`'de, Civitai `.part`'ta doğrulanır, sonra `os.replace`; `.part` bir
  sonraki koşuda yargılanır (484'ün 4.6'sı).
- **ComfyUI'nin tanımadığı int8:** özet söyler (S2), koşu durmaz.
- **Kullanıcının kaydı:** Workflows'ta ve `input/`'ta aynı adla dosya varsa dokunulmaz.

---

## 6. Doğrulanamayanlar

- **Pozisyon LoRA'larının tetikleri** (S1): `instructions.md` sürüm sayfalarına bağlanıyor.
- **Wulver Non-Turbo int8'inin ComfyUI'de yüklenmesi** (S2): RAW defterinin özeti `comfy_quant`'a
  bakıyor. Comfy-Org'un int8'lerinin işareti taşıdığı da kendi gözümle görülmedi; özet onu da basıyor.
- **Sick Ollie fp8'inin biçimi:** düz e4m3fn mi scaled mı yazılı değil; ikisini de ComfyUI A100'de bf16'ya
  çevirip okur ≈.
- **Sick Ollie ve Moody'nin RAW'dan mı Turbo'dan mı türediği** (S4).
- **Çıplak RAW'da Turbo LoRA'sı:** kaynak Wulver'ın README'si, RAW'ın bir ince ayarı için ≈.
- **RAW'ın sampler'ı ve scheduler'ı:** yazılı değil ≈.
- **Templates listesinde Krea şablonları:** paketin içi okunmadı ≈.
- **fp8 kodlayıcının A100'de hızı** ≈.
- **Krea'nın tarz LoRA'larının, Civitai LoRA'larının ve stil referansının RAW'da etkisi:** hepsi
  Turbo'da kullanılmak için; RAW'da denenmemiş ≈.
- **NSFW davranışı** Krea 2'nin kendisinde belgelenmemiş (yol haritası).
- **Civitai dosyalarının içi:** giriş gerektiği için header'ları okunamadı; bayt sayıları API'den.
