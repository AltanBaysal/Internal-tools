# WAN 2.2 arbuzai I2V — API modu (tasarım)

**Tarih:** 2026-07-19 · **Durum:** onaylandı, implementasyon planı bekliyor

## Amaç

Aynı grafiği **ComfyUI arayüzünü hiç açmadan** çalıştırmak: bir görsel + bir prompt gir, Drive'a bir mp4 düşsün.

Mevcut `wan22-arbuzai.ipynb` grafiği kurup tüneli açıyor — ayarları keşfetmek için doğru araç, üretim için değil. Her video için tarayıcıda link açmak, grafiği yüklemek, LoRA'ları yeniden takmak gerekiyor. API modu bu turu ortadan kaldırıyor.

## Bağlam

### Repoda zaten çözülmüş olanlar

Kardeş klasör `video_generator/wan22-smooth-t2v/` bu işi **şu anda** yapıyor ve aynı desende yeniden adlandırılıyor: `manual.ipynb` (grafiği kurar, tünel açar) + `api.ipynb` (UI'sız üretir) + `workflow_manual.json` + `workflow_api.json`. Yeniden icat edilmeyecek, kopyalanacak:

- `POST /prompt` + `client_id`, `node_errors` varsa ham JSON ile `RuntimeError`
- `/history/{prompt_id}` polling — websocket **yok** (repoda hiç kullanılmamış)
- `describe_comfy_error(status)` — hangi node, hangi exception, ham traceback; `node_type` "loader" ile bitiyorsa altyapı hatası
- `/view` ile çıktıyı çekme (ComfyUI'ın output klasör düzeninden bağımsız), sonra yerel kopyayı silme
- `/upload/image` ile görsel yükleme (`imageToVideo.ipynb` deseni)
- UI formatı gelirse **dönüştürme değil, reddetme**: `"nodes" in wf` → "Export (API) ile kaydet"

`imageToVideo.ipynb`'nin `wait()`'inde wall-clock timeout **yok** — bu kusur kopyalanmayacak, `loop_maker`/`api.ipynb`'nin timeout'lu hali alınacak.

### Grafikten doğrulanan gerçekler

Kullanıcının UI'da `Export (API)` ile ürettiği dosya incelendi (36 node, API formatı, `nodes` anahtarı yok). Tahmin değil, dosyadan okundu:

| Node | Tip | Durum |
|---|---|---|
| **287** | LoadImage | `"example.png"` — yazılacak |
| **233:240** | PromptGenerator | `prompt: ""`, kendi `seed`'i var — yazılacak |
| **210** | Seed (rgthree) | **`-1`** — yazılacak |
| **197 / 186** | UNETLoader | HIGH / LOW, dolu |
| **201 / 200** | Power Lora Loader | **dolu**, model girdileri 197→201 ve 186→200 |
| **164** | SaveImage | son kareyi PNG yazar |
| **198** | VHS_VideoCombine | mp4 çıktısı |
| **356 / 357** | UnetLoaderGGUF | `unet_name: null`, **hiçbir node referans vermiyor** → ComfyUI budar |

- **`seed: -1` bir tuzak.** rgthree'nin rastgeleliği **frontend widget'ında** üretiliyor; API modunda widget yok. `-1` olduğu gibi gönderilirse her çalıştırma aynı çıktıyı verir. Kardeş notebook aynı tuzağa düşmüş, çözümü oradan alınıyor.
- **Bağlantısız çıktı node'u yok.** 164 / 283 / 233:239'un girdileri bağlı. Bağlantısız bir output node'u tüm `POST /prompt`'u reddettirir (kardeş spec'te yaşanmış).
- **LoRA'lar grafikte.** 201: `lightx2v_high` + `Animations_XXX_High`; 200: `lightx2v_low` + `Animations_XXX_Low`. Ağırlıklar kullanıcının seçtiği değerler.

## Kararlar

| Karar | Gerekçe |
|---|---|
| **Ayrı notebook** (`api.ipynb`) | Kardeş klasörün deseni. Manuel notebook grafiği keşfetmek için kalıyor; iki modu tek dosyada iç içe geçirmek ikisini de okunmaz yapar. |
| **LoRA'lar grafikten gelir, notebook dokunmaz** | Kullanıcı kararı. UI'da ayarlanıp `Export (API)` ile dondurulur. Notebook rgthree'nin iç widget formatına bağımlı olmaz. |
| **Notebook yalnız 3 alan yazar** | Prompt, seed, görsel adı — her çalıştırmada değişen tek şeyler. Çözünürlük/step/cfg grafikte; kardeş notebook da böyle. |
| **Girdi görseli elle yüklenir** | Kullanıcı kararı: Colab dosya seçme penceresi. Drive'a koyup yol yazmaya gerek yok. |
| **Çıktı Drive'a, yalnız mp4** | Kullanıcı kararı. SaveImage'ın PNG'si Colab'da kalır ve silinir. |
| **`workflow_api.json` Drive'dan okunur** | Kardeş desen. Repo kopyası sürüm kaydı; çalışan kopya Drive'daki. |
| **Klasördeki dosyalar kardeşle aynı adlandırmaya geçer** | `manual.ipynb` / `api.ipynb` / `workflow_manual.json` / `workflow_api.json` — iki klasör birebir aynı desende olur. |
| **Klasör `video_generator/` altına taşınır** | Kullanıcı kararı: manuel notebook Colab'da çalıştı, artık deneme değil. `video_experiments/` "eşiği geçmemiş" işler için. |
| **16 custom node aynen kurulur** | Kanıtlanmış liste. API export'u 12 farklı paketten node kullanıyor; listeyi budamak kazancı olmayan bir risk. |

## Mimari

Klasör `video_experiments/`'ten **`collab-toolbox/video_generator/wan22-arbuzai/`'ye terfi ediyor** — manuel notebook Colab'da uçtan uca çalıştı, `video_experiments/` orada durmanın gerekçesi olan eşiği geçmiş oldu. Kardeş `wan22-smooth-t2v` de aynı yolu izledi.

| Hedef dosya | Nereden |
|---|---|
| `manual.ipynb` | `video_experiments/wan22-arbuzai/wan22-arbuzai.ipynb` |
| `workflow_manual.json` | `video_experiments/wan22-arbuzai/workflow.json` (içerik değişmez) |
| `workflow_api.json` | repo kökündeki `workflowapi.json` |
| `api.ipynb` | **yeni** |

Taşıma `git mv` ile yapılır — dosya içerikleri değişmez, yalnız yol ve ad değişir.

### api.ipynb hücre sırası

| # | Hücre | Kaynak |
|---|---|---|
| 1 | CONFIG — Drive mount, cookie, `PROMPT`, `SEED`, Drive kökü · **+ görseli seçtiren ikinci hücre** | yeni |
| 2 | Ortak yardımcılar (`log`/`human`/`head_text`/`run`/`check_safetensors`) | `manual.ipynb`'den birebir |
| 3 | ComfyUI + 16 custom node | birebir |
| 4 | Modeller (~36 GiB, gated probe + indirme) | birebir |
| 5 | ComfyUI'ı başlat — **tünel yok**, `tail -f` yok, `--enable-manager` yok | sadeleştirilmiş |
| 6 | Seçilen görseli `/upload/image` ile ComfyUI'ya gönder | yeni |
| 7 | Grafiği oku → 3 alanı yaz → gönder → bekle → Drive'a yaz | yeni |

**Görsel iki aşamada alınır.** Dosya seçimi 1. bölümde, Drive izniyle yan yana: run'ın ihtiyaç duyduğu her girdi ilk saniyelerde toplanır. `/upload/image` ise ComfyUI ayakta olmadan çalışmadığı için 6. bölümde kalır. Tek parça olsaydı ~40 dakikalık indirme bittikten sonra "görsel seçilmedi" ile patlardı — bu tasarımın kaçındığı şey tam olarak bu.

Drive düzeni: `MyDrive/imageToVideoV2/workflow_api.json` (girdi), `MyDrive/imageToVideoV2/output/YYYYMMDD_HHMMSS.mp4` (çıktı).

### Grafiğe yazılanlar

```
287       .inputs.image  = /upload/image'ın döndürdüğü sunucu tarafı ad
233:240   .inputs.prompt = CONFIG'deki PROMPT
233:240   .inputs.seed   = seed        # wildcard prompt aynı seed'de aynı açılsın
210       .inputs.seed   = seed        # sampler'ın noise seed'i buradan besleniyor
```

Her alan için ayrı fonksiyon (bir fonksiyon bir alan yazar). Node id'leri hücrenin başında adlandırılmış sabitler; üçünden biri grafikte yoksa hücre "graf değişmiş, node id'lerini güncelle" diyip durur — sessizce yanlış node'a yazmaz.

`SEED = None` bırakılırsa Python tarafında rastgele bir tam sayı üretilir; `SEED = 12345` gibi bir değer verilirse o kullanılır. Hangi durumda olursa olsun kullanılan seed **ekrana basılır** — tekrar üretilebilmesinin tek yolu bu. Grafiğe `-1` asla gönderilmez.

## Hata politikası

Hepsi `NOTEBOOK-STANDARD.md` §2: mesaj servisin **ham çıktısını** basar, sebep uydurulmaz.

| Durum | Davranış |
|---|---|
| Drive'daki dosya UI formatında (`nodes` anahtarı var) | `RuntimeError` — "Export (API) ile kaydet". Dönüştürme denenmez |
| 287 / 233:240 / 210'dan biri yok | `RuntimeError` — graf değişmiş, node id'leri güncelle |
| `POST /prompt` ≥ 400 | HTTP kodu + ComfyUI'ın yanıt gövdesi |
| `node_errors` dolu | Ham JSON |
| Çalışırken hata | `describe_comfy_error` — node id, tip, exception, ham traceback |
| 30 dakikada bitmedi | `TimeoutError` |
| `history`'de video yok | Ham `outputs` kaydı |
| ComfyUI 90 sn'de ayağa kalkmadı | Log'un son 30 satırı + `RuntimeError` |

## Riskler / açık uçlar

1. **Bayat Drive kopyası.** Grafiği UI'da değiştirip Drive'daki `workflow_api.json`'u güncellemezsen eski graf sessizce çalışır — hata vermez, sadece yanlış sonuç verir. Kardeş spec'te de açık uç.
2. **`seed: -1` düzeltmesi doğrulanmadı.** Seed'i yazmanın gerçekten farklı çıktı ürettiği Colab run'ında görülecek (aynı prompt, iki farklı seed → iki farklı video).
3. **`/upload/image` dosya adı çakışması.** Aynı adla ikinci bir görsel yüklenirse ComfyUI `overwrite` davranışına göre eskisini ezer ya da adı değiştirir; dönen ad kullanılacağı için sorun beklenmiyor ama teyit edilmedi.
4. **PNG temizliği.** SaveImage 164'ün çıktısı `history`'de `images` altında görünür; videonun `gifs`/`videos` altından ayrıştırılması gerekiyor. Yanlış ayrıştırma Drive'a PNG yazmakla sonuçlanır (kullanıcı istemiyor).
5. **Model indirme süresi.** Her oturum ~36 GiB. API modu bunu kısaltmıyor; kısaltmak isteniyorsa modelleri Drive'a almak ayrı bir iş (bu kapsamda değil).

## Doğrulama

Kabul kriteri: **UI hiç açılmadan, Drive'a doğru bir mp4 düşer.**

1. Drive'a `workflow_api.json` konur, notebook A100'de Run all → hata yok.
2. 6. hücre dosya seçme penceresi açar, görsel yüklenir.
3. İş gönderilir, `/history` biter, `MyDrive/imageToVideoV2/output/` altında zaman damgalı mp4 oluşur.
4. Video, `manual.ipynb` + UI ile aynı ayarlardan çıkana benzer (LoRA'lar grafikten geldiği için aynı olmalı).
5. Aynı prompt iki farklı `SEED` ile çalıştırılır → **iki farklı video** (risk 2'nin testi).
6. Drive'da PNG **yok**, ComfyUI'ın output klasöründe artık dosya kalmamış.

## Kapsam dışı

Toplu üretim (klasördeki her görsel), N seed varyasyonu, modelleri Drive'da önbellekleme, grafiği notebook'tan özelleştirme (LoRA/çözünürlük/step), `instructions.md` yazımı.
