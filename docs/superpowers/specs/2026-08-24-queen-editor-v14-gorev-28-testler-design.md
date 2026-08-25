# v14 Görev 28 — Galerinin indirme sırası: TEST döngüsü tasarımı

**Tarih:** 2026-08-24 · **Kaynak:** [yol haritası v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 28
**Ölçüm:** [araştırma belgesi](../research/2026-08-23-queen-editor-galeri-yavasligi.md) §0

## Neyin testi yazılıyor

Madde 28 üç istek ve iki hatadan oluşuyordu. Tasarım turunda ikisi düştü, üçü kaldı, biri de
kendiliğinden kapandı:

| Kaynak | Sonuç |
|---|---|
| *"görünmeyeni isteme — bunu kaldır"* | **Yapılıyor.** Görünürlük kapısı kalkıyor |
| *"aynı anda en fazla 2 — kontrol et doğru mu"* | **Hayır, 1 olacak.** Kullanıcı kararı: yapı en sade hâliyle kurulacak |
| *"queue gibi olsa, cevap gelince diğerini atsa"* | **Zaten böyle.** Kuyruğun bugünkü işi bu; tavan 1 ile birebir bu cümle oluyor |
| Tavanın sızması *(karo sıradan çıkıyor ama inmeye devam ediyor)* | **Kendiliğinden kapanıyor.** Karo artık kaydırmayla sıradan çıkmıyor |
| Kuyruğun yorumu bugünü anlatmıyor | **Yeniden yazılıyor.** Sayının gerekçesi 17 saniyelik bir fotoğraftan kalmaydı |

Üstüne kullanıcının aynı turda söylediği iki iş girdi: **inmemiş karonun dosya adını ekrana yazması**
ve **tavan 1'in getirdiği tıkanma riski**.

## Bugünkü sistem

Karo üç kapıdan geçince fotoğrafını çiziyor
([TileImage.jsx](../../../queen-editor/frontend/src/features/photo_generation/TileImage.jsx)):

1. **Hafıza** — URL bu oturumda ekrana gelmişse iki kapı da atlanır (madde 14).
2. **Görünürlük** — `IntersectionObserver`, 300 piksel marj. Karo görüş alanına yaklaşmadan sıraya
   bile girmiyor.
3. **Bilet** — paylaşılan kuyruktan izin gelince `src` yazılır.

Kuyruk FIFO, tavanı 2
([image_queue.js](../../../queen-editor/frontend/src/shared/image_queue.js)). Galeri
sanallaştırılmıyor: her karenin karosu DOM'da duruyor.

## Yarınki sistem

**Kapılar ikiye iniyor: hafıza → bilet.** Görünürlük kapısı gidiyor; karo mount olur olmaz sıraya
giriyor. Karolar 1'den sona doğru mount olduğu ve kuyruk FIFO olduğu için **indirme sırası kare
sırası** oluyor ve kaydırmanın hiçbir etkisi kalmıyor.

**Tavan 1.** Bir iner, biter, sıradaki çıkar.

**Karonun dört hâli var:**

| Hâl | Görünen |
|---|---|
| Sırada | Çizgili boş kutu (`wf-img`) |
| İniyor | Kutu + dönen halka (`Rendering`) — galeride tek bir tane |
| Geldi | Fotoğraf |
| Gelmedi | Çizgili boş kutu, halkasız |

`<img>` her hâlde DOM'da duruyor, ama fotoğraf gelene kadar `display: none`. Gizli resim de
indirilir — tarayıcı bunu yapar. **Dosya adının ekrana yazılmasının sebebi burada kapanıyor:** `alt`
metni yalnız görünür bir `<img>`'de çizilir. Erişilebilirlik için `alt` yerinde kalıyor.

**Bilete 30 saniye süre.** `<img>` indirmesinin zaman aşımı yok — `api.js`'teki on saniyelik iptal
yalnız `fetch` içindir. Asılı kalan bir istek ne `onLoad` ne `onError` verir, yani bileti hiç
bırakmaz; tavan 1'de bu, arkadaki bütün galerinin durması demektir. Süre dolunca slot bırakılır ve
sıradaki çıkar. Asılı karonun `src`'si yerinde kalır, halkası dönmeye devam eder: **halka fotoğrafı
anlatır, sloti değil.** Sonradan gelirse çizilir.

## Verilen kararlar

**Tavan 1, hız için değil sadelik için.** 100 karede iki slot ~35 saniye, bir slot ~70 saniye eder —
fark gerçek ama küçük. Kullanıcı kararı (24 Ağustos): *"sistemi basit tutmak, bu hız avantajları
konusunda büyük değil ama bu complexity'i maintain etmek daha sıkıntı"*. Sayı bir satır; Colab
turunda yavaş gelirse yükselir.

**Süre 30 saniye**, kullanıcı kararı. Ölçülmüş değil, yargı — ve yorumunda öyle yazacak.

**Süre karoda duruyor, kuyrukta değil.** Fotoğrafın geldiğini bilen taraf karo; kuyruk saf bir
defter olarak kalıyor ve testleri zamansız kalıyor.

**Sırada bekleyen karo halka göstermiyor.** Tasarım turunda önce *"her bekleyen halka göstersin"*
denmişti; o sırada karolar görünürlüğe göre birkaç birkaç sıraya giriyordu. Tavan 1 ile hepsi baştan
sıraya giriyor, yani galeri açılır açılmaz 90 karonun 90'ı dönerdi. Ayrımı yapmak bedava: karo zaten
`granted` değerini tutuyor.

**Üretilen kare ile inen kare karışmıyor.** İkisi de halka gösteriyor, ama üretilen karede rozet
var, inen karede yok. Kullanıcı kararı: *"üretilende zaten belirtiyoruz üstünde durumu"*.

**Yeni bileşen yazılmıyor.** Kutu (`wf-img`) ve halka
([Rendering](../../../queen-editor/frontend/src/features/photo_generation/frame_status.jsx))
uygulamada zaten var.

**Kuyruk modülü duruyor.** Sırayı `Gallery`'ye taşımak da düşünüldü — bilet nesnesi ve `done()`
gitmiş olurdu. Alınmadı: her fotoğraf bitişinde galerinin tamamı yeniden çizilirdi ve zaten büyük
olan bir dosya bir sorumluluk daha alırdı. Bir modülü silip karmaşıklığı daha büyük bir dosyaya
taşımak sadeleşme değil.

## Sabitlenecek davranışlar

### Kuyruk

| # | Ne | Neden |
|---|---|---|
| **A1** | Paylaşılan kuyruk aynı anda yalnız bir isteyene izin verir | Maddenin sayısı. Bugünkü test ikiyi sabitliyor; değişen tek satır o |

`createQueue`'nun kendi testleri kendi tavanlarını veriyor, dokunulmuyor — FIFO, atlama ve
"bir bilet bir slot" kuralları aynen duruyor.

### Karo — sıraya girme

| # | Ne | Neden |
|---|---|---|
| **A2** | Karo, görünürlük beklemeden, mount olur olmaz sıraya girer | Maddenin kendisi. Kaydırma yönü indirme sırasını belirlemeyi bırakır |
| **A3** | İzin gelmeden `src` yazılmaz | Tavan ancak sıraya girmek çizmeye yetmiyorsa tavandır |
| **A4** | İzin gelince `src` yazılır | Öbür yarısı: izin verilen karo gerçekten iner |
| **A5** | Daha önce ekrana gelmiş fotoğraf sıraya hiç girmez, doğrudan çizilir | Madde 14. Detaydan dönünce fotoğrafların kaybolmaması bu |

A2 jsdom'da gözlemci **kurulmadan** koşar: bugünkü testler bir `IntersectionObserver` taklidi
kuruyor ve onu elle sürüyordu; o taklit tümüyle siliniyor. Gözlemcinin gittiğini kanıtlayan şey bu.

### Karo — ne göründüğü

| # | Ne | Neden |
|---|---|---|
| **A6** | Sırada bekleyen karo kutu gösterir, halka göstermez | 90 dönen halka bilgi değil gürültü |
| **A7** | İzin almış karo kutu ve halka gösterir | Galeride o an ne indiğini söyleyen tek işaret |
| **A8** | Fotoğraf gelene kadar `<img>` görünmez | Şikâyetin kendisi: dosya adı ekrana yazılıyordu |
| **A9** | Fotoğraf gelince kutu gider, `<img>` görünür | — |
| **A10** | Fotoğraf gelmezse kutu kalır, halka gider | Bozuk resim ikonu ve dosya adı yerine sessiz kutu |

### Karo — bileti bırakma

| # | Ne | Neden |
|---|---|---|
| **A11** | Fotoğraf gelince bilet bırakılır | Sıranın ilerlemesi buna bağlı |
| **A12** | Fotoğraf gelmezse de bilet bırakılır | Bir bozuk dosya tavanı kalıcı olarak ısırmamalı |
| **A13** | Karo ekrandan silinince bilet bırakılır | Detaya geçiş, kare silme, sürükleme |
| **A14** | 30 saniye dolunca bilet bırakılır ve sıradaki çıkar | Tavan 1'in kendi riski: süresiz bir bilet boruyu kapatır |
| **A15** | Süre dolduktan sonra gelen fotoğraf yine çizilir ve hatırlanır | Slot bırakıldı diye indirme iptal edilmiyor |

**Bir davranışın yeni testi yok, bilerek:** süresi dolmuş bir karo fotoğrafı gelince bileti ikinci
kez bırakır, ve o ikinci bırakış slot üretmemeli. Bu kuyruğun kuralı ve kuyruğun kendi testi zaten
sabitliyor (`image_queue.test.js`, *"frees one slot however many times done is called"*). Karo
tarafında sınamak, taklit kuyruğun çağrı sayısını okumak olurdu — yani kodun kendi içini.

### Galeri — sıranın kendisi

| # | Ne | Neden |
|---|---|---|
| **A16** | Karolar kuyruğa kare sırasıyla girer — birinci kare önce, sonuncu en son | Maddenin "bitti sayılır" cümlesi |

Maddenin kendi vaadi *"galeri baştan sona sırayla doluyor"*. Bunun iki yarısı var ve ikisi de ayrı
ayrı sınanıyor: kuyruğun FIFO olması (`image_queue.test.js`) ve karonun mount olunca sıraya girmesi
(A2). Ama **birleşimini** hiçbir şey söylemiyor — karoları hangi sırada kurduğu `Gallery`'nin işi.
Bugün biri karoları ters sırada kursa takım yeşil kalır. A16 o boşluğu kapatıyor.

## Nerede duracak

| Dosya | Ne oluyor |
|---|---|
| `frontend/src/shared/image_queue.test.js` | Paylaşılan kuyruğun tavanını okuyan tek test 1'e iner. Gerisi aynı |
| `frontend/src/features/photo_generation/TileImage.test.jsx` | Gözlemci taklidi ve onu süren testler silinir; yerine A2–A15 gelir |
| `frontend/src/features/photo_generation/Gallery.test.jsx` | A16 eklenir, ve dosya kuyruğu taklit etmeye başlar |

**A16 kuyruğu taklit ediyor, gerçeğini kullanmıyor** — ve sebebi bir tuzak: paylaşılan kuyruk bir
modül tekili, jsdom'da hiçbir fotoğraf `onLoad` vermiyor, yani ilk karo tek sloti alıp hiç bırakmaz
ve dosyanın geri kalan testleri gerçek kuyrukla belirsiz hâle gelirdi. Taklit hem bunu kapatıyor hem
de A16'nin okuduğu şeyi doğrudan veriyor: **`ask` çağrılarının sırası.** Kuyruğun sıradakini
çıkarması zaten yan dosyada sınanıyor.

`TileImage.test.jsx` bu maddenin ağırlığını taşıyor. Kuyruk orada bugün olduğu gibi taklit — kuyruğun
kendi kuralları yan dosyada sınanıyor, burada sınanan **protokol**: sıraya gir, izin gelince çiz,
bitince bırak.

**İki teknik not, ikisi de tuzak:**

- Gizli `<img>`'i `getByRole("img")` bulmaz — testing-library `display: none` olanı erişilebilirlik
  ağacının dışında sayar. Sorgular `getByAltText`'e geçer. `Gallery.test.jsx` zaten `getByAltText`
  kullanıyor, o dosya bundan etkilenmiyor.
- Süre testleri sahte zamanlayıcı ister (`vi.useFakeTimers`).

## Kapsam dışı

- **Video ve ses indirmesi değişmiyor** — kullanıcı kararı (24 Ağustos). Galeri zaten hiç video
  indirmiyor; detay sayfasında sekme açılınca videonun inmesi, dalga formu için wav'ın tamamının
  inmesi ve kareden ayrıldıktan sonra inmenin sürmesi **üçü de kalıyor**: *"sıkıntı yok"*. Eksik
  değil, karar.
- **Sanallaştırma yok.** Karolar DOM'da durmaya devam ediyor; sıranın kare sırası olması buna
  dayanıyor.
- **Önbellek madde 29'un işi.** Bu madde bir koşu içindeki indirmeyi düzenliyor, koşular arasını
  değil.
- **Hız ölçülmüyor.** Tavanın ne ettiği Colab turunda (madde 30) görülür; 35 ve 70 saniye ölçülmüş
  değil, ölçülmüş rakamlardan hesaplanmış tahmindir.
- **Kod bu döngüde değişmiyor.** Testler kırmızı bırakılır; `skip`/`xfail` yok.
