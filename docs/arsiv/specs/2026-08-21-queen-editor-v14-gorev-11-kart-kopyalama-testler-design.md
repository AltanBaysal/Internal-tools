# v14 · Görev 11 — Kart kopyalama · **test turu**

**Kaynak:** yol haritası 11. madde · İstek 7 · Fark 77, 78, 79 · brif §7.

Kullanıcı bir kartı kendi eliyle çoğaltabilsin. Kopya **birebir ikiz**: fotoğraf, video, ses ve
bilgiler gelir, üretilecek bir şeyi kalmaz.

## Sıfırdan değil

Kopya kare kavramı uygulamada zaten var — `domain/copy_frame.py`. Bir kareye birden fazla video
varyantı istendiğinde fazlalıklar kopya kare olarak doğuyor: kaynağın dosyasını gösteren satırlar
yazılıyor, kaynağın üstüne yerleşiyorlar, galeride normal kare gibi davranıyorlar. Eksik olan üç şey:

1. Kullanıcının bunu isteyebileceği bir yol (bar düğmesi ve kısayol).
2. **Bütün** katmanları taşıyan bir taşıma — bugünkü `carry_layers` yalnız üretilecek katmanın
   altındakileri veriyor, çünkü bugünkü kopya üstünü kendisi üretiyor.
3. Kopyanın kendi adı.

## Verilen kararlar

### 1 · Kimlik: önek başta

`P11_1` kopyalanınca `C1_P11_1`. Sonda olsaydı katman kuyruklarının `_V1_0` / `_S1_0` çiftleriyle
karışırdı (Fark 78).

Kopyanın kopyası **düz**: `C1_P11_1` kopyalanınca `C2_P11_1`, iç içe değil. Önek tek parça kalır,
düğmeye kaç kez basılırsa basılsın. İndeks **tabana göre** sayılır ve boşluk bırakmaz — silinmiş bir
kopyanın adı yeniden kullanılmaz, `next_id`'nin kuralı burada da geçerli.

**Sayı ve varyant okunurken önek soyulur.** `C1_P11_1` hâlâ 11 numaralı prompt'un 1. varyantıdır:
kaynağının resmini paylaşıyor, o resmi yapan prompt da odur. Soyulmazsa kopya kare üstünde
"yeniden üret" ailesini bulamaz — bugün `copy_frame.family()` sayıyı kimlikten okuyor.

### 2 · İkiz tam

Kaynağın **gerçekten sahip olduğu** her katman kopyaya geçer: satırlar kaynağın dosyalarını gösterir,
diskte tek dosya kalır. Kuyruğa hiçbir şey girmez, plan satırı yazılmaz — üretilecek bir şey yok, ve
kopya galeriye kaydın kendisinden düşer (`list_frames`'in plan tanımayan kareler döngüsü).

**Patlamış katman taşınmaz.** Kaynağın kırmızı videosu diskte olmayan bir dosyayı adlandırıyor;
kopyaya `done` satırı olarak yazmak yalan olurdu. Kural taşımanın tek evinde durur, yani bugünkü
`carry_layers` da onu kazanır.

### 3 · Yerleşim ve seçim

Kopya kaynağın **bir üstüne** iner (`placed`, bugünkü kural). Seçim kopyaya geçer; **fark ediliş
budur**, ayrı bir bildirim yok.

### 4 · Bar ve kısayol

Bara "Kopyala" girer — **Sil'in solunda, çerçevesiz**. Seçim yalnız bekleyen karelerden oluşuyorsa
düğme **hiç doğmaz**; karışık seçimde durur, basılınca yalnız üretilmiş kareler çoğalır.

Kısayol **Ctrl + D**, ve tarayıcının yer imi penceresi `preventDefault` ile alınır. Onay penceresi
açıkken çalışmaz — Escape'in kuralı.

### 5 · Rota

`POST /api/projects/<proje>/frames/copy`, gövde `{frames: [...]}` — silme rotasının aynısı.
Cevap `{copies: [...], frames: [...]}`: galeri cevapla birlikte döner, üretim rotalarının kuralı,
çünkü ekran yoksa ikinci bir gidiş dönüş yapmak zorunda kalır.

Kuyruk **çalıştırılmaz**: üretilecek bir şey yok, dolayısıyla `Busy` de yok.

## Yazılacak testler

### `test_photo_name.py` — 4

| # | Ne diyor |
|---|---|
| 1 | Kopyanın kimliği kaynağının adı, önü ekli |
| 2 | Kopya hâlâ kaynağının prompt numarasını ve varyantını taşıyor |
| 3 | Öneksiz bir ad kendi tabanıdır |
| 4 | İkiz, tabanının taşıdığı en yüksek kopya indeksinin bir üstünü alıyor — boşluk kullanılmıyor |

### `test_photo_usecases.py` — 14

| # | Ne diyor |
|---|---|
| 5 | İkiz kaynağının sahip olduğu her katmanı taşıyor |
| 6 | İkizin satırları kaynağın kendi dosyalarını gösteriyor |
| 7 | İkiz her katmanın yapıldığı sözleri taşıyor |
| 8 | İkiz videonun modunu ve nerede bittiğini de taşıyor |
| 9 | İkize hiçbir şey borçlu değil — kuyrukta işi yok |
| 10 | İkiz kaynağının tam bir üstüne iniyor |
| 11 | Cevap doğan ikizleri adlarıyla söylüyor |
| 12 | İkinci kopya kopyanın kopyası, iç içe ad değil |
| 13 | Henüz üretilmemiş kare atlanıyor |
| 14 | Galerinin tanımadığı kimlik atlanıyor, reddedilmiyor |
| 15 | Patlamış katman ikize taşınmıyor |
| 16 | Hiçbir kopya doğmadıysa sıra dosyasına yazılmıyor |
| 17 | Liste, metin kimliklerinden oluşmak zorunda |
| 18 | Olmayan projede kopyalama reddediliyor |

### `test_photo_routes.py` — 3

| # | Ne diyor |
|---|---|
| 19 | Rota ikizleri ve indikleri galeriyi birlikte veriyor |
| 20 | **İkizlerden birini silmek öbürünün resmini diskte bırakıyor** |
| 21 | Kimlik listesi olmayan gövde reddediliyor |

20 numara maddenin "bitti sayılır" cümlesinin kendisi ve gerçek dosyalarla, uçtan uca kanıtlanıyor.

### `Gallery.test.jsx` — 8

| # | Ne diyor |
|---|---|
| 22 | Barda Kopyala, Sil'in solunda duruyor |
| 23 | Seçim yalnız üretilmemiş karelerden ibaretse Kopyala doğmuyor |
| 24 | Karışık seçimde yalnız üretilmiş kareler gönderiliyor |
| 25 | Seçim ikizlere geçiyor |
| 26 | Ctrl + D düğmenin yaptığını yapıyor |
| 27 | Ctrl + D tarayıcıdan alınıyor |
| 28 | Onay penceresi açıkken Ctrl + D çalışmıyor |
| 29 | Kopyalanacak kare olmayan seçimde kısayol hiçbir şey göndermiyor |

**Toplam 29 test.** 21'i python (toplanamayan dosyalarda), 8'i ekranda — ekranda 5 kırmızı, 3
doğuştan yeşil.

## Doğuştan yeşil olan üç test

| # | Neden bugün de yeşil |
|---|---|
| 23 | Kopyala düğmesi hiç yok, dolayısıyla yokluğu her seçimde doğru |
| 28 | Kısayolu dinleyen kimse yok, dolayısıyla onay penceresi de onu durdurmuş sayılıyor |
| 29 | Aynısı: dinleyen olmayınca hiçbir şey göndermemek kendiliğinden oluyor |

Üçü de bir **yokluğu** ölçüyor ve o yokluk bugün zaten doğru. Kırmızıya zorlamak — mesela düğmeyi
önce koşulsuz çizdirmek — testi değil kaynağı test turunda değiştirmek olurdu. Nöbeti uygulama
turunda tutacaklar: 23 düğme doğduktan sonra koşulun kendisini, 28 ve 29 dinleyici bağlandıktan
sonra iki korumasını sınıyor.

## Kabuk hattı: toplama hatası

Testler henüz olmayan adları içe aktarıyor (`copy_frames`, `copy_id`, `copy_parts`, `next_copy_id`),
yani üç python dosyası **toplanamıyor** — ve `test_export.py` de onlarla birlikte düşüyor, çünkü
`test_photo_usecases`'ten yardımcı alıyor. queen-editor'ın python takımı bu turda hiç koşmuyor. Bu,
9. maddede verilen kararın aynısı: dürüst kırmızı, bedeli de yazılı. Alternatifi — çağrılmayan bir
iskelet sınıf — test turunda kaynağa dokunmak olurdu.

## Kapsam dışı

- Barın görünümü (öğe aralığı, sarmama) 13. maddenin işi.
- Katman silme düğmeleri 12. maddenin işi.
- `useGeneration` ve `api.js` bağlantısı, bugün `removeFrames`/`removePhotos` nasıl duruyorsa öyle
  duruyor: kancanın düz geçiş çağrıları o dosyada sınanmıyor, sunucu tarafını rota testi tutuyor.

## Bitti sayılır

Dört komutun dördü de koşuyor; queen-agent'ın ikisi yeşil, queen-editor'ın python takımı toplama
hatasıyla duruyor, frontend takımında 5 kırmızı var. Testler kırmızı commit ediliyor.
