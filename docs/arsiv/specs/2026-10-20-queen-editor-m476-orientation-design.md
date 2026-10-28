# Madde 476 · Üretimin yönü, sunucu tarafı — tasarım

**Tarih:** 20 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md),
476 · v10-3b · **Dal:** `feat/queen-editor-v10` · **Kurallar:** queen-editor
[FOUNDATION](../../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)
· **Sayılar:** [475'in araştırması](../research/2026-10-20-queen-editor-m475-h3-16-9.md)

## Kullanıcıdan gereken

Hiçbir şey. Madde 20 Ekim'de hizalandı, sayıları kullanıcı 475'te onayladı. Ana ajan 20 Ekim'de iki
açık soruyu kullanıcının sözünden cevapladı *("üretim başına negative prompt gibi 2 opsiyon")*: yön,
negatif prompt gibi, bir üretimin istendiği her yerde istekle gelir. Bu, referans havuzundan
üretimde de, *Yeniden üret*te de böyledir (aşağıda, 3 ve 4).

## Ne, neden

Bugün üretim yalnız dikey. Bu parçadan sonra her üretim bir yön taşır, `yatay` ya da `dikey`;
varsayılan `yatay`. Fotoğraf o yönün boyutunda üretilir. Video üreticisi yön sormaz, fotoğrafın
oranını izler. Ekrandaki seçenek 477'de gelir; o gelene kadar API alanı kabul eder ve yeni her üretim
yatay çıkar. **Bu, maddenin bölünmesinin bilinen ve kabul edilmiş sonucudur.**

| Yön | Fotoğraf | H3 videosu | Director panelinin hazır ayarı |
|---|---|---|---|
| `yatay` | 1536 × 864 | 1024 × 576 | `576p` |
| `dikey` | 1024 × 1536 *(bugünkü)* | 576 × 864 *(bugünkü)* | `540p` *(bugünkü)* |

İki satırın her birinde fotoğrafın ve videonun oranı birebir aynı (16:9 ve 2:3). Videonun iki kenarı
da H3'ün 32 piksellik ızgarasında (475).

## Bugün — koddan okunanlar

- **Boyutlar yalnız üç grafikte duruyor.** Fotoğraf grafiğinde `"1"` *Width* ve `"11"` *Height*
  (`easy int`) var, `EmptyLatentImage` bunları okuyor. İki H3 grafiğinde Director `"2730"`'un
  `width` / `height`'ı ve `timeline_data`'nın `resolution.resolution`'ı var. `model_groups`'ta,
  producer'larda ve başka hiçbir yerde boyut yok.
- **Negatif prompt bir üretimin satırında gidiyor.** Rota istekten alıyor, `start_batch` →
  `plan_frames` onu her fotoğraf satırına yazıyor, `run_loop` satırdan okuyup
  `producer.generate(…)`'e veriyor. *Yeniden üret*te (`regenerate`) negatif de istekten geliyor
  ve yalnız fotoğrafın satırına yazılıyor.
- **Üreticilerin tek çağrı biçimi var** (`ports.PhotoGenerator.generate`). Fotoğrafın, H3'ün ve sesin
  üreticisi aynı argümanları alıyor, kullanmadığını yok sayıyor. `generate_batch` yalnız fotoğrafta
  var.
- **Varyantlar** aynı şeyden yapılıyorlarsa bir batch'te birlikte üretiliyor
  (`variant_batch.MADE_FROM`).
- **Video, kaynağını bellekte bayt olarak alıyor.** `source = (ad, bayt)`, kare her zaman PNG:
  `photo_file` `.png` verir, ComfyUI'nin `SaveImage`'ı PNG yazar, `ffmpeg_stills` ilk kareyi
  `first.png` olarak çıkarır.
- **REF2VA** (havuzdan kart) bir fotoğraftan başlamaz; boyutu bugün grafiğin kendi 576 × 864'ü.

## Ne değişir

### 1. `domain/orientation.py` — yönün kuralları, tek yerde

`production_mode.py`'nin eşi:

- `LANDSCAPE = "yatay"`, `PORTRAIT = "dikey"`, `ALL`, satırdaki alanın adı `FIELD = "orientation"`.
- `DEFAULT = LANDSCAPE`: yönü söylenmeden istenen bir üretim yataydır.
- `validate(value)`: bilinmeyen bir değer `InvalidOrientation` verir, cümlesi Türkçe.
- `of(job)`: satırın yönü. **Alanı olmayan satır `dikey` okunur.** 476'dan önce planlanan her satır
  dikeydi; bu yüzden eski bir karenin *Tekrar dene*si ve *Kaldığı yerden devam et*i bugünkü gibi
  dikey çıkar. Bu varsayılan `DEFAULT`'tan ayrıdır: biri yeni bir isteğin, öteki eski bir satırın
  cevabı.

### 2. Fotoğraf: satırda gider, üreticide boyuta döner

- **Rota** `POST …/generate`, `body.get("orientation", DEFAULT)` alır ve `start_batch`'e verir.
  `InvalidOrientation` gelirse 400 ve `"field": "orientation"` döner, `InvalidMode` gibi.
- **`start_batch`** değeri doğrular, `plan_frames` her fotoğraf satırına `orientation` yazar.
- **`variant_batch.MADE_FROM`** alanı içerir, yani iki yönün varyantları aynı batch'e girmez.
- **`run_loop`** `orientation.of(current)`'i `generate`'e ve `generate_batch`'e verir.
- **Port** (`generate`, `generate_batch`) `orientation=None` alır. `None`, `seconds=None` gibi
  "grafiğin kendi" demektir. Döngü her zaman bir yön verir; `None` yalnız doğrudan çağıranlar için.
  Ses üreticisi argümanı alır ve yok sayar.
- **`ComfyPhotoGenerator`** boyut tablosunu tutar (`SIZES`) ve `"1"` ile `"11"`'e yazar. Düğüm yoksa
  hangi düğümün eksik olduğunu söyleyerek durur, `BATCH_NODE`'un yaptığı gibi.
- **`fits_batch`** dikeyin rakamıyla tartmaya devam eder. Dikeyin latent'i (128 × 192) yatayınkinden
  (192 × 108) büyük — 24.576'ya 20.736 —, yani yatay bir batch güvenli taraftan, gerekenden yaklaşık
  %18,5 fazla bellekle tartılır. Yorum bunu söyler.

### 3. Video: fotoğrafın oranını izler

- **`ComfyH3VideoGenerator`** yön sormaz. Kareden yapılan her videoda (düz, döngü, bağlantılı) yönü
  **elindeki kaynak fotoğrafın PNG başlığından** okur: IHDR'nin genişliği ve yüksekliği. Genişlik
  yükseklikten büyükse yatay, değilse dikeydir. Diske ya da ağa ek bir gidiş yoktur, baytlar zaten
  bellekte.
- Tablosu (`SIZES`) Director'ın `width` / `height`'ını ve `timeline_data.resolution.resolution`'ı
  yazar: yatayda `576p`, dikeyde `540p`.
- **Eski dikey kareler** PNG'leri dikey olduğu için dikey video verir. Yeni bir alan, yeni bir kayıt
  ya da yeni bir okuma gerekmez.
- **Bağlantılı video** yatay bir kareden dikey bir kareye bağlanırsa boyut kaynağın, yani ilk
  karenindir. FL2VA son kareyi ortadan kırparak tuvale oturtur (475).
- **PNG olmayan bir kaynak** (`NotAPicture`, `frame_level`) yalnız o karenin hatasıdır: kare kırmızı
  olur ve kuyruk devam eder. Bugün böyle bir kaynak yok; satır, "boyutu okunamadı" yerine gerçek
  sebebi söylesin diye var.
- **REF2VA** bir fotoğraftan başlamaz. Yönü, öteki üretimlerde olduğu gibi istekle gelir
  *(ana ajan, 20 Ekim)*. `POST …/references/produce` `body.get("orientation", DEFAULT)` alır,
  `queue_references` doğrular, `plan_reference_cards` her kart satırına yazar, ve üretici REF2VA'da
  boyutu satırın yönünden alır. Alanı olmayan eski kart satırları `dikey` okunur, yani bugünkü
  576 × 864'le çıkar. Havuzun ilk resmine bakılmaz.

### 4. *Yeniden üret*

Fotoğrafı yeniden üretirken yön, negatif gibi istekten gelir, varsayılan `yatay`
*(ana ajan, 20 Ekim)*. `POST …/regenerate` alır, `regenerate` yalnız fotoğrafın satırına yazar.
Video ve ses satırları negatifi nasıl bırakıyorsa yönü de öyle bırakır. Bilinmeyen değer 400 ve
`"field": "orientation"` döner.

**Bilinen sonuç:** 477 alanı gönderene kadar eski dikey bir fotoğraf yeniden üretilince yatay çıkar.
**477'ye not:** *Yeniden üret* penceresi de seçeneği alır, çünkü negatif orada da ayarlanıyor.

### 5. Grafikler olduğu gibi kalır

Üç grafik export edildiği gibi, dikey kalır. İki tablo kodda durur, her işte yazılır. Grafiğin kendi
sayıları yalnız `None` ile çağrılınca kullanılır. `test_workflow_asset` dikey tablonun grafiklerin
kendi sayılarıyla aynı olduğunu tutar, yani iki yer birbirinden kopamaz.

### 6. Testler — `test_workflow_asset`

Her iki yön için: fotoğrafın ve videonun oranı **birebir** aynı (`pw · vh == ph · vw`), videonun iki
kenarı 32'nin katı, adı neyse şekli o (yatay geniş, dikey uzun), ve 475'in onaylanan sayıları. Dikey
tablo grafiklerin kendi sayılarına eşit. Bugünkü %1'lik grafik testi bu birebir teste dönüşür.

### 7. Ekran ve `settings.json`

Değişmez. Galerinin kartı plan satırını yaydığı için yeni satırlarda `orientation` alanı da gelir;
ekran onu okumaz. Panelin açılışta göstereceği yön (`settings.json`) 477'nindir.

## Maliyet

Koddan sayıldı, ölçülmedi.

| İşlem | Bugün | Sonra |
|---|---|---|
| Fotoğraf üretimi | grafiği bir kez okur | aynı; bellekte iki değer daha yazılır |
| Video üretimi | grafiği bir kez okur, kaynağı bir kez yükler | aynı; yön bellekteki baytların ilk 24'ünden okunur |
| `plan.json` | her istekte bir kez okunur, bir kez yazılır | aynı; satır başına bir alan |
| Galeri, kuyruk, export | — | değişmez |

Drive'a ya da ComfyUI'ye ek bir gidiş yok, O(1) da değil, sıfır. Proje, kare ve dosya sayısıyla
büyüyen bir şey eklenmiyor.

## Ne kaybolabilir, ne bozulabilir

- **Eski satırlar ve dosyalar** okunur, yeniden yazılmaz. Alanı olmayan satır `dikey`; eski
  `plan.json` olduğu gibi kalır, yeni satırlar onun sonuna eklenir (472'nin kaydı).
- **Aynı anda iki istek**: yön satırın içinde gider, ortak bir durum tutulmaz. Biri yatay, öteki dikey
  iki batch aynı kuyrukta kendi yönleriyle üretilir; varyant batch'i yönleri karıştırmaz.
- **Çökme**: yeni bir dosya ya da yazma sırası yok. Satır, üretimden önce yazılan plan satırıdır.
- **URL'den gelen değer** yalnız `ALL`'daki iki kelimeyle karşılaştırılır. Yola, dosya adına ya da
  grafiğe ham hâliyle hiçbir zaman girmez: tabloda bir anahtar olarak kalır.

## Bu maddenin kararları

1. **Kurallar `domain/orientation.py`'de**, `production_mode.py`'nin eşi. Değerler `yatay` / `dikey`,
   alan `orientation`.
2. **Alanı olmayan satır `dikey`, yeni istek `yatay`.** İki ayrı varsayılan, ikisi de adıyla.
3. **Video yönü fotoğrafın PNG başlığından okur.** Kayıt ya da satır taşımaz; eski kareler kendiliğinden
   dikey kalır.
4. **REF2VA ve *Yeniden üret* yönü istekten alır**, varsayılan `yatay` *(ana ajan, 20 Ekim)*.
5. **Tablolar kodda, grafikler export edildiği gibi.** Dikey tablo grafiklerle bir testle bağlı.
6. **`fits_batch` dikeyle tartar**: büyüğün rakamı, yatayda güvenli taraf.

## Sınırlar

- **Ekran 477'de.** O gelene kadar yeni üretimler, REF2VA kartları ve fotoğrafın *Yeniden üret*i
  yatay çıkar.
- **Export'un tuvali 478'de.** Bu parçada dokunulmaz.
- **Timeline'daki resim satırlarının `source_width` / `source_height`'ı** export'un örneğinden
  (1024 × 1536) kalır, yazılmaz. Kaynaktan doğrulandı: reviewer DaSiWa'nın `main`'inde
  `nodes_minimax_h3_director.py`, `helper_minimax_h3_director.py` ve
  `nodes_minimax_h3_director_guide.py`'yi okudu; hiçbiri bu alanları okumuyor, resimler
  `scale_input_media(value, input_scaling, width, height)` ile Director'ın `width` / `height`'ına
  ölçekleniyor. 478'in Colab denemesine yalnız yatay videonun görüntüsüne bakmak kalıyor.
- **Fotoğrafın yatay boyutunda figür tekrarı** riski 475'te kabul edildi. 478'in Colab denemesinde
  bakılır, yedek boyut 1344 × 768.
- Frontend ve notebook değişmez, `dist` yeniden kurulmaz.

## Bitti sayılır

1. Testler gösteriyor ki:
   - `orientation` verilmeyen bir üretimin satırı `yatay`, verilen `dikey` ise `dikey`; bilinmeyen değer
     400 döndürüyor — üretimde ve *Yeniden üret*te `"field": "orientation"` ile, referanstan üretimde
     o kapının öteki retleri gibi alansız;
   - alanı olmayan eski bir satır `dikey` okunuyor ve üreticiye `dikey` gidiyor;
   - fotoğraf üreticisi yataya 1536 × 864, dikeye 1024 × 1536 yazıyor; `None` grafiğe dokunmuyor; düğüm
     yoksa adını söylüyor; batch'te de aynı;
   - iki yönün varyantları bir batch'te birleşmiyor;
   - H3 üreticisi yatay bir PNG'den 1024 × 576 / `576p`, dikey bir PNG'den 576 × 864 / `540p` yazıyor,
     I2VA'da da FL2VA'da da; REF2VA'da satırın yönünü izliyor; PNG olmayan bir kaynak karenin hatası;
   - gerçek döngü ve gerçek üreticilerle (`test_producer_contract`): yatay bir satırın fotoğrafı
     1536 × 864, ondan yapılan video 1024 × 576; dikey satır ve alanı olmayan eski satır 1024 × 1536
     ve 576 × 864;
   - `test_workflow_asset`: iki yönde oranlar birebir, video 32 ızgarasında, şekiller adlarına uygun,
     475'in sayıları, dikey tablo grafiklere eşit.
2. İki satır yeşil: `python -m pytest queen-editor -q` ve `npm test --prefix queen-editor/frontend`.
3. Yatay H3'ün gerçek görüntüsü 478'in sonundaki Colab denemesinde görülür *(kullanıcı)*.
