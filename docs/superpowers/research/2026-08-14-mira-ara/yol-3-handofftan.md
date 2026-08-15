# Yol 3 · Handoff'tan repoya

Yalnız tasarımın yazılı sözleşmesinden (metin hâli ve aynı sözleşmenin sayfa hâli) yürüyerek,
her kararın bugünkü uygulamadaki karşılığı arandı. Çizim dosyalarına bakılmadı.

Tasarım ürüne "QueenAgent" ve kendine "v2" diyor; repodaki taban "Mira v1". Aşağıda hangi taraftan
söz edildiği her bulguda açıkça yazılı.

---

## Adlandırma ve kimlik

### Ürünün adı her yerde değişiyor
- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Adlandırma ve kimlik
- **Bugün:** Mira v1'de kenar çubuğunun kelime markası "Mira" yazıyor, her cevabın üstündeki etiket "Mira" oluyor, boş dosya listesi "No files yet — start a chat and Mira will create one." diyor ve çevrimdışı şeridi "Mira will answer when the connection is back." diyor.
- **Yeni tasarımda:** aynı yerlerin hepsinde ad "QueenAgent" olacak; cevabın etiketi büyük harfli "QUEENAGENT · saat" biçiminde okunacak ve boş dosya cümlesi "No files yet — start a chat and QueenAgent will create one." olacak.
- **Dayanak:** sözleşme ürüne baştan sona QueenAgent diyor; boş hâl cümlesini de bu adla yazıyor.

### Projelerin renk noktası
- **Tür:** öksüz
- **Etiket:** görsel
- **Alan:** Adlandırma ve kimlik
- **Bugün:** Mira v1'de her proje doğduğunda kendine bir renk tonu alıyor ve o tondaki küçük yuvarlak nokta hem kenar çubuğu satırında hem proje kartında adın solunda çıkıyor; komşu proje silinince renk değişmiyor.
- **Yeni tasarımda:** karşılığı yok.
- **Not:** tasarım söylemiyor — sözleşme projeye bağlı bir renk kimliğinden hiç söz etmiyor.
- **Dayanak:** görsel dil bölümünde yalnız tek bir vurgu rengi ve o rengin yalnız birincil eylemi işaretlediği yazıyor; proje başına renk diye bir belirteç geçmiyor.

---

## Kenar çubuğu

### Logo işareti
- **Tür:** öksüz
- **Etiket:** görsel
- **Alan:** Kenar çubuğu
- **Bugün:** Mira v1'de kelime markasının solunda vurgu renginde dolu, 22×22 boyutunda ve 6px yarıçaplı bir kare duruyor.
- **Yeni tasarımda:** karşılığı yok.
- **Dayanak:** "Deliberately removed" listesi logo işaretini tek tek sayıyor; yerleşim bölümü de kelime markasını "no logo mark" diye tarif ediyor.

### Proje satırında ⋯ menüsü
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Kenar çubuğu
- **Bugün:** bugün yok — Mira v1'de kenar çubuğundaki proje satırının üstüne gelince yalnız satırın arka planı doluyor, satır içinde açılan bir menü çıkmıyor.
- **Yeni tasarımda:** satırın üstüne gelince bir ⋯ düğmesi belirecek, tıklayınca 176px genişliğinde bir açılır kutu açılacak, içinde "Rename" ve kırmızı "Delete project" olacak; kutu ekrana göre konumlanıp sınırlandığı için kaydırılan kenar çubuğu onu kırpamayacak, Esc ya da dışarı tıklama kapatacak.
- **Dayanak:** yerleşim tablosu ve yıkıcı eylemler bölümü aynı menüyü iki kez tarif ediyor.

### Kenar çubuğunda proje ekleme düğmesi ve satır rozeti
- **Tür:** öksüz
- **Etiket:** görsel
- **Alan:** Kenar çubuğu
- **Bugün:** Mira v1'de "Projects" başlığının sağında bir "+" düğmesi duruyor ve tıklayınca yeni proje yaratılıyor; ayrıca her proje satırının sağ ucunda o projenin dosya sayısı tek başına küçük bir mono sayı olarak yazıyor.
- **Yeni tasarımda:** karşılığı yok.
- **Not:** tasarım söylemiyor — sözleşme kenar çubuğunun içeriğini "kelime markası, New chat, Projects, Recent chats" diye sayarken ne bir ekleme düğmesinden ne de satır rozetinden söz ediyor.
- **Dayanak:** yerleşim tablosunun kenar çubuğu satırı ve yapı bölümündeki kenar çubuğu dökümü.

### Recent chats'in kapsamı
- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Kenar çubuğu
- **Bugün:** Mira v1'de "Recent chats" başlığı hiç proje seçilmemişken bile duruyor ve tüm çalışma alanındaki sohbetleri, sayı sınırı olmadan, en son konuşulandan geriye doğru listeliyor.
- **Yeni tasarımda:** bölüm yalnız bir proje seçiliyken görünecek, seçili olmadığında bütünüyle yok olacak; göründüğünde yalnız o projenin sohbetlerini ve en çok 8 tanesini listeleyecek.
- **Dayanak:** boş hâller bölümü ve yapı bölümündeki kenar çubuğu tarifi aynı kuralı söylüyor.

---

## Uygulama geneli

### Uygulamanın açıldığı ekran
- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Uygulama geneli
- **Bugün:** Mira v1 kök adreste açıldığında Home geliyor: selamlama, composer ve proje kartları.
- **Yeni tasarımda:** uygulama doğrudan ilk projenin ekranıyla açılacak; hiç proje yoksa onun yerine boş çalışma alanı ekranı gelecek, Home'a yalnız "New chat" ile ulaşılacak.
- **Not:** tasarım söylemiyor — sözleşmenin metin hâli açılış ekranını hiç anmıyor, bu karar yalnız sayfa hâlinde geçiyor.
- **Dayanak:** sayfa hâlinin yapı bölümündeki "Landing" satırı.

### Kabuğun yüksekliği ve sayfanın kendisinin kaymaması
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Uygulama geneli
- **Bugün:** Mira v1'de kabuk kendisine sarmalayıcının tam yüksekliğini alıyor ama en az 600px yüksekliğinde kalıyor; pencere bundan kısaldığında kabuk görüntü alanını aşıyor.
- **Yeni tasarımda:** kabuk her zaman tam olarak görüntü alanı yüksekliğinde ve sabit olacak, sayfanın kendisi hiçbir boyda kaymayacak — yalnız iç bölgeler kayacak.
- **Dayanak:** yerleşim bölümündeki kaydırma sözleşmesi.

---

## Arama

### Arama bütünüyle kalkıyor
- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Arama
- **Bugün:** Mira v1'de kenar çubuğunun en üstünde "Search" yazan ve sağında "⌘K" rozeti taşıyan bir düğme duruyor; ona tıklayınca ya da ⌘K/Ctrl+K'ya basınca ekranı karartan bir katman üstünde "Search projects, chats and files..." kutusu açılıyor, yazdıkça proje/sohbet/dosya sonuçları türü ve hangi projede olduğuyla listeleniyor, bir sonuca tıklamak o yere gidip dosyaysa panelde açıyor, hiç sonuç yoksa "No results." yazıyor; ⌘K ikinci kez basıldığında kapatıyor.
- **Yeni tasarımda:** karşılığı yok.
- **Dayanak:** "Deliberately removed" listesi aramayı üç parçasıyla (kenar çubuğu düğmesi, ⌘K, modal) sayıyor; zihinsel model bölümü de "there is no ... search" diyor.

---

## Home

### Selamlama başlığı
- **Tür:** öksüz
- **Etiket:** görsel
- **Alan:** Home
- **Bugün:** Mira v1'de Home açıldığında composer'ın üstünde 42px Newsreader ile "Hi" başlığı duruyor.
- **Yeni tasarımda:** karşılığı yok.
- **Dayanak:** "Deliberately removed" listesi "Hi, {name}" selamlamasını sayıyor; yerleşim tablosu Home'u "composer + projects grid, no greeting" diye tarif ediyor.

### Önerilen üç istem
- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Home
- **Bugün:** Mira v1'de Home composer'ının altında "Summarize this week's notes", "Draft a meeting agenda", "Turn my sources into a table" yazan üç hap biçimli düğme duruyor; birine tıklamak taslağı o cümleyle dolduruyor, göndermiyor.
- **Yeni tasarımda:** karşılığı yok.
- **Dayanak:** "Deliberately removed" listesindeki "three suggested prompts" ve Home tarifindeki "no suggested prompts".

### Composer altındaki yardımcı notlar
- **Tür:** öksüz
- **Etiket:** görsel
- **Alan:** Composer ve model seçici
- **Bugün:** Mira v1'de Home composer'ının yer tutucusu "Ask anything — Mira saves the answer to your project as a file." diyor, proje ekranı composer'ının altında mono "the answer is saved as a file" ve sohbet composer'ının altında "save the answer as a file" yazıyor.
- **Yeni tasarımda:** karşılığı yok — composer'ın altında hiç yardımcı metin olmayacak.
- **Dayanak:** "Deliberately removed" listesindeki "save the answer as a file helper notes" ve composer bölümünün son cümlesi "No helper text under the composer."

---

## Proje ekranı

### Proje açıklaması
- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Proje ekranı
- **Bugün:** Mira v1'de her yeni proje "Click to add a description." açıklamasıyla doğuyor; bu satır proje başlığının altında ve proje kartının içinde görünüyor, satıra tıklamak açıklamayı soran bir kutu açıyor ve yazılan metin saklanıyor.
- **Yeni tasarımda:** karşılığı yok — ne alan ne de arayüzde bir yeri kalacak.
- **Dayanak:** "Deliberately removed" listesindeki "project descriptions (data field and UI)" ve yapı bölümünün proje satırındaki "No description field".

### Proje ekranındaki "← back"
- **Tür:** öksüz
- **Etiket:** görsel
- **Alan:** Proje ekranı
- **Bugün:** Mira v1'de proje ekranının en üstünde mono "← back" düğmesi duruyor ve Home'a götürüyor.
- **Yeni tasarımda:** karşılığı yok.
- **Dayanak:** "Deliberately removed" listesindeki "← back on the project screen".

### Dosya listesinin altındaki öğüt satırı
- **Tür:** öksüz
- **Etiket:** görsel
- **Alan:** Proje ekranı
- **Bugün:** Mira v1'de proje ekranındaki dosya listesinin altında, liste dolu olsa bile "Chats create the files; you just open and read them." yazan bir satır duruyor.
- **Yeni tasarımda:** karşılığı yok.
- **Not:** tasarım söylemiyor — sözleşme dolu bir dosya listesinin altına konacak açıklayıcı metinden hiç söz etmiyor, boş hâli ise "instructive, never decorative" diye sınırlıyor.
- **Dayanak:** boş hâller bölümü ve kural kartlarındaki "Empty is instructive, not decorative".

### Dosya satırının ikincil metni
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Dosya rayı ve paneli
- **Bugün:** Mira v1'de bir dosya satırı solda uzantıyı taşıyan mono bir çip, ortada dosya adı, sağda mono göreli zaman ("2h ago") biçiminde okunuyor.
- **Yeni tasarımda:** satır "project file · 2h ago" diye okunacak — dosyanın projeye ait olduğu satırın kendisinde yazacak.
- **Dayanak:** kural kartlarındaki "Files are project-owned" maddesi satırın nasıl okunacağını doğrudan veriyor.

---

## Dosya rayı ve paneli

### Ray katlanamıyor
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Dosya rayı ve paneli
- **Bugün:** Mira v1'de sohbet ekranının sağındaki 320px'lik dosya rayı her zaman açık; başlığı "Project files" yazan sabit bir etiket, tıklanabilir bir yanı yok, kapatılamıyor.
- **Yeni tasarımda:** ray başlığının kendisi katlama denetimi olacak — etiket + dosya sayısı + chevron; tıklayınca ray 46px'lik bir şeride inecek, şeritte etiket dikey yazılacak ve sayı okunur kalacak, şeride bir kez tıklamak geri açacak; seçim oturum boyunca sohbetler ve projeler arasında korunacak ve bir dosyayı açan her eylem rayı zorla genişletecek.
- **Dayanak:** yerleşim bölümündeki "Project files rail" paragrafı ve kural kartlarındaki "The rail is present but collapsible".

### Ray başlığında dosya sayısı
- **Tür:** eklenecek
- **Etiket:** görsel
- **Alan:** Dosya rayı ve paneli
- **Bugün:** bugün yok — Mira v1'de ray başlığı yalnız "Project files" yazıyor, kaç dosya olduğunu söylemiyor.
- **Yeni tasarımda:** başlıkta etiketin yanında dosya sayısı duracak ve ray katlandığında bile o sayı okunur kalacak.
- **Dayanak:** yerleşim bölümündeki ray tarifi ve kural kartındaki "label + count + chevron".

### Dosya panelinin kapatma denetimi
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Dosya okuma
- **Bugün:** Mira v1'de açık dosya panelinin başında mono "←" düğmesi duruyor ve tıklamak paneli kapatıyor.
- **Yeni tasarımda:** o denetim "×" olacak.
- **Dayanak:** "Deliberately removed" listesindeki "← in the project file panel (replaced by × close)" ve yapı bölümündeki "× closes it".

### Dosya açılınca ray listesi yok oluyor
- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Dosya rayı ve paneli
- **Bugün:** Mira v1'de sohbet ekranında bir dosya açılınca ray 560px'e genişliyor ama içindeki dosya listesi bütünüyle okuyucuyla değişiyor; açık dosyanın hangi satır olduğu görünmüyor, panel kapanmadan başka bir dosyaya geçilemiyor.
- **Yeni tasarımda:** ray 560px'e genişlerken dosya satırları yerinde kalacak ve açık dosyanın satırı seçili görünecek, böylece panelin hangi dosyayı gösterdiği her an belli olacak.
- **Dayanak:** kural kartlarındaki "The file card in the transcript is a door" ve çekirdek döngü bölümündeki "both its message card and its rail row show a selected state".

---

## Çekirdek döngü ve cevap akışı

### Mesajın altındaki dosya kartı bir kapı değil
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** Mira v1'de cevabın altına çıkan dosya kartı çip + dosya adı + "✓ saved to project" gösteriyor ama tıklanamıyor; dosyayı açmanın tek yolu sağdaki listeden satırına tıklamak.
- **Yeni tasarımda:** kartın sağ ucunda "Open ›" ipucu duracak, karta tıklamak o dosyayı sağdaki panelde açacak (ray kapalıysa önce açılacak), dosya açıkken kart seçili görünecek ve ipucu "open" yazacak.
- **Dayanak:** çekirdek döngü bölümündeki "File cards are the primary way into a file" paragrafı ve aynı kuralı tekrar eden kural kartı.

### Otomatik kaydırma kuralı
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** bugün yok — Mira v1'de yeni mesaj gelince ya da cevap akarken mesaj listesi kendiliğinden hiç kaydırılmıyor, kullanıcı listeyi kendi eliyle aşağı çekiyor.
- **Yeni tasarımda:** yeni bir mesajda liste en alta atlayacak; cevap akarken alta yapışması yalnız kullanıcı zaten alta 220px'den yakınsa sürecek, yukarı çıkıp okuyan biri asla kesilmeyecek.
- **Dayanak:** çekirdek döngü bölümündeki "Auto-scroll rule" paragrafı.

### Cevap beklenirken görünen etiket
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** Mira v1'de cevap beklenirken üç yanıp sönen nokta çıkıyor ama üstündeki etiket yalnız ürün adını yazıyor, saat taşımıyor; akış başladığında da etiket saatsiz kalıyor.
- **Yeni tasarımda:** noktaların üstündeki etiket "QUEENAGENT · saat" biçiminde okunacak.
- **Dayanak:** çekirdek döngünün 03 adımı.

### Akan cevabın ucundaki imleç
- **Tür:** eklenecek
- **Etiket:** görsel
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** bugün yok — Mira v1'de cevap parça parça birikirken metnin ucunda hiçbir imleç görünmüyor.
- **Yeni tasarımda:** akan metnin ucunda yanıp sönen bir blok imleç duracak ve akış bitince kaybolacak.
- **Dayanak:** çekirdek döngünün 04 adımı.

### Dosya yaratılırken noktaların da durması
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Durumlar ve hata
- **Bugün:** Mira v1'de üç nokta yalnız ilk metin parçası gelene kadar duruyor; dosya yaratılırken ekranda kesik çizgili "creating file…" kartı tek başına kalıyor, noktalar çoktan kaybolmuş oluyor.
- **Yeni tasarımda:** dosya yaratılırken noktalar ve kesik çizgili "creating file…" kartı birlikte duracak.
- **Dayanak:** sayfa hâlinin "States to build" bölümündeki `generating` durumu ("Dots + dashed 'creating file…' card").

### Hata kartının ikinci cümlesi
- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Durumlar ve hata
- **Bugün:** Mira v1'de cevap alınamayınca sıcak zeminli kartta "Couldn't get a response." yazıyor ve altında sunucunun kendi sözleri mono olarak duruyor; sağda "Try again" düğmesi var, kullanıcının mesajı yerinde kalıyor.
- **Yeni tasarımda:** kart "Couldn't get a response. The connection dropped." diye okunacak.
- **Dayanak:** sayfa hâlinin "States to build" bölümündeki `error` durumu.

---

## Markdown render

### Cevaplar Markdown olarak çizilmiyor
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** bugün yok — Mira v1'de cevap düz metin olarak, satır sonları korunarak yazılıyor; `#`, `**`, tablo ya da kod bloğu yazıldığında işaretlerin kendisi ekranda görünüyor. Kullanıcının mesajı da düz metin duruyor.
- **Yeni tasarımda:** cevaplar Markdown olarak çizilecek — `#`–`####` başlıklar, kalın, italik, üstü çizili, satır içi kod, çitli kod blokları, sıralı/sırasız listeler, tablolar, alıntılar, yatay çizgiler ve bağlantılar. Kullanıcının mesajı ham kalmayı sürdürecek: `**test**` yazınca yıldızlar görünecek.
- **Dayanak:** Markdown render bölümünün ilk paragrafı ve desteklenenler listesi.

### İki ayrı tipografi ölçeği
- **Tür:** eklenecek
- **Etiket:** görsel
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** bugün yok — Mira v1'de cevap metni tek bir boyutta (15.5px, 1.75 satır aralığı) ve dosya paneli tek bir boyutta (14px, 1.75) çiziliyor; ikisinde de başlık ölçeği diye bir şey yok.
- **Yeni tasarımda:** sohbet içinde balon ölçeği geçerli olacak — h1 19.5px / h2 17px Newsreader, h3 14.5px DM Sans 600; dosya panelinde belge ölçeği geçerli olacak — h1 25px / h2 20px / h3 15.5px; sayfa düzeyindeki başlık boyutları balonun içine hiç sızmayacak.
- **Dayanak:** Markdown render bölümündeki iki ölçek tablosu.

### Yarım gelen kod bloğunun kapatılması
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Cevap akışı ve Markdown
- **Bugün:** bugün yok — Mira v1'de akan metin ayrıştırılmadığı için yarım gelen bir kod bloğu diye bir durum oluşmuyor.
- **Yeni tasarımda:** akan metin her karede yeniden ayrıştırılacak ve kapanmamış bir kod çiti çizim sırasında kapatılacak, böylece yarım gelmiş bir blok yerleşimi hiç bozmayacak.
- **Dayanak:** Markdown render bölümündeki "Streaming safety" satırı.

---

## Composer ve model seçici

### Model seçici
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Composer ve model seçici
- **Bugün:** bugün yok — Mira v1'de her cevap tek bir sabit modelle üretiliyor, bu model arayüzde hiç görünmüyor ve kullanıcı onu göremiyor da değiştiremiyor da.
- **Yeni tasarımda:** sohbet composer'ında bir model düğmesi duracak; kapalıyken yalnız model adı ve küçük bir chevron gösterecek, üstüne gelince hafif bir dolgu alacak; açılınca composer'ın üstünde "MODEL" mono etiketli bir açılır kutu çıkacak, dört seçenek (Grok 4 — varsayılan, Grok 4 Fast, Grok 4 Heavy, Grok Code) birer satırlık açıklamasıyla listelenecek ve etkin olanın yanında "✓" duracak; seçim sohbete bağlı olacak, konuşmanın ortasında değiştirilebilecek ve son seçim yeni sohbetlerin varsayılanı olacak; dışarı tıklama ya da Esc kapatacak.
- **Dayanak:** model seçici bölümü ve sayfa hâlinin composer denetimleri bölümü.

### Model düğmesinin composer içindeki yeri
- **Tür:** eklenecek
- **Etiket:** görsel
- **Alan:** Composer ve model seçici
- **Bugün:** bugün yok — Mira v1'de composer'ın alt satırında yalnız (varsa) yardımcı not solda ve "Send" sağda duruyor.
- **Yeni tasarımda:** sözleşmenin iki hâli aynı düğmeyi iki ayrı yere koyuyor: metin hâli model seçiciyi sohbet composer'ının sol altına koyuyor; sayfa hâli sağ alta ve "Skills · model · Send" sırasına koyuyor.
- **Dayanak:** metin hâlindeki "Bottom-left of the chat composer" ile sayfa hâlindeki "Bottom-right of the chat composer, in order: Skills · model · Send" çelişiyor.

### Skills seçici
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Composer ve model seçici
- **Bugün:** bugün yok — Mira v1'de composer'da beceri seçimi diye bir denetim hiç yok.
- **Yeni tasarımda:** model düğmesinin yanında bir "Skills" düğmesi olacak; tek seçimli, seçenekleri Web search, Deep research, Data & tables, Code; etkin olanı yeniden seçmek seçimi temizleyecek; bir beceri seçiliyken düğme sıcak bir tonla boyanıp menü açılmadan da etkin olduğunu belli edecek; seçim sohbete bağlı kalacak ve son seçim yeni sohbetlerin varsayılanı olacak; iki açılır kutu birbirini kapatacak, Esc ikisini de kapatacak.
- **Dayanak:** sayfa hâlinin composer denetimleri bölümü.

### Açılır kutunun ekrana sığması
- **Tür:** eklenecek
- **Etiket:** görsel
- **Alan:** Composer ve model seçici
- **Bugün:** bugün yok — Mira v1'de composer'da açılan bir kutu bulunmadığı için konumlanma kuralı da yok.
- **Yeni tasarımda:** sözleşmenin iki hâli iki ayrı kural veriyor: metin hâli kutuyu composer kartının genişliğiyle sınırlayıp taşmasını böyle önlüyor; sayfa hâli kutuyu görüntü alanına göre ölçüp tetikleyicisine sağdan hizalıyor, üstte yer yoksa alta çeviriyor ve azami yükseklikle içeriden kaydırılabilir yapıyor.
- **Dayanak:** metin hâlindeki "Constrained to the composer card's width" ile sayfa hâlindeki "Placement" satırı.

---

## Yıkıcı eylemler ve geri alma

### Proje silme
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Yıkıcı eylemler ve geri alma
- **Bugün:** bugün yok — Mira v1'de bir projeyi silmenin hiçbir yolu yok; proje ekranında başlığın yanında yalnız "Rename" duruyor.
- **Yeni tasarımda:** silme bir modal açacak: başlık "Delete “X”?", altında "The N chats and N files in this project are deleted with it. This can't be undone." ve "Cancel" / "Delete project" düğmeleri olacak.
- **Dayanak:** yıkıcı eylemler tablosunun ilk satırı.

### Proje silmenin iki giriş noktası
- **Tür:** eklenecek
- **Etiket:** görsel
- **Alan:** Yıkıcı eylemler ve geri alma
- **Bugün:** bugün yok — Mira v1'de ne proje başlığında ne de kenar çubuğunda kırmızı bir silme denetimi var.
- **Yeni tasarımda:** aynı modale iki kapı açılacak: proje başlığında "Rename"in yanındaki kırmızı ana hatlı düğme (`#EBCFC9` kenar / `#B23A2E` yazı, üstüne gelince kırmızıyla doluyor) ve kenar çubuğu satırının ⋯ menüsündeki kırmızı "Delete project" satırı.
- **Dayanak:** yıkıcı eylemler bölümündeki "Two entry points for project delete, same modal".

### Proje silindikten sonra nereye gidildiği ve geri alma
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Yıkıcı eylemler ve geri alma
- **Bugün:** bugün yok — silme olmadığı için silme sonrası bir gezinme ya da geri alma da yok.
- **Yeni tasarımda:** içinde bulunulan proje silinince kalan ilk projeye geçilecek, hiç kalmadıysa boş ekrana düşülecek ve açık sohbet/önizleme temizlenecek; başka bir proje silinince açık sohbet, önizleme ve kaydırma yeri hiç oynamayacak. Her iki durumda da ekranın alt ortasında koyu (`#26231F`) bir bildirim çıkacak; içinde "Undo" ve bir kapatma olacak, Undo projeyi listedeki eski sırasına geri koyup açacak. Tek kademe geri alma, geçmiş tutulmayacak.
- **Dayanak:** yıkıcı eylemler tablosu ve kural kartlarındaki "Deleting never moves you unless it has to".

### Sohbet silmenin onayı
- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Yıkıcı eylemler ve geri alma
- **Bugün:** Mira v1'de proje ekranındaki sohbet satırının üstüne gelince bir "×" beliriyor; tıklayınca tarayıcının kendi onay kutusu "Delete this chat? Its files stay in the project." diye soruyor ve onaylanınca sohbet siliniyor, geri alma sunulmuyor.
- **Yeni tasarımda:** karşılığı yok.
- **Not:** tasarım söylemiyor — "confirmation before deleting a chat" tasarımın kendi açık bıraktığı maddelerden biri, sohbet silmenin nasıl görüneceği hiçbir yerde tarif edilmiyor.
- **Dayanak:** "Open items" listesindeki "confirmation before deleting a chat".

### Sohbeti yeniden adlandırma
- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Yıkıcı eylemler ve geri alma
- **Bugün:** Mira v1'de sohbet satırının üstüne gelince mono "name" düğmesi beliriyor; tıklayınca tarayıcının kutusu "Chat title" diye soruyor ve girilen başlık iki listede birden değişiyor, boş giriş iptal ediyor.
- **Yeni tasarımda:** karşılığı yok — sözleşme sohbetlerin yeniden adlandırılamayacağını söylüyor.
- **Not:** sözleşme burada kendi içinde çelişiyor: sayfa hâli "inline chat renaming"i kaldırılanlar arasında sayıyor ve kural kartı "Chats and files are not renameable" diyor; buna karşılık metin hâlinin duyarlı yerleşim tablosu 780px altında "the `name` button hides" diyerek aynı düğmenin varlığını varsayıyor.
- **Dayanak:** sayfa hâlinin "Deliberately removed" listesi, "Renaming is inline and cheap" kural kartı ve metin hâlinin duyarlı yerleşim tablosu.

### Dosyayı yeniden adlandırma
- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Yıkıcı eylemler ve geri alma
- **Bugün:** Mira v1'de dosya satırının üstüne gelince mono "name" düğmesi beliriyor; tıklayınca "File name" sorulup dosya yeniden adlandırılıyor, ad çakışırsa numaralanmışı kullanılıyor ve açık panel yeni ada geçiyor.
- **Yeni tasarımda:** karşılığı yok — sözleşme dosyaların yeniden adlandırılamayacağını söylüyor.
- **Not:** tasarım söylemiyor — "file rename" tasarımın açık bıraktığı maddelerden biri, nasıl görüneceği tarif edilmiyor.
- **Dayanak:** "Open items" listesindeki "file rename" ve kural kartındaki "Chats and files are not renameable (open item)".

---

## Boş hâller

### Hiç proje yokken açılan ekran
- **Tür:** eklenecek
- **Etiket:** davranış
- **Alan:** Boş hâller
- **Bugün:** bugün yok — Mira v1'de hiç proje olmasa bile Home selamlaması, composer ve boş bir kart ızgarası çıkıyor; kenar çubuğundaki "New chat" her koşulda görünüyor ve tıklanınca yine aynı boş Home'a götürüyor.
- **Yeni tasarımda:** hiç proje yokken kendine ait bir ekran gelecek: "No projects yet" + tek satırlık bir cümle + tek bir "New project" düğmesi; ne composer ne ızgara olacak, kenar çubuğundaki "New chat" ölü bir denetim olmasın diye pasifleştirilmeyip gizlenecek.
- **Dayanak:** boş hâller bölümünün ilk maddesi ve kural kartlarındaki "Empty is instructive, not decorative".

---

## Duyarlı yerleşim

### Ölçünün kaynağı ve kırılma noktaları
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Duyarlı yerleşim
- **Bugün:** Mira v1'de yerleşim tarayıcı penceresinin genişliğine bakan tek bir eşikle, 1100px'te değişiyor: kenar çubuğu 208px'e iniyor, ray sohbetin altına geçiyor, proje ızgarası ve Home kartları tek sütuna düşüyor, yatay dolgu 32px'ten 20px'e iniyor.
- **Yeni tasarımda:** yerleşim pencereye değil kabuğun ölçülen genişliğine bakacak (aynı ekran gömülü bir çerçeve içinde de doğru davranacak) ve üç eşikte değişecek: 1000px, 780px ve 640px.
- **Dayanak:** duyarlı yerleşim bölümündeki tablo ve "Driven by the shell's measured width ... not media queries" cümlesi.

### Kenar çubuğunun genişlik basamakları
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Duyarlı yerleşim
- **Bugün:** Mira v1'de kenar çubuğu 280px'ten tek adımda 208px'e iniyor ve dolgusu 18/14'ten 16/10'a geçiyor.
- **Yeni tasarımda:** basamaklar 280 → 226 → 198 → 172px olacak ve en dar basamakta dolgu ayrıca sıkışacak.
- **Dayanak:** duyarlı yerleşim bölümündeki "Sidebar steps" satırı.

### Dar pencerede başlıkların küçülmesi
- **Tür:** eklenecek
- **Etiket:** görsel
- **Alan:** Duyarlı yerleşim
- **Bugün:** bugün yok — Mira v1'de Home'un 42px'lik başlığı ve proje ekranının 36px'lik başlığı pencere ne kadar darsa da aynı boyda kalıyor.
- **Yeni tasarımda:** 780px altında 42px başlık 31px'e, 36px başlık 27px'e inecek.
- **Dayanak:** duyarlı yerleşim tablosunun 780px satırı.

### Dar pencerede sohbet satırının zaman damgası
- **Tür:** eklenecek
- **Etiket:** görsel
- **Alan:** Duyarlı yerleşim
- **Bugün:** bugün yok — Mira v1'de proje ekranındaki sohbet satırının sağındaki göreli zaman her genişlikte görünmeyi sürdürüyor.
- **Yeni tasarımda:** 780px altında zaman damgası gizlenecek, böylece başlık genişliğini koruyacak.
- **Dayanak:** duyarlı yerleşim tablosunun 780px satırı.

### Dar pencerede rayın yüksekliği ve katlanması
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Duyarlı yerleşim
- **Bugün:** Mira v1'de dar pencerede ray sohbetin altına geçiyor, üstünde bir çizgi oluyor ve yüksekliği içeriği kadar oluyor; kendi içinde kaymıyor ve katlanamıyor.
- **Yeni tasarımda:** ray sohbetin altına geçtiğinde alanın %44'ünü kaplayacak ve dikey şerit yerine tek bir başlık satırına katlanacak.
- **Dayanak:** duyarlı yerleşim tablosunun 1000px satırı ve yerleşim bölümündeki ray paragrafı.

### Dar pencerede composer'ın alta çakılı kalması
- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Duyarlı yerleşim
- **Bugün:** Mira v1'de pencere daraldığında sohbet ekranının tamamı tek bir kayan sütuna dönüşüyor; composer artık alta çakılı durmuyor, sayfayla birlikte kayıyor.
- **Yeni tasarımda:** composer her pencere boyunda alta çakılı kalacak ve kayan tek şey mesaj listesi olacak.
- **Dayanak:** yerleşim bölümündeki kaydırma sözleşmesi ("The composer is pinned to the bottom at any window size").

---

## Klavye ve erişilebilirlik

### Esc'in kapatma sırası
- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Klavye ve erişilebilirlik
- **Bugün:** Mira v1'de Esc önce açık arama kutusunu, o kapalıysa açık dosya panelini kapatıyor; başka kapatılacak bir şey tanımlı değil ve Esc hiçbir zaman geri gitmiyor.
- **Yeni tasarımda:** Esc sırayla şunları kapatacak: proje ⋯ menüsü → silme onay modalı → skills menüsü → model menüsü → açık dosya paneli; yine hiçbir zaman geri gitmeyecek.
- **Dayanak:** klavye ve erişilebilirlik bölümündeki Esc maddesi.

### Satırların gerçek düğme olması ve yıkıcı denetimlerin ipucu
- **Tür:** değişecek
- **Etiket:** davranış
- **Alan:** Klavye ve erişilebilirlik
- **Bugün:** Mira v1'de kenar çubuğu satırları ve proje kartları gerçek düğme ama proje ekranındaki sohbet satırları ile dosya satırları düğme değil, tıklanabilir kutular; klavyeyle odaklanılamıyor, Enter'la açılamıyor. Satır içindeki silme/yeniden adlandırma düğmeleri üstüne gelinince beliriyor ve fare üstünde beklerken ipucu göstermiyor, ekran okuyucuya "Delete <ad>" diye tanıtılıyor.
- **Yeni tasarımda:** her satır gerçek bir düğme olacak ve yıkıcı eylemler fare üstünde okunan bir ipucu taşıyacak.
- **Dayanak:** klavye ve erişilebilirlik bölümündeki "Every row is a real button; destructive actions carry a `title`".

---

## Görsel dil

### Vurgu renginin üstüne gelme tonu
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Görsel dil
- **Bugün:** Mira v1'de vurgu `#B5623C`; birincil düğmenin, bağlantının ve geri alma bağlantısının üstüne gelince renk `#8F4A2C`'ye dönüyor.
- **Yeni tasarımda:** vurgunun üstüne gelme tonu `#9E5232` olacak.
- **Not:** sözleşme yıkıcı renk konusunda kendi içinde çelişiyor: metin hâlinin görsel dil tablosu yıkıcı rengi `#8F4A2C` diyor, aynı belgenin yıkıcı eylemler bölümü başlıktaki silme düğmesine `#B23A2E` veriyor ve sayfa hâlinin renk şeridi yıkıcıyı `#B23A2E` diye etiketliyor.
- **Dayanak:** görsel dil tablosundaki "Accent `#B5623C` (hover `#9E5232`)" satırı ile iki hâlin yıkıcı renk değerleri.

### Ekran girişindeki yukarı kayma hareketi
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Görsel dil
- **Bugün:** Mira v1'de proje ekranı 0.35s, Home 0.4s boyunca 6px aşağıdan yukarı kayarak beliriyor; yani yerleşmiş bir öğe konum değiştirerek giriyor ve süre 220ms'yi aşıyor.
- **Yeni tasarımda:** hareket yalnız 140–220ms opaklık geçişleri ve rayın 220ms'lik genişlik geçişiyle sınırlı olacak; yerleşmiş hiçbir öğe konum değiştirmeyecek.
- **Dayanak:** görsel dil bölümündeki hareket cümlesi.

### Composer kartının köşe yarıçapı
- **Tür:** değişecek
- **Etiket:** görsel
- **Alan:** Görsel dil
- **Bugün:** Mira v1'de composer kartının yarıçapı 16px; kenar çubuğu düğmeleri ve satırları 9px kullanıyor.
- **Yeni tasarımda:** yarıçaplar üç değerde toplanacak: denetimler 8px, kartlar 12–14px, haplar 20px.
- **Dayanak:** görsel dil bölümündeki "Radii" satırı.

---

## Sohbet ekranı

### Sohbet üst çubuğunda başlık
- **Tür:** öksüz
- **Etiket:** görsel
- **Alan:** Sohbet ekranı
- **Bugün:** Mira v1'de sohbet üst çubuğu "← proje adı" düğmesinden sonra soluk bir "/" ve sohbetin başlığını da gösteriyor.
- **Yeni tasarımda:** karşılığı yok.
- **Not:** tasarım söylemiyor — sözleşme sohbet üst çubuğunu yalnız "← project name" diye tarif ediyor, başlığın orada olup olmadığını hiç söylemiyor.
- **Dayanak:** yerleşim tablosunun ve yapı bölümünün sohbet satırı.

---

## Ajan döngüsü

### Cevabın gerçekten sunucudan akması
- **Tür:** öksüz
- **Etiket:** davranış
- **Alan:** Ajan döngüsü
- **Bugün:** Mira v1'de cevap sunucudan parça parça geliyor, dosya yaratılırken "creating file…" kesik çizgili kartı çıkıyor ve akış bitince sunucunun yazdığı kayıt ekrandaki tahmini değiştiriyor.
- **Yeni tasarımda:** karşılığı yok.
- **Not:** tasarım söylemiyor — "real streaming from the backend" tasarımın açık bıraktığı maddelerden biri; sözleşmenin tarif ettiği akış zamanlayıcıyla taklit edilen bir prototip akışı (~5 karakter / 22ms) ve gerçek akışın nasıl davranacağı yazılmamış.
- **Dayanak:** "Open items" listesindeki "real streaming from the backend (the prototype fakes it on a timer)".

---

## Karşılığı bulunan ve fark görülmeyen kararlar

Aşağıdakiler tarandı ve bugünkü uygulamada sözleşmedekiyle aynı bulundu, bu yüzden bulgu yazılmadı:
zihinsel modelin tamamı (proje iki kardeş koleksiyon tutuyor, dosya projeye ait, kullanıcı dosya
yüklemiyor, her sohbet her dosyayı görüyor, sohbet satırında dosya rozeti ve "kaynak sohbete git"
bağlantısı yok); boş taslakta Send'in pasif ve `#E5DFD5` olması, imlecin "izin verilmez"e dönmesi ve
ilk karakterle vurgu rengine geçmesi; Enter'ın göndermesi, Shift+Enter'ın satır atlaması; ilk
mesajda sohbetin doğup o mesajdan 42 karakterle ve üç noktayla adlanması; kullanıcı balonunun sağa
yaslı ve saatli olması; cevabın balonsuz gelmesi; dosya okumanın ayrı bir ekran olmaması, sohbette
rayın 320→560px genişlemesi ve proje ekranında 560px panelin ızgarayı tek sütuna düşürmesi; açık
dosyada yalnız kapatma ve Download bulunması ve üst verinin altta tek mono satır olması; dosya
silmenin onaysız ve anında olup listenin üstünde "File deleted." + "Undo" şeridi bırakması; proje
adının tek bir soru kutusuyla değişmesi ve boş girişin iptal etmesi; yükleniyor hâlinde içerik
alanında iskelet blokların çıkıp kenar çubuğunun normal kalması; indirme sırasında düğmenin yerinde
durup içinde dönen bir işaret ve "preparing…" göstermesi; çevrimdışıyken içerik alanının üstünde
şerit çıkıp composer'ın açık kalması; uzun başlıkların ikinci satıra sarmayıp üç noktayla kesilmesi;
odak halkasının 2px `#B5623C` ve 2px boşluklu olması; zemin `#F7F5F1`, kenar çubuğu `#EFEBE4`, yüzey
`#FFFDFA`, çizgi `#E2DCD2`, mürekkep `#22201D`, soluk `#8B8378` değerleri; başlıklarda Newsreader,
gövdede DM Sans, etiket ve sayılarda DM Mono kullanılması.
