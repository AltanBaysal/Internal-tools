# QueenAgent v5 Yol Haritası — görmek, ölçmek, sadeleşmek

**Tarih:** 2026-08-25 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [queen-agent/BACKLOG.md](../../../queen-agent/BACKLOG.md) — kullanıcının kendi
cümleleriyle yazılmış maddeler. Bu belge onlardan türer; ters yön yok. Kapsam ya da karar değişirse
önce backlog düzelir.
**Numaralar** v4'ten devam eder (64'te bitti). **15 madde, 3 blok** — 65'ten 79'a.

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

## Üç blok

Koşu üçe ayrılıyor, ve ayrım **kimin koştuğu**. Koşma sırası belgedeki sıradır:

- **Blok 1 (65-68) tek başına koşuldu — bitti.** Dört madde; her biri kapalı uçlu, kararı verilmiş,
  bir öncekine yaslanıyor. Kullanıcı dördünü koşunun sonunda topluca denedi, ve o deneme Blok 3'ü
  doğurdu.
- **Blok 3 (76-79) tek başına koşulur.** Denemenin çıkardığı dört madde: bir hata ve üç ekran işi.
  Blok 2'den önce, çünkü biri Blok 2'nin şartı ve üçü bugün yanlış duran şeyler.
- **Blok 2 (69-75) kullanıcıyla beraber, adım adım koşulur** *(kullanıcı kararı, 25 Ağustos)*.
  Yedisinin de ya çıktının doğruluğuna ya modelin davranışına dokunduğu için karar aralarında
  veriliyor, sonunda değil.

**Blok numarası yazıldığı anı söylüyor, koşulacağı anı değil.** Blok 3 ikinci koşuyor; numarasını
kaydırmak, ona atıf yapan her cümleyi yalan yapardı — maddelerin numaralarında olduğu gibi.

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
- **Bağlam, modelden önce.** Grok Build'in penceresi 256k, bugünkü bağlam 300-500k. Bağlam işi
  bitmeden model değiştirilirse sohbetler pencereye sığmaz. **71 → 72**.
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

# Blok 3 — Denemenin çıkardıkları · tek başına

Blok 1 denendi ve dört şey çıktı: bir hata, bir yanlış çözüm, iki beğenilmemiş çizim. Dördü de
kapalı uçlu — hata bir sebebe bağlandı, kalan üçünü kullanıcı kendi cümleleriyle tarif etti — o
yüzden tek başına koşuluyor *(kullanıcı kararı, 26 Ağustos)*.

**Blok 2'den önce**, çünkü 76 Blok 2'nin şartı ve kalan üçü bugün ekranda yanlış duruyor. Yanlış
duran bir ekranın üstüne yeni iş koymak, ikisini birden düzeltmek zorunda bırakır.

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

# Blok 2 — Beraber, adım adım

Bu yedi madde kullanıcıyla birlikte koşulur *(kullanıcı kararı, 25 Ağustos)*. Sıra kullanıcının
kendi sırasıdır; Grok Build araya giriyor çünkü şartı bir önceki madde, 69 ise Blok 1'den buraya
geçti.

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

- **Ne çalışır:** sohbetler bugün başka bir modelle açılıyor ve menüde altı model duruyor. Grok Build
  hem varsayılan hem tek model olur; tek model kalınca model seçicinin de bir işi kalmaz.
- **Nasıl görülür:** yeni bir sohbet Grok Build ile açılıyor; ekranda seçilecek bir model kalmıyor.
- **Şartı:** 71. Grok Build'in penceresi 256k, bugünkü bağlam 300-500k — bağlam işi bitmeden bu madde
  açılırsa sohbetler pencereye sığmaz. Kullanıcının listesinde bu madde yoktu; buraya bu şart
  yüzünden girdi, çünkü şartı sona giden bir maddedir.
- **Spec'te karara bağlanacak:** model seçicinin tamamen kalkması mı yoksa görünmez olması mı; ve
  bugünkü sohbetlerin kayıtlarında duran model adlarına ne olacağı.

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
| Model seçici kalkacak mı, eski kayıtlardaki model adlarına ne olacak | 72 |
| Diskte duran etiket biçimli dosyalar dönüştürülecek mi | 75 |
| Hangi skiller düşecek | 74 |

76, 77 ve 79 bu tabloda yok: üçünün de kararı verilmiş, verilecek bir şey kalmadı.

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
doğurdu, yani yöntem çalıştı. **Blok 3 de durmadan koşulur**, aynı şekilde sonunda denenir.
**Blok 2'de her madde kullanıcıyla açılır**: spec'in açık soruları o maddeye gelindiğinde
konuşulur, sonra koşulur.

Ön yüze dokunan her madde `dist`i **kaynağıyla aynı commit'te** derleyip commit'ler; FOUNDATION'ın
3. kararı ve `test_dist_is_committed.py` bunu zaten zorluyor. Yerel yol birincil: `python main.py`.
