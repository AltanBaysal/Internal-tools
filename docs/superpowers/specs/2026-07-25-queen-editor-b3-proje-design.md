# Queen Editor — Bölüm 3: Proje (tasarım)

**Tarih:** 2026-07-25 · **Durum:** onaylandı, implementasyon planı bekliyor
**Şemsiye tasarım:** [2026-07-24-queen-editor-v1-design.md](2026-07-24-queen-editor-v1-design.md) · **Yol haritası:** [2026-07-24-queen-editor-roadmap.md](../plans/2026-07-24-queen-editor-roadmap.md)

## Amaç

İlk gerçek özellik: **proje oluştur ve listele**. Proje = Drive klasörü `MyDrive/queenEditor/<ad>/`.
Bölüm 2 sunucunun ayakta olduğunu kanıtladı (`/api/health`); bu bölüm Drive'a yazıp okuduğunu ve
tasarımın Projeler ekranını (artboard 01 / 01a / 02) kanıtlar.

İkinci iş: `CODE-STANDARD.md`'deki feature iskeletinin **ilk gerçek örneğini** kurmak —
`services/drive` + `features/projects` (domain / data / presentation), bağlama yalnız `main.py`'de.
Sonraki bölümler bu sınırlara yerleşir.

## Bağlam

- Bölüm 2 hazır: Flask `create_app` + `/api/health` + derlenmiş `frontend/dist` servisi, cloudflared
  tüneli, `pytest` 4 test. Frontend `App.jsx` bugün yalnız bağlantı işaretini gösteriyor.
- Tasarım hazır ve okundu (claude.ai/design projesi `simple-screens.jsx`): header `Queen Editor ·
  Projeler · [+ Yeni proje]`, 4 sütunlu **4/3** oranlı kartlar (sol üst ad, sağ alt tarih), boş
  durum metinleri, 380px'lik "Yeni proje" modalı (hatalı adda kırmızı çerçeve + altında uyarı).
- `vendor/styles.css` Bölüm 2'de çekildi ve gereken **tüm** sınıfları taşıyor: `wf-card`,
  `wf-card--shadow`, `wf-scrim`, `wf-input`, `wf-btn--hl/--ghost`, `wf-hand`, `wf-mono`, `wf-note`,
  `wf-stroke`. Yeni CSS çekilmesine gerek yok.
- Tasarımın kit dosyası (`wireframe-kit.jsx`) global dünyaya yazılmış: `import` yok, sonu
  `Object.assign(window, {…})`. ESM'e girmesi için tek bir uyarlama gerekiyor (aşağıda karar).
- Drive deseni repoda kanıtlı: `drive.mount('/content/drive')` → `/content/drive/MyDrive/<klasör>`
  (`mmaudio_generate.ipynb`, `imageToVideo.ipynb`, `mp4_converter.ipynb`).

## Kararlar

| Karar | Gerekçe |
|---|---|
| **İnce dilim:** `projects` feature'ından yalnız `list_projects` + `create_project`. `get_project` / `save_settings` bu bölümde yok | O ikisi `prompts.json`'a dokunur — Bölüm 6'nın işi. Ekranı olmayan kod yazmak yol haritasının "her bölüm Colab'da kanıtlanır" ilkesini bozar. Elenen alternatif *kısa yol* (route + `os.makedirs`, katman yok): ilk gerçek feature standardın kurulduğu yerdir, orada çiğnenmez. |
| Proje klasörü **yalnız klasör** olarak oluşur; içine hiçbir dosya yazılmaz | `prompts.json`'un sahibi `projects/data`, şeması Bölüm 6'da kararlaşır. Şimdi boş bir iskelet yazmak aynı dosyayı iki bölüme paylaştırır. |
| Kartın tarihi ve sırası **klasörün mtime'ı** (`modifiedAt`, epoch saniye); en son değişen en üstte | Tasarımın kuralı ("en son değiştirilen en üstte"), ek dosya ve ek şema gerektirmeden. Bölüm 3'te kesin doğru (klasör yeni oluşuyor). Bilinen risk aşağıda: Drive FUSE'ta dizin mtime'ının içerik yazılınca güncellenmesi garanti değil. |
| Ad doğrulaması **tek kaynak: sunucu** (`domain/name_rules.py`). Tarayıcıda kural kopyası yok | Kullanıcı kararı. Aynı kuralın iki dilde iki dosyada yaşaması repo'nun "no drift" kuralına ters. "Oluştur" yalnız kutu boşken pasif; geçersiz adda mesaj sunucudan gelir, tasarımdaki yere (kutunun altı) ve görünüme (kırmızı çerçeve) düşer. Yerel sunucu — gidiş-dönüş anlık. |
| Çakışma **birebir ad** karşılaştırması (dosya sisteminin gerçeği) | Türkçe büyük/küçük harf katlaması (İ/ı) locale'e göre değişir; "aynı sayılan" adlar sessiz sürpriz üretir. `düğün` ve `Düğün` iki ayrı projedir — Drive'da da öyle görünür. |
| `POST /api/projects` çakışmada **409**, kural hatasında **400**; gövde her iki durumda `{"error": "<Türkçe mesaj>"}` | Frontend'de tek hata yolu: mesaj neyse kutunun altına yazılır. Ayrım HTTP kodunda kalır, UI'da dallanma doğurmaz. |
| `ProjectStore` portu **iki metot**: `list()` ve `create(name) -> Project \| None` (`None` = ad zaten var) | Ayrı bir `exists()` sorusu + sonra yazma iki adımdır; `os.makedirs` zaten atomik olarak "var" der. Oluşan projenin tarihini diskten okuyup dönmek `data` katmanının işi — use case mtime'ı nereden geldiğini bilmez. Port küçük kalır, çakışma kararı tek yerde. |
| Liste çekilemezse ekranda **kırmızı hata kartı**: başlık + mono kutuda sunucunun **gerçek** mesajı + **Tekrar dene** | Kullanıcı kararı. Sessiz boş liste Drive kopmasını gizler. Repo kuralı: sebep icat edilmez, servisin çıktısı gösterilir. Boş durum ile hata durumu asla karışmaz. |
| Kart **tıklanamaz**: `cursor: pointer` ve hover kalkma efekti yok | Proje ekranı Bölüm 4-5'te. Tıklanabilir görünen ama çalışmayan kart "bozuk" hissi verir; "yakında" uyarısı ise sonraki bölümde çöpe gidecek geçici kod olur. Bölüm 4'te tek satır `onClick` eklenir. |
| Tasarımın **sahte kaydırma çubuğu ve alt gradient kararması** ürüne alınmaz | Artboard'da "bu liste kayar" demek için konulmuş wireframe işaretleri; canlı üründe tarayıcının kendi kaydırması bu işi zaten yapıyor. |
| `vendor/kit.jsx` tasarımdan birebir kopyalanır, **yalnız ihracat sınırında** uyarlanır: `Object.assign(window, {…})` → `export {…}` | Vendor dokunulmazlığının amacı gövdelerin korunması (tasarımdan yeniden çekilebilir kalması); ESM ihracatı olmadan dosya Vite'a hiç giremez. Kural `CODE-STANDARD.md`'ye yazılır: **gövdeler birebir, dönüşüm yalnız son satırda**. Kullanılmayan primitifler (`ImgPH`, `Status`, `Pill`, `Arrow` …) dosyada kalır — Bölüm 5 kullanacak, Vite kullanılmayan ihracatları eler. |
| `create_app(dist_dir, blueprints=())` — feature blueprint'i **dışarıdan enjekte** edilir | `web/` altyapı katı; hiçbir feature'ı import etmemeli. Bağlama `main.py`'de (composition root). Testler kendi blueprint'ini `tmp_path` üstünde kurar — Drive'sız route testi. |
| Drive kökü `config.DRIVE_ROOT`, `QE_DRIVE_ROOT` ortam değişkeniyle geçersiz kılınır; notebook CONFIG'inde `DRIVE_FOLDER = "queenEditor"` | Colab'da kök `/content/drive/MyDrive/queenEditor`; geliştiricide lokal bir klasör, testte `tmp_path`. Klasör adının CONFIG'de durması repo'nun notebook deseni (`DRIVE_VIDEO_FOLDER`, `DRIVE_MODEL_FOLDER`). Kök Queen Editor'ün kendi klasörü — nova-3dcg'nin `photoGenV2`'si değil; sebep [bağımsızlık spec'inde](2026-07-25-queen-editor-bagimsizlik-design.md) (yabancı alt klasör hayalet proje kartı üretir). Ad tek düğme: CONFIG'deki `DRIVE_FOLDER`; kod, yorum ve docstring adı tekrar etmez, yalnız "Drive kökü" der. |
| Kök klasörü **notebook** oluşturur (`makedirs(exist_ok=True)`) ve fail-loud doğrular; backend oluşturmaz | Backend'in eksik kökü sessizce yaratması, mount edilmemiş Drive'da `/content/drive/...` altına **yerel diske** klasör açar — fotolar Colab kapanınca buharlaşır. Kök yoksa bu bir kurulum hatasıdır, hücrede patlar. |
| Yeni proje 201'de modal kapanır ve **liste yeniden çekilir** (iyimser ekleme yok) | Tek gerçek kaynak Drive; tarih de sunucudan gelir. Kartın ekranda görünmesi "Drive'da gerçekten var" demektir — bölümün kanıtı bu. |
| Modal **Escape**, **scrim tıklaması** ve **Vazgeç** ile kapanır | Standart davranış; tasarımda gösterilmemiş ama yokluğu hata gibi görünür. |
| UI'daki "sunucuya bağlı ✓" göstergesi kalkar; `/api/health` **ucu kalır** | Bağlantının kanıtı artık listenin kendisi. Uç notebook'ta Flask'ın ayağa kalkmasını beklemek için kullanılıyor — silinirse serve hücresi kırılır. |

## Mimari

### Backend

```
queen-editor/backend/
├── config.py                        + DRIVE_ROOT (env QE_DRIVE_ROOT ile override)
├── services/
│   └── drive/storage.py             list_dirs · make_dir — hiçbir şema bilmez
├── features/projects/
│   ├── domain/
│   │   ├── project.py               Project(name, modified_at)
│   │   ├── name_rules.py            validate(name) -> Türkçe hata mesajı | None   (saf)
│   │   ├── ports.py                 ProjectStore: list() · create(name) -> Project | None
│   │   └── usecases/
│   │       ├── list_projects.py     store.list() → modified_at azalan
│   │       └── create_project.py    doğrula → store.create() → çakışma kararı
│   ├── data/project_store.py        drive üstünde; queenEditor/<ad>/ düzenini bilen TEK yer
│   └── presentation/routes.py       make_projects_blueprint(list_projects, create_project)
├── web/app.py                       create_app(dist_dir, blueprints=())
└── main.py                          storage → store → use case → blueprint → create_app
```

Bağımlılık yönü `presentation → domain ← data → services`; `feature ↛ feature`, `servis ↛ feature`,
`servis ↛ servis`. `name_rules` ve iki use case saf: Flask'ı, dosya sistemini, Drive'ı bilmez.

**Servis sınırı.** `services/drive/storage.py` yalnız dosya sistemi konuşur:

```python
class DriveStorage:
    def __init__(self, root: str): ...
    def list_dirs(self) -> list[tuple[str, float]]: ...   # (ad, mtime) — kökün alt klasörleri
    def make_dir(self, name: str) -> float | None: ...    # mtime, veya None = zaten var (atomik)
```

`modifiedAt` uca çıkarken tam saniyeye indirilir (`int(mtime)`) — presentation'ın işi.

`queenEditor` adını, proje kavramını, `prompts.json`'u bilmez. `data/project_store.py` bu servisi
`Project` nesnelerine çevirir — düzeni bilen tek yer.

**Hata yolu.** Kök yoksa veya okunamazsa `list_projects` istisnayı yukarı geçirir; route bunu
`500 {"error": "<istisnanın kendi metni>"}` yapar. Metin uydurulmaz, `str(exc)` gönderilir
(örn. `[Errno 2] No such file or directory: '/content/drive/MyDrive/queenEditor'`) — UI onu
olduğu gibi mono kutuda gösterir.

### Uç sözleşmesi

| Uç | Yanıt |
|---|---|
| `GET /api/projects` | `200 {"projects": [{"name": "düğün", "modifiedAt": 1753180320}]}` — en son değişen ilk sırada · `500 {"error": "<gerçek hata metni>"}` |
| `POST /api/projects` `{"name": "…"}` | `201 {"name": "düğün", "modifiedAt": 1753180320}` · `400 {"error": "<kural mesajı>"}` · `409 {"error": "Bu ad zaten kullanılıyor. Başka bir ad dene."}` |

### Ad kuralları (`name_rules.py`)

Sıra önemli — ilk eşleşen mesaj döner. Hepsi Türkçe, tek dosyada:

| Kural | Mesaj |
|---|---|
| boş (veya yalnız boşluk) | `Proje adı boş olamaz.` |
| baş/son boşluk | `Proje adı boşlukla başlayamaz veya bitemez.` |
| 64 karakterden uzun | `Proje adı en fazla 64 karakter olabilir.` |
| yasak karakter `/ \ : * ? " < > \|` veya kontrol karakteri | `Proje adında şu karakterler kullanılamaz: / \ : * ? " < > \|` |
| baş/son nokta (`.`, `..` dahil) | `Proje adı nokta ile başlayamaz veya bitemez.` |

Türkçe harfler, boşluk, tire ve alt çizgi serbest: `kapak çekimi`, `lookbook-mayıs`, `düğün` geçerli.

### Frontend

```
queen-editor/frontend/src/
├── App.jsx                          → <ProjectsScreen />   (bağlantı göstergesi kalkar)
├── vendor/
│   ├── styles.css                   (Bölüm 2'de çekildi, değişmez)
│   └── kit.jsx                      tasarımdan kopya; yalnız son satır export'a çevrildi
├── shared/
│   ├── api.js                       listProjects() · createProject(name)
│   └── date.js                      formatModified(epoch) → "22 Tem 2026 · 14:32"
└── features/projects/
    ├── ProjectsScreen.jsx           header · ızgara · boş durum · hata kartı · modal
    ├── ProjectCard.jsx              4/3 kart: sol üst ad, sağ alt tarih — tıklanamaz
    ├── NewProjectModal.jsx          380px; hata mesajı kutunun altında
    └── useProjects.js               durum makinesi + oluşturma
```

`api.js` sunucunun mesajını kaybetmez: yanıt `ok` değilse gövdedeki `error` alanı okunup
`Error(mesaj)` olarak fırlatılır (gövde JSON değilse HTTP kodu kullanılır). UI bu mesajı gösterir.

`date.js` biçimlendirmeyi `Intl.DateTimeFormat("tr-TR")` ile yapar — ay adları tarayıcıdan gelir,
elle Türkçe ay tablosu tutulmaz.

`useProjects` üç durumlu: `loading` · `ready(projects)` · `error(mesaj)`. `create(name)` sunucuya
yazar; başarıda listeyi yeniden çeker, hatada mesajı modala geri verir (modal açık kalır).

### Ekran durumları (artboard eşlemesi)

| Durum | Görünen | Artboard |
|---|---|---|
| yükleniyor | header + boş gövde (kısa an) | — |
| dolu | 4 sütunlu kart ızgarası, en son değişen en üstte | 01 / 01b |
| boş | `henüz proje yok` + `İlk projeni oluştur, fotoğrafların burada toplansın` | 01a |
| hata | ⚠ `Projeler yüklenemedi` + mono kutuda sunucu mesajı + **Tekrar dene** | (yeni — tasarımda yok, artboard 06'nın hata satırı deseni) |
| modal | 380px kart: ad kutusu, `Vazgeç` / `Oluştur` | 02 |
| modal hata | kutu kırmızı çerçeveli, altında sunucu mesajı | 02 |

### Notebook

`app.ipynb` iki yerden değişir:

1. **CONFIG hücresi:** `DRIVE_FOLDER = "queenEditor"` eklenir.
2. **Yeni mount hücresi** (CONFIG'den sonra, klon hücresinden önce): `drive.mount('/content/drive')`
   → `MyDrive/<DRIVE_FOLDER>` yoksa oluştur → `DRIVE_ROOT` yazdır. Mount başarısızsa hücre patlar
   (mount edilmemiş Drive'a yazmak sessizce yerel diske yazmaktır).
3. **Serve hücresi:** Flask alt sürecine `env` ile `QE_DRIVE_ROOT=<DRIVE_ROOT>` geçirilir.
   Başlık markdown'ı Bölüm 3'ü anlatır.

Mount, Run all sırasında bir kez Google yetki tıklaması ister — Colab'da kaçınılmaz, repo'nun diğer
notebook'larıyla aynı desen.

## Test

`pytest`, `queen-editor/` kökünden. Hiçbiri Drive, ComfyUI veya tünel istemez.

| Ne | Nasıl |
|---|---|
| `name_rules` | tablo testi: geçerli adlar (`düğün`, `kapak çekimi`, 64 karakter) ve her kural için bir geçersiz ad → beklenen mesaj |
| `list_projects` | sahte `ProjectStore` → sıralama azalan `modified_at`; boş liste boş döner |
| `create_project` | sahte store → geçersiz ad `store.create`'e hiç gitmez; `create` `None` dönerse çakışma sonucu; geçerli adda `Project` döner |
| `DriveStorage` + `project_store` | `tmp_path` kök: klasör oluşur ve mtime döner, ikinci kez `None`, `list_dirs` ad+mtime döner |
| route'lar | `create_app(dist_dir=tmp, blueprints=[bp])` → `GET` 200 sıralı · `POST` 201 · geçersiz 400 · tekrar 409 · kök silinmişse 500 ve gövdede gerçek metin |
| Bölüm 2 | mevcut 4 test (health + statik) bozulmadan geçer |

Frontend'in testi yok (v1 kararı) — doğrulama Colab'da gözle.

## Doğrulama (kullanıcı, Colab)

1. `app.ipynb` → Run all: Drive mount yetkisi verilir, `queenEditor` kökü hazır, klon + Flask +
   tünel linki basılır.
2. Linke gir → **Projeler** ekranı, `henüz proje yok` metni.
3. **+ Yeni proje** → `kapak çekimi` → **Oluştur** → modal kapanır, kart ızgarada belirir (ad sol
   üstte, tarih sağ altta). Drive'da `MyDrive/queenEditor/kapak çekimi/` klasörü görünür.
4. Aynı adı tekrar dene → modal açık kalır, kutu kırmızı, altında `Bu ad zaten kullanılıyor.
   Başka bir ad dene.`
5. `foto/deneme` gibi geçersiz ad → yasak karakter mesajı aynı yerde.
6. İkinci bir proje oluştur → yeni kart **en üstte** çıkar.
7. Sayfayı yenile → projeler duruyor (kaynak Drive, bellek değil).
8. Karta tıkla → hiçbir şey olmaz (proje ekranı Bölüm 4-5).
9. (Negatif) Flask'ı durdur → sayfayı yenile → kırmızı **Projeler yüklenemedi** kartı + gerçek hata
   metni + **Tekrar dene**.
10. (Geliştirici, lokal) `pytest` → tüm testler geçer.

## Riskler

- **Drive FUSE'ta dizin mtime'ı.** "En son değişen en üstte" sırası klasör mtime'ına dayanıyor;
  mount edilmiş Drive'ın içine foto yazılınca üst klasörün mtime'ını güncellediği garanti değil.
  Bölüm 3'te sonuç doğru (klasör yeni oluşuyor); Bölüm 5'ten sonra sıra "oluşturma tarihi" gibi
  davranabilir. Gözlenir; yanlışsa Bölüm 6'da `prompts.json` zaten zaman taşıyacak, kaynak oraya
  taşınır.
- **Drive yazma gecikmesi.** Klasör oluşturma FUSE üstünden ~saniye sürebilir; 201 dönene kadar
  "Oluştur" düğmesi pasif tutulur, çift oluşturma olmaz.
- **Mount yetkisi Run all'ı böler.** Yetki penceresi gelene kadar sonraki hücreler beklemez —
  Colab'ın normal davranışı; mount hücresi tamamlanmadan link basılmaz çünkü serve hücresi sonrada.
- **Tünel URL'i herkese açık** (v1 kararı, umbrella spec). Artık Drive'a klasör açabilen bir uç var;
  URL rastgele ve oturumla ölüyor — kabul edildi.

## Kapsam dışı (Bölüm 3)

Proje ekranı ve kart tıklama (Bölüm 4-5) · `prompts.json` / ayar kaydı (Bölüm 6) · proje silme ve
yeniden adlandırma (v1 dışı) · kartta foto sayısı / kapak görseli (v1 dışı) · ComfyUI, üretim,
galeri · kimlik doğrulama.
