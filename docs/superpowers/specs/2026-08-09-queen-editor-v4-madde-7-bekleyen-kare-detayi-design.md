# Madde 7 — Bekleyen ve çalışan karenin detayı

**Tarih:** 2026-08-09 · **Branch:** `feat/queen-editor-v2` · **Yol haritası:**
[v4, Madde 7](../plans/2026-08-08-queen-editor-v4-roadmap.md) ·
**Kaynak:** [tasarım v2 farkları](../research/2026-08-08-queen-editor-tasarim-v2-farklari.md), **F1-F5**

---

## 1 · Bugünkü hâl ve sorun

Madde 5 galeriyi tek diziye indirdi: bekleyen, çalışan ve hatalı kareler artık kendi sıralarında
duruyor. Detay sayfası bu değişimin dışında kaldı — hâlâ yalnız **üretilmiş** fotoğrafı tanıyor:

- Bekleyen ya da hatalı bir karenin adresine gidilirse **"Fotoğraf bulunamadı"** kartı çıkıyor.
- Galeride yalnız fotoğraf tıklanabiliyor; bekleyen karenin içine bakmanın **hiçbir yolu yok**.
- Sayaç `index + 1` yazıyor, rozet ise alttan sayıyor — **aynı kare için iki farklı numara**.
- Negatif prompt hiçbir ekranda görünmüyor.

Bu maddenin işi: sayfayı dizinin tamamına açmak. Kuyruğa atılan işin ne olduğu ancak buradan
görülebilir hâle gelir.

## 2 · Karar özeti

| Kod | Karar |
|---|---|
| **F1** | Sayfa üretilmiş · bekleyen · çalışan hâllerinin üçünü de açar |
| **F2** | Negatif kutusu gelir, prompt ile kalan alanı **eşit** paylaşır, her biri kendi içinde kayar |
| **F3** | Sıra sayacı **rozetle aynı sayıdır**; oklar bekleyen ve çalışan kareleri de gezer |
| **F4** | Bekleyende buton **Kuyruktan çıkar** olur, **onay sormaz**, sonraki kare açılır |
| **F5** | Fotoğrafı olmayan karede etiket **"Dosya adı (planlanan)"** ve değer soluk |

## 3 · Ekranın hâlleri

Tasarım üç hâl çiziyor. Bizim galerimizde **dördüncü** bir hâl var — hatalı kare (Madde 1'de kalıcı
oldu, Madde 5'te kendi yerinde kırmızı çizildi). Tasarım ondan söz etmiyor, o yüzden kararı burada
veriyoruz.

| Hâl | Görsel alanı | Alt buton | Onay |
|---|---|---|---|
| **Üretilmiş** (`done`) | tam boy fotoğraf | **Sil** | evet — bugünkü pencere |
| **Bekleyen** (`pending`) | kesikli kutu: "bekliyor" + "henüz üretilmedi" | **Kuyruktan çıkar** | hayır |
| **Çalışan** (worker'ın tuttuğu kare) | dönen gösterge | **Kuyruktan çıkar**, pasif | — |
| **Hatalı** (`failed`) | kesikli kutu, kırmızı: "üretilemedi" | **Kuyruktan çıkar** | hayır |

**Hatalı kare neden "Kuyruktan çıkar"?** Diskte silinecek bir dosya yok — çıkarma yıkıcı değil,
o yüzden onay da yok. Madde 6 aynı kararı zaten vermişti: galerinin toplu onay metni `done`
olmayan her kareyi "kuyruktan çıkarılsın mı?" diye sorar, hatalı kare de o kümede. Uygulama tek
dil konuşsun diye detay sayfası aynı ayrımı kullanır.

**Hatalı karede "Tekrar dene" yok.** Tasarım detay sayfasında böyle bir buton istemiyor; galerideki
kırmızı karenin kendi Tekrar dene'si duruyor. Akan kuyrukta Tekrar dene'nin davranışı **Madde 8**'in
işi (G10) ve orada karara bağlanacak — burada ikinci bir giriş noktası açmak o kararı iki yere
dağıtırdı.

## 4 · Sağ sütun

Dört alan, **her hâlde aynı**: Sıra · Dosya adı · Prompt · Negatif.

- **Süre alanı yok** — tasarımın çizdiği sütunda yok (fark belgesi 5. bölüm), roadmap v3'ün "süre
  detayda görünsün" isteği **Madde 11**'in açık sorusu olarak duruyor, orada karara bağlanır.
- **Seed alanı yok** — tasarım hiçbir ekranda istemiyor, üretilmiş fotoğrafta da yok.
- **Dosya adı:** fotoğrafı olan karede etiket "Dosya adı", değer tam parlaklıkta. Fotoğrafı
  **olmayan** her karede (bekleyen, çalışan, hatalı) etiket **"Dosya adı (planlanan)"**, değer soluk.
  F5 yalnız "bekleyen" diyor; ad çalışan ve hatalı karede de henüz diskte yok, dolayısıyla aynı
  kural üçüne birden uygulanır. Tersi, worker kareyi eline aldığı saniye etiketin bir yalan söylemesi
  olurdu.
- **Prompt ve Negatif:** üstteki iki küçük alandan artan boşluğu **eşit** paylaşırlar (`flex: 1`),
  her biri kendi içinde kayar. Uzun bir negatif prompt'un kutusu, prompt'un kutusunu ezmez.
- **Negatif boşsa** kutu yine çizilir, içine soluk `—` yazılır. Kutunun varlığı hâle göre
  değişmez; boşluk da bir cevaptır.

## 5 · Sıra sayacı ve oklar

**Sayaç rozetle aynı sayıyı yazar.** Rozet Madde 5'te alttan saymaya başladı (en alttaki kare 1, en
üstteki N). Detay sayfası bugün `index + 1` yazıyor, yani üstten sayıyor — aynı kare için iki farklı
numara. F3 bunu kapatıyor: sayaç `frames.length - index` olur ve tıklanan karenin rozetiyle birebir
aynı çıkar.

**Oklar galerinin okunuş sırasını izler.** `›` dizide bir aşağı (galeride sağa/aşağı), `‹` bir yukarı
gider. Uçlarda ok pasifleşir, sarmama yok — bugünkü kural aynen kalıyor.

> **Bunun görünür sonucu:** `›` sayacı **azaltır** (20 / 20 → 19 / 20). Çelişki değil, aynı kararın
> iki yüzü: numara üretim sırasıdır ve galeri yeniyi en üste koyar, dolayısıyla aşağı gitmek
> geçmişe gitmektir. Alternatif — okları numaraya göre çevirmek — okların galeride gördüğün yönle
> ters çalışması demek olurdu; tasarım "rozet dizisi = sıra sayacı = **ok sırası**" diyor, yani
> gezilen şey galerinin sırası.

Klavye aynı kuralı izler: `←`/`→` okların karşılığı, `Esc` galeriye döner.

## 6 · Kuyruktan çıkar

- Onay penceresi **yoktur** — basıldığı anda gider.
- Gittikten sonra **sonraki kare açılır**; dizinin sonundaysa bir öncekine, hiçbiri kalmadıysa
  galeriye dönülür. Silme bugün bu kuralı kullanıyor, ikisi aynı kuralı paylaşır.
- Sunucu isteği reddederse hiçbir yere gidilmez: sayfada kalınır ve hata kartı çıkar. Bugünkü silme
  bu durumda da yönlendiriyor — bu maddede kapanan bir sapma.
- Çalışan karede buton **pasiftir**: worker'ın elindeki kareyi kuyruktan çekmek Madde 4'ün
  "Duraklat çalışan kareyi keser" kuralına giren ayrı bir iştir, buradan yapılmaz.

## 7 · Çalışan kare sayfa yenilenmeden fotoğrafa döner

Detay sayfası artık **canlı**: proje ekranıyla aynı kaynağı okur (`/api/status` + `/frames`) ve aynı
ritimde yoklar — kuyruk akarken 2 saniyede bir, durunca hiç.

Bunun için ayrı bir okuyucu yazılmaz: proje ekranının `useGeneration` kancası zaten tam olarak bu
soruyu cevaplıyor (dizinin kendisi + worker'ın tuttuğu dosya adı + hata). Detay sayfası onu kullanır,
`usePhotos` kancası **silinir**. Gerekçe: aynı yoklama zincirini iki dosyada tutmak, ikisinin zamanla
ayrışmasına açık kapı bırakır; "kural tek yerde" kuralı bunu kapsıyor.

**Bir kancanın işi büyütülür:** silme çağrısı bugün hatayı yutup her hâlükârda başarılı gibi
sonuçlanıyor. Sunucunun cevabıyla (başarısızlıkta `null`) sonuçlanacak şekilde değiştirilir ki detay
sayfası "gitti mi, gitmedi mi" sorusunu sorabilsin. Galerideki toplu silmenin davranışı değişmez.

## 8 · Galeriden erişim

Bugün galeride yalnız fotoğraf bağlantıdır. F1'in "üç hâli de açar" iddiasının görünür olması için
**her kare** detayına götürür — bekleyen, çalışan ve hatalı dahil.

- Seçim modu açıkken tıklama yine **seçer**, detaya gitmez (Madde 6 kuralı).
- Kırmızı karedeki **Tekrar dene** bağlantıyı tetiklemez — buton olayı kendinde durdurur.
- Basılı tutup sürükleme kuralı değişmez: üretilmemiş kare kalkmaz, "üretilince sıralanabilir"
  ipucunu gösterir.

## 9 · Değişmeyenler

- Üst şerit, "Galeriye dön" butonu, `Esc` ile çıkış.
- **"Fotoğraf bulunamadı" kartı** — dizide hiç olmayan bir dosya adı için duruyor (silinmiş bir
  karenin eski adresi, elle yazılmış bir URL). Fark belgesi bunu 1/3 damgayla "tasarım yalnız üç hâli
  tanıyor" diye işaretlemişti; kaldıran bir karar yok, öksüz davranışlar korunur.
- Fotoğrafın kırpılmadan, kendi en-boy oranıyla çizilmesi.
- Silmede onay penceresi ve metinleri.

## 10 · Yok

- **Seed alanı** (tasarım hiçbir ekranda istemiyor).
- **Prompt/negatif düzenleme** ve **Yeniden üret** (F6-F10, kapsam dışı).
- **Üretim süresi** (Madde 11'de karara bağlanır).
- Arka uçta hiçbir değişiklik: `/frames` prompt'u, negatifi ve durumu zaten veriyor;
  `/frames/delete` bekleyen kareyi zaten kuyruktan çıkarıyor (Madde 1 ve 6).

## 11 · Kabul kriterleri (testler bunları kanıtlar)

**Detay sayfası**

1. Bekleyen karenin adresi açılınca "Fotoğraf bulunamadı" değil, kesikli "henüz üretilmedi" alanı
   çıkar; prompt ve negatif okunur.
2. Çalışan karede dönen gösterge çıkar ve alt buton pasiftir.
3. Çalışan kare bitince sayfa yeniden yüklenmeden fotoğrafa döner.
4. Hatalı karede kırmızı "üretilemedi" alanı çıkar, buton **Kuyruktan çıkar**'dır.
5. Sayaç rozetle aynı sayıyı yazar: en üstteki kare `N / N`, en alttaki `1 / N`.
6. `›` dizide bir aşağı gider ve sayaç bir azalır; en alttaki karede `›` ölüdür.
7. Bekleyen karede **Kuyruktan çıkar** onay sormadan çağırır ve sonraki kareyi açar.
8. Çıkarma başarısız olursa sayfada kalınır ve hata kartı çıkar.
9. Fotoğrafı olmayan karede etiket "Dosya adı (planlanan)".
10. Negatif kutusu her hâlde çizilir; boşken `—` yazar.

**Galeri**

11. Bekleyen kareye tıklamak detay sayfasına götürür.
12. Seçim modu açıkken bekleyen kareye tıklamak seçer, detaya gitmez.
13. Kırmızı karede **Tekrar dene**'ye basmak detaya götürmez, yalnız yeniden dener.

## 12 · Kendi eleştirim

Yazdıktan sonra spec'e dışarıdan bakınca çıkanlar — hepsi yukarıda kapatıldı:

- **"Üç hâl" eksikti.** Tasarım hatalı kareyi hiç çizmemiş, çünkü tasarım galerisinde de yok gibi
  davranılmış. Bizde var ve galeriden tıklanabilir olacak; hâli tanımlanmasa sayfa "Fotoğraf
  bulunamadı" derdi. 3. bölümde dördüncü satır olarak eklendi.
- **Sayaç yönü sessiz kalıyordu.** "Rozetle aynı sayı" ile "oklar galeri sırasını gezer" birlikte
  `›`'nin sayacı azaltması demek. Bunu yazmadan bırakmak, uygulamada tersini yapıp "tasarım öyle
  istiyordu" demenin kapısını açık bırakırdı; 5. bölümde açıkça yazıldı ve alternatifi gerekçesiyle
  reddedildi.
- **Erişim yolu unutuluyordu.** Sayfa üç hâli tanısa bile galeride bekleyen kare tıklanamadığı için
  hiçbir kullanıcı oraya varamazdı. 8. bölüm eklendi; Tekrar dene'nin bağlantıyı yutmaması da oradan
  çıktı.
- **Başarısız çıkarmada yönlendirme.** Bugünkü silme, sunucu reddetse bile sonraki fotoğrafa
  gidiyor — kullanıcı sildiğini sanıyor. Aynı hatayı "Kuyruktan çıkar"a kopyalamamak için 7. bölümde
  kancanın sonucu sunucunun cevabına bağlandı.
- **İki yoklama zinciri.** İlk taslakta detay sayfasına kendi kancasını yazacaktım; iki dosyada iki
  ayrı 2 saniye zinciri, ilerideki bir değişiklikte ayrışmaya açık. Proje ekranının kancası
  paylaşılıyor, `usePhotos` siliniyor.
- **Negatifi olmayan eski kayıtlar.** Plan dosyası negatifi kare kare taşımadan önce üretilmiş
  fotoğrafların satırında negatif olmayabilir; kutu her hâlde çizilip boşluğu `—` ile söyler,
  `undefined` basmaz.
