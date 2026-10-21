# Madde 484 · Qwen 2.1: karakter referansı, NSFW LoRA'ları ve Noct Q — Colab deneme kurulumu — plan

**Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md), 484 · v10-8 ·
**Dal:** `feat/queen-editor-v10` · **Spec yok:** madde kullanıcıyla birlikte yapılıyor; bu plan onun
yerini tutar. **Önce:** 482'nin defterleri
([collab-toolbox/photo_experiments/qwen-image-21/](../../collab-toolbox/photo_experiments/qwen-image-21/),
commit 3ed92e61) ve [482'nin araştırması](../research/2026-10-20-queen-editor-m482-qwen-image.md).

**Kullanıcının istediği (21 Ekim):** Colab oturumu gitti; defterler bir kez, baştan koşacak, ve **her şey
baştan iner** *("her şey indir abi sonra deneriz en verimlisi gibi")*. Sonradan yeni bir LoRA gerekirse
ComfyUI yeniden başlatılır, bu kabul. Hem normalde hem Turbo'da, bu sırayla:

1. resmî Qwen Image 2.1 **Image Edit** şablonunda karakter referansı: portreler resim girişlerine
   verilir, model aynı karakteri yeni bir sahnede çizer;
2. ana modelin üstünde **NSFW LoRA'ları**: LoRA yükleyici node'unu kullanıcı elle ekler ve listeden
   seçer, yeniden koşu gerekmez;
3. **Noct Q V4** checkpoint'i, karakter referansı da onunla.

**Kullanıcının kuralları:** iki ayrı defter kalır; workflow yazılmaz ve üretilmez, yalnız resmî şablonlar
kaynağından olduğu gibi iner (yazarın kendi workflow'u da olduğu gibi, adıyla); `instructions.md` kısa
kalır; doldurulacak yeni bir seçenek yok, her şey varsayılan olarak iner; boş disk kontrolü yeni toplamı
doğru tutar.

İşaretler: **✅** kaynaktan ya da dosyanın kendisinden doğrulandı · **≈** doğrulanmadı.

---

## 0. İki soru — kararlaştı

**Ana ajan 21 Ekim'de onayladı:** S1'de 1 (Turbo defteri de Noct Q V4'ü ve resmî Turbo LoRA'sını indirir;
`instructions.md` bu ikilinin hiçbir kaynakta denenmediğini açıkça söyler), S2'de evet. Ve iki ek:
`instructions.md`'ye cfg için bir satır; Civitai dosyaları API'nin bayt sayısına tutulmaz (aşağıda,
3.).

**S1. Noct Q Turbo defterine de girsin mi?**
Noct Q V4 yalnız **Base** olarak var: Civitai'deki sürümün adı *"V4.0 Base"*, ayarları 25 adım, `euler`,
`simple`, **cfg 3** ve negatif prompt ✅ ([Civitai API, model 2958896](https://civitai.com/api/v1/models/2958896),
[HF kartı](https://huggingface.co/Noctaluna/Noct-Q-Uncensored-Qwen-Image-2.1/blob/main/README.md)).
Yazarın Turbo'su V3'te kaldı — *"V3.0 Turbo (Experimental)"*, 6 adım, cfg yok, yalnız Civitai'de; HF'te
yok ✅. V4'ün Turbo'su yok. Turbo şablonu ise ayrı Turbo checkpoint'ini 8 adımlık elle verilmiş bir
sigma dizisiyle (`ManualSigmas`) koşuyor ✅; bu dizide bir Base modeli düzgün resim vermez ≈.

1. **Önerilen — ikisinde de, Turbo'da resmî Turbo LoRA'sıyla.** Comfy-Org'un README'si: *"For faster
   inference, use either the full Turbo model, or the Turbo LoRA extracted from the base model. Use 8
   steps and cfg 1."* ✅ ([README](https://huggingface.co/Comfy-Org/Qwen-Image-2.1/blob/main/README.md)).
   Noct Q V4 Base'in bir *merge*'ü ✅ (kartında `base_model_relation: merge`). Turbo defteri Noct Q V4'ü
   ve resmî Turbo LoRA'sını da indirir; kullanıcı Turbo şablonunda `unet_name`'i Noct Q'ya çevirir ve
   Turbo LoRA'sını NSFW LoRA'ları gibi elle ekler. **Çalıştığı doğrulanmadı ≈**: hiçbir kaynak Turbo
   LoRA'sını Noct Q'nun üstünde denemedi. Turbo defterine +8,17 GB.
2. Yalnız normal defterde. Turbo'da Noct Q denenmez; en sade ve kaynakların söylediğiyle tam uyumlu.
3. Turbo'da yazarın kendi Turbo'su: `V3.0 Turbo (Experimental)`, int8, 7.256.784.376 B, Civitai'den
   çerezle. V4 değil V3, ve 6 adım için yapılmış; resmî Turbo şablonunun 8 adımlık dizisiyle nasıl
   çalıştığı bilinmiyor.

**S2. Edit şablonlarının örnek resimleri insin mi?** Şablonlardaki `Load Image` node'ları Comfy'nin
örnek resimlerini adıyla istiyor (normal: `portrait_model_denim.png`, `clothing_light_blue_denim_shirt.png`;
Turbo: `ballet_dancer_photography_minimalist_architecture.png`), ve şablonun kendi *"Input Assets"* notu
adreslerini veriyor ✅. Dosya `ComfyUI/input/`'ta yoksa **Run** resmi yükleyemez ve durur. Kullanıcı
zaten kendi portrelerini yükleyecek. **Önerilen: insin** (toplam ~3,7 MB, üç istek): şablon önce olduğu
gibi bir kez koşup çalıştığını gösterir, sonra portreler konur — 482'nin "şablon dokunulmadan çalışsın"
ilkesi.

---

## 1. İnecek yeni dosyalar

Boyutlar bayt olarak. HF'tekiler HF API'sinin dosya listesinden ✅
([Comfy-Org](https://huggingface.co/api/models/Comfy-Org/Qwen-Image-2.1/tree/main?recursive=true),
[Noctaluna](https://huggingface.co/api/models/Noctaluna/Noct-Q-Uncensored-Qwen-Image-2.1/tree/main?recursive=true)).
Civitai'dekiler API'nin `sizeKB × 1024`'ü ✅ (her biri tam bir bayt sayısına çıkıyor; dosyanın kendisi
girişsiz okunamadı).

### 1.1 Resmî Edit şablonları ✅

[Comfy-Org/workflow_templates](https://github.com/Comfy-Org/workflow_templates/tree/main/templates)'te
21 Ekim'de okundu:

| Defter | Şablon | Bayt | Ham adres |
|---|---|---|---|
| normal | `image_qwen_image_2_1_image_edit.json` | 96.740 | https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/image_qwen_image_2_1_image_edit.json |
| turbo | `image_qwen_image_2_1_turbo_image_edit.json` | 100.358 | https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/image_qwen_image_2_1_turbo_image_edit.json |

İkisinin `models` listesi ✅:

- normal: `diffusion_models/qwen_image_2.1_int8_convrot`, `text_encoders/qwen3vl_8b_int8_convrot`,
  `vae/qwen_image_2.1_vae_bf16`, `text_encoders/qwen3.5_9b_qwen_image_2.1_pe_i2i.int8_convrot`;
- Turbo: aynısı, DiT yerine `qwen_image_2.1_turbo_int8_convrot`.

Yani t2i şablonlarına göre tek yeni dosya **`pe_i2i`**. Yükleyicileri ✅: `UNETLoader`, `CLIPLoader`
(`qwen_image`), `VAELoader`, ve prompt geliştirici için ikinci bir `CLIPLoader` (node 477, `mode 0`, yani
etkin). Geliştiricinin çıktısı t2i'deki gibi `ComfySwitchNode`'dan geçiyor (`refine_prompt: false`).
**482'nin gerekçesi aynen geçerli:** ComfyUI çıktıya bağlı her yükleyicinin dosyasını listede arar,
tembel dal da dahil; dosya yoksa **Run** `Value not in list` ile durur. Bu yüzden `pe_i2i` iner.

### 1.2 Hugging Face

| Defter | Klasör | Dosya | Bayt | Adres |
|---|---|---|---|---|
| ikisi | `text_encoders/` | `qwen3.5_9b_qwen_image_2.1_pe_i2i.int8_convrot.safetensors` | 9.471.072.252 | https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/text_encoders/qwen3.5_9b_qwen_image_2.1_pe_i2i.int8_convrot.safetensors |
| normal (+ turbo, S1-1) | `diffusion_models/` | `NoctQ_V4_int8_convrot.safetensors` | 7.256.784.368 | https://huggingface.co/Noctaluna/Noct-Q-Uncensored-Qwen-Image-2.1/resolve/main/NoctQ_V4_int8_convrot.safetensors |
| turbo (S1-1) | `loras/` | `qwen_image_2.1_turbo_lora_avg_rank_178_bf16.safetensors` | 913.314.512 | https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/loras/qwen_image_2.1_turbo_lora_avg_rank_178_bf16.safetensors |

Noct Q deposu açık (`gated: false`), yolu kökte, `diffusion_models/` alt klasörü yok ✅. Metin
kodlayıcısı ve VAE'si Comfy-Org'unkilerin aynısı ✅ (kartı), yani başka bir şey inmez.

### 1.3 Yazarın workflow'u — yalnız normal

| Dosya | Bayt | Adres |
|---|---|---|
| `NoctQ_V4_workflow.json` | 7.251 | https://huggingface.co/Noctaluna/Noct-Q-Uncensored-Qwen-Image-2.1/resolve/main/NoctQ_V4_workflow.json |

Olduğu gibi Workflows paneline konur, değiştirilmez. İçi ✅: yalnız çekirdek node'lar (`UNETLoader`,
`CLIPLoader`, `VAELoader`, `TextEncodeQwenImage21`, `EmptyLatentImage`, `KSampler`, `VAEDecode`,
`SaveImage`), t2i, 25 adım, cfg 3, 1024 × 1536; `models` listesinde metin kodlayıcı ve VAE var. Turbo
defterine girmez: Base ayarlarıyla geliyor.

### 1.4 Civitai — NSFW LoRA'ları, ikisinde de, `loras/`

[Civitai API](https://civitai.com/api/v1/models?baseModels=Qwen%202.1&types=LORA&nsfw=true&sort=Most%20Downloaded)'sinden,
21 Ekim. Her birinin en son sürümünün taban modeli **"Qwen 2.1"** ✅.

| Model | Sürüm (id) | Dosya | Bayt | İndirme adresi |
|---|---|---|---|---|
| [NSFW LORA \| Qwen Image 2.1](https://civitai.com/models/2958918) — TheseAlpacas, 38 bin indirme | v2.0 (3357315) | `NSFW Qwen by TheseAlpacas V2.safetensors` | 79.744.352 | https://civitai.red/api/download/models/3357315 |
| [Qwen Image 2.1 - FemaledVaginus-NSFW](https://civitai.com/models/2986844) — tawsLoRa | v1.3b (3388157) | `qwen2_1-femaledVaginus-nsfw-v1_3-fine_L22-31.safetensors` | 637.587.392 | https://civitai.red/api/download/models/3388157 |
| [NSFW UNLOCKED [LORA]](https://civitai.com/models/2063193) — The_Midnight_Lab, 39 bin indirme (bütün tabanlar) | Qwen2.1_V1 (3392016) | `Qwen_2.1_Unlocked_V1.safetensors` | 50.390.941 | https://civitai.red/api/download/models/3392016 |
| [nsfw-posture-v3](https://civitai.com/models/2988215) — ynamely | v1.0 (3388118) | `nsfw-posture-v3.safetensors` | 83.943.880 | https://civitai.red/api/download/models/3388118 |

**Toplam: 851.666.565 B ≈ 0,85 GB.** Her sürümde tek bir model dosyası var, seçici (`?fileId=`)
gerekmiyor.

**Neden bunlar.** Geniş NSFW olanlar seçildi, birbirinin kopyası olanlar değil:
- 2958918: cinsel sahneler ve anatomi geniş bir yelpazede (kartı: blowjob, cowgirl, doggystyle, missionary,
  anal…); en çok indirilen Qwen 2.1 NSFW LoRA'sı.
- 2986844: kartı *"General NSFW Enhancer"* — kadın ve erkek anatomisi, pozisyonlar.
- 2063193: çıplaklık; tetik sözcükleri *"nude, big round boobs, topless"*. Model sayfası birden çok
  taban için; Qwen 2.1 sürümü en son sürüm.
- 2988215: pozisyonlar (oral, göğüs, ayak).

**Elenenler:** 2976277 ve 2960871 — ikisi de yalnız vajina, 2986844'ün bir parçasının kopyası; 2983070
*Full Body* — yine yalnız genital bölge, ve aynı hash'li iki dosya; 2955779 — yazarı paralı yaptığını
yazıyor; 2027766 BFS — yüz değiştirme; Lenovo / NiceGirls / SamsungCam UltraReal — yalnız gerçekçilik.

**Kartların önerdiği ayarlar** (bilgi için, defter hiçbirini koymaz): 2958918 25+ adım, cfg 3–6,
`er_sde` + `beta`, güç 0,8–1; 2986844 güç 0,7–1, `er_sde` + `beta`, cfg 3, 20 adım; 2063193 cfg 3,5,
güç 0,5–0,9. Hepsi cfg > 1 öneriyor; şablonlar cfg 1'de açılıyor.

**Civitai girişi gerekiyor ✅.** Dördünün de çıplak adresi girişsiz istenince
`401 {"error":"Unauthorized","message":"The creator of this asset requires you to be logged in to download it"}`
dönüyor (21 Ekim, 64 baytlık bir range isteğiyle denendi).

### 1.5 Şablonların örnek resimleri (S2) — `ComfyUI/input/`

| Defter | Dosya | Bayt | Adres |
|---|---|---|---|
| normal | `portrait_model_denim.png` | 1.181.250 | https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/input/portrait_model_denim.png |
| normal | `clothing_light_blue_denim_shirt.png` | 1.366.572 | https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/input/clothing_light_blue_denim_shirt.png |
| turbo | `ballet_dancer_photography_minimalist_architecture.png` | 1.134.190 | https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/input/ballet_dancer_photography_minimalist_architecture.png |

Boyutlar GitHub'ın contents API'sinden ✅.

---

## 2. Yeni toplamlar (model dosyaları; şablonlar ve PNG'ler eklenmedi, ~3,9 MB)

| Defter | 482 | Eklenen | **Yeni toplam** |
|---|---|---|---|
| normal | 26.754.163.364 | `pe_i2i` + Noct Q V4 + 4 LoRA | **44.333.686.549 B ≈ 44,3 GB (41,3 GiB)** |
| turbo, S1-1 | 26.754.168.129 | `pe_i2i` + Noct Q V4 + Turbo LoRA + 4 LoRA | **45.247.005.826 B ≈ 45,2 GB (42,1 GiB)** |
| turbo, S1-2 | 26.754.168.129 | `pe_i2i` + 4 LoRA | 37.076.906.946 B ≈ 37,1 GB (34,5 GiB) |

Boş disk kontrolü 482'deki gibi: henüz yerinde olmayan her dosyanın baytı toplanır, +5 GiB pay.

---

## 3. Civitai çerezi

Çerez **gerekiyor**, Colab Secret adı **`CIVITAI_COOKIE`** — queen-editor'ün ve
[NOTEBOOK-STANDARD.md](../../collab-toolbox/NOTEBOOK-STANDARD.md) §4'ün adı, aynı Google hesabındaki tek
sır bütün defterlere yeter. Yaklaşım queen-editor'den
([colab/downloads.py](../../queen-editor/colab/downloads.py): `civitai_url`, `cookie_header`,
`civitai_probe`, `fetch`) ve standardın örneğinden
([ltx23-eros.ipynb](../../collab-toolbox/video_experiments/ltx23-eros/ltx23-eros.ipynb)):

- adres `https://civitai.red/api/download/models/<sürüm>`, başlık `Cookie: __Secure-civ-token=<değer>`;
  `?token=` API anahtarı yok;
- önce **probe**: her dosyanın ilk 1 KB'ı çerezle istenir, `downloads.py`'nin bayraklarıyla
  (`--max-time 20 --limit-rate 200k`); 2xx gelmezse ya da 9. bayttan başlayan bir safetensors header'ı
  (`{"`) yoksa hücre Civitai'nin kendi cevabıyla durur;
- indirme tek bağlantılı `curl -L --fail-with-body` ile: Civitai depoya yönlendiriyor, B2 çerez gidince
  403 veriyor, curl ise başka bir hosta çerezi taşımıyor;
- **doğrulama yalnız safetensors header'ıyla**, queen-editor'deki gibi (`_settled` → `check_safetensors`):
  header'daki `data_offsets` dosyanın nerede bitmesi gerektiğini söyler, yarım ya da hata sayfası olan
  dosya durur. Header dosyanın boyunu zaten kanıtlıyor; API'nin `sizeKB`'ı yalnız disk toplamında
  kullanılır. Probe'un
  `Content-Length` / `Content-Range`'i de okunmaz: standardın §3'ü boyutu başlıktan sormayı yasaklıyor
  (HF Xet'in 403 gövdesi bir kez "boyut" diye okunmuştu), ve `downloads.py` da sormuyor;
- **ayna yok:** queen-editor denemedeki dosyaları aynaya koymuyor (madde 327, `MIRRORLESS`); bunlar da
  deneme dosyası, doğrudan Civitai'den iner;
- değer hiçbir yere basılmaz: CONFIG yalnız "okundu" der; hata mesajları curl'ün stderr'ini ve
  Civitai'nin gövdesini basar, komut satırını değil.

---

## 4. Adımlar, dosya dosya

Her adım bitince burada işaretlenir.

### 4.1 `collab-toolbox/photo_experiments/qwen-image-21/normal.ipynb`

- [x] **Hücre 0 (başlık):** madde 484'ü ve yeni sırayı yaz: Edit şablonu (karakter referansı), LoRA'lar,
  Noct Q; toplam ~44,3 GB; gereken sırlar (`CIVITAI_COOKIE` zorunlu, `HF_TOKEN` isteğe bağlı).
- [x] **Hücre 1–2 (CONFIG):** `CIVITAI_COOKIE` Secrets'tan okunur, standardın iki assert'iyle (okundu mu;
  200 karakterden uzun mu — her biri hangi hatayı yakaladığını söyler). Değer basılmaz. Drive mount
  hâlâ yok. Yeni doldurulacak seçenek yok.
- [x] **Hücre 7–8 (modeller):**
  - `MODELS`'a iki satır: `pe_i2i` (Comfy-Org) ve Noct Q V4 (Noctaluna). Satırın ilk alanı zaten repo,
    `hf_fetch` değişmez.
  - Yeni `LORAS` listesi: `(sürüm id, dosya adı, bayt, etiket)`, 1.4'teki dört satır.
  - Civitai yardımcıları bu hücrede, `hf_fetch`'in yanında: `civitai_url`, `cookie_header`,
    `civitai_probe`, `civitai_fetch`; LoRA'ların yolu `target_of(dosya, "loras")`. `civitai_fetch`: hedef
    varsa `settled` ile doğrular ve atlar (`settled`'ın bayt sayısı isteğe bağlı olur); yoksa önceki
    koşudan kalan `.part`'ı curl'den önce yargılar (4.6'nın 1'i) ve `<hedef>.part`'a iner
    (`curl -C -`), header'la doğrular, sonra `os.replace` ile yerine konur.
  - Sıra: **disk kontrolü** (`MODELS` + `LORAS`, yerinde olmayanlar) → **dört probe** → HF indirmeleri
    → Civitai indirmeleri. İkisi de ağır indirmeden önce: eksik ya da bayat bir çerez 44 GB'tan sonra
    değil, ilk dakikada görünür.
  - Özet `loras/`'ı da listeler.
  - Markdown: yeni tablo, `pe_i2i`'nin neden indiği (482'nin paragrafı Edit şablonu için), LoRA'ların
    Civitai'den çerezle indiği.
- [x] **Hücre 9–10 (şablonlar):** tek şablon yerine bir liste: `image_qwen_image_2_1_t2i.json` ve
  `image_qwen_image_2_1_image_edit.json` (Comfy-Org), `NoctQ_V4_workflow.json` (Noctaluna, HF).
  Her biri için hücre 10'un bugünkü mantığı aynen: hedefte varsa dokunulmaz; yoksa `.part`'a iner, JSON
  mu bakılır, `models` listesindeki her dosya diskte mi bakılır, sonra `os.replace`. Ardından
  S2: örnek resimler `ComfyUI/input/`'a — yoksa iner, PNG imzasıyla başlıyorsa yerine konur (GitHub'ın
  bayt sayısına tutulmaz: resmi Comfy-Org değiştirirse defter boşuna durmasın; yarım aktarımı curl
  kendisi hata sayar); varsa dokunulmaz (kullanıcının aynı adla yüklediği bir resim ezilmez). Markdown:
  kaynak adresler, yazarın workflow'unun olduğu gibi konduğu.
- [x] **Hücre 12 (başlat):** son satırlar üç workflow'u ve LoRA'ların `loras/`'ta olduğunu söyler;
  `instructions.md`'ye yollar.

### 4.2 `collab-toolbox/photo_experiments/qwen-image-21/turbo.ipynb`

normal'in aynısı, farkları:
- [x] `MODELS`: `pe_i2i`, Noct Q V4 ve resmî Turbo LoRA'sı (S1-1).
- [x] Şablonlar: `image_qwen_image_2_1_turbo_t2i.json` ve `image_qwen_image_2_1_turbo_image_edit.json`;
  Noct Q'nun workflow'u yok.
- [x] Örnek resim: `ballet_dancer_photography_minimalist_architecture.png`.
- [x] Başlık ve özet toplamı: ~45,2 GB; başlık ve modeller bölümü Noct Q + Turbo LoRA ikilisinin hiçbir
  kaynakta denenmediğini söyler.

### 4.3 `collab-toolbox/photo_experiments/qwen-image-21/indirilecekler.md`

- [x] Şablon tablosuna iki Edit şablonu ve Noct Q'nun workflow'u.
- [x] "Defterin kendi modeli" ve "İkisinde de" tablolarına 1.2'nin satırları; Noct Q'nun ve Civitai'nin
  kendi bölümleri (1.4'ün tablosu, çerezin gerektiği, bayt sayısının yalnız disk toplamında olduğu);
  örnek resimler.
- [x] Yeni toplamlar (2.).
- [x] "Prompt geliştirici neden iniyor" Edit'in `pe_i2i`'sini de kapsar.
- [x] "İnmeyenler"den `pe_i2i` ve Turbo LoRA'sının satırları çıktı; geliştiricilerin `w4a8`'leri ve Noct
  Q'nun öteki hassasiyetleri girdi.
- [x] Klasör düzenine `loras/`, `input/` ve yeni workflow'lar.

### 4.4 `collab-toolbox/photo_experiments/qwen-image-21/instructions.md`

Kısa; test planı yok, tablo yok. 482'nin prompt listesi olduğu gibi kalır. Bugünkü "Çalıştırma"
tablosu iki madde satırına döner.
- [x] **Çalıştırma:** Secrets'a `CIVITAI_COOKIE` (nasıl alınır, tek satır) → A100 → Run all → link.
- [x] **Hangi şablon:** t2i — prompt'tan resim; Edit — karakter referansı; `NoctQ_V4_workflow` —
  yazarın kendi ayarları (yalnız normal).
- [x] **Portreler:** Edit şablonunda `image_1` düzenlenen resim, `image_2`–`image_10` referans; prompt'ta
  `<image1>`, `<image2>` diye anılır ✅ (şablonun notu). Şablonda yalnız `image_1` ve (normalde)
  `image_2`'ye bağlı `Load Image` var; fazlası için yeni bir `Load Image` eklenip `image_3`…'e bağlanır.
  Çıktının boyutu `image_1`'den gelir; başka bir boyut için `custom_size` açılır ✅.
- [x] **Noct Q'ya geçmek:** büyük node'daki `unet_name` → `NoctQ_V4_int8_convrot.safetensors` ✅
  (`unet_name` alt grafiğin girdisi, node'un üstünde görünüyor). Turbo için: aynı seçim + Turbo
  LoRA'sı, ve bu ikilinin hiçbir kaynakta denenmediği açıkça yazılı.
- [x] **cfg, tek satır** *(ana ajanın eki)*: Noct Q ve LoRA kartları cfg > 1 öneriyor; cfg 1 negatifi yok
  sayar ve yaklaşık iki kat hızlı (Noct Q'nun kartı: *"cfg 1 runs about twice as fast and then ignores
  the negative prompt"*); `cfg` büyük node'un üstünde.
- [x] **LoRA eklemek, tek satır:** alt grafiğe gir, `Load Diffusion Model` (`UNETLoader`) ile
  `QwenImage21Cache` arasına `LoraLoaderModelOnly` ekle, `lora_name`'den seç ✅ (node adı
  [docs.comfy.org](https://docs.comfy.org/tutorials/image/qwen/qwen-image-2-1)'da; model hattı dört
  şablonda da `UNETLoader → QwenImage21Cache → KSampler / CFGGuider`).

### 4.5 Bitiş

- [x] İki defterin bütün kod hücreleri `ast.parse` ile ayrıştırılır, iki `.ipynb` geçerli JSON (yerel,
  indirmesiz); diff yalnız hücrelerin `source`'una dokunuyor. Ayrıca indirilen beş workflow'un `models`
  listesi defterlerin `MODELS`'ıyla karşılaştırıldı: eksik yok, ve iki toplam (2.) koddan aynı çıkıyor.
  Colab'da koşmak kullanıcının işi.
- [x] Dört suite koşuldu (defterlere test yok; değişmediklerini gösterirler): queen-agent 1232 passed,
  queen-agent/frontend 931 passed, queen-editor 1909 passed, queen-editor/frontend 934 passed.
- [x] Yol haritasına dokunulmadı; commit ana ajanın.

### 4.6 Reviewer'ın düzeltmeleri *(21 Ekim; reviewer 484'ü geçirdi, bunlar iki defterde ve md'lerde)*

- [x] **1. `.part` curl'den önce yargılanır**, `downloads.py`'nin 129–138'i biçiminde: `invalid` →
  başı basılır, `.part` silinir, baştan iner (yorum: §3'ün "hiçbir şey silinmez"i burada geçmez — o
  baytlar bir safetensors header'ıyla başlamıyor, hiçbir ekleme onları onarmaz, ve başları basıldı);
  `partial` → `-C -` ile devam; `ok` → curl yok, `os.replace`. curl düşerse `except` silmez: inen
  baytlar iyi ve devam ettirilebilir olabilir. Hata mesajından "Yeniden denemeden önce bu dosyayı elle
  sil" çıktı; hücre 7'nin markdown'u bunu anlatıyor (elle silme yalnız HF dosyaları için).
- [x] **2. Probe kabulü:** ham baytlar okunur, `raw[8:10] == b'{"'` ve 2xx ise kabul; `head_text` yalnız
  hata mesajında.
- [x] **3. Probe bayrakları** `downloads.py`'deki gibi: `--max-time 20 --limit-rate 200k`; exit 0 ya da 28
  dışında curl'ün stderr'iyle durur.
- [x] **4. `instructions.md`, cfg:** "Turbo'da cfg 1 kalır; Turbo t2i'de cfg girişi yok." (Turbo t2i'nin
  alt grafik girdilerinde `cfg` yok ✅, Turbo Edit'inkinde var.)
- [x] **5. `instructions.md`, LoRA:** "`NoctQ_V4_workflow`'da: `Load Diffusion Model` ile `KSampler`
  arasına" (Noct Q'nun workflow'unda model hattı `UNETLoader → KSampler` ✅).
- [x] **6. `instructions.md`:** "ilk boş `image_N`'e (normalde `image_3`, Turbo'da `image_2`)".
- [x] **7.** `lora_target` kalktı; her yerde `target_of(filename, "loras")`.
- [x] **8. sizeKB sözü:** "header dosyanın boyunu zaten kanıtlıyor; API'nin sayısı yalnız disk toplamında"
  — hücre 8'in yorumunda, hücre 7'nin markdown'unda ve `indirilecekler.md` §4'te.
- [x] `downloads.py`'ye dokunulmadı.

---

## 5. Maliyet ve bozulabilecekler

- **İstekler:** her dosya bir kez iner; yerinde olan için ağa gidilmez. Civitai başına bir 1 KB'lık
  probe + bir indirme; şablon ve örnek resim başına bir istek, yalnız yoksa. Koşu başına sabit sayıda,
  N dosyada O(N).
- **Çerez yok ya da bayat:** CONFIG'de ya da probe'larda, hiçbir ağır dosya inmeden durur.
- **Yarım dosya:** HF dosyası `hf_stage`'de, Civitai dosyası `.part`'ta doğrulanır, ancak sonra gerçek
  adına taşınır; ComfyUI yarım bir dosyayı listede görmez. Bozuk bir HF dosyası silinmez, yolu basılır.
  Civitai'nin `.part`'ı bir sonraki koşuda yargılanır: yarımsa devam eder, tamsa yerine konur, header'ı
  bozuksa başı basılıp silinir — o baytlara hiçbir ekleme bir model yapamaz. curl düşerse `.part`
  kalır.
- **Kullanıcının kaydı:** Workflows'ta ve `input/`'ta aynı adla bir dosya varsa dokunulmaz.
- **Civitai'nin bayt sayısı yanlışsa** yalnız disk toplamı biraz kayar; dosya kendi header'ıyla
  doğrulanır.

---

## 6. Doğrulanamayanlar

- **LoRA'ların int8 ConvRot modelde çalışması.** ComfyUI belgesi Lightning LoRA'sını `LoraLoaderModelOnly`
  ile, int8 yükleyen şablonun model hattına koymayı söylüyor ✅; bu dört LoRA'yla int8 Qwen 2.1'de
  denendiğine dair bir kaynak yok ≈. Olmazsa bf16 DiT (14,23 GB) gerekir; plan onu indirmiyor.
- **Base'de eğitilmiş LoRA'ların resmî Turbo'da çalışması: bilinmiyor.** Turbo, 2.1'den damıtılmış aynı
  mimari (int8 dosyaları arasında 4.765 bayt fark var), yani anahtarlar yüklenir ≈; etkisini anlatan bir
  kaynak yok. 2986844 ve 2988215'in kartları *Viggle* hızlandırıcı LoRA'sıyla uyumdan söz ediyor — o
  Base'in üstüne takılan bir LoRA, resmî Turbo checkpoint'i değil.
- **Noct Q + resmî Turbo LoRA (S1-1):** denenmemiş ≈.
- **Noct Q'nun Edit şablonunda karakter tutması:** yazarı *"Image editing with the same files, in
  ComfyUI's Qwen Image 2.1 edit template"* diyor ✅; anime ya da çizim karakterinde kimliği ne kadar
  tuttuğu belgelenmemiş ≈.
- **Civitai dosyalarının içi:** giriş gerektiği için header'ları okunamadı; bayt sayıları API'den, ve
  yalnız disk toplamında kullanılıyor.
- **cfg:** LoRA kartları ve Noct Q cfg > 1 öneriyor; cfg 1'de nasıl çıktıkları bilinmiyor ≈.
