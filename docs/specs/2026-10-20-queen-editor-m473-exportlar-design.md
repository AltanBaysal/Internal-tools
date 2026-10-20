# Madde 473 · `Exportlar` klasörü — tasarım

**Tarih:** 20 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md),
473 · v10-2a · **Dal:** `feat/queen-editor-v10` · **Kurallar:** queen-editor
[FOUNDATION](../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)
· **Üstüne kurulduğu:** [472 · `Storage`](2026-10-20-queen-editor-m472-storage-design.md)

## Kullanıcıdan gereken

Hiçbir şey: madde 20 Ekim'de hizalandı ve kullanıcı klasör ağacını onayladı *(kullanıcı — "bu
olsun")*. Açık soru yok.

## Ne, neden

*(Kullanıcı, 20 Ekim — "Export dosyaları proje dosyalarının içine değil, ayrı bir klasöre
kaydedilsin", "Sorun: Export'lar proje dosyalarının arasına karışıyor, bulmak zor."; 3 Ekim —
"Exporltar ve projeler iki klasöre ayrılsa ve exportlarda export tarhi ve proje adı olarak
adlandırılsa bulması oldukça kolaylaşırdı".)*

Bugün bir export `queenEditor/<proje>/export/<YYYY-MM-DD HH-MM>/`'ye yazılıyor: onu bulmak için önce
projeyi, sonra içinde `export/`'u açmak gerekiyor. Bu maddeden sonra yeni export'lar projelerin
yanındaki tek bir klasöre, `queenEditor/Exportlar/`'a gider; her export'un orada kendi klasörü var,
adı önce tarih sonra proje: `2026-10-20 14-30 Proje A`. Drive adla dizdiği için en yeni export'lar bir
arada durur.

```
MyDrive/queenEditor/
├── arsiv.json
├── Exportlar/
│   ├── 2026-10-20 14-30 Proje A/
│   │   ├── foto/
│   │   └── Proje A.mp4
│   └── 2026-10-21 09-45 Proje B/
│       ├── foto/
│       └── video/01.mp4, 02.mp4
├── Proje A/
│   ├── settings.json, plan.json, ... 001.png, 001_V1_1.mp4, referans/
│   └── export/2026-10-18 21-05/ ...   ← eski, kalır; buraya yeni bir şey yazılmaz
└── Proje B/ ...
```

## Bugün — koddan okunanlar

- **`photo_store`** *(photo_generation/data)* — `EXPORT_DIR = "export"`; dakikalık klasör
  `_dated(project, stamp)` = `(proje, "export", tarih)`, Storage'a demet olarak. `export_dir(project)`
  özetin gösterdiği yol (`<kök>/<proje>/export`), `export_folder(project, stamp)` koşunun ekrana
  verdiği yol; ikisi de `Storage.path`'ten, hiçbir şey açmaz. `copy_photo`, `copy_video`,
  `copy_export`, `remove_export` hep `_dated`'i kullanıyor. İçerideki `foto/` ve `video/` adları
  `PHOTOS_DIR` / `VIDEOS_DIR`.
- **`run_export`** — `folder = store.export_folder(project, stamp)`; `target` ve dönen değer o.
  Sonra `make_pieces_dir`, sonra iş.
- **`export_summary`** — `"folder": store.export_dir(project)`. Ekran
  ([ExportScreen.jsx](../../queen-editor/frontend/src/features/photo_generation/ExportScreen.jsx))
  "Şuraya yazılacak:" altında `summary.folder`'ı, bitince `runs[mode].target`'ı olduğu gibi yazıyor:
  yolu sunucu söylüyor, ekranın kendi bilgisi yok.
- **`Storage`** *(472)* — bir kayıt kökü ve bir **kökün hemen altındaki** klasörü hiçbir zaman açmaz:
  `_save` geçici dosyayı açamazsa yalnız demetin **ilk parçasından aşağısını** açar (`_open_inside`),
  ilk parça açılmaz. Kökte klasör açan tek yöntem `make_dir(name)`: önce kontrol (kök stat'ı + aygıt),
  sonra `os.mkdir`; ad doluysa `None`.
- **`name_rules`** *(projects/domain)* — adın tek kuralı; `ARCHIVE_DIR = "arsiv"` her harf biçimiyle
  (`casefold`) ayrılmış: "Bu ad ayrılmış, başka bir ad dene." `create_project`, `rename_project` ve
  yazarken soran `check_name` hep `validate`'ten geçiyor.
- **`project_store.list`** — kökün klasörleri projelerdir; `ARCHIVE_DIR` atlanıyor.
  `list_archived` yalnız işaretli adları listeliyor.
- **Özellikler birbirini içe aktaramaz** *(CODE-STANDARD — `feature ↛ feature`)*; ikisinin
  buluştuğu tek yer `main.py`.

## Ne değişir

### 1. Ad: `name_rules.EXPORTS_DIR = "Exportlar"`

Kökte proje olmayan klasörlerin adını projects özelliği tutar — `project_store` "kökün her klasörü
bir projedir" diyen tek yer, ve `arsiv` de orada. `Exportlar` onun yanına girer:

- `is_reserved(name)` — saf, `casefold` ile: ad uygulamanın kendi klasörlerinden biri mi (`arsiv`,
  `Exportlar`). Ayrılmış bir klasör proje değildir; aşağıdakilerin hepsi bunu sorar.
- `validate` her harf biçimiyle reddeder (`exportlar`, `EXPORTLAR` — depo Windows'ta da koşuyor, orada
  ikisi bir klasör), `arsiv`'in cümlesiyle: "Bu ad ayrılmış, başka bir ad dene." Yaratma, yeniden
  adlandırma ve yazarken soru aynı kuraldan geçtiği için üçü birden.
- `project_store.list` ve `list_archived` onu atlar: hiçbir liste onu kart olarak çizmez.
- **URL'den gelen ad.** Tünel herkese açık ve girişsiz; reviewer Flask'ın test istemcisiyle denedi:
  `DELETE /api/projects/Exportlar` bütün export'ları siliyordu, `…/Exportlar/rename` klasörü bir
  proje kartına çeviriyordu, `…/Exportlar/archive` onu Sil düğmeli bir arşiv kartı yapıyordu.
  `delete_project`, `rename_project` (eski ad) ve `archive_project` ayrılmış bir ad için hiçbir şeye
  dokunmadan — `delete`'te üretimi durdurmadan da — `ProjectMissing` (404) verir. Ayarların kapıları
  da: `get_settings` (`GET …/settings` ve `GET …/reference-settings`), `save_settings`
  (`PUT …/settings`) ve `save_reference_settings` (`PUT …/reference-settings`) projenin var olup
  olmadığını sordukları yerde ayrılmış adı da sorar; QA `Exportlar/settings.json`'ın ve
  `reference_settings.json`'ın URL'den yazılabildiğini görmüştü. `arsiv` 221'den beri aynı
  açıktaydı, o da kapanır.

### 2. Yer: `DrivePhotoStore(storage, exports)`

`photo_store` adı kendisi yazmaz, `main.py` ona `name_rules.EXPORTS_DIR`'i verir: iki özellik aynı
klasörü ayrı ayrı yazsa biri değişince öteki eski adda kalır, ve korunan ad export'ların gittiği klasör
olmaktan çıkar. `main.py` iki özelliğin buluştuğu yer zaten.

| Bugün | Sonra |
|---|---|
| `_dated(project, stamp)` = `(proje, "export", tarih)` | `(exports, f"{tarih} {proje}")` |
| `export_dir(project)` → `<kök>/<proje>/export` | `export_dir()` → `<kök>/Exportlar` — ekranın "Şuraya yazılacak:"ı; proje adı artık yolda değil |
| `export_folder(project, stamp)` → yol, hiçbir şey açmaz | `open_export(project, stamp)` → `Exportlar`'ı gerekiyorsa açar (`make_dir`), dakikalık klasörün yolunu döner |
| `EXPORT_DIR = "export"` | gider: oraya bir şey yazılmaz, onu okuyan da yok |

`copy_photo`, `copy_video`, `copy_export`, `remove_export` imzalarıyla aynı kalır; `_dated`'den
geçtikleri için hepsi yeni yere gider. İçerisi değişmez: `foto/`, ayrı export'ta `video/01.mp4…`,
birleşikte `<Proje>.mp4`.

### 3. `Exportlar/` nasıl açılır

`Storage` bir kaydın kökün hemen altındaki bir klasörü açmasına izin vermez (472, "örtük klasör
yok"): bağlantı koparsa yol makinenin kendi diskinde yeniden açılır ve kayıt oraya düşer. `Exportlar`
kökün hemen altında, yani ilk `foto/01.png` kaydı onu açamaz — `_open_inside` demetin ilk parçasını
atlar, ve kayıt `FileNotFoundError` verir.

**Karar:** `Exportlar`'ı her export'un başında `open_export` açar, `Storage.make_dir` ile — kökte
klasör açan tek yöntem, ve kontrolden geçerek: bağlantı kopuksa `StorageError` verir ve makinenin
diskine bir şey yazılmaz. Klasör zaten varsa `make_dir` `None` döner ve bir şey olmaz. Dakikalık
klasör ve içindekiler bugünkü gibi ilk kayıtta açılır (`_open_inside`, `Exportlar`'ın altından).

Neden burada, neden böyle:

- `Storage` değişmez: kurallarını "kökte yalnız `make_dir` açar" diye koruyor, ve bir özelliğin
  klasör adını bilmesi ona girmez *(CODE-STANDARD — "no project, no JSON, no schema")*.
- Notebook'un bağlama hücresi değişmez: `Exportlar`'ı orada açmak, uygulamanın kendi yazdığı bir
  klasörü başka bir yere bağlardı, ve hücreyi atlayan bir oturum ilk export'ta düşerdi.
- Her kayıttan önce değil, koşu başına bir kez: kayıt başına bir `make_dir` N kare için N gidiş
  dönüş demek.
- `run_export`'ta `open_export`, makinedeki parça klasöründen (`make_pieces_dir`) **önce**: düşerse
  ne Drive'da ne makinede temizlenecek bir şey kalır; hata koşunun hatası olarak ekrana gelir
  (`ExportRunner._run`).

### 4. Ekran

Değişmez, `dist` yeniden kurulmaz: ekran sunucunun söylediği yolu yazıyor. "Şuraya yazılacak:"
altında `<kök>/Exportlar`, export bitince `<kök>/Exportlar/<tarih> <proje>`. Frontend testlerinin
sahte özetindeki yol (`/drive/düğün/export`) sunucunun yeni cevabına çekilir; bu yalnız test verisi,
`dist`'e girmez.

### 5. Yorumlar ve belgeler

- `rename_project` docstring'i: "her şey proje klasöründe, export'lar da" artık doğru değil — yeni
  export'lar `Exportlar`'da, yapıldıkları adla kalır; yeniden adlandırma onları taşımaz.
- **CODE-STANDARD**, *Independence from collab-toolbox*: "Every direct subfolder of our Drive root is
  a project" → projects özelliğinin ayırdığı iki ad dışında (`Exportlar`, `arsiv`). *Services*:
  kökün altında klasörü yalnız `make_dir` açar — bir proje, ya da export başlarken `Exportlar`.
- `name_rules`'taki `ARCHIVE_DIR` yorumu bayattı (başlangıçta o klasöre bakan bir onarım yok); tek
  doğru cümleye iner.
- FOUNDATION değişmez.

## Maliyet

Koddan sayıldı, ölçülmedi. Her satır bir dosya sistemi çağrısı = Colab'da Drive'a bir gidiş dönüş.

| İşlem | Bugün | Sonra |
|---|---|---|
| Export'un başı | `export_folder`: kontrol = 1 | `open_export`: `make_dir` (kontrol + `mkdir`; ilk seferde + `stat`) + `path` (kontrol) = 3–4, export başına bir kez, O(1) |
| İlk kayıt, açılan klasörler | `mkstemp` düşer → `export/` (zaten var), `<tarih>/`, `foto/` | `mkstemp` düşer → `<tarih> <proje>/`, `foto/` — bir seviye az |
| Kare başına kayıt | aynı | aynı |
| Export özeti | `path` = 1 | `path` = 1 |
| Proje listesi | `scandir` | aynı; süzme bellekte |

## Ne kaybolabilir, ne bozulabilir

- **Eski export'lar** — `<proje>/export/<tarih>/`'e hiçbir şey dokunmaz: ne taşınır ne silinir;
  yeniden adlandırma onları bugünkü gibi projeyle birlikte taşır.
- **Bağlantı kopukken export** — `open_export`'un `make_dir`'i kontrolde düşer, `StorageError`;
  makinenin diskine `Exportlar` açılmaz. Kontrolle `mkdir` arasında kopan bir bağlantıda `mkdir` kök
  yolu olmadığı için `FileNotFoundError` verir — üst klasörleri açmaz.
- **Aynı dakikada iki export** (birleşik ve ayrı) — ikisi de `make_dir`'i çağırır; biri açar, öteki
  `None` alır. Dakikalık klasörü bugünkü gibi paylaşırlar. Bu paylaşımın temizlik hatası 474'ün işi.
- **Kayıt ortasında ölen makine** — `Exportlar` boş ya da yarım bir dakikalık klasörle kalabilir;
  bugünkü gibi (oturuma bağlı export, madde 96).
- **Düşen export'un temizliği** — `remove_export` yalnız dakikalık klasörü siler, `Exportlar`'ı
  hiçbir zaman: demet `(Exportlar, "<tarih> <proje>")`.
- **Proje silinince ya da yeniden adlandırılınca** — yeni export'ları `Exportlar`'da, yapıldıkları
  adla kalır. Export kullanıcının teslim ettiği iş; projeyle silinmemesi FOUNDATION 1'e uyar.
- **URL'den `Exportlar` ya da `arsiv`** — silme, yeniden adlandırma, arşivleme ve iki ayarın okunup
  yazılması 404 verir, klasör ve içindekiler yerinde kalır, içine bir dosya yazılmaz.
- **Ad** — dakikalık klasörün adı tarih (`YYYY-MM-DD HH-MM`, iki nokta yok) + boşluk + proje adı;
  proje adı zaten `/ \ :` taşıyamaz, ve `Storage` parçayı yine de sınırdan geçirir.

## Bu maddenin kararları

1. **Ad projects'te** (`name_rules.EXPORTS_DIR`), `arsiv`'in yanında; `photo_store`'a `main.py`
   verir. İki kopya yok.
2. **`Exportlar`'ı export'un başında `make_dir` açar**, koşu başına bir kez; `Storage` ve notebook
   değişmez.
3. **`export_folder` → `open_export`**: artık bir şey açtığı için adı bunu söyler.
4. **`export_dir()` proje almaz** — yolda proje yok. Özet projeyi yine `list_frames`'le sorar (yoksa
   404).
5. **Ekranın "Şuraya yazılacak:"ı `<kök>/Exportlar`** — export'un kendi klasörünün adı ancak
   başladığı dakikada belli; bitince `target` tam yolu gösterir.
6. **Ayrılmış klasör proje değildir** — `is_reserved` listelerde, projeyi adıyla silen, taşıyan,
   arşivleyen üç kapıda ve iki ayarın okuma ve yazma kapılarında; cevap 404 "Proje yok", bir projenin
   olmadığı gibi.

## Sınırlar

- Eski export'lar taşınmaz; `EXPORT_DIR` sabiti gider ama diskteki klasörler kalır.
- 474'ün iki hatası (`01` adlı projede birleşik dosyanın bir parçanın üstüne yazılması, temizliğin
  öteki modun dosyalarını silmesi) bu maddede değil.
- Bugün adı — harf biçimi ne olursa olsun — `Exportlar` olan bir proje varsa listeden kaybolur ve
  yeni export'lar onun içine yazılır. Uygulama artık böyle bir projeyi silemez, yeniden
  adlandıramaz ve arşivleyemez. Böyle bir proje olduğu bilinmiyor; varsa Drive'da elle yeniden
  adlandırılması gerekir.
- photo_generation'ın kapıları (üretim, export, kare silme) ayrılmış bir adı yine bir klasör olarak
  bulur, ama hiçbiri bir klasörü toptan silmez; olduğu gibi kalırlar.
- Notebook, `Storage` ve frontend kodu değişmez.

## Bitti sayılır

1. Testler gösteriyor ki:
   - bir export bitince `<kök>/Exportlar/<tarih> <proje>/`'de duruyor — ayrıda `video/01.mp4` ve
     `foto/`, birleşikte `<proje>.mp4` ve `foto/` — ve proje klasöründe `export/` açılmamış
     (route düzeyinde, gerçek `Storage` ile);
   - `Exportlar` yokken ilk export onu açıyor; varken dokunmuyor; bağlantı kontrolü düşünce açılmıyor
     ve hiçbir şey yazılmıyor;
   - `open_export` parça klasöründen önce çağrılıyor, ve `target` onun yolu;
   - export özeti `<kök>/Exportlar`'ı gösteriyor;
   - `Exportlar`, `exportlar`, `EXPORTLAR` proje adı olarak reddediliyor (yaratma ve yeniden
     adlandırma), ve ne proje listesi ne arşiv listesi onu gösteriyor;
   - `Exportlar` ve `arsiv` için `DELETE /api/projects/<ad>`, `…/rename` ve `…/archive` 404
     veriyor, klasör ve içi yerinde, üretim durdurulmamış;
   - ikisi için `GET` ve `PUT …/settings` ile `…/reference-settings` 404 veriyor ve klasöre bir dosya
     yazılmıyor;
   - eski `<proje>/export/<tarih>/` klasörüne dokunulmuyor;
   - `main.py` export'ları korunan adın klasörüne yazıyor.
2. İki satır yeşil: `python -m pytest queen-editor -q` ve `npm test --prefix queen-editor/frontend`.
