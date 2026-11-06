# Yeni editör — 4. Depo

Core'un verisini Drive'da nasıl tuttuğu; aynı Drive köküne bakan birkaç Colab varken
[2. adımın](2026-11-03-yeni-editor-v1-2-alan-modeli.md) kurallarının nasıl doğru kaldığı.

## Özet

- **Her projenin bir baş dosyası vardır:** `projects/<proje>.json.gz`. Projenin şu anki hali
  (karelerin sırası, edit'ler, bekleyen işler, kuyruğu) ondadır. Hiç değişmeyen ağır veri (karelerin
  fotoğraf bilgisi, videolar, biten işler, history) projenin kendi **bloklarına** bir kez yazılır.
- **Ana liste, baş dosyalarının listelemesidir.** Projenin listedeki satırı (ad, arşiv, zamanlar,
  kuyruğunu çalıştıran Colab) baş dosyasının Drive etiketlerindedir (`properties`). `projects/`
  klasörünü listelemek bütün ana listeyi getirir: çoğunlukla tek sayfa, nadiren birkaç.
- **Bir değişiklik = Drive'a 2 çağrı:** baş dosyasının değişip değişmediğine bak (1 okuma), baş
  dosyasını içeriği ve etiketleriyle tek çağrıda yeniden yaz (1 yazma). Kuyruk değişiklikleri de
  böyledir. Proje büyüdükçe çağrı sayısı artmaz; yazılan bayt yavaş artar (sıkıştırılmış baş dosyası
  1.000 karede ~0,11 MB, 20.000'de ~0,25 MB; ölçüldü).
- **Okumalar Drive'a gitmez;** bellekten cevap verilir. `GET /health` de Drive'a gitmez. Başka
  Colab'ın değişikliği en çok ~5 sn'de bir, tek listelemeyle fark edilir.
- **Core yalnız istenen projeleri yükler.** Her istek tek bir projeye dokunur; bütün projeleri okuyan
  işlem yoktur.
- **Arka planda üç şey çalışır:** çöpe atma, üretilen işin 30 sn'de bir projesine bakması ve log'un
  5 dakikada bir Drive'a gitmesi (10. adım; yeni satır yoksa gitmez). Nabız, kira, sayaç dosyası
  yoktur. İstek, iş ve yeni log yokken Drive'a hiç gidilmez.

## Varsayımlar

**Drive çağrısının süresi** (Colab'dan; hepsi ölçülecek):

| Çağrı | Varsayılan süre |
|---|---|
| Küçük okuma (`files.get` yalnız bilgi), listeleme sayfası, etiket, çöpe atma, `generateIds` | 0,25 sn |
| Baş dosyasını yükleme (≤ 0,25 MB, tek istek) | 0,6 sn |
| İndirme, ≤ 1 MB | 0,3 sn |
| Aynı anda en çok 8 çağrı | — |

**Boyutlar** — yapay veriyle ölçüldü: bir kare kaydı ~1,8 KB (sahne, iki prompt, negatif, model,
LoRA, seed…); her kareye 1,3 iş, karelerin yarısında video; 10 edit (her biri en çok 2.000 yer), 100
bekleyen iş, iki `tail` (100 kare kaydı, 100 history kaydı).

| Kare | Baş dosyası, sıkıştırılmış (açılınca) | Bütün kayıt blokları, sıkıştırılmış (açılınca) | Bellekte |
|---|---|---|---|
| 1.000 | 0,11 MB (0,54) | 0,6 MB (3,8) | ~10 MB |
| 5.000 | 0,18 MB (0,82) | 3,0 MB (19) | ~50 MB |
| 20.000 | 0,25 MB (1,03) | 12 MB (76) | ~200 MB |

Sıkıştırma 20.000 karede ~25 ms sürer. Baş dosyası Drive'da açılıp okunamaz; buna gerek yok.

Ölçümün betiği tasarım sırasında yazıldı, depoda değil; sayılar bu tabloda.

## Ana fikir

1. **Değişen ile değişmeyen ayrıdır.** 2. adım söylüyor: fotoğraf "kareye bir kez, iş bitince
   gelir; sonra hiç değişmez"; "Son durumlar değişmez"; history kaydı "değişmez, silinmez".
   Değişmeyen veri bir kez yazılır, sonra yalnız okunur. Değişen veri küçüktür: kimliklerin listesi.
2. **Bir projenin şu anki hali tek dosyadır.** Baş dosyası yazıldıysa değişiklik olmuştur,
   yazılmadıysa olmamıştır. Drive bir dosyayı yüklemesi bitmeden değiştirmez (yeni içerik yükleme
   bitince görünür; belgede açık yazmıyor, ölçülecek). "Ya hep ya hiç" buna dayanır.
3. **Ana listenin satırı, satırın sahibi olan dosyanın üstündedir.** İki Colab iki ayrı projeye
   yazınca iki ayrı dosyaya yazar; ortak bir listenin üstüne yazıp birbirinin projesini düşürmezler.
   Satır içerikle aynı çağrıda yazılır; ikisi birbirini tutmaz hale gelemez.
4. **Yazmadan önce bakılır.** Core baş dosyasının md5'ini kimlikle okur. Bildiğinden farklıysa başka
   bir Colab yazmıştır: dosyayı indirir, kurallara yeniden bakar, sonra yazar. **Bu bir kilit
   değildir;** aynı saniyedeki iki yazmayı engellemez (koruma yok, bkz.
   [Sonraya kalanlar](2026-11-03-yeni-editor-v1-sonraya-kalanlar.md)). Gereği şudur: aynı projeyi
   sırayla iki Colab'da kullanmak (dün Colab 1, bugün Colab 2), ve kuyruğu Colab 1'de çalışan bir
   projenin Colab 2'de değişmesi. Bakmadan yazan core bellekteki eski hali yazar, öbür Colab'ın
   değişikliğini siler. Bedeli 1 okuma, ~0,25 sn.
5. **Yazma istek içinde olur, arkada değil.** Drive'a yazılmamış bir değişikliği öbür Colab'lar
   göremez; core ölürse agent "oldu" sandığı bir şeyi kaybeder. Bedeli: değiştiren her istek ~0,85 sn
   sürer.

## Drive'da ne nerede

```
<kök>/
  projects/
    <proje>.json.gz             baş dosyası: projenin şu anki hali; etiketleri ana listenin satırı
    <proje>/                    ilk blok yazılınca açılır
      kayit-<n>.jsonl.gz        kayıt blokları: kareler, videolar, biten işler, biten export'lar
      history-<n>.jsonl.gz      history blokları
      media/
        <kare>.png
        <video>.mp4
  exports/
    <YYYY-MM-DD HH-MM> <ad>/    aynı ad varsa (1), (2)…
      <ad>.mp4                  en son yüklenir
      photos/001.png …
  logs/
    <YYYY-MM-DD HH-MM> <core>/  core'un log'u, 5 dakikada bir parça (10. adım)
      001.log …
```

Colab'ın kendi diskinde: `core.json` (yalnız core'un kimliği; makine yaşadıkça core yeniden başlasa da
aynı kalır), `creates.json` (son 24 saatin proje oluşturmaları; bkz. Proje oluşturma) ve önbellek
(kapanmış bloklar, medya).

Yalnız core'un belleğinde: yüklenen projeler ve aynı anahtarla hâlâ süren istekler.

- Proje klasörü ve baş dosyası yalnız kimlikle adlanır. Ad değişince hiçbir dosyanın adı değişmez.
- Dosyalar adla aranmaz. Baş dosyası her dosyanın Drive kimliğini tutar; adlar Drive'da gezen bir
  insan içindir.
- Küçük fotoğraf ve videodan durağan görüntüler saklanmaz; istenince diskte üretilir.
- Modeller depoda değildir; core'daki model listesinden ve Colab'ın diskinde inmiş olanlardan gelir.

### Baş dosyası ne tutar

```json
{
  "v": 1,
  "seq": 812,
  "next": 4410,
  "frames": [[17, 233], [18, null], [25, 240], [4402, null]],
  "edits": [{"id": 40, "name": "kısa", "created": "2026-11-04T09:00:00Z", "updated": "2026-11-05T14:20:00Z",
             "places": [[41, 17, false], [42, 25, true]]}],
  "jobs": [{"id": 4401, "method": "t2i", "target": 4402, "output": "<ayrılmış kimlik>", "...": "..."}],
  "queue": {"paused": false, "stop_reason": null, "running": 4401, "started": "2026-11-04T09:10:00Z"},
  "exports": {},
  "trash": [],
  "records": {"blocks": [["<Drive kimliği>", 3998123]], "next": "<ayrılmış kimlik>", "tail": []},
  "history": {"blocks": [["<Drive kimliği>", 3990211, "2026-11-04T09:12:00Z"]], "next": "<ayrılmış kimlik>",
              "tail": [{"seq": 812, "key": "<istek anahtarı>", "hash": "<isteğin özeti>", "...": "..."}]},
  "folder": "<ayrılmış kimlik>",
  "media": "<ayrılmış kimlik>"
}
```

| Alan | Ne |
|---|---|
| `v` | Biçimin sürümü; eski biçim okunurken yükseltilir |
| `seq` | Projenin son history sıra numarası |
| `next` | Projede verilecek bir sonraki kimlik |
| `frames` | Karelerin sırası; her kare için şu anki videosu ya da `null`. Kare bu listede varsa vardır, fotoğrafı henüz gelmemiş olsa da |
| `edits` | Edit'ler: adı, oluşturulduğu ve son değiştiği zaman, yerleri; her yer `[yer kimliği, kare, sesi kapalı mı]` |
| `jobs` | Bekleyen ve çalışan işler, kuyruk sırasıyla: düşeceği kare, çıktısının ayrılmış kimliği, verilen her şey |
| `queue` | Durdurulmuş mu; kendiliğinden durduysa nedeni, dört alanlı hatasıyla (`stop_reason`); çalışan iş (`jobs`'ta durur, sırada sayılmaz) |
| `exports` | Yalnız süren export'lar |
| `trash` | Çöpe atılacak, henüz atıldığı kesinleşmemiş dosyalar |
| `records`, `history` | Kapanmış blokların kimliği ve boyu (history'de son kaydın zamanı da); sonraki bloğun ayrılmış kimliği; henüz bloğa geçmemiş son kayıtlar (`tail`) |
| `folder`, `media` | Proje klasörlerinin ayrılmış kimlikleri; ilk ihtiyaçta açılır |

**Etiketleri** (ana listenin satırı): `name` (Drive bir etikete en çok 124 bayt verir; Türkçe harf 2
bayt olduğundan 64 karakterlik ad gerekirse 3 etikete bölünür), `archived`, `created`, `updated`,
`runner` (kuyruğu çalıştıran core'un kimliği ya da boş). Bu bilgiler başka hiçbir yerde
durmaz.

### Bloklar ne tutar

Her satır bir kayıttır, hiç değişmez:

- `frame`: karenin fotoğrafı ve bilgileri — sahne, verilen ve modele giden prompt, negatif, model,
  LoRA seçimi ve o anki dosyaları, yön, gerçekte kullanılan seed, birlikte üretildiyse sırası, zaman,
  iş, fotoğrafın Drive kimliği, fotoğrafı başka kareden geliyorsa o kare. Kareye ürünü gelince bir kez
  yazılır (aşağıda).
- `video`: bir video — prompt'lar, model, uzunluk, seed, mutlu son, süresi, zaman, iş, kare, dosyası.
- `job`: son durumuna varmış bir iş (bitti, iptal) bütün bilgisiyle; süre olarak yalnız
  üretim süresi ([7. adım](2026-11-03-yeni-editor-v1-7-uretim-ve-kuyruk.md)).
- `export`: bitmiş, başarısız ya da iptal olmuş bir export, başladığı andaki yerlerin kopyasıyla.

History blokları: her değişikliğin kaydı — sıra, zaman, kim, hangi core, ne, neye, öncesi ve sonrası,
isteğin anahtarı ve özeti. Kuyruk değişiklikleri de buradadır. "Kareye fotoğraf geldi" kaydının
"sonrası" kare kaydının kendisidir; history onu kimliğiyle gösterir, kopyalamaz.

**`tail` ve mühürleme:** yeni kayıtlar önce baş dosyasının `tail`'ine girer; böylece bir değişiklik
yine tek yazmadır. Bir `tail` 100 kaydı ya da 256 KB'ı geçince aynı değişiklikte bloğa yazılır
("mühürlenir"). Açık blok açılınca 4 MB olana kadar büyür ve her mühürde baştan yüklenir; sonra
kapanır ve bir daha yazılmaz. Sıra hep aynıdır: **önce blok, sonra baş dosyası.**

Mühürde giden bayt (ölçüldü): dolu bir açık blok sıkıştırılınca ~0,65 MB'tır (history bloğu ~0,55
MB); ortalaması ~0,3 MB. İki akış ayrı ayrı ~100 değişiklikte bir mühürlenir: **değişiklik başına
ortalama ~6 KB, en çok ~12 KB.**

### Kare: ürününden önce ve sonra

Kare iş verildiği an var olur ve sıraya girer (2. adım). Ama fotoğrafın bilgisinin bir kısmı
(gerçekte kullanılan seed, birlikte üretildiyse sırası, dosyanın kendisi) ancak iş bitince bellidir.
Bu yüzden `frame` kaydı, iş için açılmış bir kareye ürünü gelince bir kez yazılır: `t2i`'de fotoğrafı,
`i2v`'nin yeni karesinde videosu. O zamana kadar karenin bilgisi işinden okunur.

| Ne oldu | Baş dosyasında | Blokta | Okurken |
|---|---|---|---|
| İş verildi | Karenin `frames`'te yeri; işi `jobs`'ta, `target` bu kare | — | "Üretiliyor". Kuyruğu başka Colab çalıştırıyorsa "başka bir Colab'da üretiliyor" (`runner`'dan) |
| İş hata verdi | Karenin yeri kalır; iş `jobs`'ta sıranın başına döner; kuyruk durur (`stop_reason`) | — | "Üretiliyor" |
| İş bitti | Karenin yeri kalır; iş `jobs`'tan çıkar | `frame` (yeni kareyse), `video` (i2v'yse), `job` (bitti) | Ürünüyle; fotoğrafı bir daha değişmez |
| İş iptal, kare iş için açılmıştı | Kare `frames`'ten aynı yazmada çıkar | `job` (iptal) | Kare yok |
| İş iptal, `i2v` var olan kareye düşecekti | Kare kalır | `job` (iptal) | Kare videosuz |

- Her satır tek bir değişikliktir. "Üretiliyor" yazılmaz; kareyi hedefleyen son işten
  okunur (2. adım: "Türetilen saklanmaz").
- İşi kuyrukta olan kare silinmez. Kural bellekten bakılır, Drive'a gidilmez.
- `i2v`'nin işi ve yeni karesi fotoğrafı daha kaydı yokken de kullanıyor sayılır; kaynak kare o
  arada silinse de fotoğraf çöpe gitmez, iş onunla yapılır. Fotoğraf, onu kullanan kare de iş de
  kalmayınca çöpe gider.
- **Video silmek:** `frames`'te karenin videosu `null` olur, video dosyası `trash`'e girer. Karenin
  fotoğrafı, kimliği, sıradaki ve edit'lerdeki yerleri değişmez; `video` kaydı blokta kalır (history
  onu gösterir). Onu hedefleyen başka iş yoksa yeni bir `i2v` bu kareye düşer.

## Ne nerede durur

Her bilgi tek bir yerdedir.

| Bilgi | Nerede | Kim yazar |
|---|---|---|
| Proje adı, arşiv, oluşturma, değişme | Baş dosyasının etiketleri | Projeyi değiştiren core |
| Kuyruğu hangi Colab çalıştırıyor | Baş dosyasının `runner` etiketi | Kuyruğu alan ya da bırakan core |
| Karelerin sırası, her karenin şu anki videosu | Baş dosyası `frames` | Projeyi değiştiren core |
| Karenin fotoğraf bilgisi, videonun bilgisi | Blokta (`frame`, `video`), bir kez | İşi bitiren core |
| Ürünü gelmemiş karenin bilgisi | Onu hedefleyen işte | İşi veren core |
| Edit'ler ve yerleri | Baş dosyası `edits` | Projeyi değiştiren core |
| Bekleyen işler ve sırası, çalışan iş, durdurulmuş mu | Baş dosyası `jobs` ve `queue` | Projeyi değiştiren core ya da kuyruğu çalıştıran core |
| Biten iş | Blokta (`job`) | İşi bitiren core |
| Süren export / biten export | Baş dosyası `exports` / blokta | Export'u yapan core |
| History, istek anahtarı ve isteğin özeti | `history.tail`, sonra history blokları | Değişikliği yapan core |
| Aynı anahtarla hâlâ süren istek | Yalnız isteği alan core'un belleği | O core |
| Core'un kimliği | Colab diskindeki `core.json` | O core |
| Son 24 saatte oluşturulan projelerin anahtarı ve ayrılmış kimliği | Colab diskindeki `creates.json` | Projeyi oluşturan core |
| "Üretiliyor", "başka bir Colab'da", fotoğrafı kaç kare kullanıyor | Hiçbir yerde; okurken çıkarılır | — |

İki yerde duranlar: mühürleme sırasında bir an hem blokta hem `tail`'de duran kayıtlar ve proje
oluşturmanın anahtarı (history'de ve 24 saat `creates.json`'da) (bkz. Değerlendirme 10).

## Bir değişiklik

1. Core içinde **o projenin yazma kilidi** alınır. Başka projeler beklemez; okumalar hiç beklemez.
2. Kurallar bellekteki hale karşı bakılır. Toplu istekte her şey önce bakılır; engel varsa hepsi
   sayılır, hiçbir şey yazılmaz. İstek anahtarı son 24 saatin anahtarlarında varsa ilk cevap döner.
3. Yeni hal kurulur: yeni `frames`/`edits`/`jobs`/`queue`, `tail`'e eklenen kayıtlar ve anahtarı
   taşıyan history kaydı, etiketler, çöpe gidecek dosyalar.
4. **Bak:** baş dosyasının md5'i ve etiketleri kimlikle okunur (1 okuma). Bildiğinden farklıysa başka
   bir Colab yazmıştır: baş dosyası (ve değiştiyse açık blok) indirilir, 2. adıma dönülür.
5. Bir `tail` sınırı aştıysa açık blok yazılır (1 yazma, ~100 değişiklikte bir).
6. **Yaz:** baş dosyası içeriği ve etiketleriyle **tek çağrıda** yüklenir (`files.update`,
   multipart). **Değişikliğin olduğu an budur.**
7. Bellekteki hal yenisiyle değiştirilir, kilit bırakılır, cevap döner.
8. Arkada: `trash`'teki dosyalar çöpe atılır. Atıldıkları bir sonraki değişiklikte `trash`'ten düşer;
   bunun için ayrıca yazılmaz.

Okumalar o an bellekteki hali okur; yarım bir değişiklik görmezler, Drive'ı beklemezler.

**Yazma belirsiz kalırsa** (Drive cevap vermeden bağlantı koptu): aynı içerik üstel beklemeyle en
çok ~60 sn yeniden yüklenir; aynı içeriği iki kez yazmak zararsızdır. Hâlâ bilinmiyorsa istek
`storage_unconfirmed` ile döner. Sonraki yazmanın 4. adımı akıbeti çözer: md5 denenen içeriğinkiyse
yazılmıştır, öncekininse yazılmamıştır, ikisi de değilse başka bir Colab yazmıştır. Aynı anahtarla
tekrar gelen istek de bu bakıştan geçer; yazılmışsa anahtarı bulur, ilk cevabı döner.

**Okunamayan baş dosyası:** o proje okunamıyor diye görünür, hiçbir istek ona yazmaz; boş sayılıp
üstüne yazılmaz. Öbür projeler etkilenmez. Önceki hali Drive'ın sürümlerinde durur.

### Aynı istek iki kez

- **Anahtar ve isteğin özeti** (içeriğinin karması) değişikliğin history kaydına yazılır. Aynı
  anahtar ve aynı özet: ilk cevap, değişen şeylerin bugünkü haliyle. Aynı anahtar, farklı özet: hata.
- **24 saat tutulur, sayı sınırı yoktur.** Core her yüklü proje için son 24 saatin anahtarlarını
  bellekte dizinler. Bunun için proje ilk yüklenirken son kaydı 24 saatten yeni history blokları da
  indirilir. History kaydı ~200 bayttır; dakikada 10 değişiklikle 24 saat ~2,9 MB eder: açık blok ve
  en çok bir kapanmış blok. 24 saattir değişmemiş projede hiç indirilmez.
- Anahtarlar baş dosyasında bir liste olsaydı, dakikada 10 değişiklikle 24 saatte baş dosyası ~1,35
  MB (sıkıştırılmamış) büyürdü ve her değişiklik bunu yeniden yazardı. Bu yüzden anahtar
  değişikliğin kendi kaydındadır.
- **Süren istek:** core'un belleğinde, anahtar → süren istek. Aynı anahtarla ikinci istek gelirse
  yeniden yapılmaz; ilki bitince onun cevabı ikisine de döner. Bellek yeter: adaptör bir listeyi aynı
  core'a yeniden gönderir ([8. adım](2026-11-03-yeni-editor-v1-8-agent-tarafi.md)); core yeniden
  başladıysa ilk istek ya yazılmıştır (anahtar history'de) ya hiç olmamıştır (yeniden yapılır).
  Proje oluşturmada adreste proje olmadığı için anahtar diskteki notla bulunur (Proje oluşturma).
  Kuralı 6. adım yazar.
- Reddedilen istek kaydedilmez, anahtarı da: tekrarına yeniden bakılır.

### Kuyruk

Her projenin kuyruğu baş dosyasındadır (`jobs`, `queue`, `runner` etiketi). Bir Colab bir anda tek
projenin kuyruğunu çalıştırır; hangisi olduğunu bellekte bilir. Her kuyruk değişikliği tek bir
yazmadır (bak + yaz) ve projenin history'sine girer; işin başlaması ve bitmesi history'ye girmez
(2. adım), yalnız baş dosyasına yazılır.

| Ne | Ne yazılır |
|---|---|
| Boştaki Colab'dan, kuyruğunu kimsenin çalıştırmadığı projeye iş | İş, kareleri ve `runner` = bu core, tek yazmada |
| Başka bir kuyruğu çalıştıran Colab'dan iş | Yalnız iş ve kareleri; kuyruk bekler |
| `resume`, Colab boştaysa | `runner` = bu core, `paused` = hayır |
| `resume`, Colab başka bir projenin kuyruğunu çalıştırıyorsa | Önce eski projeye: `runner` boş, çalışan işi sıranın başına; sonra yeni projeye: `runner` = bu core. İki proje, iki yazma (aşağıda) |
| `pause` | `paused` = evet; çalışan iş sıranın başına |
| Kendiliğinden durma (işin hatası, ComfyUI, model inemedi, Drive'da yer yok, ürün yüklenemedi) | `paused` = evet, `stop_reason` = nedeni, aynı yazmada; işin hatasıysa iş sıranın başına döner; bütün Colab'lar görür. `resume` ikisini de siler (kullanıcı, 5 Kasım) |
| Sırayı vermek (`PATCH …/queue`) | Yeni sıra; o arada başlamış ya da bitmiş işler atlanır, cevap onları söyler |
| Kuyruğu boşaltmak | Bekleyen işler bloğa "iptal" olarak geçer; iş için açılmış, ürünü gelmemiş kareleri aynı yazmada gider |
| İşin başlaması | `queue.running` = bu iş |
| İşin bitmesi | İş `jobs`'tan çıkar, bloğa geçer; `queue.running` boşalır |
| Kuyruğun boşalması, hangi yolla olursa (bitme, iptal, boşaltma) | `runner` boşaldığı yazmada boşalır; Colab boşta kalır |

- **`resume`'un iki yazması** bu tasarımda iki projeye yazan tek istektir. Sırası hep aynıdır: önce
  eski kuyruk bırakılır, sonra yenisi alınır. Arada kesilirse eski kuyruk durmuş, yenisi alınmamış
  kalır; ikisi de geçerli bir haldir. Aynı istek yeniden gönderilince eski projede yapılacak bir şey
  kalmamıştır, yenisi alınır.
- **Başka Colab'ın fark etmesi:** kuyruğu çalıştıran core her işten önce baş dosyasına bakar; üretim
  sürerken de 30 sn'de bir. `runner` artık kendisi değilse kuyruğu bırakır; iş iptal edildiyse,
  kuyruk durdurulduysa ya da proje silindiyse üretimi keser. Bu yüzden başka bir Colab'dan gelen
  `pause`, iptal ve proje silme o Colab'da en geç 30 sn içinde etkisini gösterir.
- **Kapanmış bir Colab'ın kuyruğu** projede, `runner`'ı eski core olarak kalır. Başka bir Colab'da
  `resume` onu kaldığı yerden sürdürür. Çalışan işi de geçer: sıranın başına döner ve burada baştan
  üretilir; öbür Colab hâlâ açıksa onu en geç 30 sn içinde keser. Core kapanmış bir Colab'ı açık
  olandan ayırt edemediği için tek kural budur; bedeli en çok bir üretimdir (kullanıcı, 4 Kasım —
  "neredeyse bitmiş bir iş atılsın, bunun bize bir zararı yok, basitse").
- **Kapanmış olabilecek Colab:** başka bir Colab'ın çalıştırdığı iş, süre sınırının (fotoğraf 5 dk,
  video 10 dk, varyantlarla çarpılmış) iki katından uzun süredir çalışıyor görünüyorsa, bu Colab'dan
  `/wait` hemen döner: "kuyruğu çalıştıran Colab kapanmış olabilir; `resume` ile buraya alınabilir;
  kullanıcıya sor" (kullanıcı, 6 Kasım). Bunun için işin başlama zamanı `queue.running`'le aynı
  yazmada baş dosyasına yazılır; nabız gerekmez.
- **Core aynı makinede yeniden başlarsa** kimliği `core.json`'dan gelir; açılıştaki listede `runner`'ı
  kendisi olan projeyi bulur, onu yükler. Çalışan iş sıranın başına, bekleyen olarak döner; kuyruk
  ComfyUI açılınca sürer (7. adım).

### Bir iş

- **Verilirken:** çıktısının Drive kimliği önceden ayrılır (core'un elindeki kimlik havuzundan;
  `files.generateIds` bir çağrıda 1000 kimlik verir). Kare o an `frames`'e girer (`t2i`: istenen
  yere, yoksa sona; `i2v` yeni kareye düşecekse kaynak karenin arkasına). İş `jobs`'un sonuna girer.
  Hepsi tek yazmadır.
- **Başlarken:** baş dosyasına ve çıktının kimliğine aynı anda bakılır (2 okuma, paralel): `runner`
  hâlâ bu core mu, kuyruk durdurulmamış mı, iş sıranın başında mı; çıktı dosyası
  zaten var mı (önceki deneme yükleyip kaydedemeden öldüyse; varsa iş GPU'ya gitmeden biter). Uygunsa
  üretim başlar ve aynı anda `queue.running` yazılır; GPU yalnız ~0,25 sn'lik bakışı bekler.
  `running` yazılamazsa üretim yine sürer; iş bitince bekleyenden bitti'ye geçer.
- **Çalışırken:** 30 sn'de bir baş dosyasının md5'ine bakılır (yukarıda).
- **Biterken:** çıktı **kilitsiz** ayrılmış kimliğe yüklenir; yeniden yükleme `409` alır, ikinci
  dosya olmaz. Sonra kilit alınır, bir değişiklik gibi yazılır: kareye ürünü gelir, iş "bitti" olarak
  bloğa geçer. Kurallar artık izin vermiyorsa (iş iptal edilmiş, proje silinmiş, kuyruk `resume` ile
  başka bir Colab'a geçmiş, yani `runner` artık bu core değil) hiçbir şey yazılmaz, dosya çöpe gider.
  Devredilen iş yeni Colab'da, yeni bir ayrılmış çıktı kimliğiyle baştan üretilir; eski kimlik
  çöpe giden dosyanındır.
- **Hata verirse** (ComfyUI reddetti ya da süre doldu): iş sıranın başına, bekleyen iş
  olarak döner, kare yerinde kalır; kuyruk aynı yazmada kendiliğinden durur (Kuyruk). Tek yazma.
- **İptal:** iş "iptal" olarak bloğa geçer; iş için açılmış, ürünü gelmemiş kare aynı yazmada
  sıradan çıkar. İş çalışıyorsa çıktı kimliği `trash`'e girer.
- Biten iş GPU'yu bekletmez: bitirme ayrı bir iş parçacığında olur, sıradaki iş hemen başlar.
- Birlikte üretilen varyantlar birlikte biter ve tek yazmayla kaydedilir (her biri kendi history
  kaydıyla).

### Export

- Colab başına aynı anda bir export (7. adım).
- **Başlarken:** `exports/` klasöründe adında o ad geçen klasörler listelenir; `(1)`, `(2)` klasörün
  bütün adına, tarih ve dakikası dahil, bakılarak verilir (2. adım). Bu **her export'ta 1 listelemedir** (100 birim, ~0,25 sn); başka Colab'ların ve elle
  açılmış klasörler de görülür. Klasör ayrılmış kimlikle açılır. Export baş dosyasına "sürüyor" diye
  yazılır.
- Fotoğraflar Drive içinde kopyalanır; videolar diskten (yoksa Drive'dan) okunur; birleşik video en
  son, ayrılmış kimliğine yüklenir.
- **Bitince:** export bloğa geçer. Başarısız ya da iptal olursa klasörü `trash`'e girer.
- **Core yarıda öldüyse:** aynı core yeniden başlayınca "sürüyor" görünen kendi export'unun birleşik
  videosuna bakar. Video tamsa export "bitti" olur; değilse "başarısız: core yeniden başladı" olur ve
  klasörü çöpe gider. Başka bir Colab da `DELETE …/exports/{id}` ile aynısını yapar. Bitmiş videosu
  olan bir klasör hiç çöpe gitmez.

### Proje oluşturma, ad, silme

- **Oluşturma:** baş dosyası ayrılmış kimlikle, etiketleriyle tek çağrıda oluşturulur (1 yazma).
  Drive listelenmez: ad tek olmak zorunda değildir; aynı adlı başka proje varsa cevap onu bellekteki
  listeden söyler. Yeniden deneme `409` alır ve aynı projeyi döner. Yarım proje olmaz: baş dosyası
  varsa proje vardır. Klasörler ilk ihtiyaçta açılır.
- **Core yeniden başlarsa:** adreste proje olmadığı için oluşturmanın anahtarı projenin history'sinde
  aranamaz. Bu yüzden core, oluşturmadan hemen önce "anahtar → isteğin özeti, proje kimliği, ayrılmış
  kimlik" notunu Colab'ın diskindeki `creates.json`'a yazar (geçici dosya, sonra yerine taşıma);
  kayıtlar 24 saat tutulur. Aynı anahtarla gelen istek nottaki kimlikle oluşturmayı dener: Drive `409`
  dönerse proje vardır, baş dosyası okunur, ilk cevap döner; oluşursa ilk deneme Drive'a hiç
  ulaşmamıştır. Özet farklıysa Drive'a gidilmeden `idempotency_key_reused`. Drive'a hiçbir şey eklenmez
  (kullanıcı, 5 Kasım). Bedeli oluşturma başına diske birkaç milisaniyelik bir yazma.
- **Colab'ın kendisi giderse** not da gider; tekrar yeni bir Colab'a gelirse ikinci proje açılabilir.
  Cevaptaki `same_name` bunu gösterir; agent kullanıcıya söyler.
- **Ad değiştirme:** bir değişiklik gibi yazılır; yeni ad etikette, history kaydı `tail`'de, aynı
  çağrıda. Aynı adlı proje varsa cevap onu söyler.
- **Silme:** projenin her şeyi Drive'ın çöpüne gider (kullanıcı, 5 Kasım — "komple silinsin"). Önce
  baş dosyası çöpe atılır (1 çağrı): proje o an yoktur, listede görünmez, hiçbir adresi okunmaz.
  Sonra proje klasörü (bloklar, history, medya) ve süren export'ların klasörleri çöpe gider. Arada
  kesilirse baş dosyası olmayan bir proje klasörü kalır; core açılıştaki listede onu görür ve çöpe
  atar. Kuyruğu başka Colab'da çalışıyorsa orada en geç 30 sn içinde durur (baş dosyası çöpte
  görünür). Kullanıcı Drive'ın çöpünden 30 gün içinde geri alabilir.

## Başka Colab'ın yaptığını görmek

Her Colab kendi UI'ını sunar ([9. adım](2026-11-03-yeni-editor-v1-9-ui.md)); hepsi aynı projeleri
görür.

| Ne | Nasıl | Ne zaman |
|---|---|---|
| Ana liste (yeni proje, ad, arşiv, silme, kuyruğu kim çalıştırıyor) | `projects/` listelenir: her baş dosyasının etiketleri ve md5'i; `nextPageToken` bitene kadar, çoğunlukla bir sayfa | Bir istek geldiğinde, son listeleme 5 sn'den eskiyse. Drive'ın listesi de gecikebilir (ölçülecek) |
| Yüklü projenin içi | Baş dosyasının md5'i kimlikle okunur; değiştiyse indirilir | O projeye istek geldiğinde, son bakış 5 sn'den eskiyse |
| Yazmadan hemen önce | Kimlikle okunur | Her zaman |

- İstek yoksa Drive'a gidilmez. UI açıkken birkaç saniyede bir sorduğu için ekran kendiliğinden
  güncellenir.
- Liste md5'i de verdiği için core, bellekteki hangi projelerin eskidiğini ayrıca sormadan bilir.
- Kapanmış bloklar hiç değişmez; başka Colab'ın değişikliği için genellikle yalnız baş dosyası
  indirilir.

## Bellek ve disk

- **Bellek sınırı: yüklü projeler için 1 GB** (ortamdan değiştirilebilir). Neden: Colab'ın belleği
  ComfyUI'yle paylaşılır ve modeller yüklenirken sistem belleği de kullanılır; Colab belleğin miktarını
  da garanti etmez. 1 GB, ~100.000 kareye yeter (ölçüldü: ~10 MB / 1.000 kare): ör. beş 20.000
  karelik ya da yüz 1.000 karelik proje.
- Sınır aşılınca en uzun süredir dokunulmayan proje bellekten çıkar. Kuyruğu bu Colab'da çalışan
  proje, süren bir isteği ya da export'u olan proje çıkmaz. Çıkan proje istenince yeniden yüklenir:
  baş dosyası indirilir, kapanmış blokları diskten okunur.
- **Disk önbelleği:** kapanmış bloklar ve medya. İkisi de hiç değişmez; önbellek bayatlamaz. Sınırı
  (ortamdan; varsayılan 10 GB) aşınca en eski kullanılan çıkar. İndirilen dosyanın md5'i kayıttakiyle
  karşılaştırılır. ComfyUI'nin girdisi buradan verilir; çıktısı yüklendikten sonra buraya girer.

## Depo portu

Port, Drive'ın dosyalarını değil projenin kayıtlarını anlatır. Baş dosyası, `tail`, bloklar, md5 ve
etiketler Drive adaptörünün içindedir; çekirdek onları bilmez.

**Projeler**

| İşlem | Ne yapar |
|---|---|
| `projects()` | Ana liste: her projenin satırı (kimlik, ad, arşiv, zamanlar, kuyruğu çalıştıran core) ve sürümü |
| `version(p)` | Projenin şu anki sürümü ve satırı; ucuz |
| `load(p)` | Projenin şu anki hali: satır, kareler ve sırası, videolar, edit'ler, işler ve kuyruk, export'lar, son 24 saatin istek anahtarları; sürümüyle |
| `create(p, satır, anahtar)` | Projeyi açar; aynı anahtarla tekrar aynı projeyi döner |
| `commit(p, beklenen sürüm, değişiklik)` | Değişiklik: satırın yeni alanları, konan kayıtlar (kare, video, iş, edit, export), kalkan kareler ve edit'ler, yeni sıra, kuyruk, anahtarı ve özetiyle history kaydı (yoksa yok), çöpe gidecek dosyalar. Sürüm farklıysa "eskimiş" döner, hiçbir şey yazmaz |
| `history(p, şu sıradan önce, kaç)` | History kayıtları |

**Dosyalar**

| İşlem | Ne yapar |
|---|---|
| `reserve(n)` | Henüz yazılmamış n dosya için adres |
| `put(ref, yer, ad, bayt)` | O adrese yazar; tekrarı güvenli; md5 ve boyut karşılaştırılır |
| `exists(ref)`, `get(ref)` | Var mı; baytlar. Çöpteki dosya yoktur |
| `copy(ref, yer, ad)` | Depo içinde kopya, bayt indirilmez |
| `trash(ref)` | Çöpe; klasörse içiyle. Zaten çöpteyse ya da yoksa başarı |
| `export_names(önek)` | O adla başlayan export klasörleri |
| `space()` | Kota, kullanılan, çöpte duran |

Kalıcı silme yoktur. Bir kayıt son durumuna vardıktan sonra (iş bitti, export bitti) bir daha
`commit`'e konmaz; 2. adım "Son durumlar değişmez" diyor. Drive adaptörü değişmeyen kayıtları bloğa
bu yüzden koyabilir. Port'un hataları deponun sözünü taşır; çekirdek onları dört alanlı hataya
çevirir. Hız sınırına karşı üstel bekleme ve belirsiz yazmanın yeniden yüklenmesi Drive adaptörünün
içindedir; çekirdek `429` görmez, yalnız son reddi ya da belirsizliği.

**Her işlem neye karşılık gelir**

| İşlem | Drive adaptörü | D1 + R2 |
|---|---|---|
| `projects()` | `files.list` `projects/`, `trashed=false`, etiketler ve md5; `nextPageToken` bitene kadar (çoğunlukla 1, nadiren birkaç sayfa) | `SELECT … FROM projects` |
| `version(p)` | `files.get` md5 ve etiketler | `SELECT version …` |
| `load(p)` | Baş dosyası + diskte olmayan kayıt blokları + son 24 saatin history blokları (paralel) | Projenin satırları, birkaç `SELECT` |
| `create` | `files.create`, ayrılmış kimlikle, etiketlerle | `INSERT` |
| `commit` | md5'e bak; gerekirse açık bloğu yaz; baş dosyasını içerik + etiketle tek çağrıda yaz | Tek `batch`: önce satırın sürümü koşulla artırılır (`UPDATE … WHERE version = ?`); tutmazsa batch geri alınır; sonra satırlar |
| `history` | `tail` + history blokları, diskte önbellek | `SELECT … ORDER BY seq DESC LIMIT` |
| `reserve` | `files.generateIds` | Anahtarın kendisi |
| `put` | Kimlikle oluşturma; 5 MB üstü resumable; tekrarda `409` | R2 `put`, `onlyIf` ile bir kez |
| `copy` | `files.copy` | R2 kopyası |
| `trash` | `trashed=true` | `trash/` önekine taşı; yaşam döngüsü kuralı 30 gün sonra siler |
| `export_names` | `files.list`, `name contains` | Önekle listeleme |
| `space` | `about.get` | Servisin kendi sınırı |

- D1'de sıra ve yerler satırın JSON sütunudur: 20.000 kare ~0,35 MB, D1'in satır sınırı 2 MB. İstek
  anahtarı history satırının bir sütunudur.
- Başka yol: her projeye bir Durable Object, kendi SQLite'ı ve transaction'ıyla; ana liste için bir
  D1 tablosu. Aynı port.
- Veritabanında `commit` gerçekten koşulludur: aynı proje iki Colab'da kendiliğinden korunur.

## Maliyet: işlem işlem

N projedeki kare sayısı. "Sırayla", birbirini bekleyen çağrı adımlarıdır. Birimler: okuma 5,
listeleme 100 (sayfa başına), yazma 50, indirme 200.

| İşlem | Drive çağrısı | Sırayla | Birim | Süre | Not |
|---|---|---|---|---|---|
| `GET /health`, `GET /api`, `GET /models` | 0 | 0 | 0 | 0 | Drive yavaşken ya da erişilemezken de hemen cevap verir |
| Ana liste (`GET /projects`) | 0; 5 sn'den eskiyse 1 listeleme | 0–1 | 0–100 | 0–0,25 sn | Drive az dönerse bir sayfa daha (+100, +0,25 sn) |
| Proje okumak, bellekte (kareler, işler, kuyruk, edit'ler, son history) | 0; 5 sn'den eskiyse 1 okuma | 0–1 | 0–5 | 0–0,25 sn | |
| Proje okumak, ilk kez | baş dosyası + B kayıt bloğu (B: N=1000 → 1, 5000 → 5, 20.000 → 19) + son 24 saatin 0–2 history bloğu | 2 | 200·(1+B+0–2) | ~1 / ~2 / ~5 sn | 20.000'de ~3 sn'si açmak ve çözmek; kapanmış bloklar diskte önbellekte kalır |
| Fotoğraf, video, durağan görüntü | ilk seferde 1 indirme | 0–1 | 0–200 | 0–~1 sn | Sonra diskten; küçük boyut ve durağan görüntü diskte üretilir |
| Kare silmek | bak + yaz; arkada 1–2 çöp | 2 | 55 + 50–100 | ~0,85 sn | Fotoğrafı başka kare ya da iş kullanıyorsa çöpe gitmez. İşi kuyruktaysa reddedilir, Drive'a gidilmez |
| Video silmek | bak + yaz; arkada 1 çöp | 2 | 105 | ~0,85 sn | Kare, fotoğrafı ve yerleri kalır |
| Bir kareyi taşımak, edit değiştirmek, arşivlemek, ad değiştirmek | bak + yaz | 2 | 55 | ~0,85 sn | |
| Karelerin bütün sırası | bak + yaz (+ N büyükse 1 blok) | 2–3 | 55–105 | ~0,85–1,5 sn | History öncesi ve sonrası: 20.000 karede ~0,7 MB, hemen mühürlenir |
| İş vermek (t2i, 4 varyant; i2v) | bak + yaz | 2 | 55 | ~0,85 sn | Kareler o an sıraya girer |
| Kuyruk: sıra, durdurmak, boşaltmak, `resume` (Colab boşken) | bak + yaz | 2 | 55 | ~0,85 sn | |
| `resume`, başka bir kuyruğu bırakarak | 2 × (bak + yaz) | 4 | 110 | ~1,7 sn | |
| İşin başlaması | 2 okuma (paralel) + 1 yazma | 2 | 60 | GPU ~0,25 sn bekler | Yazma üretimle aynı anda. Boş yer en çok dakikada bir (+5) |
| Üretim sürerken | 30 sn'de 1 okuma | — | 10/dk | — | |
| İş bitişi, fotoğraf | 1 yükleme; bak + yaz | 1 + 2 | 105 | ~1,5 sn, GPU'nun dışında | 4 varyant birlikte: 4 paralel yükleme + 1 yazma, 255 |
| İş bitişi, video (~20 MB) | resumable 1+2 parça; bak + yaz | 3 + 2 | ~205 | ~3 sn, GPU'nun dışında | |
| İş hata verdi, kuyruk durur | bak + yaz | 2 | 55 | ~0,85 sn, GPU'nun dışında | İş sıranın başında bekler, kare yerinde kalır |
| İşi iptal etmek | bak + yaz; çalışıyorsa arkada 0–1 çöp | 2 | 55–105 | ~0,85 sn | İş için açılmış kare aynı yazmada gider. Başka Colab'daki üretim en geç 30 sn'de durur |
| Aynı anahtarla tekrar | 0 | 0 | 0 | 0 | İlk cevap bellekten; ilki sürüyorsa onu bekler |
| Mühür (her akışta ~100 değişiklikte bir) | 1 yazma, değişikliğin içinde | +1 | 50 | +~0,6 sn | Giden en çok ~0,65 MB, ortalama ~0,3 MB; değişiklik başına ortalama ~6 KB |
| Export başlatmak | 1 listeleme + 1 klasör + bak + yaz | 4 | 205 | ~1,4 sn | Her export'ta 1 listeleme, `(1)`, `(2)` için |
| Export süresince | fotoğraf başına 1 kopya; diskte olmayan video başına 1 indirme; 1 resumable yükleme | — | 50·foto + 200·video | foto 500 → ~16 sn | GPU'yu beklemez |
| Export bitişi | bak + yaz | 2 | 55 | ~0,85 sn | |
| History, son kayıtlar | 0 | 0 | 0 | 0 | `tail` ve bellek |
| History, eski kayıtlar | blok başına 1 indirme, ilk seferde | 1 | 200 | ~0,4 sn | Sonra diskten |
| Proje oluşturmak | 1 oluşturma | 1 | 50 | ~0,6 sn | Drive listelenmez |
| Proje silmek | 1 çöp (baş dosyası); arkada 1–2 çöp (proje klasörü, süren export'un klasörü) | 1 | 50 + 50–100 | ~0,25 sn | |
| Core'un açılışı | kök ve klasörleri (`projects/`, `exports/`, `logs/`) için 2 listeleme; ana liste 1 listeleme; 1 `about`; 1 `generateIds`; kuyruğunu çalıştırdığı proje varsa onun yüklenmesi | 3 (+2) | ~320 (+ yükleme) | ~1,3 sn (+ yükleme) | Başka hiçbir proje okunmaz |

**Giden bayt:** değiştiren her istek baş dosyasını baştan yükler: 1.000 karede ~0,11 MB, 20.000'de
~0,25 MB. Üstüne mühürler değişiklik başına ortalama ~6 KB ekler.

**Gereksiz çağrı var mı?** Yazmadan önceki bakış (Ana fikir 4) ve işin başında çıktıya bakmak
gereklidir; ikisi de ucuzdur ve paralel yapılır. Aynı isteğin içinde bir dosya iki kez okunmaz;
yazılan bir dosya geri okunmaz (md5 yerelde hesaplanır, Drive'ın döndürdüğüyle karşılaştırılır).

## Hatalar

Her hata dört alanla döner ([11. adım](2026-11-03-yeni-editor-v1-11-kod-standardi.md)). Drive'ın
hatasında `message` Drive'ın sözüdür; `hint` neden tahmin etmez, emir vermez, yalnız durumu ve core'un
bildiği seçeneği söyler. Deponun hataları:

| `code` | `message` | `details` | `hint` |
|---|---|---|---|
| `storage_unconfirmed` | Drive'ın sözü | proje, istek anahtarı | "Kaydedilip kaydedilmediği bilinmiyor. Aynı anahtarla yeniden gönderilirse yapılmışsa ilk cevap döner, yapılmamışsa bir kez yapılır." |
| `storage_rejected` | Drive'ın sözü (ör. kota, hız sınırı ~60 sn sürdü) | proje, Drive'ın hata kodu | "Hiçbir şey yazılmadı. İstek aynı anahtarla yeniden gönderilebilir." |
| `project_unreadable` | Okuyucunun sözü | proje, baş dosyasının Drive kimliği | "Bu projeye yazılmıyor. Baş dosyasının önceki hali Drive'ın sürüm geçmişinde durur; geri almak kullanıcının kararıdır." |
| `project_newer_format` | Projenin bu core'dan yeni bir sürümle yazıldığı | projenin `v`'si, core'un bildiği | "Bu core bu projeye yazmaz. Bu Colab'ı yeni sürümle açmak gerekir; kullanıcıya sor." |
| `storage_low` (export isteği) | Boş yer, gereken yer, çöpün tuttuğu | aynıları, bayt olarak | "Export başlamadı. Drive'da yer açılınca yeniden denenebilir; kullanıcıya sor." |
| `storage_low` (kuyruğun durma nedeni) | Aynısı | Aynısı | "Kuyruk durdu, işler bekliyor. Drive'da yer açılınca `resume` ile sürdürülür; kullanıcıya sor." |

Adlar örnektir; kesin listeyi 6. adım yazar.

## Kota, çöp ve hesap

- **Önden bakış:** bir iş üretime ya da bir export başlamadan önce, boş yer çıktının tahmini + 2
  GB'tan azsa başlamaz (`storage_low`). `space()` dakikada en çok bir kez okunur. İş başlamazsa
  kuyruk kendiliğinden durur ve nedenini söyler; işler bekler, kaybolmaz. Yer açılınca `resume` ile
  sürer (2. adım).
- Dolu Drive'da yükleme düşer, hiçbir şey yazılmaz, hata Drive'ın sözüdür.
- Core yalnız çöpe atar, `files.delete` hiç çağırmaz. Çöp kotaya sayılır; Drive onu 30 günde kendisi
  boşaltır.
- **Hesap:** dosyalar Colab'ı açan Google hesabının Drive'ındadır, queen-editor'daki gibi; bütün
  Colab'lar aynı hesapla açılır. Çöpe yalnız dosyanın sahibi atabildiği için bu, bütün dosyaların
  sahibini tek tutar.
- **İzin:** core Drive'a, Colab'ı açan hesabın izniyle gider: notebook açılınca Colab'ın giriş
  penceresi onaylanır. Token saklanmaz.
- **Kullanıcı Drive'da elle bir şey yaparsa:** klasörü taşımak ya da yeniden adlandırmak zararsızdır
  (kimlikle bağlı). Medyayı çöpe atmak okurken "Drive'da bu dosya yok" diye görünür. Bir baş
  dosyasını çöpe atmak projeyi listeden düşürür; çöpten geri almak geri getirir.
- **Büyük yüklemeler:** 5 MB'a kadar tek istek; üstü resumable, 16 MB'lık parçalar. Kopan parça
  kaldığı yerden sürer; yarım oturum Drive'da dosya bırakmaz.

## Bellek içi adaptör

- Drive adaptörünü taklit eder: adres ayırma, aynı adrese yazma, md5 ve boyut, etiketler, sayfalı
  liste, çöp, ayarlanabilir kota.
- Hata enjeksiyonu: yazmadan önce düş, yazdıktan sonra düş (akıbet bilinmez), yavaş ol, reddet
  (Drive adaptörünün beklemesi bittikten sonraki ret gibi).
- Core'un ölmesi ve ikinci Colab: aynı depo üstünde ikinci bir core açılır; Değerlendirme 1'in her
  satırı ve kuyruğun Colab'dan Colab'a geçişi böyle denenir. Saat ve beklemeler dışarıdan verilir.
- Aynı sözleşme testleri iki adaptörde koşar. Drive'ınki bu makineden, ayrı bir deneme Google
  hesabının Drive'ında koşar; hesabın token'ı depoda durmaz. Bir kez de Colab'ın ücretsiz katmanında
  (12. adım).
- Drive adaptörünün kendi testleri (`tail` ve mühür, etiketin bölünmesi, `409`, `429`'a karşı üstel
  bekleme, Drive çağrısı sayıları) sahte bir Drive API'ye karşı koşar (12. adım).

## Değerlendirme

### 1. Dayanıklılık

Her yazma tek bir bütün dosyadır; Drive yüklemesi bitmemiş dosyayı değiştirmez (resumable için
belgede: dosya yükleme bitince oluşur; var olan dosyanın güncellenmesi için açık yazmıyor, ölçülecek).

| Nerede kesilir | Ne kalır | Ne kaybolur | Kim onarır |
|---|---|---|---|
| Bakıştan ya da yazmadan önce | Eski hal | Değişiklik olmadı | Aynı anahtarla tekrar; bir kez yapılır |
| Baş dosyası yazıldı, cevap gitmedi | Yeni hal, anahtarı history kaydında | Hiçbir şey | Aynı anahtarla tekrar ilk cevabı döner |
| İstek sürerken core yeniden başladı | Ya eski hal ya yeni hal | Süren isteğin bellekteki kaydı | Aynı anahtarla tekrar: anahtar history'deyse ilk cevap, değilse yeniden yapılır |
| Proje oluşturuldu, cevap gitmeden core yeniden başladı | Proje; anahtarı history'de ve `creates.json`'da | Hiçbir şey | Aynı anahtarla tekrar: not aynı kimliği verir, Drive `409` döner, proje döner |
| `resume`'un iki yazması arasında | Eski kuyruk bırakılmış, yenisi alınmamış | Hiçbir şey | Aynı istekle tekrar |
| Açık blok yazıldı, baş dosyası yazılmadı | Kayıtlar hem blokta hem `tail`'de | Hiçbir şey | Okurken kimlikten teke iner; sonraki mühür aynı bloğu yeniden yazar |
| Yeni blok oluşturuldu, baş dosyası yazılmadı | Blok, önceden ayrılmış kimlikte | Hiçbir şey; sahipsiz dosya kalmaz | Sonraki mühür aynı kimliğe yazar |
| Yazıldı, çöpe atma bitmedi | `trash` listesi baş dosyasında | Hiçbir şey; dosyalar geç çöpe gider | Projeyi yazan ya da yükleyen sonraki core |
| Medya yüklenirken | Drive yarım dosya oluşturmaz | GPU süresi | İş bekliyor kalır; aynı kimliğe yeniden yüklenir |
| Medya yüklendi, kayıt yazılmadı | Dosya ayrılmış kimlikte; iş bekliyor, kare "üretiliyor" | Hiçbir şey | İş yeniden başlarken dosyayı görür, GPU'suz bitirir |
| Export sürerken | "Sürüyor" | O export | Aynı core yeniden başlayınca ya da başka Colab iptal edince |
| Colab makinesi gider | Drive'daki her şey, kuyruk dahil | Bellek | Başka Colab'da `resume` |

Yarım ya da bozuk dosya bırakan bir adım yok. Okunamayan bir baş dosyasının üstüne yazılmaz; önceki
hali Drive'ın sürümlerindedir.

### 2. Tekrar deneme ve artıklar

- Her yeni dosya (baş dosyası, blok, klasör, fotoğraf, video, export) önceden ayrılmış kimlikle
  oluşturulur; tekrar `409` alır, çift dosya olmaz (Drive belgesi).
- Değiştiren her istek anahtar taşır; anahtar projenin history kaydındadır, 24 saat bakılır, başka
  Colab'a gönderilse de bulunur. Hâlâ süren aynı anahtar beklenir. Çift iş, çift kare olmaz.
- Baş dosyasının ve açık bloğun güncellenmesi aynı içerikle tekrarlanır; zararsız.
- **Sahipsiz kalabilenler**, ikisi de ender:
  - İptal edilen bir işin çıktısı: iptal çıktının kimliğini `trash`'e koyar, ama iş o sırada
    çalışıyorsa çıktı iptalden sonra yüklenebilir. İşi çalıştıran core sonucu kendisi çöpe atar; o
    an ölürse dosya sahipsiz kalır.
  - Aynı saniyedeki iki yazmada kaybolan değişikliğin medyası.
  Bunları bugün kimse temizlemez. Yaşanırsa: proje klasörünü listeleyip hiçbir kaydın göstermediği
  dosyaları çöpe atan bir süpürme (proje başına 1 listeleme). v1'de yok.

### 3. Tek core içinde eşzamanlılık

Aynı projeye yazan her şey (istekler, işin başlaması ve bitmesi, export) o projenin yazma kilidini
alır; sırayla yazarlar, her biri bir öncekinin sonucuna karşı kurallara bakar. Biten iş dosyasını
kilitsiz yükler, kilidi yalnız ~0,85 sn'lik kayıt için alır: bir istek en çok bir yazma kadar bekler.
Kare silmek işi kuyruktayken reddedildiği için biten işin karesi kaybolmaz; iş o arada iptal
edildiyse biten iş bunu görür ve sonucunu çöpe atar. Aynı anahtarla iki istek gelirse ikincisi ilkini
bekler. `resume` iki projenin kilidini aynı anda tutmaz: önce eskisini, sonra yenisini alır. Başka
projeler beklemez. Okumalar kilit almaz; yazma bitince bellekteki hal tek hamlede yenisiyle değişir.

### 4. Aynı proje iki Colab'da

Koruma yok; aynı proje iki Colab'da aynı anda açılmaz (Sonraya kalanlar).

- **Sırayla:** Colab 1'de çalışılan proje sonra Colab 2'de değiştirilirse sorun yok: Colab 2
  yazmadan önce Drive'daki hali okur. Kuyruğu Colab 1'de çalışırken projenin Colab 2'de değişmesi de
  böyle: işin başlaması ve bitişi de yazmadan önce bakar.
- **Aynı anda:** risk, iki yazmanın ~0,85 sn'lik bakış–yazma aralığında çakışmasıdır (ör. iki boş
  Colab aynı projeye aynı saniyede iş verir). En kötü sonuç: önce yazanın değişikliği bütünüyle
  kaybolur, history kaydıyla birlikte. Proje bozulmaz: baş dosyası her zaman bir core'un kurallara
  uyan bütün halidir.
- Kaybolan değişiklik bir ürünün gelişiyse: dosyası Drive'da kalır, iş "bekliyor" görünür; iş yeniden
  başlarken dosyayı görür ve GPU'suz bitirir.
- Kaybeden core bunu fark eder: sonraki bakışta aynı sıra numarasında başka core'un kaydını görür;
  "Bu projede şu değişikliğiniz başka bir Colab'ın aynı andaki değişikliğiyle kayboldu" der:
  `GET /projects/{p}`'nin `lost_changes`'inde (6. adım) ve log'da. Bilgi bu core'un belleğindedir,
  depoya yazılmaz.
- Açık blokta bir an tutarsızlık olabilir (bir core'un mühürlediği kayıtlar ötekinin baş dosyasında
  yok); kural: baş dosyası doğrudur, onun göstermediği kayıt yok sayılır.

### 5. Ortak ana liste

Ortak bir dosya yok. Her projenin satırı kendi baş dosyasındadır; farklı projelerde çalışan iki
Colab ayrı dosyalara yazar. **Bir proje listeden düşemez.** Aynı anda iki proje oluşturmak iki ayrı
dosyadır. Ad tek olmak zorunda olmadığı için paylaşılan bir kural da yok; aynı ad cevapta bellekteki
listeden söylenir.

### 6. Görünürlük

- Ana liste: bir istek geldiğinde, son listeleme 5 sn'den eskiyse; `nextPageToken` bitene kadar
  okunur. Drive listesinin kendi gecikmesi belgelenmemiş; ölçülecek. Beklenen: birkaç saniye.
- Yüklü proje: o projeye istek geldiğinde, 5 sn'den eskiyse kimlikle okunur; listenin gecikmesine
  bağlı değildir.
- Yazmadan önce: her zaman güncel.
- Kuyruğu çalıştıran Colab başka Colab'dan gelen `pause`, iptal, `resume` ve silmeyi en geç 30 sn'de
  görür.
- UI açıkken birkaç saniyede bir sorduğu için başka Colab'ın değişikliği ~5–10 sn içinde görünür.

### 7. Çağrı tablosu

Yukarıdaki "Maliyet: işlem işlem". Özetle: değiştiren her istek, kuyruk değişiklikleri dahil, 2
sıralı çağrı, ~0,85 sn, 55 birim ve 0,11–0,25 MB; ~100 değişiklikte bir mühür (+1 yazma, ortalama
~0,3 MB). İşin başlaması GPU'yu ~0,25 sn bekletir. Okumalar ve `GET /health` 0; ana liste en çok 5
sn'de 1 listeleme. Gereksiz okuma ya da aynı dosyayı iki kez okuma yok.

### 8. Büyüme

| Ne büyür | Çağrı sayısı | Yazılan / okunan veri |
|---|---|---|
| Kare sayısı N | Hiçbir işlemde artmaz (ilk yükleme hariç: 1 + N/~1.000 indirme; 4 MB'lık blok ~1.000 karenin kare, video ve iş kayıtlarını tutar) | Her değişiklik baş dosyasını yazar: 1.000 karede 0,11 MB, 20.000'de 0,25 MB (sıkıştırılmamış halinde sırada kare başına ~13 bayt, edit'te yer başına ~25 bayt, ~0,3 MB'ı N'den bağımsız) |
| Proje sayısı P | Ana liste: 1000 projeye bir sayfa, Drive az dönerse birkaç; başka hiçbir işlem P'ye bağlı değil | Liste satırı başına ~200 bayt |
| History | Artmaz | `tail` en çok 256 KB; yüklerken yalnız son 24 saat, eski kayıtlar istenince blok blok |
| İstek anahtarları | Artmaz | History kaydında ~70 bayt; baş dosyası büyümez |
| Biten işler | Artmaz | Bloklarda; yüklerken okunur |

**Verinin tamamını okuyan tek işlem** bir projeyi bir Colab'da ilk kez yüklemektir (o projenin bütün
kayıt blokları; kapanmış bloklar diskte önbellekte kaldığı için aynı makinede bir kez). **Verinin
tamamını yazan işlem yok.** Silinen karelerin kayıtları bloklarda kalır (history onları gösterir);
ilk yükleme onları da okur. Bellek 1 GB'la sınırlıdır (Bellek ve disk).

### 9. Kota, hız sınırı ve depolama

Bir Colab, dakikada (kullanım profili):

| Ne | Birim |
|---|---|
| 10 değişiklik × 55, ~%10'u mühürlü (+50) | ~600 |
| 2 iş: başlama (60), bitiş (fotoğraf 105, video ~205), üretim sürerken bakışlar (10) | ~440 |
| UI açık: 5 sn'de bir liste (12 × 100) + açık projeye bakış (12 × 5) | 1.260 |
| Çöpe atma (~3 × 50), boş yer (5), export adı (en çok 100) | ~255 |
| **Toplam** | **~2.550** |

**4 Colab: dakikada ~10.200 birim, 325.000'in ~%3'ü.** En büyük kalem UI'ın listesidir; liste
önbelleğini 10 sn yapmak bunu yarıya indirir. Liste birkaç sayfaya bölünürse o kalem sayfa sayısıyla
çarpılır; yine %10'un altında kalır.

Ani yükler: 20.000 karelik projeyi ilk yüklemek ~4.000; 500 fotoğraflı export ~25.000.

Sınıra takılınca Drive `403 User rate limit exceeded` ya da `429` döner. Drive adaptörü, belgenin
önerdiği gibi üstel bekler (en çok ~32 sn, rastgele kaydırmayla) ve yeniden dener; istek yavaşlar, bir şey
kaybolmaz. ~60 sn'de olmazsa istek `storage_rejected` ile döner. Saniye başına sınır belgelenmemiş;
bu makineden, deneme hesabıyla dört süreçle ölçülecek (Ölçülmemiş varsayımlar).

**Drive'ın eski sürümleri.** Baş dosyasının her güncellemesi Drive'da bir sürüm bırakır (ölçülecek;
belge bunu açık yazmıyor). Belgeye göre ikili dosyaların eski sürümleri genellikle 30 gün tutulur;
dosyanın 100 sürümü olunca daha erken silinebilir. "Keep Forever" işaretli sürümler kotaya sayılır;
ötekilerin sayılıp sayılmadığını belge söylemiyor, doğrulanmadı.

| Proje başına, değiştiği sürece | Tutabileceği eski sürüm |
|---|---|
| Baş dosyası, 100 sürüm × 0,11–0,25 MB | 11–25 MB |
| Açık kayıt bloğu (~25 mühürde kapanır) | ~10 MB |
| Açık history bloğu (~200 mühürde kapanır) | ~40 MB |
| **Toplam** | **~60–75 MB**; değişiklik durduktan en çok ~30 gün sonra Drive kendisi siler |

Kotaya sayılıyorsa (ölçülecek) yapılacaklar, sırayla: (1) history bloğunu 1 MB'ta kapatmak (~40 →
~4 MB); (2) eski sürümleri adaptörün içinde silmek (`revisions.delete`). İkincisi kalıcı silmedir;
"Core hiçbir dosyayı kalıcı silmez" kuralına istisnadır ve ancak kullanıcı onaylarsa yapılır.

### 10. Normalizasyon

Her bilgi tek yerdedir (tablo: "Ne nerede durur"). Türetilen hiçbir şey saklanmaz: kare ve video
durumu, işin başka Colab'da üretilmesi, fotoğrafın kaç karede kullanıldığı, kare sayısı okunurken
çıkarılır. Kuyruğun sırası ayrı bir liste değildir: `jobs`'un kendi sırasıdır. İstek anahtarı ayrı
bir liste değildir, değişikliğin kendi kaydındadır.

İki yerde duranlar ve neden:

| Ne | Nerede | Neden | Tutmazsa doğru olan |
|---|---|---|---|
| Mühürlenen kayıtlar | Bir an hem açık blokta hem `tail`'de | Önce blok, sonra baş dosyası yazılır | Aynı kayıttır; baş dosyası doğrudur |
| Yüklü projeler | Core'un belleği | Okumalar Drive'a gitmesin | Drive; yazmadan önce bakılır |
| Kapanmış bloklar, medya | Colab diskinde önbellek | Bir daha indirilmesin | Hiç değişmedikleri için tutmazlık olmaz; md5'le karşılaştırılır |
| Proje oluşturmanın anahtarı | History'de ve 24 saat `creates.json`'da | Core yeniden başlayınca projeyi bulmak için | Drive; not yalnız ayrılmış kimliği verir, sonucu Drive'ın `409`'u söyler |

Liste satırı (ad, arşiv, `runner`) başka hiçbir yerde durmaz; içerikle aynı çağrıda, aynı dosyaya
yazılır.

### 11. Değişime açıklık

- **Yeni bir alan** (ör. karede bir not): kaydın JSON'una eklenir; eski kayıtta yoksa varsayılanı
  okunur. Hiçbir dosya yeniden yazılmaz.
- **Ana listeye yeni bir bilgi** (ör. kare sayısı, kapak fotoğrafı): baş dosyasına bir etiket daha;
  içerikle aynı çağrıda yazıldığı için tutarsız kalamaz. Bu türetilmiş bir kopya olur; 2. adımın
  "Türetilen saklanmaz" kuralına bir istisna olarak yazılmalıdır.
- **Yeni bir varlık** (ör. referans havuzu): değişen kısmı baş dosyasına yeni bir bölüm, değişmeyen
  kısmı yeni bir kayıt türü; port'un `commit`'ine yeni bir kayıt türü; D1'de yeni bir tablo.
- **Biçim değişirse:** baş dosyası ve her kayıt `v` taşır. Eski sürüm okunurken bellekte yükseltilir;
  baş dosyası sonraki değişiklikte yeni biçimle yazılır, bloklar hiç yeniden yazılmaz, her okunuşta
  yükseltilir.
- Eski kod yeni biçimi açmaz: `v` bilmediği bir sayıysa proje `project_newer_format` ile görünür,
  yazılmaz. Bütün Colab'ların aynı sürümle açılması gerekir.

### 12. Tek veritabanına geçiş

Port Drive'a özgü şunları saklar: baş dosyası, `tail` ve mühürleme, bloklar, md5'in sürüm olarak
kullanılması, etiketlerin liste satırı olarak kullanılması, adın etiketlere bölünmesi, "bak sonra
yaz", Drive kimliklerinin ayrılması, Drive'ın çöpü ve sürümleri.

- **Değişen kod:** yalnız adaptör. Çekirdek ve endpoint'ler değişmez. Aynı sözleşme testleri iki
  adaptörde koşar.
- **Veri taşıma:** bütün core'lar kapalıyken tek seferlik bir betik, iki adaptör arasında port
  üstünden: her proje için `load` ve `history` Drive'dan okunur, D1'e yazılır. Medya Drive'dan R2'ye
  kopyalanır; R2 anahtarı Drive kimliğinin kendisi seçilirse kayıtlardaki dosya adresleri hiç
  değişmez. Export klasörleri taşınmaz, Drive'da kalır.
- **Geçişte kendiliğinden düzelenler:** aynı proje iki Colab'da (koşullu `commit`), `resume`'un iki
  yazması (tek `batch`), bütün projelerde aramanın ucuzlaması (SQL; Sonraya kalanlar), eski
  sürümlerin depolaması.

### 13. Sadelik

- **Drive'da dosya türleri:** baş dosyası, kayıt bloğu, history bloğu, medya (fotoğraf, video),
  export dosyaları. Colab diskinde: `core.json` (yalnız kimlik), `creates.json` (son 24 saatin proje
  oluşturmaları), önbellek.
- **Hareketli parçalar:** proje başına yazma kilidi; yazmadan önce bakış; `tail` ve mühürleme;
  `trash` listesi; kimlik havuzu; 5 sn'lik liste önbelleği; üretim sürerken 30 sn'lik bakış; süren
  isteklerin bellekteki anahtarları; belleğin sınırı.
- **Arka planda çalışan:** çöpe atma, üretim sürerken bakış ve 5 dakikada bir log. İstek, iş ve yeni
  log yokken Drive'a hiçbir çağrı gitmez: nabız, kira, sayaç dosyası yok.
- En karmaşık parça mühürlemedir. Onsuz her değişiklik ya iki yazma olurdu (baş + blok) ya da baş
  dosyası bütün history'yi taşırdı. Sınırları sayıyla belli (100 kayıt / 256 KB, 4 MB) tek bir
  fonksiyondur.

### 14. Ölçülmemiş varsayımlar

| Varsayım | Neye dayanıyor | Küçük deney |
|---|---|---|
| Kimlikle okuma (md5) başka bir Colab'ın yazmasından hemen sonra günceldir | Bakış–yazma | İki Colab: A 200 kez yazar ve her yazmada B'ye haber verir (küçük bir dosyayla); B hemen md5 okur. Eski md5 kaç kez döndü |
| İçerik + etiket tek multipart `files.update`'te ya birlikte olur ya hiç | Liste satırı ile içeriğin tutması | Bir döngü dosyayı içinde ve etiketinde aynı sayaçla yazar; öbürü sürekli indirir ve etiketi okur. Sayaçlar hiç ayrıştı mı, yarım içerik okundu mu |
| Var olan dosyanın güncellenmesinde yeni içerik yalnız yükleme bitince görünür | Yarım baş dosyası olmaması | Yukarıdaki deneyde yükleme ortasında bağlantıyı kes; dosya eski haliyle mi |
| `files.list` etiketleri ve md5'i döner; listenin gecikmesi kaç saniye | Görünürlük | Yaz, sonra 0,5 sn'de bir listele; 100 denemede gecikmenin dağılımı |
| `files.list` 1000'e kadar projeyi çoğunlukla tek sayfada döner | Ana liste ve kota | 1000 dosyalı klasörü `pageSize=1000` ile 100 kez listele; kaç sayfa geldi |
| Ayrılmış kimlikler günlerce geçerlidir | Önceden ayrılan blok, klasör, çıktı kimlikleri | 10 kimlik ayır; 1, 3, 7 gün sonra onlarla dosya oluştur |
| Çok dosyalı bir klasör tek çağrıda çöpe gider | Proje silme | 2.000 dosyalı bir klasörü çöpe at; içindekilerin `trashed`'ine bak |
| Dört Colab aynı hesapla saniye sınırına takılmaz | Kota hesabı | Ücretsiz katmanda bu makineden ölçülür, deneme hesabıyla dört süreç: bir dakika boyunca saniyede 3'er yazma; `403/429` sayısı |
| Her güncelleme bir sürüm bırakır; eski sürümler kotaya sayılmaz | Depolama (Değerlendirme 9) | Bir dosyayı 500 kez güncelle; `revisions.list` sayısına ve `about.storageQuota` farkına bak |
| `name contains` export adlarında büyük/küçük harfe bakmaz | Export klasör adı | "Final" ve "final" adlı iki klasörle sorgula |
| Çağrı süreleri (0,25 / 0,6 / 0,3 sn) | Bütün süre tahminleri | Her çağrı türünden 100'er tane, Colab'dan |

## Kaynaklar

- [Drive API sınırları ve birim maliyetleri: okuma 5, listeleme 100, yazma 50, indirme 200; kullanıcı başına dakikada 325.000; saniye sınırı yazmaz; `403`/`429` ve üstel bekleme](https://developers.google.com/workspace/drive/api/guides/limits)
- [Yüklemeler: multipart en çok 5 MB; ayrılmış kimlikle tekrar güvenli, başarılı ise `409`; resumable dosya yükleme bitince oluşur](https://developers.google.com/workspace/drive/api/guides/manage-uploads)
- [`files.update`: multipart ile içerik ve bilgi tek istekte; koşullu yazma parametresi yok](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/update)
- [`files.list`: sayfa başına en çok 1000; "The service may return fewer than this value"; `nextPageToken` liste bitince yoktur; güncellik belgelenmemiş](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/list)
- [`files` kaynağı: `md5Checksum`, `version`, `properties`](https://developers.google.com/workspace/drive/api/reference/rest/v3/files)
- [Özel etiketler: etiket başına 124 bayt (anahtar dahil), dosya başına en çok 30 açık etiket](https://developers.google.com/workspace/drive/api/guides/properties)
- [`files.generateIds`](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/generateIds)
- [Çöp ve silme: 30 gün, yalnız sahip çöpe atar](https://developers.google.com/workspace/drive/api/guides/delete)
- [Sürümler (revisions): eski ikili sürümler genellikle 30 gün; 100 sürüm olunca daha erken silinebilir; "Keep Forever" sürümleri kotaya sayılır, ötekiler için bir şey söylemez](https://developers.google.com/workspace/drive/api/guides/manage-revisions)
- [Drive yardımı, sürümler: "might be permanently deleted after 30 days or if there are 100 newer versions"](https://support.google.com/drive/answer/2409045)
- [`about.storageQuota`](https://developers.google.com/workspace/drive/api/reference/rest/v3/about)
- [Colab SSS: kaynaklar garanti edilmez, zamanla değişir](https://research.google.com/colaboratory/faq.html)
- [D1 `batch()`: "Batched statements are SQL transactions"; biri düşerse bütünü geri alınır](https://developers.cloudflare.com/d1/worker-api/d1-database/)
- [D1 sınırları: satır en çok 2 MB, SQL cümlesi 100 KB, veritabanı 10 GB, sorgu başına 100 parametre](https://developers.cloudflare.com/d1/platform/limits/)
- [R2 tutarlılığı ve koşullu yazma](https://developers.cloudflare.com/r2/reference/consistency/)
- [R2 yaşam döngüsü kuralları](https://developers.cloudflare.com/r2/buckets/object-lifecycles/)
- [Durable Objects SQLite depolaması ve transaction'ı](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/)
