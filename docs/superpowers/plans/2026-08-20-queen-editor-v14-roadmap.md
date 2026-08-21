# Queen Editor — Yol Haritası v14

**Tarih:** 2026-08-20 · **Koşu dalı:** `feat/queen-editor-v4` · **Durum:** 6/31
**Öncesi:** [v13](2026-08-14-queen-editor-v13-roadmap.md)

## Neden bu koşu var

İki liste birleşti.

**[İstek listesi](2026-08-20-queen-editor-istekler.md)** — kullanıcının 20 Ağustos'ta saydığı 10 iş.
Ne istendiğini söylüyor.

**[Tasarım v4 fark listesi](../research/2026-08-20-queen-editor-tasarim-v4-farklari.md)** — tasarımın
20 Ağustos turu ile bugünkü uygulama arasındaki 136 fark. Üç bağımsız yolun çakıştırmasından çıktı.

İkisi farklı sorulara cevap veriyordu ve yalnız beş yerde örtüşüyorlardı. İsteklerin dördü (galeri
hızı, video modelinin gücü, varyant varsayılanı, üretme hızı) fark listesinde hiç yok — tasarım
bunlardan söz etmiyor. Fark listesinin yaklaşık seksen beş maddesi de isteklerde yok — toplu katman
silme, panel hata dili, rozet düzeni, detay panelinin ritmi bunların başında geliyor.

Fark listesinin **31 maddesi karara bağlanıp kapandı**; kararlar o belgenin 5. bölümünde. Bu koşu
kalanları taşıyor.

**Bir boşluk vardı, kapatıldı.** İstek listesi loop ve sonrakine bağlama için *"bugün son kare
verilemiyor, asıl iş bu"* diyordu; fark listesinde bunun karşılığı yoktu, çünkü üç yol da arayüz
karşılaştırması yaptı. Roadmap'in ilk iki maddesi o eksik temeldir — onlar olmadan üretim modu
arayüzü arkasında hiçbir şey olmayan bir kabuk olurdu.

## Nasıl çalışacağız

**Her görev iki döngü.** Önce yalnız testler: spec → plan → testleri yaz → commit. O commit takımı
kırmızı bırakır. Sonra implementasyon: spec → plan → kodu yaz → commit; takım yeşile döner.

Sebebi: test kodla aynı nefeste yazılınca kodun zihin modelini miras alıyor ve aynı körlüğü
taşıyor.

**Ön yüz değişen her görevde derlenmiş çıktı implementasyon commit'ine girer.** Kullanıcı en sonda
toplu Colab testi yapar; koşu boyunca durulmaz.

**Sıra bağımlılığa göre.** Bir madde neyin üstünde duruyorsa o önce gelir. Bağımlılığı olmayan
maddelerde sıra, o ekranın bir kez açılıp bir kez kapanmasına göre kuruldu.

**Görsel hizalamalar ekran bazında gruplu.** Bir davranış değişikliği kendi maddesi ve kendi testi;
on iki tane ölçü düzeltmesi tek maddede toplanıp birlikte doğrulanıyor, çünkü zaten aynı ekrana
dokunuyorlar.

**Biten madde satırında işaretlenir.** İki tur da bitip takım yeşile döndüğünde maddenin **İş**
hücresi ✅ ile başlar ve başlıktaki sayaç ilerler. Asıl kayıt commit'lerdir — her madde iki commit,
biri kırmızı testler biri kod — ama otuz bir satırlık bir listede "7/31" hangi yedisi olduğunu
söylemiyor, işaret onun için var. Yarım kalan madde işaretlenmez: bir maddeyi kısmen bitmiş
göstermenin yolu yok, çünkü "bitti sayılır" sütunu bölünmüyor.

**A'dan G'ye kadar tek başına yürür; H kullanıcıyla birlikte.** Son bölümün hiçbir maddesi ekranda
görünmüyor ve hiçbirinin "bitti" yargısı koda bakarak verilemiyor. O bölüme sıra gelince
kullanıcıyla birlikte oturulur.

## Kapsam sınırı

- **LoRA'nın uygulamadan seçilebilmesi düştü.** İstek listesinin 2.1 maddesi; kullanıcı kararıyla
  bu koşuda da yakın koşularda da yok.
- **Export ekranı bu koşuda hiç açılmıyor.** Kullanıcı ekranı düzgün buldu; fark listesinin export
  maddelerinin tamamı — görsel olanı da olmayanı da — kullanıcı kararıyla düştü.
- **Kararla kapanan 31 fark maddesi dışarıda.** Bugünkü hâlleriyle kalıyorlar.
- **Tasarım tarafında iki satır güncellenmeli.** Açılışta kuyruğun kendiliğinden sürmesi ve yeniden
  üretimin tur numarası, kullanıcı kararıyla bugünkü hâlinde kaldı; tasarımın kural metni hâlâ
  tersini söylüyor. Güncellenmezse bir sonraki karşılaştırmada aynı çelişkiler yeniden çıkar.

---

## A · Motor tarafı — ekranda görünmeyen işler

| # | İş | Bitti sayılır | Kaynak |
|---|---|---|---|
| 1 | ✅ **Motorun bitiş karesi alabilmesi.** Üretim, bugün yalnız ilk kareyi alıyor; yanına son kareyi de alacak. | Bir kareye kendi fotoğrafı bitiş karesi verilerek üretim yapılıyor ve dönen video başladığı yere dönüyor. | İstek 3 |
| 2 | ✅ **Kuyruk işinin üretim modunu taşıması.** Kuyruğa giren video işi standart, loop ya da bağlı olduğunu kaydedecek; motor onu okuyup bitiş karesini buna göre seçecek. | Üç modda da kuyruğa iş eklenip beklendiğinde çıkan videolar birbirinden farklı; bağlı modda bitiş karesi sonraki karenin fotoğrafı. | İstek 3 · Fark 22 |
| 3 | ✅ **Video ve sesin tohumunun kayda geçmesi.** Eksik tohum kayda geçmiyordu, dolayısıyla bir satır yeniden üretilemiyordu. Tohumu motor seçiyor ve aynı sayıyı hem üreticiye hem satıra veriyor. | Tohum verilmeden yapılan üretimde satıra bir sayı yazılıyor ve üreticiye giden sayı o. | Bekleyen işler |

1 ve 2 olmadan B bölümünün tamamı çalışmayan bir kabuk. 3 tek başına durur, sırası buraya
bağımlılıktan değil aynı tarafta olmasından geldi.

## B · Üretim modu arayüzü

| # | İş | Bitti sayılır | Kaynak |
|---|---|---|---|
| 4 | ✅ **Video panelinde Üretim modu seçicisi.** Kapsam ile Varyant arasına gelir; varsayılanı Standart, diğerleri Loop ve Sonrakine bağla. Ses panelinde doğmaz. | Panelden mod seçilip kuyruğa eklenince iş o modla kaydediliyor; ses panelinde satır hiç görünmüyor. | İstek 3 · Fark 22, 23, 34 |
| 5 | ✅ **Sonrakine bağla ardışık seçim istiyor.** Galeride ardışık olmayan kareler seçiliyken seçenek pasifleşir ve altında sebebi tek satır yazar. | Dağınık seçimle seçenek tıklanamıyor ve sebep görünüyor; ardışık seçimde açılıyor. | İstek 3 · Fark 24 |
| 6 | ✅ **Tahmin ve onay metinleri moda göre değişiyor.** Butonun altındaki tahmin ve eklendikten sonraki yeşil onay, seçilen modu söyler. | Üç modda üç ayrı cümle çıkıyor; hiçbirinde eski tek kalıp kalmamış. | İstek 3 · Fark 25, 26 |
| 7 | **Galeride loop rozeti.** Loop modunda üretilmiş videosu olan kare, "video" yerine "loop" yazan rozeti gösterir; ikisi aynı yeri paylaşır. | Loop videolu karede "loop", standart videolu karede "video" okunuyor; ikisi bir arada hiç görünmüyor. | İstek 3 · Fark 63 |
| 8 | **Detayda Üretim modu bilgi satırı.** Video sekmesinde, bu videonun hangi modda üretildiğini salt bilgi olarak yazar; bağlı modda hedefi adıyla söyler. Ses sekmesinde doğmaz. | Üç modda üretilmiş üç karenin video sekmesinde üç ayrı değer okunuyor, satır tıklanmıyor, ses sekmesinde yok. | İstek 3 · Fark 93 |
| 9 | **Detayda Yeni mod seçicisi.** Yeniden üret formuna gelir, varsayılanı bu videonun modudur. Dizinin son karesinde "Sonrakine bağla" seçilirse kutu uyarıya döner ve yeniden üret pasifleşir. Butonun altında ne doğacağını söyleyen tek satır durur. | Mod değiştirilmeden basınca mod korunuyor; son karede bağla seçilince üretim kapanıyor ve sebep görünüyor. | İstek 3 · Fark 94, 95, 96 |

İzleme davranışı bu koşuda değişmiyor: video hangi modda üretilmiş olursa olsun bugünkü gibi döner.
Kullanıcı kararı; fark listesinin 97. maddesi bu yüzden kapandı.

## C · Galeri ve seçim barı

| # | İş | Bitti sayılır | Kaynak |
|---|---|---|---|
| 10 | **Toplu kart taşıma.** Seçili bir kart sürüklenince seçimin tamamı bitişik blok olarak taşınır, sıra korunur; seçili olmayan sürüklenirse yalnız o gider. Dağınık seçim bırakıldığı yerde yan yana gelir. Yeni bir öğe eklenmez. | Üç dağınık kare seçilip taşınınca yan yana iniyor, aralarındaki sıra korunuyor, aradaki kartlar boşluğu kapatıyor. | İstek 5 · Fark 70, 71, 72 |
| 11 | **Kart kopyalama.** Seçim barına Kopyala gelir, kısayolu Ctrl + D. Kopya birebir doğar, adı kopya önekiyle başlar, kaynağın bir üstüne iner, seçim kopyaya geçer. Yalnız bekleyen kareler seçiliyse buton doğmaz. | Bir kare kopyalanınca üstünde ikizi beliriyor, seçim ona geçiyor, ikizden birini silmek öbürünü bozmuyor. | İstek 7 · Fark 77, 78, 79 |
| 12 | **Toplu katman silme.** Seçim barına Videoları sil ve Sesleri sil gelir. Kareler yerinde kalır, yalnız katman düşer; katmanı olmayan seçili kareler atlanır ve onay metni bunu söyler. | On iki kare seçilip videoları silinince kareler ve fotoğrafları duruyor, videosu olmayanlar atlanmış ve sayı onayda doğru yazmış. | Fark 80, 81 |
| 13 | **Seçim barının görünümü.** Öğeler arası boşluk daralır ve bar sarmaz; seçimde bekleyen kare varsa katman silme düğmeleri hiç çizilmez. | Beş düğme tek satırda kalıyor, yalnız bekleyen seçiminde bar üç öğeye iniyor. | Fark 82, 83, 84 |
| 14 | **Detaydan dönünce galerinin yerinde durması.** Bir kare açılıp geri gelince galeri sıfırdan yüklenmeyecek, sayfa bırakıldığı yerde duracak. | Kare açılıp kapanınca galeri baştan kurulmuyor; kayma yeri ve o ana kadar yüklenmiş kareler duruyor. | İstek 1.2 / 6 |
| 15 | **Galeri kartının görsel hizalaması** *(grup)*. Sahiplik rozetleri sol alta taşınır, ikonlarını bırakır, her katman kendi kutusunu alır; ikinci bekleyen katmanın hapı birincinin altına dizilir; hover'da numara kalkar; sürükleme basılı tutmayla başlar; bekleyen hapının tonu ve hatalı karenin perdesi düzeltilir. | Listedeki on farkın hepsi ekranda kapanmış. | Fark 60–62, 64, 65, 69, 73, 74, 75, 76 |

## D · Üretim panelleri

| # | İş | Bitti sayılır | Kaynak |
|---|---|---|---|
| 16 | **Panel hata dili.** Buton hiçbir eksik alan için pasifleşmez — basmadan önce panel sakin durur, basınca altında hata kartı doğar ve sebep tek satır yazar. Sebep dört ayrı duruma göre değişir. Varyant boşken kutu uyarıya döner. Buton yalnız süren işlemde pasif kalır. | Dört sebebin dördü ayrı ayrı çıkarılıyor; hiçbirinde buton önceden kilitli değil; varyant kutusuna yazmaya başlayınca uyarı temizleniyor. | İstek 4.3 · Fark 27, 28, 29, 35 |
| 17 | **Panelin görsel hizalaması** *(grup)*. Kapsam satırına seçim dairesi gelir, model satırı açılır kutuya döner, kapsam satırının adı tam yazılır, Süre bloğu kalkar. | Dört farkın dördü de kapanmış; panelde Model, Kapsam, Üretim modu, Varyant ve buton dışında blok kalmamış. | Fark 30–33 |
| 18 | **Fotoğraf varyant varsayılanı 4 → 2.** Bir prompt'tan kaç kare üretileceğinin varsayılanı iki olur. Katman panelindeki varyant değişmez. | Panel açıldığında kutuda 2 yazıyor. | İstek 8 |

## E · Detay sayfası

| # | İş | Bitti sayılır | Kaynak |
|---|---|---|---|
| 19 | **Her sekme yalnız kendi katmanını gösterir.** Alt katmanların dosya adları ve prompt kutuları gider; karenin kendi adı ve sırası üstte kalır. Kuyrukta bekleyen katmanın kutusunda ortalanmış tek satır durur. | Video sekmesinde yalnız video prompt'u, ses sekmesinde yalnız ses prompt'u görünüyor; kare adı üç sekmede de duruyor. | İstek 4.1 · Fark 86, 87, 92 |
| 20 | **Sekmelerin ayrılması.** Foto, Video ve Ses sekmeleri arasına boşluk girer, her biri kendi köşe yarıçapını alır; açık sekme yalnız rengiyle belli olur. | Üç sekme ayrı ayrı okunuyor, açık olan renginden ayırt ediliyor, olmayan katmanın sekmesi pasif duruyor. | İstek 4.2 · Fark 85 |
| 21 | **Sağ panelin düzeni.** Panel iki gruba ayrılır — üstte kare bilgisi, altta üretim — grup başlığı ve ayraç olmadan. Prompt kutuları sabit yüksekliğe geçip büyür, taşan metin kendi içinde kayar. Her prompt başlığının sağına kopyala ikonu gelir. Etiketler hangi katmanı okuduğunu söyler. | Pencere boyu değişince kutular esnemiyor; kopyala ikonu metni panoya alıyor; etiketler katman adını taşıyor. | Fark 88–91 |
| 22 | **Detayın görsel hizalaması** *(grup)*. Oynatıcı çubuğu ve dalga videonun içine iner, oynat düğmesi çerçeve alır, sahnenin üst boşluğu açılır, hap ve düğme metinleri düzeltilir, negatif prompt düzenlenebilir olur. | Listedeki farkların hepsi ekranda kapanmış. | Fark 98–117 |

## F · Proje ekranı

| # | İş | Bitti sayılır | Kaynak |
|---|---|---|---|
| 23 | **Proje adı değiştirme.** Proje kartına kalem düğmesi gelir; pencere yeni proje penceresinin aynısıdır, alan mevcut adla dolu ve seçili gelir. Ad başka bir projede kullanılıyorsa uyarı aynı yerde çıkar. Yalnız ad değişir; klasör içeriği, kare adları ve kuyruk etkilenmez, üretim akarken de yapılabilir. Yıkıcı bir eylem değildir. | Üretim akarken bir projenin adı değiştiriliyor, kuyruk kesintisiz sürüyor, kare adları olduğu gibi kalıyor. | İstek 10 · Fark 1–4 |
| 24 | **Proje ekranının hizalaması** *(grup)*. Karttaki silme düğmesi yıkıcı eylem standardına geçer, yeni proje penceresi yeniden adlandırma penceresiyle aynı ölçüye iner, liste uzayınca kayma göstergesi belirir, silme onayının cümle sırası değişir. | Dört farkın dördü de kapanmış. | Fark 5, 6, 8, 9 |

## G · Kuyruk

| # | İş | Bitti sayılır | Kaynak |
|---|---|---|---|
| 25 | **Kısmi üretici eksikliğinde uyarının kendi kartına geçmesi.** Yalnız bir türün üreticisi eksikken panelin geneli etkilenmez; uyarı ve kurulum düğmesi o türün kendi kartının içinde durur, diğer türler normal akar. | Ses üreticisi eksikken foto ve video kartları akıyor, uyarı yalnız ses kartında duruyor. | Fark 38 |
| 26 | **Kurulum bitince kuyruğun kendiliğinden sürmesi.** Üretici eksikliği yüzünden bekleyen kuyruk, üretici geldiğinde kullanıcıdan bir hamle beklemeden akar; bekleme kartı bunu önceden söyler. | Eksik üretici kurulunca kuyruk kendiliğinden akmaya başlıyor. | Fark 37 |
| 27 | **Kuyruk panelinin görsel hizalaması** *(grup)*. Tür kartının başlık dili ve büyük sayısının rengi, duraklatılıyor hâlindeki nokta, tamamlandı kartının tonu, hata kartının düğme metni ve ne zaman doğduğu, bekleme hâlinde boşaltma düğmesinin görünmesi, durdu kartının tek satıra inmesi, kurulum düğmesinin her yerde aynı yazması. | Listedeki farkların hepsi ekranda kapanmış. | Fark 41–48, 50, 59 |

---

## H · Kullanıcıyla birlikte yapılacak işler — koşunun en sonu

**Bu bölüm tek başına yapılmaz.** Maddelerin hiçbiri ekranda görünmüyor: dosyaların boyu, üretim
tarifi, süreler. Hiçbirinin "bitti" yargısı da koda bakarak verilemiyor — queen-editor yerelde
koşmuyor, defteri kullanıcı çalıştırıyor ve sonucu kullanıcı görüyor. Dolayısıyla bu dört madde
kullanıcıyla **birlikte** yürütülür: koşulur, bakılır, karar verilir.

Kullanıcı bunların bir arada ve en sonda yapılmasını istedi.

| # | İş | Bitti sayılır | Kaynak |
|---|---|---|---|
| 28 | **Colab turu.** Dal yayınlanır ve defter koşulur; galeri açıkken çıkan zaman aşımının kalkıp kalkmadığı görülür. Sonuç 29. maddenin sırasını belirler. | Galeri açıkken üretim sürerken zaman aşımı çıkmıyor — ya da çıkıyor ve bu yazıya geçmiş. | İstek 1.1 |
| 29 | **Küçük önizleme üretimi.** Galeri karoları bugün dosyanın tam boyunu indiriyor. Karolar için küçük birer önizleme üretilecek, galeri onları gösterecek. Önizlemenin ne zaman üretileceği ve kare değişince ne olacağı kendi spec'inde çözülür. | Galeri açılırken inen veri belirgin biçimde azalmış ve karolar gözle görülür hızda doluyor. | İstek 1.1 |
| 30 | **Video prompt talimatının güçlenmesi.** Kullanıcı yazmazsa video prompt'unu yapay zekâ yazıyor; ona verilen talimat güçlenecek. Yazan modeli değiştirmek bu maddede yok. | Aynı fotoğraflardan üretilen video prompt'ları öncekilerle yan yana konup kullanıcıyla birlikte değerlendirilmiş. | İstek 2.2 |
| 31 | **Üretme hızı.** Motor her kare için süreyi zaten yazıyor ve üretimin payı ile yazmanın payı ayrı duruyor. İş, önce o satırları toplamak, sonra hangisinin büyük olduğuna göre karar vermek. Yol olarak hız ayarları denenecek. | Hangi payın büyük olduğu ölçülmüş ve bir sonraki adım kullanıcıyla birlikte karara bağlanmış. | İstek 9 |

> 30. ve 31. maddeler birbirini ters yöne çekiyor: biri videoyu güçlendirmek, öteki üretimi
> hızlandırmak istiyor. Aynı ayarlara dokunuyorlar, birlikte bakılmalı — bu da bölümün neden bir
> arada durduğunun bir sebebi.

---

## Sonraki koşuya kalanlar

- **Bu koşuyu kapatacak Colab turundan çıkacak yeni maddeler.**

Başka bir şey bekletilmiyor. Kapsam dışı kalan her şey kullanıcı kararıyla düştü; sıra beklemiyor.
