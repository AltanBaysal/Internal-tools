# Backlog — Queen Editor

Gerçek ama henüz bir koşuya bağlanmamış işler. Sırası gelince buradan çıkar, o koşunun yol
haritasına girer.

---

### Hata — silinen standart videodan sonra loop eklenince ikisi birden üretiliyor gibi görünüyor

*(Kullanıcı bildirimi, 6 Eylül.)*

**Nasıl çıktı:** kareye standart video eklendi → silindi → yerine loop video eklendi. Ekranda **ikisi
birden** üretiliyormuş gibi görünüyor, standart ve loop yan yana.

Sebebi **araştırılmadı**, ve buraya bir tahmin yazılmıyor: silinen işin gerçekten iptal edilmemesi de
olabilir, yalnız ön yüzün eski satırı bırakması da. İkisi çok farklı yerlerde durur.

**Ele alınırken kullanıcıya sorulacak:** silinen video gerçekten üretilmiş miydi yoksa sırada mıydı,
ekranda kaç satır göründü, ve dışa aktarmaya hangisi düştü — yani hata yalnız görüntüde mi, yoksa
diske de mi ulaşıyor.

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

### MiniMax eklenecek

*(Kullanıcı, 6 Eylül.)* Hangi işi alacağı — fotoğraf mı video mu, bugünkü tarifin yerine mi yanına
mı — **kararlaşmadı.**

### Slime girl videosu eklenecek

*(Kullanıcı, 6 Eylül.)* Bir video türü — *slime girl*. Bir model değil, üretilecek bir içerik biçimi.

**Kararlaşmadı:** kendi LoRA'sıyla mı geliyor, kendi üretim tarifiyle mi, yoksa yalnız prompt
tarafında mı kalıyor.
