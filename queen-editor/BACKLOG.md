# Backlog — Queen Editor

Gerçek ama henüz bir koşuya bağlanmamış işler. Sırası gelince buradan çıkar, o koşunun yol
haritasına girer.

---

### Fotoğraf üretim hızı — hız LoRA'ları

Üretim hızlansın; yol olarak hız LoRA'ları denenecek. Kazanç fotoğraf tarafında görünüyor, video
zaten hızlı koşacak şekilde ayarlı.

### Video LoRA denemesi — anatomik hatalar

Video üretiminde anatomik hatalar çıkıyor; üretim tarifinin LoRA'ları değiştirilip denenecek.

### Karakter LoRA'sı eklenecek

*(Kullanıcı, 6 Eylül.)* Aynı kişinin her karede aynı çıkması için. Bugün bunu tutan tek şey etiket:
QueenAgent karakteri bir kez yazıp onu adlayan her kareye koyuyor, ama etiket bir yüzü sabitlemiyor.

**Kararlaşmadı:** hazır bir LoRA yüklemek mi, yoksa karakter başına eğitmek mi — ve eğitilecekse o
işin nerede koşacağı.

### Editör kısmı eklenecek

*(Kullanıcı, 6 Eylül.)* Uygulama bugün **üretip dışa aktarıyor**: kare bir fotoğrafla başlıyor,
üstüne video ve ses biniyor, dışa aktarma hepsini tek klasörde birleştiriyor. Çıkanı **değiştiren**
hiçbir yer yok — beğenilmeyen kare yeniden üretiliyor.

Neyi kapsayacağı **kararlaşmadı**: fotoğrafın kendisine dokunmak mı *(kırpma, rötuş, inpaint)*,
video/ses tarafını kesip düzenlemek mi, yoksa karelerin sırasıyla oynamak mı.

### Konuşma özelliği eklenecek

*(Kullanıcı, 11 Eylül.)* Karelerde konuşma olacak. Ne olduğu **daha detaylandırılacak** — kullanıcı
bunu sonraya bıraktı, ve buraya bir tahmin yazılmıyor.

**Kararlaşmadı:** karakterin videoda konuşması mı *(ağzın sözle uyumu)*, kareye konuşma sesinin
binmesi mi *(metinden ses, bugünkü ses katmanının yanına ya da yerine)*, yoksa ikisi birden mi. Bunun
ardından gelen soru da açık: konuşmanın metnini kim yazıyor — kullanıcı mı, QueenAgent mı.

### Toplu seçme — Shift ile aralık

*(Kullanıcı, 11 Eylül.)* Galeride kartlar **Windows'ta dosya seçer gibi** seçilecek: bir karta
tıklanır, Shift basılı tutulup başka bir karta tıklanır, ve aradaki bütün kartlar seçili gelir.

Kullanıcının çerçevesi: bu **tümünü seç'in alternatifi** — arada kalan bir yol, çünkü bugün bir kare
grubunu seçmenin yolu ya tek tek tıklamak ya da hepsini birden almak.

**Kararlaşmadı:** Ctrl ile tek tek ekleme de gelecek mi. Windows'ta ikisi birlikte gelir, ama
kullanıcı yalnız Shift'i saydı.

### Karta sağ tık — bağlam menüsü

*(Kullanıcı, 11 Eylül.)* Karta sağ tıklanınca bir menü açılacak ve oradan iş yapılabilecek; kullanıcı
ikisini saydı, **silme** ve **kopyalama**, ve *"vs"* diyerek listeyi açık bıraktı. Yine **Windows
gibi**.

Eylemlerin kendisi bugün var — seçim barında duruyorlar. Menü yeni bir yetenek değil, aynı işlere
ikinci bir kapı.

**Kararlaşmadı:** menüde silme ve kopyalama dışında ne olacağı. Ve asıl soru: birden çok kart
seçiliyken sağ tıklanan menü **seçimin tamamına** mı uygulanır yoksa yalnız tıklanan karta mı —
Windows'ta seçime uygulanır, ama bu karar burada da aynı olmak zorunda değil.

### Fotoğraf modeli her şeyi NSFW'ye çeviriyor

*(Kullanıcı, 11 Eylül.)* Bugünkü fotoğraf modeli, **başka bir şey istense bile** çıkanı NSFW'ye
çeviriyor. Üretim çalışıyor ve kare geliyor — gelen kare istenen şey olmuyor. Yani eksik olan bir
yetenek değil, modelin kendi eğilimi.

**Kararlaşmadı:** çözümün yeni bir fotoğraf modeli eklemek mi *(bugünkünün yanına, kare bazında
seçilebilir)*, bugünküyü değiştirmek mi, yoksa LoRA ya da prompt tarafında kalmak mı olduğu.

---

## Hedefler

**Bölünmeden koşuya giremeyecek kadar büyük işler.** Yukarıdaki liste bir yol haritasının olduğu gibi
alabileceği maddeleri tutuyor; burası ise tek madde olmayı reddedenleri.

Bir hedefin sırası geldiğinde yapılan **ilk iş onu parçalara ayırmaktır**. Parçalar yukarıdaki
listeye ya da doğrudan o koşunun yol haritasına gider; hedefin kendisi, parçaları bitene kadar
burada durur.

### AI agent implement edilecek

*(Kullanıcı, 11 Eylül.)* Kullanıcının kendi tarifi: **çok büyük ve zorlayıcı bir iş**, küçük parçalara
bölünerek yapılacak. Buraya yazılmasının sebebi bu.

**Kararlaşmadı — henüz hiçbiri:** agent'ın queen-editor'ün içinde ne yapacağı; bu depoda zaten duran
**QueenAgent'la ilişkisi** *(onun taşınması mı, yanına ayrı bir şey mi, ikisinin konuşması mı)*; ve
parçalanmanın nereden başlayacağı. Üçü de sırası gelince detaylandırılacak, ve buraya bir tahmin
yazılmıyor.
