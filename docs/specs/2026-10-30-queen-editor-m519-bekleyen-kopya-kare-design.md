# Madde 519 · Bekleyen kopya kare doğru görünür ve yerinde kalır — tasarım

**Tarih:** 30 Ekim 2026 · **Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-18),
519 · v11-18 (yama v11.1) · **Dal:** `feat/queen-editor-v11.1` · **Plan:**
[2026-10-30-queen-editor-m519-bekleyen-kopya-kare-plan.md](../plans/2026-10-30-queen-editor-m519-bekleyen-kopya-kare-plan.md)
· **Kurallar:** queen-editor [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kabul koşulu (maddeden)

Videosunu bekleyen bir kopya kare, kare sayfasında kaynağın fotoğrafını ve "kaynak foto · kopya kare"
etiketini gösteriyor. Fotoğraf sekmesinden "Kuyruktan çıkar" ile çıkarılınca galerideki yerinde kalıyor,
sona atlamıyor.

Kullanıcı — *"bu hatalarıda çöz istersen"*. Madde BACKLOG'un iki işi (516'nın coder'ı): *"Sıradaki kopya
kare kaynağının fotoğrafı yerine "bekliyor" gösteriyor"* ve *"Sıradaki kopya kare "Kuyruktan çıkar"dan
sonra geri geliyor"*. 511–518'e dokunulmaz.

## Bugün

Kopya kare ikinci bir video varyantından doğar (`queue_layer`): kaynağın fotoğrafı ona kayıtta taşınır
(`copy_frame.carry_layers`), planlanmaz; planda yalnız kopyanın video işi var.

- **Durum** (`list_frames`): kartın durumu, onu açan işin durumu. Kopyanın kartını açan iş video işi,
  sırada olduğu için durum `pending`. Galeri ve kare sayfası "fotoğraf burada mı" sorusunu bu durumdan
  okuyor (`PhotoDetail`'in `produced`'ı, galeri karosunun `state === "done"`'ı). Bu yüzden kare sayfasında
  kaynağın resmi yerine "bekliyor" kutusu, galeride kesik çizgili boş bir karo çıkıyor; etiket hiç
  görünmüyor. Ekranın testleri kopya kareyi `done` sayıyor (`QUEUED_COPY`), sunucuyla uyuşmuyor.
- **Fotoğraf sekmesinin "Kuyruktan çıkar"ı** `remove_frames`'e gidiyor. Durum `pending` olduğu için kopya
  "üretilmemiş" sayılıyor: video işine `removed` yazılıyor ve kare galeri sırasından çıkıyor. Ama kopya
  kaynağın fotoğrafını hâlâ tuttuğu için `list_frames`'in "tutulan" kuralı onu bir sonraki okumada
  bitmiş bir ikiz olarak geri getiriyor; sırada yeri olmadığı için galerinin en üstüne çıkıyor
  (`apply_order`). Ekran da kareyi gitti sanıp komşusuna geçiyor.

Bugünkü kodla geçici bir deneme ikisini doğruladı, ve aynı yolda üçüncüsünü buldu:

- **Silinen kare, videosu sıradayken geri geliyor.** Kendi fotoğrafı inmiş, videosu sırada bir kare
  silinince (fotoğraf sekmesinin "Sil"i ya da seçim çubuğu), `remove_frames` yalnız dolu hücreleri
  kapatıyor; sıradaki video işi açık kalıyor. Açık iş kartı galeride tuttuğu için (madde 294) kare, artık
  fotoğrafı olmayan bir bekleyen kart olarak galerinin en üstünde beliriyor. Madde 295'in kuralı
  (*"bir kartı çıkarmak ona borçlu her işi kapatır"*) yalnız üretilmemiş kareye uygulanıyordu.

## Ne yapılır

### Hangi yer karar verir: sunucunun durumu

İki yol vardı: ekran kopyanın fotoğraf katmanını kendisi okur (`layers.photo`), ya da sunucunun durumu
kopya için doğru cevabı verir. **Sunucu**, çünkü:

- "Bu kartın resmi burada mı" sorusunu durumdan okuyan yalnız kare sayfası değil: galeri karosu, seçim
  çubuğu (Kopyala, Sil'in hangi pencereyi açacağı), video panelinin kapsamı (`LayerPanel`), Bağlantılı
  modun hedefi (ekranda `noTarget`, sunucuda `production_mode.frame_after`), ve sunucuda `queue_layer`,
  `copy_frames`, `regenerate`, `remove_frames`. Ekranda okunan bir istisna bunların her birine ayrı ayrı
  yazılırdı; kural ekrana kopyalanmış olurdu (FOUNDATION, karar 4).
- Kopya, doğduğu anda kaynağın resmini tutuyor; ilk katmanı o resim. Durum bunu söyleyince kopya, kendi
  fotoğrafı inmiş ve videosu sırada olan bir kareyle aynı şekilde davranıyor — her kapı onu zaten
  tanıyor.

**`list_frames`:** fotoğraf hücresinde inmiş bir resim tutan kartın durumu `done`; tutmayanın durumu
bugünkü gibi onu açan işinki. Plandaki fotoğraf işiyle açılan kartta bu zaten aynı cevap (işin durumu
hücrenin durumu); değişen yalnız resmi taşınmış kartlar: videosunu (ya da 514'ten önce kalmış sesini)
bekleyen kopya, ve videosu kırmızı olan kopya. Videodan doğmuş, resmi olmayan kart değişmez. Kartın
satırı, sözleri, borcu (`owed`), dosya adı değişmez.

Bunun ekrandaki sonuçları — her biri, kendi fotoğrafı olan karenin bugünkü davranışı:

- Kare sayfası kaynağın resmini ve "kaynak foto · kopya kare" etiketini gösterir; etiketin yanında
  "video kuyrukta". Ayrıntılardaki satır "Dosya adı (planlanan)" değil "Dosya adı".
- Galeri karosu resmi gösterir, köşesinde video bekliyor etiketiyle.
- Seçim çubuğu kopyayı üretilmiş sayar: Kopyala onu ikizler (`copy_frames`; yalnız resmi, video henüz
  yok, ikizin bekleyen işi yok), Sil *"1 kare silinsin mi?"* penceresini açar. Silmek kopyayı ve bekleyen
  videosunu birlikte götürür (aşağıda); resim kaynağın olduğu için diskten hiçbir şey gitmez.
- Kare sayfasının fotoğraf sekmesi "Yeniden üret — yeni kare"yi gösterir; sunucu da kabul eder
  (`regenerate` kaynağın `done` olmasını istiyor): kopyanın resminden yeni bir kare doğar.
- Bağlantılı modda bekleyen kopya bir hedef olabilir: resmi orada.
- Videosu kırmızı kopya kırmızı bir kutu değil, resmi ve üstünde Tekrar dene ile görünür.

### `queue_layer`'ın kapsamı değişmez

`frames_in_scope` bir karenin üstüne iş asılabilir mi diye bugün `status == "done"`'a bakıyor; kuralın
kendisi madde 292'nin: *"yalnız oturmuş kart bir şey taşıyabilir — onu açan katman inmiş"*. Durum artık
kopyada bunu söylemiyor: resmi orada, ama doğduğu katman (video) hâlâ sırada ya da kırmızı. Bakılmasa,
iki varyantlı ikinci bir video basışı ilk basışın bekleyen kopyasına da kendi kopyasını verirdi — her
basışta kopyalar çoğalırdı; 512 ve 513'ün iki testi bunu kırmızıyla gösterdi. Bu yüzden kapsam onu açan
katmanı da sorar: satırın okunduğu plan işinin katmanı (`queue.type_of(frame)`) borçluysa ya da kırmızıysa
kart oturmamıştır. Kendi fotoğrafıyla açılan kartta bu katman fotoğraf, ve durumu `done` iken ne borçlu ne
kırmızı: o kartlar için hiçbir şey değişmez. Bekleyen ve videosu kırmızı kopya, bugünkü gibi kapsam dışı.

Satırın `type`'ı, `list_frames`'in `card()`'ının satıra yaydığı açan plan işinin alanı. `type`'ı olmayan
satır — eski bir fotoğraf işi, ya da kendisi için henüz bir şey planlanmamış, kayıttan okunan bir Kopyala
ikizi — fotoğrafla açılmış sayılır ve kapsamdadır. İkize bir video planlanınca onu o iş açar, bir varyant
kopyasını açtığı gibi; videosu beklerken ikinci basışta kendi kopyasını almaz — 519'dan önce de öyleydi.

Ekranın video paneli kapsamı önizleme olarak sayar (`LayerPanel`'in `eligible`'ı). Bugün yalnız
`status === "done"`'a bakıyor; durum değişince bekleyen ve videosu kırmızı kopya "Videosu olmayan kareler"
ve "Seçili kareler" sayılarına girerdi, sunucu ise onlara iş vermez. Önizleme aynı soruyu sorar: `done`, ve
açan katman (`type`, yoksa fotoğraf) ne `owed`'da ne `failed`'da (reviewer).

### Fotoğraf sekmesinin "Kuyruktan çıkar"ı kopyada işi çıkarır

`PhotoDetail`: fotoğraf sekmesinde, resmi kaynağın olan (`produced && !ownsItsPhoto`) ve kendisine bir şey
borçlu (`awaited`) karede düğme `remove_frames` yerine 516'nın kapısına gider:
`handleDequeue(frame.owed[0])`. Kopyanın borçlu olabileceği katmanlar resmin üstündekiler; en alttaki
(`owed[0]`), kapının `falls_with`'iyle üstünde asılı olanı da götürür (video ve sesi). Etiket "Kuyruktan
çıkar" kalır, basış sormaz (bitmiş hiçbir şey gitmez). Kare galeride kaldığı için sayfa karede kalır ve
Foto sekmesi açık kalır. Reddin başlığı *"Video kuyruktan çıkarılamadı"*, 516'daki gibi.

Bekleyen katmanlardan biri çizilirken (`running` bu kareyi tutuyor) düğme kapalı: iş artık beklemiyor,
katmanın kendi sekmesi onu çizilirken gösteriyor ve orada da düğme yok, ve basış ancak inen katmanın
ezeceği bir satır yazabilirdi (reviewer).

`handleDequeue` çıkaracağı katmanı parametre olarak alır; bekleyen katmanın sekmesi `open`'ı verir.
Başka hiçbir düğme değişmez: kendi resmi olan karenin "Sil"i önce sorar, fotoğrafı sırada olan karenin
"Kuyruktan çıkar"ı ve kırmızı katmanın "Kareyi sil"i `remove_frames`'e gider.

Çıkarıldıktan sonra kopya, kaynağın resmini tutan bitmiş bir ikizdir; planda onu açan iş kalmadığı için
`list_frames`'in "tutulan" yolundan gelir. Kapı sıra dosyasına dokunmadığı için yeri değişmez.

516'nın spec'i fotoğraf sekmesinin bu düğmesi için *"değişmez"* demişti ve geri gelmeyi BACKLOG'a
yazmıştı; bu madde onu kapatır.

### `remove_frames`: silinen kare bekleyen işlerini de götürür

Üretilmiş bir kare silinince, dolu hücreleri bugünkü gibi kapanır ve dosyaları (başka kare tutmuyorsa)
silinir; ek olarak sıranın ona hâlâ borçlu olduğu işlere `removed` yazılır — üretilmemiş karede bugün
yazıldığı gibi, aynı döngüyle, 513'ün `seen`'iyle. Galeri okunduktan sonra inmiş bir katman kapanan
hücreler arasındadır ve `deleted` satırını alır; ona ayrıca `removed` yazılmaz. Hiç üretilmemiş ve hiçbir
şey borçlu olmayan kartın fotoğraf hücresine `removed` yazılması bugünkü gibi yalnız üretilmemiş karede.

Bu, seçim çubuğunun bekleyen kopyayı silmesi için gerekli (durumu artık `done`): yoksa kopyanın açık video
işi onu resimsiz bir bekleyen kart olarak geri getirirdi. Aynı değişiklik yukarıdaki üçüncü hatayı da
kapatır.

### Katmanı üretilen kare silinmez

QA (30 Ekim) aynı sözün bir deliğini buldu — *silinen kare bir daha gelmez*: kendi videosu çizilirken
silinen kare (fotoğraf sekmesinin Sil'i, onay): fotoğraf `deleted` ve diskten gitti, video `removed`
(`from` boş), ardından çizim `done` yazdı — 513'e göre inen katman her zaman kazanır — ve kare galerinin
en üstüne videosuyla ve olmayan bir resimle (404) döndü. Seçim çubuğunun Sil'i de, bekleyen kopya da aynı
yoldan geçiyor.

İnen katman kazanmaya devam eder; değişen, silmenin o ana düşmemesi. **İşçinin bir katmanını yaptığı kare
silinemez:**

- **Sunucu, `remove_frames`:** işçi (`PhotoRunner`) artık kapının ilk parametresi, `cancel_generation`'daki
  gibi. Plan kilidinde, galeri okunduktan sonra işçinin durumuna bakılır: bu projede çalışıyorsa, elindeki
  kare (`current.id`) ve aynı çizimdeki öteki kareler (`batch`, madde 411) yapılıyor demektir. İstenen
  karelerden biri onlardansa basışın tamamı `Busy` ile reddedilir — *"Kare şu an üretiliyor, bitince
  silinebilir: P5_0"*, 409 — ve hiçbir şey silinmez, yazılmaz. **Neden sunucuda da:** ajan ve bir yoklama
  geride kalan ekran oraya ekranın düğmesinden geçmeden varıyor. **Neden mümkün:** işçinin durumu bellekte;
  okumak disk ya da ağ istemiyor, ve işçi zaten pek çok kapıya böyle veriliyor. **Neden atlamak değil
  reddetmek:** atlanırsa cevap öteki karelerin gittiğini söylerken kullanıcının kastettiği kare kalırdı.
  Prompt yazılırken `current` boş: o tur bir şey yapmıyor, ve sonraki tur çizmeden önce kaydı yeniden
  okuyor, silinen işi görmüyor.
- **Kare sayfası:** kareyi ya da bekleyen işlerini götüren her düğme — fotoğraf sekmesinin Sil / Kuyruktan
  çıkar / Kareyi sil'i, dolu ve kırmızı katman sekmelerinin Kareyi sil'i — işçi bu karenin bir katmanını
  yaparken (`running`) kapalı (`binOff`).
- **Seçim çubuğu:** seçimde işçinin yaptığı bir kare varsa Sil kapalı ve yanında *"Üretilen kare bitince
  silinebilir."* yazar. Seçim dairesi yalnız fotoğraf çizilirken kalkıyor; video çizilirken kare
  seçilebiliyor, ve çizim başlamadan yapılmış bir seçim kalıyor — bu yüzden düğme seçime bakıyor.

### Kaynağı diskte olmayan katman çizilmez

Yukarıdaki güvenli sonuç bugüne kadar üreticinin kendi denetimine dayanıyordu: döngü (`run_loop._source_for`)
kayıtta adı geçen kaynak dosya diskte yoksa üreticiye boş bayt veriyordu, ve H3'ün grafiği PNG olmayan
girdiyi reddettiği için iş düşüyordu. Bu artık döngünün kendi kuralı (reviewer): kaynak okunamazsa
`MissingSource` kare düzeyinde düşer, `MissingEndFrame`'in yaptığı gibi — o kare kırmızı olur, sıra sürer.
Prompt yazımı da aynı kaynağı okuduğu için, resmi olmayan bir video için prompt da yazılmaz.

## Maliyet

Proje, sohbet ve dosya sayısından bağımsız; her basış bir istek.

| İş | Ne yapar |
|---|---|
| Galeri (`list_frames`) | değişmez: aynı okumalar; kart başına zaten okunmuş hücrelerden bir sözlük bakışı. |
| Kuyruğa ekle (`queue_layer`) | değişmez: kapsam, galerinin zaten okunmuş satırına bir soru daha sorar. |
| Fotoğraf sekmesinin "Kuyruktan çıkar"ı, kopyada | bir `POST …/layers/video/dequeue`: plan kilidinde galeri bir kez, hücreler bir kez okunur; borçlu katman başına `photos.jsonl`'e bir satır. Sıra dosyası yazılmaz, dosya silinmez. Cevaptan sonra hook galeriyi bir kez okur. Eskisi: aynı okumalar, bir satır, artı sıra dosyasının bir yazması — ve kare geri geliyordu. |
| Kare silme (`remove_frames`) | aynı okumalar ve yazmalar; üretilmiş karede borçlu iş başına bir satır fazla; işçinin durumuna bir bakış (bellek). Reddedilen basış galeriyi bir kez okur, hiçbir şey yazmaz. |

## Ne kaybolabilir, ne bozulabilir

- **Çıkarma** yalnız `removed` satırı yazar, `seen`'le: sıra o arada videoyu indirdiyse satır geçersiz
  kalır, video yerinde durur (513, 516). Dosya silinmez, dolu hücre kapanmaz, sıra dosyası yazılmaz.
- **Silme:** her satır okunduğu durumun üstüne yazılır. Galeri okunduktan sonra inen katman kapanan
  hücreler arasındadır, bugünkü gibi silinir; `removed` satırı almaz. Aynı anda gelen Kuyruğa ekle ile
  silme plan kilidinde sıraya girer (512).
- **Durum değişikliği hiçbir şey yazmaz;** yalnız okunan cevabı değiştirir. Hiçbir kapı artık daha fazla
  şey silmiyor: kopyanın resmi kaynağın olduğu için `files_to_unlink` onu diskte bırakır (madde 101).
- **Çizilmeye başlamış bir videoya basış:** ekran sıranın çizdiğini gördüyse fotoğraf sekmesinin düğmesi
  kapalı. Görmediyse (son yoklamadan sonra başladıysa) basış `removed` yazar, çizim bitince `done` onu ezer
  ve video yine gelir — 516'nın belgelediği sınır; hiçbir şey kaybolmaz.
- **Çizilen karenin silinmesi:** sunucu reddeder. Kalan aralık, döngünün kaydı okuduğu an ile elindeki
  kareyi bildirdiği an arası (arada yalnız prompt kaydına bir bakış var); aynı çizimdeki öteki kareler için
  biraz daha uzun, çünkü onlar ancak çizimin kendi raporuyla bildiriliyor. Silme oraya düşerse sonuç
  karenin türüne bağlı:
  - **Kendi fotoğrafı olan kare, videosu sırada:** silme fotoğrafı döngü okumadan diskten götürür. Döngü
    kaynağı okuyunca dosyayı bulamaz ve iş kare düzeyinde düşer (`MissingSource`, *"Kaynak dosya yok:
    0_a.png"*, aşağıda); `failed` satırı (`from` boş) silmenin kapattığı bir yuvaya düşer ve 513'e göre
    geçersiz sayılır. Kare silinmiş kalır, eksik resim yok.
  - **Kopya (resmi kaynağın) ya da fotoğrafını bekleyen kare:** resim diskte kalır ya da hiç yoktu; çizim
    iner ve silmeyi geri alır (513: inen katman kazanır). Resim sağlam, kare yerinde.
  Kapatmak döngüyü kapıların kilidine almayı isterdi; 513 GPU'yu o kilidin dışında tuttu, bu madde de
  tutuyor.

## Sınırlar

- Fotoğraf sekmesinde, videosu beklerken kopyayı bütünüyle silen bir düğme yok: önce "Kuyruktan çıkar",
  sonra "Kareyi sil" — ya da seçim çubuğunun Sil'i.
- Seçim çubuğunda bekleyen kopya için ayrı bir "kuyruktan çıkar" yok; madde fotoğraf sekmesinin düğmesini
  istiyor. Çubuk kopyayı, kendi fotoğrafı olan kare gibi, siler.

## Ne zaman bitti

- **Sunucu:**
  - videosunu bekleyen kopya `done`, dosyası kaynağın resmi, `layers` `{photo}`, `owed` `["video"]`
    (bugün kırmızı);
  - videosu kırmızı kopya `done`, `failed` `["video"]` (bugün kırmızı);
  - iki varyantlı "videosu olmayan kareler" basışı bekleyen kopyaya kendi kopyasını vermez; 512'nin
    (`test_two_video_presses_at_once_give_their_variants_their_own_frames`) ve 513'ün
    (`test_a_second_video_press_before_the_first_is_made_does_not_add_the_frames_own_job_again`) testleri
    değişmeden geçer (kapsam sorusu olmadan kırmızı);
  - kendisi için bir şey planlanmamış Kopyala ikizi kapsamda; videosu planlanmış ikiz ikinci basışta kendi
    kopyasını almaz;
  - kopyanın videosu çıkarılınca sıra dosyası değişmez, kopya yerinde, `done`, borcu boş;
  - videosu sırada kendi fotoğraflı kare silinince video `removed`, borç boş, kare geri gelmez (bugün
    kırmızı);
  - bekleyen kopya silinince video `removed`, diskten hiçbir şey gitmez, kopya geri gelmez (bugün kırmızı);
  - işçinin bir katmanını yaptığı kare (elindeki ya da çizimindeki) silinmez: `Busy`, hiçbir şey silinmez,
    hiçbir satır yazılmaz, sıra dosyası aynı; kapı 409 ve kareyi adlandırır; başka bir kare çizilirken ya da
    başka bir projenin koşusu sürerken silme geçer (bugün kırmızı);
  - kaydın adını verdiği fotoğrafı diskte olmayan video çizilmez: üretici çağrılmaz, video `failed`,
    hatası *"Kaynak dosya yok: 0_a.png"* (bugün kırmızı: üretici boş baytla çağrılıyordu);
  - `remove_frames`'in, `dequeue_layer`'ın ve galerinin bütün eski testleri işçiyle çağrılıp geçer.
- **Ekran:**
  - bekleyen kopyanın fotoğraf sekmesinde "Kuyruktan çıkar" → `dequeueLayer("düğün", ["P0_1"], "video")`;
    `removeFrames` çağrılmaz, onay kutusu yok, sayfa karede ve Foto sekmesinde kalır (bugün kırmızı);
  - ret: *"Video kuyruktan çıkarılamadı"* ve sunucunun cümlesi;
  - kopyanın videosu çizilirken fotoğraf sekmesinin "Kuyruktan çıkar"ı kapalı (bugün kırmızı);
  - kendi videosu çizilen karenin fotoğraf sekmesinde Sil kapalı (bugün kırmızı);
  - seçim çubuğunda, seçimde çizilen bir kare varken Sil kapalı ve *"Üretilen kare bitince silinebilir."*;
    yalnız öteki kareler seçiliyken açık (bugün kırmızı);
  - video paneli bekleyen ve videosu kırmızı kopyayı ne "Videosu olmayan kareler"de ne seçimde sayar
    (bugün kırmızı);
  - `QUEUED_COPY` sunucunun cevabı (`done`); kopyanın resmini ve etiketini gösteren testler olduğu gibi
    geçer.
- `dist` yeniden derlendi; iki queen-editor takımı yeşil
  (`test_notebook_clones_its_branch.py`'nin iki testi kullanıcının Colab denemesi için kasten kırmızı).

## Aynı değişiklikte

BACKLOG'dan iki iş silinir: *"Sıradaki kopya kare kaynağının fotoğrafı yerine "bekliyor" gösteriyor"* ve
*"Sıradaki kopya kare "Kuyruktan çıkar"dan sonra geri geliyor"*. Bir iş girer (reviewer): *"Aynı kimlik iki
kez gelince kare iki kez sayılıyor"* — `checked` tekrar eden kimliği ayıklamıyor. QA'dan iki iş, ikisi de
519'dan eski: *"Katmanı kırmızı karonun seçim dairesine basılamıyor"* ve *"Video paneli zaten sırada olan
videoyu da sayıyor"*.
