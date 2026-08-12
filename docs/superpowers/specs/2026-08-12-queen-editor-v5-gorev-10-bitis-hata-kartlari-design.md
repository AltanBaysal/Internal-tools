# Queen Editor v5 · Görev 10 — Bitiş, hata ve bilgi kartları · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 3, Görev 10 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
37, 38, 39, 43 (42 Görev 5'te kapandı) · **Tür:** arka uç + ön yüz.

## Neden

Kuyruk bitince ekranda tek cümle var: **"20 kare üretildi, 3 hatalı"**. İyi haberle kötü haber aynı
cümleye sıkışıyor, kötü haberin ardından yapılacak tek şey ise galeriye gidip kareleri tek tek
bulmak — kartın sunduğu bağlantı da tam olarak bunu yapıyor: seni galeriye atıyor ve orada bırakıyor.

Tasarım ikisini ayırıyor. Yeşil kart yalnız iyi haberi verir; hata varsa **altında kendi kırmızı
kartı** doğar ve o kart bir şey **yapar**: hepsini birden kuyruğa geri gönderir. Galeriye gönderen
bağlantı kalkar, çünkü hatalı kareler zaten galeride kırmızı duruyor.

## Bugün ne var

| Yer | Bugünkü hâli |
|---|---|
| Bitiş | tek kart: "Kuyruk tamamlandı" + "20 kare üretildi, 3 hatalı" |
| Hata satırı | altı çizili kırmızı "3 kare üretilemedi — galeride göster", basınca galeri kayar |
| Kartın rengi | bütün hâllerde nötr çerçeve ve zemin; yalnız nokta ve başlık renk değiştirir |
| Açılışta sürme | kuyruk kendiliğinden sürüyor ama bunu söyleyen hiçbir şey yok |
| Toplu tekrar | yok — hatalı kareler tek tek, galerideki kendi butonlarından denenir |

## Ne olacak

| Yer | Yeni hâli |
|---|---|
| Bitiş | yeşil kart yalnız "Kuyruk tamamlandı" + "20 kare üretildi" |
| Hata kartı | ayrı kırmızı kart: "3 kare üretilemedi — 2 foto · 1 video" + **"Hepsini tekrar dene"** |
| Kartın rengi | tamamlandı → yeşil çerçeve + saydam yeşil zemin · durdu → kırmızı çerçeve + saydam kırmızı zemin · ötekiler nötr |
| Açılışta sürme | tür kartının altında "uygulama açıldı — kuyruk kaldığı yerden sürüyor" |
| Toplu tekrar | tek istek bütün hatalı işleri kuyruğa geri koyar |

## Kararlar

### 1. Hata kartı da tür tür sayar

Kart "3 kare üretilemedi — **2 foto · 1 video**" diyor; yani hata sayısı da kuyruk sayısı gibi
**katman başına** biliniyor olmalı. Kuyruk için Görev 9'da kurulan şeklin aynısı kullanılır:
`failures` artık dosya adları dizisi değil, `[{ layer, count }]`.

Dökümü yalnız **birden çok katman** hata verdiğinde yazılır. Tek katmanda "3 kare üretilemedi —
3 foto" demek aynı şeyi iki kez söylemek olurdu.

### 2. Galeriye gönderen bağlantı kalkar, yerine hiçbir şey gelmez

Madde 38 bağlantıyı kaldırıyor ve gerekçesini de veriyor: hatalı kareler galeride zaten kırmızı
duruyor. Bu, ön yüzden iki şeyin birden düşmesi demek — panelin `onShowFailures` çağrısı ve proje
ekranının "ilk hatalı kareye kaydır" işi. İkisi de bu görevde silinir; bir kullanıcısı kalmayan kod
durmaz.

Dosya adları listesi de böylece gereksizleşiyor — kartın ihtiyacı sayı, kaydırmanın ihtiyacıysa
artık yok. Karar 1'in `[{layer, count}]` biçimi bu yüzden kayıpsız.

### 3. "Hepsini tekrar dene" var olan uca dosyasız gider

Tek kare denemek bugün `/retry` ucuna `{file}` göndermek. Hepsini denemek aynı ucun **dosyasız**
çağrısıdır: "şu kareyi tekrar dene" ile "tekrar dene" arasındaki fark, cümlenin nesnesi.

Sunucu tarafında iki ayrı kullanım senaryosu olur — biri tek kareyi, öteki **hatalı bütün işleri**
kuyruğa geri koyar; hangisinin koşacağına yalnızca isteğin gövdesine bakan sunum katmanı karar
verir. Böylece iki kural iki dosyada kalır ve hiçbiri ötekinin bayrağını taşımaz.

Toplu tekrar **katman ayırmaz**: hatalı ne varsa geri döner. Kuyruğun tür sırası (foto → video →
ses) ve "geri gönderilen iş taze işin arkasında bekler" kuralı zaten üstüne oturur, o yüzden burada
sıra kararı verilmez.

### 4. Renk kartın hâlini anlatır, sayının değil

Madde 39: tamamlanan kart yeşil, duran kart kırmızı çerçeve ve saydam zemin alır; ötekiler nötr
kalır. Başlık tek aralıklı yazıya döner ve iç boşluk her yönde 14 piksel olur.

Büyük sayının kırmızıya dönme kuralı Görev 9'da zaten kalkmıştı (sayı vurgu renginde); bu görev onu
tamamlıyor — durmayı **kart** anlatıyor.

### 5. Açılış satırı, ekranın kendi başlattığı koşu sürerken durur

Madde 43 satırı istiyor ama **ne kadar kalacağını tasarım söylemiyor**. Uydurulmuş bir süre yerine
satırın kendi doğal ömrü kullanılır: satır, **bu ekranın kendiliğinden başlattığı** koşu akarken
durur ve koşu bitince kaybolur. Sayaç yok, zamanlayıcı yok, uydurulmuş saniye yok.

Kullanıcının kendi bastığı "Devam et" bu satırı doğurmaz — o zaten ne yaptığını biliyor. Satırın
söylediği tek şey, **kimsenin basmadığı** bir şeyin olduğudur.

## Nasıl görülür

1. Hatasız biten kuyrukta tek yeşil kart: "Kuyruk tamamlandı" + "20 kare üretildi". Kırmızı kart
   yok.
2. Hatalı biten kuyrukta iki kart: yeşil kart yalnız iyi haberi verir, altında kırmızı kart
   "3 kare üretilemedi" der ve "Hepsini tekrar dene" taşır.
3. Butona basınca üç kare de kuyruğa döner ve üretim başlar; galeride kırmızı hapları "foto
   kuyrukta"ya döner.
4. Durmuş kuyrukta kart kırmızı çerçeve ve saydam kırmızı zemin alır; tamamlanmışta yeşil.
5. Yarım kuyruklu bir projeyi açınca tür kartının altında "uygulama açıldı — kuyruk kaldığı yerden
   sürüyor" okunur; kuyruk bitince satır gider.
6. Hiçbir yerde "galeride göster" yok.

## Testler

**Arka uç:**

| Konu | Test |
|---|---|
| Toplu tekrar | hatalı bütün işler kuyruğa döner ve üretilir |
| Kapsam | hatasız iş dokunulmadan kalır (biten kare yeniden üretilmez) |
| Uç nokta | dosyasız `/retry` hepsini dener, dosyalı olan yalnız onu |

**Ön yüz:**

| Konu | Test |
|---|---|
| İki kart | hatalı bitişte yeşil kart yalnız iyi haberi verir, kırmızı kart ayrı doğar |
| Kırmızı kart yok | hatasız bitişte kırmızı kart hiç çizilmez |
| Döküm | iki katman hata verince "2 foto · 1 video" yazılır, tek katmanda yazılmaz |
| Buton | "Hepsini tekrar dene" çağrıyı yapar; "galeride göster" hiç yok |
| Renk | tamamlanmış kart yeşil, durmuş kart kırmızı çerçeve alır |
| Açılış satırı | ekran kuyruğu kendiliğinden sürdürdüğünde satır çıkar, kullanıcı Devam et'e basınca çıkmaz |

## Kapsam dışı

- **Boş kuyruk kartının metni** (42) — Görev 5'te kapandı.
- **Kuyruk kartlarının kendisi** (34-36, 40, 41, 46) — Görev 9'da yapıldı.
- **Galerideki tek kare Tekrar dene'si** (67-69) — Görev 19; bu görevde bugünkü hâliyle kalır.
- **"Kare" dilinin geneli** (104) — Görev 31. Hata kartının "kare üretilemedi" cümlesi tasarımın
  kendi cümlesidir ve burada birebir yazılır.

## Riskler

- **`failures` biçiminin değişmesi** proje ekranındaki kaydırma işini siliyor. Silinen şey maddenin
  açıkça kaldırdığı davranış; testi de onunla birlikte gider.
- **Açılış satırının ömrü** (karar 5) tasarımın suskun kaldığı yer. Yanlışsa bedeli tek koşul.
