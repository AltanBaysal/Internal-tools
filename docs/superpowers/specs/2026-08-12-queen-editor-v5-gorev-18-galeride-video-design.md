# Queen Editor v5 · Görev 18 — Galeride video · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 5, Görev 18 ·
**Kaynak madde:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
58'in video yarısı · **Tür:** arka uç + ön yüz.

## Neden

Video artık gerçekten üretiliyor (Görev 17) ama galeri bunu hiç bilmiyor: kare hâlâ yalnız
fotoğrafını gösteriyor, videosu olan kare olmayandan ayırt edilemiyor ve videosu kuyrukta olan kopya
kare "bitmiş" görünüyor. Dahası galeri, videosu **üretilirken** kareyi yüklenme kutusuna çeviriyor —
fotoğrafı ekrandan kayboluyor.

## Ne olacak

Videolu karenin sağ altında koyu zeminli **sahiplik rozeti** (oynat üçgeni + "video") doğar. Videosu
kuyrukta olan kare fotoğrafıyla durur ve sol üstünde **"video kuyrukta"** hapı taşır; üretilirken hap
"video üretiliyor"a döner, fotoğraf yerinde kalır.

## Kararlar

### 1. Kare satırı ne beklediğini ve neyin patladığını söyler

Galeri bugün kareye "ne oldu"yu tek bir alandan okuyor (`status`) ve o alan fotoğrafın hâli. Katmanlar
gelince bu yetmiyor: bir karenin fotoğrafı bitmişken videosu kuyrukta olabilir.

`list_frames` her satıra iki liste ekler:

- **`owed`** — kuyruğun o kareye hâlâ borçlu olduğu katmanlar (`["video"]`), motorun kendi
  sırasında.
- **`failed`** — kaydın son satırı "hata" diyen katmanlar.

İkisi de tek yerden çıkıyor: plan neyin istendiğini, kayıt ne olduğunu söylüyor — galeriyi tek cevap
yapan kural (Görev 3'ün `list_frames`'i) katmanlara aynen uzuyor. `status` ve `layers` olduğu gibi
kalır; ekranın "fotoğraf var mı" ve "hangi dosyalar" soruları değişmedi.

### 2. Çalışan işin katmanı ekrana kadar gelir

Ekran bugün "şu an üretilen kare" bilgisini bir dosya adı olarak alıyor ve o kareyi yüklenme
kutusuna çeviriyor. Video işi için bu **yanlış**: karenin fotoğrafı duruyor, üretilen şey videosu.

Çalışan işin **türü** de ekrana taşınır. Kural: yüklenme kutusu yalnız **foto** işinde çizilir;
başka bir katman üretilirken kare fotoğrafıyla durur ve hap "video üretiliyor" der.

### 3. Rozet yalnız biten katman için

Madde 58: "Rozetler yalnız katman tamamlandığında görünecek; ara hâlleri sol üstteki durum hapı
anlatacak." Yani `layers.video` **var** ve o katman `failed` listesinde **değil**. Hatalı katman
yuvayı doldurur (yeniden üretim onu ezemesin diye) ama rozet doğurmaz.

Rozet sağ altta, sıra numarasının karşı köşesinde: sağ üst sıra, sol üst durum, sağ alt sahiplik —
madde 57'nin üç düzlemi.

### 4. Tek karede tek hap

Bir karede aynı anda birden çok şey olabilir (fotosu hatalı, videosu kuyrukta). Hap **bir** tane
kalır ve şu sırayla seçilir: çalışan → hatalı → kuyrukta; eşitlikte katman sırası (foto, video, ses).
Sebep: hap köşede duran küçük bir etiket, iki tanesi kartı okunmaz yapar; kalanı detay sayfasının
işi (Görev 23).

### 5. Kuyruk paneli video işlerini de sayar

Panel bugün video ve ses için sıfır sayıyor — kodun kendi yorumu "sunucu sayınca düzelir" diyor.
Sunucu artık söylüyor (karar 1), o yüzden sayım karelerin `owed`/`failed` listelerinden gelir.
Görev 14-17 kuyruğa video işi koyduğu hâlde panelin "0" demesi yalanı burada kapanır.

## Nasıl görülür

1. Videolu karenin sağ altında oynat üçgeni + "video" duruyor.
2. Videosu kuyrukta olan kopya kare kaynağın fotoğrafını gösteriyor, sol üstünde "video kuyrukta".
3. Video üretilirken kare fotoğrafıyla duruyor, hap canlı noktayla "video üretiliyor" diyor.
4. Videosu hata almış karede rozet yok, hap "video hata" diyor.
5. Kuyruk panelinde "video" kartı gerçek sayıyı gösteriyor.

## Testler

**Arka uç:** kuyrukta video işi olan karenin `owed`'ı `["video"]` · biten video `owed`'dan düşer ·
hatalı video `failed`'e girer · fotosu bekleyen karenin `owed`'ı `["photo"]`.

**Ön yüz:** videolu karede rozet var · videosuz karede yok · hatalı videoda rozet yok, hap "video
hata" · videosu kuyrukta olan kare fotoğrafını gösteriyor + "video kuyrukta" · video üretilirken
fotoğraf duruyor ve hap "video üretiliyor" · foto üretilirken yüklenme kutusu (bugünkü davranış) ·
kuyruk sayıları video işlerini sayıyor.

## Kapsam dışı

- **Videonun oynatılması** — galeri karosu fotoğrafı gösterir; oynatma detay sayfasının işi
  (Görev 24).
- **Hatalı katmanda Tekrar dene** — Görev 19.
- **Ses rozeti** — Görev 22.

## Riskler

- **Satır büyüyor.** Her kare iki liste daha taşıyor; 48 karelik projede fark ölçülemez, kazanç
  ekranın ikinci bir kaynağa (canlı kuyruk raporu) ihtiyacı olmaması.
