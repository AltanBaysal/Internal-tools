# Madde 523 · Referans sırası ve arşiv işaretleri aynı anda yazılınca kaybolmaz — tasarım

**Tarih:** 30 Ekim 2026 · **Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-22),
523 · v11-22 (yama v11.1) · **Dal:** `feat/queen-editor-v11.1` · **Plan:**
[2026-10-30-queen-editor-m523-referans-arsiv-ayni-anda-plan.md](../plans/2026-10-30-queen-editor-m523-referans-arsiv-ayni-anda-plan.md)
· **Kurallar:** queen-editor [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kabul koşulu (maddeden)

Referans havuzuna ekleme, çıkarma ve sıralama, ve projeleri arşivleme, geri alma, silme, adlandırma
aynı anda iki kez gelince ikisi de kalıyor.

Kullanıcı — *"bu hatalarıda çöz istersen"*. BACKLOG'un işi: *"Referans sırası ve arşiv işaretleri aynı
anda iki yazmada birini kaybedebilir"* (512'nin coder'ı). Yanındaki iş de aynı düzeltmeden çıktığı için
bu maddeye alındı: *"Proje silinirken gelen bir basış silinecek klasörde koşu başlatabilir"* (522'nin
reviewer'ı). İkisi de bu yamadan eski. Ekran değişmez; `dist` derlenmez.

## Hata, görüldüğü gibi

Testler gerçek bir geçici klasörde (`Storage` ve gerçek depolar), ikinci yazmayı birincinin okuması
ile yazması arasına bir iş parçacığında sokarak yazıldı (`test_written_at_once.py`): dosya tutmayan bir
sahte depo yazma kaybedemez. Eski kodda hepsi kırmızı:

**1. Referans havuzu.** Üç kapı da havuzu ve sıra dosyasını (`references.json`) okur, karar verir,
sırayı bütün olarak geri yazar; kilit yok.

- *Aynı adla iki yükleme:* ikisi de boş adı okudukları havuzdan seçer, ikisi de `kedi.png` alır; sonra
  yazan öncekinin dosyasının üstüne yazar. Kırmızı: `[b'ILK'] == [b'IKINCI', b'ILK']` — bir dosya gitti.
- *Bir yazmanın ortasına düşen yükleme* (`yeni.png`), birinci kapı yükleme, çıkarma ya da sürükleme
  olunca: birincinin geri yazdığı sıra `yeni.png`'yi bilmez, yeni dosya sıradan düşer ve satırın sonu
  yerine adının sıralandığı yerde durur. Kırmızı: `['eski.png', 'bir.png']`, `[]`, `['eski.png']`
  (beklenen her birinde `yeni.png` sonda).

**2. Arşiv işaretleri.** `arsiv.json` bütün projeler için tek dosya. `DriveProjectStore`'un dört
değişikliği (arşive kaldırma, geri alma, silme, yeniden adlandırma) işaretleri okur ve bütün olarak geri
yazar; kilit yok. Arasına başka bir projenin arşive kaldırılması (`kına`) düşünce o işaret silinir.
Kırmızı, dördünde de: `['düğün']`, `[]`, `[]`, `['nişan']` (beklenen her birinde `kına` da).

**3. Silme ile basış.** `delete_project` koşuyu durdurur (`halt_project`), sonra klasörü siler, ve
projenin yazma kapısını almaz. Arasına düşen Kuyruğa ekle işini yazar ve boş işçiyi alır; klasör
ardından gider, işçi var olmayan bir projeye damgalı kalır. Kırmızı: basış `ProjectMissing` almadı,
işi kabul edildi.

**Reviewer'ın buldukları** (ilk sürüm kapıyı ekledikten sonra, hepsi testle kırmızı görüldü):

- *Kapı bütün yükleme boyunca tutuluyordu:* her klip için ffprobe ve her dosyanın Drive'a yazılması
  (onlarca MB) kapının içindeydi; o projeye her basış bunu bekliyor, ekranın 10 saniyelik zaman aşımı
  iş eklenmişken "Zaman aşımı" diyebiliyordu (ikinci basış işi ikiler). Kırmızı: süre kapının içinde
  soruldu (`[True] == [False]`).
- *Eski bir sekmenin sürüklemesi başka sekmenin yüklemesini sıradan düşürüyordu:* sürükleme bir türün
  satırını sekmenin kendi listesiyle bütün olarak değiştiriyordu. Kırmızı: `['iki.png', 'bir.png']`
  (beklenen sonda `aaa.png`).
- *Silmede işaretin klasörden önce düşmesi:* Drive'da yarıda kalan bir silme arşivli projeyi etkin
  projelerin arasına geri getiriyordu. Kırmızı: arşiv `[]` (beklenen `['düğün']`).

## Ne yapılır

### Referans havuzunun üç kapısı projenin yazma kapısında

`add_references`, `remove_reference`, `save_reference_order` projenin yazma kapısını (**G**,
`plan_store.held`, 512) projeye bakıştan cevaba kadar tutar. Üçü de `plan_store`'u bir parametre olarak
alır (`main.py`'deki `partial`'lar `_plan_store`'u verir); yalnız kapısı için.

Neden G, kendi kilidi değil: havuz proje başına ve G zaten proje başına "okuyup birlikte geri yazan
kapıların" kapısı. Üstelik aynı kapıyı yeniden adlandırma (522) ve artık silme de alıyor; yükleme bir
taşımanın ya da silmenin iki yanına düşemez (dosyalar eski klasörde, sıra yazması yok olan klasörde
düşmez). Ayrı bir kilit bunu vermezdi ve bir parça daha olurdu.

Varlık bakışı kapının içinde, 522'nin kuralıyla: taşımanın ya da silmenin hangi yanında olduğu ancak
orada kesindir. Sürüklemenin gövde denetimi (`InvalidReferenceOrder`) diske gitmediği için dışarıda.
Cevap (havuzun son hali) kapının içinde okunur: dışarıda okunsa, kapı bırakılır bırakılmaz gelen bir
taşıma kabul edilmiş bir yüklemeyi 404'le cevaplatırdı (522'nin F1'i).

### Yükleme iki adımda: uzun iş kapının dışında

Kapının içinde yalnız havuzu gerektiren şey kalır; elimizdeki baytlarla yapılabilen her şey önce,
kapısız yapılır:

1. **Kapısız:** projeye bakış (yoksa baytlar Drive'a gitmeden "Proje yok"), her dosyanın türü ve
   satırı, süresi (ffprobe, `_length`), basışın havuz olmadan da çiğnediği sınırlar
   (`references.check([], …)` — fazla uzun bir klip baytları Drive'a yazılmadan reddedilir), ve
   baytların havuz klasörüne **gizli adlarla** yazılması (`pool.stage`; `Storage.stage_bytes`,
   `TEMP_PREFIX`'li ad, hiçbir listeleme görmez).
2. **Kapıda:** projeye yeniden bakış, havuzun listesi, boş adların seçimi, sınırların havuzla birlikte
   tartılması, her gizli dosyanın adına çevrilmesi (`pool.place`; `Storage.rename_file`, tek
   `os.replace`), sıranın yazılması, cevap.

Reddedilen ya da yarıda kalan bir yükleme (`finally`) yerine konmamış gizli dosyaları siler
(`pool.discard`; hiç hata atmaz, yüklemenin kendi hatası söylenecek olandır, kalan dosya zaten gizli).

Gizli dosya yine de yüklemesinden uzun yaşayabilir: baytlar yazıldıktan sonra, kapıdan önce proje
yeniden adlandırılırsa dosyalar klasörle birlikte taşınır ve eski adla `discard` onları bulamaz; ya da
sunucu arada ölür. Görünmezler ama her biri Drive'da onlarca MB tutar (reviewer). Bu yüzden her yükleme,
kapıda, havuz klasöründe bir saatten (`STAGED_FOR`) eski gizli dosyaları süpürür (`pool.sweep`;
`Storage.sweep_staged`). Daha genç olan bir başka yüklemenin kapıyı bekleyen dosyası olabilir, kalır;
yüklemenin kendi dosyaları da genç olduğu için kalır. Silinemeyen dosya gizli kalır, yükleme düşmez.
Storage'ın `_save`'i iki parçaya ayrıldı — gizli dosyayı yazan `_staged` ve yerine koyan `os.replace` —
davranışı aynı; `stage_bytes` yalnız birinci parçayı kullanır. `DriveReferenceStore.save` artık
kullanılmadığı için yerini `stage`, `place`, `discard` aldı.

### Sürükleme, adını vermediği dosyanın yerini korur

`save_reference_order` her gönderilen tür için satırı artık `gallery_order.keep_unnamed(adlar, havuzdaki
satır)` ile kurar (512'nin galeri sürüklemesindeki kural): sürüklemenin adını vermediği bir dosya — başka
sekmenin, bu sekme havuzu çizdikten sonra yüklediği — altında durduğu dosyanın hemen üstüne, altında bir
şey yoksa sona konur. Havuzda olmayan adlar eskisi gibi düşer.

### `arsiv.json`'ın kendi kilidi: `DriveProjectStore`

Dosya bütün projelerin; proje başına bir kapı iki farklı projenin işaretini korumaz. Bu yüzden
`DriveMuteStore`'un yolu (BACKLOG'un önerdiği): depoda tek bir `threading.Lock` (**M**), her
okuma-değiştirme-yazmanın çevresinde. Okumalar (`list`, `list_archived`, `is_archived`) kilit almaz:
yazma geçici dosya ve `os.replace` ile bütün ya da hiç.

- `archive`, `restore`: işaretlerin okunması ve yazılması M'de. `archive`'ın klasör bakışı dışarıda,
  eskisi gibi.
- `rename`: okuma, klasörün taşınması (tek `os.rename`) ve yazma M'de — okuma ile yazma arasına başka
  bir değişiklik düşmesin diye taşıma da içeride.
- `delete`: işaretler önce okunur (kilitsiz), klasör silinir, sonra M'de **yeniden okunur** ve
  (proje işaretliyse) yazılır. Eskiden tek okuma vardı: önce okunur, klasör silinir, okunan liste
  yazılırdı.
  - Neden M klasörün silinmesi boyunca tutulmaz: yeniden adlandırmanın `store.rename`'i adın kilidinin
    (**N**) içinde çalışır (522), döngü de N'yi bekler. M bir rmtree boyunca — Drive'da yüzlerce dosya,
    onlarca saniye — tutulsaydı başka bir projenin yeniden adlandırması M'yi, döngü de N'yi o kadar
    beklerdi: GPU boş kalırdı.
  - Neden ikinci okuma: silmenin süresince başka bir projenin işaret değişikliği gelebilir; önceden
    okunan liste yazılsaydı o değişiklik kaybolurdu.
  - Neden işaret klasörden sonra: yarıda kalan bir silme arşivli projeyi arşivde bırakır (reviewer;
    işaret önce düşerse etkin projelerin arasına dönüyordu).
  - Eski güvence aynen kalır: okunamayan dosya silmeyi proje henüz bütünken durdurur.
  - Birinci okuma kilitsiz: yazmalar dosyayı bütün olarak değiştirir (geçici dosya, `os.replace`), okuma
    ya eski listeyi ya yenisini görür ve hiçbir şey geri yazmaz; kilit bir şey korumazdı.

### Silme projenin yazma kapısında

Yeni port `follow_delete(runner, plan_store, interrupt, sleep, project, remove)` (photo_generation):
G'yi tutarak koşuyu durdurur (`halt_project`, eskisi gibi) ve `remove`'u çalıştırır, cevabını döner.
`delete_project(store, end, name)` klasörün silinmesini (`lambda: store.delete(name)`) bu porta verir;
`halt` portunun yerine. 522'nin `follow_rename`'iyle aynı biçim: projeler özelliği kapıyı bilmez,
`main.py` iki özelliği birleştirir. "Önce koşu durur" kuralı artık porttadır; projeler özelliğinin testi
porta silmeyi verdiğini, photo_generation'ın testi durdurmanın silmeden önce olduğunu söyler.

Bir basışın kapı tutuşu **K** (işi yazar, işçiyi alır), silmenin kapı tutuşu **D** (durdurur, siler):

- **K, D'den önce:** iş yazılmış, işçi alınmış; D o koşuyu durdurur, sonra klasörü siler. Bugünkü
  "silme koşuyu durdurur" sözü.
- **D, K'den önce:** K geldiğinde klasör yok; kapı projeye kapının içinde bakar, "Proje yok" der, hiçbir
  şey yazmaz, işçiyi almaz.

## Neden hiçbir yazma kaybolmaz

- **Havuz:** aynı projenin üç kapısının havuzu okuyup yazan kısmı aynı G'de, yani biri ötekinden
  tamamen önce olur; ikinci kapı birincinin yazdığı havuzu ve sırayı okur. Aynı adla ikinci yükleme
  birinciyi görür, `kedi-2.png` olur. Kapının dışında yazılanlar gizli adlarda: hiçbir kapının okuduğu
  havuzda yoklar, adlarını ve sıradaki yerlerini kapıda alırlar.
- **Eski sekmenin sürüklemesi:** adını vermediği dosya sırada yerini korur, düşmez.
- **İşaretler:** dört değişikliğin okuma-yazması aynı M'de; ikinci okuma birincinin yazdığını görür.
  `delete`'in klasör silmesi M'nin dışında, ama yazdığı liste M'de, klasör gittikten sonra okunur —
  kaybolan işaret yok.
- **Silme:** basış ya silmeden önce biter ve koşusu durdurulur, ya sonra gelir ve projeyi bulamaz.

## Kilitler

Beş kilit: projenin yazma kapısı **G** (`plan_store.held`, proje başına), adın kilidi **N**
(`RunningName`), işçinin kilidi **R** (`PhotoRunner._lock`), izleme kilidi **W** (`QueueWatch`) ve
yeni, işaretlerin kilidi **M** (`DriveProjectStore._lock`).

| Kim | Sıra |
|---|---|
| Kuyruğa iş koyan kapı | G → R (bırakılır) → N (`took`, bırakılır) → W (522'deki gibi) |
| Yeniden adlandırma | G(küçük ad) → G(büyük ad) → N (`moved`) → M (`store.rename`, içinde taşıma) → bırakılır → R (`rename`) |
| Silme (yeni) | G → R (`halt_project`, kısa tutuşlar) → işaretler okunur (kilitsiz) → klasör silinir → M (işaretler, bırakılır) |
| Havuzun üç kapısı (yeni) | G yalnız; yüklemenin ffprobe'u ve baytları G'den önce, kilitsiz |
| Arşive kaldırma, geri alma (yeni) | M yalnız |
| Döngü | N (tutuşlar); R ayrı; G ve M hiç |

Kenarlar G→R, G→N, G→W, G→M, N→M ve G(x)→G(y) yalnız x < y için. M bir yaprak: içinde hiçbir kilit
alınmaz, tutulurken yalnız bir okuma, en çok bir yazma ve (yeniden adlandırmada) bir `os.rename`
var. N'yi tutan hiç kimse G'yi almaz; M'yi tutan hiç kimse bir şey almaz. Döngü yok, kilitlenme yok.

**GPU hiçbir kapıyı beklemez:** döngü G'yi de M'yi de hiç almaz. Havuzu adın kilidinde okur (522), havuzun
kapılarını beklemez. Döngünün tek dolaylı bekleyişi 522'deki gibi N'de süren bir yeniden adlandırma; o
da artık M'yi bekleyebilir, M'yi tutan da en çok bir işaret okuması ve yazmasıdır (başka bir projenin
arşive kaldırılması, geri alınması ya da silinmesi aynı anda gelirse): döngünün bir yeniden adlandırmayı
bekleyişi en çok Drive'da iki gidiş dönüş uzar. Silmenin klasör silmesi bu yüzden M'nin dışında.

## Maliyet

- **Yükleme (M dosya):** Drive'a eskisine göre ek olarak bir klasör bakışı (kapıdan önceki varlık
  bakışı), dosya başına bir yeniden adlandırma (`os.replace`) — O(M) — ve kapıda süpürme: havuz
  klasörünün bir listesi daha (bir gidiş dönüş; yalnız gizli dosyalar için birer stat, süpürülecek
  her dosya için bir silme — çoğu yüklemede hiç). Baytlar eskisi gibi bir kez
  yazılır. Kapının dışında: yüklenen her klip için bir ffprobe ve M dosyanın yazılması (uzun kısım).
  Kapıda: bir varlık bakışı, havuz listesi (bir klasör listesi, havuzdaki N klip için N ffprobe —
  bugünkü gibi), M yeniden adlandırma, sıranın okunması ve yazılması, cevap için havuz listesi
  yeniden. Kapıyı bekleyenler (aynı projenin basışları, yeniden adlandırması, silmesi, öteki havuz
  yazmaları) artık yüklemenin baytlarını beklemez; havuzdaki klip sayısı kadar ffprobe'u bekler. Başka
  projeler hiç beklemez.
- **Havuzla reddedilen yükleme:** baytlar yazılıp silinir (dosya başına bir yazma ve bir silme); basışın
  tek başına çiğnediği sınırlar ise baytlar gitmeden söylenir.
- **Çıkarma, sürükleme:** Drive'a ek işlem yok; kapı tutuşu kapının bütün işi kadar (havuz listesi,
  sıranın okunup yazılması, cevap). `keep_unnamed` bellekte, satırdaki dosya sayısıyla.
- **İşaretler:** Drive'a ek işlem yok. M bir okuma ve en çok bir yazma kadar tutulur (yeniden
  adlandırmada bir `os.rename` daha); aynı anda gelen başka bir işaret değişikliği en çok bunu bekler.
  Proje sayısından bağımsız: `arsiv.json` her değişiklikte bir kez okunur, bir kez yazılır, eskisi gibi.
- **Silme:** `arsiv.json` iki kez okunur (eskiden bir): klasör gitmeden önceki okuma güvence için,
  sonraki M'de yazılacak listeyi okumak için — arada başka bir değişiklik olabileceğinden ilki
  yazılamaz. Küçük bir dosya, bir gidiş dönüş. G durdurma (en çok 5 saniye, `halt_project`), işaretler
  ve klasörün silinmesi (projedeki dosya sayısı kadar silme, O(dosya)) boyunca tutulur; o projeye gelen
  basışlar bekler, sonra "Proje yok" alır. Başka projeler beklemez.
- **Döngü:** okumaları aynı, sayısı aynı; yukarıdaki en çok iki gidiş dönüşlük bekleyiş dışında değişmez.

## Ne kaybolabilir, ne bozulabilir

- Diskte hiçbir biçim değişmez; kilitler bellekte, bir süreç bütün basışlara hizmet eder (512'nin
  varsayımı). Sunucu ölürse kilitler gider, dosyalar yerinde.
- Silmede işaret klasörden sonra gider: Drive'da yarıda kalan bir silme arşivli projeyi arşivde bırakır
  (testi var). Klasör gittikten sonra, işaret yazılmadan ölen bir sunucu arşivde hiçbir şeyi göstermeyen
  bir ad bırakır; bugünkü gibi (o adla açılacak proje arşivde doğar).
- Havuzun yazmaları eskisi gibi: önce dosyalar, sonra sıra. Bir dosya ya gizli adıyla yazılmış ya
  adıyla yerinde; yarım dosya hiçbir listede görünmez.
- Gizli dosyalar ile adlandırma arasında ölen bir sunucu havuz klasöründe gizli dosyalar bırakır
  (`Storage`'ın her yarım kaydı gibi): hiçbir listeleme görmez; o projeye bir saat sonra gelen ilk
  yükleme süpürür. Süpürme yalnız havuz klasörüne (`referans/`) bakar; oraya yalnız yüklemeler yazar,
  yani oradaki her gizli dosya bir yüklemenin artığıdır, ve bir saatlik olan hiçbir sürmekte olan
  yüklemenin değildir.

## Sınırlar

- Arşive kaldırma ile aynı projenin silinmesi aynı anda gelirse silinen projenin adı arşivde kalabilir:
  arşive kaldırmanın klasör bakışı ile silmenin klasör silmesi M'nin dışında, ve arşive kaldırmanın
  işareti silmenin işaret düşürmesinden sonra yazılırsa ad kalır. Bu maddeden eski, yazma kaybı değil;
  BACKLOG'a yazıldı: *"Arşive kaldırma ile silme aynı anda gelince silinen projenin işareti
  kalabilir"*.
- Döngü havuzu G'siz okur (GPU beklemesin diye): bir yükleme dosyayı yerine koyup sırayı yazmadan okunursa
  o videonun referansları bir an ada göre sıralanabilir. Bu maddeden eski; BACKLOG'a yazıldı: *"Referans
  yüklenirken başlayan bir video referansları bir an ada göre sıralı okuyabilir"*.
- Baytlar yazıldıktan sonra, kapıdan önce proje yeniden adlandırılırsa yükleme "Proje yok" alır ve
  gizli dosyalar eski adla silinemez, yeni klasörde gizli kalır (`discard` hata atmaz) — o projeye bir
  saat sonra gelen ilk yükleme süpürene kadar. Hiç yükleme gelmezse kalır.

## Ne zaman bitti

- Aynı adla aynı anda iki yükleme iki dosyayı da tutar (`kedi.png`, `kedi-2.png`), ikisi de sırada.
- Bir yüklemenin, çıkarmanın ya da sürüklemenin ortasına düşen yükleme sıranın sonunda ve havuzda orada.
- Arşive kaldırma, geri alma, silme ve yeniden adlandırmanın ortasına düşen başka bir projenin arşive
  kaldırılması kalır.
- Silmenin ortasına düşen basış "Proje yok" alır; işçi boş, koşu başlamadı, klasör silindi.
- Silmenin iki okumasından birinin ardına düşen başka bir projenin arşive kaldırılması kalır.
- Yarıda kalan bir silme arşivli projeyi arşivde bırakır.
- Yükleme süreleri ve baytları kapı tutulmadan okur ve yazar; yalnız adlandırma kapıda.
- Havuzla reddedilen bir yükleme klasörde gizli dosya bırakmaz.
- Bir yükleme kapıda havuz klasöründeki bir saatten eski gizli dosyaları süpürür, gençleri bırakır.
- Yüklemeyi görmemiş bir sekmenin sürüklemesi yüklenen dosyayı sırada yerinde bırakır.
- Silme portu koşuyu silmeden önce durdurur.
- BACKLOG'dan iki iş silindi; iki yeni iş eklendi.
- `python -m pytest queen-editor -q` (bilerek kırmızı iki `test_notebook_clones_its_branch` testi
  dışında) ve `npm test --prefix queen-editor/frontend` yeşil.

## Yalnız Colab'da görülecek

- İki sekmede aynı anda aynı projeye referans yüklemek: iki dosya da havuzda, sıranın sonunda.
- İki sekmede aynı anda iki farklı projeyi arşive kaldırmak: ikisi de arşivde.
- Kuyruk çalışırken başka bir projeyi silmek ve aynı anda bir projeyi yeniden adlandırmak: sıra
  durmadan sürüyor.
