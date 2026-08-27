# QueenAgent v6 Yol Haritası — akış

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [karar defteri](../../2026-08-27-queenagent-skill-kararlari.md) ve
[akış tasarımı](../../2026-08-27-queenagent-akis-tasarimi.md). Bu belge onlardan türer; ters yön yok.
**Numaralar** v5.5'ten devam eder (94'te bitti), yani **95'ten** başlar.

---

## Neden bu koşu var

Madde 94 skilleri bire indirdi, ve geriye kalan tek metin promptu **kuran** metin. Ama kullanıcı
oraya gelene kadar yolun tamamı metinsiz: karakterlerin, mekânların ve sahnelerin nasıl toplanacağını
söyleyen bir şey yok, ve kullanıcı her seferinde boş sayfadan başlıyor.

Bu koşu o yolu getiriyor — **Start a scenario** — ve yolun altındaki üç zemini düzeltiyor: promptun
kendi sırası, şemanın nerede durduğu, ve modelin yazma yetkisinin nasıl sorulduğu.

## Nasıl koşulur

Madde madde. Bir madde iki turda biter — önce testler kırmızı commit'lenir, sonra kod yeşile
döndürülür — sonra sıradaki konuşulur.

**Koşma sırası:** 95 → 96 → 97 → 98 → 99 → 100 → 101. Sona kalan 101, çünkü şartı öteki altısı:
akış şemayı araçtan okuyor, planını `edit` kipinde yazıyor, denemeyi kendi aracıyla kuruyor.

## Maddeler

### Madde 95 — Promptun sırası düzelir, kişi sayısı yerine oturur

- **Ne çalışır:** iki karakterli bir karede iki tarif yan yana duruyor ve birbirine bulaşıyor —
  birinin saçı ötekinin üstüne geçiyor. Ayrıca kişi sayısı karakterin kendi tanımında taşınıyor,
  yani aynı karakter tek başınayken de "bir kız" diyor, biriyleyken de. Sıra değişir: **ana karakter
  promptun başında**, geri kalan herkes kameradan sonra. Kişi sayısı karenin kendi alanından
  geliyor ve kalite etiketlerinden hemen sonra bir kez yazılıyor.
- **Nasıl görülür:** iki karakterli bir kare kurulup prompt üretildiğinde ana karakter başta, ikinci
  kişi sonda çıkıyor, ve kişi sayısı bir kez yazıyor. Kıyafet her zaman sahibinin yanında duruyor.
- **Kararı verilmiş** *(K1–K8)*: ana karakter, karenin karakter listesinde **en öne yazılan**
  isimdir — şemaya ayrı bir alan girmiyor, çünkü sıra zaten bilgi taşıyor. Sayıyı **model yazar, kod
  yerleştirir**; kod sayamaz, çünkü bir karakterin ne olduğu hiçbir alanda durmuyor.
- **Bilerek kabul edilen:** üç kişilik bir karede ikinci ve üçüncü sonda yan yana kalıyor, yani
  aralarında karışma riski sürüyor. Korunması gereken ana karakter *(K5)*.
- **Değişmeyen:** diskte duran yapı dosyaları. Kişi sayısı alanı olmayan bir kare bugünkü gibi
  çıkıyor — kod eksik alanı atlıyor *(K26)*.

### Madde 96 — Şema ve kural kitabı skill metninden çıkar, araçtan gelir

- **Ne çalışır:** yapı dosyasının şeması bugün skill metninin içinde duruyor, ve yönerge her turda
  yeniden gönderiliyor *(Madde 93)* — yani şema, yalnız yazma anında lazım olduğu hâlde her tur
  ödeniyor. Üstelik iki skill de dosya yazacağı için ikisinin birden bilmesi gerekiyor, ki bu ikinci
  bir kopya demek. Şema ve kural kitabı tek bir yere iner ve **çağrılınca** gelir.
- **Nasıl görülür:** model yapı dosyasını yazmadan önce şemayı okuyor; skill metinleri kısalıyor ve
  şemayı artık taşımıyor.
- **Kararı verilmiş** *(K28)*: ikisi birlikte döner. Kural kitabı da dosyayı yazan tarafın işi,
  yalnız kuranın değil.
- **Yanında kapanan:** kural kitabı altıncı maddesini burada alıyor — kişi sayısı ya da tek başınalık
  bir karakterin kendi tanımındaysa yanlış yerde *(K27)*.
- **Şartı:** 95 — şemanın anlattığı kişi sayısı alanını kodun zaten kuruyor olması lazım.

### Madde 97 — Plan yazmak edit kipinin de işi olur

- **Ne çalışır:** plan yazan araç bugün yalnız plan kipinde elde. Akış ise dosya yazdığı için edit
  kipinde çalışıyor, yani planını yazamıyor.
- **Nasıl görülür:** edit kipinde bir plan yazılıyor ve tur bitmiyor — iş aynı turda devam ediyor.
- **Değişmeyen:** planın turu bitirme kuralı. O yalnız plan kipinde geçerli *(K22)*.

### Madde 98 — Karakter tek başına denenir

- **Ne çalışır:** kullanıcı bir karakteri sahneye girmeden görmek istiyor — *"bakayım nasıl
  çıkıyor"* — ve bugün bunun için ayrı bir deneme dosyası yazdırmak gerekiyor. İkinci bir kurucu
  gelir: karakter × kıyafetler, düz bir prompt listesi.
- **Nasıl görülür:** bir karakter adı veriliyor ve o karakterin her kıyafeti için bir prompt taşıyan
  liste çıkıyor. Kıyafeti olmayan karakter tek satır veriyor.
- **Kararı verilmiş** *(K36)*: içinde model yok. Kod etiketleri birleştiriyor, tıpkı sahne
  promptlarında olduğu gibi — yani karakter denemede nasıl görünüyorsa sahnede de öyle görünüyor.
- **Değişmeyen:** çıktının biçimi. Sahne listesiyle aynı, yapıştırılmaya hazır. Kendi dosyasına
  yazılıyor, sahnenin listesine karışmıyor.
- **Şartı:** 95 — aynı kurucuyu paylaşıyor.

### Madde 99 — İzin tur ortasında sorulur, onay kipi değiştirir

- **Ne çalışır:** kip bugün modele hangi araçların verildiğini söylüyor, ve verilmeyen araç
  çağrılamıyor. Doğru bir kural, ama bir yan etkisi var: yanlış kipte duran kullanıcı ilk adımda
  takılıyor ve neden takıldığını ekran söylemiyor. Kip artık **sormadan çalışabilenlerin** listesi
  olur: izin verilmeyen bir çağrı geldiğinde tur durur, ekran sorar, ve cevap gelene kadar bekler.
- **Nasıl görülür:** soru kipinde dosya yazmayı gerektiren bir iş isteniyor; ekran izin soruyor;
  onay verilince kip değişiyor ve **aynı tur** kaldığı yerden devam ediyor.
- **Kararı verilmiş** *(K37, K38, kullanıcının kendi cümlesi: "claude güzelce çözmüş bunu")*: red
  turu bitirmiyor. Modele bir açıklamayla dönüyor — kip değişmedi, bu araç bu kipte yok, yazmadan
  devam et — ve **kullanıcı kendi sebebini de yazabiliyor**, o da modele gidiyor.
- **Yetki hâlâ kodda:** model izin almadan yazamıyor. Değişen tek şey kapının araç listesinden değil
  çalıştırma anından geçmesi; yönergeye "yazma" diye bir cümle girmiyor *(Madde 91 yerinde)*.
- **Koşunun en büyük maddesi.** Cevap tek isteğin içinde akıyor *(Madde 88)*, yani akışın o isteğin
  ortasında beklemesi gerekiyor. Spec'i açıldığında birden fazla maddeye bölünmesi beklenen sonuç;
  numaralar kaymaz, yeni numaralar sondan verilir.
- **Değişmeyen:** çağrı kartları. Reddedilen çağrı da sohbette görünüyor *(Madde 84, 85)*.

### Madde 100 — Skill seçimi yenilemeden sonra hatırlanır

- **Ne çalışır:** skill seçimi bugün oturumun kipi *(Madde 86)*, ve sayfa yenilenince kayboluyor.
  Beş adımlık bir akışın ortasında bu, bir sonraki mesajın yönergesiz gitmesi demek — ve ekranda
  bunu söyleyen bir şey yok. Seçim tarayıcıda hatırlanır.
- **Nasıl görülür:** skill seçilip sayfa yenileniyor ve seçici seçili hâlinde geliyor; gönderilen
  mesaj o skill'in yönergesiyle gidiyor.
- **Kararı verilmiş** *(K39)*: Madde 86 bunu bilerek dışarıda bırakmıştı, ve gerekçesi *"buna
  değecek bir şey yok"*tu. Akış o gerekçeyi değiştiriyor.
- **86'nın korktuğu geri gelmiyor:** ekranın gösterdiği ile isteğin taşıdığı hâlâ tek değer.
  Hatırlanan şey o değerin kendisi, ikinci bir kaynak değil.

### Madde 101 — Start a scenario doğar

- **Ne çalışır:** kullanıcıyı sorarak yürüten ikinci skill gelir. Karakterleri sorar, mekânları
  sorar, sahneleri yazar, promptları kurar — ve nerede kaldığını bir plan dosyasında tutar.
- **Nasıl görülür:** seçicide ikinci satır var; seçilip bir cümle yazıldığında plan dosyası doğuyor,
  her adım onay bekliyor, ve sonunda prompt listesi çıkıyor.
- **Kararı verilmiş** *(K29, K30)*: akış **dallanmaz** — her adımın tek çıktısı var, ve o çıktı
  kullanıcının ne kadar anlattığına göre değişmez; değişen yalnız adımın kaç tur sürdüğü. Her adım
  kendi içinde döngü: kullanıcı onaylayana kadar bir sonrakine geçilmez.
- **Kararı verilmiş** *(K32)*: promptları akış kendisi kuruyor. Kullanıcı sonda skill değiştirmiyor.
  prompt+ yerinde duruyor, işi **var olanı güncellemek**.
- **Kararı verilmiş** *(K34)*: anlatılmayan karakter ve mekân için yer tutucu yazılıyor. Akış tarif
  bekleyerek durmuyor.
- **Yarım kalan iş yeni bir sohbetten sürüyor:** dosyalar projenin, sohbetin değil. Akış ilk iş
  olarak projeye baktığı için orada duran planı görüyor ve açık adımdan devam ediyor — bağlam tavana
  çarptığında *(Madde 92)* yapılacak şey de bu.
- **Bilerek kabul edilen** *(K33)*: sahneler iki yerde duruyor — yapı dosyasında etiket, md'de
  cümle. Biri elle düzeltilip öteki unutulursa ayrışıyorlar; kod bunu kovalamıyor.
- **Şartı:** 96, 97, 98.

## Açık sorular

| Soru | Nerede kapanır |
|---|---|
| Şema kişi sayısı dışında başka ne alıyor | 95 |
| İzin sorusunun ekranda nasıl göründüğü ve bekleyen turun nasıl taşındığı | 99 |
| Akış metninin adımları hangi cümlelerle söylediği | 101 |

## Kapsam dışı

**`BREAK`** — kalabalık karede karakterleri ayırmanın bilinen ilacı, ve şartı queen-editor'ün bir
düğüm açması. İki backlog'da duruyor *(K12–K15)*.

**Okumayı alt ajana taşımak** ve **özetleme** — v5.5'te kapsam dışı bırakılmışlardı, burada da
öyleler. Bekleyen bir kayıtları yok.
