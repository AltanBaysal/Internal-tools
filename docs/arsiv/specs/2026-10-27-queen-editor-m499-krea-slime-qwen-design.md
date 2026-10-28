# Madde 499 · Translucent Penetration Krea'da, ve Qwen Image 2.1 Turbo yeni model olarak — tasarım

**Tarih:** 27 Ekim 2026 · **Madde:** [v11 yol haritası](../roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-1),
499 · v11-1 · **Dal:** `feat/queen-editor-v11` · **Kurallar:** queen-editor
[FOUNDATION](../../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)
· **Önce:** [482](../specs/2026-10-21-queen-editor-m482-krea2-photo-option-design.md) (Krea kendi grafiğiyle),
[486](../specs/2026-10-21-queen-editor-m486-krea-panel-boxes-design.md) (Krea'nın LoRA kutusu) · **Kaynaklar:**
484'ün denemesi `collab-toolbox/photo_experiments/qwen-image-21/`,
[482'nin Qwen araştırması](../research/2026-10-20-queen-editor-m482-qwen-image.md)

## Kullanıcıdan gereken

Hiçbir şey. Madde 27 Ekim'de hizalandı; kullanıcının kararları ve "Claude'un kararları" yol
haritasında. Bu spec onları yeniden açmaz.

## Ne, neden

Bu maddeden sonra:

- **Krea seçiliyken** LoRA kutusunda üç seçenek var: **SNOFS** (varsayılan, bugünkü gibi), **SNOFS +
  Slime** (ikisi birlikte yüklenir) ve **Boş** (LoRA yok). Kutu artık seçilebilir.
- **Model kutusunda Qwen Image 2.1 Turbo** var (notebook'ta işaretlendiyse). LoRA kutusunda
  **Translucent Penetration** ve **Boş**; negatif kutusu yok, Krea'daki gibi.
- Slime ya da Translucent Penetration seçilince tetik kelimesi, *translucent penetration*, Nova'daki
  Slime'da olduğu gibi prompt'un önüne Queen Editor tarafından eklenir.
- Bir Krea senaryosunun prompt listesi Qwen seçilerek de çizilir. QueenAgent'ta bir şey değişmez:
  liste panele yapıştırılır, model kutusundan Qwen seçilir.

## Seçilen LoRA sürümleri

İkisi de Translucent Penetration'ın kendi sayfasında, aynı yazarın (DustyDrab) sürümleri:
[civitai.com/models/2322841](https://civitai.com/models/2322841). Nova ve DaSiWa'nın bugünkü Slime'ı
aynı sayfanın `v5+Illustrious` sürümü (3077575). Sayfa 27 Ekim'de Civitai'nin API'sinden okundu
(`/api/v1/models/2322841`).

| Model | Sürüm | Civitai sürüm id | Dosya (Civitai'de) | Boyut | Güç |
|---|---|---|---|---|---|
| Krea 2 | [v5+Krea2](https://civitai.com/models/2322841?modelVersionId=3117012) | 3117012 | `translucent_penetration_v5+krea2.safetensors` | 229.202,87 KB | **1,0** |
| Qwen 2.1 | [v5+Qwen-Image-2.1](https://civitai.com/models/2322841?modelVersionId=3370853) | 3370853 | `translucent_penetration-V5+Qwen-Image-2.1.safetensors` | 155.699,66 KB | **1,0** |

**Neden bunlar.** Sayfada her taban model için tek sürüm var; ikisi de en sonuncusu ve v5'in veri
setiyle eğitilmiş. Taban modelleri Civitai'de "Krea 2" ve "Qwen 2.1": bizim çizdiğimiz modeller.

**Güçler, sayfanın kendi cümleleri:**
- Krea: *"The default strength of 1.0 should work."*
- Qwen: *"Use with CFG ~3.0 and a weight of 1.0 unless you are using a turbo lora"* ve yazarın genel
  notu *"I haven't really tested with turbo but if something is getting messed up try lowering the
  weight."* Biz Turbo checkpoint'iyle, cfg 1'de çiziyoruz; yazar bunu denememiş. 1,0'la başlanır,
  bozuk çıkarsa düşürülür — kullanıcının Colab denemesi gösterir.
- SNOFS bugünkü gibi **0,8** (kullanıcının kararı).

**Tetik kelimesi.** Krea sürümünün `trainedWords`'ü `translucent penetration`. Qwen sürümünün listesi
boş: yazar Qwen için başlıkları düzyazıyla yeniden yazmış. Sayfanın genel notu *"translucent
penetration should be the only thing needed to trigger it"*. Kullanıcının kararı tetiği Queen
Editor'ün eklemesi; ikisinde de bu iki kelime eklenir.

**Dosya adları bizim.** Civitai'nin adlarında `+` var. Notebook dosyayı kendi verdiğimiz adla indirir
(`civitai_fetch` hedef adı alır), aynaya da o adla gider:
`translucent_penetration_v5_krea2.safetensors` ve `translucent_penetration_v5_qwen_image_2_1.safetensors`.

## Bugün — koddan okunanlar

- **Katalog** (`domain/catalog.py`): `MODELS`'taki Krea satırı tek bir sabit LoRA taşır,
  `KREA2_LORA` (SNOFS), ve `negative: False`. `LORAS` Nova ile DaSiWa'nın kutusu: USNR, Slime. `own_lora`
  ve `drawn_with` Krea'nın satırını grafiğin LoRA'sına bağlar; Krea satırı her zaman `snofs` kaydeder.
- **`/api/models`** Krea satırına `"lora": {"value": "snofs", "label": "SNOFS"}` koyar; panel bunu
  kapalı, tek satırlık bir kutu olarak gösterir.
- **Krea grafiği** SNOFS'u `53:15` `LoraLoaderModelOnly`'de 0,8'de yükler. `53:23` (*Enable LoRA?*)
  `53:22`'nin modeli ve `53:28`'in prompt'u arasında seçer; kapalıyken model doğrudan `53:10`'dan gelir.
  Üretici yalnız prompt'u, seed'i ve boyutu yazar.
- **Qwen** Queen Editor'de yok. 484'ün denemesinde resmî Turbo t2i şablonu ComfyUI'nin arayüzünde
  elle sürüldü. Şablon UI biçiminde ve bir **subgraph**: API'ye verilebilmesi için düzleştirilmesi gerekir.
- **Panel** tek bir `lora` değeri tutar; Krea'da kutu o değeri göstermez, Krea'nın tek satırını
  gösterir. Projenin `settings`'i de tek bir `lora` tutar: son gönderilen.

## Kararlar

### 1. Katalog: bir modelin kendi LoRA listesi

Krea ve Qwen'in satırı tek bir LoRA yerine **kendi listesini** taşır. Listedeki her seçenek bir ya da
daha çok dosya (sırayla yüklenir) ve tetik kelimesidir:

```python
SLIME_TRIGGER = "translucent penetration"
SNOFS_KREA = {"lora": "snofs_krea_v1_5.safetensors", "strength": 0.8}
SLIME_KREA = {"lora": "translucent_penetration_v5_krea2.safetensors", "strength": 1.0}
SLIME_QWEN = {"lora": "translucent_penetration_v5_qwen_image_2_1.safetensors", "strength": 1.0}

KREA2_LORAS = [
    {"id": "snofs", "label": "SNOFS", "files": [SNOFS_KREA], "trigger": ""},
    {"id": "snofs_slime", "label": "SNOFS + Slime", "files": [SNOFS_KREA, SLIME_KREA],
     "trigger": SLIME_TRIGGER},
]
QWEN_LORAS = [
    {"id": "translucent_penetration", "label": "Translucent Penetration", "files": [SLIME_QWEN],
     "trigger": SLIME_TRIGGER},
]
MODELS = [..., {"id": KREA2, ..., "loras": KREA2_LORAS, "negative": False},
          {"id": QWEN, "label": "Qwen Image 2.1 Turbo", "loras": QWEN_LORAS, "negative": False}]
```

- **Boş** listede yazmaz: `NO_LORA` (`"none"`) bugünkü gibi her kutunun son satırıdır, `list_models` ekler.
- **`QWEN = "qwen21turbo"`.** Plan satırına yazılan kimlik; adı modelin tam adı, çünkü bir gün normal
  Qwen 2.1 gelirse iki kimlik karışmasın. Notebook'taki kutusu `PHOTO_QWEN21TURBO`.
- **`LORAS`'ın biçimi değişmez.** Nova ve DaSiWa'nın satırları (`lora`, `strength`, `trigger`) olduğu
  gibi; `ComfyPhotoGenerator`'a dokunulmaz. Yeni seçenek biçimi `files` listesidir, çünkü SNOFS + Slime
  iki dosyadır; dosyanın kendi biçimi `LORAS` satırınınkiyle aynı anahtarlar (`lora`, `strength`).
- **SNOFS'un 0,8'i artık katalogda.** 486'da güç grafiğindi ve katalog onu tekrar etmiyordu. Şimdi
  üretici SNOFS'u da seçenekten yazıyor (4), bu yüzden güç katalogda durur; `test_workflow_asset`
  grafiğin `53:15`'i ile katalogdaki dosya ve gücün aynı olduğunu sorar.

Fonksiyonlar:
- `own_loras(model)` — modelin kendi listesi, ya da `None` (checkpoint, bilinmeyen değer). 486'nın
  `own_lora`'sının yerine geçer.
- `find_lora(lora)` — bugünkü gibi yalnız ortak kutunun (`LORAS`) satırı. İki kutunun satırları ayrı
  biçimde olduğu için tek bir arama ikisini birden döndürmez.
- `find_own_lora(model, lora)` — modelin kendi kutusundaki satır, ya da `None`.
- `drawn_with(model, lora, negative)` — kendi listesi olan modelde boş ya da listede olmayan bir
  değer (Boş dışında) listenin ilk satırına düşer; Boş kalır. Negatif bugünkü gibi. Yani bir Krea
  satırı artık kutunun seçimini kaydeder: `snofs`, `snofs_slime` ya da `none`. Listede olmayan bir
  değer yalnız önceden planlanmış satırlardan gelir (2): 486'dan önce planlanmış, Nova'nın
  LoRA'sını taşıyan bir Krea satırı yeniden üretilince bugünkü gibi `snofs`.
- `own_pick(model, lora)` — üreticinin çizdiği seçenek: `drawn_with`'in seçtiği satır, Boş için `None`.
  Krea ve Qwen üreticisi bunu çağırır; satırın kaydettiğiyle çizilen aynı kuraldan geçer, bilinmeyen
  bir değer üreticide hata vermez.
- `with_trigger(prompt, lora)` — tetik kuralı tek yerde: satırın tetiği varsa prompt'un önüne
  `"<tetik>, "`. Nova'nın (`ComfyPhotoGenerator`), Krea'nın ve Qwen'in üreticisi bunu çağırır.

### 2. `start_batch` — doğrulama

238'in kuralı her kutu için: kendi listesi olan bir model (Krea, Qwen) kendi listesine karşı
doğrulanır, öteki her değer ortak listeye. Boş (`""`) ve `none` her kutuda geçer; listede olmayan
değer `InvalidLora`'yla durur — Krea'da Nova'nın `slime`'ı, Nova'da Krea'nın `snofs_slime`'ı da.

486'nın istisnası (kendi LoRA'sı olan modelde kutu doğrulanmaz) kalktı: o zaman kutu Krea'nın çizdiği
şey değildi, şimdi o. Eski bir `{krea2, slime}` kaydı batch'i durdurmaz, çünkü panel Krea'da Krea'nın
listesinden gösterdiğini gönderir (7). `drawn_with`'in ilk satıra düşürmesi yalnız önceden
planlanmış satırlar için kalır: yeniden üretme, ajanın düzeltmesi ve üreticiler.

### 3. `/api/models` — satır kendi listesini söyler

`list_models` kendi listesi olan bir modelin satırına 486'nın tek `lora` alanı yerine `loras` koyar,
son satırı Boş:

```json
{"value": "krea2", "label": "Krea 2 Turbo", "negative": false,
 "loras": [{"value": "snofs", "label": "SNOFS"}, {"value": "snofs_slime", "label": "SNOFS + Slime"},
           {"value": "none", "label": "Boş"}]}
{"value": "qwen21turbo", "label": "Qwen Image 2.1 Turbo", "negative": false,
 "loras": [{"value": "translucent_penetration", "label": "Translucent Penetration"},
           {"value": "none", "label": "Boş"}]}
```

Nova ve DaSiWa'nın satırı bugünkü gibi `{"value", "label"}`; kutuları cevabın `loras` listesidir.
Ön yüz bir modeli kimliğiyle tanımaz; satırın ne dediğine bakar (FOUNDATION 4).

### 4. Krea grafiği — üç seçenek nasıl yazılır

Grafik dosyası değişmez. Üretici her işte, prompt, seed ve boyuttan sonra:

| Seçenek | Ne yazılır |
|---|---|
| SNOFS | `53:15`'e SNOFS ve 0,8 (dosyadakiyle aynı). `53:23` açık. Grafik bugünküyle aynı gider. |
| SNOFS + Slime | `53:15`'e SNOFS; arkasına yeni bir `LoraLoaderModelOnly` (`lora:1`), Slime Krea 1,0, modeli `53:15`'ten. `53:22`'nin `on_true`'su `lora:1`. Prompt'un önüne `translucent penetration, `. |
| Boş | `53:23` kapalı: model `53:10`'dan, prompt `53:20`'den, tetik düğümü (`53:27`) devre dışı. |

Neden SNOFS da seçenekten yazılıyor: zincirin ilk halkası her seçenekte aynı yerde, `53:15`'te, ve
grafiğin anahtarı (`53:23`) Boş'u kendisi çözüyor. Yeni bir düğüm yalnız ikinci dosya için eklenir.
Kapalı dal da ComfyUI'nin doğrulamasından geçer (484'ün bulgusu); `53:15`'in SNOFS'u diskte olduğu
için Boş'ta da sorun yok.

`load_graph`'ın aradığı düğümler altıya çıkar: `53:19`, `53:3`, `53:5`, `53:15`, `53:22`, `53:23`.

**Zincir** tek bir küçük fonksiyon, `data/lora_chain.py` — `chain_loras(graph, model, files)`: her dosya
için bir `LoraLoaderModelOnly` ekler (`lora:1`, `lora:2`, …), her biri bir öncekinin modelini alır; son
modelin bağlantısını döndürür, dosya yoksa verileni. Krea ve Qwen ikisi de kullanır. `comfy_graph.py`'ye
girmez: o dosya grafiği okur, ne yazılacağı üreticilerin.

### 5. Qwen grafiği — resmî şablon, API biçiminde

`assets/workflow_photo_qwen_api.json`, Comfy-Org'un
[`image_qwen_image_2_1_turbo_t2i.json`](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_qwen_image_2_1_turbo_t2i.json)
şablonundan (27 Ekim'de indirildi) elle API biçimine çevrildi. Subgraph düzleştirildi, düğüm
kimlikleri şablonunkiler, girdilerin adları ComfyUI'nin `comfy_extras/nodes_qwen.py` ve
`nodes_custom_sampler.py`'sinden. Değerler şablonun kendi değerleri:

| Düğüm | Sınıf | Değerler |
|---|---|---|
| `451` | `UNETLoader` | `qwen_image_2.1_turbo_int8_convrot.safetensors`, `default` |
| `453` | `CLIPLoader` | `qwen3vl_8b_int8_convrot.safetensors`, `qwen_image`, `default` |
| `454` | `VAELoader` | `qwen_image_2.1_vae_bf16.safetensors` |
| `452` | `TextEncodeQwenImage21` | `prompt` ← satırın prompt'u; `negative_prompt` `""`; `resolution` 1024 |
| `456` | `EmptyLatentImage` | 1024 × 1024 × 1 ← yönün boyutu |
| `490` | `QwenImage21Cache` | `auto`, `default` |
| `484` | `ManualSigmas` | `1.0, 0.978453, 0.95418, 0.926626, 0.89508, 0.845148, 0.704534, 0.414568, 0` (8 adım) |
| `487` | `KSamplerSelect` | `euler` |
| `488` | `RandomNoise` | `noise_seed` ← satırın seed'i |
| `489` | `CFGGuider` | **cfg 1** |
| `486` | `SamplerCustomAdvanced` | — |
| `457` | `VAEDecode` | — |
| `461` | `SaveImage` | `Qwen_image_2.1` |

Şablondan **çıkanlar**, ve neden:
- **Prompt geliştirici dalı** (`471` TextGenerate, `473` CLIPLoader, `474` anahtar, `475` sistem prompt'u,
  `472` PreviewAny). Şablonda kapalı (`refine_prompt: false`); kapalıyken prompt `474`'ten ve `472`'den
  değişmeden `452`'ye gidiyor. Dal grafikte kalsaydı ComfyUI, kapalı da olsa, yükleyicisinin
  dosyasını (`qwen3.5_9b_…_pe_t2i.int8_convrot`, **9,47 GB**) diskte arardı (484'ün bulgusu); her Qwen
  kurulumu çizimde hiç kullanılmayan 9,47 GB indirirdi. Prompt'u bizde kullanıcı ve QueenAgent yazıyor.
  Çıkan resim aynı: prompt `452`'ye aynı metin olarak gidiyor.
- **`ResolutionSelector`** (`13`): boyutu üretici yazıyor, `456`'ya sayı olarak.
- **`SaveImageAdvanced` → `SaveImage`.** `fetch_output` resmi `/history`'nin `images`'ından alıyor;
  `SaveImage` bunu Krea'nın ve fotoğrafın grafiğinde zaten veriyor. Ayarları (PNG, 8 bit, sRGB)
  `SaveImage`'ın kendi çıktısı.
- Notlar (`MarkdownNote`): API biçiminde düğüm değiller.

Bu, kullanıcının kendi export'u değil (Krea'nınki öyleydi). Bir girdinin adı yanlışsa ComfyUI işi
ilk Qwen karesinde kendi cümlesiyle reddeder; kare kırmızı olur. Bunu yalnız Colab denemesi gösterir.

### 6. Qwen üreticisi

`data/comfy_qwen_photo_generator.py` — `ComfyQwenPhotoGenerator`, Krea'nınkinin eşi: Qwen grafiğini
bilen tek yer. Her işte grafiği diskten okur (`load_graph`, düğümler `452`, `488`, `456`, `451`, `490`),
ve yazar:
- `452.prompt` ← tetik (seçenekte varsa) + `", "` + prompt;
- `488.noise_seed` ← seed;
- `456` ← yönün boyutu (`orientation=None` grafiğinkini bırakır);
- LoRA: `490.model` ← `chain_loras(graph, ["451", 0], seçeneğin dosyaları)`. Boş'ta `451`'e bağlı kalır.

Negatif yazılmaz (cfg 1'de ComfyUI negatifi hesaplamaz; satırın negatifi zaten boş, 1). `generate_batch`
ve `fits_batch` yok: varyantlar Krea'daki gibi tek tek. `main.py` onu `PhotoByModel`'in haritasına
`catalog.QWEN` ile ekler; `config.QWEN_WORKFLOW_PATH` grafiği gösterir.

**Boyutlar:** yatay **1536 × 864**, dikey **1024 × 1536** — Nova'nın boyutlarıyla aynı.

| Neden | |
|---|---|
| Videonun oranı birebir (475'in kuralı) | 16:9 ve 2:3 |
| 32'nin katı | Şablonun notu *"Prefer multiples of 32"*; Krea'nın 1280 × 720'si (720 = 32 × 22,5) tutmuyor |
| LoRA'nın aralığında | Qwen sürümünün sayfası *"Works best within 1.0 MP - 2.5 MP"*; bunlar 1,33 ve 1,57 MP |
| Şablonun 1 MP'sine yakın | Turbo 8 adımda, A100'de; 2K (4 MP) üç kat pahalı ve LoRA orada eğitilmemiş |

### 7. Panel — kutunun seçimi listesine göre

`GeneratePanel` artık tek bir `lora` değil, **liste başına bir seçim** tutar (`picks`): Nova ile
DaSiWa'nın ortak listesi bir anahtar (`""`), kendi listesi olan her model kendi kimliğiyle. Böylece:

- Nova'da Slime seçili, Krea'ya geçilip SNOFS + Slime seçilir, Nova'ya dönülür: Nova'da Slime yerinde,
  Krea'ya yeniden gidilince SNOFS + Slime yerinde (486'nın "seçilen LoRA yerinde"si, şimdi iki kutu için).
- **Kendi listesi olan modelde** kutu seçimi gösterir; seçim listede yoksa ya da hiç yapılmadıysa
  listenin ilk satırını (SNOFS, Translucent Penetration) gösterir ve onu gönderir. Sunucunun
  `drawn_with`'i aynı kuralı uygular; kutu gösterdiğini gönderir.
- **Ortak listede** bugünkü kural: boşsa ilk satır (USNR), listede olmayan kayıtlı bir seçim kendi
  değeriyle görünür ve sunucu karar verir (238).
- **Açılış:** projenin `settings`'indeki `lora`, kaydedildiği modelin kendi listesindeyse o modelin
  seçimi olur, değilse ortak listenin. Yani 486'dan kalan `{model: "krea2", lora: "slime"}` bir
  projede Nova'nın kutusu Slime açılır, Krea'nınki SNOFS.
- Taslak (`REMEMBERED`) seçimleri ve kayıtlı değeri birlikte saklar; detay sayfasından dönünce kutular
  yerinde.

**Bilinen sınır:** `settings` tek bir `lora` tutuyor — son gönderilenin. Krea'da SNOFS + Slime ile
gönderilip sayfa yenilenirse Krea'nın kutusu SNOFS + Slime açılır, Nova'nınki USNR (o oturumda Nova'da
ne seçildiyse unutulur). 486'da Krea, Nova'nın değerini gönderdiği için Nova'nınki korunuyordu; Krea'nın
artık kendi seçimi olduğu için ikisi birden ancak `settings`'e yeni bir alanla korunur. Kayıt biçimini
değiştirmek bu maddede yok; gerekirse ayrı iş.

Negatif kutusu bugünkü gibi `negative === false` olan modelde (Krea, Qwen) çizilmez.

### 8. Ayrıntı sayfası

`PhotoDetail` LoRA'nın adını önce karenin modelinin kendi listesinde (`madeBy.loras`), sonra ortak
listede arar. Bir Krea karesi **SNOFS + Slime**, bir Qwen karesi **Translucent Penetration** ya da
**Boş** yazar. Negatif kutusu Qwen karesinde de yok.

### 9. Üreticiler paneli

`model_groups.py`:
- `KREA2_FILES`'a Slime'ın Krea dosyası girer (Krea kutusuyla iner).
- Yeni `QWEN_FILES`: DiT, metin kodlayıcı, VAE ve Translucent Penetration'ın Qwen dosyası.
- `GROUPS["photo"]`'nun ilk satırı üç seçenekli: herhangi bir checkpoint, Krea'nın beş dosyası ya da
  Qwen'in dört dosyası. Yalnız Qwen işaretlenmiş bir makinede fotoğraf kurulu sayılır.

`test_workflow_asset` her grafiğin yüklediği dosyalar ile katalogdaki seçeneklerin dosyalarının
birleşiminin, gruptaki satırla aynı olduğunu sorar.

### 10. Notebook

- **CONFIG:** `PHOTO_QWEN21TURBO = False  #@param {type:"boolean"}`; fotoğraf seçilip model
  seçilmeyince duran kontrol onu da sayar.
- **Model hücresi:**
  - `PHOTO_MODELS`'a `(PHOTO_QWEN21TURBO, "qwen21turbo", None)`.
  - `CIVITAI_KREA2`'ye Slime'ın Krea'sı: `(3117012, LORA, "translucent_penetration_v5_krea2.safetensors", …)`.
  - `HF_QWEN`: `Comfy-Org/Qwen-Image-2.1`'den DiT (`diffusion_models/`, 7.256.787.829 B), metin
    kodlayıcı (`text_encoders/`, 9.350.798.360 B), VAE (`vae/`, 675.509.688 B) — HF'in dosya
    listesinden, 27 Ekim. `hf_fetch` ile doğrudan, ayna yok (Krea'nınkiler gibi).
  - `CIVITAI_QWEN`: `(3370853, LORA, "translucent_penetration_v5_qwen_image_2_1.safetensors", …)`,
    aynadan (`civitai_fetch`), `MIRRORLESS`'a girmez.
  - İkisi `PHOTO_QWEN21TURBO` işaretliyse `HF_PHOTO` ve `CIVITAI_PHOTO`'ya eklenir; yani yalnız
    `INSTALL_PHOTO` ve Qwen'in kutusu birlikteyken iner.
  - **Disk:** Qwen'in dört dosyası ≈ 17.442.532.333 B ≈ 16,2 GiB → `PHOTO_GIB`'e `+ 17`. Krea'nın
    beşi ≈ 20.786.074.662 B ≈ 19,4 GiB; `+ 20` yetiyor.
  - **Klasörler:** `diffusion_models`, `vae`, `text_encoders` Qwen için de gösterilir
    (`INSTALL_QWEN = INSTALL_PHOTO and PHOTO_QWEN21TURBO`).
- **Klon hücresi** beşinci grafiği de arar.
- **ComfyUI** her koşuda `master`'dan; Qwen 2.1'in düğümleri ComfyUI'nin kendinde, custom node yok.

## Maliyet

| İşlem | Disk / ağ |
|---|---|
| Krea karesi | Değişmez: grafik repo'dan 1 okuma (yerel disk), ComfyUI'ye 1 gönderme, bekleme, 1 `/view`. Yazma bellekte. |
| Qwen karesi | Aynısı: 1 yerel okuma + 1 gönderme + bekleme + 1 `/view`. Varyant başına bir iş. |
| `GET /api/models` | Değişmez: katalog bellekte; disk ya da ağ yok. Satırlar biraz büyür (n = 4 model). |
| Panelde model ya da LoRA değiştirmek | İstek yok; listelerde arama, O(satır sayısı). |
| Batch, yeniden üretme, ajanın düzeltmesi | Değişmez: aynı plan yazımı; `drawn_with` bellekte. |
| Üreticiler paneli | Bugünküne en fazla +5 yerel stat (Qwen'in dört dosyası, Krea'nın beşincisi), Drive'a ya da ağa gidiş yok. |
| Drive | Yeni okuma ya da yazma yok; plan satırının biçimi aynı, değişen yalnız Krea/Qwen satırının `lora` değeri. |
| Notebook | Qwen işaretliyse +16,2 GiB (HF + Civitai/ayna), Krea işaretliyse +0,22 GiB. İşaretli değilse hiçbir şey. |

## Neyi kırabilir

- **Eski Krea satırları:** `snofs` kaydetmişler; bugünkü gibi SNOFS'la çizilirler. 486'dan önceki
  `slime`/`usnr` taşıyanlar `drawn_with`'le SNOFS'a düşer (bugünkü davranış). **Ama 486'dan önce
  planlanmış, Nova'nın kutusundaki Boş'u (`none`) taşıyan bir Krea satırı artık SNOFS'suz çizilir:**
  `none` Krea'nın kutusunda da Boş. 486'da bu satır SNOFS'la çiziliyordu. Bu satırlar yalnız 482'nin
  deneme makinelerinde var (486'nın spec'i).
- **Aynada olmayan iki dosya:** Slime'ın Krea'sı ve Qwen'i HF aynasında henüz yok. Krea ya da Qwen
  işaretli ilk Colab koşusu onları Civitai'den indirir — bunun için `CIVITAI_COOKIE` gerekir, yoksa
  hücre `civitai_fetch`'in kendi cümlesiyle durur — ve aynaya yükler; sonraki koşular aynadan alır.
- **Eski `settings`:** `{krea2, slime}` taşıyan projede Krea SNOFS, Nova Slime açılır (7). Kayıt biçimi
  değişmez, taşıma yok.
- **Yarım indirme / bozuk dosya:** notebook'un bugünkü yolu: header'dan doğrulama, `.part`'tan yerine
  taşıma. Yeni bir yol yok.
- **Qwen grafiği elle çevrildi:** bir girdi adı yanlışsa ComfyUI ilk Qwen karesini kendi cümlesiyle
  reddeder; kare kırmızı, kuyruğun üç deneme kuralı geçerli. Nova, DaSiWa ve Krea etkilenmez.
- **Kart:** Krea (13,5 GB DiT + 5,2 GB kodlayıcı) ve Qwen (7,3 GB + 9,4 GB) A100'ün 40 GB'ında ayrı
  ayrı sığar; aynı kuyrukta ikisi sırayla gelirse ComfyUI birini boşaltıp ötekini yükler (yavaşlar,
  bozulmaz). Gerçek bellek kullanıcının Colab denemesinde görülür.
- **Lisans:** Qwen Image 2.1 Turbo'nun lisansı Qwen Research (ticari değil); 482'nin araştırması söyledi,
  kullanıcı Qwen'i Queen Editor'e almaya 27 Ekim'de karar verdi.

## Bitti sayılır

1. Krea seçiliyken LoRA kutusu **SNOFS** (varsayılan), **SNOFS + Slime** ve **Boş** gösteriyor; seçilen
   gidiyor ve karenin satırına yazılıyor.
2. SNOFS + Slime'da Krea grafiğine iki `LoraLoaderModelOnly` (SNOFS 0,8, Slime Krea 1,0) ve prompt'un
   önüne `translucent penetration, ` gidiyor; Boş'ta LoRA anahtarı kapalı.
3. Model kutusunda **Qwen Image 2.1 Turbo** var (işaretlendiyse); LoRA kutusu **Translucent Penetration**
   ve **Boş**, negatif kutusu yok. Kare `workflow_photo_qwen_api.json`'la 8 adım, cfg 1, yönün boyutuyla
   çiziliyor; Translucent Penetration'da LoRA ve tetik gidiyor.
4. Bir Krea senaryosunun prompt listesi Qwen seçilerek çiziliyor (QueenAgent'ta değişiklik yok).
5. Ayrıntı sayfası Krea ve Qwen karesinin LoRA'sını adıyla yazıyor.
6. Yalnız Qwen işaretli bir makinede üreticiler paneli fotoğrafı kurulu sayıyor; notebook Qwen'in dört
   dosyasını yalnız kutusu işaretliyse indiriyor, diski sayıyor, klasörleri gösteriyor.
7. Nova ve DaSiWa'nın kutusu, kaydı ve ayrıntı sayfası değişmedi.
8. Dört takım yeşil; `dist` yeniden kuruldu.

**Yalnız kullanıcının Colab denemesinde görülecekler:** gerçek Krea + Slime ve Qwen fotoğrafları
(LoRA'nın etkisi, güç 1,0'ın Turbo'da bozup bozmadığı), elle çevrilmiş Qwen grafiğinin ComfyUI'de koşması,
Qwen kurulu bir A100'de kartın ve diskin yetmesi, Krea ile Qwen'in aynı kuyrukta sırayla çizilmesi.
