# v14 · Görev 12 — Toplu katman silme · **test turu**

**Kaynak:** yol haritası 12. madde · Fark 80, 81.

Seçim barına "Videoları sil" ve "Sesleri sil" giriyor. Kareler yerinde kalıyor, yalnız katman
düşüyor; o katmanı olmayan seçili kareler atlanıyor ve onay metni bunu söylüyor.

## Sıfırdan değil, ama sözleşme değişiyor

Bir katmanı kaldırmak zaten var — `usecases/remove_layer.py`, tek kare için. Detay sayfası onu
kullanıyor. Toplu silme aynı işin çoğul hâli, dolayısıyla **ikinci bir kullanım durumu açılmıyor**:
bugünkü `remove_layer` bir **kimlik listesi** alıyor, detay sayfası da tek elemanlı liste
gönderiyor. `remove_frames`'in kendi belgesindeki cümle bu: *"One use case for one frame and for
many."*

Adı tekil kalıyor ve doğru kalıyor: giden **bir katman**, çoğul olan kareler.

### Neden döngü değil, tek geçiş

`remove_frames` gibi: hangi dosyaların diskten gideceği **tek satır yazılmadan önce** hesaplanıyor.
Sebebi ikizler — bir videoyu iki kare tutuyorsa, ikisinden de aynı basışta alındığında dosyanın
gitmesi gerekiyor. Kare kare döngü, her adımda kaydı yeniden okumak zorunda kalır ve iki yazma
arasında bayat bir okuma dosyayı diskte bırakırdı.

### Bilinmeyen kimlik atlanıyor

Bugün `remove_layer` tanımadığı kimliğe `FrameMissing` atıyor. Toplu basışta bu yanlış: başka bir
sekme bir kareyi silmişken, bir ad yüzünden bütün basışı reddetmek geri kalanını kullanıcının kendi
kararına rağmen yapmamak olur. `remove_frames`'in kuralı buraya da geçiyor — **atlanıyor,
reddedilmiyor**. Tek kare için de aynı: pencere açıkken kaybolan kare zaten bir sonraki yoklamada
ekrandan gidiyor.

### Üçüncü kopya: gövde denetimi ortak eve taşınıyor

Aynı denetim artık üç yerde olurdu — silme, kopyalama ve katman silme. Üçünün kuralı bir, cümlesi
yalnız fiilde ayrılıyor. `domain/frame_list.py` açılıyor: `InvalidFrames` ve `checked(frames, what)`.
`remove_frames`'in `InvalidFiles`'ı oraya taşınıp adını da düzeltiyor — gövde `files` değil `frames`
taşıyor, yani ad zaten bayattı.

## Verilen kararlar

### 1 · Kim atlanıyor

Karenin o katmanı **gerçekten** taşıyor olması gerekiyor: `layers`'ta dosyası var **ve** patlamamış.
Galerinin kendi sözü bu (`layer_words.owned`) — kırmızı bir video karenin sahip olduğu bir video
değil, o rozet hiç çizilmiyor. Kırmızı katmanın yolu "Tekrar dene" ve detay sayfası.

Ekran yalnız katmanı olanları gönderiyor, yani istek onayın söz verdiği şeyin aynısı.

### 2 · Düğmeler ne zaman var

Seçimde o katmanı taşıyan **en az bir kare** varsa çiziliyor. Yoksa hiç doğmuyor: yoksa açacağı
pencere "0 karenin videosu silinsin mi?" derdi. Kopyala'nın kuralının aynısı.

*(Seçimde bekleyen kare varsa hiç çizilmemeleri Fark 82, yani 13. maddenin işi. Bu madde onu
kurmuyor.)*

### 3 · Pencerenin sözleri

| | Başlık | Gövde |
|---|---|---|
| video | `9 karenin videosu silinsin mi?` | `Kareler ve fotoğrafları kalır. Videoya bindirilen sesler de gider.` |
| ses | `9 karenin sesi silinsin mi?` | `Kareler, fotoğrafları ve videoları kalır.` |

Atlananlar varsa gövdenin **başına** bir cümle daha geliyor — başlıktaki sayıyı o açıklıyor, yani
sonra gelirse okuyan önce şaşırıyor:

> `Seçili 12 kareden videosu olmayan 3 kare atlanır.`

**Fark 81'in cümlesi "…3'ü atlanır" diyor; burada "3 kare atlanır" yazılıyor.** Sebebi dil: Türkçede
sayıya gelen ek son rakama göre değişiyor (1'i, 2'si, 3'ü, 6'sı, 20'si, 100'ü) ve bunun için bir
tablo, cümlenin değdiğinden fazla makine olurdu. Anlam ve iki sayı da duruyor.

Sözler `layer_words.js`'e giriyor — bugün de galeri rozetleriyle silme onayının aynı kelimeleri
kullanmasını orası sağlıyor.

### 4 · Pencere hangi pencere

Galeride bugün tek bir onay penceresi var ve durumu `true`/`false`. Üç pencere olunca durum
**hangisi** olmak zorunda: `null` / `"frames"` / `"video"` / `"audio"`. Aynı anda bir pencere, ve
durumun kendisi hangisi olduğunu söylüyor.

Genişlik sözlerle birlikte geliyor (madde 105): atlama cümlesi olmayan pencere 400, olan 420.

### 5 · Silindikten sonra

Seçim kapanıyor — iş bitti, ve barın öbür düğmeleri altından değişmiş bir seçimi anlatmaya devam
etmiyor. "Sil"in bugünkü davranışının aynısı.

## Yazılacak testler

### `test_photo_usecases.py` — 5 yeni

| # | Ne diyor |
|---|---|
| 1 | Bir katman, adı verilen her kareden düşüyor |
| 2 | İki karenin paylaştığı dosya, ikisi de aynı basışta bırakınca gidiyor |
| 3 | Galerinin tanımadığı kimlik atlanıyor, reddedilmiyor |
| 4 | Liste, metin kimliklerinden oluşmak zorunda |
| 5 | Videosu giden her karenin borçlu olduğu ses de kuyruktan düşüyor |

### `test_photo_routes.py` — 2 yeni

| # | Ne diyor |
|---|---|
| 6 | Rota tek basışta birden çok kareden katmanı alıyor |
| 7 | Kimlik listesi olmayan gövde reddediliyor |

### `Gallery.test.jsx` — 11 yeni

| # | Ne diyor |
|---|---|
| 8 | Barda iki katman düğmesi Sil'in sağında duruyor |
| 9 | Seçimde video yoksa Videoları sil doğmuyor |
| 10 | Seçimde ses yoksa Sesleri sil doğmuyor |
| 11 | Başlık yalnız katmanı olan kareleri sayıyor |
| 12 | Gövde atlanacakları söylüyor |
| 13 | Herkeste katman varsa atlama cümlesi yok |
| 14 | Ses penceresi videonun kalacağını söylüyor |
| 15 | Yalnız katmanı olan kareler gönderiliyor |
| 16 | Vazgeçilirse hiçbir şey gönderilmiyor |
| 17 | Katman gidince seçim kapanıyor |
| 18 | Patlamış video sayılmıyor |

**Toplam 18 yeni test.**

### Sözleşme yüzünden güncellenen testler

Bunlar yeni davranış yazmıyor, bugünkü kuralları yeni imzayla söylüyor:

- `test_photo_usecases.py`: `remove_layer`'ı çağıran yedi test kimliği listeye alıyor;
  `FrameMissing` bekleyen test yerini 3 numaraya bırakıyor; `InvalidFiles` / `InvalidFrames` içe
  aktarmaları `frame_list`'e dönüyor.
- `test_photo_routes.py`: `delete_layer_request` gövdesi `{frames: [...]}` oluyor; bilinmeyen kareyi
  404 bekleyen test artık atlandığını söylüyor.
- `PhotoDetail.test.jsx`: `removeLayer` çağrısı tek elemanlı liste bekliyor.

## Kapsam dışı

- Barın boşluğu, sarmaması ve bekleyen seçimde küçülmesi 13. maddenin işi (Fark 82, 83, 84).
- Detay sayfasının kendi katman silme pencereleri değişmiyor; yalnız çağrısı listeye dönüyor.
- Fark 101 (onayda dosya adı) bu maddede yok.

## Doğuştan yeşil olan tek test

13 numara — "herkeste katman varsa atlama cümlesi yok" — bir **yokluğu** ölçüyor ve o yokluk bugün de
doğru: düğme yokken açılacak pencere de yok. Kırmızıya zorlamak, testi değil kaynağı test turunda
değiştirmek olurdu. Nöbeti uygulama turunda, cümle doğduktan sonra tutuyor.

## Bitti sayılır

Dört komut da koşuyor. queen-editor'ın python takımı `frame_list` olmadığı için toplanamıyor
(`test_photo_usecases.py` ve onunla `test_export.py`); frontend'de 11 kırmızı duruyor. Testler
kırmızı commit ediliyor.
