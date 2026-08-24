# Backlog — bekleyen işler

Gerçek ama henüz bir koşuya bağlanmamış işler. Sırası gelince buradan çıkar, o koşunun yol
haritasına girer.

---

### Fotoğraf üretim hızı — hız LoRA'ları

Üretim hızlansın; yol olarak hız LoRA'ları denenecek. Kazanç fotoğraf tarafında görünüyor, video
zaten hızlı koşacak şekilde ayarlı.

### Video LoRA denemesi — anatomik hatalar

Video üretiminde anatomik hatalar çıkıyor; üretim tarifinin LoRA'ları değiştirilip denenecek.

### Önbellek koşular arasında yaşamıyor — sabit adres

Her Colab koşusu yeni bir trycloudflare adresi alıyor. Tarayıcıda bayt saklayan her depo — HTTP
önbelleği, Cache Storage, IndexedDB — origin'e, yani konak adının kendisine göre bölünmüş durduğu
için dün tamamen inmiş bir fotoğraf bugün yabancı sayılıp yeniden iniyor. Kendi önbelleğimizi
yazmak bunu çözmüyor; tek kapı adresi sabitlemek, o da cloudflared'in named tunnel kipi ve
kullanıcının kendi alan adı.

İş defterin tünel satırında duruyor: uygulamanın kodu değişmiyor, foto rotasındaki `immutable`
başlığı adres sabitlendiği gün kendiliğinden ikinci yarısını da yapmaya başlar. Başlayabilmesi için
alan adının nameserver'larının Cloudflare'i göstermesi ve Colab secret'ına bir tünel token'ı
konması gerekiyor — ikisi de kullanıcının tarafında.

Kararı bekleyen yan etki: sabit adres, koşu ayaktayken herkesin bilebileceği kalıcı bir kapı demek;
bugünkü rastgele adresin sağladığı örtü kalkıyor. Yol haritası v14, madde 29.

### Gönderilmemiş prompt metni kayboluyor — iki ekranın aynı soruya iki cevabı

Fotoğraf üret panelinin kutularına yazılan metin yalnızca **Kuyruğa ekle**'ye basıldığında kayda
geçiyor. Yazıp basmadan bir kareye bakmaya gidince dönüşte kutular boş.

Tek başına bir eksik gibi görünüyor ama değil: detay sayfası aynı soruya bilerek *"kare terk edilince
yazı ölür"* diye cevap vermiş durumda (v4 tasarım kuralı, madde 76). Paneli hatırlar hâle getirmek
iki ekranı birbirine ters düşürür, ikisini birden değiştirmek de "kaydedilmemiş yazı ne kadar
yaşamalı" sorusunun kendisini açar — o da bir tasarım kararı, bir düzeltme değil.

Karar kullanıcınındır. Yol haritası v14, K bölümü, dışarıda bırakılan iş.
