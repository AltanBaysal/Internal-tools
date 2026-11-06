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

**QA'nın buldukları** (c8e0bd23'ten sonra, ikisi de testle kırmızı görüldü):

- *F1 — yükleme silmenin iki yanına düşebiliyordu:* yüklemenin ilk varlık bakışı ve baytları kapının
  dışında; silme klasörü Drive'da onlarca saniyede silerken klasör hâlâ vardı, baytlar silinen
  `referans/`'a yazıldı, silme "klasör boş değil" ile düştü, proje içi boşalmış halde kaldı; yükleme
  sonra kapıyı aldı, projeyi buldu ve 200 verdi — silinen proje yalnız o referansla geri geldi. Kırmızı:
  `DID NOT RAISE ProjectMissing`. Aynı yerde: silme yüklemenin varlık bakışı ile baytları arasına
  düşerse yükleme işletim sisteminin cümlesiyle düşüyordu (`FileNotFoundError … referans`).
- *F2 — havuz kapıda iki kez listeleniyordu:* yükleme (adlar için, sonra cevap için) ve sürükleme;
  havuzdaki her klip iki ffprobe, üç videoda o projeye bir basış 5,79 saniye bekledi (ekranın zaman
  aşımı 10 saniye). Kırmızı: kapıda `5 == 2` ffprobe (yükleme), `6` yerine `3` (sürükleme).

## Ne yapılır

### Referans havuzunun üç kapısı projenin yazma kapısında

`add_references`, `remove_reference`, `save_reference_order` projenin yazma kapısını (**G**,
`plan_store.held`, 512) projeye bakıştan cevaba kadar tutar. Üçü de `plan_store`'u bir parametre olarak
alır (`main.py`'deki `partial`'lar `_plan_store`'u verir); yalnız kapısı için.

Neden G, kendi kilidi değil: havuz proje başına ve G zaten proje başına "okuyup birlikte geri yazan
kapıların" kapısı. Üstelik aynı kapıyı yeniden adlandırma (522) ve artık silme de alıyor; çıkarma ve
sürükleme bir taşımanın ya da silmenin iki yanına düşemez, yüklemenin kapıdaki kısmı da (adlandırma,
sıra). Yüklemenin kapıdan önceki kısmı (baytlar) için aşağıya bakın: taşıma ve silme klasörü tek bir
`os.rename` ile götürür, baytlar ya o adımdan önce yazılıp klasörle gider ya sonra yazılamaz. Ayrı bir
kilit bunu vermezdi ve bir parça daha olurdu.

Varlık bakışı kapının içinde, 522'nin kuralıyla: taşımanın ya da silmenin hangi yanında olduğu ancak
orada kesindir. Sürüklemenin gövde denetimi (`InvalidReferenceOrder`) diske gitmediği için dışarıda.
Cevap (havuzun son hali) kapının içinde kurulur: dışarıda okunsa, kapı bırakılır bırakılmaz gelen bir
taşıma kabul edilmiş bir yüklemeyi 404'le cevaplatırdı (522'nin F1'i). İkinci bir listeleme değil
(QA'nın F2'si): yükleme cevabı kapıdaki tek listeden ve yerine koyduğu dosyalardan, sürükleme tek
listesinden kurar (`references.placed`, yeni sırayla). Kapıda havuzdaki her klip bir kez ffprobe'lanır.

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

Baytlar yazılırken klasör yoksa (`FileNotFoundError`: proje varlık bakışından sonra silindi ya da
yeniden adlandırıldı) yükleme projeye yeniden bakar; proje yoksa "Proje yok" der, varsa hatayı olduğu
gibi bırakır — tahmin değil, sorulmuş cevap.

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
- `delete`: okuma, klasörün **çöpe** taşınması (`Storage.trash_dir`: kökte gizli bir ada tek
  `os.rename`) ve işaretin yazılması M'de — `rename` gibi. Cevabı çöpün adı (yoksa `False`).
  Klasörün asıl silinmesi ayrı: `clear(trash)`, silme kapısını bıraktıktan sonra (aşağıda).
  - Neden çöp (QA'nın F1'i): Drive'da bir klasörü silmek onlarca saniye sürer; o sürede klasöre yazan
    bir yükleme silmeyi "klasör boş değil" ile düşürüyor, içi boşalmış proje kalıyor ve yükleme onu
    bulup geri getiriyordu. Tek bir yeniden adlandırma adı hemen götürür: sonra gelen yazma yolu
    bulamaz, öncesinde yazılan çöpe gider. Silme yarıda kalırsa geride proje değil, hiçbir listenin
    göstermediği gizli bir çöp kalır.
  - M bir rmtree boyunca hiç tutulmaz: yeniden adlandırmanın `store.rename`'i adın kilidinin (**N**)
    içinde çalışır (522), döngü de N'yi bekler; M bir silme boyunca tutulsaydı GPU o kadar boş kalırdı.
  - İşaret çöpe taşımadan sonra yazılır: taşıma düşerse (bir `os.rename`) hiçbir şey değişmemiştir,
    arşivli proje arşivde kalır (reviewer'ın istediği güvence). Okunamayan dosya silmeyi proje henüz
    bütünken durdurur, eskisi gibi. `arsiv.json` bir kez okunur.
- `clear(trash)`: çöpü siler (`delete_dir`) ve kökte bir saatten (`STALE`) eski çöpleri süpürür
  (`Storage.sweep_trash`; zaman çöpün adında, çünkü bir klasörün mtime'ı içinin son değiştiği anı
  söyler, çöpe atıldığı anı değil). Daha genç bir çöp başka bir silmenin olabilir, hâlâ siliniyor
  olabilir; kalır. Hata atmaz: proje zaten gitmiştir, bir hata kullanıcıya olmamış bir başarısızlığı
  söylerdi; silinemeyen çöp gizli kalır, sonraki silme süpürür.
- `Storage.list_dirs` `TEMP_PREFIX`'li klasörleri atlar (`list_files`'ın dosyalar için yaptığı gibi):
  çöp hiçbir listede proje kartı olmaz. Bir proje adı noktayla başlayamadığı için (`name_rules`) hiçbir
  proje bu öneki taşıyamaz.

### Silme projenin yazma kapısında

Yeni port `follow_delete(runner, plan_store, interrupt, sleep, project, remove)` (photo_generation):
G'yi tutarak koşuyu durdurur (`halt_project`, eskisi gibi) ve `remove`'u çalıştırır, cevabını döner.
`delete_project(store, end, name)` projenin götürülmesini (`lambda: store.delete(name)`, çöpe taşıma)
bu porta verir; `halt` portunun yerine. Port döndükten sonra, G bırakılmışken, çöpü `store.clear` ile
siler: G bir Drive silmesi boyunca tutulmaz, o projeye gelen basışlar hemen "Proje yok" alır. 522'nin `follow_rename`'iyle aynı biçim: projeler özelliği kapıyı bilmez,
`main.py` iki özelliği birleştirir. "Önce koşu durur" kuralı artık porttadır; projeler özelliğinin testi
porta silmeyi verdiğini, photo_generation'ın testi durdurmanın silmeden önce olduğunu söyler.

Bir basışın kapı tutuşu **K** (işi yazar, işçiyi alır), silmenin kapı tutuşu **D** (durdurur, siler):

- **K, D'den önce:** iş yazılmış, işçi alınmış; D o koşuyu durdurur, sonra klasörü çöpe taşır. Bugünkü
  "silme koşuyu durdurur" sözü.
- **D, K'den önce:** K geldiğinde klasör yok; kapı projeye kapının içinde bakar, "Proje yok" der, hiçbir
  şey yazmaz, işçiyi almaz.

Bir yüklemenin kapısız kısmı (varlık bakışı, baytlar) için D'nin çöpe taşıması tek adımdır:

- **Baytlar taşımadan önce yazıldı:** klasörle çöpe gider. Yükleme kapıda projeyi bulamaz, "Proje
  yok"; gizli dosyaları eski adla silinemez, çöple birlikte silinir.
- **Baytlar taşımadan sonra yazılacaktı:** yol yok, yazma `FileNotFoundError` verir, yükleme projeye
  yeniden bakar, "Proje yok". Hiçbir şey yazılmaz.
- Silinen klasöre hiçbir yazma düşmez (silme çöpü siler, adı artık kimse bilmez); silme bu yüzden
  "klasör boş değil" ile düşmez, düşse de proje geri gelmez.

## Neden hiçbir yazma kaybolmaz

- **Havuz:** aynı projenin üç kapısının havuzu okuyup yazan kısmı aynı G'de, yani biri ötekinden
  tamamen önce olur; ikinci kapı birincinin yazdığı havuzu ve sırayı okur. Aynı adla ikinci yükleme
  birinciyi görür, `kedi-2.png` olur. Kapının dışında yazılanlar gizli adlarda: hiçbir kapının okuduğu
  havuzda yoklar, adlarını ve sıradaki yerlerini kapıda alırlar.
- **Eski sekmenin sürüklemesi:** adını vermediği dosya sırada yerini korur, düşmez.
- **İşaretler:** dört değişikliğin okuma-yazması aynı M'de; ikinci okuma birincinin yazdığını görür.
  `delete`'in çöpü silmesi M'nin dışında, okuması ve yazması içinde — kaybolan işaret yok.
- **Silme:** basış ya silmeden önce biter ve koşusu durdurulur, ya sonra gelir ve projeyi bulamaz; bir
  yükleme ya projeyle çöpe gider ya hiç yazmaz, ikisinde de "Proje yok" alır.

## Kilitler

Beş kilit: projenin yazma kapısı **G** (`plan_store.held`, proje başına), adın kilidi **N**
(`RunningName`), işçinin kilidi **R** (`PhotoRunner._lock`), izleme kilidi **W** (`QueueWatch`) ve
yeni, işaretlerin kilidi **M** (`DriveProjectStore._lock`).

| Kim | Sıra |
|---|---|
| Kuyruğa iş koyan kapı | G → R (bırakılır) → N (`took`, bırakılır) → W (522'deki gibi) |
| Yeniden adlandırma | G(küçük ad) → G(büyük ad) → N (`moved`) → M (`store.rename`, içinde taşıma) → bırakılır → R (`rename`) |
| Silme (yeni) | G → R (`halt_project`, kısa tutuşlar) → M (okuma, çöpe taşıma, yazma; bırakılır) → G bırakılır → çöp silinir, kilitsiz |
| Havuzun üç kapısı (yeni) | G yalnız; yüklemenin ffprobe'u ve baytları G'den önce, kilitsiz |
| Arşive kaldırma, geri alma (yeni) | M yalnız |
| Döngü | N (tutuşlar); R ayrı; G ve M hiç |

Kenarlar G→R, G→N, G→W, G→M, N→M ve G(x)→G(y) yalnız x < y için. M bir yaprak: içinde hiçbir kilit
alınmaz, tutulurken yalnız bir okuma, en çok bir yazma ve (yeniden adlandırmada ve silmede) bir
`os.rename` var. N'yi tutan hiç kimse G'yi almaz; M'yi tutan hiç kimse bir şey almaz. Döngü yok, kilitlenme yok.

**GPU hiçbir kapıyı beklemez:** döngü G'yi de M'yi de hiç almaz. Havuzu adın kilidinde okur (522), havuzun
kapılarını beklemez. Döngünün tek dolaylı bekleyişi 522'deki gibi N'de süren bir yeniden adlandırma; o
da artık M'yi bekleyebilir, M'yi tutan da en çok bir işaret okuması ve yazmasıdır (başka bir projenin
arşive kaldırılması, geri alınması ya da silinmesi aynı anda gelirse): döngünün bir yeniden adlandırmayı
bekleyişi en çok Drive'da üç gidiş dönüş (okuma, `os.rename`, yazma) uzar. Silmenin çöpü silmesi bu
yüzden hiçbir kilitte değil.

## Maliyet

- **Yükleme (M dosya):** Drive'a eskisine göre ek olarak bir klasör bakışı (kapıdan önceki varlık
  bakışı), dosya başına bir yeniden adlandırma (`os.replace`) — O(M) — ve kapıda süpürme: havuz
  klasörünün bir listesi daha (bir gidiş dönüş; yalnız gizli dosyalar için birer stat, süpürülecek
  her dosya için bir silme — çoğu yüklemede hiç). Baytlar eskisi gibi bir kez
  yazılır. Kapının dışında: yüklenen her klip için bir ffprobe ve M dosyanın yazılması (uzun kısım).
  Kapıda: bir varlık bakışı, süpürme, havuzun **tek** listesi (bir klasör listesi, havuzdaki N klip
  için N ffprobe), M yeniden adlandırma, sıranın okunması ve yazılması; cevap bellekte kurulur. Eskiden
  kapıda 2N + M ffprobe vardı (QA'nın F2'si). Kapıyı bekleyenler (aynı projenin basışları, yeniden
  adlandırması, silmesi, öteki havuz yazmaları) artık yüklemenin baytlarını beklemez; havuzdaki klip
  sayısı kadar ffprobe'u bekler. Başka projeler hiç beklemez.
- **Havuzla reddedilen yükleme:** baytlar yazılıp silinir (dosya başına bir yazma ve bir silme); basışın
  tek başına çiğnediği sınırlar ise baytlar gitmeden söylenir.
- **Sürükleme:** kapıda havuzun tek listesi (N ffprobe), sıranın okunup yazılması; cevap bellekte.
  Eskiden iki liste, 2N ffprobe. `keep_unnamed` bellekte, satırdaki dosya sayısıyla.
- **Çıkarma:** Drive'a ek işlem yok; dosyanın silinmesi, sıranın okunup yazılması, cevap için bir
  liste (zaten tekti).
- **İşaretler:** Drive'a ek işlem yok. M bir okuma ve en çok bir yazma kadar tutulur (yeniden
  adlandırmada bir `os.rename` daha); aynı anda gelen başka bir işaret değişikliği en çok bunu bekler.
  Proje sayısından bağımsız: `arsiv.json` her değişiklikte bir kez okunur, bir kez yazılır, eskisi gibi.
- **Silme:** `arsiv.json` bir kez okunur, en çok bir kez yazılır, eskisi gibi; ek olarak bir
  `os.rename` (çöpe taşıma) ve bir kök listesi (süpürme). G yalnız durdurma (en çok 5 saniye,
  `halt_project`) ve M'deki üç adım boyunca tutulur; o projeye gelen basışlar onu bekler, sonra "Proje
  yok" alır. Çöpün silinmesi (projedeki dosya sayısı kadar silme, O(dosya), Drive'da onlarca saniye)
  hiçbir kilitte değil; kimse onu beklemez, yalnız silme isteğinin cevabı.
- **Döngü:** okumaları aynı, sayısı aynı; yukarıdaki en çok iki gidiş dönüşlük bekleyiş dışında değişmez.

## Ne kaybolabilir, ne bozulabilir

- Diskte hiçbir biçim değişmez; kilitler bellekte, bir süreç bütün basışlara hizmet eder (512'nin
  varsayımı). Sunucu ölürse kilitler gider, dosyalar yerinde.
- Silmede proje tek adımda (çöpe taşıma) gider; Drive'da yarıda kalan bir silme geride proje değil,
  gizli bir çöp bırakır, bir saat sonraki ilk silme süpürür (testi var). Çöpe taşıma düşerse hiçbir şey
  değişmemiştir; arşivli proje arşivde kalır (testi var). Taşıma ile işaretin yazılması arasında ölen
  bir sunucu arşivde hiçbir şeyi göstermeyen bir ad bırakır; bugünkü gibi (o adla açılacak proje arşivde
  doğar).
- Çöp adının içindeki zaman sunucunun saatidir; Drive'ın değil. Süpürme yalnız bir saatten eskileri
  aldığı için saat kayması önemsiz.
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
  saat sonra gelen ilk yükleme süpürene kadar. Hiç yükleme gelmezse kalır. (Silmede bu olmaz: gizli
  dosyalar çöple silinir.)
- Bir URL çöpün adını proje adı olarak verse de proje bulunmaz. Tek kural, `Storage`'da (`_hidden`:
  klasör yolunda `TEMP_PREFIX`'li bir ad), adla klasöre ulaşan her kapıda:
  - `dir_exists` `False` der (`list_dirs`'in onu listelemediği gibi); bütün proje kapıları varlığı
    ona sorar — kuyruğa iş, yükleme ya da export çöpe gidemez (reviewer);
  - `rename_dir` ve `trash_dir` "taşınacak bir şey yok" der (`False`): çöpü adlandırmak "Proje yok"
    alır, çöp proje olarak geri gelmez; çöpü silmek de "Proje yok" alır (QA'nın N1'i);
  - `path` bir yol vermez, `FileNotFoundError` atar; fotoğrafı ve referansı sunan iki yol bunu 404
    olarak cevaplar, olmayan her dosya gibi (QA'nın N2'si).
  Çöpe yalnız kendi işi ulaşır: `trash_dir` onu yapar, `sweep_trash` listeleyerek bulur, `delete_dir`
  ona `trash_dir`'in verdiği adla siler. `name_rules` bu öneki taşıyan bir adı zaten yeni proje adı
  olarak kabul etmez.

## Ne zaman bitti

- Aynı adla aynı anda iki yükleme iki dosyayı da tutar (`kedi.png`, `kedi-2.png`), ikisi de sırada.
- Bir yüklemenin, çıkarmanın ya da sürüklemenin ortasına düşen yükleme sıranın sonunda ve havuzda orada.
- Arşive kaldırma, geri alma, silme ve yeniden adlandırmanın ortasına düşen başka bir projenin arşive
  kaldırılması kalır.
- Silmenin ortasına düşen basış "Proje yok" alır; işçi boş, koşu başlamadı, klasör silindi.
- Silme yavaş giderken araya düşen yükleme projeyi geri getirmez, "Proje yok" alır; silme düşmez.
- Silme, yüklemenin varlık bakışı ile baytları arasına düşerse yükleme "Proje yok" alır.
- Silmenin çöpü silemediği bir silme geride proje bırakmaz (iki listede de yok, ad yeniden açılabilir,
  arşivde doğmaz); çöpe taşıması düşen silme arşivli projeyi arşivde bırakır.
- Silme çöpünü G bırakıldıktan sonra siler ve bir saatten eski çöpleri süpürür, gençleri bırakır.
- Yükleme ve sürükleme kapıda havuzdaki her klibi bir kez ffprobe'lar.
- Çöpün adıyla gelen bir yükleme "Proje yok" alır; `dir_exists` çöpe `False` der.
- Çöpün adıyla gelen yeniden adlandırma ve silme "Proje yok" (404) alır, hiçbir şey taşınmaz; çöpteki
  bir fotoğraf ya da referans sunulmaz (404).
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
- Büyük bir projeyi silerken başka sekmeden ona referans yüklemek: proje gidiyor ve geri gelmiyor,
  yükleme "Proje yok" diyor; Drive'da kökte gizli çöp klasörü silme bitince kalmıyor.
- Kuyruk çalışırken başka bir projeyi silmek ve aynı anda bir projeyi yeniden adlandırmak: sıra
  durmadan sürüyor.
