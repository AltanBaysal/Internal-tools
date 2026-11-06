# Madde 532 · Drive adaptörü: projeler ve kayıtlar — tasarım

**Tarih:** 6 Kasım 2026 · **Madde:** [v1 yol haritası](../roadmaps/2026-11-06-queen-studio-v1-roadmap.md#v1-8),
532 · v1-8 · **Dal:** `feat/queen-studio-v1`

## Ne ve neden

[Depo portunun](2026-11-06-queen-studio-m531-depo-portu-design.md) proje işlemleri Drive'da:
`projects`, `version`, `load`, `create`, `commit`, `history`, `trash_project` ve `create`'in
gerektirdiği `reserve`. Dosya işlemleri (`put`, `get`, `exists`, `copy`, `trash`, `export_folder`,
`export_names`, `space`) v1-9'undur; burada "v1-9" diyen bir `NotImplementedError` verirler.
Tasarım [4. adımın Depo'su](../research/2026-11-03-yeni-editor-v1-4-depo.md): baş dosyası, etiketleri,
`tail`, bloklar ve mühür; çağrı sayıları onun tablosu, ölçülen davranış
[`drive.json`](../../queen-studio/measurements/drive.json) (madde 528).

Kabul koşulu: sözleşme testleri taklit Drive API'ye karşı ve bu makineden gerçek Drive'da, deneme
hesabıyla yeşil; bir değişiklik iki çağrı ve proje büyüdükçe artmıyor, sayılar tabloyla tam eşit; hız
sınırında istek yavaşlıyor, kaybolmuyor; belirsiz ya da reddedilen yazma Drive'ın sözüyle dönüyor;
okunamayan baş dosyasının üstüne yazılmıyor.

## Yerleri

```
core/clock/clock.py            SystemClock eklendi: gerçek saat, gerçek Drive testleri ve başlangıç için
core/disk/cache.py             DiskCache: diskte, md5'le adreslenen, bayt sınırlı önbellek (kapı: Colab diski)
core/storage/drive/api.py      DriveApi: adaptörün Drive'dan istediği altı çağrı; DriveError, DriveLost, Page
core/storage/drive/google.py   GoogleDrive: DriveApi'nin Drive'ın resmi kütüphanesiyle yazılmışı; zaman aşımları, q kaçışı
core/storage/drive/retry.py    Drive'ı beklemek: Backoff (üstel, saatle, bütçeyle), hangi hata yeniden denenir, üç bekleyiş (read, again, written)
core/storage/drive/limits.py   Limits: adaptörün bütün sınırları tek yerde; test küçüklerini verir
core/storage/drive/head.py     baş dosyasının ve blokların biçimi: paketleme, sınırlı açma, okunamayanın sözü, satır ↔ etiket
core/storage/drive/seal.py     değişikliğin planı, iki yarıda: önce bloklar (sealed), yazıldıktan sonra Drive'ın zamanlarıyla baş (finish)
core/storage/drive/commit.py   Writer: bakıştan sonra bir değişikliğin yazmaları — klasör, bloklar, son tarihiyle baş, sonra toparlama
core/storage/drive/blocks.py   blokları okumak (disk ya da Drive, portla yaşayan tek iş parçacığı havuzu), yazmak, klasörü süpürmek
core/storage/drive/writes.py   her parçanın küçük yazmaları: ayrılmış kimlikte klasör, çöpe atmak, çöpten geri almak
core/storage/drive/pool.py     ayrılmış kimlik havuzu; Drive'ın artık almadığı kimlikte yenisi
core/storage/drive/kept.py     Kept: portun çağrılar arasında tuttukları — baş dosyasının yeri, verilen sürüm, taban baş
core/storage/drive/adapter.py  DrivePort: port'un proje işlemleri
tests/disk/test_cache.py
tests/clock/test_clock.py      SystemClock
tests/storage/drive/fake.py            FakeDrive: taklit Drive API, çağrıları sayar, hata enjekte eder
tests/storage/drive/rigs.py            iki sözleşme koşusunun ortağı: DriveRig, "files: v1-9" listesi
tests/storage/drive/test_contract.py   PortContract taklit Drive'da
tests/storage/drive/test_real.py       PortContract gerçek Drive'da; yalnız QUEEN_STUDIO_DRIVE_TOKEN verilince
tests/storage/drive/test_adapter.py    adaptörün kendi testleri: çağrı sayıları, mühür, yarışlar, bekleme, sınırlar
tests/storage/drive/test_head.py, test_seal.py, test_retry.py, test_google.py
```

Kapı kuralı (CODE-STANDARD, Düzen): depo saati ve disk önbelleğini kendisine verilen türler olarak
alır, kurmaz. `DiskCache` Colab diskinin kapısındadır, çünkü v1-13'ün medya önbelleği aynı yeri, tek
toplam sınırla paylaşacak; bu madde yalnız blokların kullandığı kısmı yazar. `adapter.py` ~520
satır: port'un işlemleri, bakış ve v1-9'un yer tutucuları; v1-9'un dosya işlemleri kendi modülüne
(ör. `files.py`) gider, `DrivePort` ona devreder. Port `close()` ile indirme iş parçacıklarını
bitirir; başlangıç dosyası core'la kapatır, testler her portu kapatır.

## Drive'da

```
<kök>/
  projects/
    <p>.json.gz               baş dosyası; etiketleri ana listenin satırı
    <p>/                      ilk mühürde açılır, kimliği oluşturmada ayrılır
      records-<n>.jsonl.gz    kayıt blokları
      history-<n>.jsonl.gz    history blokları
```

Adaptör bir kök klasörün kimliğiyle açılır. Kökü Drive'da bulmak (Colab'ın hesabında adıyla) ve
token'ı Colab'ın girişinden almak v1-25'indir. `exports/`, `logs/` ve `<p>/media/` v1-9 ile v1-25'in.

### Baş dosyası

Gzip'li JSON, `application/gzip`; gzip başlığının zamanı 0, aynı içerik hep aynı baytlar:

```json
{"v": 1, "w": "9f2c01d4a7be3355", "format": 1, "seq": 12, "state": {"frames": []},
 "records": {"blocks": [{"id": "…", "count": 980, "size": 3990211, "gz": "<md5>"}],
             "tail": [{"kind": "frame", "id": 17, "data": {}}]},
 "history": {"blocks": [{"id": "…", "count": 100, "size": 20113, "gz": "<md5>",
                         "latest": "2026-11-06T09:12:00Z"}],
             "tail": [{"seq": 12, "time": "2026-11-06T09:30:00Z", "data": {}}]},
 "retired": [{"id": "…", "at": "2026-11-06T09:30:00Z"}]}
```

| Alan | Ne |
|---|---|
| `v` | Baş dosyasının kendi biçimi, adaptörün; bilmediği `v` okunamaz (aşağıda) |
| `w` | Bu yazmanın rastgele kimliği, 16 onaltılık hane (aşağıda, Sürüm) |
| `format` | Grupların biçimi, port'un `format`'ı |
| `seq` | Son history kaydının `seq`'i; yoksa 0 |
| `state` | Port'un hali, olduğu gibi |
| `blocks` | Başın adını verdiği bloklar, yazıldıkları sırayla; sonuncusu 4 MB'tan küçükse açıktır. `count` satır sayısı, `size` satırların bayt boyu, `gz` bloğun md5'i. History bloğunda `latest` en geç zaman. Bloğun ilk `seq`'i saklanmaz: history 1'den sırayla gider, öncekilerin `count`'larının toplamı + 1'dir |
| `tail` | Henüz bloğa geçmemiş kayıtlar |
| `retired` | Artık adı verilmeyen bloklar ve adlarının ne zamandan beri verilmediği (aşağıda, Mühür) |

**Etiketleri:** `n0`, `n1`, `n2` (ad, UTF-8'de anahtarıyla 124 baytı aşmayan, karakter sınırında
kesilmiş en çok üç parça), `archived` (`true`/`false`), `created`, `updated`
(`2026-11-06T09:00:00Z`), `runner` (yoksa etiket de yok), `folder` (proje klasörünün kimliği). Her
yazma bütün anahtarları gönderir, kullanılmayanı `null`'la: Drive gönderilmeyen etiketi olduğu gibi
bırakır.

Blok satırları başın `tail`'iyle aynı nesneler, satır başına bir JSON. Blok bir kez yazılır ve bir
daha hiç yazılmaz; okuyan baytlarının md5'ine (`gz`) ve satır sayısına bakar.

### Sürüm

Sürüm baş dosyasının md5'idir: yazmadan önce yerelde hesaplanır, Drive'ın `md5Checksum`'ıyla aynıdır
(madde 528, 1: 200/200). **Yazmanın kimliği `w`:** satır etikettedir, md5 yalnız içeriği tutar.
Aynı içerik iki kez yazılırsa — hal A→B→A dönüp history kaydı eklenmezse, ya da iki core aynı
tabandan aynı değişikliği aynı anda yazarsa — iki yazma aynı md5'i, aynı sürümü taşırdı, satırları
farklıyken: eski A'yı yüklemiş core'un `commit`'i bakıştan geçer ve aradaki satır değişikliğini
(ör. `runner`) ezerdi; kaybolan yazmanın bakışı da başka core'un yazmasını kendisininki sanardı.
Her yazma yeni bir rastgele `w` taşır, md5'i kendisinindir; aynı yazmanın tekrarı aynı baytlardır.
İlk yazılan sayaçtı; ikinci durum (iki core, aynı taban) sayacı da aynı yapar, testte görüldü.

## İşlemler

P proje, B diskte olmayan blok. Her satırın çağrı sayısı testte taklit API'nin saydığıyla tam eşit.

| İşlem | Drive çağrısı | 4. adım |
|---|---|---|
| Açılış | 1 listeleme (kökte `projects/`) + `projects/`'in sayfaları; ilk kez +1 `generateIds` +1 klasör +1 yeniden listeleme; yarım silinen proje başına +1 çöp | "Core'un açılışı" satırının depo payı |
| `projects()` | sayfa başına 1 listeleme, 1000 projeye 1 | Aynı |
| `version(p)` | 1 `files.get` (`md5Checksum,size,properties,trashed`); haritada değilse onun yerine 1 ad araması | Aynı |
| `load(p)` | 1 `files.get` + taban başta değilse 1 indirme + B blok indirmesi (paralel, en çok 4) | Sapma 1 |
| `load(p)`, değişmemiş | 1 `files.get`; bloklar diskten | — |
| `create` | 1 `files.create`; havuz boşsa +1 `generateIds` | Aynı |
| `commit` | 1 `files.get` + 1 `files.update`; havuz boşsa +1 `generateIds`; taban baş önbellekten çıktıysa +1 indirme | Aynı |
| `commit`, mühürle (~100 değişiklikte bir) | yukarıdakiler + mühürlenen akış başına 1 blok oluşturma; baş yazıldıktan sonra çöpe gitme vakti gelen emekli blok başına 1 + 1 listeleme (süpürme) + sahipsiz blok başına 1 + çöpte bulunan adlı blok başına 1 (geri alma); açık blok diskte değilse +1 indirme; projenin ilk mühründe +1 klasör; bloğun oluşturması kaybolup `409` aldıysa zamanı için +1 `files.get` | Mühür satırı (+1); listeleme ve çöp yeni |
| `history` | 1 `files.get` + taban başta değilse 1 indirme + diskte olmayan eski blok başına 1 | `tail`; blok başına ilk seferde 1 |
| `trash_project` | 2 güncelleme (baş dosyası, klasör); haritada değilse +1 ad araması | 1 + 1–2 |
| `reserve(n)` | havuz yetmiyorsa 1 `generateIds` (1000 kimlik); çoğu çağrı 0 | Aynı |

Çağrılar proje sayısına bağlı değildir, `projects()` ve açılış dışında; `commit` projenin
büyüklüğüne de. Aynı işlemde bir dosya iki kez okunmaz; yazılan geri okunmaz: md5 yerelde hesaplanır.

### `projects()` ve proje kimliğinden baş dosyasına

`projects/`'in çöpte olmayan, klasör olmayan çocukları, `files(id,name,md5Checksum,properties)`,
`nextPageToken` bitene kadar. Adı `<p>.json.gz` olmayan dosya sayılmaz. İçeriği okunamayan baş
dosyası listededir (sözleşme öyle ister). **Etiketi okunamayan** baş dosyası listede yer almaz, log'a
yazılır; `version` onda `Unreadable` verir: port'un `Listed`'i bir satır taşır ve Drive'da satır yok;
onu "okunamaz" diye listelemek port'u değiştirmek olurdu.

Adaptör **proje kimliği → baş dosyası ve klasör kimliği** haritasını tutar: açılış, `projects()`,
`create` ve ad araması doldurur. Haritada olmayan proje için tek bir ad araması yapılır
(`'<projects>' in parents and name = '<p>.json.gz' and trashed = false`); yoksa `NotFound`, iki
tane varsa `Unreadable`. Harita P kadar büyür; `trash_project` ve çöpte görünen proje onu siler.

### `load(p, since, format)`

1. **Bak:** `files.get` `md5Checksum,size,properties,trashed`. Çöpteyse `NotFound`; sıkıştırılmış
   boyu sınırı aşıyorsa `Unreadable`, indirilmeden.
2. md5 taban baş önbellekteki aynı sürümse indirilmez. Değilse indirilir (Range ile sınırın bir baytı
   fazlası); indirilenin md5'i bakıştakinden farklıysa arada biri yazmıştır: bak ve indir yeniden, en
   çok 3 kez, sonra `Rejected`.
3. Açılır ve okunur (aşağıda, Okunamayan); `format`'tan yeniyse `NewerFormat`.
4. **Bütün projenin sınırı:** başın açılmış boyu ile okunacak blokların `size`'ları toplamı
   `project_most`'u (128 MiB) aşarsa `Unreadable`, hiçbir blok indirilmeden.
5. Bütün kayıt blokları ve `latest`'i `since`'ten yeni history blokları, tek seferde, diskten ya da
   indirerek (en çok 4'ü birlikte, portun ömrü boyunca açık tek havuzla).
6. Taban baş önbelleğine konur, sürüm verilir.

**Sapma 1 — `load` baş dosyası için 2 çağrı,** 4. adım 1 indirme sayıyordu. `files.get` dört şey için:
çöpteki baş dosyası yine indirilebilir, sözleşme `NotFound` ister (`trashed`); boyu indirmeden önce
bilinmeli (sınır); satır yalnız etiketlerde durur (`properties`); indirilenin md5'i onunla
karşılaştırılır, araya giren yazma yakalanır. Karşılığında başka Colab'ın bir şey değiştirmediği
projeyi yeniden yüklemek tek çağrıdır: md5 tabanınkiyse baş indirilmez, bloklar diskten okunur.

### Taban baş önbelleği

Adaptör, verdiği her sürüm için o sürümün açılmış baş dosyasını tutar (20.000 karede ~1 MB); `commit`
onun üstüne kurar. **Sınırı:** en son kullanılan 32 proje (`bases`) ve açılmış toplam 32 MiB
(`bases_bytes`; Python nesnesi olarak ~4,7 katı, ~150 MB, aşağıda Sınırlar); en yenisi, ne boyda
olursa olsun, kalır. Çıkan projenin verilen sürümü kalır,
`commit`'i baş dosyasını bir kez indirip md5'ini karşılaştırarak sürer (+1 indirme, sayılı).
Önbellekteki taban hep verilen sürümündür; `history` daha yeni bir başı indirirse onu önbelleğe
koymaz. Boşalır: `trash_project`'te, yenisi konunca, proje çöpte görününce.

### `create(p, ref, değişiklik)`

Etiketler ve satır kontrolü, `seq`'in 1'den başlaması, JSON ve **mühürlenebilirlik** — hepsi Drive'a
gitmeden: kayıtlar ya da history kayıtları bir bloğun alabileceğinden (`block_most`, 8 MiB) büyükse
`ValueError`; öyle bir tail hiç mühürlenemez, projenin sonraki her değişikliği mühürde düşerdi.
Havuzdan bir kimlik, proje klasörünün (4. adım: her yeni dosya önceden ayrılmış kimlikle). Sonra tek
`files.create`, `ref` kimliğiyle, içerik ve etiketlerle. `create` mühürlemez: tail sınırı aşsa da bir
sonraki `commit` mühürler; böylece proje klasörü baş dosyasından önce hiç var olmaz ve açılıştaki
temizlik onu yarım silinmiş sanmaz.

`409` gelince `ref`'e bakılır (+1 `files.get`): `projects/`'te bir baş dosyasıysa `Exists`, değilse
`Taken`. Kaybolan bir denemeden sonraki `409`'da md5 bu denemeninkiyse yazılmıştır, sürüm döner.
`400` ("The provided file ID is not usable", ayrılmamış kimlik) Drive'ın sözüyle `Rejected`.

### `commit(p, beklenen, değişiklik)`

1. `beklenen` bu portun son verdiği değilse `ValueError`.
2. **Proje başına kilit:** bir core'da bir projenin `commit`'leri sırayla. Aynı sürüm üstüne kurulan
   ikinci `commit` ilki bitene kadar bekler, sonra bakışta `Stale` alır — bellek içi adaptördeki gibi.
   Kilitler proje sayısı kadardır.
3. **Son tarih:** kilit alınınca, planın anından `commit_most` (10 dk) sonrası (aşağıda).
4. Taban önbellekteyse değişiklik bakmadan planlanır: satır, `seq` (`check_entries` tabanın
   `seq`'iyle), JSON, bloklar, başın sınırı (baş bir kez, yerel saatle paketlenip denenir) — uymayan
   `ValueError`, Drive'a gitmeden.
5. **Bak:** `files.get`. Çöpteyse `NotFound`; md5 `beklenen` değilse `Stale`. Taban önbellekte
   değildiyse şimdi indirilir ve 4. adım yapılır.
6. Taban `format`'ı değişikliğinkinden yeniyse `NewerFormat`.
7. Mühür varsa: projenin ilk mühründe klasör; sonra bloklar, her biri Drive'ın oluşturma zamanıyla.
8. Baş, blokların zamanlarıyla kurulur ve **yazılır:** `files.update`, içerik ve etiketler tek
   multipart istekte, `fields=md5Checksum,trashed`, son tarihe kadar. Cevapta `trashed` doğruysa baş
   dosyası arada çöpe gitmiştir: Drive yazmayı kabul eder, adaptör `NotFound` verir.
9. Yeni taban ve sürüm; mühür varsa, **baş yazıldıktan sonra** çöp ve süpürme (aşağıda, Mühür).

**Son tarih.** Emekli bloğun bir saat beklemesi (Mühür), bir `commit`'in başını sınırlı bir sürede
yazdığına dayanır. Bu sınır tutulur: `written` her yazma denemesinden önce saate bakar, beklemesinin
bütçesi de son tarihte biter. Son tarih geçtiyse baş yazılmaz: `Rejected` (önceki bir deneme
kaybolduysa `Unconfirmed`); yazılmış bloklar hiçbir başın adını vermediği sahipsizlerdir, süpürme
alır. Saat duvar saatidir: uyuyan bir makine uyandığında son tarihin geçtiğini görür.

**Kaybolan yazmaya yeniden yazmadan önce bakılır.** Yazma cevapsız kalır ya da `5xx`, `429`,
`403 userRateLimitExceeded` alırsa, bekledikten sonra md5'e bakılır (+1 `files.get` her denemede):
yeni içeriğinse yazılmıştır; `beklenen`se yeniden yazılır; ne o ne buysa başka bir Colab yazmıştır,
bizimki önce yazılıp ezilmiş de olabilir, olmamış da: `Unconfirmed`. Bütçe biterse ya da yeniden
denenmeyecek bir hata gelirse: hiçbir deneme kaybolmadı ve `5xx` almadıysa — yalnız `4xx`, hız
sınırının `429`/`403`'ü de, Drive yazmadan reddetti — `Rejected`; yoksa `Unconfirmed`, çünkü kesilen
yazma 1–2 sn sonra da yazılabiliyor (madde 528, 3). Körü körüne yeniden yüklemek, ~60 sn boyunca,
arada yazan başka bir Colab'ın değişikliğini ezebilirdi.

Bir blok yazması bütçeyi tüketirse baş dosyası yazılmamıştır, değişiklik olmamıştır: Drive'ın son
sözüyle `Rejected`. Yazılmış ama hiçbir başın adını vermediği blok okunmaz; süpürme alır (aşağıda).
Ayrılmış klasör kimliği reddedilip yeni kimlikle açılan klasör, değişiklik sonra başarısız olursa
(`Unconfirmed` dışında) çöpe gider, içine konan bloklarla: onun adını veren baş yoktur.

### Mühür

Bir değişiklikten sonra bir akışın `tail`'i 100 kaydı ya da 256 KB'ı geçerse aynı değişiklikte
bloğa geçer (4. adım). **Her mühür, havuzdan taze bir kimlikte yeni bir blok yazar;** hiçbir blok
yerinde yeniden yazılmaz ve iki core aynı kimliği hiç paylaşmaz. Son blok açıksa (4 MB'tan küçük) ve
tail'le birlikte 8 MB'ı geçmiyorsa yeni blok onun satırlarını ve tail'i tutar ve onun yerini alır;
yerini verdiği blok **emekliye ayrılır** (`retired`; zamanı, yerini alan bloğun Drive'daki oluşturma
zamanı). Değilse tail yeni bir bloğa gider.
Açık bloğun satırları diskteki önbellekten, yoksa indirerek (+1). Sıra hep **önce blok, sonra baş
dosyası.**

**Neden:** bakış kilit değildir. İki core aynı açık bloğu aynı anda mühürlerse her biri kendi
dosyasını yazar; sonra yazan baş dosyası bütünüyle kalır — port'un sözü bu (m531). Bloklar yerinde
yeniden yazılsaydı kazanan baş, ötekinin yazdığı satırları gösterirdi ve proje kalıcı olarak okunamaz
olurdu. Bloklar artık değişmediği için satır öneki denetimine gerek yok, kaldırıldı: blok baytlarının
md5'i (`gz`) ve satır sayısı denetlenir; tutmazsa `Unreadable`.

**Emekli blok çöpe ne zaman gider:** hemen değil. Bakışını emekli bloğu hâlâ adlandıran bir başta
yapmış ve yazması süren bir `commit`, o bloğu yeniden adlandıran bir baş yazabilir; blok o an çöpteyse
30 gün sonra kalıcı silinir ve proje okunamaz olur. Böyle bir `commit` başını planından en çok
`commit_most` (10 dk) sonra yazar (yukarıda, Son tarih) ve planı, bloğu emekliye ayıran başın
yazılmasından önceydi; o baş da kendi planından en çok `commit_most` sonra yazıldı. Yani emekliye
ayrılıştan sonra en çok iki `commit_most` (20 dk). Emekli blok `retire_after` (1 saat, üç katı) sonra,
ilk **mühürlü** değişiklikte, **baş yazıldıktan sonra** çöpe gider ve o baştan düşer; çöpe
gidemezse sahipsiz olur, sonraki süpürme alır. Mühürsüz değişiklik çöpe atmaz: yine bakış ve yazma,
iki çağrı. Çöp hiç kalıcı silme değildir (FOUNDATION 1); Drive 30 günde kendisi boşaltır.

**İki tarafta Drive'ın saati:** emekli bloğun zamanı, yerini alan bloğun Drive'daki oluşturma zamanıdır
(blok `files.create`'ten `fields=id,createdTime` ile döner, ek çağrı yok); "şimdi" de bu değişikliğin
en yeni bloğunun oluşturma zamanı; süpürmenin sahipsiz bloğun yaşına baktığı `createdTime` da
Drive'ın. Böylece core'ların saatleri birbirini tutmasa da karşılaştırmalar tek saatledir.
**Kalan varsayım:** son tarih yerel saatle ölçülür; son tarihten önce gönderilen baş yazması
Drive'a saniyeler içinde varır, ve yerel saat Drive'ınkinden dakikalarca hızlı ya da yavaş akmaz.
Payı bunlar içindir: iki `commit_most`, `retire_after`'ın üçte biridir.

**Sahipsiz bloklar ve süpürme:** baş dosyasının hiç adını vermediği bloklar üç yoldan kalır: blok
yazıldı ama baş yazılamadı (çökme, red, son tarih), aynı anda iki mühürde kaybeden core'un bloğu, ya
da çöpe gidemeyen emekli. Her mühürlü değişiklik, **baş yazıldıktan sonra** proje klasörünü **bir
kez listeler** ve şunları çöpe atar: adı `records-<n>.jsonl.gz` ya da `history-<n>.jsonl.gz` olan,
yeni başın adını vermediği, emekli listesinde olmayan ve **iki `retire_after`'dan** (2 saat) önce
oluşturulmuş dosyalar. Daha yenisine dokunulmaz: kaybeden core'un başından yola çıkmış ve yazması
süren bir `commit` onu adlandırabilir.

**Geri alma, son güvence:** liste tamsa (`pages`'te kesilmediyse) yeni başın adını verdiği ama
listede olmayan blok çöptedir — vaktinden önce çöpe gitmiş, projeyi 30 gün sonra öldürecek tek hata —
ve çöpten geri alınır (`trashed=false`; yalnız o zaman +1). Drive onu artık hiç tutmuyorsa log'a hata
yazılır.

Süpürmenin bedeli mühür başına 1 listeleme (sayfası en çok 1000, en çok `pages` sayfa; bir klasörde
adı verilen bloklar, son bir saatin emeklileri ve seyrek sahipsizler durur, çoğunlukla tek sayfa),
sahipsiz başına 1 çöp ve geri alınan başına 1. Süpürmenin, çöpün ya da geri almanın hatası
değişikliği ne geciktirir ne düşürür: baştan sonradır, log'a yazılır, sonraki mühür yeniden dener.
Açılıştaki temizlik süpürme yapmaz: her projenin başını okumak O(P) indirme olurdu.

**Kota:** 4. adım açık bloğun yerinde yeniden yazılmasıyla eski hallerin Drive'ın sürümlerinde
durduğunu ve kotaya sayılmadığını ölçmüştü (madde 528, 9). Şimdi her mühürde yerini veren açık blok
bir saat sonra çöpe gider ve **30 gün çöpte kotaya sayılır.** Sıkıştırılmış boylarla (4. adım, Bloklar
ne tutar; dolu açık blok ~0,55–0,65 MB gz): bir kopya ortalama yarı doludur, ~0,3 MB. Kapanan bir blok
başına çöpe giden, kopya sayısı × ~0,3 MB'tır; kopya sayısı 4 MB'ın bir mühürde eklenen tail'e
bölümü. **Kayıt bloğu:** tail 100 kayıt × ~1–1,8 KB (kare kaydı 1,8 KB, iş ve video kaydı daha küçük)
= ~100–180 KB, ~22–40 kopya → kapanan kayıt bloğu başına çöpte **~3–7 MB** (sıkıştırılmış).
**History bloğu:** history kaydı ~200 bayt, tail 100 kayıt = ~20 KB, ~200 kopya → kapanan history
bloğu başına çöpte **~55 MB**; 4. adımın açık history bloğu için eski sürümlerde öngördüğü ~40 MB'la
aynı mertebe. Değişiklik başına çöpe giden ortalama
~6 KB'tır (4. adımın mühür baytı): Colab başına dakikada 10 değişiklikle saatte ~3,6 MB, sürekli
çalışan bir Colab için 30 günde en çok ~2,6 GB. Azaltmanın yolu 4. adımın Değerlendirme 9'daki ilk
önlemidir: history bloğunu 1 MB'ta kapatmak (~55 → ~4 MB); bu maddede yapılmadı, ana agent'ın kararı.

### `history(p, before, count)`

Bakış (1 `files.get`): çöpteyse `NotFound`, md5 tabanınkiyse taban, değilse baş indirilir (+1) ve
açılır; okunamazsa `Unreadable`. Kayıtlar önce `tail`'den, sonra ilk `seq`'i `before`'dan küçük
bloklardan yeniden eskiye, `count` dolana kadar; bloğun ilk `seq`'i öncekilerin `count`'larından
çıkar. Bloklar diskten ya da indirerek.

### `trash_project(p)`

Baş dosyası çöpe (1): proje o an yoktur. Sonra klasörü (1; hiç açılmamışsa Drive `404` der,
başarıdır). Klasörün çöpe gidemeyişi işlemi düşürmez: log'a yazılır, açılıştaki temizlik alır.
Haritada değilse önce ad araması; yoksa başarı. **Yarım silme:** baş dosyası çöpte, klasör değilse
açılışta `projects/`'in listesinde baş dosyası olmayan `<p>` klasörü olarak görülür ve çöpe atılır.
Kullanıcı baş dosyasını Drive'ın çöpünden geri alırsa klasörünü de geri alması gerekir.

### Açılış

`DrivePort.open(api, kök, saat, önbellek)`: kökte `projects` adlı klasörü listeler; yoksa havuzdan
kimlikle açar ve **yeniden listeler,** en eski oluşturulanı alır: aynı anda ilk kez açılan iki core
aynı klasörde buluşur. Port, klasör bulunduktan sonra kurulur. Sonra `projects/`'i bir kez listeler:
haritayı doldurur, yarım silinenleri çöpe atar (atamazsa log'a yazar, açılış sürer).

### Drive'ın `404`'ü

Drive'ın `404`'ü hiçbir yerde içeride kalmaz; olduğu yerde adlandırılır: kök yoksa açılış, Drive'ın
sözüyle `Rejected`; `projects/` yoksa listeleme ve `create` `Rejected`, ad araması `NotFound`; baş
dosyası yoksa `NotFound`; blok yoksa `Unreadable`; proje klasörü yoksa (blok yazılırken) `Rejected`;
çöpe atılacak dosya yoksa başarı. Taklit API bilinmeyen üst klasörün listesinde `404` verir, gerçek
Drive gibi.

### Drive'ın artık almadığı kimlik

Ayrılmış kimlikler zamanla geçersizleşebilir (madde 528, 6: 1, 3 ve 7 günlük bakışlar sürüyor).
Ayrılmış kimlikte oluşturmaya `400` gelirse havuz bütünüyle bırakılır (o kimliklerle birlikte
ayrılmışlardır) ve bir kez yeni kimlikle denenir: proje klasöründe yeni klasör kimliği etikete
(`folder`) aynı yazmada yazılır ve bloklar hemen yeni havuzdan yeniden planlanır (bir `generateIds`);
bir blok kimliği yine de reddedilirse değişiklik bir kez daha planlanır. İkinci
`400` Drive'ın sözüyle `Rejected`. Başın kendi `ref`'i core'undur (`creates.json`): onda `400`
`Rejected`.

### Okunamayan

Drive'dan gelen bayt dışarıdan gelen girdidir. Baş dosyası ve bloklar sınırla açılır:
`zlib.decompressobj(wbits=31).decompress(veri, sınır + 1)`. Sınırı aşan, yarım gzip, ardında başka
bayt, JSON hatası, `RecursionError`, beklenmeyen biçim, bilinmeyen `v`, biçimsiz kimlik ya da md5,
`404` veren blok, md5'i ya da satır sayısı başınkini tutmayan blok, bütün projenin sınırı — hepsi
`Unreadable`, okuyucunun sözüyle; hiçbiri boş sayılmaz, okunamayan projeye yazılmaz: `commit`'in
bakışında md5 değişmiştir, `Stale`.

**Bilinmeyen `v`** `Unreadable`'dır, `NewerFormat` değil: `v` adaptörün kendi dosya biçimidir,
`NewerFormat` grupların `format`'ı içindir; bilinmeyen bir `v`'nin içindeki `format` okunamaz.

### Hatalar ve bekleme

| Drive | Adaptör |
|---|---|
| `429`, `403 userRateLimitExceeded`/`rateLimitExceeded`, `500`, `502`, `503`, `504`, cevapsız kalan çağrı | Üstel bekleme (1, 2, 4, 8, 16, 32 sn'ye kadar, +0–1 sn rastgele), saat `Clock`'tan; bütçe ~60 sn, saatle ölçülür, zaman aşımına uğrayan çağrının süresi de içinde |
| Bütçe bitti, okumada | `Rejected`, Drive'ın son sözü ve kodu |
| Bütçe bitti, yazmada | Bir deneme kaybolduysa ya da `5xx` aldıysa `Unconfirmed`, yoksa `Rejected`; ikisi de Drive'ın son sözü ve koduyla |
| `409` | `create`'te yukarıdaki gibi; klasör ve blok için aynı oluşturmanın önceki denemesi |
| `404` | Yukarıda, Drive'ın `404`'ü |
| `400`, ayrılmış kimlikte oluşturma | Yukarıda, Drive'ın artık almadığı kimlik |
| Başka `4xx` | `Rejected`, Drive'ın sözü ve kodu (`reason`) |

`DriveError` Drive'ın durum kodunu, `reason`'ını ve `message`'ını taşır; `DriveLost` bağlantının
sözünü (zaman aşımı, kopma). İkisinde de token yoktur: token yalnız isteğin başlığındadır, hata
mesajına girmez. Token'ın yolu `GoogleDrive.from_token(yol)`'a verilir; kod onu okur, hiçbir yere
basmaz.

### Disk önbelleği

`DiskCache(klasör, en_çok, boş_kalacak)`: anahtar içeriğin md5'i, dosyanın adı da odur. `get(md5)`
dosyayı okur ve md5'ine bakar: tutmazsa siler, yok sayar — hiç güvenilmez. `put(veri)` geçici
dosyaya yazar, sonra yerine taşır; önce diskte `boş_kalacak` kadar yer kalacak mı bakar
(`shutil.disk_usage`): önbelleğin hepsi boşalsa da yer kalmayacaksa hiçbir şeyi çıkarmadan yazmaz;
en çok bayt aşılacaksa en uzun süredir kullanılmayandan çıkarır. Önbellek bir kolaylıktır: yer yoksa
ya da yazma düşerse yazmaz, log'a yazar, işlem sürer. Açılırken klasörü bir kez tarar (diskte,
Drive'da değil); yarım `.part` dosyalarını siler. Anahtar Drive'ın baş dosyasından gelir:
`[0-9a-f]{32}` değilse `ValueError`, hiçbir yol kurulmaz. Bloklar hiç değişmez; önbellek bayatlamaz.

## Sınırlar

| Ne | Sınır | Aşılınca | Testte |
|---|---|---|---|
| Her küçük Drive çağrısı | 30 sn soket zaman aşımı (`small`) | `DriveLost`, bütçe içinde yeniden | 0,05 sn'lik sınırla, cevap vermeyen yerel sokete |
| Yükleme ve indirme isteği | 120 sn (`transfer`) | Aynı | Aynı |
| Yeniden deneme | ~60 sn, saatle; tek bekleme en çok 32 sn | `Rejected` / `Unconfirmed` | `ManualClock`'la; asılı kalan çağrı saati 30 sn ilerletir |
| Baş dosyası, açılmış | 16 MiB (`head_most`) | Okurken `Unreadable`; yazarken `ValueError`, Drive'a gitmeden | Sınır küçültülerek |
| Baş dosyası, sıkıştırılmış | 16 MiB; indirmeden önce boyuna bakılır, Range sınırın bir fazlası | `Unreadable` | Aynı |
| Blok, açılmış ve sıkıştırılmış | 8 MiB (`block_most`) | Okurken `Unreadable`; yazacak mühür ve mühürlenemeyecek `create` `ValueError` | Aynı |
| Bütün proje, açılmış | 128 MiB (`project_most`), baş ve okunacak bloklar; Python nesnesi olarak ~4,7 katı (`PARSED`, 532 review'unda kayıtlarda ölçüldü), ~600 MB: 4. adımın yüklü projelere verdiği 1 GB'ın içinde, 20.000 karelik ~77 MB'lık proje sığar | `Unreadable`, blok indirilmeden | Küçültülerek |
| Bir `commit` planından baş yazmasının son denemesine | 10 dk (`commit_most`), duvar saatiyle; bekleme bütçesi de orada biter | `Rejected` (önceki deneme kaybolduysa `Unconfirmed`) | Kanca saati baş yazmasından önce ilerletir; hız sınırında bütçe |
| Açık blok | 4 MiB'ta kapanır (`block_full`) | Yeni blok | Küçültülerek |
| `tail` | 100 kayıt ya da 256 KiB | Mühür | Küçültülerek |
| Emekli blok | `retire_after` (1 saat) sonra çöpe; sahipsiz 2 saat sonra | Sonraki mühürde | `ManualClock` ilerletilerek |
| Listeleme (`projects/`, süpürme) | sayfa en çok 1000, en çok 20 sayfa (`pages`) | `projects/`'te `Rejected`, sessizce kesilmez; süpürmede log, kalanı sonra | Sayfası 2'lik taklitle |
| Araya giren yazmada `load`'ın yeniden denemesi | 3 | `Rejected` | Kanca her indirmeden önce yazar |
| Taban baş önbelleği | 32 proje (`bases`), açılmış 32 MiB (`bases_bytes`), nesne olarak ~150 MB | En eski çıkar, +1 indirmeyle sürer | `bases=1` ve `bases_bytes=1` ile |
| Proje kilitleri | proje başına bir | — | — |
| Disk önbelleği | en çok bayt ve boş kalacak yer, parametre | En eski çıkar / yazılmaz | Birkaç baytla |
| `q`'daki değer | `'` ve `\` kaçışlanır | — | Birim testi |
| `generateIds` | en çok 1000; az dönerse | `Rejected` | Var olan |

`RecursionError` derin iç içe JSON'da Python'un kendi sınırıdır; yakalanır, `Unreadable`.

## Testler

Önce düşen testle; taklit API'li hiçbir test gerçek bir saniye beklemez (yalnız zaman aşımı testleri
0,05 sn), dosyaları birkaç bayttır.

- **Sözleşme taklit Drive'da** (`test_contract.py`): `PortContract`'ın bütün proje testleri;
  dosya testleri adlarıyla bir listede, "files: v1-9" diye atlanır, v1-9 listeyi siler.
  `contract.py`'ye dokunulmaz.
- **Sözleşme gerçek Drive'da** (`test_real.py`): aynı sınıf ve aynı liste; yalnız
  `QUEEN_STUDIO_DRIVE_TOKEN` token dosyasının yolunu verince koşar, yoksa atlanır. Kendi açtığı
  `queen-studio-532-<rastgele>` klasöründe; sonunda klasörü çöpe atar. Gerçek saatle bekler. Üstüne
  bir mühür denemesi: klasör, bloklar, yerini veren açık blok, başka core'un okuması, çöp.
- **Adaptörün kendi testleri** (`test_adapter.py`, taklit API'yle): yukarıdaki tablonun her satırı
  çağrı çağrı tam eşitlikle; küçük ve büyük projede `commit` aynı iki çağrı; mühür (ilk mühürde
  klasör, yeni blok, yerini veren açık blok ve emekliliği, emeklinin bir saat sonra çöpe gitmesi,
  açık bloğun indirilmesi, dolan bloğun kapanması); başı yazılamamış bloğun iki saat sonra
  süpürülmesi; aynı anda iki mühürde sonra yazan başın bütünüyle kalması; bir core'da aynı sürüme iki
  `commit`'te ikincinin `Stale`'i; yazmanın kimliğiyle aynı içerik farklı sürüm; kaybolan yazmanın üç
  sonucu; hız sınırında bekleme ve yeniden; bütçe sonu `Rejected` ve `Unconfirmed`; asılı çağrı;
  çöpteki başa yazma `NotFound`; `409`'da `Exists` ve `Taken`; ayrılmamış kimlik `Rejected`; yarım
  silinmenin temizliği; `projects/`'in açılışta bulunması, açılması ve aynı anda açan iki core'un en
  eskide buluşması; taban önbellekten sayıyla ve baytla çıkınca +1 indirme; araya giren yazmada
  `load`; sayfa sınırı; etiketi okunamayan baş dosyası; klasörünü kaybetmiş başa yazılmaması;
  mühürlenemeyecek `create`; bütün projenin sınırı; kökün ve `projects/`'in `404`'ü; Drive'ın artık
  almadığı klasör ve blok kimlikleri (yeniden plan hemen, tek `generateIds`); başarısız değişikliğin
  yeni kimlikli klasörünün çöpe gitmesi; son tarihten sonra baş yazmasının `Rejected`'ı (saati
  baş yazmasından önce ilerleten kancayla) ve beklemenin de son tarihte bitmesi; çöpte bulunan adlı
  bloğun süpürmede geri alınması.
- `test_head.py`: adın üç etikete bölünmesi (Türkçe, dört baytlık karakter), satır ↔ etiket, sınırlı
  açma, her okunamayan biçim, md5'i ya da satır sayısı tutmayan blok; `test_seal.py`: mühür, plan,
  emeklilik ve çöpün vakti, mühürlenemeyen tail; `test_retry.py`: bekleme ve bütçe; `test_google.py`:
  `q` kaçışı, Drive hatasının çevrilmesi, zaman aşımı yerel sokete karşı; `test_cache.py`: md5'i
  tutmayan dosya, LRU, boş yer, boşaltmak yetmezken hiçbir şeyi çıkarmamak, `.part`, biçimsiz anahtar.

## Ne bozulabilir

- **Okunamayan baş dosyası boş sayılıp yazılır:** hiçbir okuma hatası boş hal vermez; `commit`
  bakışta md5'i görür, `Stale`; testle.
- **Aynı anda iki yazma:** sonra yazan bütünüyle kalır, öncekinin değişikliği kaybolur (4. adım,
  Değerlendirme 4); mühürde de, çünkü her mühür kendi dosyasını yazar; testle.
- **Emekli blok erken çöpe gider, yeniden adlandırılır:** her `commit`'in başı son tarihine kadar
  yazılır ya da hiç; emekli bir saat, sahipsiz iki saat bekler; yine de çöpte bulunan adlı blok
  süpürmede geri alınır; testle.
- **Cevapsız yazma:** yeniden yazmadan önce bakılır; testle.
- **Çöpteki başa yazma:** başarı döner, `NotFound`'a çevrilir; testle.
- **Çökme:** her yeni dosya ayrılmış kimlikle; sıra klasör → blok → baş; blok yazılıp baş yazılmazsa
  hiçbir baş onu göstermez, süpürme alır; testle.
- **Asılı soket:** her çağrı zaman aşımlı, bütçe saatle; testle.
- **Drive'dan gelen büyük ya da bozuk bayt:** açmadan önce boy, açarken sınır, bütün projenin
  sınırı; testle.
- **Token:** yalnız yolu verilir; hata mesajına, log'a girmez.
- **Disk önbelleğinde bozuk dosya:** md5'i tutmayan güvenilmez, silinir; testle.
- **İki core aynı anda ilk açılış:** iki `projects/` açılabilir; ikisi de en eskisini kullanır; testle.
- **Bir core'da aynı projeye iki istek:** proje kilidi; testle.

## Bitti sayılır

Kabul koşulunun üç satırı: sözleşme taklit API'de ve gerçek Drive'da yeşil (dosya testleri v1-9'a
atlanmış); çağrı sayıları tabloyla tam eşit, `commit` proje büyüdükçe artmıyor; hız sınırında
yavaşlayan, Drive'ın sözüyle reddedilen ve belirsiz kalan yazma, okunamayan başın üstüne yazılmaması
testli. Suite yeşil, ruff ve pyright temiz; `openapi.json` değişmez. Paketler `requirements.txt`'te
sabit sürümle.

## 4. adımdan sapmalar

1. **`load` baş dosyası için 2 çağrı** (`files.get` + indirme), 4. adım 1 indirme sayıyordu; değişmemiş
   projede 1 (yukarıda).
2. **Her mühür taze kimlikte yeni blok yazar,** 4. adımın "açık blok her mühürde baştan yüklenir" ve
   akışın baş dosyasındaki `next` kimliğinin yerine. Yerini veren blok emekliye ayrılır, bir saat
   sonra çöpe gider; sahipsiz bloğu mühürlü değişiklik süpürür. Neden: aynı anda iki mühürde sonra
   yazan baş bütünüyle kalsın (m531'in sözü); yerinde yazmada proje kalıcı okunamaz olurdu. Bedeli:
   mühür başına +1 listeleme ve emekli başına bir çöp; çöp kotaya sayılır (yukarıda, Kota).
3. **Yazmanın kimliği `w`** baş dosyasında: md5'in sürüm olması her yazmada içeriğin değişmesini
   ister; aynı tabandan aynı anda aynı değişikliği yazan iki core da ayrı sürüm alır.
4. **Kaybolan yazma körü körüne yeniden yüklenmez;** 4. adım "aynı içerik ~60 sn yeniden yüklenir,
   zararsızdır" diyordu. Her denemeden önce md5'e bakılır; arada başka Colab yazdıysa `Unconfirmed`.
5. **Proje klasörünün kimliği baş dosyasının etiketinde** (`folder`): proje silmek baş dosyasını
   indirmeden klasörü bulur. Etiketler artık yalnız ana listenin satırı değildir.
6. **`create` mühürlemez,** ilk mühür ilk `commit`'te; bir bloğa sığmayacak tail'i `create` reddeder.
7. **Bilinmeyen baş dosyası biçimi (`v`) `Unreadable`,** 4. adım `project_newer_format` diyordu;
   `NewerFormat` grupların `format`'ı içindir (m531).
8. **Disk önbelleğinin anahtarı md5,** yer Colab diskinin kapısında; v1-13'ün medyası aynı nesneyi
   ve sınırı paylaşacak.

## Sonraki maddeler için

- **v1-9:** `rigs.py`'deki "files: v1-9" listesini sil; dosya işlemleri `DrivePort`'taki
  `NotImplementedError`'ların yerine, kendi modüllerinde. `<p>/media/` klasörü için kimlik baş
  dosyasında yok: ilk medyada havuzdan ayrılır ve tutulacağı yer v1-9'un kararıdır. Süpürme yalnız
  `records-`/`history-` adlı dosyalara ve klasör olmayanlara dokunur; `media/` ona girmez.
  `exports/`'in açılışı burada değil.
- **v1-13:** `DiskCache` medya için de; bugün bayt verir, büyük video için yol vermesi gerekir.
- **v1-25:** kökü bulmak, token'ı Colab'dan almak, `SystemClock` ile `DrivePort.open`'ı başlangıç
  dosyasında bağlamak; önbelleğin klasörü ve sınırı ortamdan.
- **v1-10:** `Unconfirmed`'de `load`'la akıbet; aynı andaki iki yazmayı Drive'da taklit API'nin
  kancasıyla.
