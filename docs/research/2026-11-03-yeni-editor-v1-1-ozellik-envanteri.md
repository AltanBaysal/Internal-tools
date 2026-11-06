# Yeni editör — 1. Dışarıya açılanlar

Agent'ın ve UI'ın kullandığı endpoint'ler, gruplu.

Yeni editör queen-editor'ı kopyalamaz, ondan iyisini yapar: agent'a en fazla kontrolü verir
(kullanıcı, 3 Kasım — "Queen Editor'e bağlı kalma, burada Queen Editor'den daha iyi bir şey yapmak
istiyoruz, agent'a maksimum kontrol vermek istiyoruz.").

Core sade kalır, akıl agent'tadır (kullanıcı, 3 Kasım — "Agent'a maksimum kontrol veriyoruz ve
core'u daha basit bırakıyoruz. Seed gibi gerçekten sorun olmayacak şeylerin varsayılan değeri
olabilir, ama video promptu gibi şeyler olmaz."). Core, agent'ın yerine karar vermez; yalnız seed
gibi zararsız değerlerin varsayılanı vardır.

## Nasıl okunur

Her endpoint bir fiil ve bir adresten oluşur. Dört fiil var:

- **GET** — okur. Hiçbir şeyi değiştirmez.
- **POST** — yeni bir şey yapar: bir proje oluşturur, bir üretim başlatır.
- **PATCH** — var olan bir şeyin bir kısmını değiştirir: bir projenin adını, bir edit'in adını.
- **DELETE** — siler.

Adresteki `{id}`, hangi şeyin kastedildiğidir: `/projects/{id}` bir projeyi gösterir.

Bütün endpoint'ler `/api` altındadır (ör. `/api/projects/{p}/frames`); `GET /api` onların listesidir.
Geri kalan adresler UI'ındır, çünkü core UI'ı da aynı adresten sunar (kullanıcı, 5 Kasım). Bu
belgede `/api` öneki yazılmaz.

Bir projenin içindeki her şeyin adresi o projenin altındadır; `{p}` projenin kimliğidir:
`/projects/{p}/frames/{id}` o projenin bir karesini gösterir. Her istek tek bir projeye dokunur,
adresin kendisi bunu söyler (kullanıcı, 4 Kasım — "aynı anda tek proje değiştirmesi mantıklı
gibi"). Projenin dışında yalnız `GET /api`, `GET /health`, modeller ve proje listesi vardır.
Bütün projelerde aramak v1'de yoktur; agent projeleri tek tek arar.

Listeleyen her endpoint aynı biçimde aranabilir; sorgunun yazışı PostgREST'inkidir (ör.
`?status=eq.waiting&order=created.desc`, 6. adım):

- bir alana göre süzmek (ör. yalnız videosu olanlar)
- adda ya da metinde regex ile aramak
- tarih aralığı
- sıralama
- sayfa sayfa almak
- yalnız istenen alanları almak (agent gereksiz veriyle uğraşmasın diye)

## Discovery

- **`GET /api`**
  - Ortak kurallar bir kez; sonra bölüm bölüm (Projects, Frames, Jobs…) bölümün iki üç cümlelik
    tanımı ve endpoint'leri, her biri tek satır.
  - Bir adresin ayrıntısı `GET /api?path=/projects/{p}/frames` ile alınır: o adresteki her fiilin
    aldığı alanlar, döndürdüğü ve kendine özgü hataları. Modelin alanları `GET /models/{id}`'dedir,
    burada tekrar yazılmaz.
  - Agent işe buradan başlar; ayrıntıya yalnız kullanacağı endpoint için bakar. Endpoint sayısı
    arttıkça ilk okuma yalnız birkaç satır büyür (kullanıcı, 5 Kasım — "token olarak efficient
    olsun, model tool listesi ve ne yaptığını bilsin, gerekince detaylı olarak o endpoint'e baksın";
    "endpoint miktarı scale oldukça patlamayalım diye").

- **`GET /health`**
  - Core'un ayakta olduğunu ve kim olduğunu söyler: uygulama, core'un kimliği, sürümü.
  - Küçüktür; adaptör ve notebook core'a ulaşabildiklerini buradan anlar. Drive'a gitmez; Drive
    yavaşken ya da erişilemezken de hemen cevap verir.

## Models

Seçilebilecek her şey modelin kendisindedir; agent bir iş istemeden önce neyi seçebileceğini
buradan öğrenir. Modeller projeye değil Colab'a kurulur; her Colab kendi diskine indirir (10. adım).
Model listesi uzayabilir; ortak liste kurallarıyla süzülür ve sayfa sayfa alınır (kullanıcı, 5
Kasım — "model listesi çok uzayabilir").

- **`GET /models`**
  - İndirilebilecek bütün ana modeller: her birinin ne olduğu, fotoğraf mı video mu, boyutu, hangi
    ekran kartlarında çalıştığı ve bu Colab'da kurulu, iniyor (yüzdesiyle), inemedi (hatasıyla) ya da
    kurulu değil olduğu.
  - Ör. yalnız video modelleri, yalnız kurulu olanlar, yalnız bu Colab'ın kartında çalışanlar.

- **`GET /models/{id}`**
  - Bir modelin her şeyi:
    - desteklediği yöntemler (bugün fotoğrafta t2i, videoda i2v) ve aldığı parametreler (ör. Krea
      negatif prompt almaz)
    - sunduğu LoRA seçimleri (bir seçim, güçleri sabit bir ya da birkaç LoRA dosyasıdır; her
      modelde "LoRA yok" da bir seçimdir)
    - yönler (yatay, dikey), video uzunlukları, en çok kaç varyant istenebileceği

- **`POST /models/{id}/download`**
  - Ana modeli, LoRA'ları ve yardımcı dosyalarıyla birlikte bu Colab'ın diskine indirmeye başlar;
    önceden de istenebilir. Model bu Colab'ın kartında çalışmıyorsa reddedilir. Modeli kurulu
    olmayan ve inmeyen bir iş verilemez.

- **`GET /models/{id}/wait`**
  - İndirme bitene kadar bekler, en çok 90 sn; sonra modelin durumunu döndürür.

## Projects

- **`GET /projects`**
  - Projelerin listesi, bütün Colab'larınkiler. Başka bir Colab'da oluşturulan, değişen ya da
    silinen proje birkaç saniye içinde görünür.
  - Örnek: adında "gece" geçenler, son bir haftada değişenler, arşivdekiler.

- **`GET /projects/{id}`**
  - Bir projenin bilgileri.

- **`POST /projects`**
  - Yeni bir proje oluşturur; adı verilir.
  - Ad kurala uymuyorsa neden olmadığını söyler. Aynı adla başka bir proje varsa yine oluşturur ve
    cevapta o projeyi söyler.

- **`PATCH /projects/{id}`**
  - Bir projede şunları değiştirir: adını, arşivde olup olmadığını.

- **`DELETE /projects/{id}`**
  - Projeyi siler: projenin bütün dosyaları, history'si dahil, Drive'ın çöpüne gider; silinmiş
    projeden hiçbir şey okunmaz (kullanıcı, 5 Kasım — "komple silinsin, history'si okunamasın").
  - Yalnız UI'dan, bir onayla; agent proje silmez (9. adım, 8. adım).
  - Projenin üretimi sürüyorsa önce durdurulur.

## Frames

Kareler projenin içeriğidir: üretilen fotoğraflar ve videolar. Bir kare bir fotoğraf ve istenirse
o fotoğraftan yapılan bir videodur. Promptları, modeli ve durumu onunla birlikte durur.

Karenin fotoğrafı değişmez. Videosu silinebilir: kare fotoğrafıyla, aynı kimlikle ve aynı yerde
kalır; ona yeniden video üretilebilir. Beğenilmeyen fotoğrafın karesi silinir, yenisi üretilir.

Kareler bir sıradadır: hikâyenin akışı, üretildikleri sıra. Film bu sırayla değil, **Edits**
altında kurulur. Kareler burada yönetilir; üretmek **Jobs** altındadır.

- **`GET /projects/{p}/frames`**
  - Projenin kareleri.
  - Örnekler:
    - bütün kareler, sırasıyla baştan sona
    - promptunda "yağmur" geçen kareler
    - videosu olmayan kareler

- **`GET /projects/{p}/frames/{id}`**
  - Bir karenin bilgileri: promptları, negatifi, modeli, seed'i, durumu.
  - Fotoğrafın ve videonun kendisi gelmez; yalnız var olup olmadıkları ve bilgileri (ne zaman
    üretildi, video kaç saniye). Dosyaların kendisi **Media** altındaki endpoint'lerle alınır.

- **`PATCH /projects/{p}/frames/{id}`**
  - Karenin sıradaki yerini değiştirir (ör. 5. kareyi 2.'nin arkasına almak).
  - Karenin kendisi değişmez.

- **`PATCH /projects/{p}/frames`**
  - Projenin bütün sırasını tek seferde yeniden verir.

- **`DELETE /projects/{p}/frames/{id}`**
  - Bir kareyi bütünüyle siler: fotoğrafı ve videosuyla.
  - Kare için kuyrukta bir iş ya da onu kullanan süren bir export varsa silinmez; hata neyin
    kullandığını ve önce ne yapılacağını söyler.
  - Kare kuyruktaysa hata işin kimliğini söyler ve işi kuyruktan çıkarmanın yeteceğini, fotoğrafı
    henüz gelmemiş karenin de silineceğini söyler.

- **`DELETE /projects/{p}/frames/{id}/video`**
  - Karenin videosunu siler. Kare fotoğrafıyla, aynı kimlikle, sırada ve edit'lerde aynı yerde
    kalır; ona yeniden video üretilebilir.
  - Kare için kuyrukta bir iş ya da onu kullanan süren bir export varsa yapılmaz.

- **`DELETE /projects/{p}/frames`**
  - Birden çok kareyi birden siler.

## Media

Bir karenin dosyaları.

- **`GET /projects/{p}/frames/{id}/photo`**
  - Karenin fotoğrafı.
  - Küçük boyutta istenebilir; agent bir resme bakarken tam boyutuna ihtiyaç duymaz.

- **`GET /projects/{p}/frames/{id}/video`**
  - Karenin videosu.

- **`GET /projects/{p}/frames/{id}/video/stills/{n}`**
  - Videonun `n`. saniyesindeki kare, tek bir resim; `n` tam sayıdır, aralığı core seçer (kullanıcı,
    5 Kasım — "genel bakış için 1 saniye arayı biz yapalım"). 5 sn'lik videoya bakmak `0`…`5` için
    tek listede altı çağrıdır.
  - Agent videoyu izleyemez; bu görüntülerle içinde ne olduğuna bakar. Belli bir ana bakmak v1'de
    yoktur (bkz. Sonraya kalanlar).


## Edits

Edit, karelerden kurulan bir filmdir. Projenin karelerinden istediklerini alır ve kendi sırasıyla
dizer; karelerin sırası onu bağlamaz. Bir projede birçok edit olabilir: aynı karelerden kısa bir
versiyon, uzun bir versiyon, farklı sıralı bir versiyon.

Edit'teki her yer bir kareyi gösterir; kareyi ve dosyalarını kopyalamaz. Aynı kare bir edit'te
birden çok yerde, birçok edit'te aynı anda olabilir.

- **`GET /projects/{p}/edits`**
  - Projenin edit'leri.

- **`GET /projects/{p}/edits/{id}`**
  - Bir edit: adı ve yerleri sırasıyla. Her yer için hangi kareyi gösterdiği ve sesinin kapalı olup
    olmadığı.
  - Gösterdiği kare silinmiş bir yerde "silindi" yazar.

- **`POST /projects/{p}/edits`**
  - Projede yeni bir edit oluşturur; adı verilir.
  - İstenirse yerleri de baştan verilir. Örnek: projenin bütün kareleri, karelerin sırasıyla.

- **`PATCH /projects/{p}/edits/{id}`**
  - Bir edit'te şunları değiştirir:
    - adını
    - yerlerini: kare eklemek, bir yeri çıkarmak, bir yeri taşımak ya da bütün sırayı baştan vermek
    - bir yerin sesinin kapalı olup olmadığını: sesi kapalı yer export'ta sessiz çıkar
  - Kopyalamak da buradadır: aynı kareyi edit'e bir kez daha koymak. Dosya çoğalmaz. Örnek: aynı
    video filmin hem başında hem sonunda; birinde sesli, ötekinde sessiz.
  - Örnek: silinmiş bir yere yeni üretilen kareyi koymak.

- **`DELETE /projects/{p}/edits/{id}`**
  - Edit'i siler. Kareler kalır.

## Jobs

Fotoğraf ve video üretmek bir iştir. İşler kuyruğa girer ve sırayla yapılır. Başladıktan sonra
her iş aynıdır: aşağıdaki listeleme, bekleme ve kuyruktan çıkarma hepsi için ortaktır.

Her üretim yöntemi kendi endpoint'idir (kullanıcı, 3 Kasım — "Çünkü ileride referanstan video
üretecek olsak o zaman patlarız. Böyle olursa bence daha tutarlı ve özgür oluruz."):

- **Yöntem endpoint'i belirler.** Yeni bir yöntem (ör. referanstan fotoğraf ya da video) yeni bir
  endpoint olarak eklenir; var olanlar değişmez.
- **Model bir parametredir.** Aynı yöntemi yapan modeller (ör. Nova, DaSiWa, Krea) aynı
  endpoint'ten çağrılır; yeni bir model yeni bir endpoint değildir.
- **Modelin ne alıp almadığını model söyler.** Hangi modelin hangi yöntemi desteklediğini ve
  hangi parametreleri aldığını `GET /models/{id}` verir. Bir model almadığı bir şeyi alırsa (ör. Krea'ya
  negatif) core onu sessizce atmaz, hata verir.

Bütün üretim endpoint'lerinde:

- Core agent'ın yerine karar vermez: gerekli bir şey eksikse ne eksik olduğunu söyler. Yalnız seed
  verilmemişse rastgele seçilir.
- İhtiyaç duyulan şey yoksa iş oluşturulmaz; hata neyin olmadığını söyler (ör. "bu kare yok").
- Aynı istek iki kez gelirse iş iki kez yapılmaz.

- **`POST /projects/{p}/jobs/photo/t2i`** — yazıdan fotoğraf
  - Fotoğraf üretir; her fotoğraf için yeni bir kare, iş verildiği an sıraya girer; fotoğrafı
    gelene kadar "üretiliyor" görünür.
  - Agent şunları verir: prompt, negatif, model, LoRA seçimi, yön, kaç varyant, seed.
  - Seed tektir, isteğe bağlıdır; verilmezse rastgele seçilir. Varyantların seed'i ondan türetilir:
    seed, seed+1, seed+2… (kullanıcı, 5 Kasım).
  - Sahne (zorunlu): bu karede ne olduğunun kısa açıklaması.
  - Yeni karelerin sırada nereye gireceğini de söyleyebilir.

- **`POST /projects/{p}/jobs/video/i2v`** — fotoğraftan video
  - Bir karenin fotoğrafıyla başlayan video yapar.
  - Agent şunları verir: başladığı kare, model, prompt, uzunluk, seed, mutlu son (açık ya da kapalı).
    Model zorunludur, `t2i`'deki gibi (kullanıcı, 5 Kasım — "ileride yeni modeller gelebilir, bu
    nedenle zorunlu olsun").
  - Video nereye düşer:
    - karenin videosu yoksa ve onu hedefleyen başka iş yoksa o kareye
    - değilse yeni bir kareye: yeni kare aynı fotoğrafı kullanır (dosya çoğalmaz) ve sırada
      eskisinin hemen arkasına girer
  - Örnek: aynı fotoğraftan başka bir promptla ikinci bir video denemek.

Video yeni bir kareye düştüyse bunu agent tahmin etmez: isteğin yanıtı ve `GET /projects/{p}/jobs/{id}`
videonun hangi kareye düşeceğini söyler.

- **`GET /projects/{p}/jobs`**
  - Projenin bütün işlerinin kaydı, bitenler dahil.
  - Örnek: bekleyen videolar.

- **`GET /projects/{p}/jobs/{id}`**
  - Bir iş: ne olduğu ve durumu (bekliyor, çalışıyor, bitti, iptal). İş başarısız olmaz: hata
    verirse kuyruk durur, iş sıranın başında bekler (2. adım).
  - Kuyruk kendiliğinden durduysa nedeni; ürettiği şeyin hangi kareye düştüğü (bitmeden önce de, düşeceği kare).

- **`GET /projects/{p}/jobs/{id}/wait`**
  - İş bitene kadar bekler, en çok verilen süre kadar; sonra işin durumunu döndürür.
  - Agent işin bitip bitmediğini sürekli sormak zorunda kalmaz.
  - Kuyruk durmuşsa, onu hiçbir Colab çalıştırmıyorsa ya da onu çalıştıran öbür Colab kapanmış
    olabilirse iş kendiliğinden ilerlemez; bekleme hemen döner ve nedenini söyler. Agent boşuna
    beklemez.

- **`DELETE /projects/{p}/jobs/{id}`**
  - Bekleyen ya da çalışan bir işi kuyruktan çıkarır; çalışan iş durur. Kuyruğu başka bir Colab
    çalıştırıyorsa iş orada en geç 30 saniye içinde durur.
  - İş için açılmış yeni kare, ürünü gelmeden işi çıkarılınca silinir; cevap bunu söyler.

- **`DELETE /projects/{p}/jobs`**
  - Seçilen işleri birden kuyruktan çıkarır; çalışan varsa durur.
  - Örnek: projenin bütün bekleyen işleri.

## Queue

Her projenin bir kuyruğu vardır: bekleyen işlerinin sırası. Kuyruğu bir anda tek bir Colab
çalıştırır; bir Colab da bir anda tek projenin kuyruğunu çalıştırır, queen-editor'daki gibi.
Sırayı tamamen agent belirler.

- **`GET /projects/{p}/queue`**
  - Yalnız henüz yapılmamış işlerin sırası: durdurulmuş mu, kendiliğinden durduysa nedeni (dört
    alanlı hatasıyla: işin hatası, ComfyUI, model inemedi, Drive'da yer yok, ürün Drive'a
    yüklenemedi), onu hangi Colab'ın çalıştırdığı (bu
    ya da başka bir Colab), şu an hangi iş üretiliyor, bekleyen işlerin kimlikleri sırasıyla.
  - Kuyruk kendiliğinden durmuşken projeye iş verilirse iş kabul edilir; cevap kuyruğun neden
    durduğunu da söyler.
  - İşlerin bilgisi burada değil, `GET /projects/{p}/jobs`'tadır. Biten iş kuyruktan çıkar; kaydı `GET /projects/{p}/jobs`'ta
    kalır.

- **`GET /projects/{p}/queue/wait`**
  - Kuyruk boşalana ya da durana kadar bekler, en çok verilen süre kadar.

- **`PATCH /projects/{p}/queue`**
  - Sırayı işlerin kimlikleriyle değiştirir: bir işi istediği yere taşır ya da bütün sırayı baştan
    verir.

- **`POST /projects/{p}/queue/pause`**
  - Üretimi hemen durdurur; kuyruğu başka bir Colab çalıştırıyorsa en geç 30 saniye içinde. İşler
    kuyrukta kalır; o an üretilen iş kesilir ve sıranın başına döner.

- **`POST /projects/{p}/queue/resume`**
  - Kuyruğu bu Colab'da, kaldığı yerden çalıştırır.
  - Bu Colab başka bir projenin kuyruğunu çalıştırıyorsa o durur ve yerinde bekler.
  - Başka bir Colab bu kuyruğu çalıştırıyorsa kuyruk buraya geçer; o an üretilen iş de geçer:
    sıranın başına döner ve burada baştan üretilir, öbür Colab onu en geç 30 saniye içinde keser.
    Kapanmış bir Colab'ın kuyruğu da böyle kaldığı yerden sürer.

- **`DELETE /projects/{p}/queue`**
  - Kuyruğu boşaltır: bekleyen bütün işler iptal olur.
  - Çalışan iş ve ürünü gelmiş kareler kalır; iş için açılmış, ürünü gelmemiş kareler gider.

Bir projeye iş verilince: o projenin kuyruğu bu Colab'da çalışıyorsa iş sıraya girer. Bu Colab
hiçbir kuyruğu çalıştırmıyorsa ve bu projenin kuyruğunu başka bir Colab çalıştırmıyorsa, bu
projenin kuyruğunu çalıştırmaya başlar. Bu Colab başka bir
projenin kuyruğunu çalıştırıyorsa iş bekler; o kuyruk kesilmez, geçmek için `resume` denir. Kuyruk
boşalınca Colab onu bırakır ve boşta kalır.

## Exports

Export, bir edit'i dışarıya verilecek dosyalara çevirir. Edit'in sırasını kullanır, karelerin
sırasını değil. GPU kullanmaz; bu yüzden kuyruğa girmez ve üretimle aynı anda çalışabilir.

- **`POST /projects/{p}/exports`**
  - Bir edit'in export'unu başlatır: tek bir birleşik video.
  - `name` isteğe bağlı; verilmezse `<proje> - <edit>`, 2. adımdaki gibi kısaltılmış.
  - Cevap export'u döner: kimliği, adın son hali (`(1)` dahil), klasörünün adı ve Drive bağlantısı.
    `GET /projects/{p}/exports` ve `GET /projects/{p}/exports/{id}` de bunları döner.
  - Önce yalnız ne çıkacağını gösterebilir: kaç video, toplam kaç saniye, sesi kapalı yerler,
    videosu olmayan kareler.
  - Edit boşsa, ya da edit'te silinmiş bir yer ya da videosu olmayan bir kare varsa export başlamaz;
    hata o yerleri söyler.
  - Bu Colab'da başka bir export sürüyorsa başlamaz; hata onun kimliğini söyler.

- **`GET /projects/{p}/exports`**
  - Projenin export'ları.

- **`GET /projects/{p}/exports/{id}`**
  - Bir export ve durumu.

- **`GET /projects/{p}/exports/{id}/wait`**
  - Export bitene kadar bekler, en çok verilen süre kadar.
  - Export'u başka bir Colab yapıyorsa hemen döner ve bunu söyler; o Colab kapandıysa export
    `DELETE /projects/{p}/exports/{id}` ile iptal edilebilir.

- **`DELETE /projects/{p}/exports/{id}`**
  - Süren bir export'u iptal eder; başka bir Colab'ınkini de. Birleşik videosu tam yüklenmişse
    iptal edilmez, export "bitti" olur.

- **`GET /projects/{p}/exports/{id}/files`**
  - Export'un çıkardığı dosyalar.

## History

Yapılan her değişiklik, olduğu sırayla kaydedilir. Agent ne yaptığını, kullanıcı da agent'ın ne
yaptığını buradan görür.

- **`GET /projects/{p}/history`**
  - Projenin değişikliklerinin kaydı. Her kayıtta:
    - ne zaman yapıldığı
    - ne yapıldığı (kare silme, sıra değiştirme, edit değiştirme, iş verme…)
    - neye yapıldığı (proje, kare, edit, iş ya da kuyruk)
    - hangi Colab'da yapıldığı
    - öncesi ve sonrası (ör. edit'in eski ve yeni sırası)
  - Örnekler: bu projede bugün silinenler; bir edit'in sırasının nasıl değiştiği.
  - Yalnız değişiklikler kaydedilir, okumalar kaydedilmez.
  - Yalnız okunur: kayıt değiştirilemez, silinemez.

## Not in the core

- Video promptunu kendiliğinden yazan özellik: yok; promptu agent yazar.
- Fotoğrafı promptuyla karşılaştıran Queen AI kontrolü: yok; karşılaştırmayı agent yapar.
- Referans havuzu ve referans videosu: şimdilik yok.
- Yazıdan video (`t2v`) ve ilk-son fotoğraftan video (`fl2v`): şimdilik yok; gelince kendi
  endpoint'leriyle eklenir.
- Geri alma: şimdilik yok; ileride **History**'deki kaydın üstüne kurulacak.
- Uygulamanın içindeki agent ve sohbetleri: agent artık dışarıda.
- Fotoğraf ve referans panellerinin hatırladığı kutular: UI'ın kendi taslağı.
- Ad yazarken kontrol: `POST /projects` zaten söyler.
- queen-editor'ın projelerini açmak: şimdilik yok.
- Bütün projelerde aramak: v1'de yok; agent projeleri tek tek arar (bkz. Sonraya kalanlar).
