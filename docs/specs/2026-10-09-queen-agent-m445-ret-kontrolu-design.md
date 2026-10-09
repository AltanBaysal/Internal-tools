# Madde 445 · Ret kontrolü — tasarım

**Tarih:** 9 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
445 (eski adı v10-1b) · **Dal:** `feat/queenagent-v10`, ana klasörde, **commit'lenmeden** — kontrolün
metni modele gider, kullanıcı onu VS Code'un Changes'inde okur ve onayıyla commit'lenir · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Tasarım:** `queen-design`'ın `queen-agent-v4` dalı, maddeler 216 ve 221 —
`projects/queen-agent/BEHAVIOUR.md`'nin *The failed answer* bölümü, `chat/` sayfasının
`turn=model-refused` anı, `messages/`'ın beş retli tohum sohbeti (`c1b8e4a7d02f6`), `data.js`'in
`REFUSED_SAID`'i ve `shell.js`'in `message`'ı · **Öncesi:** [440](2026-10-09-queen-agent-m440-kara-kutu-design.md),
kutu.

## Ne, neden

Kullanıcı, 5 Ekim: *"Deepseek kontrol katmanı ekle cevaba bak red ise tekrar gönder"*. 440 kutuyu
kurdu: hata ve boş cevap yeniden gidiyor, beşi de olmazsa teknik hatanın kartı. 445 kutunun ikinci
yarısı: **sözlü bir cevap, döndürülmeden önce DeepSeek'e kontrol ettirilir**; ret ise asıl istek aynen
yeniden gider.

Bugün `black_box.ask` sözlü cevabı olduğu gibi döndürüyor, ve yerinde bir yorum kontrolün nereye
geleceğini söylüyor. Model reddederse ret sohbete cevap olarak yazılıyor. 440'ın reviewer'ı iki şeyin
445'te değişeceğini not etti: başarısızlık yalnız metin olarak tutuluyor ve dönüş hep teknik — oysa
*"son deneme karar verir"* her denemenin türünü bilmeyi istiyor; ve `text.strip() or calls` testi
ikiye ayrılıyor: çağrılar kontrolsüz geçer, sözler kontrol edilir.

## Olacak

### 1 · Kontrolün metni — `domain/prompt.py`

QueenAgent'ın modele söylediği her metin `prompt.py`'de (Madde 189), ve bu da onlardan biri: `CHECK`,
yanında `APPROVED` — kontrolün onay için yazacağı tek kelime, ve kutunun aradığı kelime. Metin
bu modülün öbür metinleri gibi yazılır: parantez içinde satır satır dizeler, altında neden öyle
olduğunu söyleyen bir belge dizesi; biçimi beceri metinlerinin *Context / Rules* düzeni.

Metin queen-editor'ün `CHECK_INSTRUCTION`'ıyla kelimesi kelimesine aynı *(kullanıcı, 9 Ekim — "konrol
metni queen editordekini kullansın aynısı")*. Kopyalanır, paylaşılmaz: ikisini hiçbir şey bağlamaz,
hiçbir test ikisini karşılaştırmaz *(kullanıcı, 8 Ekim — "bunalr tammaen ayrı bir proje")*; birinde
değişen öbüründe elle değişir. İlk yazımda QueenAgent'a özgü bir satır vardı — soru sormak, ne
yapıldığını söylemek ve aranan şeyin olmadığını söylemek ret değildir —; kullanıcı onu almadı.

Kontrol yalnız cevabı görür, birebir; isteği, konuşmayı, araçları görmez. Cevabın iyi, doğru ya da
izinli olup olmadığına bakmaz — yalnız ret mi değil mi. Yetişkin içerik ret değildir.

### 2 · Kontrolün yolu — `Engine.stream_alone`

`Engine`'in `stream`'i her isteğin önüne QueenAgent'ın system prompt'unu ve sahibin ekini koyuyor
(`model_engine.py`'nin `_for_model`'ı). Kontrol o sayfanın önünde gitmemeli: araçlar, dosyalar ve
sohbetler üstüne bir sayfa, işi tek kelime olan bir modelin önünde — Madde 175'in `write_once`'ı da
bu yüzden `_for_model`'dan geçmiyordu.

Port'a ikinci bir yol: `stream_alone(system, text, on_open=None)` — bir talimat ve bir metin, kendi
isteklerinde: QueenAgent'ın system prompt'u yok, konuşma yok, araç yok. `stream` gibi parça parça
cevaplar, ve kutu onu aynı `_read`'le okur. `ModelEngine` onu varsayılan modelin client'ının
`stream`'inden geçirir: `[{"role": "system", "content": system}, {"role": "user", "content": text}]`.

- **Neden akış:** Stop kontrolü de kesmeli, bir istek gibi. Kesme yolu (`on_open`) yalnız akışta var;
  akışsız bir yol Stop'un kesemediği bir istek olurdu.
- **Neden ayrı bir yol, `stream`'e bir parametre değil:** test sahteleri `stream`'i senaryoyla
  cevaplıyor; kontrol aynı kapıdan gelseydi her sahte iki tür isteği ayırmak zorunda kalırdı, ve
  senaryolarının cevapları kontrole gidebilirdi. Ayrı yolda bir sahte kontrolü tek satırla onaylar.
- `client.py` değişmez: ona yalnız bir mesaj listesi gidiyor.

### 3 · Kutu — `domain/black_box.py`

Bir deneme: istek, ve cevap sözlüyse onun kontrolü. Beş deneme (`TRIES`) ikisini birlikte sayar.

- **Araç çağrısı kontrolsüz geçer** *(yol haritası)*, yanındaki sözlerle: o bir şey istiyor,
  cevaplamıyor; sözler de agent'ın isterken söyledikleri.
- **Sözsüz cevap kontrol edilmez:** kontrol edecek söz yok. Boşsa 440'taki gibi yeniden denenir;
  çağıran sessizliği cevap saydıysa (`silence_is_an_answer`, Madde 38) olduğu gibi döner.
- **Sözlü cevap kontrol edilir:** `engine.stream_alone(CHECK, answer.text, on_open)`. Sözler birebir
  gider — kırpılmaz, eklenmez. Kontrolün sözü boşluklarından arınınca tam `APPROVED` ise cevap döner.
  **Başka her şey onaylamamıştır** — `REFUSAL`, boş, başka bir kelime, bir açıklama: tek kelime bir
  kapı, ve onu söylemeyen kontrol hiçbir şeyi onaylamamış sayılır. Ret, aynı isteğin aynen yeniden
  gitmesi demek.
- **Kontrolün kendi hatası** — fırlattığı her şey — bir deneme gibi teknik hatadır, sözü kendi sözü.
- **Her başarısız denemede `stopped()` sorulur** — hata, boş cevap, ret: Stop hiçbir zaman yeniden
  denenmez. Kontrol sürerken Stop'a basılırsa kesme yolu onun bağlantısını keser (`on_open`, 440'taki
  `stops.hold`), kontrol hata verir, kutu boş bir `Answer()` döner.
- **Son deneme karar verir:** kutu her denemenin sonucunu bir `Answer` olarak tutar — tür ve söz
  birlikte — ve beşinden sonra sonuncuyu döner. Ret: `Answer(text=REFUSED_SAID, failed=REFUSED)`;
  teknik: `Answer(text=<hatanın sözü ya da NOTHING>, failed=TECHNICAL)`. Bu, 440'ın reviewer'ının
  notu: tür artık metinle birlikte, deneme başına.
- **Yeni adlar:** `REFUSED = "refused"` (tür, `TECHNICAL`'ın yanında) ve `REFUSED_SAID = "The model
  returned an error. Try asking another way."` (tasarımın `data.REFUSED_SAID`'i, sözcüğü sözcüğüne).
  `NOTHING` gibi kutuda dururlar: modele gitmez, kayda ve ekrana giderler.
- **Kontrolün bedeli sayılmaz:** cevabın `usage`'ı cevabın isteğinin. 440'ta da yeniden denenen
  denemelerin harcadığı sayılmıyor; kontrol kısa bir istek, ve damga cevabın ne gönderdiğini söylüyor.

### 4 · Döngü ve kayıt

Değişmez, yalnız yorumlar. `stream_answer` başarısız cevabı türüne bakmadan yazıyor
(`failed=failure.failed`, `text=failure.text`); `chat.py` başarısız cevabı türüne bakmadan
göndermiyor ve tartmıyor (`sent_messages`, `_size`); `file_chat_store` alanı türüne bakmadan yazıp
okuyor. Yani retli cevap kayda `failed: "refused"` ve ret mesajıyla geçer, yenileyince durur, modele
gitmez, doluluğa sayılmaz. Bunu tutan testler yazılır; kod yazılmaz.

Try again'in sunucu tarafı (`drop_failed_answer`) da türüne bakmıyor; ekran ret için düğme
göstermediği için oraya ulaşılmaz, ve değişmez.

### 5 · Ekran — `ChatScreen.jsx` *(tasarım 216 ve 221)*

Retli cevap düz cevap yazısıdır (tasarımın `shell.js`'i: kart yalnız `"technical"`):

- Sözleri `msg__text`'te, her cevap gibi Markdown'la; kart yok, Try again yok.
- Kutusu `msg--failed` sınıfını taşır, tasarımdaki gibi (`said.failed` doluysa); bu sınıfın tek kuralı
  kartı (`.failure`) gerdiriyor, yani düz yazıya bir şey yapmaz.
- **Damgası yalnız saat:** tasarımda başarısız cevabın `usage`'ı sıfır; burada kayıt biten turların
  harcadığını tutuyor (440), ve ekran onu durmuş cevaptaki gibi çizmez.
- Az önce geldiyse sözleri her cevap gibi 200 ms'de belirir (`msg--arrived`) — bugünkü kod bunu zaten
  yapıyor.

## Sınırlar

- Denemeler ve kontrol ekranda hiç görünmez (v10-1c iptal): sayaç yok, cevapta iz yok.
- Kontrol araç çağrısına ve sözsüz cevaba bakmaz. Bir turun ara turlarındaki — çağrının yanındaki —
  sözler de kontrol edilmez; kontrol, turu bitiren sözlü cevaptadır.
- Kontrolün bedeli kayda geçmez. Denemeler arasında bekleme yok.
- `client.py`, `config.py`, `main.py`, `routes.py`'nin kuralları ve `useChat.js` değişmez.
  queen-editor'e dokunulmaz, ve iki aracı bağlayan bir test yazılmaz.

## Değişen dosyalar

- `queen-agent/backend/features/workspace/domain/prompt.py` — `APPROVED`, `CHECK`.
- `…/domain/black_box.py` — `REFUSED`, `REFUSED_SAID`; deneme başına `Answer`; kontrol.
- `…/domain/ports.py` — `Engine.stream_alone`.
- `…/data/model_engine.py` — `stream_alone`.
- `…/domain/chat.py`, `…/domain/usecases/stream_answer.py`, `…/presentation/routes.py` — yorumlar.
- `queen-agent/frontend/src/features/workspace/ChatScreen.jsx` — retli cevap.
- `queen-agent/frontend/dist` — yeniden derlenir.
- Testler: `test_black_box.py`, `test_model_engine.py`, `test_ports.py`, `test_stream_answer.py`,
  `test_chats_api.py`; tur koşan sahte engine'lere `stream_alone` — `test_last_activity.py`,
  `test_pin_archive.py`; `ChatScreen.test.jsx`.

## Testler

**Kutu (`test_black_box.py`):** sözlü cevap kontrole birebir, `CHECK`'le gider ve onaylanınca döner;
çağrılı cevap — sözleriyle — kontrolsüz döner; sessizliği cevap sayılan boş cevap kontrolsüz döner;
ret asıl isteği aynen yeniden gönderir; beş retten sonra `Answer(REFUSED_SAID, failed=REFUSED)`;
`APPROVED`'dan başka her söz — boş da — ret; boşlukları arasında `APPROVED` onay; kontrolün hatası
bir deneme sayılır ve beşi de öyleyse teknik hata, sözü kendi sözü; ret ve hata karışınca son deneme
karar verir (iki yönde); kontrolün kesme yolu da Stop'a verilir; kontrol sürerken Stop'ta başka istek
gitmez, cevap boş; retten sonra Stop'ta başka istek gitmez; cevabın `usage`'ı cevabın isteğinin.

**Engine (`test_model_engine.py`, `test_ports.py`):** `stream_alone` client'a yalnız talimatı ve metni
gönderir — QueenAgent'ın system prompt'u yok, araç yok —, kesme yolunu geçirir; port'un imzası
adaptörünkiyle aynı.

**Döngü (`test_stream_answer.py`):** beş retten sonra tur biter, mesaj `failed="refused"` ve ret
mesajıyla, adımlar kalır, modele başka istek gitmez; retli cevap sonraki turda modele gönderilmez.

**Kapı (`test_chats_api.py`):** beş ret kayda `failed: "refused"` ve ret mesajıyla geçer, akış `done`
ile biter, `error` yok; retli cevap doluluğa sayılmaz.

**Ekran (`ChatScreen.test.jsx`):** retli cevap düz yazı, kart ve Try again yok, `msg--failed`,
damgası yalnız saat.

## Bitti sayılır

- Yukarıdaki testler yeşil, dört suite yeşil (`test_dist_is_committed` commit'e kadar kırmızı),
  `dist` yeniden derlenmiş.
- Kullanıcının denemesinde: DeepSeek reddedince ret metni sohbete yazılmıyor, istek yeniden gidiyor;
  araç çağrısı kontrolsüz geçiyor. Beş denemede onaylı cevap gelmezse sohbette *"The model returned an
  error. Try asking another way."* düz cevap olarak, düğmesiz, altında yalnız saatle görünüyor, tur
  bitiyor, ve mesaj yenileyince duruyor.
- Kullanıcı kontrolün metnini Changes'te okuyup onaylıyor; commit ondan sonra.
