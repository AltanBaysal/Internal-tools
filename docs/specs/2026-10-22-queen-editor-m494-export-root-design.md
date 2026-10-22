# Madde 494 · Export'ların kendi kökü, `queenEditorExport` — tasarım

**Tarih:** 22 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md),
494 · **Dal:** `feat/queen-editor-v10` · **Kurallar:** queen-editor
[FOUNDATION](../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)
· **Üstüne kurulduğu:** [472 · `Storage`](2026-10-20-queen-editor-m472-storage-design.md),
[473 · `Exportlar`](2026-10-20-queen-editor-m473-exportlar-design.md)

## Kullanıcıdan gereken

Hiçbir şey: madde 22 Ekim'de hizalandı *(kullanıcı — "olur yap böyle", "queenEditorExport bu iyi")*.
Açık soru yok.

## Ne, neden

*(Kullanıcı, 22 Ekim — "proje yapısı böyle olunca exportu bulması zor oluyor", "exportları
queeneditorun içinde değil queen editorun yanında queen editor export diye açalım oraya koyalım";
taşıma için — "taşıma yok, exportlar boş, daha publish etmedik".)*

473 yeni export'ları `queenEditor/Exportlar/`'a koydu: klasör projelerin arasında duruyor, ve proje
listesinden ayrıca dışlanıyor. Bu maddeden sonra export'lar `queenEditor`'ün yanında, kendi
klasöründe: `MyDrive/queenEditorExport/<tarih> <proje>/`. İçi değişmez. `queenEditor`'de yalnız
projeler kalır, bu yüzden 473'ün `Exportlar` dışlaması gider.

```
MyDrive/
├── queenEditor/                       ← yalnız projeler
│   ├── arsiv.json
│   ├── Proje A/ ...
│   └── Proje B/ ...
└── queenEditorExport/                 ← her export'un kendi klasörü
    ├── 2026-10-22 14-30 Proje A/
    │   ├── foto/
    │   └── Proje A.mp4
    └── 2026-10-22 15-05 Proje B/
        ├── foto/
        └── video/01.mp4, 02.mp4
```

## Bugün — koddan okunanlar

- **Notebook** — CONFIG `DRIVE_FOLDER = "queenEditor"`; bağlama hücresi
  `DRIVE_ROOT = /content/drive/MyDrive/{DRIVE_FOLDER}`'ı `os.makedirs` ile açar ve var mı diye bakar;
  sunucuyu başlatan hücre onu `QE_DRIVE_ROOT` olarak verir. `config.DRIVE_ROOT` onu okur; yazılı
  değer yalnız ortam boşken.
- **`Storage`** *(472)* — tek kök bilir. Her işlemden önce kökü bir kez stat eder ve aygıtını ilk
  kullanımdakiyle karşılaştırır; her adı birleştirmeden önce sınırdan geçirir. Kökün **hemen
  altında** klasörü yalnız `make_dir` açar; bir kayıt yalnız demetin ilk parçasının altını açar
  (`_open_inside`). Kendi kökünü hiçbir zaman açmaz: önce stat eder.
- **`DrivePhotoStore(storage, exports)`** *(473)* — `exports` bir klasör adı (`"Exportlar"`);
  dakikalık klasör `_dated` = `("Exportlar", "<tarih> <proje>")`. `open_export` `make_dir("Exportlar")`
  çağırır, dakikalık klasörü ilk kayıt açar. `export_dir()` `<kök>/Exportlar`. `copy_photo` kaynağı
  proje klasöründen (`path(project, photo)`) okur, hedefi export klasörüne yazar.
- **`remove_export`** *(474)* — kendi videolarını siler; fotoğrafları yalnız başka export orayı
  kullanmıyorsa (`in_use`) ve orada başka çıktı yoksa; sonra `video/`'yu ve dakikalık klasörü boşsa
  siler.
- **`name_rules`** — `EXPORTS_DIR = "Exportlar"` ve `ARCHIVE_DIR = "arsiv"` ayrılmış adlar;
  `is_reserved` listelerde ve URL'den ad alan kapılarda (silme, yeniden adlandırma, arşivleme, iki
  ayar) soruluyor.
- **`main.py`** — `_storage = Storage(config.DRIVE_ROOT)`; `DrivePhotoStore(_storage,
  name_rules.EXPORTS_DIR)`.

## Ne değişir

### 1. Export'ların kökü notebook'tan: `QE_EXPORT_ROOT`

- **Notebook CONFIG:** `EXPORT_FOLDER = "queenEditorExport"`, `DRIVE_FOLDER`'ın altında.
- **Bağlama hücresi:** `EXPORT_ROOT = /content/drive/MyDrive/{EXPORT_FOLDER}`, `DRIVE_ROOT` gibi
  `os.makedirs` ile açılır ve var mı diye bakılır.
- **Sunucu hücresi:** `"QE_EXPORT_ROOT": EXPORT_ROOT`.
- **`config.EXPORT_ROOT`** = `os.environ.get("QE_EXPORT_ROOT",
  "/content/drive/MyDrive/queenEditorExport")` — `DRIVE_ROOT`'un yanında, onun gibi.

**Neden notebook, neden projeler kökünün kardeşi diye türetilmiyor:** FOUNDATION 7 — Drive'daki
klasörlerin adı tek bir yerde, CONFIG'de yazılır ve değiştirmek orada tek satırdır. `config.py`'de
`dirname(DRIVE_ROOT) + "queenEditorExport"` diye türetmek ikinci bir ad yeri olurdu.

**Neden kökü notebook açar:** `Storage` kendi kökünü açmaz, önce stat eder — bağlantı kopukken
açılan bir kök makinenin diskine düşer (472). Projeler kökü de böyle, bağlama hücresinde açılıyor;
export kökü onun yanında, aynı satırla. 473 `Exportlar`'ı notebook'ta açmamıştı, çünkü o
uygulamanın proje kökü içindeki kendi klasörüydü; şimdi bir kök, projeler kökü gibi.

### 2. İkinci `Storage`: export'lar onun kapısından geçer

`main.py`: `_exports = Storage(config.EXPORT_ROOT)`, `DrivePhotoStore(_storage, _exports)`.

- `Storage`'ın yapısı değişmez: hâlâ tek kök bilir, ve iki kök iki örnektir. Her biri kendi kökünü
  stat eder, kendi aygıtını kaydeder, kendi adlarını sınırdan geçirir. Export'un hiçbir yazması
  `queenEditorExport`'ın dışına çıkamaz; projeler kökündeki bir silme de oraya ulaşamaz.
- `DrivePhotoStore`'un ikinci argümanı bir ad değil, export'ların `Storage`'ı olur. Projeyle ilgili
  her şey (`save`, `read`, `delete`, `path`) projeler kapısından, export'un her yazması export
  kapısından geçer. `copy_photo` kaynağın yolunu projeler kapısından alır, hedefe export kapısıyla
  yazar.
- **`Storage`'ın üç cümlesi kökten söz eder:** "Proje köküne ulaşılamıyor", "Proje kökü başka bir
  aygıtta", "Proje kökü silinemez". Export kökü için yanlış ad olurlardı; "Kök klasöre
  ulaşılamıyor", "Kök klasör başka bir aygıtta", "Kök klasör silinemez." olur. Hangi kök olduğunu
  cümlenin kendisi söyler: OS'in hatası yolu taşıyor, aygıt cümlesi kökü yazıyor. Frontend'in test
  verisindeki eski cümle sunucunun ne dediğinin sahtesi; yine de yeni cümleye çekilir — yalnız
  testler, `dist` değişmez.

### 3. Dakikalık klasörü `open_export` açar

Dakikalık klasör artık kökün **hemen altında**: `_dated` = `"<tarih> <proje>"`, içindekiler
`(ad, "foto")` gibi. Bir kayıt kökün hemen altında klasör açmaz — orada olmayan bir klasör hata
olarak kalır, içinde tek dosyayla geri gelmez (472) — bu yüzden `open_export` onu `make_dir` ile
açar, 473'ün `Exportlar`'ı açtığı yerde. Zaten varsa (aynı dakikada öteki mod) `make_dir` `None`
döner ve bir şey olmaz. `foto/` ve `video/` bugünkü gibi ilk kayıtta açılır.

| Bugün (473) | Sonra |
|---|---|
| `DrivePhotoStore(storage, "Exportlar")` | `DrivePhotoStore(storage, exports)` — `exports` bir `Storage` |
| `_dated` = `("Exportlar", "<tarih> <proje>")` | `"<tarih> <proje>"` |
| `open_export`: `make_dir("Exportlar")` + `path` | `make_dir("<tarih> <proje>")` + `path` |
| `export_dir()` → `<projeler kökü>/Exportlar` | `<export kökü>` |

### 4. Temizlik dakikalık klasörü yalnız kimse yazmıyorken siler

473'te dakikalık klasör ikinci seviyedeydi: silinse bile öteki export'un ilk kaydı onu yeniden
açardı. Artık birinci seviyede ve bir kayıt onu açamaz. Örnek: birleşik export parçalarını kesiyor
(Drive'a henüz bir şey yazmadı, dakikalık klasör boş), aynı dakikada başlayan ayrı export iptal
ediliyor; temizliği boş klasörü silerse birleşik export dakikalar sonra ilk fotoğrafında
`FileNotFoundError` ile düşer.

**Karar:** `remove_export` dakikalık klasörü yalnız `in_use` yanlışken siler. `in_use` doğruysa
klasör öteki koşunundur: o biter (klasör dolar) ya da düşer ve kendi temizliğinde, artık kimse
yazmıyorken, klasörü siler. 474'ün sözü — boş kalan klasör silinir — böyle de tutar.

**İkisi birlikte iptal edilince** (ekranın İptal'i iki modu birden durdurur, `main.py`'nin
`_cancel_export`'u): iki temizlik de ötekini hâlâ yazıyor görürdü, ve ne paylaşılan fotoğraflar ne
klasör silinirdi — yarım bir export kalırdı. **Karar:** `ExportRunner.others_writing` iptal bayrağı
kalkmış bir modu yazıyor saymaz; o kendi yazdıklarını geri almaya gidiyor. Böylece temizliği son
yapan klasörü alır.

### 5. `Exportlar` ayrılmış ad olmaktan çıkar

- `name_rules.EXPORTS_DIR` gider; ayrılmış ad yalnız `arsiv`. `is_reserved` ve onu soran bütün kapılar
  kalır — `arsiv` için.
- `Exportlar` artık sıradan bir proje adı: yaratılabilir, listelenir.
- Testlerdeki `[EXPORTS_DIR, ARCHIVE_DIR]` parametreleri yalnız `ARCHIVE_DIR` kalır.

### 6. Ekran

Değişmez, `dist` yeniden kurulmaz: ekran sunucunun söylediği yolu yazıyor. "Şuraya yazılacak:"
altında `/content/drive/MyDrive/queenEditorExport`, bitince `…/queenEditorExport/<tarih> <proje>`.
Yalnız `ExportScreen.test.jsx`'in sahte özetindeki `/drive/Exportlar` yolu `/drive/queenEditorExport`
olur — test verisi, `dist`'e girmez.

### 7. Yorumlar ve belgeler

- `photo_store`, `name_rules`, `project_store`, `delete_project`, `rename_project` yorumları: export
  klasörü artık projelerin arasında değil.
- **CODE-STANDARD** — *Independence from collab-toolbox*: kökün tek istisnası `arsiv`; export'ların
  kendi kökü var (`QE_EXPORT_ROOT`, CONFIG'de `EXPORT_FOLDER`). *Services*: `Storage` kök başına
  bir örnek; kökün altında klasörü yalnız `make_dir` açar — bir proje, ya da başlarken bir
  export'un kendi klasörü.
- **FOUNDATION 7** — "tek Drive kökü, tek yerde adlandırılmış" → iki klasör, projeler ve yanında
  export'lar, ikisi de tek yerde, CONFIG'de adlandırılmış. Kuralın sebebi — ad değiştirmek tek
  satır — aynen kalır.
- Notebook'un ilk markdown'ı: export'ların yeri.

## Maliyet

Koddan sayıldı, ölçülmedi. Her satır bir dosya sistemi çağrısı = Colab'da Drive'a bir gidiş dönüş.

| İşlem | Bugün (473) | Sonra |
|---|---|---|
| Export'un başı | `make_dir("Exportlar")`: kontrol + `mkdir` (klasör çoğu zaman var, `stat` yok) + `path`'in kontrolü = 3; ilk export'ta + `stat` = 4 | `make_dir("<tarih> <proje>")`: kontrol + `mkdir` + `stat` + `path`'in kontrolü = 4; aynı dakikada öteki mod açtıysa `stat` yok, 3. Export başına bir kez, O(1) |
| İlk kayıt, açılan klasörler | `mkstemp` düşer → `<tarih> <proje>/`, `foto/` | `mkstemp` düşer → `foto/` — bir seviye az |
| Kare başına kayıt | `stamp` + kaynak `path` + `save_file` | aynı; kaynak yolu projeler kapısından, kayıt export kapısından |
| Export özeti | `path` = 1 | `path(())` = 1 |
| Temizlik | aynı | aynı; `in_use`'ta bir `rmdir` az |
| Proje listesi | `scandir` + bellekte süzme | aynı |

İki kapı iki ayrı kök stat'ı demek değil, her işlem yalnız kendi kapısınınkini yapar; sayı bugünkü
gibi.

## Ne kaybolabilir, ne bozulabilir

- **Export kökü yok** (bağlama hücresi atlandı, ya da kullanıcı klasörü Drive'da sildi) — export
  `Kök klasöre ulaşılamıyor: [Errno 2] … queenEditorExport` ile düşer, hiçbir şey yazılmaz; projeler
  çalışmaya devam eder. Kök yeniden açılmaz: projeler kökü de açılmıyor. Export ekranının özeti
  "Şuraya yazılacak:" için export kökünü sorar (`export_dir` → `path(())`, kontrolle), bu yüzden
  eksik bir `queenEditorExport` hatasını export başlamadan, ekran açılırken gösterir.
- **Bağlantı kopukken export** — `open_export`'un `make_dir`'i kontrolde düşer, `StorageError`;
  makinenin diskine bir şey açılmaz. Kontrolle `mkdir` arasında kopan bağlantıda `mkdir` üst klasör
  olmadığı için `FileNotFoundError` verir.
- **Aynı dakikada iki export** — ikisi de `make_dir`'i çağırır; biri açar, öteki `None` alır, klasörü
  paylaşırlar (474). Biri düşerken öteki yazıyorsa dakikalık klasör kalır (karar 4).
  **Kabul edilen pencere:** öteki koşu `open_export` ile ekrana `target`'ını bildirmesi arasındaysa
  (`make_dir` + `path`, iki gidiş dönüş) koşucu onun hedefini henüz bilmez ve `in_use` yanlış döner;
  o anda düşen koşu boş klasörü silerse öteki ilk kaydında `FileNotFoundError` ile düşer ve ekrana
  yazar. Hiçbir şey kaybolmaz; export yeniden başlatılır.
- **İkisi birlikte iptal** — iptal edilmiş mod yazıyor sayılmaz (karar 4), temizliği son yapan
  fotoğrafları ve boş klasörü alır; yarım export kalmaz. İptal bir iş biriminin ortasında gelirse o
  mod birimini bitirene kadar yazar; klasör o arada giderse kaydı `FileNotFoundError` ile düşer, koşu
  hata gösterir ve kendi temizliğini yapar — Drive'da yarım bir şey kalmaz.
- **Kayıt ortasında ölen makine** — dakikalık klasör yarım kalabilir; bugünkü gibi (madde 96).
- **Proje silinince ya da yeniden adlandırılınca** — export'lar başka bir kökte, projeler kapısının
  hiçbir işlemi oraya ulaşamaz.
- **Ad** — dakikalık klasörün adı tarih (`YYYY-MM-DD HH-MM`) + boşluk + var olan bir projenin adı;
  export kapısı adı yine sınırdan geçirir.
- **`queenEditor/Exportlar/`** — v10 yayımlanmadı, export yok; taşıma yok. Kullanıcının denemesinde
  açılmış bir `Exportlar` olursa artık bir proje kartı olarak görünür; Drive'da elle silinir.

## Bu maddenin kararları

1. **Export kökü notebook'tan, `QE_EXPORT_ROOT`;** CONFIG'de `EXPORT_FOLDER`, bağlama hücresi açar.
   Kardeş diye türetilmez: ad tek yerde.
2. **İkinci bir `Storage` örneği;** `Storage`'ın yapısı değişmez, yalnız kökten söz eden üç cümlesi
   genelleşir.
3. **`DrivePhotoStore(storage, exports)`'un `exports`'u bir `Storage`.**
4. **Dakikalık klasörü `open_export` `make_dir` ile açar,** export başına bir kez.
5. **Temizlik dakikalık klasörü yalnız `in_use` yanlışken siler.**
6. **`Exportlar` ayrılmış ad olmaktan çıkar;** `arsiv` kalır.
7. **İptal edilmiş bir mod `others_writing`'de yazıyor sayılmaz,** ikisi birlikte iptal edilince yarım
   export kalmasın diye.

## Sınırlar

- Taşıma yok; `queenEditor/Exportlar/`'a ve 473'ten önceki `<proje>/export/<tarih>/`'lere dokunulmaz.
- Frontend kodu değişmez, `dist` yeniden kurulmaz.
- Notebook'un `BRANCH` satırı `"feat/queen-editor-v10"` kalır; `test_notebook_clones_its_branch`'in
  iki testi bilerek kırmızı.

## Bitti sayılır

1. Testler gösteriyor ki:
   - bir export bitince `<export kökü>/<tarih> <proje>/`'de duruyor — ayrıda `video/01.mp4` ve `foto/`,
     birleşikte `<proje>.mp4` ve `foto/` — projeler kökünde `Exportlar` ya da `export/` açılmamış
     (route düzeyinde, gerçek iki `Storage` ile);
   - `open_export` dakikalık klasörü açıyor ve yolunu dönüyor, varsa dokunmuyor; export kökünün
     bağlantı kontrolü düşünce hiçbir şey açılmıyor;
   - export kökü yoksa export düşüyor ve kök açılmıyor;
   - export özeti export kökünü gösteriyor;
   - öteki export yazarken düşen export'un temizliği boş dakikalık klasörü bırakıyor, kimse
     yazmıyorken siliyor; ikisi birlikte iptal edilince ikisinin temizliğinden sonra export kökü boş;
   - `Exportlar` geçerli bir proje adı ve listede görünüyor; `arsiv` hâlâ ayrılmış;
   - `main.py` export'ları `QE_EXPORT_ROOT`'a yazıyor;
   - notebook export kökünü açıyor ve sunucuya `QE_EXPORT_ROOT` diye veriyor.
2. `python -m pytest queen-editor -q` — `test_notebook_clones_its_branch`'in bilerek kırmızı iki
   testi dışında yeşil; `npm test --prefix queen-editor/frontend` yeşil.
