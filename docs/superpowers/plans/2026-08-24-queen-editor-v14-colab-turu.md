# Queen Editor v14 — Colab turu kontrol listesi

**Tarih:** 2026-08-24 · **Koşu:** [v14 yol haritası](2026-08-20-queen-editor-v14-roadmap.md), madde 30 ·
**Dal:** `feat/queen-editor-v4`

Yol haritası maddeleri **bağımlılığa** göre sıralar — neyin neyin üstünde durduğuna. Bu liste aynı
maddeleri **ekran sırasına** göre dizer: bir tur boyunca ekranlar hangi sırayla açılıyorsa o sırayla.
Maddelerin neden var olduğu ve "bitti" yargısının tam metni yol haritasındadır; burada yalnız turda
göze bakılacak olan var. Parantez içindeki sayılar yol haritasının madde numaraları.

## Turdan önce

Dal `origin`'e itilmiş, derlenmiş ön yüz en son kaynak commit'iyle aynı commit'te. Defterin klon
hücresi bu dala bakıyor — `queen-editor/app.ipynb` yüklenip koşulur, başka ayar yok.

## 1 · Açılışta — bu koşunun en büyük iki işi

- [x] **Galeri kilitlenmiyor** (27). Tünel TCP'ye alındı. Çok kareli bir projede karolar gözle
      görülür hızda dolmalı, "sunucuya ulaşılamadı" hiç çıkmamalı.
- [x] **İndirme sırası** (28). Kareler kaydırma yönünden bağımsız, baştan sona sırayla dolmalı;
      görünmeyen istenmemeli; aynı anda en fazla 2 fotoğraf inmeli.

## 2 · Proje ekranı

- [x] **Ad değiştirme** (23). Kartta kalem düğmesi; pencere yeni proje penceresinin aynısı, alan
      mevcut adla dolu ve seçili. Ad başka projede kullanılıyorsa uyarı aynı yerde.
- [ ] **Üretim akarken ad değiştirme** (23). Kuyruk kesilmemeli, kare adları ve klasör içeriği aynı
      kalmalı.
- [ ] **Ekranın hizalaması** (24). Silme düğmesi yıkıcı eylem standardında, yeni proje penceresi
      yeniden adlandırmayla aynı ölçüde, liste uzayınca kayma göstergesi, silme onayının cümle
      sırası.

## 3 · Galeri ve seçim barı

- [ ] **Toplu taşıma** (10). Üç dağınık kare seçilip sürüklenince bitişik blok olarak insin, sıra
      korunsun, aradaki kartlar boşluğu kapatsın. Seçili olmayan sürüklenirse yalnız o gitsin.
- [ ] **Kopyalama** (11). Ctrl + D — kopya kaynağın bir üstüne iner, adı kopya önekiyle başlar,
      seçim kopyaya geçer. İkizden birini silmek öbürünü bozmamalı. Yalnız bekleyen kare seçiliyken
      buton doğmamalı.
- [ ] **Toplu katman silme** (12). Kareler ve fotoğrafları yerinde kalsın, katmanı olmayan seçili
      kareler atlansın, onay metni sayıyı doğru yazsın.
- [ ] **Seçim barı** (13). Beş düğme tek satırda, sarmıyor. Seçimde bekleyen kare varsa katman silme
      düğmeleri hiç çizilmiyor.
- [ ] **Detaydan dönünce galeri yerinde** (14). Galeri baştan kurulmamalı; kayma yeri ve o ana kadar
      yüklenmiş kareler durmalı. *(24 Ağustos: tur burada durdu — kartların yerinde bir yükleniyor
      çıktı ve 14'ün kendisi görülemedi. Sebep 14'ün kapsamadığı bir cevaptı; yol haritasının K
      bölümü buradan doğdu. Aşağıdaki dört satır onun.)*
- [ ] **Ekran beklemeden açılıyor** (31). Bir projeye ilk girişte de bir kareden dönüşte de galeri
      hemen görünmeli; yükleniyor işareti yalnız fotoğraf üret panelinin kendi sütununda çıkmalı,
      tüm ekranı kaplamamalı.
- [ ] **Dönüş sessiz** (32). Bir kare açılıp kapandığında ekranın hiçbir yerinde yükleniyor
      çıkmamalı — model kutusu ve üretici satırları olduğu gibi durmalı.
- [ ] **Kuyruk paneli yanlış konuşmuyor** (33). Üretim akarken bir kare açılıp dönülünce panel bir an
      bile "kuyruk boş" dememeli.
- [ ] **Açık panel yerinde** (34). Kuyruk paneli açıkken bir kare açılıp dönülünce panel yerinde
      kalmalı; kapalı bırakılmışsa kapalı dönmeli. *(Galeri seçimi bu satırdan çıktı — kullanıcı
      kararı: seçim varken karta tıklamak kareyi açmıyor, yani seçimin kaybolduğu bir yol yok.)*
- [ ] **Yazılan metin yerinde** (35). Fotoğraf üret panelinin bir kutusuna bir şey yazılıp
      gönderilmeden bir kare açılıp dönülünce yazılan durmalı — kutuda en son gönderilen metin
      olmamalı. Sayfa yenilenirse kutular kayıttan dolar, o beklenen.
- [ ] **Kart görünümü** (15). Sahiplik rozetleri sol altta ve ikonsuz, her katman kendi kutusunda;
      ikinci bekleyen hap birincinin altında; hover'da numara yok; sürükleme basılı tutmayla
      başlıyor; bekleyen hapının tonu ve hatalı karenin perdesi düzelmiş.
- [ ] **Loop rozeti** (7). Loop modunda üretilmiş karede "loop", standart videoluda "video"; ikisi
      bir arada hiç görünmüyor.

## 4 · Üretim panelleri

- [ ] **Hata dili** (16). Buton eksik alan yüzünden önceden pasifleşmemeli; basınca altında hata
      kartı doğmalı, sebep dört duruma göre değişmeli. Buton yalnız süren işlemde pasif.
- [ ] **Varyant uyarısı** (16). Varyant boşken kutu uyarıya döner, yazmaya başlayınca temizlenir.
- [ ] **Panel düzeni** (17). Model açılır kutu, kapsam satırında seçim dairesi ve tam ad, Süre bloğu
      kalkmış — Model, Kapsam, Üretim modu, Varyant ve butondan başka blok kalmamalı.
- [ ] **Varyant varsayılanı** (18). Foto panelinde kutuda 2 yazmalı; katman panelindeki varyant
      değişmedi.

## 5 · Üretim modu — koşunun yeni yeteneği

- [ ] **Mod seçicisi** (4). Kapsam ile Varyant arasında, varsayılan Standart; Loop ve Sonrakine
      bağla. Ses panelinde hiç görünmemeli.
- [ ] **Ardışıklık şartı** (5). Dağınık seçimde "Sonrakine bağla" pasif ve altında tek satır sebep;
      ardışık seçimde açılıyor.
- [ ] **Tahmin ve onay** (6). Üç modda üç ayrı cümle; eski tek kalıp hiçbirinde kalmamış.
- [ ] **Motor — üç mod** (1, 2). Üç modda kuyruğa iş eklenip beklendiğinde çıkan videolar birbirinden
      farklı; loop videosu başladığı yere dönüyor; bağlı modda bitiş karesi sonraki karenin
      fotoğrafı.
- [ ] **Tohum** (3). Tohum verilmeden yapılan üretimde satırda bir sayı yazılı.

## 6 · Detay sayfası

- [ ] **Sekme yalıtımı** (19). Video sekmesinde yalnız video prompt'u, ses sekmesinde yalnız ses
      prompt'u; kare adı ve sırası üç sekmede de üstte. Kuyrukta bekleyen katmanın kutusunda
      ortalanmış tek satır.
- [ ] **Sekmelerin ayrılması** (20). Aralarında boşluk, kendi köşe yarıçapları, açık sekme yalnız
      renginden belli, olmayan katmanın sekmesi pasif.
- [ ] **Sağ panel** (21). İki grup — üstte kare bilgisi, altta üretim — başlık ve ayraç yok. Prompt
      kutuları sabit yükseklikte: pencere boyu değişince esnememeli, taşan metin kendi içinde
      kaymalı. Kopyala ikonu metni panoya alıyor.
- [ ] **Üretim modu bilgi satırı** (8). Video sekmesinde salt bilgi, tıklanmıyor, bağlı modda hedefi
      adıyla söylüyor; ses sekmesinde yok.
- [ ] **Yeni mod seçicisi** (9). Yeniden üret formunda, varsayılanı bu videonun modu. Dizinin son
      karesinde "Sonrakine bağla" seçilince kutu uyarıya döner ve yeniden üret pasifleşir.
- [ ] **Detayın görseli** (22). Oynatıcı çubuğu ve dalga videonun içinde, oynat düğmesi çerçeveli,
      sahnenin üst boşluğu açık, negatif prompt düzenlenebilir.

## 7 · Kuyruk

- [ ] **Kısmi üretici eksikliği** (25). Yalnız ses üreticisi eksikken foto ve video kartları akmalı;
      uyarı ve kurulum düğmesi yalnız ses kartının içinde durmalı.
- [ ] **Kuyruk görünümü** (26). Tür kartının başlık dili ve büyük sayısının rengi, duraklatılıyor
      hâlindeki nokta, tamamlandı kartının tonu, hata kartının düğme metni ve ne zaman doğduğu,
      bekleme hâlinde boşaltma düğmesi.

## Hata sanılmayacaklar — kararla böyleler

- **Fotoğraflar iki koşu arasında yeniden iniyor** (29). Cloudflare her koşuda yeni adres veriyor,
  tarayıcı önbelleği adresi anahtar sayıyor. Çözüm sabit adres; bu koşunun işi değil, kaydı
  [backlog](../backlog.md)'da. Koşu *içinde* önbellek çalışıyor: galeri kaydırması ve detaydan dönüş
  ağa çıkmıyor.
- **Export ekranı** bu koşuda hiç açılmadı — kullanıcı düzgün bulduğu için tüm export farkları
  düştü.
- **LoRA'nın uygulamadan seçilmesi** yok; kullanıcı kararıyla düştü.
- **İzleme davranışı** değişmedi: video hangi modda üretilirse üretilsin bugünkü gibi dönüyor.

## Turdan sonra

Çıkan her şey yazıya geçip [backlog](../backlog.md)'a eklenir — 30. maddenin "bitti sayılır" şartı
budur.
