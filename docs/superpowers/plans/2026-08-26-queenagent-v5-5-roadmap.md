# QueenAgent v5.5 Yol Haritası — sadeleştirme

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** kullanıcının konuşma sırasında söyledikleri. Bu belge onlardan türer; ters yön yok.
**Numaralar** v5'ten devam eder (85'te bitti), yani **86'dan** başlar.

---

## Neden bu koşu var

İki dert var, ve ikisi de v5'in bitirdiği ekranın altında duruyor.

**Birincisi makinenin kendisi:** aynı şeyin iki yerde durduğu, kodun sözleşmesinin yalan söylediği,
bir şeyin olduğunu hiçbir yerin söylemediği yerler. 86'dan 90'a kadar olanlar bunlar.

**İkincisi modelin nasıl çalıştığı:** yetkinin ricayla tutulması, işin bölünmesinin modelden
istenmesi, bağlamın sınırsız büyümesi, yönergenin konuşmanın ortasında solması. 91'den 94'e kadar
olanlar bunlar, ve hepsi 26 Ağustos'ta yapılan araştırmadan çıktı — ajan araçlarının uzun
konuşmaları nasıl kaldırdığı, işi neden böldükleri, bağlamın uzadıkça niye kalite kaybettirdiği.

**Bu koşu v5'in Blok 2'sinden önce koşulur** *(kullanıcı kararı, 26 Ağustos)*. Sıra şöyle: önce
v5.5, sonra v5'te kalan maddeler. Tek istisna 73 — 94'ün şartı olduğu için v5.5'in içine, 94'ten
hemen önce girer. Blok 2'nin kalanı (69, 70, 71, 75) v5.5 bittikten sonra koşulur.

## Maddeler

Konuştukça ekleniyor *(kullanıcı kararı, 26 Ağustos: "senle konuştukça ekleyeceğiz")*. Her madde
geldiğinde numarası sondan verilir ve bir daha kaymaz.

**Nasıl koşulur** *(kullanıcı kararı, 26 Ağustos: "roadmapı nasıl koşuyorsak")*: madde madde. Bir
madde iki turda biter — önce testler kırmızı commit'lenir, sonra kod yeşile döndürülür — sonra
sıradaki konuşulur. Blok 4'ün ritmi.

**Koşma sırası:** 86 → 87 → 88 → 89 → 90 → 92 → 91 → 93 → 73 → 94. İlk altısının hiçbir şartı yok;
91 ile 93 mekanik, tek başlarına koşabilirler; 94 en sonda, çünkü şartı 73 ve 91.

**87, 88 ve 89 ayrı maddeler olarak koşar** *(karar, 26 Ağustos)*, birleştirilmez — üçü de aynı üç
dosyanın aynı bölgesine dokunduğu ve aynı testleri arka arkaya yeniden yazdırdığı hâlde. Sebebi:
üçü ayrı ayrı görülebiliyor — 87 iki uç yerine bir uç, 88 iki istek yerine bir istek, 89 yazan ucun
durum döndürmemesi. Birleştirilirse tek bir kırmızı tur uçları, use case'leri, hook'u ve ekranı aynı
anda kırar, ve kırmızı bir test hangi kararın yanlış olduğunu söyleyemez. Sıra da bu yüzden bu sıra:
önce kapı birleşir, sonra o kapıdan geri ne geldiği değişir, en sonda geri gelen şey kırpılır. Tersi
her dizilişte önceki maddenin işi sonraki tarafından atılıyor.

### Madde 86 — Skill sohbetin değil oturumun kipi olur

- **Ne çalışır:** skill seçimi bugün sunucuya yazılıyor — sohbet kaydında bir alan, onu yazan bir uç
  ve bir use case var. Ama cevap yolu o alanı hiç okumuyor: turu yöneten yönerge mesajın kendi
  skill'inden geliyor, yani gönderim anında yazılan değerden. Sunucudaki alan yalnız seçicinin ne
  göstereceğini söylüyor. Sistem sökülür: seçili skill isteğin içine yazılır ve başka hiçbir yerde
  durmaz.
- **Nasıl görülür:** skill seçilip mesaj gönderiliyor, model o yönergeyle cevaplıyor; sayfa
  yenilendiğinde seçici boş dönüyor ve sohbetin kaydında hiçbir skill alanı yazmıyor.
- **Yanında kapanan bir hata:** bugün seçici sohbetin kaydını gösteriyor, gönderim ise oturumun son
  seçimini yolluyor. İkisi ayrıştığı anda ekran bir şey diyor, isteğe başka bir şey gidiyor —
  yenilemeden sonra skill'i olan eski bir sohbeti açıp mesaj göndermek bunu her seferinde yapıyor.
  Tek kaynak kalınca hata ortadan kalkıyor; yazılacak bir senkron yok, çünkü senkronlanacak ikinci
  bir yer yok.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: skill sohbette saklanmaz. Bedeli biliniyor ve
  kabul edildi — yenilemeden sonra seçici boş başlar, ve bir sohbette seçilen skill ötekine de geçer.
  Artık sohbetin değil oturumun kipi. Tarayıcı hafızasına da yazılmaz: sildiğimiz karmaşıklığı başka
  bir yere taşımak olurdu.
- **Değişmeyen:** mesajın kendi skill alanı. Her tur hangi yönergeyle konuştuğunu söylemeye devam
  eder, yani geçmiş yalan söylemez. Skill seçicinin kendisi de duruyor — kalkan şey seçimin nerede
  hatırlandığı.
- **Eski kayıtlar:** diskteki skill anahtarı JSON'da kalır ve kimse okumaz; sohbet bir daha
  yazıldığında kendiliğinden düşer. Madde 82'nin model anahtarında olduğu gibi.
- **Yanında düşen bir uç:** sohbeti güncelleyen PATCH ucu başka hiçbir şey yapmıyor — skill dışındaki
  her anahtarı reddediyor. Skill oradan çıkınca ucun kendisi de gider.

### Madde 87 — Mesaj tek kapıdan girer, sohbeti sunucu yaratır

- **Ne çalışır:** "kullanıcı bir cümle söyledi" işi bugün iki ayrı isteğe bölünmüş — ilk mesaj sohbeti
  yaratan uca, sonrakiler mesaj ekleyen uca gidiyor. Hangisinin çağrılacağını frontend seçiyor: bir
  bayrak yüzünden gönderme işinin iki ayrı yolu var. Sunucuda da iki use case aynı şeyi yapıyor —
  metni doğrula, mesajı yaz, kaydı döndür. Tek kapı kalır: frontend her zaman aynı yere gönderir,
  sohbet yoksa sunucu yaratır, varsa ekler.
- **Nasıl görülür:** taslak ekranda ilk cümle gönderiliyor ve sohbet açılıyor; aynı ekranda ikinci
  cümle gönderiliyor ve sohbete ekleniyor. İkisi de aynı uca gidiyor.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos: "sadece mesaj atalım, chat yok oluştursun")*:
  sohbeti yaratma işi kendi ucunu kaybeder.
- **Değişmeyen:** boş sohbet yok — sohbet hâlâ ilk mesajıyla doğuyor ve başlığını hâlâ o cümleden
  alıyor. Boş metin hâlâ reddediliyor. Taslak ekran da duruyor; kalkan şey onun hangi uca
  gideceğine karar vermesi.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: sohbetin id'si yolda değil, isteğin içinde
  taşınır ve boş olabilir. Boşsa sunucu sohbeti yaratır, doluysa var olana ekler — kararı veren tek
  soru bu, ve isteğe bakan yer cevabı orada görür.
- **Yanında düşenler:** sohbet yaratan uç, onun use case'i, ve frontend'in ikinci gönderme yolu.

### Madde 88 — Cevabı sunucu başlatır, tarayıcı değil

- **Ne çalışır:** bugün mesaj diske yazılıyor ve bağlantı kapanıyor; cevap ancak tarayıcı ikinci bir
  istek attığı için doğuyor. Tarayıcıda "bu sohbet bir cevap borçlu" diye bir kural var, ve o kural
  yalnız gönderimden sonra değil, sayfa yenilenince ve bağlantı geri gelince de tetikleniyor — yani
  kullanıcının istemediği bir anda cevap kendiliğinden baştan başlıyor. Mesaj yazıldıktan sonra cevap
  aynı isteğin içinde üretilmeye başlar ve aynı bağlantıdan akar.
- **Nasıl görülür:** bir cümle gönderiliyor ve cevap tek bir istek içinde akmaya başlıyor; cevapsız
  duran bir sohbet açılıp sayfa yenilendiğinde kendiliğinden konuşmaya başlamıyor.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: otomatik tekrar deneme yok. Yarıda kalan tur
  durdurulduğunu yazar, o kadar — kullanıcı devam etmek isterse yeni bir cümle yazar. Bu, öteki
  sohbet uygulamalarının yaptığı şey.
- **Yeni sohbetin adresi akışın ilk karesinde gelir** *(karar, 26 Ağustos)*: 87 id'yi isteğin içine
  koyuyor ve boş bırakılabiliyor, bu madde de cevabı aynı isteğe taşıyor — ikisi birleşince o isteğin
  cevabı artık JSON değil, akış. Yani yeni sohbetin id'si bir gövde alanı olarak dönemez. İlk kare
  olur: sunucu id'yi mesajı yazmadan önce zaten üretiyor, yani ilk model tokenından önce
  söylenebilecek durumda. Tarayıcı adresi orada değiştirir, cevap da doğru sohbetin içinde akar —
  yarıda durdurulsa bile sohbet görünür kalır. **Her istekte gönderilir**, sohbet yeni olsun ya da
  olmasın: sunucuda koşul olmaz, tarayıcı yalnız elindekinden farklıysa adresi değiştirir.
- **Değişmeyen:** akış. Metin ve çağrı kartları akmaya devam eder; Madde 66, 78, 84 ve 85'in
  görünürlük işi olduğu gibi duruyor. İlk kare olayların diline bir giriş ekliyor, yeni bir taşıma
  yolu değil — `chunk`, `call`, `file`, `done` nasıl okunuyorsa bu da öyle okunuyor.
- **Yanında düşen:** tarayıcıdaki "cevap borçlu" kuralı ve onu koşturan efekt. Madde 81'in yazdığı
  boş kayıt kalıyor ama sebebi teke iniyor: ekranda "durduruldu" yazabilmek. Kendiliğinden yeniden
  başlamayı önleme işi, önleyecek bir şey kalmadığı için düşüyor.
- **Sırası:** 87'den sonra — tek kapı açıldıktan sonra bu kural tek bir yazma yoluna uygulanır.

### Madde 89 — Sohbetin şekli tek yerde kurulur

- **Ne çalışır:** sohbetin JSON'unu bugün beş yer üretiyor — iki mesaj ucu, skill ucu, okuma ucu ve
  akışın son karesi. Kayda bir alan eklendiğinde beşi birden değişmek zorunda. Yazan uçlar durum
  döndürmeyi bırakır: sohbeti yalnız okuma ucu döndürür, ve yazan bir iş bittiğinde tarayıcı onu
  okur.
- **Nasıl görülür:** cevap bittiğinde ekran kaydı okuyup çiziyor, ve sohbetin şeklini kuran tek bir
  yer kalıyor.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: okumak ile yazmak ayrı yapılar olur, çünkü
  ayrı olunca yönetmesi kolaydır. Akışın son karesi gövdesiz.
- **88'e devredilen:** *"yeni sohbet yaratan istek yalnız id döndürür"* cümlesi buraya yazılmıştı;
  88 o isteğin cevabını akışa çevirdiği için id'nin nasıl döneceği orada karara bağlandı — ilk kare.
  Bu madde 88'den sonra koştuğu için geriye kalan işi şu: son kare gövdesiz olur, ve tarayıcı kaydı
  okuma ucundan okur.
- **Değişmeyen:** akan metin ve çağrılar. Değişen tek şey akışın kaydı taşımaması: akan şey geçici
  bir gösterim, gerçek olan okunan kayıt.
- **Bedeli:** her turdan sonra fazladan bir okuma isteği. Yerelde ihmal edilebilir, ve karşılığında
  kaydın şekli tek yerde durur.
- **Sırası:** 88'den sonra.

### Madde 90 — Durdurma tek yoldan iner ve bağlantıyı keser

- **Ne çalışır:** durdurma bugün iki yarımdan oluşuyor. Bir bayrak var ve koşan cevap onu ancak
  xAI'den bir kare geldiğinde soruyor — ilk kelime beklenirken kimse sormuyor, yani düşünen bir
  modelde durdurmaya basmak dakikalarca hiçbir şey yapmayabiliyor ve xAI o süre boyunca üretmeye ve
  faturalamaya devam ediyor. Bağlantının kapanması ise döngüden çıkmanın yan etkisi, kimsenin verdiği
  bir karar değil. İki yarım tek iptal olur: durdurma isteği, koşan cevabın xAI'ye açık duran
  bağlantısını doğrudan kapatır. Okuma nerede blokeliyse orada uyanır — ilk kelime beklenirken de —
  ve sağlayıcı tarafında üretim ile fatura o anda durur *(xAI'nin bağlantı kesilince üretimi
  durdurduğu sağlayıcı belgeleriyle doğrulandı, 26 Ağustos)*.
- **Nasıl görülür:** model daha ilk kelimeyi söylemeden durduruluyor ve tur o anda bitiyor — ekranda
  durdurulduğu yazıyor, beklemeye devam etmiyor.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos: "2 ayrı iptal yerine tek bir iptal")*: bayrak
  ve yan etki diye iki mekanizma kalmaz, iptal tek mekanizmadır.
- **Yanında düşen:** bayrağın kendisi. Yerine geçen kayıt yine bellekte, yine kilitli, yine cevapla
  birlikte doğup ölüyor — bayrağın yaşam kuralı olduğu gibi devralınıyor; değişen, tutulan şeyin
  "istendi" notu değil bağlantının kendisi olması.
- **Dikkat isteyen bir ayrım:** bizim kapattığımız bağlantının hatası bir durdurmadır, ağın kendisi
  koptuğunda aynı hata bir arızadır. İkisini ayıran tek bilgi kayıtta — kapatan biziz ya da değiliz —
  ve hata mesajına sebep uydurmama kuralı burada da geçerli.
- **Değişmeyen:** durdurulan turun diske `stopped` işaretiyle yazılması, kelimeden önce durdurulan
  turun boş kayıt bırakması, düğmenin iki hâli. 67, 79, 80 ve 81'in tamamı yerinde.
- **Sırası:** 88'den sonra — cevap tek isteğin içine taşındıktan sonra kesilecek bağlantı da tek.

### Madde 91 — Kip gelir: plan, sor, düzenle

- **Ne çalışır:** modelin neyi yapıp yapamayacağı bugün yönergeyle tutuluyor. En açık örneği kontrol
  skill'i: metni *"hiçbir şey düzeltme, dosya yaratma, dosya düzenleme"* diyor — bir yetki kuralını
  ricaya çevirmiş, ve rica tutmayınca kontrol eden skill dosya düzeltiyor. Üç kip gelir — **plan**,
  **sor**, **düzenle** — ve hangi araçların isteğe konacağını kip belirler. Kural koda geçer.
- **Nasıl görülür:** sor kipinde dosyaya dayanan bir iş isteniyor; model okuyor, cevaplıyor, hiçbir
  dosya doğmuyor — çünkü yazma araçları isteğe hiç konmadı, model kendini tutmaya çalışmadı.
- **Plan kipi ne yapar:** işi maddelere böler, planı bir dosyaya yazar, ve **tur orada biter.**
  Kullanıcı planı okur, isterse dosyanın kendisinde düzeltir, sonra yürütür. Kötü bir plan sekiz tur
  yanmadan yakalanır, ve düzeltmek için sohbette tartışmak gerekmez.
- **Planı yazan ayrı bir araç** *(kullanıcı kararı, 27 Ağustos)*: `write_plan`. Plan kipinin elinde
  okuma araçları ve yalnız bu var — yani plandan başka bir şey yazacak aracı yok. Kural bir sayaçta
  değil, araç kümesinin kendisinde duruyor: `create_file` verilseydi model aynı turda planı da
  teslimatı da yazabilirdi, ki maddenin şikâyet ettiği tam olarak bu. Araç yaratır ya da üstüne
  yazar *("eldeki planı güncelleyebilir veya plan oluşturabilir")*, ve adı `-plan.md` ile bitmeye
  zorlanır.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: plan bir skill değil, bir kiptir. Skill
  olsaydı yedinci bir seçenek olurdu — oysa Madde 74 seçenekleri bire indiriyor — ve *"uzun iş
  vermeden önce plan skill'ini seçmeyi hatırla"* diye bir kural doğardı. Kip, hatırlanacak bir şey
  değil, açık bir denetim.
- **Kararı verilmiş:** bir görevin ürünü **dosyadır**, sohbet mesajı değil. Temiz bağlam, önceki
  görevin sohbette ne dediğini bilmez; yalnız diskte ne bıraktığını bilir. İstisnası olamaz, çünkü
  ihlali sessizdir — sonraki görev aradığını bulamaz ve kimse sebebini söylemez.
- **Değişmeyen:** var olan beş araç. Değişen, hangilerinin o kipte isteğe konduğu — ve yanına
  altıncı olarak `write_plan` giriyor, yukarıdaki karar gereği.
- **Yanında düşen:** skill metinlerindeki yapma-etme cümleleri, ve uzun işi gruplara bölmeyi rica
  eden paragraflar — plan yürüyen kod olunca üçü de gereksizleşiyor.
- **Sırası:** şartı yok, tek başına koşabilir — işi araçların isteğe konmasını koda almak, ve o iş
  hiçbir yönerge metnine dayanmıyor. Yalnız 94'ten önce gelmesi gerekiyor: 94 skill metinlerindeki
  yapma-etme cümlelerini siliyor, ve o cümlelerin işini kipin devralmış olması lazım.
- **İlişkisi:** v5'in 74'ü. Kip, 74'ün *"skiller tek akışta toplanır"* sorusunun büyük kısmını
  cevaplıyor: akış plan oluyor.

### Madde 92 — Bağlamın tavanı olur, ve tavana çarpmak bir olaydır

- **Ne çalışır:** bağlam büyüdükçe bugün hiçbir şey olmuyor. İstek gitmeye devam ediyor, cevabın
  kalitesi sessizce düşüyor, ve iş sonunda pencereye sığmayan bir istekle hataya bağlanıyor. Bir
  tavan konur: tur, tavanın üstünde yeni istek atmaz — durur ve neden durduğunu söyler.
- **Nasıl görülür:** sohbet uzadıkça composer'ın ayağındaki daire doluyor; tavana gelindiğinde tur
  duruyor ve sebebi ekranda yazıyor; arka arkaya hata veren istekler yok.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: tavan 50k civarı. Sebebi kapasite değil
  **kalite** — pencere 256k, yani tavan onun beşte biri. Ölçümler modellerin girdi uzadıkça
  kötüleştiğini ve ortada kalan bilginin gözden kaçtığını gösteriyor, yani sığmak yetmiyor.
- **Üçüncü bir gerekçe, fiyatta** *(xAI fiyat sayfasından doğrulandı, 26 Ağustos)*: 200k'nın üstünde
  girdi fiyatı ikiye katlanıyor — 1M token başına $1.00 yerine $2.00, önbellekten gelen için $0.20
  yerine $0.40. Bugünkü 300-500k'lık bağlam hem pencereye sığmıyor hem de iki katı ödüyor.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: tavana çarpınca istek atmak **engellenir** ve
  ekranda yeni bir sohbet açması söylenir. Özetleme yapılmaz — *şimdilik*. Özet, konuşmayı sürdürmenin
  yolu ama kendi başına bir iş; bu madde yalnız tavanı ve durmayı getiriyor. Özetlemeyi getirmek
  isteyen gün, 71'in işi.
- **Hangi sayıya bakılır** *(kullanıcı kararı, 26 Ağustos)*: bir turun büyüklüğü ancak cevap dönünce
  öğreniliyor, o yüzden tavan **bir önceki cevabın** sayısına bakar. Yani ölçü bir tur eski, ve
  tavana çarpan istek aslında bir önceki isteğin boyuyla durduruluyor. 50k'lık tavanda bu fark
  önemsiz — bir turun kendisi tavanı aşacak kadar büyük değil.
- **Ekranda ne görünür** *(kullanıcı kararı, 26 Ağustos)*: composer'ın ayağında **dolan turuncu bir
  daire** — Claude Code'un bağlam göstergesindeki gibi. Doluluk oranı aynı sayıdan geliyor: son
  cevabın gönderdiği token, tavana bölünmüş. Kullanıcı tavana çarpmadan önce yaklaştığını görüyor,
  yani durma sürpriz olmuyor.
- **Taslak ekranda görünmez** *(karar, 26 Ağustos)*: composer iki ekranda da aynı bileşen, ama henüz
  sohbet yokken ölçülecek bir bağlam da yok. Boş bir daire çizmek kullanıcıya okuyacak bir şey
  vermiyor, yalnız hep orada duran bir işaret veriyor. Daire ilk cevap dönünce doğar.
- **Nerede durur** *(kullanıcı kararı, 26 Ağustos)*: ayağın **solunda**. Skills, model adı ve
  gönder düğmesi karar 1'den beri sağda duruyor — ayak bugün uçtan sağa dayalı; daire karşı uca
  geçiyor, yani ayak iki uca yaslanan bir satır oluyor. Sebebi: gösterge bir denetim değil, okunan
  bir şey; sağdaki üçlünün arasına girerse tıklanacak bir şey gibi görünür.
- **Şartı:** 76 — sayı zaten her cevabın altında yazıyor, ölçü kurulu. Daire de, tavan da o sayıyı
  okuyor; yeni bir ölçüm kurulmuyor.
- **İlişkisi:** v5'in 71'i bağlamı küçültmenin yolunu arıyor; bu madde onun **tabanını** koyuyor. 71
  hiç gelmese bile tavan tek başına koruyor, ve 71 geldiğinde tavan yine yerinde kalıyor.

### Madde 93 — Yönerge isteğin sonuna iner, sabit olan başta kalır

- **Ne çalışır:** yönerge bugün konuşmanın **ortasına** konuyor — skill'in değiştiği yere. Skill dört
  kez değiştiyse konuşmanın içinde dört ayrı yönerge metni duruyor, ve en eskisi kırk mesaj geride
  kalmış oluyor. İstek yeniden dizilir: sabit olan başa, yönerge **en sona**. Konuşmanın içinde
  dağınık kopyalar kalmaz, yalnız güncel olan gider ve en sonda durur.
- **Nasıl görülür:** uzun bir sohbette skill'e bağlı bir iş isteniyor ve model yönergeye uyuyor —
  yönerge konuşmanın kırk mesaj gerisinde kalmış olsa bile, çünkü artık orada değil.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: iki ayrı ölçü aynı yeri gösterdiği için.
  **Dikkat:** doğruluk bağlamın başında ve sonunda en yüksek, ortasında %30'dan fazla düşüyor —
  yönergenin en sonda olması onu yüksek dikkat bölgesine koyuyor. **Önbellek:** sabit olan başta
  durursa önek korunur, değişken olan sonda durursa değiştiğinde yalnız kendisi geçersizleşir.
- **Bedeli biliniyor ve kabul edildi:** blok her turda sonda kalmak için taşınıyor, yani her turda
  yeniden işleniyor. On altı turluk bir cevapta bu ~8k token, yani kuruşlar — önbellekten gelen girdi
  1M token başına $0.20 *(xAI fiyat sayfasından doğrulandı, 26 Ağustos)*.
- **Taşınamayan tek şey araç listesi:** `tools` isteğin ayrı bir alanı ve her zaman en başta
  işleniyor. Kipin *metni* sona iner, *araç kısıtı* başta kalır — ve iş zaten kısıtın kendisinde.
- **Değişmeyen:** mesajın kendi skill alanı. Kayıt hangi turun hangi yönergeyle konuştuğunu söylemeye
  devam eder; değişen yalnız modele ne gönderildiği.
- **İlişkisi:** 91'in kipi ve v5'in 73 ile 74'ü. 74'ün *"yönerge nerede durur"* sorusunu kapatıyor.

### Madde 94 — Tek skill kalır, beşi silinir

- **Ne çalışır:** bugün altı skill var ve hangisinin ne zaman geleceğini kullanıcı seçiyor. Beşi
  silinir; geriye yapıdan prompt kuran tek skill kalır — kodun promptu birleştirdiği, modelin elle
  yazmasının yasak olduğu yol.
- **Nasıl görülür:** seçilecek bir skill listesi yok; bir senaryodan prompt listesine kadar olan yol
  tek bir metinle yürüyor.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: prompt+ dışında hepsi gider. Bu, v5'in 74'ünün
  *"hangi skiller düşecek"* açık sorusunun cevabı — hepsi, biri hariç.
- **Zaten fazlalık olan biri:** promptları elle yazan yol, yapıdan kuran yolla aynı işi yapıyor ve
  karakteri kopyaladığı için FOUNDATION 5 ile çarpışıyor. v5 onu şimdiden aday göstermişti.
- **Kaybı biliniyor:** silinen metinlerde işin kendi bilgisi de var — bir karenin bir-iki cümle
  olduğu, kare listesinin kullanıcının dilinde yazıldığı *(yapı dosyası ve prompt listesi İngilizce
  kalırken)*, karakter adaylarının hangi dosya biçiminde verildiği. Kontrol skill'i gidince
  kural kitabı yalnız kurma anında uygulanır, ayrıca "dosyalarımı denetle" diye bir yol kalmaz.
- **Spec'te karara bağlanacak:** bu bilgiden hangisinin kalan skill'e ya da taban yönergeye
  taşınacağı, hangisinin gerçekten gereksiz olduğu. Hepsini taşımak silmeyi anlamsız kılar, hiçbirini
  taşımamak da modeli her seferinde yeniden icat etmeye bırakır.
- **Seçici kalıyor** *(kullanıcı kararı, 26 Ağustos)*: Madde 82'nin model seçicisine benzemiyor.
  Orada tek model vardı ve seçmemek diye bir hâl yoktu; burada **skill seçmemek olağan bir hâl**, yani
  tek satırlık bir seçici bile iki durum taşıyor — skill'li ve skill'siz, ve hangisi olacağı
  kullanıcının kararı. Üstelik listeye ileride yenileri gelecek; şimdi sökmek yakında geri koymak
  olurdu.
- **Şartı:** 73 ve 91. Taban yönerge ortak davranışı söylemeye başlamadan ve kip yetki kurallarını
  devralmadan metinlerden fazlalık bırakılamaz.

## Açık sorular

| Soru | Nerede kapanır |
|---|---|
| v5'in 74'ü ile bu koşunun 94'ü aynı işi iki belgede anlatıyor — ikisi de "skiller ne olacak" diyor, ikisinin de açık sorusu aynı. Hangisi ötekine devredecek? | 94'e gelinmeden önce |
| 94'ün silmesiyle kaybolacak bilgiden hangisi kalan skill'e, hangisi taban yönergeye taşınacak | 94'ün spec'inde, 73 koşulduktan sonra |

**Numara sorusu kapandı:** sayaç tek. Bu koşu 86'dan 94'e kadarını aldı, ve bundan sonra hangi
belgeye madde eklenirse eklensin 95'ten devam eder. v5.5 önce koştuğu için Blok 4'ün açık uçlu olması
bir çakışma doğurmuyor.

## Kapsam dışı

**Proje çapası dosyası** *(kullanıcı kararı, 26 Ağustos)* — her projede "bu proje nedir, karakterler
kim" diyen ve her isteğin başına konan bir dosya. Ajan araçlarının kullandığı bir kalıp, ama burada
gerek görülmedi: projede zaten dosyalar var ve modelin onları listelemesi ucuz.

**Okumayı alt ajana taşımak** *(kullanıcı kararı, 26 Ağustos)* — dosya okumanın ayrı, sınırlı bir
bağlamda olması ve ana konuşmaya yalnız özetin dönmesi. Araştırmanın en büyük kaldıracı, ama en büyük
işi de. Sonraya bırakıldı: 91'in plan kipi zaten her göreve temiz bir bağlam veriyor, ve faydasının
çoğunu ondan alıyoruz. Ölçü hâlâ sorun gösterirse açılır.

**Kip değiştirmenin önbellek maliyetini optimize etmek** — araç listesi isteğin en başında durduğu
için kip değişimi o tek isteği tam fiyattan ödetiyor. 40k'lık bir sohbette bu üç kuruş *(xAI fiyat
sayfasından doğrulandı, 26 Ağustos)*. Etrafından dolaşmaya değmez.
