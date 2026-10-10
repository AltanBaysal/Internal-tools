# Madde 462 · Ekran sunucunun durumunu çizer — tasarım

**Tarih:** 10 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
462 · **Dal:** `feat/queenagent-v10`, ana klasörde · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Kaynak:** mimarın sohbet tasarımı (`tmp/chat-turn-design.md`), 9. bölümün 3. adımı; 1, 3, 4, 5, 6 ve 7.
bölümlerin üstüne kurulu. **Öncesi:** [461](2026-10-10-queen-agent-m461-tur-kendi-basina-design.md) — turun
sunucuda kendi başına koşması; bu madde onun ara boşluklarını kapatır ve köprüsünü kaldırır.

## Ne, neden

**Bugün** (461'den sonra) tur sunucuda kendi iş parçacığında koşuyor, ama ekran onu yalnız POST'un
akışından biliyor: POST bir köprüyle eski kareleri veriyor. Bundan çıkanlar:

- Sayfa yenilenince süren tur, Stop ve bekleyen izin kartı gelmiyor; izin bekleyen bir tur sohbeti
  sunucu yeniden başlayana kadar tutuyor ve her istek 409 alıyor (461'in 3. aralığı).
- Stop ve izin tur kimliği taşımıyor: yeni bir tur başladıktan sonra gelen eski bir basış yeni turu
  buluyor (461'in 1. aralığı).
- Bağlantı koparsa *"network error"* kartı çıkıyor ve Try again gerekiyor; 449'un ilk-kare hilesi bu
  yüzden var.
- Tur sürerken reddedilen bir düzenleme sohbeti yenilenene kadar boş gösteriyor, ve ret konsola
  yakalanmamış hata olarak düşüyor (461'in QA'sı).
- Stop görünürken Enter gönderiyor ve sunucu "still answering" diye reddediyor.
- Durum kuralları tarayıcıda: `useChat.js`'teki owner / streamingInto / streamingChatId / live / held,
  thinking, creatingFile, createdFiles, streamingCalls, progress, permission durumları, retry ile
  answerAgain ayrımı.

**Olacak** (kullanıcı — *"chatin state'i direkt backend'de durur"*):

- Sohbeti okumak durumunu (`status`) ve süren turu (`turn`) da verir.
- Tarayıcı sohbeti dinler (`GET …/chats/<c>/events`, tarayıcının kendi `EventSource`'u): ilk karede
  turun güncel hâli, sonra her değişiklikte bütün hâli, 15 saniyede bir sinyal; tur bitince son kare
  ve akış kapanır. Bağlantı koparsa `EventSource` kendiliğinden yeniden bağlanır.
- Sayfa yenilenince süren tur, Stop ve bekleyen izin kartı sohbetin okunuşundan gelir; iki sekme aynı
  turu dinler.
- Try again'in kendi kapısı var (`POST …/chats/<c>/retry`): tur sürüyorsa yalnız yeniden bağlanır,
  cevapsız ya da başarısızsa döngüyü başlatır, soruyu hiç ikinci kez yazmaz.
- **Kullanıcının kararları:** cevapsız kalmış soru düz görünür, hata kartı yok *(kullanıcı — "cevapsız
  kalmış soru düz sorulsun, hata gibi görünmesin abi, şu anki tasarımdaki gibi")*; durdurulmuş cevapta
  Try again yok *(kullanıcı — "tabii ki olmasın, UI tasarımı değişmesine gerek yok burada")*; ekranın
  görünüşü değişmez.

## Nasıl

### Backend

**Sohbeti okumak — `domain/usecases/read_chat.py`** (yeni). `read_chat(turns, chat_store, proje,
sohbet)` → `(chat, snapshot)`. Tur varsa kayıt turdan, diske gitmeden (461); yoksa diskten. **Önce tur,
sonra kaydı okunur:** iki okuma arasında biten bir tur böylece son görüntüsüyle ve son kaydıyla eşleşir
— tarayıcı dinler ve sonu hemen duyar. Ters sıra, bitmiş bir turu cevaptan önceki kayıtla eşlerdi:
cevapsız görünen, dinlenecek bir şeyi de olmayan bir soru.

**Durum — `domain/turn.py`.** `status_of(chat, live)` değişmedi; canlı turda kaydın okunmadığı yazıldı
ve test edildi (olay kapısı ve Stop kayıtsız çağırır).

**Cevapların şekli — `presentation/routes.py`.**

- `_turn_json(snapshot)`: canlı tur için `{id, status, calls, files, creating, progress, permission:
  {wait, tool, arguments}}`, yoksa ya da bitmişse `null`. Her yerde aynı nesne.
- `_chat_state(chat, snapshot)`: sohbetin bugünkü JSON'u + `status` + `turn`.
- `GET …/chats/<c>`: `_chat_state`.
- `POST …/messages` (mesaj ve düzenleme): **202** + `_chat_state` (taslakta doğan sohbetin `id`'si
  içinde); tur sürerken **409** + `{error: BUSY}` ve `_chat_state` — sohbet, turun tuttuğu hâliyle,
  diske gitmeden (arkasında sohbet olmayan bir ad için yalnız `{error, turn}`); 400 / 404 bugünkü
  gibi. **Metinsiz istek artık
  boş mesajdır** (400 *"a message needs text"*): Try again'in kendi kapısı var, bir kapı tek anlam.
- `POST …/chats/<c>/retry` `{mode}`: başlattıysa **202**, başlatacak bir şey yoksa ya da tur sürüyorsa
  **200** — ikisi de `_chat_state`. Dolu sohbet 400, olmayan sohbet 404 *"chat not found"*, olmayan
  proje 404 *"project not found"* — mesaj kapısının sözü; hangisinin olmadığını bellekteki liste söyler.
  Mod 463'e kadar istekle gelir.
- `POST …/chats/<c>/stop` `{turn}` ve `POST …/chats/<c>/permission` `{turn, wait, allowed, reason}`:
  kimlikler canlı tura ve bekleyen soruya uymazsa hiçbir şey yapmaz; cevap `{turn}` — basıştan sonraki
  tur, diske gitmeden. Tur yoksa `{turn: null}` (sohbet listede yoksa 404, bugünkü gibi).
- `GET …/chats/<c>/events`: `_listened(live)` — tur yoksa tek kare `{turn: null}` ve kapanır; varsa
  ilk karede görüntü, her değişiklikte bütün görüntü, 15 saniye değişiklik yoksa `: beat` yorum satırı,
  tur bitince `{turn: null}` — turun kendi kodu bozulduysa `{turn: null, error}` — ve kapanır. Karelerin
  olay adı yok (EventSource'un `onmessage`'ı), olay kaydı ve olay kimliği yok. Başlıklar
  `Cache-Control: no-cache`, `X-Accel-Buffering: no`. Tur, istek gelir gelmez bulunur (akışın içinde
  değil): dinlenen tur, istek anında koşan turdur. Sohbet okunmaz.
- Köprü (`_sse`, `_told`'un eski hâli ve kare adları) gider.

**Tasarımdan ayrılış (ana agent'ın onayıyla):** tasarım mesajın, düzenlemenin ve Try again'in cevabını
`{status, mode, turn}` diye çiziyordu. Bunlar `GET`'in şeklini döner — kayıt + `status` + `turn`. Neden:
POST cevap verince iyimser baloncuk sunucunun kaydına geçmeli, başarısız cevabın Try again'i düşürülen
cevabı ekrandan almalı, zaten yazılmış cevaptaki Try again cevabı göstermeli; yalnız durumla her biri
POST'tan hemen sonra bir `GET` isterdi (her seferinde bir gidiş-dönüş daha, "nothing" yolunda bir disk
okuması). Kayıt zaten elde: 0 fazladan disk, 0 fazladan gidiş-dönüş, ve ön yüz tek şekil tanır. Bedeli
202'nin gövdesi O(sohbet) — yerine geçtiği `GET`'in gövdesi kadar. 409 da sohbeti döner (QA'nın
bulduğu: geride kalmış bir sekme turu izliyordu, ama kendi eski kaydının altında — öbür sekmenin sorusu
yok, bekleyişin saati yok); tur sürerken kayıt turda, 0 disk. Stop ve izin `{turn}` döner: durumu tur
olmadan bilmek sohbeti okumak olurdu.

**`mode` alanı yok:** sunucuda henüz mod yok (463). `lastMode`, Try again'in mod argümanı ve Allow'un
Edit'e geçirmesi `App.jsx`'te her biri tek yerde duruyor; 463 onları taşır.

**Bulunan iş — `data/live_turns.py` (461'in kodu, ana agent'ın onayıyla):** `hold_chat`'in tuttuğu tur
(sürüm, Continue here) ve tutulduktan sonra reddedilen bir mesaj (dolu sohbet, okuma hatası) turu
bırakıyor ama hiç `end()` çağırmıyordu. O anda abone olan bir dinleyici (tam o anda yenilenen sayfa)
sonsuza kadar beklerdi. Şimdi `release(proje, sohbet, tur, error="")` bırakır ve **sonra** o turu
bitirir; `end` bir kez işler; iş parçacığının `finally`'si `release(…, error)` çağırır — "önce bırak,
sonra söyle" sırası korunur. Port `Turns.release` belgesi buna göre.

**Cevabın saati — `run_turn`, `advance_chat`:** `now` değeri yerine `clock` fonksiyonu. Soru
`advance_chat`'te `clock()` anında, cevap `run_turn`'ün son yazısında `clock()` anında damgalanır: dakikalar
süren bir turun cevabı artık başladığı anı göstermiyor. Route `_now`'ı verir.

**`advance_chat`'in `Nothing`'i** kaydı taşır (`Nothing(chat)`): Try again cevabı göstermek için onu
yeniden okumaz.

### Frontend

**`features/workspace/useChat.js` yeniden yazıldı.** Hook sunucunun söylediğini tutar: `chat` (kapının
ya da okumanın verdiği hâliyle). Sunucunun `status`'u ve turun `status`'u cevaplarda durur ama ön yüz
onları okumaz ve güncel tutmaz: çizdiği her şey kayıttan ve `turn`'den. Kendine ait yalnız yazılmakta
olan şeyler: yolda olan cümle (`pending` — kapı cevap verene kadar), az önce cevaplanmış sorunun kimliği
(`decided` — kart sunucunun karesini beklemeden iner, görünüş bugünkü gibi; istek sunucuya ulaşmazsa
kart geri gelir), cümle yoldayken basılmış Stop (`early`), `refused`/`error` kartları ve doğan sohbetin
adresi için `onChatBorn`.

- **Dinleme:** her tur için bir `EventSource` (anahtar: proje / sohbet / tur). Ekrandaki sohbetin canlı
  turu varsa ekran onu dinler ve sohbetten çıkınca kapatır. **Hook'un kendi başlattığı tur** (mesaj, Try
  again) akışını, ekran nerede olursa olsun tur bitene kadar açık tutar: 452'nin `onTurnEnd`'i —
  dosyalar ve kenar çubuğu — böylece hâlâ çalışır. İki dinleme aynı turu bulursa tek akış kullanılır.
- **Kare:** `{turn}` ekrandaki sohbetin `turn`'ünü değiştirir; dosya sayısı arttıysa `onFileCreated`
  (her ekran için). `{turn: null}` ya da başka bir turun kimliği: akış kapanır, kendi turuysa
  `onTurnEnd`, ekran o sohbetteyse kayıt okunur, cevap belirerek gelir (214); `error` varsa kart onun
  sözüyle. Kayıt okunana kadar bekleyiş durur, cevap gelmeden boşluk olmaz.
- **Kopma:** `EventSource` `CONNECTING`'e düşerse kendisi bağlanır, kart yok; ilk karesi turun güncel
  hâli. `CLOSED`'a düşerse (tünelin 502'si ya da 524'ü gibi bir ret — EventSource sebebini söylemez):
  - **Akış daha önce kare vermişse** okumadan, ekranda da ekran dışında da, yeniden açılır: kapının ilk
    karesi turun sürüp sürmediğini diske gitmeden söyler, `{turn: null}` her son gibi biter (kendi
    turuysa `onTurnEnd`).
  - **Hiç kare vermemişse ve ekran o sohbetteyse** sohbet bir kez okunur. Okuma başarısızsa bugünkü
    kart okumanın sözüyle. Tur bitmişse kayıt çizilir. Tur hâlâ sürüyorsa olay kapısı bir kez elle
    sorulur (`shared/api.js`'in `reach`'i, gövdesi okunmadan): ret ise kart sunucunun kendi sözüyle
    (`failureFrom`), Try again'i retry kapısı — turu geri verir ve yeniden dinletir; cevap verirse bir
    kez daha dinlenir, o da kare vermeden reddedilirse kapı ikinci kez sorulmaz, kart *"the browser
    closed this answer's stream"* der — ağda sebep yok, söz yalnız olanı söyler.
  - **Bu kart bekleyişin yerini alır**, başarısız cevabın kartı gibi: duyulamayan bir tur tur gibi
    çizilmez — üstünde donmuş üç nokta, şerit, Stop ya da kesik çizgili dosya kartı kalmaz, tur görmeden
    bitmiş olsa da. Try again canlı görünümü geri getirir.
  - **Hiç kare vermemişse ve ekran başka yerdeyse**, kendi turuysa `onTurnEnd` bir kez burada çağrılır:
    sonu duyulmayacak, ve tazelediği listeler bellekten okunur.
- **Gönderme:** baloncuk hemen çizilir (düzenlemede eski mesajın yerinde). 202 gelince kapının verdiği
  kayıt çizilir ve tur dinlenir; doğan sohbet için `onChatBorn`. Ret (400, ağ): kayıt dokunulmadan
  sunucununki kalır, yalnız baloncuk gider. 409: cevabın taşıdığı sohbet — turun tuttuğu hâli, geride
  kalmış bir sekmenin görmediği soru dahil — çizilir ve ekran o turu izler. İkisinde de cümle kutuya
  döner (yanıt) ya da düzenleme alanına döner (düzenleme); sunucunun sözü kartta.
- **Try again:** iki kartın düğmesi de retry kapısı; yalnız reddedilmiş bir yanıtın kartı kutuyu
  gönderir (Madde 349, tek sahip). Kapının cevabı kayıttır: başarısız cevap düğmeye basılınca değil,
  kapı cevap verince gider.
- **Stop ve izin** turun kimliğini, izin ayrıca sorunun `wait`'ini taşır. Bekleyiş ve Stop cümle yola
  çıkar çıkmaz durur, bugünkü gibi; kapı daha cevap vermeden basılan Stop o gönderim için saklanır ve
  kapı turu adlandırınca onun kimliğiyle gider; reddedilen gönderimle birlikte düşer.
- **Sekmeye dönmek** (`focus` ya da `visibilitychange`): sohbet bir kez okunur — o sohbetteki bir turu
  zaten bir akış izlemiyorsa ve yolda bir cümle yoksa; okuma dönünce aynı şey yeniden sorulur, böylece
  bakış sürerken cevaplanmış bir gönderimin daha yeni kaydını ezmez. Okuma bir tur gösterirse ekranın
  dinleme etkisi onu dinler. Başarısız bir bakış hiçbir şey söylemez, ekran olduğu gibi kalır.
- Ekrana giden adlar aynı (`thinking`, `creatingFile`, `createdFiles`, `streamingCalls`, `progress`,
  `permission`), ama artık `chat.turn`'den ve yoldaki cümleden türetiliyor.

**`ChatScreen.jsx`:** reddedilen düzenleme cümlesiyle kendi alanına döner (bugün yakalanmayan ret).
Bekleyişin saati açık hattın son mesajından, yani cevaplanan sorudan okunur — yoldaki cümle ya da turdan
önce yazılmış soru: yenilemeden sonra da sorunun soruldu anı, maliyetsiz. Taslakta kapı cevap verene
kadar baloncuk çizilmez; orada saat cümlenin yola çıktığı an (hook'un `sentAt`'i). Bugünkü `askedAt`
durumu ve etkisi gitti.

**`Composer.jsx`:** Stop görünürken Enter hiçbir şey göndermez, cümle kutuda kalır; durdurmak bir basış
olarak kalır.

**`shared/failure.js`:** reddin gövdesi `failure.body` olarak taşınır (409'un sohbeti için).
**`shared/api.js`:** `reach(path)` — bir kapının cevap verip vermediği, gövdesi okunmadan; ret
`failureFrom`'la. İstekler yine tek yerden çıkar.

**Gidenler:** `shared/sse.js` ve testi (POST okuyucusu); 449'un ilk-kare hilesi (`reached`, ilk karede
yeniden okuma); owner / streamingInto / streamingChatId / live; akış durumları;
`features/workspace/chatTitle.js` ve testi — taslak için ayağa kaldırılan kayıt artık yok (yeni sohbetin
kaydı kapının cevabı, sunucunun verdiği adla), böylece sunucunun ad kuralının tarayıcıdaki kopyası da
gitti (FOUNDATION, Karar 4).

## Maliyet

Sohbet dosyası işlemleri, R okuma W yazma; tarayıcının okumaları ayrı yazılı. Her sohbet yazısı ayrıca
`projects.json`'ın kuyruğuna bir değişiklik bırakır (447). Hepsi proje, sohbet ve dosya sayısından
bağımsız, O(1); bir yazının boyu O(sohbetin boyu). Adımlar diske hiç gitmez.

| İşlem | 461 | 462 |
|---|---|---|
| Var olan sohbete mesaj (ya da düzenleme) | 1R + 2W; tarayıcı sonda 1R | **1R + 2W**; kapının cevabı kayıt (0 ek); tarayıcı sonda 1R |
| Taslaktan ilk mesaj | 0R + 2W; sonda 1R | **0R + 2W**; sonda 1R |
| Try again, başarısız cevap | 1R + 2W; ilk karede GET (bellekten) + sonda 1R | **1R + 2W**; cevap kayıt; sonda 1R |
| Try again, cevapsız soru | 1R + 1W; sonda 1R | **1R + 1W**; sonda 1R |
| Try again, cevap zaten yazılmış ya da durdurulmuş | 1R; ardından tarayıcı 1R | **1R**, cevap kayıt; ek okuma yok |
| Try again, tur sürerken (yeniden bağlanmak) | 0, 409 | **0**, 200 + kayıt (bellekten) |
| Mesaj ya da düzenleme, tur sürerken | 0, 409 | **0**, 409 + kayıt (bellekten); sürüm ya da Continue here tutarken gelirse kayıt diskten, 1R |
| Stop, izin | 0 | **0** |
| Olay kapısına abone olmak, sinyal, kare | — | **0** |
| Tur sürerken sayfayı yenilemek | GET 0 (tur görünmüyordu) | **GET 0 + abonelik 0** |
| Turun sonu, ekran başka sohbetteyken | sonda 1R | **0** (dönüşteki açılış okuması zaten 1R) |
| Akış reddedilince (CLOSED), önce kare vermişse | — | **0**: okumadan yeniden açılır |
| Akış reddedilince, hiç kare vermemişse (ekranda) | — | bir GET (tur sürüyorsa 0, bittiyse 1R) + tur sürüyorsa olay kapısına bir elle soru (0) |
| Sekmeye dönmek | — | bir GET: tur yoksa 1R, başka sekmenin turu sürüyorsa 0; bir akış zaten izliyorsa hiçbiri; uzaktayken bağlantı yok |
| Sürüm, Continue here | 1R + 1W; tur sürerken 0, 409 | aynı |

Ağ: bir mesaj bir POST + bir uzun bağlantı (olay akışı) + sonda bir GET — 461'deki uzun POST + GET ile
aynı sayı. Kare başına bütün görüntü: bir adım ~80 B; 30 adımlı bir turun son karesi ~3 KB, bütün tur
O(adım²) bayt — 100 adımda birkaç yüz KB, bir kerelik. 202'nin gövdesi O(sohbet), yerine geçtiği GET
kadar.

Sunucu: dinleyen her bağlantı, tur sürdüğü sürece bir iş parçacığı tutar (koşulda en çok 15 sn bekler).

## Kaybolan, bozulan

- **Giden dinleyici** turu bitirmez: akışın bir sonraki yazışında (en geç 15 sn) kapanır, iş parçacığı
  serbest kalır, tur sürer.
- **Sunucu yeniden başlarsa** tur ölür; açık `EventSource`'lar yeniden bağlanınca `{turn: null}` alır,
  kapanır, sohbet bir kez okunur: cevapsız soru düz durur.
- **Yeniden bağlanma fırtınası:** `CONNECTING` kopmaları tarayıcının kendi aralığıyla (~3 sn) dener,
  akış başına tek bağlantı. Ret (`CLOSED`): işlemiş bir akış okumadan yeniden açılır — bir döngü için
  her seferinde bir kare gerekir, yani çalışan bir akış. Hiç işlememiş akışta kapı bir kez elle sorulur
  ve en fazla bir kez daha dinlenir; ondan sonra kart.
- **HTTP/1.1'de köken başına altı bağlantı** (localhost): her açık `EventSource` birini tutar — ekranın
  akışı ve bu sekmenin başlatıp hâlâ süren her turu. Aynı anda çok sohbette tur başlatıp başka sekmeler
  de açılırsa diğer istekler sıraya girebilir. Kod eklenmedi: sıradan kullanımda bir iki akış. Tünel
  tarayıcıya HTTP/2 verir, orada sınır yok — denenmedi.
- **trycloudflare üstünden `EventSource` denenmedi.** Tasarımın söylediği yapıldı: `text/event-stream`,
  `Cache-Control: no-cache`, `X-Accel-Buffering: no`, 15 saniyelik sinyal (tünelin ~100 sn'lik boşta
  kesmesine karşı). Gerçek werkzeug sunucusunda, sahte yavaş bir motorla denendi (`tmp/m462/serve.py`):
  kareler anında, sinyaller aralıkla, son kare ve kayıt doğru. Colab'da denemek kullanıcının roadmap
  testinde.
- **İş parçacıkları:** turun alanları tek koşul altında (461); yeni kapılar yalnız okur ya da 461'in
  kimlikli `stop`/`decide`'ını çağırır. `release`'in sonundaki `end` koşulun içinde, kilit tutulurken
  başkasının kodu çağrılmaz.
- **Ekran dışında reddedilen kendi akışı:** işlemişse yeniden açılır ve sonu duyulur; hiç işlememişse
  `onTurnEnd` ret anında bir kez çağrılır — tur o an hâlâ sürüyorsa, sonunda yazdığı dosyalar listeye bir
  sonraki tur sonunda, Refresh'te ya da All projects'e girişte gelir.

## Sınırlar

- **Cevapsız kalmış sorunun Try again'i yok** (kullanıcının kararından): sunucunun yeniden başlamasıyla
  cevapsız kalan bir soru ancak düzenlenerek ya da yeni bir mesajla cevaplatılabilir. Turun kendi kodu
  bozulursa, o sırada dinleyen sekme kartı turun sözüyle ve Try again'le görür; yenileyince düz soru.
  Ana agent bunu roadmap testinde kullanıcıya soracak.
- **Boşta duran ikinci sekme** *(kullanıcı, 10 Ekim — önerilen yol, "hepsi için önerdiğini yap sıkıntı yok")*: olay kapısı yalnız
  canlı bir turu dinletir. B sekmesi sohbette boştayken A sekmesi mesaj gönderirse, B'ye dönüldüğünde —
  sekmeler arasında geçilince ya da yandaki pencereye tıklanınca — B sohbeti bir kez okur, turu görür ve
  dinler. **Kapsamadığı:** A'nın yanında görünür duran ama hiç odak almayan bir B, odak alana kadar turu
  görmez; B o sırada gönderirse 409 alır ve turu izler.
- **Mod 463'te**, gönderme anahtarı (tasarımın 5. adımı) backlog'da, model daha konuşmadan basılan
  Stop'un beklemesi 464'te.
- **461'in 4. aralığı kaldı:** sürüm ya da Continue here yazarken gelen mesaj BUSY sözünü alır; o kısa
  aralıkta (1R + 1W) sohbeti okuyan biri onu süren bir tur gibi görür, ve tutuş bitince son kareyle
  düzelir.
- Ekranın görünüşü değişmez.

## Yolda bulunanlar

- `release`'in turu bitirmemesi (yukarıda, düzeltildi).
- `chatTitle.js`: tarayıcıdaki sunucu kuralı kopyası, bu maddeyle kullanılmaz oldu ve silindi.
- CODE-STANDARD'ın Frontend bölümü `shared/`'ı "the two request roads" diye anlatıyor; POST okuyucusu
  gidince tek yol kaldı — öneri raporda.

## Testler

Önce test, kırmızı görülerek. Backend: `test_live_turns.py` (bırakış turu bitirir; `end` bir kez),
`test_run_turn.py` (cevap yazıldığı an damgalanır), `test_advance_chat.py` (`clock`, `Nothing` kaydı
taşır), `test_read_chat.py` (yeni: tur yoksa disk, tur varsa bellek, önce tur sonra kayıt), `test_turn.py`
(canlı turda kayıtsız durum), `test_chats_api.py` yeniden yazıldı — GET'in her durum için `status` ve
`turn`'ü, süren ve bekleyen turda; olay kapısının ilk karesi, her değişikliğe bir kare (bütün görüntü),
sinyal, sonda `{turn: null}`, turun kendi hatası, boşta `{turn: null}`, iki dinleyici, sürüm tutuşunu
dinleyen; mesaj ve düzenleme 202 ve 409 + tur, 409'un turun tuttuğu sohbeti diske gitmeden vermesi;
olmayan projede Try again'in *"project not found"*'u; Try again'in her durumu ve tur sürerken yeniden bağlanma;
Stop ve iznin eski kimliklerle hiçbir şey yapmaması; okuma/yazma sayıları (dinlemek, tur sürerken Try
again ve okumak 0). `test_pin_archive.py`, `test_last_activity.py` turun sonunu olay kapısından bekler.
Frontend: `useChat.test.jsx` (yeni: tur sürerken yenileme, izin beklerken yenileme ve kimlikli cevap,
ulaşmayan cevapta kartın geri gelmesi, Stop'un kimliği, kopmanın kartsız onarılması, kare vermeden
reddedilen akışta kapının elle sorulup kartın sunucunun sözüyle çıkması, cevap veren kapının bir kez daha
dinlenip ikinci kez sorulmaması, işlemiş akışın okumadan yeniden açılması, bitmiş turda kaydın çizilmesi,
okumanın sözüyle kart, iyimser baloncuğun kayda geçmesi, kapıdan önce basılan Stop'un turun kimliğiyle
gitmesi ve reddedilen gönderimle düşmesi, taslağın doğması, tur sürerken reddedilen düzenlemenin sohbeti
bütün bırakması, ekran dışında `onTurnEnd` — işleyen ve hiç işlemeyen akışla —, ekranın açtığı akışın
kapanması, dosyanın bir kez duyurulması, turun kendi hatası, cevapsız sorunun kartsız çizilmesi, Try
again kapısı, sekmeye dönünce okunan ve dinlenen tur, başka sekmenin turuna reddedilen gönderimde
409'un sohbetinin çizilmesi, reddedilen akışın kartının bekleyişin yerini alması ve Try again'le canlı
görünümün dönmesi), `Composer.test.jsx` (Stop görünürken Enter),
`ChatScreen.test.jsx` (reddedilen düzenlemenin alana dönmesi, bekleyişin saatinin sorudan gelmesi),
`api.test.js` (`failure.body`, `reach`), `App.test.jsx` — akış testleri
yeni protokolle, ve yeni: cevapsız soru kartsız, durdurulmuş cevapta Try again yok, tur sürerken ve izin
beklerken yenileme. `test-setup.js`'e testin konuşturduğu sahte bir `EventSource`.

## Bitti sayılır

Sohbetin okunuşu `status` ve `turn` veriyor; olay kapısı ilk karede güncel hâli, her değişiklikte bütün
hâli, 15 saniyede bir sinyali veriyor ve tur bitince kapanıyor; tarayıcı kopan bağlantıya kendiliğinden
yeniden bağlanıyor; sayfa yenilenince süren tur, Stop ve bekleyen izin kartı ekranda; iki sekme aynı turu
dinliyor, boşta duran sekme dönülünce turu görüyor; kare vermeden reddedilen bir akış sonsuz bekleyiş
değil, sunucunun sözüyle bir kart bırakıyor; Stop ve izin tur ve soru kimliği taşıyor, eski bir basış hiçbir şey yapmıyor; Try again tur
sürerken yalnız yeniden bağlanıyor, cevapsız ya da başarısızsa döngüyü başlatıyor, soruyu hiç ikinci kez
yazmıyor; tur sürerken reddedilen mesaj ya da düzenleme sohbeti olduğu gibi bırakıyor ve cümleyi geri
veriyor; Stop görünürken Enter göndermiyor; cevapsız soru düz, durdurulmuş cevapta Try again yok; ekranın
görünüşü bugünkü gibi; köprü, `sse.js` ve 449'un hilesi yok; dört suite yeşil, `dist` yeniden kurulmuş.

## Kural dosyaları için öneriler (kullanıcıya gider)

- **CODE-STANDARD, Stack:** *"Live progress is server-sent events, not websockets — the stream is
  one-way and short-lived."* yerine: *"Live progress is server-sent events, not websockets: the stream
  is one-way. Every command is a plain request answered with JSON, and the browser listens to a chat's
  running turn on its own stream, `GET …/chats/<c>/events` — the turn's whole snapshot first and on every
  change, a beat every 15 seconds so a tunnel never sees it idle, and an end when the turn ends.
  EventSource reconnects by itself, so a dropped connection needs nothing from the screen."*
- **CODE-STANDARD, Frontend:** *"the two request roads"* → *"the one request road"*.
- **FOUNDATION, 2. ilke:** 461'in taslağı ("a running turn lives in memory, a restart ends it"; tur
  sürerken sohbet dosyasına elle yapılan değişikliğin ezilmesi) — ana agent'ta.
