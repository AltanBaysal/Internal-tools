# Madde 534 · Drive adaptörü: dosyalar — tasarım

**Tarih:** 7 Kasım 2026 · **Madde:** [v1 yol haritası](../roadmaps/2026-11-06-queen-studio-v1-roadmap.md#v1-9),
534 · v1-9 · **Dal:** `feat/queen-studio-v1`

## Ne ve neden

[Depo portunun](2026-11-06-queen-studio-m531-depo-portu-design.md) dosya işlemleri Drive'da: `put`,
`exists`, `get`, `copy`, `trash`, `export_folder`, `export_names`, `space` (`reserve` 532'de yazıldı).
532'nin `NotImplementedError`'larının yerine; `DrivePort` onlara devreder, `adapter.py` büyümez.
Tasarım [4. adımın Depo'su](../research/2026-11-03-yeni-editor-v1-4-depo.md) (Depo portu; Kota, çöp ve
hesap; Maliyet), ölçülen davranış [`drive.json`](../../queen-studio/measurements/drive.json) (madde 528).

Kabul koşulu: sözleşmenin dosya testleri iki adaptörde ve gerçek Drive'da yeşil; aynı yüklemenin
tekrarı ikinci dosya bırakmıyor; kopan büyük yükleme kaldığı yerden sürüyor, yarım dosya kalmıyor;
core hiçbir dosyayı kalıcı silmiyor; çağrı sayıları 4. adımın tablosuyla tam eşit.

## Yerleri

```
core/storage/drive/files.py     Files: port'un dosya işlemleri; DrivePort devreder
core/storage/drive/places.py    Places: bir yerin (InProject, InExport) Drive'daki klasörü; media/, exports/, <p>/'nin açılışı
core/storage/drive/transfer.py  disk ile Drive arasında bayt: yükleme (tek istek ya da parça parça), indirme (geçici dosya, md5)
core/storage/drive/retry.py     + resumed: parçanın beklemesi — kopunca Drive'a nerede kaldığını sorar; 409'da Conflict
core/storage/drive/writes.py    + folder_listed, folder_named (adıyla klasör, yoksa açıp en eski), listed (sayfalı liste, PastPages)
core/storage/drive/commit.py    + Writer.rename_folder: <p>/ yeni kimlikte açılınca başın folder etiketi, projenin kilidinde
core/storage/drive/head.py      + check_ref: ref bir Drive kimliği mi
core/storage/drive/blocks.py    süpürme writes.listed'le
core/storage/memory.py          çöpteki dosyanın ref'ine put ve copy Taken (sözleşmede)
core/storage/port.py            put'un ve copy'nin belgesi: çöpteki dosyanın ref'i Taken, çöpteki kaynak kopyalanabilir
core/storage/drive/api.py       + altı çağrı: stream, copy, about, upload_start, upload_chunk, upload_status
core/storage/drive/google.py    + o çağrılar; baytlar google-auth'un AuthorizedSession'ıyla, akarak
core/storage/drive/limits.py    + simple_most, chunk, keep_free, PIECE
core/storage/drive/adapter.py   DrivePort dosya işlemlerini Files'a devreder; kökün kimliğini tutar (exports/ için); projects/ folder_named'le,
                                liste listed'le; açılıştaki temizlik adı başına bütün klasörleri alır
tests/storage/drive/fake.py            + altı çağrı, yükleme oturumları
tests/storage/drive/rigs.py            "files: v1-9" listesi silindi
tests/storage/drive/test_files.py      dosya işlemleri: çağrı sayıları, tekrarlar, yerler, sınırlar
tests/storage/drive/test_transfer.py   yükleme ve indirme: parçalar, kopma, yarım dosya, md5
tests/storage/drive/test_retry.py, test_google.py, test_adapter.py, test_real.py   eklemeler
tests/storage/contract.py              + çöpteki dosyanın ref'ine put Taken
```

Her dosyanın tek işi var: `files.py` port'un sözünü tutar (tekrar, `Taken`, `NotFound`), `places.py`
yerin klasörünü bulur ya da açar, `transfer.py` baytı taşır. Bekleme `retry.py`'nin, küçük çağrılar
(`folder_at`, `trash`, adıyla klasör, sayfalı liste) `writes.py`'nin, kimlikler `pool.py`'nin, başa
yazmak `commit.py`'nin. Adıyla klasör ve sayfalı liste artık tek yerde: `projects/`, `media/`,
`exports/` aynı `folder_named`'i, `projects/`'in listesi, süpürme ve `export_names` aynı `listed`'i
kullanır; her biri kendi `404` ve sayfa sınırı sözünü söyler.

## Drive'da

```
<kök>/
  projects/
    <p>.json.gz           baş dosyası (532)
    <p>/                  ilk dosyada ya da ilk mühürde açılır, hangisi önce gelirse
      records-<n>.jsonl.gz, history-<n>.jsonl.gz
      media/              projenin fotoğrafları ve videoları: proje çöpe gidince onlarla gider
        <ad>              her dosya kendi ayrılmış kimliğinde (ref)
  exports/                ilk export'ta açılır
    <tarih> <ad>/         export_folder
      <ad>.mp4
      photos/001.png …
```

Dosyalar kimlikleriyle (`ref`) okunur, adlarıyla hiç aranmaz; klasörler yalnız dosyaların yeri ve
insan içindir. Süpürme (532) `<p>/`'yi listeler ve yalnız `records-`/`history-` adlı, klasör olmayan
dosyalara dokunur: medya `media/`'dadır, süpürmenin listesine girmez, listeyi de büyütmez.

**`media/`'nın kimliği hiçbir yerde saklanmaz** (532'nin bıraktığı karar): `<p>/` içinde adıyla
bulunur (`name = 'media'`, 1 listeleme) ve portun belleğinde tutulur, proje başına bir kimlik. Yoksa
havuzdan bir kimlikle açılır ve **yeniden listelenir,** en eski alınır: aynı anda açan iki core aynı
klasörde buluşur (`projects/`'in açılışı gibi); boş kalan ikincisi projeyle çöpe gider. Neden: baş
dosyasına yazmadan — `put` baş dosyasına dokunmaz, bir değişiklik değildir — ve her core'un, yeniden
başlayan core'un da, aynı yeri bulması için.

**`<p>/`'nin açılışı.** Kimliği oluşturmada ayrılır ve baş dosyasının `folder` etiketindedir (532). Proje
ilk mühürden önce dosya alırsa (her yeni projede böyledir: ilk işin çıktısı yüzüncü değişiklikten
önce gelir) `<p>/`'yi `put` açar, o kimlikte (`folder_at`; `409` açılmıştır). İlk mühür aynı kimliği
açmaya kalkar, `409` alır, sürer. Drive hiç açılmamış bir klasörü boş listeler, `404` vermez (534,
gerçek Drive): `<p>/`'de `media` bulunmazsa — `<p>/` yoktur ya da yalnız `media/` — `<p>/` ayrılmış
kimliğinde açılır (varsa `409`) ve `media/` orada bulunur ya da açılır. İki hal aynı altı çağrıdır.

Ayrılmış kimliği Drive artık almazsa (`400`; 528, 6: ayrılmış kimliklerin ömrü ölçülüyor) klasör
yeni bir kimlikte açılır (havuz bırakılır, tek yeni kimlik; `pool.make`) ve başın `folder` etiketi
ona çevrilir: **yalnız etiket,** içeriksiz tek `files.update` — sürüm, yani içeriğin md5'i, değişmez;
yüklü tabanlar geçerli kalır. Önce içerik sonra onu gösteren: klasör açılır, sonra etiket yazılır;
etiket yazılamazsa yeni klasör çöpe gider. Etiketi `commit.py`'nin `Writer.rename_folder`'ı yazar,
**projenin kilidinde** (`DrivePort` onu `Places`'e bir çağrı olarak verir): bu core'un o projedeki
hiçbir `commit`'i bakışıyla baş yazması arasında değildir. Kilit sırası hep önce yerin (`Places`),
sonra projenin; `commit` `Places`'in kilidini hiç almaz. Kilidin içinde etikete yeniden bakılır (+1
`files.get`): başka bir core yeni bir klasörü çoktan adlandırdıysa onunki kullanılır, bizimki çöpe.
Kalan risk başka bir core'dadır: onun bir `commit`'i bakışını eski etiketle yapmış ve başını bizim
etiketimizden sonra yazarsa — pencere o `commit`'in bakışından baş yazmasına kadardır, ~1 sn — eski
etiketi geri yazar: klasör sahipsiz kalır, dosyaları kimlikleriyle okunur; proje silinince açılıştaki
temizlik (532) baş dosyası olmayan `<p>` klasörlerinin hepsini çöpe atar. Kayıp yok, yalnız çöpe geç
gitme.

**`exports/`** kökte adıyla bulunur, portun belleğinde tutulur; ilk `export_folder` yoksa açar
(havuzdan kimlik, yeniden listeleme, en eski). Açılışta değil: hiç export yapmayan core onun için
Drive'a gitmez. `export_names` `exports/` yoksa açmaz, `()` döner.

## İşlemler

Her satır testte taklit API'nin saydığıyla tam eşit. "Yeri bilinen": proje portta biliniyor (açılış
`projects/`'i listeler, her başın yerini bilir) ve `media/`'sı bu portta bir kez bulundu.

| İşlem | Drive çağrısı | 4. adım |
|---|---|---|
| `put`, ≤ 5 MiB, yeri bilinen | 1 `files.create` (multipart, içerik ve bilgi tek istekte) | "1 yükleme" |
| `put`, > 5 MiB | 1 `files.get` (`ref`'e bakış) + 1 oturum açma + ⌈boy / 16 MiB⌉ parça; kopan parça başına, beklemeden sonra +1 durum sorusu | "resumable 1+2 parça" (20 MB), + 1 bakış: Sapma 8 |
| `put`, aynı `ref`'e tekrar | ≤ 5 MiB: 1 `files.create` (`409`) + 1 `files.get`; büyükte yalnız bakışın 1 `files.get`'i, bayt gitmez | "tekrarda `409`" |
| `put`/`copy` `InProject`, projeye bu portta ilk dosya | `media/` bulunursa + 1 listeleme; bulunmazsa + 1 listeleme + 1 klasör (`<p>/`, açıksa `409`) + 1 listeleme + 1 klasör (`media/`) + 1 listeleme; proje portta bilinmiyorsa + 1 ad araması; havuz boşsa + 1 `generateIds` | "klasörler ilk ihtiyaçta açılır" |
| `exists` | 1 `files.get` (`md5Checksum,size,trashed`) | Aynı |
| `get` | 1 `files.get` + 1 indirme, boyu ne olursa olsun (akarak); boş dosyada indirme yok | Sapma 1 |
| `copy` | 1 `files.copy`, ayrılmış kimliğe; tekrarda + 2 `files.get` (`ref` ve kaynak) | "1 kopya" |
| `trash` | 1 güncelleme (`trashed=true`) | Aynı |
| `export_folder` | 1 klasör; tekrarda + 1 `files.get`; portun ilk export'unda + 1 listeleme (kökte `exports`), yoksa + 1 klasör + 1 listeleme | "1 klasör" |
| `export_names` | `exports/`'in sayfası başına 1 listeleme (1000 klasöre 1); portta ilk kez + 1 kök listelemesi; `exports/` yoksa yalnız o | "1 listeleme" |
| `space` | 1 `about.get` (`storageQuota`) | Aynı |

Hiçbir işlem proje sayısına ya da projenin dosya sayısına bağlı değildir; `export_names` export
sayısının binde biriyle büyür, çünkü `(1)`, `(2)` bütün adlara bakarak verilir. Yazılan geri okunmaz:
`put`'un md5'i gönderilen baytlardan yerelde hesaplanır, `get`'inki diske yazılan baytlardan.
Bir işlemde bir dosya iki kez okunmaz.

### `put(ref, kaynak, ad, yer)`

1. `ref` bir Drive kimliği biçiminde değilse `ValueError` (adresten gelmiş olabilir, hiçbir şeye
   bakılmadan); `InProject`'te proje kimliği de (`check_project`).
2. Yerin klasörü (`Places.folder`): `InExport(f)` için `f`; `InProject(p)` için `p`'nin `media/`'sı.
   Hiç olmamış proje `NotFound`.
3. Kaynak ≤ `simple_most` (5 MiB, Drive'ın multipart sınırı) ise **tek istek:** baytlar okunur (en
   çok `simple_most`+1; fazlası okunurken büyümüş dosyadır, `ValueError`), md5'leri hesaplanır,
   `files.create` ayrılmış kimlikle, `fields=id,md5Checksum,size`. Kaybolan cevapta `again` yeniden
   dener; önceki deneme yazdıysa `409` gelir.
4. Büyükse önce **`ref`'e bakılır** (1 `files.get`): orada bir şey varsa 5. adımdaki gibi
   karşılaştırılır, bayt gönderilmez. Drive kullanılmış kimliği yalnız son parçada reddeder (534,
   gerçek Drive): bakışsız bir tekrar bütün parçaları yeniden gönderirdi. Yoksa **parça parça**
   (aşağıda, Yükleme).
5. **`409`:** `ref`'te bir şey var. `files.get` (`md5Checksum,size,trashed`): boyu ve md5'i
   kaynağınkiyse aynı dosyadır, `Stored` döner — ikinci dosya yoktur; değilse, klasörse ya da
   çöpteyse `Taken`.
6. Drive'ın cevabındaki md5 ya da boy gönderilenden farklıysa `Taken`, iki md5 ve iki boyla: `ref`'te
   gönderilenden başka baytlar durur; aynı `put`'un tekrarı da `Taken` alırdı. Mesaj neden tahmin
   etmez.
7. `Stored(ref, boy, md5)`, md5 yerelde hesaplanan.

`400` (ayrılmamış ya da Drive'ın artık almadığı kimlik) Drive'ın sözüyle `Rejected`: `ref` core'undur,
yenisini core ayırır. `404` (yer yok) `NotFound`; projenin `media/` hatırası silinir, sonraki `put`
yeniden bulur.

### Yükleme

**Tek istek** 5 MiB'a kadar (`simple_most`). Üstü Drive'ın resumable yüklemesiyle:

1. `upload_start`: bilgi (kimlik, ad, üst klasör, tür) ve boy, 1 istek; Drive bir oturum adresi verir.
   Oturum dosya oluşturmaz: dosya son bayt varınca oluşur (Drive belgesi; 528, `cut_upload`). Bu
   yüzden yarım dosya hiç olmaz. Kullanılmış kimlikte de oturum açılır: `409` son parçayla gelir
   (534, gerçek Drive); onu `put`'un baştaki bakışı önler (yukarıda, 4).
2. Parçalar sırayla, her biri `chunk` (16 MiB; Drive son parça dışında 256 KiB'ın katını ister)
   kadar, bellekte bir parça. Her parçanın cevabı Drive'ın elindeki bayt sayısıdır, son parçanınki
   dosyanın bilgisi.
3. **Kopan parça** (cevapsız, `5xx`, hız sınırı): `retry.resumed` bekler ve Drive'a oturumun nerede
   kaldığını sorar (`upload_status`, `Content-Range: bytes */boy`). Gönderim oradan sürer: parçanın
   Drive'ın aldığı kısmı yeniden gönderilmez, hiçbir bayt körü körüne iki kez gitmez.
4. **md5 Drive'ın aldığı baytlardan:** her cevaptan sonra, parçanın Drive'ın onayladığı kısmı md5'e
   eklenir; parçanın yarısı alındıysa yarısı. Böylece md5 tam olarak yazılanındır.
5. **Durma sınırı:** ilerlemeden geçen bekleme `Backoff`'un ~60 sn'lik bütçesindedir; bütçe her
   ilerlemede yenilenir. Uzun ama akan bir yükleme kesilmez; bir dakika hiç ilerlemeyen biter.
6. Bütçe biterse: son parça değilse `Rejected` (dosya oluşmadı); son parça gönderilmiş ve cevabı
   kaybolmuşsa `Unconfirmed` (oluşmuş olabilir; aynı `put`'un tekrarı `409`'la aynı dosyayı bulur).
   İlerlemeyen her tur bir kez bekler: kopmadan sonra `resumed` zaten beklemiştir.
7. **Son parçada `409`:** bakıştan sonra aynı `ref`'e bir yükleme daha biterse (iki yükleme üst üste
   bindi: core yeniden başladı, aynı `put` yeniden) öbürünün son parçası `409` alır. `resumed` onu
   `again` gibi `Conflict` verir; yükleme `409` yoluna döner: kaynağın md5'i yerelde, `ref`'teki
   dosyayla karşılaştırılır.
   Oturumun `404`'ü (bitmiş ya da düşmüş oturum) son parçada `Unconfirmed`, öncesinde `Rejected`.
   Drive önceki onayından geri ya da gönderilenden ileri bir sayı derse `Rejected`.

**Oturum adresi bir anahtardır** (içindeki `upload_id` o yüklemeyi sürdürmeye yeter): hiçbir mesaja,
log'a girmez. Bağlantı hatası metnindeki `upload_id` `(hidden)` olur (`google.py`, testle).

### `exists(ref)`

1 `files.get` `md5Checksum,size,trashed`. Yoksa (`404`), çöpteyse, klasörse (md5'i yok) ya da
Drive'ın alanları biçimsizse `None`; değilse `Stored`. İşin çıktısı zaten Drive'daysa iş bununla,
indirmeden biter (4. adım, Bir iş). Çöpe giden klasörün içindekiler `trashed`'i 10–20 sn geç alır
(528, 7); sözleşme buna bakmaz.

### `get(ref, hedef, en_çok)`

1. `files.get` `md5Checksum,size,trashed`: yoksa, çöpteyse ya da klasörse `NotFound`.
2. Boy `en_çok`'u aşıyorsa `TooLarge(boy, en_çok)`, diske hiçbir şey yazılmadan.
3. **Diskte yer:** hedefin klasörü açılır; dosya diskte `keep_free`'den (1 GiB) azını bırakacaksa
   `TooLarge(boy, kalan_yer)` — port'un sözüyle, `en_çok` "diskte kalan yer"i de anlatır.
4. **Tek indirme, akarak:** `Range: bytes=0-<boy>` — dosyanın boyunun bir baytı fazlası, kablodan
   fazlası hiç geçmez; Drive Range'e uymasa da istemci o kadarından sonra keser. Parçalar geldikçe
   hedefin yanındaki geçici dosyaya (`<ad>….part`) yazılır ve md5'e eklenir; bellekte en çok bir
   parça (1 MiB).
5. Kopan indirme `read`'in beklemesiyle baştan denenir; geçici dosya boşaltılır.
6. Yazılanın boyu ve md5'i `files.get`'inkiyse geçici dosya hedefin yerine taşınır (`os.replace`);
   değilse dosya okunurken değişmiştir: geçici dosya silinir, `Rejected`. Her hatada geçici dosya
   silinir: hedefte ya bütün dosya olur ya hiçbir şey.

**Sapma 1 — `get` 2 çağrı,** 4. adım "1 indirme" sayıyordu. Drive çöpteki dosyanın baytlarını da verir
(532, Sapma 1'in aynısı), sözleşme `NotFound` ister (`trashed`); `TooLarge` hiçbir şey yazılmadan ve
gerçek boyla gelmeli (`size`); yazılanın md5'i Drive'ınkiyle karşılaştırılır (m531, Sonraki
maddeler). Karşılığında indirme, boyu ne olursa olsun tek istektir: 20 MB'lık video da.

### `copy(kaynak, ref, ad, yer)`

`files.copy` kaynağın kimliğiyle, gövdede ayrılmış `ref`, ad ve yerin klasörü (Drive'ın `generateIds`'i
"create ya da copy" için kimlik verir); `fields=id,md5Checksum,size`; bayt indirilmez. `409`: `ref` ile
kaynağa bakılır (+2 `files.get`); aynı boy ve md5'se aynı kopyadır, değilse `Taken`; kaynak yoksa
`NotFound`. `404`: kaynak ya da yer yok, `NotFound`, Drive'ın sözüyle (hangi kimliği bulamadığını
söyler). Çöpteki kaynağın kopyası reddedilmez: kopya tek çağrıdır, kaynağa ayrıca bakmak her
kopyaya +1 olurdu; core çöpteki dosyayı zaten kopyalatmaz.

### `trash(ref)`

1 güncelleme, `trashed=true` (`writes.trash`); `404` başarıdır. Klasör içiyle gider. Core hiçbir
dosyayı kalıcı silmez: `DriveApi`'de silme çağrısı yoktur (testle).

### `export_folder(ref, ad, inside)`

Klasör ayrılmış `ref`'te, `inside` verilmezse `exports/`'te, verilirse onun içinde. `409`: `ref`'e
bakılır (+1 `files.get` `name,mimeType,parents`); aynı ad, klasör ve aynı üst klasörse başarı, değilse
`Taken`. `404`: `inside` varsa `NotFound` (o klasör yok); yoksa `exports/` Drive'dan gitmiştir,
`Rejected` ve hatırası silinir.

### `export_names(önek)`

`exports/`'in çöpte olmayan klasörleri, `files(name)`, `nextPageToken` bitene kadar, en çok `pages`
(20) sayfa; aşarsa `Rejected`, sessizce kesilmez. Ad kodda `fold` ile karşılaştırılır (`ilike`'ın dört
i'si): Drive'ın `name contains`'i Türkçe I'yı eşlemez (528: `IŞIK` `ışık`'ı bulmadı), ve önekin
Drive'a hiç gitmez. `exports/` içindeki klasörler (`photos/`) `exports/`'in çocukları değildir,
sayılmaz.

### `space()`

1 `about.get` `storageQuota`: `limit` (yoksa `None`: sınırsız), `usage`, `usageInDriveTrash`. Biri
biçimsizse `Rejected`, Drive'ın cevabıyla.

## Hatalar

| Drive | Adaptör |
|---|---|
| `409` | `put`, `copy`: içerik karşılaştırılır, aynıysa başarı, değilse `Taken`; `export_folder`: ad ve yer |
| `404` | Yer: `NotFound`; dosya: `exists` `None`, `get` ve `copy` `NotFound`, `trash` başarı; `exports/`, kök, `projects/`: `Rejected` |
| `400` ayrılmış kimlikte | `ref`'te `Rejected` (core'un kimliği); `media/`, `exports/`, `<p>/` için `pool.make` bir kez yeni kimlik |
| Hız sınırı, `5xx`, cevapsız | `retry.py`'nin beklemeleri; yüklemede `resumed` |
| Bütçe sonu | `Rejected`, oluşmuş olabilecek dosyada `Unconfirmed`; Drive'ın son sözüyle |

`ref` ve `InExport`'un klasörü Drive kimliği biçiminde değilse (`[A-Za-z0-9_-]{1,128}`) `ValueError`,
Drive'a gitmeden: `q`'ya ya da adrese denetlenmemiş değer girmez.

## Sınırlar

| Ne | Sınır | Aşılınca | Testte |
|---|---|---|---|
| Tek istekli yükleme | 5 MiB (`simple_most`), Drive'ın multipart sınırı | Parça parça | `simple_most=4` |
| Yükleme parçası | 16 MiB (`chunk`; Drive'da 256 KiB'ın katı); bellekte bir parça | Sonraki parça | `chunk=4`; gerçek Drive'da 256 KiB |
| Her parçanın, indirmenin ve kopyanın isteği | 120 sn soket zaman aşımı (`transfer`) | `DriveLost`, bekleme içinde | 0,05 sn'lik sınırla, cevap vermeyen yerel sokete |
| İlerlemeyen yükleme | ~60 sn (`Backoff`), her ilerlemede yenilenir | `Rejected` / `Unconfirmed` | `ManualClock`'la |
| `get`'in baytı | `en_çok`; Range `bytes=0-<boy>`, istemci boy+1'den sonra keser | `TooLarge`, yazılmadan | Küçük `en_çok`; Range'e uymayan yerel sunucu |
| İndirmenin belleği | Parça 1 MiB | — | — |
| Diskte boş yer | `keep_free` (1 GiB) kalmalı | `TooLarge(boy, kalan)`, yazılmadan | Verilen `free` ile |
| Tek istekli yüklemenin okunması | `simple_most`+1 bayt | `ValueError` (okunurken büyüyen kaynak) | — |
| `export_names` listesi | sayfa en çok 1000, en çok 20 sayfa (`pages`) | `Rejected` | Sayfası 2'lik taklit, `pages=2` |
| `q`'daki değer | Kimlikler biçimle denetlenir, adlar sabit (`media`, `exports`); önek `q`'ya girmez | `ValueError` | Tırnaklı önek, taklidin gördüğü ad |
| md5 | Gönderilen ve yazılan baytlardan, yerelde | `Taken` / `Rejected` | Farklı md5 veren taklit |
| `media/` hatırası | proje başına bir kimlik | — | — |

`keep_free` v1-25'te ortamdan verilebilir; 1 GiB Colab diskinin ComfyUI'ye ve önbelleğe bıraktığı paydır.

## Testler

Önce düşen testle; taklit API'li hiçbir test gerçek bir saniye beklemez, dosyaları birkaç bayttır.

- **Sözleşme** (`test_contract.py`, `test_real.py`): `PortContract`'ın 15 dosya testi artık atlanmaz;
  `rigs.py`'deki liste silindi, `contract.py`'ye dokunulmadı.
- **`test_files.py`** (taklit API): yukarıdaki tablonun her satırı tam eşitlikle; `<p>/`'yi ilk dosyanın
  açması ve ilk mührün `409`'la sürmesi; iki core'un `media/`'da ve `exports/`'te en eskide buluşması;
  `<p>/`'nin kimliğini Drive almayınca yeni klasör ve yalnız etiket, sürüm aynı; başka core'un
  adlandırdığı klasörün kullanılması; tekrarda aynı dosya, başka içerikte ve çöpteki dosyada `Taken`;
  biçimsiz `ref` `ValueError`; `export_folder`'ın tekrarı ve başka yerde `Taken`; `export_names`'in
  sayfa sınırı, önekin `q`'ya gitmemesi; `space`; diskte yer; `DriveApi`'de silme çağrısı olmaması.
- **`test_transfer.py`** (taklit API): tek istek ve parça sınırı; parçaların sırası; cevabı kaybolan
  parçadan sonra durum sorusu ve kalanla sürmek; parçanın yarısını alan Drive; bütçe sonu `Rejected`
  ve son parçada `Unconfirmed`; yarıda kalan oturumun dosya bırakmaması; md5'in yerel oluşu ve
  Drive'ınkiyle tutmazsa `Taken`; indirmede geçici dosya, kopan akışın baştan denenmesi, okunurken
  değişen dosyada hedefin boş kalması.
- **`test_retry.py`:** `resumed` — ilk hatadan sonra durum sorusu, belirsizlik yalnız gönderimde.
- **`test_google.py`:** parça ve akan indirme zaman aşımında `DriveLost`; hata metninde `upload_id`
  görünmez; `Range` cevabının okunması; Range'e uymayan sunucuda en çok `en_çok`+1 bayt.
- **`test_real.py`:** sözleşmenin dosya testleri; üstüne 256 KiB'lık parçalarla ~0,8 MB'lık bir
  yükleme: çağrılar sayılır, ikinci parçanın cevabı düşürülür ve yükleme Drive'ın söylediği yerden
  sürer, tekrarı `409` ile aynı dosya, yarıda bırakılan oturum dosya bırakmaz.

## Ne bozulabilir

- **Aynı yüklemenin tekrarı ikinci dosya bırakır:** her dosya ayrılmış kimlikte, tekrarı `409`;
  içerik karşılaştırılır; testle.
- **Kopan yükleme yarım dosya bırakır:** resumable dosyayı son baytta oluşturur; yarıda kalan oturum
  hiçbir şey bırakmaz; testle, gerçek Drive'da da.
- **Kopan parça iki kez yazılır ya da atlanır:** gönderim Drive'ın söylediği bayttan sürer, md5
  yalnız onaylanan baytlardan; testle.
- **`get` yarım dosya bırakır:** geçici dosya, md5 ve boy tutunca `os.replace`; her hatada silinir;
  testle.
- **Disk dolar:** indirmeden önce boş yere bakılır; testle.
- **Oturum adresi log'a düşer:** hata metninden ayıklanır; testle.
- **İki core aynı anda `media/` ya da `exports/` açar:** ikisi de en eskisini alır; testle.
- **Kalıcı silme:** `DriveApi`'de yok; testle.
- **Adresten gelen biçimsiz kimlik:** `ValueError`, Drive'a gitmeden; testle.
- **`<p>/`'nin kimliğini Drive almaz:** yeni klasör, yalnız etiket, projenin kilidinde; başka bir
  core'un `commit`'inin bakışı ile baş yazması arasına düşen etiket yazmasını o `commit` geri
  yazarsa klasör sahipsiz kalır, dosyaları okunur, proje silinince açılıştaki temizlik alır
  (yukarıda).
- **Yazılırken çöpe giden projeye `put`:** Drive çöpteki klasöre dosya yapar ve dosyanın kendisi
  çöpte değildir (534, gerçek Drive). Başka bir core'un sildiği proje bu portta hâlâ biliniyorsa
  `put` başarır, dosya çöpteki `media/`'ya gider. Core onu kaybetmiş sayılmaz: dosyayı anan tek
  kayıt projenin kendisidir, o da çöptedir — işin bitişini yazan `commit` `NotFound` alır, hiçbir
  canlı proje dosyayı anmaz; kullanıcı projeyi çöpten geri alırsa klasör de döner, dosya içindedir.
  Bu portun kendi sildiği projede `Places` her `put`'ta portun bildiği yere bakar, proje orada yoksa
  adıyla arar: `NotFound`. Sözleşme yalnız hiç olmamış proje için `NotFound` ister (m531).
- **`media/` canlı projede elle çöpe atılır:** `Places` onu bu portun ömrü boyunca hatırlar, sonraki
  dosyalar çöpteki klasöre gider; canlı ve okunur kalırlar, ama çöp boşalınca Drive onları klasörle
  birlikte silebilir. Core'un kendi işlemleri `media/`'yı yalnız projeyle çöpe atar
  (`trash_project`); bu Drive'da bir elin yapacağıdır, ve 4. adım medyaya elin dokunuşunu
  kullanıcınınki sayar. Kapatmanın bedeli `media/`'ya portta bir süre sonra yeniden bakmaktır (proje
  başına, örneğin 10 dakikada bir `files.get`): ana agent'ın kararı.

## Bitti sayılır

Kabul koşulunun üç satırı: sözleşmenin dosya testleri taklit API'de, bellek içi adaptörde ve gerçek
Drive'da yeşil; tekrarın tek dosya bırakması, kopan yüklemenin sürmesi ve yarım dosya bırakmaması,
kalıcı silme olmaması testli; çağrı sayıları tabloyla tam eşit. Suite yeşil, ruff ve pyright temiz;
`openapi.json` değişmez; yeni paket yok (`requests` zaten sabit sürümle `requirements.txt`'te).

## 4. adımdan sapmalar

1. **`get` 2 çağrı** (`files.get` + indirme), 4. adım 1 indirme sayıyordu (yukarıda). İndirme, boy ne
   olursa olsun tek istek.
2. **`media/`'nın kimliği saklanmaz,** 4. adımın baş dosyasındaki `media` alanının yerine: adıyla
   bulunur, portun belleğinde durur, aynı anda açan core'lar en eskide buluşur. Bedeli: projeye bu
   portta ilk dosyada +1 listeleme.
3. **`<p>/`'yi ilk dosya da açar,** 532'de yalnız ilk mühür. Ayrılmış kimliği Drive almazsa yeni
   klasör ve yalnız `folder` etiketi yazılır; sürüm değişmez.
4. **`exports/` ilk export'ta bulunur,** 4. adımın açılıştaki kök listelemesinde değil: boştaki core
   onun için Drive'a gitmez.
5. **`export_names` `name contains` kullanmaz:** Türkçe I'yı eşlemediği için daraltması da yanlış
   olurdu (528); bütün export klasörleri listelenir, 1000'e bir sayfa.
6. **Çöpteki dosyanın `ref`'ine `put` ve `copy` `Taken`** alır: `ref` kullanılmıştır, dosyası yoktur,
   core başka bir `ref` ayırır. Sözleşmede (yeni test); bellek içi adaptör de öyle yapar artık.
   **Çöpteki kaynağın kopyası** sözleşmeye bağlanmadı: Drive'da reddedilmez (kaynağa bakmak her
   kopyaya +1 olurdu), bellek içi adaptör `NotFound` der; port'un belgesi çöpteki kaynağın
   kopyalanabileceğini söyler.
7. **Baytlar google-auth'un `AuthorizedSession`'ıyla** (`requests`) gider: httplib2 cevabı bütünüyle
   belleğe alır, büyük dosya akarak inmez. Bilgi çağrıları Drive'ın kütüphanesinde kalır.
8. **Büyük `put` önce `ref`'e bakar** (+1 `files.get`): Drive kullanılmış kimliği resumable
   yüklemenin yalnız son parçasında reddeder (534); bakışsız bir tekrar bütün baytları yeniden
   gönderirdi. Küçük `put` değişmez.

## Gerçek Drive

Gerçek Drive'ı yalnız ana agent koşar (kullanıcının isteği); token'ın yolu `QUEEN_STUDIO_DRIVE_TOKEN`'dan:
`QUEEN_STUDIO_DRIVE_TOKEN=<token yolu> queen-studio/.venv/Scripts/python -m pytest queen-studio/tests/storage/drive/test_real.py -q`.

**Birinci koşu** (7 Kasım): 35 geçti, 1 düştü, 1 hata, 257 sn. Sözleşme dosya testleriyle bütünüyle
geçti. Düşen büyük yükleme denemesiydi (sayan sarmalayıcı anahtar kelime almıyordu). Hata, koşunun
klasörünün çöpe atılmasında: `403 appNotAuthorizedToChild`.

**Teşhis** (`tmp/m534-diag/diag.py`, birinci koşunun klasörü): 78 görünen çocuğun hepsi
`isAppAuthorized`, `ownedByMe`, `canTrash`; hepsi tek tek çöpe gitti, hiçbiri reddetmedi; klasörün
kendisi yine, yeniden denemede de reddedildi. Ret görünen tek bir dosyadan gelmiyor: uygulamanın
göremediği bir çocuktan ya da bir işlem dizisinden.

**İkinci koşu** (7 Kasım): 37 geçti, 1 düştü, 1 hata, 389 sn; klasörün çöpü yine reddedildi. Düşen
büyük yükleme denemesiydi: tekrarın `409`'u oturumun açılışında değil son parçada geldi (aşağıda).
Yoklamaların bulduğu, şimdi `test_what_the_adapter_assumes_of_drive_holds`'ta doğrulanan:

| Ne | Gerçek Drive | Kodda |
|---|---|---|
| Kullanılmış kimlikte resumable oturum | Açılır; `409` yalnız son parçayla gelir | Büyük `put` önce `ref`'e bakar (+1); taklit de son parçada reddeder |
| Hiç açılmamış klasörün listesi | Boş liste, `404` değil | `Places` boş listede `<p>/`'yi açar; taklit de boş verir |
| Ayrılmış kimliğe `files.copy` | Kabul; cevapta md5 ve boy, `isAppAuthorized` doğru | Aynı |
| Bitmiş oturumun son parçası ve durum sorusu | İkisi de kimlik, md5, boy | Aynı |
| `about.storageQuota` | `limit`, `usage`, `usageInDrive`, `usageInDriveTrash` | Aynı |
| `alt=media`, `Range: bytes=0-3` | `206`, `bytes 0-3/10`, yönlendirme yok | Aynı; yönlendirme izlenmez, reddedilir |
| `308`'in `Range`'i | 256 KiB'ın katları (262144, sonra 524288) | Aynı |
| Yalnız etiket güncellemesi | md5 aynı kalır | `rename_folder` buna dayanır |
| Çöpteki klasöre dosya | Kabul; dosya çöpte değil | Ne bozulabilir'de |
| Tek türde çocuk tutan klasörün çöpü (multipart, resumable, havuz kimliğinde klasör, ayrılmış kimliğe kopya, kimliksiz kopya) | Hepsi çöpe gitti | Ret türden gelmiyor |

Bilinmeyen kalan: *açılıp sonra silinmiş* bir klasörün listesi (`404` mü, boş mu; core kalıcı
silmediği için denenemez). 532'nin kodu `projects/` gidince listede `404` bekler; boş gelirse
`projects()` boş liste verir ve ad araması `NotFound` der. Çağrı sayısı değişmez.

**Bölme** (üçüncü koşu, sonucu bekleniyor): her sözleşme testi ve her gerçek Drive testi koşunun
klasöründe kendi klasöründe çalışır; test bitince o klasör çöpe atılır, Drive'ın sözü
`tmp/m534-real/trash.json`'a yazılır, koşu düşmez. Yoklamaların kapsamadığı diziler de kendi
klasörlerinde: çöpteki klasöre dosya, çocuğun annesinden önce çöpe gitmesi, havuz kimliklerinde üç
kat (`projects/<p>/media/`), bitmemiş oturum, ayrılmış kimlikte `409`, son parçada `409`, hiç
ayrılmamış kimlik, hiç açılmamış klasöre oluşturma, kopya sonra kaynağın çöpü, çöpe atıp geri alma,
içeriğiyle ve yalnız etiketle güncellenen baş dosyası. Reddedilen klasör suçlu diziyi gösterir.

*(Üçüncü koşunun sonucu ve çözüm buraya.)*

## Sonraki maddeler için

- **v1-13 (medya):** `put` ve `get` `InProject(p)` ile; `get`'in `en_çok`'u türün bütçesi.
  `DiskCache` bugün bayt alır; büyük video için yol alan bir `put` gerekir. `get` çökerse hedefin
  yanında `<ad>….part` kalır: medya önbelleği açılırken onları siler (`DiskCache`'in `.part`'ı gibi).
  Diskte yer bakışı tek `get`'indir: aynı anda iki `get` aynı boş yeri görüp ikisi birden sığabilir
  sanabilir; aynı anda inenlerin toplamını önbelleğin tek sınırı tutmalı.
- **v1-15 (işler):** çıktı `exists(ref)` ile, indirmeden; `put`'un `Unconfirmed`'inde aynı `put`
  yeniden (`409` aynı dosyayı bulur); `Taken` core'un yanlışıdır.
- **v1-21 (export):** `export_names` her export'ta bir listeleme; `export_folder(ref, ad)`,
  `export_folder(photos, "photos", inside=ref)`, `put(…, InExport(ref))`, `copy(…, InExport(photos))`.
- **v1-25:** `keep_free` ortamdan; `logs/`'un yeri (`Place`) yok, log'u gönderen madde ekler.
