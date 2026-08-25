# QueenAgent v5 Yol Haritası — görmek, ölçmek, sadeleşmek

**Tarih:** 2026-08-25 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [queen-agent/BACKLOG.md](../../../queen-agent/BACKLOG.md) — kullanıcının kendi
cümleleriyle yazılmış maddeler. Bu belge onlardan türer; ters yön yok. Kapsam ya da karar değişirse
önce backlog düzelir.
**Numaralar** v4'ten devam eder (64'te bitti). **10 madde, 2 blok** — 65'ten 74'e.

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

## İki blok

Koşu ikiye ayrılıyor, ve ayrım **kimin koştuğu**:

- **Blok 1 (65-69) tek başına koşulur.** Beş madde; her biri kapalı uçlu, kararı verilmiş,
  bir öncekine yaslanıyor. Kullanıcı bunları koşunun sonunda topluca dener.
- **Blok 2 (70-74) kullanıcıyla beraber, adım adım koşulur** *(kullanıcı kararı, 25 Ağustos)*.
  Beşinin de ya çıktının doğruluğuna ya modelin davranışına dokunduğu için karar aralarında
  veriliyor, sonunda değil.

Blok 2'nin kendi içindeki sıra kullanıcının söylediği sıradır; araya giren tek madde Grok Build ve
onun yeri zorunlu (aşağıda).

### Tasarım bu koşuda kodu takip ediyor *(kullanıcı kararı, 25 Ağustos)*

66, 67 ve 68 tasarımda hiç karşılığı olmayan üç eleman doğuruyor, ve normalde bu deponun kuralı
tersidir: tasarım görsel şartnamedir, kod onu izler. Bu koşuda beklenmiyor — elemanlar önce kodda
doğuyor, [tasarım promptları](2026-08-25-queenagent-v5-tasarim-promptlari.md) sonra atılıyor ve
tasarım koda uyduruluyor.

Bedeli önden biliniyor ve kabul edildi: renkler ve ölçüler var olan görsel dilden türetiliyor ama
kararı veren tasarım değil, kod. Tasarım döndüğünde farklar çıkarsa ilgili maddenin üstüne ikinci
bir tur gelir. Bu, o turun sürpriz olmadığının kaydıdır.

### Sırayı zorlayan bağlar

- **Görmek, durdurmaktan önce.** Neyin sürdüğü ekranda yokken durdurma düğmesi neyi kestiğini
  söyleyemez. **66 → 67**.
- **Ölçü, optimizasyondan önce.** [FOUNDATION](../../../queen-agent/FOUNDATION.md) 3. ilke ölçülmemiş
  bir sorunu optimize etmeyi yasaklıyor. **68 → 71**, ve bu tek başına ölçüm maddesinin neden Blok
  1'de kaldığını açıklıyor: Blok 2 ona yaslanıyor.
- **Bağlam, modelden önce.** Grok Build'in penceresi 256k, bugünkü bağlam 300-500k. Bağlam işi
  bitmeden model değiştirilirse sohbetler pencereye sığmaz. **71 → 72**.
- **Taban yönerge, skillerden önce.** Skillerin üstündeki fazlalık ancak taban onu söylemeye
  başladıktan sonra bırakılabilir. **73 → 74**.

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
| Skiller tek bir akışta toplansın | 74 |
| Prompt listesi karışıyor | **bu koşuda yok** — backlog'da kalıyor |

"Çalışan cevap durdurulamıyor" iki madde oluyor: içindeki iki şikâyet ayrı işler ve biri ötekinin
şartı. Görünmek isteyen yarısı, "tool call'lar görünsün" maddesiyle aynı işe baktığı için 66'da
birleşiyor.

---

# Blok 1 — Tek başına

## Faz 1 — Açılış ve görünürlük

### Madde 65 — Uygulama taslak sohbet ekranına açılır

- **Ne çalışır:** uygulama bugün ilk projenin ekranına düşüyor ve oradaki yazma kutusunda skill ile
  model seçici yok; seçiciler yalnız sohbet ekranında. Açılış doğrudan boş bir taslak sohbete düşer,
  yani kullanıcı ilk saniyeden itibaren seçicilerin önündedir. Proje ekranı ayrı bir kapı olarak
  kalır.
- **Nasıl görülür:** uygulama açılıyor ve hiçbir şey yazmadan skill seçilebiliyor; proje ekranına
  sidebar'dan girilmeye devam ediliyor.
- **Yok:** yeni bir ekran — o ekran zaten var, değişen yalnız açılış adresi.

### Madde 66 — Tool call'lar sohbette görünür

- **Ne çalışır:** model bir cevabın içinde dosya listeliyor, okuyor, düzenliyor ve prompt kuruyor;
  bugün bunların hiçbiri ekranda yok, yalnız yeni bir dosya doğunca bir kart çıkıyor. Her çağrı
  olduğu anda sohbette görünür ve orada kalır — sonradan bakan da ne yapıldığını okur.
- **Nasıl görülür:** dosyaya dayanan bir soru soruluyor; cevap gelmeden önce hangi dosyanın okunduğu
  ekranda yazıyor. Sayfa yenilendiğinde o satırlar hâlâ duruyor.
- **Spec'te karara bağlanacak:** çağrıların sohbet kaydına yazılıp yazılmayacağı — yazılırsa kaydın
  biçimi değişir ve eski sohbetlerin bunu taşımadığı hesaba katılmalı. Bir de çağrının ne kadarının
  gösterileceği: adı mı, aldığı değerler de mi.

### Madde 67 — Çalışan cevap durdurulur

- **Ne çalışır:** başlayan bir cevabı kesmenin yolu yok; sohbetten çıkmak sunucudaki turu bitirmiyor
  ve geri dönüldüğünde cevap baştan isteniyor. Bir durdurma düğmesi gelir, cevap gerçekten kesilir ve
  sunucu tarafındaki tur da biter.
- **Nasıl görülür:** uzun bir cevabın ortasında durduruluyor; sohbet olduğu yerde kalıyor, geri
  dönüldüğünde kendi kendine yeniden başlamıyor.
- **Spec'te karara bağlanacak:** durdurulan cevabın yarısına ne olacağı. Bugünkü kural "cevap ya
  vardır ya yoktur" — yarım metin diske yazılmıyor. Durdurmak bu kuralı doğrudan sorguya çekiyor:
  kullanıcının okuduğu yarım cevap kaybolacak mı, yoksa durdurma onu kalıcı mı kılacak.

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
  toplamında mı, ikisinde de mi.

## Faz 2 — Dosyalar

### Madde 69 — Doküman güncellenir, yeniden yaratılmaz

- **Ne çalışır:** model var olan bir dosyayı düzeltmesi gerektiğinde yenisini yazıyor; yaratma işlemi
  üstüne yazmadığı için eski dosya yerinde kalıyor ve yanına numaralı bir kopya düşüyor. Sonuçta
  aynı işin iki sürümü duruyor ve bir sonraki adımın hangisini okuyacağı belirsizleşiyor. Düzeltmenin
  gerçekten düzeltme olması sağlanır — yönergeye bir cümle daha ekleyerek değil.
- **Nasıl görülür:** bir senaryo yazdırılıp arkasından düzeltiliyor; projede tek bir senaryo dosyası
  kalıyor ve içinde düzeltilmiş hâli duruyor.
- **Spec'te karara bağlanacak:** numaralı kopya üretmenin hangi durumlarda hâlâ doğru olduğu —
  bugünkü kural kullanıcının emeğini korumak için var ve tamamen kaldırılması o ilkeye dokunur.

---

# Blok 2 — Beraber, adım adım

Bu beş madde kullanıcıyla birlikte koşulur *(kullanıcı kararı, 25 Ağustos)*. Sıra kullanıcının kendi
sırasıdır; Grok Build araya giriyor çünkü şartı bir önceki madde.

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

### Madde 74 — Skiller tek akışta toplanır

- **Ne çalışır:** altı skill var ve hangisinin ne zaman geleceğini kullanıcı seçiyor. Bir kısmı
  gerçekten gereksiz; kalanlar da birbirini izleyen tek bir zincir — senaryo, kareler, karakter,
  promptlar, kontrol. Gereksizler düşer ve geri kalan tek bir akışa iner.
- **Nasıl görülür:** bir senaryodan prompt listesine kadar olan yol tek bir akışla yürüyor; kullanıcı
  arada skill değiştirmiyor.
- **Şartı:** 73 — taban yönerge ortak davranışı söylemeye başlamadan skillerden fazlalık
  bırakılamaz.
- **Spec'te karara bağlanacak:** hangi skillerin düşeceği. Bir aday şimdiden belli — promptları elle
  yazan yol, yapıdan kuran yolla aynı işi yapıyor ve karakteri elle kopyaladığı için FOUNDATION'ın
  5. ilkesiyle çarpışıyor. Karar yine de spec'te, beraber verilir.
- **Koşunun son maddesi:** bu bittiğinde skill seçicinin ne göstereceği de belli olur.

---

## Açık sorular

Hepsi ilgili maddenin spec'inde kapanır; yol haritası hiçbirini beklemez.

| Soru | Nerede kapanır |
|---|---|
| Tool call'lar sohbet kaydına yazılacak mı, ne kadarı gösterilecek | 66 |
| Durdurulan cevabın yarısı kaydedilecek mi | 67 |
| Tüketim sayısı nerede duracak | 68 |
| Üstüne yazma kuralı nerede istisna tutacak | 69 |
| Bugünkü yapı dosyalarındaki sayı etiketleri temizlenecek mi | 70 |
| Bağlamın hangi yolla yönetileceği | 71 — 68'in ölçüsüne bakarak |
| Model seçici kalkacak mı, eski kayıtlardaki model adlarına ne olacak | 72 |
| Hangi skiller düşecek | 74 |

## Kapsam dışı

**Prompt listesinin tek ve tanımlı bir yeri olması** *(kullanıcı kararı, 25 Ağustos)* — listeden
çıkarıldı, backlog'da kalıyor. Not: 69 üstüne yazma kuralını değiştirdiğinde bu maddenin bir kısmı
kendiliğinden kapanabilir; kalanı backlog'da beklemeye devam eder.

Ayrıca: Grok Build dışında model eklemek · sohbet arama · çok kullanıcı ve paylaşım · defterin
kendisi (v4'te kapandı, bu koşuda değişmiyor) · Drive'ın yavaşlığı (ölçülmemiş, FOUNDATION 3).

## Nasıl çalışacağız

Her madde, iki cümlelik bir işte bile, iki tam turdan geçer — önce yalnız testler yazılıp kırmızı
commit'lenir, sonra kod yazılıp yeşile döndürülür. İkisinin de kendi spec'i ve kendi planı olur.

**Blok 1 durmadan koşulur**, kullanıcı beşini sonunda topluca dener. **Blok 2'de her madde
kullanıcıyla açılır**: spec'in açık soruları o maddeye gelindiğinde konuşulur, sonra koşulur.

Ön yüze dokunan her madde `dist`i **kaynağıyla aynı commit'te** derleyip commit'ler; FOUNDATION'ın
3. kararı ve `test_dist_is_committed.py` bunu zaten zorluyor. Yerel yol birincil: `python main.py`.
