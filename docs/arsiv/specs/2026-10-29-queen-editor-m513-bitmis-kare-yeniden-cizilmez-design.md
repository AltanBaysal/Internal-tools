# Madde 513 · Bitmiş bir kare yeniden çizilmez — tasarım

**Tarih:** 29 Ekim 2026 · **Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-12),
513 · v11-12 (yama v11.1) · **Dal:** `feat/queen-editor-v11.1` · **Kurallar:** queen-editor
[FOUNDATION](../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kabul koşulu (maddeden)

- Sıra çalışırken proje yeniden adlandırılınca bitmiş hiçbir kare yeniden üretilmiyor ve hiçbir dosyanın
  üstüne yazılmıyor. Sıra kaldığı yerden, yeni addaki klasörde sürüyor.
- Hiçbir basış bitmiş bir katmanı yeniden üretmiyor; yeni bir varyant isteyen yeni bir varyant alıyor.

Kullanıcının kararı maddede yazılı: *"galeri sırada / kayıt bitti demesi lazım değil mi"*. Sırada ya da
bitmiş bir iş yeniden eklenmiyor; kayıt "bitti" dediyse, ondan önce verilmiş bir "yeniden yap" kararı
onu ezemiyor. Sıra bunun için beklemiyor: yeni bir kilit yok, döngü 512'nin yazma kapısını hiç almıyor,
GPU hiçbir kapıyı beklemiyor. Ekrandaki sürüm V11 kalıyor; ekran değişmiyor.

## Hata, görüldüğü gibi

**Yeniden adlandırma** *(511'in QA'sı)*: döngünün her turu planı, kaydı ve galeri sırasını üç ayrı
okumayla, her birinde adı yeniden sorarak okuyordu (`run_loop.snapshot`). Plan eski adla okunduktan
sonra klasör taşınınca kayıt eski adla boş geliyordu: planın bütün işleri borçlu görünüyor, ilki
yeniden çiziliyor ve yeni klasörde, adın kapısında (`named.steady()`) bitmiş dosyanın üstüne
yazılıyordu. Test önce kırmızı görüldü
(`test_a_rename_between_the_loops_reads_never_makes_a_finished_frame_again`, gerçek `Storage` ile
geçici klasörde): üretilen `['ilk', 'ikinci']`, `P0_0.png` yeniden yazıldı.

**Aynı kareye ikinci video basışı** *(512'nin QA'sı)*: `queue_layer` karenin videosu var mı sorusunu
galeriden (`list_frames`), boş yeri yeniden açıp açmayacağını kayıttan (`record.slots`) okuyordu; arada
bir okuma daha var. Döngü kaydı kapının dışında yazdığı için (512'nin sınırı) iki okuma arasına sıranın
"bitti" satırı düşebiliyordu: galeri "video yok", kayıt "video bitti" diyordu; basış bitmiş yeri boş
sayıp üstüne `queued` yazıyor ve video `0_a_V1_0.mp4`'ün üstüne yeniden üretiliyordu. İki testle kırmızı
görüldü: yer hiç yazılmamışken ve yer çıkarılıp (`removed`) yeniden sıraya alınmışken; ikisinde de yer
sonunda `done`'un üstünde `queued`.

**Aynı türden, öteki kapılarda** (bu maddenin okumasından):

- **Tekrar dene, fotoğraf bitmişken:** `retry_frame` karede kırmızı bir şey bulmazsa fotoğrafı
  *"artık olmayan bir fotoğraf"* sayıp `queued` yazıyordu, fotoğraf bitmiş olsa bile. Yarış gerekmiyor:
  bir an geride kalan ekran kırmızı kareyi gösterirken fotoğraf inmiş olabilir. Kırmızı görüldü: fotoğraf
  bir kez daha üretildi.
- **Aynı anda iki Tekrar dene** (`retry_frame` ve `retry_failed`): B kırmızıyı okur; A onu sıraya
  koyar, döngü üretir ve `done` yazar; B ardından `queued` yazar ve bitmiş katman yeniden üretilir. İki
  kapı da kapıyı tutmaz. İkisi de kırmızı görüldü: iki üretim.
- **Çıkarma, sıra o işi bitirirken:** `cancel_generation` borçlu işleri okur ve `removed` yazar;
  `remove_frames` beklenen kartın borçlu katmanlarını galeriden okur ve `removed` yazar. Arada inen
  katmanın üstüne `removed` düşünce dosya diskte kalıyor ama yer boş görünüyordu; sonraki basış yeri
  `removed`'dan yeniden açıyor ve dosyanın üstüne yeniden üretiyordu. İkisi de kırmızı görüldü.
- **Çıkarılıp yeniden istenen, sıra onu çizerken:** sıra bir videoyu çizerken kullanıcı onu çıkarıp
  yeniden ister; basış `removed`'ı okur, video iner, basışın `queued`'u `done`'un üstüne düşer ve video
  yeniden üretilir.
- **Kopyanın tuttuğu dosya** (yarış gerekmez): bir katman, karesinin verdiği sabit adla yeniden
  üretilir (`layer_file`; videonun adı her zaman `<kare>_V1_0.mp4`), ve silinen bir katmanın dosyası onu
  bir kopya kare tutarken diskte kalır (`files_to_unlink`, madde 101). Ses kopyası `C1_P1_0`,
  `P1_0_V1_0.mp4`'ü tutarken `P1_0`'ın videosu silinip `P1_0`'a video basılınca `queue_layer` yeri
  `deleted`'dan açıyor ve döngü yeni videoyu kopyanın videosunun üstüne kaydediyordu. Fotoğrafı
  silinmiş karede Tekrar dene de aynı yolla kopyanın resminin üstüne. İkisi de kırmızı görüldü.

`regenerate`, `queue_references`, `start_batch`, `copy_frames` ve `fix_photo` yeni bir kimlik doğurur
ya da yalnız kapatır; hiçbiri bitmiş bir yeri yeniden açmaz.

## Ne yapılır

### Kararın satırı neyin üstüne verildiğini söyler

Kaydı (`photos.jsonl`) yazan her karar — bir kapının ya da döngünün `record.mark`'ı — o yer için
okuduğu durumu satıra yazar: `record.mark(..., seen=<durum>)` satıra `"from"` koyar; hiç yazılmamış
yer için `null`. `seen` zorunlu ve yalnız adıyla verilir (`*, seen`): `from`'suz bir karar yazılamaz,
unutan kapı hata alır. Kayıt katlanırken (`DrivePhotoRecord`) `from`'lu bir satır ancak yerin o satıra
gelindiğindeki durumu `from`'a eşitse uygulanır; değilse, yazılmış bir prompt'un satırı gibi, üstünden
geçilir. Kural tek yerde, alan bilgisi olarak `queue.applies(now, seen)`'de; kayıt onu çağırır
(`photo_record._applied`). Yerin durumunu okuyan üç katlama aynı satırları okur: `slots`, `list`
(fotoğrafı silinmiş sayan satır da buna tabi) ve `written_prompts`. Adları sayan `max_number` ve
sözleri okuyan `prompts` bütün satırları okumaya devam eder: kararların satırında söz yok, ve her ad
sayılmalı.

`done` hiçbir zaman `from` taşımaz ve her zaman uygulanır: dosyası diskte, onu düşürmek dosyanın
üstünde boş bir yer bırakırdı. Drive'daki eski satırların `from`'u yok ve bugünkü gibi uygulanır;
taşıma yok.

| Kim | Ne yazar | `from` |
|---|---|---|
| döngü | `failed` | işi aldığı açık durum (yok ya da `queued`) — çıkarıldıktan sonra inen hata işi çıkarılmış bırakır |
| `queue_layer` | `queued` | yalnız `removed` ya da `deleted`'ın üstüne |
| `retry_frame`, `retry_failed` | `queued` | `failed`; `retry_frame`'in fotoğraf dalında fotoğrafın okunan durumu |
| `cancel_generation` | `removed` | işin okunan açık durumu |
| `remove_frames`, `remove_layer` | `deleted`, `removed` | yerin okunan durumu |
| `fix_photo` | `deleted` | yerin okunan durumu |

### Kapılar kayda bakarak karar verir

- **Dosya adını başka bir kare tutan yer doludur.** `layers.held_elsewhere(slots, frame, file)`: o
  kareden başka bir karenin dolu bir yeri bu dosyayı adlandırıyor mu. `queue_layer` ve `retry_frame`
  aynı yardımcıyı, döngünün kaydedeceği adla (`layer_file`, `photo_file`) sorar.
- **`queue_layer`:** karenin kendi yeri için kararı galeriden değil, kayıttaki durumdan verir:
  - sırada — `queued`, ya da planda borçlu ve kayıtta hiç yazılmamış (ikinci basış birincisi
    üretilmeden geldiğinde olağan durum): yerin işi yeniden eklenmez ve sayılmaz; ilk varyant odur,
    kalan varyantlar kopya kare olur. Böylece ilk basışın kipi ve süresi karenin işinde kalır: plana
    düşen ikinci bir satır son satır olup onları değiştirirdi. "Planda borçlu" galerinin `owed`'udur,
    planın cevabı, ve planı yalnız kapıdaki kapılar yazar.
  - `done` ya da `failed`, ya da adı başka bir karenin dolu yerinde: yer doludur; seçimle istendiyse
    bütün varyantlar kopya kare olur — yeni varyant, kendi adıyla (bugünkü gibi) — "videosu olmayan
    kareler" ise kare atlanır: galeri okunduktan sonra inmiştir, ya da adı bir kopyanındır.
    Kullanıcı video istediyse bir video alır, hiçbir dosyanın üstüne yazılmaz.
  - `removed` ya da `deleted`: `queued` yazılır, `from` o durum, ve iş eklenir.
  - hiç yazılmamış ve planda borçlu değil: iş eklenir (bugünkü gibi).
- **`retry_frame`:** kırmızı bir şey yoksa fotoğrafı ancak yerinde fotoğraf yoksa (`is_taken` değilse)
  ve başka bir karenin dolu yeri o adı (`photo_file(fid)`) tutmuyorsa yeniden ister; yoksa hiçbir şey
  yazmaz. Ekran Tekrar dene'yi yalnız kırmızı bir katmanda gösteriyor (galerinin kırmızı kartı ve
  katman perdesi, kare sayfasının kırmızı katmanı), bu yüzden bu dal yalnız bir an geride kalmış bir
  basışla çalışır: kırmızı katmanı başka bir basış (Tümünü tekrar dene, ya da başka bir sekme) zaten
  sıraya koymuştur. Kopya kare fotoğrafını tutarken fotoğrafı silinmiş bir karede (madde 101) bu dal
  fotoğrafı yeniden ister ve döngü onu tam o adla, kopyanın resminin üstüne kaydederdi. Kırmızı
  görüldü (`test_tekrar_dene_never_makes_a_photo_over_the_picture_a_copy_still_holds`). Hiçbir şey
  yazmamak, geride kalan basışın istediğini zaten yapılmış bulur: kırmızı katman sıradadır.
- **`remove_layer`:** galeri okunduktan sonra inmiş, kayıtta dolu okunan bir yeri düşürülecekler
  listesine koymaz: o yer zaten kapananlar arasında, `deleted` satırı yeter; uygulanmayacak bir satır
  yazılmaz.
- **`remove_frames`:** beklenen bir kartın katmanı galeri okunduktan sonra inmişse (kayıt `done`
  diyor) ona `removed` yazmaz: çizim kazanır, `remove_frames`'in yorumunun hep söylediği gibi.

`retry_*` ve `cancel_generation` kapıyı almaz; `list_frames`'e dokunulmaz.

### Döngü turunu tek adla okur

`snapshot()` planı, kaydı ve galeri sırasını adın kapısında (`named.steady()`) okur ve okuduğu adı
döndürür; tur o adı kullanır (`named.now()`'ı ayrıca sormaz). Yeniden adlandırma klasörü aynı kapıda
taşıdığı için (`RunningName.moved`) üç okuma ya hep taşımadan önce, ya hep sonra olur. `summary()` da
aynı `snapshot`'ı okur.

## Neden hiçbir bitmiş katman yeniden üretilmez

Döngü bir yeri yalnız turunun okumasında açıkken (yazılmamış ya da `queued`) üretir. Bir yer `done`
olunca onu yeniden açabilecek tek satır, `done`'un üstüne uygulanan bir satırdır. Uygulanan bir satır
ya `from`'suz eski bir satırdır ya `from`'u yerin o anki durumuna eşit bir karardır:

- `from`'suz satırı artık hiçbir kod yazamıyor (`seen` zorunlu); Drive'dakiler eklendikleri yerde
  duruyor, sıraları değişmiyor.
- `from = done` ile yazılan tek karar `deleted`: dosya önce silinir, satır sonra. Yer `deleted`'dan
  yeniden açılırsa üstüne yazılacak bir dosya yoktur.
- `queued` hiçbir zaman `from = done` taşımaz (`queue_layer` yalnız `removed`/`deleted`'dan, Tekrar dene
  `failed`'dan ya da dolu olmayan bir fotoğraftan açar); `removed` da taşımaz (`cancel` açık durumdan,
  `remove_frames` `done`'u atlar, `remove_layer` dolu okuduğu yeri yalnız `deleted`'la kapatır);
  döngünün `failed`'ı açık durumdan.

Yani `done` olmuş bir yeri, dosyasını silen bir silme dışında hiçbir satır yerinden oynatamaz; kim ne
zaman okumuş olursa olsun. Yarış yarış:

- **Galeri ile kayıt arasına inen video:** `queue_layer` artık kayda bakıyor. İniş okumadan önceyse
  kayıt `done` der: yeni bir varyant ya da hiçbir şey. Sonraysa basış ya karenin işini sırada bulur ve
  hiçbir şey yazmaz (`queued`, ya da planda borçlu ve yazılmamış), ya da `queued`'u
  `removed`/`deleted`'dan yazar ve bu satır `done`'un üstüne düşerse üstünden geçilir.
- **Çıkarılıp yeniden istenen, çizilirken:** basışın `queued`'u `from = removed`; video ondan önce inerse
  satır uygulanmaz, sonra inerse `done` yine son sözdür. Bir kez üretilir.
- **İki Tekrar dene:** B'nin `queued`'u `from = failed`; A'nın açtığı ve döngünün bitirdiği yerde durum
  `done`, B'nin satırı uygulanmaz.
- **Tekrar dene, fotoğraf bitmişken ya da bir kopya onun dosyasını tutarken:** yazılmıyor.
- **Kopyanın tuttuğu dosya:** bir yer ancak döngünün kaydedeceği ad başka hiçbir karenin dolu yerinde
  değilse yeniden açılır (`queue_layer`, `retry_frame`); kopya kare dosyayı tuttuğu sürece onu bırakan
  kare o adla bir şey istemez. Kopya da kapı da 512'nin kapısında olduğu için ikisinin arasına yeni bir
  kopya giremez; döngü yeni kare doğurmaz.
- **Çıkarma, iniş sırasında:** `cancel`'ın `removed`'ı açık durumdan; arada inen `done`'un üstüne
  uygulanmaz. `remove_frames` kayıtta `done` gördüğü katmana yazmaz; okumasından sonra inene yazdığı
  satır da açık durumdan.
- **Hata, çıkarıldıktan sonra:** döngünün `failed`'ı işi aldığı durumdan; arada yazılan `removed`'ın
  üstüne uygulanmaz, iş çıkarılmış kalır.
- **Yeniden adlandırma:** turun üç okuması tek adla, taşımanın bir yanında; bitmiş bir iş borçlu
  görünemez. Turun yazmaları eskisi gibi adın kapısında, klasörün o anki adıyla.

### Neye dayanır

Kural satırları dosyadaki sırayla okur, ve bu sıranın ekleme sırası olmasına dayanır: döngü ve kapılar
`photos.jsonl`'e kilitsiz ekliyor. Yerel Linux'ta tek bir `O_APPEND` yazması ötekine karışmaz ve
sırayla durur; Drive'ın FUSE bağlamasında bu henüz denenmedi. 512'nin açtığı BACKLOG maddesi
([*"Fotoğraf kaydına aynı anda iki satır yazılabilir"*](../../queen-editor/BACKLOG.md)) artık 513'ün
de denemesi: satırların sırası da bakılacak.

### Kilitler

Yeni kilit yok. `snapshot` adın kilidini (`RunningName`, yeniden girilebilir) üç okuma boyunca tutar ve
içinde başka kilit almaz; döngü 512'nin yazma kapısını hiç almaz. Kapıların kilitleri değişmedi:
yazma kapısını tutan kapılar adın kilidini almaz, `run_queue` kapının dışında, işçinin kilidi
(`PhotoRunner._lock`) içinde hiçbir kilit alınmaz. Kilitler arasında döngü yok, kilitlenme yok.

## Maliyet

- **Basış başına:** Drive'a ek okuma ya da yazma yok; kapılar eskisi kadar okuyup yazıyor
  (`cancel_generation` kaydı bir kez okuyup hem borç hem durum için kullanıyor). `held_elsewhere`
  aynı okumada, bellekte, bütün yerlere bakar: `retry_frame`'de bir kez, `queue_layer`'da kapsamdaki
  her kare için bir kez — kare sayısının karesi kadar adım, yüzlerce karede önemsiz. Satır başına birkaç
  bayt (`"from": …`). Drive'a giden işlem sayısı proje, kare ve dosya sayısından bağımsız: O(1).
- **Kaydın katlanması:** yine bellekte, satır sayısı kadar adım; satır başına bir karşılaştırma daha.
  `slots`, `list` ve `written_prompts` kaydı eskisi gibi birer kez yürür; dosya `FileCache`'ten gelir.
- **Döngü:** turun okumaları değişmedi; hiçbir şeyi beklemez. Yeniden adlandırma en çok bir
  `snapshot`'ı (üç okuma, Drive'da birkaç gidiş dönüş) bekler — bugün de bir kaydın yazılmasını bekliyor.

## Ne kaybolabilir, ne bozulabilir

- Dosyanın biçimi aynı, yalnız bir alan eklendi; eski satırlar aynı okunur. Kayıt yine yalnız
  eklenir: üstünden geçilen satır da diskte kalır, ne olduğunu söyler.
- Üstünden geçilen bir karar sessizce düşmez: kararı veren basış, gördüğü duruma göre doğru cevabı
  vermiştir; yer o arada daha yeni bir söz almıştır (`done`, ya da bir çıkarma).
- Yarım yazılmış son satır eskisi gibi atlanır.
- Bu kodu tanımayan eski bir sürüm aynı kaydı okursa `from`'u bilmez ve satırları eskisi gibi
  uygular; Sınırlar'a bakın.

## Sınırlar

- Galeri okunduktan sonra videosu inen kareye seçimle basılan video yeni bir varyant (kopya kare) olur
  — basış kayıtta videoyu görmüştür. İnişten önce okuyan basış karenin kendi işini sırada bulur ve
  yeniden eklemez; o yer bir kez üretilir.
- Çıkarılıp başka bir kipte yeniden istenen video çizilirken inerse, inen video kalır ve yeni istek onu
  yeniden üretmez: yer bitmiştir. Başka kip isteyen yeni bir varyant ister.
- Çıkarılan beklenen bir kartın fotoğrafı o sırada inerse kart galeride kalır ve sıra dosyasında
  yeri olmadığı için tepeye çıkar (çizim kazanır, bugünkü gibi).
- Yeniden adlandırma, turun render'dan önceki öteki okumalarına (karenin sözleri, altındaki fotoğraf,
  yazılmış prompt) düşerse video boş prompt'la üretilebilir; bitmiş bir şeyin yeniden üretilmesi
  değil. BACKLOG: *"Yeniden adlandırma bir videoyu boş prompt'la ürettirebilir"*.
- Aynı anda bir basış ve bir yeniden adlandırma hâlâ bir işi bekletebilir (511'in BACKLOG maddesi).
- 513'ten eski bir commit (örneğin bu dal birleşmeden `main`'i klonlayan defter) 513'ün yazdığı bir
  projeyi açarsa, 513'ün üstünden geçtiği satırları uygular ve bir katmanı yeniden üretebilir; bu
  yüzden kullanıcının denemesi birleşmeye kadar bu dalla yapılır.
- Döngünün videodan çıkardığı ilk kareyi kopyanın tuttuğu fotoğraf adına kaydetmesi bu maddenin dışında
  kaldı: BACKLOG, *"Silinmiş fotoğraftan video, ve kopya karenin fotoğrafının üstüne yazılması"*. Ses
  kopyasının kendi sesinin adı kaynağın sesinin adıyla aynı çıkabiliyor; 514 MMAudio'yu kaldırdığı için
  dokunulmadı.

## Ne zaman bitti

- `test_made_once.py`:
  - turun plan ve kayıt okumaları arasına düşen yeniden adlandırmada bitmiş kare yeniden üretilmiyor,
    `P0_0.png` aynı kalıyor, sıra yeni klasörde bitiyor;
  - ilk video inerken gelen ikinci basışta, yer yazılmamışken de `removed`'dan yeniden açılmışken de,
    karenin kendi videosu bir kez iniyor ve `done` kalıyor;
  - sırada videosu olan kareye video basışı hiçbir şey eklemiyor; birincisi üretilmeden gelen ikinci
    basış (iki varyant) karenin kendi işini yeniden eklemiyor, yalnız eklediğini sayıyor (`1`), ve
    karenin işinde ilk basışın kipi kalıyor;
  - videosunu bir ses kopyasının tuttuğu, kendi videosu silinmiş kareye video basışı `P1_0_V1_0.mp4`'ün
    üstüne kaydetmiyor: seçimle yeni varyantlar kendi adlarıyla, "videosu olmayan kareler"de hiçbir şey;
  - fotoğrafı bitmiş kareye, ya da fotoğrafı silinmiş ama dosyasını bir kopyanın tuttuğu kareye Tekrar
    dene hiçbir şey üretmiyor; aynı anda iki Tekrar dene (tek kare ve hepsi) bir kez üretiyor;
  - sıra temizlenirken ve beklenen kare silinirken inen fotoğraf `done` kalıyor, dosya silinmiyor;
  - katlama: başka bir durumun üstüne verilmiş karar geçilmiyor, aynı durumun üstüne verilen uygulanıyor,
    `from`'suz satır eskisi gibi uygulanıyor, `done` her zaman uygulanıyor, çıkarmadan sonra inen hata
    geçiliyor; `list` ve `written_prompts` de geçilen satırı saymıyor.
- `python -m pytest queen-editor -q` ve `npm test --prefix queen-editor/frontend` yeşil. Ekran
  değişmediği için `dist` yeniden kurulmuyor.

## Yalnız Colab'da görülecek

- Gerçek Drive'da sıra çalışırken yeniden adlandırılan projede bitmiş karelerin yeniden çizilmemesi.
- `photos.jsonl`'e aynı anda eklenen satırların eklendikleri sırada durması (BACKLOG maddesi).
