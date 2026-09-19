# Madde 221 · Projeler arşivlenebilecek — test turunun tasarımı

**Tarih:** 16 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Karar

Kullanıcı sorulmadan verdi: *"proje durumu değil, arşiv klasörü olsun — basınca oraya gitsin,
akıllılık yapmasın."* Yani arşiv bir **işaret değil, bir yer**: proje klasörü Drive kökündeki
`arsiv/` altına **taşınıyor**.

Bu seçim iki soruyu kendiliğinden cevaplıyor, ve maddenin sorduğu ikinci kararı ortadan kaldırıyor:

- **Arşivdeki proje listede yok**, çünkü artık kökte değil.
- **Açılamaz, üretilemez, dışa aktarılamaz** — `project_exists` onu bulamıyor. Bunun için ayrıca
  bir kural yazmaya gerek yok; taşımanın kendisi kuralı kuruyor.
- **Geri getirmek = geri taşımak.**

## Bugün ne var

- Bir proje **Drive'daki bir klasör**: `MyDrive/queenEditor/<proje>/`.
  [`DriveStorage.list_dirs`](../../../queen-editor/backend/services/drive/storage.py) kökün **her**
  alt klasörünü veriyor, [`list_projects`](../../../queen-editor/backend/features/projects/domain/usecases/list_projects.py)
  onları son değişme tarihine göre sıralıyor. Süzme yok, sayfalama yok.
- [`Project`](../../../queen-editor/backend/features/projects/domain/project.py) yalnız **ad ve
  tarih** taşıyor — durum diye bir alan hiç yok, ve bu kararla hiç olmayacak da.
- **Silme ve yeniden adlandırma zaten var.** `rename_project` işi
  [`DriveStorage.rename_dir`](../../../queen-editor/backend/services/drive/storage.py)'a veriyor:
  kopyalamıyor, `os.rename` ediyor — *"one operation that either happened or did not"*. Arşivleme de
  aynı hareket, yalnız hedefi bir alt klasör.
- `delete_project` **önce `halt(name)`** çağırıyor: koşan bir üretim, klasörü kaybolan bir yere
  yazmasın diye. Arşivleme de taşıma olduğu için aynı şeye ihtiyaç duyuyor.

## Tuzak: arşiv klasörünün kendisi proje gibi görünür

`list_dirs` kökteki her klasörü proje sayıyor. `arsiv/` kökte duracağına göre, hiçbir şey
yapılmazsa **listede "arsiv" adlı bir proje** belirir. İki yerde kapatılıyor:

1. Proje listesi bu adı **atlıyor**.
2. `arsiv` **ayrılmış bir ad**: o adla proje açmak ya da bir projeyi o ada çevirmek reddediliyor,
   ve rediin cümlesi öteki ad kurallarıyla aynı yerden geliyor
   *([`name_rules`](../../../queen-editor/backend/features/projects/domain/name_rules.py))*.
   **Büyük-küçük harf ayırmadan**, çünkü depo Windows'ta da koşuyor ve orada `Arsiv` ile `arsiv`
   aynı klasör.

## Çivilenecek olgular

### Ad kuralı

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | `arsiv` proje adı olarak reddediliyor, harf büyüklüğü fark etmeden | **kırmızı** |
| 2 | Redin cümlesi Türkçe ve sebebini söylüyor | **kırmızı** |

### Klasör katmanı

| # | Ne diyor | Bugün |
|---|---|---|
| 3 | `list_dirs` bir alt klasörün içini de listeleyebiliyor | **kırmızı** |
| 4 | `rename_dir` hedefin üst klasörünü yoksa açıyor — ilk arşivleme boş bir `arsiv/`'e düşmüyor | **kırmızı** |
| 5 | Taşıma hâlâ `os.rename`, yani kopya yok | yeşil, ve öyle kalmalı |

### Proje deposu

| # | Ne diyor | Bugün |
|---|---|---|
| 6 | Proje listesi `arsiv` klasörünü proje olarak göstermiyor | **kırmızı** |
| 7 | Arşiv listesi `arsiv/` içindekileri veriyor, aynı `Project` biçiminde | **kırmızı** |
| 8 | Arşivlemek klasörü taşıyor: kökte yok, arşivde var | **kırmızı** |
| 9 | Geri almak tersini yapıyor | **kırmızı** |
| 10 | Arşivlenen proje artık **yok sayılıyor** — `project_exists` false | **kırmızı** |

Onuncusu, kararın bedava verdiği şeyin çivisi: üretim ve dışa aktarma projeye adıyla ulaşıyor, ve
taşınmış bir projeyi bulamıyorlar. Ayrı bir yasak yazılmıyor; yazılmadığı **burada** kanıtlanıyor.

### Kullanım

| # | Ne diyor | Bugün |
|---|---|---|
| 11 | Arşivlemeden **önce** koşan üretim durduruluyor | **kırmızı** |
| 12 | Olmayan bir projeyi arşivlemek `ProjectMissing` | **kırmızı** |
| 13 | Arşivde aynı adla bir şey varsa `NameTaken` | **kırmızı** |
| 14 | Arşivde olmayanı geri almak `ProjectMissing` | **kırmızı** |
| 15 | Kökte aynı adla bir proje varken geri almak `NameTaken` | **kırmızı** |

Onbirincisi `delete_project`'in kuralının aynısı ve aynı sebeple: taşınan klasöre yazan bir işçi,
yarısı burada yarısı orada bir proje bırakır.

### Rotalar

| # | Ne diyor | Bugün |
|---|---|---|
| 16 | `POST /api/projects/<p>/archive` arşivliyor ve 204 dönüyor | **kırmızı** |
| 17 | `POST /api/projects/<p>/restore` geri alıyor | **kırmızı** |
| 18 | `GET /api/projects/archived` arşivdekileri listeliyor | **kırmızı** |
| 19 | Her red kendi kodunu taşıyor — yok 404, dolu 409, işletim sistemi 500 | **kırmızı** |

Ondokuzuncusu yeni bir sözleşme değil: `delete` ve `rename` bugün tam olarak bunu yapıyor, ve
arşivin farklı davranması ön yüzde ikinci bir hata dili doğururdu.

### Ön yüz

| # | Ne diyor | Bugün |
|---|---|---|
| 20 | Proje kartında bir **Arşivle** düğmesi var | **kırmızı** |
| 21 | Başlıkta bir **Arşiv** anahtarı var; açıkken liste arşivdekileri gösteriyor | **kırmızı** |
| 22 | Arşiv görünümündeki kartta sil/yeniden adlandır yok, **Geri al** var | **kırmızı** |
| 23 | Arşivlemek ve geri almak listeyi Drive'dan **yeniden okuyor** | **kırmızı** |

Yirmiüçüncüsü ekranın kendi kuralı — *"Drive is the single source of truth: re-read the list rather
than guess which card disappeared"*.

## Bu turda değişen

Yalnız testler:

- `queen-editor/backend/tests/test_projects.py` *(ya da ad kuralları nerede duruyorsa)* — 1–2, 6–15
- `queen-editor/backend/tests/test_storage.py` — 3–5
- `queen-editor/backend/tests/test_project_routes.py` — 16–19
- `queen-editor/frontend/src/features/projects/ProjectsScreen.test.jsx` ve `ProjectCard.test.jsx` — 20–23
