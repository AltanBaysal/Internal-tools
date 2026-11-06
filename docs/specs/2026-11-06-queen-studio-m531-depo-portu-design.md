# Madde 531 · Depo portu ve bellek içi adaptör — tasarım

**Tarih:** 6 Kasım 2026 · **Madde:** [v1 yol haritası](../roadmaps/2026-11-06-queen-studio-v1-roadmap.md#v1-7),
531 · v1-7 · **Dal:** `feat/queen-studio-v1`

## Ne ve neden

Core verisine yalnız depo portu üzerinden ulaşır; port projenin kayıtlarını anlatır, Drive'ın
dosyalarını değil; kalıcı silme yoktur, yalnız çöp ([4. adım, Depo portu](../research/2026-11-03-yeni-editor-v1-4-depo.md#depo-portu);
FOUNDATION, Karar 3). Arkasında iki adaptör durur: Drive'ınki (v1-8 projeler ve kayıtlar, v1-9
dosyalar) ve testlerin koştuğu bellek içi adaptör. Bu madde portu, bellek içi adaptörü ve port'un
sözleşme testlerini yazar; sözleşme testleri bir kez yazılır, Drive adaptörü aynılarını koşar. Bu
maddede Drive çağrısı yoktur.

Bellek içi adaptör Drive adaptörünü taklit eder: hata enjekte eder (yazmadan önce ya da sonra düşmek,
yavaşlamak, reddetmek), aynı depo üstünde ikinci bir core açılır, saat dışarıdan verilir (4. adım,
Bellek içi adaptör; 12. adım).

## Yerleri

```
core/clock/clock.py      saat kapısı: Clock (now, sleep) ve ManualClock
core/storage/port.py     port: Port, verinin türleri, hatalar, sınırlar ve iki adaptörün ortak bakışları
core/storage/memory.py   bellek içi adaptör: MemoryStore (deponun verisi), MemoryPort (bir core'un portu)
core/storage/faults.py   bir core'un depoya giderken karşılaştığı: enjekte edilen hatalar ve sayılan çağrılar
tests/clock/test_clock.py
tests/storage/contract.py     PortContract: her adaptörün geçtiği testler; Rig bir adaptörü bağlar
tests/storage/test_port.py    port'un bakışları; port ile hata listesinin tutması; core'un portun ardına geçmemesi
tests/storage/test_memory.py  sözleşme bellek içi adaptörde, üstüne adaptörün kendi testleri
```

CODE-STANDARD'ın Düzen'i bunları zaten sayıyor: kapılar ayrı durur, `storage` (port, Drive ve bellek
içi adaptörüyle) ve saat. Kapı kuralına bir cümle eklendi: bir kapı başka bir kapıya yalnız kendisine
verilen bir türü için bakar (depo beklemek için bir `Clock` alır, kurmaz); kuralın nedeni, her kapının
yerine bir taklit konabilmesi, böylece korunur. `export_names` `core.lists.pattern.fold`'u kullanır:
`core/lists/` grup da kapı da değil, kökün ortak parçasıdır. Gerçek saat (`time.sleep`) ilk bekleyen
parçayla, v1-8'in üstel beklemesiyle, başlangıç dosyasında bağlanır; bugün hiçbir şey beklemez.

## Port

Bir proje dört şeydir:

| Ne | Ne tutar | Nasıl değişir |
|---|---|---|
| **Satır** (`Row`) | ad, arşiv, oluşturma ve değişme zamanı, kuyruğu çalıştıran core (`runner`) | Her `commit` bütününü yazar |
| **Hal** (`state`) | Değişen her şey, tek bir JSON nesnesi: karelerin sırası, edit'ler, bekleyen işler ve kuyruk, süren export'lar, çöpe gidecek dosyalar. Biçimi grupların | Her `commit` bütününü yazar |
| **Kayıtlar** (`Record`) | Bir kez yazılıp hiç değişmeyenler: karenin fotoğraf bilgisi, video, biten iş, biten export. `kind`, `id`, `data` | `commit` yenilerini ekler; var olan hiç değişmez |
| **History** (`Entry`) | Her değişikliğin kaydı: `seq`, `time`, `data` (kim, ne, neye, öncesi ve sonrası, isteğin anahtarı ve özeti) | `commit` yenilerini ekler; kayıt değişmez |

Port yalnız bu ayrımı bilir: neyin her yazmada baştan yazıldığını (satır ve hal) ve neyin bir kez
yazılıp kaldığını (kayıtlar ve history). Drive adaptörü ilkini baş dosyasına ve etiketlerine, ikincisini
`tail`'e ve bloklara koyar; D1'de ilki satırın JSON sütunu, ikincisi kendi tabloları. Kare, edit, iş
nedir, port bilmez; onları gruplar kurar (v1-11'den sonra). Böylece 4. adımın "değişen ile değişmeyen
ayrıdır" ilkesi portun kendisi olur, port gruplar yazılmadan önce kurulabilir ve 4. adımın çağrı
sayıları değişmez (reviewer'ın bakışı).

### Projeler

| İşlem | Ne yapar |
|---|---|
| `projects()` | Ana liste: her projenin kimliği, sürümü ve satırı (`Listed`). Çöpteki proje yoktur; okunamayan proje vardır |
| `version(p)` | Projenin sürümü ve satırı; ucuz. Okunamayan projede de döner |
| `load(p, since, format)` | Projenin bütünü (`Project`): sürümü, satırı, hali, biçimi, bütün kayıtları yazıldığı sırayla ve `since`'ten bu yana (dahil) history kayıtları `seq` sırasıyla. `format` çağıranın okuduğu en yeni biçim; proje daha yeniyse `NewerFormat` |
| `create(p, ref, değişiklik)` | Projeyi `reserve`'ün verdiği `ref`'te, değişikliğin satırı, hali, biçimi, kayıtları ve history'siyle açar; sürümünü döner. O `ref`'te daha önce proje açıldıysa `Exists`; orada dosya ya da klasör varsa `Taken`; ikisinde de hiçbir şey yazılmaz |
| `commit(p, beklenen, değişiklik)` | Değişikliği yazar, yeni sürümü döner. `beklenen`, bu portun o proje için en son verdiği sürüm olmalı; değilse `ValueError`. Proje o sürümde değilse `Stale`; proje değişikliğin biçiminden yeni bir biçimdeyse `NewerFormat`; ikisinde de hiçbir şey yazılmaz |
| `history(p, before, count)` | `seq`'i `before`'dan küçük (`None`: hepsi) en yeni `count` kayıt, yeniden eskiye |
| `trash_project(p)` | Projenin her şeyi — satırı, hali, kayıtları, history'si ve projeye konmuş dosyalar — çöpe. Proje o an yoktur. Zaten yoksa başarı |

- **Değişiklik** (`Commit`): yeni satır, yeni hal, biçimi, eklenen kayıtlar, eklenen history
  kayıtları. Kalkan kareler, yeni sıra, kuyruk, çöpe gidecek dosyalar yeni halin içindedir. Bir
  değişiklikte birden çok history kaydı olabilir: birlikte üretilen varyantlar tek yazmayla, her biri
  kendi kaydıyla biter (4. adım, Bir iş).
- **Sürüm** opaktır (`str`): Drive'da baş dosyasının md5'i, D1'de bir sayı, bellekte bir sayaç.
- **Değişiklik yüklenen sürümün üstüne kurulur.** `commit`'in `beklenen`'i, bu portun o proje için
  `load`, `create` ya da `commit` ile en son verdiği sürümdür; değişiklik ona bakılarak kurulmuştur.
  Başkası — `version()`'ın ya da `projects()`'in sürümü, başka bir core'un, ya da bu portun daha eski
  bir sürümü — core'un yanlışıdır, `ValueError`: V1'e bakılarak kurulan hal V2'nin üstüne yazılsaydı,
  V2'yi yapan Colab'ın değişikliği sessizce kaybolurdu. Bir port bu yüzden yüklediği her proje için
  son verdiği sürümü tutar; Drive adaptörü onunla birlikte o sürümün baş dosyasını (Sonraki maddeler
  için, v1-8). Yazması belirsiz kalan (`Unconfirmed`) `commit` tuttuğunu değiştirmez: core `load`'la
  hangisinin olduğunu öğrenir. `trash_project` o projeninkini bırakır.
- **Bakış kilit değildir** (4. adım, Ana fikir 4; Değerlendirme 4): Drive'da `commit` önce bakar,
  sonra yazar. Sırayla iki core'da değişen proje doğru kalır: ikinci core'un eski sürümle gelen
  değişikliği `Stale` alır. Aynı anda gelen iki değişiklik ikisi de bakıştan geçebilir; sonra yazan
  kazanır ve önce yazanın değişikliği — hali, kayıtları, history'si — bütünüyle kaybolur. Sözleşme
  bunu yasaklamaz; D1 gerçekten koşullu yazar, daha güçlüsünü verir. Kaybeden core bunu sonraki
  bakışta aynı `seq`'te başka core'un kaydını görerek anlar (v1-10).
- **History sırayla gider:** her değişikliğin history kayıtları projenin son `seq`'inden bir bir
  devam eder, ilk kayıt 1'dir. Uymayan değişiklik iki adaptörde de `ValueError`'dır, yazılmaz
  (`check_entries`): kaybolan değişiklik `seq`'inden bulunur. Drive adaptörü son `seq`'i baş
  dosyasından bilir.
- **Biçim** (`format`): grupların hal, kayıt ve history biçiminin sürümü (4. adım, Değerlendirme 11).
  Adaptör onu saklar; daha yeni biçimli projeyi eski core ne okur ne yazar (`NewerFormat`, `found` ve
  `known`'la). Eski biçimli proje okunur, `Project.format` onu söyler; core bellekte yükseltir ve
  sonraki `commit` yeni biçimle yazar. Baş dosyasının kendi biçimi (`v`) Drive adaptörünündür.
- **Anahtar portun değildir.** Aynı oluşturmanın tekrarını core `creates.json`'daki notla bilir (4.
  adım, Proje oluşturma): notta proje kimliği ve ayrılmış `ref` vardır; tekrar aynı `ref`'le gelir,
  `Exists` alır, core projeyi `load` eder ve anahtarı history'de bulur. Değişikliğin anahtarı ve özeti
  history kaydının `data`'sındadır; port onlara bakmaz. Son 24 saatin kayıtlarını `load(p, since, …)`
  verir; 24 saat core'un kuralıdır, sınırını core söyler.
- **Okunamayan proje** (`Unreadable`): listede ve `version`'da görünür; `load` ve `history` hatayı
  verir; port onun üstüne yazmaz, boş sayıp yazmaz (4. adım, Okunamayan baş dosyası). Okunamadan önce
  yüklenmiş sürümle gelen `commit` `Stale` alır: proje o arada değişmiştir.
- **Satır** Drive'ın etiketlerine sığar (`check_row`): ad 1–64 karakter (`MOST_NAME`, 2. adımın ad
  kuralı; Drive'da ad en çok 3 etikete bölünür, etiket başına anahtarıyla 124 bayt; 64 karakter en çok
  256 bayttır, 3 parçaya anahtarlarıyla ve bir karakterin baytları arasına düşen kesimle sığar),
  `runner` bir core kimliği ya da boş, zamanlar UTC ve saniyeyle (6. adım, Zaman). History kaydının
  zamanı da öyle (`check_time`). Uymayan iki adaptörde de `ValueError`'dır: Drive etiketi metindir,
  bellekte de aynı satır dönsün.
- **Proje kimliği** 10 küçük harf ya da rakamdır (6. adım). Başka biçim adresten gelmiş ama
  denetlenmemiş bir değerdir: iki adaptör de hiçbir şeye bakmadan `ValueError` verir
  (`check_project`); `put` ve `copy`'nin `InProject` yeri de.

### Dosyalar

| İşlem | Ne yapar |
|---|---|
| `reserve(n)` | Henüz yazılmamış `n` dosya ya da klasör için adres (`ref`); 1 ≤ n ≤ 1000 |
| `put(ref, kaynak, ad, yer)` | Diskteki `kaynak`'ı ayrılmış `ref`'e, `yer`'e yazar; `Stored` (ref, boyut, md5) döner. Aynı içerikle tekrarı aynı `Stored`'u döner, ikinci dosya olmaz; başka içerikle `Taken`. Ayrılmamış `ref` `Rejected` |
| `exists(ref)` | Oradaki dosyanın `Stored`'u (boyut, md5) ya da `None`. Çöpteki yoktur; klasör dosya değildir. Çıktısı zaten Drive'da olan iş, indirmeden, bununla biter (4. adım, Bir iş) |
| `get(ref, hedef, en_çok)` | Dosyayı diske, `hedef`'e yazar (geçici dosya, sonra yerine); `Stored` döner. `en_çok` bayttan büyükse `TooLarge`, diske hiçbir şey yazılmaz. Yoksa `NotFound` |
| `copy(kaynak, ref, ad, yer)` | Depo içinde kopya, ayrılmış `ref`'e; bayt indirilmez. Tekrarı `put`'unki gibi |
| `trash(ref)` | Çöpe; klasörse içiyle, içindeki klasörler dahil. Zaten çöpteyse ya da yoksa başarı |
| `export_folder(ref, ad, inside=None)` | Export klasörünü ayrılmış `ref`'te açar; `inside` verilirse o export klasörünün içinde bir klasör (`photos/`). Aynı adla ve aynı yerde tekrarı başarı, başkası `Taken`; `inside` yoksa `NotFound` |
| `export_names(önek)` | Adı, büyük/küçük harfe bakmadan, `önek`'le başlayan export klasörleri; içlerindeki klasörler export değildir, sayılmaz |
| `space()` | Kota (`None`: sınırsız), kullanılan (çöp dahil), çöpte duran; bayt |

- **Yer** (`Place`): `InProject(p)` — projenin kendi dosyaları, fotoğraf ve video; proje çöpe
  gidince onlar da gider — ya da `InExport(ref)` — bir export klasörü ya da içindeki bir klasör,
  `export_folder`'ın açtığı. Bir export 2. adımdaki gibidir: `<tarih> <ad>/<ad>.mp4` ve
  `<tarih> <ad>/photos/001.png`.
- **Her yeni dosya önceden ayrılmış adresle oluşur** (4. adım, Değerlendirme 2): `put`, `copy`,
  `export_folder` ve `create`. Tekrarı ikinci dosya bırakmaz; Drive'da `409` alır.
- **Bayt diskten diske gider.** `put` diskteki dosyayı okur, `get` diske yazar: işin ürünü
  ComfyUI'nin diskindedir, export'un birleşik videosu ffmpeg'in; medya diskte önbellekte kalır (4.
  adım, Bellek ve disk). Birkaç GB'lık bir export videosu belleğe alınmaz.
- **`get`'in sınırı çağıranındır:** `en_çok`, hem o dosya türünün bütçesi hem diskte boş kalan yer
  (CODE-STANDARD, Maliyet: her disk yazmasından önce boş yere bakılır). Disk başka bir kapıdır; depo
  ona bakmaz, sınırı çağıran verir. Drive adaptörü boyutu indirmeden önce bilir.
- **`export_names`'in karşılaştırması `ilike`'ınkidir** (`core.lists.pattern.fold`): Türkçe ve
  İngilizce i'ler birlikte, gerisi Unicode'un küçültmesiyle. Drive'ın ad araması Türkçe I'yı
  eşlemediği için (madde 528) Drive adaptörü adları kodda karşılaştırır; `(1)`, `(2)`'yi export grubu
  verir (v1-21).
- **Çöp gecikebilir:** Drive bir klasörün içini çöpe 10–20 sn'de taşır (madde 528, 7). Sözleşme
  klasörün ve projenin kendisinin hemen gittiğini söyler, içindekilerin değil; core çöpe giden
  projenin ya da klasörün içini zaten okumaz. Bellekte içi de hemen gider.
- **Hiç olmamış projeye dosya konmaz:** `put`, `InProject(p)`'de `p` hiç olmadıysa `NotFound`.
  Yazılırken çöpe giden projeye konan dosya için sözleşme bir şey söylemez: Drive dosyayı çöpteki
  klasöre koyabilir, o da projeyle birlikte çöpe gitmiş olur.

### Hatalar

Port'un hataları `StorageError`'dır. Deponun kendi sözünü taşıyanlarda (`said`, varsa `code`) core
onları 6. adımın dört alanlı hatasına çevirir (v1-10'dan sonra); çağrıyı tekrarlamak ve üstel bekleme
Drive adaptörünün içindedir, çekirdek yalnız son reddi ya da belirsizliği görür.

| Hata | Ne zaman | Core'da |
|---|---|---|
| `Rejected(said, code)` | Depo reddetti, hiçbir şey yazılmadı: kota, ~60 sn süren hız sınırı, ayrılmamış adres | `storage_rejected` |
| `Unconfirmed(said)` | Yazmanın akıbeti bilinmiyor: yazılmış da olabilir, olmamış da | `storage_unconfirmed` |
| `Unreadable(said)` | Projenin verisi okunamıyor | `project_unreadable` |
| `NewerFormat(found, known)` | Proje bu core'un biçiminden yeni bir biçimle yazılmış | `project_newer_format` |
| `NotFound` | Proje ya da dosya yok, ya da çöpte | `project_not_found`, `no_media` |
| `Stale` | `commit`'in beklediği sürüm şu anki değil | Core projeyi yeniden yükler, kurallara yeniden bakar |
| `Exists` | `create`'in adresinde daha önce proje açılmış | Core projeyi yükler, anahtarı history'de arar |
| `Taken` | Adreste başka bir şey var: `put`, `copy`, `export_folder`'da başka içerik; `create`'te dosya ya da klasör | Core'un hatası: bir adres iki şeye verilmiş |
| `TooLarge(size, most)` | `get`'in dosyası `en_çok`'tan büyük | Çağıranın sınırı |

`Rejected` okumalarda da olabilir (depo cevap vermedi). `Unconfirmed` yalnız yazmalarda.
`ValueError` core'un kendi yanlışıdır (biçimsiz kimlik, sınırı aşan sayı ya da ad, UTC dışı zaman,
sırasız history, bu portun vermediği sürüm); deponun sözü değildir. Her hata alanlarını `args` olarak
taşır: kopyası aynı hatadır.

## Bellek içi adaptör

```python
store = MemoryStore(quota=10_000)        # deponun verisi: Colab'lar için Drive neyse o
a = store.open(clock)                    # bir core'un portu; saatini o core getirir
b = store.open(clock)                    # aynı depoda ikinci core; yeniden başlayan core da böyle açılır
a.inject("commit", Drop(after=True))     # bir sonraki commit yazar, sonra Unconfirmed
store.quota = 20_000                     # kullanıcı Drive'da yer açtı (v1-18)
```

- **Veri JSON olarak tutulur.** Hal, kayıtların ve history'nin `data`'sı yazılırken JSON metnine
  çevrilir, okunurken geri: Drive'da da öyledir. Böylece JSON olmayan bir değer (`datetime`, `NaN`)
  bellekte de düşer; core'un yazdıktan sonra değiştirdiği bir sözlük depodakini değiştirmez, okunan
  hal de depoyu değiştirmez.
- **Her projenin bir anlık görüntüsü** (`_Snapshot`) vardır: sürüm, adres, satır, hal, biçim,
  kayıtlar, history. `commit` bakıştaki görüntüden yenisini kurar ve yerine koyar. Arada başka bir
  core yazdıysa onun değişikliği bütünüyle kaybolur: Drive'daki gibi (yukarıda, Bakış kilit değildir).
- **Port verdiği sürümleri tutar:** proje başına en son verdiği, sözlükte; yüklediği proje kadar
  büyür, `trash_project` o projeninkini siler.
- **Bekçi:** bir kaydın `id`'si projede bir kez. Uymayan değişiklik `ValueError`'dır, yazılmaz. Core'un
  yanlışını, onu sınayan testte yakalasın diyedir; Drive adaptörü bütün kayıtları bilmediği için
  sözleşmede değildir.
- **Kota ayarlanabilir,** açarken ve sonra (`store.quota`): `put` ve `copy` kotayı aşacaksa, dosya
  okunmadan önce `Rejected` (`storageQuotaExceeded`), hiçbir şey yazılmaz (4. adım, Kota: dolu
  Drive'da yükleme düşer). Yalnız dosyalar sayılır; projelerin kendi verisi küçüktür ve sayılmaz.
- **Liste tek seferdedir.** 4. adım bellek içi adaptörün sayfalı listeyi de taklit etmesini
  söylüyordu; sayfa portun dışında kalır (`projects()` ve `export_names` bütün listeyi verir), sayfalar
  Drive adaptörünün kendi testlerinde, taklit API'ye karşı sınanır.
- **Bir kilit** deponun bütün verisini korur: her işlem kendi içinde bütündür. Aynı anda iki istek
  birbirinin yarım yazmasını görmez. `put` küçük kaynak dosyasını kilit altında okur: kotaya bakıştan
  sonra, aynı adrese ikinci bir `put` araya girmesin diye.

### Hata enjeksiyonu

`port.inject(op, fault, times=1, skip=0, project=None)`: o core'un `op` işleminin, `skip` çağrı
geçtikten sonraki `times` çağrısında hata olur; `project` verilirse yalnız o projeye dokunan
çağrılarda. Hatalar core başınadır: `a`'ya enjekte edilen `b`'yi etkilemez.

| Hata | Ne yapar | Hangi işlemde |
|---|---|---|
| `Refuse(said, code)` | Hiçbir şey yapmadan `Rejected`: Drive adaptörünün beklemesi bittikten sonraki ret gibi | Her işlem |
| `Drop()` | Bağlantı depoya varmadan düşer: hiçbir şey yazılmaz, `Unconfirmed` | Yazmalar |
| `Drop(after=True)` | Yazar, cevap gelmeden düşer: yazılmıştır, `Unconfirmed` | Yazmalar |
| `Slow(seconds)` | Önce saatin `sleep`'i: `ManualClock`'ta saat ilerler, gerçek bir saniye beklenmez. Drive yoğun yazmada reddetmez, yavaşlatır (madde 528: yazma ortancası 2,4 sn, en uzunu 35 sn; kararlar, Sapmalar 6) | Her işlem |
| `Run(then)` | İşlemden önce `then()`; bir test onunla yarışı kurar ya da işlemi bir `Event`'te bekletir | Her işlem |
| `Run(then, between=True)` | `commit`'in bakışından sonra, yazmasından önce `then()`: aynı andaki iki yazma | Yalnız `commit` |

- **Sıra:** bir çağrıda, işlemi sürdüren her hata önce ateşlenir — `Slow`, `Run`, `Drop(after=True)` —
  enjekte edildikleri sırayla; sonra durduranların ilki, `Refuse` ya da `Drop()`. Durduran bir hata
  yalnız ateşlenince harcanır: ikinci bir `Refuse` sonraki çağrıyı bekler.
- Yazmalar: `create`, `commit`, `trash_project`, `put`, `copy`, `trash`, `export_folder`. Okumada
  `Drop`, `commit` dışında `between`, `times` < 1 ya da `skip` < 0 `ValueError`'dır: öyle bir hata
  olamaz. Yarışlar zaman penceresiyle değil bu kancalarla kurulur (12. adım); kanca yoksa `commit`'in
  bakışı ve yazması tek kilitte olur, sonuç her koşuda aynıdır. Kanca ateşlenirken hiçbir kilit
  tutulmaz: kanca depoyu çağırabilir, bekleyen kanca başka çağrıyı bekletmez.

### Sayılan çağrılar

`port.calls`: o core'un her port çağrısı, sırayla, `(işlem, proje)` olarak. Proje, işlemin dokunduğu
projedir: proje işlemlerinin projesi; `put`'un ve `copy`'nin `InProject` yeri; `get`, `exists` ve
`trash`'in dosyasının projesi; `copy`'nin kaynağının projesi (kaynak bir projede değilse yerininki);
yoksa `None`. Reddedilen çağrı da sayılır: depoya gitmiştir. Sonraki maddelerin maliyet testleri
endpoint'lerin port çağrılarını bununla tam eşitlikle sayar ve hiçbir isteğin başka projeye
dokunmadığına bakar; her port işleminin kaç Drive çağrısı olduğunu Drive adaptörünün kendi testleri
sayar (aşağıda, Maliyet). İkisi birlikte 4. adımın tablosudur.

## Saat

```python
class Clock(Protocol):
    def now(self) -> datetime: ...      # UTC
    def sleep(self, seconds: float) -> None: ...
```

`ManualClock(start)` yalnız söylenince ilerler: `sleep(s)` saati `s` saniye ilerletir ve hemen döner.
Başlangıcı UTC olmalı. Bekleyen her parça (bellek içi adaptörün `Slow`'u, Drive adaptörünün üstel
beklemesi, sonraki maddelerin 5 sn'lik ve 30 sn'lik bakışları) saati dışarıdan alır; hiçbir test
gerçek bir saniye beklemez (12. adım).

## Sözleşme testleri

`tests/storage/contract.py`'nin `PortContract`'ı her adaptörün geçtiği testlerdir. Bir adaptörün test
dosyası onu miras alır ve `rig` fixture'ını verir:

```python
class Rig(Protocol):
    def open(self) -> Port: ...                # bir core'un portu; her çağrı aynı depoda başka bir core
    def spoil(self, project: str) -> None: ... # projenin verisini, bir çöküşün ya da elin yapacağı gibi, okunamaz yapar
```

Drive adaptörü (v1-8, v1-9) aynı sınıfı kendi `Rig`'iyle miras alır: `open` deneme hesabının
Drive'ında bir core'un portu, `spoil` baş dosyasına bozuk bayt yükler. Yeni biçimli proje `Rig`'siz
kurulur: yeni bir core'u taklit eden ikinci port projeyi `format + 1` ile yazar, eski core onu ne okur
ne yazar; Drive'da da aynı yoldan, baş dosyasına el değmeden. Sözleşme testleri yalnız her depoda tutan
şeylere bakar:

- Boş bir depo beklemez: gerçek Drive'da başka projeler olabilir; kimlikler rastgeledir, liste kümeyle
  karşılaştırılır.
- Projenin ya da klasörün içinin çöpe hemen gittiğine bakmaz (yukarıda).
- Aynı andaki iki yazmayı denemez: Drive'ınkini Drive adaptörünün taklit API'li testleri, belleğinkini
  bellek içi adaptörün kendi testleri dener.
- Kotanın tam baytına bakmaz: Drive kotayı geç günceller; yalnız biçimine bakar.

Her test birkaç çağrıdır: gerçek Drive'da çağrı başına ~0,1–0,8 sn (madde 528).

## Sınırlar

Girdinin sürebildiği her harcama iş yapılmadan önce sınırlıdır (CODE-STANDARD, Maliyet); her sınır
bir testle, gerekirse küçültülerek:

| Ne | Sınır | Neden | Aşılınca |
|---|---|---|---|
| `reserve(n)` | 1–1000 (`MOST_RESERVED`) | Drive'ın `generateIds`'i bir çağrıda en çok 1000 verir | `ValueError`, depoya gitmeden |
| `history(p, before, count)` | 1–1000 (`MOST_ENTRIES`) | Bir liste sayfasının en çoğu (madde 530, `MOST_LIMIT`) | `ValueError` |
| Projenin adı | 1–64 karakter (`MOST_NAME`) | 2. adımın ad kuralı; Drive'ın 3 etiketine sığar (yukarıda) | `ValueError`, depoya gitmeden |
| `get`'in dosyası | çağıranın `most`'u | Dosya türünün bütçesi ve diskteki boş yer çağıranındır | `TooLarge`, diske yazılmadan |
| `put` ve `copy` (bellek) | kota | 4. adım, Kota | `Rejected`, dosya okunmadan |
| Proje kimliği, `runner` | `[a-z0-9]{10}` | Adresten gelir; etiketin boyu | `ValueError`, depoya gitmeden |
| Verilen sürümler (bellek) | yüklenen proje başına 1 | Port yalnız en sonuncuyu tutar | — |

Drive'dan gelen bayt (baş dosyası, bloklar) Drive adaptörünün sınırıdır: açılmadan önce boyuna bakılır
(v1-8). Bellek içi adaptörün verisi core'un kendi yazdığıdır.

## Maliyet

| İşlem | Drive adaptörü (4. adım; v1-8 ve v1-9 tam eşitlikle sınar) | Bellek içi adaptör |
|---|---|---|
| `projects()` | `files.list`, sayfa başına 1, çoğunlukla 1 | O(P) |
| `version(p)` | 1 `files.get` | O(1) |
| `load(p, since, format)` | baş dosyası + diskte olmayan kayıt blokları + `since`'ten yeni history blokları, paralel | O(projenin boyu): JSON'dan okunur |
| `create` | 1 `files.create` | O(değişikliğin boyu) |
| `commit` | 1 okuma + 1 yazma; `tail` sınırı aştıysa +1 blok | O(N + değişikliğin boyu): kayıtların demeti yeniden kurulur, `id` bekçisi |
| `history` | `tail`; eski blok başına ilk seferde 1 indirme | O(history) |
| `trash_project` | 1 çöp (baş dosyası) + 1–2 (klasörler) | O(1) |
| `reserve(n)` | 1 `generateIds` (havuzdan; çoğu çağrı 0) | O(n) |
| `put` | 1 oluşturma; 5 MB üstü resumable; tekrarda `409` + 1 okuma | O(dosya): okunur, md5 |
| `exists` | 1 `files.get`, `md5Checksum,size` alanlarıyla | O(1) |
| `get` | 1 indirme | O(dosya): diske yazılır |
| `copy` | 1 `files.copy` | O(dosya) |
| `trash` | 1 güncelleme | O(1) |
| `export_folder` | 1 oluşturma | O(1); `inside`'ın yukarısı kadar |
| `export_names` | `files.list` `exports/`, sayfa başına 1 | O(klasör) |
| `space` | 1 `about.get` | O(dosya) |

P proje, N projenin kayıt sayısı. Bellek içi adaptör ağa ve diske gitmez (`put` kaynağı okur, `get`
hedefi yazar); maliyeti testin kendi verisidir. `commit`'in O(N)'i yalnız bellekte: Drive'da
`commit` yalnız baş dosyasını yazar, kayıtların bütününe dokunmaz. Aynı istek içinde bir şey iki kez
okunmaz; yazılan geri okunmaz: `put`'un md5'i yerelde hesaplanır.

## Ne bozulabilir

- **Bakış ile yazma arasında başka core yazar:** sonra yazan kazanır, öncekinin değişikliği bütünüyle
  kaybolur, proje bozulmaz (Değerlendirme 4). Bellekte `Run(between=True)` ile kurulur; hem hal hem
  kayıtlar hem history kaybolur, testle.
- **Eski bir hale bakılarak kurulan değişiklik yeni halin üstüne yazılır:** `commit` yalnız bu portun
  son verdiği sürümü alır, testle.
- **Yazma yarıda düşer:** `Drop()` hiçbir şey yazmaz, `Drop(after=True)` bütününü yazar; yarım
  değişiklik yoktur. İkisinde de core `Unconfirmed` görür ve `load`'la hangisi olduğunu öğrenir; aynı
  değişikliği yeniden yazmak `Stale` alır, testle.
- **Okunamayan proje boş sayılıp üstüne yazılır:** `load` `Unreadable` verir; eski sürümle gelen
  `commit` `Stale`, testle.
- **Eski core yeni biçimli projenin üstüne yazar:** `load` ve `commit` `NewerFormat`, testle.
- **Aynı adrese iki dosya:** tekrar aynı içerikse aynı dosya, değilse `Taken`; ikinci dosya olmaz.
- **Core yazdığı sözlüğü sonra değiştirir, depo da değişir:** veri JSON metni olarak tutulur, testle.
- **Adresten gelen biçimsiz kimlik:** `ValueError`, hiçbir şeye bakılmadan; `put` ve `copy`'nin yeri
  de, testle.
- **Etikete sığmayan ad:** `ValueError`, testle.
- **`get` yarım dosya bırakır:** geçici dosyaya yazılır, sonra yerine; büyükse hiç yazılmaz.
- **Kalıcı silme:** portta yoktur; port'un işlemleri ile hata listesinin işlemleri aynı kümedir ve
  testle karşılaştırılır.
- **Core portun ardına geçer:** `core/storage/` dışında hiçbir modül `core.storage.port`'tan başkasını
  almaz, testle. Gerçek adaptör başlangıç dosyasında bağlanır.
- **İki istek aynı anda:** bir kilit; `commit`'in bakışı ile yazması kanca yoksa aynı kilitte.

## Testler

Önce düşen testle; hiçbiri ağ açmaz, gerçek bir saniye beklemez, dosyaları pytest'in `tmp_path`'inde
birkaç baytlıktır.

- `tests/clock/test_clock.py`: `ManualClock` yalnız `sleep`'le ilerler, beklemez; UTC dışı başlangıç
  ve eksi süre `ValueError`.
- `tests/storage/test_port.py`: `check_project`, `check_time`, `check_count`; port'un işlemleri ile
  `Op` aynı küme ve hiçbiri kalıcı silme değil; `core/storage/` dışındaki modüller yalnız
  `core.storage.port`'u alır.
- `tests/storage/contract.py` (`PortContract`): yazılan aynen okunur, ikinci core da okur; liste
  satırı ve sürümü `version`'la aynı; aynı adrese ikinci `create` `Exists`, dosyanın ya da klasörün
  adresine `Taken`; `commit` yeni sürüm ve eklenen kayıtlar, eski sürümle `Stale` ve hiçbir şey
  yazılmaz; bu portun vermediği sürüm `ValueError`; history'nin `seq`'i; yeni biçim okunmaz ve
  yazılmaz, eski biçim okunur ve sonraki `commit`'le yükselir; `load`'ın `since`'i; `history`'nin
  `before`'u, `count`'u ve sırası; bilinmeyen proje `NotFound`; `trash_project` ve tekrarı, yükleyen
  core da yazamaz; okunamayan proje; biçimsiz kimlik (`put` ve `copy`'nin yeri dahil), UTC dışı zaman,
  sığmayan satır, sınır dışı sayılar `ValueError`; `reserve`; `put`/`get` gidiş dönüşü ve `exists`'in
  `Stored`'u, tekrarı, başka içerikle `Taken`, ayrılmamış adres `Rejected`, `get`'in `most`'u; `trash`
  ve tekrarı; `copy`; export'un videosu ve `photos/` klasörü, içteki klasör `export_names`'te yok,
  olmayan klasörün içi `NotFound`; `export_names`'in Türkçe i'leri; hiç olmamış projeye dosya konmaz;
  `space`'in biçimi.
- `tests/storage/test_memory.py`: `PortContract` bellek içi adaptörde; üstüne her hata türü (her
  işlemde `Refuse`; `Drop` önce ve sonra; `Slow` saati ilerletir; `Run`; `between` ile kaybolan
  değişiklik, hali, kayıtları ve history'siyle; bir `commit` kancada beklerken başka proje yazılır);
  `times`, `skip`, `project`; sürdürenler durdurandan önce ve durduran yalnız ateşlenince harcanır;
  hatalar core başına; geçersiz enjeksiyon `ValueError`; çağrıların projesiyle sayılması, reddedilen
  de; JSON olmayan değer ve sonradan değişen sözlük; `id` bekçisi; çöpe giden projenin verdiği sürüm
  de gider; kota, sonradan değişen kota ve `space`; çöpe giden projenin, klasörün ve içindeki
  klasörün dosyaları hemen yok.

## Bitti sayılır

Kabul koşulunun üç satırı: port projenin kayıtlarını anlatıyor, kalıcı silme yok ve core'un portun
ardına geçmediği testle; bellek içi adaptör dört hatayı enjekte ediyor, ikinci core aynı depoda
açılıyor, saat dışarıdan; sözleşme testleri bellek içi adaptörde yeşil ve Drive adaptörü aynı sınıfı
miras alacak. İki suite yeşil; ruff ve pyright temiz; `openapi.json` değişmez.

## 4. adımdan sapmalar

Ana agent'ın kararlar belgesine yazması için; hepsi reviewer'la konuşuldu, 1 ve 2'si onun bulgusuyla
kesinleşti:

1. **`commit`'in değişikliği** 4. adımda tek tek sayılıyordu (satırın alanları, konan kayıtlar,
   kalkan kareler ve edit'ler, yeni sıra, kuyruk, history kaydı, çöpe gidecek dosyalar). Burada: yeni
   satır, yeni hal (sıra, edit'ler, bekleyen işler, kuyruk, süren export'lar, çöpe gidecekler, hepsi
   birlikte), biçim, eklenen kayıtlar, eklenen history kayıtları. Neden: port gruplardan önce yazılıyor
   ve kare, iş, edit bilmemeli; Drive adaptörü de yalnız neyin baştan yazıldığını, neyin bir kez
   yazıldığını bilmeli. Bilgi aynı, kapları ikiye indi; 4. adımın çağrı sayıları değişmez.
2. **`exists(ref)` `Stored | None` döner,** 4. adımdaki gibi `bool` değil: çıktısı zaten Drive'da olan
   iş, kaydı için boyutu ve md5'i indirmeden alır (aynı tek `files.get`, `md5Checksum,size` alanlarıyla).
3. **`load(p, since, format)`:** 24 saatlik pencerenin sınırını core verir; 24 saat 6. adımın, core'un
   kuralıdır. `format` aşağıda.
4. **`create(p, ref, değişiklik)`:** ayrılmış adres `creates.json`'daki nottan gelir (4. adım, Proje
   oluşturma); tekrarı `Exists` alır, projeyi döndürmez: core zaten `load` eder, Drive adaptörü
   fazladan okumaz. Adreste dosya ya da klasör varsa `Taken`.
5. **`commit` yalnız bu portun son verdiği sürümü alır;** başkası `ValueError`. 4. adım "sürüm
   farklıysa eskimiş" diyordu ve hangi sürüm olduğunu söylemiyordu; `version()`'ın sürümüyle, bir
   başka hale bakılarak kurulmuş değişiklik yazılabilirdi.
6. **`format`** `Commit`'te ve `Project`'te: grupların biçimi portun bir alanıdır, adaptör onu saklar
   ve yeni biçimli projeyi eski core'a okutmaz, yazdırmaz (4. adım, Değerlendirme 11'in `v`'si; baş
   dosyasının kendi `v`'si Drive adaptörünün kalır). History kayıtlarının sırası (`seq` 1'den, birer)
   her adaptörün kuralıdır.
7. **`trash_project(p)`** eklendi: 4. adımın tablosunda proje silmenin port işlemi yoktu.
8. **`copy` ayrılmış adrese** yazar, **`export_folder(ref, ad, inside)`** eklendi: export'un klasörü (4.
   adım, Export: "1 klasör"), `photos/` alt klasörü (2. adım) ve kopyaları da her yeni dosya gibi
   ayrılmış adresle oluşur.
9. **`put` ve `get` baytı diskten diske taşır,** `get` `most` alır: export'un birleşik videosu
   birkaç GB olabilir, belleğe alınmaz; medya zaten diskte önbellekte durur.
10. **Bellek içi adaptör sayfalı listeyi taklit etmez:** liste tek seferde; sayfa Drive adaptörünün
    kendi testlerinindir.
11. **Kapı kuralı** (CODE-STANDARD): bir kapı başka bir kapıya yalnız kendisine verilen türü için
    bakar; depo `Clock` alır.

## Sonraki maddeler için

- **v1-8 (Drive, projeler):**
  - `class TestDrivePort(PortContract)`, `Rig`'i deneme hesabının Drive'ı; her port işleminin Drive
    çağrısı sayısı Maliyet'teki sütunla tam eşit.
  - **Proje kimliğinden baş dosyasına:** adaptör `projects()`'in listesinden proje kimliği → baş
    dosyasının Drive kimliği haritasını tutar. Haritada olmayan proje için tek bir ad araması
    (`name = '<p>.json.gz'`, `projects/` içinde, `trashed=false`); bulunamazsa `NotFound`.
  - **Taban baş dosyası:** adaptör, yüklediği ya da yazdığı her proje için verdiği son sürümü ve o
    sürümün baş dosyasını (açılmış hali, 20.000 karede ~1 MB) tutar; `commit` onun üstüne kurar ve
    md5 bakışı onunla karşılaştırır. Sınırı: core'un yüklü projeleri kadar, onların bellek sınırının
    (1 GB, 4. adım) içinde; baş dosyasını tutan yer en çok son kullanılan birkaç düzine projedir,
    çıkan projenin sürümü kalır ve `commit`'i baş dosyasını bir kez indirip md5'i karşılaştırarak
    sürer (+1 indirme, sayılı). Boşalır: `trash_project`'te, `load`/`commit` yenisini koyunca, proje
    çöpte görününce (`NotFound`).
  - **Yetişmek bir `load`'dır:** başka Colab'ın değişikliğini görmek bütün projeyi yeniden yüklemektir;
    kapanmış bloklar diskte kaldığı için çoğunlukla yalnız baş dosyası iner, ilk kez yüklenen 20.000
    karelik proje ~3 sn sürer.
  - `files.update`'in cevabından `trashed` okunur: çöpteki baş dosyasına yazma Drive'da başarı
    döner, adaptör onu `NotFound`'a çevirir.
  - `Rejected`/`Unconfirmed` Drive'ın sözüyle; `429`, `403 userRateLimitExceeded` ve
    `503 transientError` üstel beklemeyle, saat `Clock`'tan. Okunamayan baş dosyası `Unreadable`.
    Baş dosyasının ve blokların boyuna açmadan önce bakılır. Gerçek saat başlangıç dosyasında.
  - Yarıda kalan proje silmenin (baş dosyası çöpte, klasör değil) temizliği adaptörün içindedir:
    açılıştaki listede görülür, klasörü çöpe atılır.
  - `seq`'in sırası `check_entries`'le, satır `check_row`'la, ikisi de yazmadan önce.
- **v1-9 (Drive, dosyalar):**
  - Aynı `PortContract`'ın dosya testleri; `get` boyutu indirmeden önce `most`'la karşılaştırır ve
    yazdığının md5'ini hesaplayıp Drive'ınkiyle karşılaştırır.
  - `exists` tek `files.get`, `fields=md5Checksum,size,trashed`; klasör `None`.
  - `export_names` `q`'daki tırnağı kaçışlar (`'` → `\'`) ve sayfa sayısını sınırlar; adları kodda
    `fold`'la karşılaştırır.
  - Yazılırken çöpe giden projeye `put`: sözleşme yalnız hiç olmamış proje için `NotFound` söyler.
  - `logs/`'un yeri (`Place`) henüz yok; log'u Drive'a gönderen v1-25 ekler.
- **v1-10:** değiştiren her istek `commit` ile, son yüklenen sürümün üstüne; `Stale`'de yeniden yükle
  ve kurallara yeniden bak; `Unconfirmed`'de `load`'la akıbeti öğren; maliyet testleri `port.calls`'la;
  aynı andaki iki yazma `Run(between=True)` ile; 4. adımın Dayanıklılık satırları `Drop` ile, belli
  bir projeye ya da birkaç çağrıdan sonrakine `project=` ve `skip=` ile. `seq` 1'den başlar, her kayıt
  bir sonrakidir.
- **v1-11:** `projects()` ve `version(p)` 5 sn'lik bakışın; proje silme `trash_project`; oluşturma
  `create` ve `Exists`.
- **v1-12, v1-13:** kareler bellek içi adaptörde `create`/`commit` ile kurulur; medya `put` ve `get`,
  `InProject(p)`.
- **v1-18:** `store.quota` ile Drive'da yer açılması.
- **v1-21:** export `export_folder(ref, ad)`, `export_folder(photos, "photos", inside=ref)`, video
  `put(…, InExport(ref))`, fotoğraflar `copy(…, InExport(photos))`.
