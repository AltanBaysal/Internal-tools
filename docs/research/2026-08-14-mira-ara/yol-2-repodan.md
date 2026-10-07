# Yol 2 · Repodan tasarıma

**Tarih:** 2026-08-14 · **Yön:** uygulamadan tasarıma

Bu belge iki işin bulgularını taşır:

- **İŞ A — fark çıkarma.** Bugünkü uygulamanın envanteri, QueenAgent tasarım v2'ye karşı sorgulanır
  (`eklenecek` · `değişecek` · `öksüz` türleri).
- **İŞ B — sadakat denetimi.** Aynı envanter, repodaki **Mira v1** belgelerine karşı sorgulanır
  (`düzeltilecek` türü).

> **İŞ A ikinci koşuda tamamlandı.** İlk koşuda QueenAgent tasarım v2 kaynağına erişecek araç kapalı
> olduğu için yalnız İŞ B yapılabilmişti; ikinci koşuda `HANDOFF.md`, `QueenAgent Handoff.dc.html`,
> `QueenAgent.dc.html` ve `QueenAgent Frames.dc.html` okundu ve İŞ A'nın bulguları belgenin ikinci
> bölümüne ("İŞ A — QueenAgent tasarım v2'ye karşı fark") eklendi. Aşağıdaki ilk blok — ürün
> adı bulgusu ve onu izleyen `düzeltilecek` bulguları — tasarım kaynağı görülmeden yazıldı; ürün adı
> bulgusundaki "tasarım söylemiyor" notu o kısıttan geliyor.

---

## Bulgular

### Ürünün adı iki taraf arasında ayrışıyor

- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Adlandırma ve kimlik
- **Bugün:** Uygulama açıldığında kenar çubuğunda "Mira" kelime-markası durur, cevap gelince mesajın
  üstünde "Mira · 11:04" yazar, boş dosya listesi "No files yet — start a chat and Mira will create
  one." der, ağ gidince şerit "Mira will answer when the connection is back." der ve modele giden
  yönerge "You are Mira, a small AI workspace." diye başlar.
- **Yeni tasarımda:** aynı yerlerde ürünün adı **QueenAgent** olur.
- **Not:** tasarım söylemiyor — tasarım kaynağı okunamadığı için ad değişiminin arayüzün hangi
  metinlerine dokunduğu, kelime-markasının biçimi ve modelin kendini nasıl tanıtacağı bu bulgudan
  çıkarılamadı.
- **Dayanak:** tasarım projesinin dosya adları (`QueenAgent Handoff`, `QueenAgent Frames`) ürünü
  QueenAgent diye anıyor; repo tarafındaki ad her yüzeyde Mira.

### Home'un composer'ında hedef etiketi hiç çıkmıyor

- **Tür:** düzeltilecek
- **Etiket:** görsel
- **Alan:** Composer ve model seçici
- **Bugün:** Home açılıp composer'a yazılmaya başlandığında kutunun altında yalnız Send butonu
  belirir; mesajın nereye gideceğini söyleyen mono satır hiçbir anda çıkmaz. Aynı kutu proje
  ekranında "the answer is saved as a file" yazar, Home'da yazmaz.
- **Tarifi neydi:** Mira v1'in Faz 5 kararı Home'un mono etiketini "a new project" olarak
  belirlemişti — Faz 2'de bilerek boş bırakılan satırın, hedefi karara bağlandığı anda dolması
  gerekiyordu.
- **Dayanak:** Mira v1 Faz 5 tasarım belgesi ("Composer'ın mono etiketi burada doğar… Home'un
  etiketi `a new project` yazar") ile Home ekranının bugünkü çizimi.

### Cevap beklenirken Mira etiketi saatsiz kalıyor

- **Tür:** düzeltilecek
- **Etiket:** görsel
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** Mesaj gönderilince üç noktanın üstünde yalnız "Mira" yazar; metin akmaya başlayınca da
  etiket "Mira" olarak kalır. Saat ancak akış bitip cevap kaydedildikten sonra belirir ve etiket
  "Mira · 11:04" hâline geçer.
- **Tarifi neydi:** Mira v1'in Madde 14'ü ekranda "MIRA · saat" etiketini ve cevap gelene kadar üç
  yanıp sönen noktayı birlikte istiyordu; etiketin saatli hâli beklemenin başında da orada olacaktı.
- **Dayanak:** Mira v1 yol haritası Madde 14 ile sohbet ekranının bekleme ve akış hâlleri.

### Reddedilen mesaj, motor arızasının kartını çıkarıyor

- **Tür:** düzeltilecek
- **Etiket:** davranış
- **Alan:** Durumlar ve hata
- **Bugün:** Sohbet ekranından gönderilen bir mesajı sunucu reddederse iyimser balon geri alınır ve
  yerine "Couldn't get a response." başlıklı sıcak tonlu kart ile **Try again** düğmesi çıkar — yani
  hiç gönderilememiş bir mesaj, cevabı alınamamış bir mesajın diliyle anlatılır ve Try again cevabı
  yeniden ister.
- **Tarifi neydi:** Mira v1'in Faz 5 kararı bu durumda "iyimser balon geri alınır ve **tek satır
  hata** çıkar" diyordu; "Couldn't get a response." + Try again kartı ise Faz 7'de akışın ölmesi için
  tanımlanmıştı.
- **Dayanak:** Mira v1 Faz 5 ve Faz 7 tasarım belgeleri ile sohbet ekranının gönderme hata yolu.

### Okunan dosya, projeden çıkıp dönünce kendiliğinden yeniden açılıyor

- **Tür:** düzeltilecek
- **Etiket:** davranış
- **Alan:** Dosya okuma
- **Bugün:** Bir projede dosya açıkken kenar çubuğundan başka bir projeye geçilince panel kapanmış
  gibi görünür; ilk projeye geri dönüldüğünde aynı dosya panelde yeniden açılır — kullanıcı onu
  kapatmadığı hâlde kapanmış, kapatmadığı için de geri gelmiş olur.
- **Tarifi neydi:** Mira v1'in Faz 10 kararı "açık dosya… **proje değişince kapanır**; aynı projenin
  iki ekranı arasında gidip gelirken açık kalır" diyordu — proje değişimi kapatma anıydı, gizleme
  anı değil.
- **Dayanak:** Mira v1 Faz 10 tasarım belgesi ile açık dosyanın projeyle birlikte tutulma biçimi.

### Model `.md` dışında bir uzantı isterse o uzantıyla yazılıyor

- **Tür:** düzeltilecek
- **Etiket:** davranış
- **Alan:** Ajan döngüsü
- **Bugün:** Model dosya yazmak istediğinde verdiği ad temizlenir — klasör yolu atılır, geçersiz
  karakterler `-` olur, hiç nokta yoksa sonuna `.md` eklenir. Ama ad zaten bir noktayla bitiyorsa
  uzantı olduğu gibi kabul edilir: "report.txt" isteyen bir model projeye `report.txt` bırakır ve
  dosya listesinde çipi `txt` olarak görünür.
- **Tarifi neydi:** Mira v1'in Faz 8 kararı yol haritasının "üretilen dosya `.md` dışına çıkacak mı"
  açık maddesini kapatırken "uzantı yoksa `.md` eklenir. **v1'de üretilen dosya markdown'dır**"
  diyordu; aracın kendi tarifi de modele "A short file name ending in .md." diyor.
- **Dayanak:** Mira v1 Faz 8 tasarım belgesi ile ad temizleme kuralının bugünkü hâli.

### Öğretici ikinci satır, dosya listesi doluyken de duruyor

- **Tür:** düzeltilecek
- **Etiket:** görsel
- **Alan:** Boş hâller
- **Bugün:** Proje ekranında dosya sütunu boşken "No files yet — start a chat and Mira will create
  one." çıkar ve altında "Chats create the files; you just open and read them." durur; sohbetler
  dosya üretip liste dolduktan sonra ilk cümle gider ama ikinci cümle sütunun altında kalmaya devam
  eder. Sohbetteki ray ise boşken bile ikinci cümleyi hiç göstermez.
- **Tarifi neydi:** Mira v1'in Faz 3 kararı iki cümleyi birlikte **boş** dosya listesinin öğretici
  metni olarak tanımlıyordu — "Boş dosya listesi öğretici konuşur: … Altında tasarımın ikinci satırı".
- **Dayanak:** Mira v1 Faz 3 tasarım belgesi ile proje ekranının dosya sütunu ve sohbetteki rayın boş
  hâli.

### Composer ve arama kutusuna klavyeyle girilince odak halkası çıkmıyor

- **Tür:** düzeltilecek
- **Etiket:** görsel
- **Alan:** Klavye ve erişilebilirlik
- **Bugün:** Sekme tuşuyla dolaşırken her düğme ve satır 2px'lik vurgu renkli bir halka kazanır; sıra
  composer'ın metin alanına ya da arama panelinin girdisine geldiğinde halka hiç çizilmez, odak
  görünmez olur.
- **Tarifi neydi:** Mira v1'in Faz 0 kararı odağı uygulama genelinde tek kural yapıyordu —
  "`2px solid var(--accent)`, `outline-offset: 2px`… **hiçbir madde kendi odak stilini yazmaz**".
- **Dayanak:** Mira v1 Faz 0 tasarım belgesi ile composer ve arama girdilerinin kendi odak
  kapatmaları.

### Ekran ve kart girişleri izin verilen hareket süresinin dışında

- **Tür:** düzeltilecek
- **Etiket:** görsel
- **Alan:** Görsel dil
- **Bugün:** Home açıldığında sütun 400ms'de aşağıdan yukarı süzülerek belirir, proje ve sohbet
  ekranlarının sütunu 350ms'de, cevabın altındaki dosya kartı 250ms'de, arama katmanı 150ms'de.
  Rayın 320'den 560px'e genişlemesi ise 220ms sürer.
- **Tarifi neydi:** Mira v1 hareketi tek bir banda kapatıyordu — "yalnız opaklık geçişleri
  (**180–220ms**) ve rayın genişlik geçişi (220ms)"; bugün yalnız ray ve şerit bu bandın içinde.
- **Dayanak:** Mira v1 tasarım belgesi 7. bölüm ve Faz 0 belgesinin hareket kuralı ile ekranların
  bugünkü giriş animasyonları.

### Kontrollerin yarıçapı 8px yerine 9px

- **Tür:** düzeltilecek
- **Etiket:** görsel
- **Alan:** Görsel dil
- **Bugün:** Kenar çubuğundaki Search kutusu, New chat düğmesi, proje satırları ve composer'ın Send
  düğmesi 9px yuvarlatılır; aynı ekrandaki sohbet satırları, dosya satırları ve şerit 8px
  yuvarlatılır — iki kenar yan yana durduğunda köşeler eşleşmez.
- **Tarifi neydi:** Mira v1 yarıçapları üçe kilitliyordu — "kontrol 8px · kart 12–14px · hap 20px".
- **Dayanak:** Mira v1 tasarım belgesi 7. bölüm ve Faz 0 belgesinin yarıçap tablosu ile kenar
  çubuğu/composer stilleri.

### Composer kutusunun yarıçapı kart bandının dışında

- **Tür:** düzeltilecek
- **Etiket:** görsel
- **Alan:** Composer ve model seçici
- **Bugün:** Home'da, proje ekranında ve sohbetin altında duran composer kutusu 16px yuvarlatılır;
  hemen yanındaki proje kartları ve dosya kartları 12–14px yuvarlatılır, yani composer aynı yüzey
  ailesinden daha yumuşak bir köşeyle durur.
- **Tarifi neydi:** Mira v1 kart yarıçapını 12–14px aralığına bağlamıştı ve bu aralığın dışında bir
  yüzey tanımlamıyordu.
- **Dayanak:** Mira v1 tasarım belgesi 7. bölüm ve Faz 0 belgesinin yarıçap tablosu ile composer'ın
  bugünkü stili.

### Sunucunun kendi cümlesi ekrana hiç ulaşmıyor

- **Tür:** düzeltilecek
- **Etiket:** davranış
- **Alan:** Durumlar ve hata
- **Bugün:** Bir dosyayı silip başka bir dosya aynı adı aldıktan sonra Undo'ya basılırsa şeridin
  altında "POST /api/projects/p1/trash/plan.md/restore failed with 409" yazar; sunucunun gönderdiği
  "a file by that name is back in the project" cümlesi hiçbir yerde görünmez. Aynısı proje listesi
  çekilemediğinde ve yeniden adlandırma reddedildiğinde de olur — ekrana çıkan satır yöntem, adres ve
  durum kodundan ibarettir. Yalnız motor arızası bu kuraldan kaçar: akışın içinden gelen hata,
  motorun gerçek satırını kartın altına yazar.
- **Tarifi neydi:** Mira v1 hata dilini iki yerde aynı cümleyle bağlamıştı — Faz 11 "altında
  **sunucunun kendi sözleri** yazar; sebep uydurulmaz", Faz 2 "sunucunun gerçek çıktısı gösterilir";
  reponun genel kuralı da hata metninin servisin söylediğini, HTTP kodu **ve gövdesiyle** taşımasını
  istiyor.
- **Dayanak:** Mira v1 Faz 2 ve Faz 11 tasarım belgeleri ile tarayıcının tek istek yolunun hata
  metnini kurma biçimi.

### Çekilemeyen liste, boş liste gibi konuşuyor

- **Tür:** düzeltilecek
- **Etiket:** davranış
- **Alan:** Boş hâller
- **Bugün:** Proje ekranı açılırken dosya listesi isteği başarısız olursa iskelet bloklar kaybolur ve
  yerine "No files yet — start a chat and Mira will create one." çıkar; sohbet listesi başarısız
  olursa sütun sessizce boşalır. Ekran, cevabı alamadığı bir soruya "hiç yok" diye cevap vermiş olur.
  Aynı durumda proje listesi bunu yapmaz — o, tek satırlık bir hata metni gösterir.
- **Tarifi neydi:** Mira v1'in Faz 14 kararı tam olarak bu ayrımı kurmak için `loading` alanını
  getirmişti — "boş-durum cümleleri yalnız yükleme bittikten sonra çıkar; bugüne kadar bir an için
  **yanlış cümle** görünüyordu" — ve Faz 2 listenin çekilememesi hâlinde tek satırlık bir hata metni
  istiyordu.
- **Dayanak:** Mira v1 Faz 2 ve Faz 14 tasarım belgeleri ile sohbet/dosya listelerinin hata yolu.

---

## İŞ A — QueenAgent tasarım v2'ye karşı fark

Aşağıdakiler ikinci koşuda, tasarım kaynağı açıldıktan sonra çıkarıldı. Envanter bugünkü
uygulamadan başlar; her madde QueenAgent tasarım v2'de aranır.

### Uygulama ilk açılışta Home'a değil, ilk projeye iniyor

- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Uygulama geneli
- **Bugün:** Adres kökten açıldığında Home gelir — composer ve proje kartları — ve bir projeye
  girmek için karta ya da kenar çubuğundaki satıra tıklamak gerekir.
- **Yeni tasarımda:** uygulama doğrudan **ilk projenin** ekranında açılır; Home'a ancak "New chat"
  ile gidilir, hiç proje yoksa açılan şey boş ekran olur.
- **Dayanak:** QueenAgent v2 handoff sayfasının 1. bölümü ("The app opens on the first project, not
  on a home screen") ve tuvaldeki D1 karesinin altyazısı.

### Projesi olmayan kullanıcıya ayrı bir ekran açılıyor

- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Boş hâller
- **Bugün:** Hiç proje yokken Home yine de açılır: composer, "Projects" başlığı, "New project"
  düğmesi ve altında boş bir ızgara durur; kenar çubuğunun "New chat" düğmesi de yerinde kalır ve
  basılınca aynı boş Home'a döner.
- **Yeni tasarımda:** composer ve ızgara hiç çizilmez, ortada tek bir ekran durur — "No projects
  yet", altında "Chats live inside a project, and the files they create stay there. Create a project
  to start." ve tek bir dolgulu **New project** düğmesi; kenar çubuğunun "New chat" düğmesi de
  devre dışı bırakılmaz, **gizlenir**.
- **Dayanak:** QueenAgent v2 handoff belgesinin 7. bölümü ve referans yapının boş hâl ekranı; tuvalde
  A0 karesi.

### Kenar çubuğunun logo karesi

- **Tür:** öksüz
- **Etiket:** görsel
- **Alan:** Adlandırma ve kimlik
- **Bugün:** Kenar çubuğunun tepesinde kelime-markasının solunda 22px'lik, 6px yuvarlatılmış, vurgu
  renginde dolu bir kare durur.
- **Yeni tasarımda:** karşılığı yok
- **Not:** tasarım söylemiyor — kaldırılan işaretin yerine bir şey konup konmayacağı yazılı değil;
  yalnız "no logo mark" deniyor.
- **Dayanak:** QueenAgent v2 handoff belgesinin 2. ve 11. bölümleri (kelime-markası "no logo mark",
  "Logo mark" bilerek kaldırılanlar arasında) ile bugünkü kenar çubuğunun markası.

### Arama bütünüyle kalkıyor

- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Arama
- **Bugün:** Kenar çubuğunda "Search" kutusu ve yanında "⌘K" rozeti durur; hem tıklayınca hem
  ⌘K/Ctrl+K ile ortada bir katman açılır, "Search projects, chats and files..." yazan girdi odağı
  alır, yazıldıkça en çok sekiz sonuç çipli satırlar hâlinde listelenir, hiçbiri yoksa "No results."
  yazar, bir satıra basınca ilgili projeye/sohbete gidilir ve dosya sonucu paneli açar.
- **Yeni tasarımda:** karşılığı yok
- **Not:** tasarım bunu üç parçasıyla birlikte (kenar çubuğu düğmesi, ⌘K, katman) "bilerek
  kaldırıldı, karar alınmadan geri getirilmesin" diye anıyor ve gerekçesini "proje yapısı zaten
  gezinmenin kendisi" diye veriyor.
- **Dayanak:** QueenAgent v2 handoff belgesinin 1. ve 11. bölümleri ile bugünkü arama katmanı.

### Proje satırının üstünde ⋯ menüsü beliriyor

- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Kenar çubuğu
- **Bugün:** Kenar çubuğundaki proje satırı yalnız açılabilir; üstüne gelince satır arka plan alır ve
  başka hiçbir kontrol çıkmaz, projeye ait işler ancak proje ekranına girilince görünür.
- **Yeni tasarımda:** satırın üstüne gelince sağında bir **⋯** düğmesi belirir ve 176px'lik bir
  açılır kutu açar — "Rename" ve kırmızı "Delete project"; kutu sabit konumlanır ve görünüm alanına
  kıstırılır ki kayan kenar çubuğu onu kesmesin, Esc ya da dışarı tıklama kapatır.
- **Dayanak:** QueenAgent v2 handoff belgesinin 2. ve 6. bölümleri ile referans yapının proje satırı.

### Recent chats yalnız seçili projenin sohbetlerini, en çok sekiz tanesini gösteriyor

- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Kenar çubuğu
- **Bugün:** "Recent chats" başlığı her ekranda durur ve altında tüm çalışma alanının sohbetleri en
  yenisi başta olmak üzere sayı sınırı olmadan sıralanır — Home'da hiç proje seçili değilken bile
  başlık orada kalır.
- **Yeni tasarımda:** bölüm ancak bir proje seçiliyken çizilir, hiç seçili yoksa başlığıyla birlikte
  yok olur, ve listelediği şey yalnız **o projenin** sohbetleridir, en çok **8** tanesi.
- **Dayanak:** QueenAgent v2 handoff belgesinin 2. ve 7. bölümleri ile bugünkü kenar çubuğunun
  sohbet listesi.

### Home'un selamlaması

- **Tür:** öksüz
- **Etiket:** görsel
- **Alan:** Home
- **Bugün:** Home açıldığında composer'ın üstünde 42px'lik Newsreader başlık olarak "Hi" durur.
- **Yeni tasarımda:** karşılığı yok
- **Not:** tasarım selamlamayı bilerek kaldırılanlar arasında sayıyor ve Home'un composer ile
  başlamasını istiyor.
- **Dayanak:** QueenAgent v2 handoff belgesinin 2. ve 11. bölümleri ("No greeting", "Hi, {name}"
  greeting kaldırıldı) ile Home'un bugünkü başlığı.

### Composer'ın altındaki üç öneri hapı

- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Home
- **Bugün:** Home'un composer'ının altında 20px yuvarlatılmış üç hap durur — "Summarize this week's
  notes", "Draft a meeting agenda", "Turn my sources into a table" — ve birine basmak taslağı o
  cümleyle doldurur, göndermez.
- **Yeni tasarımda:** karşılığı yok
- **Not:** tasarım "three suggested prompts"u bilerek kaldırılanlar arasında sayıyor.
- **Dayanak:** QueenAgent v2 handoff belgesinin 2. ve 11. bölümleri ile Home'un bugünkü hapları.

### Home'dan gönderilen mesaj artık yeni bir proje açmıyor

- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Home
- **Bugün:** Home'un kutusuna yazılıp gönderilince sunucu tek adımda **yeni bir proje** ve içinde bir
  sohbet açar, projenin adını da o ilk cümleden alır (42 karakter, taşarsa "…"), ve ekran o yeni
  sohbete gider.
- **Yeni tasarımda:** mesaj var olan bir projeye düşer — listedeki **ilk projeye** — ve orada yeni
  bir sohbet açar; proje doğmaz, adı da değişmez.
- **Dayanak:** QueenAgent v2 referans yapısının gönderme yolu (hedef proje seçili değilse listenin
  ilkidir) ve handoff sayfasının 1. bölümü ("no target-project label").

### Home sütununun üst boşluğu

- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Home
- **Bugün:** Home'un 720px'lik sütunu pencerenin tepesinden 14vh aşağıda başlar.
- **Yeni tasarımda:** aynı sütun 18vh aşağıda başlar.
- **Dayanak:** QueenAgent v2 referans yapısının Home sütunu ile bugünkü Home'un üst boşluğu.

### Projenin açıklama satırı

- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Proje ekranı
- **Bugün:** Her yeni proje "Click to add a description." açıklamasıyla doğar; bu cümle proje
  ekranında başlığın altında tıklanabilir bir paragraf olarak durur, tıklayınca tarayıcının kendi
  kutusu "Project description" diye sorar, ve aynı metin Home'daki proje kartında adın altında
  ikinci satır olarak görünür.
- **Yeni tasarımda:** karşılığı yok
- **Not:** tasarım açıklamayı hem veri alanı hem arayüz olarak bilerek kaldırılanlar arasında sayıyor;
  proje kartı da yalnız nokta, ad ve "N chats · N files" satırından oluşuyor.
- **Dayanak:** QueenAgent v2 handoff belgesinin 11. bölümü ("Project descriptions (data field and
  UI)") ve referans yapısının proje kartı ile bugünkü proje ekranı ve kartı.

### Proje ekranının "← back" düğmesi

- **Tür:** öksüz
- **Etiket:** görsel
- **Alan:** Proje ekranı
- **Bugün:** Proje ekranının en üstünde, başlığın üstünde, mono 12px "← back" düğmesi durur ve
  Home'a döner.
- **Yeni tasarımda:** karşılığı yok
- **Not:** tasarım bu düğmeyi bilerek kaldırılanlar arasında sayıyor; proje ekranı doğrudan başlıkla
  başlıyor.
- **Dayanak:** QueenAgent v2 handoff belgesinin 11. bölümü ("← back on the project screen") ve
  referans yapısının proje başlığı ile bugünkü proje ekranı.

### Bir proje silinebiliyor

- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Yıkıcı eylemler ve geri alma
- **Bugün:** Bir projeyi silmenin hiçbir yolu yok — ne proje ekranında ne kenar çubuğunda böyle bir
  düğme var, sunucu da böyle bir isteği tanımıyor; proje bir kez doğduktan sonra yalnız adı ve
  açıklaması değişebiliyor.
- **Yeni tasarımda:** iki giriş kapısı aynı kutuya çıkar — proje başlığının yanındaki kırmızı
  çerçeveli **Delete** (`#EBCFC9` çerçeve, `#B23A2E` yazı, üstüne gelince kırmızı dolar) ve kenar
  çubuğu satırının ⋯ menüsündeki "Delete project" — ve açılan kutu "Delete “X”?" diye sorup altında
  "The N chats and N files in this project are deleted with it. This can't be undone." der,
  **Cancel** ile **Delete project** sunar; içinde bulunulan proje silinirse ekran kalan ilk projeye
  düşer (hiç kalmazsa boş ekrana), başka bir proje silinirse açık sohbet ve kaydırma yeri
  kıpırdamaz.
- **Dayanak:** QueenAgent v2 handoff belgesinin 6. bölümü ve referans yapısının onay kutusu ile
  bugünkü uygulamanın proje işlemleri.

### Silinen proje için koyu bir şerit ve tek adımlık geri alma

- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Yıkıcı eylemler ve geri alma
- **Bugün:** Geri alma yalnız dosya için var: silinen dosya listenin üstünde açık renkli bir şeritle
  "File deleted." + "Undo" der. Projeye ait böyle bir şerit yok, çünkü proje silinemiyor.
- **Yeni tasarımda:** proje silinince ekranın **alt ortasında** koyu bir şerit (`#26231F`) belirir,
  "Project “X” deleted." yazar, yanında **Undo** ve bir kapatma çarpısı taşır; Undo projeyi listede
  **eski sırasına** geri koyar ve açar. Tek adımlıktır, geçmişi yoktur; dosyanınki listenin üstünde
  satır içi şerit olarak kalır.
- **Dayanak:** QueenAgent v2 handoff belgesinin 6. bölümü ve referans yapısının koyu şeridi ile
  bugünkü dosya geri alma şeridi.

### Sohbet silmek artık soru sormuyor

- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Yıkıcı eylemler ve geri alma
- **Bugün:** Proje ekranındaki sohbet satırının × düğmesine basılınca tarayıcının kendi onay kutusu
  "Delete this chat? Its files stay in the project." diye sorar; ancak onaylanırsa sohbet gider ve
  geri alma sunulmaz.
- **Yeni tasarımda:** × basılır basılmaz sohbet listeden çıkar — soru yok, şerit yok.
- **Not:** tasarım sohbet silmeden önce bir onay istemeyi **açık madde** olarak bırakıyor, yani
  bugünkü davranışın karşılığı v2'de henüz karara bağlanmamış bir istek.
- **Dayanak:** QueenAgent v2 handoff belgesinin 12. bölümü ("confirmation before deleting a chat")
  ve referans yapısının sohbet satırı ile bugünkü silme yolu.

### Sohbet satırının "name" düğmesi

- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Proje ekranı
- **Bugün:** Proje ekranındaki sohbet satırının üstüne gelince × düğmesinin yanında mono "name"
  düğmesi belirir; basınca tarayıcının kutusu "Chat title" diye sorar ve verilen başlık hem proje
  listesine hem kenar çubuğunun listesine işlenir.
- **Yeni tasarımda:** karşılığı yok
- **Not:** tasarım "inline chat renaming"i bilerek kaldırılanlar arasında sayıyor ve sohbetlerin
  yeniden adlandırılamayacağını ayrıca yazıyor.
- **Dayanak:** QueenAgent v2 handoff sayfasının 9. bölümü ve "Renaming is inline and cheap" kuralı
  ("Chats and files are not renameable") ile bugünkü sohbet satırı.

### Dosya satırının "name" düğmesi

- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Dosya rayı ve paneli
- **Bugün:** Hem proje ekranındaki hem sohbetteki dosya satırının üstüne gelince mono "name" düğmesi
  belirir; basınca "File name" sorulur, sunucu istenen ad doluysa numaralı bir ad döndürür, açık olan
  panel de dosyayı yeni adıyla izlemeye devam eder.
- **Yeni tasarımda:** karşılığı yok
- **Not:** tasarım dosya yeniden adlandırmayı **açık madde** olarak sayıyor, yani bugünkü davranışın
  karşılığı v2'de henüz kararlaştırılmamış bir istek.
- **Dayanak:** QueenAgent v2 handoff belgesinin 12. bölümü ("file rename") ve referans yapısının
  dosya satırı ile bugünkü yeniden adlandırma yolu.

### Composer'ın altındaki mono yardım satırı

- **Tür:** öksüz
- **Etiket:** görsel
- **Alan:** Composer ve model seçici
- **Bugün:** Proje ekranındaki kutunun altında, gönder düğmesinin solunda mono 11.5px "the answer is
  saved as a file" durur; sohbetin altındaki kutuda aynı yerde "save the answer as a file" yazar.
- **Yeni tasarımda:** karşılığı yok
- **Not:** tasarım hem `project: X` etiketini hem "save the answer as a file" yardım notlarını bilerek
  kaldırılanlar arasında sayıyor ve composer için "No helper text under the composer" diyor.
- **Dayanak:** QueenAgent v2 handoff belgesinin 11. bölümü ve handoff sayfasının 4. bölümü ile
  bugünkü composer'ın alt satırı.

### Composer'a bir model seçici geliyor

- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Composer ve model seçici
- **Bugün:** Hangi modelin cevap verdiği ekranda hiç görünmez ve hiç seçilemez; model sunucunun
  ayarından tek bir değer olarak gelir ve her sohbet için aynıdır.
- **Yeni tasarımda:** sohbet composer'ının sağ altında modelin adı ve küçük bir ok durur, üstüne
  gelince soluk bir dolgu alır; tıklayınca kutunun üstünde bir açılır katman açılır — mono "MODEL"
  başlığı ve dört satır, her biri tek satırlık açıklamasıyla, seçili olanda ✓: **Grok 4** ("Best for
  long, careful answers.", varsayılan), **Grok 4 Fast** ("Quicker replies, everyday questions."),
  **Grok 4 Heavy** ("Hard reasoning and long documents."), **Grok Code** ("Code, data and structured
  output."). Seçim **sohbete** yapışır, konuşmanın ortasında değiştirilebilir ve son seçim yeni
  sohbetlerin varsayılanı olur; katman dışarı tıklamayla ve Esc ile kapanır, görünüm alanına göre
  ölçülüp tetikleyicisine sağdan hizalanır, yukarıda yer yoksa aşağı çevrilir ve içi kaydırılır ki
  ekran dışına taşmasın.
- **Not:** tasarım seçimin sunucuda saklanmasını **açık madde** olarak bırakıyor.
- **Dayanak:** QueenAgent v2 handoff belgesinin 5. bölümü ve handoff sayfasının 4. bölümü ile
  bugünkü composer.

### Composer'a bir "Skills" seçici geliyor

- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Composer ve model seçici
- **Bugün:** Cevabın nasıl üretileceğine dair kullanıcıya sunulan hiçbir seçenek yok; modele verilen
  yönerge sabittir ve ekranda karşılığı bulunmaz.
- **Yeni tasarımda:** sohbet composer'ının sağ altında, modelin solunda bir **Skills** düğmesi durur;
  açılan katman model katmanıyla aynı biçimde dört satır sunar — **Web search** ("Look things up and
  cite the sources."), **Deep research** ("Read many sources before answering. Slower."), **Data &
  tables** ("Turn findings into structured tables."), **Code** ("Write and explain code in the
  answer.") — tek seçimliktir, seçili olana yeniden basmak seçimi temizler, seçiliyken düğme sıcak
  bir tonla boyanır ki menü açılmadan da etkin olduğu okunsun; iki katman birbirini kapatır ve seçim
  sohbete yapışır.
- **Not:** tasarım seçimin sunucuda saklanmasını **açık madde** olarak bırakıyor.
- **Dayanak:** QueenAgent v2 handoff sayfasının 4. bölümü ile bugünkü composer.

### Composer kutusunun yarıçapı ekrana göre ayrışıyor

- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Composer ve model seçici
- **Bugün:** Üç ekranın da composer kutusu aynı kalıptan çıkar ve hepsi 16px yuvarlatılır.
- **Yeni tasarımda:** Home'un kutusu 16px kalır, proje ekranının ve sohbetin kutusu 14px olur — yani
  yanlarında duran kart ailesiyle aynı köşeye iner.
- **Dayanak:** QueenAgent v2 referans yapısının üç composer'ı ile bugünkü tek composer stili.

### Cevap düz metin değil, Markdown olarak çiziliyor

- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** Modelin cevabı ne gelirse olduğu gibi yazılır: satır sonları korunur ama `##`, `**`,
  tablo çubukları ve kod çitleri ekranda ham işaret olarak görünür. Aynı şey panelde açılan dosya
  için de geçerli — dosyanın metni düz metin olarak çizilir.
- **Yeni tasarımda:** cevap Markdown olarak çizilir — `#`–`####` başlıklar, kalın, italik, üstü
  çizili, satır içi kod, çitli kod blokları, sıralı/sırasız listeler, tablolar, alıntılar, yatay
  çizgiler ve bağlantılar; **kullanıcının mesajı ham kalır** (yazılan `**test**` yıldızlarıyla
  görünür). İki ayrı ölçek vardır ve karışmaz: sohbette **balon ölçeği** (h1 19.5px / h2 17px
  Newsreader, h3 14.5px DM Sans 600), dosya panelinde **belge ölçeği** (h1 25px / h2 20px / h3
  15.5px). Akış sürerken metin her karede yeniden ayrıştırılır ve kapanmamış bir kod çiti çizim
  sırasında kapatılır ki yarım gelen blok yerleşimi bozmasın.
- **Dayanak:** QueenAgent v2 handoff belgesinin 4. bölümü ve handoff sayfasının 3. bölümü ile
  bugünkü cevap ve dosya paneli çizimi.

### Akan cevabın ucunda yanıp sönen bir blok imleç duruyor

- **Tür:** eklenecek
- **Etiket:** görsel
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** Parçalar geldikçe metin uzar ve sonunda hiçbir işaret olmaz; akışın sürdüğü yalnız
  metnin büyümesinden anlaşılır.
- **Yeni tasarımda:** akan metnin sonunda yanıp sönen bir blok imleç durur ve akış bitince kaybolur;
  metin karakter karakter (yaklaşık 5 karakter / 22ms) yazılır.
- **Not:** tasarım bu hızın prototipte zamanlayıcıyla taklit edildiğini ve arka uçtan gerçek akışı
  **açık madde** olarak taşıdığını söylüyor.
- **Dayanak:** QueenAgent v2 handoff belgesinin 3. bölümü (04 · Streaming) ile bugünkü akış çizimi.

### Kullanıcı satırının etiketi "You" değil, kişinin adı

- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** Kullanıcının balonunun üstünde mono, büyük harfli "You · 11:04" yazar.
- **Yeni tasarımda:** aynı yerde kişinin **adı** ve saat yazar (örnek veride "ALEX · 14:32"), yapay
  zekânın satırında ise ürünün adı ve saat durur.
- **Dayanak:** QueenAgent v2 referans yapısının mesaj etiketi ile bugünkü mesaj etiketi.

### Mesaj listesi kendiliğinden dibe iniyor

- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** Mesaj gönderildiğinde ve cevap aktığında liste kendiliğinden kaymaz; yeni gelen metin
  görünür alanın dışında kalırsa kullanıcı elle aşağı inmek zorundadır.
- **Yeni tasarımda:** yeni bir mesaj eklenince liste dibe atlar; akış sürerken ise ancak kullanıcı
  zaten dibe **220px'den yakınsa** dibe yapışır — yukarı çıkıp okuyan biri hiç bölünmez.
- **Dayanak:** QueenAgent v2 handoff belgesinin 3. bölümü (Auto-scroll rule) ve referans yapısının
  kaydırma kuralı ile bugünkü sohbetin kaydırma davranışı.

### Her cevap tam olarak bir dosya doğuruyor

- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Ajan döngüsü
- **Bugün:** Cevabın dosya doğurup doğurmayacağına model karar verir: yönerge ona "yalnız saklamaya
  değer bir şey istendiğinde" dosya yazmasını söyler, sıradan bir cevap dosyasız biter; buna karşılık
  tek bir turda birden çok dosya yazabilir ve mesajın altında o kadar kart belirir. Dosya yazılmadan
  önce adsız, kesik çizgili bir "creating file…" kutusu çıkar, dosya doğar doğmaz kart onun yerini
  alır ve listeler yeniden okunur.
- **Yeni tasarımda:** akış biter bitmez mesajın altına **tek** bir dolgulu dosya kartı takılır — çip
  + dosya adı + "✓ saved to project" — ve dosya aynı anda hem proje listesinin hem rayın başına
  eklenir; cevabın dosyasız bitmesi diye bir hâl yoktur.
- **Dayanak:** QueenAgent v2 handoff belgesinin 3. bölümü (05 · Saved) ve referans yapısının akış
  sonu ile bugünkü ajan döngüsü.

### Dosyanın adı modelin isteğinden değil, kullanıcının cümlesinden çıkıyor

- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Adlandırma ve kimlik
- **Bugün:** Adı model söyler; gelen ad temizlenir (klasör yolu atılır, geçersiz karakterler `-`
  olur, nokta yoksa `.md` eklenir) ve projede aynı ad varsa `plan.md` → `plan-2.md` diye numaralanır.
- **Yeni tasarımda:** ad kullanıcının gönderdiği cümleden türetilir — küçük harfe indirilir, harf ve
  rakam dışındakiler atılır, **ilk üç kelime** tirelerle birleştirilir ve sonuna `.md` eklenir; hiç
  kelime kalmazsa `note.md` olur.
- **Not:** tasarım aynı adın ikinci kez doğması hâlinde ne olacağını söylemiyor.
- **Dayanak:** QueenAgent v2 referans yapısının dosya doğurma adımı ile bugünkü ad temizleme kuralı.

### Transkriptteki dosya kartı bir kapı hâline geliyor

- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Dosya rayı ve paneli
- **Bugün:** Cevabın altındaki kart yalnız haber verir — çip, ad ve "✓ saved to project" — tıklanamaz;
  dosyayı açmanın tek yolu raydaki ya da proje ekranındaki satıra basmaktır.
- **Yeni tasarımda:** kart bir düğmedir, sağında mono "Open ›" ipucu taşır ve tıklayınca o dosyayı
  sağdaki panelde açar — ray katlanmışsa önce açılır; dosya ekrandayken ipucu "open" olur.
- **Dayanak:** QueenAgent v2 handoff belgesinin 3. bölümü ("File cards are the primary way into a
  file") ve handoff sayfasının "The file card in the transcript is a door" kuralı ile bugünkü kart.

### Açık dosyanın kartı ve ray satırı seçili görünüyor

- **Tür:** eklenecek
- **Etiket:** görsel
- **Alan:** Dosya rayı ve paneli
- **Bugün:** Panelde bir dosya açıkken listedeki satırı ve mesajın altındaki kartı hiçbir şey
  ayırmaz; hangi dosyanın okunduğu yalnız panelin başlığından anlaşılır.
- **Yeni tasarımda:** açık dosyanın ray satırı `#EFEBE4` zemin alır, transkriptteki kartı `#F4EFE7`
  zemine ve `#CFC3B2` çerçeveye geçer, ipucu da "open" der — panelin hangi dosyayı gösterdiği
  transkriptten okunur.
- **Dayanak:** QueenAgent v2 referans yapısının seçili satır ve kart stilleri ile bugünkü satır ve
  kart.

### Dosya rayı katlanabilir hâle geliyor

- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Dosya rayı ve paneli
- **Bugün:** Ray her zaman açıktır ve 320px yer kaplar; başlığı "Project files" yazan sabit bir
  etikettir, dosya sayısı hiçbir yerde durmaz ve rayı kapatmanın yolu yoktur.
- **Yeni tasarımda:** rayın başlığının kendisi katlama düğmesidir — etiket + dosya sayısı + şevron —
  ve basıldığında ray **46px'lik bir şeride** iner: etiket dikey yazılır, sayı okunur kalır, şeride
  tek tıklama rayı geri açar. Seçim oturum boyunca sohbetler ve projeler arasında korunur, bir
  dosyayı açan her eylem rayı zorla geri açar; 1000px'in altında ray sohbetin altına iner ve şerit
  yerine tek satırlık bir başlığa katlanır.
- **Dayanak:** QueenAgent v2 handoff belgesinin 2. bölümü ve handoff sayfasının "The rail is present
  but collapsible" kuralı ile bugünkü ray.

### Raydaki satırlar silme ve adlandırma düğmesi taşımıyor

- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Dosya rayı ve paneli
- **Bugün:** Sohbetin yanındaki raydaki dosya satırı, proje ekranındaki satırla birebir aynıdır:
  üstüne gelince "name" ve × düğmeleri belirir, buradan silinen dosya için de rayın içinde "File
  deleted. / Undo" şeridi çıkar.
- **Yeni tasarımda:** raydaki satır yalnız çip, ad ve zaman taşır ve tek işi dosyayı açmaktır; silme
  çarpısı ve geri alma şeridi proje ekranındaki dosya listesinde kalır.
- **Dayanak:** QueenAgent v2 referans yapısının ray satırı ile bugünkü ray satırı.

### Proje ekranında dosya okurken dosya sütunu ekrandan kalkıyor

- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Dosya okuma
- **Bugün:** Proje ekranında bir dosya açılınca sağda 560px'lik panel belirir ve ızgara tek sütuna
  iner; sohbetler ve dosyalar sütunları alt alta yığılarak ekranda kalmaya devam eder, yani aynı
  dosya listesi hem solda hem panelde durur.
- **Yeni tasarımda:** panel açıkken **dosyalar sütunu hiç çizilmez**; solda yalnız başlık, composer
  ve sohbet listesi kalır.
- **Dayanak:** QueenAgent v2 referans yapısının proje ekranı (panel açıkken dosya sütunu koşullu
  olarak düşer) ile bugünkü okuma yerleşimi.

### Proje panelinin kapatma düğmesi ok değil çarpı

- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Dosya okuma
- **Bugün:** Proje ekranında açılan panelin başlığının solunda mono bir "←" durur ve paneli kapatır;
  sohbetin rayında açılan panelde de aynı "←" vardır.
- **Yeni tasarımda:** proje ekranının panelinde ok yerine sağ uçta bir **×** durur, indirme
  düğmesinin yanında; sohbetin rayındaki panel "←" ile kapanmayı sürdürür.
- **Not:** tasarım "←"i yalnız proje ekranının paneli için bilerek kaldırılanlar arasında sayıyor.
- **Dayanak:** QueenAgent v2 handoff belgesinin 11. bölümü ("← in the project file panel (replaced by
  × close)") ve referans yapısının iki panel başlığı ile bugünkü panel başlığı.

### Panelin alt satırında boyut ve uzantı yerine dosyanın nereye ait olduğu yazıyor

- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Dosya okuma
- **Bugün:** Panelin en altında, çizginin altında mono satır uzantıyı, boyutu ve son değişme zamanını
  birleştirir — "md · 1.2 KB · 2h ago" gibi.
- **Yeni tasarımda:** aynı satır zamanı ve dosyanın kime ait olduğunu söyler — "2h ago · project
  file"; uzantı ve boyut orada durmaz.
- **Dayanak:** QueenAgent v2 referans yapısının panel alt satırı ve handoff sayfasının "Reading is a
  panel, not a page" kuralı ile bugünkü panel alt satırı.

### Hata kartı sebebini söylüyor, sunucunun sözlerini değil

- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Durumlar ve hata
- **Bugün:** Akış ölünce sıcak zeminli kartın içinde iki satır çıkar: üstte "Couldn't get a
  response.", altında mono renkte motorun kendi cümlesi; sağda **Try again**.
- **Yeni tasarımda:** kartta tek satır durur — "Couldn't get a response. The connection dropped." —
  ve sağında **Try again**; ikinci satır yoktur, kullanıcının mesajı yerinde kalır.
- **Dayanak:** QueenAgent v2 handoff sayfasının 7. bölümündeki `error` hâli ve referans yapısının
  hata kartı ile bugünkü hata kartı.

### Çevrimdışı şeridinin cümlesi ve rengi

- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Durumlar ve hata
- **Bugün:** Bağlantı gidince içeriğin üstünde sarımsı bir şerit belirir (`#fbf6ec` zemin, `#eadfc8`
  alt çizgi, `#8a6a37` yazı) ve "You're offline. Messages are saved; Mira will answer when the
  connection is back." der; başında hiçbir işaret yoktur.
- **Yeni tasarımda:** aynı yerde pembemsi-sıcak bir şerit belirir (`#F5E9E3` zemin, `#E7D3C8` alt
  çizgi, `#8A5237` yazı), başında 7px'lik vurgu renginde bir nokta taşır ve "You're offline —
  messages are saved and will send when you reconnect." der.
- **Dayanak:** QueenAgent v2 referans yapısının çevrimdışı şeridi ile bugünkü şerit.

### İskelet tek tek listelerin değil, içerik alanının tamamının yerine geçiyor

- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Durumlar ve hata
- **Bugün:** Bekleyen her liste kendi iskeletini çizer: Home'un ızgarasında iki sütunlu dört kart
  bloğu, proje ekranının sohbet ve dosya sütunlarında üçer 44px'lik satır, açılmamış sohbette iki
  68px'lik blok — hepsi 1.6s'de yanıp söner.
- **Yeni tasarımda:** yükleme sırasında içerik alanının tamamı tek bir iskelet düzenine bırakılır —
  280px'lik bir başlık çubuğu, 104px'lik bir blok, 180px'lik ince bir satır ve altında 2×2, 96px'lik
  kart bloğu, blokların yanıp sönmesi kademeli gecikmelerle — kenar çubuğu ise normal çizilir ki
  gezinme hiç kilitlenmesin.
- **Dayanak:** QueenAgent v2 handoff sayfasının 7. bölümündeki `loading` hâli ve referans yapısının
  iskelet düzeni ile bugünkü iskeletler.

### Adres yanlışsa ya da liste gelmezse çıkan satırlar

- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Durumlar ve hata
- **Bugün:** Adres çubuğuna olmayan bir proje kimliği yazılırsa ekran "That project does not exist.",
  olmayan bir sohbet için "That chat does not exist." der; panelde açılan dosya silinmişse "That file
  is gone." çıkar; proje listesi çekilemezse Home'da başlığın altında tek satırlık kırmızımsı bir
  hata metni belirir.
- **Yeni tasarımda:** karşılığı yok
- **Not:** tasarım söylemiyor — v2'nin verisi bellekte durduğu ve dosyaya kendi adresi verilmediği
  için yanlış kimlik ya da çekilemeyen liste diye bir hâl tarif edilmiyor.
- **Dayanak:** QueenAgent v2 handoff sayfasının 7. bölümündeki hâl listesi (yalnız idle, sending,
  typing, generating, error, loading, downloading, offline) ile bugünkü bulunamadı/hata satırları.

### ⌘K gidiyor, Esc'in kapatma sırası uzuyor

- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Klavye ve erişilebilirlik
- **Bugün:** ⌘K/Ctrl+K arama katmanını açar ve kapatır; Esc'e basıldığında önce arama katmanı, o
  kapalıysa açık dosya paneli kapanır ve başka hiçbir şeye dokunulmaz.
- **Yeni tasarımda:** ⌘K'nın bağlandığı bir şey kalmaz; Esc sırayla proje ⋯ menüsünü, silme onay
  kutusunu, Skills menüsünü, model menüsünü ve en son açık dosya panelini kapatır — hiçbir zaman
  geri gitmez.
- **Dayanak:** QueenAgent v2 handoff belgesinin 9. ve 11. bölümleri ile bugünkü klavye dinleyicisi.

### Liste satırları gerçek düğme değil

- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Klavye ve erişilebilirlik
- **Bugün:** Proje ekranının sohbet satırı ve her dosya satırı tıklanabilir birer kutudur, düğme
  değildir: sekmeyle sıraya girmezler, Enter/Boşluk ile açılmazlar, odak halkası almazlar — yalnız
  içlerindeki "name" ve × düğmeleri klavyeyle erişilebilir. Yıkıcı düğmeler kendini yalnız ekran
  okuyucuya tanıtır, fareyle üstünde durunca çıkan bir başlık taşımaz.
- **Yeni tasarımda:** her satır gerçek bir düğmedir ve klavyeyle sıraya girer; yıkıcı eylemler
  üstünde durunca okunan bir başlık taşır ("Delete", "Project options", "Dismiss" gibi).
- **Dayanak:** QueenAgent v2 handoff belgesinin 9. bölümü ("Every row is a real button; destructive
  actions carry a `title`") ve referans yapısının satırları ile bugünkü satırlar.

### Duyarlı yerleşim tek eşikten üç eşiğe çıkıyor

- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Duyarlı yerleşim
- **Bugün:** Tek bir eşik var, 1100px: kenar çubuğu 280px'ten 208px'e iner ve içi 16px/10px'e
  daralır, sohbet ve proje yerleşimleri sütuna dönüp ray/panel içeriğin altına geçer, ızgaralar tek
  sütuna iner, yanlardaki boşluk 32px'ten 20px'e düşer. Başlıklar her genişlikte aynı kalır (Home
  42px, proje 36px) ve sohbet satırının zamanı hiç gizlenmez. Eşiği belirleyen şey pencerenin
  genişliğidir.
- **Yeni tasarımda:** eşikler üçe çıkar ve pencereye değil, kabuğun **ölçülen genişliğine** bakılır
  (gömülü bir çerçevede de aynı bileşen uyum sağlasın diye). 1000px'in altında sohbetin dosya rayı
  sohbetin altına iner (yüksekliğin %44'ü, üstünde çizgi, katlanınca tek satırlık başlık), proje
  ekranı tek sütuna düşer ve açılan panel alanın tamamını alır; 780px'in altında Home'un kartları tek
  sütuna iner, başlıklar 42→31px ve 36→27px olur, boşluk 32→20px'e düşer, sohbet satırının zamanı ve
  "name" düğmesi gizlenir; 640px'in altında kenar çubuğu 172px'e iner. Kenar çubuğunun basamakları
  280 → 226 → 198 → 172px'tir.
- **Dayanak:** QueenAgent v2 handoff belgesinin 8. bölümü ve handoff sayfasının 6. bölümü ile
  bugünkü tek medya sorgusu.

### Sayfanın kendisi hiç kaymıyor, composer her boyda dibe çakılı kalıyor

- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Duyarlı yerleşim
- **Bugün:** Kabuk pencerenin yüksekliğini alır ama en az 600px'te durur; dar pencerelerde sohbet ve
  proje yerleşimleri kendileri kayan birer sütuna dönüşür, yani composer da mesajlarla birlikte
  yukarı kayar ve dipte durmaz.
- **Yeni tasarımda:** kabuk `100dvh`e sabitlenir ve sayfanın kendisi hiçbir boyda kaymaz; zincirdeki
  her sütun kendi taşmasını sıfırlar, böylece kayan tek şey mesaj listesi olur ve composer her
  pencere boyunda dibe çakılı kalır. Hiçbir genişlikte yatay kaydırma çıkmaz.
- **Dayanak:** QueenAgent v2 handoff belgesinin 2. bölümü (Scroll contract) ve handoff sayfasının 1.
  bölümü ile bugünkü kabuk ve dar pencere davranışı.

### Palete yıkıcı bir kırmızı giriyor

- **Tür:** eklenecek
- **Etiket:** görsel
- **Alan:** Görsel dil
- **Bugün:** Palette kırmızı yoktur: silme düğmeleri gri durur, üstüne gelince sıcak kahverengiye
  (`#8a5237`) döner, ve dolgulu kırmızı bir düğme hiçbir yerde çizilmez.
- **Yeni tasarımda:** yıkıcı eylemler için ayrı bir renk tanımlanır — proje başlığındaki Delete
  çerçevesi ve üstüne gelince dolan zemin, ⋯ menüsündeki "Delete project" satırı ve onay kutusunun
  dolgulu "Delete project" düğmesi bu renkle çizilir; vurgu rengi tek başına ve yalnız birincil
  eylemi işaretler.
- **Not:** tasarımın iki hâli bu rengin değerinde çelişiyor — handoff'un markdown hâlinin renk
  tablosu "Destructive `#8F4A2C`" diyor, aynı belgenin sayfa hâlindeki renk örneği ve referans yapının
  bütün yıkıcı yüzeyleri `#B23A2E` kullanıyor. İkisi de yazıldı, karar verilmedi.
- **Dayanak:** QueenAgent v2 handoff belgesinin 10. bölümü, handoff sayfasının 8. bölümü ve referans
  yapının silme yüzeyleri ile bugünkü palet.

### Vurgu renginin koyu hâli

- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Görsel dil
- **Bugün:** Dolgulu vurgu düğmelerinin (New chat, hazır durumdaki Send) üstüne gelince zemin
  `#8f4a2c`e koyulur; aynı değer bağlantıların üstüne gelme rengi olarak da kullanılır.
- **Yeni tasarımda:** dolgulu vurgu düğmeleri üstüne gelince `#9E5232`e koyulur; bağlantıların üstüne
  gelme rengi `#8F4A2C` olarak kalır — yani iki kullanım ayrışır.
- **Dayanak:** QueenAgent v2 handoff belgesinin 10. bölümü ("Accent `#B5623C` (hover `#9E5232`)") ve
  referans yapının düğme/bağlantı stilleri ile bugünkü tek koyu vurgu değeri.

### Dosya rayının kendi zemini oluyor

- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Dosya rayı ve paneli
- **Bugün:** Sohbetin sağındaki ray tuvalin zeminini paylaşır; onu ayıran tek şey soldaki 1px'lik
  çizgidir.
- **Yeni tasarımda:** ray kendi zeminini alır (`#FBF9F5`) ve çizgiyle birlikte tuvalden ayrı bir
  yüzey olarak durur — dar pencerede sohbetin altına indiğinde de aynı zeminle iner.
- **Dayanak:** QueenAgent v2 referans yapısının ray stili ile bugünkü ray.

### Dosya çipi hapdan kareye dönüyor

- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Görsel dil
- **Bugün:** Dosya satırlarının ve kartların solundaki uzantı çipi metne göre daralıp genişleyen
  küçük bir kutudur: 5px yuvarlatılmış, `#f0ece5` zeminli, 3px/6px içi boşluklu, mono 10px, büyük
  harfli.
- **Yeni tasarımda:** çip sabit 30×30px'lik, 7px yuvarlatılmış bir kareye dönüşür, zemini `#F0E7DE`
  olur ve harfleri mono 9.5px olarak ortalanır — böylece uzantı ne kadar uzun olursa olsun satırın
  hizası kaymaz.
- **Dayanak:** QueenAgent v2 referans yapısının çip tanımı ile bugünkü çip.

### "creating file…" kutusu beklemenin içine giriyor

- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** Model dosya yazmaya kalkınca kesik çizgili kutu, akan cevabın ve o ana kadar doğmuş
  kartların **altında**, kendi başına belirir ve içinde yalnız mono "creating file…" yazar.
- **Yeni tasarımda:** aynı kesik çizgili kutu yanıp sönen üç noktanın hemen **altında**, aynı bekleme
  bloğunun içinde belirir, solunda 30px'lik boş bir kare taşır ve en fazla 340px genişler.
- **Dayanak:** QueenAgent v2 referans yapısının bekleme bloğu ve tuvaldeki B3 karesi ile bugünkü
  kesik çizgili kutu.

### Ekran ve kart girişlerinin hareket süresi

- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Görsel dil
- **Bugün:** Home açılınca sütun 400ms'de aşağıdan yukarı süzülür, proje ve sohbet ekranlarının
  sütunu 350ms'de, cevabın altındaki dosya kartı 250ms'de, arama katmanı 150ms'de; rayın genişlemesi
  220ms sürer.
- **Yeni tasarımda:** hareketin tamamı **140–220ms**'lik opaklık geçişleri ile rayın 220ms'lik
  genişlik geçişinden ibaret olur ve yerleşmiş hiçbir öğe yana kaymaz.
- **Not:** tasarımın iki hâli de bu bandı yazıyor ama aynı tasarımın referans yapısı Home'un sütununu
  400ms'de, proje/sohbet sütununu 350ms'de ve 6px'lik bir yukarı süzülmeyle çiziyor — yani yazılı
  kural ile çalışan örnek birbirini tutmuyor. İkisi de yazıldı, karar verilmedi.
- **Dayanak:** QueenAgent v2 handoff belgesinin 10. bölümü, handoff sayfasının 8. bölümü ve referans
  yapının giriş animasyonları ile bugünkü giriş animasyonları.
