# Queen Editor v5 · Görev 19 — Katman hatası davranışı · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 5, Görev 19 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
67, 68, 69 · **Tür:** arka uç + ön yüz.

## Neden

Video artık hata alabiliyor (Görev 17) ve galeri bunu hapla söylüyor (Görev 18) — ama karenin
kurtulma yolu yok. Fotoğrafı duran bir karede bugünkü kırmızı kart yanlış: kart dolu, üstünü
kapatmak fotoğrafı saklamak olur. Bir de kuyruğa girdiğini söylemeyen "Tekrar dene" var: basınca
hiçbir şey değişmiyor, ikinci kez basılabiliyor.

## Ne olacak

Fotosu duran ama katmanı hata almış karenin üstüne imleç gelince **koyu bir örtü** iner ve ortasında
kırmızı çerçeveli **Tekrar dene** belirir. Basınca o katman **aynı kareye** yeniden üretilmek üzere
kuyruğa girer — yeni kare doğmaz — ve buton pasifleşip **"Kuyruğa eklendi"** der.

## Kararlar

### 1. Tekrar dene karenin kırmızı katmanını geri gönderir

`retry_frame` bugün hep foto yuvasını kuyruğa iade ediyor. Bundan sonra karenin **hata almış
katmanlarını** iade eder: videosu patlamış karede video, fotosu patlamış karede foto. Yeni kare
açılmaz — "üret = ekle" kuralının tek istisnası budur (madde 68), çünkü eksik katmanı kopyaya
üretmek kullanıcının kurtarmak istediği kareyi kurtarmaz.

Hiç hatalı katman yoksa foto yuvası iade edilir: silinmiş fotoğrafını geri isteyen kare bugün böyle
çalışıyor ve o davranış duruyor.

### 2. Fotosu duran kare örtüyle kurtarılır, kartı kapanmaz

Madde 67: fotosu **olmayan** kırmızı karede buton kartın ortasında (bugünkü hâl). Fotosu **duran**
karede kart olduğu gibi kalır; imleç gelince %55 koyu örtü iner ve butonu taşır. Sebep: kartta
gerçek bir fotoğraf var, onu kalıcı bir kutuyla kapatmak kareyi kaybetmiş gibi gösterir.

Örtü görünmezken tıklamayı da yemez — altındaki fotoğraf hâlâ tıklanabilir, detay sayfası açılır.

### 3. Basılan buton kuyruğa girdiğini söyler

Madde 69: basınca buton pasifleşir ve "Kuyruğa eklendi" yazar. İkinci basış böylece mümkün olmaz.
Bu, ekranın kendi hafızası: sunucu "bu kare kuyruğa alındı" diye ayrı bir şey tutmaz, sonraki
yoklama kareyi zaten bekleyen olarak getirir ve kart kendiliğinden değişir.

Kural iki buton için de aynı — ortadaki de örtüdeki de.

## Nasıl görülür

1. Videosu hata almış karenin üstüne gelince örtü ve kırmızı çerçeveli Tekrar dene çıkıyor.
2. Basınca buton "Kuyruğa eklendi" olup pasifleşiyor, galeride yeni kare belirmiyor.
3. Sırası gelince aynı karenin videosu üretiliyor.
4. Fotosu hata almış boş kare bugünkü hâlinde: buton kartın ortasında.

## Testler

**Arka uç:** videosu hatalı karede Tekrar dene video yuvasını kuyruğa iade eder, foto yuvasına
dokunmaz · fotosu hatalı karede foto yuvasını iade eder · hiç hatası olmayan (silinmiş fotolu) kare
bugünkü gibi foto yuvasını iade eder · yeni kare doğmaz.

**Ön yüz:** fotosu duran hatalı katmanlı karede örtü + buton var · fotosu olmayan hatalı karede
buton kartın ortasında (örtü yok) · basınca buton "Kuyruğa eklendi" ve pasif · basış `onRetry`'ı
karenin dosya adıyla çağırıyor.

## Kapsam dışı

- **Detay sayfasındaki katman sekmeleri ve oradaki Tekrar dene** — Blok 7.
- **Kopya karedeki "Kareyi sil" ikinci yolu** — silme zaten seçim şeridinde var; madde 68'in o
  yarısı detay sayfasının işi (Görev 27).
- **Ses** — Blok 6 aynı kalıba girer, bu görevde iş çıkmaz.

## Riskler

- **Fotosu silinmiş, videosu hatalı kare.** Tekrar dene videoyu iade eder ama fotoğraf yok; video
  işi "kaynak foto verilmedi" diyip koşuyu durdurur. Dar bir köşe: fotoğrafı silinen kare zaten
  galeriden düşüyor, bu hâle ancak silme ile hata yarışırsa girilir.
