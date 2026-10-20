# Madde 472 · Tek kapı: `Storage` — tasarım

**Tarih:** 20 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md),
472 · v10-1 · **Dal:** `feat/queen-editor-v10` · **Kurallar:** queen-editor
[FOUNDATION](../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Kod için hiçbir şey: madde 20 Ekim'de hizalandı, ve tasarımı — iki mimar ve bir reviewer çizdi —
kullanıcı aynı gün onayladı *(kullanıcı — "amacım save için save olduğu kanıtlanmadan user başarılı
göstermek yok ve bütün saveler ve readler bu katmandan geçer bu kadar basit"; "şöyle overengineering
yaplımaz ama SOLID Prensibleri takip edilir")*. Bu spec o tasarımın koddaki hâli.

Bitti sayılmak için **bir Colab denemesi** gerekiyor, ve onu yalnız kullanıcı yapabilir: aşağıda,
*Bitti sayılır*'ın son adımı.

## Ne, neden

Bugün Drive'a giden okumaların ve yazmaların bir kısmı `DriveStorage`'dan geçiyor, bir kısmı
yanından: `photo_store` export klasörlerini `os.makedirs` / `shutil` ile kendisi açıyor ve siliyor,
ayrı export'ta ffmpeg parçaları doğrudan Drive'a yazıyor, `reference_store` ffprobe'a bir yol
uzatıyor, iki route dosyaları `send_from_directory` ile doğrudan diskten sunuyor. `DriveStorage`
de bir kaydı yerinde yazıyor — yarım dosya kalabilir — ve eksik klasörü kendisi açıyor: Drive
bağlantısı oturum ortasında koparsa `/content/drive/MyDrive/...` makinenin kendi diskinde yeniden
açılır, yazma oraya düşer ve ekran başarılı der *(colabtools #3441)*.

**Madde 472 hepsini tek bir kapıdan geçirir:** `backend/services/storage/`'daki `Storage`. Bir kayıt
yalnız dosyanın tamamı Drive bağlantısına yazılıp `fsync` edildikten ve yerine konduktan sonra
başarılı döner; bağlantı kopuksa, ad kökten dışarı çıkmaya çalışıyorsa ya da bir şey okunamıyorsa,
işlem diskin kendi cümlesiyle durur ve o cümle ekrana gelir.

```
Bugün                                         Sonra

Ekran                                         Ekran
  │                                             │  hata: 503 {"error": "<diskin cümlesi>"}
  ▼                                             ▼
backend store'ları                            backend store'ları
  │        │            │                       │  (dosya adları ve şemalar aynı)
  ▼        ▼            ▼                       ▼
DriveStorage  os/shutil   ffmpeg,             Storage   backend/services/storage/
              doğrudan    send_from_directory   │  1. kontrol: kök stat + aygıt kimliği
  │        │            │                       │     (Errno 107 / bulunamadı / başka aygıt → ✘)
  ▼        ▼            ▼                       │  2. ad sınırı: "", ".", "..", / \ NUL : → ✘ (400)
/content/drive                                  │  3. geçici dosya, hedefin klasöründe
  (bağlantı koparsa yazmalar makinenin          │  4. fsync
   diskine düşer, ekran yine ✔ der)             │  5. os.replace → ✔
                                                ▼
                                              /content/drive
```

## Bugün — koddan okunanlar

- **`services/drive/storage.py` · `DriveStorage`** — on dört yöntem. `write_bytes`, `write_text`,
  `append_line` klasörü `os.makedirs` ile açıyor; `rename_dir` hedefin üst klasörünü açıyor (madde
  221'in arşiv taşımasından kalma — 227'den beri arşiv bir işaret, taşınan bir şey yok).
  `read_text` / `read_bytes` `os.path.isfile` ile soruyor, `list_files` / `list_dirs`
  `os.path.isdir` ile, `dir_exists` `os.path.isdir` ile, `stamp` her `OSError`'ı "yok" sayıyor: bu
  dördü bağlantı hatasını "dosya yok" diye yutuyor. `list_dirs(subdir)`'in `subdir`'ini artık kimse
  vermiyor. `dir_path` kökle bir adı hiçbir denetim olmadan birleştiriyor.
- **Store'lar** — `project_store`, `settings_store`, `reference_settings_store`, `plan_store`,
  `order_store`, `photo_record` (+ `file_cache`), `reference_order_store`, `reference_store`,
  `video_length_store`, `happy_ending_store`, `photo_store`, `chat_record`. Hepsi `DriveStorage`'ı
  kurucudan alıyor. `project_store` `arsiv.json`'u kökte `read_text("", …)` ile okuyor; `""` kök
  demek. `reference_store` alt klasörü `os.path.join(project, "referans")` ile kuruyor.
  `plan_store.append` ve `project_store`'un işaret güncellemeleri dosyayı okuyup üstüne yazıyor;
  okunamayan bir dosyayı boş sayıyorlar, yani bozuk bir `plan.json`'a eklemek bütün kuyruğu,
  bozuk bir `arsiv.json`'a işaret koymak bütün arşivi siliyor.
- **`photo_store`'un yan kapıları** — `make_export_folder` / `make_videos_dir` (`os.makedirs`),
  `copy_photo` / `copy_export` (`tempfile.mkstemp` + `shutil.copyfile` + `os.replace`, fsync yok),
  `remove_dir` (`shutil.rmtree`, hataları yutuyor), `photo_dir` / `file_path` / `export_dir`
  (`dir_path` + `os.path.join`). `make_pieces_dir` makinenin geçici alanı.
- **`run_export`** — birleşik modda parçalar makinede kesiliyor, birleşen dosya `copy_export` ile
  Drive'a gidiyor (madde 282). Ayrı modda ffmpeg parçaları doğrudan Drive'daki `video/`'ya yazıyor.
  İkisi de `target` olarak dakikalık klasörün tam yolunu ekrana veriyor; özet de `export_dir`'i.
- **`reference_store._seconds`** — ffprobe'a `dir_path` + `os.path.join` ile kurulan yolu veriyor.
- **Route'lar** — `/photos/<project>/<filename>` ve `/references/<project>/<filename>`
  `send_from_directory(photo_dir(project), filename)`. `send_from_directory` yalnız `filename`'i
  sınırlıyor; `project` = `..` olunca klasör kökün üstü oluyor. Reviewer 20 Ekim'de Flask'ın test
  istemcisiyle denedi: `DELETE /api/projects/..` (`%2E%2E` de) `delete_dir("..")`'ya ulaşıyor ve
  `rmtree` bütün MyDrive'ı siliyor; `.` bütün projeleri; `/photos/../<dosya>` MyDrive'ın en üstündeki
  dosyaları sunuyor.
- **`OSError` yakalayan route'lar** — `projects/presentation/routes.py`'de dokuz, 
  `reference_settings_routes.py`'de iki, `photo_generation/presentation/routes.py`'de iki,
  `agent/presentation/routes.py`'de bir: hepsi `500 {"error": str(exc)}`. Geri kalan route'larda
  bir `OSError` Flask'ın HTML 500 sayfası olur ve ekran "500 INTERNAL SERVER ERROR" der.
- **`web/app.py`** — hata işleyicisi yok. **`main.py`** — tek `DriveStorage(config.DRIVE_ROOT)`,
  bütün store'lara veriliyor.
- **`test_composition_root.py`** — `main`'i ortamdaki kökle yüklüyor; altı test kök vermeden
  (`/content/drive/MyDrive/queenEditor`, bu makinede yok) 404 bekliyor. Kurulum diske dokunmamalı:
  "nothing in the graph reaches out at construction".
- **Notebook'un bağlama hücresi** — `drive.mount("/content/drive")`, sonra kökü `os.makedirs(…,
  exist_ok=True)` ile açıp `assert` ediyor. Kök sunucu kalkmadan önce orada. Bu madde hücreye
  dokunmaz: kökü açan tek yer orası, ve uygulamanın kendisi kökü hiç açmaz.

## Ne değişir

### 1. `backend/services/storage/storage.py` · `Storage`

`services/drive/` gider; `Storage` onun yerine `services/storage/`'a gelir. Tek uygulaması olduğu
için Protocol yok. Kurucu yalnız kökü saklar, diske dokunmaz.

**Klasör nasıl söylenir.** Her yöntemin `folder`'ı kökün altındaki yerdir: **bir dize, kökün
hemen altındaki tek klasör** (bir proje — bugünkü çağrıların hepsi böyle), **ya da parçalardan bir
demet** (`(proje, "referans")`, `(proje, "export", tarih, "foto")`), ve **`()` kökün kendisi**
(`arsiv.json`). Bugünkü `""` = kök kalkar: boş dize artık geçersiz bir ad. Parçaların ayrı ayrı
verilmesi, ad sınırını parça parça uygulayabilmek için: `/` ile birleştirilmiş bir yol, içinde `/`
olan bir adla ayırt edilemezdi.

**Her işlemden önce, sırayla:**

1. **Ad sınırı** — her klasör parçası ve dosya adı: boş, `.`, `..`, ya da `/`, `\`, NUL veya `:`
   içeren bir ad `NameRefused` (bir `StorageError`) ile reddedilir; birleştirmeden ve diske
   dokunmadan. `:` da, çünkü Windows'ta `os.path.join(kök, "C:")` kökü düşürür; proje adları onu
   zaten yasaklıyor.
2. **Bağlantı kontrolü** — kök bir kez `os.stat` edilir. Hata — `FileNotFoundError` dahil, Errno 107
   dahil — `StorageError("Proje köküne ulaşılamıyor: <OS'un cümlesi>")` olur. Aygıt kimliği
   (`st_dev`) **ilk kullanımda** kaydedilir — kurulumda değil, kurulum diske dokunmaz —, sonraki her
   işlemde karşılaştırılır; farklıysa `StorageError("Proje kökü başka bir aygıtta: <kök> (<eski> →
   <yeni>)")`. Yeniden bağlanma yok *(kullanıcı — "hata versin yeter biz anlarız")*.

`StorageError` bir `OSError`: ekrana giden yol aynı (aşağıda, 6).

**Yöntemler** (bugünkülerin adları kalır; yeni olan ikisi *yeni*):

| Yöntem | Ne yapar | "Yok" |
|---|---|---|
| `list_dirs()` | kökün alt klasörleri `[(ad, mtime)]` | — (kök yoksa kontrol durdurur) |
| `make_dir(name)` | kökte bir proje klasörü açar; mtime, ad doluysa `None`. **Klasör açan tek yöntem budur** — kökü ve projeyi | — |
| `delete_dir(folder)` | klasörü içiyle siler; yoksa `False`. Kök silinemez | `FileNotFoundError` |
| `rename_dir(old, new)` | kökteki bir klasörü taşır; yoksa `False`, hedef doluysa `None`. **`makedirs` kalkar** | `FileNotFoundError` |
| `dir_exists(folder)` | klasör var mı | `FileNotFoundError` |
| `list_files(folder)` | dosya adları; **geçici önekli adlar atlanır**; klasör yoksa `[]` | `FileNotFoundError` |
| `read_bytes` / `read_text` / `read_lines` | içerik; yoksa `None` / `None` / `[]` | `FileNotFoundError` |
| `stamp(folder, name)` | `(mtime, boyut)`; yoksa `None` | `FileNotFoundError` |
| `write_bytes` / `write_text` | **kayıt** (aşağıda) | — |
| `save_file(folder, name, source)` *yeni* | makinedeki bir dosyayı **kayıt** olarak Drive'a koyar | — |
| `append_line(folder, name, line)` | ekleme kipi + `flush` + `fsync`; dosyayı açar, klasörü açmaz | — |
| `delete_file(folder, name)` | siler; zaten yoksa hata değil | `FileNotFoundError` |
| `path(folder, name=None)` *yeni*, `dir_path`'in yerine | bir yolu süreç dışındaki bir okura verir — ffmpeg, ffprobe, Flask'ın gönderici — ve ekrana yazılan export yeri. Ad sınırı ve kontrol ondan da geçer | — |

**"Yok" yalnız `FileNotFoundError`.** Başka her `OSError` — Errno 107, EIO, izin — okumada, listede,
`dir_exists`'te ve `stamp`'te yükseltilir, hiçbir zaman boş diye dönmez.

**Kayıt** (`write_bytes`, `write_text`, `save_file`): hedefin kendi klasöründe
`tempfile.mkstemp(prefix=".qe-tmp-")` ile bir geçici dosya açılır, içerik yazılır, `flush` +
`os.fsync`, kapatılır, `os.replace` ile hedefin üstüne konur. Bir şey ters giderse geçici dosya
silinmeye çalışılır ve hata yükselir; hedef olduğu gibi kalır. Başarı yalnız bu demek.

**Örtük klasör yok.** Bir kayıt kökü ya da bir proje klasörünü hiçbir zaman açmaz: proje yoksa
`FileNotFoundError` yükselir. Projenin **içindeki** klasörler — `referans/`, `export/<tarih>/foto/`,
`…/video/` — ilk kayıtta açılır, bugün olduğu gibi; ama yalnız geçici dosya klasör olmadığı için
açılamadığında (`FileNotFoundError`), parça parça `os.mkdir` ile, projenin kendisinden aşağısı. Proje
yoksa ilk `mkdir` de `FileNotFoundError` verir. Klasör zaten oradaysa bu yol hiç yürümez.

### 2. Store'lar

Dosya adları, şemalar ve domain değişmez. Her store'un kurucusu `Storage` alır; sınıf adları
(`DriveProjectStore`, …) kalır.

- **`project_store`** — `arsiv.json` `()`'dan okunur ve yazılır. Liste ve `is_archived` okunamayan
  dosyayı bugünkü gibi boş arşiv sayar (liste her zaman çizilir). **İşareti değiştiren dördü** —
  `archive`, `restore`, `delete`, `rename` — dosyayı katı okur: okunamıyorsa (`ValueError` ya da
  şekil yanlış) `OSError("arsiv.json okunamıyor, üstüne yazılmadı: …")`. `delete` ve `rename`
  işareti artık klasöre dokunmadan **önce** okur: bozuk bir `arsiv.json` projeyi silip sonra hata
  vermek yerine hiçbir şeyi değiştirmeden hata verir. Okuma sayısı aynı (bir).
- **`plan_store`** — `read` bugünkü gibi hoşgörülü; `append` dosyayı katı okur: okunamıyorsa
  `OSError("<proje>/plan.json okunamıyor, üstüne yazılmadı: …")`, kuyruk silinmez.
- **`reference_store`** — alt klasör `(proje, "referans")`; ffprobe'a verilen yol ve kendi
  `dir_path`'inin cevabı `Storage.path`'ten gelir.
- **Öteki store'lar** — yalnız docstring'deki "over DriveStorage" → "over Storage".

### 3. `photo_store` ve `run_export` — export

`photo_store` Drive'a yalnız `Storage`'dan dokunur; makinenin geçici alanı (`make_pieces_dir`,
parçaların yolu, parça klasörünün silinmesi) `Storage`'ın dışında kalır.

| Bugün | Sonra |
|---|---|
| `make_export_folder(project, stamp)` → klasörü açar, yolunu döner | `export_folder(project, stamp)` → yalnız yolu döner (ekrana yazılan); hiçbir şey açılmaz, ilk kayıt açar |
| `make_videos_dir(folder)` | gider — `copy_video` `video/`'yu kaydında açar |
| `export_path(folder, name)` | `piece_path(pieces, name)` — yalnız makinedeki parça klasörü için |
| `copy_photo(source, folder, name)` | `copy_photo(project, photo, stamp, name)` — hedefte varsa (`stamp`) yazmaz; yoksa `save_file(…/foto, name, path(project, photo))` |
| — | `copy_video(project, stamp, source, name)` — makinede kesilen parçayı `…/video/`'ya kaydeder |
| `copy_export(source, folder, name)` | `copy_export(project, stamp, source, name)` — birleşen dosyayı dakikalık klasöre kaydeder |
| `remove_dir(path)` — Drive'ı da makineyi de | `remove_export(project, stamp)` → `delete_dir` · `remove_pieces(path)` → makinedeki parçalar |
| `photo_dir` / `file_path` / `export_dir` | `storage.path(...)` üstünden |

**`run_export`** — iki mod da parçalarını artık makinede keser. Ayrı modda her parça kesilir
kesilmez `copy_video` ile Drive'a gider; sayaç bunu sayar, yani "N yazıldı" Drive'da duran N video
demek. Birleşik mod bugünkü gibi: parçalar makinede, birleşen dosya `copy_export` ile Drive'a. Bitince
iki modda da makinedeki parça klasörü silinir; düşen ya da iptal edilen bir koşu dakikalık klasörü
(`remove_export`) ve parçaları (`remove_pieces`) birlikte götürür, bugünkü gibi (madde 94) —
önce parçaları, çünkü onların silinmesi düşemez. İptal bir kez, işin dışında temizlenir. Düşen bir
koşuda ekrana koşunun kendi hatası gelir; temizlik de düşerse ekran tek cümle gösterdiği için ikisi
bir cümlede gelir — önce koşunun hatası, sonra "Yarım export silinemedi: …" — ve koşunun hatası
sebep olarak zincirlenir. Ayrı modun makinedeki parçaları koşunun sonunda klasörüyle gider,
tek tek değil: makinenin diski dar değil, ve tek tek silmek bir yöntem ve bir çağrı daha demek.
`target` ve dönen değer `export_folder`'ın yolu — ekranda yazan aynı yol. Sıra (önce videolar, sonra
fotoğraflar, sonra birleştirme) ve adlar değişmez.

### 4. Route'lar

`/photos/<project>/<filename>` ve `/references/<project>/<filename>` `send_from_directory`'yi tutar,
ama klasörü `Storage.path`'ten alır: proje adı sınırdan ve kontrolden geçer, dosya adını
`send_from_directory`'nin kendi `safe_join`'i sınırlar, eksik dosya 404 olur, ve video için tarayıcının
istediği parça parça okuma (Range) bugünkü gibi çalışır. Dosyanın tamamını belleğe okuyup göndermek
(`read_bytes`) bunu kaybederdi.

### 5. `main.py`

`Storage(config.DRIVE_ROOT)`; yorum aynı. Kurulum diske dokunmaz.

### 6. `web/app.py` — ekranda gerçek hata

`create_app` bir `OSError` işleyicisi kaydeder: `503 {"error": str(exc)}`. Disk ya da ağ, her
`OSError`'ı yakalar: Drive'ın hataları, ComfyUI'de zaman aşımına uğrayan bir soket, ve DeepSeek'ten
gelen `requests` hataları (onlar `IOError`). `StorageError` ve store'ların "okunamıyor" hatası da
`OSError` olduğu için aynı yoldan gelir. Reddedilen bir ad (`NameRefused`) isteyenin hatası: kendi
işleyicisi `400` döner — Flask en yakın sınıfın işleyicisini seçer. Route'lardaki on dört `except OSError
→ 500` bloğu kalkar: aynı işi ikinci bir yerde yapıyorlar, ve tek işleyici her route'u kapsıyor —
bugün `OSError` yakalamayan route'lar HTML 500 sayfası veriyor. `api.js` `body.error`'u zaten
gösteriyor.

**Frontend yine de bir yerde değişir, ve `dist` yeniden kurulur.** QA bağlantıyı koparınca gördü:
galerinin okuması (`/frames`) 503 ve Drive'ın cümlesiyle düşüyor, ama aynı yoklamadaki `/api/status`
Drive'a hiç dokunmadığı için başarılı dönüyor ve `useGeneration`'ın `setError(null)`'ı galerinin
hatasını siliyordu. Uygulama içinde gezinince hatırlanan liste (boşsa "henüz kare yok"), sayfa baştan
yüklenince sonsuz bir dönen işaret kalıyordu — yani okunamayan bir şey ekranda boş ya da güncel
görünüyordu, ki bu maddenin "Bitti sayılır"ı bunu yasaklıyor. Düzeltme en küçük hâliyle:

- `useGeneration` galerinin okuma hatasını kendi durumunda tutar (`framesError`, sunucunun cümlesi);
  `/status`'un başarısı onu silmez, galerinin bir sonraki başarılı okuması siler.
- `ProjectScreen` onu `Gallery`'ye `failure` olarak verir; `Gallery` o varken listenin, boş galerinin
  ya da dönen işaretin yerine cümleyi çizer — eski liste güncelmiş gibi durmaz.
- Hook'un yapısı değişmez; `dist` `npm run build --prefix queen-editor/frontend` ile yeniden kurulur.

### 7. Belgeler

- **CODE-STANDARD**, *Services*: `drive/` → `storage/`, ve kapının kuralları: her okuma ve yazma
  ondan geçer, kontrol, ad sınırı, kayıt, örtük klasör yok, "yok" yalnız `FileNotFoundError`.
- **FOUNDATION**, karar 7: Drive'ın tek kapısı `services/storage/`, ve bir kaydın başarısı ne demek.

## Maliyet

Koddan sayıldı, ölçülmedi. Her satır bir dosya sistemi çağrısı = Colab'da Drive'a bir gidiş dönüş.
Hepsi proje, sohbet ve dosya sayısından bağımsız, O(1); listeler O(N) ve bugünkü gibi tek çağrı.

| İşlem | Bugün | Sonra |
|---|---|---|
| Her `Storage` işlemi | — | +1 (kök stat) |
| `read_text` / `read_bytes` | `isfile` + `open` = 2 | stat + `open` = 2 |
| `write_text` / `write_bytes` | `makedirs` (1–2) + `open` = 2–3 | stat + `mkstemp` + `fsync` + `replace` = 4 |
| `append_line` | `makedirs` + `open` = 2 | stat + `open` + `fsync` = 3 |
| `list_files` / `list_dirs` | `isdir` + `scandir` = 2 | stat + `scandir` = 2 |
| Galerinin bir sorgusu | ~8 | ~12 (roadmap'in sayısı) |
| Bir fotoğraf / referans sunmak | `isfile` + `open` | stat + `isfile` + `open` |
| Export, kare başına | ayrı: ffmpeg Drive'a yazar; foto: `makedirs` + `exists` + kopya + `replace` | ayrı: ffmpeg makineye + `copy_video` (stat + `mkstemp` + kopya + `fsync` + `replace`); foto: `stamp` + `path` + `save_file` |
| Referans havuzu, N klip | `scandir` + N ffprobe | stat + `scandir` + N × (stat + ffprobe) |

Ayrı export'ta Drive'a giden bayt sayısı aynı; değişen, ffmpeg'in Drive'ın FUSE bağlantısına parça parça
yazması yerine dosyanın tek bir kopyayla gitmesi (madde 282'nin birleşik moda yaptığı). Yavaş gelirse
roadmap'in yolu açık: kontrol yalnız yazmalarda yapılır.

## Ne kaybolabilir, ne bozulabilir

- **Kayıt ortasında ölen makine** — hedef eski hâliyle durur; geriye `.qe-tmp-…` önekli bir geçici
  dosya kalabilir. Listeler onu atlar; silen yok (sınır).
- **Ekleme ortasında ölen makine** — en çok eklenen son satır yarım kalır; okurlar onu bugün de
  atlıyor.
- **Aynı dosyaya iki kayıt aynı anda** — her biri kendi geçici dosyasını açar (`mkstemp` adı
  benzersiz), sonuncu `replace` kazanır; yarım dosya hiçbir zaman görünmez. Kimin kazandığı bugünkü
  gibi isteklerin sırasına kalır.
- **Bağlantı oturum ortasında koparsa** — kontrol stat hatasını ya da kökün yokluğunu görür, işlem
  durur, ekran OS'un cümlesini gösterir; makinenin diskine hiçbir şey yazılmaz, çünkü hiçbir yazma
  kökü ya da projeyi açmaz. Kontrol ile yazma arasındaki kısa aralıkta kopan bir bağlantıda yazma
  kendisi düşer (proje klasörü yok → `FileNotFoundError`), yine diske bir şey bırakmadan.
- **URL'den gelen bir ad** — `..`, `.`, `/`, `\`, NUL, `:`: diske dokunmadan reddedilir, `400`.
- **Olmayan bir projeye kayıt** — `FileNotFoundError`, ve hata geçici dosyanın değil kaydın kendi
  dosyasının yolunu söyler (`mkstemp`'in hatasından zincirlenir).
- **Bozuk `plan.json` / `arsiv.json`** — okumada boş görünür (ekran açılır), yazmada hata verir ve
  üstüne yazılmaz.
- **Düşen bir export'un temizliği** — dakikalık klasörü artık `Storage.delete_dir` siler, ve bugünkü
  `rmtree(ignore_errors=True)`'nun tersine hatasını yutmaz. Makinedeki parçalar önce silinir (hata
  yutarak: onlar Drive değil), sonra dakikalık klasör. Temizlik bağlantı koptuğu için düşerse yarım
  klasör Drive'da kalır — bağlantı yokken silinecek bir şey de yok; ekran bunu söyler: önce düşen
  koşunun kendi hatası, sonra "Yarım export silinemedi: …". İptalde temizliğin hatası koşunun
  hatasıdır.
- **Bugünden kalan, bu maddenin değil:** birleşik export birleşen dosyayı makinede
  `<parça klasörü>/<proje>.mp4` olarak keser; adı `01`, `02`, … olan bir projede bu bir parçanın
  adıyla çakışır.

## Bu maddenin kararları

Maddenin bırakıp spec'in verdiği kararlar:

1. **Klasör, parça demetiyle** — `str` (tek klasör) ya da `tuple` (parçalar), kök `()`.
2. **`path(folder, name=None)`** — süreç dışındaki okurlara yol veren tek yöntem; ekrandaki export
   yeri de ondan. Kontrol ondan da geçer.
3. **Sunma `send_from_directory` ile kalır**, klasörü `Storage.path`'ten alarak (Range ve 404 için).
4. **`StorageError(OSError)`** — kontrolün ve ad sınırının hatası; tek işleyici onu da yakalar.
   **`NameRefused(StorageError)`** ad sınırının kendi türü: isteyenin hatası olduğu için ikinci bir
   işleyiciyle `400` döner (503 "sonra yine dene" der).
5. **Store'ların "okunamıyor"u düz `OSError`** — iki ayrı feature'da, birbirini içe aktaramazlar; tek
   işleyiciden gelir.
6. **Route'lardaki `except OSError` blokları kalkar** — tek işleyici yeter.
7. **Proje içindeki klasörler kayıtta açılır**, yalnız gerektiğinde: örtük klasör yasağı kök ve proje
   için.
8. **`list_dirs`'in `subdir`'i gider** — kullanan kalmadı.
9. **Ayrı export'un parçaları da makinede kesilir** ve sayaç Drive'a konanları sayar.

## Sınırlar

- Önbellek, değişiklik izleme, iki oturum, Drive API'si yok *(roadmap, 9)*. Yeniden bağlanma yok.
- "Kanıtlandı", canlı bağlantının dosyanın tamamını kabul etmesi demek; Google'a yükleme birkaç saniye
  sonra gelir *(roadmap, 8 — kullanıcı: "evet sıkıntı yok")*.
- Geride kalan `.qe-tmp-…` dosyalarını silen yok.
- Notebook değişmez. Frontend'de yalnız galerinin okuma hatası (6'nın sonu), ve onunla `dist`.
  QueenAgent'a dokunulmaz.
- Store'ların dosya adları ve şemaları, domain'in kuralları değişmez.

## Bitti sayılır

1. `queen-editor/backend/` altında `services/storage/` dışında Drive'a `open` / `os` / `shutil` ile
   dokunan bir satır yok; makinenin geçici alanı (`tempfile`, `make_pieces_dir`, ffmpeg'in parça
   klasörleri) hariç.
2. Testler gösteriyor ki:
   - kök stat'ı Errno 107 verince ya da kök yokken ya da aygıt değişince her işlem `StorageError` ile
     duruyor, cümlesi OS'unki, ve ne kökte ne başka yerde bir şey yazılmıyor;
   - kurulum diske dokunmuyor (`test_composition_root`);
   - bir kayıt yarıda düşünce hedef eski hâliyle duruyor ve geçici dosya listede görünmüyor;
   - yazmalar kökü ve projeyi açmıyor; `rename_dir` hedefin üst klasörünü açmıyor;
   - `FileNotFoundError` dışındaki her `OSError` okumada, listede, `dir_exists`'te ve `stamp`'te
     yükseliyor;
   - bozuk `plan.json`'a ekleme ve bozuk `arsiv.json`'da işaret değişikliği hata veriyor ve dosya
     olduğu gibi kalıyor;
   - route düzeyinde: `DELETE /api/projects/..` ve `%2E%2E`, `.`, `/photos/../<dosya>`,
     `/photos/%2E%2E/<dosya>`, `/references/../<dosya>` `400 {"error": "Geçersiz ad: '..'"}` ile
     reddediliyor ve kökün dışında hiçbir şey silinmiyor ya da sunulmuyor;
   - `Storage`'ın her açık yöntemi, kök Errno 107 verince `StorageError` ile duruyor ve hiçbir şey
     yazmıyor; sonradan eklenen bir yöntem listeye girmeden test geçmiyor;
   - bir `OSError` 503 ve `{"error": "<cümle>"}` olarak dönüyor;
   - temizliği Drive'ın reddettiği bir export parçaları yine siliyor, ve ekranda önce koşunun kendi
     hatası, sonra yarım export'un Drive'da kaldığı yazıyor; iptal bir kez temizleniyor;
   - ayrı export parçalarını makinede kesip Drive'a `copy_video` ile koyuyor; birleşik export bugünkü
     gibi.
   - galerinin okuması düşünce galeri sunucunun cümlesini gösteriyor, `/status`'un başarısı onu
     silmiyor, ve eski liste ya da boş galeri ya da dönen işaret onun yerine durmuyor.
3. İki satır yeşil: `python -m pytest queen-editor -q` ve `npm test --prefix queen-editor/frontend`;
   `dist` yeniden kurulmuş.
4. **Colab denemesi — kullanıcının, en son:** notebook bu dalı klonlar; bir projede galeride bir kare
   arka arkaya 20 kez sürüklenir (her bırakış `order.json`'u yeniden yazar), ve **her bırakışın
   süresi ölçülür** (tarayıcının ağ sekmesinde `PUT …/order`'ın süresi): `fsync`'in DriveFS'te
   yüklemeyi bekleyip beklemediği oradan anlaşılır. Sonra Drive'ın web'inde
   proje klasörüne ve çöp kutusuna bakılır: **çöp kutusu `order.json`'larla dolmuyor, klasörde aynı
   addan iki dosya yok, `.qe-tmp-…` dosyası kalmamış.** Olmazsa birleştirmeden önce kullanıcıya
   söylenir.
