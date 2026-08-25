# Queen Editor — Yol Haritası v14

**Tarih:** 2026-08-20 · **Koşu dalı:** `feat/queen-editor-v4` · **Durum:** 36/37
*(Numaralar ve bölüm harfleri okuma sırasına göre gidiyor. 27 düşüp 21 Ağustos'ta yeniden açıldı —
H bölümü; 28 ve 29, 27'nin teşhisinden doğup 24 Ağustos'ta eklendi — I bölümü; 29 aynı gün
kullanıcı kararıyla düştü, o yüzden 30'a kadarki payda 30 değil 29. 31–34 turun kendi içinden
doğup aynı gün eklendi — K bölümü; 35, 36, 37 ve 38 ertesi gün kullanıcının isteğiyle eklendi.)*
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

**J dışındaki her bölüm tek başına yürür.** J'nin maddesi ekranda görünmüyor ve "bitti" yargısı
koda bakarak verilemiyor; o bölüme sıra gelince kullanıcıyla birlikte oturulur.

## Kapsam sınırı

- **LoRA'nın uygulamadan seçilebilmesi düştü.** İstek listesinin 2.1 maddesinin **ikinci** yarısı;
  kullanıcı kararıyla bu koşuda da yakın koşularda da yok.
- **Export ekranı bu koşuda hiç açılmıyor.** Kullanıcı ekranı düzgün buldu; fark listesinin export
  maddelerinin tamamı — görsel olanı da olmayanı da — kullanıcı kararıyla düştü.
- **Kararla kapanan 31 fark maddesi dışarıda.** Bugünkü hâlleriyle kalıyorlar.
- **27 düştü ve aynı gün yeniden açıldı** — H bölümüne bakın. Önce "küçük önizleme üretimi" diye
  yazılmıştı; asıl derdi *uygulamanın çok fotoğrafta kilitlenmesi* olduğu için o adla geri döndü.
- **29 düştü — I bölümüne bakın.** Önbelleğin koşular arası yarısı yalnız sabit bir adresle açılıyor;
  o da defterin tünel satırı ve kullanıcının alan adı, yani bu koşunun elindeki bir iş değil.
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
| 7 | ✅ **Galeride loop rozeti.** Loop modunda üretilmiş videosu olan kare, "video" yerine "loop" yazan rozeti gösterir; ikisi aynı yeri paylaşır. | Loop videolu karede "loop", standart videolu karede "video" okunuyor; ikisi bir arada hiç görünmüyor. | İstek 3 · Fark 63 |
| 8 | ✅ **Detayda Üretim modu bilgi satırı.** Video sekmesinde, bu videonun hangi modda üretildiğini salt bilgi olarak yazar; bağlı modda hedefi adıyla söyler. Ses sekmesinde doğmaz. | Üç modda üretilmiş üç karenin video sekmesinde üç ayrı değer okunuyor, satır tıklanmıyor, ses sekmesinde yok. | İstek 3 · Fark 93 |
| 9 | ✅ **Detayda Yeni mod seçicisi.** Yeniden üret formuna gelir, varsayılanı bu videonun modudur. Dizinin son karesinde "Sonrakine bağla" seçilirse kutu uyarıya döner ve yeniden üret pasifleşir. Butonun altında ne doğacağını söyleyen tek satır durur. | Mod değiştirilmeden basınca mod korunuyor; son karede bağla seçilince üretim kapanıyor ve sebep görünüyor. | İstek 3 · Fark 94, 95, 96 |

İzleme davranışı bu koşuda değişmiyor: video hangi modda üretilmiş olursa olsun bugünkü gibi döner.
Kullanıcı kararı; fark listesinin 97. maddesi bu yüzden kapandı.

## C · Galeri ve seçim barı

| # | İş | Bitti sayılır | Kaynak |
|---|---|---|---|
| 10 | ✅ **Toplu kart taşıma.** Seçili bir kart sürüklenince seçimin tamamı bitişik blok olarak taşınır, sıra korunur; seçili olmayan sürüklenirse yalnız o gider. Dağınık seçim bırakıldığı yerde yan yana gelir. Yeni bir öğe eklenmez. | Üç dağınık kare seçilip taşınınca yan yana iniyor, aralarındaki sıra korunuyor, aradaki kartlar boşluğu kapatıyor. | İstek 5 · Fark 70, 71, 72 |
| 11 | ✅ **Kart kopyalama.** Seçim barına Kopyala gelir, kısayolu Ctrl + D. Kopya birebir doğar, adı kopya önekiyle başlar, kaynağın bir üstüne iner, seçim kopyaya geçer. Yalnız bekleyen kareler seçiliyse buton doğmaz. | Bir kare kopyalanınca üstünde ikizi beliriyor, seçim ona geçiyor, ikizden birini silmek öbürünü bozmuyor. | İstek 7 · Fark 77, 78, 79 |
| 12 | ✅ **Toplu katman silme.** Seçim barına Videoları sil ve Sesleri sil gelir. Kareler yerinde kalır, yalnız katman düşer; katmanı olmayan seçili kareler atlanır ve onay metni bunu söyler. | On iki kare seçilip videoları silinince kareler ve fotoğrafları duruyor, videosu olmayanlar atlanmış ve sayı onayda doğru yazmış. | Fark 80, 81 |
| 13 | ✅ **Seçim barının görünümü.** *(Fark 84 kapandı: bar 28 pikselde kalıyor — v4 fark listesi, karar 27.)* Öğeler arası boşluk daralır ve bar sarmaz; seçimde bekleyen kare varsa katman silme düğmeleri hiç çizilmez. | Beş düğme tek satırda kalıyor, yalnız bekleyen seçiminde bar üç öğeye iniyor. | Fark 82, 83, 84 |
| 14 | ✅ **Detaydan dönünce galerinin yerinde durması.** Bir kare açılıp geri gelince galeri sıfırdan yüklenmeyecek, sayfa bırakıldığı yerde duracak. | Kare açılıp kapanınca galeri baştan kurulmuyor; kayma yeri ve o ana kadar yüklenmiş kareler duruyor. | İstek 1.2 / 6 |
| 15 | ✅ **Galeri kartının görsel hizalaması** *(grup)*. *(28–31. kararlar kapandı: sürükleme, hover'daki numara, bırakma anı ve karışık seçim onayı bugünkü hâlinde kalıyor — v4 fark listesi.)* Sahiplik rozetleri sol alta taşınır, ikonlarını bırakır, her katman kendi kutusunu alır; ikinci bekleyen katmanın hapı birincinin altına dizilir; hover'da numara kalkar; sürükleme basılı tutmayla başlar; bekleyen hapının tonu ve hatalı karenin perdesi düzeltilir. | Listedeki on farkın hepsi ekranda kapanmış. | Fark 60–62, 64, 65, 69, 73, 74, 75, 76 |

## D · Üretim panelleri

| # | İş | Bitti sayılır | Kaynak |
|---|---|---|---|
| 16 | ✅ **Panel hata dili.** Buton hiçbir eksik alan için pasifleşmez — basmadan önce panel sakin durur, basınca altında hata kartı doğar ve sebep tek satır yazar. Sebep dört ayrı duruma göre değişir. Varyant boşken kutu uyarıya döner. Buton yalnız süren işlemde pasif kalır. | Dört sebebin dördü ayrı ayrı çıkarılıyor; hiçbirinde buton önceden kilitli değil; varyant kutusuna yazmaya başlayınca uyarı temizleniyor. | İstek 4.3 · Fark 27, 28, 29, 35 |
| 17 | ✅ **Panelin görsel hizalaması** *(grup)*. Kapsam satırına seçim dairesi gelir, model satırı açılır kutuya döner, kapsam satırının adı tam yazılır, Süre bloğu kalkar. | Dört farkın dördü de kapanmış; panelde Model, Kapsam, Üretim modu, Varyant ve buton dışında blok kalmamış. | Fark 30–33 |
| 18 | ✅ **Fotoğraf varyant varsayılanı 4 → 2.** Bir prompt'tan kaç kare üretileceğinin varsayılanı iki olur. Katman panelindeki varyant değişmez. | Panel açıldığında kutuda 2 yazıyor. | İstek 8 |

## E · Detay sayfası

| # | İş | Bitti sayılır | Kaynak |
|---|---|---|---|
| 19 | ✅ **Her sekme yalnız kendi katmanını gösterir.** Alt katmanların dosya adları ve prompt kutuları gider; karenin kendi adı ve sırası üstte kalır. Kuyrukta bekleyen katmanın kutusunda ortalanmış tek satır durur. | Video sekmesinde yalnız video prompt'u, ses sekmesinde yalnız ses prompt'u görünüyor; kare adı üç sekmede de duruyor. | İstek 4.1 · Fark 86, 87, 92 |
| 20 | ✅ **Sekmelerin ayrılması.** Foto, Video ve Ses sekmeleri arasına boşluk girer, her biri kendi köşe yarıçapını alır; açık sekme yalnız rengiyle belli olur. | Üç sekme ayrı ayrı okunuyor, açık olan renginden ayırt ediliyor, olmayan katmanın sekmesi pasif duruyor. | İstek 4.2 · Fark 85 |
| 21 | ✅ **Sağ panelin düzeni.** Panel iki gruba ayrılır — üstte kare bilgisi, altta üretim — grup başlığı ve ayraç olmadan. Prompt kutuları sabit yüksekliğe geçip büyür, taşan metin kendi içinde kayar. Her prompt başlığının sağına kopyala ikonu gelir. Etiketler hangi katmanı okuduğunu söyler. | Pencere boyu değişince kutular esnemiyor; kopyala ikonu metni panoya alıyor; etiketler katman adını taşıyor. | Fark 88–91 |
| 22 | ✅ **Detayın görsel hizalaması** *(grup)*. *(36–39. kararlar kapandı: uçtaki oklar, kuyruktaki kopyanın şeridi, katmanı kuyruktan alan düğme ve hapın konumu bugünkü hâlinde kalıyor — v4 fark listesi.)* Oynatıcı çubuğu ve dalga videonun içine iner, oynat düğmesi çerçeve alır, sahnenin üst boşluğu açılır, hap ve düğme metinleri düzeltilir, negatif prompt düzenlenebilir olur. | Listedeki farkların hepsi ekranda kapanmış. | Fark 98–117 |

## F · Proje ekranı

| # | İş | Bitti sayılır | Kaynak |
|---|---|---|---|
| 23 | ✅ **Proje adı değiştirme.** Proje kartına kalem düğmesi gelir; pencere yeni proje penceresinin aynısıdır, alan mevcut adla dolu ve seçili gelir. Ad başka bir projede kullanılıyorsa uyarı aynı yerde çıkar. Yalnız ad değişir; klasör içeriği, kare adları ve kuyruk etkilenmez, üretim akarken de yapılabilir. Yıkıcı bir eylem değildir. | Üretim akarken bir projenin adı değiştiriliyor, kuyruk kesintisiz sürüyor, kare adları olduğu gibi kalıyor. | İstek 10 · Fark 1–4 |
| 24 | ✅ **Proje ekranının hizalaması** *(grup)*. *(43–45. kararlar: karttaki kalem çerçevesiz kalıyor, liste kendi içinde kayıyor — 9 Ağustos'un N3 kararı geri alındı — ve bant taşmaya değil sayıya bakıyor.)* Karttaki silme düğmesi yıkıcı eylem standardına geçer, yeni proje penceresi yeniden adlandırma penceresiyle aynı ölçüye iner, liste uzayınca kayma göstergesi belirir, silme onayının cümle sırası değişir. | Dört farkın dördü de kapanmış. | Fark 5, 6, 8, 9 |

## G · Kuyruk

| # | İş | Bitti sayılır | Kaynak |
|---|---|---|---|
| 25 | ✅ **Kısmi üretici eksikliğinde uyarının kendi kartına geçmesi.** *(46. karar: farkın motor yarısı zaten doğruydu — motor bir türü bitirmeden ötekine başlamıyor. Değişen, panelin ne zaman ve nerede konuştuğu.)* Yalnız bir türün üreticisi eksikken panelin geneli etkilenmez; uyarı ve kurulum düğmesi o türün kendi kartının içinde durur, diğer türler normal akar. | Ses üreticisi eksikken foto ve video kartları akıyor, uyarı yalnız ses kartında duruyor. | Fark 38 |
| 26 | ✅ **Kuyruk panelinin görsel hizalaması** *(grup)*. *(47–49. kararlar: onayın "kare" sözcüğü ve durdu kartının ham çıktı kutusu kalıyor; fark 59 zaten 25. maddede kapandı.)* Tür kartının başlık dili ve büyük sayısının rengi, duraklatılıyor hâlindeki nokta, tamamlandı kartının tonu, hata kartının düğme metni ve ne zaman doğduğu, bekleme hâlinde boşaltma düğmesinin görünmesi. | Listedeki farkların hepsi ekranda kapanmış. | Fark 41–48, 50, 59 |

---

## H · Yeniden açılan iş — 21 Ağustos

**Bu bölüm koşunun ortasında açıldı.** Kullanıcı, kendi saydığı bir işin tanınmaz hâle geldiğini
söyledi; madde geri kondu.

Kaydı istek listesinde vardı ve bu koşuda bir numara alıp düşürülmüştü —
**yeniden açılıyor, numarası değişmiyor.**

| # | İş | Bitti sayılır | Kaynak |
|---|---|---|---|
| 27 | ✅ **Galeri çok fotoğrafta uygulamayı kilitliyor.** *(Yeniden açıldı; ilacı 24 Ağustos'ta ölçümle değişti.)* Fotoğraflar Colab'dan tarayıcıya saniyede 112 KB ile geliyordu — bir kare 17 saniye, boru dolunca da arayüz "sunucuya ulaşılamadı" veriyordu. Sebep ölçüldü: sunucuyu dışarı açan tünel varsayılan olarak UDP kullanıyor, Colab'ın ağı da UDP'yi kısıyor. **İlaç tek ayar: tünel TCP'ye alınır**; aynı kare 0.18 saniyeye iniyor. *Küçük önizleme fikri düştü* — ölçüm baytın sebep olmadığını gösterdi; ayrıntı [araştırma belgesinde](../research/2026-08-23-queen-editor-galeri-yavasligi.md). | Çok kareli bir projede galeri açılırken uygulama kilitlenmiyor ve karolar gözle görülür hızda doluyor. | İstek 1.1 |

**27 koddur.** İşi bu tarafta yazıldı ve iki turla bitirildi — yalnız "bitti sayılır" yargısı Colab
turunu bekliyor.

---

## I · Galeri deneyimi — 24 Ağustos'ta eklendi

**Bu bölüm 27'nin teşhisinden doğdu.** Boru açılırken galeri kuyruğunun kodu okundu ve kullanıcının
20 Ağustos'ta söylediklerinin hâlâ karşılanmadığı görüldü; ardından kullanıcı önbelleğin neden
işlemediğini fark etti. İkisi de o koşunun yan ürünü; 28 bu koşuda bitti, 29 aynı gün düştü.

| # | İş | Bitti sayılır | Kaynak |
|---|---|---|---|
| 28 | ✅ **Galerinin indirme sırası.** Kullanıcının kendi cümleleriyle üç iş: *"görünmeyeni isteme — bunu kaldır"*, *"aynı anda en fazla 2 fotoğraf — bunu kontrol et doğru mu diye"*, *"bir queue gibi olsa, istek atsa, cevap gelince tamamlanınca diğerini atsa"*. Üstüne teşhiste bulunan iki hata: kuyruğun kendi açıklaması yaptığı işi anlatmıyor, ve bir karo sıradan çıktıktan sonra indirmeye devam ediyor — yani aynı anda kaç fotoğraf indiği kâğıt üstünde yazandan büyük. | Galeri kareleri kaydırma yönünden bağımsız, baştan sona sırayla doluyor; aynı anda inen kare sayısı kodun söylediği sayı. | İstek 1.1 |
| 29 | **Önbellek koşular arasında yaşamıyor** — *24 Ağustos'ta açıldı, aynı gün kullanıcı kararıyla **düştü**.* Kullanıcının tespiti: *"cache çalışmıyor çünkü cloudflare her seferinde random generated bir adres veriyor."* Her Colab koşusu yeni bir adres alıyor, tarayıcı önbelleği de adresi anahtar olarak kullanıyor — yani dün tamamen inmiş bir fotoğraf bugün yabancı sayılıp yeniden iniyor. Tespit doğru kabul edildi, çözümü bu koşuya ait değil. | — *(düşen maddenin bitti yargısı olmuyor)* | Kullanıcı tespiti, 24 Ağustos |

**29 ölçülmeden düştü, ve bu koşunun kendi dersiyle çelişmiyor.** *"Ölçmeden sıralama yazılmaz"*
dersi, birden çok aday varken hangisinin önce geldiğini yazmayı yasaklıyor. Burada sıralanacak aday
yok: tarayıcıda bayt saklayan **her** depo — HTTP önbelleği, Cache Storage, IndexedDB — origin'e
göre bölünüyor, origin de konak adının kendisi. Adres değişince hepsi birden yabancılaşıyor, yani
"kendi önbelleğimizi yazalım" diye bir aile hiç yok. Sabit adres seçeneklerden biri değil, **tek
kapı** — ve o kapı defterin tünel satırıyla kullanıcının alan adında duruyor, uygulamanın kodunda
değil. Kayıt [backlog](../../../queen-editor/BACKLOG.md)'a geçti.

**Foto rotasının `immutable` başlığı yerinde kalıyor.** Bugün yarısı zaten çalışıyor: koşu içinde
galeri kaydırması ve detaydan dönüş ağa hiç çıkmıyor. Silmek bunu geri götürür ve yer de
kazandırmaz — başlık olmayınca Werkzeug `no-cache` koyuyor, yani bayt yine diske iniyor, üstüne her
fotoğraf için bir gidiş-dönüş ekleniyor. Adres sabitlendiği gün başlığın ikinci yarısı kod
değişmeden açılır.

---

## K · Geri dönüş — 24 Ağustos, turun kendi içinden

**Bu bölüm turun ortasında doğdu.** Kullanıcı 30. maddenin turunu yaparken, üçüncü bölümün
*"detaydan dönünce galeri yerinde"* kontrolünde kartların yerinde bir yükleniyor gördü. Tur o noktada
durdu; K bitince kaldığı yerden sürer ve K'nin kendi satırlarını da kapsar.

**14 yanlış işaretlenmedi.** O madde kayma yerinin ve o ana kadar yüklenmiş karelerin durmasını
istiyordu; ikisi de duruyor. Ekranı boşaltan şey onun hiç kapsamadığı başka bir cevap: fotoğraf üret
panelinin kutularını dolduran proje kaydı. Galeri o kaydı kullanmıyor bile, ama bugün onu bekliyor.

**İşi dörde bölen şey kullanıcının kendi kuralı:** *"yüklenmesi ve güncellenmesi gereken bir şey
varsa yüklenebilir, sorun yok — ama her biri kendi parçasını güncellesin. Kartı etkileyen bir şey
yoksa orası etkilenmesin. Kartlarda güncelleme lazımsa ve zaten veri varsa sessiz yapılsın, çünkü
aktif kartları göremiyoruz."*

| # | İş | Bitti sayılır | Kaynak |
|---|---|---|---|
| 31 | ✅ **Galeri, kendisine gerekmeyen bir cevabı beklemez.** Bugün proje kaydı gelene kadar tüm ekran tek bir yükleniyor işaretine dönüyor — galerisi, başlığı ve sağdaki rayıyla birlikte. Bundan sonra ekran anında açılır; bekleyen tek yer fotoğraf üret paneli olur ve beklediğini kendi sütununun içinde söyler. Kayıt okunamazsa hata kartı da tam ekran yerine o panelde durur. | Bir projeye ilk kez girildiğinde de bir kareden dönüldüğünde de galeri hemen görünüyor; yükleniyor işareti yalnız fotoğraf üret panelinin içinde çıkıyor. | Colab turu · kullanıcı kuralı, 24 Ağustos |
| 32 | ✅ **Elde cevap varken hiçbir gösterge yanmaz.** Proje kaydı, model listesi ve üretici listesi bir ziyaret boyunca hatırlanır; geri dönüşte arkada tazelenir, ekranda hiçbir şey kıpırdamaz. Kareler, fotoğraflar ve kayma yeri bunu zaten yapıyor — eksik olan üçü tamamlanıyor. | Bir kare açılıp kapandığında ekranın hiçbir yerinde yükleniyor çıkmıyor; model kutusu ve üretici satırları olduğu gibi duruyor. | Kullanıcı kuralı: *"zaten veri varsa sessiz yapılsın"* |
| 33 | ✅ **Ekran, kuyruğun durumunu bilmeden konuşmaz.** Sunucu ilk cevabını vermeden kuyruk paneli "kuyruk boş" diyor — akan bir üretim varken bile. Bilmediği sürece o kart susar. | Üretim akarken bir kare açılıp dönülünce kuyruk paneli bir an bile "kuyruk boş" demiyor. | Teşhis, 24 Ağustos |
| 34 | ✅ **Açık panel geri dönüşte yerinde kalır.** Bugün hangi panel açıksa kapanıp fotoğraf üret paneline dönüyor. | Kuyruk paneli açıkken bir kare açılıp dönülüyor; panel yerinde. | Colab turu, 24 Ağustos |
| 35 | ✅ **Yazılmış ama gönderilmemiş metin geri dönüşte duruyor.** Fotoğraf üret panelinin kutularına yazılan metin diske yalnız Kuyruğa ekle'ye basıldığında geçiyor; arada bir kareye bakıp dönen kullanıcı yazdığını kaybediyor ve kutuda en son gönderdiği metni buluyor. | Panele bir şey yazılıyor, gönderilmeden bir kare açılıp dönülüyor; yazılan metin kutuda duruyor. | Kullanıcı, 24 Ağustos |
| 36 | ✅ **Fotoğraf inerken karonun bekleme hâli.** Halka karonun sol üstüne yapışıp deforme oluyor, ve karo aynı anda hem çizgili hem halkalı — iki gösterge birden. Halka ortasında ve yuvarlak durur; çizgi beklemeden kalkar, "piksel yok" diyen hâllere bırakılır. | Çok kareli bir projede fotoğraflar inerken her karonun ortasında yuvarlak bir halka dönüyor, arkasında çizgi yok. | Kullanıcı, 25 Ağustos |

| 37 | ✅ **Export fotoğrafları da taşır.** Bugün export yalnız video yazıyor; fotoğraflar hiç girmiyor. Exportun içine `photos/` klasörü gelir ve videosu olan her karenin fotoğrafı, videosuyla aynı numarayla oraya kopyalanır. Birleşik ve ayrı export aynı anda alınırsa fotoğraflar bir kez iner. | Export alındığında klasörün içinde `photos/` var ve içindekiler `.mp4` listesiyle birebir eşleşiyor; iki mod aynı anda alınınca fotoğraflar tek kopya. | Kullanıcı, 25 Ağustos |

| 38 | ✅ **Açık sekme kareler arasında yerinde kalır.** Detayda video izlerken sonraki kareye geçilince sekme fotoğrafa düşüyor ve video her seferinde yeniden seçiliyor. Bundan sonra sekme yerinde kalır; yalnız sonraki karede o katman yoksa fotoğrafa döner. | Videosu olan kareler arasında oklarla gezilirken video sekmesi açık kalıyor; videosuz bir kareye gelince fotoğrafa düşüyor. | Kullanıcı, 25 Ağustos |

**33, 34'ün önünde durmalı.** 34 tek başına yapılırsa kuyruk paneli açık dönmeye başlar ve 33'ün
sustuğu yanlış cümle ilk kez ekrana çıkar.

**Galeri seçiminin hatırlanması 34'ten çıkarıldı — kullanıcı kararı, 24 Ağustos.** Seçim modundayken
bir kareyi açmanın yolu yok: seçim varken karta tıklamak kareyi açmıyor, seçime ekliyor. Yani
"detaydan dönünce seçim kayboluyor" diye bir durum hiç oluşmuyor. Seçimin gerçekten kaybolduğu tek
yol export ekranına gidip dönmek, ve o ayrı bir kapı. Kaydı [backlog](../../../queen-editor/BACKLOG.md)'a geçti.

**35, detay sayfasının kuralıyla çelişmiyor.** Orada yazı *başka bir kareye geçilince* ölüyor
(madde 76) — panel ise tek bir forma ait ve hiçbir yere geçmiyor. Aynı soruya iki cevap değil, iki
ayrı soru.

---

## J · Kullanıcıyla birlikte yapılacak işler — koşunun en sonu

**Bu bölüm tek başına yapılmaz.** Bölümün "bitti" yargısı koda bakarak verilemiyor — queen-editor
yerelde koşmuyor, defteri kullanıcı çalıştırıyor ve sonucu kullanıcı görüyor.

**Bu bölümün maddesi koşunun testidir** ve H, I ile K de dahil **her şeyden sonra**, en sonda durur.
Kullanıcı koşuyu maddeler arasında değil, en sonda bir kerede deniyor. *(24 Ağustos'ta bir kez
başladı ve K bölümünü doğurup durdu; K bitince aynı listeden sürer.)*

| # | İş | Bitti sayılır | Kaynak |
|---|---|---|---|
| 30 | **Colab turu — koşunun tek testi ve en sonu.** Dal yayınlanır ve defter koşulur; kullanıcı koşunun **tamamını** birden dener. H ve I bölümlerinin maddeleri de bu turda görülür. | Kullanıcı turu yapmış; çıkan her şey yazıya geçmiş ve [backlog](../../../queen-editor/BACKLOG.md)'a eklenmiş. | İstek 1.1 |
