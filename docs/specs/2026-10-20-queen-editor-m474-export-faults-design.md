# Madde 474 · Export'un iki eski hatası — tasarım

**Tarih:** 20 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md),
474 · v10-2b · **Dal:** `feat/queen-editor-v10` · **Kurallar:** queen-editor
[FOUNDATION](../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)
· **Üstüne kurulduğu:** [472 · `Storage`](2026-10-20-queen-editor-m472-storage-design.md),
[473 · `Exportlar`](2026-10-20-queen-editor-m473-exportlar-design.md)

## Kullanıcıdan gereken

Hiçbir şey: madde 20 Ekim'de hizalandı *(kullanıcı — "tamma olur")*. Fotoğrafların iki export
arasında paylaşıldığı ortaya çıkınca ana ajan 20 Ekim'de kullanıcının kararından cevapladı: düşen bir
export'un temizliği öteki export'un dosyalarını bırakır; fotoğraflar paylaşıldığı için klasörün,
koşan ya da bitmiş bir export'tan kaybolmaz (aşağıda, 2).

## Ne, neden

472'de iki eski hata bulundu, ikisi de export'un kendisinde:

- **(a)** Birleşik export parçalarını makinede `01.mp4`, `02.mp4`, … diye keser, ve birleştirdiği
  dosyayı aynı klasöre `<proje>.mp4` diye yazar. Adı `01` olan bir projede bu bir parçanın adı:
  ffmpeg çıktısını açarken (`-y`) kendi girdisini siler, ve birleşik dosya bozuk çıkar.
- **(b)** Ayrı ve birleşik export aynı dakikada başlarsa aynı tarihli klasörü paylaşır (tasarım v3,
  92). Düşen ya da iptal edilen bir export'un temizliği **bütün klasörü** siliyor: ötekinin yazdıkları
  da gidiyor — koşuyor olsa da, bitmiş olsa da.

## Bugün — koddan okunanlar

- **`run_export`** *(photo_generation/domain/usecases)* — `_write` önce videoları keser (ayrıda her
  parça kesilince `copy_video` ile Drive'a, `video/NN.mp4`), sonra fotoğrafları (`copy_photo`,
  `foto/NN.<uzantı>`), birleşikte en sonda `joined = piece_path(pieces_dir, f"{project}.mp4")`,
  `merge`, `copy_export(…, f"{project}.mp4")`. Düşerse ya da iptal edilirse `_clean`: önce
  `remove_pieces`, sonra `remove_export` (bütün dakikalık klasör). Temizlik de düşerse cümle
  "<koşunun hatası> — Yarım export silinemedi: …", koşunun hatası sebep olarak; iptal bir kez
  temizlenir.
- **`photo_store`** — `_dated` = `(Exportlar, "<tarih> <proje>")`. `copy_photo` hedefte dosya varsa
  (`stamp`) yazmaz: aynı dakikadaki iki export'tan fotoğrafa önce hangisi varırsa o yazar, öteki
  bulur ve geçer (madde 236). Yani `foto/` iki export'undur. `remove_export` = `delete_dir(_dated)`.
- **`ExportRunner`** — mod başına durum; koşan bir modun `target`'ı yazdığı klasörün yolu
  (`run_export` `open_export`'tan sonra bildirir). Dinlenen durumlar `RESTING` = idle, done, error.
- **`FfmpegVideoExporter.merge`** — parçaların klasörüne `pieces.txt` yazar, sessiz parçalar için
  `NN-sound.mp4` keser. Adı `01-sound` olan bir projenin `<proje>.mp4`'ü de bunlardan biriyle çakışır.
- **`Storage`** — klasör silmek için yalnız `delete_dir` (içindekilerle birlikte) var; boşsa silen
  yok.

## Ne değişir

### 1. (a) Birleşik dosya sabit bir adla kesilir

`run_export`'ta `JOINED = "birlesik.mp4"`: birleşik dosya makinede `<parça klasörü>/birlesik.mp4`
olarak kesilir, Drive'a yine `copy_export(…, f"{project}.mp4")` ile `<proje>.mp4` adıyla gider.

- Parçaların adı hep iki haneli sayı (`01.mp4`, madde 283) ve değişmez; `birlesik.mp4` hiçbir
  parçanın, `pieces.txt`'in ya da `NN-sound.mp4`'ün adı olamaz. Adı `01` ya da `01-sound` olan
  projelerin çakışması birlikte gider.
- Ad, parçaların adlarının yanında, `run_export`'ta durur: ikisi aynı klasörü paylaşır ve ancak
  birlikte okununca çakışmadıkları görülür.
- Drive'da görünen hiçbir şey değişmez.

### 2. (b) Temizlik yalnız kendi yazdığını siler

**Kimin dosyası:**

| Dosya | Kimin | Temizlikte |
|---|---|---|
| `video/NN.mp4` | ayrı export'un — onu yalnız o yazar | koşunun kendi yazdıkları silinir |
| `<proje>.mp4` | birleşik export'un | koşunun son adımı ve tek kayıt: düşen bir koşu onu hiç yazmamıştır, silinecek bir şey yok |
| `foto/…` | klasörün — ikisi paylaşır | başka hiçbir export ona ihtiyaç duymuyorsa `foto/` bütün olarak gider |

**Fotoğraflar ne zaman kalır:** ikisinden biri doğruysa `foto/` olduğu gibi kalır.

- Öteki mod **şu anda aynı klasöre yazıyor**: `ExportRunner.others_writing(mode, target)` — öteki modun
  durumu dinlenmiyor ve `target`'ı bu klasör. Koşan birleşik export'un Drive'da fotoğraflarından
  başka bir şeyi henüz yoktur; onu yalnız koşucunun durumu bilir.
- Klasörde **başka bir export'un çıktısı var**: kendi videoları silindikten sonra `video/`'da bir dosya
  ya da dakikalık klasörün kendisinde bir dosya (birleşik dosya; klasörün kendisinde başka dosya
  durmaz). Bitmiş bir export'u bu bulur — koşucu onu artık başka bir dakikada yeniden koşuyor olsa
  bile.

**Sonra:** `video/` boşsa silinir, sonra dakikalık klasör boşsa silinir. `Exportlar` hiçbir zaman:
demet `(Exportlar, "<tarih> <proje>")`'nin altı.

**Yerleri:**

- `run_export` — `_write`'a bir liste verir; ayrı modda her `copy_video` döndükten sonra adı ona
  eklenir. Kayıt bütün ya da hiç olduğu için (472) listede yalnız Drive'da bütün duran videolar olur.
  `_clean` → `remove_pieces` (önce, bugünkü gibi), sonra
  `store.remove_export(project, stamp, own, in_use=runner.others_writing(mode, folder))`.
  Kural ("öteki yazıyorsa") domain'de, çünkü koşucuyu o tutuyor; klasörün düzeni (`video/`, `foto/`,
  birleşik dosya) data'da.
- `photo_store.remove_export(project, stamp, videos, in_use)` — kendi videolarını `delete_file` ile
  siler; `in_use` değilse ve klasörde başka bir export'un çıktısı yoksa `foto/`'yu `delete_dir` ile;
  sonra `video/` ve dakikalık klasör için `remove_empty_dir`.
- `ExportRunner.others_writing(mode, target)` — kilit altında, bellekte.
- `Storage.remove_empty_dir(folder)` — yeni açık yöntem: `os.rmdir`; klasör yoksa ya da içinde bir
  şey varsa `False`, sildiyse `True`. Kontrol ve ad sınırı her yöntem gibi; kök `()` reddedilir
  (`delete_dir` gibi). Başka her `OSError` yükseltilir. `test_storage`'ın `CALLS` listesine girer.

**Aynı kalan:** temizlik önce makinedeki parçaları siler; temizlik düşerse cümle
"<koşunun hatası> — Yarım export silinemedi: …" ve koşunun hatası sebep; iptal bir kez, işin dışında
temizlenir; tek başına düşen bir export'tan geriye hiçbir şey kalmaz (madde 94). Klasörün adı ve
paylaşım değişmez.

### 3. Yorumlar ve belgeler

- `run_export`'un modül docstring'i ("A run that fails takes its folder with it") ve `_clean`'inki;
  `photo_store.remove_export`'unki.
- CODE-STANDARD ve FOUNDATION değişmez: `Storage`'ın kuralları aynı, yalnız bir yöntem daha.

## Maliyet

Koddan sayıldı, ölçülmedi. Her `Storage` işlemi = kök stat'ı + kendi çağrısı; Colab'da her biri Drive'a
bir gidiş dönüş. K = düşen koşunun Drive'a koyduğu video sayısı (birleşikte 0).

| İşlem | Bugün | Sonra |
|---|---|---|
| Başarılı export | — | aynı; liste bellekte, kayıt başına bir ekleme |
| Düşen export'un temizliği | `delete_dir` = stat + `rmtree` (içi kadar silme) | K × `delete_file` (2) + çıktı kontrolü (yalnız öteki yazmıyorsa: `video/` ve dakikalık klasörün `list_files`'ı, 2 × 2) + `foto/`'nun `delete_dir`'i (yalnız gidiyorsa, stat + `rmtree`) + 2 × `remove_empty_dir` (2) — O(K) + ~10 |
| `others_writing` | — | bellekte, diske gitmez |

Temizlik yalnız düşen ya da iptal edilen bir koşuda olur; `rmtree` de içindeki her dosya için bir
silme yapıyordu, yani dosya başına maliyet aynı, sabit kısım birkaç çağrı fazla.

## Ne kaybolabilir, ne bozulabilir

- **Aynı dakikada iki export, biri düşer** — düşenin kendi videoları gider; öteki koşuyorsa ya da
  bitmişse `foto/` ve ötekinin dosyaları kalır, ve klasör boş değildir, silinmez.
- **İkisi de sırayla düşer** — ilki ötekinin koşmasına bakıp fotoğrafları bırakır; ikincisi ilkinin
  artık yazmadığını ve çıktısı kalmadığını görür, `foto/`'yu ve boş klasörü götürür: geriye bir şey
  kalmaz.
- **Bitmiş export, aynı modun yeni bir koşusu başka dakikada** — eski klasördeki birleşik dosya ya da
  videolar diskte durur; çıktı kontrolü onları bulur, fotoğraflar kalır.
- **Temizlik ortasında kopan bağlantı** — o andaki işlem `StorageError` verir, kalanı yapılmaz; ekran
  bugünkü gibi iki cümleyi gösterir. Silinmiş videolar silinmiş kalır; yarım export Drive'da kalabilir
  ve ekran bunu söyler.
- **Geride kalmış bir `.qe-tmp-…` dosyası** — klasör boş sayılmaz, `remove_empty_dir` `False` döner,
  klasör kalır. Bir şeyi silmemek, başkasının olabilecek bir şeyi silmekten iyidir.
- **Birleşik dosyanın makinedeki adı** — her koşunun kendi `mkdtemp` klasörü var; iki koşu aynı
  `birlesik.mp4`'ü paylaşmaz.

## Bu maddenin kararları

1. **Sabit ad `birlesik.mp4`, `run_export`'ta**, parça adlarının yanında.
2. **Fotoğraflar klasörün:** başka bir export ona ihtiyaç duymuyorsa `foto/` bütün olarak gider;
   "ihtiyaç" = öteki mod şimdi aynı klasöre yazıyor ya da klasörde başka bir export'un çıktısı var
   *(ana ajan, 20 Ekim, kullanıcının kararından)*.
3. **Birleşik dosya kendi listesine girmez:** son adım ve tek kayıt; düşen bir koşuda Drive'da
   yoktur.
4. **Kural bölünür:** "öteki şimdi yazıyor mu" domain'de (`others_writing`), "klasörde başka çıktı var
   mı" data'da (`remove_export`) — her biri bilginin olduğu yerde, tek bir çağrıyla.
5. **`Storage.remove_empty_dir`** — ana ajan onayladı; boş olmayanı hiçbir zaman silmez.

## Sınırlar

- **İki export aynı anda düşerse** ikisi de ötekini hâlâ koşuyor görebilir ve `foto/`'yu bırakır;
  klasör `foto/` ile kalır *(ana ajan, 20 Ekim — kabul edildi)*.
- **Temizlik sırasında öteki mod aynı dakikada başlıyorsa** — `in_use` silmelerden önce bir kez
  okunur, ve öteki mod `start` ile `target`'ını bildirmesi arasında "yazmıyor" görünür. Çoğu zaman
  zararsız: o anda Drive'da onun bir şeyi yoktur, ilk fotoğrafı `foto/`'yu yeniden açar ve kendisi
  yazar; klasör onun `_open_inside`'ı ile `rmdir` arasında silinirse kaydı `FileNotFoundError` ile
  düşer ve ekranda görünür. Ama öteki, temizlik `foto/`'yu `rmtree` ile silerken bir fotoğrafı
  yazabilir ya da orada bulup geçebilir; o fotoğraf öteki export'tan **sessizce** eksik kalır. Pencere
  dar — aynı dakikada, birinin temizliğiyle ötekinin ilk fotoğrafları üst üste gelmeli —, ve kabul
  edildi.
- **Aynı mod aynı dakikada iki kez** — ikinci koşu birincinin `video/01.mp4`'ünün üstüne aynı adla
  yazar (474'ten eski bir durum); ikincisi düşerse temizliği kendi listesindeki adları siler, yani
  birincinin bitmiş videolarını da. 474'ten önce bütün klasör gidiyordu; şimdi en çok o adlar gider.
- Eski export'lar (`<proje>/export/<tarih>/`) ve `Exportlar`'ın kendisi dokunulmaz.
- Frontend, notebook değişmez; `dist` yeniden kurulmaz.

## Bitti sayılır

1. Testler gösteriyor ki:
   - adı `01` olan bir projenin birleşik export'u parçalarını bozmadan birleşiyor, birleşen dosya
     makinede `birlesik.mp4`, ve Drive'a `01.mp4` adıyla iniyor (gerçek `Storage` ile);
   - aynı dakikada bitmiş bir birleşik export varken ayrı export düşünce yalnız kendi videoları
     siliniyor; `<proje>.mp4` ve `foto/` kalıyor (gerçek `Storage` ile);
   - bitmiş bir ayrı export varken birleşik export düşünce videolar ve `foto/` kalıyor;
   - öteki mod aynı klasöre yazarken düşen export `foto/`'yu bırakıyor;
   - tek başına düşen ya da iptal edilen bir export'tan geriye ne dakikalık klasör ne `foto/` kalıyor,
     `Exportlar` duruyor;
   - temizlik düşünce iki cümle ve sebep bugünkü gibi; iptal bir kez temizleniyor; parçalar önce;
   - `remove_empty_dir` boşu siliyor, doluya ve olmayana `False` diyor, kökü reddediyor, bağlantı
     kopukken hiçbir şeye dokunmuyor;
   - `others_writing` yalnız öteki mod dinlenmezken ve aynı klasöre yazarken doğru.
2. İki satır yeşil: `python -m pytest queen-editor -q` ve `npm test --prefix queen-editor/frontend`.
3. Koşunun sonunda kullanıcının Colab denemesinde: aynı dakikada biri bitmiş, öteki düşen iki
   export'tan sonra bitmişin dosyaları Drive'da duruyor. Güvence gerçek bağlantının `os.rmdir`'inin
   boş olmayan bir klasörü reddetmesine dayanıyor; testler bunu yalnız makinenin diskinde gördü.
