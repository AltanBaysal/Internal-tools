# Queen Editor v5 · Görev 24 — Oynatma · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 7, Görev 24 ·
**Kaynak madde:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
74 · **Tür:** ön yüz.

## Neden

Video ve ses üretiliyor, detayda sekmeleri var (Görev 23), ama hiçbir yerde **oynamıyorlar**. Kare
sesli oynasın diye ayrı bir dosya olarak durmalarına karar verilmişti (Görev 22); o kararın karşılığı
burada ödenir.

## Ne olacak

Video sekmesi 16:9 alanda videoyu **döngüde** oynatır: ortada 64 piksellik yuvarlak oynat düğmesi,
altında süre · ilerleme çubuğu · süre. Ses sekmesi ayrı bir oynatıcı açmaz — **video ile sesi
birlikte** oynatır ve ilerleme çubuğunun yerini 46 çubuklu dalga formu alır; çalınmış kısım mor.

## Kararlar

### 1. Tek oynatıcı, iki sekme

Ses sekmesi videoyu da oynatır (madde 74), yani iki sekme aynı bileşenin iki hâli: fark, sesin
`<audio>` olarak eşlik etmesi ve ilerleme çubuğunun yerini dalga formunun alması. İki ayrı oynatıcı
yazmak, aynı davranışı iki yerde tutmak olurdu.

### 2. Ses videoya kodda değil, oynatmada eşlik eder

Dosyalar ayrı (Görev 22). Oynatma sırasında ses videoyla birlikte başlar, birlikte durur ve
videonun döngüsünde başa sarar. Kaymayı düzeltmenin kuralı basit: her ilerleme bildiriminde ses ile
videonun zamanı **çeyrek saniyeden** fazla ayrıldıysa ses videonun zamanına çekilir.

Neden bu: kayma insan kulağının fark ettiği yerde düzeltilir, her karede değil — her karede
`currentTime` yazmak sesi cızırdatır.

### 3. Dalga formu sesin kendisinden çıkar

46 çubuğun yüksekliği, wav dosyası tarayıcıda çözülüp (Web Audio) tepe değerlerinden hesaplanır.
Uydurma bir dalga çizmek, aracın "asla uydurma" kuralının görsel hâlde çiğnenmesi olurdu.

Çözemeyen ortamda (ya da dosya okunamazsa) çubuklar **düz** kalır: ilerleme yine görünür, yalan
olan bir şey görünmez.

### 4. Süre videodan okunur

Toplam süre `<video>`'nun kendi `duration`'ı. Panelin "5 saniye" cümlesi bir üretim ayarı; burada
ekrana yazılan şey dosyanın gerçek süresidir.

### 5. Alan 16:9

Video alanı tasarımın verdiği oranda. Fotoğraf alanı bugünkü hâlinde (oran verilmez, kırpılmaz)
kalır — fotoğrafın oranını sunucu bilmiyor, videonunki ise grafiğin kendi ayarı.

## Nasıl görülür

1. Video sekmesinde ortada yuvarlak oynat düğmesi; basınca video dönmeye başlıyor ve düğme duraklat
   oluyor.
2. Altta sol ve sağda süreler, aralarında dolan çubuk.
3. Ses sekmesinde aynı video oynuyor, sesi duyuluyor; çubuğun yerinde dalga formu ve çalınan kısım
   mor.
4. Videosu olmayan karede sekme zaten pasif — oynatıcı hiç çizilmiyor.

## Testler

**Ön yüz:** video sekmesi videoyu döngüyle çiziyor · oynat düğmesi videoyu başlatıyor ve etiketi
duraklata dönüyor · ilerleme bildirimi süreleri ve çubuğu güncelliyor · ses sekmesinde ses ögesi de
var ve kaynak wav · ses sekmesinde çubuk yerine 46 çubuk var · foto sekmesinde oynatıcı yok.

> jsdom `play()`/`pause()` ve `AudioContext` tanımıyor; testler bunları taklit eder, dalga formu
> testte düz kalır.

## Kapsam dışı

- **Prompt düzenleme ve Yeniden üret** — Görev 25.
- **Sekme başına yıkıcı eylem** — Görev 26.
- **Galeride oynatma** — tasarımda yok; karo fotoğraf gösterir.

## Riskler

- **Tarayıcı otomatik oynatmayı engelleyebilir.** Oynatma kullanıcının basışıyla başlıyor, yani
  engel yok; ses de aynı basıştan doğuyor.
- **Kayma.** Ses ve video ayrı ögeler; çeyrek saniyelik eşik kayma birikirse düzeltir. Tek dosyaya
  karıştırmak (ffmpeg) bu sürümde kapsam dışı ve videoyu yeniden yazmak demek olurdu.
