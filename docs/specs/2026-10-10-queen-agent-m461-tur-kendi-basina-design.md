# Madde 461 · Tur sunucuda kendi başına koşar — tasarım

**Tarih:** 10 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
461 · **Dal:** `feat/queenagent-v10`, ana klasörde · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Kaynak:** mimarın sohbet tasarımı (`tmp/chat-turn-design.md`), 9. bölümün 2. adımı; 2, 3, 5, 6, 7 ve 8.
bölümlerin üstüne kurulu. Kullanıcı tasarımı beş cevabıyla onayladı (yol haritasının 461 – 463
satırları). **Öncesi:** [440](2026-10-09-queen-agent-m440-kara-kutu-design.md) kara kutu,
[449](2026-10-09-queen-agent-m449-kopan-baglanti-design.md) kopan bağlantı,
[460](2026-10-10-queen-agent-m460-model-sure-design.md) modelin sessizlik sınırı; 458'in yerini alır.

## Ne, neden

**Bugün** tur, onu başlatan POST'un kendisi: `routes.py` `stream_answer`'ı HTTP cevabının içinde
koşturuyor. Bundan dört şey çıkıyor:

- Sekme kapanınca ya da bağlantı kopunca tur ölüyor — bir sonraki yazışında. Model uzun düşünürken hiç
  yazmadığı için tünel bağlantıyı ~100 sn'de kesiyor (sinyal yalnız izin beklerken atılıyor).
- Stop ve izin sohbete bağlı (`MemoryStops`, `MemoryPermissions`, anahtar `(proje, sohbet)`): turlar
  arasında basılan bir Stop sonraki turu doğarken kesiyor, erken bırakılmış bir Allow sonraki turun
  sorusunu kimseye sormadan geçiriyor.
- Aynı sohbette iki tur aynı anda koşabiliyor; bağlantısı kopan turu tünel yaşatırsa sohbete iki cevap
  yazılıyor. Tur sürerken sürüm değiştirmek ve Continue here de sohbet dosyasını yazıyor, ve turun son
  yazısı onların yazdığını eziyor ya da tersi.
- Sohbet dosyası bir mesajda dört kez okunuyor: route, `append_message`, `stream_answer`'ın başı ve
  sonundaki `append_message`.

**Olacak** (kullanıcı — *"chatin durumları vs frontendin değil backendin sorumluluğu olur … try again
sadece durmuşsa başlatır loop'u"*):

- Tur sunucuda kendi iş parçacığında koşar, tarayıcı bağlı olsun olmasın. Tarayıcının gitmesi yalnız
  onu dinleyeni bitirir, turu değil.
- Sohbet başına tek tur. Tur sürerken gelen ikinci istek — yeni mesaj, düzenleme, Try again — 409 ve
  *"this chat is still answering -- try again once it has finished"* alır *(kullanıcı — "İkinci istek
  reddedilir")*; sürüm değiştirmek ve Continue here de aynı sözle; projeyi silmek, projenin bir sohbeti
  cevap verirken *"a chat in this project is still answering -- try again once it has finished"* ile.
- Stop ve izin o turun kendisine bağlı: tur bitince ikisi de onunla gider, sonraki tura ulaşamaz.
- **İzin bekleyen tur sonsuza kadar bekler** *(kullanıcı — "sonsuza kadar beklesin")*; **bekleyen izin
  yalnız bellekte** *(kullanıcı — "(a) yalnız bellek")*: sunucu yeniden başlarsa tur ölür ve soru
  cevapsız kalır.
- Tur kendisine verilen kayıtla çalışır: sohbet dosyası bir mesajda bir okuma ve iki yazma.
- **Ekran değişmez.** POST bugünkü kareleri geçici bir köprüyle verir: köprü canlı turu dinler, ve 15
  saniyede bir sinyal atar — tünelin kesmesi turun bütün süresince önlenir.
- Backlog'dan katılanlar: Try again'in zaten yazılmış cevapta döngüye girmesi, tur sürerken sürüm
  değiştirme ve kırpma, sohbet dosyasının iki kez okunması.

## Nasıl

### Durum: `domain/turn.py`

Yeni modül, saf kurallar. `status_of(chat, live)` sohbetin durumunu tek yerden söyler:

| Durum | Ne zaman |
|---|---|
| `running` | canlı bir tur var, soru beklemiyor |
| `waiting` | canlı tur bir izin sorusunda bekliyor |
| `answered` | açık hattın son mesajı sıradan bir cevap |
| `stopped` | son mesaj durdurulmuş cevap |
| `failed` | son mesaj başarısız cevap (440, 445) |
| `unanswered` | son mesaj kullanıcının — eski bir sohbet dosyası da, ölen bir tur da böyle okunur |
| `idle` | sohbette mesaj yok |

`running` ve `waiting` yalnız bellekte; ötekiler diskteki son mesajdan okunur. Sohbet dosyasında yeni
alan ve taşıma yok (tasarım 8). `is_owed_an_answer` gider: yerini `unanswered` alır.

Aynı modülde turun anlık görüntüsü, `Snapshot`: turun kimliği, bir sürüm numarası, `progress`,
`creating` (bir dosya yazılıyor), `files`, `calls`, `permission` (bekleyen soru: `wait`, araç,
argümanlar), `ended` ve `error`. Değişmez bir değer; her değişiklik sürümü bir artırır. `applied(snapshot,
piece)` turun bir parçasını — `Progress`, `FileStarted`, `FileWritten`, `ToolCall`, `PermissionWanted` —
görüntüye uygular. Sorunun `wait` kimliği, onu koyan değişikliğin sürüm numarasıdır: turun içinde tek,
artan, ve saf bir fonksiyonun üretebileceği bir değer. `Progress` buraya taşınır: onu doğuran turdur, ve
`stream_answer.py`'nin yerini alan modül turun kendisi değil, döngüsü.

### Döngü: `usecases/run_turn.py`

`stream_answer.py` `run_turn.py` olur (tasarım 3). İmza: `run_turn(chat_store, file_store, engine,
project_id, chat, now, control, mode)`.

- **Kayıt verilir, okunmaz:** `chat_store.get` yok; son cevap verilen kayda eklenip bir kez yazılır.
- **`control` (port `TurnControl`):** `stopped()`, `hold(cut)`, `decision()`. Stop ve izin artık bu tek
  nesnenin, yani o turun: anahtar sohbet değil.
- **İzin:** döngü `PermissionWanted`'ı verir, sonra `control.decision()` bekler — bir `Decision`, ya da
  Stop gelirse `None`. `Waiting`, `HEARTBEAT_SECONDS` ve `_waited_on`'ın saat döngüsü gider; sinyal
  köprünün işi.
- **Hiç temizlik yok:** `stops.clear` ve `permissions.clear` gider; her tur yeni bir nesne, bir öncekinin
  bıraktığı hiçbir şey ona ulaşmaz.
- Söyleyecek hiçbir şeyi olmayan tur (`EmptyMessage`) `EngineFailed(NOTHING)` olarak biter: bugün bu
  çeviri route'taydı.
- **Mod** bu maddede hâlâ istekle gelir ve parametre olarak kalır; sohbetin satırına ve
  `TurnControl`'e 463'te geçer.

### Canlı turlar: `data/live_turns.py`

`MemoryStops`, `MemoryPermissions` ve 458'in `memory_turns.py`'si gider; yerine iki sınıf:

- **`LiveTurns`** — sohbet → `LiveTurn` haritası, tek kilitle. `reserve(proje, sohbet)` boşsa yeni bir
  turu kimliğiyle koyar ve döner, doluysa `None` — bakmak ve almak tek adım (458'in `begin`'i).
  `release(proje, sohbet, tur)` yalnız o turu kaldırır: geç kalan bir bırakış sonraki turu silemez.
  `get`, `any_in(proje)` ve `start(proje, tur, kayıt, parçalar)`: `start` kaydı tura verir ve döngüyü
  **daemon** bir iş parçacığında koşturur; iş parçacığı her parçayı tura uygular, son kaydı alır,
  bitince — nasıl biterse bitsin — önce rezervasyonu bırakır, sonra turu bitmiş işaretler. Turun kendi
  kodunun hatası (`EngineFailed`, disk) log'a ve görüntünün `error`'ına yazılır.
- **`LiveTurn`** — bir tur sürdüğü sürece: kimliği; Stop bayrağı ve o anki isteğin kesmesi; bekleyen
  soru ve kararı; verilen kayıt; görüntü. Her alanı tek bir `Condition` altında değişir; her değişiklik
  `notify_all` eder — bekleyen karar da, dinleyen köprüler de aynı koşulda uyanır. `stop(tur)` ve
  `decide(tur, wait, …)` yalnız kimlikleri tutarsa bir şey yapar; `decision()` zaman sınırı olmadan
  bekler.

Neden daemon: izin bekleyen daemon olmayan bir iş parçacığı SIGTERM'de çıkışı sonsuza kadar bekletirdi
(tasarım 5). `projects.json`'ın yazıcısı daemon değil, öyle kalır: tur iş parçacığından tetiklense bile
`daemon=False` açıkça yazılı.

### Kurallar use case'lerde, route'lar yalnız çevirir

Turun kuralları — okumadan önce tutmak, her ret ve hatada bırakmak, yazılan sorunun turu başlatması,
sürümün, kırpmanın ve silmenin turu beklemesi — domain'de; route'lar sonucu ve hataları durum
kodlarına çevirir (CODE-STANDARD). Retler, buradaki öteki use case'ler gibi domain hataları
(`errors.py`: `ChatHeld`, `ChatFull`, `NothingToAnswer`, `VersionNotFound`, `ProjectAnswering`): böylece
bırakış tek yolda, `except` ile yapılır.

- **`usecases/advance_chat.py`** — mesaj, düzenleme ve Try again: sonuç `Started(turn, chat)` ya da
  `Nothing(chat_id)`; retler hata.
- **`usecases/hold_chat.py`** — `hold_chat(turns, proje, sohbet, iş)`: sohbeti işi bitene kadar tutar,
  tutulmuşsa `ChatHeld`. `trim_chat` ve yeni `open_version` (sürüm route'unun eski gövdesi) onu kullanır.
- **`delete_project`** `turns`'ü alır; projenin canlı turu varsa `ProjectAnswering`.
- **Port `LiveTurn`** (`TurnControl`'ün üstüne): isteklerin tura eriştiği taraf — `id`, `record`,
  `snapshot`, `changed_since`, `stop`, `decide`. `Turns`'ün `reserve` ve `get`'i onu döner.

### Route'lar

- **Mesaj (`POST …/messages`)**: önce `reserve` — okumadan önce; dolu ise 409 + `BUSY`, hiçbir şey
  okunmadan ve yazılmadan. Sonra sohbet bir kez okunur, tavan ve boş metin bugünkü gibi; metinli istek
  soruyu yazar (`append_message` artık sohbeti alır, okumaz), metinsiz istek Try again'dir. Başlayacak bir
  tur varsa `turns.start`, ve cevap köprü. Reddedilen her istek, ve başlamadan düşen her hata
  rezervasyonu bırakır.
- **Try again = `retry_turn`** (yeni use case; `drop_failed_answer.py` onun içine girer): `unanswered`
  → turu başlatır, hiçbir şey yazmadan; `failed` → başarısız cevabı çıkarıp tek yazmayla başlatır
  (Continue here'in işareti sorusuna geçer, 440'taki gibi); `answered`, `stopped`, `idle` → hiçbir şey.
  Soruyu hiç yazmaz. Canlı turdaki Try again rezervasyonda 409 alır. **"Hiçbir şey"in cevabı** bu
  maddede yalnız `chat` ve `done` karelerinden oluşan bir akış: ekran bugünkü gibi kaydı okur ve zaten
  yazılmış cevabı gösterir. Backlog'un *"Cevap zaten yazılmışken Try again döngüye giriyor"*u böyle
  kapanır — bugün 400 alıyor, kart duruyor ve cevap görünmüyordu.
- **Stop ve izin**: canlı turu bellekten bulur, diske gitmez; tur yoksa hiçbir şey yapmaz (sohbet
  `projects.json`'ın satırlarında yoksa 404, bugünkü gibi). Tarayıcı tur ve soru kimliğini 462'de
  taşıyacak; bu maddede route canlı turun kendi kimliğini ve o an bekleyen sorunun `wait`'ini verir.
- **Sohbeti okumak**: canlı bir turun kaydı varsa bellekten, diske gitmeden.
- **Sürüm ve Continue here**: işleri sürerken sohbeti `reserve` ile tutarlar, bitince bırakırlar —
  canlı tur varken 409. Kontrol ve yazma arasına bir tur giremez.
- **Proje silmek**: projenin canlı turu varsa 409.

### Köprü (geçici, 462'de gider)

POST'un cevabı `_sse(chat_id, turn)`: önce `chat` karesi (soru yazılmış; 449'un işareti), sonra turun
görüntüsünü dinler. Her uyanışta önceki görüntüyle yenisi arasındaki farkı bugünkü karelere çevirir:
`progress` değiştiyse `progress`; yeni dosyalar `file`; yeni adımlar `call`; ardından, bir dosya
yazılıyorsa ve bu yazış yeni ise — `creating` açıldıysa, ya da aynı farkta yeni bir dosya ya da adım
geldiyse — `file-start`; yeni bir soru `permission`; bitince `done`, ya da turun kendi hatası varsa
`error`. 15 saniye değişiklik olmazsa `: waiting` sinyali (tarayıcının ayrıştırıcısı onu atar).
Dinleyen yavaşsa birkaç değişiklik tek farkta gelir: ekran durumu çizdiği için aynı yere varır.
`file-start`'ın dosyalardan ve adımlardan sonra gelmesi bunun için: bir yazış biter bitmez sonraki
başladığında — aralarında disk yok — köprü ikisini tek uyanışta görür; ekranda `file` ve `call` kartı
indirir, ve sıradaki yazışın kartı onlardan sonra yeniden söylenmezse o yazış (Drive'da saniyeler)
kartsız geçer. Yalnız uyanıştan kısa süren bir yazış kartsız kalabilir; o an zaten bitmiştir.

## Maliyet

Sohbet dosyası işlemleri, R okuma W yazma. Her sohbet yazısı ayrıca `projects.json`'ın kuyruğuna bir
değişiklik bırakır (447): istek onu beklemez. Hepsi proje, sohbet ve dosya sayısından bağımsız, O(1);
bir yazının boyu O(sohbetin boyu). Adımlar diske hiç gitmez.

| İşlem | Bugün | 461 |
|---|---|---|
| Var olan sohbete mesaj (ya da düzenleme) | 4R + 2W | **1R + 2W** |
| Taslaktan ilk mesaj | 2R + 2W | **0R + 2W** |
| Try again, başarısız cevap | 3R + 2W | **1R + 2W** |
| Try again, cevapsız soru | 3R + 1W | **1R + 1W** |
| Try again, cevap zaten yazılmış | 1R, 400 | **1R + 0W**, `chat` + `done` |
| Tur sürerken mesaj / Try again / düzenleme | ikinci tur başlıyordu | **0, 409** |
| Stop, izin | 1R | **0** |
| Tur sürerken sohbeti okumak | 1R | **0** |
| Sürüm, Continue here | 1R + 1W | 1R + 1W; tur sürerken **0, 409** |
| Tur sürerken projeyi silmek | taşıyordu | **0, 409** |
| Köprünün sinyali | — | 0 |

Tarayıcının tur sonundaki okuması bugünkü gibi 1R; metinsiz Try again'in ilk karede yaptığı okuma artık
tur sürerken bellekten.

Bellek: canlı tur başına bir nesne ve bir iş parçacığı; izin bekleyen tur bir iş parçacığını park
eder (tasarım 5, kullanıcının kabulü).

## Kaybolan, bozulan

- **Sunucu yeniden başlarsa** tur ölür. Diskte soru ve turun yazdığı dosyalar durur; sohbet
  `unanswered` okunur ve Try again soruyu yeniden cevaplatır. Ölen turun adımları tutulmaz. Kapanışta
  yarıda kalan bir sohbet yazısı dosyayı bozmaz (geçici dosya + yerine koyma), yalnız bir `.writing`
  dosyası kalabilir.
- **Tur sürerken sohbet dosyasının tek yazarı turun iş parçacığı.** Son yazı verilen kayıttan kurulur;
  tur sürerken Drive'da o dosyaya elle yapılan bir değişiklik turun cevabıyla ezilir. FOUNDATION'ın 2.
  ilkesine bunu söyleyen cümle gerekiyor — kural dosyası olduğu için önerisi rapordadır, kullanıcıya
  gider.
- **Aynı anda iki istek:** `reserve` atomik; sekiz iş parçacığı aynı anda denese de biri alır. Stop ve
  izin tura bağlı: bitmiş bir turun nesnesine düşen bir basış sonraki turu bulamaz.
- **Kalan dar aralıklar** (462'de kapanır ya da bilerek bırakılır):
  1. Tarayıcı henüz kimlik taşımadığı için, yeni bir tur başladıktan sonra gelen eski bir Stop ya da
     Allow yeni turu bulur — bugün turlar arasında da buluyordu.
  2. Projeyi silmek ile aynı anda gelen bir mesaj arasında, kontrolden sonra rezervasyon alan istek
     silinen projenin klasörünü bir sohbet dosyasıyla yeniden açabilir — listede görünmez, çöpteki proje
     bütün kalır. Backlog'da, reviewer'ın çözüm önerisiyle.
  3. **Ara durumun boşluğu, 462 kapatır:** izin bekleyen bir turun tarayıcısı giderse tur sohbeti
     sunucu yeniden başlayana kadar tutar, ve bu maddenin ekranı onu bırakamaz — sayfa yenilenince izin
     kartı da Stop da gelmez (ikisi POST'un akışıyla geliyor), her yeni istek 409 alır. 462 kartı ve Stop'u
     sohbetin okunuşundan çizer. Bilerek kod eklenmedi: 462 sıradaki madde, ve dal o zamana kadar
     kimsenin kullanımında değil.
  4. Sürüm değiştirmek ve Continue here sohbeti yazarken tutar (okuma ile yazma arasına tur girmesin
     diye); o kısa aralıkta — bir okuma ve bir yazma — gelen mesaj *"this chat is still answering"*,
     proje silmek *"a chat in this project is still answering"* alır, oysa cevap veren yok. Tarafsız bir
     söz için `reserve`'ün kimin tuttuğunu söylemesi gerekirdi; iki satırı aşıyor, söz bırakıldı.
- **Hata log'a yazılır:** turun kendi kodunun hatası (bir araç, disk) artık tarayıcıya bağlı olmadan da
  görünsün diye; içinde anahtar yok — modelin hataları kara kutuda kalır, cevap olarak yazılır.

## Sınırlar

- Ekran değişmez; 409'un sözü bugünkü kartta görünür. Olay rotası, tarayıcının taşıdığı kimlikler, JSON
  cevaplar ve `useChat`'in yeniden yazılması 462; mod 463; servis daha cevap vermeden basılan Stop'un
  `MODEL_IDLE_SECONDS`'a kadar beklemesi 464.
- Canlı turdaki Try again bu maddede 409 alır (tasarımın tablosunda "yeniden bağlan"; köprü dönemi
  bitince 462'de).
- `status_of` bu maddede yalnız Try again'de okunur; sohbetin okunuşunda durum 462'de görünür.

## Yolda bulunanlar

- **Cevabın saati turun başladığı an** (`now` turu başlatan istekte alınır), cevabın yazıldığı an
  değil; 461'den önce de böyleydi. 462 / 463'te ele alınır.
- **Proje silme ile aynı anda gelen mesaj** (yukarıda, aralık 2): backlog'a yazıldı.
- `test_model_client.py`'deki bir yorum araç çağrılarını okuyanı `stream_answer` diye anıyordu; 440'tan
  beri kara kutu okuyor. Yeniden adlandırmayla birlikte düzeltildi.

## Testler

Önce test, kırmızı görülerek. Yeni: `test_turn.py` (`status_of` her durum için, açık hat, eski bir sohbet
dosyası, `applied`), `test_live_turns.py` (rezervasyon, sekiz iş parçacıklı bariyer — 458'den —, bırakış,
Stop ve kararın kimlik eşleşmesi, `decision`'ın Stop'la uyanması, iş parçacığının sırası: bitiş
söylendiği anda sohbet bırakılmış), `test_retry_turn.py` (her durumun Try again'i), `test_advance_chat.py`
(sahte turlarla: tutulmuş sohbet okunmadan ret, her ret ve hata bırakıyor, taslak doğacağı kimlikle
tutuluyor), `test_delete_project.py`'ye canlı turlu proje. Köprü: aynı uyanışta biten ve başlayan iki
yazış (`_told`'un birim testi), ve her yazışı köprü kartını söyleyene kadar bekleyen bir dosya
deposuyla iki dosyalı bir round — iki `file-start`. `test_stream_answer.py` `test_run_turn.py` olur: sahte
`control`'lerle, saat ve temizlik testleri gider. `test_chats_api.py`'ye: POST'un istemcisi gidince
süren tur; tur sürerken ikinci mesaj, Try again, düzenleme, sürüm, Continue here, proje silmek 409 ve
hiçbir şey yazmıyor; geç Stop ve erken Allow sonraki turu etkilemiyor; tarayıcısız bekleyen izin
sonradan cevaplanıyor; sohbet dosyası okuma/yazma sayıları (mesaj, Try again, Stop, izin, tur sürerken
okuma); köprünün sinyali. `test_stops.py` ve `test_permissions.py` modülleriyle gider.

## Bitti sayılır

Bir tur sürerken aynı sohbete gelen mesaj, düzenleme ve Try again 409 ve *"this chat is still answering
-- try again once it has finished"* alıyor ve hiçbir şey yazmıyor; iki tur hiçbir zaman aynı anda
koşmuyor; POST'un istemcisi gidince tur bitiyor ve cevabını yazıyor; geç bir Stop ya da Allow sonraki
turu etkilemiyor — turlar arasında gelen için şimdi, yeni tur başladıktan sonra gelen için 462'nin
taşıdığı kimliklerle (aralık 1); izin bekleyen tur tarayıcı olmadan bekliyor ve cevaplanınca sürüyor; POST 15 saniyede
bir sinyal atıyor, yani 100 saniyeden uzun düşünen bir model tünelde kesilmiyor; tur sürerken sürüm
değiştirmek, kırpmak ve projeyi silmek reddediliyor; mesaj bir okuma iki yazma; Try again yazılmış
cevapta cevabı gösteriyor; ekran bugünkü gibi; dört suite yeşil, frontend testleri değişmeden.
