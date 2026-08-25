# Backlog — QueenAgent

Gerçek ama henüz bir koşuya bağlanmamış işler. Sırası gelince buradan çıkar, o koşunun yol
haritasına girer.

---

### Grok Build varsayılan ve tek model olsun

Sohbetler bugün Grok 4.3 ile açılıyor ve menüde altı model duruyor; istenen, Grok Build'in hem
varsayılan hem de tek model olması — o zaman model seçicinin de bir işi kalmıyor. Sert bir
çarpışma var: Grok Build'in penceresi 256k, oysa bugün bağlam hızla 300-500k'ya çıkıyor. Yani bu
madde, bir alttaki context maddesi çözülmeden açılamaz.

### Context yönetimi ve işi böldürme

Bağlam çok hızlı büyüyor, 300-500k'yı buluyor: bir cevap on altı tura kadar dönerken her turda
sohbetin tamamı yeniden gönderiliyor. İşi parçalara bölme isteği şu an yalnız skill metinlerinde
bir ricâ; tutan bir şey yok. Hem isteğin nasıl kurulduğu hem de uzun işin gerçekten parçalanması
için modern bir çözüm gerekiyor.

### Doküman güncellenmiyor, yeniden yaratılıyor

Model var olan dosyayı düzeltmek yerine yenisini yazıyor, yaratma aracı da üstüne yazmadığı için
eski dosya yerinde kalıyor ve yanına numaralı bir kopya düşüyor. Aynı işin iki sürümü duruyor,
bir sonraki adımın hangisini okuyacağı belirsizleşiyor. Skiller düzeltmeyi zaten yazıyla istiyor.

### Skiller tek bir akışta toplansın

Altı skill var — senaryo, karakter promptu, kareye bölme, prompt üretimi (iki ayrı sürüm) ve
kontrol — ve hangisinin ne zaman geleceğini kullanıcı seçiyor. Bir kısmı gerçekten gereksiz;
kalanlar da birbirini izleyen tek bir zincir. İstenen, gereksizlerin atılıp geri kalanın tek bir
skill akışına inmesi.

### Prompt listesi karışıyor — hangisi güncel belli değil

Prompt listesi iki ayrı skill'den doğabiliyor ve her biri ayrı bir dosya adı bırakıyor; düz olan
yol üstüne yazmadığı için aynı listenin numaralı kopyaları da birikiyor. Ne kullanıcı ne de model
dosya adına bakarak hangisinin şu anki liste olduğunu söyleyebiliyor.

### İki karakter aynı karede patlıyor (1girl / 2girls)

Karakterin değişmeyen kısmı `1girl` etiketiyle birlikte yazıldığı için iki karakterli bir karede
prompt bu etiketi iki kez taşıyor; görüntü modelinin beklediği ise `2girls`. Kontrol skill'inin
kural listesi bu durumu görmüyor, yani hata sessizce geçiyor.

### Agentic davranışı arttıran bir sistem promptu

Bugünkü sistem promptu dört kısa paragraf: kim olduğu, proje dosyalarını görebildiği, ne zaman
dosya yazacağı. Ne zaman plan yapacağı, yazmadan önce okuyacağı, kendi çıktısını kontrol edeceği
hiçbir yerde yazmıyor — hepsi tek tek skill metinlerine bırakılmış.

### Çalışan cevap durdurulamıyor, arka plandaki skill görünmüyor

Cevap başladıktan sonra kesmenin yolu yok: durdurma düğmesi yok, sohbetten çıkmak sunucudaki turu
bitirmiyor ve geri dönüldüğünde cevap baştan isteniyor. O bekleme boyunca model dosya okuyor ya da
prompt kuruyor olabilir; ekranda yalnızca üç nokta var.

### Tool call'lar sohbette görünsün

Model bir turda dosya listeleyip okuyup düzenleyebiliyor ama bu adımların hiçbiri sohbete
yazılmıyor; yalnızca yeni bir dosya doğduğunda bir kart çıkıyor. Sohbet kaydına hiç düşmediği için
kullanıcı ne yapıldığını sonradan da göremiyor.

### Uygulama açılınca taslak sohbet ekranı gelsin

Uygulama bugün ilk projenin ekranına düşüyor ve oradaki yazma kutusunda skill ile model seçici yok;
seçicilerin durduğu boş sohbet ekranına yalnız sidebar'daki "+ New chat" ile giriliyor. Karar
verildi: açılış doğrudan taslak sohbet ekranına düşecek, proje ekranı ayrı bir kapı olarak kalacak.
Yeni bir ekran yazılmıyor — o ekran zaten var, değişen yalnız açılış adresi.

### Promptlar SDXL promptu gibi değil, cümle şeklinde çıksın

Bugün hem karakter dosyaları hem kare promptları virgülle ayrılmış kısa etiketler; skill metni bunu
açıkça "asla cümle değil" diye söylüyor, kod da parçaları virgülle birleştiriyor. İstenen, promptun
etiket dizisi olarak değil düz cümle olarak çıkması.

### Cached token olayını çöz, sistemi optimize et

Servisin döndürdüğü tüketim bilgisi hiçbir yerde okunmuyor; önbellekten gelen token ile yeniden
ödenen token birbirinden ayrılamıyor. İstenen önce tüketimin görünür olması — kaç token'ın nereden
geldiği okunabilsin; neyi optimize edeceğimiz ondan sonra belli olur.
