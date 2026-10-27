# Yol 1 · Tasarımdan repoya

Kaynak: tasarımın çizilmiş hâli — çalışan prototip ve 14 kareli ekran tuvali. Yazılı sözleşme
okunmadı. Karşı taraf: bugünkü uygulamanın ekranları, stilleri, istemci kancaları ve kuralları.

---

## Adlandırma ve kimlik

### Ürünün adı
- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Adlandırma ve kimlik
- **Bugün:** Kenar çubuğunun tepesinde "Mira" yazıyor, ürün her metinde kendine Mira diyor.
- **Yeni tasarımda:** Kenar çubuğunun tepesinde "QueenAgent" yazacak ve ürün adı geçen her cümle
  ("Files QueenAgent created", cevap akışındaki rol etiketi, boş hâl cümleleri) o adı taşıyacak.
- **Dayanak:** Prototipin kenar çubuğu ve ekran tuvalinin başlığı.

### Ad yanındaki işaret karesi
- **Tür:** öksüz
- **Etiket:** görsel
- **Alan:** Adlandırma ve kimlik
- **Bugün:** Kenar çubuğunun tepesinde adın solunda 22×22, 6px yarıçaplı vurgu renginde dolu bir kare
  duruyor.
- **Yeni tasarımda:** karşılığı yok
- **Dayanak:** Prototipin kenar çubuğu başlığında yalnız serif kelime-işareti var, ondan önce bir
  öge yok.

### Kullanıcının kendi mesajının etiketi
- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Adlandırma ve kimlik
- **Bugün:** Kullanıcının balonunun üstünde sabit "You · 11:04" yazıyor.
- **Yeni tasarımda:** Aynı yerde kullanıcının kendi adı ve saat yazacak; ad dışarıdan verilen bir
  değer ve verilmezse "Alex" görünüyor.
- **Not:** Adın nereden geleceğini tasarım söylemiyor.
- **Dayanak:** Prototipte mesaj rol etiketi kullanıcı adı özelliğinden kuruluyor.

---

## Kenar çubuğu

### Arama düğmesi ve kısayolu
- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Kenar çubuğu
- **Bugün:** Adın hemen altında "Search" yazan, sağında "⌘K" rozeti olan bir düğme var; tıklanınca
  arama katmanı açılıyor.
- **Yeni tasarımda:** karşılığı yok
- **Dayanak:** Prototipin kenar çubuğunda ad ile "New chat" arasında hiçbir öge yok; tuvalin 14
  karesinin hiçbirinde arama görünmüyor.

### "New chat" düğmesinin varlığı proje sayısına bağlanıyor
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Kenar çubuğu
- **Bugün:** Hiç proje yokken de "New chat" düğmesi duruyor ve basınca ana ekrana gidiyor.
- **Yeni tasarımda:** Proje sayısı sıfıra düştüğünde "New chat" düğmesi kenar çubuğundan tümüyle
  kalkacak, ilk proje doğduğunda geri gelecek.
- **Dayanak:** Prototipte düğme proje varlığı koşuluna sarılı; A0 karesinin notu da bunu söylüyor.

### Proje satırında "⋯" menüsü
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Kenar çubuğu
- **Bugün:** Kenar çubuğundaki proje satırında yalnız nokta, ad ve dosya sayısı var; satırdan proje
  üzerinde bir işlem yapılamıyor.
- **Yeni tasarımda:** İşaretçi satırın üstüne gelince adın sağında "⋯" düğmesi belirecek (görünmezken
  yer kaplamayı sürdürüyor), basınca imlecin bittiği noktada 176px genişliğinde bir menü açılacak ve
  içinde "Rename" ile kırmızı "Delete project" duracak.
- **Dayanak:** Prototipin proje gezinme satırı ve ona bağlı satır menüsü.

### "Recent chats" listesinin kapsamı
- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Kenar çubuğu
- **Bugün:** Başlık her zaman duruyor ve altında bütün projelerden derlenmiş son sohbetler listeleniyor.
- **Yeni tasarımda:** Bölüm yalnız açık projenin sohbeti varsa görünecek, o projenin en yeni sekiz
  sohbetini listeleyecek, proje boşsa başlığıyla birlikte kaybolacak.
- **Dayanak:** Prototipte bölümün koşulu ve listesi açık projeye bağlı.

### Kenar çubuğu genişliğinin daralması
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Kenar çubuğu
- **Bugün:** Genişlik 280px; pencere 1100px altına inince tek adımda 208px'e düşüyor ve iç boşluk
  18/14'ten 16/10'a geçiyor.
- **Yeni tasarımda:** Genişlik üç adımda inecek — 1000px altında 226px, 840px altında 198px, 640px
  altında 172px — ve iç boşluk yalnız en dar adımda 18/14'ten 14/10'a düşecek.
- **Dayanak:** Prototipin kenar çubuğu stilini genişlik eşiklerinden kuran hesabı.

---

## Boş hâller

### Hiç proje yokken açılan ekran
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Boş hâller
- **Bugün:** Hiç proje yokken ana ekran yine selamlama, yazma kutusu, öneri düğmeleri ve "Projects"
  başlığıyla açılıyor; kart ızgarası boş kalıyor.
- **Yeni tasarımda:** Proje sayısı sıfırken ekranın tamamı ortalanmış tek bir boş hâle dönüşecek:
  serif 34px "No projects yet" başlığı, altında "Chats live inside a project, and the files they
  create stay there. Create a project to start." cümlesi ve tek bir dolu vurgu düğmesi
  "+ New project".
- **Dayanak:** Prototipin boş hâl dalı ve tuvalin A0 karesi.

---

## Home

### Selamlama başlığı
- **Tür:** öksüz
- **Etiket:** görsel
- **Alan:** Home
- **Bugün:** Ana ekran açılınca yazma kutusunun üstünde serif 42px "Hi" başlığı duruyor.
- **Yeni tasarımda:** karşılığı yok
- **Dayanak:** Prototipin ana ekran dalı doğrudan yazma kutusuyla başlıyor, üstünde başlık yok.

### Öneri düğmeleri
- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Home
- **Bugün:** Yazma kutusunun altında üç hap düğme duruyor ("Summarize this week's notes", "Draft a
  meeting agenda", "Turn my sources into a table"); birine basınca taslak o cümleyle doluyor,
  gönderilmiyor.
- **Yeni tasarımda:** karşılığı yok
- **Dayanak:** Prototipin ana ekranında kutunun altında doğrudan "Projects" başlığı geliyor; A1
  karesinin notu "no suggested prompts" diyor.

### Ana ekranın üst boşluğu
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Home
- **Bugün:** Sütun ekranın üstünden 14vh aşağıda başlıyor.
- **Yeni tasarımda:** Sütun 18vh aşağıda başlayacak.
- **Dayanak:** Prototipin ana ekran sütununun üst dolgusu.

### Proje kartındaki açıklama satırı
- **Tür:** öksüz
- **Etiket:** görsel
- **Alan:** Home
- **Bugün:** Kart üç satır gösteriyor: ad, açıklama cümlesi, sonra "3 chats · 3 files" sayacı.
- **Yeni tasarımda:** karşılığı yok
- **Dayanak:** Prototipin ana ekran kartı yalnız nokta, ad ve sayaç satırından kurulu.

### Ana ekrandan gönderilen mesajın nereye düştüğü
- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Home
- **Bugün:** Ana ekranda yazıp Send'e basınca "New project" adlı yeni bir proje doğuyor ve sohbet
  onun içinde açılıyor.
- **Yeni tasarımda:** Aynı hareket var olan bir projenin içinde sohbet açacak; ekranda mesajın nereye
  gideceğini söyleyen bir etiket bulunmayacak.
- **Not:** Hangi projenin seçileceğini tasarım söylemiyor; A1 karesi yalnız "hedef proje etiketi yok"
  diyor.
- **Dayanak:** Prototipte gönderme hareketi açık projeye, o yoksa listedeki ilk projeye bağlanıyor;
  A1 karesinin notu.

---

## Proje ekranı

### Geri düğmesi
- **Tür:** öksüz
- **Etiket:** görsel
- **Alan:** Proje ekranı
- **Bugün:** Proje başlığının üstünde mono "← back" düğmesi duruyor ve ana ekrana götürüyor.
- **Yeni tasarımda:** karşılığı yok
- **Dayanak:** Prototipin proje ekranı doğrudan başlık satırıyla başlıyor.

### Proje açıklaması
- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Proje ekranı
- **Bugün:** Başlığın altında açıklama paragrafı duruyor, yeni proje "Click to add a description."
  diye doğuyor ve paragrafa tıklayınca tarayıcının kendi kutusu "Project description" diye soruyor.
- **Yeni tasarımda:** karşılığı yok
- **Dayanak:** Prototipin proje ekranında başlık satırından sonra doğrudan yazma kutusu geliyor;
  proje nesnesinin taşıdığı alanlar arasında açıklama yok.

### Projeyi silme
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Yıkıcı eylemler ve geri alma
- **Bugün:** Bir proje hiçbir yerden silinemiyor; başlık satırında yalnız "Rename" var.
- **Yeni tasarımda:** Başlık satırında "Rename"in yanında kırmızı çerçeveli "Delete" duracak (üstüne
  gelince kırmızıyla dolup yazısı beyazlaşacak); basınca ekranın üstünü karartan bir onay kutusu
  açılacak: serif 23px «Delete "<ad>"?» başlığı, altında "The 3 chats and 3 files in this project are
  deleted with it. This can't be undone." cümlesi ve "Cancel" ile dolu kırmızı "Delete project"
  düğmeleri. Sayaçlar tekil olduğunda "1 chat" / "1 file" biçimine düşecek.
- **Dayanak:** Prototipin proje başlık satırı ve onay kutusu.

### Silinen projenin geri alınması
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Yıkıcı eylemler ve geri alma
- **Bugün:** bugün yok
- **Yeni tasarımda:** Proje silindiği anda ekranın altında ortalanmış koyu bir şerit belirecek
  (#26231F zemin, 11px yarıçap): «Project "<ad>" deleted.» yazısı, turuncu "Undo" ve kapatan bir "×".
  Undo'ya basınca proje eski sırasına geri konacak ve o projenin ekranı açılacak; şerit zamanla kendi
  kendine kapanmayacak.
- **Dayanak:** Prototipin proje geri alma şeridi ve geri alma hareketi.

### Sohbet satırındaki yeniden adlandırma
- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Proje ekranı
- **Bugün:** Sohbet satırının üstüne gelince "name" yazan mono bir düğme beliriyor, basınca tarayıcı
  kutusu "Chat title" diye soruyor.
- **Yeni tasarımda:** karşılığı yok
- **Dayanak:** Prototipin sohbet satırında yalnız silme düğmesi var.

### Sohbet silmenin onayı
- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Yıkıcı eylemler ve geri alma
- **Bugün:** Sohbet satırındaki "×" basılınca tarayıcının onay kutusu "Delete this chat? Its files
  stay in the project." diye soruyor, onaylanınca sohbet gidiyor ve geri alma sunulmuyor.
- **Yeni tasarımda:** "×" basılınca sohbet doğrudan gidecek; ne onay sorulacak ne de geri alma
  sunulacak.
- **Dayanak:** Prototipin sohbet satırındaki silme hareketi.

### Sohbet satırındaki silme düğmesinin görünürlüğü
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Proje ekranı
- **Bugün:** Satırdaki "×" saydam duruyor, ancak işaretçi satıra gelince ya da düğme klavyeyle
  odaklanınca görünür oluyor.
- **Yeni tasarımda:** "×" satırda her zaman görünür duracak (#B5ADA2), üstüne gelince yazısı kırmızıya
  döner ve arkasında yuvarlatılmış bir zemin belirir.
- **Dayanak:** Prototipin sohbet satırındaki silme düğmesinin sabit rengi ve üzerine gelme stili.

### Sohbet satırındaki zaman damgasının dar ekranda gizlenmesi
- **Tür:** eklenecek
- **Etiket:** görsel
- **Alan:** Proje ekranı
- **Bugün:** Zaman damgası her genişlikte satırın sağında duruyor.
- **Yeni tasarımda:** Pencere 780px'in altına indiğinde sohbet satırındaki zaman damgası satırdan
  tümüyle kalkacak, ad tek başına kalacak.
- **Dayanak:** Prototipin satır üstü verisini genişlik eşiğine bağlaması.

### Yazma kutusunun altındaki mono not
- **Tür:** öksüz
- **Etiket:** görsel
- **Alan:** Composer ve model seçici
- **Bugün:** Proje ekranındaki kutunun ayağında "the answer is saved as a file", sohbet ekranındaki
  kutunun ayağında "save the answer as a file" yazan mono bir not duruyor.
- **Yeni tasarımda:** karşılığı yok
- **Dayanak:** Prototipin her iki yazma kutusunda da ayağında yalnız düğmeler var.

### Silinen dosyanın geri alma şeridi
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Yıkıcı eylemler ve geri alma
- **Bugün:** Dosya listesinin üstünde beliren şerit beyazımsı yüzey renginde, 8px yarıçaplı; içinde
  "File deleted." ve "Undo" var, bir de başarısız bir işlem olursa altına mono bir hata satırı
  ekleniyor.
- **Yeni tasarımda:** Aynı şerit kenar çubuğu tonunda (#EFEBE4) ve 10px yarıçaplı olacak; içinde
  yalnız "File deleted." ve "Undo" duracak.
- **Not:** Şeridin bir hata cümlesi taşıyıp taşımayacağını tasarım söylemiyor.
- **Dayanak:** Prototipin dosya sütunundaki geri alma şeridi.

---

## Composer ve model seçici

### Model seçici
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Composer ve model seçici
- **Bugün:** Model bir yapılandırma değeri; ekranda hangi modelin cevapladığını gösteren ya da
  değiştiren hiçbir kontrol yok.
- **Yeni tasarımda:** Sohbetteki yazma kutusunun ayağında, Send'in solunda o an seçili modelin adı ve
  bir "▼" duracak; basınca 296px genişliğinde bir menü açılacak, başlığı "Model" olacak ve dört satır
  listelenecek — "Grok 4" ("Best for long, careful answers."), "Grok 4 Fast" ("Quicker replies,
  everyday questions."), "Grok 4 Heavy" ("Hard reasoning and long documents."), "Grok Code" ("Code,
  data and structured output."). Seçili satırın sağında vurgu renginde bir "✓" duracak; menü
  yukarıda yer yoksa düğmenin altına açılacak.
- **Dayanak:** Prototipin yazma kutusu ayağındaki model düğmesi ve model listesi.

### Beceri (Skills) seçici
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Composer ve model seçici
- **Bugün:** bugün yok
- **Yeni tasarımda:** Yazma kutusunun ayağında, model düğmesinin solunda bir düğme duracak; hiçbiri
  seçili değilken üstünde "Skills" yazacak, biri seçilince o becerinin adını taşıyacak ve düğme
  kızılımsı bir çerçeveyle işaretlenecek. Menü başlığı "Skills", satırlar "Web search" ("Look things
  up and cite the sources."), "Deep research" ("Read many sources before answering. Slower."),
  "Data & tables" ("Turn findings into structured tables."), "Code" ("Write and explain code in the
  answer."). Seçili satıra ikinci kez basmak seçimi kaldıracak — aynı anda en çok bir beceri açık
  olacak.
- **Dayanak:** Prototipin yazma kutusu ayağındaki beceri düğmesi ve beceri listesi.

### Model ve becerinin sohbete yazılması
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Ajan döngüsü
- **Bugün:** Her cevap aynı tek modelle üretiliyor; sohbetin kendisi hangi modelle konuşulduğunu
  taşımıyor.
- **Yeni tasarımda:** Seçilen model ve beceri açık sohbete iliştirilecek; başka bir sohbete geçip
  dönünce o sohbetin kendi seçimi geri gelecek, yeni açılan sohbet ise o an ekranda duran seçimle
  doğacak.
- **Not:** Beceri seçiminin cevabı nasıl değiştireceğini tasarım söylemiyor.
- **Dayanak:** Prototipte seçimlerin hem genel duruma hem açık sohbete yazılması.

---

## Cevap akışı ve Markdown

### Cevabın Markdown olarak çizilmesi
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** Mira'nın cevabı düz metin olarak, satır sonları korunarak yazılıyor; `#`, `**`, `|` gibi
  işaretler ekranda olduğu gibi görünüyor.
- **Yeni tasarımda:** Cevap Markdown olarak çizilecek: dört düzey başlık (ilk ikisi serif), madde ve
  numaralı listeler, satır içi kod ve kod bloğu, alıntı çubuğu, yatay çizgi, kalın/eğik/üstü çizili,
  altı çizili bağlantı, ve mono büyük harf başlıklı tablo. Balon içindeki ölçek dosya okuyucudakinden
  bir tık küçük olacak (örneğin birinci düzey başlık 19.5px'e karşı 25px).
- **Dayanak:** Prototipin cevap balonunu Markdown'dan kurması ve iki ayrı ölçek tanımlaması.

### Akarken yanıp sönen imleç
- **Tür:** eklenecek
- **Etiket:** görsel
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** Cevap parça parça uzuyor, sonuna hiçbir işaret konmuyor.
- **Yeni tasarımda:** Cevap akmaya devam ettiği sürece metnin sonunda 7×15px, yanıp sönen bir blok
  imleç duracak; son parça gelince imleç kaybolacak.
- **Dayanak:** Prototipin akış hâlindeki mesaja eklediği imleç.

### Cevabın altındaki dosya kartı
- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** Kart tıklanamayan bir kutu: uzantı rozeti, dosya adı ve "✓ saved to project" yazıyor,
  dosyayı açmak için ray listesine gitmek gerekiyor.
- **Yeni tasarımda:** Kart bir düğme olacak; sağında mono "Open ›" ipucu duracak ve basınca dosya
  okuyucuda açılacak. Açık olan dosyanın kartı zeminini ve çerçevesini koyultacak, ipucu da "open"a
  dönüşecek. Kart en çok 340px genişliğinde, 12px yarıçaplı olacak.
- **Dayanak:** Prototipin mesaj altındaki dosya kartı ve seçili hâli.

### "creating file…" ara hâli
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** Dosya yazılırken kesik çerçeveli küçük bir kutuda mono "creating file…" yazısı beliriyor;
  kutu yalnız yazı kadar geniş.
- **Yeni tasarımda:** Aynı kesik çerçeveli kutu en çok 340px genişliğinde olacak ve yazının solunda
  30×30, 7px yarıçaplı boş bir rozet yeri duracak — böylece doğacak dosyanın kartıyla aynı iskeleti
  taşıyacak.
- **Dayanak:** Prototipin üretim sırasındaki yer tutucu kartı ve B3 karesi.

### Bekleme noktalarının etiketi
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** Üç nokta beklerken üstünde yalnız "Mira" yazıyor, saat yok.
- **Yeni tasarımda:** Aynı yerde "QueenAgent" yazacak; üç nokta ile etiket arasındaki boşluk 10px
  olacak.
- **Dayanak:** Prototipin bekleme dalındaki etiket ve yerleşimi.

---

## Dosya rayı ve paneli

### Rayın başlığı bir katlama düğmesine dönüşüyor
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Dosya rayı ve paneli
- **Bugün:** Rayın tepesinde "Project files" yazan sabit bir başlık var; ray hep 320px açık duruyor ve
  kapatılamıyor.
- **Yeni tasarımda:** Başlık satırının tamamı bir düğme olacak: solunda "Project files", sağında mono
  dosya sayısı, en sağda bir "›" işareti. Basınca ray 46px genişliğinde dikey bir şeride inecek;
  şeritte yazı 90 derece döndürülmüş hâlde "Project files", yanında sayı ve bir "‹" duracak, şeride
  basınca ray geri açılacak. Genişlik geçişi 220ms sürecek.
- **Dayanak:** Prototipin ray başlığı, katlanmış şerit dalı ve genişlik hesabı.

### Raydaki dosya satırının içindeki düğmeler
- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Dosya rayı ve paneli
- **Bugün:** Raydaki her dosya satırının üstüne gelince "name" ve "×" düğmeleri beliriyor; sohbet
  ekranından dosya adı değiştirilebiliyor ve dosya silinebiliyor.
- **Yeni tasarımda:** karşılığı yok
- **Dayanak:** Prototipin ray satırı yalnız rozet, ad ve zamandan kurulu; silme yalnız proje
  ekranındaki listede var.

### Proje ekranındaki dosya satırında yeniden adlandırma
- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Dosya rayı ve paneli
- **Bugün:** Satırın üstüne gelince "name" düğmesi beliriyor ve tarayıcı kutusu "File name" diye
  soruyor; ad çakışırsa sunucu numaralı bir ad veriyor ve panel yeni ada geçiyor.
- **Yeni tasarımda:** karşılığı yok
- **Dayanak:** Prototipin dosya satırında yalnız silme düğmesi var.

### Dosya satırının iki satıra açılması
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Dosya rayı ve paneli
- **Bugün:** Rozet, ad ve zaman tek satırda yan yana duruyor; zaman sağa yaslı.
- **Yeni tasarımda:** Ad ile zaman alt alta duracak — ad 13.5px üstte, mono 11px zaman hemen altında —
  ve rozet solda ikisinin hizasında kalacak.
- **Dayanak:** Prototipin hem ray hem proje listesi satırının iç yerleşimi.

### Uzantı rozetinin biçimi
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Dosya rayı ve paneli
- **Bugün:** Rozet metin genişliğinde küçük bir etiket: 10px mono, 3/6px dolgu, 5px yarıçap.
- **Yeni tasarımda:** Rozet 30×30 sabit bir kare olacak: 7px yarıçap, ortalanmış 9.5px mono büyük
  harf, zemini #F0E7DE.
- **Dayanak:** Prototipin rozet stilini tek yerden tanımlaması; aynı rozet dosya kartında da
  kullanılıyor.

### Rayın kendi zemini
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Dosya rayı ve paneli
- **Bugün:** Rayın zemini yok, tuval rengini gösteriyor; soldan bir çizgiyle ayrılıyor.
- **Yeni tasarımda:** Ray ve proje ekranındaki okuma paneli kendi zeminini taşıyacak (#FBF9F5), çizgi
  yine solda kalacak.
- **Dayanak:** Prototipin ray ve proje paneli stilleri.

### Seçili dosya satırı
- **Tür:** eklenecek
- **Etiket:** görsel
- **Alan:** Dosya rayı ve paneli
- **Bugün:** Bir dosya okunurken listede hangi satırın açık olduğunu gösteren bir işaret yok.
- **Yeni tasarımda:** Okunan dosyanın satırı zeminini #EFEBE4 yapıp öyle kalacak; üstüne gelinen
  satır ise #F0ECE5 olacak.
- **Dayanak:** Prototipin satır stilini açık dosyaya bağlaması.

---

## Dosya okuma

### Okuyucunun gövdesi
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Dosya okuma
- **Bugün:** Dosya içeriği düz metin olarak, satır sonları korunarak 14px/1.75 ile yazılıyor.
- **Yeni tasarımda:** İçerik Markdown olarak çizilecek ve daha büyük bir ölçek kullanacak (14.5px,
  1.8 satır aralığı, 26/28px iç boşluk); başlıklar serif, tablolar mono başlıklı olacak.
- **Dayanak:** Prototipin okuyucu gövdesini belge ölçeğiyle Markdown'dan kurması.

### Okuyucunun alt bilgisi
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Dosya okuma
- **Bugün:** İçeriğin altında mono bir satır "md · 1.2 KB · 2h ago" yazıyor ve içerikle birlikte
  kayıyor.
- **Yeni tasarımda:** Aynı yerde "2h ago · project file" yazacak; satır panelin dibine sabitlenecek,
  üstünde bir ayırıcı çizgiyle duracak ve gövde kayarken yerinde kalacak. Başlık satırı da aynı
  şekilde tepeye sabitlenecek.
- **Dayanak:** Prototipin okuyucu üst ve alt çubukları ile üst bilgi metni.

### Proje ekranındaki panelin kapatma düğmesi
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Dosya okuma
- **Bugün:** Proje ekranında açılan panel de sohbet rayındaki panelin aynısı: solda "←" düğmesi, sonra
  ad, sonra "Download".
- **Yeni tasarımda:** Proje ekranındaki panel solda geri oku taşımayacak; sırayla dosya adı,
  "Download" ve en sağda bir "×" kapatma düğmesi duracak. Sohbet rayındaki panel ise "←" ile
  kalacak.
- **Dayanak:** Prototipin proje paneli ile ray paneli başlıklarının ayrı kurulması.

### İndirme sırasındaki dönen halka
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Dosya okuma
- **Bugün:** "Download" basılınca düğme "preparing…" yazısına ve 11px'lik, 1.5px kalınlığında bir
  dönen halkaya dönüşüyor; düğme sabit genişlikte kaldığı için yerinden oynamıyor.
- **Yeni tasarımda:** Aynı geçişte halka 2px kalınlığında olacak ve halka ile yazı arasındaki boşluk
  8px'e çıkacak.
- **Dayanak:** Prototipin indirme düğmesi ve C2 karesi.

---

## Durumlar ve hata

### Cevap alınamadığında görünen kart
- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Durumlar ve hata
- **Bugün:** Kart iki satır gösteriyor: "Couldn't get a response." ve altında mono ile servisin kendi
  sözleri; sağında "Try again" duruyor.
- **Yeni tasarımda:** Kart tek satır olacak: "Couldn't get a response. The connection dropped."
  yanında "Try again".
- **Not:** İki ifade birbirini tutmuyor — biri sebebi söylemiyor, öteki bağlantının koptuğunu
  söylüyor.
- **Dayanak:** Prototipin hata dalındaki tek cümlesi ve E2 karesi.

### Çevrimdışı şeridi
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Durumlar ve hata
- **Bugün:** Ana bölgenin tepesinde sarımsı bir şerit beliriyor (#fbf6ec zemin, #eadfc8 alt çizgi,
  #8a6a37 yazı) ve "You're offline. Messages are saved; Mira will answer when the connection is back."
  yazıyor.
- **Yeni tasarımda:** Şerit kızılımsı olacak (#F5E9E3 zemin, #E7D3C8 alt çizgi, #8A5237 yazı),
  cümlenin solunda 7px'lik dolu vurgu rengi bir nokta duracak ve metin "You're offline — messages are
  saved and will send when you reconnect." olacak.
- **Dayanak:** Prototipin çevrimdışı şeridi ve E3 karesi.

### İlk yükleme iskeleti
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Durumlar ve hata
- **Bugün:** İskelet listenin yerine giriyor: ana ekranda kart ızgarasında iki sütunlu 96px bloklar,
  sohbet ve dosya listelerinde 44px çubuklar; ekranın geri kalanı (selamlama, yazma kutusu, başlıklar)
  gerçek hâliyle duruyor.
- **Yeni tasarımda:** Yükleme sırasında ana bölgenin tamamı tek bir iskelete dönüşecek: 280×38 bir
  çubuk, 104px bir blok, 180×16 bir çubuk ve altında iki sütunlu dört adet 96px kart; kenar çubuğu bu
  sırada dolu görünecek. Blokların yanıp sönmesi 1.4s ve kademeli gecikmeli olacak.
- **Dayanak:** Prototipin yükleme dalı ve E1 karesi.

### Adresten gelen bulunamadı hâlleri
- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Durumlar ve hata
- **Bugün:** Olmayan bir projeye gidilince "That project does not exist.", olmayan bir sohbete
  gidilince "That chat does not exist.", açık dosya silinmişse "That file is gone." cümleleri
  görünüyor.
- **Yeni tasarımda:** karşılığı yok
- **Not:** Adres çubuğuyla doğrudan bir ekrana gidilebilmesini tasarım söylemiyor.
- **Dayanak:** Prototipte ekranlar arasında yalnız tıklamayla geçiliyor, olmayan bir hedef için dal
  yok.

---

## Arama

### Aramanın tamamı
- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Arama
- **Bugün:** Kenar çubuğundaki "Search" düğmesi ya da ⌘K/Ctrl+K ekranın üstünü karartan bir katman
  açıyor; içindeki kutuda "Search projects, chats and files..." yazıyor, yazdıkça sonuçlar
  listeleniyor, her sonucun solunda türünü söyleyen bir rozet ve sağında projesinin adı duruyor,
  hiçbir şey bulunmazsa "No results." yazıyor, seçilen sonuç ilgili ekranı açıyor.
- **Yeni tasarımda:** karşılığı yok
- **Dayanak:** Prototipte ne bir arama düğmesi ne bir katman var; tuvalin 14 karesi arama göstermiyor.

---

## Klavye ve erişilebilirlik

### Escape'in kapatma sırası
- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Klavye ve erişilebilirlik
- **Bugün:** Escape önce arama katmanını, o kapalıysa açık dosya panelini kapatıyor.
- **Yeni tasarımda:** Escape sırayla şunu kapatacak: proje satır menüsü, sonra silme onay kutusu,
  sonra beceri menüsü, sonra model menüsü, sonra açık dosya paneli — hangisi açıksa bir tuşta yalnız
  biri.
- **Dayanak:** Prototipin pencereye bağladığı tuş dinleyicisindeki sıra.

### Menülerin dışına tıklamak
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Klavye ve erişilebilirlik
- **Bugün:** Kapanabilir tek katman arama; dışına tıklayınca kapanıyor, içine tıklamak sayılmıyor.
- **Yeni tasarımda:** Model menüsü, beceri menüsü ve proje satır menüsünün her biri ekranın tamamını
  kaplayan görünmez bir yakalayıcıyla açılacak: menünün dışında herhangi bir yere tıklamak onu
  kapatacak. Silme onay kutusunda da karartının kendisine tıklamak iptal sayılacak.
- **Dayanak:** Prototipin her menüden önce serdiği tam ekran katman ve onay kutusunun iptal
  bağlantısı.

---

## Duyarlı yerleşim

### Kırılma noktaları
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Duyarlı yerleşim
- **Bugün:** Tek bir eşik var: 1100px altında kenar çubuğu daralıyor, ray sohbetin altına iniyor, iki
  sütunlu ızgaralar tek sütuna düşüyor ve yatay dolgular 32'den 20'ye iniyor.
- **Yeni tasarımda:** Üç eşik olacak — 1000px (ray ve panel alta iner, proje ızgarası tek sütuna
  düşer), 780px (yatay dolgular 20'ye iner, ana ekran kartları tek sütuna düşer, başlıklar 42→31 ve
  36→27px küçülür, sohbet satırındaki zaman kalkar), 640px (kenar çubuğu 172px'e ve dolgusu 14/10'a
  iner).
- **Dayanak:** Prototipin genişlikten türettiği üç eşik ve onlara bağlı stiller.

### Dar ekranda okuma paneli sütunun yerine geçiyor
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Duyarlı yerleşim
- **Bugün:** Dar pencerede dosya paneli açıldığında sohbet ya da proje sütunu yerinde kalıyor, panel
  onun altına ekleniyor ve sayfa uzuyor.
- **Yeni tasarımda:** 1000px altında bir dosya açıldığında sohbet sütunu (proje ekranındaysa proje
  sütunu) ekrandan tümüyle kalkacak ve okuyucu bütün alanı alacak; panel kapanınca sütun geri
  gelecek.
- **Dayanak:** Prototipin dar genişlikte sütun gösterme koşullarını önizlemeye bağlaması.

### Dar ekranda rayın yüksekliği
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Duyarlı yerleşim
- **Bugün:** Ray sohbetin altına indiğinde yüksekliği içeriğine göre serbest kalıyor ve sayfa
  bütünüyle kayıyor.
- **Yeni tasarımda:** Alta inen ray ekranın %44'ü kadar bir bant olacak, en çok 250px en az 150px; kendi
  içinde kayacak, sohbet üstte kendi kaydırmasını sürdürecek. Ray katlanmışsa bant yalnız başlık
  satırı kadar kalacak.
- **Dayanak:** Prototipin dar genişlikteki ray stili.

---

## Görsel dil

### Yıkıcı eylemin rengi
- **Tür:** eklenecek
- **Etiket:** görsel
- **Alan:** Görsel dil
- **Bugün:** Uygulamada kırmızı yok; silme düğmeleri gri duruyor, üstlerine gelince kızıl kahveye
  (#8a5237) dönüyor.
- **Yeni tasarımda:** Palete ayrı bir yıkıcı kırmızı girecek: #B23A2E (üstüne gelince #973026),
  yumuşak zemini #FDF4F2 ve çerçevesi #EBCFC9. Onay kutusundaki "Delete project" bu renkle dolu
  olacak — uygulamada dolu kırmızı bir düğme ilk kez görünecek.
- **Dayanak:** Prototipin proje silme düğmesi, satır menüsü ve onay kutusu.

### Ana ekran ile sohbet kutusunun yarıçapları
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Görsel dil
- **Bugün:** Yazma kutusu her ekranda 16px yarıçaplı ve 16/16/12 dolgulu.
- **Yeni tasarımda:** Ana ekrandaki kutu 16px kalacak, proje ve sohbet ekranındakiler 14px olacak ve
  dolguları 14/16/10'a inecek.
- **Dayanak:** Prototipin üç yazma kutusunu ayrı ayrı ölçülendirmesi.

### Dosya listesi kabının yarıçapı
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Görsel dil
- **Bugün:** Proje ekranındaki dosya listesinin kabı 12px yarıçaplı, satırları 8px.
- **Yeni tasarımda:** Kap 12px kalacak, ama ana ekran kartları 14px, menüler 12px, satır menüsü 11px,
  onay kutusu 14px, geri alma şeridi 10px ve alttaki koyu şerit 11px olacak — yarıçap kümesi bugünkü
  8/12/20 üçlüsünden geniş olacak.
- **Dayanak:** Prototipteki kutuların tek tek verilmiş yarıçapları.

---

## Uygulama geneli

### Bir haftadan eski zaman damgası
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Uygulama geneli
- **Bugün:** Zaman damgası "just now", "5m ago", "2h ago", "yesterday", "3 days ago" diye ilerliyor;
  bir haftayı geçince "12 Aug" gibi bir tarihe dönüyor.
- **Yeni tasarımda:** Bir haftayı geçen kayıt "1 week ago" diye görünecek.
- **Not:** Daha eski kayıtların nasıl yazılacağını tasarım söylemiyor.
- **Dayanak:** Prototipin sohbet ve dosya listelerinde kullandığı zaman metinleri.

### Sayaçların tekil hâli
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Uygulama geneli
- **Bugün:** Proje kartı "1 chat · 3 files" biçiminde tekil/çoğul ayrımı yapıyor; kenar çubuğundaki
  rozet yalnız dosya sayısını gösteriyor ve sıfırken hiç yazmıyor.
- **Yeni tasarımda:** Aynı biçim korunacak; ek olarak silme onayındaki cümle de aynı kuralla
  kurulacak ("1 chat and 1 file" ↔ "3 chats and 3 files") ve kenar çubuğundaki rozet sıfırken
  yazısını saydamlaştırıp yerini koruyacak.
- **Dayanak:** Prototipin proje kartı verisi, rozet stili ve onay cümlesi.

### Uzun proje adının başlık satırında sarması
- **Tür:** eklenecek
- **Etiket:** görsel
- **Alan:** Proje ekranı
- **Bugün:** Başlık, "Rename" düğmesiyle tek satırda duruyor ve satır sarmıyor.
- **Yeni tasarımda:** Başlık satırı sarabilecek: sığmayan düğmeler bir alt satıra inecek, satırın
  altındaki boşluk 30px olacak.
- **Dayanak:** Prototipin proje başlık satırındaki sarma ayarı.
