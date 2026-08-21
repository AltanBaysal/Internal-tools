# Tasarım v4 ile bugünkü uygulamanın farkları

## 0 · Başlık notu

### Üçlü isim çakışması

"v4" bu belgede geçen üç ayrı şeyin adı; hiçbir yerde yalın "v4" yazmıyoruz.

- **Tasarım v4** — karşılaştırdığımız şey: tasarımcının 20 Ağustos'ta bitirdiği tur.
- **Roadmap v4** — repodaki 8 Ağustos yol haritası. Bitti, geçti, bu belgeyle ilgisi yok.
- **feat/queen-editor-v4** — üzerinde çalışılan dal adı.

Öncüllerden farklı olarak burada bir **roadmap eşlemesi yok**: tasarım v4'ün repo karşılığı henüz
yazılmadı. Repo tarafına "bugünkü uygulama" diyoruz.

### İki geçersizlik kuralı

Tasarımın belgeleri geçmişi de taşıyor; her cümlesi geçerli değil.

**Katman kuralı.** Tasarımın kural metni üst üste binmiş katmanlardan oluşuyor. Geçerlilik sırası:

> **v3.6 > v3.5 > v3.4 > v3.3 > v3.2 > v3.1 > v3 > v2 > v1**

Sonraki katman öncekiyle çeliştiğinde sonraki geçerlidir. Üstü çizili metin ölüdür, bulgu üretmez.

> **Not:** Bu turun planı sırayı v3.5'te bitiriyordu. Kaynakta **v3.6** diye bir katman daha var ve
> en üstteki odur — v4 turunun panel hata standardı, detay sağ paneli düzeni, sekme ayrımı ve kart
> kopyalama kararları orada duruyor. Tarama bu düzeltilmiş sırayla yapıldı.

**Geri alma kuralı.** Tasarımın değişiklik günlüğü denenip vazgeçilenleri de kaydediyor.
"Kaldırıldı", "vazgeçildi", "reddedildi", "geri alındı" diyen her madde **yalnız son hâliyle**
geçerlidir. Bu turda ara aşamada kalıp bulgu üretmemesi gereken kararlar: kartın üstündeki mod
şeridi, sahiplik rozetlerinin ikon aşaması, detay panelindeki space-between denemesi, grup
başlıkları, bitişik sekme kararı, panelin altındaki prompt açıklama satırları, ses sekmesindeki
üretim modu satırı ve bekleyen prompt kutusunun tamamen boş bırakılması.

### Bugünkü tabanın durumu

Tasarım v3 karşılaştırmasından bu yana uygulama tarafı epey ilerledi; tarama bu ilerlemiş hâlin
üstünde yapıldı. 20 Ağustos istek listesinin hiçbir maddesi henüz uygulanmadı — yani bu belgedeki
farkların tamamı gerçekten açık. Tarama tam kapsamlıdır: tasarım v4'ün dokunduğu her alan ve
uygulamanın tasarım v4'ün dokunmadığı alanları da denetlendi.

### Yöntem

Üç alt-ajan aynı anda, birbirini görmeden çalıştı; her biri ayrı bir kaynağa demirlendi. Yasaklı
kaynak her ajanın elinden yapısal olarak uzak tutuldu — kimse görmemesi gerekeni okuyamadı.

| Yol | Neye demirlendi | Neyi göremedi | Özel yakaladığı |
|---|---|---|---|
| **Yol 1 · Anlatı** | Tasarımın yazılı kararları: kural metni, ekran notları, değişiklik günlüğü, proje kuralları | Çizimin tamamı | Kararların **gerekçeleri** ve yazılı olup çizilmemiş kurallar |
| **Yol 2 · Tasarım kaynağı** | Çizimin kendisi ve durum makinesi | Yazılı anlatının tamamı | **Yazıya hiç geçmemiş** ayrıntılar: ölçü, ara durum, tam metin |
| **Yol 3 · Ters yön** | İkisi birden; uygulamadan tasarıma yürüdü | — | **Öksüzler** ve uygulamanın kendi tarifinden sapmaları |

Bu turda çizimin açıklama yazıları kartlardan sökülüp ayrı bir belgeye taşındığı için Yol 2'nin işi
öncekilerden zordu: kaynak artık kendini anlatmıyor, ne yaptığı yalnız çizimden okunuyor. Ham bulgu
sayısındaki farkın sebebi de bu.

**Yol × üretim**

| Yol | Ham bulgu | Taradığı | Kendi işaretlediği boşluk |
|---|---|---|---|
| Yol 1 | 44 | Kural metninin tüm katmanları, ekran notlarının 01→19 tamamı, değişiklik günlüğünün her v4 maddesi, yıkıcı eylem standardı | Kuyrukta biten türün kartının kaybolmasını arayüz tarafından doğrulayamadı; detay sekmelerindeki ikonlardan tasarım hiç söz etmediği için o ayrıntıyı bulgu saymadı |
| Yol 2 | 109 | 01'den 19'a tüm ekranlar ve hâlleri, brief kartı, bileşen kiti, stil dosyası | Kurulu üreticiyi kaldırma, panel kilidi, çıkış balonunun tetiği, dizinin ucundaki okların davranışı — dördü de işaretlendi; iki bulgusunu uygulamaya bakıp kendisi geri çekti |
| Yol 3 | 89 (İş A 83 · İş B 6) | Uygulamanın tüm ekran, panel, kart, hap, rozet, pencere ve davranış envanteri; sonda kapanış taraması | Atladığı yer bildirmedi |

**Damga dağılımı**

| Damga | Ne demek | Adet |
|---|---|---|
| kesin | üç yol da gördü | 31 |
| güçlü | iki yol gördü | 39 |
| zayıf sinyal | tek yol gördü | 60 |
| çelişki | kaynaklar birbirini tutmuyor, karar verilmedi | 6 |
| **toplam** | | **136** |

242 ham bulgu 136 satıra indi: aynı geçişi anlatan bulgular tek satırda eritildi ve beş bulgu elle
doğrulamada düştü (aşağıda).

Zayıf sinyal bir kusur değil, **beklenen** sonuçtur: her yolun yalnız kendisinin görebileceği bir
sınıf var (Yol 1 gerekçeler, Yol 2 yazıya geçmemiş ölçüler, Yol 3 öksüzler), o sınıftaki bulguyu tek
başına yakalaması normaldir. Zayıf sinyallerin hepsi kaynağına kadar takip edildi; hiçbiri sessizce
silinmedi. Doğrulananların yanında *elle doğrulandı* notu var, doğrulanamayanlar damgasıyla listede
duruyor.

`düzeltilecek` türünde tavan **2/3**'tür: Yol 2 uygulamanın yazılı tarifini hiç görmediği için o
türü üretemez. O türde 2/3, "kesin"in karşılığıdır.

**Tür × yol matrisi** (ham bulgular)

| Tür | Yol 1 | Yol 2 | Yol 3 |
|---|---|---|---|
| eklenecek | 17 | 29 | 30 |
| değişecek | 22 | 68 | 42 |
| düzeltilecek | 4 | — (üretemez) | 6 |
| öksüz | 1 | 12 | 11 |

**Elle doğrulamada düşen beş bulgu**

1. **Export'ta proje adının yeri** (Yol 1) — çizimde ad özet kartının dışında ve en büyük yazıyla
   duruyor; bugünkü uygulama da öyle. Ekran notlarının "tek kutuda" cümlesi yanıltıcı. Fark yok.
2. **Export ilerlemesinde canlı nokta** (Yol 1) — çizimde buton çalışırken canlı nokta gösteriyor;
   bugünkü uygulama da öyle. Fark yok.
3. **Kurulu üreticiyi kaldırma** (Yol 2) — ekran etiketi "Kaldır" diyor ama çizimde öyle bir düğme
   yok ve ekran notları "kaldırma bu sürümde yok" diyor. Etiket bayat.
4. **Panelin üretim sırasında kilitlenmesi** (Yol 2) — stil dosyasındaki kural hiçbir ekranda
   kullanılmıyor; önceki sürümden kalmış ölü kural.
5. **Silme onaylarının pencere genişlikleri** (Yol 2) — Yol 2'nin kendi notu: bugünküyle örtüşüyor.

---

## 1 · Özet

Tasarım v4 tek bir cümleyle: **videoya bir "üretim modu" kavramı giriyor, kart dili ikondan
kelimeye dönüyor, detay sayfası sadeleşiyor ve seçim barı toplu eylemlerle genişliyor.**

Üretim modu (standart / loop / sonrakine bağla) üç yerde birden görünür oluyor: üretim panelinde bir
seçici, galeri kartında bir rozet, detay sayfasında hem geçmişi söyleyen bir bilgi satırı hem de
gelecek üretimi belirleyen ikinci bir seçici. Kartın üstünde hiçbir mod göstergesi yok — tasarım
bunu deneyip geri aldı. Galeride sahiplik rozetleri sol alta taşınıyor, ikonlarını bırakıp yalnız
kelimeyle konuşuyor. Seçim barına kopyalama ve katman silme giriyor, çoklu seçim tek parça
sürüklenebiliyor. Detay sayfası her sekmede yalnız o katmanı gösteriyor, dosya adı satırları
kalkıyor, prompt kutuları sabitleniyor. Panellerin hata dili baştan kuruluyor: buton artık eksik
alan yüzünden kilitlenmiyor, sebep basıldıktan sonra kırmızı bir kartta tek satırla söyleniyor.

---

## 2 · Fark listesi

Numaralandırma kesintisiz tektir; alt başlıklar yalnız okunabilirlik için ve numarayı sıfırlamaz.

> **"Bugün yanlış" ile "tasarım v4'te değişecek" iki ayrı iddiadır.** `düzeltilecek` türü, tasarım
> v4'ün getirdiği bir yenilik değil, uygulamanın kendi yazılı tarifinden sapmasıdır — orada
> "Tasarım v4'te" yerine "Tarifi neydi" yazar. Tür sütunu ikisini ayırır.

### Projeler

**1. Proje adı değiştirilebiliyor** · eklenecek · davranış · **kesin** (Y1 Y2 Y3)
- Bugün: bir projenin adını değiştirmenin hiçbir yolu yok.
- Tasarım v4'te: kartın sağ üstündeki kalem düğmesine basınca "Projeyi yeniden adlandır" penceresi
  açılır, alan mevcut adla dolu ve seçili gelir, Kaydet'e basınca yalnız ad değişir — klasör
  içeriği ve kare adları olduğu gibi kalır.

**2. Yeniden adlandırmada ad çakışması uyarısı** · eklenecek · davranış · **kesin** (Y1 Y2 Y3)
- Bugün: bugün yok.
- Tasarım v4'te: pencerede başka bir projenin adı yazılınca alan kırmızı çerçeveye döner ve altında
  "Bu ad zaten kullanılıyor. Başka bir ad dene." belirir; yazmaya başlayınca uyarı temizlenir.
- Not: projenin kendi adını aynen kaydetmek hata sayılmaz. Yol 2 çizimden okuduğu için ayrıca
  "Kaydet pasifleşir" diyor; yazılı kural bunu söylemiyor.

**3. Yeniden adlandırma yıkıcı bir eylem değil** · eklenecek · davranış · **güçlü** (Y1 Y3)
- Bugün: bugün yok.
- Tasarım v4'te: kalem düğmesine basınca ne kırmızı buton, ne çöp ikonu, ne onay penceresi gelir;
  pencere doğrudan açılır ve üretim akarken de kullanılabilir.

**4. Yeniden adlandırma penceresinin ölçüsü ve dili** · eklenecek · görsel · **zayıf sinyal** (Y2)
  *elle doğrulandı*
- Bugün: bugün yok.
- Tasarım v4'te: pencere 380px genişlikte ve 20px iç boşlukla açılır; başlığı "Projeyi yeniden
  adlandır", alan etiketi "PROJE ADI", sağ altta sırayla "Vazgeç" ve vurgu renginde "Kaydet" durur.

**5. Proje kartındaki eylem düğmelerinin görünümü** · değişecek · görsel · **çelişki** (Y1 Y2 Y3)
- Bugün: kartın sağ üstünde çerçevesiz, yazısız, yalnız kırmızı bir çöp ikonu durur.
- Tasarım v4'te: sağ üstte 4px aralıklı iki çerçevesiz düğme durur — solda nötr kalem, sağda kırmızı
  çöp.
- Not: tasarımın kendi metinleri burada birbirini tutmuyor. Proje kuralları belgesi proje silmeyi
  yıkıcı eylem standardının örnekleri arasında sayıyor (dolgusuz buton, kırmızı çerçeve, kırmızı
  metin, çöp ikonu); ekran notları ve çizim aynı kartta yalnız iki ikon düğme gösteriyor. İki ifade
  de burada, karar verilmedi.

**6. Yeni proje penceresinin genişliği** · değişecek · görsel · **güçlü** (Y2 Y3)
- Bugün: "Yeni proje"ye basınca 400px genişliğinde pencere açılır.
- Tasarım v4'te: aynı pencere 380px açılır — yeniden adlandırma penceresiyle aynı ölçü.

**7. Boş proje listesinin ikinci satırı** · değişecek · görsel · **güçlü** (Y2 Y3)
- Bugün: hiç proje yokken "İlk projeni oluştur, karelerin burada toplansın" okunur.
- Tasarım v4'te: aynı yerde "İlk projeni oluştur, fotoğrafların burada toplansın" okunur.
- Not: tasarımın kendi terminoloji kuralı içerik birimi için "kare" diyor, çizimi bu cümlede
  "fotoğraf" diyor. İki ifade de kaynakta.

**8. Çok proje varken kayma göstergesi** · eklenecek · görsel · **zayıf sinyal** (Y2)
  *elle doğrulandı*
- Bugün: proje sayısı arttıkça ızgara aşağı uzar, sayfanın kendi kaydırması dışında hiçbir işaret
  çıkmaz.
- Tasarım v4'te: liste sekizi geçince sağında ince bir kaydırma tutamağı belirir ve listenin altında
  zemine karışan bir soluklaşma bandı çıkar; liste alanı sabit kalır, içi kayar.

**9. Proje silme onayının cümle sırası** · değişecek · görsel · **güçlü** (Y2 Y3)
- Bugün: onayda önce silinecek kareler, sonra "Çalışan üretim durdurulur, kuyruktaki işler atılır."
  okunur.
- Tasarım v4'te: üretim cümlesi başa gelir — önce çalışan üretimin durdurulacağı, sonra karelerin
  fotoğraf, video ve sesiyle birlikte kalıcı silineceği söylenir.

**10. Proje listesinin yükleme ve hata halleri** · öksüz · davranış · **güçlü** (Y2 Y3)
- Bugün: liste gelene kadar ortada dönen bir gösterge, gelmezse "Projeler yüklenemedi" kartı ve
  tekrar dene düğmesi çıkar.
- Tasarım v4'te: karşılığı yok.

**11. Yazarken anlık ad doğrulaması** · öksüz · davranış · **zayıf sinyal** (Y3)
- Bugün: yeni proje penceresinde ad yazılırken kısa bir beklemeden sonra kontrol edilir ve uyarı
  anında belirir.
- Tasarım v4'te: karşılığı yok.
- Not: tasarım uyarının nerede çıkacağını söylüyor, ne zaman kontrol edileceğini söylemiyor.

### Proje ekranı ve panel şeridi

**12. Panelin kendi ikonuyla kapanması** · öksüz · davranış · **zayıf sinyal** (Y3)
- Bugün: açık panelin şeritteki ikonuna tekrar basınca panel tümden kapanır ve genişliği galeriye
  geçer.
- Tasarım v4'te: karşılığı yok.
- Not: tasarımın bütün ekranlarında bir panel açık çizilmiş; panelsiz bir hâl yok.

**13. Başka projede üretim sürerken çıkan engel** · öksüz · davranış · **güçlü** (Y2 Y3)
- Bugün: başka bir projenin kuyruğu akarken bu projede "Kuyruğa ekle" pasifleşir ve
  "Üretim sürüyor: <proje> — bitmesini bekle." satırı çıkar.
- Tasarım v4'te: karşılığı yok.

**14. Çıkış bilgi balonunun yeri ve tetiği** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: fare "Projeden çık" düğmesinin üstüne gelince altına bir bilgi balonu iner ve başlığı vurgu
  renginde okunur; fare çekilince kaybolur.
- Tasarım v4'te: balon üst şeridin altında sabit bir yerde durur ve başlığı normal metin renginde
  okunur; yanındaki nokta vurgu renginde nabız atar.
- Not: tasarım balonun neyle açılıp nasıl kapandığını söylemiyor.

**15. AI agent panelinin yazı ölçüsü** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: panel açılınca ortada 12px'lik soluk "Agent buradan çalışacak." okunur.
- Tasarım v4'te: aynı metin 13px olur ve ortalanmış, yanlardan biraz içeride durur.

**16. Şerit hücrelerinin boşluğu** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: şerit üstten 12px boşlukla başlar, ikon hücreleri arasında boşluk yoktur.
- Tasarım v4'te: şerit üstten 8px boşlukla başlar, hücreler arasında 2px boşluk vardır ve şeridin
  dibinde son ikondan sonra 8px boşluk kalır.

**17. Panelin kendi içinde kayması** · öksüz · görsel · **zayıf sinyal** (Y2)
- Bugün: sağ panelin içeriği pencereye sığmayınca panel kendi içinde dikey kayar.
- Tasarım v4'te: karşılığı yok.

### Fotoğraf üret

**18. Panel içindeki kurulum kartının ilerlemesi** · eklenecek · davranış · **kesin** (Y1 Y2 Y3)
- Bugün: panelin tepesindeki karttan "Kur"a basınca kart olduğu gibi kalır, kurulum ilerlemesi
  hiçbir yerde görünmez.
- Tasarım v4'te: "Kur"a basınca düğme kaybolur, yerine ince bir ilerleme çubuğu ile canlı nokta ve
  "kuruluyor… bitince bu kart kaybolur" satırı gelir; kurulum bitince kart tümüyle yok olur ve o ana
  kadar "Kuyruğa ekle" pasif kalır.

**19. Kurulum kartının cümlesi ve tonu** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: üretici eksikken kartta soluk tonda "<üretici> kurulu değil." ve altında üreticinin kendi
  açıklama satırı görünür.
- Tasarım v4'te: aynı cümle en parlak tonda görünür, açıklama satırı hiç doğmaz ve altında tam
  genişlikte vurgu renkli "Kur" durur.

**20. Prompt listesi kutusunun yer tutucusu** · öksüz · görsel · **zayıf sinyal** (Y2)
- Bugün: prompt listesi boşken kutuda örnek bir liste yer tutucu olarak okunur.
- Tasarım v4'te: karşılığı yok — kutu tümüyle boş çizilmiş.

**21. Yeşil onay kartının ömrü** · değişecek · davranış · **çelişki** (Y3)
- Bugün: yeşil onay kartı basıldıktan sonra 10 saniye durup kaybolur.
- Tasarım v4'te: kart birkaç saniye sonra kaybolur.
- Not: uygulamanın kendi kaydı bugünkü sürenin kullanıcı tercihi olduğunu ve tasarımın iki ayrı sayı
  söylediğini yazıyor. İki ifade de kaynakta, karar verilmedi.

### Video üret

**22. Üretim modu satırı** · eklenecek · davranış · **kesin** (Y1 Y2 Y3)
- Bugün: bugün yok — panelde Kapsam ile Varyant arasında hiçbir şey yok ve kuyruğa yazılan işte de
  mod diye bir alan yok.
- Tasarım v4'te: Kapsam ile Varyant arasındaki "Üretim modu" seçicisinden Standart (varsayılan),
  Loop ya da Sonrakine bağla seçilir; seçim kuyruğa eklenen işe yazılır, sonradan değiştirmek
  yeniden üretmek demektir.

**23. Üretim modu seçicisinin görünümü** · eklenecek · görsel · **zayıf sinyal** (Y2)
- Bugün: bugün yok.
- Tasarım v4'te: kutu kapalıyken sağında aşağı, açıkken yukarı ok okunur; açılınca çerçevesi vurgu
  rengine döner, üç satırlı liste panelin diğer içeriğinin üstüne biner ve seçili satırın solunda
  vurgu renkli bir onay işareti durur.

**24. Sonrakine bağla ardışık seçim istiyor** · eklenecek · davranış · **kesin** (Y1 Y2 Y3)
- Bugün: bugün yok.
- Tasarım v4'te: galeride ardışık olmayan kareler seçiliyken liste açılınca "Sonrakine bağla" satırı
  soluklaşıp tıklanmaz olur ve listenin altında "Sonrakine bağla için ardışık kareler seçilmeli."
  belirir; ardışık seçim yapılınca seçenek açılır.

**25. Tahmin ve onay metinleri moda göre değişiyor** · değişecek · davranış · **kesin** (Y1 Y2 Y3)
- Bugün: kapsam ve varyant seçilince butonun altında hep aynı kalıp yazar ("9 video üretilecek — her
  kare kendi videosunu alır.") ve eklendikten sonra yeşil kart hep "9 video kuyruğa eklendi" der.
- Tasarım v4'te: loop seçiliyken tahmin "9 loop video üretilecek — her video kendine döner.", bağlı
  modda "3 bağlı video üretilecek — her video sıradaki karede biter." olur; yeşil onay da "6 bağlı
  video kuyruğa eklendi" gibi moda göre yazar.

**26. Seçili kapsamda kopya uyarısı** · değişecek · davranış · **güçlü** (Y2 Y3)
- Bugün: zaten videosu olan bir kare seçiliyken de tahmin cümlesi değişmez.
- Tasarım v4'te: cümle kopya kareyi söyler — "6 video üretilecek — videolu 1 kare için yeniler kopya
  kare olur, eskisi durur."; ses tarafında aynı cümle "sesi olan 1 kare için…" biçiminde okunur.

**27. Buton eksik alan yüzünden pasifleşmiyor** · değişecek · davranış · **kesin** (Y1 Y2 Y3)
- Bugün: kapsamda iş kalmayınca ya da varyant kutusu boşalınca "Kuyruğa ekle" kilitlenir ve altında
  silik gri bir cümle durur; kullanıcı neden basamadığını denemeden öğrenemez.
- Tasarım v4'te: basmadan önce panel sakin durur — kırmızı çerçeve, uyarı satırı yok — ve buton
  basılabilir kalır; basınca butonun altında yeşil onay kartının kırmızı ikizi doğar. Buton yalnız
  süren işlemde pasiftir: üretici kuruluyorken ve "Ekleniyor…" halinde.
- Not: ekran notlarının ses bölümünde bir yerde "kapsam 0 → buton pasif" de yazıyor. Bu, panel hata
  standardından **önceki** katmanın cümlesi; en üst katman ve değişiklik günlüğünün v4 maddesi
  butonun pasifleşmemesini söylüyor, dolayısıyla geçerli olan budur.

**28. Boş kapsamın sebebi dörde ayrılıyor** · değişecek · davranış · **kesin** (Y1 Y2 Y3)
- Bugün: fotoğrafı üretilmemiş kareler seçilse de, hiç kare olmasa da, hepsinin videosu olsa da aynı
  cümle çıkar: "Tüm karelerin videosu var — üretilecek bir şey yok."
- Tasarım v4'te: butona basılınca sebep hangisiyse o tek satır yazılır — "Tüm karelerin videosu
  var." · "Henüz üretilmiş kare yok." · "Seçili karelerin fotoğrafı henüz üretilmedi." · "Varyant
  sayısı girilmedi — en az 1 yaz." Cümlenin "— üretilecek bir şey yok" kuyruğu hiç yazılmaz.

**29. Varyant kutusu boşken kırmızıya dönüyor** · eklenecek · görsel · **kesin** (Y1 Y2 Y3)
- Bugün: varyant kutusu boşaltılınca hiçbir renk değişmez ve kutu odaktan çıkınca sessizce 1'e
  döner.
- Tasarım v4'te: kutu boşken kırmızı çerçeveye döner ve butona basılınca altta "Varyant sayısı
  girilmedi — en az 1 yaz." çıkar; yazmaya başlayınca uyarı temizlenir.

**30. Kapsam satırının adı eksik yazılıyor** · düzeltilecek · görsel · **kesin** (Y1 Y2 Y3)
- Bugün: video panelinin ilk kapsam satırında "Videosu olmayanlar" okunur.
- Tarifi neydi: satır "Videosu olmayan kareler · N" diye okunacaktı; ses panelindeki eşi ("Videosu
  olup sesi olmayan kareler") tam yazılırken video tarafı kısalmış.
- Not: Yol 2 bu satırı `değişecek` diye yazdı — uygulamanın yazılı tarifini göremediği için o türü
  üretemiyor. Aynı geçiş, tür farkı yapısal.

**31. Kapsam satırının radyo dairesi** · değişecek · görsel · **güçlü** (Y2 Y3)
- Bugün: kapsam satırında yalnız metin ve sayı vardır, seçili olan çerçeve rengiyle belli olur.
- Tasarım v4'te: satırın solunda bir daire durur — seçilide vurgu renginde kalın, ötekinde ince ve
  soluk — ve satır biraz daha ferah bir iç boşlukla çizilir.

**32. Model satırı seçilebilir kutu oluyor** · değişecek · görsel · **güçlü** (Y2 Y3)
- Bugün: video ve ses panellerinde model, seçilemeyen soluk bir metin satırıdır.
- Tasarım v4'te: model, fotoğraf panelindekiyle aynı görünümde bir açılır kutudur — çerçeveli ve
  sağında aşağı oklu.

**33. Paneldeki "Süre" bloğu** · öksüz · görsel · **kesin** (Y1 Y2 Y3)
- Bugün: varyantın altında "Süre" başlıklı bir blok durur — "Her video 5 saniye — bu sürümde
  sabit." / "Ses videonun süresince üretilir."
- Tasarım v4'te: karşılığı yok — panelde Model, Kapsam, Üretim modu, Varyant ve Kuyruğa ekle dışında
  blok yoktur.

### Ses üret

**34. Üretim modu satırı ses panelinde doğmuyor** · eklenecek · davranış · **zayıf sinyal** (Y1)
  *elle doğrulandı*
- Bugün: bugün yok.
- Tasarım v4'te: ses paneli açıldığında üretim modu satırı hiç doğmaz — mod videoya ait bir
  kavramdır.

**35. Ses panelinin boş kapsam cümlesi** · değişecek · görsel · **güçlü** (Y2 Y3)
- Bugün: iş kalmayınca soluk tonda "Videosu olup sesi olmayan kare yok — üretilecek bir şey yok."
  okunur.
- Tasarım v4'te: butona basılınca kırmızı kartta "Tüm karelerin sesi var." okunur.

### Kuyruk

**36. Uygulama açılınca kuyruğun sürmesi** · düzeltilecek · davranış · **çelişki** (Y1 Y2 Y3)
- Bugün: yarım kalmış bir kuyrukla proje açılınca hiçbir şey üretilmez; kuyruk duraklatılmış görünür
  ve kullanıcı "Kaldığı yerden devam et"e basana kadar öyle kalır.
- Tarifi neydi: uygulama açılınca kuyruk kendiliğinden sürecek, "devam edilsin mi?" diye
  sorulmayacak, yarıda kesilen kare baştan üretilecekti.
- Not: uygulamanın kendi kaydı bu davranışın 13 Ağustos 2026'da **kullanıcı kararıyla bilerek**
  değiştirildiğini söylüyor; tasarım metni hâlâ kendiliğinden sürmesini istiyor. İki ifade de
  burada, karar verilmedi.

**37. Kurulum bitince kuyruğun sürmesi** · düzeltilecek · davranış · **kesin** (Y1 Y2 Y3)
- Bugün: üretici eksikliği yüzünden duran kuyrukta üretici geldiğinde kart "Üretici kurulduktan
  sonra kuyruğu sen sürdürürsün." der ve devam düğmesi gösterir; kullanıcı basana kadar hiçbir iş
  üretilmez.
- Tarifi neydi: kurulum bitince kuyruk kendiliğinden akacaktı; bekleme kartı bunu önceden söyleyip
  "Kurulum bitince kuyruk kendiliğinden sürer." diyecekti.

**38. Kısmi üretici eksikliğinde uyarının yeri** · değişecek · davranış · **kesin** (Y1 Y2 Y3)
- Bugün: yalnız bir türün üreticisi eksikken kuyruk paneli bütünüyle bekleme hâline geçer; uyarı ve
  "Kur" ortak kartta durur, diğer türlerin kartları soluklaşır.
- Tasarım v4'te: yalnız o türün kartı kendi içinde "Üretici kurulu değil." ve küçük bir "Kur"
  gösterir; panelin geneli etkilenmez, diğer türler normal akar ve sıra o türe gelince motor bekler.

**39. Kuyruk akarken durum kartı** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: kuyruk akarken panelde yalnız tür kartları görünür, "Üretiliyor" başlıklı durum kartı hiç
  çizilmez.
- Tasarım v4'te: akarken panelde nabız atan nokta ve "Üretiliyor" başlığını taşıyan durum kartı
  durur, içinde büyük bir sayı ve yanında "kare bekliyor" okunur.

**40. Tür kartlarıyla durum kartının bir arada durması** · değişecek · görsel · **çelişki** (Y2 Y3)
- Bugün: kuyruk duraklatılmış, durmuş ya da bitmişken hem tür kartları hem de altlarında ayrı bir
  durum kartı çizilir.
- Tasarım v4'te: panelde ya tür kartları ya da tek bir durum kartı durur; ikisi aynı anda çizilmez
  ve tür başına ayrı kart yalnız kuyruk karışıkken doğar.
- Not: tasarımın kendi içinde çelişkisi var — kural metni "tür başına ayrı kart" derken çizim
  duraklatıldı, durdu ve bitti hâllerini tek kartla gösteriyor. İki ifade de burada.

**41. Tür kartının başlık dili** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: karışık kuyrukta kart başlığında "Foto · üretiliyor" ve "Video · sırada" okunur.
- Tasarım v4'te: "Foto — üretiliyor" ve "Video — sırada" okunur; üreticisi eksik olan tür için
  "Video — bekliyor" okunur.

**42. Tür kartındaki büyük sayının rengi** · değişecek · görsel · **güçlü** (Y2 Y3)
- Bugün: her tür kartındaki büyük sayı, kart çalışıyor da sırada da olsa hep vurgu renginde yazılır.
- Tasarım v4'te: çalışan türün sayısı normal metin renginde, sıradakilerinki soluk tonda olur; vurgu
  rengi yalnız başlık satırında kalır.

**43. Duraklatılıyor hâlinde noktanın rengi** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: "Duraklat"a basılınca kartın noktası vurgu renginde nabız atmaya devam eder.
- Tasarım v4'te: nokta soluk tona düşer ve öyle nabız atar, başlık da soluk tonda "Duraklatılıyor…"
  olur.

**44. Tamamlandı kartının cümle rengi** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: kuyruk bitince kartta yeşil tonda "<n> kare üretildi" okunur.
- Tasarım v4'te: başlık yeşil "Kuyruk tamamlandı" kalır ama altındaki "<n> kare üretildi" soluk
  tonda okunur.

**45. Hata kartının düğme metni** · değişecek · görsel · **güçlü** (Y2 Y3)
- Bugün: üretilemeyen kare varken kırmızı karttaki düğmede "Hepsini tekrar dene" okunur.
- Tasarım v4'te: aynı düğmede "Tekrar dene" okunur.

**46. Hata kartının ne zaman doğduğu** · değişecek · davranış · **zayıf sinyal** (Y2)
- Bugün: üretilemeyen kare varsa kırmızı kart kuyruk akarken de, duraklamışken de, bitmişken de
  görünür.
- Tasarım v4'te: kırmızı kart yalnız kuyruk tamamlandığında doğar.

**47. Bekleme hâlinde kuyruğu boşaltma** · değişecek · davranış · **zayıf sinyal** (Y2)
- Bugün: kuyruk üretici beklerken panelin dibinde "Kuyruğu boşalt" çıkmaz.
- Tasarım v4'te: beklerken de panelin dibinde "Kuyruğu boşalt" durur ve basılabilir.

**48. Kuyruğu boşalt onayının cümlesi** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: onayda "Bekleyen <n> kare üretilmeden kuyruktan çıkar. Üretilmiş kareler galeride kalır."
  okunur.
- Tasarım v4'te: ikinci cümle "Üretilmiş fotoğraflar galeride kalır." olur.

**49. Kuyruğu boşalt onayının butonu** · değişecek · görsel · **çelişki** (Y1 Y3)
- Bugün: onay penceresinin butonu "Boşalt" der.
- Tasarım v4'te: buton "Çıkar" der — dosya silinmediği için dil silmeye değil kuyruktan çıkarmaya
  bağlanır.
- Not: tasarımın kendi içinde çelişkisi var — ekran notları "onay butonu 'Çıkar'" derken çizim aynı
  pencerede "Boşalt" gösteriyor. Çizim geçerli sayılırsa bugünkü uygulamada değişecek bir şey yok.

**50. Durdu kartının ham çıktısı** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: üretim durunca kartta sunucunun cümlesi ve altında açılıp kapanan bir ham çıktı kutusu
  görünür.
- Tasarım v4'te: yalnız tek satır teknik neden okunur ("Bağlantı hatası — 3 kez denendi, sunucuya
  ulaşılamadı"); açılır ham çıktı kutusu yoktur.

**51. Bağlantı kopunca çıkan kuyruk hata kartı** · öksüz · davranış · **güçlü** (Y2 Y3)
- Bugün: kuyruk durumu okunamayınca panelin dibinde "Sunucuya ulaşılamıyor — son bilinen: <n> kare
  bekliyor" başlıklı ayrı bir kart belirir.
- Tasarım v4'te: karşılığı yok.

### Üreticiler ve kurulum

**52. "Kur" kurulumu başlatmıyor** · değişecek · davranış · **çelişki** (Y1 Y2 Y3)
- Bugün: "Kur"a basınca hiçbir kurulum başlamaz; satıra "Bu üretici Colab defterinden kurulur —
  defterde kutusunu işaretleyip çalıştır." cümlesi düşer ve iş kullanıcıya kalır.
- Tasarım v4'te: "Kur"a basınca kurulum doğrudan başlar, kart kuruluyor hâline geçer ve bitince
  kendiliğinden kaybolur; kurulum panel kapansa bile sürer.
- Not: uygulamanın kendi temel kararlarından biri "kurulumu defter yapar, uygulama yalnız neyin
  burada olduğunu söyler" diyor; tasarım bunun tersini tarif ediyor. Bu bir görsel ayrıntı değil,
  iki belgenin sorumluluk paylaşımı konusunda ayrışması. İki ifade de burada, karar verilmedi.

**53. Üretici satırında kurulum ilerlemesi** · eklenecek · görsel · **güçlü** (Y2 Y3)
- Bugün: Üreticiler panelinde "Kur"a basınca satır olduğu gibi kalır, indirme ilerlemesi görünmez.
- Tasarım v4'te: satırda ince bir ilerleme çubuğu belirir, altında canlı nokta ile "kuruluyor…"
  okunur ve satırın sağında kırmızı bir "İptal" durur.

**54. Kurulumu iptal etme ve onayı** · eklenecek · davranış · **kesin** (Y1 Y2 Y3)
- Bugün: bugün yok.
- Tasarım v4'te: kuruluyorken "İptal"e basınca onay penceresi açılır — "Kurulum iptal edilsin mi?" +
  "İnen kısım atılır, sonra baştan kurmak gerekir. Kuyruktaki video işleri atılmaz — kurulum
  yapılana kadar beklemede kalır." İptal kırmızıdır ama çöp ikonu taşımaz: dosya silmiyor, işi
  kesiyor.

**55. Üreticiler panelindeki "Kur" onayı** · eklenecek · davranış · **güçlü** (Y2 Y3)
- Bugün: "Kur"a basınca hiçbir onay sorulmaz.
- Tasarım v4'te: Üreticiler panelindeki "Kur", "Video üreticisi kurulsun mu? Kurulum uzun sürebilir.
  Üretimi engellemez, arkada sürer." onayını açar.
- Not: "onay yok" kuralı **panel içindeki** Kur içindir (üretim panelinin tepesindeki kart); orada
  kurulum onaysız başlar. Üreticiler panelindeki Kur ayrı bir yerdir ve onayı vardır. Kaynaklar
  çelişmiyor, iki farklı yerden söz ediyorlar.

**56. Şerit ikonundaki canlı nokta** · düzeltilecek · görsel · **güçlü** (Y2 Y3)
- Bugün: bir üretici arka planda kurulurken şeritteki üreticiler ikonunda hiçbir işaret çıkmaz.
- Tarifi neydi: kurulum panel kapanınca durmuyor; süren kurulumu şeritteki ikondaki canlı nokta
  belli edecekti. Gösterge yerinde duruyor ama hiç beslenmiyor.

**57. Üretici durumu okunamayınca** · öksüz · davranış · **zayıf sinyal** (Y2)
- Bugün: üretici listesi gelmezse panelde "Üretici durumu okunamadı" kartı ve altında ham çıktı
  görünür.
- Tasarım v4'te: karşılığı yok.

**58. Üretici satırının ölçüsü ve tonu** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: satırın iç boşluğu dar, adı soluk tonda ve küçük, kurulu işareti normal yazıyla.
- Tasarım v4'te: satır her yönde ferah bir iç boşluk alır, adı en parlak tonda ve bir punto büyür,
  kurulu işareti "✓ kurulu" olarak monospace yazılır.

**59. Kuyruk panelindeki "Kur" düğmesinin yazısı** · değişecek · görsel · **zayıf sinyal** (Y3)
- Bugün: kuyruk beklerken çıkan düğme "Video üreticisini kur" der.
- Tasarım v4'te: düğme her yerde yalnız "Kur" der.

### Galeri

**60. Sahiplik rozetleri sağ alttan sol alta taşınıyor** · değişecek · görsel · **kesin** (Y1 Y2 Y3)
- Bugün: videosu olan bir kare üretilip galeriye düşünce rozet karonun sağ alt köşesinde belirir.
- Tasarım v4'te: aynı kare düşünce rozet sol alt köşede belirir; sağ alt bilerek boş kalır ve dört
  köşe birbirine hiç girmez.

**61. Rozetlerden ikon kalkıyor** · değişecek · görsel · **kesin** (Y1 Y2 Y3)
- Bugün: video üretilip kare tamamlanınca rozette küçük bir oynat işareti ile "video" yan yana
  çıkar; ses üretilince de dalga işaretiyle "ses" birlikte çıkar.
- Tasarım v4'te: rozet yalnız kelimeyi yazar — ikon hiç doğmaz.

**62. Her rozet kendi kutusunu taşıyor** · değişecek · görsel · **güçlü** (Y2 Y3)
- Bugün: videosu ve sesi olan karede iki kelime tek bir koyu kutunun içine yan yana dizilir.
- Tasarım v4'te: her katman kendi kutusunu taşır — iki ayrı rozet, aralarında ince bir boşlukla.

**63. Loop rozeti** · eklenecek · görsel · **kesin** (Y1 Y2 Y3)
- Bugün: bugün yok — loop diye bir kavram olmadığı için loop videolu kare öteki videolu karelerle
  aynı rozeti taşır.
- Tasarım v4'te: loop modunda üretilmiş videosu olan kare sol altta "video" yerine "loop" yazar;
  ikisi aynı yeri paylaşır, bir arada asla görünmez. Sesi de varsa yanına "ses" eklenir.

**64. İkinci bekleyen katmanın hapı** · değişecek · görsel · **kesin** (Y1 Y2 Y3)
- Bugün: bir karenin hem videosu hem sesi kuyruğa girince karoda tek bir durum hapı görünür,
  ikincisi hiç çıkmaz.
- Tasarım v4'te: iki katmanı birden bekleyen karede ikinci hap birincinin altına dizilir, ikisi
  birlikte okunur.

**65. Bekleyen hapının rengi ve ölçüsü** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: bekleyen kareye ait hap parlak tonda yazılır, zemini daha opak ve iç boşluğu dardır.
- Tasarım v4'te: aynı hap soluk tonda yazılır, zemini biraz daha saydam ve iç boşluğu genişçedir.

**66. Hapta "bekliyor" sözcüğü** · öksüz · görsel · **güçlü** (Y2 Y3)
- Bugün: kuyruk akmıyorken bekleyen katmanın hapı "kuyrukta" yerine "bekliyor" yazar.
- Tasarım v4'te: karşılığı yok — kart hapının yalnız üç değeri var: kuyrukta, üretiliyor, hata.

**67. Boş galerinin metni** · değişecek · görsel · **güçlü** (Y2 Y3)
- Bugün: projede hiç kare yokken "henüz kare yok" ve altında "Prompt'ları yaz, Kuyruğa ekle'ye
  bas — kareler burada belirecek" okunur.
- Tasarım v4'te: aynı yerde "henüz fotoğraf yok" ve "…fotoğraflar burada belirecek" okunur.
- Not: 7. maddedeki terminoloji çelişkisinin ikinci yüzü — kural "kare" derken çizim "fotoğraf"
  diyor.

**68. Galeri yüklenirken** · öksüz · görsel · **zayıf sinyal** (Y2)
- Bugün: proje açılınca kare listesi gelene kadar galerinin ortasında dönen bir gösterge görünür.
- Tasarım v4'te: karşılığı yok.

**69. Sürükleme basılı tutmayla başlıyor** · değişecek · davranış · **zayıf sinyal** (Y2)
- Bugün: karta basar basmaz sürükleme başlar.
- Tasarım v4'te: kart basılı tutulup sonra sürüklenince sıra değişir.

**70. Çoklu seçim tek parça sürükleniyor** · eklenecek · davranış · **kesin** (Y1 Y2 Y3)
- Bugün: üç kare seçiliyken biri sürüklenmeye çalışılınca hiçbir şey kalkmaz — seçim varken
  sürükleme kapalıdır; seçimi bozup kartları tek tek taşımak gerekir ve aralarındaki sıra bozulur.
- Tasarım v4'te: seçili bir kart sürüklenince seçili kartların hepsi aynı anda "sürükleniyor"
  görünümüne geçer, bırakıldıkları yere bitişik bir blok olarak iner ve kendi aralarındaki sıra
  korunur. Seçili olmayan bir kart sürüklenirse yalnız o gider ve seçim bozulmaz.

**71. Toplu taşımaya yeni bir öğe eklenmiyor** · eklenecek · görsel · **güçlü** (Y1 Y3)
- Bugün: bugün yok.
- Tasarım v4'te: sayı rozeti, yığın görüntüsü ve özel sürükleme imgesi doğmaz; bırakma yuvası
  göstergesi de değişmez — bugünkü tek kart efekti olduğu gibi seçimin tamamına uygulanır.

**72. Dağınık seçim bırakıldığı yerde toplanıyor** · eklenecek · davranış · **güçlü** (Y1 Y3)
- Bugün: bugün yok.
- Tasarım v4'te: dağınık seçim (örneğin 3, 7 ve 9) bırakıldığı yerde yan yana gelir, kendi
  aralarındaki sıra korunur ve aralarında kalan kartlar boşluğu kapatır.

**73. Hover'da numaranın gizlenmesi** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: seçim açıkken numara gizlenir ama fare bir kartın üstündeyken görünmeye devam eder.
- Tasarım v4'te: fare bir kartın üstündeyken de numara kalkar, yerini o kartın kendi eylemi alır.

**74. Bekleyen kare bırakıldığı yerden üretiliyor** · değişecek · davranış · **zayıf sinyal** (Y2)
- Bugün: bekleyen kare araya taşınınca yeni sıra kaydedilir, ama kartın durumu değişmez.
- Tasarım v4'te: bırakma anında kart bekleyenden çalışana döner ve üretim oradan sürer.

**75. Hatalı katmanın üstündeki perde** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: fotoğrafı duran ama katmanı patlamış karenin üstüne fare gelince saf siyah tonunda bir
  perde iner.
- Tasarım v4'te: perde koyu kahve-siyah tonuna döner ve altındaki "Tekrar dene" düğmesi kart zemini
  renginde durur.

**76. Karışık seçim silme onayının alt satırı** · değişecek · görsel · **zayıf sinyal** (Y3)
- Bugün: karışık seçimde onay penceresi yalnız başlığı gösterir, altında açıklama doğmaz.
- Tasarım v4'te: başlığın altında "Kareler videosu ve sesiyle birlikte kalıcı olarak silinir — bu
  geri alınamaz. Bekleyen kareler üretilmeden kuyruktan çıkar." satırı durur.

### Seçim barı ve toplu eylemler

**77. Kopyala düğmesi ve Ctrl + D** · eklenecek · davranış · **kesin** (Y1 Y2 Y3)
- Bugün: bugün yok.
- Tasarım v4'te: bir kare seçilip bardaki "Kopyala"ya (Sil'in solunda, çerçevesiz) ya da Ctrl + D'ye
  basınca kartın birebir ikizi doğar — fotoğraf, video, ses ve bilgiler gelir, üretilecek bir şey
  kalmaz. Kopya kaynağın bir üstüne iner ve seçim kopyaya geçer; fark ediliş budur, ayrı bildirim
  yok. İkinci kez basınca kopyanın kopyası doğar.

**78. Kopya karenin adı** · eklenecek · davranış · **güçlü** (Y1 Y3)
- Bugün: bugün yok.
- Tasarım v4'te: kopya öneki adın **başına** gelir — P11_1 kopyalanınca C1_P11_1 olur; sonda olsaydı
  katman kuyruklarıyla karışırdı. Dosyalar kaynakla paylaşılır, ikizden birini silmek öbürünü
  bozmaz.

**79. Kopyala düğmesinin seçime göre görünmesi** · eklenecek · davranış · **güçlü** (Y1 Y3)
- Bugün: bugün yok.
- Tasarım v4'te: seçim yalnız bekleyen karelerden oluşuyorsa "Kopyala" barda hiç doğmaz; karışık
  seçimde durur, basılınca yalnız üretilmiş kareler çoğalır ve sayı buna göre yazılır.

**80. Videoları sil ve Sesleri sil** · eklenecek · davranış · **kesin** (Y1 Y2 Y3)
- Bugün: barda yalnız "Sil" vardır; videoları toplu kaldırmak için kareler tek tek detay sayfasında
  açılıp orada silinmek zorundadır.
- Tasarım v4'te: barda "Sil"in yanında "Videoları sil" ve "Sesleri sil" durur — üçü de dolgusuz
  kırmızı ve çöp ikonlu. Birine basınca onay açılır ("9 karenin videosu silinsin mi? Kareler ve
  fotoğrafları kalır. Videoya bindirilen sesler de gider.") ve onaylanınca kareler yerinde kalır,
  yalnız katman düşer.

**81. Toplu katman silmede atlanan kareler** · eklenecek · davranış · **güçlü** (Y1 Y3)
- Bugün: bugün yok.
- Tasarım v4'te: seçili karelerin bazısında o katman yoksa atlanır ve onay metni bunu tek cümlede
  söyler — "12 seçili kareden videosu olmayan 3'ü atlanır."; başlıktaki sayı yalnız katmanı olan
  kareyi sayar.

**82. Barın seçime göre küçülmesi** · eklenecek · davranış · **zayıf sinyal** (Y2)
- Bugün: seçimin içeriği ne olursa olsun bardaki düğmeler aynı kalır.
- Tasarım v4'te: seçimde bekleyen kare varsa "Videoları sil" ve "Sesleri sil" barda hiç çizilmez;
  yalnız bekleyen seçiminde geriye "Tümünü seç · Sil · Vazgeç" kalır.

**83. Barın boşluğu ve sarmaması** · değişecek · görsel · **kesin** (Y1 Y2 Y3)
- Bugün: bar açılınca öğeler arasında 14px boşluk kalır ve bar sarmaya açıktır.
- Tasarım v4'te: boşluk 10px'e iner ve bar hiç sarmaz — buton yazıları asla iki satıra düşmez.

**84. Barın konumu** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: bar galerinin alt kenarından 28px yukarıda durur.
- Tasarım v4'te: bar alt kenardan 20px yukarıda ortalanır.

### Detay sayfası

**85. Katman sekmeleri ayrılıyor** · değişecek · görsel · **kesin** (Y1 Y2 Y3)
- Bugün: bir kare açılınca üstteki Foto · Video · Ses sekmeleri uç uca yapışık tek bir parça gibi
  okunur.
- Tasarım v4'te: sekmelerin arasına 8px boşluk girer ve her biri kendi köşe yarıçapıyla üç ayrı
  sekme gibi okunur; açık sekme yalnız rengiyle belli olur, ek işaret yoktur. Karenin sahip olmadığı
  katmanın sekmesi pasif kalır, gizlenmez.

**86. Dosya adı satırları kalkıyor** · değişecek · görsel · **kesin** (Y1 Y2 Y3)
- Bugün: foto sekmesinde sağ sütunda Sıra'nın yanında "Dosya adı" satırı çıkar (üretilmemişse "Dosya
  adı (planlanan)"); sekme değiştikçe alt katmanların dosya adları da eklenir.
- Tasarım v4'te: hangi sekme açılırsa açılsın üst grupta yalnız Sıra durur; hiçbir sekmede dosya adı
  satırı doğmaz.

**87. Her sekme yalnız kendi katmanının prompt'unu gösteriyor** · değişecek · davranış · **güçlü**
  (Y1 Y3)
- Bugün: video sekmesine geçilince video prompt'unun altında fotoğrafın prompt'u da salt okunur bir
  kutuda görünür; ses sekmesinde ses prompt'unun altında video prompt'u da açılır.
- Tasarım v4'te: açık sekme yalnız kendi katmanının prompt'unu gösterir; alt katmanların prompt'ları
  hiç doğmaz. ("Bu katman neyden yapıldı görünsün" kararı geri alındı.)

**88. Prompt etiketleri katmanını söylüyor** · değişecek · görsel · **kesin** (Y1 Y2 Y3)
- Bugün: hangi sekme açık olursa olsun kutunun başlığı "Prompt", ikincisi "Negatif" der.
- Tasarım v4'te: foto sekmesinde "FOTO PROMPT'U" ve "FOTO NEGATİF PROMPT'U", video sekmesinde
  "VİDEO PROMPT'U", ses sekmesinde "SES PROMPT'U" — etiket hangi katmanı okuduğunu söyler.

**89. Prompt kutuları sabit yüksekliğe geçiyor** · değişecek · görsel · **kesin** (Y1 Y2 Y3)
- Bugün: pencere boyu değişince prompt ve negatif kutuları esneyip kalan alanı aralarında paylaşır;
  kısa bir pencerede ikisi de daralır.
- Tasarım v4'te: kutular sabit yükseklikte durur (öncekinden yarı yarıya büyük: foto prompt'u 162px,
  foto negatifi 96px, video ve ses prompt'ları 150px) ve metin taşarsa kutunun kendi içinde
  kaydırılır — panel uzayıp altındaki butonları aşağı itmez.

**90. Prompt başlığında kopyala ikonu** · eklenecek · davranış · **kesin** (Y1 Y2 Y3)
- Bugün: bugün yok.
- Tasarım v4'te: her prompt başlığının sağındaki kopyala ikonuna basınca o kutunun metni panoya
  alınır.

**91. Sağ panelin iki grubu ve dikey ritmi** · değişecek · görsel · **güçlü** (Y1 Y3)
- Bugün: sağ sütun tek bir akıştır; bloklar arası 14px, etiketle değeri arası 4px, etiketle kutu
  arası 6px — üç ayrı ölçü.
- Tasarım v4'te: sütun iki gruba ayrılır — üstte salt bilgi, altta üretim — ikisi de yukarıdan
  hizalıdır ve aralarında ne grup başlığı ne ayraç vardır. Tek dikey ritim kalır: bloklar arası
  16px, etiket-kutu arası 6px.

**92. Kuyrukta bekleyen katmanın prompt kutusu** · değişecek · görsel · **kesin** (Y1 Y2 Y3)
- Bugün: videosu kuyrukta bekleyen karenin video sekmesi açılınca kutunun içinde sola dayalı, silik
  bir "üretim sırası gelince LLM yazacak" satırı görünür.
- Tasarım v4'te: aynı kutuda ortalanmış tek satır durur — "Prompt yok — üretim sırası geldiğinde
  eklenecek." Kutu asla tamamen boş bırakılmaz, kullanıcı prompt'un silindiğini sanmasın diye.

**93. Video sekmesinde "Üretim modu" satırı** · eklenecek · görsel · **kesin** (Y1 Y2 Y3)
- Bugün: bugün yok.
- Tasarım v4'te: videolu bir karenin video sekmesinde sağ sütunda "Üretim modu" satırı durur ve bu
  videonun modunu salt bilgi olarak yazar — tıklanmaz, değişmez. Bağlı modda hedefi kare numarasıyla
  değil dosya adıyla söyler ("Sonrakine bağla → P11_4.png"), çünkü sıra değişince numara yalan olur.
  Satır ses sekmesinde hiç doğmaz.

**94. Yeniden üret formunda "Yeni mod" seçicisi** · eklenecek · davranış · **kesin** (Y1 Y2 Y3)
- Bugün: video sekmesinde prompt değiştirilip yeniden üretilince yeni kare, hangi modda üretileceği
  sorulmadan kuyruğa girer.
- Tasarım v4'te: formda "Yeni mod" seçicisi durur ve varsayılanı bu videonun modudur — kullanıcı
  yalnız prompt'u değiştirip basarsa mod kendiliğinden korunur. Mod değişince kutu vurgu rengine
  döner.

**95. Son karede "Sonrakine bağla" geçersiz** · eklenecek · davranış · **kesin** (Y1 Y2 Y3)
- Bugün: bugün yok.
- Tasarım v4'te: dizinin son karesinde yeni mod olarak "Sonrakine bağla" seçilebilir, ama seçilince
  kutu kırmızıya döner, altında "Bu son kare — bağlanacak sonraki kare yok." yazar ve yeniden üret
  pasifleşir. (Seçeneği baştan pasif yapmak da, basıldıktan sonra hata vermek de açıkça reddedildi.)

**96. Yeniden üretin ne doğuracağını söyleyen satır** · eklenecek · görsel · **güçlü** (Y2 Y3)
- Bugün: yeniden üret düğmesinin altında hiçbir açıklama satırı yoktur.
- Tasarım v4'te: düğmelerin altında moda göre değişen tek satır yazar — "Yeni bir kare açılır — P11_3
  kopyası, loop video."

**97. İzleme moda uyuyor** · değişecek · davranış · **güçlü** (Y1 Y3)
- Bugün: oynat'a basılınca video hangi modda üretilmiş olursa olsun kesintisiz döner ve
  kendiliğinden durmaz.
- Tasarım v4'te: loop videosu kesintisiz döner; standart video bir kez oynar ve ilk karesinde durur;
  bağlı video bir kez oynar ve biterken sonraki karenin fotoğrafını gösterir.

**98. Negatif prompt düzenlenebiliyor** · değişecek · davranış · **zayıf sinyal** (Y3)
- Bugün: foto sekmesindeki negatif prompt salt okunur bir kutuda durur.
- Tasarım v4'te: negatif de prompt gibi düzenlenir ve düzenlenince kutu vurgu rengine döner.

**99. Kuyruktan çıkarmanın üç ayrı metni** · değişecek · görsel · **güçlü** (Y2 Y3)
- Bugün: kuyrukta bekleyen bir katmanın detayında düğme her durumda "Kuyruktan çıkar" der — üstelik
  bu düğme yalnız foto sekmesinde vardır, video ve ses sekmelerinde hiç doğmaz.
- Tasarım v4'te: düğme sekmede durur ve duruma göre üç ayrı metin taşır: kopya kare için "Kuyruktan
  çıkar", karenin kendi katmanı için "Kuyruktan çıkar — kare kalır", hatalı katman için "Kareyi
  sil".

**100. Hatalı katman sekmesinde ikinci yol** · eklenecek · davranış · **zayıf sinyal** (Y3)
- Bugün: katman hata aldığında sekmede yalnız "Tekrar dene" çıkar, ikinci bir yol yoktur.
- Tasarım v4'te: "Tekrar dene"nin yanında "Kareyi sil" durur — videosuz kopya anlamsız kalacağı için
  ikinci yol budur.

**101. Katman silme onayında dosya adı** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: videoyu sil onayında "Bu video ve üzerindeki ses kalıcı olarak silinir…" okunur.
- Tasarım v4'te: silinecek şey adıyla anılır — "P11_3_V1_0.mp4 ve üzerindeki ses kalıcı olarak
  silinir…"

**102. Tek kare silme onayının başlığı** · değişecek · görsel · **zayıf sinyal** (Y3)
- Bugün: detaydan silerken onay başlığı "Bu kare silinsin mi?" der.
- Tasarım v4'te: başlık kareyi sayar — "1 kare silinsin mi?" — seçim barından açılan pencereyle aynı
  dil.

**103. Sekme şeridinin ve sahnenin üst boşluğu** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: sahnenin iç boşluğu her yönde eşit, şerit üstten 16px aşağıdadır.
- Tasarım v4'te: sahne üstten belirgin biçimde daha ferah başlar, yanlarda ve altta aynı kalır;
  şerit üstten 12px aşağıda durur.

**104. Dizinin ucundaki oklar** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: ilk ya da son kareye gelince o yöndeki ok soluklaşır ve tıklanmaz olur.
- Tasarım v4'te: oklar her karede tam opaklıkta ve tıklanabilir durur.
- Not: tasarım dizinin ucunda oka basılınca ne olacağını söylemiyor.

**105. Üretilmemiş karenin sahnedeki yazısı** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: kesikli kutunun içinde "bekliyor" ve altında "henüz üretilmedi" aynı ölçüde okunur.
- Tasarım v4'te: "bekliyor" monospace ve büyükçe, "henüz üretilmedi" belirgin biçimde küçük ve daha
  soluk olur — iki satır arasında açık bir kademe vardır.

**106. Hatalı karenin sahnedeki metni** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: "Bu kare üretilemedi" monospace, altındaki sebep normal yazıyla okunur.
- Tasarım v4'te: başlık normal yazıyla ve bir punto büyük, sebep monospace ve küçük olur — bugünkü
  düzenin tam tersi.

**107. Kuyruğa girdi hapında canlı nokta** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: yeniden üret'e basılınca sol üstte "yeniden üretilecek — kuyrukta" hapı belirir, yanında
  nokta yoktur.
- Tasarım v4'te: aynı hapın solunda nabız atan bir nokta durur ve hap fotoğrafın biraz içine iner.

**108. Tekrar denendi hapının metni** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: hatalı katmanda "Tekrar dene"ye basılınca sol üstte "yeniden üretilecek — kuyrukta" okunur.
- Tasarım v4'te: aynı yerde "kuyrukta — tekrar denenecek" okunur.

**109. Hatalı katmanın düğme metni** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: hatalı katmanın düğmesinde "Tekrar dene" okunur.
- Tasarım v4'te: "Tekrar dene — bu kareye" okunur — yeni kare açmadığını düğmenin kendisi söyler.

**110. Yeniden üret düğmesinin boyu** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: "Yeniden üret — yeni kare" düğmesi küçük boy çizilir.
- Tasarım v4'te: tam boy ve vurgu renginde dolgulu çizilir; altındaki silme düğmesi küçük boy kalır.

**111. Üretim sürerken silme düğmesinin rengi** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: kare üretilirken silme düğmesi pasifleşir ama kırmızı rengini ve çerçevesini korur.
- Tasarım v4'te: pasifleşirken kırmızıyı bırakır ve nötr çerçeveye döner.

**112. Kuyruktaki kopya karede sekme şeridi** · değişecek · davranış · **zayıf sinyal** (Y2)
- Bugün: videosu kuyrukta bekleyen kopya karenin detayında da Foto · Video · Ses şeridi çizilir.
- Tasarım v4'te: şerit hiç çizilmez; sahnede kaynağın fotoğrafı "kaynak foto · kopya kare"
  etiketiyle durur.

**113. Katman üretilirken sahnenin görünümü** · değişecek · davranış · **zayıf sinyal** (Y2)
- Bugün: videosu üretilen karenin detayında sahne boşalır ve yerine dönen göstergeli bir yer tutucu
  gelir.
- Tasarım v4'te: sahnede kaynak fotoğraf durmayı sürdürür, üstüne ortalanmış koyu bir kutu iner ve
  içinde nabız atan nokta ile "video üretiliyor…" okunur.

**114. Oynatıcı çubuğunun yeri** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: zaman etiketleri ve ilerleme çizgisi videonun altında, ayrı ve çerçeveli bir satırda durur.
- Tasarım v4'te: ikisi de videonun içine, alt kenarın biraz yukarısına iner; çizgi çerçevesiz ve
  vurgu renginde dolar.

**115. Dalga çubuklarının boş kısmı** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: ses sekmesinde dalga videonun altında ayrı çizilir ve çalınmamış çubuklar en soluk metin
  tonundadır.
- Tasarım v4'te: dalga videonun içine girer, alçalır ve çalınmamış çubuklar saydam beyaza döner.

**116. Oynat düğmesinin çerçevesi** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: sahnenin ortasındaki yuvarlak oynat düğmesi çerçevesizdir ve içindeki işaret metin
  karakteridir.
- Tasarım v4'te: düğme ince bir çerçeve taşır, zemini biraz daha opaktır ve içindeki işaret çizimdir.

**117. Detaydaki prompt kutusunun yazı tipi** · düzeltilecek · görsel · **zayıf sinyal** (Y1)
- Bugün: üretim panelinde prompt listesi monospace görünürken, aynı prompt detay sayfasında normal
  arayüz yazısıyla görünür — iki ekranda aynı metin iki ayrı yazıyla okunur.
- Tarifi neydi: görsel dil kuralı "dosya adları, sayılar, prompt kutusu ve küçük alan etiketleri
  monospace" diyordu; prompt kutusu nerede olursa olsun monospace olacaktı.

**118. Detayın yükleme ve bulunamadı halleri** · öksüz · görsel · **güçlü** (Y2 Y3)
- Bugün: kare listesi okunurken sahnenin ortasında dönen bir gösterge, adres hiçbir kareye denk
  gelmiyorsa "Kare bulunamadı" kartı çıkar.
- Tasarım v4'te: karşılığı yok.

**119. Reddedilen istek kartları** · öksüz · görsel · **zayıf sinyal** (Y3)
- Bugün: silme, katman silme veya yeniden üretme isteği reddedilirse sağ sütunda "Kare silinemedi" /
  "Video silinemedi" gibi başlıklı, altında ham cevabı açan bir kart belirir.
- Tasarım v4'te: karşılığı yok.
- Not: tasarım detayda yalnız üretim hatasını anlatıyor, bir isteğin reddedilmesini anlatmıyor.

### Export ekranı

**120. Özet kartının ölçüleri** · değişecek · görsel · **güçlü** (Y2 Y3)
- Bugün: özet kartı dar bir iç boşlukla, sütun geniş blok aralıklarıyla ve sayfa üstten sabit bir
  boşlukla çizilir.
- Tasarım v4'te: kart daha ferah bir iç boşluk alır, kart içindeki bloklar sıkışır, sütundaki
  bloklar arası daralır ve sütunun tamamı dikeyde biraz yukarı kayar.

**121. Özet satırındaki sayının biçimi** · değişecek · görsel · **güçlü** (Y2 Y3)
- Bugün: "22 video export edilecek · 1:50 dk" tek parça hâlinde tek ölçüde okunur.
- Tasarım v4'te: "22 video export edilecek" monospace ve büyük, "· 1:50 dk" belirgin biçimde küçük
  ve soluk okunur — iki ayrı ölçü.

**122. Hedef klasör satırının tonu** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: "Şuraya yazılacak:" satırı büyükçe ve orta tonda, altındaki yol küçük ve soluk okunur.
- Tasarım v4'te: tam tersi — başlık küçülüp soluklaşır, yol biraz büyür ve parlaklaşır.

**123. Export düğmelerinin ölçüsü** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: iki düğme eşit sütunlu bir ızgarada, standart düğme yüksekliğinde durur.
- Tasarım v4'te: düğmeler yan yana, aralarında biraz daha boşlukla ve belirgin biçimde daha kalın —
  yazısı da bir punto büyük.

**124. Bitiş kartının dizilimi ve dosya satırı** · değişecek · görsel · **güçlü** (Y2 Y3)
- Bugün: export bitince alt alta iki satır çıkar ve alt satır basılan düğmenin adını tekrar eder
  ("Birleşik videoyu export et → <hedef>").
- Tasarım v4'te: tek satırda yan yana üç parça çıkar — onay işareti, "Export tamamlandı" ve yazılan
  dosyanın **kendi adı** ile hedefi ("dugun.mp4 → düğün / export / 2026-08-11 14-32 /").

**125. Bitiş kartının yeşili** · düzeltilecek · görsel · **güçlü** (Y2 Y3)
- Bugün: yeşil kart temanın kendi başarı rengini değil, doğrudan yazılmış ayrı bir yeşili kullanır.
- Tarifi neydi: başarı rengi temanın kendi değişkenidir; uygulamadaki bütün yeşiller aynı tonu
  kullanacaktı.

**126. Hata kartının biçimi** · değişecek · görsel · **güçlü** (Y2 Y3)
- Bugün: "Export başarısız" ikonsuz yazılır, sebep altında orta tonda okunur.
- Tasarım v4'te: kartın başında üçgen uyarı ikonu durur, başlık bir punto büyür ve tek satır teknik
  sebep monospace ve en soluk tonda okunur.

**127. Çıkış onayının düğme metni** · değişecek · görsel · **güçlü** (Y2 Y3)
- Bugün: export sürerken çıkışa basınca açılan onayın sağ düğmesi yalnız "Çık" der.
- Tasarım v4'te: düğme "Çık — export iptal" der.

**128. Üretim sürerken uyarı kartının ölçüsü** · değişecek · görsel · **zayıf sinyal** (Y2)
- Bugün: kuyruk akarken düğmelerin üstünde eşit iç boşluklu kırmızı bir kart çıkar.
- Tasarım v4'te: aynı kart yanlardan daha geniş, dikeyde daha dar bir iç boşluk alır ve üstünde ayrı
  bir boşluk bırakır.

**129. Birleşik export sürerken buton yazısı** · değişecek · görsel · **zayıf sinyal** (Y3)
- Bugün: birleşik export'a basılınca buton önce "7 / 22 yazıldı…" diye sayar, ancak parçalar
  bittikten sonra "birleştiriliyor…" der.
- Tasarım v4'te: birleşik butonu çalışırken yalnız canlı nokta ve "birleştiriliyor…" gösterir; sayaç
  ayrı export butonunun dilidir.

**130. Birleşik export'un bıraktığı dosyalar** · değişecek · davranış · **zayıf sinyal** (Y3)
- Bugün: birleşik export da klasöre önce numaralı parçaları yazar ve birleştirdikten sonra bunları
  silmez.
- Tasarım v4'te: birleşik export'un çıktısı proje adıyla tek dosyadır; numaralı dosyalar ayrı
  export'un çıktısıdır.
- Not: tasarım iki export aynı klasöre yazınca ne olacağını anlatıyor ama birleşik export'un tek
  başına ne bırakacağını açıkça söylemiyor.

**131. Export klasörünün adı** · düzeltilecek · davranış · **zayıf sinyal** (Y3)
- Bugün: klasörün adı her basışta o anki dakikadan üretilir — iki export farklı dakikalara denk
  gelirse ayrı klasörlere yazar.
- Tarifi neydi: iki export aynı tarih klasörüne yazacaktı; yeni tarih klasörünü açan şey yeni bir
  Export **açılışı**, basış değil.

**132. Export özeti okunamayınca** · öksüz · görsel · **güçlü** (Y2 Y3)
- Bugün: özet gelmezse "Export özeti yüklenemedi" kartı çıkar ve altında ham cevap açılabilir.
- Tasarım v4'te: karşılığı yok.

### Adlandırma ve kimlik

**133. Yeniden üretim tur numarasını artırmıyor** · düzeltilecek · davranış · **zayıf sinyal** (Y3)
- Bugün: bir katman yeniden üretilince doğan kare her zaman o katmanın birinci turunu ve sıfırıncı
  varyantını alır; tur numarası hiç büyümez.
- Tarifi neydi: yeniden üretim turu artıracaktı — prompt düzenlenip tekrar üretilince ikinci tur
  doğacak, birinci tur yerinde duracaktı; ad hangi sonucun hangi turdan geldiğini taşıyacaktı.
- Not: uygulamanın kendi kaydı bu davranışı bilerek seçtiğini ve gerekçesini ("ikinci deneme yeni
  bir karedir, o da kendi ilk turudur") yazıyor. İki ifade de burada, karar verilmedi.

**134. Varyantlar aynı karenin adı altında sıralanmıyor** · düzeltilecek · davranış ·
  **zayıf sinyal** (Y3)
- Bugün: üç varyant istenince kaynak kare birinci varyantı alır, kalan ikisi yeni fotoğraf varyant
  numaralarıyla ayrı kimlikler doğurur ve adları o yeni kimlikten türer.
- Tarifi neydi: üç varyant aynı karenin adından türeyecekti — üçü ayrı karedir ama fotoğraf dosyası
  ortaktır.

### Uygulama geneli

**135. "Galeriye dön" butonundaki ok** · değişecek · görsel · **güçlü** (Y1 Y3)
- Bugün: detay sayfasında ve export ekranında "Galeriye dön" butonunun solunda bir ok ikonu durur.
- Tasarım v4'te: buton yalnız yazıyla görünür; ok kaldırıldı.

**136. Ham çıktının açılabildiği hata kartları** · öksüz · görsel · **güçlü** (Y2 Y3)
- Bugün: birçok yerde tek cümlelik hata başlığının altında, açılıp kapanabilen ham sunucu ya da
  tarayıcı çıktısı durur.
- Tasarım v4'te: karşılığı yok — tasarım sebep için her yerde "tek satır teknik dil" diyor, açılır
  bir ham çıktı alanından hiç söz etmiyor.

---

## 3 · Brif ne dedi, tasarım ne yaptı

Bu maddeler repo ile tasarım arasındaki fark **değildir** — ikisinde de karşılığı yoktur. Burada
durmalarının sebebi, kullanıcının 20 Ağustos brifinde **"Karar verildi"** diyerek verdiği kararların
tasarımca geri alınmış olmasıdır. Brifin "karar sende" dediği konular listeye girmedi: tasarımcıya
bırakılmış bir soruya tasarımın cevap vermesi beklenen şeydir.

Hangisinin doğru olduğu söylenmiyor.

**1. Mod seçimi kartın üstünde yapılır**
- Brifin kararı: loop / sonrakine bağla seçimi kartın üstünde yapılacak; her kart üç durumdan
  birinde duracak.
- Tasarımın yerine koyduğu: kart üstüne hover'da beliren mod şeridini bir kez denedi, sonra tamamen
  kaldırdı; seçimi video üret panelindeki "Üretim modu" satırına taşıdı.
- Tasarımın gerekçesi: işaretleme üretim başlatmadığı için kullanıcı geri bildirimsiz söz veriyor ve
  iş iki adıma çıkıyor; mod bir üretim parametresidir (model, kapsam, varyant gibi), karenin kalıcı
  niteliği değil.

**2. Seçim üretimi başlatmaz — kart işaretlenir, toplu üretime kadar bekler**
- Brifin kararı: kart işaretlenecek, üretim toplu üretime kadar bekleyecek.
- Tasarımın yerine koyduğu: işaretleme kavramını tümden bıraktı; mod yalnız üretim anında, kuyruğa
  eklenirken verilir ve kuyruğa giren işe yazılır.
- Tasarımın gerekçesi: videosu olmayan karede "gelecekte loop olacak" diye bir hayalet durum
  kalıyor; sıra değişince ya da kare silinince o işaret anlamsızlaşıyor.

**3. Kart hangi modda olduğunu ikonla gösterir**
- Brifin kararı: kart, modunu ikonla gösterecek.
- Tasarımın yerine koyduğu: kart üstündeki mod göstergesini bütünüyle kaldırdı; modu yalnız
  üretilmiş videonun sahiplik rozetinde ve yalnız kelimeyle söylüyor ("loop"). Üstelik rozetlerdeki
  mevcut ikonları da attı.
- Tasarımın gerekçesi: iki soyut ikonu 22px'te birbirinden ayırmak tahmin gerektiriyor; kelime
  varken ikon süs.
- Not: brifin "hangi ikonlarla gösterilir" sorusu "karar sende" başlığındaydı, ama "ikonla gösterir"
  kararının kendisi "Karar verildi" başlığı altındadır. Geri alınan, kararın kendisidir.

**4. Sonrakisi olmayan karede üretim engellenmez**
- Brifin kararı: "sonrakine bağla" işaretli kartın sonrakisi yoksa üretim engellenmeyecek — o kare
  kuyruğa girmeyecek, diğerleri girecek; panel bunu tek satırla söyleyip durum sürdüğü sürece orada
  tutacak.
- Tasarımın yerine koyduğu: iki yerde de engelledi — panelde seçim ardışık değilse seçenek pasif
  olur, detayda son karede seçilirse kutu kırmızıya döner ve yeniden üret pasifleşir.
- Tasarımın gerekçesi: panel tarafında "sessizce garip sonuç üretmesin"; detay tarafında gerekçe
  kullanıcının kendi seçiminin altında yazsın diye seçenek açık bırakıldı ama üretim kapatıldı —
  hata tıklamadan önce görünmeli, basıldıktan sonra hata vermek reddedildi.

**5. Detayda üstte kartın adı ve sırası durur**
- Brifin kararı: üç sekmenin de üstünde kartın adı ve sırası duracak, altında yalnız o sekmenin
  prompt'u olacak.
- Tasarımın yerine koyduğu: üst grupta yalnız Sıra bıraktı; kare adını oradan da çıkardı.
- Tasarımın gerekçesi: kimlik zaten başlıkta duruyor, ad panelde ikinci kez yazılmıyor.

**6. Bekleyen katmanın prompt kutusu boş görünsün**
- Brifin kararı: video prompt'u sırası gelene kadar boş; kutu boş görünsün yeter, ayrı bir boş sayfa
  tasarımı istenmiyor. (Brif bu maddede açıkça "senden karar beklemiyoruz" diyor.)
- Tasarımın yerine koyduğu: önce tamamen boş bıraktı, sonra vazgeçip kutunun içine ortalanmış tek
  satır koydu: "Prompt yok — üretim sırası geldiğinde eklenecek."
- Tasarımın gerekçesi: boş kutu bırakılırsa kullanıcı prompt'un silindiğini sanıyor.

**7. Video panelinde bugünkü gibi tek bir mesaj kalsın**
- Brifin kararı: iş kalmadığında bugünkü gibi tek bir mesaj kalsın, yalnız sebebe göre değişsin.
- Tasarımın yerine koyduğu: mesajın yerini değiştirdi — panel basılmadan önce tamamen sakin duruyor,
  mesaj ancak butona basınca altında yeni bir kırmızı hata kartının içinde doğuyor; buton da artık
  hiçbir eksik alan için pasifleşmiyor.
- Tasarımın gerekçesi: "silik gri metin + kilitli buton" kalıbında kullanıcı neden basamadığını
  anlamıyordu; hata kartı yeşil onay kartının kırmızı ikizi olarak kuruldu. (Cümlenin sonundaki
  "— üretilecek bir şey yok" kuyruğunun atılması brifin istediği yönde.)

---

## 4 · Tasarımın cevaplamadıkları

Aşağıdaki konularda tasarım v4 bir şey söylemiyor. Hiçbiri uydurulmadı; her biri ilgili fark
maddesinin içinde de not olarak duruyor, burada tek yerde toplandı ki karar verilmesi gereken açık
uçlar görünsün.

1. **Ad doğrulaması ne zaman yapılır?** Tasarım uyarının nerede çıkacağını söylüyor, kontrolün
   yazarken mi yoksa kaydederken mi yapılacağını söylemiyor. → madde 11
2. **Çıkış bilgi balonu neyle açılır, nasıl kapanır?** Balonun yeri çizilmiş, tetiği ve kapanışı
   çizilmemiş. → madde 14
3. **Birleşik export tek başına ne bırakır?** İki export aynı klasöre yazınca ne olacağı anlatılmış;
   birleşik export'un ara dosyaları bırakıp bırakmayacağı anlatılmamış. → madde 130

Bu bölümde dördüncü bir madde daha vardı — dizinin ucundaki oka basılınca ne olacağı. Elle
doğrulamada düştü: tasarım bunu **söylüyor**, ekran notlarının foto detay bölümü "oklar ilk/son
karede pasif, sarmaz" diyor ve bugünkü uygulama zaten böyle. Yol 2 "tasarım söylemiyor" diye
işaretlemişti çünkü yalnız çizimi görüyordu; çizimde oklar koşulsuz tıklanabilir duruyor. Madde 104
de bu yüzden düştü.

Ayrıca tasarımın kendi kaynakları dört yerde birbirini tutmuyor; bunlar "cevaplanmamış" değil,
"iki ayrı cevap verilmiş" durumudur ve fark listesinde **çelişki** damgasıyla duruyorlar:

- Proje kartındaki silme düğmesinin görünümü — yıkıcı eylem standardı mı, iki ikon düğme mi
  (madde 5)
- Kuyruk panelinde tür kartlarıyla durum kartının bir arada durup durmayacağı (madde 40)
- Kuyruğu boşalt onayının buton yazısı — "Çıkar" mı, "Boşalt" mı (madde 49)
- Boş ekran metinlerinde "kare" mi, "fotoğraf" mı (madde 7 ve 67)

Bunlara ek olarak üç yerde çelişki tasarımla uygulama arasında değil, **tasarımla uygulamanın kendi
yazılı kararları** arasındadır: kurulumun sorumlusu (madde 52), açılışta kuyruğun kendiliğinden
sürmesi (madde 36) ve yeniden üretimin tur numarası (madde 133). Üçünde de uygulama tarafı kararını
gerekçesiyle birlikte kendi içinde kayda geçirmiş.

---

## 5 · Verilen kararlar

2. bölüm **ne bulunduğunun** kaydıdır ve olduğu gibi durur. Bu bölüm **ne karar verildiğinin**
kaydıdır ve çakıştığı yerde 2. bölümü ezer. Kararlar 20 Ağustos 2026'da, belge okunduktan sonra
madde madde verildi.

### Tasarımın kendi içinde çeliştiği yerler

| # | Karar | Kapattığı madde |
|---|---|---|
| 1 | Proje kartındaki silme düğmesi **yıkıcı eylem standardını** kullanır: dolgusuz, kırmızı çerçeveli, çöp ikonlu. Tasarımın proje kuralları belgesindeki örnek listesi geçerlidir; ekran notlarının "iki ikon düğme" tarifi değil. | 5 |
| 2 | Kuyruk panelinde **tür kartlarıyla durum kartı bugünkü gibi bir arada durur**. Buna bağlı olarak kuyruk akarken durum kartının doğmaması da bugünkü hâliyle kalır. | 40, 39 |
| 3 | "Kuyruk boşaltılsın mı?" penceresinin butonu **"Boşalt"** kalır. Uygulama iki fiili ayrı anlamda kullanıyor: *çıkar* = seçtiklerimi kuyruktan al, *boşalt* = kuyruğun tamamını boşalt. | 49 |
| 4 | Boş ekran metinlerinde **"kare"** kalır. Çizimdeki "fotoğraf" sözcüğü, terminoloji netleşmeden önceki dilden kalmış. | 7, 67 |

### Tasarımla uygulamanın kendi kararlarının çarpıştığı yerler

| # | Karar | Kapattığı madde |
|---|---|---|
| 5 | **Kurulum defterde kalır.** Uygulama indirme yapmaz, yalnız neyin kurulu olduğunu söyler — uygulamanın temel kararı geçerlidir. Tasarımın panel içi kurulum akışının tamamı düşer. | 18, 52, 53, 54, 55, 56 |
| 6 | **Açılışta kuyruk kendiliğinden sürmez**, kullanıcı başlatır. 13 Ağustos 2026'daki karar geçerlidir; tasarımın karşı ifadesi ondan eski bir katmanda duruyor. | 36 |
| 7 | **Yeniden üretim tur numarasını artırmaz.** Sonuç yeni bir karedir ve tur numarası o karenin kendi sayacıdır. | 133 |
| 8 | Yeşil onay kartı **10 saniye** kalır. | 21 |

> Kararlar 6 ve 7 tasarımın kural metniyle çelişiyor. Tasarım tarafındaki ilgili satırlar
> güncellenmezse bir sonraki karşılaştırmada aynı çelişkiler yeniden çıkar.

### Tasarımın cevaplamadığı konular

| # | Karar | Kapattığı madde |
|---|---|---|
| 9 | Proje adı **yazarken** doğrulanır, uyarı anında belirir. Yeniden adlandırma penceresi aynı kuralı miras alır. | 11 |
| 10 | Çıkış bilgi balonu **fare düğmeye yaklaşınca** çıkar, çekilince kaybolur. | 14 |
| 12 | Birleşik export **numaralı parçaları klasörde bırakır** — bugünkü hâl. | 130 |

### Bugün var, tasarımda karşılığı yok

| # | Karar | Kapattığı madde |
|---|---|---|
| 13 | **Sekiz yükleme ve hata hâlinin hepsi kalır.** Wireframe'ler bu hâlleri çizmez; bu bir kaldırma kararı değil, çizim âdeti. | 10, 51, 57, 68, 118, 119, 132, 136 |
| 14 | Panel şeritteki ikonuna basınca **kapanabilir** — kalır. | 12 |
| 15 | Sağ panel **kendi içinde kayar** — kalır. | 17 |
| 16 | Başka projede üretim sürerken çıkan **engel kalır**. Motor tek; ayrıca yeni panel hata standardı süren işlem için butonu kilitlemeye izin veriyor. | 13 |
| 17 | Paneldeki **"Süre" bloğu kalkar**. Tasarımın panel açıklama satırlarını kaldırma gerekçesi buna da uyuyor: kural yazılı belgede duruyor, panelde yer tutmasına gerek yok. | 33 |
| 18 | Kuyruk durmuşken kart hapındaki **"bekliyor" sözcüğü kalır**. | 66 |
| 19 | Prompt listesi kutusundaki **örnek yer tutucu kalır** — kutunun liste beklediğini ancak o söylüyor. | 20 |

### Brifin geri alınan kararları

| # | Karar | Kapattığı brif maddesi |
|---|---|---|
| 20 | **Üretim modu panelde, üretim anında seçilir** — tasarım geçerli. Kartta tutulan, bayatlayabilen bir durum olmaz. Bu karar işaretleme kavramını da ortadan kaldırdığı için brifin 2. maddesi ayrıca karara bağlanmadı. | 1, 2 |
| 21 | **Rozetler yalnız kelime taşır**, ikon yok — tasarım geçerli. | 3 |
| 22 | **Bağlanacak sonraki kare yokken üretim engellenir** — tasarım geçerli. Ardışıklık bir "eksik alan" değil, seçimin kendi yapısıdır; bu yüzden 25. kararın hata dilinin istisnası olarak durur. | 4 |
| 23 | **Detayda kare adı ve sırası durur** — brif geçerli. Tasarımın "kimlik zaten başlıkta" gerekçesi tutmuyor: detay sayfasının üst şeridinin ortasında proje adı yazıyor, kare adı değil. Alt katmanların dosya adları yine de doğmaz (madde 87). Bu karar madde 86'yı kısmen tersine çevirir: karenin kendi adı kalır, kalkan yalnız alt katmanların adlarıdır. | 5 |
| 24 | Bekleyen katmanın prompt kutusunda **ortalanmış tek satır** durur — tasarım geçerli. Boş kutu bırakmak kullanıcıya prompt silinmiş gibi geliyor. | 6 |
| 25 | **Panel hata dili tasarım gibi olur:** buton hiçbir eksik alan için pasifleşmez, sebep basıldıktan sonra kırmızı hata kartında tek satır olarak doğar. Maddeler 27, 28, 29 ve 35 bu kararın parçasıdır. | 7 |

### Yol haritası kurulurken verilen ek karar

| # | Karar | Kapattığı madde |
|---|---|---|
| 26 | **İzleme moda uymaz.** Video hangi modda üretilmiş olursa olsun detayda bugünkü gibi döner — loop'a, standarda ve bağlıya özel oynatma davranışı yazılmaz. | 97 |

### Koşu sırasında verilen ek kararlar

*(21 Ağustos 2026, 13, 15, 20, 21, 22, 23, 24, 25 ve 27. madde uygulanırken.)*

| # | Karar | Kapattığı madde |
|---|---|---|
| 27 | **Seçim barı alt kenardan 28 pikselde kalır.** Tasarımın istediği 20, kullanıcının v3'te "en dibe yapışık" dediği değerin ta kendisi; 28 o bulguya (v3 madde 108) verilmiş cevaptır ve v5'in 33. görev spec'inde yazılıdır. Tasarımın 20'si tek artboard'dan gelen zayıf sinyal. Bu madde 2. bölümde `değişecek` göründüğü için 5–8'in yanına yazılmamıştı; oysa aynı istisnadır — "sapma" sanılan şey sonradan verilmiş bir karardı. | 84 |
| 28 | **Sürükleme basıştan itibaren açık kalır.** Basılı tutma 14 Ağustos'ta bir hata raporu üzerine kaldırıldı: tarayıcı bir basışın sürüklemeye dönüşüp dönüşemeyeceğine `mousedown` anında karar veriyor, dolayısıyla sonradan açılan `draggable` o basışı geri kazanmıyor ve galeri hiç sıralanamıyordu. Sebep ve ölçüsü v12'nin 2. görev spec'inde yazılı. Tutuşun asıl derdi tarayıcının kendi piksel eşiğiyle zaten karşılanıyor. | 69 |
| 29 | **Numara hover'da zaten kalkıyor.** `app.css`'teki `.qe-tile:hover .qe-badge` kuralı 13 Ağustos'ta, bu turdan bir hafta önce yazıldı; yerini de tasarımın istediği seçim halkası alıyor. Gözlem bayat, madde doğuştan kapalı. | 73 |
| 30 | **Bırakma üretim başlatmaz.** Farkın özü zaten doğru: motor her turda sırayı yeniden okuyor, yani öne çekilen bekleyen kare bırakıldığı yerden üretiliyor. Eksik olan tek şey kartın bırakma anında "üretiliyor" yazması — motor başka bir kareyi tutarken bu yalan olur, kuyruk duruyorken de 6. karara aykırı. | 74 |
| 31 | **Karışık seçim onayı yalnız başlık kalır.** Kullanıcının 12 Ağustos 2026 kararı (v3 fark listesi, madde 64): "alt satır hiç yazılmayacak — pencerede yalnız başlık ve butonlar kalacak." Fark listesi aynı wireframe'i yeniden görmüş. | 76 |
| 32 | **Açık sekmenin çerçevesi vurgu rengini korur.** Tasarım "yalnız rengiyle belli olur, ek işaret yoktur" diyor; bugün açık sekmede yazı da çerçeve de vurgu rengine dönüyor ve ikisi de renk. İşaret, tasarımın sözlüğünde *eklenen* bir şey — alt çizgi, nokta, ok. Her sekmenin zaten sahip olduğu çerçevenin açık olanda renk değiştirmesi, sekmenin renklenmesidir. Bitişikken o çerçeve sürekli bir şeridin içinde açık parçayı kutulama işini de görüyordu; ayrılınca o işi bırakıyor, rengini değil. Madde geometriden ibaret kalıyor. | 85 |
| 33 | **Kopya ikonu cevabını kendi adında verir.** Tasarım yalnız "basınca metin panoya alınır" diyor; basıştan sonrasını söylemiyor. Sessizlik cevap değil, ve reddedilen bir pano sessizce geçerse kullanıcı metni aldığını sanır. İkon 2,5 saniye boyunca **Kopyalandı** / **Kopyalanamadı** adını alıyor ve vurgu ya da tehlike rengine dönüyor — `RawOutput`'un kelimeleri ve süresi. Panele satır eklemiyor: başlığın yanında beliren bir kelime altındaki kutuyu aşağı iterdi, ki fark 89'un derdi tam olarak buydu. | 90 |
| 34 | **Kutu boşken ikon basılamaz.** Boş bir kutuyu kopyalayıp "Kopyalandı" demek yalan olurdu. İkonu gizlemek de bir cevap ama kullanıcı yazıp sildikçe başlık seğirir. İkon yerinde duruyor ve pasif kalıyor — evin pasif düğme dili. | 90 |
| 35 | **Panel kendi içinde kayar.** Kutular sabit yüksekliğe geçince sütunun toplam boyu da sabitleniyor. Tasarım "panel uzayıp altındaki butonları aşağı itmez" diyor ama panelden kısa bir pencerede ne olacağını söylemiyor. Sütun kendi içinde kayıyor; yoksa silme düğmesi ekranın altında, ulaşılamayacak bir yerde kalırdı. | 89 |
| 36 | **Oklar dizinin ucunda sönük kalır.** Fark okların her karede tam opak ve tıklanabilir durmasını istiyor ve kendi notu "uçta basılınca ne olacağını tasarım söylemiyor" diyor. Tasarım başka bir yerde uçların dönmediğini söylüyor; dönmüyorsa uçtaki oka basınca hiçbir şey olmaz, ve hiçbir şey yapmayan tam opak bir ok orada bir kare olduğunu söyler. Sönüklük o cümlenin dürüst karşılığı. Gözlem ortadaki bir kareyi çizen artboard'dan geliyor olmalı — orada iki ok da zaten tam opak. | 104 |
| 37 | **Kuyruktaki kopya karede şerit duruyor, etiket geliyor.** Farkın şeridi hiç çizmeme yarısı alınmıyor: aynı listenin 92. maddesi kuyrukta bekleyen katmanın sekmesi açılınca kutusunda ne yazacağını tarif ediyor (19. maddede uygulandı), 99. maddesi de düğmenin sekmede durmasını istiyor — şerit kalkarsa ikisi de ulaşılamaz olur. Etiket yarısı alınıyor: sahnedeki resmin bu kareye ait olmadığını bugün hiçbir şey söylemiyor, köşeye "kaynak foto · kopya kare" giriyor. | 112 |
| 38 | **"Kuyruktan çıkar — kare kalır" yazılmıyor.** Kuyruk kareyi çıkarıyor, katmanı değil: `remove_frames.py` kimliklerle çalışıyor ve üretilmemiş bir kareyi kuyruktan düşürüyor. Bir katmanı kuyruktan alıp kareyi bırakan bir basış yok, dolayısıyla "kare kalır" diyen bir düğme motorun yapamadığını vaat ederdi. Farkın asıl şikâyeti — düğmenin yalnız foto sekmesinde olması — düzeltiliyor. | 99 |
| 39 | **Hap fotoğrafın içine inmiyor.** Köşe sahneye göre konumlanıyor, fotoğrafa göre değil: resim sahnenin ortasında `contain` ile duruyor ve sol kenarının nerede olduğu ancak yerleşimden sonra belli. Tutturulacak bir kenar yok. Hapın nabız atan noktası alınıyor, konumu bugünkü yerinde kalıyor. | 107 |
| 40 | **Klasör taşınır, kopyalanmaz.** İstek listesi "adı değiştirmek klasörü değiştirmek demek" deyip cevabı spec'e bırakıyor. Kopyalamak yarıda kalabilir: bir projede binlerce dosya olabilir, Drive üzerinden kopyalama dakikalar sürer, ve kesilirse ortada iki eksik klasör kalır. Ad değiştirme dosya sisteminin kendi atomik işlemi. Sonucu: kare adları, plan, kayıt, ayarlar ve dışa aktarımlar klasörün içinde olduğu için birlikte taşınıyor ve hiçbiri yeniden yazılmıyor. | İstek 10 |
| 41 | **Koşan iş adı her turda yeniden okur, yazarken kilit tutar.** Bugün iş adı bir kez alıyor; klasör altından taşınırsa bir sonraki tur okuyamıyor ve koşu "error" ile bitiyor — yani bugünkü hâliyle ad değiştirmek üretimi öldürür. İş adı bir tutamaktan okuyor, ve yazma anı o tutamağın kilidini alıyor: `write_bytes` eksik klasörü kendisi açtığı için, eski adla çözülmüş bir yazma taşınmadan sonra düşerse yanına hayalet bir klasör bırakırdı. Render kilidin dışında, yani bekleme bir dosya yazma kadar. İşçinin durumundaki proje damgası da adı takip ediyor, yoksa ekran kendi koşusunu tanımaz. | İstek 10 |
| 42 | **Eski dışa aktarımlar taşınır, adları değişmez.** Dışa aktarım klasörü projenin içinde, dolayısıyla klasörle gidiyor. Ama birleştirilmiş dosyanın adı `{proje}.mp4` ve yeniden yazılmıyor: o dosya o adla yapıldı ve kullanıcı onu indirmiş olabilir. Bundan sonrakiler yeni adı alıyor. | İstek 10 |
| 43 | **Karttaki kalem çerçevesiz kalıyor.** 1. karar çöpü yıkıcı eylem standardına soktu; standart yıkıcı bir düğmenin neye benzediğini söylüyor ve kalem yıkıcı değil (fark 3). İkisini düzen adına benzetmek standardın var olma sebebini silerdi: kırmızı çerçeve, yanındaki çıplak ikondan ayrıldığı için işaret. Kalem `ghost` varyantını alıyor — çizgisiz, ama aynı kutu; `border: none` kutuyu her kenardan bir piksel küçültüp düğmeleri kaydırıyordu. | 5 |
| 44 | **Liste kendi içinde kayıyor; 9 Ağustos 2026'nın N3 kararı geri alınıyor.** O karar tasarım v2'ye karşı verildi ve v2'de çizilmiş bir tutamak yoktu — ortada seçenek değil "bugünkü hâl yeter mi" sorusu vardı. v4 hem tutamağı hem bandı çiziyor ve ikisi ancak kırpılmış bir kutuda var olabilir: sayfa kayıyorsa tarayıcının kendi çubuğu zaten var ve altı soluklaşacak bir liste alanı yok. Uygulamanın diğer dört ekranı zaten `height: 100vh` + içeride kayan gövde. | 8 |
| 45 | **Bant sayıya bakıyor, taşmaya değil.** Tasarımın ölçüsü bir sayı: "liste sekizi geçince" — dört sütunun iki satırı. Taşmayı ölçmek uygulanabilir değil: `scrollHeight > clientHeight` jsdom'da iki sıfırı karşılaştırır ve o kuralı doğrulayan test yerleşimi taklit etmek zorunda kalır. Tutamak bu ayrımdan etkilenmiyor — kutu `overflow-y: auto` ve tarayıcı kayacak bir şey yoksa tutamağı çizmiyor. | 8 |
| 46 | **Fark 38'in motor yarısı zaten doğru; değişen yalnız panel.** `queue.ORDER` foto → video → ses ve motor bir türü bitirmeden ötekine başlamıyor: her tür kendi üreticisini yüklüyor, aralarında zıplamak her turda bir model yeniden yüklerdi, ve bir video üstüne asıldığı fotoğrafın önce var olmasını istiyor. Sırayı koruyan bir test de var (`test_the_engine_does_not_skip_past_the_type_it_is_waiting_for`). Yani "diğer türler normal akar, sıra o türe gelince motor bekler" bugün de böyle. Bu maddenin işi panelin **ne zaman ve nerede** konuştuğu: eksiklik, motor o türe gelene kadar hiç söylenmiyordu. | 38 |
| 47 | **Fark 48 düşüyor — "kare" kalıyor.** 4. kararın kapattığı sorunun aynısı: tasarımın terminoloji kuralı içerik birimi için "kare" diyor, çizimi bazı cümlelerde "fotoğraf" diyor ve o sözcük terminoloji netleşmeden önceki dilden kalmış. 4. karar boş ekran metinleri için verilmişti; gerekçe sözcüğün kendisine ait. | 48 |
| 48 | **Fark 50 düşüyor — ham çıktı kutusu kalıyor.** İstenen tek satır zaten ilk satır: kart kuralın cümlesini üstte, servisin cevabını altındaki kutuda gösteriyor. Kalkması istenen cümle değil **kanıt**, ve deponun kuralı hata mesajında sebep uydurmayı yasaklıyor — uygulama tasarımın örnek cümlesindeki sentezlenmiş teşhisi ("3 kez denendi") üretemez, üretirse uydurur. Kutu ayrıca uzun çıktının düğmeleri panelden itmemesi için yazılmış, ve kopyalanabilir olması kullanıcının hatayı taşıyabilmesinin tek yolu. | 50 |
| 49 | **Fark 59 zaten kapandı.** 25. maddede kurulum düğmesi koşu kartından tür kartına indi ve orada yalnız "Kur" yazıyor; "Video üreticisini kur" hiç kalmadı. | 59 |

### Karar gerektirmeyenler

Kalan maddeler karar beklemiyordu: `düzeltilecek` türündekiler uygulamanın kendi tarifinden
sapmaları, `eklenecek` ve `değişecek` türündekiler de tasarımın açıkça getirdiği farklar. Yalnız
5, 6, 7 ve 8 numaralı kararlar istisnaydı — orada "sapma" sanılan şey aslında sonradan verilmiş bir
karardı.
