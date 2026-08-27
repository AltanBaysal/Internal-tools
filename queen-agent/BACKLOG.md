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

### Kalabalık karede karakterleri BREAK ile ayırmak

Bir karede iki karakter olunca tanımları birbirine bulaşıyor — birinin saçı ötekinin üstüne
geçiyor. Sebebi SDXL'in metin kodlayıcısı: promptu 75 jetonluk parçalar hâlinde okuyor, ve karışma
o parçanın **içinde** oluyor. `BREAK` bunun bilinen ilacı; yazıldığı yerde parçayı kapatıp yenisini
açıyor, iki karakter ayrı ayrı kodlanıyor.

**Bugün seçilen ilaç sıra:** ana karakter promptun başında, geri kalan `camera`'dan sonra — arayı
açmak. Kullanıcı bunu elle deneyip işe yaradığını gördü *(27 Ağustos)*, o yüzden önce o yapılıyor.
Bilinen tek şüphe duruyor ve kayda geçiyor: erken jetonlar daha fazla ağırlık taşıyor, yani ikinci
karakteri sona atmak onu ayırmakla kalmayıp zayıflatabilir. `BREAK`'te bu bedel yok — parçalar
bağımsız kodlandığı için ikisi de kendi parçasının başında duruyor.

**Bu tarafta tek başına yapılamaz.** `BREAK` bir model özelliği değil, promptu okuyan arayüzün
özelliği, ve promptlar buradan kullanıcının ComfyUI tabanlı arayüzüne — queen-editor'e — düz metin
olarak gidiyor. Orası bugün desteklemiyor: pozitif yolda tek bir `CLIPTextEncode` var ve `BREAK`
kelime olarak kodlanıyor. Açılacak düğüm ve bedeli
[queen-editor backlog'unda](../queen-editor/BACKLOG.md).

**Sırası:** queen-editor o düğümü açtıktan sonra. O gün `build_prompts` karakter bloklarının arasına
`BREAK` koyar, ve sıra düzeltmesinin hâlâ bir işi olup olmadığı yeniden sorulur — ikisi aynı derde
iki ayrı ilaç, ve biri ötekini gereksiz kılabilir.

Araştırmanın tamamı ve kaynakları:
[skill problemleri belgesi](../docs/2026-08-27-queenagent-skill-problemleri.md).

### Cached token olayını çöz, sistemi optimize et

Servisin döndürdüğü tüketim bilgisi hiçbir yerde okunmuyor; önbellekten gelen token ile yeniden
ödenen token birbirinden ayrılamıyor. İstenen önce tüketimin görünür olması — kaç token'ın nereden
geldiği okunabilsin; neyi optimize edeceğimiz ondan sonra belli olur.
