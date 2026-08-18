# Mira ile QueenAgent tasarım v2 arasındaki farklar

**Tarih:** 2026-08-14 · **Yöntem:**
[fark çıkarma planı](../plans/2026-08-14-mira-tasarim-fark-cikarma.md) ·
[tasarım belgesi](../specs/2026-08-14-mira-tasarim-fark-cikarma-design.md)

## 0 · Künye

**İki taraf.** Bir yanda bugün repoda çalışan uygulama; tarifi
[Mira v1 tasarım belgesi](../specs/2026-08-09-mira-v1-design.md) ve
[v1 yol haritası](../plans/2026-08-09-mira-v1-roadmap.md). Öte yanda claude.ai/design'daki tasarımın
yeni sürümü; kendine **"v2 (post road-map)"** diyor. Belge boyunca ikisi de tam adıyla anılır:
**Mira v1** ve **tasarım v2**.

**Ürün adı değişmiş.** Tasarım ürüne baştan sona **QueenAgent** diyor. Bu belge bugünkü tarafı "Mira",
tasarım tarafını "QueenAgent" diye anar; adın kendisi de bir fark maddesidir (madde 1).

**Sözleşme tek katman.** Tasarımın yazılı sözleşmesi üst üste binmiş sürümlerden oluşmuyor; kendini
"bugünkü davranışı anlatır, eski spec'i değil" diye tanımlıyor. Sözleşmenin iki hâli var — bir
markdown, bir de aynı metnin sayfası — ve birkaç yerde birbirini tutmuyorlar; o maddeler `çelişki`
damgası taşır.

**Üç yol.** Fark üç bağımsız ajanla, birbirini görmeden çıkarıldı. **Y1** yalnız tasarımın çizilmiş
hâline baktı (prototip ve ekran tuvali), **Y3** yalnız yazılı sözleşmeye, **Y2** ise ters yönden —
uygulamadan tasarıma — yürüdü ve tasarımın tamamını görebildi. Damga, farkı kaç yolun gördüğünü
söyler: **3/3 kesin · 2/3 güçlü · 1/3 zayıf sinyal.** Hangi maddeyi hangi yolun gördüğü tek bakışta
[Ek A · Çakıştırma tablosu](#ek-a--çakıştırma-tablosu)'nda duruyor.

**Zayıf sinyaller elle doğrulandı.** Tek bir yolun gördüğü her madde kaynağına kadar takip edildi;
sonuç maddenin altına "Elle doğrulandı" notuyla yazıldı. Doğrulanamayan bir madde silinmez, damgasıyla
listede kalır — bu turda öyle bir madde çıkmadı, ama iki madde **kısmen çürütüldü** (5 ve 11) ve bir
madde birleştirilip damgası yükseldi (54).

**`düzeltilecek` damgalanmaz.** O tür bugünkü uygulamanın **Mira v1'den** sapmasını gösterir, tasarım
v2 farkını değil; yalnız Y2 üretebildiği için tavanı 1/3'tür ve örtüşme onun hakkında bir şey
söylemez. Bu belgede tür sütunu iki iddiayı ayırır: *"bugün yanlış"* ile *"tasarım v2'de değişecek"*
farklı şeylerdir.

**Belge karar vermez.** Hiçbir madde neyin uygulanacağını, neyin öncelikli olduğunu ya da bir
çelişkide hangi tarafın kazandığını söylemez.

**Dil.** Belge Türkçe; arayüz metinleri kaynaktaki hâliyle, İngilizce alıntılanır.

---

## 1 · Özet

Tasarım v2 üç şey yapıyor. **Çıkarıyor:** arama tümüyle gidiyor (kenar çubuğu düğmesi, ⌘K, katman),
selamlama, üç öneri hapı, proje açıklamaları, logo işareti, composer'ın altındaki yardım notları,
`← back` ve satır içi yeniden adlandırmalar. **Ekliyor:** proje silme (modal, iki giriş kapısı, koyu
şerit ve tek adımlık geri alma), composer'a model ve Skills seçicileri, cevapların Markdown olarak
çizilmesi, katlanabilir dosya rayı, transkriptteki dosya kartının bir kapıya dönüşmesi, hiç proje
yokken açılan kendine ait bir ekran. **Sıkılaştırıyor:** tek kırılma noktası üçe çıkıyor ve ölçü
pencereden kabuğun kendisine geçiyor, sayfa hiçbir boyda kaymıyor, hareket tek bir banda iniyor,
yarıçaplar üç değere toplanıyor, palete ayrı bir yıkıcı renk giriyor.

Ayrıca uygulamanın açıldığı yer değişiyor: Home yerine ilk proje.

---

## 2 · Fark listesi

### Adlandırma ve kimlik

**1. Ürünün adı** — `değişecek` · davranış · **kesin** (Y1·Y2·Y3)
Bugün kenar çubuğu "Mira" yazar, cevabın etiketi "Mira · 11:04" olur, boş dosya listesi "…and Mira
will create one." der, çevrimdışı şeridi "Mira will answer…" der ve modele giden yönerge "You are
Mira…" diye başlar → tasarım v2'de aynı yerlerin hepsinde ad **QueenAgent** olur; cevabın etiketi
büyük harfli "QUEENAGENT · saat" biçiminde okunur.

**2. Ad yanındaki logo karesi** — `öksüz` · görsel · **kesin** (Y1·Y2·Y3)
Bugün adın solunda 22×22, 6px yarıçaplı, vurgu renginde dolu bir kare durur → tasarım v2'de karşılığı
yok; sözleşme kelime markasını açıkça "no logo mark" diye tarif ediyor. *Yerine bir şey konup
konmayacağını tasarım söylemiyor.*

**3. Kullanıcı satırının etiketi** — `değişecek` · görsel · **güçlü** (Y1·Y2)
Bugün kullanıcının balonunun üstünde sabit "You · 11:04" yazar → tasarım v2'de kişinin kendi adı ve
saat yazar (örnek veride "ALEX · 14:32"). *Adın nereden geleceğini tasarım söylemiyor.*

**4. Üretilen dosyanın adı nereden çıkıyor** — `değişecek` · davranış · **zayıf sinyal** (Y2)
Bugün adı model söyler; gelen ad temizlenir (klasör yolu atılır, geçersiz karakterler `-` olur, nokta
yoksa `.md` eklenir) ve çakışırsa `plan.md` → `plan-2.md` diye numaralanır → tasarım v2'de ad
kullanıcının gönderdiği cümleden türetilir: küçük harfe indirilir, harf ve rakam dışındakiler atılır,
**ilk üç kelime** tirelerle birleştirilir, sonuna `.md` gelir; hiç kelime kalmazsa `note.md` olur.
*Aynı adın ikinci kez doğması hâlinde ne olacağını tasarım söylemiyor.*
**Elle doğrulandı — dayanağı zayıf çıktı.** Yazılı sözleşme dosya adlandırmadan **hiç** söz etmiyor;
bu kural yalnız tasarımın çalışan örneğinin içinden okundu. Tasarımın kendi kuralı ise "prototipin
**kodu bağlayıcı değil**, bağlayıcı olan görüntüsüdür" diyor — bir adlandırma algoritması görüntü
değil koddur. Yani bu, tasarımın verilmiş bir kararı olmayabilir.

**5. Projenin renk noktası** — `öksüz` · görsel · **zayıf sinyal, kısmen çürütüldü** (Y3)
Bugün her proje doğduğunda kendine bir renk tonu alır ve o tondaki nokta hem kenar çubuğu satırında
hem proje kartında adın solunda görünür → tasarım v2'de sözleşme projeye bağlı bir renk kimliğinden
hiç söz etmiyor; görsel dil bölümü yalnız tek bir vurgu rengi tanıyor.
**Elle doğrulandı — iddia daraldı:** noktanın **kendisi** tasarımda duruyor. Çizilmiş hâle bakan yol,
proje kartını "nokta, ad ve sayaç satırından kurulu" diye tarif ediyor (madde 20'nin dayanağı). Yani
öksüz olan nokta değil, yalnız **projeye özel renk** olabilir — ve onu da tasarım ne kaldırıyor ne
onaylıyor, hiç anmıyor.

### Kenar çubuğu

**6. Aramanın tamamı** — `öksüz` · davranış · **kesin** (Y1·Y2·Y3)
Bugün kenar çubuğundaki "Search" düğmesi ya da ⌘K/Ctrl+K ekranı karartan bir katman açar; kutuda
"Search projects, chats and files..." yazar, yazdıkça proje/sohbet/dosya sonuçları türü ve projesiyle
listelenir, hiçbiri yoksa "No results." çıkar, seçilen sonuç ilgili ekranı açar → tasarım v2'de
karşılığı yok. Sözleşme aramayı üç parçasıyla birlikte "bilerek kaldırıldı, karar alınmadan geri
getirilmesin" diye anıyor ve gerekçesini "proje yapısı zaten gezinmenin kendisi" diye veriyor.

**7. Proje satırında ⋯ menüsü** — `eklenecek` · davranış · **kesin** (Y1·Y2·Y3)
Bugün kenar çubuğundaki proje satırının üstüne gelince yalnız arka planı dolar, satırdan projeye dair
bir işlem yapılamaz → tasarım v2'de adın sağında bir "⋯" düğmesi belirir ve 176px genişliğinde bir
menü açar: "Rename" ve kırmızı "Delete project". Menü ekrana göre konumlanıp sınırlanır ki kayan kenar
çubuğu onu kırpmasın; Esc ya da dışarı tıklama kapatır.

**8. "Recent chats" bölümünün kapsamı** — `değişecek` · davranış · **kesin** (Y1·Y2·Y3)
Bugün başlık her ekranda durur ve altında tüm çalışma alanının sohbetleri sayı sınırı olmadan
listelenir → tasarım v2'de bölüm yalnız bir proje seçiliyken çizilir, yalnız o projenin sohbetlerini
ve en çok **8** tanesini listeler, proje seçili değilse başlığıyla birlikte yok olur.

**9. "New chat" düğmesinin varlığı** — `eklenecek` · davranış · **kesin** (Y1·Y2·Y3)
Bugün düğme her koşulda durur ve hiç proje yokken de basılabilir → tasarım v2'de proje sayısı sıfıra
düştüğünde düğme kenar çubuğundan **gizlenir** (pasifleştirilmez — ölü bir denetim kalmasın diye),
ilk proje doğduğunda geri gelir.

**10. Kenar çubuğunun genişlik basamakları** — `değişecek` · görsel · **kesin** (Y1·Y2·Y3)
Bugün genişlik 280px'ten tek adımda 208px'e iner ve iç boşluk 18/14'ten 16/10'a geçer → tasarım v2'de
basamaklar **280 → 226 → 198 → 172px** olur ve iç boşluk yalnız en dar basamakta sıkışır.

**11. "+" proje ekleme düğmesi ve satır rozeti** — ~~`öksüz`~~ · **çürütüldü, fark değil** (Y3)
İddia şuydu: bugün "Projects" başlığının sağında bir "+" düğmesi durur ve her proje satırının sağ
ucunda dosya sayısı mono bir sayı olarak yazar; sözleşme kenar çubuğunu "kelime markası, New chat,
Projects, Recent chats" diye sayarken ikisinden de söz etmez.
**Elle doğrulandı — iddia düştü.** Sözleşme gerçekten susuyor, ama tasarımın **çizilmiş hâlinde
ikisi de var:** kenar çubuğundaki "Projects" başlığının sağ ucunda çerçevesiz bir "+" düğmesi (başlıkla
aynı gri, üstüne gelince koyulaşıyor) ve her proje satırında dosya sayısı rozeti (madde 15). Yalnız
sözleşmeye bakan yol, yazılmamış olanı yok sanmış. **Burada bir fark yok; madde listede çürütülmüş
olarak duruyor, silinmiyor.**

### Uygulama geneli

**12. Uygulamanın açıldığı ekran** — `değişecek` · davranış · **güçlü** (Y2·Y3)
Bugün kök adres Home'u açar: selamlama, composer, proje kartları → tasarım v2'de uygulama doğrudan
**ilk projenin** ekranıyla açılır; Home'a yalnız "New chat" ile ulaşılır, hiç proje yoksa boş ekran
gelir. *Bu karar sözleşmenin yalnız sayfa hâlinde geçiyor; markdown hâli açılış ekranını hiç
anmıyor.*

**13. Kaydırma sözleşmesi** — `değişecek` · görsel · **güçlü** (Y2·Y3)
Bugün kabuk pencerenin yüksekliğini alır ama en az 600px'te durur; dar pencerelerde sohbet ve proje
yerleşimleri kendileri kayan sütunlara dönüşür ve composer mesajlarla birlikte yukarı kayar → tasarım
v2'de kabuk `100dvh`e sabitlenir, **sayfanın kendisi hiçbir boyda kaymaz**, zincirdeki her sütun kendi
taşmasını sıfırlar; kayan tek şey mesaj listesidir ve composer her pencere boyunda dibe çakılı kalır.
Hiçbir genişlikte yatay kaydırma çıkmaz.

**14. Bir haftadan eski zaman damgası** — `değişecek` · görsel · **zayıf sinyal** (Y1)
Bugün zaman "just now / 5m ago / 2h ago / yesterday / 3 days ago" diye ilerler, bir haftayı geçince
"12 Aug" gibi bir tarihe döner → tasarım v2'de bir haftayı geçen kayıt "1 week ago" diye görünür.
*Daha eski kayıtların nasıl yazılacağını tasarım söylemiyor.*
**Elle doğrulandı** — ekranda okunan bir metin, yani tasarımın kendi kuralına göre bağlayıcı.

**15. Sayaçların tekil hâli** — `değişecek` · görsel · **zayıf sinyal** (Y1)
Bugün proje kartı "1 chat · 3 files" diye tekil/çoğul ayrımı yapar ve kenar çubuğu rozeti sıfırken
hiç yazmaz → tasarım v2'de aynı kural silme onayındaki cümleye de uzanır ("1 chat and 1 file" ↔
"3 chats and 3 files") ve rozet sıfırken yazısını saydamlaştırıp yerini korur.
**Elle doğrulandı** — onay cümlesinin tekil/çoğul hâli sözleşmede de birebir yazılı ("The N chats and
N files…"); rozetin sıfırdaki davranışı yalnız çizimden geliyor ama görünür bir ayrıntı.

### Home

**16. Selamlama başlığı** — `öksüz` · görsel · **kesin** (Y1·Y2·Y3)
Bugün composer'ın üstünde serif 42px "Hi" başlığı durur → tasarım v2'de karşılığı yok; Home doğrudan
composer'la başlar.

**17. Üç öneri hapı** — `öksüz` · davranış · **kesin** (Y1·Y2·Y3)
Bugün composer'ın altında üç hap durur ("Summarize this week's notes", "Draft a meeting agenda",
"Turn my sources into a table") ve birine basmak taslağı o cümleyle doldurur, göndermez → tasarım
v2'de karşılığı yok.

**18. Home'dan gönderilen mesajın nereye düştüğü** — `değişecek` · davranış · **güçlü** (Y1·Y2)
Bugün Home'un kutusuna yazıp göndermek tek adımda **yeni bir proje** ve içinde bir sohbet açar,
projenin adı o ilk cümleden alınır → tasarım v2'de mesaj var olan bir projeye düşer ve orada yeni bir
sohbet açar; proje doğmaz. Ekranda mesajın nereye gideceğini söyleyen etiket de bulunmaz.
*Hangi projenin seçileceğini sözleşme söylemiyor; tasarımın çalışan örneği açık projeye, o yoksa
listedeki ilk projeye gönderiyor.*

**19. Home sütununun üst boşluğu** — `değişecek` · görsel · **güçlü** (Y1·Y2)
Bugün 720px'lik sütun pencerenin tepesinden 14vh aşağıda başlar → tasarım v2'de 18vh aşağıda başlar.

### Proje ekranı

**20. Proje açıklaması** — `öksüz` · davranış · **kesin** (Y1·Y2·Y3)
Bugün her yeni proje "Click to add a description." ile doğar; bu satır proje başlığının altında
tıklanabilir bir paragraf olarak durur, tıklayınca tarayıcının kutusu "Project description" diye
sorar, ve aynı metin proje kartında ikinci satır olarak görünür → tasarım v2'de karşılığı yok — ne
veri alanı ne arayüzde bir yeri kalır; kart yalnız nokta, ad ve "N chats · N files" satırından
oluşur.

**21. "← back" düğmesi** — `öksüz` · görsel · **kesin** (Y1·Y2·Y3)
Bugün proje başlığının üstünde mono "← back" durur ve Home'a götürür → tasarım v2'de karşılığı yok;
ekran doğrudan başlık satırıyla başlar.

**22. Sohbet satırının "name" düğmesi** — `öksüz` · davranış · **kesin** (Y1·Y2·Y3)
Bugün satırın üstüne gelince mono "name" düğmesi belirir ve tarayıcı kutusu "Chat title" diye sorar →
tasarım v2'de karşılığı yok; sözleşme satır içi sohbet yeniden adlandırmayı kaldırılanlar arasında
sayıyor ve "Chats and files are not renameable" diyor. **Çelişki:** aynı sözleşmenin duyarlı yerleşim
tablosu 780px altında "the `name` button hides" diyerek o düğmenin varlığını varsayıyor. İki ifade de
burada duruyor.

**23. Dosya listesinin altındaki öğüt satırı** — `öksüz` · görsel · **zayıf sinyal** (Y3)
Bugün proje ekranındaki dosya listesinin altında, liste dolu olsa bile "Chats create the files; you
just open and read them." satırı durur → tasarım v2'de karşılığı yok. *Sözleşme dolu bir listenin
altına konacak açıklayıcı metinden söz etmiyor; boş hâli ise "instructive, never decorative" diye
sınırlıyor.* (Aynı satırın bugünkü davranışı ayrıca madde 79'da bir sapma olarak duruyor.)
**Elle doğrulandı.** Sözleşme boş hâllerin metinlerini tek tek veriyor ve dolu liste için hiçbir
metin tanımlamıyor; çizilmiş hâle bakan yol da bu satırı tasarımda hiç görmemiş.

**24. Sohbet satırındaki silme düğmesinin görünürlüğü** — `değişecek` · görsel · **zayıf sinyal** (Y1)
Bugün satırdaki "×" saydam durur, ancak işaretçi satıra gelince ya da düğme klavyeyle odaklanınca
görünür olur → tasarım v2'de "×" satırda her zaman görünür durur (`#B5ADA2`), üstüne gelince yazısı
kırmızıya döner ve arkasında yuvarlatılmış bir zemin belirir.
**Elle doğrulandı** — görünür bir hâl. Sözleşme kenar çubuğundaki ⋯ düğmesi için tersini söylüyor
("üstüne gelince belirir"), yani tasarım iki denetimi bilerek ayırmış olabilir; çelişki değil.

**25. Uzun proje adının başlık satırında sarması** — `eklenecek` · görsel · **zayıf sinyal** (Y1)
Bugün başlık, düğmesiyle tek satırda durur ve satır sarmaz → tasarım v2'de satır sarabilir: sığmayan
düğmeler bir alt satıra iner ve satırın altındaki boşluk 30px olur.
**Elle doğrulandı — listedeki en zayıf madde bu.** Yalnız çalışan örneğin bir sarma ayarından
okundu; sözleşme uzun başlıklar için tam tersini söylüyor ama **liste satırları** için: "üç noktayla
kesilir, ikinci satıra sarmaz". Proje başlığı liste satırı değil, yani çelişki değil — ama tasarımın
yazılı bir kararı da değil.

### Yıkıcı eylemler ve geri alma

**26. Proje silme** — `eklenecek` · davranış · **kesin** (Y1·Y2·Y3)
Bugün bir projeyi silmenin hiçbir yolu yok; başlık satırında yalnız "Rename" var ve sunucu böyle bir
isteği tanımıyor → tasarım v2'de aynı onay kutusuna **iki kapı** açılır: proje başlığında "Rename"in
yanındaki kırmızı çerçeveli "Delete" (üstüne gelince kırmızıyla dolar) ve kenar çubuğu satırının ⋯
menüsündeki kırmızı "Delete project". Kutu «Delete "X"?» diye sorar, altında "The N chats and N files
in this project are deleted with it. This can't be undone." der ve "Cancel" ile dolu kırmızı "Delete
project" sunar.

**27. Silinen projenin şeridi ve geri alınması** — `eklenecek` · davranış · **kesin** (Y1·Y2·Y3)
Bugün geri alma yalnız dosya için var → tasarım v2'de proje silinince ekranın **alt ortasında** koyu
bir şerit belirir (`#26231F`, 11px yarıçap): «Project "X" deleted.» yazısı, turuncu "Undo" ve kapatan
bir "×". Undo projeyi listedeki **eski sırasına** geri koyar ve açar. Tek adımlıktır, geçmişi yoktur.

**28. Silmenin nereye götürdüğü** — `eklenecek` · davranış · **güçlü** (Y2·Y3)
Bugün proje silinemediği için böyle bir kural da yok → tasarım v2'de **içinde bulunulan** proje
silinirse ekran kalan ilk projeye düşer (hiç kalmazsa boş ekrana) ve açık sohbet ile önizleme
temizlenir; **başka bir** proje silinirse açık sohbet, önizleme ve kaydırma yeri hiç kıpırdamaz.

**29. Sohbet silmenin onayı** — `değişecek` · davranış · **kesin** (Y1·Y2·Y3)
Bugün "×" basılınca tarayıcının onay kutusu "Delete this chat? Its files stay in the project." diye
sorar, onaylanınca sohbet gider ve geri alma sunulmaz → tasarım v2'de "×" basılır basılmaz sohbet
listeden çıkar; ne soru sorulur ne geri alma sunulur. *Sözleşme "confirmation before deleting a chat"
maddesini kendi **açık maddeleri** arasında sayıyor — yani bugünkü davranışın karşılığı henüz karara
bağlanmamış bir istek.* **Tür çelişkisi:** iki yol bunu `değişecek`, biri `öksüz` saydı.

**30. Dosya yeniden adlandırma** — `öksüz` · davranış · **kesin** (Y1·Y2·Y3)
Bugün hem ray hem proje listesindeki dosya satırının üstüne gelince mono "name" düğmesi belirir,
"File name" sorulur, ad doluysa sunucu numaralı bir ad döndürür ve açık panel yeni adı izler →
tasarım v2'de karşılığı yok. *"file rename" tasarımın kendi açık maddelerinden biri; nasıl görüneceği
tarif edilmiyor.*

**31. Silinen dosyanın geri alma şeridi** — `değişecek` · görsel · **zayıf sinyal** (Y1)
Bugün şerit beyazımsı yüzey renginde ve 8px yarıçaplı; içinde "File deleted." ve "Undo" var, başarısız
bir işlemde altına mono bir hata satırı ekleniyor → tasarım v2'de şerit kenar çubuğu tonunda
(`#EFEBE4`) ve 10px yarıçaplı olur; içinde yalnız "File deleted." ve "Undo" durur. *Şeridin bir hata
cümlesi taşıyıp taşımayacağını tasarım söylemiyor.*
**Elle doğrulandı** — sözleşme şeridin **yerini** yazıyor ("dosya listesinin üstünde satır içi şerit
olarak kalır"), rengini ve yarıçapını yazmıyor; o değerler yalnız çizimden geliyor.

### Composer ve model seçici

**32. Model seçici** — `eklenecek` · davranış · **kesin** (Y1·Y2·Y3)
Bugün hangi modelin cevap verdiği ekranda hiç görünmez ve seçilemez; model sunucunun ayarından tek bir
değer olarak gelir → tasarım v2'de composer'ın ayağında o an seçili modelin adı ve bir chevron durur,
üstüne gelince soluk bir dolgu alır; basınca 296px genişliğinde, mono "MODEL" başlıklı bir menü
açılır ve dört satır listelenir: **Grok 4** ("Best for long, careful answers.", varsayılan), **Grok 4
Fast** ("Quicker replies, everyday questions."), **Grok 4 Heavy** ("Hard reasoning and long
documents."), **Grok Code** ("Code, data and structured output."). Etkin olanın yanında "✓" durur.

**33. Skills seçici** — `eklenecek` · davranış · **kesin** (Y1·Y2·Y3)
Bugün cevabın nasıl üretileceğine dair kullanıcıya sunulan hiçbir seçenek yok → tasarım v2'de model
düğmesinin yanında bir düğme durur; hiçbiri seçili değilken üstünde "Skills" yazar, biri seçilince o
becerinin adını taşır ve sıcak bir tonla boyanır. Menü satırları: **Web search** ("Look things up and
cite the sources."), **Deep research** ("Read many sources before answering. Slower."), **Data &
tables** ("Turn findings into structured tables."), **Code** ("Write and explain code in the
answer."). Tek seçimliktir; seçili olana yeniden basmak seçimi temizler. *Beceri seçiminin cevabı
nasıl değiştireceğini tasarım söylemiyor.*

**34. Seçimlerin sohbete yapışması** — `eklenecek` · davranış · **kesin** (Y1·Y2·Y3)
Bugün her cevap aynı tek modelle üretilir ve sohbetin kendisi hangi modelle konuşulduğunu taşımaz →
tasarım v2'de model ve beceri seçimi açık sohbete iliştirilir; başka bir sohbete geçip dönünce o
sohbetin kendi seçimi geri gelir, yeni açılan sohbet ise son seçimle doğar. Konuşmanın ortasında
değiştirilebilir. *Seçimin sunucuda saklanmasını tasarım **açık madde** olarak bırakıyor.*

**35. Model düğmesinin composer içindeki yeri** — `eklenecek` · görsel · **çelişki** (Y1·Y2·Y3)
Bugün composer'ın alt satırında yalnız (varsa) yardım notu solda ve "Send" sağda durur → tasarım
v2'nin iki hâli iki ayrı yer söylüyor: sözleşmenin **markdown hâli** model seçiciyi *sohbet
composer'ının sol altına* koyuyor; **sayfa hâli** ve çalışan örnek *sağ alta*, "Skills · model · Send"
sırasına koyuyor. İki ifade de burada duruyor.

**36. Açılır kutunun ekrana sığması** — `eklenecek` · görsel · **çelişki** (Y2·Y3)
Bugün composer'da açılan bir kutu olmadığı için konumlanma kuralı da yok → tasarım v2'nin iki hâli iki
ayrı kural veriyor: **markdown hâli** kutuyu composer kartının genişliğiyle sınırlayıp taşmasını böyle
önlüyor; **sayfa hâli** kutuyu görüntü alanına göre ölçüp tetikleyicisine sağdan hizalıyor, üstte yer
yoksa alta çeviriyor ve azami yükseklikle içeriden kaydırılabilir yapıyor.

**37. Composer'ın altındaki mono yardım notu** — `öksüz` · görsel · **kesin** (Y1·Y2·Y3)
Bugün proje ekranındaki kutunun ayağında "the answer is saved as a file", sohbetteki kutunun ayağında
"save the answer as a file" durur; Home'un yer tutucusu da "Ask anything — Mira saves the answer to
your project as a file." der → tasarım v2'de karşılığı yok; sözleşme "No helper text under the
composer" diyor ve `project: X` etiketini de kaldırılanlar arasında sayıyor.

**38. Composer kutusunun yarıçapı** — `değişecek` · görsel · **güçlü** (Y1·Y2)
Bugün üç ekranın da kutusu aynı kalıptan çıkar ve hepsi 16px yuvarlatılır → tasarım v2'de Home'un
kutusu 16px kalır, proje ve sohbet ekranındakiler **14px** olur ve dolguları 14/16/10'a iner.

### Cevap akışı ve Markdown

**39. Cevabın Markdown olarak çizilmesi** — `değişecek` · davranış · **kesin** (Y1·Y2·Y3)
Bugün cevap düz metin olarak, satır sonları korunarak yazılır; `#`, `**`, tablo çubukları ve kod
çitleri ekranda ham işaret olarak görünür → tasarım v2'de cevap Markdown olarak çizilir: `#`–`####`
başlıklar, kalın, italik, üstü çizili, satır içi kod, çitli kod blokları, sıralı/sırasız listeler,
tablolar, alıntılar, yatay çizgiler, bağlantılar. **Kullanıcının mesajı ham kalır** — yazılan
`**test**` yıldızlarıyla görünür.

**40. İki ayrı tipografi ölçeği** — `eklenecek` · görsel · **kesin** (Y1·Y2·Y3)
Bugün cevap metni tek boyutta (15.5px) ve dosya paneli tek boyutta (14px) çizilir; başlık ölçeği diye
bir şey yok → tasarım v2'de sohbette **balon ölçeği** geçerlidir (h1 19.5px / h2 17px Newsreader, h3
14.5px DM Sans 600), dosya panelinde **belge ölçeği** (h1 25px / h2 20px / h3 15.5px). Sayfa
düzeyindeki başlık boyutları balonun içine sızmaz.

**41. Yarım gelen kod bloğu** — `eklenecek` · davranış · **güçlü** (Y2·Y3)
Bugün akan metin ayrıştırılmadığı için böyle bir durum oluşmaz → tasarım v2'de akan metin her karede
yeniden ayrıştırılır ve kapanmamış bir kod çiti çizim sırasında kapatılır, böylece yarım gelmiş bir
blok yerleşimi bozmaz.

**42. Akan cevabın ucundaki imleç** — `eklenecek` · görsel · **kesin** (Y1·Y2·Y3)
Bugün cevap parça parça uzar, sonuna hiçbir işaret konmaz → tasarım v2'de akış sürdüğü sürece metnin
sonunda 7×15px, yanıp sönen bir blok imleç durur ve son parça gelince kaybolur. Metin karakter
karakter yazılır (yaklaşık 5 karakter / 22ms). *Bu hızın prototipte zamanlayıcıyla taklit edildiğini
ve arka uçtan gerçek akışın **açık madde** olduğunu tasarım kendisi söylüyor.*

**43. Otomatik kaydırma kuralı** — `eklenecek` · davranış · **güçlü** (Y2·Y3)
Bugün yeni mesaj gelince ya da cevap akarken liste kendiliğinden hiç kaydırılmaz → tasarım v2'de yeni
bir mesajda liste dibe atlar; akış sürerken dibe yapışması yalnız kullanıcı zaten dibe **220px'den
yakınsa** sürer — yukarı çıkıp okuyan biri asla kesilmez.

**44. Cevabın altındaki dosya kartı bir kapı oluyor** — `değişecek` · davranış · **kesin** (Y1·Y2·Y3)
Bugün kart tıklanamayan bir kutudur: uzantı çipi, dosya adı ve "✓ saved to project"; dosyayı açmanın
tek yolu listedeki satıra basmaktır → tasarım v2'de kart bir düğmedir, sağında mono "Open ›" ipucu
taşır ve basınca o dosyayı sağdaki panelde açar (ray katlanmışsa önce açılır). Kart en çok 340px
genişliğinde, 12px yarıçaplı olur.

**45. Açık dosyanın seçili görünmesi** — `eklenecek` · görsel · **kesin** (Y1·Y2·Y3)
Bugün bir dosya okunurken listede hangi satırın açık olduğunu gösteren bir işaret yok → tasarım v2'de
okunan dosyanın ray satırı `#EFEBE4` zemin alır, transkriptteki kartı `#F4EFE7` zemine ve `#CFC3B2`
çerçeveye geçer ve ipucu "Open ›" yerine "open" der.

**46. "creating file…" kutusunun yeri ve biçimi** — `değişecek` · görsel · **kesin** (Y1·Y2·Y3)
Bugün kesik çerçeveli kutu akan cevabın ve o ana kadar doğmuş kartların **altında**, kendi başına
belirir; içinde yalnız mono "creating file…" yazar ve kutu yazı kadar geniştir; üç nokta çoktan
kaybolmuştur → tasarım v2'de aynı kutu yanıp sönen üç noktanın hemen altında, **aynı bekleme
bloğunun içinde** durur; solunda 30×30, 7px yarıçaplı boş bir rozet yeri taşır ve en çok 340px
genişler — doğacak dosyanın kartıyla aynı iskeleti taşır.

**47. Bekleme etiketi** — `değişecek` · görsel · **güçlü** (Y1·Y3)
Bugün üç noktanın üstünde yalnız ürün adı yazar, saat yoktur → tasarım v2'de etiket "QUEENAGENT ·
saat" biçiminde okunur; nokta ile etiket arasındaki boşluk 10px olur. (Bugünkü saatsizlik ayrıca
madde 74'te bir sapma olarak duruyor.)

### Ajan döngüsü

**48. Her cevabın bir dosya doğurup doğurmadığı** — `değişecek` · davranış · **zayıf sinyal** (Y2)
Bugün cevabın dosya doğurup doğurmayacağına model karar verir: yönerge ona yalnız saklamaya değer bir
şey istendiğinde dosya yazmasını söyler, sıradan bir cevap dosyasız biter; buna karşılık tek turda
birden çok dosya yazabilir ve mesajın altında o kadar kart belirir → tasarım v2'nin çekirdek
döngüsünde akış biter bitmez mesajın altına **tek** bir dosya kartı takılır ve dosya aynı anda hem
proje listesinin hem rayın başına eklenir; **dosyasız cevap diye bir hâl yoktur.** *Tasarım dosyasız
cevabı ne kaldırılanlar ne açık maddeler arasında anıyor — sekiz durumun içinde de böyle bir hâl yok.*
**Elle doğrulandı — sözleşmenin kendisinden.** Çekirdek döngü tablosunun 05. adımı koşulsuz yazılmış
("akış bitince mesajın altına dolu bir dosya kartı takılır") ve kaldırılanlar, açık maddeler ve sekiz
durumun hiçbirinde dosyasız cevap geçmiyor. Tek bir yolun okuma hatası değil.

**49. Gerçek akışın kaynağı** — `öksüz` · davranış · **zayıf sinyal** (Y3)
Bugün cevap sunucudan parça parça gelir ve akış bitince sunucunun yazdığı kayıt ekrandaki tahmini
değiştirir → tasarım v2'de karşılığı yok. *"real streaming from the backend (the prototype fakes it on
a timer)" tasarımın kendi açık maddelerinden biri; gerçek akışın nasıl davranacağı yazılmamış.*
**Elle doğrulandı — sözleşmenin açık maddeler listesinde bu cümle birebir duruyor.**

### Dosya rayı ve paneli

**50. Rayın katlanabilir olması** — `eklenecek` · davranış · **kesin** (Y1·Y2·Y3)
Bugün ray her zaman açıktır ve 320px yer kaplar; başlığı sabit bir etikettir, kapatmanın yolu yoktur →
tasarım v2'de başlığın kendisi katlama düğmesidir — etiket + dosya sayısı + chevron. Basınca ray
**46px'lik bir şeride** iner: etiket 90 derece döndürülmüş yazılır, sayı okunur kalır, şeride tek
tıklama rayı geri açar. Seçim oturum boyunca sohbetler ve projeler arasında korunur ve bir dosyayı
açan her eylem rayı zorla geri açar. Genişlik geçişi 220ms sürer.

**51. Ray başlığındaki dosya sayısı** — `eklenecek` · görsel · **güçlü** (Y2·Y3)
Bugün başlık yalnız "Project files" yazar, kaç dosya olduğunu söylemez → tasarım v2'de etiketin
yanında sayı durur ve ray katlandığında bile okunur kalır.

**52. Raydaki satırların düğmeleri** — `değişecek` · davranış · **güçlü** (Y1·Y2)
Bugün raydaki satır proje ekranındakiyle birebir aynıdır: üstüne gelince "name" ve "×" belirir,
buradan silinen dosya için rayın içinde bir geri alma şeridi çıkar → tasarım v2'de raydaki satır
yalnız çip, ad ve zaman taşır ve tek işi dosyayı açmaktır; silme ve geri alma proje ekranındaki
listede kalır.

**53. Dosya açılınca ray listesinin yerinde kalması** — `değişecek` · davranış · **güçlü** (Y2·Y3)
Bugün sohbette bir dosya açılınca ray 560px'e genişler ama içindeki liste bütünüyle okuyucuyla
değişir; panel kapanmadan başka bir dosyaya geçilemez → tasarım v2'de ray genişlerken dosya satırları
yerinde kalır ve açık dosyanın satırı seçili görünür.

**54. Dosya satırı iki satıra açılıyor** — `değişecek` · görsel · **güçlü** (Y1·Y3)
Bugün çip, ad ve zaman tek satırda yan yana durur, zaman sağa yaslıdır → tasarım v2'de ad ile ikincil
metin alt alta durur — ad 13.5px üstte, mono 11px ikincil satır hemen altında — ve çip solda ikisinin
hizasında kalır.
**Elle doğrulandı — iki madde birleşti ve damga yükseldi.** Çakıştırmada ayrı sanılmışlardı: çizilmiş
hâle bakan yol satırın **yerleşimini** (ad üstte, ikincil metin altta), yazılı sözleşmeye bakan yol
aynı satırın **metnini** ("project file · 2h ago") görmüş. İkisi aynı değişikliğin iki yüzü.

**55.** — madde 54 ile birleşti.

**56. Uzantı çipinin biçimi** — `değişecek` · görsel · **güçlü** (Y1·Y2)
Bugün çip metne göre daralıp genişleyen küçük bir etikettir: 10px mono, 3/6px dolgu, 5px yarıçap,
`#f0ece5` zemin → tasarım v2'de çip sabit **30×30px** bir kareye dönüşür: 7px yarıçap, ortalanmış
9.5px mono büyük harf, `#F0E7DE` zemin — uzantı ne kadar uzun olursa olsun satırın hizası kaymaz.

**57. Rayın kendi zemini** — `değişecek` · görsel · **güçlü** (Y1·Y2)
Bugün rayın zemini yoktur, tuval rengini gösterir; onu ayıran tek şey soldaki çizgidir → tasarım v2'de
ray kendi zeminini alır (`#FBF9F5`) ve çizgiyle birlikte ayrı bir yüzey olarak durur; dar pencerede
sohbetin altına indiğinde de aynı zeminle iner.

### Dosya okuma

**58. Okuyucunun gövdesi** — `değişecek` · görsel · **güçlü** (Y1·Y2)
Bugün dosya içeriği düz metin olarak, 14px/1.75 ile yazılır → tasarım v2'de içerik Markdown olarak ve
belge ölçeğiyle çizilir (14.5px, 1.8 satır aralığı, 26/28px iç boşluk); başlıklar serif, tablolar mono
başlıklı olur.

**59. Okuyucunun alt bilgisi** — `değişecek` · görsel · **güçlü** (Y1·Y2)
Bugün içeriğin altında mono bir satır "md · 1.2 KB · 2h ago" yazar ve içerikle birlikte kayar →
tasarım v2'de aynı yerde "2h ago · project file" yazar; satır panelin dibine sabitlenir, üstünde bir
ayırıcı çizgiyle durur ve gövde kayarken yerinde kalır. Başlık satırı da tepeye sabitlenir.

**60. Proje ekranındaki panelin kapatma düğmesi** — `değişecek` · görsel · **kesin** (Y1·Y2·Y3)
Bugün proje ekranında açılan panel sohbet rayındakinin aynısıdır: solda "←", sonra ad, sonra
"Download" → tasarım v2'de proje ekranının paneli geri oku taşımaz; sırayla dosya adı, "Download" ve
en sağda bir "×" durur. Sohbet rayındaki panel "←" ile kalır.

**61. Panel açıkken dosya sütununun kalkması** — `değişecek` · davranış · **zayıf sinyal** (Y2)
Bugün proje ekranında bir dosya açılınca 560px'lik panel belirir ve ızgara tek sütuna iner, ama
sohbetler ve dosyalar sütunları alt alta yığılarak ekranda kalır — aynı dosya listesi hem solda hem
panelde durur → tasarım v2'de panel açıkken **dosyalar sütunu hiç çizilmez**; solda yalnız başlık,
composer ve sohbet listesi kalır.
**Elle doğrulandı.** Sözleşme "proje ekranında 560px'lik panel yandan açılır ve **ızgara tek sütuna
iner**" diyor; hangi sütunun düştüğünü yazmıyor, ama panel zaten dosyayı gösterdiği için ayakta kalan
sütunun sohbetler olması sözleşmeyle tutarlı. Çalışan örnek de bunu yapıyor.

**62. İndirme sırasındaki dönen halka** — `değişecek` · görsel · **zayıf sinyal** (Y1)
Bugün "Download" basılınca düğme "preparing…" yazısına ve 11px'lik, 1.5px kalınlığında dönen bir
halkaya dönüşür → tasarım v2'de halka 2px kalınlığında olur ve halka ile yazı arasındaki boşluk 8px'e
çıkar.
**Elle doğrulandı** — görünür ölçü, ama listedeki en düşük etkili madde; sözleşme yalnız `downloading`
hâlinin varlığını yazıyor, ölçüsünü değil.

### Durumlar ve hata

**63. Cevap alınamadığında görünen kart** — `değişecek` · davranış · **kesin** (Y1·Y2·Y3)
Bugün kart iki satır gösterir: "Couldn't get a response." ve altında mono ile servisin kendi sözleri;
sağında "Try again" durur → tasarım v2'de kart tek satır olur: "Couldn't get a response. The
connection dropped." yanında "Try again". *İki ifade birbirini tutmuyor — biri sebebi hiç söylemiyor,
öteki bağlantının koptuğunu söylüyor. Bu belge hangisinin doğru olduğunu söylemez.*

**64. Çevrimdışı şeridi** — `değişecek` · görsel · **güçlü** (Y1·Y2)
Bugün ana bölgenin tepesinde sarımsı bir şerit belirir (`#fbf6ec` zemin, `#eadfc8` alt çizgi,
`#8a6a37` yazı) ve "You're offline. Messages are saved; Mira will answer when the connection is back."
der → tasarım v2'de şerit kızılımsı olur (`#F5E9E3` / `#E7D3C8` / `#8A5237`), cümlenin solunda 7px'lik
dolu vurgu rengi bir nokta durur ve metin "You're offline — messages are saved and will send when you
reconnect." olur.

**65. İlk yükleme iskeleti** — `değişecek` · görsel · **güçlü** (Y1·Y2)
Bugün bekleyen her liste kendi iskeletini çizer ve ekranın geri kalanı (selamlama, composer,
başlıklar) gerçek hâliyle durur → tasarım v2'de yükleme sırasında ana bölgenin tamamı tek bir iskelete
bırakılır: 280×38 bir çubuk, 104px bir blok, 180×16 bir çubuk ve altında iki sütunlu dört adet 96px
kart; kenar çubuğu bu sırada dolu görünür ki gezinme kilitlenmesin. Blokların yanıp sönmesi 1.4s ve
kademeli gecikmelidir.

**66. Adresten gelen "bulunamadı" hâlleri** — `öksüz` · davranış · **güçlü** (Y1·Y2)
Bugün olmayan bir projeye gidilince "That project does not exist.", olmayan bir sohbete gidilince
"That chat does not exist.", açık dosya silinmişse "That file is gone." çıkar; proje listesi
çekilemezse tek satırlık bir hata metni belirir → tasarım v2'de karşılığı yok. *Tasarım sekiz durum
sayıyor (idle · sending · typing · generating · error · loading · downloading · offline) ve bunların
arasında yanlış adres ya da çekilemeyen liste yok; adres çubuğuyla doğrudan bir ekrana gidilebildiğini
de hiç anmıyor.*

### Klavye ve erişilebilirlik

**67. Esc'in kapatma sırası ve ⌘K** — `değişecek` · davranış · **kesin** (Y1·Y2·Y3)
Bugün ⌘K/Ctrl+K arama katmanını açıp kapatır; Esc önce arama katmanını, o kapalıysa açık dosya
panelini kapatır → tasarım v2'de ⌘K'nın bağlandığı bir şey kalmaz ve Esc sırayla şunları kapatır:
proje ⋯ menüsü → silme onay kutusu → Skills menüsü → model menüsü → açık dosya paneli. Hiçbir zaman
geri gitmez.

**68. Menülerin dışına tıklamak** — `eklenecek` · davranış · **güçlü** (Y1·Y3)
Bugün kapanabilir tek katman aramadır → tasarım v2'de model menüsü, Skills menüsü ve proje satır
menüsünün her biri ekranın tamamını kaplayan görünmez bir yakalayıcıyla açılır: menünün dışına
tıklamak onu kapatır. Silme onay kutusunda karartının kendisine tıklamak iptal sayılır.

**69. Satırların gerçek düğme olması** — `değişecek` · davranış · **güçlü** (Y2·Y3)
Bugün proje ekranındaki sohbet satırları ve dosya satırları düğme değil tıklanabilir kutulardır:
sekmeyle sıraya girmezler, Enter/Boşluk ile açılmazlar, odak halkası almazlar; yıkıcı düğmeler kendini
yalnız ekran okuyucuya tanıtır → tasarım v2'de her satır gerçek bir düğmedir ve yıkıcı eylemler fareyle
üstünde beklenince okunan bir başlık taşır.

### Duyarlı yerleşim

**70. Ölçünün kaynağı ve kırılma noktaları** — `değişecek` · görsel · **kesin** (Y1·Y2·Y3)
Bugün tek bir eşik var, 1100px, ve ölçü tarayıcı penceresinin genişliğidir → tasarım v2'de ölçü
**kabuğun kendi ölçülen genişliğidir** (aynı ekran gömülü bir çerçeve içinde de doğru davransın diye)
ve üç eşik olur: **1000px** (ray ve panel alta iner, proje ekranı tek sütuna düşer, açılan panel alanın
tamamını alır), **780px** (yatay dolgu 32→20px, Home kartları tek sütuna iner, başlıklar 42→31 ve
36→27px küçülür, sohbet satırındaki zaman gizlenir), **640px** (kenar çubuğu 172px'e ve dolgusu
14/10'a iner).

**71. Dar ekranda okuma panelinin sütunun yerine geçmesi** — `eklenecek` · davranış · **güçlü** (Y1·Y2)
Bugün dar pencerede dosya paneli açıldığında sohbet ya da proje sütunu yerinde kalır, panel altına
eklenir ve sayfa uzar → tasarım v2'de 1000px altında bir dosya açıldığında sütun ekrandan tümüyle
kalkar ve okuyucu bütün alanı alır; panel kapanınca sütun geri gelir.

**72. Dar ekranda rayın yüksekliği** — `değişecek` · görsel · **kesin** (Y1·Y2·Y3)
Bugün ray sohbetin altına indiğinde yüksekliği içeriğine göre serbest kalır ve sayfa bütünüyle kayar →
tasarım v2'de alta inen ray alanın **%44'ü** kadar bir bant olur (en çok 250px, en az 150px), kendi
içinde kayar ve sohbet üstte kendi kaydırmasını sürdürür. Katlanmışsa bant dikey şerit yerine tek bir
başlık satırına iner.

**73. Dar pencerede başlıkların ve zaman damgasının davranışı** — `eklenecek` · görsel · **kesin** (Y1·Y2·Y3)
Bugün Home'un 42px'lik ve proje ekranının 36px'lik başlığı her genişlikte aynı kalır, sohbet satırının
zaman damgası hiç gizlenmez → tasarım v2'de 780px altında başlıklar 31px ve 27px'e iner, sohbet
satırının zaman damgası satırdan kalkar.

### Görsel dil

**74. Palete yıkıcı bir renk giriyor** — `eklenecek` · görsel · **kesin, değerinde çelişki** (Y1·Y2·Y3)
Bugün palette kırmızı yoktur: silme düğmeleri gri durur, üstüne gelince sıcak kahverengiye (`#8a5237`)
döner ve dolu kırmızı bir düğme hiçbir yerde çizilmez → tasarım v2'de yıkıcı eylemler için ayrı bir
renk tanımlanır; proje başlığındaki Delete çerçevesi, ⋯ menüsündeki "Delete project" satırı ve onay
kutusunun dolu düğmesi bu renkle çizilir. Vurgu rengi tek başına kalır ve yalnız birincil eylemi
işaretler. **Çelişki:** sözleşmenin markdown hâlindeki renk tablosu yıkıcıyı `#8F4A2C` diyor; aynı
belgenin yıkıcı eylemler bölümü, sayfa hâlinin renk şeridi ve çalışan örneğin bütün yıkıcı yüzeyleri
`#B23A2E` kullanıyor. İki değer de burada duruyor.

**75. Vurgu renginin üstüne gelme tonu** — `değişecek` · görsel · **güçlü** (Y2·Y3)
Bugün dolu vurgu düğmelerinin üstüne gelince zemin `#8f4a2c`e koyulur ve aynı değer bağlantılar için
de kullanılır → tasarım v2'de dolu vurgu düğmeleri `#9E5232`e koyulur; bağlantıların üstüne gelme
rengi `#8F4A2C` kalır — iki kullanım ayrışır.

**76. Hareketin bandı** — `değişecek` · görsel · **güçlü, kendi içinde çelişkili** (Y2·Y3)
Bugün Home açılınca sütun 400ms'de aşağıdan yukarı süzülür, proje ve sohbet sütunu 350ms'de, dosya
kartı 250ms'de, arama katmanı 150ms'de; rayın genişlemesi 220ms sürer → tasarım v2'de hareketin
tamamı **140–220ms**'lik opaklık geçişleri ile rayın 220ms'lik genişlik geçişinden ibarettir ve
yerleşmiş hiçbir öğe yana kaymaz. **Çelişki:** sözleşmenin iki hâli de bu bandı yazıyor, ama aynı
tasarımın çalışan örneği Home'un sütununu 400ms'de, proje/sohbet sütununu 350ms'de ve 6px'lik bir
yukarı süzülmeyle çiziyor. İkisi de burada duruyor.

**77. Yarıçap kümesi** — `değişecek` · görsel · **kesin** (Y1·Y2·Y3)
Bugün küme 8/9/12/16/20px arasında dağılmıştır: kenar çubuğu denetimleri 9px, satırlar ve şerit 8px,
kaplar 12px, composer 16px → tasarım v2'de yarıçaplar üç değerde toplanır — **denetim 8px, kart
12–14px, hap 20px** — ve bu kümenin içinde menüler 12px, satır menüsü 11px, onay kutusu 14px, geri
alma şeridi 10px, alttaki koyu şerit 11px olarak ayrışır.

---

## 3 · Bugünkü uygulamanın Mira v1'den sapmaları

Bu bölüm tasarım v2 farkı **değildir.** Uygulamanın kendi tarifini — Mira v1 belgesini ve yol
haritasını — tutturamadığı yerlerdir; hepsi ters yönden yürüyen tek yolun (Y2) bulgusudur ve
damgalanmaz.

**78. Home composer'ının hedef etiketi hiç çıkmıyor** — `düzeltilecek` · görsel
Bugün Home'da composer'a yazılmaya başlandığında kutunun altında yalnız Send belirir; mesajın nereye
gideceğini söyleyen mono satır hiçbir anda çıkmaz. *Tarifi neydi:* Faz 5 kararı Home'un mono etiketini
"a new project" olarak belirlemişti.

**79. Öğretici ikinci satır, dosya listesi doluyken de duruyor** — `düzeltilecek` · görsel
Bugün "Chats create the files; you just open and read them." satırı liste dolduktan sonra da kalır;
sohbetteki ray ise boşken bile o satırı hiç göstermez. *Tarifi neydi:* Faz 3 iki cümleyi birlikte
**boş** dosya listesinin öğretici metni olarak tanımlamıştı.

> **Güncelleme (18 Ağustos, Madde 32): kapandı.** İkinci satır üründe yok; hem ray hem proje sütunu
> tek cümle gösteriyor ve o cümle yalnız liste boşken çıkıyor. Madde 20-22 ray ile sütunu yeniden
> yazarken kapanmıştı; Madde 32 bunu doğruladı ve yapacak iş bulmadı.

**80. Bekleme etiketi saatsiz kalıyor** — `düzeltilecek` · görsel
Bugün üç noktanın üstünde yalnız ürün adı yazar; saat ancak akış bitip cevap kaydedildikten sonra
belirir. *Tarifi neydi:* Madde 14 ekranda "MIRA · saat" etiketini ve üç noktayı **birlikte**
istiyordu.

**81. Reddedilen mesaj, motor arızasının kartını çıkarıyor** — `düzeltilecek` · davranış
Bugün sunucu bir mesajı reddederse iyimser balon geri alınır ve yerine "Couldn't get a response."
kartı ile "Try again" çıkar — hiç gönderilememiş bir mesaj, cevabı alınamamış bir mesajın diliyle
anlatılır. *Tarifi neydi:* Faz 5 bu durumda **tek satır hata** istiyordu; "Couldn't get a response."
kartı Faz 7'de akışın ölmesi için tanımlanmıştı.

**82. Sunucunun kendi cümlesi ekrana hiç ulaşmıyor** — `düzeltilecek` · davranış
Bugün tarayıcının tek istek yolu sunucunun gövdesini atıp yerine yöntem, adres ve durum kodunu yazar:
ekrana "POST /api/… failed with 409" çıkar, sunucunun yazdığı "a file by that name is back in the
project" cümlesi hiçbir yerde görünmez. Yalnız motor arızası bu kuraldan kaçar. *Tarifi neydi:* Faz 11
"altında **sunucunun kendi sözleri** yazar; sebep uydurulmaz", Faz 2 "sunucunun gerçek çıktısı
gösterilir" diyordu.

**83. Çekilemeyen liste, boş liste gibi konuşuyor** — `düzeltilecek` · davranış
Bugün dosya listesi isteği başarısız olursa iskelet kaybolur ve yerine "No files yet — start a chat
and Mira will create one." çıkar; sohbet listesi başarısız olursa sütun sessizce boşalır. Ekran,
cevabını alamadığı bir soruya "hiç yok" diye cevap vermiş olur. *Tarifi neydi:* Faz 14 `loading`
alanını tam da bunun için getirmişti — "boş-durum cümleleri yalnız yükleme bittikten sonra çıkar".

**84. Okunan dosya, projeden çıkıp dönünce kendiliğinden yeniden açılıyor** — `düzeltilecek` · davranış
Bugün bir projede dosya açıkken başka projeye geçilince panel kapanmış görünür; geri dönüldüğünde aynı
dosya yeniden açılır. *Tarifi neydi:* Faz 10 "açık dosya… **proje değişince kapanır**" diyordu —
kapatma anıydı, gizleme anı değil.

**85. Model `.md` dışında bir uzantı isterse o uzantıyla yazılıyor** — `düzeltilecek` · davranış
Bugün gelen ad zaten bir uzantıyla bitiyorsa olduğu gibi kabul edilir: "report.txt" isteyen bir model
projeye `report.txt` bırakır. *Tarifi neydi:* Faz 8 "uzantı yoksa `.md` eklenir. **v1'de üretilen
dosya markdown'dır**" diyordu.

> **Güncelleme (18 Ağustos, Madde 32): bu sapma eskidi, düzeltilmiyor.** Dayanağı v1'in "üretilen
> dosya markdown'dır" cümlesiydi; Faz 7 onu geçersiz kıldı — `Generate prompts+` bir `.json` yapı
> dosyası yazıyor, `build_prompts` bir `.py` üretiyor, okuyucu Madde 30'da ikisini göstermeyi
> öğrendi. Uzantıyı `.md`'ye çevirmek bugün üretim hattını kırardı. Bugünkü davranış bilerek
> kalıyor: uzantı verilmişse korunur, verilmemişse `.md` eklenir.

**86. Composer ve arama kutusunda odak halkası çıkmıyor** — `düzeltilecek` · görsel
Bugün sekmeyle dolaşırken her düğme ve satır 2px'lik vurgu renkli halka kazanır, ama sıra composer'ın
metin alanına ya da arama girdisine gelince halka hiç çizilmez. *Tarifi neydi:* Faz 0 odağı uygulama
genelinde tek kural yapıyordu — "hiçbir madde kendi odak stilini yazmaz".

**87. Ekran ve kart girişleri izin verilen hareket bandının dışında** — `düzeltilecek` · görsel
Bugün Home 400ms, proje ve sohbet 350ms, dosya kartı 250ms, arama katmanı 150ms'de belirir. *Tarifi
neydi:* Mira v1 hareketi tek banda kapatıyordu — "yalnız opaklık geçişleri (180–220ms) ve rayın
genişlik geçişi (220ms)". (Tasarım v2 aynı bandı 140–220ms diye yeniden yazıyor; madde 76.)

**88. Denetimlerin yarıçapı 8px yerine 9px** — `düzeltilecek` · görsel
Bugün kenar çubuğundaki Search kutusu, New chat düğmesi, proje satırları ve Send düğmesi 9px
yuvarlatılır; aynı ekrandaki sohbet ve dosya satırları 8px yuvarlatılır — köşeler yan yana
eşleşmez. *Tarifi neydi:* Mira v1 yarıçapları üçe kilitliyordu: kontrol 8px, kart 12–14px, hap 20px.

**89. Composer kutusunun yarıçapı kart bandının dışında** — `düzeltilecek` · görsel
Bugün composer 16px yuvarlatılır; yanındaki proje ve dosya kartları 12–14px. *Tarifi neydi:* Mira v1
kart yarıçapını 12–14px'e bağlamıştı ve bu aralığın dışında bir yüzey tanımlamıyordu. (Tasarım v2 bu
kutuyu ekrana göre ayırıyor; madde 38.)

---

## 4 · Repo belgeleri çarpışması

Tasarım v2'nin, repodaki yazılı kuralların **kendisiyle** çeliştiği yerler. Bu bölüm iki metni yan
yana koyar; hangisinin kazanacağını söylemez.

| Konu | Repo belgesi bugün ne diyor | Tasarım v2 ne getiriyor |
|---|---|---|
| Ürün adı | `CLAUDE.md` bölümü "**mira** — Mira (web UI)"; `FOUNDATION.md` ve `CODE-STANDARD.md` başlıkları "Mira"; klasör `mira/`; kök değişkeni `MIRA_ROOT` | Ürün her yüzeyde **QueenAgent** |
| Yıkıcı eylem güvencesi | `FOUNDATION.md` 1. ilke: "Every destructive action is either explicitly confirmed or explicitly undoable — **never neither**" | Sohbet silme **ne onay sorar ne geri alma sunar** (madde 29) |
| Cevap–dosya ilişkisi | `CLAUDE.md`: model "decides whether a reply becomes a file"; Mira v1'in kendi ifadesiyle "tasarımda olmayan tek yeni hâl: dosyasız cevap" | Çekirdek döngüde akış biter bitmez **tek bir dosya** doğar; dosyasız cevap hâli yok (madde 48) |
| Arama | `CODE-STANDARD.md`: "Search is a use case inside `workspace`, not a feature of its own" | Arama üç parçasıyla birlikte **bilerek kaldırılmış** (madde 6) |
| Hata metninin kaynağı | `CLAUDE.md` monorepo kuralı: "**Never invent a cause in an error message.** Print what the command or the service actually said" | Hata kartı tek satırda sebebi kendisi söylüyor: "Couldn't get a response. **The connection dropped.**" (madde 63) — bağlantının koptuğu servisin söylediği değil, kartın varsaydığı şey |
| Proje verisi | `CODE-STANDARD.md` mağaza tablosu: `project.json` — "what is this project called and **how does it look**" | Proje açıklaması hem veri alanı hem arayüz olarak kalkıyor (madde 20); projeye bağlı renk kimliğinden hiç söz edilmiyor (madde 5) |
| Ajan araçları | `CLAUDE.md`: ajan döngüsünün **üç aracı** — `list_files`, `read_file`, `create_file` | Skills seçicisi "Web search" ve "Deep research" sunuyor (madde 33); bunların hangi araçla karşılanacağı tasarımda yazılı değil |
| Ürünün amaç alanı | `CLAUDE.md`: "küçük bir AI çalışma alanı… hiçbir üretim hattına bağlı değil"; Mira v1 belgesi: "amaç alanı serbesttir" | Tasarım Skills seçicisini getiriyor (madde 33) ve dört seçeneğini yer tutucu olarak çiziyor. **Kullanıcının verdiği gerçek beceri kümesi** — senaryo oluştur · senaryoyu parçalara böl (hangi sahne kaç prompt) · promptları oluştur — ürünü bir üretim hattının ön yüzü hâline getiriyor. *Bu satırın kaynağı tasarım değil, kullanıcıdır; tasarım yalnız seçicinin varlığını getiriyor.* |
| Model seçimi | `CLAUDE.md`: "xAI Grok drives an agent loop"; model sunucu ayarından tek değer | Dört model kullanıcıya sunuluyor ve seçim sohbete yapışıyor (madde 32, 34) |
| Görsel dilin sahibi | `CODE-STANDARD.md`: "`shared/app.css` owns the colour variables, the radii, the focus ring and the four keyframes… The accent `--accent` marks the primary action and nothing else" | Palete ayrı bir **yıkıcı renk** giriyor (madde 74), yarıçap kümesi yeniden toplanıyor (madde 77), hareket bandı 140–220ms'e çekiliyor (madde 76) |
| Arayüz dili | `CODE-STANDARD.md`: "Everything is English… Do not carry the neighbouring tool's rule over here" | Değişmiyor — tasarımın bütün metinleri İngilizce |

---

## 5 · Tasarımın cevaplamadıkları

Tasarım v2'nin sustuğu ya da kendi açık maddesi olarak bıraktığı konular. Uydurulmadı, işaretlendi.

**Tasarımın kendi "Open items" listesi:** dosya sürümleme (v1/v2 + diff) · dosya yeniden adlandırma ·
dosya listesini sıralama ve filtreleme · arka uçtan gerçek akış · sohbet silmeden önce onay · model
seçiminin sunucuda saklanması. Bunlardan **dördü bugün uygulamada zaten var** (dosya yeniden
adlandırma, gerçek akış, sohbet silme onayı ve — kısmen — sunucu tarafı model ayarı), yani tasarımın
"henüz karar vermedim" dediği yerde uygulamanın verilmiş bir kararı duruyor.

**Sözleşmede adı geçip hiç tarif edilmeyen:** Skills menüsü, sözleşmenin markdown hâlinde yalnız
klavye sırasında ("Esc closes… skills menu") anılıyor; ne olduğu, ne yaptığı ve seçimin cevabı nasıl
değiştireceği yalnız sayfa hâlinde ve çalışan örnekte var.

**Hiç sorulmamış olanlar:**

- **Proje yaratmanın yolları yazıya geçmemiş.** Sözleşme yalnız boş hâl ekranındaki "+ New project"
  düğmesini anıyor; kenar çubuğundaki "+" düğmesi ile Home'un "Projects" başlık satırındaki "New
  project" düğmesi çizimde var ama hiçbir yerde yazılı değil. Tuvalde de proje yaratmayı gösteren tek
  kare boş hâl karesi. (Bu bir fark değil — ikisi de bugün uygulamada duruyor; madde 11.)
- Kullanıcının adı nereden gelecek (madde 3).
- Kaldırılan logo işaretinin yerine bir şey konacak mı (madde 2).
- Home'dan gönderilen mesaj **hangi** projeye düşecek (madde 18).
- Üretilen dosyanın adı ikinci kez aynı çıkarsa ne olacak (madde 4).
- Bir haftadan eski kayıtların tarihi nasıl yazılacak (madde 14).
- Dosya geri alma şeridi bir hata cümlesi taşıyacak mı (madde 31).
- Adres çubuğuyla doğrudan bir ekrana gidilebilmesi (madde 66) — tasarımın verisi bellekte durduğu
  için yanlış adres diye bir hâl tarif edilmiyor.
- Projeye bağlı renk kimliği (madde 5) — kaldırıldığı söylenmiyor, hiç anılmıyor.
- Dosyasız cevap (madde 48) — ne kaldırılanlar ne açık maddeler arasında; sekiz durumun içinde de
  yok.

**Sözleşmenin kendi içindeki çelişkiler (tekrar):** model düğmesinin yeri (madde 35), açılır kutunun
konumlanma kuralı (madde 36), yıkıcı rengin değeri (madde 74), hareket bandı ile çalışan örneğin
süreleri (madde 76), ve sohbetin yeniden adlandırılamaması ile 780px'te "`name` düğmesi gizlenir"
kuralı (madde 22).

---

## Ek A · Çakıştırma tablosu

Her maddeyi hangi yolun gördüğü. **Y1** yalnız tasarımın çizilmiş hâline baktı, **Y3** yalnız yazılı
sözleşmeye, **Y2** ters yönden yürüdü ve tasarımın tamamını gördü. `düzeltilecek` türü yalnız Y2'den
çıkabildiği için damgalanmaz.

| # | Madde | Tür | Y1 | Y2 | Y3 | Damga |
|---|---|---|:-:|:-:|:-:|---|
| 1 | Ürünün adı | değişecek | ✓ | ✓ | ✓ | kesin |
| 2 | Ad yanındaki logo karesi | öksüz | ✓ | ✓ | ✓ | kesin |
| 3 | Kullanıcı satırının etiketi | değişecek | ✓ | ✓ | — | güçlü |
| 4 | Üretilen dosyanın adı nereden çıkıyor | değişecek | — | ✓ | — | zayıf · doğrulandı, dayanağı bağlayıcı değil |
| 5 | Projenin renk noktası | öksüz | — | — | ✓ | zayıf · **kısmen çürütüldü** |
| 6 | Aramanın tamamı | öksüz | ✓ | ✓ | ✓ | kesin |
| 7 | Proje satırında ⋯ menüsü | eklenecek | ✓ | ✓ | ✓ | kesin |
| 8 | "Recent chats" kapsamı | değişecek | ✓ | ✓ | ✓ | kesin |
| 9 | "New chat" düğmesinin varlığı | eklenecek | ✓ | ✓ | ✓ | kesin |
| 10 | Kenar çubuğu genişlik basamakları | değişecek | ✓ | ✓ | ✓ | kesin |
| 11 | "+" düğmesi ve satır rozeti | ~~öksüz~~ | — | — | ✓ | **çürütüldü — fark değil** |
| 12 | Uygulamanın açıldığı ekran | değişecek | — | ✓ | ✓ | güçlü |
| 13 | Kaydırma sözleşmesi | değişecek | — | ✓ | ✓ | güçlü |
| 14 | Bir haftadan eski zaman damgası | değişecek | ✓ | — | — | zayıf · doğrulandı |
| 15 | Sayaçların tekil hâli | değişecek | ✓ | — | — | zayıf · doğrulandı |
| 16 | Selamlama başlığı | öksüz | ✓ | ✓ | ✓ | kesin |
| 17 | Üç öneri hapı | öksüz | ✓ | ✓ | ✓ | kesin |
| 18 | Home mesajının nereye düştüğü | değişecek | ✓ | ✓ | — | güçlü |
| 19 | Home sütununun üst boşluğu | değişecek | ✓ | ✓ | — | güçlü |
| 20 | Proje açıklaması | öksüz | ✓ | ✓ | ✓ | kesin |
| 21 | "← back" düğmesi | öksüz | ✓ | ✓ | ✓ | kesin |
| 22 | Sohbet satırının "name" düğmesi | öksüz | ✓ | ✓ | ✓ | kesin · **çelişki** |
| 23 | Dosya listesi altındaki öğüt satırı | öksüz | — | — | ✓ | zayıf · doğrulandı |
| 24 | Sohbet satırındaki "×"in görünürlüğü | değişecek | ✓ | — | — | zayıf · doğrulandı |
| 25 | Uzun proje adının sarması | eklenecek | ✓ | — | — | zayıf · **en zayıf madde** |
| 26 | Proje silme | eklenecek | ✓ | ✓ | ✓ | kesin |
| 27 | Silinen projenin şeridi ve geri alınması | eklenecek | ✓ | ✓ | ✓ | kesin |
| 28 | Silmenin nereye götürdüğü | eklenecek | — | ✓ | ✓ | güçlü |
| 29 | Sohbet silmenin onayı | değişecek | ✓ | ✓ | ✓ | kesin · **tür çelişkisi** |
| 30 | Dosya yeniden adlandırma | öksüz | ✓ | ✓ | ✓ | kesin |
| 31 | Silinen dosyanın geri alma şeridi | değişecek | ✓ | — | — | zayıf · doğrulandı |
| 32 | Model seçici | eklenecek | ✓ | ✓ | ✓ | kesin |
| 33 | Skills seçici | eklenecek | ✓ | ✓ | ✓ | kesin |
| 34 | Seçimlerin sohbete yapışması | eklenecek | ✓ | ✓ | ✓ | kesin |
| 35 | Model düğmesinin yeri | eklenecek | ✓ | ✓ | ✓ | **çelişki** |
| 36 | Açılır kutunun ekrana sığması | eklenecek | — | ✓ | ✓ | **çelişki** |
| 37 | Composer'ın altındaki yardım notu | öksüz | ✓ | ✓ | ✓ | kesin |
| 38 | Composer kutusunun yarıçapı | değişecek | ✓ | ✓ | — | güçlü |
| 39 | Cevabın Markdown olarak çizilmesi | değişecek | ✓ | ✓ | ✓ | kesin |
| 40 | İki ayrı tipografi ölçeği | eklenecek | ✓ | ✓ | ✓ | kesin |
| 41 | Yarım gelen kod bloğu | eklenecek | — | ✓ | ✓ | güçlü |
| 42 | Akan cevabın ucundaki imleç | eklenecek | ✓ | ✓ | ✓ | kesin |
| 43 | Otomatik kaydırma kuralı | eklenecek | — | ✓ | ✓ | güçlü |
| 44 | Dosya kartı bir kapı oluyor | değişecek | ✓ | ✓ | ✓ | kesin |
| 45 | Açık dosyanın seçili görünmesi | eklenecek | ✓ | ✓ | ✓ | kesin |
| 46 | "creating file…" kutusunun yeri | değişecek | ✓ | ✓ | ✓ | kesin |
| 47 | Bekleme etiketi | değişecek | ✓ | — | ✓ | güçlü |
| 48 | Her cevabın bir dosya doğurması | değişecek | — | ✓ | — | zayıf · doğrulandı |
| 49 | Gerçek akışın kaynağı | öksüz | — | — | ✓ | zayıf · doğrulandı |
| 50 | Rayın katlanabilir olması | eklenecek | ✓ | ✓ | ✓ | kesin |
| 51 | Ray başlığındaki dosya sayısı | eklenecek | — | ✓ | ✓ | güçlü |
| 52 | Raydaki satırların düğmeleri | değişecek | ✓ | ✓ | — | güçlü |
| 53 | Dosya açılınca ray listesinin kalması | değişecek | — | ✓ | ✓ | güçlü |
| 54 | Dosya satırı iki satıra açılıyor | değişecek | ✓ | — | ✓ | güçlü · **birleştirildi** |
| 56 | Uzantı çipinin biçimi | değişecek | ✓ | ✓ | — | güçlü |
| 57 | Rayın kendi zemini | değişecek | ✓ | ✓ | — | güçlü |
| 58 | Okuyucunun gövdesi | değişecek | ✓ | ✓ | — | güçlü |
| 59 | Okuyucunun alt bilgisi | değişecek | ✓ | ✓ | — | güçlü |
| 60 | Proje panelinin kapatma düğmesi | değişecek | ✓ | ✓ | ✓ | kesin |
| 61 | Panel açıkken dosya sütununun kalkması | değişecek | — | ✓ | — | zayıf · doğrulandı |
| 62 | İndirme sırasındaki dönen halka | değişecek | ✓ | — | — | zayıf · doğrulandı |
| 63 | Cevap alınamadığında görünen kart | değişecek | ✓ | ✓ | ✓ | kesin |
| 64 | Çevrimdışı şeridi | değişecek | ✓ | ✓ | — | güçlü |
| 65 | İlk yükleme iskeleti | değişecek | ✓ | ✓ | — | güçlü |
| 66 | Adresten gelen "bulunamadı" hâlleri | öksüz | ✓ | ✓ | — | güçlü |
| 67 | Esc'in kapatma sırası ve ⌘K | değişecek | ✓ | ✓ | ✓ | kesin |
| 68 | Menülerin dışına tıklamak | eklenecek | ✓ | — | ✓ | güçlü |
| 69 | Satırların gerçek düğme olması | değişecek | — | ✓ | ✓ | güçlü |
| 70 | Ölçünün kaynağı ve kırılma noktaları | değişecek | ✓ | ✓ | ✓ | kesin |
| 71 | Dar ekranda panelin sütunun yerine geçmesi | eklenecek | ✓ | ✓ | — | güçlü |
| 72 | Dar ekranda rayın yüksekliği | değişecek | ✓ | ✓ | ✓ | kesin |
| 73 | Dar pencerede başlıklar ve zaman damgası | eklenecek | ✓ | ✓ | ✓ | kesin |
| 74 | Palete yıkıcı bir renk giriyor | eklenecek | ✓ | ✓ | ✓ | kesin · **değer çelişkisi** |
| 75 | Vurgu renginin üstüne gelme tonu | değişecek | — | ✓ | ✓ | güçlü |
| 76 | Hareketin bandı | değişecek | — | ✓ | ✓ | güçlü · **çelişki** |
| 77 | Yarıçap kümesi | değişecek | ✓ | ✓ | ✓ | kesin |
| 78–89 | Mira v1'den sapmalar (12 madde) | düzeltilecek | — | ✓ | — | damgalanmaz |

**Toplam:** 30 kesin · 25 güçlü · 12 zayıf sinyal · 4 çelişki · 12 damgalanmayan sapma. Bir madde
çürütüldü ve fark sayılmıyor (11).

**Elle doğrulama turunun sonucu:** 13 zayıf sinyalin 11'i doğrulandı. **Madde 11 tümüyle çürütüldü** —
hem "+" düğmesi hem satır rozeti tasarımın çizilmiş hâlinde duruyor, yalnız yazılı sözleşmeye
geçmemişler; yalnız sözleşmeye bakan yol yazılmamış olanı yok sanmış. **Madde 5'in iddiası daraldı** —
nokta tasarımda var, tartışmalı olan yalnız projeye özel renk. **Madde 54 ile 55 birleşti** ve damgası
yükseldi: iki yol aynı değişikliğin iki ayrı yüzünü görmüştü. Doğrulanamayan madde kalmadı.

**Yöntem notu.** Çürütülen iki maddenin ikisi de aynı yerden geldi: yalnız yazılı sözleşmeye bakan
yol, sözleşmenin **sustuğu** bir şeyi "yok" sandı. Yazılı kaynak eksiksiz değil; çizilmiş hâlde duran
ama yazıya geçmemiş epey şey var. Bu, üç yollu yöntemin neden çalıştığının da kanıtı — tek bir
kaynağa demirlenmiş bir tur bu iki maddeyi yanlış raporlardı.
