# Madde 518 · Açık sayfa dışarıdan eklenen işi görür — tasarım

**Tarih:** 30 Ekim 2026 · **Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-17),
518 · v11-17 (yama v11.1) · **Dal:** `feat/queen-editor-v11.1` · **Plan:**
[2026-10-30-queen-editor-m518-acik-sayfa-isi-gorur-plan.md](../plans/2026-10-30-queen-editor-m518-acik-sayfa-isi-gorur-plan.md)
· **Kurallar:** queen-editor [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kabul koşulu (maddeden)

Sıra boşken açık duran bir kare ya da proje sayfası, ajanın ya da başka bir sekmenin eklediği işi
yenilemeden gösteriyor.

Kullanıcı — *"bu hatalarıda çöz istersen"*. Madde BACKLOG'un *"Açık ve boştaki bir sayfa dışarıdan eklenen
işi görmüyor"* işi (516'nın QA'sı). Kullanıcı 27 Ekim'de olayla çalışan bir yol istemişti, tekrar tekrar
sormak değil (*"event driven … long polling"*); 509'un tutulan isteği bu yüzden var.

## Bugün

- **Sayfa yalnız sıra çalışırken yokluyor.** `useGeneration`'ın `poll`'u açılışta bir kez `/api/status` ve
  galeriyi soruyor, 2 sn'lik zinciri yalnız durum `running` ise yeniden kuruyor. Sıra boşken açılan proje,
  kare ya da export sayfası bir daha sormuyor. Ajanın düzeltmesi (`fix_photo`), başka bir sekmenin Kuyruğa
  ekle'si ya da Yeniden üret'i sırayı sunucuda başlatıyor; bu sayfa yenilenene kadar hiçbirini görmüyor.
  Kendi ajan paneli 481'den beri `follow` ile haber veriyor, ama yalnız aynı ekrandan.
- **Kaçan olay yalnız sıranın başlaması.** İş eklemenin her yolu `PhotoRunner.start`'a varıyor: boştaki
  işçiyi alıyor (claim), süren koşuya katılıyor (join, 511) ya da başka bir projenin koşusu işçiyi
  tutuyorsa reddediliyor. Son ikisi yalnız bir koşu sürerken olur, ve o sırada açık her sayfa zaten
  yokluyor — başka bir projenin koşusu da zinciri sürdürüyor. Görünmeyen tek an, sıranın çalışmazken
  çalışmaya geçmesi.
- **Sekmede zaten bir tutulan istek var** (509): `App`'te tek dinleyici, `GET /api/queue/ended?after=E`,
  yalnız sıranın bitişlerini sayıyor (`EndedWatch`).
- **`/api/status`'un `pending`'i** (517'nin QA'sı, ana ajan, 30 Ekim — "drop the field"): döngü her turun
  başında sıranın borçlu işlerini dosya adlarıyla yazıyor. Kuyruktan çıkarılan bir iş, o turun render'ı
  bitene kadar — bir video için dakikalarca — listede kalıyor; 517'nin QA'sının gördüğü buydu. Ama listeyi
  ne ekran ne ajan okuyor: ekran borcu galeriden sayıyor (`owed`).

## Ne yapılır

**Sıranın başlaması da sekmeye bitişi gibi ulaşır, ve sayfa normal yoklamasına başlar.** Yeni bir yoklama
yok: 509'un tek tutulan isteği iki olayı da taşır.

### Sunucu

**Adlar ne olduklarını söyler** (ana ajan, 30 Ekim — seçenek 1; 509'un ad değişikliğiyle aynı gerekçe).
`git mv` ile:

| 509'daki ad | 518'deki ad |
|---|---|
| `backend/features/queue_ended/` | `backend/features/queue_watch/` |
| `EndedWatch` | `QueueWatch` |
| `make_ended_blueprint`, `GET /api/queue/ended?after=E` | `make_watch_blueprint`, `GET /api/queue/watch?started=S&ended=E` |
| `test_ended_watch.py`, `test_ended_routes.py` | `test_queue_watch.py`, `test_queue_watch_routes.py` |
| `main._ended`, `_ended_bp` | `main._queue_watch`, `_queue_watch_bp` |

- **`QueueWatch`** iki sayaç tutar: `started()` sıranın kaç kez başladığını, `ended(state)` bugünkü gibi
  kaç kez bittiğini ve son bitişi. Tutulan istek, sorulan iki sayı da durduğu gibiyken bekler; biri
  değişince ya da süre (50 sn) dolunca `{started, ended, last}` ile cevaplar. İki sayı birlikte gelmezse
  hemen, durduğu gibi cevaplanır (açılış). Bellekte: yeniden başlayan sunucu ikisini de 0'dan sayar.
- **`PhotoRunner`** işçiyi alan basışta, almanın ardından, işi başlatmadan önce ve kilidin dışında
  `started()` der. Kilidin dışında, çünkü `ended` de öyle söyleniyor ve duyan `/api/status`'u sorduğunda
  `running` okur. Katılma ve reddedilen basış bir şey demez: biri süren koşuya katılır, öteki başka bir
  projenin koşusuna çarpar; ikisinde de açık sayfalar zaten yokluyor.
- **`pending` alanı gider.** Döngünün iki raporu artık onu yazmaz; okuyan yok, ve tek söylediği sıranın
  bir tur önceki hâliydi. Galerinin borcu (`owed`) değişmez.

### Ekran

- **`shared/queue_watch.js`** — tutulan istek `useEndedNotification`'dan buraya taşınır: `useQueueWatch()`
  `App`'te bir kez kurulur, ekranlar arasında kopmaz; `onQueueMoved(listener)` dinleyiciyi ekler ve
  çıkaranı döner. Açılış sayaçsız bir sorudur, hemen cevaplanır ve kimseye söylenmez. Sonraki her cevapta
  iki sayıdan **biri** son duyulandan farklıysa her dinleyiciye `(said, before)` söylenir; aynıysa (süre
  doldu) söylenmez. Ulaşmayan bir sorudan sonra 10 sn beklenir, bugünkü gibi.
- **Neden "biri farklıysa", "başlama arttıysa" değil:** yeniden başlayan bir sunucu sayaçları 0'dan sayar.
  Sekme `started: 1` duymuşken sunucu yeniden başlar ve sıra bir kez başlarsa yeni sayı yine 1'dir;
  yalnız başlamaya bakan bir gözcü o cevabı hiç vermezdi. Bitiş sayısı (0) farklı olduğu için cevap gelir;
  ne yapılacağına her dinleyici kendi karar verir.
- **`useEndedNotification`** dinleyici olur: `ended` arttıysa bugünkü cümleyle çalar. Azaldıysa (sunucu
  yeniden başladı) çalmaz, bugünkü gibi.
- **`useGeneration`** dinleyici olur: başlama sayısı değişince bugünkü `poll()`'unu çağırır — galeri ve
  `/api/status`. Durum `running` ise bugünkü 2 sn'lik zincir oradan sürer; bitiş görülünce bugünkü gibi bir
  kez daha galeri okunur ve zincir durur. İki istek arasında başlayıp biten bir koşu da başlama sayısını
  değiştirir. **Yalnız bitiş yoklatmaz** (reviewer): koşuyu izleyen zincir bitişi kendisi gördü, ve her
  bitişte açık her sayfaya bir galeri okuması yaptırmak boşa olurdu. **Küçülen bitiş sayısı yoklatır:** o,
  yeniden başlayan bir sunucu; ardından gelen başlama, sekmenin önceden duyduğu başlama sayısını geri
  getirebilir (yukarıdaki örnek). Proje, kare ve export sayfası üçü de bu hook'u kullandığı için üçü de
  görür. Proje listesi galeriyi okumadığı için yalnız bildirimi duyar.
- **`api.js`:** `waitForEnded(after)` → `waitForQueue(seen)`, `ENDED_ASK_TIMEOUT_MS` →
  `QUEUE_ASK_TIMEOUT_MS` (80 sn, bugünkü gibi).

## Maliyet

- **Boştaki bir sekme, saatte:** bu madde hiçbir şey eklemez. 509'un tutulan isteği bugünkü gibi en çok 50
  sn'de bir döner: sekme başına saatte ~72 istek, her biri sunucunun belleğinden cevaplanır; Drive'a da
  ComfyUI'ye de gidilmez. Bir sekme hangi ekranda olursa olsun tek istek tutar.
- **Sıra bir kez başlayınca:** açık her proje, kare ya da export sekmesi bir `/api/status` (bellek) ve bir
  galeri okuması yapar — sıra çalışırken her 2 sn'de yapılan okumanın aynısı. Sonrası bugünkü yoklama.
  Sıranın bitişi haberden bir istek getirmez; zincirin son okuması bugünkü gibi. Proje listesindeki sekme
  hiç sormaz.
- **Sunucuda:** bir başlama ve bir bitiş birer sayaç artışı ve bekleyen isteklerin uyandırılması; disk yok.
- **`pending`'in gidişi:** her turun raporundan bir liste eksilir; ağ ve disk değişmez.

## Ne kaybolabilir, ne bozulabilir

Hiçbir şey yazılmıyor; sayaçlar bellekte, kayıpları bir sayfanın bir olayı geç duyması.

- **Başlama, sekme iki istek arasındayken:** sonraki istek eski sayılarla sorar ve hemen cevaplanır.
  Olay geç duyulur, kaybolmaz.
- **İki istek arasında birden çok başlama ve bitiş:** tek bir cevap olarak duyulur; sayfa bir kez yoklar ve
  durumu olduğu gibi okur. Bildirim bugünkü gibi son bitişi söyler.
- **Başlama sayfanın ilk yoklamasından önce:** sayfa açılışta zaten soruyor; koşu sürüyorsa `running`
  görür. Koşu çabuk bittiyse (ör. kurulu olmayan üretici) galeri yine okunur.
- **Sunucu yeniden başladı:** sayaçlar 0'dan; sekme küçülen bir bitiş sayısı duyar, bir kez yoklar,
  çalmaz. Colab'da her başlatış yeni bir Quick Tunnel açtığı için eski sekme yeni sunucuya hiç ulaşmaz.
- **Haber gelince sayfa zaten yokluyor:** `poll` önce zamanlayıcıyı temizler, iki zincir aynı anda işlemez.
- **Sayfa söküldü:** dinleyici efektin temizliğinde çıkar; söylenen haber ona varmaz.
- **`pending`:** onu okuyan bir ekran ya da ajan yok; aynı adı taşıyan galeri durumu (`status: "pending"`)
  ayrı bir şey ve değişmez.

## Sınırlar

- Sırayı başlatmayan bir değişiklik — başka bir sekmenin silmesi, Kuyruktan çıkar'ı, kopyalaması — sıra
  boşken açık sayfaya bugünkü gibi ulaşmaz; madde dışarıdan eklenen işi istiyor. İş eklemenin her yolu
  sırayı başlatır ya da süren koşuya katılır, biri dışında: başka bir projenin koşusu işçiyi tutarken
  yapılan basış, plan satırı yazıldıktan sonra meşgul diye reddedilir. O iş de görünür, çünkü o koşu
  sürerken açık her sayfa yokluyor ve koşunun bitişini kendi zinciri görüp galeriyi bir kez daha okuyor.
- Sekme kapalıyken kimse dinlemez; açılan sayfa açılışta zaten sorar.

## Ne zaman bitti

- **Boştaki sayfa dışarıdan başlayan sırayı görür** (bugün kırmızı): sıra boşken açılan sayfa, tutulan
  istek bir başlama getirince galeriyi ve durumu yeniden sorar, yeni işi gösterir ve 2 sn'lik yoklamaya
  geçer; uygulama düzeyinde de, açık bir proje sayfası başka yerden eklenen kareyi yenilemeden gösterir.
- **Sunucunun yeniden başlaması ve ardından gelen başlama kaçmaz** (bugün kırmızı): `started` aynı, `ended`
  küçük bir cevap dinleyicilere söylenir ve sayfa yoklar.
- **Yalnız bitiş sayfaya yoklatmaz;** bildirimi bugünkü gibi çalar.
- **Süresi dolan, aynı sayılı cevap kimseye söylenmez;** açılışın cevabı da söylenmez.
- **Sunucu:** işçiyi alan basış `started()` der, ve işi başlamadan önce, `running` yazıldıktan sonra;
  katılma ve reddedilen basış demez. Tutulan istek bir başlamayı da hemen duyar. Kapı iki sayıyı birlikte
  okur; biri eksikse hemen cevaplar. Uygulama sıranın hiç başlamamış ve bitmemiş hâliyle kalkar.
- **`pending` yok:** döngünün hiçbir raporunda alan yok.
- Bildirimin bugünkü testleri (çalma, cümleler, yeniden başlayan sunucuda sessizlik) dinleyici olarak
  olduğu gibi geçer.
- `dist` yeniden derlendi; iki queen-editor takımı yeşil
  (`test_notebook_clones_its_branch.py`'nin iki testi kullanıcının Colab denemesi için kasten kırmızı).

## Aynı değişiklikte

BACKLOG'dan *"Açık ve boştaki bir sayfa dışarıdan eklenen işi görmüyor"* silinir.
