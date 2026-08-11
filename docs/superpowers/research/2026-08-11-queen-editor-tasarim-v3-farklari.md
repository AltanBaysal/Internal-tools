# Queen Editor — Tasarım "Basit v3" ile bugünkü uygulamanın farkları

**Tarih:** 2026-08-11 · **Branch:** `feat/mira-v1`
**Tasarım belgesi:** [fark çıkarma tasarımı](../specs/2026-08-11-queen-editor-tasarim-v3-fark-cikarma-design.md) ·
**Plan:** [fark çıkarma planı](../plans/2026-08-11-queen-editor-tasarim-v3-fark-cikarma.md) ·
**Öncülü:** [tasarım v2 fark belgesi](2026-08-08-queen-editor-tasarim-v2-farklari.md)

---

## 0 · Başlık notu

**İsim çakışması.** Tasarım projesindeki **"Basit v3"**, repodaki **roadmap v5**'e karşılık gelir.
Bir önceki eşleşme "Basit v2" = roadmap v4 idi. Belge boyunca ikisi de tam adıyla anılır.

**Öncelik kuralı.** Tasarımın anlatısı üst üste binmiş katmanlardan oluşuyor. Geçerlilik sırası:
**v3.2 > v3.1 > v3 > v2 > v1.** Üstü çizili metin ölüdür ve bulgu üretmemiştir. Bu kural iki yerde
işledi: v3 "Export değişmedi" diyordu, v3.2 Export'u baştan tasarladı — v3.2 geçerli. Ve v3
wireframe'i hâlâ eski JSON export'unu çiziyor — yine v3.2 geçerli.

**Bugünkü tabanın durumu.** Roadmap v4'ün 1-11. maddeleri uygulandı ve push edildi; 12. madde
(Colab turu) yalnız yüzeysel koşuldu. Sonucu: **`düzeltilecek` tipli maddelerde "kod yanlış" ile
"kod doğru, çalışırken patlıyor" ayrımı yapılamaz.**

### Yöntem ve damga

Üç yol aynı anda, birbirini görmeden koştu ve her biri bulgularını kendi dosyasına yazdı:

| Yol | Neye demirledi | Bulgu |
|---|---|---|
| **Y1 · Anlatı** | tasarımın yazılı kararları; wireframe kaynağına erişimi yoktu | 55 |
| **Y2 · Tasarım kaynağı** | v3 wireframe'inin kendisi; yazılı anlatıyı hiç görmedi | 51 |
| **Y3 · Ters yön** | bugünkü uygulama; tasarım tarafının tamamı açıktı | 64 |

Ham toplam 170 bulgu, çakıştırmadan sonra **106 madde**; kullanıcının elle geçişi (2026-08-12) iki
madde daha ekledi (107-108, damgasız) — liste **108 madde**. Damgalar:

| Damga | Anlamı |
|---|---|
| **kesin** | üç yol da gördü |
| **güçlü** | iki yol gördü |
| **zayıf sinyal** | tek yol gördü — atılmadı, damgasıyla listede duruyor |

Bir uyarı: **`düzeltilecek` türünde tavan 2/3'tür.** O tür, uygulamanın kendi eski tarifini
tutturup tutturmadığını sorar; Y2 o tarifi hiç görmedi, dolayısıyla o türde bulgu üretemezdi.

---

## 1 · Özet

Tasarım "Basit v3" tek bir fikrin etrafında dönüyor: **kare artık yalnız fotoğraf değil.** Bir kare
foto, en fazla bir video ve en fazla bir sesten oluşan bir katman yığını; ses videoya bindiriliyor.
Bunun üç sonucu var. Birincisi, **hiçbir üretim var olanı ezmiyor** — "üret = ekle, sil = kaldır";
varyant istemek kareyi kopyalamak demek. İkincisi, **sağ panel şeridi üçten altıya çıkıyor**
(fotoğraf · video · ses · kuyruk · agent · üreticiler); video ve ses prompt'ları kullanıcıya
sorulmuyor, sırası gelince bir dil modeli yazıyor. Üçüncüsü, **kuyruk tek kart olmaktan çıkıp tür
başına karta bölünüyor** ve motor tür tür bitiriyor: önce fotolar, sonra videolar, sonra sesler.
Yanında: JSON export tamamen kalkıyor ve yerine kendi ekranı olan, birleşik ya da ayrı video yazan
bir Export geliyor; dosya adları katmanları taşıyacak biçimde yeniden tanımlanıyor; silme dili
fotoğraftan kareye geçiyor; kurulum akışı üretim panellerinin içine giriyor.

---

## 2 · Fark listesi

Tek düz liste, kesintisiz numaralandırma. Alt başlıklar okunabilirlik içindir, numarayı sıfırlamaz.

Türler: **eklenecek** (bugün hiç karşılığı yok) · **değişecek** (karşılığı var, farklı) ·
**düzeltilecek** (bugün kendi tarifine göre zaten yanlış) · **öksüz** (bugün var, tasarımda yok).

**"Bugün yanlış" ile "v3'te değişecek" farklı iki iddiadır** ve tür sütunu onları ayırır:
`düzeltilecek` bir hatayı gösterir, `değişecek` bir tasarımcı kararını.

### Projeler

**1. Proje silme onayı kare dilini konuşacak ve üretimin akıbetini söyleyecek** · `değişecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün proje kartındaki çöp kutusuna basınca onay "«düğün» projesi silinsin mi?" ve altında "İçindeki
tüm fotoğraflar kalıcı olarak silinir. Bu işlem geri alınamaz." diyor; üretime ne olacağı hiç
geçmiyor.
Tasarımda alt satır "İçindeki tüm kareler — fotoğraf, video ve ses dosyalarıyla birlikte — kalıcı
olarak silinir." olacak ve metin ayrıca "Çalışan üretim durdurulur, kuyruktaki işler atılır"
diyecek.

**2. Proje silmek çalışan üretimi gerçekten durduracak** · `değişecek` · davranış · zayıf sinyal · Y3
Bugün onaydan sonra proje klasörü siliniyor ama motor o projeyi üretiyorsa durdurulmuyor; kuyruktaki
işler atılmıyor ve koşu klasörü bulamayınca kendi hatasıyla düşüyor.
Tasarımda proje silmek üretimi durduracak ve kuyruktaki işleri atacak — onay metni bunu önceden
söylediği için davranışın da ona uyması gerekecek.

**3. Proje kartındaki silme butonu çerçevesini bırakacak** · `değişecek` · görsel · zayıf sinyal · Y2
Bugün proje kartının sağ üstündeki silme butonu kırmızı çerçeveli bir kutu olarak çiziliyor.
Tasarımda aynı köşede çerçevesiz, zeminsiz kırmızı çöp ikonu duracak — kutu çizgisi olmayacak.

**4. Uzun proje listesinde kaydırma çubuğu ve solma perdesi yok** · `düzeltilecek` · görsel · zayıf sinyal · Y3
Bugün proje sayısı ekrana sığmayınca sayfa olağan biçimde kayıyor; ızgaranın sağında ayrı bir
kaydırma çubuğu, altında listenin devam ettiğini söyleyen bir perde belirmiyor.
Tarifi neydi: sekizden çok proje olunca ızgaranın sağında ince bir kaydırma çubuğu ve altta yaklaşık
70 piksellik, sayfa zeminine karışan bir solma perdesi belirmeliydi.
> Tasarımın kendi içinde çelişkisi var: yazılı anlatı "ızgaranın kendi içinde ayrı bir kaydırma
> alanı yok" derken ekran çizimi sekiz projeden sonra çubuğu ve perdeyi koyuyor. İki ifade de
> yazıldı.
> **Karar (kullanıcı, 2026-08-12):** Sayfa kayacak. Izgara içi kaydırma, çubuk ve solma perdesi
> olmayacak — bugünkü davranış kalıyor, çizimdeki çubuk ve perde ölü.

**5. "Bu ad zaten kullanılıyor" uyarısı yazarken değil, basınca çıkıyor** · `düzeltilecek` · davranış · zayıf sinyal · Y3
Bugün yeni proje kutusuna yazarken geçersiz karakter, boşluk ve uzunluk uyarıları anında beliriyor;
ama var olan bir proje adı yazıldığında hiçbir şey olmuyor, uyarı ancak Oluştur'a basılıp sunucu
reddettikten sonra çıkıyor.
Tarifi neydi: ad kullanılıyorsa kutunun altında kırmızı satır belirmeli ve uyarı varken Oluştur pasif
kalmalıydı.
> Uygulamanın kendi gerekçesi var: "kullanılan ad bir kural ihlali değil, çakışmadır" diyerek
> yazarken sunucuya sormamayı seçmiş. Tasarım uyarının hangi anda çıkacağını doğrudan yazmıyor.
> **Karar (kullanıcı, 2026-08-12):** Bugünkü davranış kalıyor — uyarı Oluştur'a basılınca çıkar,
> yazarken sunucuya sorulmaz.

**6. Projeler listesinin yükleme ve hata hâlleri tasarımda karşılıksız** · `öksüz` · görsel · zayıf sinyal · Y3
Bugün ekran açılırken gövdenin ortasında dönen gösterge duruyor; liste okunamazsa "Projeler
yüklenemedi" kartı ve Tekrar dene çıkıyor, ızgara hiç çizilmiyor.
Tasarımda karşılığı yok — yalnız dolu ve boş liste çizilmiş.

### Proje ekranı ve panel şeridi

**7. Şeritte üç ikon var, altı olacak** · `değişecek` · görsel · **kesin** · Y1 Y2 Y3
Bugün sağ kenardaki 48 piksellik şeritte üç ikon duruyor — Üretime ekle · Kuyruğu takip et ·
AI agent — ve basılan ikon vurgu rengine dönüp sağında dikey çizgi çıkarıyor.
Tasarımda şeritte altı ikon olacak: fotoğraf üret · video üret · ses üret · kuyruk · agent, en altta
boşlukla ayrılmış üreticiler. Üreticiler ikonu kurulum sürerken köşesinde yanıp sönen mor nokta
taşıyacak.

**8. Şeridin kendi zemini ve seçili işareti değişecek** · `değişecek` · görsel · zayıf sinyal · Y2
Bugün şeridin kendi zemini yok, ikon hücreleri 40×40 ve seçili ikonun sağında hücreden taşan kısa
bir mor çizgi duruyor.
Tasarımda şeridin kart zemini olacak, hücreler şeridin tam genişliğini kaplayacak (48×46) ve seçili
hücrenin sağ kenarı boydan boya 2 piksel mor olacak; seçili olmayanlar aynı kalınlıkta saydam çizgi
taşıyacağı için ikonlar seçimle kaymayacak.

**9. Fotoğraf panelinin ikonu değişecek** · `değişecek` · görsel · zayıf sinyal · Y1
Bugün şeridin ilk ikonu artı işareti.
Tasarımda fotoğraf çerçevesi ikonu olacak; video panelininki video kamera, ses panelininki dalga.

**10. Projeden çıkış onayı kalkacak, yerine bilgi balonu gelecek** · `değişecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün "Projeden çık"a basınca "Projeden çıkılsın mı?" onay penceresi açılıyor; üretim akıyor olması
bu pencereyi değiştirmiyor.
Tasarımda onay penceresi hiç açılmayacak, doğrudan çıkılacak. Kuyruk akarken butonun üstüne gelince
300 piksellik bilgi balonu belirecek: canlı mor nokta + "Üretim arka planda sürüyor" ve altında
"Projeden çıksan da pencereyi kapatsan da kuyruk durmaz. Döndüğünde biten kareleri galeride
bulursun." Kuyruk boşken hiçbir şey gösterilmeyecek.

**11. Aynı anda tek projede üretim kısıtı tasarımda karşılıksız** · `öksüz` · davranış · **kesin** · Y1 Y2 Y3
Bugün başka bir projede üretim sürerken bu projenin ekleme butonu pasifleşiyor, hem üretim hem
kuyruk panelinde "Üretim sürüyor: «öbür proje» — bitmesini bekle." satırı çıkıyor ve gönderilen
istek reddediliyor.
Tasarımda karşılığı yok — hiçbir katman projeler arası kilitten söz etmiyor, kuyruk tek projenin
akışı olarak anlatılıyor.

**12. Proje açılırken bekleme ve "ayarlar okunamadı" hâlleri tasarımda karşılıksız** · `öksüz` · görsel · zayıf sinyal · Y3
Bugün bir projeye girince ayarları okunana kadar app bar'ın altında tek bir dönen gösterge duruyor;
okunamazsa "Proje ayarları yüklenemedi" kartı ve Tekrar dene geliyor, galeri ve panel hiç
çizilmiyor.
Tasarımda karşılığı yok — paneli her zaman dolu varsayıyor.

### Fotoğraf üret

**13. Panelin başlığı "Fotoğraf üret" olacak** · `değişecek` · görsel · güçlü · Y1 Y2
Bugün panelin tepesindeki büyük harfli küçük başlık "ÜRETİME EKLE" diyor.
Tasarımda "Fotoğraf üret" diyecek — panel adı ürettiği şeyi söyleyecek, kuyruğa girme eylemini
değil.

**14. Ana butonun adı "Kuyruğa ekle" olacak** · `değişecek` · görsel · **kesin** · Y1 Y2 Y3
Bugün formun altındaki mor butonda "Üretime ekle" yazıyor; basılınca "Ekleniyor…" oluyor.
Tasarımda "Kuyruğa ekle" yazacak; ara durum aynı kalacak. Aynı etiket video ve ses panellerinde de
kullanılacak, önlerinde kendi katman ikonlarıyla.

**15. Format hatasında "Kuyruğa eklenemedi" de çıkıyor — iki durum birbirine karışıyor** · `düzeltilecek` · davranış · güçlü · Y1 Y2 · *elle doğrulandı*
Bugün prompt listesi okunamayacak biçimdeyken butona basınca kutu kırmızı çerçeveye giriyor ve
altında "Format hatası — liste okunamadı" yazıyor; **aynı anda** butonun altında ikinci bir kırmızı
satır olarak "Kuyruğa eklenemedi" beliriyor. Tek olay iki farklı sebeple anlatılıyor.
Tarifi neydi: bunlar iki ayrı durum — format hatası kutunun altındaki satırla anlatılmalı,
"Kuyruğa eklenemedi" ise kareler kuyruğa yazılamadığında çıkan ayrı bir satır olmalıydı.
Tasarımda butonun altındaki yer boş kalmayacak ama oraya format hatasının kendi metni gelecek:
kutunun altında kısa "Format hatası", butonun altında ortalanmış "Format hatası — liste okunamadı".
> Kaynağa kadar takip edildi: panel, sunucudan sayı dönmeyen her isteği ayrım yapmadan "reddedildi"
> sayıyor ve "Kuyruğa eklenemedi" satırını basıyor; format hatası da o reddin bir türü olduğu için
> ikisi birlikte doğuyor.

**16. "Kuyruğa eklenemedi" satırı ne yapılacağını söyleyecek** · `değişecek` · görsel · **kesin** · Y1 Y2 Y3
Bugün kareler kuyruğa yazılamayınca butonun altında sola yaslı kırmızı "Kuyruğa eklenemedi" satırı
çıkıyor.
Tasarımda aynı yerde ortalanmış "Kuyruğa eklenemedi — tekrar dene" duracak; ya hepsi ya hiçi kuralı,
alanların açık kalması ve akan kuyruğun etkilenmemesi aynen sürecek.

**17. Yeşil onay kartı iki saniye kalacak** · `değişecek` · görsel · zayıf sinyal · Y2
Bugün kuyruğa ekleme başarılı olunca yeşil onay kartı çıkıyor ve dört saniye sonra kayboluyor.
Tasarımda kart iki parçaya ayrılacak (ayrı bir onay işareti + metin) ve iki saniye sonra kaybolacak.
> Tasarım süre için iki ayrı şey söylüyor: fotoğraf panelinin notu "birkaç saniye sonra kendiliğinden
> kaybolur" derken video/ses panelinin notu "2 sn kalır" diyor. İki ifade de yazıldı.
> **Karar (kullanıcı, 2026-08-12):** Kart 10 saniye kalacak — iki tasarım değerinin ikisi de değil.

**18. Model listesi okunamayınca kart formun içinde kalıyor** · `değişecek` · görsel · zayıf sinyal · Y1
Bugün model listesi çekilemezse üretim panelinin içinde, model kutusunun hemen altında "Model
listesi okunamadı" kartı beliriyor ve altında sunucunun kendi cümlesi duruyor; kuyruğa ekleme yine
mümkün kalıyor.
Tasarımda bu bir üretim/bağlantı hatası sayılacak ve kuyruk panelindeki ölümcül hata kartıyla aynı
kalıba girecek; ayrı bir ekran tasarlanmayacak.
> Tasarım kalıbın aynı olacağını söylüyor, kartın hangi panelde duracağını söylemiyor.

**19. Kayıtlı model artık kurulu değilse çıkan uyarı tasarımda karşılıksız** · `öksüz` · görsel · güçlü · Y1 Y2
Bugün daha önce seçilmiş model üreticinin listesinde yoksa seçim değiştirilmiyor, seçili kalıyor ve
model kutusunun altında kırmızı "Bu model artık kurulu değil." satırı çıkıyor.
Tasarımda karşılığı yok — model açılır kutusunun hiçbir hata ya da uyarı hâli çizilmemiş; kurulum
konusu Üreticiler paneline taşınmış.

**20. Model alanının yükleme ve boş hâlleri tasarımda karşılıksız** · `öksüz` · görsel · zayıf sinyal · Y3
Bugün model listesi okunurken açılır listede tek seçenek olarak "yükleniyor…" duruyor ve alan
tıklanamıyor; liste boş dönerse "model bulunamadı" yazıyor.
Tasarımda karşılığı yok — model alanının yalnız kapalı hâli ve seçili değeri çizilmiş.

**21. Prompt kutusundaki örnek liste tasarımda karşılıksız** · `öksüz` · görsel · zayıf sinyal · Y3
Bugün prompt kutusu boşken içinde soluk bir örnek duruyor; yazmaya başlayınca kayboluyor.
Tasarımda karşılığı yok — boş liste ekranında kutu tamamen boş çizilmiş.

**22. Kuyruğa eklemeden önce panelin kaydedilmesi tasarımda karşılıksız** · `öksüz` · davranış · zayıf sinyal · Y3
Bugün butona basınca önce prompt listesi, negatif, varyant ve model projeye yazılıyor; bu yazma
başarısız olursa istek hiç gönderilmiyor ve butonun altında kaydın kendi hata satırı çıkıyor.
Tasarımda karşılığı yok — formun saklandığını söylüyor ama saklamanın gönderime bağlı olup
olmadığını yazmıyor.

### Video üret

**23. Video üret paneli yok** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün yok.
Tasarımda şeritteki video ikonuna basınca 320 piksellik panel "Video üret" başlığıyla açılacak:
model (örnek "WAN 2.1") · kapsam (iki radyo satırı — "Videosu olmayanlar" ve "Seçili kareler", her
satırın sağında o kapsamdaki kare sayısı; seçili olan mor çerçeve ve mor sayı alacak, öteki %40
opaklığa düşecek) · varyant (56 piksellik ortalanmış sayı kutusu) · mor "Kuyruğa ekle" · altında
tahmin satırı ("9 video üretilecek — her kare kendi videosunu alır.") · en altta "Video prompt'u
otomatik: LLM her fotonun kendi prompt'undan yazar. Detayda okunur, düzenlenir."

**24. Kapsam radyosu galerideki seçime uyacak** · `eklenecek` · davranış · güçlü · Y1 Y2
Bugün yok.
Tasarımda galeride hiçbir kare seçili değilken "Seçili kareler" seçeneği soluk duracak; galeride
kare seçilince radyo kendiliğinden ona geçecek.

**25. Varyantın fazlası kopya kare doğuracak, videolu kare ezilmeyecek** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün yok.
Tasarımda videosuz kareye varyant 1 ile video istenince video karenin kendisine takılacak; varyantın
fazlası ve zaten videosu olan karenin bütün varyantları galeriye yeni kopya kareler olarak girecek.
Kopyalar orijinalin hemen yanında duracak ve foto dosyasını onunla paylaşacak.

**26. Seçimdeki bekleyen ve çalışan kareler atlanacak** · `eklenecek` · davranış · güçlü · Y1 Y2
Bugün yok.
Tasarımda seçimde fotosu henüz olmayan bekleyen ya da çalışan kare varsa video işi kurulurken o
kareler atlanacak.

**27. Video prompt'u sorulmayacak, dil modeli yazacak** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün yok.
Tasarımda üretim başlatılırken video prompt'u sorulmayacak; iş sırası gelince dil modeli fotonun
kendi prompt'undan yazacak, yazdığı metin kaydedilecek ve detay sayfasında okunup düzenlenebilecek —
foto prompt'u orada salt okunur olacak.

**28. Video süresi bu sürümde sabit olacak** · `eklenecek` · davranış · zayıf sinyal · Y1
Bugün yok.
Tasarımda her video 5 saniye olacak ve ayarı bulunmayacak.

**29. Panelin ara ve boş hâlleri** · `eklenecek` · görsel · güçlü · Y2 Y3
Bugün yok.
Tasarımda butona basınca buton pasifleşip yanıp sönen nokta + "Ekleniyor…" gösterecek; bitince
altında yeşil onay kartı doğacak ("6 video kuyruğa eklendi") ve iki saniyede kaybolacak, galeride
kopya kareler o anda "video kuyrukta" hapıyla belirecek. Kapsam boşsa buton pasif olacak ve tahmin
satırının yerine "Tüm karelerin videosu var — üretilecek bir şey yok." yazacak; hata rengi
kullanılmayacak.

### Ses üret

**30. Ses üret paneli yok** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün yok.
Tasarımda video panelinin birebir aynısı "Ses üret" başlığıyla açılacak: model örneği "MMAudio v2",
kapsam satırı "Videosu olup sesi olmayan kareler", buton önünde dalga ikonu, onay metni "6 ses
kuyruğa eklendi", boş hâl metni "Videosu olup sesi olmayan kare yok — üretilecek bir şey yok."

**31. Videosuz kare ses kapsamına hiç girmeyecek** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün yok.
Tasarımda ses videoya bindirileceği için videosu olmayan kare kapsama girmeyecek; seçiliyse
atlanacak.

**32. Ses prompt'u foto ve video prompt'undan yazılacak** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün yok.
Tasarımda iş sırası gelince dil modeli karenin hem foto hem video prompt'undan ses prompt'unu
yazacak; detayda okunup düzenlenecek, video prompt'u orada salt okunur olacak.

### Kuyruk

**33. Foto, video ve ses işleri aynı kuyrukta akacak** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün kuyrukta yalnız fotoğraf işi var; bir parti eklenince kareler planın sonuna yazılıyor ve motor
sırayla onları üretiyor.
Tasarımda üç türün işi de tek kuyrukta akacak (donanım tek); video ve ses işleri sona girecek,
duraklatma, boşaltma, hata ve üç deneme kuralları aynı kalacak.

**34. Kuyruk tek kart yerine tür başına karta bölünecek** · `değişecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün kuyruk panelinde tek durum kartı var: canlı nokta + "Üretiliyor" başlığı, altında 26 puntoluk
tek sayı ve yanında "kare bekliyor".
Tasarımda karışık kuyrukta her tür kendi kartını alacak (Foto · Video · Ses); her kartta durum satırı
(canlı nokta + "üretiliyor" ya da soluk "sırada"), büyük sayı ve "iş bekliyor" duracak. Çalışan kart
mor çerçeve alacak, sıradakiler %55 opaklığa düşecek. Salt fotoluk kuyrukta tek kart ve "kare
bekliyor" sürecek.

**35. Kuyruk sözcüğü "kare"den "iş"e dönecek** · `değişecek` · görsel · **kesin** · Y1 Y2 Y3
Bugün sayının yanında "kare bekliyor" okunuyor.
Tasarımda "iş bekliyor" okunacak — video ve ses işi yeni kare açmadığı, var olan karenin katmanını
ürettiği için "kare" saymak yanlış olacak.

**36. Kart sırası üretim sırası olacak, motor tür tür bitirecek** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün yok.
Tasarımda kartların sırası motorun çalışma sırasını gösterecek: önce tüm fotolar, sonra videolar,
sonra sesler. Ses üretilirken kuyruğa foto eklenirse o iş turun bitmesini bekleyecek; biten türün
kartı kaybolacak.

**37. Bitiş tek satır yerine iki ayrı kart olacak** · `değişecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün kuyruk bitince aynı kartta yeşil "20 kare üretildi" yazıyor ve hatalı varsa aynı cümlenin
devamına kırmızı ", 3 hatalı" ekleniyor.
Tasarımda yeşil kart yalnız iyi haberi verecek; hata varsa altında ayrı bir kırmızı kart doğacak —
"3 kare üretilemedi — 2 foto · 1 video" — ve içinde topluca kuyruğa geri gönderen bir Tekrar dene
duracak. Hata yoksa kırmızı kart hiç doğmayacak.

**38. Hata satırındaki "galeride göster" kalkacak, yerine "Hepsini tekrar dene" gelecek** · `değişecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün hatalı kare varsa kartta altı çizili kırmızı satır çıkıyor — "3 kare üretilemedi — galeride
göster" — ve tıklayınca galeri ilk hatalı karenin üstüne kayıyor.
Tasarımda satır "3 kare üretilemedi — 2 foto · 1 video" diyecek ve yanında "Hepsini tekrar dene"
duracak; galeriye gönderen bağlantı kaldırılmış, gerekçe olarak hatalı karelerin galeride zaten
kırmızı durduğu söylenmiş.

**39. Kuyruk durum kartı hâline göre renk alacak** · `değişecek` · görsel · zayıf sinyal · Y2
Bugün kartın çerçevesi ve zemini bütün hâllerde aynı nötr renkte; yalnız nokta ve başlık yazısı renk
değiştiriyor.
Tasarımda kart "Kuyruk tamamlandı" hâlinde yeşil çerçeve ve saydam yeşil zemin, "Üretim durdu"
hâlinde kırmızı çerçeve ve saydam kırmızı zemin alacak; öteki hâllerde nötr kalacak. İç boşluk her
yönde 14 piksel, başlık tek aralıklı olacak.

**40. Panelin başlığı "Kuyruk" olacak** · `değişecek` · görsel · zayıf sinyal · Y2
Bugün panel açıkken başlığı "KUYRUĞU TAKİP ET" — şerit ikonunun adının aynısı.
Tasarımda şeridin ikon adı "Kuyruğu takip et" kalacak ama panelin başlığı yalnız "Kuyruk" olacak.

**41. "Kuyruğu boşalt" panelin en dibine inecek** · `değişecek` · görsel · zayıf sinyal · Y2
Bugün Kuyruğu boşalt butonu, devam et butonunun hemen altında, onunla aynı öbekte duruyor.
Tasarımda ikisinin arasına esneyen bir boşluk girecek: ana buton kartın altında kalacak, yıkıcı olan
panelin en dibine itilecek.

**42. Boş kuyruk kartı panelin yeni adını söyleyecek** · `değişecek` · görsel · güçlü · Y2 Y3
Bugün kuyruk boşken kart "Üretime ekle panelinden kare gönder." diyor.
Tasarımda "Fotoğraf üret panelinden kare gönder." diyecek.

**43. Açılışta kuyruğun kendiliğinden sürdüğünü söyleyen satır gelecek** · `eklenecek` · görsel · zayıf sinyal · Y2
Bugün proje açılınca yarım kalan kuyruk kendiliğinden sürüyor ama bunu söyleyen bir şey yok.
Tasarımda sayının altında "uygulama açıldı — kuyruk kaldığı yerden sürüyor" satırı duracak.
> Sürmenin kendisi bugün de tasarımın istediği gibi oluyor; eksik olan yalnız bunu söyleyen satır.
> Satırın ne kadar kalacağını tasarım söylemiyor.

**44. Üretim sürerken bekleyen sayısı çalışan kareyi de sayıyor** · `düzeltilecek` · davranış · zayıf sinyal · Y1 · *elle doğrulandı*
Bugün üretim sürerken kart "8 kare bekliyor" diyor — o an üretilmekte olan kare de bu sayıya dahil.
Duraklat'a basılınca çalışan kare bitiyor, sayı 7'ye iniyor.
Tarifi neydi: üretiliyorken sayı çalışan kareyi saymamalı (7), duraklatınca yarım kalan kare kuyruğa
geri döndüğü için 8'e çıkmalıydı.
> Kaynağa kadar takip edildi: bekleyen sayısı diskte durumu "bekliyor" olan karelerden okunuyor ve
> üretilmekte olan karenin diskteki durumu hâlâ "bekliyor" — galeri onu yalnız görüntülerken
> "çalışıyor" gösteriyor.
> **Tasarımın kendi içinde çelişkisi var:** aynı paragraf hem "çalışan kare yarıda kesilmez, biter
> sonra durur" diyor hem "duraklayınca yarım kalan kare kuyruğa geri döner (7 → 8)". Kare bitiyorsa
> geri dönecek yarım kare yok. Hangi okuma kazanırsa kazansın, **üretim sürerken sayının çalışan
> kareyi sayması** tasarımın tablosuna aykırı.
> **Karar (kullanıcı, 2026-08-12):** Çalışan kare bitirilmez — yarım kalan iş kuyruğa geri döner,
> sayı 7'den 8'e çıkar.

**45. Kare üç deneme dolmadan hatalı sayılıyor** · `değişecek` · davranış · zayıf sinyal · Y1
Bugün üretici "bu kare düştü" diye cevap verdiği anda kare tek denemeyle kırmızıya dönüyor ve kuyruk
sonraki kareye geçiyor; üç deneme kuralı yalnız hiç cevap gelmeyen durumlarda işliyor.
Tasarımda kare kırmızı hapı ancak üç deneme başarısız olduktan sonra alacak; detaydaki sebep satırı
da bunu söyleyecek.
> Tasarımın iki cümlesi farklı yerde duruyor: hata bölümünün son satırı "3 deneme, sonra kuyruk
> durur" derken durum dili tablosu kırmızı hapı "3 deneme başarısız" diye tanımlıyor. İki ifade de
> yazıldı.
> **Karar (kullanıcı, 2026-08-12):** Üç deneme — aynı iş üç kez hata verince kırmızı. Daha önce
> verilmiş bir kararın teyidi.

**46. Kuyruğun büyük sayısı vurgu renginde değil** · `düzeltilecek` · görsel · zayıf sinyal · Y1
Bugün kuyruk kartındaki bekleyen sayısı, ekrandaki en büyük yazı olmasına rağmen olağan metin
renginde duruyor; yalnız üretim durduğunda kırmızıya dönüyor. Seçim barındaki "3 seçili" ise mor.
Tarifi neydi: vurgu rengi mor — marka adının, ilerleme sayacının, ana butonların ve sayı
vurgularının rengi.
> Kural yalnız v1'in görsel dil bölümünden geliyor; v2 ve v3.1 bu sayıyı "büyük sayı" diye anıyor
> ama rengini yazmıyor.

**47. Bağlantı kopunca son bilineni söyleyen kart tasarımda karşılıksız** · `öksüz` · davranış · zayıf sinyal · Y3
Bugün sunucuya ulaşılamayınca kuyruk kartının altında kırmızı kart beliriyor — akan ya da
duraklatılmış kuyrukta "Sunucuya ulaşılamıyor — son bilinen: 7 kare bekliyor" — altında tarayıcının
ham hata satırıyla; yoklama iki saniyede bir denemeye devam ediyor ve ilk başarılı cevapta kart
kayboluyor.
Tasarımda karşılığı yok — hiçbir katman bağlantı kopmasını ayrı bir hâl olarak çizmiyor.

### Üreticiler ve kurulum

**48. Üreticiler paneli yok** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün yok.
Tasarımda şeridin en altındaki ikon "Üreticiler" panelini açacak: başlığın altında "Her üretici kendi
model grubunu kurar. Kullanmadığın kurulmaz." ve üç çerçeveli satır — Fotoğraf · Video · Ses
üreticisi. Kurulu olan satır yeşil "✓ kurulu" gösterecek; kurulu olmayan tam genişlikte mor "Kur"
butonu taşıyacak. Bu sürümde kaldırma olmayacak ve boyut yazılmayacak.
> Panelin içeriği yalnız wireframe'de çizili, yazılı anlatıda yok.
> **Karar (kullanıcı, 2026-08-12):** İçerik tasarımda belli sayıldı — wireframe'deki hâli kaynak.

**49. Üretim panellerinin içine kurulum uyarısı gelecek** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün yok.
Tasarımda üretici kurulu değilken ilgili panelin en üstünde, başlığın hemen altında mor çerçeveli
kart duracak: "… üreticisi kurulu değil." + tam genişlikte küçük mor "Kur". Kart durduğu sürece
"Kuyruğa ekle" pasif kalacak. Kurulum sürerken kart mor ilerleme çubuğu + canlı nokta + "kuruluyor…
bitince bu kart kaybolur" gösterecek ve bitince tamamen kaybolacak. Üç panelde de aynı bileşen
olacak.

**50. Kur butonu nerede onay sorar** · `eklenecek` · davranış · güçlü · Y2 Y3 · **çelişki çözüldü**
Bugün yok.
Tasarımda **iki ayrı Kur butonu** var ve davranışları farklı: Üreticiler panelindeki satırın Kur'u
360 piksellik onay penceresi açacak ("Video üreticisi kurulsun mu? · Kurulum uzun sürebilir. Üretimi
engellemez, arkada sürer."); üretim panelinin içindeki kurulum kartının Kur'u ise onay penceresi
AÇMADAN kurulumu doğrudan başlatacak.
> Y1 anlatıdan "onay penceresi yoktur" okudu, Y2 wireframe'de onay penceresini gördü. Çelişki değil:
> iki farklı butonmuş. Kaynaklar birleştirilerek çözüldü.

**51. Kurulumun kendi iptali ve onayı** · `eklenecek` · davranış · güçlü · Y2 Y3
Bugün yok.
Tasarımda kurulum sürerken satırın yanında ghost kırmızı "İptal" duracak; basınca "Kurulum iptal
edilsin mi? · İnen kısım atılır, sonra baştan kurmak gerekir. Kuyruktaki video işleri atılmaz —
kurulum yapılana kadar beklemede kalır." penceresi açılacak. İptal edilen üretici "kurulu değil"
hâline dönecek.

**52. Kur butonlarının metni yalın "Kur" olacak** · `eklenecek` · görsel · zayıf sinyal · Y1
Bugün yok.
Tasarımda butonda her yerde yalnız "Kur" yazacak; v3'teki "Kur — arkada sürer" metni v3.1'de
kısaltıldı.

**53. Üretici eksikken kuyruk bekleyecek, işler atılmayacak** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün yok.
Tasarımda kuyruktaki tüm işlerin üreticisi kurulu değilse kart "Bekliyor — üretici kurulu değil"
diyecek, altında hangi işlerin beklediğini ("5 video") ve "Kurulum bitince kuyruk kendiliğinden
sürer." satırını gösterecek, tek buton "Video üreticisini kur" olacak. Kısmi eksiklikte yalnız o
türün kartı uyaracak ve sıra o türe gelince kurulum yoksa motor sonraki türe de geçmeyecek. Kurulum
iptali kuyruktaki işleri atmayacak.

### Galeri

**54. Bekleyen kartın ortasındaki "bekliyor" yazısı kalkacak** · `değişecek` · görsel · **kesin** · Y1 Y2 Y3
Bugün henüz üretilmemiş kare kesikli çerçeveli, iyice soluk bir kart olarak duruyor ve tam ortasında
"bekliyor" yazıyor.
Tasarımda kartın ortasında hiçbir metin olmayacak — kesikli çerçeve tek başına "piksel yok"
diyecek.

**55. Çalışan kartın "Çalışıyor" yazısı kalkacak** · `değişecek` · görsel · **kesin** · Y1 Y2 Y3
Bugün sıra bir kareye gelince kartın zemini mor eğik çizgilere dönüyor ve ortasında dönen göstergenin
altında "Çalışıyor" yazıyor; aynı yazı detay sayfasındaki bekleme alanında da çıkıyor.
Tasarımda yalnız dönen gösterge kalacak, yazı kalkacak.

**56. Kartın sol üstüne katman + durum hapı gelecek** · `eklenecek` · görsel · **kesin** · Y1 Y2 Y3
Bugün bir karenin durumu ancak görünüşünden anlaşılıyor: kesikli çerçeve bekliyor, dönen gösterge
üretiliyor, kırmızı çerçeve hata demek; yazılı bir durum etiketi yok.
Tasarımda sol üstte tek kalıpta bir hap belirecek — koyu saydam zeminli, 3 piksel köşeli, 9 punto
tek aralıklı: "foto kuyrukta" (soluk), "foto üretiliyor" (mor + yanıp sönen nokta), "foto hata"
(kırmızı). Aynı kalıp video ve ses için de kullanılacak; bir karede aynı anda tek hap olacak.

**57. Rozet düzeni üç düzleme ayrılacak** · `değişecek` · görsel · güçlü · Y1 Y3
Bugün kartın üstünde tek rozet var: sağ üstteki sıra numarası. Sol üstte yalnız seçim dairesi
beliriyor.
Tasarımda üç düzlem birden olacak — sağ üst sıra numarası, sağ alt sahiplik, sol üst durum hapı.
Seçim modunda onay dairesi sol üstü aldığı için hap sol alta kayacak.

**58. Sağ alta video ve ses sahiplik rozetleri gelecek** · `eklenecek` · görsel · **kesin** · Y1 Y2 Y3
Bugün yok.
Tasarımda karenin videosu varsa sağ altında koyu saydam zeminli küçük rozet duracak — oynat üçgeni +
"video"; sesi de varsa yanına dalga ikonu + "ses" gelecek. Rozetler yalnız katman tamamlandığında
görünecek; ara hâlleri sol üstteki durum hapı anlatacak.

**59. Bekleyen ve çalışan kareler de sürüklenebilecek** · `değişecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün bir kartı kısa süre basılı tutunca yalnız üretilmiş kare kalkıyor; bekleyen ya da çalışan
kareyi basılı tutunca kart kalkmıyor, üstüne karartma ve "üretilince sıralanabilir" ipucu iniyor.
Tasarımda bekleyen ve çalışan dahil bütün kartlar sürüklenebilecek, ipucu kalkacak. Çalışan kare
sürüklenince GPU'daki iş yarıda kesilmeyecek: bitecek, yeni yerinde duracak.

**60. Galeri sırası üretim sırası olacak** · `değişecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün kareleri sürükleyip sıralayınca yalnız görünen sıra, rozet numaraları ve export listesinin
sırası değişiyor; motor bir sonraki kareyi plan sırasına göre seçtiği için üretim sırası aynı kalıyor
ve galeri sırası ayrı bir yerde tutuluyor.
Tasarımda ayrı bir kuyruk sıralaması tutulmayacak; bekleyen bir kare üretilmişlerin arasına
bırakılınca hâlâ bekleyen üst karelerden önce üretilecek. v3.1 bunu tür içine daraltıyor: galeri
sırası tür içinde geçerli olacak, türler arası sırayı (foto → video → ses) değiştirmeyecek.

**61. Boş galeri metni butonun yeni adını söyleyecek** · `değişecek` · görsel · **kesin** · Y1 Y2 Y3
Bugün hiç kare olmayan projede ortada "henüz fotoğraf yok" ve altında "Prompt'ları yaz, Üretime
ekle'ye bas — fotoğraflar burada belirecek" okunuyor.
Tasarımda ikinci satır "Prompt'ları yaz, Kuyruğa ekle'ye bas — fotoğraflar burada belirecek"
olacak.

**62. Silme onayı kare dilini konuşacak ve katmanları sayacak** · `değişecek` · görsel · **kesin** · Y1 Y2 Y3
Bugün seçimden silerken onay "3 fotoğraf silinsin mi?" ve altında "Bu işlem geri alınamaz." diyor.
Tasarımda "3 kare silinsin mi?" ve altında "Karelerin videosu ve sesi de birlikte silinir (2 video ·
1 ses). Bu işlem geri alınamaz." diyecek.

**63. Yalnız bekleyen seçiminin alt satırı değişecek** · `değişecek` · görsel · güçlü · Y2 Y3
Bugün yalnız bekleyen kareler seçiliyken onayın alt satırı "Bu kareler üretilmeyecek. Galerideki
fotoğraflara dokunulmaz." diyor.
Tasarımda "Bu kareler üretilmeyecek. Üretilmiş karelere ve dosyalarına dokunulmaz." diyecek —
korunan şey fotoğraf değil, üretilmiş kare ve bütün dosyaları olacak.

**64. Karışık seçim onayı da kare diline geçecek** · `değişecek` · görsel · güçlü · Y2 Y3
Bugün onay "2 fotoğraf silinsin, 2 bekleyen kare kuyruktan çıkarılsın mı?" + "Fotoğraflar kalıcı
olarak silinir — bu geri alınamaz. Bekleyen kareler üretilmeden kuyruktan çıkar." diyor.
Tasarımda "2 kare silinsin, 2 bekleyen kare kuyruktan çıkarılsın mı?" + "Kareler videosu ve sesiyle
birlikte kalıcı olarak silinir — bu geri alınamaz. Bekleyen kareler üretilmeden kuyruktan çıkar."
diyecek.
> Alt satırı yalnız wireframe yazıyor; yazılı anlatı bu senaryoda sadece başlığı veriyor.
> **Karar (kullanıcı, 2026-08-12):** Alt satır hiç yazılmayacak — pencerede yalnız başlık ve
> butonlar kalacak. Wireframe'in çizdiği açıklama satırı kullanılmayacak.

**65. Seçim barındaki butonun etiketi hep "Sil" olacak** · `değişecek` · görsel · zayıf sinyal · Y2
Bugün alt bardaki kırmızı buton, seçimde üretilmiş kare yoksa "Çıkar", varsa "Sil" yazıyor.
Tasarımda bardaki buton üç senaryoda da "Sil" yazacak; yalnız açılan onay penceresinin metni
değişecek.

**66. Alt seçim barına video butonu konmayacak** · `eklenecek` · davranış · zayıf sinyal · Y1
Bugün kare seçilince alttaki yüzen şeritte "N seçili · Tümünü seç · Sil · Vazgeç" beliriyor.
Tasarımda aynı şerit görünecek ama içine video üretme butonu konmayacak; video işleri yalnız panelden
kuyruğa girecek.
> Tasarım aynı şeyi ses için ayrıca söylemiyor.
> **Karar (kullanıcı, 2026-08-12):** Alt bardan hiçbir üretim tetiklenmeyecek — video da ses de
> yalnız panelden. Sesin boşluğu da böylece kapandı.

**67. Video ve ses hatasında Tekrar dene imleç üstüne gelince çıkacak** · `eklenecek` · görsel · güçlü · Y1 Y2
Bugün yok.
Tasarımda foto hatası olan boş karede Tekrar dene kartın ortasında duracak; video ya da ses hatası
olan karede kartta zaten foto durduğu için üstüne gelince %55 koyu bir örtü inecek ve ortasında
kırmızı çerçeveli, döngü ikonlu buton belirecek.

**68. Katman hatasında Tekrar dene yeni kare açmayacak** · `eklenecek` · davranış · güçlü · Y1 Y3
Bugün yok.
Tasarımda video ya da ses katmanı hata alınca Tekrar dene kareyi çoğaltmayacak, eksik katmanı o
karenin kendisine üretecek — "üret = ekle" kuralının tek istisnası bu olacak. Kopya karenin katmanı
hata alırsa ikinci yol "Kareyi sil" olacak.

**69. "Tekrar dene"ye basınca buton kuyruğa girdiğini söyleyecek** · `değişecek` · davranış · zayıf sinyal · Y3
Bugün kırmızı karedeki Tekrar dene'ye basınca kare kuyruğun sonuna giriyor ama buton olduğu gibi
kalıyor; kartın görünümü ancak bir sonraki yoklamada değişiyor ve arada butona ikinci kez
basılabiliyor.
Tasarımda basınca buton pasif "Kuyruğa eklendi" olacak.

**70. "Tümünü seç"in ikinci basışı tasarımda karşılıksız** · `öksüz` · davranış · zayıf sinyal · Y3
Bugün "Tümünü seç"e basınca çalışan kare dışındaki her kare seçiliyor; hepsi zaten seçiliyken tekrar
basılırsa seçim tümden boşalıyor ve şerit kalkıyor.
Tasarımda karşılığı yok — butonun ikinci basışı hiçbir katmanda tanımlanmamış.

**71. Sıra kaydedilemeyince geri dönme davranışı tasarımda karşılıksız** · `öksüz` · görsel · güçlü · Y1 Y3
Bugün sürükleyip bırakılınca kartlar hemen yeni yerine geçiyor; sunucu bu sırayı yazamazsa "Sıra
kaydedilemedi." satırı çıkıyor ve galeri sunucudan yeniden okunarak eski sıraya dönüyor.
Tasarımda karşılığı yok — sıralamayı yalnız başarılı hâliyle anlatıyor.

**72. Galerinin ilk yükleme göstergesi tasarımda karşılıksız** · `öksüz` · görsel · zayıf sinyal · Y3
Bugün kare listesi ilk kez okunurken galeri "henüz fotoğraf yok" demiyor, ortada dönen gösterge
çıkıyor; boş cümle ancak projenin gerçekten boş olduğu bilinince yazılıyor.
Tasarımda karşılığı yok — boş galeriyi tek hâl olarak çiziyor.

### Detay sayfası

**73. Detaya Foto | Video | Ses sekme şeridi gelecek** · `eklenecek` · görsel · **kesin** · Y1 Y2 Y3
Bugün detay sayfasında görsel alanının üstünde hiçbir şerit yok; alan doğrudan fotoğrafı gösteriyor.
Tasarımda görsel alanının üst ortasında birleşik üç küçük buton duracak: "Foto" · oynat ikonu +
"Video" · dalga ikonu + "Ses". Açık olan mor yazı ve mor çerçeve alacak, karenin sahip olmadığı
katmanın sekmesi gizlenmeyip pasif kalacak ve katman üretilince açılacak.

**74. Video ve ses detayda oynayacak** · `eklenecek` · davranış · güçlü · Y2 Y3
Bugün yok.
Tasarımda video sekmesi 16:9 alanda videoyu 5 saniyelik döngüde oynatacak — ortada 64 piksellik
yuvarlak oynat düğmesi, altta süre · ilerleme çubuğu · süre. Ses sekmesi ayrı bir ses oynatıcı
açmayacak, video ile sesi beraber oynatacak ve ilerleme çubuğunun yerini 46 çubuklu dalga formu
alacak (çalınmış kısım mor).

**75. Sağ sütun katman katman genişleyecek** · `değişecek` · görsel · **kesin** · Y1 Y2 Y3
Bugün sağdaki 300 piksellik sütunda yan yana Sıra ve Dosya adı, altlarında kalan yeri eşit paylaşan
Prompt ve Negatif kutuları duruyor; ikisi de salt okunur ve seed alanı yok.
Tasarımda sütun Sıra · Foto (dosya adı) · Video (dosya adı) · Video prompt (düzenlenebilir) · Foto
prompt (salt okunur) satırlarına ayrılacak; ses sekmesinde aynı iskelet ses için tekrarlanacak ve
orada video prompt'u salt okunur olacak.

**76. Detaydaki prompt kutuları düzenlenebilir olacak** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün detaydaki Prompt ve Negatif kutuları yalnız okunur.
Tasarımda kutular düzenlenebilecek ve düzenleme geçici olacak — "Yeniden üret"e basılana kadar
hiçbir şey kaydedilmeyecek. Bir şey değişince kutunun çerçevesi mora dönecek.
> **Daha önce kapsam dışı bırakılmıştı.**

**77. Detaya "Yeniden üret — yeni kare" butonu gelecek** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün üretilmiş bir karenin detayında tek eylem butonu var ve o da Sil; beğenilmeyen kare ancak
silinip panelden yeni parti gönderilerek yenilenebiliyor.
Tasarımda buton "Yeniden üret — yeni kare" olacak: onay penceresi çıkmadan iş kuyruğun sonuna
girecek, kaynak kare ve dosyası aynen duracak, sonuç kaynağın hemen yanına yeni kare olarak
girecek. Basıldıktan sonra buton pasifleşip "Kuyruğa eklendi" yazacak ve fotoğrafın sol üstünde
canlı "yeniden üretilecek — kuyrukta" rozeti belirecek.
> **Bu madde geri alınmış bir kararı yerinden ediyor.** v2 turunda *"Yeniden üret kapsam dışı —
> uygulanmayacak"* kararı verilmişti. Tasarım Basit v3 aynı adımı hem geri getiriyor hem de "ezer"
> yerine "yanına ekler" biçimine çevirip video ve sese yayıyor. Belge hangisinin geçerli olduğunu
> söylemez.
> **Karar (kullanıcı, 2026-08-12):** Bilinçli geri dönüş — buton yapılacak. v2 turundaki "kapsam
> dışı" kararı bu maddeyle kapandı.

**78. Yeniden üret butonu her durumda vurgulu olacak** · `eklenecek` · görsel · güçlü · Y1 Y2
Bugün yok.
Tasarımda buton prompt değişsin değişmesin her durumda mor duracak; yalnız iş kuyruktayken ya da
üretilirken pasifleşecek. v2'nin "kutu değişince öne çıkar" kuralı kalkacak.

**79. Hata detayında sebep ve Tekrar dene gelecek** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün hatalı karenin detayında kesikli kırmızı alan ve "üretilemedi" yazısı var; sebep yazılmıyor ve
sayfadan tekrar denenemiyor — kullanıcı galeriye dönüp karenin üstündeki butona basmak zorunda
kalıyor.
Tasarımda alan kırmızı çerçeve ve kırmızı zemin alacak, içinde uyarı ikonu + "Bu kare üretilemedi" +
tek satır teknik sebep ("CUDA out of memory — 3 kez denendi") duracak; sağ sütunda mor "Tekrar dene"
olacak ve prompt düzenlenip denenebilecek. Sebep galeride görünmeyecek — orada yalnız hap olacak.

**80. Detayda sekme başına tek yıkıcı eylem olacak** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün detayın altında tek yıkıcı buton var: üretilmişse onay soran "Sil", bekliyorsa onay sormayan
"Kuyruktan çıkar", çalışıyorsa pasif.
Tasarımda Video sekmesinde "Videoyu sil — kare kalır" duracak ve 400 piksellik onay soracak ("Video
silinsin mi? · … ve üzerindeki ses kalıcı olarak silinir — bu geri alınamaz. Kare ve fotoğrafı
galeride kalır."); Ses sekmesinde "Sesi sil — video kalır" olacak ("… Video ve kare kalır; video
sessiz oynar."). Kareyi tümden silmek yalnız Foto sekmesinde mümkün olacak; istisnası kuyruktaki
kopya karede duran "Kuyruktan çıkar" ile hatalı kopyadaki "Kareyi sil".

**81. Kuyruktaki kopya kare detayda nasıl görünecek** · `eklenecek` · davranış · güçlü · Y1 Y3
Bugün yok.
Tasarımda kopya kare kuyruktayken görsel alanında kaynağın fotoğrafı duracak ve üstünde canlı "video
kuyrukta" rozeti olacak, video prompt kutusu boş kalacak ("üretim sırası gelince LLM yazacak");
"Kuyruktan çıkar" onay sormadan kopya kareyi de kaldıracak. Gezinme dizisi değişmeyecek, kopya
kareler de dizide olacak.

**82. Bekleyen ve çalışan kare detayının görsel alanı değişecek** · `değişecek` · görsel · zayıf sinyal · Y2
Bugün bekleyen karenin detayında kesikli kare (1:1) tutucu duruyor ve içinde "bekliyor" + "henüz
üretilmedi" yazıyor.
Tasarımda tutucunun oranı karenin kendi oranı olacak ve içindeki iki satır %45 opaklıkta
çizilecek; çalışan karede alan dönen göstergeye dönecek.

**83. Detay sayfasındaki Sil butonu arka planını bırakmıyor** · `düzeltilecek` · görsel · zayıf sinyal · Y1
Bugün detayın altındaki Sil butonu kırmızı metin, kırmızı çerçeve ve çöp ikonu taşıyor ama arka
planını temizlemiyor; galerideki Sil, kuyruktaki "Kuyruğu boşalt", kartın üstündeki çöp kutusu ve
onay penceresinin son onay butonu arka planlarını açıkça siliyor — yalnız bu buton silmiyor.
Tarifi neydi: yıkıcı eylem butonu her yerde dolgusuz olmalıydı — kırmızı metin, kırmızı çerçeve,
arka plan yok, solunda çöp ikonu; dolu kırmızı buton hiçbir yerde kullanılmıyor.

**84. Adresi bilinmeyen kareyi gösteren ekran tasarımda karşılıksız** · `öksüz` · görsel · güçlü · Y1 Y3
Bugün silinmiş bir karenin eski adresine ya da elle yazılmış bir adrese gidilince detay sayfası
"Fotoğraf bulunamadı" kartını ve altında adı gösteriyor; oklar ve sağ sütun hiç çizilmiyor.
Tasarımda karşılığı yok — detayın yalnız katman hâlleri tanımlı.

### Export ekranı

**85. Export butonu dosya indirmek yerine ekran açacak** · `değişecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün app bar'daki Export bir indirme bağlantısı — basınca ekranda hiçbir şey açılmadan bir veri
dosyası iniyor; içinde projenin klasör yolu ve üretilmiş fotoğrafların, galerinin tersi sırayla
dizilmiş dosya adı + prompt listesi var.
Tasarımda aynı buton dördüncü bir ekranı açacak: kendi app bar'ı olan (ortada "düğün · Export",
sağda "← Galeriye dön"), 560 piksel genişlikte ortalanmış bir sayfa. Veri dosyası olarak export
tamamen kalkacak.
> Wireframe hâlâ eski JSON export'unu çiziyor; öncelik kuralı gereği v3.2 geçerli.

**86. Özet kartı gelecek** · `eklenecek` · görsel · **kesin** · Y1 Y2 Y3
Bugün yok.
Tasarımda kartın DIŞINDA 30 puntoluk proje adı duracak; altındaki çerçeveli özet kartında sırayla
26 puntoluk ana satır ("22 video export edilecek · 1:50 dk"), varsa kırmızı uyarı satırları, 1
piksellik ayraç, en altta "Şuraya yazılacak:" + tek aralıklı yol. Tip ölçeği yalnız üç boyut
kullanacak (26 / 14 / 12), her şey sola dayalı olacak.

**87. İki eşit mor buton yan yana duracak** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün yok.
Tasarımda özet kartının altında yan yana iki eşit mor buton olacak: "Birleşik videoyu export et" ve
"Videoları ayrı export et". Açıklama satırı ve hiyerarşi olmayacak.

**88. Ekranın kendisi onay adımı olacak** · `eklenecek` · davranış · güçlü · Y1 Y3
Bugün yok.
Tasarımda butonlardan birine basınca ayrıca "emin misin?" penceresi çıkmayacak; vazgeçmek Galeriye
dön demek olacak. Önizleme ve video listesi konmayacak.

**89. Koşullu kırmızı uyarı satırları gelecek** · `eklenecek` · görsel · **kesin** · Y1 Y2 Y3
Bugün yok.
Tasarımda koşul oluştukça özet kartında kırmızı satırlar doğacak — "⚠ 16 videonun sesi yok",
"⚠ 3 videosuz kare diziye girmeyecek", kuyruk duraklatılmışken "⚠ 5 karenin videosu kuyrukta
bekliyor — diziye girmeyecek" — koşul yoksa satır hiç görünmeyecek.

**90. Üretim akarken export engellenecek, duraklatılmışken serbest kalacak** · `eklenecek` · davranış · güçlü · Y1 Y2 · **çelişki**
Bugün yok.
Tasarımda kuyruk akarken butonlar pasif olacak ve butonların hemen üstünde kendi kırmızı kartında
"⚠ Üretim sürüyor — 5 video kuyrukta. Kuyruğun bitmesini bekle veya duraklat." okunacak; kuyruk
duraklatılınca export serbest kalacak ve bekleyen video işleri yalnız bilgi satırıyla söylenecek.
> **Tasarım aynı konuyu iki yerde farklı anlatıyor.** Uyarı satırlarını sayan bölüm akan üretimi
> engel diye tarif edip duraklatılmış kuyrukta export'u serbest bırakırken, durumları sayan tablo
> "export yapılamaz — butonlar pasif + kırmızı sebep satırı" diyor. Hangisinin kazanacağı söylenmez.
> **Karar (kullanıcı, 2026-08-12):** Anlatının okuması kazandı. Üretim akarken export engel —
> butonlar pasif, kırmızı sebep satırı okunur; kuyruk duraklatılınca export serbest kalır.

**91. Butonların pasiflik kuralları** · `eklenecek` · davranış · zayıf sinyal · Y2
Bugün yok.
Tasarımda iki buton da üç koşulda pasif olacak (%40 opaklık): öteki buton çalışıyorsa (kendi
çalışması hariç), export edilecek video yoksa, kuyruk akıyorsa.

**92. Export çıktısı Drive'da tarih klasörüne yazılacak** · `değişecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün export tarayıcının indirme klasörüne tek bir metin dosyası bırakıyor; Drive'a hiçbir şey
yazılmıyor.
Tasarımda her export açılışı yeni bir tarih klasörü açacak (`düğün / export / 2026-08-11 14-32 /`);
ayrı export `01.mp4 … 22.mp4` yazacak (numara = galeri sırası, 01 dizinin başı), birleşik export
proje adıyla tek dosya yazacak. Videosuz kareler atlanacak, sesli kareler sesiyle girecek, dosyalar
kopya olacak ve proje klasöründeki orijinaller yerinde kalacak. Aynı açılışın iki export'u aynı
klasöre yazacak, eskiler ezilmeyecek.

**93. Export sürerken butonun yerinde ilerleme okunacak** · `eklenecek` · görsel · **kesin** · Y1 Y2 Y3
Bugün yok.
Tasarımda basılan butonun yerinde canlı nokta + "7 / 22 yazıldı…" ya da "birleştiriliyor…"
görünecek, yüzde ve çubuk olmayacak; öteki buton basılabilir kalacak, iki export aynı anda
çalışabilecek. Bitince tam genişlikte yeşil kartta "✓ Export tamamlandı" ve altında dosya → hedef
satırı okunacak.

**94. Export hatası baştan başlatacak** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün yok.
Tasarımda export hata alınca yarım klasör otomatik silinecek (arayüz bunu söylemeyecek), kırmızı
kartta "Export başarısız" ve tek satır teknik sebep okunacak; ayrı bir Tekrar dene olmayacak, export
butonları yerinde duracak ve yeni basış yeni tarih klasörü açacak.

**95. Hiç video yokken ekran yönlendirmeye dönecek** · `eklenecek` · görsel · **kesin** · Y1 Y2 Y3
Bugün hiç fotoğraf üretilmemiş projede Export'a basınca yine dosya iniyor, içindeki liste boş
oluyor.
Tasarımda özet kartı "Export edilecek video yok" + "Hiçbir karenin videosu yok — önce Video üret
panelinden video üret." diyecek ve iki buton pasif kalacak; bu bir hata görünümü olmayacak.

**96. Export sürerken ekrandan çıkmak export'u iptal edecek** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün yok.
Tasarımda çıkışa basınca 380 piksellik onay açılacak: "Export sürüyor — çıkılsın mı? Çıkarsan export
iptal olur, yarım kalan klasör silinir. Galerine ve karelerine dokunulmaz." Onaylayınca export iptal
olacak; kuyruktaki üretimin aksine export oturuma bağlı olacak, arka planda sürmeyecek. Yıkıcı
sayılmadığı için kırmızı buton kullanılmayacak.

### Adlandırma ve kimlik

**97. Dosya adı şeması katmanlı hâle gelecek** · `değişecek` · görsel · **kesin** · Y1 Y2 Y3
Bugün kare adları `11_d.png` biçiminde — sayı prompt sırasını, harf varyantı gösteriyor; ad galeri
kartının altında ve detayda okunuyor.
Tasarımda ad her katman için bir çift sayı taşıyacak: `P11_3.png`, videolu karede `P11_3_V1_0.mp4`,
sesli karede `P11_3_V1_0_S1_0.wav`. Olmayan katman ada hiç yazılmayacak; harf varyantı sayıya
dönecek (a=0, b=1, c=2, d=3).

**98. Yeniden üretim ad içinde tur numarasını artıracak** · `eklenecek` · davranış · güçlü · Y1 Y3
Bugün yok.
Tasarımda prompt düzenlenip tekrar üretilince yeni tur doğacak — birinci turun dosyaları yerinde
kalırken ikinci tur eklenecek; sıralama önce tur, sonra varyant olacak.

**99. Yeni karenin numarası prompt'un değişip değişmediğine bakacak** · `eklenecek` · davranış · güçlü · Y1 Y3
Bugün yok.
Tasarımda prompt değişmediyse yeni kare aynı ailenin varyantı sayılacak ve numara oradan büyüyecek
(`P11_2` → `P11_4`); prompt değiştiyse sıradaki prompt numarasını alacak (`P15_0`) ama konumu yine
kaynağının yanı olacak. Prompt numaralarının galeri sırasıyla birebir gitmemesi yan etki olarak
kabul edilmiş.

**100. Kopya kareler foto dosyasını paylaşacak** · `eklenecek` · davranış · güçlü · Y1 Y3
Bugün yok.
Tasarımda bir fotodan birden çok video istenince doğan kopya kareler diskte tek foto dosyasını
paylaşacak, video dosyaları ayrı olacak.

**101. Kareyi silmek katmanlarını da silecek** · `eklenecek` · davranış · zayıf sinyal · Y3
Bugün üretilmiş bir kare silinince yalnız kendi dosyası diskten kalkıyor.
Tasarımda kareyi silmek adındaki tüm katman dosyalarını birlikte götürecek — videoyu ve sesi de —
ama paylaşılan foto başka bir karede yaşıyorsa o dosya yerinde kalacak.

**102. Varyant, üstündeki türev katmanları taşımayacak** · `eklenecek` · davranış · güçlü · Y1 Y3
Bugün varyant yalnız fotoğraf üretiminde bir çarpan: 12 prompt × 4 varyant 48 ayrı kare planlıyor ve
aralarında bir bağ tutulmuyor.
Tasarımda varyant, üretilen katmana kadarını taşıyacak: foto varyantında yalnız foto olacak, video
varyantında foto + video olacak ama ses gelmeyecek (sesli bir kareden alınsa bile), ses varyantında
üçü birden olacak. Video yeniden üretilince kopya sessiz doğacak; ses yeniden üretilince kopya kare
videoyu paylaşacak.

### Uygulama geneli

**103. Kare bir katman yığını olacak, üretim hiçbir şeyi ezmeyecek** · `eklenecek` · davranış · **kesin** · Y1 Y2 Y3
Bugün yok — bugün hiçbir üretim var olan bir kareyi ezmiyor, ama bunun sebebi kuralın konmuş olması
değil, yeniden üretmenin hiç bulunmaması.
Tasarımda kural açıkça konacak ve üç katmanı da bağlayacak: kare foto + en fazla 1 video + en fazla
1 sesten oluşacak, ses videoya bindirilecek, hiçbir üretim var olanı ezmeyecek, varyant istemek
kareyi kopyalamak olacak. v2'nin "yerine geçer" kuralı kalkacak.

**104. Arayüz metinlerinde içerik birimi "kare" olacak** · `değişecek` · görsel · güçlü · Y1 Y3
Bugün aynı ekranda iki sözcük birden dolaşıyor: kuyruk kartı "8 kare bekliyor" derken boş galeri
"henüz fotoğraf yok", kuyruk boşaltma onayı "Üretilmiş fotoğraflar galeride kalır" ve seçim onayı
"3 fotoğraf silinsin mi?" diyor.
Tasarımda içerik için her yerde "kare" kullanılacak; "fotoğraf" yalnız foto katmanını kastederken
geçecek. "Kart" ise arayüzdeki kutunun adı olacak.

**105. Onay pencerelerinin genişliği metne göre değişecek** · `değişecek` · görsel · zayıf sinyal · Y2
Bugün kuyruk boşaltma, bekleyen çıkarma ve karışık silme onaylarının hepsi 320 piksel genişlikte
açılıyor; yalnız proje silme 340.
Tasarımda genişlik metnin uzunluğuna göre değişecek: fotoğraf silme 320, proje silme 340, kuyruk
boşaltma 380, yeni proje ve bekleyen çıkarma 400, karışık silme 420, kurulum ve iptal onayları 360,
export çıkış onayı 380.

**106. Pencerelerin klavye ve zemin davranışı tasarımda karşılıksız** · `öksüz` · davranış · zayıf sinyal · Y3
Bugün her onay penceresi Esc ile kapanıyor ve karartılmış zemine tıklamak da vazgeçmek sayılıyor; iş
sürerken ikisi de çalışmıyor, yeni proje kutusunda Enter da Oluştur demek. Seçim modu da Esc ile
kapanıyor.
Tasarımda karşılığı yok — yalnız seçim modunun ve detay sayfasının Esc ile kapandığı yazılı,
pencerelerin klavye ve dış tıklama davranışı hiçbir katmanda çizilmemiş.

### Kullanıcının elle geçişinden (2026-08-12)

Bu iki madde üç yoldan değil, kullanıcının uygulamayı elle gezmesinden geldi. Damga taşımazlar;
tarifleri tasarım katmanları değil, kullanıcının kendisi verdi.

**107. Uygulama açılışta yatayda kayıyor** · `düzeltilecek` · görsel · kullanıcı
Bugün uygulama açılınca yatay kaydırma çubuğu beliriyor — sayfa cihaz ekranından geniş çiziliyor.
Tarif (kullanıcı): varsayılan ekran cihaz ekranına tam oturmalı; yatayda taşma ve kaydırma çubuğu
olmamalı.

**108. Seçim barı en dibe yapışık, yüzer olmalı** · `düzeltilecek` · görsel · kullanıcı
Bugün kare seçilince çıkan bar (madde 66'nın anlattığı "N seçili · Tümünü seç · Sil · Vazgeç"
şeridi) ekranın en dibine yapışık duruyor.
Tarif (kullanıcı): bar yüzer olmalı — en aşağıya yapışmamalı, alt kenardan boşlukla ayrılıp
içeriğin üstünde durmalı.

---

## 3 · queen-tools çarpışması

`collab-toolbox/queen-tools/` iki notebook'tan oluşan ayrı bir zincir: Queen Editor'ün Export
dosyasını okuyup foto prompt'larını hareket prompt'una çeviriyor, sonra o plandan videoları
üretiyor. Tasarım Basit v3 bu zincirin dayandığı her şeye birden dokunuyor. **Belge karar vermez;
yalnız iki tarafın ne beklediğini yan yana koyar.**

| Konu | queen-tools bugün neye dayanıyor | Tasarım Basit v3 ne getiriyor |
|---|---|---|
| **İş emri** | Zincirin girdisi, Colab'a yüklenen Export dosyası. Çevirici dosyanın alanlarını doğruluyor, yoksa durup hata veriyor. | Veri dosyası olarak export tamamen kalkıyor; Export butonu artık bir ekran açıyor ve Drive'a video yazıyor. Zincirin okuyacağı dosya ortadan kalkıyor. |
| **Video üretimi** | `photo_to_video` foto→video işini dışarıda, kiralık güçlü bir donanımda yapıyor; çıktı kendi klasöründe numaralı klipler. | Video üretimi uygulamanın içine giriyor: kendi paneli, kuyruğu, kare başına en fazla bir videosu. Aynı iş iki yerde yapılabilir hâle geliyor. |
| **Hareket prompt'u** | Çevirici, foto prompt'undan hareket prompt'u yazdırıyor (kare başına bir istek, düz metin) ve sonucu kendi plan dosyasında saklıyor. | Video prompt'unu dil modeli uygulamanın içinde yazıyor, kareye kaydediyor ve detayda düzenlettiriyor. queen-tools tasarımı bunu kendi kapsam dışı listesinde *"hareket prompt'unun kare başına Queen Editor'de tutulması ileriki bir iş"* diye anmıştı. |
| **Birleştirme** | Kapsam dışı bırakılmış: "kliplerin tek videoda birleştirilmesi" bilinçle dışarıda tutulmuş, çıktı ayrı klipler. | Export ekranında "Birleşik videoyu export et" butonu var; galeri sırasıyla uç uca ekleyip proje adıyla tek dosya yazıyor. |
| **Ad şeması** | `11_d.png` biçimini bekliyor; çıktı adları plan dosyasındaki konumdan geliyor. | Adlar `P11_3.png` / `P11_3_V1_0.mp4` biçimine geçiyor. |
| **Ses** | Zincir kendi klasöründe bitiyor; foley için ayrı bir araca elle taşınıyor. | Ses üret paneli sesi videoya bindiriyor ve kareye bağlıyor. |
| **Sıra** | Export listesinin sırası videonun sırası; çevirici sırayı değiştirmiyor. | Sıra galeri sırası olmayı sürdürüyor, ama artık üretim sırası da o — ve export sırası galerinin tersi değil, doğrudan galeri sırası. |

---

## 4 · Tasarımın cevaplamadıkları

**Tasarımın kendi içindeki çelişkiler** — belge yazılırken hiçbiri karara bağlanmamıştı; beşini de
kullanıcı 2026-08-12'de karara bağladı. İki ifade de maddelerde duruyor, karar da yanlarına yazıldı:

| Konu | Madde | Karar (kullanıcı, 2026-08-12) |
|---|---|---|
| Üretim akarken export: engel mi, serbest mi | 90 | Akarken engel, duraklatınca serbest — anlatının okuması |
| Duraklatma çalışan kareyi bitiriyor mu, kuyruğa mı iade ediyor | 44 | Kuyruğa iade — 7 → 8 |
| Kırmızı hap bir denemeden mi üç denemeden sonra mı doğuyor | 45 | Üç deneme — aynı iş üç kez hata verince |
| Uzun proje listesinde kaydırma çubuğu var mı | 4 | Yok — sayfa kayıyor, bugünkü davranış kalıyor |
| Yeşil onay kartı kaç saniye kalıyor | 17 | 10 saniye — iki tasarım değerinin ikisi de değil |

**Tasarımın hiç konuşmadıkları:**

- **AI agent paneli hâlâ boş.** Şeritte yerini koruyor, içeriği "sonraki sürümde tasarlanacak"
  deniyor. Bugünkü uygulamada da boş bir panel olarak duruyor.
- **Kuyruk kartlarında canlı noktanın davranışı.** Tür başına kart geldiğinde birden çok kart aynı
  anda görünecek; hangisinin noktasının yanacağı, bekleyen türlerin noktasının nasıl duracağı
  yazılmamış.
- **Üreticiler panelinin kendi içeriği** yalnız wireframe'de var, yazılı anlatıda yok — panel adı
  şerit sırasında geçiyor ama ne göstereceği hiçbir bölümde anlatılmamış (madde 48 wireframe'den
  çıkarıldı). *Karar (kullanıcı, 2026-08-12): wireframe'deki hâli kaynak sayıldı.*
- **Alt seçim barının ses butonu.** Tasarım "video butonu yoktur" diyor; ses için aynı şeyi ayrıca
  söylemiyor (madde 66). *Karar (kullanıcı, 2026-08-12): alt bardan hiçbir üretim yok — ses de
  panelden.*
- **Karışık seçim onayının alt satırı** yazılı anlatıda yok, orada yalnız başlık verilmiş; metni
  yalnız wireframe yazıyor — madde 64'teki alt satır oradan (420 piksellik karton). *Karar
  (kullanıcı, 2026-08-12): alt satır hiç yazılmayacak — pencerede yalnız başlık kalacak.*
- **Bugün var, tasarımda hiç karşılığı olmayan on üç davranış:** projeler arası tek üretim kilidi
  (11), projeler listesinin yükleme/hata hâlleri (6), proje ekranının yükleme hâli (12), kayıtlı
  modelin listeden düşmesi (19), model alanının ara hâlleri (20), prompt kutusundaki örnek (21),
  panelin gönderimden önce kaydedilmesi (22), bağlantı kopma kartı (47), "Tümünü seç"in ikinci
  basışı (70), sıra kaydedilememesi (71), galerinin ilk yükleme göstergesi (72), adresi bilinmeyen
  kare ekranı (84) ve pencerelerin klavye davranışı (106). *Karar (kullanıcı, 2026-08-12): on üçü
  de kalıyor — tasarımın susması kaldırma sayılmadı.*
- **Yeniden adlandırma.** v1'den beri "bu sürümde yok" deniyor; Basit v3'ün kapsam dışı listesinde de
  duruyor. Bugünkü uygulamada da yok.

**Kaynakta bulunan, hiçbir ekranın göstermediği bir şey:** wireframe kaynağında 400 piksellik bir
"video üret" penceresi tanımlı ama ekran haritasındaki hiçbir karton onu göstermiyor — v3'te video
üretimi panelden yürüyor. Ölü bir bileşen olduğu düşünülüyor; bulgu olarak yazılmadı, teyit
edilmeli. *Karar (kullanıcı, 2026-08-12): kalıntı — yok sayıldı, teyit kapandı.*

---

## Bu belgenin sınırı

Üç yol da tam koştu ve listeler çakıştırıldı; bu turun yöntemi işledi. İki bilinen boşluk var:

1. **Renk ve boşluk değerleri kısmen doğrulanmadı.** Y1'e verilen yasak listesinde geçen bir dosya
   adı, uygulamanın kendi biçem dosyasıyla çakıştı ve o yol biçem değerlerini hiç açmadı; görsel
   bulgularını bileşenlerin satır içi stillerinden çıkardı. Y2 tasarımın renk belirteçlerini görüp
   uygulamayı okuduğu için boşluğun büyük kısmı kapandı, ama tam bir renk denetimi yapılmadı.
2. **Zayıf sinyaller elenmedi.** 1/3 damgalı maddelerden yalnız ikisi (15 ve 44) kaynağa kadar takip
   edilip doğrulandı. Kalanlar atılmadı, damgalarıyla listede duruyor — çoğu, o yolun özel yakaladığı
   sınıftan olduğu için tek başına görülmesi beklenen şeyler.
