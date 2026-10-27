# v14 · Görev 22 — Detayın görsel hizalaması · **test turu**

**Kaynak:** yol haritası 22. madde · tasarım v4 fark listesi 98–117 · 36, 37, 38, 39. kararlar.

Koşunun en büyük maddesi ve E bölümünün kapanışı: yirmi fark, tek ekran. Hepsi aynı sayfaya
dokunduğu için tek maddede toplandılar.

## Kapanan dört fark

Dördü de **zayıf sinyal** — üç yoldan yalnız biri gördü — ve dördü de tasarımın kendi başka bir
sözüyle ya da motorun yapabildiğiyle çelişiyor. Kararlar kaynağa 36–39 olarak yazıldı.

### 36 · Oklar uçta sönük kalmaya devam ediyor *(fark 104)*

Fark, okların her karede tam opaklıkta ve tıklanabilir durmasını istiyor, ve kendi notu ekliyor:
*"tasarım dizinin ucunda oka basılınca ne olacağını söylemiyor."*

Tasarım başka bir yerde **uçların dönmediğini** söylüyor — ilk kareden son kareye atlanmıyor.
Dönmüyorsa uçtaki oka basınca hiçbir şey olmaz, ve hiçbir şey yapmayan tam opak bir ok orada bir
kare olduğunu söyler. Sönüklük o cümlenin dürüst karşılığı.

Gözlem muhtemelen ortadaki bir kareyi çizen artboard'dan geliyor: orada iki ok da zaten tam opak.

### 37 · Kuyruktaki kopya karede şerit duruyor, etiket geliyor *(fark 112)*

Farkın iki yarısı var. **Şeridin hiç çizilmemesi yarısı alınmıyor:** aynı listenin 92. maddesi
kuyrukta bekleyen katmanın *sekmesi açılınca* kutusunda ne yazacağını tarif ediyor ve o 19. maddede
uygulandı; 99. maddesi de düğmenin *sekmede* durmasını istiyor. Şerit kalkarsa ikisi de ulaşılamaz
olur.

**Etiket yarısı alınıyor:** sahnede duran resmin bu kareye ait olmadığını bugün hiçbir şey
söylemiyor. Köşeye ikinci bir etiket giriyor — **"kaynak foto · kopya kare"**.

### 38 · "Kuyruktan çıkar — kare kalır" yazılmıyor *(fark 99'un ikinci metni)*

Kuyruk **kareyi** çıkarıyor, katmanı değil: `remove_frames.py` kimliklerle çalışıyor ve üretilmemiş
bir kareyi kuyruktan düşürüyor. Bir katmanı kuyruktan alıp kareyi bırakan bir basış yok, dolayısıyla
"kare kalır" diyen bir düğme motorun yapamadığı bir şeyi vaat ederdi.

Farkın asıl şikâyeti — *"bu düğme yalnız foto sekmesinde vardır"* — düzeltiliyor: kuyrukta bekleyen
bir katmanın sekmesinde de aynı düğme, foto sekmesinin taşıdığı sözlerle duruyor.

### 39 · Hap fotoğrafın içine inmiyor *(fark 107'nin ikinci yarısı)*

Köşe sahneye göre konumlanıyor, fotoğrafa göre değil: resim sahnenin ortasında `contain` ile
duruyor ve sol kenarının nerede olduğu ancak yerleşimden sonra belli. "Fotoğrafın biraz içi" diye
tutturulacak bir kenar yok. Hapın **nabız atan noktası** alınıyor, konumu bugünkü yerinde kalıyor.

## Uygulanan on altı fark

### Sahne

| Fark | Ne değişiyor |
|---|---|
| 103 | Sahne üstten ferahlıyor (24 → **48**), yanlar ve alt 24'te kalıyor; şerit 16 → **12** |
| 105 | "bekliyor" 14 punto monospace, "henüz üretilmedi" 10 punto ve bir ton daha soluk |
| 106 | Başlık normal yazı ve 13 punto, sebep monospace ve 11 — bugünkünün tam tersi |
| 112 | Kopya karenin köşesine "kaynak foto · kopya kare" |
| 113 | Katman üretilirken resim duruyor, üstüne koyu bir kutu iniyor: nabız atan nokta ve "video üretiliyor…" |

113'ün istisnası: **fotoğrafın kendisi üretilirken** ekranda tutulacak bir resim yok, orada bugünkü
dönen gösterge kalıyor.

### Haplar ve düğmeler

| Fark | Ne değişiyor |
|---|---|
| 107 | "yeniden üretilecek — kuyrukta" hapına nabız atan nokta |
| 108 | Tekrar denendiğinde hap "kuyrukta — tekrar denenecek" diyor |
| 109 | Hatalı katmanın düğmesi "Tekrar dene — bu kareye" |
| 100 | Yanında ikinci yol duruyor: "Kareyi sil" |
| 99 | Kuyrukta bekleyen katmanın sekmesinde de kuyruktan çıkarma düğmesi |
| 110 | "Yeniden üret" tam boy ve vurgu dolgulu; altındaki silme küçük kalıyor |
| 111 | Üretim sürerken pasifleşen silme düğmesi kırmızıyı bırakıyor |

### Onay pencereleri

| Fark | Ne değişiyor |
|---|---|
| 101 | Katman silme onayı silineceği adıyla anıyor: "P0_0_V1_0.mp4 ve üzerindeki ses…" |
| 102 | Tek kare silme onayının başlığı sayıyor: "1 kare silinsin mi?" — seçim barının diliyle aynı |

### Kutular

| Fark | Ne değişiyor |
|---|---|
| 98 | Negatif prompt düzenlenebiliyor, değişince kutusu vurgu rengine dönüyor |
| 117 | Prompt kutusunun yazısı monospace — görsel dil kuralının kendi cümlesi |

**98 motora da dokunuyor.** `/regenerate` bugün gövdede `frame`, `layer`, `prompt` ve `mode`
taşıyor; negatif yok, ve `regenerate` yeni karenin satırına *kaynağın* negatifini yazıyor
(`regenerate.py:96`). Kutuyu yazılabilir yapıp bunu bırakmak, vurgu çerçevesinin yeni karenin farklı
olacağını söylediği ama negatifin hiç yola çıkmadığı bir ekran olurdu. Yol `prompt`'un yolu:
kullanıcıya ne gösterildiyse o iniyor.

Negatif yalnız **fotoğrafın** satırına yazılıyor. Üstündeki katmanlar altlarındakinden yapılıyor ve
negatif taşımıyorlar — bu kural bugün de böyle, değişmiyor.

### Oynatıcı

| Fark | Ne değişiyor |
|---|---|
| 114 | Zaman etiketleri ve ilerleme çizgisi videonun içine, alt kenarın biraz yukarısına iniyor; çizgi çerçevesiz |
| 115 | Dalga da videonun içine giriyor, çalınmamış çubuklar saydam beyaza dönüyor |
| 116 | Oynat düğmesi ince çerçeve ve daha opak zemin alıyor; içindeki işaret metin karakteri değil çizim |

## Kapsam dışı

- **97** (izleme moda uyar) kullanıcı kararıyla B bölümünde kapandı.
- **118, 119** öksüz: tasarımda karşılığı olmayan, uygulamanın kendi kararları. Duruyorlar.
- **96** 9. maddede kapandı.

## Yazılacak testler

### `PhotoDetail.test.jsx` — 18 yeni

| # | Ne diyor | Fark |
|---|---|---|
| 1 | Sahne üstten ferah başlıyor, şerit ona yaklaşıyor | 103 |
| 2 | Bekleyen karenin iki satırı arasında kademe var | 105 |
| 3 | Hatalı sahnede başlık ve sebep yazılarını değiş tokuş ediyor | 106 |
| 4 | Katman üretilirken resim duruyor, üstüne kutu iniyor | 113 |
| 5 | Fotoğrafın kendisi üretilirken gösterge dönmeye devam ediyor *(doğuştan yeşil)* | 113 |
| 6 | Kopya karede resmin kimin olduğu yazıyor | 112 · karar 37 |
| 7 | Kuyruğa girdi hapı nabız atıyor | 107 |
| 8 | Tekrar denenen katmanın hapı bunu söylüyor | 108 |
| 9 | Hatalı katmanın düğmesi yeni kare açmadığını söylüyor | 109 |
| 10 | Hatalı katmanda ikinci yol duruyor | 100 |
| 11 | Kuyrukta bekleyen katmanın sekmesinde de düğme var | 99 · karar 38 |
| 12 | Yeniden üret tam boy ve dolgulu, silme küçük | 110 |
| 13 | Üretim sürerken silme düğmesi kırmızıyı bırakıyor | 111 |
| 14 | Katman onayı silineceği adıyla anıyor | 101 |
| 15 | Kare onayı kareyi sayıyor | 102 |
| 16 | Negatif yazılabiliyor | 98 |
| 17 | Değişen negatifin kutusu işaretleniyor | 98 |
| 18 | Yazılabilir prompt kutusu monospace | 117 |
| 19 | Salt okunur kutu da monospace | 117 |

### `LayerPlayer.test.jsx` — 5 yeni

| # | Ne diyor | Fark |
|---|---|---|
| 20 | Zaman etiketleri videonun içinde duruyor | 114 |
| 21 | İlerleme çizgisi çerçevesini bırakıyor | 114 |
| 22 | Dalga da videonun içinde | 115 |
| 23 | Çalınmamış çubuklar saydam beyaz | 115 |
| 24 | Oynat düğmesi çerçeve ve çizim taşıyor | 116 |

### Motor tarafı — 3 yeni

| # | Dosya | Ne diyor |
|---|---|---|
| 25 | `test_photo_usecases.py` | Yeni fotoğrafın satırı verilen negatifi taşıyor |
| 26 | `test_photo_usecases.py` | Fotoğrafın üstündeki katman ne verilirse verilsin negatif taşımıyor |
| 27 | `test_photo_routes.py` | Gövdedeki negatif yeni karenin satırına ulaşıyor |

### Düzeltilen üç test

- `puts the frame back in line without asking` — "Tekrar dene" arıyor, **kırmızı**.
- `asks before deleting, then opens the next photo` — "Bu kare silinsin mi?" arıyor, **kırmızı**.
- `takes it out of the queue without asking` — aynı başlığın **yokluğunu** arıyor; adı düzeltiliyor,
  iki tarafta da yeşil.

### Doğan tutamaklar

Hepsi **uygulama turunda** doğuyor.

| Tutamak | Ne |
|---|---|
| `data-stage` | detayın sahnesi — üst boşluğu oradan okunuyor |
| `data-making` | resmin üstüne inen koyu kutu |
| `data-scene` | oynatıcının kendi 16:9 sahnesi |
| `data-track` | zaman ve ilerme satırı |

**5. test doğuştan yeşil.** 113'ün istisnasını ölçüyor: fotoğrafın kendisi üretilirken ekranda
tutulacak resim yok, dolayısıyla gösterge kalıyor. Bugün de öyle. Test yazılıyor çünkü farkın
cümlesi bu durumu hiç anmıyor ve *"resmi koru"* diye okunursa olmayan bir resim korunmaya
çalışılır — testin işi o okumayı engellemek.

**Ön yüzde 25 yeni test: 494 → 519, yirmi altısı kırmızı** (24 kırmızı doğan + 2 düzeltilen).
**Motorda 3 yeni test: 694 → 697, üçü de kırmızı.**

## Bitti sayılır

Dört komut da koşuyor; queen-editor'ün Python takımında **3**, frontend takımında **26** kırmızı
duruyor. Testler kırmızı commit ediliyor.
