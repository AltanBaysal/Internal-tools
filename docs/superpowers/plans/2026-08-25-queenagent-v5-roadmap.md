# QueenAgent v5 Yol Haritası — görmek, ölçmek, sadeleşmek

**Tarih:** 2026-08-25 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [queen-agent/BACKLOG.md](../../../queen-agent/BACKLOG.md) — kullanıcının kendi
cümleleriyle yazılmış maddeler. Bu belge onlardan türer; ters yön yok. Kapsam ya da karar değişirse
önce backlog düzelir.
**Numaralar** v4'ten devam eder (64'te bitti). **21 madde, 4 blok** — 65'ten 85'e.

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

## Dört blok

Koşu dörde ayrılıyor, ve ayrım **kimin koştuğu**. Koşma sırası belgedeki sıradır:

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
- **Prompt dili, skiller toplanmadan önce.** Promptun neye benzeyeceğini söyleyen metin skillerin
  içinde duruyor. Dil değişmeden skiller tek akışta toplanırsa aynı metin iki kez yazılır.
  **75 → 74**.

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
Numarası ve bloğu yerinde: blok kimin koştuğunu söylüyor, ve 72 de kullanıcıyla açıldı. Kalan altı
madde sırasını koruyor.

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

### Madde 70 — Karede iki karakter varsa prompt iki kişiyi söyler

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

### Madde 71 — Bağlam yönetilir, iş bölünür

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

### Madde 75 — Promptlar cümle olarak çıkar

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

### Madde 74 — Skiller tek akışta toplanır

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

## Açık sorular

Hepsi ilgili maddenin spec'inde kapanır; yol haritası hiçbirini beklemez.

| Soru | Nerede kapanır |
|---|---|
| ~~Tool call'lar sohbet kaydına yazılacak mı, ne kadarı gösterilecek~~ | 66 — kapandı |
| ~~Durdurulan cevabın yarısı kaydedilecek mi~~ | 67 — kapandı |
| ~~Tüketim sayısı nerede duracak~~ | 68 — kapandı |
| Tool call satırının alt satırı ne söyleyecek | 78 |
| Üstüne yazma kuralı nerede istisna tutacak | 69 |
| Bugünkü yapı dosyalarındaki sayı etiketleri temizlenecek mi | 70 |
| Bağlamın hangi yolla yönetileceği | 71 — **76**'nın ölçüsüne bakarak |
| ~~Model seçici kalkacak mı, eski kayıtlardaki model adlarına ne olacak~~ | 72 — kapandı: ikisi de olduğu gibi kalıyor |
| Diskte duran etiket biçimli dosyalar dönüştürülecek mi | 75 |
| Hangi skiller düşecek | 74 |

76'dan 85'e kadar olanlar bu tabloda yok: onunun da kararı verilmiş, verilecek bir şey kalmadı.
81'in
sorusu vardı — kelimeden önce durdurulan turun diske yazılıp yazılmayacağı — ve maddeye gelindiğinde
kullanıcıyla konuşulup kapandı.

## Kapsam dışı

**Prompt listesinin tek ve tanımlı bir yeri olması** *(kullanıcı kararı, 25 Ağustos)* — listeden
çıkarıldı, backlog'da kalıyor. Not: 69 üstüne yazma kuralını değiştirdiğinde bu maddenin bir kısmı
kendiliğinden kapanabilir; kalanı backlog'da beklemeye devam eder.

**Beş tasarım promptunun gönderilmesi** *(26 Ağustos)* — [belgesi](2026-08-25-queenagent-v5-tasarim-promptlari.md)
duruyor ama gönderilmiyor. Tasarım kullanıcıdan döndü, ve 78 ile 79 onun cümlelerini uyguluyor.

Ayrıca: Grok Build dışında model eklemek · sohbet arama · çok kullanıcı ve paylaşım · defterin
kendisi (v4'te kapandı, bu koşuda değişmiyor) · Drive'ın yavaşlığı (ölçülmemiş, FOUNDATION 3).

## Nasıl çalışacağız

Her madde, iki cümlelik bir işte bile, iki tam turdan geçer — önce yalnız testler yazılıp kırmızı
commit'lenir, sonra kod yazılıp yeşile döndürülür. İkisinin de kendi spec'i ve kendi planı olur.

**Blok 1 durmadan koşuldu**, kullanıcı dördünü sonunda topluca denedi — ve o deneme Blok 3'ü
doğurdu, yani yöntem çalıştı. **Blok 3 de durmadan koşuldu** ve aynı şekilde denendi; o deneme de
Blok 4'ü doğurdu. **Blok 4'te madde tek tek gelir**: kullanıcı bir düzeltme söylüyor, o madde iki
turda bitiyor, sonra sıradaki konuşuluyor. **Blok 2'de her madde kullanıcıyla açılır**: spec'in
açık soruları o maddeye gelindiğinde konuşulur, sonra koşulur.

Ön yüze dokunan her madde `dist`i **kaynağıyla aynı commit'te** derleyip commit'ler; FOUNDATION'ın
3. kararı ve `test_dist_is_committed.py` bunu zaten zorluyor. Yerel yol birincil: `python main.py`.
