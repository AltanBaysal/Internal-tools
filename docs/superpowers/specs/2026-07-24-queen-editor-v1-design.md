# Queen Editor — Basit v1 (tasarım)

**Tarih:** 2026-07-24 · **Durum:** onaylandı, implementasyon planı bekliyor

## Amaç

`nova-3dcg/api.ipynb` çalışıyor ama girdi yüzeyi bir CONFIG hücresi: prompt listesi, negatif ve varyant sayısı Python kaynağına elle yazılıyor, çıktılar tek bir `output/` klasörüne yığılıyor. Queen Editor bu girdi yüzeyini iki ekranlık bir web arayüzüne taşır ve çıktıyı **projelere** böler. Üretim motoru değişmez — aynı ComfyUI grafiği, aynı enjeksiyon node'ları, aynı hata politikası.

Proje zamanla büyüyecek (katmanlı prompt, motor seçimi, video köprüsü aday). v1'in ikinci işi bu büyümeyi taşıyacak iskeleti kurmak: feature-first, servisleri bağımsız, standartları yazılı.

## Bağlam

- Görsel tasarım hazır: claude.ai/design projesi `Queen Editor` → `Queen Editor Basit v1.html` (+ `styles.css`, `wireframe-kit.jsx`, `simple-screens.jsx`, `simple-app.jsx`). 8 artboard, iki ekran. `styles.css` "Dark Minimal v2" — bitmiş bir koyu ürün teması: `#0f0f10` zemin, IBM Plex Sans/Mono, mor accent `#a78bfa`.
- Motor `nova-3dcg`: Nova 3DCG XL + USNR LoRA + FaceDetailer. Enjeksiyon node'ları `api.ipynb`'de tespit edilmiş — `PROMPT_NODE = "3"`, `NEGATIVE_NODE = "4"`, `SEED_NODE = "40"`. Tek positive kutusu, referans görsel yok; tasarımın "referans görsel v1'de yok" kararıyla örtüşüyor.
- `sdxl-ipadapter` grafiği **seçilmedi**: asıl sebep görsel kalitesinin düşük olması (kullanıcı tespiti); ayrıca referans görsel zorunlu kılıyor ve 4 katmanlı prompt yapısı tek kutuyu bozuyor.
- Kanıtlı desenler devralınıyor: `ComfyClient` (POST `/prompt` → `/history` polling → `/view`), `describe_comfy_error`/`is_infra`, üst üste 3 hatada durma, cloudflared tüneli (`manual.ipynb`).

## Kararlar

| Karar | Gerekçe |
|---|---|
| Motor = **nova-3dcg grafiği**, node id'leri `api.ipynb`'den sabit | Kullanıcı kararı. Tek prompt kutusu + referans görselsiz akış tasarımın brief'iyle birebir; id'ler zaten doğrulanmış. sdxl-ipadapter'ın görsel kalitesi düşük. |
| **Feature-first + bağımsız servisler.** `services/` altında tek iş yapan, hiçbir feature'ı tanımayan servisler (comfy foto üretici, drive); `features/` altında her feature kendi `domain / data / presentation` katmanlarıyla | Kullanıcı kararı ("servisler ayrı ayrı; feature için bir araya gelip feature'ları oluştururlar — data, domain, presentation katmanlarıyla"). Kullanıcının Flutter'dan bildiği clean arch düzeni — "her yerde aynı davranış" hedefi buna dahil. Foto üretici yalnız (prompt, negatif, seed) alır; Drive yalnız oku/yaz/listele. Feature'lar birbirini import etmez; bağlama yalnız composition root'ta. |
| **Use case = dosya başına bir** (`domain/usecases/` altında) | Kullanıcı kararı. 15-40 satırlık tek işli dosyalar; test ve büyüme kolay, bedeli dosya sayısı. |
| Drive'da proje başına **iki JSON**: `prompts.json` (ayarlar — sahibi projects) ve `runs.json` (üretim geçmişi + aktif plan — sahibi generation) | Feature izolasyonunun zorunlu sonucu: tek dosyayı iki feature yazsaydı şema iki feature'a sızardı. Her dosyanın tek sahibi var; foto↔prompt izi `runs.json`'da. Ekran açılışında birleştirmeyi frontend yapar (iki uç çağrılır) — sunucuda feature sınırı delinmez. |
| Standartlar **`queen-editor/CODE-STANDARD.md`**'de yazılı, `CLAUDE.md`'den link | Kullanıcı kararı ("standartlar bir yerde yazmalı, her yerde aynı davranılsın"). `NOTEBOOK-STANDARD.md` deseninin koda uyarlanmışı. İkinci web uygulaması gelirse repo köküne terfi eder. |
| Frontend **Vite + React**; geliştirici derler, `frontend/dist/` **commit'lenir**, Colab yalnız klonlar+servis eder (build Colab'da çalışmaz) | Kullanıcı kararı — önceki "build'süz UMD+Babel" kararını bilinçli tersine çevirir (build'süz modülerlik ya yavaş dosya-başı Babel ya bakımı patlayan script listesi demekti; tasarımın JSX'i Vite'a değişmeden girer). CI olmadığından build kontrollü ortamda (geliştirici) bir kez alınır, Colab runtime'da kırılacak bir şey kalmaz. Gerekçenin tamamı + reddedilen "Colab derler" alternatifi: [frontend build/dağıtım karar spec'i](2026-07-25-queen-editor-frontend-build-delivery-design.md). |
| Prompt kutusu **tek**, içerik **tam Python list** — başka format kabul edilmez | Kullanıcı kararı ("tam python listesi başkasını kabul etmesin şuanlık"). Notebook'tan kopyala-yapıştır doğrudan çalışır. Bozuk girdide kutunun altında hata + **Üret** pasif. Çözümleyici `generation/domain/prompt_list.py` — saf fonksiyon, tek başına test edilir. |
| **Tek negatif prompt**, tüm prompt'lara uygulanır | Tasarımdaki tek satırlık kutu. `api.ipynb`'nin paralel `NEGATIVES` listesi v1'de yok — iki listeyi senkron tutma hatası doğmasın. |
| Kod Colab'a **`git clone` ile** gelir; repo private olduğu için CONFIG'de GitHub token alanı | Kullanıcı kararı: "kod notebookta olmasın, direkt repodan çekilsin". UI değişikliği = push + notebook'u yeniden çalıştır; notebook hiç değişmez. Token notebook'a yazılmaz; Colab Secrets'ta saklanıp `userdata.get` ile okunur (Bölüm 1 kararı). |
| `workflow_api.json` **repodan** okunur (`queen-editor/workflow_api.json`) | Kullanıcı kararı: "Drive'da durmasına gerek yok". Klonla birlikte gelir. Ayar değişikliği = ComfyUI'dan yeni export → commit. Tek kaynak, "hangisi geçerli" belirsizliği yok. |
| Backend **Flask** | Colab'da kurulu, ek indirme yok. Flask yalnız `presentation/` ve composition root'ta görünür; domain/data onu bilmez — ileride değiştirmek presentation'ı değiştirmektir. |
| Tasarımın `styles.css`'i ve kit primitifleri **`vendor/` altında birebir**, elle düzenlenmez | Bitmiş tasarım; ileride claude.ai/design'dan yeniden çekilebilir kalmalı. Uygulamanın kendi stilleri ayrı dosyada — drift olmaz. Sınıf adları (`wf-*`) wireframe döneminden kalma ama görünüm ürün UI'ı; yeniden adlandırma sadece drift üretir. |
| Erişim **cloudflared tüneli** → yeni sekme | Repoda kanıtlı desen; 1440px'lik layout tam ekran sığar, fotoğrafı yeni sekmede açmak çalışır. |
| Proje = Drive klasörü `photoGenV2/<ad>/`; ad Türkçe ve boşluk serbest | Tasarımın brief'i + kullanıcı kararı. Sadece dosya sisteminde geçersiz karakterler (`/ \ : * ? " < > |`), baş/son boşluk ve nokta engellenir; 1–64 karakter. Tasarımdaki örnek adlar (`kapak çekimi`, `lookbook-mayıs`) aynen çalışır. |
| Ayarlar **Drive'da** (brief'teki yalnız-localStorage kararından sapma) | Kullanıcı kararı. Brief "Drive'a yazılan tek şey fotolar" diyordu; bunun iki bedeli vardı — proje başka cihazdan açılınca prompt'lar boş gelir, ve `12_a.png`'nin hangi prompt'tan üretildiği hiçbir yerde yazmaz. İki küçük JSON ikisini de çözer, ayrıca oturum ölümünden devam etmenin ön şartı. |
| Numaralandırma: klasördeki **en büyük numara + 1**'den başla, prompt *i* → `base+i` | Tasarımın brief'i. Üstüne yazma imkânsız; ikinci kez **Üret** = aynı prompt'lardan bir tur daha. `api.ipynb`'nin "zaten var, atla" resume'u burada **yok** — kullanıcı onayladı. |
| Seed varyant başına rastgele, loglanır | `api.ipynb` ile aynı. Varyant = aynı prompt, farklı seed. |
| Hata politikası `api.ipynb` ile **aynı** | Tekil kare patlarsa kırmızı işaretlenir, sıradakine geçilir (artboard 05). Altyapı hatası veya üst üste 3 hata → üretim durur, "Kaldığı yerden devam et" kartı (artboard 06). Üretilenler korunur. Politika kararları `generation/domain/policy.py`'da (saf); thread'i `runner.py` yönetir — ikisi de Comfy'yi ve Flask'ı bilmez. |
| **Tekrar dene** = aynı dosya adı, yeni seed | Numara sırası bozulmaz, galeride kalıcı boşluk kalmaz. Üretim sürüyorsa kuyruğun sonuna eklenir. |
| Üretim **backend thread'inde** yaşar; UI durumu sorar | Sekme kapansa/yenilense üretim sürer, UI yeniden bağlanır. Colab oturumu ölürse iş ölür (kaçınılmaz) — aşağıdaki devam mekanizması bunu karşılar. |
| Aktif üretim planı `runs.json`'a **üretim başında** yazılır | Oturum ölümünden devam etmenin şartı. Bellekteki kuyruk kernel'le ölür; plan diskte kalır. |

## Mimari

### Yapı kuralı

İki tür yapı taşı:

- **Servis** (`services/`): tek iş yapan, kendi klasöründe duran, hiçbir feature'ı tanımayan bağımsız parça.
- **Feature** (`features/`): kullanıcıya görünen bir yetenek; servisleri bir araya getirir. İçi üç katman — **domain** (saf kural + port tanımları + use case'ler; hiçbir dış şey import etmez), **data** (portların gerçeklemesi; servisleri kullanır, dosya şemalarını bilen tek yer), **presentation** (Flask route'ları; istek/yanıt çevirir, iş kuralı içermez).

```
presentation → domain ← data → services

feature ↛ feature      (asla)
servis  ↛ feature      (asla)
servis  ↛ servis       (asla)
```

Somut sınıflar tek yerde bağlanır: `main.py` (composition root) servisleri kurar, data gerçeklemelerini feature'ların portlarına takar. Kuralların tamamı ve "yeni kod nereye gider" tablosu `CODE-STANDARD.md`'de.

### Dosya yapısı

```
queen-editor/
├── app.ipynb                 Colab: custom node'lar + modeller + ComfyUI headless
│                             + repo klonu (derlenmiş dist dahil) + backend + tünel
├── workflow_api.json         ComfyUI Export (API) grafiği (nova-3dcg'den kopya)
├── CODE-STANDARD.md          yapı kuralı · servis/feature sınırları · adlandırma
│                             · yeni kod nereye gider · vendor/ dokunulmazlığı
├── README.md                 kullanım
├── backend/
│   ├── main.py               composition root: servis → data → use case → route
│   ├── config.py             Drive kökü, ComfyUI adresi, node id'leri — tek yer
│   ├── services/
│   │   ├── comfy/            ★ foto üretici — (prompt, negatif, seed) → bytes
│   │   │   ├── client.py       POST /prompt · /history polling · /view
│   │   │   ├── workflow.py     grafiği yükle, 3 node'a enjekte et
│   │   │   └── generator.py    dışa açılan tek kapı
│   │   └── drive/            ★ klasör/dosya oku-yaz-listele — hiçbir şema bilmez
│   │       └── storage.py
│   └── features/
│       ├── projects/
│       │   ├── domain/
│       │   │   ├── name_rules.py     proje adı doğrulama (saf)
│       │   │   ├── ports.py          ProjectStore
│       │   │   └── usecases/         list_projects · create_project
│       │   │                         · get_project · save_settings
│       │   ├── data/
│       │   │   └── project_store.py  drive üstünde; prompts.json şemasını bilen TEK yer
│       │   └── presentation/
│       │       └── routes.py         /api/projects*
│       └── generation/
│           ├── domain/
│           │   ├── prompt_list.py    Python list çözümleyici (saf)
│           │   ├── run_plan.py       (promptlar, varyant, mevcut max no) → kareler (saf)
│           │   ├── policy.py         hata politikası kararları (saf)
│           │   ├── ports.py          PhotoGenerator · PhotoStore · RunStore
│           │   └── usecases/         start · stop · resume · retry_frame
│           │                         · get_status · list_photos
│           ├── data/
│           │   ├── photo_store.py    drive üstünde; N_a.png ad şemasını bilen TEK yer
│           │   └── run_store.py      drive üstünde; runs.json şemasını bilen TEK yer
│           ├── runner.py             thread + kuyruk; domain politikasını uygular
│           └── presentation/
│               └── routes.py         /api/generate* · /photos
└── frontend/
    ├── package.json          react · react-dom · vite
    ├── vite.config.js        çıktı → dist/, backend'e proxy (dev)
    ├── index.html
    └── src/
        ├── main.jsx          giriş + iki ekranlı yönlendirme
        ├── vendor/           tasarımdan birebir, elle düzenlenmez
        │   ├── styles.css
        │   └── kit.jsx       Hand · Mono · Note · Btn · Icon · ImgPH · Status · Pill
        ├── shared/
        │   ├── api.js        tek fetch sarmalayıcı — hata/JSON işleme burada
        │   └── app.css       uygulamanın kendi eklediği stiller
        └── features/
            ├── projects/     ProjectsScreen · ProjectCard · NewProjectModal · useProjects
            ├── project/      ProjectScreen · Gallery · PhotoTile · SettingsPanel
            └── generation/   GenerationPanel · useGeneration
```

★ **İki keskin sınır** (kullanıcının koyduğu):

```python
class PhotoGenerator(Protocol):
    def generate(self, prompt: str, negative: str, seed: int) -> bytes: ...
```

`services/comfy` bundan fazlasını bilmez — proje, varyant, dosya adı, kuyruk yok. `services/drive` yalnız oku/yaz/listele; `prompts.json` şemasını `projects/data`, `runs.json` ve `N_a.png` şemalarını `generation/data` bilir. Test: use case'lere sahte port geçilir, ComfyUI'sız ve Drive'sız çalışır.

Frontend aynı feature-first düzeni izler: hook = data erişimi, bileşen = presentation; ayrı `domain/` klasörü ancak gerçek kural doğunca açılır (v1'de gerekmiyor — kural `CODE-STANDARD.md`'de).

`app.ipynb`'nin kurulum bölümü (7 custom node paketi, 5 model, ComfyUI headless) `nova-3dcg/api.ipynb`'den kopyalanır — bilinçli tekrar; iki notebook bağımsız kalsın diye. `nova-3dcg/api.ipynb` değişmez.

### Drive düzeni

```
MyDrive/photoGenV2/
└── <proje adı>/
    ├── prompts.json     ayarlar: prompt listesi · negatif · varyant  (sahibi: projects)
    ├── runs.json        üretim geçmişi + aktif plan                 (sahibi: generation)
    └── 0_a.png … 11_d.png
```

`runs.json` her üretim için kaydeder: başlangıç numarası, prompt anlık kopyası, varyant sayısı, durum. İki işi birden görür — `12_a.png`'nin hangi prompt'tan üretildiğinin izi, **ve** yarım kalan üretimin planı.

Tek gerçek kaynak ayrımı: **diskteki fotolar** ne bittiğini söyler (`12_a.png` varsa o kare tamamdır), **plan** ne biteceğini söyler. Devam etmek = planda olup diskte olmayan kareleri üretmek. Bu ayrım tünel kopmasına, sekme kapanmasına ve Colab oturumunun ölmesine aynı şekilde cevap verir — üçü de "bellek gitti, disk duruyor" durumudur.

### Ekranlar

| Artboard | Ekran | Durum |
|---|---|---|
| 01 / 01a / 01b | Projeler | dolu (4 sütunlu grid) · boş · çok proje (dikey kayma) |
| 02 | Projeler + modal | Yeni proje — ad çakışması ve geçersiz karakterde aynı yerde kırmızı uyarı |
| 03 | Proje | hazır — sağda prompt/negatif/varyant + **Üret**, solda 5 sütunlu galeri |
| 04 | Proje | üretiliyor — 7/48, ilerleme çubuğu, şu anki prompt, **Durdur** |
| 05 | Proje | tekil hata — kırmızı kare + **Tekrar dene**, üretim devam eder |
| 06 | Proje | üretim durdu — neden + hata detayı + **Kaldığı yerden devam et** |

**Artboard 06 iki yerden çıkar:** üretim sırasında ölümcül hata olunca, *ve* proje açılışında `runs.json`'da yarım plan görülünce. İkincisinde hata satırında `Colab oturumu kapandı` yazar. Yeni ekran gerekmez.

Galeride yeni en üstte; fotoğrafa tıklanınca yeni sekmede açılır. Proje ekranı açılışta iki feature'ın uçlarını ayrı çağırır (ayarlar + fotolar/durum) — birleştirme istemcide.

### Backend yüzeyi

| Uç | Feature · use case |
|---|---|
| `GET /api/projects` | projects · list_projects |
| `POST /api/projects` | projects · create_project |
| `GET /api/projects/<ad>` | projects · get_project (ayarlar) |
| `PUT /api/projects/<ad>/settings` | projects · save_settings |
| `GET /api/projects/<ad>/photos` | generation · list_photos |
| `POST /api/projects/<ad>/generate` | generation · start_generation |
| `POST /api/generate/stop` | generation · stop_generation |
| `POST /api/generate/resume` | generation · resume_generation |
| `POST /api/generate/retry` | generation · retry_frame |
| `GET /api/status` | generation · get_status (canlı ilerleme + yarım plan) |
| `GET /photos/<ad>/<dosya>` | generation · dosya servisi (use case yok) |

Durum güncelleme yöntemi (polling aralığı vs. akış) implementasyonda kararlaşır — protokolü değil, tazeleme sıklığını etkiler.

## Doğrulama (kullanıcı, Colab)

1. T4 runtime'da `app.ipynb` → Run all: custom node'lar kurulur, 5 model iner, ComfyUI kalkar, repo klonlanır (derlenmiş dist dahil), backend başlar, tünel URL'i basılır.
2. URL yeni sekmede açılır → Projeler ekranı, henüz proje yok mesajı.
3. **Yeni proje** → `kapak çekimi` → Drive'da `photoGenV2/kapak çekimi/` oluşur. Aynı adı tekrar denemek kırmızı uyarı verir.
4. Projeye gir → prompt listesini yapıştır (Python list), negatif yaz, varyant 4 → **Üret**. Sayaç `12 prompt × 4 varyant = 48 foto` gösterir.
5. Üretim ilerler; fotolar galeride belirir, Drive'da `0_a.png` … dizisi oluşur. Fotoğrafa tıklamak yeni sekmede açar.
6. Sekme kapatılıp URL yeniden açılır → üretim sürüyor, ilerleme doğru yerden görünür.
7. Üretim bitince tekrar **Üret** → numaralar kaldığı yerden devam eder, hiçbir dosyanın üstüne yazılmaz.
8. Bozuk prompt listesi (kapatılmamış tırnak) → kutunun altında hata, **Üret** pasif.
9. Colab runtime yeniden başlatılır, `app.ipynb` yeniden çalıştırılır → proje açılınca "üretim durdu" kartı çıkar, **Kaldığı yerden devam et** yalnız eksik kareleri üretir.
10. (Geliştirici, lokal) `pytest backend/` — domain + use case testleri sahte portlarla, ComfyUI'sız ve Drive'sız geçer.

## Riskler

- **Tünel URL'i herkese açık.** v1'de kimlik doğrulama yok; URL'i bilen ComfyUI'ı kullanabilir. URL rastgele ve oturumla ölüyor — kabul edildi.
- **Oturum ölümünden devam bedava değil:** notebook baştan çalışır, modeller yeniden iner (~10-15 dk). Üretilmiş fotolar kaybolmaz, kalan kareler baştan üretilmez.
- **Kurulum hücreleri `api.ipynb` ile tekrarlanır.** İki notebook bağımsız kalsın diye bilinçli; model listesi değişirse iki yerde güncellenir.
- **Feature-first iskelet v1'de dosya sayısını artırır** (~35 küçük dosya). Bilinçli bedel: her dosya tek iş yapar, büyüme mevcut sınırlara yerleşir, kurallar `CODE-STANDARD.md`'de.

## Kapsam dışı (v1)

Proje silme ve yeniden adlandırma · foto sayısı / kapak görseli · referans görsel · bağlantı durumu çubuğu · prompt başına ayrı negatif · katmanlı prompt (kalite/karakter/aksiyon/arka plan) · motor seçimi · kimlik doğrulama · çoklu kullanıcı · TypeScript'e geçiş.
