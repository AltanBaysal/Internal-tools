# QueenAgent v5 Yol Haritası — görmek, ölçmek, sadeleşmek

**Tarih:** 2026-08-25 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [queen-agent/BACKLOG.md](../../../queen-agent/BACKLOG.md) — kullanıcının kendi
cümleleriyle yazılmış maddeler. Bu belge onlardan türer; ters yön yok. Kapsam ya da karar değişirse
önce backlog düzelir.
**Numaralar** v4'ten devam eder (64'te bitti). **42 madde, 7 blok** — 65'ten 106'ya.

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

## Yedi blok

Koşu yediye ayrılıyor, ve ayrım **kimin koştuğu**. Koşma sırası belgedeki sıradır:

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
- **Blok 7 (104-106) madde madde koşuldu — bitti.** Üçüncü denemenin çıkardıkları: prompt yüzeyi
  koşusundan sonra defter denendi *(28 Ağustos)* ve üçü de sohbet ekranından çıktı. Aynı gün üçü de
  iki turda koşuldu. Blok 4 gibi açık uçlu: deneme sürdükçe madde eklenir, numaralar sondan
  verilir.

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
| Prompt listesi karışıyor | **bu koşuda yok** — backlog'da kalıyor |

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

**Açık satır kalmadı** *(28 Ağustos)*: 65'ten 102'ye kadar sorulan her şey ya koşuldu ya karara
bağlandı. Son üçü Blok 6'nındı, ve üçü de kendi maddesinin spec'inde kapandı.

76'dan 85'e kadar olanlar bu tabloda yok: onunun da kararı verilmiş, verilecek bir şey kalmadı.
81'in
sorusu vardı — kelimeden önce durdurulan turun diske yazılıp yazılmayacağı — ve maddeye gelindiğinde
kullanıcıyla konuşulup kapandı.

**Numara sorusu kapandı:** sayaç tek. Bu belge 65'ten 103'e kadarını aldı, ve bundan sonra madde
nereye eklenirse eklensin 104'ten devam eder.

## Kapsam dışı

**Prompt listesinin tek ve tanımlı bir yeri olması** *(kullanıcı kararı, 25 Ağustos)* — listeden
çıkarıldı, backlog'da kalıyor. Not: 69 üstüne yazma kuralını değiştirdiğinde bu maddenin bir kısmı
kendiliğinden kapanabilir; kalanı backlog'da beklemeye devam eder.

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
