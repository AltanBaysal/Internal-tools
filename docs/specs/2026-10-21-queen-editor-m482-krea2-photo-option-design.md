# Madde 482 · Krea 2 Turbo, fotoğraf üretiminde bir seçenek — tasarım

**Tarih:** 21 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md),
482 · v10-4 · **Dal:** `feat/queen-editor-v10` · **Kurallar:** queen-editor
[FOUNDATION](../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)
· **Kaynaklar:** 485'in denemesi, `collab-toolbox/photo_experiments/krea-2/indirilecekler.md`

## Kullanıcıdan gereken

Hiçbir şey. Madde 21 Ekim'de hizalandı. Ana ajan aşağıdaki kararların hepsini 21 Ekim'de onayladı;
üreticiler panelinin yeni satır biçimini de (5).

## Ne, neden

Kullanıcı Krea 2 Turbo'yu denedi ve beğendi *("turbo krea işe yarıyor gibi")*; tarzı prompt'taki cümle
belirliyor. Bu maddeden sonra Model kutusunda **Krea 2 Turbo** da var. Seçilirse fotoğraf, kullanıcının
ComfyUI'den API olarak verdiği workflow'la üretilir. Notebook'ta bir kutu daha var, `PHOTO_KREA2`;
işaretlenirse Krea'nın dosyaları iner.

Nova 3DCG ile DaSiWa'nın yolu değişmez: aynı grafik, aynı sınıf, aynı batch hesabı.

## Bugün — koddan okunanlar

- **Model kutusu** `catalog.MODELS`'tan gelir. Satırda `id`, `label` ve `checkpoint` var; liste
  notebook'un `QE_PHOTO_MODELS`'ıyla süzülür (`list_models`).
- **Üretici tek.** `main.py` bir `ComfyPhotoGenerator` kurar ve kuyruğa fotoğraf üreticisi olarak
  verir. O sınıf `assets/workflow_api.json`'u (SDXL: FaceDetailer, upscale, Power Lora Loader, sabit cfg 6
  ve 28 adım) doldurur: prompt, negatif, seed, checkpoint, LoRA, boyut ve batch.
- **Varyantlar** kart kaldırırsa tek ComfyUI işinde yapılır. `run_loop._made_together`
  `producer.fits_batch(sayı)` diye sorar. Hesap SDXL'in ağırlığıyla ve cfg'nin iki katıyla yapılır.
- **Üreticiler paneli** fotoğrafı, `GROUPS["photo"]`'nun her satırı diskteyse kurulu sayar. İlk satır
  "checkpoints'te herhangi bir `.safetensors`". Krea checkpoint değil; yalnız Krea'yı işaretleyen bir
  makinede panel "kurulu değil" der ve *Kuyruğa ekle* kapalı kalır. Bu yüzden 5. bölüm gerekiyor.
- **Notebook** `PHOTO_MODELS`'ın her satırında bir kutu, bir id ve bir checkpoint taşır. Civitai
  dosyaları önce HF aynasından iner (`civitai_fetch`). HF'teki dosyalar `hf_fetch` ile doğrudan iner.

## Kararlar

### 1. Grafik olduğu gibi taşınır

Repo kökündeki `Unsaved Workflow.json` bayt bayt aynı haliyle
`queen-editor/assets/workflow_photo_krea2_api.json` olur. Adı, H3'ünkiler gibi önce türü, sonra modeli
söylüyor. Her işte yalnız üç düğüm yazılır, gerisi kullanıcınındır:

| Düğüm | Ne | Ne yazılır |
|---|---|---|
| `53:19` | `PrimitiveStringMultiline` *"Text String (User Prompt)"* | `value` ← prompt |
| `53:3` | `KSampler` | `seed` ← satırın seed'i |
| `53:5` | `EmptyLatentImage` | `width`, `height` ← yönün boyutu |

Değişmeyenler: 8 adım, cfg 1, euler/simple. SNOFS 0,8'de, anahtarı (`53:23`) açık. Prompt'u genişleten
dal (`53:24`) kapalı. `ResolutionSelector` (`57`) grafikte kalır, ama `53:5` artık ondan okumadığı için
çalışmaz. ComfyUI yalnız çıkışa giden düğümleri koşturur. `PreviewAny` (`53:20`) metin çıkarır, resim
çıkarmaz; `fetch_output` yalnız `images`'a baktığı için tek resim `SaveImage`'ınkidir.

### 2. Ayrı bir üretici ve modele göre seçen ince bir kapı

- **`data/comfy_krea_photo_generator.py` — `ComfyKreaPhotoGenerator`:** Krea'nın grafiğini bilen tek
  yer. `generate(...)` kuyruğun tek çağrı biçimini alır (`ports.PhotoGenerator`) ve kullanmadıklarını
  yok sayar. Her işte grafiği diskten yeniden okur (repo'daki dosya, Drive değil), API biçiminde
  olduğunu ve üç düğümün durduğunu denetler. Sonra doldurur, gönderir, bekler, resmi alır. Düğüm
  yoksa adını söyleyerek durur, `ComfyPhotoGenerator` gibi. `generate_batch` ve `fits_batch` yok
  (bkz. 4).
- **`data/photo_by_model.py` — `PhotoByModel`:** kuyruğa verilen fotoğraf üreticisi. Her işi satırının
  modeline göre gönderir: haritada (`{catalog.KREA2: krea}`) olan model kendi üreticisine, öteki her
  değer `ComfyPhotoGenerator`'a gider. Boş, eski `recipe:…` ve dosya adı da buna dahildir. Yani bugünkü
  her satır bugünkü yerine gider. Bir ağ, disk ya da dosya işi yoktur.
- **`catalog`:** `KREA2 = "krea2"` ve `MODELS`'ta `{"id": KREA2, "label": "Krea 2 Turbo"}`. Satırda
  `checkpoint` yok, çünkü Krea kendi grafiğiyle çizilir. `ComfyPhotoGenerator` bu satırı hiç görmez.
- **`main.py`** ikisini `PhotoByModel`'le birleştirir. `config.KREA2_WORKFLOW_PATH` yeni grafiği
  gösterir.

### 3. Negatif, LoRA kutusu ve prompt Krea'da

- **Negatif kullanılmaz.** Grafiğin negatifi `ConditioningZeroOut`; cfg 1'de ComfyUI negatif koşulu hiç
  hesaplamaz. Panelin negatifi satırda kalır (planlanan budur) ama Krea'ya gitmez.
- **LoRA kutusu kullanılmaz.** USNR ve Slime Illustrious/SDXL LoRA'ları, Krea'ya yüklenemezler.
  Krea, kullanıcının workflow'undaki gibi SNOFS'la çizer. LoRA'nın tetik kelimesi prompt'un önüne
  **eklenmez**, çünkü o LoRA yüklenmiyor. Kutunun değeri yine `start_batch`'te doğrulanır ve satıra
  yazılır.
- **Prompt değişmeden gider.** QueenAgent'ın `BREAK`'le bağlanmış etiket prompt'ları da öyle
  gider: Qwen3-VL için `BREAK` bir kelimedir. Krea'ya göre prompt yazmak QueenAgent v11-5'in işi.
  Grafiğin LoRA tetik kelimesi düğümü (`53:27`, `string_b` boş, ayraç `", "`) prompt'un sonuna `", "`
  ekler; zararsız, olduğu gibi kalır.
- **Ekran değişmez.** Model listesi yeni bir şey istemiyor. Bilinen sonuç: Krea seçiliyken LoRA ve
  negatif kutuları görünmeye devam eder, ve Krea karesinin ayrıntı sayfası seçilen LoRA'yı yazar.
  Ana ajan bunu kullanıcıya götürüyor (sonraki iş).

### 4. Boyutlar ve batch

| Yön | Krea | H3 videosu | Oran |
|---|---|---|---|
| `yatay` | 1280 × 720 | 1024 × 576 | 16:9, birebir |
| `dikey` | 832 × 1248 | 576 × 864 | 2:3, birebir |

Neden: kullanıcının workflow'u 1 MP'de (16:9, 1 MP). Bu iki boyut 1 MP'nin yanında (0,92 ve 1,04 MP)
ve 475'in kuralını tutuyor: fotoğrafın oranı videonunkiyle birebir aynı. İki kenar da 16'nın katı
(Qwen Image VAE'nin 8'i × DiT'in 2'lik yaması). `orientation=None` grafiğin kendi boyutunu bırakır
(16:9, 1 MP). Döngü her zaman bir yön verir.

**Batch yok: Krea'nın varyantları tek tek üretilir.** Kart hesabı ComfyUI'nin kendi kurallarıyla
yapılıyor (madde 411). Krea'nın `memory_usage_factor`'ı bu repodan okunamıyor ve bir sayı
uydurulmuyor. 12,9 milyar parametrelik bir DiT 1 MP'de kartı zaten doldurur, batch'ten kazancı az.
Bunun için `BatchPhotoGenerator.fits_batch` `model=""` alır, ve `_made_together` grubun ilk satırının
modelini verir (gruptaki her satırın modeli aynı, `variant_batch.MADE_FROM`). `PhotoByModel` soruyu
modelin üreticisine sorar; `fits_batch`'i olmayan üretici "sığmaz" demektir. `ComfyPhotoGenerator`'ın
hesabı (SDXL, cfg'nin iki katı) değişmez; `model`'i alır ve yok sayar, çünkü her checkpoint'i aynı
ağırlıkta tartar. Krea'nın batch'i, kullanıcının kartında ölçülünce ayrı bir iş olabilir.

### 5. Üreticiler paneli: "bunlardan biri" satırı

`GROUPS["photo"]`'nun ilk satırı üçüncü bir biçim alır. Her seçenek, hepsi diskte olması gereken
satırların listesidir:

```python
{"any": [[{"folder": "checkpoints", "suffix": ".safetensors"}],
         KREA2_FILES]}
```

`KREA2_FILES`, Krea grafiğinin yüklediği dört dosya:
`diffusion_models/krea2_turbo_int8_convrot`, `text_encoders/qwen3vl_4b_fp8_scaled`,
`vae/qwen_image_vae` ve `loras/snofs_krea_v1_5` (`.safetensors`). Ardından bugünkü beş satır gelir
(USNR, Slime, Remacri, yüz dedektörü, SAM). Bunlar yalnız Krea işaretlense de her fotoğraf koşusuyla
iner, bugünkü gibi; ~2 GiB, ana ajan kabul etti.

`list_producers` bir satırı küçük, özyineli bir kontrolle cevaplar (`_here`): `any` ise
seçeneklerden birinin bütün satırları, `name` ise o dosya, `suffix` ise o türden bir dosya.
**Maliyet:** panel her okunuşta en fazla 4 stat fazla yapar, makinenin kendi diskinde. Drive'a ya da
ağa gidiş yok, satır sayısıyla O(n).

### 6. Notebook

- **CONFIG:** `PHOTO_KREA2 = False  #@param {type:"boolean"}`. Fotoğraf seçilip hiçbir model
  işaretlenmezse duran kontrol Krea'yı da sayar.
- **Model hücresi:** `PHOTO_MODELS`'a `(PHOTO_KREA2, "krea2", None)`. Krea'nın checkpoint'i yok,
  `CHOSEN_CHECKPOINTS` yalnız dolu olanları alır. `QE_PHOTO_MODELS` `krea2`'yi taşır; Model kutusu onu
  böyle gösterir.
- **Kaynaklar, 485'in denemesindekiler:**
  - `HF_KREA2`: `Comfy-Org/Krea-2`'den DiT (`diffusion_models/`, 13.492.686.496 B), metin kodlayıcı
    (`text_encoders/`, 5.242.467.968 B) ve VAE (`vae/`, 253.806.246 B). `hf_fetch` ile doğrudan iner,
    **ayna yok**: dosyalar zaten HF'te, açık bir repoda.
  - `CIVITAI_KREA2`: SNOFS, Civitai sürüm 3390681, `loras/snofs_krea_v1_5.safetensors`
    (1.562.410.216 B). `civitai_fetch`'le **aynadan** iner, aynada yoksa Civitai'den ve sonra aynaya
    yüklenir, Civitai'nin öteki dosyaları gibi. Artık denemede değil, `MIRRORLESS`'a girmez.
  - İkisi de `HF_PHOTO` ve `CIVITAI_PHOTO`'ya `PHOTO_KREA2` işaretliyse eklenir, yani yalnız
    `INSTALL_PHOTO` ve `PHOTO_KREA2` ikisi birden açıkken iner.
- **Disk:** dört dosya 20.551.370.926 B ≈ 19,1 GiB. `PHOTO_GIB`'e Krea işaretliyse 20 eklenir.
- **Klasör listesi:** `diffusion_models`, `vae` ve `text_encoders` video için olduğu gibi Krea için de
  gösterilir.
- **Klon hücresi** dördüncü grafiği de arar.
- **ComfyUI** her koşuda `master`'dan güncelleniyor (`install_comfy`). Grafiğin düğümleri comfy-core
  0.25.0'ın kendinde, custom node gerekmiyor.

## Maliyet

| İşlem | Disk / ağ |
|---|---|
| Krea karesi | Grafik repo'dan 1 okuma (yerel disk) + ComfyUI'ye 1 gönderme, bekleme, 1 `/view`. Bugünkü bir fotoğrafla aynı. |
| Krea'nın varyantları | Varyant başına bir iş: N varyant N iş. |
| Nova / DaSiWa | Değişmez. |
| Üreticiler paneli | Bugünküne en fazla +4 yerel stat. |
| Drive | Hiçbir okuma ya da yazma değişmez. Satırın biçimi aynı. |

## Neyi kırabilir

- Yeni bir alan, dosya ya da kayıt biçimi yok. Eski satırlar bugünkü üreticiye gider.
- Krea grafiğinde düğüm eksikse iş, hangi düğümün eksik olduğunu söyleyerek düşer. Kare kırmızı olur,
  kuyruğun üç deneme kuralı geçerli.
- Krea dosyası eksik bir makinede ComfyUI kendi cümlesiyle reddeder. Panel bunu önceden "kurulu
  değil" diye söyler, ama yalnız hiçbir fotoğraf modeli tam değilse: panel üretici başına bakıyor,
  model başına değil. Bugün de böyle.
- T4'te Krea'nın int8 DiT'i (13,5 GB) karta sığmaz; ComfyUI ağırlığı kısmen dışarı alıp yavaş çizer.
  Kullanıcı Krea'yı A100'de denedi.

## Bitti sayılır

1. Model kutusunda Krea 2 Turbo var (notebook'ta işaretlendiyse). Seçilen her kare
   `workflow_photo_krea2_api.json`'la, satırın prompt'u, seed'i ve yönün boyutuyla çizilir. Negatif,
   LoRA ve tetik kelimesi Krea'ya gitmez.
2. Krea'nın varyantları tek tek, Nova ve DaSiWa'nınki bugünkü gibi batch'le yapılır.
3. Yalnız Krea işaretlenmiş bir makinede üreticiler paneli fotoğrafı kurulu sayar.
4. Notebook `PHOTO_KREA2`'yle Krea'nın dört dosyasını iner, diski sayar, klasörleri gösterir.
5. Dört takımın hepsi yeşil. Colab'da, kullanıcının denemesinde: Krea seçilince yatay ve dikey Krea
   fotoğrafı geliyor, Nova ve DaSiWa bugünkü gibi çalışıyor.
