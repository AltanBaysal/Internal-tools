# Madde 516 · "Kuyruktan çıkar" yalnız sıradaki işi çıkarır — tasarım

**Tarih:** 29 Ekim 2026 · **Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-15),
516 · v11-15 (yama v11.1) · **Dal:** `feat/queen-editor-v11.1` · **Plan:**
[2026-10-29-queen-editor-m516-kuyruktan-cikar-yalniz-isi-plan.md](../plans/2026-10-29-queen-editor-m516-kuyruktan-cikar-yalniz-isi-plan.md)
· **Kurallar:** queen-editor [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kabul koşulu (maddeden)

Kare sayfasında sırada bekleyen bir katmanın (örneğin video) sekmesindeki "Kuyruktan çıkar", yalnız o
sıradaki işi çıkarıyor. Karenin bitmiş fotoğrafı ve öteki katmanları yerinde kalıyor, kare galeride
duruyor. Hiçbir bitmiş dosya sorulmadan silinmiyor.

Kullanıcı, 29 Ekim — *"Yamaya ekleyip düzeltelim: düğme yalnız sıradaki işi çıkarsın"*. 511–515'e
dokunulmaz. Ekrandaki sürüm V11 kalır.

## Bugün

- **Ekran** (`PhotoDetail`): bekleyen katmanın sekmesindeki (`openState === "pending"`) "Kuyruktan
  çıkar" `handleRemove`'u çağırıyor: `removePhotos([kare])` → `POST …/frames/delete` →
  `remove_frames`. Sormuyor.
- **Sunucu** (`remove_frames`): fotoğrafı inmiş karenin durumu `done`. Bu yüzden karenin dolu bütün
  hücrelerini kapatıyor, kimsenin tutmadığı dosyaları siliyor ve kareyi galeri sırasından çıkarıyor.
  Fotoğrafı inmiş, videosu sırada bir karede bu, bitmiş fotoğrafın sorulmadan silinmesi demek (514'ün
  QA'sının bulduğu).
- Fotoğraf sekmesindeki silme ise karenin kendi fotoğrafı varsa önce soruyor
  (`ownsItsPhoto ? setAsking("frame") : handleRemove`).

### Karar 38 ve neden bugün tutmuyor

Düğmenin kareyi silmesi bilinçli bir karardı: tasarım v4'ün farkları arasında 99. fark
([araştırma](../arsiv/research/2026-08-20-queen-editor-tasarim-v4-farklari.md)) düğmenin sekmede
durmasını ve karenin kendi katmanında *"Kuyruktan çıkar — kare kalır"* demesini istiyordu. Görev 22
([spec](../arsiv/specs/2026-08-21-queen-editor-v14-gorev-22-detay-hizalamasi-testler-design.md), karar
38) düğmeyi sekmeye taşıdı, ama "kare kalır"ı yazmadı: *"Kuyruk kareyi çıkarıyor, katmanı değil …
Bir katmanı kuyruktan alıp kareyi bırakan bir basış yok."* Yalnız `remove_frames`'e bakılmıştı.
`remove_layer` ise ilk yazıldığı günden beri (`4d84393c`, 12 Ağustos) katmanın sırada bekleyen kendi
işine `removed` yazıyor. Yani karar 38'in dayandığı eksik, karar alındığında da yoktu.

**Karar 38'den değişen:** "kuyruk kareyi çıkarır, katmanı değil" artık doğru değil. Bekleyen
katmanın sekmesi o katmanın işini çıkarır, kareyi değil. **Değişmeyen:** düğme sekmede kalır (99. fark),
basış sormaz (bitmiş hiçbir şey kaybolmaz), ve etiket "Kuyruktan çıkar" kalır. Tasarımın "— kare kalır"
eki geri gelmiyor: kullanıcının maddesi düğmeyi bu adla anıyor ve etiketi değiştirmiyor.

## Ne yapılır

### Sunucu — kendi kapısı

`POST /api/projects/<proje>/layers/<katman>/dequeue`, gövde `{"frames": [...]}`, cevap
`{"removed": [...]}`: gerçekten çıkarılan işler, her birinin kaydedileceği dosya adıyla.

- **Neden ayrı kapı, silme kapısının bir modu değil:** silme kapısı (`…/layers/<katman>/delete`,
  `remove_layer`) dolu hücreyi siler. Ona bir bayrak eklenseydi, bayrağın yokluğu silme demek olurdu.
  İleride bayrağı unutan bir çağıran, "Kuyruktan çıkar"ı sessizce sorulmayan bir silmeye geri çevirirdi:
  bu maddenin düzelttiği hatanın kendisi. Ayrı kapıda böyle bir yanlış okuma yok (reviewer'ın önerisi).
- **Neden silme kapısının bugünkü hali yetmiyor:** ekran sunucunun gerisinde kalabilir: geç bir
  yoklama, arka plandaki bir sekme (tarayıcı zamanlayıcıyı dakikada bire kadar yavaşlatır), ya da
  tünelin kopması. Ekran videoyu hâlâ "sırada" gösterirken basılan düğme, o arada inmiş bir videoyu
  `remove_layer` ile sorulmadan silerdi. Basış işi kastediyor; kapı da yalnız işi çıkarır.
- **`domain/usecases/dequeue_layer.py`**:
  - `dequeue_layer(record, store, plan_store, order_store, now, project, frames, kind)`: kare listesi
    `checked` ile denetlenir. Plan kilidinin (512) içinde galeri ve hücreler birer kez okunur. Her
    kimlik bir kez sayılır, galerinin bilmediği kimlik atlanır. `owed_on`'un verdiği işlere 513'ün
    `seen`'iyle `removed` yazılır. Hiçbir dosya silinmez, hiçbir dolu hücre kapanmaz, sıra dosyası
    yazılmaz.
  - `owed_on(frame, cells, kind)`: bir karenin `falls_with(kind)` içinde sıranın hâlâ borçlu olduğu ve
    hücresi dolu olmayan işleri, `(hücre, dosya adı, okunduğu durum)` olarak. Ses borçluysa o da gider,
    çünkü videoya asılı (`layers.NEEDS`).
  - **Kilit neden:** aynı anda gelen bir Kuyruğa ekle, işi hâlâ sırada görüp bir şey eklemezdi, ve
    güvendiği iş ardından çıkarılırdı: *"Eklendi denen hiçbir iş kaybolmuyor"* (512). Kilitte ikisi
    sıraya girer: önce çıkarılır, sonra Kuyruğa ekle işi yeniden sıraya koyar.
- **`remove_layer`**: davranışı değişmez. Kapanan katmanın üstünde borçlu kalan işleri artık aynı
  `owed_on` ile buluyor; tek kopya. Eski süzgeç (`(fid, slot) not in closing`) ile `owed_on`'unki
  (hücre dolu değil) aynı şeyi seçiyor, çünkü o karenin `closing`'i tam olarak `falls_with(kind)`
  içindeki dolu hücreler.
- **`routes.py`**: `DEQUEUEABLE = (video, audio)`. Fotoğraf yok, çünkü fotoğrafını bekleyen kare o işin
  kendisi ve `…/frames/delete`'ten çıkar. Başka bir katman için 404 *"Kuyruktan çıkarılabilir bir katman
  değil: <katman>"*. Bozuk kare listesi 400, olmayan proje 404, silme kapısındaki gibi.
- **`main.py`**: kapının bağlantısı.
- Silme kapısı, seçim çubuğunun "Videoları sil"i ve `remove_frames` 516'dan önceki gibi.

### Ekran

- **`api.dequeueLayer(project, frames, kind)`**: yeni kapıya istek. `api.removeLayer` değişmez.
- **`useGeneration.dequeueLayer(frames, kind)`**: `removeLayer` gibi; cevaptan sonra galeriyi bir kez
  okur, ret olursa sunucunun cümlesini `error`'a koyar. `removeLayer` değişmez.
- **`PhotoDetail`**:
  - Bekleyen sekmenin düğmesi `handleRemove` yerine `handleDequeue`'yu çağırır. Sormaz. Kare galeride
    kaldığı için sayfa karede kalır ve Foto sekmesine döner, katman silmenin yaptığı gibi.
  - `handleDequeue`, `handleRemoveLayer`'ın yanında durur. Reddin başlığı *"Video kuyruktan
    çıkarılamadı"*. `handleRemoveLayer` ve onay kutusu değişmez.
  - Sil düğmelerinin üstündeki karar-38 yorumu bugünkü kuralı söyler.

### Fotoğraf sekmesinin "Kuyruktan çıkar"ı — değişmez

Fotoğraf sekmesinde düğme "Kuyruktan çıkar" der, ama yalnız karenin fotoğrafı kendisinin değilken ve
kareye bir şey borçluyken (`!ownsItsPhoto && awaited`). Bu iki durumda olur:

- **Fotoğrafı sırada olan kare:** kare zaten bekleyen fotoğrafın kendisi; diskte hiçbir şeyi yok (video
  ancak fotoğrafı inmiş karede istenebilir). `remove_frames` borçlu işlere `removed` yazar ve kare
  galeriden çıkar. Doğru olan bu; hiçbir şey kaybolmaz.
- **Videosunu bekleyen kopya kare:** `remove_frames` kopya karede hiçbir hücre kapatmaz, yalnız video
  işine `removed` yazar. Yani bugün de yalnız sıradaki işi çıkarıyor, ve hiçbir dosya silinmiyor.
  Ama kare galeriden çıkmıyor: kaynağın fotoğrafını tuttuğu için bir sonraki okumada bitmiş bir ikiz
  olarak en üste geri geliyor. Bu bu maddeden eski; BACKLOG'a girdi, burada düzeltilmiyor.

Karenin kendi fotoğrafı varsa fotoğraf sekmesinin düğmesi "Sil"dir ve bugünkü gibi önce sorar.

## Maliyet

Proje, sohbet ve dosya sayısından bağımsız, bir istek. Plan kilidinin içinde:

| İş | Ne yapar |
|---|---|
| Kuyruktan çıkar (bekleyen sekme) | bir `POST …/dequeue`: galeri bir kez okunur (`list_frames`: projeye bakış, kayıt, plan, sözler, sıra) ve hücreler bir kez okunur (`FileCache`'le). Borçlu katman başına `photos.jsonl`'e bir satır eklenir; videosu sırada bir karede tek satır. Dosya silinmez, sıra dosyası yazılmaz. Cevaptan sonra hook galeriyi bir kez okur. |
| Eskisi (karşılaştırma için) | aynı okumalar, artı karenin her dolu hücresi için bir silme ve bir satır, artı sıra dosyasının bir yazması. |

## Ne kaybolabilir, ne bozulabilir

- Kapı hiçbir dosya silmez ve hiçbir dolu hücreyi kapatmaz. Yazdığı tek şey `removed` satırı, o da
  513'ün `seen`'iyle. En kötü durumda iş sıradan çıkmaz (aşağıda, Sınırlar).
- **Sıralamalar:**
  - Video galeri okunmadan önce indiyse: borçlu listesinde yok, hiçbir şey yazılmaz.
  - Galeri okunduktan sonra, hücreler okunmadan önce indiyse: hücre dolu, atlanır.
  - Hücreler okunduktan sonra indiyse: `removed` satırı `seen=None` taşır, video `done` yazınca o satır
    geçersiz kalır (513). Video yerinde kalır.
  - Aynı anda bir Kuyruğa ekle: plan kilidi ikisini sıraya koyar, eklenen iş kaybolmaz.
- Silme kapısı ve onun çağıranları değişmediği için, onların davranışı da değişmez.

## Sınırlar

- **Çizilmeye başlamış bir işe basış:** sıra işi ekranın son yoklamasından sonra çizmeye başladıysa,
  sayfa onu hâlâ "sırada" gösterir ve basış `removed` yazar. Çizim bitince yazılan `done` onu ezer
  (513: üretilen katmanın satırı `seen` taşımaz, her zaman geçerli), ve video, kullanıcı onu çıkardıktan
  sonra yine de gelir. Hiçbir şey kaybolmaz, hiçbir şeyin üstüne yazılmaz. Bugünkü `remove_frames`'in
  belgelediği davranışla aynı.
- Ses sekmesi: 514'ten beri ses kuyruğa eklenemiyor. Eski sırada kalmış bir ses işi varsa düğme aynı
  kapıdan yalnız onu çıkarır (`falls_with("audio")`).
- Sırada bekleyen videonun üstünde ses borçluysa ikisi birlikte çıkar, çünkü ses videoya asılı.
- Galerinin seçim çubuğunda katman başına bir "kuyruktan çıkar" yok; bu madde yalnız kare sayfasının
  düğmesini değiştirir.

## Ne zaman bitti

- **Use case (`dequeue_layer`):**
  - videosu sırada olan karede: `{"removed": ["0_a_V1_0.mp4"]}`, video `removed`, borç boş, kare `done`
    ve fotoğrafıyla galeride, hiçbir şey silinmedi;
  - ekranda sırada, sunucuda inmiş video: `{"removed": []}`, hiçbir şey silinmedi, video `done` kalır
    (önce kırmızı);
  - sıradaki videonun üstünde bekleyen ses de çıkar;
  - kopya karede: video `removed`, taşınan fotoğraf `done`, kaynak dokunulmamış;
  - bilinmeyen ve iki kez gelen kimlik bir kez sayılır; kimlik listesi olmayan gövde `InvalidFrames`.
- **Kilit:** çıkarmayla aynı anda gelen Kuyruğa ekle işi yeniden sıraya koyar (kilitsiz kırmızı).
- **Kapı:**
  - sıradaki videoyu çıkarır, fotoğraf diskte, kare galeride, borç boş;
  - sıraya alınmış ve inmiş videoya basış: 200 `{"removed": []}`, dosya diskte, galeride video;
  - `photo` için 404; bozuk kare listesi 400; olmayan proje 404.
- **`remove_layer`'ın bütün eski testleri** değişmeden geçer.
- **Ekran:**
  - fotoğrafı inmiş, videosu sırada karenin Video sekmesinde "Kuyruktan çıkar" →
    `dequeueLayer("düğün", ["P0_0"], "video")`; `removeLayer` ve `removeFrames` çağrılmaz, onay kutusu
    yok, sayfa karede kalır, Foto sekmesi açılır;
  - ret: *"Video kuyruktan çıkarılamadı"* ve sunucunun cümlesi;
  - kopya karenin Video sekmesinde kopyanın kimliğiyle;
  - `api.dequeueLayer` `…/layers/video/dequeue`'ya `{frames}` gönderir;
  - katman silmenin testleri 516'dan önceki gibi geçer.
- Fotoğraf sekmesinin bugünkü testleri (bekleyen fotoğraf karesi, kopya kare) olduğu gibi geçer.
- `dist` yeniden derlendi; iki queen-editor takımı yeşil.

## Aynı değişiklikte

BACKLOG'a üç iş, üçü de bu koşudan eski: birleşik export'ta sesin sonraki parçaya ~50 ms taşması (515'in
QA'sı), bekleyen kopya karenin sunucudan `pending` gelmesi yüzünden ekranda "bekliyor" görünmesi, ve
bekleyen kopya karenin `remove_frames`'ten sonra ikiz olarak geri gelmesi.
