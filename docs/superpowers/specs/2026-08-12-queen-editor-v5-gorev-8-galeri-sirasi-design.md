# Queen Editor v5 · Görev 8 — Galeri sırası ve sürükleme · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 2, Görev 8 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
59, 60 · **Tür:** arka uç + ön yüz.

## Neden

Galeride bugün **iki sıra** var. Kullanıcının sürükleyerek kurduğu sıra yalnız görünümü, rozet
numaralarını ve export listesini değiştiriyor; motor bir sonraki kareyi **planın** sırasına göre
seçiyor. Yani kullanıcı "şunu önce üret" diyemiyor — sürükleme üretimi hiç ilgilendirmiyor.

Üstüne, bekleyen ve hatalı kareler **sürüklenemiyor**: basılı tutunca kart kalkmıyor, üstüne
"üretilince sıralanabilir" ipucu iniyor. Yani sıralayabildiğin tek şey zaten üretilmiş olan — sıra
hiçbir işe yaramayan tek şey.

Tasarım ikisini birden kaldırıyor: her kare sürüklenir ve **galerinin sırası üretimin sırasıdır**.

## Bugün ne var

| Soru | Cevabı veren |
|---|---|
| Hangi kareler istendi, hangi içerikle | plan dosyası |
| Hangi sırayla üretilir | **plan dosyasının dizisi** |
| Galeride hangi sırayla görünür | sıra dosyası |
| Hangi kare sürüklenebilir | yalnız üretilmiş olan |

## Ne olacak

| Soru | Cevabı veren |
|---|---|
| Hangi kareler istendi, hangi içerikle | plan dosyası (değişmedi) |
| Hangi sırayla üretilir | **sıra dosyası** — galerinin kendi sırası |
| Galeride hangi sırayla görünür | sıra dosyası (değişmedi) |
| Hangi kare sürüklenebilir | **hepsi** |

## Kararlar

### 1. Üretim sırası, galerinin alttan yukarı okunuşudur

Galeri **en yeni üstte** çiziliyor; en eski kare en altta ve o, ilk üretilmiş olan. Demek ki
üretimin yönü **alttan yukarı**. Maddenin cümlesi de bunu söylüyor: bekleyen bir kare üretilmişlerin
arasına (yani aşağı) bırakılınca, hâlâ **yukarıda** bekleyen karelerden **önce** üretilir.

Kural tek cümle: **sıradaki iş, galerinin en altındaki açık iştir.**

### 2. Yeni bir dosya doğmaz — kuyruk galerinin dosyasını okur

"Ayrı bir kuyruk sıralaması tutulmayacak" demek, üçüncü bir dosya eklemek değil, **var olan
ikisinden birinin sıra iddiasından vazgeçmesi** demek. Vazgeçen plan olur:

- **plan** — hangi kareler istendi, hangi prompt/seed/model ile. Dizisi artık yalnız "hangi sırayla
  istendi"yi söyler.
- **sıra dosyası** — kareler hangi sırada. Bu soru artık hem galeriyi hem kuyruğu kapsıyor;
  ikisi tasarımda **aynı soru**, o yüzden `CODE-STANDARD`'ın "bir dosya bir soru" kuralı korunuyor.
  Belgedeki tablo bu görevde düzeltilir.

Planın kendi dizisini **yeniden yazmak** seçenek değildi: plan'ın tek yazarı var (batch eklenmesi),
ve sürüklemenin ona ikinci bir yazar olarak girmesi aynı kuralın öteki yarısını ("her dosyanın tek
yazarı ve tek yazılma anı vardır") bozardı.

### 3. Sıra dosyasının tanımadığı iş, planın sırasında ve sona kalır

Galeri kuralı zaten böyle: sıra dosyasının bilmediği kare **en üste** girer ve kendi aralarında
plan sırasını korur. Üretim bunun aynası — sıra dosyasının bilmediği iş **en sona** kalır, kendi
aralarında plan sırasında.

Sonucu: hiç sürükleme yapılmamış projede davranış **bugünküyle birebir aynı**. Yeni gönderilen
batch de bugünkü gibi en sona girer.

### 4. Tekrar dene katmanı yerinde kalır

Bir tür içinde bugün iki kat var: hiç sırası gelmemiş işler önce, kullanıcının Tekrar dene ile geri
gönderdikleri sonra (tasarım v2, G10). Madde 60 **sıradan** söz ediyor, bu kuraldan değil ve v3'te
onu kaldıran bir madde yok. Galeri sırası bu yüzden **her katın içinde** işler: katlar korunur,
kat içindeki dizilim galerinin.

### 5. Türler arası sıra dokunulmaz

v3.1 kuralı açık: galeri sırası **tür içinde** geçerli, foto → video → ses sırasını değiştirmez.
Motor türleri zaten dıştan döndüğü için tür içinde sıralamak bunu kendiliğinden korur — video işini
galerinin en altına sürüklemek onu fotolardan önce üretmez.

### 6. Sıra deposu isteğe bağlı bir bağımlılıktır

Kuyruğun sıra dosyasına erişmesi gerekiyor; onu koşuya taşıyan zincir uzun
(`start_batch`/`resume_batch`/`retry_frame` → `run_queue` → `run_loop`). Yeni bağımlılık her
halkaya **anahtarlı ve varsayılanı olan** bir parametre olarak girer: verilmezse sıra yok demektir
ve dizilim planın olur — yani "sıra dosyası yok" hâlinin zaten doğru cevabı.

Böylece bu kararı ilgilendirmeyen çağrılar (`cancel_generation`, `resume_batch`'in "borç var mı"
sorusu) ve onların testleri olduğu gibi kalır: ikisi de sırayı değil **kümeyi** soruyor.

### 7. Her kare sürüklenir; çalışan kare yarıda kesilmez

"üretilince sıralanabilir" ipucu ve onu doğuran tutma kuralı kalkar — kart basılı tutulunca kalkar,
durumu ne olursa olsun.

Çalışan kare sürüklendiğinde GPU'daki iş **yarıda kesilmez**: motor o turun işini elinde tutuyor,
bitirir ve satırını yazar; sıra dosyasının yeni hâlini bir **sonraki** turda okur. Yani "biter, yeni
yerinde durur" kendiliğinden doğru — bu görevde motora bu iş için bir şey eklenmez.

## Nasıl görülür

1. Bekleyen bir kareyi basılı tut: kart kalkar, ipucu çıkmaz. Hatalı ve çalışan kare de öyle.
2. Bekleyen bir kareyi galerinin altına, üretilmişlerin arasına bırak: sıra gelince **o** üretilir,
   üstünde kalan bekleyenlerden önce.
3. Hiç sürükleme yapılmamış projede üretim sırası bugünküyle aynı.
4. Çalışan kareyi sürükle: üretim durmaz, kare biter ve yeni yerinde kalır.
5. Kuyrukta hem foto hem video işi varken bir video işini en alta sürükle: yine bütün fotolardan
   sonra üretilir.

## Testler

**Arka uç** (`pytest`, sahte port'larla):

| Konu | Test |
|---|---|
| Sıra | sıra dosyası verildiğinde bir türün işleri galerinin alttan yukarı dizilişinde çıkar |
| Bilinmeyen iş | sıra dosyasının tanımadığı iş sona kalır, kendi aralarında plan sırasında |
| Varsayılan | sıra verilmezse dizilim planın (bugünkü davranış) |
| Katman | Tekrar dene ile geri gönderilen iş, galeri onu alta koysa da taze işlerin arkasında kalır |
| Tür | galerinin en altındaki video işi, fotolar bitmeden atılmaz |
| Uçtan uca | sürükleme kaydedildikten sonra motorun ürettiği ilk kare galerinin en altındaki bekleyen kare olur |

**Ön yüz** (`npm test`):

| Konu | Test |
|---|---|
| Sürükleme | bekleyen kare basılı tutulunca kalkar · hatalı kare de kalkar · çalışan kare de kalkar |
| İpucu | "üretilince sıralanabilir" hiçbir durumda çıkmaz |

Var olan iki test ("tells a waiting frame why it cannot be moved", "says the same to a failed
frame") tersine çevrilir — aynı jest, artık kartı kaldırıyor.

## Kapsam dışı

- **Kuyruk panelinin görünümü** (madde 33-46) — Görev 9-10.
- **Video ve ses işlerinin gerçekten üretilmesi** — Blok 5-6. Bu görevde tür sırası yalnız
  **kuralla** doğrulanır, gerçek bir video üreticisiyle değil.
- **Galeri kartının durum dili** — Görev 7'de yapıldı.
- **Export'un sırası** — zaten galeriyi okuyor, değişmez.

## Riskler

- **Sürükleme artık üretimi değiştiriyor.** Kullanıcı bunu bilmeden sürüklerse üretim sırası
  değişir. Tasarımın istediği tam olarak bu; ayrıca yıkıcı değil — hiçbir kare kaybolmaz, yalnız
  sıraya girer.
- **Zincire taşınan yeni parametre** (karar 6) altı dosyaya dokunuyor. Anahtarlı ve varsayılanlı
  olduğu için var olan çağrılar ve testleri kırılmaz; kırılırsa da derhal görünür.
- **`CODE-STANDARD.md`'nin dosya tablosu** bu görevde güncellenmezse belge kodla çelişir. Görevin
  kapanışına dahil.
