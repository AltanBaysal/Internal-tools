# Queen Editor v5 · Görev 9 — Tür kartları ve panel düzeni · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 3, Görev 9 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
34, 35, 36, 40, 41, 46 · **Tür:** yalnız ön yüz.

## Neden

Kuyruk paneli tek kart, tek sayı: "8 kare bekliyor". Video ve ses işleri kuyruğa girdiğinde bu sayı
yalanlaşır — üç türün işi tek sayıya toplanınca ne kadar foto, ne kadar video kaldığı görünmez, ve
motor türleri sırayla bitirdiği için "sıradaki hangisi" sorusunun cevabı ekranda hiç olmaz.

Tasarım kuyruğu **tür başına karta** bölüyor. Bu görev o düzeni **tek türle** kuruyor: bugün
ekranda yine tek kart var, ama artık o kart "foto işleri" kartıdır. Video geldiğinde ikinci kart
yeni kod değil, listeye giren yeni bir satır olarak doğar.

## Bugün ne var

Tek kart, beş hâli birden taşıyor:

| Hâl | Kartın söylediği |
|---|---|
| Üretiliyor | canlı nokta + "Üretiliyor" · **8** · "kare bekliyor" |
| Duraklatılıyor… | aynı kart, başlık değişir |
| Duraklatıldı | soluk nokta + "Duraklatıldı" · **8** · "kare bekliyor" |
| Üretim durdu | kırmızı nokta + "Üretim durdu" · **8** · sunucunun sebebi |
| Kuyruk tamamlandı / boş | kendi cümleleri |

Panelin başlığı şerit ikonunun adıyla aynı: "KUYRUĞU TAKİP ET". "Kuyruğu boşalt" ana butonun hemen
altında. Büyük sayı olağan metin renginde.

## Ne olacak

Panel iki katmana ayrılır:

**1. Tür kartları** — kuyruğun borcu olan her tür için bir kart, **üretim sırasında** (foto → video
→ ses). Her kart: durum satırı, büyük sayı (vurgu renginde), birim sözcüğü.

| Kartın durumu | Satır | Kartın görünümü |
|---|---|---|
| Motorun üstünde olduğu tür, koşu akarken | canlı mor nokta + "üretiliyor" | mor çerçeve |
| Öteki türler | soluk nokta + "sırada" | %55 opaklık |

Borcu biten türün kartı kaybolur.

**2. Koşu kartı** — koşunun kendisine ait, türe ait olmayan hâller: duraklatılıyor · duraklatıldı ·
üretim durdu · kuyruk tamamlandı · kuyruk boş. Koşu düz akarken bu kart **hiç çizilmez**; ne olduğu
tür kartında yazıyor.

Panel başlığı **"Kuyruk"** olur (şerit ikonunun adı "Kuyruğu takip et" kalır). "Kuyruğu boşalt"
esneyen bir boşluğun ardından **panelin en dibine** iner.

## Kararlar

### 1. Birim sözcüğü katmanın kendisine bağlıdır

Madde 35 sözcüğün "kare"den **"iş"e** dönmesini istiyor; madde 34'ün son cümlesi ise salt fotoluk
kuyrukta **"kare bekliyor"un süreceğini** söylüyor. İkisi de `kesin` damgalı ve doğrudan çelişiyor.

Çelişki, madde 35'in **kendi gerekçesi** okunduğunda çözülüyor: *"video ve ses işi yeni kare
açmadığı, var olan karenin katmanını ürettiği için «kare» saymak yanlış olacak."* Foto işi ise yeni
bir kare **açar** — orada kare saymak doğrudur.

**Karar:** birim sözcüğü karta göre değişir — **foto kartı "kare bekliyor"**, video ve ses kartları
**"iş bekliyor"** der. Bu, 35'in gerekçesini birebir uygular ve 34'ün cümlesini de bozmaz. Bugün
ekranda yalnız foto kartı olduğu için görünen sözcük değişmez.

### 2. Koşu kartı büyük sayısını tür kartına devreder

Bugün duraklamış ya da durmuş kuyrukta da büyük sayı koşu kartında duruyor. Tür kartları geldiğinde
aynı sayı iki yerde çizilirdi. Sayı **tür kartının**; koşu kartı yalnız koşunun hâlini söyler.

Sonuç: duraklamış kuyrukta ekranda iki kart olur — "foto · sırada · 8 kare bekliyor" ve
"Duraklatıldı". İkisi iki ayrı soruyu cevaplıyor: ne kadar iş var, ve motor neden çalışmıyor.

### 3. Panel tür listesini hazır alır, kendisi türetmez

Panel `queue` adında bir liste alır: `[{ layer, owed }]`, üretim sırasında ve yalnız borcu olan
türlerle. Bugün bu listeyi hazırlayan yer galeriyi sayan `useGeneration`; yarın arka uç sayacak.
Panel ikisini de bilmez — **kart çizmek listeden okumaktır**, ve Blok 5'te değişecek olan listeyi
dolduran yer, panelin kendisi değil.

Bu, bugünkü `pending` (dosya adları dizisi) prop'unun yerini alır: aynı sorunun iki cevabı olmaz.
Adları isteyen kimse kalmadı — panel sayıyor, proje ekranı "borç var mı" diye soruyor.

### 4. "Üretiliyor" hangi karta düşer

Bir tür kartı ancak **motor o türün işini yaparken** canlı olur: koşu gerçekten akıyorsa ve o an
elindeki işin türü o kartın türüyse. Duraklamış, durmuş ya da başka projenin tuttuğu koşuda hiçbir
kart canlı değildir — hepsi "sırada" der.

Motorun elindeki işin türü koşunun kendi raporundan okunur (`job.current.type`); türü yazmayan eski
bir plan foto işi demektir, arka uçtaki kuralın aynısı.

### 5. Büyük sayı vurgu rengine döner

Madde 46 `düzeltilecek`: vurgu rengi (mor) marka adının, sayaçların ve ana butonların rengi;
ekrandaki en büyük sayının olağan metin renginde durması v1'in görsel diline aykırı. Sayı artık
vurgu renginde. Kırmızıya dönme kuralı kalkar — durmuş koşuyu **koşu kartı** anlatıyor, sayı değil.

### 6. Bu görevde kalan her şey yerinde durur

Bitiş ve hata kartlarının ikiye ayrılması (37), "Hepsini tekrar dene" (38), kartın hâline göre renk
alması (39), boş kuyruk metni (42) ve açılış satırı (43) **Görev 10'un** işi. Bu görevde onlar
bugünkü hâlleriyle koşu kartının içinde kalır — yalnız yerleri değişir, metinleri değil.

## Nasıl görülür

1. Üretim akarken panelde tek kart: mor çerçeveli, canlı nokta + "üretiliyor", vurgu renginde büyük
   sayı, "kare bekliyor". Ayrıca "Üretiliyor" başlıklı bir kart yok.
2. Duraklatınca iki kart: foto kartı "sırada" der ve soluklaşır, altında "Duraklatıldı".
3. Panelin başlığı "Kuyruk"; şeritteki ikonun adı hâlâ "Kuyruğu takip et".
4. "Kuyruğu boşalt" panelin en dibinde, ana butondan boşlukla ayrılmış.
5. Kuyruk boşken tür kartı hiç yok; yalnız "Kuyruk boş" kartı.

## Testler

| Dosya | Test |
|---|---|
| `QueuePanel.test.jsx` | akan kuyrukta tür kartı canlı ve koşu kartı yok · duraklamışta kart "sırada" der ve koşu kartı doğar · kart sırası üretim sırası · borcu olmayan türün kartı çizilmez · foto kartı "kare bekliyor", video kartı "iş bekliyor" · başlık artık kartta "Üretiliyor" demiyor · "Kuyruğu boşalt" belgede ana butondan sonra geliyor |
| `SidePanel.test.jsx` | açık panelin başlığı "Kuyruk", şerit ikonunun adı "Kuyruğu takip et" |
| `useGeneration.test.jsx` | `queue` borcu olan türü sayar ve çalışan işi dışarıda bırakır |

Var olan testlerdeki `pending` prop'u `queue`ya çevrilir; sayıyı soran iddialar aynen kalır.

## Kapsam dışı

- **Bitiş, hata ve bilgi kartları** (37, 38, 39, 43) — **Görev 10**.
- **Video ve ses işlerinin gerçekten kuyruğa girmesi** (33) — Blok 5-6. Bu görevde ikinci kart
  yalnız **testte** doğar; ekranda foto kartı vardır.
- **Şeridin zemini ve seçili işareti** (8) — Görev 11.
- **Kuyruk kartındaki canlı noktanın davranışı** — tasarım suskun; bugünkü nabız kuralı
  (yalnız iş uçarken atar) korunur ve tür kartına aynen taşınır.
- **Panelde "kare" diyen iki cümle daha var** — boşaltma onayı ("Bekleyen 2 kare üretilmeden
  kuyruktan çıkar") ve bağlantı kartı ("son bilinen: 2 kare bekliyor"). İkisi de karışık kuyrukta
  yeniden okunmalı ama ikisi de **Görev 31'in** ("kare" dilinin geneli) işi; bu görevde
  dokunulmazlar.

## Riskler

- **Karar 1 iki `kesin` maddeyi uzlaştırıyor.** Yanlışsa bedeli tek sözcük ve tek satır: birim
  sözcüğü zaten kart başına veriden geliyor.
- **`pending` prop'unun kalkması** paneli ve proje ekranını birlikte değiştiriyor. Sayıyı soran her
  test aynen kalıyor, yalnız beslendiği prop değişiyor — kırılırsa derhal görünür.
