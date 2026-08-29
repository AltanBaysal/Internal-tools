# QueenAgent v5 Yol Haritası — görmek, ölçmek, sadeleşmek

**Tarih:** 2026-08-25 · **Branch:** `feat/queenagent-v5`, ve **123'ten sonrası
`feat/queenagent-m123-skill-rewrite`** — o madde çalışan bir ritüele dokunduğu için kendi dalına
alındı *(kullanıcı kararı, 29 Ağustos)*, ve 124'ten 132'ye kadar olanlar orada koşuldu ·
**Kaynak:** [queen-agent/BACKLOG.md](../../../queen-agent/BACKLOG.md) — kullanıcının kendi
cümleleriyle yazılmış maddeler. Bu belge onlardan türer; ters yön yok. Kapsam ya da karar değişirse
önce backlog düzelir.
**Numaralar** v4'ten devam eder (64'te bitti). **72 madde, 12 blok** — 65'ten 136'ya. *(Açılışta 49
madde ve 7 bloktu; Blok 8'den 12'ye kadar olanlar sonraki beş denemeden doğdu ve sondan eklendi.)*

**Koşu kapandı** *(29 Ağustos)*. On iki bloğun on ikisi bitti, açık soru kalmadı, ve dal
`main`'e alındı — defterin `BRANCH`'i de aynı commit'te `main`'e döndü, çünkü başkasının çalıştırdığı
defter yayınlanmış olanı klonlar. Buradan sonrası yeni bir yol haritasıdır; bu belge artık kayıt.

**Bu belge üç ayrı belgeden birleşti** *(kullanıcı kararı, 27 Ağustos)*. Blok 5 *"v5.5 Yol Haritası"*
adıyla 26 Ağustos'ta, Blok 6 akış koşusu adıyla 27 Ağustos'ta yazılmıştı. Üçü de aynı branch'te, aynı
sayaçla, biri ötekinin bıraktığı yerden ilerliyordu — ayrı dosyalarda durmaları yalnız okumayı
zorlaştırıyordu. Madde metinleri olduğu gibi taşındı ve **hiçbir numara kaymadı**; değişen yalnız
belge içi atıflar *("v5.5'in 94'ü" artık "Blok 5'in 94'ü")*, ve maddelerin üstüne düşen düzeltme
notları her zamanki gibi duruyor.

---

## Neden bu iş var

QueenAgent bugün cevabı veriyor ama ne yaptığını göstermiyor: model dosya okurken, prompt kurarken
ya da yanlış giderken ekranda üç nokta var, ve başlayan bir cevabın durdurulması mümkün değil. Aynı
körlük paranın üstünde de duruyor — bağlam hızla 300-500k'ya çıkıyor ve bunun ne kadarının
önbellekten geldiği hiçbir yerde okunmuyor.

Bunun altında ikinci bir katman var: yönergeyle tutulmaya çalışılan şeyler. Dosyanın üstüne
yazılmaması, karakterin her karede aynı okunması, işin parçalara bölünmesi — üçü de bugün modelden
*rica* ediliyor. Rica tutmayınca projede aynı işin iki kopyası kalıyor ya da çıktı bozuluyor.

Koşu bu ikisini sırayla kapatıyor: önce ekran ne olduğunu söylesin ve ölçü gelsin; sonra o ölçüye
bakarak bağlam, model ve yönerge birlikte elden geçsin.

## On iki blok

Koşu on ikiye ayrılıyor, ve ayrım **kimin koştuğu**. Koşma sırası belgedeki sıradır:

- **Blok 1 (65-68) tek başına koşuldu — bitti.** Dört madde; her biri kapalı uçlu, kararı verilmiş,
  bir öncekine yaslanıyor. Kullanıcı dördünü koşunun sonunda topluca denedi, ve o deneme Blok 3'ü
  doğurdu.
- **Blok 3 (76-79) tek başına koşuldu — bitti.** Denemenin çıkardığı dört madde: bir hata ve üç
  ekran işi. Blok 2'den önce koştu, çünkü biri Blok 2'nin şartı ve üçü o gün yanlış duran şeylerdi.
- **Blok 4 (80-) madde madde koşulur** *(kullanıcı kararı, 26 Ağustos)*. Blok 3 denenirken çıkan
  ekran düzeltmeleri. Blok 3'ten farkı yalnız tempo: *"adım adım gidelim artık"* — kullanıcı bir
  düzeltme veriyor, o madde iki turda bitiyor, sonra sıradaki geliyor. **Bu blok açık uçlu**:
  deneme sürdükçe madde ekleniyor, ve numaralar sondan veriliyor.
- **Blok 2 (69-75) kullanıcıyla beraber, adım adım koşulur** *(kullanıcı kararı, 25 Ağustos)*.
  Yedisinin de ya çıktının doğruluğuna ya modelin davranışına dokunduğu için karar aralarında
  veriliyor, sonunda değil.
- **Blok 5 (86-94) madde madde koşuldu — bitti.** Sadeleşme: makinenin kendi fazlalıkları ve modelin
  nasıl çalıştığı. Blok 2'nin kalanından **önce** koşuldu *(kullanıcı kararı, 26 Ağustos)*, ve
  koştuğunda Blok 2'nin bekleyen üç maddesinin işini de yaptı.
- **Blok 6 (95-103) madde madde koşuldu — bitti.** Akış: kullanıcıyı sorarak yürüten ikinci skill,
  ve altına gereken üç zemin. Bu bloğun tamamı 27 Ağustos'ta konuşulan kararlardan türüyor. **102,
  99'un spec'i açılınca doğdu** *(28 Ağustos)* — yol haritasının o maddede beklediği bölünme. Koşma
  sırası 99 → 102 → 100 → 101; numara her zamanki gibi sondan verildi. **103 koşu kapandıktan sonra
  doğdu** *(28 Ağustos)* — akış çizimine karşı okununca — ve tek başına koşuldu.
- **Blok 7 (104-113) madde madde koşuldu — bitti.** Üçüncü denemenin çıkardıkları: prompt
  yüzeyi koşusundan sonra defter denendi *(28 Ağustos)*. **104-106** sohbet ekranındandı;
  **108-113** aynı günün ikinci denemesinden, ve hepsi akışın kendisinden: devir, promptu bozan iki
  yapı hatası, iki üslup işi, ve prompt+'ın eksik yarısı. Sekizinin sekizi aynı gün, ikişer turda
  koşuldu. **107 önce ertelendi** *(28 Ağustos: akış stabil, ritüele dokunmak onu bozabilir)*
  **ve 29 Ağustos'ta koşuldu** — altıncı denemede token canı yakınca şartı gerçekleşti.
  Blok 4 gibi açık uçlu: deneme sürdükçe madde eklenir, numaralar sondan verilir.
- **Blok 8 (114-115) madde madde koşuldu — bitti.** Üçüncü denemenin yapı dosyası gerçek SDXL
  promptlarının yanına konunca çıkan iki kalıntı, ve ikisi de tek bir yerden besleniyordu: şemanın
  kendi örneği. Öğreten, kuralının tersini öğretiyordu.
- **Blok 9 (116-124) madde madde koşuldu — bitti.** Dördüncü deneme. Yedisi akışın ve şemanın
  metinlerinden, biri markdown çiziminden, ve sonuncusu ölçüden: **123** skill metinlerini persona
  ile yeniden yazdı ve kendi dalını açtı *(`feat/queenagent-m123-skill-rewrite`)*, **124** önbellek
  anahtarını taktı.
- **Blok 10 (125-127) madde madde koşuldu — bitti.** Altıncı deneme: 123'ün kısalttığı metinlerin
  üstünde ritüel ölmemişti. Bu blok yasak eklemiyor — ya çelişkiyi kaldırıyor *(araç tanımları
  tabanla barışıyor)* ya işi fiziken gereksizleştiriyor *(adlar isteğin kuyruğunda)*.
- **Blok 11 (128-132) madde madde koşuldu — bitti.** Yedinci deneme ve onun üstüne yapılan araç
  karşılaştırması. Aracın sözleşmesi değişiyor: okuma satır numarası veriyor, düzenleme her
  eşleşmeyi alabiliyor, kare eklemenin kendi aracı oluyor, ve prompt+ kapanışını söylüyor.
  **131 ile 132 karşılaştırmadan doğdu** *(29 Ağustos)* ve numaraları sondan verildi; koşma sırası
  129 → 131 → 132 → 128 → 130.
- **Blok 12 (133-135) madde madde koşulur.** Sekizinci deneme: iki mesajlık bir sohbet tavana
  çarptı, ve sebebi tavanın turun raundlarını toplayıp bağlam sanması. Yanında iki geri okuma daha
  çıktı. Blok 4 gibi açık uçlu.

**Blok numarası yazıldığı anı söylüyor, koşulacağı anı değil.** Blok 3 ikinci, Blok 4 üçüncü
koşuyor; numaralarını kaydırmak, onlara atıf yapan her cümleyi yalan yapardı — maddelerin
numaralarında olduğu gibi.

**69 Blok 1'den Blok 2'ye geçti** *(kullanıcı kararı, 26 Ağustos)*. Numarası yerinde kaldı, yeri
değişti — yazılı spec'ler numarayı anıyor. Sebep maddenin kendi açık sorusu: üstüne yazmama kuralı
kullanıcının emeğini korumak için var, ve onu gevşetmenin nereye kadar doğru olduğu tek başına
verilecek bir karar değil.

Blok 2'nin kendi içindeki sıra kullanıcının söylediği sıradır; araya giren iki madde Grok Build ile
prompt dili, ve ikisinin de yeri zorunlu (aşağıda).

### Tasarım bu koşuda kodu takip ediyor *(kullanıcı kararı, 25 Ağustos)*

66, 67 ve 68 tasarımda hiç karşılığı olmayan üç eleman doğuruyor, ve normalde bu deponun kuralı
tersidir: tasarım görsel şartnamedir, kod onu izler. Bu koşuda beklenmiyor — elemanlar önce kodda
doğuyor, [tasarım promptları](2026-08-25-queenagent-v5-tasarim-promptlari.md) sonra atılıyor ve
tasarım koda uyduruluyor.

Bedeli önden biliniyor ve kabul edildi: renkler ve ölçüler var olan görsel dilden türetiliyor ama
kararı veren tasarım değil, kod. Tasarım döndüğünde farklar çıkarsa ilgili maddenin üstüne ikinci
bir tur gelir. Bu, o turun sürpriz olmadığının kaydıdır.

**O tur geldi, ve tasarım claude.ai/design'dan değil kullanıcıdan döndü** *(26 Ağustos)*. 66 ile
67'nin ekrandaki hâli beğenilmedi; ikisi de Blok 3'te yeniden çiziliyor. Beş tasarım promptu
gönderilmedi ve gönderilmeyecek — yerine geçen şey kullanıcının kendi cümleleri.

### Sırayı zorlayan bağlar

- **Görmek, durdurmaktan önce.** Neyin sürdüğü ekranda yokken durdurma düğmesi neyi kestiğini
  söyleyemez. **66 → 67**.
- **Ölçü, optimizasyondan önce.** [FOUNDATION](../../../queen-agent/FOUNDATION.md) 3. ilke ölçülmemiş
  bir sorunu optimize etmeyi yasaklıyor. **68 → 76 → 71**. Bağ önce 68'e yazılmıştı; 68 boruyu
  döşedi ama sayı gelmedi, yani ölçü hâlâ kurulmadı. Şartı bugün 76 taşıyor, ve bu Blok 3'ün neden
  Blok 2'den önce koştuğunun tek cümlelik sebebi.
- **~~Bağlam, modelden önce.~~** Grok Build'in penceresi 256k, bugünkü bağlam 300-500k. Bağlam işi
  bitmeden model değiştirilirse sohbetler pencereye sığmaz. **71 → 72** — **kullanıcı kararıyla
  kaldırıldı (26 Ağustos)**. Endişe söylendi, sayılarıyla: varsayılan Grok 4.3'ün penceresi 1M, Grok
  Build'inki 256k, yani dörtte bir. Kullanıcı yine de istedi. Bağ yanlış değil; kaldıran şey
  kullanıcının kararı, ve 71 geldiğinde çözeceği sorun aynı sorun.
- **Taban yönerge, skillerden önce.** Skillerin üstündeki fazlalık ancak taban onu söylemeye
  başladıktan sonra bırakılabilir. **73 → 74**.
- **~~Prompt dili, skiller toplanmadan önce.~~** Promptun neye benzeyeceğini söyleyen metin skillerin
  içinde duruyor. Dil değişmeden skiller tek akışta toplanırsa aynı metin iki kez yazılır.
  **75 → 74** — **bağ düştü (27 Ağustos)**. Şart yanlış değildi, ama 75 iptal oldu: dil değişmiyor,
  etiket kalıyor *(K9)*. Yani şartın sorduğu soru cevaplandı, ve 74'ü bekleten bir şey kalmadı.

### Backlog karşılığı

| Backlog maddesi | Bu koşuda |
|---|---|
| Uygulama açılınca taslak sohbet ekranı | 65 |
| Tool call'lar sohbette görünsün | 66 |
| Çalışan cevap durdurulamıyor, arka plandaki skill görünmüyor | 66 (görünmek) + 67 (durdurmak) |
| Cached token olayını çöz | 68 |
| Doküman güncellenmiyor, yeniden yaratılıyor | 69 |
| İki karakter aynı karede patlıyor | 70 |
| Context yönetimi ve işi böldürme | 71 |
| Grok Build varsayılan ve tek model | 72 |
| Agentic davranışı arttıran sistem promptu | 73 |
| Promptlar SDXL promptu gibi değil, cümle şeklinde çıksın | 75 |
| Skiller tek bir akışta toplansın | 74 |
| Prompt listesi karışıyor | **bu koşuda yok** — kaydı aşağıda, Kapsam dışı'nda |

"Çalışan cevap durdurulamıyor" iki madde oluyor: içindeki iki şikâyet ayrı işler ve biri ötekinin
şartı. Görünmek isteyen yarısı, "tool call'lar görünsün" maddesiyle aynı işe baktığı için 66'da
birleşiyor.

**Blok 3'ün dördü bu tablonun dışında.** Backlog'dan gelmediler — Blok 1 denendiğinde çıktılar.
Backlog da değişmiyor: orada duran maddeler hâlâ duruyor, bunlar onların üstüne gelen düzeltmeler.

---

# Blok 1 — Tek başına · **bitti**

Dördü de koşuldu ve yeşil. Deneme dönüşünde üçünün üstüne bir düzeltme geldi — her birinin altında
yazılı, ve düzeltmelerin kendisi Blok 3'te.

### Madde 65 — Uygulama taslak sohbet ekranına açılır

- **Ne çalışır:** uygulama bugün ilk projenin ekranına düşüyor ve oradaki yazma kutusunda skill ile
  model seçici yok; seçiciler yalnız sohbet ekranında. Açılış doğrudan boş bir taslak sohbete düşer,
  yani kullanıcı ilk saniyeden itibaren seçicilerin önündedir. Proje ekranı ayrı bir kapı olarak
  kalır.
- **Nasıl görülür:** uygulama açılıyor ve hiçbir şey yazmadan skill seçilebiliyor; proje ekranına
  sidebar'dan girilmeye devam ediliyor.
- **Yok:** yeni bir ekran — o ekran zaten var, değişen yalnız açılış adresi.
- **Denemede geri alındı** *(26 Ağustos)*: doğru teşhis, yanlış çözüm. Sorun seçicilerin proje
  ekranında olmaması; açılışı kaçırmak onu çözmüyor, sadece bir ekranı saklıyor. **77'ye devrediyor.**

### Madde 66 — Tool call'lar sohbette görünür

- **Ne çalışır:** model bir cevabın içinde dosya listeliyor, okuyor, düzenliyor ve prompt kuruyor;
  bugün bunların hiçbiri ekranda yok, yalnız yeni bir dosya doğunca bir kart çıkıyor. Her çağrı
  olduğu anda sohbette görünür ve orada kalır — sonradan bakan da ne yapıldığını okur.
- **Nasıl görülür:** dosyaya dayanan bir soru soruluyor; cevap gelmeden önce hangi dosyanın okunduğu
  ekranda yazıyor. Sayfa yenilendiğinde o satırlar hâlâ duruyor.
- **Spec'te karara bağlanacak:** çağrıların sohbet kaydına yazılıp yazılmayacağı — yazılırsa kaydın
  biçimi değişir ve eski sohbetlerin bunu taşımadığı hesaba katılmalı. Bir de çağrının ne kadarının
  gösterileceği: adı mı, aldığı değerler de mi.
- **Denemede:** davranış doğru, görünüm beğenilmedi *(26 Ağustos)*. Kayıt ve kalıcılık duruyor;
  değişen yalnız satırın çizimi. **78'e devrediyor.**

### Madde 67 — Çalışan cevap durdurulur

- **Ne çalışır:** başlayan bir cevabı kesmenin yolu yok; sohbetten çıkmak sunucudaki turu bitirmiyor
  ve geri dönüldüğünde cevap baştan isteniyor. Bir durdurma düğmesi gelir, cevap gerçekten kesilir ve
  sunucu tarafındaki tur da biter.
- **Nasıl görülür:** uzun bir cevabın ortasında durduruluyor; sohbet olduğu yerde kalıyor, geri
  dönüldüğünde kendi kendine yeniden başlamıyor.
- **Spec'te karara bağlanacak:** durdurulan cevabın yarısına ne olacağı. Bugünkü kural "cevap ya
  vardır ya yoktur" — yarım metin diske yazılmıyor. Durdurmak bu kuralı doğrudan sorguya çekiyor:
  kullanıcının okuduğu yarım cevap kaybolacak mı, yoksa durdurma onu kalıcı mı kılacak.
- **Denemede:** durdurma çalışıyor, ayrı bir düğme olması beğenilmedi *(26 Ağustos)*. Gönder düğmesi
  zaten o anda işlevsiz duruyor. **79'a devrediyor.**

### Madde 68 — Token tüketimi okunur

- **Ne çalışır:** bir cevabın kaça mal olduğu hiçbir yerde okunmuyor; servis her cevapta kaç token'ın
  önbellekten geldiğini söylüyor ve bu bilgi hiç alınmıyor. Tüketim alınır ve kullanıcının
  görebileceği bir yere yazılır: ne kadar gitti, ne kadarı önbellekten geldi, ne kadarı yeniden
  ödendi.
- **Nasıl görülür:** bir soru soruluyor ve cevabın yanında tüketim okunuyor; aynı sohbette ikinci
  soruda önbellekten gelen payın büyüdüğü görülüyor.
- **Neden Blok 1'in sonu:** Blok 2'nin bağlam maddesi bir optimizasyon, ve FOUNDATION ölçülmemiş bir
  sorunu optimize etmeyi yasaklıyor. Bu madde o ölçüyü kurar, yani beraber koşulacak bloğa elimizde
  bir sayıyla giriyoruz.
- **Spec'te karara bağlanacak:** sayının nerede duracağı — her cevabın altında mı, sohbetin
  toplamında mı, ikisinde de mi. *Karar: her cevabın altında, tek sayı (26 Ağustos).*
- **Denemede ekranda hiçbir sayı çıkmadı** *(26 Ağustos)*. Sebep bu belgede yazılı bir yanlışta:
  "servis her cevapta söylüyor" cümlesi xAI'nin akış kılavuzundan alınmıştı, API referansı tersini
  söylüyor — istekte `stream_options` gönderilmeden **her karenin `usage` alanı `null`**. Yani boru
  döşendi ama ölçü kurulmadı; **76 kuruyor**, ve 71'in şartı oraya geçti.

---

# Blok 3 — Denemenin çıkardıkları · tek başına · **bitti**

Blok 1 denendi ve dört şey çıktı: bir hata, bir yanlış çözüm, iki beğenilmemiş çizim. Dördü de
kapalı uçlu — hata bir sebebe bağlandı, kalan üçünü kullanıcı kendi cümleleriyle tarif etti — o
yüzden tek başına koşuldu *(kullanıcı kararı, 26 Ağustos)*.

**Blok 2'den önce**, çünkü 76 Blok 2'nin şartı ve kalan üçü o gün ekranda yanlış duruyordu. Yanlış
duran bir ekranın üstüne yeni iş koymak, ikisini birden düzeltmek zorunda bırakır.

Dördü de yeşil ve commit'li. Denemesi Blok 4'ü doğurdu.

### Madde 76 — Token gerçekten görünür

- **Ne çalışır:** 68 tüketimi okuyup saklayan yolu kurdu ama ekranda hiçbir sayı çıkmıyor. Sebep
  istekte: xAI akan bir cevapta tüketimi ancak `stream_options` ile istenirse gönderiyor, yoksa her
  karenin `usage` alanı `null` geliyor. İstenir hâle gelir ve sayı görünür.
- **Nasıl görülür:** bir soru soruluyor ve cevabın altında sayı çıkıyor; aynı sohbette ikinci soruda
  önbellekten gelen payın büyüdüğü kayıttan okunuyor.
- **Beraberinde düzelen bir söz:** 68'in belgeleri "sayı her parçada geliyor" diyor ve buna
  dayanarak "durdurulan cevap da harcadığını söyler" diyor. Sayı tek karede, en sonda geliyor —
  durdurulan cevap ona ulaşmıyor. Söz koda uydurulur, tersi değil.
- **Şartı olduğu madde:** 71. Bağlam işi bir optimizasyon, ve ölçü buradan geliyor.

### Madde 77 — Seçiciler proje ekranına iner, açılış eskiye döner

- **Ne çalışır:** 65 açılışı taslak sohbete kaçırmıştı, ama asıl sorun proje ekranının yazma
  kutusunda skill ve model seçicinin olmaması. Açılış eski hâline döner ve seçiciler proje ekranına
  gelir — böylece ilk cümle yazılırken de seçilebilirler.
- **Nasıl görülür:** uygulama proje ekranına açılıyor, ve oradaki yazma kutusunda hiçbir şey
  yazmadan skill seçilebiliyor.
- **Neden geri alma:** 65'in teşhisi doğruydu, çözümü değil. Bir ekranı atlamak, o ekranın eksiğini
  kapatmıyor — sadece görünmez kılıyor.

### Madde 78 — Tool call satırı yeniden çizilir

- **Ne çalışır:** çağrılar sohbette görünüyor ve kayıtta kalıyor, ama satırın çizimi beğenilmedi.
  Claude Code'un biçimine geçer: çağrının başında bir işaret, aracın adı, parantez içinde konusu, ve
  altında ne olduğunu söyleyen girintili bir satır.
- **Nasıl görülür:** dosyaya dayanan bir soru soruluyor ve her adım okunur bir satır olarak
  düşüyor; sayfa yenilendiğinde satırlar aynı biçimde duruyor.
- **Değişmeyen:** ne kaydedildiği ve kalıcı olduğu. 66'nın davranışı doğru; bu madde yalnız çizime
  dokunuyor.
- **Spec'te karara bağlanacak:** alt satırın ne söyleyeceği — bugün kayıtta çağrının sonucu yok,
  yalnız aracın adı ve konusu var. Sonucu göstermek kaydın biçimini değiştirir.

### Madde 79 — Gönder düğmesi cevap akarken durdurmaya döner

- **Ne çalışır:** durdurma bugün ayrı bir düğme ve gönder düğmesinin yanında duruyor. Oysa cevap
  akarken gönderilecek bir şey yok; o düğme zaten işlevsiz. İkisi tek düğme olur — cevap akarken
  durdurur, boştayken gönderir.
- **Nasıl görülür:** cevap akarken yazma kutusunda tek bir düğme var ve durdurmayı söylüyor;
  basıldığında cevap kesiliyor ve düğme gönderme hâline dönüyor.
- **Değişmeyen:** durdurmanın kendisi. 67'nin arka ucu, yarım metni saklaması ve kendiliğinden
  yeniden başlamaması aynen duruyor.

---

# Blok 4 — İkinci denemenin çıkardıkları · madde madde

Blok 3 denenirken çıkan ekran düzeltmeleri. Blok 3'ün dördü nasıl geldiyse öyle geliyorlar —
kullanıcının kendi cümlesiyle, denerken. **Fark tempo:** biri veriliyor, iki turda bitiyor, sonra
sıradaki geliyor *(kullanıcı kararı, 26 Ağustos: "adım adım gidelim artık")*.

**Blok açık uçlu.** Deneme sürdükçe madde ekleniyor; numaralar sondan veriliyor ve hiçbiri kaymıyor.

### Madde 80 — Gönder ve durdur düğmesi ikon taşır

- **Ne çalışır:** 79 iki düğmeyi tek düğmede topladı ama düğme hâlâ `Send` / `Start` / `Stop` yazıyor.
  Yazı ikona bırakır: hazırken bir gönderme oku, cevap akarken bir durdurma karesi. Düğmenin adı
  gitmez — görünmez olur, ve ekran okuyucuya da fareyle üstünde bekleyene de aynı kelimeyi söyler.
- **Nasıl görülür:** yazma kutusunun sağında kelime değil ikon duruyor; üstüne gelince ne yaptığı
  yazıyor. Cevap akarken ok kareye dönüyor, basılınca cevap kesiliyor ve kare oka dönüyor.
- **Değişmeyen:** düğmenin ne yaptığı. 79'un iki durumu, 67'nin durdurması, boş taslakta kapalı
  olması — üçü de aynen duruyor. Bu madde yalnız düğmenin üstündeki şeye dokunuyor.
- **Kararı verilmiş:** ikonun şekli deponun kendi görsel dilinden geliyor — her denetim
  `--radius-control` ile yuvarlanıyor ve bunu bir test tutuyor, yani ikon düğmesi de yuvarlak değil
  köşeli kalır. Daire bu dilde yalnız nokta demek.

### Madde 81 — Durdurulan tur durdurulduğunu söyler

- **Ne çalışır:** durdurulan cevabın bugün tek işareti metnine çekilen gri bir sol çizgi; hiçbir yerde
  kelime yok, ve altı ay sonra bakan o çizgiyi okuyamıyor. Bir de daha kötüsü var: ilk kelime
  gelmeden durdurulursa diske hiçbir şey yazılmıyor, yani basıyorsun ve ekranda hiçbir iz kalmıyor.
  Durdurulan tur bunu **yazıyla** söyler, ve kelimeden önce durdurulan tur da bir kayıt bırakır.
- **Nasıl görülür:** uzun bir cevap ortasında durduruluyor ve altında durdurulduğu yazıyor; sayfa
  yenilendiğinde o yazı hâlâ duruyor. İlk kelime gelmeden durdurulan turda da aynı yazı çıkıyor.
- **Beraberinde kapanan bir delik:** kelimeden önce durdurulunca sohbetin son mesajı kullanıcınınki
  kalıyor, yani sohbet hâlâ bir cevap borçlu sayılıyor. Bunu tutan tek şey tarayıcıdaki bayrak, ve o
  bayrak yenilemede sıfırlanıyor — bugün **durdurup yenileyince cevap kendi kendine baştan
  başlıyor**. Boş bir kayıt yazılınca bu kendiliğinden kapanıyor.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: boş ve `stopped` işaretli cevap **diske
  yazılır**. Bedeli biliniyor ve kabul edildi — 67'nin *"cevap ya vardır ya yoktur"* kuralı esniyor.
  Kural yeni hâliyle şu: bir mesaj ya bir söz, ya bir dosya, **ya da bir durdurma** taşır.

### Madde 82 — Model seçme sistemi kalkar, tıklanamaz bir etiket kalır

- **Ne çalışır:** 72 modeli teke indirdi ama etrafındaki bütün makine duruyor — sohbet kaydında bir
  `model` alanı, onu okuyup yazan bir uç nokta, bir menü, bir liste, bir isim çözücü, ve sunucudan
  ekrana kadar taşınan bir varsayılan. Tek model varken hepsi boşa çalışıyor. Sistem sökülür; yazma
  kutusunun ayağında **tıklanamayan bir etiket** kalır *(kullanıcı kararı, 26 Ağustos)*.
- **Nasıl görülür:** ayakta `Grok Build` yazıyor ve basılmıyor, menü açılmıyor. Yeni sohbet de eski
  sohbet de Grok Build ile cevaplıyor.
- **Eski kayıtlar:** diskteki `"model": "grok-4.3"` anahtarı JSON'da kalıyor ama **kimse okumuyor** —
  o sohbetler de Grok Build'e gidiyor. Göç yazılmıyor; sohbet bir daha yazıldığında anahtar
  kendiliğinden düşüyor. Kullanıcının *"grok-4.3 kullanmıyoruz"* şartı böyle sağlanıyor.
- **Modelin adı tek yerde kalıyor:** `config.py`. Etiketin insan okuyan hâli ön yüzde yazılı, ve
  ikisi birlikte hareket eder. Bedeli: ortamdan `XAI_MODEL` ezilirse etiket bunu söylemez. Bu bir
  geliştirici işi ve geliştirici kendi ezdiğini bilir.
- **Yanında gelen iki sadeleşme:** açık menü durumu ikiliye iniyor *(geriye tek menü kaldı)*, ve
  Escape sırası kısalıyor — `fark 67`'nin beşli sırası dörde düşüyor.

### Madde 83 — Mesajın damgası altına iner

- **Ne çalışır:** bir cevap bugün iki not taşıyor ve ikisi mesajın iki ucunda duruyor — üstte
  `QUEENAGENT · 11:05`, altta `13.2k tokens`. `QueenAgent` her cevapta tekrarlanıyor, oysa kenar
  çubuğunda zaten yazılı ve cevabın solda oluşu onu ikinci kez söylüyor. İki satır tek satır olur,
  mesajın altına iner, ve ad düşer: `11:05 · 13.2k tokens`.
- **Nasıl görülür:** bir cevabın üstünde hiçbir şey yok, altında saat ve sayı tek satırda yazıyor;
  kullanıcının kendi mesajının saati de baloncuğunun altında duruyor.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: kullanıcının mesajının damgası da alta
  iniyor. Bir sohbette birinin damgası üstte, ötekininki altta olsaydı kaza gibi okunurdu.
- **Değişmeyen:** sayının kendisi. Neyin toplandığı, binden sonra kısaltılması, önbellek payının
  çizilmemesi — üçü de 68 ile 76'nın kararı ve aynen duruyor. Bu madde yalnız damganın nerede
  durduğuna ve ne yazdığına dokunuyor.

### Madde 84 — Tool call'lar karta döner ve tek kapının arkasına girer

- **Ne çalışır:** çağrılar bugün mono, gri, kenarlıksız iki satır — 78 onları bilerek sessiz yaptı ve
  ekranda yeterince iyi durmuyorlar. Her çağrı bir **kart** olur, ve kartlar tek bir kapının arkasına
  girer: kapalıyken cevabın üstünde tek satırlık bir kart durur, basılınca hepsi alt alta açılır.
- **Nasıl görülür:** dosyaya dayanan bir soru soruluyor; cevap akarken üstte tek kart var ve o an ne
  yapıldığını yazıyor. Cevap bitince aynı kart `5 steps` diyor; basılınca beş kart açılıyor, tekrar
  basılınca kapanıyor.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: kartlar **tam ağırlık** — deponun dosya kartı
  neyse o. Kapalıyken akan turda **son çağrı**, bitmiş turda **adım sayısı** görünür. Tutamak da bir
  kart.
- **Ayrım:** basılan kart bir kapı, basılmayan kart bir kayıt. Tutamak `<button>`, çağrı kartları
  değil — imleç değişmez, hover'da oynamaz. `⎿` düşüyor: kartın sınırı onun işini yapıyor. Rozet
  yok — dosya kartındaki kare bir uzantı taşıyor, çağrının uzantısı yok.
- **Değişmeyen:** ne kaydedildiği ve kalıcı olduğu. 66'nın kaydı ve 78'in parantez kararı *(konusu
  olmayan çağrının parantezi de yok)* aynen duruyor. Açık/kapalı **diske yazılmaz**: bir bakış
  tercihi, sohbet hakkında bir olgu değil.

### Madde 85 — Çağrı kartı geriye oturur

- **Ne çalışır:** 84 kartı dosya kartının iskeletiyle kurdu ve kart ekranda fazla canlı duruyor.
  İki sebebi var: zemini `--surface` *(`#fffdfa`)*, yani sayfadan **daha parlak** — kart sayfanın
  üstünde duruyor; ve metni `--ink`, neredeyse siyah. Kart geriye oturur: zemin sayfadan bir tık
  koyu bir tona iner, metin `Stopped` satırının grisine.
- **Nasıl görülür:** çağrı kartları hâlâ kart ama cevabın önüne geçmiyor; yazıları durdurulmuş bir
  turun altındaki `Stopped` ile aynı ağırlıkta okunuyor.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: **zemin kalkmıyor**, susuyor. Çerçevesiz bir
  kart önerildi ve kullanıcı reddetti — kart kart kalacak, yalnız geriye oturacak.
- **Neden dosya kartından ayrışıyor:** dosya kartı bir kapı ve öne çıkması gerekiyor, o yüzden
  sayfadan parlak. Çağrı kartı bir kayıt; aynı iskeleti giyer ama aynı ışığı almaz.
- **Değişmeyen:** iskelet. Kenarlık, 12px köşe, 340px sınır, kapının basılabilirliği — 84'ün stil
  kilidi ikisinde de yeşil kalıyor. Bu madde yalnız iki renge dokunuyor.

---

# Blok 2 — Beraber, adım adım

Bu yedi madde kullanıcıyla birlikte koşulur *(kullanıcı kararı, 25 Ağustos)*. Sıra kullanıcının
kendi sırasıdır; Grok Build araya giriyor çünkü şartı bir önceki madde, 69 ise Blok 1'den buraya
geçti.

**72 sıradan çıkıp öne alındı** *(kullanıcı kararı, 26 Ağustos)* — Blok 4'ün arasında koşuldu.
Numarası ve bloğu yerinde: blok kimin koştuğunu söylüyor, ve 72 de kullanıcıyla açıldı.

**Blok bitti** *(27 Ağustos)*. 69, 72 ve 73 koşuldu; 74 Blok 5'in 94'üne, 70 Blok 6'nın 95'ine
devredildi; 75 iptal oldu; 71'in işini Blok 5 yaptı. Yedi maddenin hiçbiri koşulmayı beklemiyor.

### Madde 69 — Doküman güncellenir, yeniden yaratılmaz

- **Ne çalışır:** model var olan bir dosyayı düzeltmesi gerektiğinde yenisini yazıyor; yaratma işlemi
  üstüne yazmadığı için eski dosya yerinde kalıyor ve yanına numaralı bir kopya düşüyor. Sonuçta
  aynı işin iki sürümü duruyor ve bir sonraki adımın hangisini okuyacağı belirsizleşiyor. Düzeltmenin
  gerçekten düzeltme olması sağlanır — yönergeye bir cümle daha ekleyerek değil.
- **Nasıl görülür:** bir senaryo yazdırılıp arkasından düzeltiliyor; projede tek bir senaryo dosyası
  kalıyor ve içinde düzeltilmiş hâli duruyor.
- **Neden kod:** üstüne yazan bir yol zaten var — `edit_file` dosyayı yerinde değiştiriyor. Eksik
  olan onu kullanmanın modelin seçimine bırakılmış olması, ve yönergeye "onu kullan" yazmak
  FOUNDATION'ın 5. ilkesine çarpıyor: modelin her seferinde tekrarlaması gereken şeyi kod yapar.
- **Spec'te karara bağlanacak:** numaralı kopya üretmenin hangi durumlarda hâlâ doğru olduğu —
  bugünkü kural kullanıcının emeğini korumak için var (1. ilke) ve tamamen kaldırılması o ilkeye
  dokunur. Bu soru maddeyi Blok 2'ye taşıdı.

### Madde 70 — Karede iki karakter varsa prompt iki kişiyi söyler · **95'e devredildi**

> **Bu madde tek başına koşulmuyor** *(kullanıcı kararı, 27 Ağustos)*. İçeriği bütünüyle Blok 6'nın
> **Madde 95**'ine girdi; kararları [karar defterinde](../../2026-08-27-queenagent-skill-kararlari.md).
> Devrin sebebi yalnız kapsam değil: sıra düzeltmesi de `people` alanı da aynı iki yere dokunuyor —
> `build_prompts.py` ve prompt+ metni — yani ayrı koşulsalar biri ötekinin işini bozardı.
>
> **Devrederken iki yeri düzeltildi.** *"Kaç kişi olduğunu artık kod söyler: kareye giren karakterler
> sayılır"* yanlış: kod sayamaz, çünkü bir karakterin ne olduğu şemada hiçbir alanda durmuyor ve o
> alan bilerek açılmadı. Sayıyı model yazar, kod yerleştirir *(K6–K8)*. İkincisi, maddenin asıl
> şikâyeti sayı değil **sıra** — iki tarif yan yana durduğu için birbirine bulaşıyor *(K1–K5)*; bu
> hiç yazılmamıştı.
>
> **Açık sorusu da beraber gitti ve orada kapandı:** diskte duran yapı dosyaları oldukları gibi
> kalıyor, kod eksik alanı atlıyor *(K26)*. Aşağıdaki metin 25 Ağustos'un kaydı.

- **Ne çalışır:** iki karakterli bir kare bugün görüntü modeline "bir kız" etiketini iki kez
  gönderiyor, oysa iki kişi için beklenen ayrı bir etiket. Kaç kişi olduğunu artık **kod** söyler:
  kareye giren karakterler sayılır ve sayı etiketi bir kez, doğru hâliyle yazılır. Karakter
  tanımının içinde sayı taşınmaz.
- **Nasıl görülür:** iki karakterli bir kare kurulup prompt üretildiğinde çıktı iki kişiyi söyleyen
  tek bir etiket taşıyor; tek karakterli kare eskisi gibi çıkıyor.
- **Neden kod:** FOUNDATION'ın 5. ilkesi — modelin her karede tekrarlamak zorunda kalacağı şeyi kod
  yapar. Yönergeye "sayıyı düzelt" yazmak aynı hatayı görünmez kılar.
- **Spec'te karara bağlanacak:** bugün yazılmış yapı dosyalarındaki sayı etiketlerine ne olacağı —
  temizlenecek mi, olduğu gibi bırakılıp üstüne mi yazılacak.

### Madde 71 — Bağlam yönetilir, iş bölünür · **Blok 5'te çözüldü**

> **Bu madde koşulmuyor: işi Blok 5 yaptı** *(kullanıcı kararı, 27 Ağustos)*. Üç madde şikâyetin üç
> yarısını da kapattı:
>
> - **92** bağlama bir tavan koydu — 50k — ve tavana çarpan tur duruyor. Sınırsız büyüme bitti.
> - **93** yönergeyi isteğin sonuna indirdi; sabit olan başta kaldığı için önek korunuyor ve
>   önbellek işliyor.
> - **91** plan kipini getirdi. *"Uzun iş parçalara bölünsün"* ricası, planı dosyaya yazan bir
>   araca dönüştü — yani tutan bir şey var artık.
>
> **Backlog'a geri dönmüyor.** İki şey bilerek yapılmadı ve yapılmıyor: özetleme, ve okumayı alt
> ajana taşımak. İkisi de bu maddenin çözdüğü sorunun ilacı değil, onun ötesindeki bir iş — ve
> bugünkü ölçüyle gerek görülmedi. İstenirse yeni bir madde olarak doğar. Madde silinmiyor,
> numarası kaymıyor. Aşağıdaki metin 25 Ağustos'un kaydı.

- **Ne çalışır:** bağlam çok hızlı büyüyor, 300-500k'yı buluyor: bir cevap on altı tura kadar
  dönerken her turda sohbetin tamamı yeniden gönderiliyor. Uzun işin parçalara bölünmesi bugün yalnız
  skill metinlerinde bir ricâ; tutan bir şey yok. Bu madde iki şeyi birden yapar — isteğin nasıl
  kurulduğunu ve uzun işin nasıl bölündüğünü.
- **Nasıl görülür:** 68'in getirdiği ölçü aynı işte önceki hâline göre belirgin şekilde düşüyor, ve
  uzun bir kare listesi tek cevapta değil parçalar hâlinde iniyor.
- **Şartı:** 68 — yol, ölçü elde olmadan seçilmez. Bu yüzden bu belgeye bir yol adı yazılmıyor;
  spec 68'in çıktısına bakarak yazılır.
- **Koşunun en büyük maddesi.** Spec'i açıldığında birden fazla maddeye bölünmesi beklenen sonuç;
  numaralar kaymaz, yeni numaralar sondan verilir.

### Madde 72 — Grok Build varsayılan ve tek model

- **Ne çalışır:** sohbetler bugün Grok 4.3 ile açılıyor ve menüde altı model duruyor. Grok Build hem
  varsayılan hem menüdeki tek satır olur.
- **Nasıl görülür:** yeni bir sohbet Grok Build ile açılıyor; menü açıldığında tek satır var.
- **Sırası öne alındı** *(kullanıcı kararı, 26 Ağustos)*. Şartı 71'di ve o şart hâlâ doğru — pencere
  1M'den 256k'ya iniyor, yani uzun bir iş sığmayabilir. Endişe sayılarıyla söylendi, kullanıcı yine
  de istedi, ve karar kullanıcınındır. Sığmayan iş çıkarsa hata verecek ve 76'nın sayısı sebebini
  gösterecek.
- **Kapsamı kullanıcı daralttı** *(26 Ağustos: "başka bir şey istemiyorum")*. İki dosya değişiyor:
  varsayılan ve menü listesi. **Model seçici kalkmıyor** — tek satırla duruyor. **Eski sohbetlerin
  kayıtlarındaki model adları temizlenmiyor** — o sohbetler kendi modelleriyle cevaplamaya devam
  ediyor ve düğmelerinde ham id görünüyor. İkisi de bilinen ve kabul edilen sonuç.

### Madde 73 — Agentic davranış taban yönergeye iner

- **Ne çalışır:** bugünkü sistem yönergesi dört kısa paragraf: kim olduğu, proje dosyalarını
  görebildiği, ne zaman dosya yazacağı. Ne zaman plan yapacağı, yazmadan önce okuyacağı, kendi
  çıktısını kontrol edeceği hiçbir yerde yazmıyor — hepsi tek tek skill metinlerine bırakılmış, o
  yüzden skill seçilmeyen konuşmada davranış dağılıyor. Hangi skill seçili olursa olsun geçerli olan
  davranış taban yönergeye taşınır.
- **Nasıl görülür:** hiçbir skill seçilmeden dosyaya dayanan bir iş isteniyor; model yazmadan önce
  bakıyor ve sonunda ne yaptığını söylüyor.

### Madde 75 — Promptlar cümle olarak çıkar · **iptal**

> **Bu madde koşulmuyor: dediği şey yanlış** *(kullanıcı kararı, 27 Ağustos — K9)*. Metin
> *"çıkan şey etiket dizisi değil, düz cümledir"* diyor; kullanıcı bunun tersini söyledi —
> *"promptların cümle ile çıkması problem, SDXL promptları cümle değil."* Kullanılan modeller SDXL
> temelli ve SDXL etiketle çalışır.
>
> Madde backlog'un belirsiz yazılmış bir satırından doğmuştu: *"Promptlar SDXL promptu gibi değil,
> cümle şeklinde çıksın."* Cümle iki türlü okunuyor, ve yol haritasına yanlış okuma geçmiş.
>
> **Sonucu:** `build_prompts` yaşıyor ve biçim değiştirmiyor *(K10)*. 74'ün *"prompt dili belli
> olmadan tek akışın metni yazılamaz"* şartı bu kararla zaten karşılandı. Madde silinmiyor, çünkü
> numaralar kaymıyor. Aşağıdaki metin 25 Ağustos'un kaydı.

- **Ne çalışır:** bugün hem karakter dosyaları hem kare promptları SDXL etiketi olarak yazılıyor —
  virgülle ayrılmış kısa parçalar; skill metni bunu "asla cümle değil" diye söylüyor, prompt listesini
  kuran kod da parçaları virgülle birleştiriyor. Prompt dili değişir: çıkan şey etiket dizisi değil,
  düz cümledir.
- **Nasıl görülür:** bir kare listesinden prompt üretiliyor ve dosyadaki her satır virgüllü etiketler
  değil, okunan bir cümle.
- **Sırası:** 74'ten önce — bağ yukarıda. Kullanıcının listesinde bu madde yoktu; buraya prompt
  dilinin skillerin içinde yazılı olması yüzünden girdi.
- **Spec'te karara bağlanacak:** kalite etiketlerinin cümlede ne olacağı; bugün diskte duran etiket
  biçimindeki karakter ve yapı dosyalarına ne olacağı — dönüştürülecek mi, yoksa iki biçim birden mi
  okunacak; ve 70'in getirdiği kişi sayısının cümlede nasıl söyleneceği.

### Madde 74 — Skiller tek akışta toplanır · **94'e devredildi**

> **Bu madde koşulmuyor.** Blok 5'in **Madde 94**'ü aynı işi
> anlatıyor ve 74'ün *"hangi skiller düşecek"* açık sorusunun cevabını taşıyor: prompt+ dışında
> hepsi *(kullanıcı kararı, 26 Ağustos)*. Bir karar, kendisini soran soruyu kapatır. 74 silinmiyor,
> çünkü numaralar kaymıyor ve yazılmış spec'ler onlara atıf yapıyor. Aşağıdaki metin o günün kaydı.

- **Ne çalışır:** altı skill var ve hangisinin ne zaman geleceğini kullanıcı seçiyor. Bir kısmı
  gerçekten gereksiz; kalanlar da birbirini izleyen tek bir zincir — senaryo, kareler, karakter,
  promptlar, kontrol. Gereksizler düşer ve geri kalan tek bir akışa iner.
- **Nasıl görülür:** bir senaryodan prompt listesine kadar olan yol tek bir akışla yürüyor; kullanıcı
  arada skill değiştirmiyor.
- **Şartı:** 73 ve 75 — taban yönerge ortak davranışı söylemeye başlamadan skillerden fazlalık
  bırakılamaz, prompt dili belli olmadan da tek akışın metni bir kez yazılamaz.
- **Spec'te karara bağlanacak:** hangi skillerin düşeceği. Bir aday şimdiden belli — promptları elle
  yazan yol, yapıdan kuran yolla aynı işi yapıyor ve karakteri elle kopyaladığı için FOUNDATION'ın
  5. ilkesiyle çarpışıyor. Karar yine de spec'te, beraber verilir.
- **Koşunun son maddesi:** bu bittiğinde skill seçicinin ne göstereceği de belli olur.

---

# Blok 5 — Sadeleşme · **bitti**

> Bu blok *"v5.5 Yol Haritası — sadeleştirme"* adıyla 26 Ağustos'ta ayrı bir belgede yazıldı ve
> 27 Ağustos'ta buraya taşındı. **Kaynağı** kullanıcının konuşma sırasında söyledikleri.

İki dert var, ve ikisi de ilk dört bloğun bitirdiği ekranın altında duruyor.

**Birincisi makinenin kendisi:** aynı şeyin iki yerde durduğu, kodun sözleşmesinin yalan söylediği,
bir şeyin olduğunu hiçbir yerin söylemediği yerler. 86'dan 90'a kadar olanlar bunlar.

**İkincisi modelin nasıl çalıştığı:** yetkinin ricayla tutulması, işin bölünmesinin modelden
istenmesi, bağlamın sınırsız büyümesi, yönergenin konuşmanın ortasında solması. 91'den 94'e kadar
olanlar bunlar, ve hepsi 26 Ağustos'ta yapılan araştırmadan çıktı — ajan araçlarının uzun
konuşmaları nasıl kaldırdığı, işi neden böldükleri, bağlamın uzadıkça niye kalite kaybettirdiği.

**Bu blok Blok 2'nin kalanından önce koşuldu** *(kullanıcı kararı, 26 Ağustos)*. Tek istisna 73 —
94'ün şartı olduğu için bu bloğun içine, 94'ten hemen önce girdi.

**Nasıl koşuldu** *(kullanıcı kararı, 26 Ağustos: "roadmapı nasıl koşuyorsak")*: madde madde. Bir
madde iki turda bitti — önce testler kırmızı commit'lendi, sonra kod yeşile döndü — sonra sıradaki
konuşuldu. Blok 4'ün ritmi.

**Koşma sırası:** 86 → 87 → 88 → 89 → 90 → 92 → 91 → 93 → 73 → 94. İlk altısının hiçbir şartı yok;
91 ile 93 mekanik, tek başlarına koşabilirler; 94 en sonda, çünkü şartı 73 ve 91.

**87, 88 ve 89 ayrı maddeler olarak koştu** *(karar, 26 Ağustos)*, birleştirilmedi — üçü de aynı üç
dosyanın aynı bölgesine dokunduğu ve aynı testleri arka arkaya yeniden yazdırdığı hâlde. Sebebi:
üçü ayrı ayrı görülebiliyor — 87 iki uç yerine bir uç, 88 iki istek yerine bir istek, 89 yazan ucun
durum döndürmemesi. Birleştirilirse tek bir kırmızı tur uçları, use case'leri, hook'u ve ekranı aynı
anda kırar, ve kırmızı bir test hangi kararın yanlış olduğunu söyleyemez. Sıra da bu yüzden bu sıra:
önce kapı birleşir, sonra o kapıdan geri ne geldiği değişir, en sonda geri gelen şey kırpılır. Tersi
her dizilişte önceki maddenin işi sonraki tarafından atılıyor.

### Madde 86 — Skill sohbetin değil oturumun kipi olur

- **Ne çalışır:** skill seçimi bugün sunucuya yazılıyor — sohbet kaydında bir alan, onu yazan bir uç
  ve bir use case var. Ama cevap yolu o alanı hiç okumuyor: turu yöneten yönerge mesajın kendi
  skill'inden geliyor, yani gönderim anında yazılan değerden. Sunucudaki alan yalnız seçicinin ne
  göstereceğini söylüyor. Sistem sökülür: seçili skill isteğin içine yazılır ve başka hiçbir yerde
  durmaz.
- **Nasıl görülür:** skill seçilip mesaj gönderiliyor, model o yönergeyle cevaplıyor; sayfa
  yenilendiğinde seçici boş dönüyor ve sohbetin kaydında hiçbir skill alanı yazmıyor.
- **Yanında kapanan bir hata:** bugün seçici sohbetin kaydını gösteriyor, gönderim ise oturumun son
  seçimini yolluyor. İkisi ayrıştığı anda ekran bir şey diyor, isteğe başka bir şey gidiyor —
  yenilemeden sonra skill'i olan eski bir sohbeti açıp mesaj göndermek bunu her seferinde yapıyor.
  Tek kaynak kalınca hata ortadan kalkıyor; yazılacak bir senkron yok, çünkü senkronlanacak ikinci
  bir yer yok.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: skill sohbette saklanmaz. Bedeli biliniyor ve
  kabul edildi — yenilemeden sonra seçici boş başlar, ve bir sohbette seçilen skill ötekine de geçer.
  Artık sohbetin değil oturumun kipi. Tarayıcı hafızasına da yazılmaz: sildiğimiz karmaşıklığı başka
  bir yere taşımak olurdu. *(Bu son cümle **Madde 100'de değişti** — akış onu geçersiz kıldı.)*
- **Değişmeyen:** mesajın kendi skill alanı. Her tur hangi yönergeyle konuştuğunu söylemeye devam
  eder, yani geçmiş yalan söylemez. Skill seçicinin kendisi de duruyor — kalkan şey seçimin nerede
  hatırlandığı.
- **Eski kayıtlar:** diskteki skill anahtarı JSON'da kalır ve kimse okumaz; sohbet bir daha
  yazıldığında kendiliğinden düşer. Madde 82'nin model anahtarında olduğu gibi.
- **Yanında düşen bir uç:** sohbeti güncelleyen PATCH ucu başka hiçbir şey yapmıyor — skill dışındaki
  her anahtarı reddediyor. Skill oradan çıkınca ucun kendisi de gider.

### Madde 87 — Mesaj tek kapıdan girer, sohbeti sunucu yaratır

- **Ne çalışır:** "kullanıcı bir cümle söyledi" işi bugün iki ayrı isteğe bölünmüş — ilk mesaj sohbeti
  yaratan uca, sonrakiler mesaj ekleyen uca gidiyor. Hangisinin çağrılacağını frontend seçiyor: bir
  bayrak yüzünden gönderme işinin iki ayrı yolu var. Sunucuda da iki use case aynı şeyi yapıyor —
  metni doğrula, mesajı yaz, kaydı döndür. Tek kapı kalır: frontend her zaman aynı yere gönderir,
  sohbet yoksa sunucu yaratır, varsa ekler.
- **Nasıl görülür:** taslak ekranda ilk cümle gönderiliyor ve sohbet açılıyor; aynı ekranda ikinci
  cümle gönderiliyor ve sohbete ekleniyor. İkisi de aynı uca gidiyor.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos: "sadece mesaj atalım, chat yok oluştursun")*:
  sohbeti yaratma işi kendi ucunu kaybeder.
- **Değişmeyen:** boş sohbet yok — sohbet hâlâ ilk mesajıyla doğuyor ve başlığını hâlâ o cümleden
  alıyor. Boş metin hâlâ reddediliyor. Taslak ekran da duruyor; kalkan şey onun hangi uca
  gideceğine karar vermesi.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: sohbetin id'si yolda değil, isteğin içinde
  taşınır ve boş olabilir. Boşsa sunucu sohbeti yaratır, doluysa var olana ekler — kararı veren tek
  soru bu, ve isteğe bakan yer cevabı orada görür.
- **Yanında düşenler:** sohbet yaratan uç, onun use case'i, ve frontend'in ikinci gönderme yolu.

### Madde 88 — Cevabı sunucu başlatır, tarayıcı değil

- **Ne çalışır:** bugün mesaj diske yazılıyor ve bağlantı kapanıyor; cevap ancak tarayıcı ikinci bir
  istek attığı için doğuyor. Tarayıcıda "bu sohbet bir cevap borçlu" diye bir kural var, ve o kural
  yalnız gönderimden sonra değil, sayfa yenilenince ve bağlantı geri gelince de tetikleniyor — yani
  kullanıcının istemediği bir anda cevap kendiliğinden baştan başlıyor. Mesaj yazıldıktan sonra cevap
  aynı isteğin içinde üretilmeye başlar ve aynı bağlantıdan akar.
- **Nasıl görülür:** bir cümle gönderiliyor ve cevap tek bir istek içinde akmaya başlıyor; cevapsız
  duran bir sohbet açılıp sayfa yenilendiğinde kendiliğinden konuşmaya başlamıyor.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: otomatik tekrar deneme yok. Yarıda kalan tur
  durdurulduğunu yazar, o kadar — kullanıcı devam etmek isterse yeni bir cümle yazar. Bu, öteki
  sohbet uygulamalarının yaptığı şey.
- **Yeni sohbetin adresi akışın ilk karesinde gelir** *(karar, 26 Ağustos)*: 87 id'yi isteğin içine
  koyuyor ve boş bırakılabiliyor, bu madde de cevabı aynı isteğe taşıyor — ikisi birleşince o isteğin
  cevabı artık JSON değil, akış. Yani yeni sohbetin id'si bir gövde alanı olarak dönemez. İlk kare
  olur: sunucu id'yi mesajı yazmadan önce zaten üretiyor, yani ilk model tokenından önce
  söylenebilecek durumda. Tarayıcı adresi orada değiştirir, cevap da doğru sohbetin içinde akar —
  yarıda durdurulsa bile sohbet görünür kalır. **Her istekte gönderilir**, sohbet yeni olsun ya da
  olmasın: sunucuda koşul olmaz, tarayıcı yalnız elindekinden farklıysa adresi değiştirir.
- **Değişmeyen:** akış. Metin ve çağrı kartları akmaya devam eder; Madde 66, 78, 84 ve 85'in
  görünürlük işi olduğu gibi duruyor. İlk kare olayların diline bir giriş ekliyor, yeni bir taşıma
  yolu değil — `chunk`, `call`, `file`, `done` nasıl okunuyorsa bu da öyle okunuyor.
- **Yanında düşen:** tarayıcıdaki "cevap borçlu" kuralı ve onu koşturan efekt. Madde 81'in yazdığı
  boş kayıt kalıyor ama sebebi teke iniyor: ekranda "durduruldu" yazabilmek. Kendiliğinden yeniden
  başlamayı önleme işi, önleyecek bir şey kalmadığı için düşüyor.
- **Sırası:** 87'den sonra — tek kapı açıldıktan sonra bu kural tek bir yazma yoluna uygulanır.

### Madde 89 — Sohbetin şekli tek yerde kurulur

- **Ne çalışır:** sohbetin JSON'unu bugün beş yer üretiyor — iki mesaj ucu, skill ucu, okuma ucu ve
  akışın son karesi. Kayda bir alan eklendiğinde beşi birden değişmek zorunda. Yazan uçlar durum
  döndürmeyi bırakır: sohbeti yalnız okuma ucu döndürür, ve yazan bir iş bittiğinde tarayıcı onu
  okur.
- **Nasıl görülür:** cevap bittiğinde ekran kaydı okuyup çiziyor, ve sohbetin şeklini kuran tek bir
  yer kalıyor.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: okumak ile yazmak ayrı yapılar olur, çünkü
  ayrı olunca yönetmesi kolaydır. Akışın son karesi gövdesiz.
- **88'e devredilen:** *"yeni sohbet yaratan istek yalnız id döndürür"* cümlesi buraya yazılmıştı;
  88 o isteğin cevabını akışa çevirdiği için id'nin nasıl döneceği orada karara bağlandı — ilk kare.
  Bu madde 88'den sonra koştuğu için geriye kalan işi şu: son kare gövdesiz olur, ve tarayıcı kaydı
  okuma ucundan okur.
- **Değişmeyen:** akan metin ve çağrılar. Değişen tek şey akışın kaydı taşımaması: akan şey geçici
  bir gösterim, gerçek olan okunan kayıt.
- **Bedeli:** her turdan sonra fazladan bir okuma isteği. Yerelde ihmal edilebilir, ve karşılığında
  kaydın şekli tek yerde durur.
- **Sırası:** 88'den sonra.

### Madde 90 — Durdurma tek yoldan iner ve bağlantıyı keser

- **Ne çalışır:** durdurma bugün iki yarımdan oluşuyor. Bir bayrak var ve koşan cevap onu ancak
  xAI'den bir kare geldiğinde soruyor — ilk kelime beklenirken kimse sormuyor, yani düşünen bir
  modelde durdurmaya basmak dakikalarca hiçbir şey yapmayabiliyor ve xAI o süre boyunca üretmeye ve
  faturalamaya devam ediyor. Bağlantının kapanması ise döngüden çıkmanın yan etkisi, kimsenin verdiği
  bir karar değil. İki yarım tek iptal olur: durdurma isteği, koşan cevabın xAI'ye açık duran
  bağlantısını doğrudan kapatır. Okuma nerede blokeliyse orada uyanır — ilk kelime beklenirken de —
  ve sağlayıcı tarafında üretim ile fatura o anda durur *(xAI'nin bağlantı kesilince üretimi
  durdurduğu sağlayıcı belgeleriyle doğrulandı, 26 Ağustos)*.
- **Nasıl görülür:** model daha ilk kelimeyi söylemeden durduruluyor ve tur o anda bitiyor — ekranda
  durdurulduğu yazıyor, beklemeye devam etmiyor.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos: "2 ayrı iptal yerine tek bir iptal")*: bayrak
  ve yan etki diye iki mekanizma kalmaz, iptal tek mekanizmadır.
- **Yanında düşen:** bayrağın kendisi. Yerine geçen kayıt yine bellekte, yine kilitli, yine cevapla
  birlikte doğup ölüyor — bayrağın yaşam kuralı olduğu gibi devralınıyor; değişen, tutulan şeyin
  "istendi" notu değil bağlantının kendisi olması.
- **Dikkat isteyen bir ayrım:** bizim kapattığımız bağlantının hatası bir durdurmadır, ağın kendisi
  koptuğunda aynı hata bir arızadır. İkisini ayıran tek bilgi kayıtta — kapatan biziz ya da değiliz —
  ve hata mesajına sebep uydurmama kuralı burada da geçerli.
- **Değişmeyen:** durdurulan turun diske `stopped` işaretiyle yazılması, kelimeden önce durdurulan
  turun boş kayıt bırakması, düğmenin iki hâli. 67, 79, 80 ve 81'in tamamı yerinde.
- **Sırası:** 88'den sonra — cevap tek isteğin içine taşındıktan sonra kesilecek bağlantı da tek.

### Madde 91 — Kip gelir: plan, sor, düzenle

- **Ne çalışır:** modelin neyi yapıp yapamayacağı bugün yönergeyle tutuluyor. En açık örneği kontrol
  skill'i: metni *"hiçbir şey düzeltme, dosya yaratma, dosya düzenleme"* diyor — bir yetki kuralını
  ricaya çevirmiş, ve rica tutmayınca kontrol eden skill dosya düzeltiyor. Üç kip gelir — **plan**,
  **sor**, **düzenle** — ve hangi araçların isteğe konacağını kip belirler. Kural koda geçer.
- **Nasıl görülür:** sor kipinde dosyaya dayanan bir iş isteniyor; model okuyor, cevaplıyor, hiçbir
  dosya doğmuyor — çünkü yazma araçları isteğe hiç konmadı, model kendini tutmaya çalışmadı.
- **Plan kipi ne yapar:** işi maddelere böler, planı bir dosyaya yazar, ve **tur orada biter.**
  Kullanıcı planı okur, isterse dosyanın kendisinde düzeltir, sonra yürütür. Kötü bir plan sekiz tur
  yanmadan yakalanır, ve düzeltmek için sohbette tartışmak gerekmez.
- **Planı yazan ayrı bir araç** *(kullanıcı kararı, 27 Ağustos)*: `write_plan`. Plan kipinin elinde
  okuma araçları ve yalnız bu var — yani plandan başka bir şey yazacak aracı yok. Kural bir sayaçta
  değil, araç kümesinin kendisinde duruyor: `create_file` verilseydi model aynı turda planı da
  teslimatı da yazabilirdi, ki maddenin şikâyet ettiği tam olarak bu. Araç yaratır ya da üstüne
  yazar *("eldeki planı güncelleyebilir veya plan oluşturabilir")*, ve adı `-plan.md` ile bitmeye
  zorlanır.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: plan bir skill değil, bir kiptir. Skill
  olsaydı yedinci bir seçenek olurdu — oysa Madde 74 seçenekleri bire indiriyor — ve *"uzun iş
  vermeden önce plan skill'ini seçmeyi hatırla"* diye bir kural doğardı. Kip, hatırlanacak bir şey
  değil, açık bir denetim.
- **Kararı verilmiş:** bir görevin ürünü **dosyadır**, sohbet mesajı değil. Temiz bağlam, önceki
  görevin sohbette ne dediğini bilmez; yalnız diskte ne bıraktığını bilir. İstisnası olamaz, çünkü
  ihlali sessizdir — sonraki görev aradığını bulamaz ve kimse sebebini söylemez.
- **Değişmeyen:** var olan beş araç. Değişen, hangilerinin o kipte isteğe konduğu — ve yanına
  altıncı olarak `write_plan` giriyor, yukarıdaki karar gereği. *(Kipin tanımı **Madde 99'da**
  genişledi: araç listesi değil, sormadan çalışabilenlerin listesi.)*
- **Yanında düşen:** skill metinlerindeki yapma-etme cümleleri, ve uzun işi gruplara bölmeyi rica
  eden paragraflar — plan yürüyen kod olunca üçü de gereksizleşiyor.
- **Sırası:** şartı yok, tek başına koşabilir — işi araçların isteğe konmasını koda almak, ve o iş
  hiçbir yönerge metnine dayanmıyor. Yalnız 94'ten önce gelmesi gerekiyor: 94 skill metinlerindeki
  yapma-etme cümlelerini siliyor, ve o cümlelerin işini kipin devralmış olması lazım.
- **İlişkisi:** 74. Kip, 74'ün *"skiller tek akışta toplanır"* sorusunun büyük kısmını cevaplıyor:
  akış plan oluyor.

### Madde 92 — Bağlamın tavanı olur, ve tavana çarpmak bir olaydır

- **Ne çalışır:** bağlam büyüdükçe bugün hiçbir şey olmuyor. İstek gitmeye devam ediyor, cevabın
  kalitesi sessizce düşüyor, ve iş sonunda pencereye sığmayan bir istekle hataya bağlanıyor. Bir
  tavan konur: tur, tavanın üstünde yeni istek atmaz — durur ve neden durduğunu söyler.
- **Nasıl görülür:** sohbet uzadıkça composer'ın ayağındaki daire doluyor; tavana gelindiğinde tur
  duruyor ve sebebi ekranda yazıyor; arka arkaya hata veren istekler yok.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: tavan 50k civarı. Sebebi kapasite değil
  **kalite** — pencere 256k, yani tavan onun beşte biri. Ölçümler modellerin girdi uzadıkça
  kötüleştiğini ve ortada kalan bilginin gözden kaçtığını gösteriyor, yani sığmak yetmiyor.
- **Üçüncü bir gerekçe, fiyatta** *(xAI fiyat sayfasından doğrulandı, 26 Ağustos)*: 200k'nın üstünde
  girdi fiyatı ikiye katlanıyor — 1M token başına $1.00 yerine $2.00, önbellekten gelen için $0.20
  yerine $0.40. Bugünkü 300-500k'lık bağlam hem pencereye sığmıyor hem de iki katı ödüyor.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: tavana çarpınca istek atmak **engellenir** ve
  ekranda yeni bir sohbet açması söylenir. Özetleme yapılmaz. Özet, konuşmayı sürdürmenin yolu ama
  kendi başına bir iş; bu madde yalnız tavanı ve durmayı getiriyor. *(Buraya önce "şimdilik" ve
  "71'in işi" yazılmıştı. 71 düştü — işini 92, 93 ve 91 yaptı — ve özetleme kullanıcı kararıyla
  planlanmıyor. İstenirse yeni bir madde olarak doğar; bekleyen bir kaydı yok.)*
- **Hangi sayıya bakılır** *(kullanıcı kararı, 26 Ağustos)*: bir turun büyüklüğü ancak cevap dönünce
  öğreniliyor, o yüzden tavan **bir önceki cevabın** sayısına bakar. Yani ölçü bir tur eski, ve
  tavana çarpan istek aslında bir önceki isteğin boyuyla durduruluyor. 50k'lık tavanda bu fark
  önemsiz — bir turun kendisi tavanı aşacak kadar büyük değil.
- **Ekranda ne görünür** *(kullanıcı kararı, 26 Ağustos)*: composer'ın ayağında **dolan turuncu bir
  daire** — Claude Code'un bağlam göstergesindeki gibi. Doluluk oranı aynı sayıdan geliyor: son
  cevabın gönderdiği token, tavana bölünmüş. Kullanıcı tavana çarpmadan önce yaklaştığını görüyor,
  yani durma sürpriz olmuyor.
- **Taslak ekranda görünmez** *(karar, 26 Ağustos)*: composer iki ekranda da aynı bileşen, ama henüz
  sohbet yokken ölçülecek bir bağlam da yok. Boş bir daire çizmek kullanıcıya okuyacak bir şey
  vermiyor, yalnız hep orada duran bir işaret veriyor. Daire ilk cevap dönünce doğar.
- **Nerede durur** *(kullanıcı kararı, 26 Ağustos)*: ayağın **solunda**. Skills, model adı ve
  gönder düğmesi karar 1'den beri sağda duruyor — ayak bugün uçtan sağa dayalı; daire karşı uca
  geçiyor, yani ayak iki uca yaslanan bir satır oluyor. Sebebi: gösterge bir denetim değil, okunan
  bir şey; sağdaki üçlünün arasına girerse tıklanacak bir şey gibi görünür.
- **Şartı:** 76 — sayı zaten her cevabın altında yazıyor, ölçü kurulu. Daire de, tavan da o sayıyı
  okuyor; yeni bir ölçüm kurulmuyor.
- **İlişkisi:** 71 bağlamı küçültmenin yolunu arıyordu; bu madde onun **tabanını** koydu.

### Madde 93 — Yönerge isteğin sonuna iner, sabit olan başta kalır

- **Ne çalışır:** yönerge bugün konuşmanın **ortasına** konuyor — skill'in değiştiği yere. Skill dört
  kez değiştiyse konuşmanın içinde dört ayrı yönerge metni duruyor, ve en eskisi kırk mesaj geride
  kalmış oluyor. İstek yeniden dizilir: sabit olan başa, yönerge **en sona**. Konuşmanın içinde
  dağınık kopyalar kalmaz, yalnız güncel olan gider ve en sonda durur.
- **Nasıl görülür:** uzun bir sohbette skill'e bağlı bir iş isteniyor ve model yönergeye uyuyor —
  yönerge konuşmanın kırk mesaj gerisinde kalmış olsa bile, çünkü artık orada değil.
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: iki ayrı ölçü aynı yeri gösterdiği için.
  **Dikkat:** doğruluk bağlamın başında ve sonunda en yüksek, ortasında %30'dan fazla düşüyor —
  yönergenin en sonda olması onu yüksek dikkat bölgesine koyuyor. **Önbellek:** sabit olan başta
  durursa önek korunur, değişken olan sonda durursa değiştiğinde yalnız kendisi geçersizleşir.
- **Bedeli biliniyor ve kabul edildi:** blok her turda sonda kalmak için taşınıyor, yani her turda
  yeniden işleniyor. On altı turluk bir cevapta bu ~8k token, yani kuruşlar — önbellekten gelen girdi
  1M token başına $0.20 *(xAI fiyat sayfasından doğrulandı, 26 Ağustos)*.
- **Taşınamayan tek şey araç listesi:** `tools` isteğin ayrı bir alanı ve her zaman en başta
  işleniyor. Kipin *metni* sona iner, *araç kısıtı* başta kalır — ve iş zaten kısıtın kendisinde.
- **Değişmeyen:** mesajın kendi skill alanı. Kayıt hangi turun hangi yönergeyle konuştuğunu söylemeye
  devam eder; değişen yalnız modele ne gönderildiği.
- **İlişkisi:** 91'in kipi ve 73 ile 74. 74'ün *"yönerge nerede durur"* sorusunu kapatıyor.

### Madde 94 — Tek skill kalır, beşi silinir

- **Ne çalışır:** bugün altı skill var ve hangisinin ne zaman geleceğini kullanıcı seçiyor. Beşi
  silinir; geriye yapıdan prompt kuran tek skill kalır — kodun promptu birleştirdiği, modelin elle
  yazmasının yasak olduğu yol.
- **Nasıl görülür:** seçicide tek satır var; bir senaryodan prompt listesine kadar olan yol taban
  yönerge artı tek bir metinle yürüyor, ve metni olan yalnız son ayak. *(94'ün spec'inde düzeltildi,
  27 Ağustos: ilk yazımı "seçilecek bir skill listesi yok" diyordu ve maddenin kendi "Seçici kalıyor"
  satırıyla çelişiyordu.)*
- **Kararı verilmiş** *(kullanıcı kararı, 26 Ağustos)*: prompt+ dışında hepsi gider. Bu, 74'ün
  *"hangi skiller düşecek"* açık sorusunun cevabı — hepsi, biri hariç.
- **Zaten fazlalık olan biri:** promptları elle yazan yol, yapıdan kuran yolla aynı işi yapıyor ve
  karakteri kopyaladığı için FOUNDATION 5 ile çarpışıyor. Blok 2 onu şimdiden aday göstermişti.
- **Kaybı biliniyor:** silinen metinlerde işin kendi bilgisi de var — bir karenin bir-iki cümle
  olduğu, kare listesinin kullanıcının dilinde yazıldığı *(yapı dosyası ve prompt listesi İngilizce
  kalırken)*, karakter adaylarının hangi dosya biçiminde verildiği. Kontrol skill'i gidince
  kural kitabı yalnız kurma anında uygulanır, ayrıca "dosyalarımı denetle" diye bir yol kalmaz.
  *(Bu dördünün **hiçbiri geri gelmiyor** — kullanıcı kararı, 27 Ağustos, K31.)*
- **Seçici kalıyor** *(kullanıcı kararı, 26 Ağustos)*: Madde 82'nin model seçicisine benzemiyor.
  Orada tek model vardı ve seçmemek diye bir hâl yoktu; burada **skill seçmemek olağan bir hâl**, yani
  tek satırlık bir seçici bile iki durum taşıyor — skill'li ve skill'siz, ve hangisi olacağı
  kullanıcının kararı. Üstelik listeye ileride yenileri gelecek; şimdi sökmek yakında geri koymak
  olurdu. *(Geleni **Madde 101** getiriyor.)*
- **Şartı:** 73 ve 91. Taban yönerge ortak davranışı söylemeye başlamadan ve kip yetki kurallarını
  devralmadan metinlerden fazlalık bırakılamaz.

---

# Blok 6 — Akış · madde madde · **bitti**

> Bu blok 27 Ağustos'ta ayrı bir belge olarak yazıldı ve aynı gün buraya taşındı. **Kaynağı**
> [karar defteri](../../2026-08-27-queenagent-skill-kararlari.md) ve
> [akış tasarımı](../../2026-08-27-queenagent-akis-tasarimi.md).

Madde 94 skilleri bire indirdi, ve geriye kalan tek metin promptu **kuran** metin. Ama kullanıcı
oraya gelene kadar yolun tamamı metinsiz: karakterlerin, mekânların ve sahnelerin nasıl toplanacağını
söyleyen bir şey yok, ve kullanıcı her seferinde boş sayfadan başlıyor.

Bu blok o yolu getiriyor — **Start a scenario** — ve yolun altındaki üç zemini düzeltiyor: promptun
kendi sırası, şemanın nerede durduğu, ve modelin yazma yetkisinin nasıl sorulduğu.

**Koşma sırası:** 95 → 96 → 97 → 98 → 99 → 102 → 100 → 101 → 103. Sona kalan 101, çünkü şartı
öteki yedisi: akış şemayı araçtan okuyor, planını `edit` kipinde yazıyor, denemeyi kendi aracıyla
kuruyor. 102 araya 99'un hemen ardından girdi — 99'un sorduğu soruyu ekranda gösteren madde o. 103
ondan da sonra, koşu kapanmışken doğdu: akış çizimine karşı okundu ve tek bir çatışma çıktı.

### Madde 95 — Promptun sırası düzelir, kişi sayısı yerine oturur

- **Ne çalışır:** iki karakterli bir karede iki tarif yan yana duruyor ve birbirine bulaşıyor —
  birinin saçı ötekinin üstüne geçiyor. Ayrıca kişi sayısı karakterin kendi tanımında taşınıyor,
  yani aynı karakter tek başınayken de "bir kız" diyor, biriyleyken de. Sıra değişir: **ana karakter
  promptun başında**, geri kalan herkes kameradan sonra. Kişi sayısı karenin kendi alanından
  geliyor ve kalite etiketlerinden hemen sonra bir kez yazılıyor.
- **Nasıl görülür:** iki karakterli bir kare kurulup prompt üretildiğinde ana karakter başta, ikinci
  kişi sonda çıkıyor, ve kişi sayısı bir kez yazıyor. Kıyafet her zaman sahibinin yanında duruyor.
- **Kararı verilmiş** *(K1–K8)*: ana karakter, karenin karakter listesinde **en öne yazılan**
  isimdir — şemaya ayrı bir alan girmiyor, çünkü sıra zaten bilgi taşıyor. Sayıyı **model yazar, kod
  yerleştirir**; kod sayamaz, çünkü bir karakterin ne olduğu hiçbir alanda durmuyor.
- **Bilerek kabul edilen:** üç kişilik bir karede ikinci ve üçüncü sonda yan yana kalıyor, yani
  aralarında karışma riski sürüyor. Korunması gereken ana karakter *(K5)*.
- **Değişmeyen:** diskte duran yapı dosyaları. Kişi sayısı alanı olmayan bir kare bugünkü gibi
  çıkıyor — kod eksik alanı atlıyor *(K26)*.
- **İlişkisi:** 70. Bu madde onun devraldığı iş — ve 70'in yazılı hâlindeki iki yanlışı düzeltiyor.

### Madde 96 — Şema ve kural kitabı skill metninden çıkar, araçtan gelir

- **Ne çalışır:** yapı dosyasının şeması bugün skill metninin içinde duruyor, ve yönerge her turda
  yeniden gönderiliyor *(Madde 93)* — yani şema, yalnız yazma anında lazım olduğu hâlde her tur
  ödeniyor. Üstelik iki skill de dosya yazacağı için ikisinin birden bilmesi gerekiyor, ki bu ikinci
  bir kopya demek. Şema ve kural kitabı tek bir yere iner ve **çağrılınca** gelir.
- **Nasıl görülür:** model yapı dosyasını yazmadan önce şemayı okuyor; skill metinleri kısalıyor ve
  şemayı artık taşımıyor.
- **Kararı verilmiş** *(K28)*: ikisi birlikte döner. Kural kitabı da dosyayı yazan tarafın işi,
  yalnız kuranın değil.
- **Yanında kapanan:** kural kitabı altıncı maddesini burada alıyor — kişi sayısı ya da tek başınalık
  bir karakterin kendi tanımındaysa yanlış yerde *(K27)*.
- **Şartı:** 95 — şemanın anlattığı kişi sayısı alanını kodun zaten kuruyor olması lazım.

### Madde 97 — Plan yazmak edit kipinin de işi olur

- **Ne çalışır:** plan yazan araç bugün yalnız plan kipinde elde. Akış ise dosya yazdığı için edit
  kipinde çalışıyor, yani planını yazamıyor.
- **Nasıl görülür:** edit kipinde bir plan yazılıyor ve tur bitmiyor — iş aynı turda devam ediyor.
- **Değişmeyen:** planın turu bitirme kuralı. O yalnız plan kipinde geçerli *(K22)*.

### Madde 98 — Karakter tek başına denenir

- **Ne çalışır:** kullanıcı bir karakteri sahneye girmeden görmek istiyor — *"bakayım nasıl
  çıkıyor"* — ve bugün bunun için ayrı bir deneme dosyası yazdırmak gerekiyor. İkinci bir kurucu
  gelir: karakter × kıyafetler, düz bir prompt listesi.
- **Nasıl görülür:** bir karakter adı veriliyor ve o karakterin her kıyafeti için bir prompt taşıyan
  liste çıkıyor. Kıyafeti olmayan karakter tek satır veriyor.
- **Kararı verilmiş** *(K36)*: içinde model yok. Kod etiketleri birleştiriyor, tıpkı sahne
  promptlarında olduğu gibi — yani karakter denemede nasıl görünüyorsa sahnede de öyle görünüyor.
- **Değişmeyen:** çıktının biçimi. Sahne listesiyle aynı, yapıştırılmaya hazır. Kendi dosyasına
  yazılıyor, sahnenin listesine karışmıyor.
- **Şartı:** 95 — aynı kurucuyu paylaşıyor.

### Madde 99 — Kapı çalıştırma anına iner

> **Spec'i açıldı ve madde ikiye bölündü** *(28 Ağustos,
> [izin tasarımı](../specs/2026-08-28-queenagent-izin-tasarimi-design.md))*. Aşağıdaki metin
> bölünmeden önce yazıldı ve olduğu gibi duruyor; anlattığı işin **arka yüzü** 99'da kaldı, ekranı
> 102'ye gitti. Başlık yeni sınıra göre değişti — eski adı *"İzin tur ortasında sorulur, onay kipi
> değiştirir"*, ve o ad artık iki maddenin toplamını anlatıyor.
>
> **Bekleyişin üç kararı** *(kullanıcı kararı, 28 Ağustos)*: bekleyiş süresiz — depoda zaten hiçbir
> yerde zaman aşımı yok, ve xAI de sunucu tarafında bir sınır belgelemiyor. Çıkış kapısı sayı değil
> **Stop**. Ve beklerken **nabız** atılıyor, tünel boruyu kesmesin diye.

- **Ne çalışır:** kip bugün modele hangi araçların verildiğini söylüyor, ve verilmeyen araç
  çağrılamıyor. Doğru bir kural, ama bir yan etkisi var: yanlış kipte duran kullanıcı ilk adımda
  takılıyor ve neden takıldığını ekran söylemiyor. Kip artık **sormadan çalışabilenlerin** listesi
  olur: izin verilmeyen bir çağrı geldiğinde tur durur, ekran sorar, ve cevap gelene kadar bekler.
- **Nasıl görülür:** soru kipinde dosya yazmayı gerektiren bir iş isteniyor; ekran izin soruyor;
  onay verilince kip değişiyor ve **aynı tur** kaldığı yerden devam ediyor.
- **Kararı verilmiş** *(K37, K38, kullanıcının kendi cümlesi: "claude güzelce çözmüş bunu")*: red
  turu bitirmiyor. Modele bir açıklamayla dönüyor — kip değişmedi, bu araç bu kipte yok, yazmadan
  devam et — ve **kullanıcı kendi sebebini de yazabiliyor**, o da modele gidiyor.
- **Yetki hâlâ kodda:** model izin almadan yazamıyor. Değişen tek şey kapının araç listesinden değil
  çalıştırma anından geçmesi; yönergeye "yazma" diye bir cümle girmiyor *(Madde 91 yerinde)*.
- **Bloğun en büyük maddesi.** Cevap tek isteğin içinde akıyor *(Madde 88)*, yani akışın o isteğin
  ortasında beklemesi gerekiyor. Spec'i açıldığında birden fazla maddeye bölünmesi beklenen sonuç;
  numaralar kaymaz, yeni numaralar sondan verilir.
- **Değişmeyen:** çağrı kartları. Reddedilen çağrı da sohbette görünüyor *(Madde 84, 85)*.
- **Bölünmeden sonra 99'un sınırı:** arka yüzün tamamı — kural, kayıt, kareler, kapı. Uçtan uca
  görülüyor; görülmeyen tek şey kartın kendisi, o 102'de.

### Madde 100 — Skill seçimi yenilemeden sonra hatırlanır

- **Ne çalışır:** skill seçimi bugün oturumun kipi *(Madde 86)*, ve sayfa yenilenince kayboluyor.
  Beş adımlık bir akışın ortasında bu, bir sonraki mesajın yönergesiz gitmesi demek — ve ekranda
  bunu söyleyen bir şey yok. Seçim tarayıcıda hatırlanır.
- **Nasıl görülür:** skill seçilip sayfa yenileniyor ve seçici seçili hâlinde geliyor; gönderilen
  mesaj o skill'in yönergesiyle gidiyor.
- **Kararı verilmiş** *(K39)*: Madde 86 bunu bilerek dışarıda bırakmıştı, ve gerekçesi *"buna
  değecek bir şey yok"*tu. Akış o gerekçeyi değiştiriyor.
- **86'nın korktuğu geri gelmiyor:** ekranın gösterdiği ile isteğin taşıdığı hâlâ tek değer.
  Hatırlanan şey o değerin kendisi, ikinci bir kaynak değil.

### Madde 101 — Start a scenario doğar

> **Bölünme 28 Ağustos'ta değişti** *(kullanıcı kararı — K40, K32'yi devirdi)*: akış promptları
> kurmaz. Bıraktığı şey temel — karakter ve mekânları taşıyan yapı dosyası *(frames boş)* + tek
> cümlelik sahne listesi *(`bar-scene-scenes.md`)* — ve son sözü kullanıcıyı prompt+'a yönlendirir;
> frame'leri o yazar, `build_prompts`'ı o çağırır. Aşağıdaki metin 27 Ağustos'un kaydı.

- **Ne çalışır:** kullanıcıyı sorarak yürüten ikinci skill gelir. Karakterleri sorar, mekânları
  sorar, sahneleri yazar, promptları kurar — ve nerede kaldığını bir plan dosyasında tutar.
- **Nasıl görülür:** seçicide ikinci satır var; seçilip bir cümle yazıldığında plan dosyası doğuyor,
  her adım onay bekliyor, ve sonunda prompt listesi çıkıyor.
- **Kararı verilmiş** *(K29, K30)*: akış **dallanmaz** — her adımın tek çıktısı var, ve o çıktı
  kullanıcının ne kadar anlattığına göre değişmez; değişen yalnız adımın kaç tur sürdüğü. Her adım
  kendi içinde döngü: kullanıcı onaylayana kadar bir sonrakine geçilmez.
- **Kararı verilmiş** *(K32)*: promptları akış kendisi kuruyor. Kullanıcı sonda skill değiştirmiyor.
  prompt+ yerinde duruyor, işi **var olanı güncellemek**.
- **Kararı verilmiş** *(K34)*: anlatılmayan karakter ve mekân için yer tutucu yazılıyor. Akış tarif
  bekleyerek durmuyor.
- **Yarım kalan iş yeni bir sohbetten sürüyor:** dosyalar projenin, sohbetin değil. Akış ilk iş
  olarak projeye baktığı için orada duran planı görüyor ve açık adımdan devam ediyor — bağlam tavana
  çarptığında *(Madde 92)* yapılacak şey de bu.
- **Bilerek kabul edilen** *(K33)*: sahneler iki yerde duruyor — yapı dosyasında etiket, md'de
  cümle. Biri elle düzeltilip öteki unutulursa ayrışıyorlar; kod bunu kovalamıyor.
- **Şartı:** 96, 97, 98.
- **İlişkisi:** 74 ve 94. 94 seçiciyi tam da bunun için bırakmıştı.

### Madde 102 — Ekran sorar

- **Ne çalışır:** 99 soruyu soruyor ve cevabı bekliyor, ama cevabı verecek olan kullanıcının onu
  göreceği bir yer yok. Duraklayan turun altında bir kart çıkıyor: hangi araç, hangi argümanlarla,
  ve iki düğme.
- **Nasıl görülür:** izin karesi geldiğinde kart çıkıyor; Allow kapıya onayı gönderiyor ve kip
  seçicisi edit'e kayıyor; Deny sebep kutusundaki cümleyi taşıyor.
- **Kararı verilmiş** *(K38)*: sebep kutusu Deny'ın yanında. Onaylarken söylenecek bir şey yok.
- **Değişmeyen:** gönder düğmesi. Kart dururken tur çalışıyor sayılıyor, yani düğme Stop —
  bekleyişin çıkış kapısı zaten o.
- **Yanında gelen:** `dist` aynı commit'te derleniyor.
- **Şartı:** 99.

### Madde 103 — write_plan turun sonunu kipe değil işe bağlar

> **Koşu kapandıktan sonra doğdu** *(28 Ağustos)*: akış çizimine karşı okundu, ve çizimle kodun tek
> çatışması bu tek cümle çıktı.

- **Ne çalışır:** `write_plan`'ın modele giden açıklaması *"tur burada biter: kullanıcı planı okur,
  isterse düzeltir, kendisi koşar"* diyor — her istekte, her kipte. Madde 97'den beri bu yalnız plan
  kipinde doğru: edit kipinde plan yazan tur devam ediyor, ve akış ilk sorusunu aynı turda soruyor.
  97'nin spec'i bunu kelimesiyle yazmış, araç açıklaması ise hiç tartılmamıştı. Model kipi görmüyor;
  cümle bu yüzden kipe değil işe bağlanır — yalnız plan istenen tur biter, büyük bir işin ilk adımı
  olan plan sıradan bir adımdır ve tur sürer.
- **Nasıl görülür:** akış başlatıldığında model planı yazıp karakterleri **aynı turda** soruyor;
  plan kipinde hiçbir şey değişmiyor — turu kesen zaten sunucu *(`ends_the_turn` ellenmiyor)*.
- **Değişmeyen:** sunucunun kuralı ve kipler. Yanlış olan modele söylenen cümleydi, kod değil.
- **Şartı:** 97, 101.

---

# Blok 7 — Üçüncü denemenin çıkardıkları · madde madde · **bitti**

> Prompt yüzeyi koşusu kapandıktan sonra defter denendi *(28 Ağustos)*, ve üçü de sohbet ekranından
> çıktı. Blok 3 ve 4 gibi backlog'dan gelmiyorlar — backlog değişmiyor. Kök nedenler burada
> yazılmıyor: her biri kendi koşusunda araştırılır *(kullanıcının sözü: önce yaz, çözerken araştır)*.
>
> **Üçü de aynı gün koşuldu.** Kök nedenler koşuda bulundu ve her maddenin kendi testler
> tasarımında duruyor: 104 taslağa geçişte bırakılmayan kayıt, 105 oturuma yazılan seçim, 106
> sohbete anahtarsız akış durumu — 104 ile 106 beklendiği gibi aynı mahalle çıktı ama iki ayrı
> düzeltme istedi.

### Madde 104 — Yeni sohbet gönderilen ilk mesajla kendi adresinde kalır

- **Ne çalışır:** yeni sohbet açılıp ilk mesaj atıldığında ekran orada kalmıyor — kullanıcı eski bir
  sohbete ışınlanıyor. Doğru davranış: ilk mesaj sohbeti doğurur, adres doğana geçer, cevap oraya
  akar.
- **Nasıl görülür:** projede eski sohbetler varken New chat açılıp bir cümle gönderiliyor; ekran
  yeni doğan sohbette kalıyor, cevap orada akıyor, kenar çubuğunda seçili satır o.
- **İlişkisi:** 88 — adresi akışın ilk karesi taşıyor; ışınlanmanın mahallesi bu. 106 ile muhtemelen
  tek kök.

### Madde 105 — Skill seçimi sohbetin olur

- **Ne çalışır:** seçim bugün oturumun *(Madde 86)* ve tarayıcı hatırlıyor *(Madde 100)* — bir
  sohbette seçilen skill başka sohbete geçince de seçili duruyor. Seçim seçildiği sohbete özel olur:
  her sohbet kendi seçimini taşır, birinde akış seçmek ötekini değiştirmez.
- **Nasıl görülür:** bir sohbette Start a scenario seçiliyor, başka sohbete geçiliyor — seçici orada
  o sohbetin kendi hâlini gösteriyor; geri dönülünce ilk sohbetin seçimi yerinde.
- **Devirdiği karar:** 86'nın *"seçim oturumundur"* kuralı *(kullanıcı kararı, 28 Ağustos)*. 100'ün
  hatırlaması yeni sınıra uyar: hatırlanan, sohbetin kendi seçimi. Taslak sohbetin ve proje
  ekranının ne taşıyacağı maddenin kendi koşusunda kararlaştırılır.

### Madde 106 — Akan cevap kendi sohbetinin ekranında kalır

- **Ne çalışır:** bir sohbet cevap üretirken başka sohbete geçilince akan metin oraya taşınıyor —
  öteki sohbetin ekranında eski sohbetin akışı görünüyor. Akan cevap yalnız kendi sohbetinde
  görünür; geçilen sohbet kendi kaydını gösterir.
- **Nasıl görülür:** uzun bir cevap sürerken başka sohbete geçiliyor — ekran o sohbetin kendi
  geçmişini gösteriyor, akan satır yok; ilk sohbete dönülünce akış, bitmişse yazılmış cevap orada.
- **Değişmeyen:** sunucu tarafı. Cevap yazılmaya devam ediyor *(Madde 88'in tek-istek akışı
  yerinde)*; iş ekranın hangi sohbette ne gösterdiğinde.
- **İlişkisi:** 104 ile muhtemelen tek kök; koşuda birlikte açılır.

> **İkinci deneme, aynı gün** *(28 Ağustos)*: 104-106 kapandıktan sonra akış uçtan uca koşuldu ve
> üç şey çıktı. Bugünkü biçim işi kanıtlandı — `action` değerleri cümle değil, parça — ve
> adlandırma sözleşmesi *(`senaryo.json` ↔ `senaryo-scenes.md`)* kendiliğinden tuttu. Aşağıdaki
> üçü, o koşunun bıraktıkları.

### Madde 107 — Tur ritüeli iner

> **Bu koşuda koşulmuyor** *(kullanıcı kararı, 28 Ağustos)*: akış bugünkü hâliyle stabil çalışıyor,
> ve ritüele dokunmak çalışan bir şeyi bozma riski taşıyor. Madde duruyor; token gerçekten canını
> yaktığında koşulur.
>
> **Şart gerçekleşti ve madde koşuldu** *(29 Ağustos, kullanıcı onayı)*: altıncı denemede tek bir
> *"nerde kaldık"* turu 8 adım koştu — list_files, plan, üç preview dosyası, şema — ve 19.2k
> gösterdi. `feat/queenagent-m123-skill-rewrite` dalında, 123'ün kısalttığı metinlerin üstünde
> koşuldu; teşhisteki dört cümle düzeltildi, kod değişmedi. Cache tarafındaki kardeşi **124**.

- **Ne çalışır:** akış her turda baştan başlıyor: `list_files` + planı okuma her turda tekrar,
  şema tek koşuda **altı kez**, ve model kendi yazdığını hemen geri okuyor. *"Bitti mi?"* sorusu
  yedi araç adımı sürüyor. Adım = ayrı istek, ve her istek büyüyen bağlamın tamamını ödüyor; iki
  turda 50k token bu yüzden. Ritüel turun başından iner: ilk tur bir kez kurar, sonraki turlar
  bağlamdan sürer.
- **Nasıl görülür:** aynı senaryonun ilk iki turu belirgin az adımla koşuyor — şema yapı dosyası
  yazılmadan hemen önce bir kez çağrılıyor, plan adım kapanınca bir kez yazılıyor, ve yazılan
  dosya geri okunmuyor.
- **Kararı verilmiş:** metin işi, kod değişmiyor. Sebebi bilinen dört cümle *(akışın 1. adımı,
  2. adımın şema çağrısı, planın hafıza cümlesi, taban yönergenin taze-okuma cümlesi)* zayıf
  modelde aşırı çalışıyor — hepsi doğru, hiçbiri fiyatıyla tartılmamıştı.
- **Değişmeyen:** planın hafıza olması *(yarım kalan iş yeni sohbetten sürer)* ve taze okumanın
  kendisi — sınır, **dosyayı başkası değiştirmiş olabilecekse** okumaktır.
- **İlişkisi:** 93, 96, 101.

### Madde 108 — Devir beşinci adım olur

- **Ne çalışır:** akış sahne listesinden sonra durmadı: Generate prompts+'ı hiç göstermedi,
  frame'leri *"yazayım mı?"* diye kendisi teklif etti, planına beşinci bir adım yazdı ve
  frame'lerin onunu tek `edit_file`'da yazdı *(beşli parti kuralı prompt+'ın metninde)*. Devir
  numaralı bir adım olur ve plana beşinci satır olarak girer — iki dosyayı adıyla söyler,
  prompt+'ı gösterir, durur.
- **Nasıl görülür:** sahne listesi onaylanınca kapanış iki dosyayı adıyla söylüyor, senaryonun
  hazır olduğunu söylüyor ve prompt+'ı gösteriyor; *"frame'leri yaz"* denince akış yönlendiriyor,
  kendisi yazmıyor.
- **Kararı verilmiş — kullanıcı ısrar ederse akış yine yazmaz:** yönlendirir. Partili yazım ve
  craft izni prompt+'ta duruyor; onun turnusolu bu koşuda görüldü — tek nefeste on frame.
- **Sebebi biliniyor:** devir cümlesi numaralı listenin **dışında** ve emir kipinde değil; 4. adım
  ise *"the frames will be written from"* diyerek devamı ima ediyor. Zayıf model listeyi bitirince
  duruyor, ve listeye en yakın imayı takip ediyor.
- **İlişkisi:** K40, 101. Gösterdiği skill'in düzenleyici yarısı **113**'te.

### Madde 109 — Kıyafet giyenin olur

- **Ne çalışır:** iki karakterli senaryoda model tek `outfits` girdisi yazdı ve ikisine birden
  verdi: `"...dark pants for man, black dress for woman"` ve `"...t-shirt or blouse"`. Kod metni
  ikisine de aynen bastığı için **beşinci karede erkek siyah elbise giyiyor**, ve `or` / `for man`
  bir görüntü modeline çöp gidiyor. Şema *"iki karakter aynı kıyafeti giyebilir"* diyor; farklı
  giyinen bir çiftin **iki ayrı girdi** istediğini hiçbir yer söylemiyor.
- **Nasıl görülür:** iki karakterli bir senaryoda kıyafetler kişiye göre ayrı girdiler oluyor, ve
  üretilen promptların hiçbirinde `or` ya da `for man` geçmiyor.
- **Kararı verilmiş:** ertelenen örnek işinin şartı gerçekleşti — kullanıcının sözü *"structure'da
  hata olursa o zaman tekrardan düşünürüz"*. Kalabalık ikinci kare örneği bu maddeyle geri
  geliyor; iki karakterin ayrı kıyafet girdileriyle durduğu bir kare, kuralı anlatan cümleden daha
  çok iş görüyor.
- **Değişmeyen:** kod. `build_prompts` adı ne buluyorsa onu basıyor *(K26'nın çizgisi)*; iş
  şemanın düzyazısında, kural kitabında ve örnekte.
- **İlişkisi:** 95, 96.

### Madde 110 — Kalite etiketleri koddan gelir

- **Ne çalışır:** `quality` bugün dosyanın alanı, yani modelin yazdığı şey — ve model onu şemadaki
  örnekten kopyalıyor. Örnekteki dizi iki ayrı model ailesinin karışımı, dolayısıyla her senaryo o
  karışımı taşıyor. Kalite zinciri senaryodan senaryoya değişmiyor: koda iner. Kod prompt kurarken
  en başa ekler ve dosya alanı taşımaz. Bir senaryo başka bir zincir isterse alan yine yazılabilir,
  ve yazılmışsa kod onu kullanır.
- **Nasıl görülür:** akışın kurduğu yapı dosyasında `quality` alanı yok, ama üretilen promptların
  hepsi kalite zinciriyle başlıyor. Alan elle yazılan bir dosyada promptlar o zinciri taşıyor.
- **Kararı verilmiş** *(kullanıcı kararı, 28 Ağustos: "hep aynı olur, prompttan çıkarıp otomatik
  jsona atalım")*. Yazmayan model yanlış zincir de yazamaz — kopyalama sorununu kökten kapatıyor.
- **Varsayılan zincir kullanıcının kendi çalışan promptundan gelir**
  *([araştırma belgesi §5c](../research/2026-08-18-queenagent-beceriler-tasarim-kararlari.md))*. Tek
  sabit, tek yerde: model ailesi değişirse orası değişir, dosyalar değişmez.
- **Değişmeyen:** birleştirme sırası — kalite en başta, bir kez *(Madde 95)* — ve kural kitabının
  "kalite etiketleri karenin kendi alanlarında tekrarlanmaz" maddesi.
- **İlişkisi:** 95, 96. 109 ile aynı dosyalara dokunuyor; ikisi sırayla koşulur.

### Madde 111 — Kamera tek tipten çıkar

- **Ne çalışır:** on karelik bir senaryonun yedisi düz `medium shot` çıktı. prompt+ metni kamerayı
  kendi işi sayıyor ama neye benzediğini söylemiyor, ve şemanın örneği tek bir kamera gösteriyor.
  Çekim ölçüsü ile açı ayrı ayrı seçilir, ve komşu kareler birbirinden ayrışır.
- **Nasıl görülür:** on sahnelik bir senaryoda kamera değerleri çeşitleniyor — ölçü *(yakın, orta,
  boy)* ve açı *(yandan, yukarıdan, arkadan)* — ve aynı değer arka arkaya tekrarlamıyor.
- **Bilerek yapılmayan:** koda kamera listesi girmiyor. Kod ne yazıldıysa onu basar; iş metnin.
- **İlişkisi:** 109 ile aynı iki dosya.

### Madde 112 — Cevabın sonuna seçenek listesi eklenmez

- **Ne çalışır:** model her turun sonuna beş şıklı bir menü yazıyor — *"promptları görmek ister
  misin · birkaçını değiştirelim mi · başka bir şey mi"*. Akış zaten adım başına tek soru soruyor;
  menü hem cevabı uzatıyor hem kullanıcıyı seçmeye zorluyor. Bir tur tek soruyla biter.
- **Nasıl görülür:** adım sonlarında tek bir soru var, altında şık listesi yok.
- **İlişkisi:** taban yönergenin *"End by saying what you did"* cümlesi ile akış metninin onay
  döngüsü; ikisinden hangisine yazılacağı maddenin spec'inde kapanır.

### Madde 113 — prompt+ var olanı da düzenler

- **Ne çalışır:** prompt+'ın metni yalnız baştan kurmayı anlatıyor — açılışı *"this is the skill
  that builds them"*, gövdesi iskeletten listeye giden yol. *"Bu promptu beğenmedim, üçüncü kareyi
  değiştir"* senaryosu hiçbir yerde geçmiyor, ve metinde görmediği işi zayıf model ya reddeder ya
  baştan kurar. Skill iki işi birden söyler: kurar **ve** değiştirir.
- **Nasıl görülür:** var olan bir senaryoda *"üçüncü karenin kamerası yakın olsun"* denince o kare
  `edit_file` ile düzeltiliyor ve `build_prompts` yeniden çağrılıyor; prompt dosyası elle
  yamanmıyor, baştan kuruluyor. Bir harita girdisi değişince onu anan bütün kareler değişiyor.
- **Kararı verilmiş — ayrı bir düzenleme skill'i yok** *(kullanıcı kararı, 28 Ağustos)*: aynı
  dosya, aynı araçlar, aynı kurucu, aynı şema; ikinci bir metin şemayı ve elle-kurma yasağını
  kopyalardı, ve kopya sapar *(96'nın gerekçesi)*.
- **Kaydı zaten vardı:** Madde 94, prompt+'ın işini *"var olanı güncellemek"* diye yazmıştı; o
  cümle skill metnine hiç geçmemiş. Bu madde onu geçiriyor.
- **Yanında gelen:** seçicideki satır. Bugün *"Build the prompts from a structure file you already
  have"* diyor, yani düzenleyici arayan kullanıcıyı başka yere bakmaya gönderiyor — `dist`
  kaynağıyla aynı commit'te derlenir.
- **İlişkisi:** 94, 108. 108 kullanıcıyı buraya yolluyor; burası da onu karşılayabilmeli.

---

# Blok 8 — Örnek öğretmendir · madde madde · **bitti**

> Blok 7 kapandıktan sonra üçüncü denemenin `senaryo.json`'ı bir kez daha, bu sefer gerçek SDXL
> promptlarının yanına konarak okundu *(28 Ağustos)*. Değerler artık cümle değil — Madde 95 sonrası
> biçim düzeltmesi tuttu — ama iki kalıntı duruyor, ve ikisi de tek bir yerden besleniyor: şemanın
> kendi örneği.
>
> **Dışarıdan gelen ölçü.** SDXL rehberlerinin kuralı birebir *"Avoid natural sentences and
> articles"*, kamera açıları da danbooru yazımıyla `from side` / `from above` / `from behind`
> — bizim örneğimiz ikisini de tutmuyor. Kaynaklar:
> [PixAI SDXL rehberi](https://blog.pixai.art/en/general-guide-of-writing-prompts-for-sdxl-models/),
> [Danbooru açı tag'leri](https://danbooru.donmai.us/wiki_pages/angle),
> [Nova Anime3D XL](https://civitai.com/models/1518336/nova-anime3d-xl) *(kullanıcının modeli,
> Illustrious tabanlı)*. Model-agnostik kalınır: yazılan şey biçimdir, bir ailenin doktrini değil.
>
> **Kalite zinciri bu bloğun dışında.** Nova'nın sayfası başka bir zincir öneriyor; koddaki
> `DEFAULT_QUALITY` kullanıcının çalışan zinciri ve ancak onun sözüyle değişir.

### Madde 114 — Şemanın örneği model sözlüğüyle yazılır

- **Ne çalışır:** şema *"The example is the measure"* diyor ve kural defterinin 7. maddesi artikeli
  açıkça yasaklıyor — ama örneğin kendisi artikel taşıyor *(`standing by the window`)*, kamera
  düzyazısı da *(`from the side`)*, ve örnekteki bir kamera hiç tag değil *(`from slightly above`)*.
  Öğretmen kuralın tersini öğretiyor. Koşudaki `sitting on the couch`, `walking together in the
  park`, `on the bed`, `looking at the moon and city lights` bunun doğrudan kopyası.
- **Nasıl görülür:** şemanın örneğinde ve kamera düzyazısında artikel kalmıyor — `by the window` ile
  `from the side` metinde geçmiyor, yerlerini `standing by window`, `from side` ve `from above`
  alıyor. Biçim paragrafı artikelin düştüğünü kendi küçük örneğiyle söylüyor. On sahnelik bir
  senaryoda action ve camera değerleri artikelsiz çıkıyor.
- **Bilerek yapılmayan:** `cowboy shot` girmiyor. Gerçek danbooru tag'i o, ama "shot" süpürme pinini
  gevşetmek gerekirdi ve `medium shot` çalışıyor. Karakter değerlerindeki `in her mid 20s` de
  duruyor — kullanıcının çalışan promptunun üslubu *(araştırma belgesi §5c)*.
- **İlişkisi:** 95 biçimi öğretti, bu madde öğreteni kuralına uyduruyor. 111 kamera düzyazısını
  yazdı, sözlüğü burada tag'e dönüyor. 109 örneğin ikinci karesini ekledi — artikel oradan girdi.

### Madde 115 — Action yalnız kadrajda görüneni taşır

- **Ne çalışır:** koşunun kalan yarısı biçim değil içerik. `facing each other after argument,
  reconciling` ve `one cutting vegetables, other making coffee` — *"after argument"* resimde
  görünmez, *"one … other …"* ise Türkçe sahne cümlesinin yeniden anlatımı. Sahne listesi hikâyeyi
  taşır, kare yalnız kadrajı taşır; bu ayrımı bugün hiçbir metin söylemiyor.
- **Nasıl görülür:** hikâyeden gelen bir sahne — *"küçük bir tartışmadan sonra barışıyorlar"* —
  kadrajda görünene çevriliyor *(oturuş, el teması, ifade, bakış)*, ve neden-sonuç sözü action'a
  girmiyor. Kural defteri bunu ayrı bir madde olarak yakalıyor.
- **Bilerek yapılmayan:** sahne listesi değişmiyor. Hikâye onun işi ve kullanıcının okuduğu şey o;
  ayıklama kareyi yazarken olur.
- **İlişkisi:** 108 yazma işini prompt+'a taşıdı, 113 düzenlemeyi ekledi, 114 biçimi düzeltiyor —
  bu madde içeriği. prompt+'ın *"the sentence is a brief, never text to copy"* cümlesi mekanizmayı
  tutuyor, kuralı değil.

---

# Blok 9 — Dördüncü denemenin çıkardıkları · madde madde · **bitti**

> Blok 8 kapandıktan sonra defter yeniden denendi *(28 Ağustos)*. Kök nedenler burada yazılmıyor:
> her biri kendi koşusunda araştırılır *(kullanıcının sözü: önce yaz, çözerken araştır)*.

### Madde 116 — Sohbetin adı ilk mesajın kısaltılmışı olur

> **Hangisi olduğu koşuda bulundu** *(28 Ağustos)*: ad `chat_title`'dan gelmiyor — turun sonuna
> kadar. Taslaktan doğan sohbet için ekran iyimser bir kayıt ayağa dikiyor ve onun `title`'ı
> mesajın tamamı; sunucunun kırpılmış adı ancak tur bitip kayıt geri okununca geliyor, akışın ilk
> turu ise dakikalar sürüyor. Kenar çubuğu sunucudan okuduğu için zaten doğruydu; yanlış duran yer
> sohbet başlığıydı. Ayrıntı [spec'te](../specs/2026-08-28-queenagent-m116-sohbet-adi-testler-design.md).

- **Ne çalışır:** yeni sohbet açılıp ilk mesaj gönderilince kenar çubuğundaki ad mesajın tamamı
  çıkıyor. Beklenen, ilk mesajın kısa bir başlığa inmesi. **Kodda kısaltma zaten var** —
  `chat.py`'de `TITLE_LIMIT = 42` ve `chat_title` sınırı aşanı `…` ile kesiyor, `append_message` de
  sohbeti doğururken onu çağırıyor. Yani görünen davranış koddaki kuralla çelişiyor: ya ad oradan
  gelmiyor, ya kesilmiş metin ekranda kesilmiş görünmüyor *(satır sonları duruyor olabilir —
  `chat_title` yalnız kırpıyor, satırları tek satıra indirmiyor)*. Hangisi olduğu koşuda bulunur.
- **Nasıl görülür:** uzun ve çok satırlı bir ilk mesajla açılan sohbetin kenar çubuğundaki adı tek
  satır ve kısa; mesajın tamamı başlıkta durmuyor.
- **İlişkisi:** 104 — doğan sohbetin adresi ve kaydı orada, ad da aynı doğumda yazılıyor.

### Madde 117 — *Sen karar ver* yalnız sorulduğu adımı kapatır

- **Ne çalışır:** akışta mekân sorusu *"yatak odası, açık renkler, sen karar ver"* ile cevaplandı
  ve model bunu akışın tamamının yetkisi olarak okudu: mekân adımı onaysız kapandı, sahne adımının
  *"kaç sahne, hangi anlar"* sorusu hiç sorulmadı, ve plana karar adsız yazıldı — *"user said sen
  karar ver"* — yani planı okuyan taze bir sohbet de aynı geniş yetkiyi miras alıyor. *Sen karar
  ver* cevabın dördüncü geliş yolu olur: yalnız sorulduğu adımı kapatır, sonraki adımın sorusu yine
  sorulur, kararı bırakılan adım yine seçileni gösterip onayla biter, ve plana hangi adımı
  kapattıysa o adla yazılır.
- **Nasıl görülür:** mekân sorusuna *"sen karar ver"* deniyor; akış mekânı kendi seçip gösteriyor
  ve onay istiyor, sahnelere gelince sayıyı ve anları yine soruyor.
- **Sebebi bu maddeyi açan konuşmada bulundu** *(28 Ağustos — blokun "önce yaz" sırası bozulmadı,
  araştırma soruyu getiren konuşmanın kendisiydi)*: akış metni cevabın üç geliş yolunu sayıyor —
  etiket, tarif, hiç — ve kararın bırakılması üçünden biri değil; kapsamını söyleyen cümle
  olmayınca model en geniş okumayı seçti, plan da o okumayı kalıcılaştırdı.
- **Bilerek yapılmayan:** taban yönerge ve prompt+ ellenmez. Skill'siz sohbette *"sen karar ver"*
  gerçekten işin tamamını devreder ve taban yönergenin *"Ask rather than invent"* cümlesi bunu
  doğru karşılıyor; prompt+ da zaten kendi başına koşmak için yazıldı — *"asking is for names
  never settled, not for craft"*.
- **İlişkisi:** 101 onay döngüsünü, 108 kapanış adımını yazdı; bu madde ikisinin arasında açık
  kalan kapıyı kapatıyor. 112'nin tek-soru kuralı duruyor — sorulan soru yine tek.

### Madde 118 — Akış kurucuyu çağırmaz

- **Ne çalışır:** akış sahne listesini yazdıktan sonra kullanıcıyı prompt+'a göndermedi;
  `build_prompts`'u kendisi çalıştırmayı teklif etti, yanına karakter önizlemesi koydu ve
  *"onaylıyor musun, yoksa bir değişiklik var mı?"* diye kapattı. Oysa devir adımı onay beklemeyen
  son sözdür, ve akışın bıraktığı dosyada frames bilerek boş — kurucu çağrılsa boş liste üretirdi.
  Yasak işin kendisine göre yazılır: kurucu da prompt+'ındır, akış `build_prompts`'u çağırmaz, ve
  devir mesajı teklif değil bildirimdir — bir şey önermez, bir şey sormaz.
- **Nasıl görülür:** sahne listesi onaylanınca kapanış iki dosyayı adıyla söylüyor, prompt+'ı
  gösteriyor ve duruyor; build_prompts teklifi de seçenek menüsü de soru işareti de yok.
- **Sebebi biliniyor** *(metin okumasından, koşuda doğrulanır)*: 108'in yasağı adıyla frame
  yazmayı söylüyor ve model adı konmuş yasağın etrafından dolaştı — frame yazmadı, kurmayı önerdi.
  Taban yönergenin *"ask the one question that decides what happens next"* cümlesi de kapanışı
  soruya çevirmeye itiyor; devir adımında o soru yoktur, çünkü sıradaki hamle skill menüsünde.
- **İlişkisi:** 108 frame'leri kapattı, bu madde kurucuyu. 112 seçenek menüsünü yasaklamıştı —
  buradaki teklif o menünün tek maddelik hâli.

### Madde 119 — Şema okurunu söyler

- **Ne çalışır:** beşinci denemenin yapı dosyası hareket yönetmenliği taşıyor — `head moving back
  and forth`, `riding with hips moving` — çünkü promptların kime gittiğini modelin okuduğu hiçbir
  metin söylemiyor. *"Modeller SDXL temelli, etiketle çalışır"* bilgisi *(K9)* yalnız yol
  haritasında ve karar defterinde duruyor — modelin asla görmediği iki belgede — ve bir karenin
  **tek bir donmuş fotoğraf** olduğu hiçbir yerde yazmıyor; *"camera"* kelimesi tek başına videoyu
  da çağrıştırıyor. Şema iki olguyla açılır: her prompt SDXL ailesinden, etiket okuyan bir görüntü
  modeline gider, ve bir kare tek bir donmuş andır — hareket, zaman, ses taşımaz. Kamera çifti de
  şemanın kendi listelerinden seçilir: `from side profile` diye bir tag yok.
- **Nasıl görülür:** on karelik bir senaryoda action'larda hareket ve zaman sözü çıkmıyor,
  kamera değerleri şemadaki listelerden geliyor.
- **İlişkisi:** 114 örneği sözlüğe uydurdu, 115 kadraj kuralını yazdı — ikisinin de varsaydığı
  olguyu bu madde söylüyor. 121 aynı sızıntıların defter girdileri.

### Madde 120 — İşin bağlamı skillere ve plana iner

- **Ne çalışır:** kullanıcının kendi cümlesiyle: *"modele ne yaptığımızın contextini vermezsek
  nereden bilecek?"* İki skill metni de işin ne olduğunu söylemeden başlıyor — akış *"walks them
  through it by asking"* diyor ama neye doğru yürüdüğünü söylemiyor, prompt+ *"builds the
  prompts"* diyor ama promptun neye gittiğini söylemiyor. Her skill metni işi söyleyerek açılır:
  kullanıcı bir hikâyeyi SDXL ailesinden bir görüntü modelinin tek tek çizeceği donmuş karelere
  çeviriyor. Akışın yazdığı plan da bir bağlam satırıyla doğar — ne yapılıyor, kim için — ki planı
  okuyan taze sohbet adımları değil işi devralsın.
- **Nasıl görülür:** taze bir sohbet yarım planı açıp devam ettiğinde bağlamı plandan okuyor;
  her iki skill'in ilk cümleleri işin kendisini söylüyor.
- **İlişkisi:** 117 plana devrin nasıl yazılacağını söyledi — plan zaten taze sohbetin hafızası;
  bu madde o hafızaya işin kendisini koyuyor. 119 aynı olgunun şemadaki yarısı.

### Madde 121 — Action sızıntıları kural defterine girer

- **Ne çalışır:** beşinci denemenin dosyasında dört sızıntı var ve hiçbirini defter yakalamıyor:
  action'da hareket (`head moving back and forth`), action'da kamera sözü (`full body view`,
  `upper body visible`), action'da rol-akrabalık adı (`stepson thrusting` — kamera akrabalık
  görmez, kim olduğunu characters haritası söylüyor), ve `or` (`hands gripping wall or body` —
  8. madde onu yalnız outfits için yasaklamıştı). Bir de giysi adının giyene göre konması
  (`milf_pink`, `male_nude` — düzyazıda kural vardı, model es geçti, defterin sayılabilir
  listesine iner; aynı metni taşıyan iki girdi tek giysidir). Hepsi kural defterine girer —
  defter, dosya yazılmadan önce *"buna karşı kontrol et"* denilen liste.
- **Nasıl görülür:** aynı senaryo yeniden kurulduğunda action'larda hareket, kamera sözü, rol adı
  ve `or` çıkmıyor; nude tek girdi.
- **İlişkisi:** 119 olguyu öğretiyor, bu madde zayıf model için çitleri sayıyor — 108→118 gösterdi
  ki ikisi de gerekiyor. 109'un `or` yasağının genelleşmiş hâli.

### Madde 122 — Numaralı liste bire takılmıyor

- **Ne çalışır:** sohbetteki markdown'da numaralı liste `1 2 3` yerine `1 1 1` çıkıyor. Kök neden
  bu belgede yazılmıyor — koşusunda bulunur *(Blok 9 kuralı)*.
- **Nasıl görülür:** üç maddelik numaralı bir liste içeren cevap ekranda 1, 2, 3 sayıyor; sayfa
  yenilenince de öyle.
- **İlişkisi:** 13 markdown çizimini getirdi; bu onun bir düzeltmesi.

### Madde 123 — Skill metinleri persona ile açılır ve tarif biçiminde kısalır

- **Ne çalışır:** beş koşunun yaması üst üste bindi ve iki skill metni yasak biriktirerek uzadı —
  akış ~700 kelimeye dayandı, ve uzayan metinde zayıf model ortadakini okumuyor; 108→118 de
  gösterdi ki adı konmuş yasağın etrafı dolaşılıyor. İki metin yeniden yazılır: başa persona
  *(kullanıcının cümlesi: "sen uzman bir senaryo yazarısın... zemini kurup uzman prompt yazarına
  bırakacağız")*, gövde yasak listesi değil adım tarifi, hedef yarıya yakın uzunluk. Kazanılmış
  davranışların hepsi kalır: mevcut pin testleri bekçi olarak korunur, kırmızıyı yeni pinler verir
  — iki persona açılışı ve kelime tavanı.
- **Nasıl görülür:** aynı senaryo koşusu aynı davranışları gösteriyor — adım onayları, devrin
  kapsamı, teklifsiz kapanış, beşli parti — ve metinler belirgin kısalmış.
- **Kendi dalında koşulur** *(kullanıcı kararı, 29 Ağustos)*: `feat/queenagent-m123-skill-rewrite`.
  Denenip beğenilirse v5'e merge edilir; beğenilmezse dal ölür ve numara kaydıyla kalır — çalışan
  ritüele dokunulduğu için *(107'nin uyarısı)* deneme dala alındı.
- **İlişkisi:** 101, 108, 112, 113, 117, 118 ve 120'nin davranışları aynen korunur; değişen yalnız
  anlatım. Sonrasında yazılan skillerin writing-skills gözüyle bir daha okunması ayrıca konuşuldu.

### Madde 124 — İstek cache anahtarını taşır

- **Ne çalışır:** xAI'nin prefix cache'i otomatik ama isabet garanti değil: girdiler bellek
  baskısıyla düşüyor ve istekler farklı sunuculara gidebiliyor; dokümanın kendi cümlesi *"use
  x-grok-conv-id to maximize cache hit rates"*. Client bugün yalnız `Authorization` ve
  `Content-Type` gönderiyor — bir turun on-yirmi isteği aynı cache'e yönlendirilmiyor. Sohbet
  kimliği `stream_answer`'dan motora, motordan client'a iner ve her istek `x-grok-conv-id`
  başlığını taşır; kimliği olmayan yol *(ad üretimi gibi)* başlıksız kalır.
- **Nasıl görülür:** aynı sohbetin ikinci sorusundan itibaren cevabın altındaki sayının
  önbellekten gelen payı kayıttan belirgin büyük okunuyor — ölçüyü 68/76 kurmuştu.
- **Kaynak:** [xAI prompt caching](https://docs.x.ai/developers/advanced-api-usage/prompt-caching/how-it-works)
  *(29 Ağustos'ta okundu)*. Araştırmanın diğer yarısı bir maddeye dönmedi: araç sonuçlarını
  turlar arası taşımak Anthropic'in kendi kılavuzunda da tersine çevrilmiş durumda *(tool result
  clearing — "why would the agent need to see the raw result again?")*; QueenAgent'ın turlar arası
  silmesi o felsefeyle uyumlu, ve FOUNDATION 3 ölçülmemişken büyütmeyi yasaklıyor. Önce 107+124,
  sonra ölçüm.
- **İlişkisi:** 93 prefix'i sabitledi, 68/76 ölçüyü kurdu, 107 istek sayısını indirdi; bu madde
  kalan isteklerin ucuza inmesi. `feat/queenagent-m123-skill-rewrite` dalında koşuldu.

---

# Blok 10 — Ritüel metinle ölmedi · madde madde · **bitti**

> Altıncı deneme *(29 Ağustos, 107 ve 124 koşulmuş dalda)*: iki mesajlık bir koşunun ikinci turu
> 12 adım ve ~120k `sent` tuttu. Adımlar tek tek okundu ve israfın üç kaynağı çıktı: model olmayan
> bir dosya adı uydurdu ve aynı planı art arda iki kez okudu *(adlar hiçbir istekte hazır değil)*;
> kendi yazdığı dosyayı her yazımdan sonra geri okudu *(araç tanımları bunu emrediyor — taban
> yönergenin yeni cümlesiyle çelişerek)*; planı bir turda üç kez yazdı. 107'nin dersi: zayıf model
> düzyazı ricayı değil, önüne konanı ve araç tanımını dinliyor — o yüzden bu blok yasak eklemiyor,
> ya çelişkiyi kaldırıyor ya işi fiziken gereksizleştiriyor. Tasarım kullanıcıyla konuşuldu
> *(brainstorming, 29 Ağustos)*; tam gömme — bütün dosya içeriklerinin her isteğe konması —
> reddedildi: *"read filesı hala kendi yapsın karışmaması için"*, içerik JIT kalır *(124'ün
> araştırma notuyla uyumlu)*.

### Madde 125 — Araç tanımları tabanla barışır

- **Ne çalışır:** taban artık *"never to check your own writing"* derken, her istekte giden iki
  araç tanımı tersini emrediyor: `edit_file` koşulsuz *"so read the file first"* diyor,
  `write_plan` *"read it first and hand back the whole plan"*. Denemedeki `create_file` →
  `read_file` → `edit_file` zinciri bu emrin doğrudan ürünü. İki tanım koşullanır: bu turda
  görülmemiş dosya önce okunur, bu turda kendi yazdığın zaten aynen eldedir.
- **Nasıl görülür:** bir turda doğan ya da düzenlenen dosya aynı turda geri okunmuyor; okumalar
  yalnız turun görmediği dosyalara gidiyor.
- **İlişkisi:** 107 tabanın cümlesini yazdı; bu madde araç tanımlarını o cümleye uyduruyor.
  Çelişki 107'nin koşusunda görülmedi çünkü tanımlar 107'nin kapsamı dışındaydı.

### Madde 126 — Plan işaretlemesi tek dokunuştur

- **Ne çalışır:** denemede tek adımın kapanışı plana üç yazım mal oldu — `write_plan`,
  `edit_file`, tekrar `write_plan`. Akış metninin *"marked done"* cümlesi işaretlemenin ne
  olduğunu söylemiyor, model iki mekanizmayı da deniyor. Cümle netleşir: işaretleme tek bir
  `edit_file`'dır, tam yeniden yazım değil — kelime tavanının içinde kalarak.
- **Nasıl görülür:** bir adım onaylanınca plana tek bir düzenleme gidiyor; `write_plan` yalnız
  planın doğduğu ilk turda görünüyor.
- **İlişkisi:** 101 döngüyü, 117 devrin kaydını yazdı; 125 `write_plan` tanımını düzeltiyor, bu
  madde akış tarafını.

### Madde 127 — Dosya adları isteğin kuyruğunda hazırdır, `list_files` kalkar

- **Ne çalışır:** adlar hiçbir istekte hazır olmadığı için model ya her turu `list_files` ile
  açıyor ya da ad uyduruyor *(`plan.md`)*. `stream_answer` her raundda `file_store`'dan adları
  çeker ve isteğin sonuna, skill metninin hemen önüne bir system satırı koyar — *"The project's
  files right now: bar-scene.json, bar-scene-scenes.md"*, boş projede *"This project holds no
  files yet."* Sona binmesi 93'ün kalıbı: başa binse her dosya doğumu konuşmanın prefix cache'ini
  öldürür; sonda prefix sağlam kalır ve `create_file`'dan sonraki raund taze listeyi görür.
  `list_files` aracı tamamen kalkar — spec'i de `run_tool` dalı da: liste hep öndeyken araç ölü
  ağırlık, ve duran araç çağrılmaya devam eder *(kullanıcı kararı, 29 Ağustos)*. Ona değinen üç
  metin güncellenir: taban *("Use list_files to see what exists")* yerine adların her isteğin
  sonunda zaten önünde durduğunu söyleyen cümleyi alır; akışın 1. adımı *("opens with list_files,
  then write_plan")* yalnız `write_plan`'a iner; prompt+ *("find them with list_files")* çifti
  listeden adıyla bulur. Tur içi hafızanın öğretimi 125'in koşullu cümlesinde: bu turda okuduğun
  ya da yazdığın zaten aynen elinde.
- **Nasıl görülür:** taze bir turda model ad uydurmuyor ve hiçbir tur listeleme adımıyla
  açılmıyor; tur başına istek sayısı düşüyor, `cached` payı 124'ün ölçüsüyle büyük okunuyor.
- **Bilerek yapılmayan:** dosya *içerikleri* gömülmüyor — `read_file` durur, okuma modelin JIT
  işidir; turlar arası araç sonucu taşınmaz *(124'ün araştırma notu)*. Üretilmiş `.py` dosyaları
  da yalnız adıyla görünür.
- **İlişkisi:** 93 kuyruk kalıbını kurdu, 107 ilk-tur cümlesini yazdı *(pin değişir: `write_plan`
  kalır, `list_files` düşer)*, 124 cache anahtarını taktı — bu madde anahtarın koruduğu prefix'i
  kısaltmadan adları ulaştırıyor.

---

# Blok 11 — Aracın sözleşmesi ne derse o olur · madde madde · **bitti**

> **Beşi de koşuldu** *(29 Ağustos)*, sırası 129 → 131 → 132 → 128 → 130. Kalan iş kullanıcının:
> sekizinci deneme. 128'in gerekçesi hâlâ ölçülmemiş — deneme onu doğrularsa madde yerinde kalır,
> doğrulamazsa `add_frames` sökülür ve 131 ile 132 yerinde kalır. Ayrı maddeler olmalarının sebebi
> buydu.

> Yedinci deneme *(29 Ağustos, Blok 10 koşulmuş dalda)*: prompt+ turu 16 adım ve 335k `sent`
> tuttu. Blok 10'un kazandıkları duruyor — tur `list_files` ile açılmadı, iki dosyanın adı da
> doğru yazıldı *(uydurma yok)*, şema tam bir kez çekildi. Kalan israf tek bir kalıpta: her
> `edit_file`'dan sonra bir `read_file`, beş kez, ve sonunda aynı 156 satırlık dosya üst üste
> üç kez.
>
> **Dersi 125'in sınırı.** Tanımdaki *"bu turda görmediysen oku"* cümlesi tutmadı, çünkü aynı
> tanımın bir cümle önünde duran şart okumayı gerektiriyor: *old metin diskte tam olarak bir kez
> geçmeli.* Kareler birbirine benziyor, model her batch'te bu şartı tutturabildiğinden emin
> olmak için okuyor — ve haklı. Modele okuma dememek yetmiyorsa, okumayı gerektiren sözleşme
> değişir.
>
> **Maliyeti bileşik.** 156 satırlık her okuma sonucu tur boyunca konuşmada duruyor ve sonraki
> her isteğe yeniden biniyor; 335k bunun toplamı, tek bir isteğin boyu değil.
>
> **Önce araştırıldı** *(kullanıcının sözü: "bunları yapmadan önce araştır")* —
> [araç tasarımı araştırması](../research/2026-08-29-queenagent-arac-tasarimi-arastirma.md).
> Üç şey çıktı: sorun bu araç ailesinin bilinen davranışı *(ölçülmüş: Claude Code, Cursor ve
> Codex oturumlarında token'ın %42'si kaçınılabilir işlemlerde, başı çeken kalem tekrarlı
> okuma)*; kök neden string eşleşmeli düzenlemenin kendisi, yani yasak değil **şart**
> değişmeli; ve bayat sonuçları temizlemenin bir bedeli var — önbelleklenmiş prefix'i geçersiz
> kılıyor. Bu üçüncüsü Madde 129'un sırasını değiştirdi.

> **129 koştuktan sonra araçlar Claude Code'unkilerle yan yana kondu** *(29 Ağustos, kullanıcının
> sözü: "kesinlikle claude gibi olsun read ve edit, adamlar uğraşıp çözmüş")*. Karşılaştırma iki
> şey gösterdi. Birincisi: `edit_file`'ın *"tam bir kez geçmeli"* şartı bizim icadımız değil —
> Anthropic'in kendi text editor aracı da aynısını söylüyor *("`old_str`: must match exactly,
> including whitespace and indentation")*, ve Claude Code'un `Edit`'i de. Yani şart kalıyor,
> etrafındaki iki kolaylık eksik: **satır numaralı okuma** ve **`replace_all`**. 131 ile 132
> bunlar.
>
> İkincisi 128'i ilgilendiriyor: **Claude Code'un satır numaralı bir insert aracı yok.** Anthropic
> onu API'sindeki text editor aracına koymuş *(`insert_line`, `insert_text`)* ama kendi kod
> ajanına vermemiş. Verdiği tek insert `NotebookEdit`'inki, ve o **satır değil `cell_id`** ile
> çalışıyor — yani yapılandırılmış bir dosyaya yapı-farkındalıklı insert. `add_frames` o kalıbın
> bizdeki karşılığı, `insert_lines` ise Claude Code'da karşılığı olmayan bir araç olurdu.
> Kaynaklar: [text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool),
> [Claude Code tools reference](https://code.claude.com/docs/en/tools-reference).

### Madde 128 — Kare eklemenin kendi aracı olur

> **Gerekçesi değişti, kendisi değişmedi** *(kullanıcı kararı, 29 Ağustos)*. Madde okumayı
> ortadan kaldırmak için yazılmıştı — *"çapa yok, dolayısıyla okuma gerekçesi de yok"* — ve
> okumanın gerekçesini **129 zaten kaldırdı**: kap her istekte dosyanın güncel hâlini modelin
> önüne koyuyor, yani çapayı doğrulamak için okumaya gerek kalmıyor. Madde artık okuma için değil,
> geriye kalan iki bedel için koşuluyor: **çapanın çıktı token'ı** *(diskte duran metin `old`'da
> bir, `new`'da bir daha yazılıyor — en pahalı token sınıfında)* ve **çakışma retleri**, ki
> kareler birbirine benzediği için *"appears 3 times"* gerçek bir yol.
>
> **İkisi de ölçülmedi, ve bu biliniyor:** elimizdeki 335k 129 öncesinin sayısı, ve 129'dan sonra
> deneme koşulmadı. Kullanıcı yine de istedi, ve karar kullanıcınındır. Sebebi araç
> karşılaştırmasından: `NotebookEdit`'in insert'i satır numarasıyla değil **`cell_id`** ile
> çalışıyor — yapılandırılmış bir dosyaya yapı-farkındalıklı ekleme, Anthropic'in de verdiği
> biçim. Ve madde bir hız işi olmasa bile bir **hata sınıfını** kapatıyor: konumu model vermediği
> için yanlış veremiyor.
>
> **Koşma sırası: 131 → 132 → 128 → 130.** 131 ile 132 var olan araçların biçimini düzeltiyor, 128
> yeni aracı getiriyor, 130 en sonda — kelime tavanı 128'in kısalttığı cümleden açılıyor.
> Numaralar kaymıyor: 131 ile 132 sondan verildi, koşma sırası belgedeki sıra değil bu satır.

- **Ne çalışır:** `add_frames(name, frames)`: kod yapı dosyasını okur, verilen kareleri `frames`
  listesinin sonuna ekler, yazar. Çapa yok, *"tam bir kez"* şartı yok — dolayısıyla okuma
  gerekçesi de yok. `build_prompts`'un zaten yürüdüğü yol *(FOUNDATION 5: kararı kod verir)*, ve
  prompt+'ın beşerli ritmi metinden koda geçmez: uzun cevabın sonunda kalite düşer, o yüzden
  model yine parça parça çağırır — ama her parça arasında okumaz.
- **Nasıl görülür:** 25 karelik bir senaryo kurulurken `read_file` yalnız açılıştaki çifte
  gidiyor; kare ekleme adımlarının arasında hiç okuma yok.
- **Aracın cevabı sayı taşır:** kaç kare eklendi, dosya artık kaç kare tutuyor. İki iş birden
  görüyor — model durumu okumadan bilir, ve eklemenin bilinen tuzağı *(idempotent değildir; aynı
  çağrı iki kez koşarsa kareler iki kez girer)* modelin gözü önünde kalır.
- **Araştırmanın işaret ettiği yol bu:** Amazon Science'ın CODESTRUCT'ı string düzenleme yerine
  *ayrık, iyi tanımlı işlemler* öneriyor, ve trueline-mcp aynı sorunu çapaya kimlik takarak
  çözüyor. Bizde ikincisine gerek yok: hedef dosya zaten yapılandırılmış, eklenen şey serbest
  metin değil şeması yazılı bir nesne.
- **Değişmeyen:** `edit_file` durur — var olan bir kareyi düzeltmek ve harita girdisi değiştirmek
  hâlâ onun işi *(113'ün düzenleme yolu)*. `build_prompts` ve şema aynen kalır.
- **İlişkisi:** 125 tanımı düzeltti, bu madde tanımın gerektirdiği okumayı ortadan kaldırıyor.
  96 ve 98'in kalıbı: modelin elle yaptığı iş koda iniyor.

### Madde 129 — Okunan dosyalar bir bağlam kabında, hep güncel durur

> **Tasarımı kullanıcının kendi cümlesiyle döndü** *(29 Ağustos)*: *"tool call olunca biz ordan
> döneriz + ekleriz contexte, sonraki turlarda ordan kullanır direkt"* ve *"bir de her tool
> çıktısı değil, çıktısı anlam taşıyanlar — read file gibi, read schema gibi."* İlk taslak eski
> sonucu **silmeyi** öneriyordu; bu daha iyisi: eskisini silmek yerine tek bir yerde **güncel**
> tutmak. Silinen bilgiyi model yeniden okumak zorunda kalır, güncel tutulanı okumaz.

- **Ne çalışır:** bir `read_file` sonucu konuşmaya yazıldığı yerde donuyor — dosya sonra değişse
  de o mesaj ilk okunan hâli taşımaya devam ediyor. Model bunu bildiği için tekrar okuyor, ve
  ikinci kopya da yanına ekleniyor; yedinci denemede aynı dosya üç kez, her biri tur boyunca her
  isteğe binerek. Bunun yerine: bu sohbetin okuduğu dosyalar bir **kapta** toplanır, ve kap her
  istekte diskten tazelenerek isteğin sonunda gider. Kap turlar arası yaşar — ikinci mesajda
  model dosyayı yeniden okumaz, zaten önündedir.
- **Kapta ad durur, içerik değil.** Kabın kendisi kayıttan türetilir: `Message.calls` hangi aracın
  hangi dosyaya dokunduğunu zaten yazıyor *(Madde 66 ve 78)*, ve içerik her istekte diskten
  okunur. Yeni bir disk alanı yok, göç yok — ve içerik hiçbir zaman kopyalanmadığı için
  bayatlayamaz. Silinen dosya kaptan kendiliğinden düşer.
- **Ne girer:** çıktısı anlam taşıyanlar — `read_file` ve `read_prompt_structure_schema`.
  `create_file`, `edit_file`, `build_prompts` girmez: onların çıktısı zaten tek cümle. Okunmuş
  bir dosya sonradan yazılırsa kap onu güncel gösterir; okunmamış bir dosya yazılmakla kaba
  girmez.
- **Kaç tane:** son 5 *(kullanıcı kararı)*. Sohbet uzadıkça kap büyümez.
- **Nasıl görülür:** aynı dosyayı iki kez okuyan bir tur ikinci kopyayı taşımıyor; bir turda
  yazılan dosyanın yeni hâli sonraki raundda kapta görünüyor; ikinci mesaj `read_file` ile
  açılmıyor.
- **Önbellek:** kap isteğin sonunda, zaten her raundda değişen bölgede — konuşmanın kendisi
  değişmediği için Madde 124'ün anahtarladığı prefix bozulmaz. Anthropic'in `clear_tool_uses`'ı
  ortadaki mesajı düzenlediği için prefix'i geçersiz kılıyor ve `clear_at_least` ile kendini
  korumak zorunda kalıyor *([araştırma](../research/2026-08-29-queenagent-arac-tasarimi-arastirma.md))*;
  kap o bedeli hiç ödemiyor.
- **İlişkisi:** 127 adları isteğe koydu, bu madde içerikleri — ikisi de aynı yerde, isteğin
  kuyruğunda. 92 tavanı koydu, 124 önbelleği taktı. 128'in `add_frames`'i bu maddeden sonra
  hâlâ değerli *(çapayı geri yazmak çıktı token'ı yakar)* ama artık zorunlu değil.

### Madde 130 — prompt+ turu da menüyle bitmez

- **Ne çalışır:** yedinci denemenin kapanışı üç şıklı bir menüydü — *"bir kareyi değiştirelim ·
  sadece belirli kareleri göster · başka bir şey ekle"* — ve öncesinde model `build_prompts`'un
  yazdığı dosyayı okuyup 25 promptu cevaba döktü. Dosya zaten projede. Madde 112 bu kuralı taban
  yönergeye yazdı; prompt+ turunda tutmuyor, çünkü skill metni isteğin son sözü ve kapanış
  hakkında bir şey söylemiyor. prompt+ kendi kapanışını söyler: kurulan dosya cevabın kendisidir,
  promptlar geri basılmaz, menü açılmaz.
- **Nasıl görülür:** kurma turu dosyayı adıyla söyleyip bitiyor; ne prompt listesi ne şık listesi.
- **Yer nereden geliyor:** 128 prompt+'ın kare ekleme cümlesini kısaltıyor; kelime tavanı bu
  madde için orada açılıyor *(123'ün kuralı: bir cümle ancak bir cümle silinerek girer)*.
- **İlişkisi:** 112 tabanı, 118 akışın kapanışını yazdı; bu üçüncüsü.

### Madde 131 — `read_file` satır numarasıyla döner

- **Ne çalışır:** okuma bugün ham metin veriyor, yani model dosyayı satır numarası olmadan
  görüyor — ve `edit_file`'ın çapasını seçerken bir metnin dosyada kaç kez geçtiğini ancak gözüyle
  tarayarak kestiriyor. Kareler birbirine benzediği için kestirim tutmuyor ve *"appears 3 times"*
  reddi geliyor. Claude Code'un `Read`'i `cat -n` biçiminde dönüyor. Okuma numaralı döner, ve
  **129'un kabı da aynı biçimde** — yoksa aynı dosya modelin önünde iki ayrı şekilde durur.
- **Nasıl görülür:** bir dosya okunduğunda her satır numarasıyla geliyor, bağlam kabındaki aynı
  dosya da numaralı, ve `edit_file` numarasız metinle eşleşmeye devam ediyor.
- **Köprü araç tanımında:** çapayı yazarken satır numarası önekinin atılacağı `edit_file`'ın
  tanımına bir cümle olarak girer. Claude Code'un Edit'i de bunu tanımında söylüyor — numaralı
  okuma ile numarasız eşleşme arasındaki bağ kodda değil, modele söylenen cümlede duruyor.
- **Değişmeyen:** eşleşmenin kendisi. `_edit` diskteki ham içerikte arıyor, ve şart yerinde
  kalıyor — Anthropic'in kendi aracı da aynı şartı koyuyor.
- **İlişkisi:** 129 kabı kurdu, bu madde kabın ve okumanın biçimini tek biçimde birleştiriyor.
  132 aynı derdin öteki yarısı.

### Madde 132 — `edit_file` `replace_all` alır

- **Ne çalışır:** çapa birden çok kez geçiyorsa düzenleme reddediliyor ve modelin tek çıkışı
  çapayı büyütüp baştan denemek — bir raunt yanıyor, ve büyüyen çapa daha çok çıktı token'ı
  demek. Claude Code'da ret tek çıkış değil: *"Claude either supplies a longer string with enough
  surrounding context, or sets `replace_all: true` to replace them all."* Araç aynı bayrağı alır.
- **Nasıl görülür:** aynı metnin üç yerde geçtiği bir dosyada `replace_all` ile tek çağrıda üçü de
  değişiyor; bayraksız çağrı hâlâ *"appears 3 times"* diyor.
- **Kararı verilmiş:** varsayılan **ret**. Bayrak verilmemişse bugünkü davranış aynen duruyor —
  sessizce hepsini değiştirmek, tek bir yeri düzeltmek isteyen modele fark ettirmeden fazlasını
  yaptırırdı, ve o dosya kullanıcının *(1. ilke)*.
- **İlişkisi:** 131 çapayı seçmeyi kolaylaştırıyor, bu madde çakıştığında çıkışı açıyor. İkisi de
  128'in iki bedelinden birine dokunuyor, araç eklemeden.

---

# Blok 12 — Sekizinci denemenin çıkardıkları · madde madde · **bitti**

> **Dördü de koşuldu** *(29 Ağustos)*, sırası 133 → 134 → 135 → 136. Blok 4 gibi açık uçlu:
> dokuzuncu deneme madde çıkarırsa 137'den devam eder.
>
> **136 denemeden değil, 135'in koşusundan doğdu** — aynı hata `_build`'da da duruyordu ve orası
> 135'in kapsamı dışındaydı. Kapsam dışında görülen bir şey kendi maddesini alır; sessizce
> düzeltilirse ne testi ne kaydı olur.

> Sekizinci deneme *(29 Ağustos, Blok 11 koşulmuş dalda)*: iki mesajlık bir sohbet **50k tavanına
> çarpıp kapandı**. Turlar 6 ve 5 adımdı, kartlarında 48.8k ve 51.4k yazıyordu.
>
> **Sayılar doğru, tavanın onları okuması yanlış.** `usage.sent` bir turun *bütün raundlarının
> toplamı* — `stream_answer` her raundu üstüne ekliyor — ve tavan o toplamı bağlam boyu sanıyor.
> Sohbetin gerçek bağlamı ~10-12k'ydı, yani tavanın beşte biri. `last_sent`'in kendi docstring'i
> varsayımı yazmış: *"no single turn is large enough to cross it on its own"*, ve bir tur
> raundları toplandığı için tek başına geçebiliyor.
>
> **Ölçü dışarıdan da bakıldı** *(kullanıcının sözü: "araştır claude ne kadar harcıyor")*. Claude
> Code'un taze bir oturumu daha ilk prompt yazılmadan ~4.2k sistem promptu ve ~1.8k CLAUDE.md
> taşıyor; dosya okumaları 1.1k-2.4k; beş orta boy dosyaya atıf 30k'yı buluyor. QueenAgent'ın
> istek başına ~8-10k'sı aynı mertebede — **anormal olan harcama değil, tavanın onu okuma
> biçimi.** Kaynaklar:
> [Claude Code Context Window](https://getunblocked.com/blog/claude-code-context-window/),
> [Token Efficiency 2026](https://www.futureproofing.dev/resources/ai-native-team/claude-code-vs-cursor-token-efficiency-2026).
>
> Aynı koşu iki geri okuma daha gösterdi, ve ikisi 134 ile 135. Blok 4 gibi açık uçlu.

### Madde 133 — Tavan bağlamı okur, kart harcamayı göstermeye devam eder

- **Ne çalışır:** `usage.sent` turun raundlarının toplamı, ve üç yer birden onu okuyor — kartın
  altındaki sayı, composer'ın dairesi, ve tavanın kendisi. Biri doğru okuyor, ikisi yanlış:
  tavan bir **bağlam** tavanı, ve sabitin kendi açıklaması bunu söylüyor *("models get worse as
  the input grows and what sits in the middle of a long request goes unread")* — o cümle tek bir
  isteğin boyu hakkında. `Usage` ikinci bir sayı taşır: turun **son raundunun** `sent`'i, yani tur
  bittiğindeki bağlam boyu. Tavan ve daire onu okur.
- **Nasıl görülür:** altı adımlık bir turun kartında hâlâ turun toplamı yazıyor; dairenin doluluğu
  ondan küçük; ve iki mesajlık bir sohbet tavana çarpmıyor.
- **Kararı verilmiş** *(kullanıcı kararı, 29 Ağustos)*: **kart turun toplamını gösterir** — bir
  cevabın kaça mal olduğu sorusunun cevabı o. **Daire bağlamı gösterir**, çünkü göstergenin tek
  işi durmadan önce yaklaştığını söylemek, ve tavanla aynı şeyi ölçmezse o işi yapamaz. İki
  sayının farklı olması doğru: biri harcama, öteki doluluk.
- **Tavan 50k'da kalır** *(kullanıcı kararı, 29 Ağustos)*. Gerekçesi zaten gerçek bağlam için
  yazılmıştı — pencerenin beşte biri, ve uzun girdide düşen kalite. Bugüne kadar yaklaşık beşte
  bir sıkılıkta çalıştı; düzeltince sohbetler kabaca beş kat uzuyor, ve bu bilinen ve kabul edilen
  sonuç.
- **Sayı saklanır, türetilemez:** toplamdan son raundu geri çıkarmanın yolu yok. Eski kayıtlar 0
  okur, yani hiçbiri dolu sayılmaz — göç yazılmıyor, alan bir sonraki turda kendiliğinden doluyor,
  ve müsamahakâr taraf doğru taraf: bir sohbeti yanlışlıkla kapatmaktansa bir tur geç kapatmak.
- **Ön yüz değişmiyor.** Uç zaten `context: {sent, ceiling}` gönderiyor ve gösterge onu okuyor;
  değişen yalnız o alanın hangi sayıyı taşıdığı. `dist` derlenmiyor.
- **İlişkisi:** 92 tavanı koydu, 68 ile 76 ölçüyü kurdu, 83 kartı yerleştirdi. Bu madde ikisinin
  aynı sayıya bakmasını bitiriyor.

### Madde 134 — Akış yazdığı planı geri okumaz

- **Ne çalışır:** akış planı `write_plan` ile yazdıktan hemen sonra aynı dosyayı `read_file` ile
  geri okudu. 125 tanımı koşullu yapmıştı — *"read it first if this turn has not seen it"* — ve
  tur onu az önce yazmıştı. Şüphe akış metninde: 1. adım *"A plan already there is that memory:
  read it and carry on from the step it left open"* diyor, ve model kendi yazdığını *"already
  there"* saymış olabilir. **Kök neden koşuda doğrulanır** *(Blok 9 kuralı: önce yaz, çözerken
  araştır)*.
- **Nasıl görülür:** akışın ilk turu planı yazıp okumadan devam ediyor; **var olan** bir planla
  açılan taze bir sohbet onu yine okuyor.
- **Değişmeyen:** planın hafıza olması. Yarım kalan iş yeni sohbetten sürüyor ve o sohbet planı
  okuyor — kalkan yalnız kendi yazdığını okumak.
- **İlişkisi:** 107 ritüeli indirdi, 125 tanımları düzeltti, 126 işaretlemeyi tek dokunuşa indirdi.
  Bu dördüncüsü, ve aynı kalıp: yasak eklemek değil, çelişkiyi kaldırmak.

### Madde 135 — Karakter önizlemesi promptu cevabında taşır

- **Ne çalışır:** `build_character_prompts` *"Wrote 1 prompts to ..."* diyor ve kurduğu promptu
  taşımıyor, o yüzden model önizlemeyi kullanıcıya göstermek için dosyayı `read_file` ile geri
  okudu. Suç modelin değil: Madde 98 bu aracı **bir bakış** diye tanımladı, ve bakılacak şeyi
  döndürmeyen bir bakış bir okuma daha demek. Araç kurduğu promptları cevabında verir.
- **Nasıl görülür:** bir karakter önizlemesi isteniyor ve model promptu dosyayı okumadan
  gösteriyor.
- **`build_prompts` bunu almaz.** 130 promptların geri basılmamasını söylüyor, ve 25 promptu
  cevaba koymak tam da onu davet ederdi. Ayrım işin kendisinde: önizleme bakılmak için var, kurulan
  liste dosyada durmak için.
- **İlişkisi:** 98 aracı getirdi, 130 kapanışı yazdı, 128 ile 129 aynı israfın öteki yarılarını
  aldı.

### Madde 136 — Tek kare tek prompt sayılır

- **Ne çalışır:** `build_prompts`'un cevabı `f"Wrote {len(prompts)} prompts to ..."` diyor — ham
  sayı, sabit çoğul. Tek kareli bir senaryoda ekranda **`Wrote 1 prompts`** yazıyor. Aynı
  `return`'ün bir satır altındaki `outcome` doğru sayıyor, çünkü `counted()` çağırıyor: bir sonuç,
  iki farklı gramer.
- **Nasıl görülür:** tek kareli bir yapıdan prompt kurulduğunda cevap `1 prompt` diyor; iki
  karelide `2 prompts` demeye devam ediyor.
- **135'in kapsamı dışındaydı ve o yüzden ayrı madde.** Aynı hata `build_character_prompts`'ta da
  vardı ve orada düzeldi; buraya uzanmak istenmemiş bir değişiklik olurdu. Kullanıcıya raporlandı,
  kullanıcı istedi *(29 Ağustos)*.
- **Değişmeyen:** cevabın geri kalanı. `build_prompts` promptlarını hâlâ geri vermiyor — 130'un
  kuralı ve 135'in sınırı yerinde; değişen tek şey bir kelimenin tekili.
- **İlişkisi:** 135, ve `counted()`'ın kendi cümlesi: *"One of a thing is one of it, not one of
  them."*

---

## Açık sorular

Hepsi ilgili maddenin spec'inde kapanır; yol haritası hiçbirini beklemez.

| Soru | Nerede kapanır |
|---|---|
| ~~Tool call'lar sohbet kaydına yazılacak mı, ne kadarı gösterilecek~~ | 66 — kapandı |
| ~~Durdurulan cevabın yarısı kaydedilecek mi~~ | 67 — kapandı |
| ~~Tüketim sayısı nerede duracak~~ | 68 — kapandı |
| ~~Tool call satırının alt satırı ne söyleyecek~~ | 78 — kapandı: çağrının sonucunu söylüyor |
| ~~Üstüne yazma kuralı nerede istisna tutacak~~ | 69 — kapandı: istisna yok. `create_file` alınmış bir adı reddediyor ve `edit_file`'ı gösteriyor; numaralı kopya düştü |
| ~~Bugünkü yapı dosyalarındaki sayı etiketleri temizlenecek mi~~ | **Kapandı** — [karar defteri](../../2026-08-27-queenagent-skill-kararlari.md) K26, K27: dosyalar olduğu gibi kalıyor, tanımda kalan etiketi kural kitabı yakalıyor |
| ~~Bağlamın hangi yolla yönetileceği~~ | **Kapandı** — Blok 5'in 92, 93 ve 91'i cevapladı |
| ~~Model seçici kalkacak mı, eski kayıtlardaki model adlarına ne olacak~~ | 72 — kapandı: ikisi de olduğu gibi kalıyor |
| ~~Diskte duran dosyalar dönüştürülecek mi~~ | **Kapandı** — K26: dönüştürülmüyor, kod eksik alanı atlıyor |
| ~~Hangi skiller düşecek~~ | 94 — kapandı: prompt+ dışında hepsi. Yerine gelen akış skill'i Madde 101 *(K16)* |
| ~~v5'in 74'ü ile 94 aynı işi iki belgede anlatıyor. Hangisi ötekine devredecek?~~ | **94 devraldı** — 74 açık bir soruydu, 94 o sorunun cevabını taşıyor |
| ~~94'ün silmesiyle kaybolacak bilgiden hangisi kalan skill'e, hangisi taban yönergeye taşınacak~~ | **Hiçbiri** *(kullanıcı kararı, 27 Ağustos)* — kalan metin bugünkü hâliyle kalıyor. Kaybın tek tek sayımı [94'ün spec'inde](../specs/2026-08-27-queenagent-m94-tek-skill-testler-design.md) |
| ~~Şema kişi sayısı dışında başka ne alıyor~~ | 95 — kapandı |
| ~~İzin sorusunun ekranda nasıl göründüğü ve bekleyen turun nasıl taşındığı~~ | 99 ve 102 — kapandı |
| ~~Akış metninin adımları hangi cümlelerle söylediği~~ | 101 — kapandı |
| ~~Kare eklemek kendi aracını mı ister, yoksa `edit_file` yeter mi~~ | **128 — kapandı** *(kullanıcı kararı, 29 Ağustos)*: kendi aracını ister. 129 okuma gerekçesini kaldırdı ama çapanın çıktı token'ı ve çakışma retleri duruyor, ve konumu koda almak bir hata sınıfını kapatıyor |

**Açık satır kalmadı** *(28 Ağustos)*: 65'ten 102'ye kadar sorulan her şey ya koşuldu ya karara
bağlandı. Son üçü Blok 6'nındı, ve üçü de kendi maddesinin spec'inde kapandı.

76'dan 85'e kadar olanlar bu tabloda yok: onunun da kararı verilmiş, verilecek bir şey kalmadı.
81'in
sorusu vardı — kelimeden önce durdurulan turun diske yazılıp yazılmayacağı — ve maddeye gelindiğinde
kullanıcıyla konuşulup kapandı.

**Numara sorusu kapandı:** sayaç tek. Cümle 28 Ağustos'ta *"bu belge 65'ten 103'e kadarını aldı,
bundan sonra 104'ten devam eder"* diye yazılmıştı; dört blok daha eklendi ve kural aynen işledi.
Bugünkü hâli: belge **65'ten 136'ya** kadarını aldı, ve bundan sonra madde nereye eklenirse
eklensin **137'den** devam eder.

## Kapsam dışı

**Prompt listesinin tek ve tanımlı bir yeri olması** *(kullanıcı kararı, 25 Ağustos)* — listeden
çıkarıldı. İlk yazımı *"backlog'da kalıyor"* diyordu, ve
[BACKLOG.md](../../../queen-agent/BACKLOG.md) onu hiç taşımadı — orada tek madde `BREAK`. Cümle
koda değil kendine uyduruldu *(29 Ağustos)*: maddenin tek kaydı bu satır.

**Bir kısmı kendiliğinden kapandı:** 69'dan beri `create_file` alınmış bir adı reddedip
`edit_file`'ı gösteriyor, yani aynı listenin numaralı ikinci kopyası artık doğmuyor. Kalanı
listenin *nerede* duracağıydı, ve `build_prompts` onu da bir yere bağladı — çıktı yapı dosyasının
adından türeyen tek bir dosya, ve her koşuda üstüne yazılıyor. Bugün ayakta bir şikâyet yok;
çıkarsa yeni bir madde olarak doğar.

**Beş tasarım promptunun gönderilmesi** *(26 Ağustos)* — [belgesi](2026-08-25-queenagent-v5-tasarim-promptlari.md)
duruyor ama gönderilmiyor. Tasarım kullanıcıdan döndü, ve 78 ile 79 onun cümlelerini uyguluyor.

**Proje çapası dosyası** *(kullanıcı kararı, 26 Ağustos)* — her projede "bu proje nedir, karakterler
kim" diyen ve her isteğin başına konan bir dosya. Ajan araçlarının kullandığı bir kalıp, ama burada
gerek görülmedi: projede zaten dosyalar var ve modelin onları listelemesi ucuz.

**Okumayı alt ajana taşımak** *(kullanıcı kararı, 26 Ağustos)* — dosya okumanın ayrı, sınırlı bir
bağlamda olması ve ana konuşmaya yalnız özetin dönmesi. Araştırmanın en büyük kaldıracı, ama en büyük
işi de. Sonraya bırakıldı: 91'in plan kipi zaten her göreve temiz bir bağlam veriyor, ve faydasının
çoğunu ondan alıyoruz. Ölçü hâlâ sorun gösterirse açılır.

**Özetleme** — 92 tavanı koydu, özet yazmayı getirmedi. Bekleyen bir kaydı yok; istenirse yeni bir
madde olarak doğar.

**Kip değiştirmenin önbellek maliyetini optimize etmek** — araç listesi isteğin en başında durduğu
için kip değişimi o tek isteği tam fiyattan ödetiyor. 40k'lık bir sohbette bu üç kuruş *(xAI fiyat
sayfasından doğrulandı, 26 Ağustos)*. Etrafından dolaşmaya değmez.

**`BREAK`** — kalabalık karede karakterleri ayırmanın bilinen ilacı, ve şartı queen-editor'ün bir
düğüm açması. İki backlog'da duruyor *(K12–K15)*.

**Okumanın tavanı ve sayfalanması** *(29 Ağustos, araç karşılaştırması)* — Claude Code'un `Read`'i
büyük bir dosyayı kapatıp `PARTIAL view` notuyla `offset` ile `limit`'i gösteriyor; bizim
`read_file`'ın tavanı yok, ve 129'dan beri okunmuş dosya her isteğe biniyor. Madde yazılmadı çünkü
**ölçü yok**: bugüne kadar görülen en büyük dosya 156 satır, ve 92'nin tavanı bağlamın tamamını
zaten koruyor *(FOUNDATION 3)*. Büyük bir dosya bir turu tıkarsa madde olarak doğar.

**Tam dosyayı üstüne yazan bir yol** *(29 Ağustos)* — Claude Code'un `Write`'ı var olan dosyayı
üstüne yazıyor; bizde `create_file` alınmış adı reddediyor, yani tek değiştirme yolu `edit_file`
*(plan dosyaları hariç — `write_plan` üstüne yazıyor)*. Fark gerçek: küçük bir dosyada beş
düzenleme yerine tek yazım daha ucuz olurdu. Ama bu **Madde 69'un kararı** ve kullanıcının emeğini
koruyor; değişmesi 69'un yeniden açılmasını ister, ve bu koşuda açılmıyor.

**İçerik araması** *(29 Ağustos)* — Claude Code'da `Glob` ile `Grep` var, bizde ne arama ne
listeleme *(127 `list_files`'ı da kaldırdı)*. Gerek görülmedi: bir proje birkaç dosya tutuyor ve
adları 127'den beri her isteğin sonunda duruyor. Adlar bir satıra sığmayacak kadar çoğalırsa
yeniden bakılır.

Ayrıca: Grok Build dışında model eklemek · sohbet arama · çok kullanıcı ve paylaşım · defterin
kendisi (v4'te kapandı, bu koşuda değişmiyor) · Drive'ın yavaşlığı (ölçülmemiş, FOUNDATION 3).

## Nasıl çalışacağız

Her madde, iki cümlelik bir işte bile, iki tam turdan geçer — önce yalnız testler yazılıp kırmızı
commit'lenir, sonra kod yazılıp yeşile döndürülür. İkisinin de kendi spec'i ve kendi planı olur.

**Blok 1 durmadan koşuldu**, kullanıcı dördünü sonunda topluca denedi — ve o deneme Blok 3'ü
doğurdu, yani yöntem çalıştı. **Blok 3 de durmadan koşuldu** ve aynı şekilde denendi; o deneme de
Blok 4'ü doğurdu. **Blok 4'te madde tek tek gelir**: kullanıcı bir düzeltme söylüyor, o madde iki
turda bitiyor, sonra sıradaki konuşuluyor. **Blok 2'de her madde kullanıcıyla açılır**: spec'in
açık soruları o maddeye gelindiğinde konuşulur, sonra koşulur. **Blok 5, Blok 6 ve Blok 7 de Blok
4'ün ritminde**: bir madde iki turda biter, sonra sıradaki konuşulur.

Ön yüze dokunan her madde `dist`i **kaynağıyla aynı commit'te** derleyip commit'ler; FOUNDATION'ın
3. kararı ve `test_dist_is_committed.py` bunu zaten zorluyor. Yerel yol birincil: `python main.py`.
