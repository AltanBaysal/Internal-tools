# Madde 512 · Aynı anda basılan iki Kuyruğa ekle'nin ikisi de sırada kalır — tasarım

**Tarih:** 29 Ekim 2026 · **Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-11),
512 · v11-11 (yama v11.1) · **Dal:** `feat/queen-editor-v11.1` · **Kurallar:** queen-editor
[FOUNDATION](../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kabul koşulu (maddeden)

- Aynı projeye aynı anda iki iş eklenince — çift tıklamada ya da kullanıcı ve ajan birlikte eklerken —
  ikisi de sıraya giriyor ve ikisi de üretiliyor.
- "Eklendi" denen hiçbir iş kaybolmuyor; bir iş eklenemezse ekran bunu sistemin kendi sözüyle söylüyor.

Ekrandaki sürüm V11 kalır; ekran değişmez.

## Hata, görüldüğü gibi

Plan dosyasını (`plan.json`) yazan tek yer `DrivePlanStore.append`: dosyayı okur, yeni satırları
sonuna ekler, bütün dosyayı geçici dosya ve `os.replace` ile yeniden yazar. Kilit yok. Kuyruğa yeni iş
koyan her kapı da işlerine ad (numara ve varyant) **okuduğundan** verir: `start_batch` ve
`queue_references` `next_number` ile (disk, plan, kayıt), `regenerate` ve `fix_photo` `next_number` ya
da `next_id` ile, `queue_layer` kopya kareleri `next_id` ile, `copy_frames` ikizleri `next_copy_id` ile
(plan ve kayıt, `known_ids`). Aynı projeye aynı anda iki basış gelince:

1. ikisi de planı ve kaydı okur, birbirinin yazmadığını görür;
2. ikisi de aynı adları alır;
3. ikisi de planı yazar; sonra yazan, öncekinin satırlarını içermeyen planı koyar.

Önceki basış "eklendi" demiştir ama işi plandan gitmiştir; ya da ikisi kalır, aynı kimlikle — kayıt
kimliğe göre tutulduğu için biri bitince öteki de bitmiş görünür ve hiç üretilmez. 511'in QA'sı 15
kabul edilmiş basıştan 8 iş saydı.

Test önce kırmızı görüldü (`backend/tests/test_plan_hold.py`; ikinci basış, birincinin ilk yazmasının
hemen önünde içeri alınır):

- `append`'in okuması ile yazması arasına giren başka bir `append` kayboluyor: plan `['bir']`, `'iki'` yok.
- Sekiz `append` aynı anda: Windows'ta üçü `PermissionError(13, 'Access is denied')` ile düştü — QA'nın
  gördüğü `[WinError 5] … .qe-tmp-… -> …\plan.json`.
- Her kapı ikinci basışa aynı adı veriyor: `start_batch` ve `queue_references` `['P0_0', 'P0_0']`,
  `queue_layer`'ın kopyası ve aynı sözlü `regenerate` `['P0_1', 'P0_1']`, `copy_frames`
  `['C1_0_a', 'C1_0_a']`, `fix_photo` aynı fotoğrafı iki kez düzeltiyor (`['fixed', 'fixed']`).

Hata 511'den eski.

**Ve kare kapatan kapılar** (reviewer'ın okumasından): `remove_frames` ve `remove_layer` kayıttaki
yerleri okur, hangi dosyayı başka hiçbir karenin tutmadığına karar verir ve sonra siler. Arada bir
kopya doğarsa (`copy_frames`, ya da `queue_layer`'ın ikinci varyantı) satırları aynı dosyayı gösterir,
ve silme onun fotoğrafını götürür: yeni kopyanın sıradaki videosu olmayan bir fotoğrafa düşer —
"eklendi" denen iş kaybolur. `save_order` da galeriyi okuyup sırayı bütün yazar; arada yerleştirilen
bir kopyanın yeri gider. Üçü de testle kırmızı görüldü: silme ile aynı anda kopya `['C1_0_a']` doğdu,
fotoğraf katmanı silinirken video basışı `2` iş ekledi, sürükleme kopyanın yerini sildi (`['0_a']`).

**Ve sürüklemenin listesi** (512'nin QA'sından): kilit yalnız sürükleme kapıya önce varınca yetiyordu.
Kopya önce düşer de ekran listesini kopya gelmeden yaptıysa, `save_order` ekranın listesini — bilinen
karelere süzülmüş — olduğu gibi yazıyordu; listede olmayan ikiz sıradan düşüp galerinin tepesine
çıkıyordu (QA'nın `race.py dragfirst`'ünde 10/10, tam aynı anda 16/30). Testle kırmızı görüldü
(`test_a_drag_sent_before_a_copy_arrived_keeps_the_copy_above_its_source`): `['0_a', '1_a']`, ikiz yok.

## Ne yapılır

**Projenin yazma kapısı tutulur.** `DrivePlanStore` her proje için bir kilit tutar ve onu dışarıya
`held(project)` olarak verir. Planın deposunda durur, çünkü işe planla başladı, ama planın kilidinden
fazlasıdır: kare adlandıran ya da kapatan kapıların, planı, kaydı ve galeri sırasını birlikte okuyup
yazdıkları kısmın kapısıdır. Döngü kaydı onun dışında yazar: biten katmanın satırı kendi yerini
söyler ve bir yer hakkındaki son satır geçerlidir (`remove_frames`'in eski kuralı). Kilit yeniden
girilebilir (`RLock`), çünkü tutan kapı kendisi de `append` çağırır. Kilitler adla bir sözlükte,
sözlüğün kendi küçük kilidinin altında açılır; her proje adı süreç boyunca bir kez. Port `PlanStore`
`held`'i söyler.

**`append` planı kendisi tutar.** Okuma ve yeniden yazma `held(project)` içinde: tek başına çağrılan
bir `append` de başka bir `append`'in yazdığını kaybettiremez. Okunamayan planın üstüne yazmama kuralı
aynı kalır.

**Ad veren kapılar planı adları okumadan önce tutar, yazdıktan sonra bırakır**, sırayı çalıştırmadan
(`run_queue`) önce:

| Kapı | Tutulan kısım |
|---|---|
| `start_batch` | `next_number` → `plan_frames` → `append` |
| `queue_references` | `next_number` → kartlar → `append` |
| `queue_layer` | galeri → kapsam → `known_ids` → kopyaların satırları ve kayıtları → sıra → `append` |
| `regenerate` | galeri → yeni ad → kopyanın kayıtları → `append` → sıra |
| `fix_photo` | galeri ve "değişti mi" bakışı → yeni ad → `append` → sıra → eski fotoğrafın silinmesi ve kayıtları |
| `copy_frames` | galeri → `known_ids` → ikizlerin kayıtları → sıra |

`copy_frames` planı yazmaz, ama ikizlere adı planla kaydın birlikte söylediğinden verir; tutmazsa iki
kopya basışı aynı ikizi doğurur.

**Kare kapatan kapılar ve sürükleme de tutar**, ilk okumadan son yazmaya:

| Kapı | Tutulan kısım |
|---|---|
| `remove_frames` | galeri ve yerler → silinecek dosyalar → silme → kayıt satırları → sıra |
| `remove_layer` | galeri ve yerler → silinecek dosyalar → silme → kayıt satırları |
| `save_order` | galeri → sıra |

Böylece galeri sırasını (`order.json`) yazan her kapı — `queue_layer`, `regenerate`, `fix_photo`,
`copy_frames`, `remove_frames`, `save_order` — sırayla yazar. Üçü de `run_queue` çağırmaz.

**Sürükleme listesinin adlandırmadığı kareler yerinde kalır.** Kilit altında `save_order`, ekranın
listesini (bilinen karelere süzülmüş, tekrarlar atılmış) alır ve galerinin şimdiki sırasında olup
listede olmayan her kareyi, galeride hemen altındaki karenin hemen üstüne geri koyar; altında hiçbir
şey yoksa en alta. Galeri alttan yukarı yürünür, böylece yan yana atlanan kareler kendi aralarındaki
sırayı korur. Ekranın listesi kopya gelmeden yapıldıysa ikiz, `copy_frame.placed`'in koyduğu yerde,
kaynağının hemen üstünde kalır. Kural `gallery_order.keep_unnamed`'de, saf bir fonksiyon. Galerinin
şimdiki sırası zaten okunan galeriden (`list_frames`) gelir; sıra dosyası ikinci kez okunmaz. Bugüne
kadar listenin unuttuğu kare bir sonraki okumada tepeye çıkıyordu; artık yerinde kalır. Sıra
dosyasının hiç bilmediği yeni bir kare de (galerinin tepesinde duran) o an tepedeki karenin üstüne
yazılır.

`retry_frame` ve `retry_failed` tutmaz: yeni ad vermezler, yalnız kırmızı bir videonun planda zaten
olan satırını projenin şimdiki ayarıyla yeniden yazarlar (`video_settings.as_set_now`). Aradaki bir
basış o satırı değiştirmez, ve yazmalarını `append`'in kendi kilidi korur.

`run_queue` kilidin dışında kalır: işçiyi almak bellekte bir adımdır (511) ve tutmaya ihtiyacı yoktur;
dışarıda olunca kilidin içinde başka bir kilit (işçinin kilidi) alınmaz.

## Neden hiçbir yazma kaybolmaz, hiçbir ad iki kez verilmez

- **Plan dosyası:** onu yazan tek yer `append`, ve her `append` okumasını ve yazmasını aynı projenin
  kilidinde yapar. İki `append` sırayla olur; sonraki, öncekinin `os.replace`'i döndükten sonra okur,
  yani öncekinin satırlarını okur ve onlarla birlikte yazar. İki yazma aynı anda dosyanın üstüne
  taşınmaz, bu yüzden geçici dosyalar da çarpışmaz.
- **Adlar:** ad veren her kapı adları okuduğu yerlerin (disk, plan, kayıt) okumasından o adları
  yazdığı yerlerin (plan, kayıt) yazmasına kadar aynı kilidi tutar. Aynı projenin ikinci basışı kilidi
  ancak birincinin yazmaları döndükten sonra alır ve okuduğunda onları görür; bu yüzden aldığı ad
  birincininkinden sonra gelir.
- **Silinen dosyalar:** silen kapı, hangi dosyayı kimsenin tutmadığına karar verdiği okumadan silmenin
  ve satırlarının sonuna kadar kilidi tutar. Kopya doğuran kapılar da kilitte; bu yüzden bir kopya ya
  silmeden önce doğar (ve silme onu görüp dosyayı bırakır) ya sonra (ve kaynağı silinmiş bulup
  doğmaz). Silinmiş bir fotoğrafa iş eklenmez.
- **Galeri sırası:** onu yazan her kapı onu okuduğu galeriden yazar ve aynı kilidi tutar; sonraki,
  öncekinin yazdığı sırayı okur. Sürükleme ise ekranın listesini yazar, ama o listede olmayan her
  kareyi okuduğu galerideki yerine geri koyar; bu yüzden ekran onu görmeden önce gelmiş bir kare de
  yerini kaybetmez, kim önce gelirse gelsin.
- **"Eklendi" denen iş:** kapı "eklendi"yi ancak `append` döndükten sonra söyler; o andan sonraki her
  `append` onun satırlarını okuyup yeniden yazar. Sırayı başlatmak ya da çalışan sıraya katılmak 511'in
  işi: yazılmış her iş ya yeni bir koşuyu başlatır ya onu sonra okuyacak bir geçişe katılır.
- **Eklenemeyen iş:** okunamayan plan, Drive'ın düşen bağlantısı ya da dolu Drive eskisi gibi bir
  `OSError` olur ve `web/app.py` onu ekrana sistemin kendi sözüyle getirir (`503`). Kilit hata olunca
  da bırakılır (`with`).

Bütün basışlar tek süreçte: Colab'da bir Flask sunucusu, iş parçacığıyla; ajanın `fix_photo`'su da aynı
sürecin `main.py`'sinden geçer. Kilit bellekte olduğu için bu yeter (`DriveMuteStore` da öyle).

## Maliyet

- **Basış başına:** bir kilit sözlüğü bakışı ve bir kilit alışı, bellekte. Drive'a ek okuma ya da
  yazma yok: kapılar eskiden ne okuyup ne yazıyorsa onu okuyup yazar. Proje, kare ve dosya sayısından
  bağımsız: O(1).
- **Aynı projeye aynı anda iki basış** (ad veren, kare kapatan ya da sürükleyen herhangi ikisi):
  ikincisi, birincinin tuttuğu kısım bitene kadar bekler — o kapının galeriyi okuması (kayıt, disk
  listesi, plan, sıra) ve yazmaları, silmede de dosya silmeleri; Drive'da birkaç gidiş dönüş, birkaç
  saniye, çok kare silinirken kare başına bir silme daha. Sonra kendi işini aynı maliyetle yapar.
- **Sürükleme:** Drive'a eskisi kadar gidiş dönüş; listede olmayan kareleri geri koymak bellekte,
  kare sayısının karesi kadar adım (kare başına bir arama), yüzlerce karede önemsiz.
- **Başka projelere basış:** beklemez; her projenin kendi kilidi var.
- **Döngü, `/api/status`, galeri ve sıra okumaları:** kilidi almaz, beklemez. Durdur ve yeniden
  adlandırma da almaz.
- **Bellek:** süreç boyunca basılmış her proje adı için bir kilit.

## Ne kaybolabilir, ne bozulabilir

- Diskte hiçbir şeyin biçimi değişmez; kilit bellekte yaşar. Sunucu tutarken ölürse plan ya eski ya
  yeni haliyle durur (geçici dosya ve `os.replace`, bugünkü gibi); yarım kalan basışın işi ya planda
  ya hiç yoktur, ve "eklendi" yalnız birincisinde söylenmiştir.
- Kilit tutulurken alınan başka kilit yok (kayıt, sıra ve disk yazmaları kilitsiz; `run_queue` dışarıda),
  döngü kilidi hiç almaz: kilitler arasında döngü yok, kilitlenme olmaz.
- Basış sürerken proje yeniden adlandırılırsa, eski addaki yazmalar klasör bulunamadığı için düşer
  (Drive'ın kapısı proje klasörünü hiç açmaz) ve basış hatayı ekrana verir; "eklendi" demez. Basış ile
  yeniden adlandırmanın başka bir yarışı 511'den beri BACKLOG'da.

## Sınırlar

- Videosu olmayan bir kareye aynı anda iki video basışı: 513'ten beri
  ([spec](2026-10-29-queen-editor-m513-bitmis-kare-yeniden-cizilmez-design.md)) ikinci basış karenin
  kendi video işini sırada bulur ve yalnız kopya karelerini ekler; karenin kendi işi bir kez planlanır
  ve bir kez üretilir — art arda iki basış da böyle davranır. İkinci varyantlar her basışın kendi kopya
  karesidir ve ikisi de üretilir.
- Windows'ta, plan okunurken (döngü, galeri) onun üstüne taşınan yazma hâlâ `Access is denied`
  alabilir: Windows açık bir dosyanın üstüne taşımaya izin vermez. Colab Linux'tur, orada olmaz; yalnız
  yerelde. Bu Drive'ın kapısının (`services/storage/`) her dosya için davranışı; bu madde ona
  dokunmuyor ([BACKLOG](../../queen-editor/BACKLOG.md), *"Windows'ta okunan bir dosyanın üstüne
  kayıt düşebilir"*).
- Referans havuzunun sırası ve arşiv işaretleri (`arsiv.json`) de okunup bütün yeniden yazılıyor,
  kilitsiz; bu madde onlara dokunmuyor. BACKLOG'a: *"Referans sırası ve arşiv işaretleri aynı anda iki
  yazmada birini kaybedebilir"*.
- Fotoğraf kaydına (`photos.jsonl`) döngü ve kapılar aynı anda, kilitsiz satır ekliyor. Yerel Linux'ta
  tek bir `O_APPEND` yazması ötekine karışmaz; Drive'ın FUSE bağlamasında bilinmiyor. BACKLOG'a:
  *"Fotoğraf kaydına aynı anda iki satır yazılabilir"*, Colab'da denenecek.
- Sürüklemenin listesinde olmayan kare artık tepeye çıkmaz, galerideki yerinde kalır; ekran her
  sürüklemede bütün galeriyi gönderdiği için bunu yalnız ekranın henüz görmediği kare yaşar. Ekranın
  bilmediği bir kare sürüklenerek taşınamaz: yeri, altındaki kareye bağlı kalır ve ekran onu
  gördüğünde kullanıcı onu ayrıca sürükler.

## Ne zaman bitti

- `append`'in okuması ile yazması arasına giren başka bir `append`'in satırları planda kalıyor.
- Sekiz `append` aynı anda: hepsi planda, hiçbiri hata vermiyor.
- Bir projenin planı tutulurken başka bir projeye `append` beklemeden yazıyor.
- Aynı projeye aynı anda iki basış, her kapıda: `start_batch` ve `queue_references` `P0_0` ve `P1_0`,
  `queue_layer`'ın kopyaları `P0_1` ve `P0_2`, aynı sözlü `regenerate` `P0_1` ve `P0_2`, `copy_frames`
  `C1_0_a` ve `C2_0_a` (ikisi de galerinin sırasında); `fix_photo`'nun biri `fixed`, öteki `changed` ve
  planda tek yeni satır.
- Bir kare silinirken aynı anda kopyası istenirse kare bütün gidiyor ve kopya doğmuyor; bir karenin
  fotoğraf katmanı silinirken aynı anda video istenirse video işi eklenmiyor (`0`).
- Sürükleme ile aynı anda doğan kopya, hangisi önce gelirse gelsin, sırada kaynağının hemen üstünde
  kalıyor: sürükleme önce gelince kopya onun yazdığı sıraya yerleşiyor; kopya önce gelip ekranın
  listesi onu bilmeyince `save_order` onu `['C1_0_a', '0_a', '1_a']` diye geri koyuyor. Listenin
  atladığı yan yana kareler kendi sıralarını koruyor.
- `python -m pytest queen-editor -q` ve `npm test --prefix queen-editor/frontend` yeşil. Ekran
  değişmediği için `dist` yeniden kurulmaz.

## Yalnız Colab'da görülecek

- Gerçek Drive'da çift tıklanan Kuyruğa ekle'nin iki işi de sıraya alıp üretmesi, ve ikinci basışın
  birkaç saniye beklemesi.
