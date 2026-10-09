# Madde 440 · Agent'ın kara kutusu — tasarım

**Tarih:** 9 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
440 (eski adı v10-1a) · **Dal:** `feat/queenagent-v10` · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Tasarım:** `queen-design`'ın `queen-agent-v4` dalı, maddeler 214, 215, 216, 221 —
`projects/queen-agent/BEHAVIOUR.md`'nin *Turn*, *Stops*, *The failed answer* bölümleri ve `chat/`,
`turn/`, `messages/`, `stops/` sayfaları.

## Ne, neden

Kullanıcı, 5 Ekim: *"Deepseek kontrol katmanı ekle cevaba bak red ise tekrar gönder"*,
*"yani agetna bir şye dönsün yoksa agentic döngü kırılır"*. 440 bunun ilk parçası: agent'ın
DeepSeek'e attığı her istek tek bir kutudan geçer; kutu hatada isteği yeniden gönderir, cevabı bütün
döner, ve beşinde de olmazsa hata fırlatmaz — hatanın kendi metnini cevap olarak döner. Ret kontrolü
445'in; kutuda onun yeri açık bırakılır, kendisi yazılmaz.

Bugün:

- Döngü (`stream_answer.py`) her turda `engine.stream(...)`'i doğrudan okur. Bir HTTP hatası, kopan
  bir akış ya da anahtarın yokluğu turu `EngineFailed`'la bitirir; sohbette kayda geçmeyen geçici bir
  *"Couldn't get a response."* kartı çıkar, ve soru cevapsız kalır.
- Sözler geldikçe tarayıcıya `chunk` olarak gider, ve ekran onları canlı yazar
  (`ChatScreen.jsx`'in `streamingText`'i).
- Stop'ta o ana kadar söylenen yarım cevap kalır, sol çizgiyle (`test_what_was_already_said_is_kept`).

## Olacak

### 1 · Kutu — `backend/features/workspace/domain/black_box.py`, yeni

Adı `black_box`: ön uçta *box* yazı kutusunun (composer'ın) adı, ve `context_box.py` de var.

`ask(engine, messages, tools, on_open, stopped) → Answer`. Döngü her turda isteğini — konuşma, araçlar
— buraya atar; kutu `engine.stream`'i sonuna kadar okur ve cevabı bütün döner.

- **`Answer`** donmuş bir dataclass: `text` (sözler), `calls` (bütün araç çağrıları), `usage` (bir
  `Usage`, ya da engine bir şey demediyse `None`), `failed` (`""` ya da `"technical"`).
- **En çok 5 deneme (`TRIES`).** Aynı istek aynen yeniden gider:
  - **hata** — `engine.stream`'in fırlattığı her şey: HTTP hatası, kopan akış, internet yok,
    anahtar yok (`ModelNotConfigured`). Liste değil, `except Exception`: anahtarsızlık hiçbir şey
    göndermeden reddediliyor, beş denemesi bedava; tek kural bir listeden basit.
  - **boş cevap** — ne söz (boşluk sayılmaz) ne araç çağrısı; yalnız turda henüz hiçbir dosyaya
    yazılmadıysa. **Dosya yazıp susan tur bitmiş sayılır**, bugünkü gibi *(Madde 38; kullanıcı, 9
    Ekim, Claude'un önerisini seçerek — "the thing is you recommend it")*: yeni bir dosya da, var
    olanı değiştirmek de yazmaktır; *"Already there"* diyen bir `create_file` hiçbir şey yazmamıştır.
    Bunu turu bilen döngü söyler: `ask(..., silence_is_an_answer=writes.wrote)` — kutu tur bilmez,
    isteğe bakar; sözsüz cevabı yeniden denemeden dönmesini çağıran ister.
- **Stop yeniden denenmez.** Bir deneme koptuğunda ya da boş geldiğinde kutu önce `stopped()`'a
  sorar; Stop istenmişse boş bir `Answer()` döner, başka istek gitmez. `Answer`'da ayrıca bir stop
  alanı yok: Stop'u bilen tek yer `Stops` kaydı, ve döngü her cevaptan sonra ona zaten soruyor.
- **Beşi de olmazsa fırlatmaz:** `Answer(text=<son hatanın kendi metni>, failed="technical")`. Boş
  cevabın metni `NOTHING` — *"The model returned nothing."*, bugün route'un yazdığı cümle; route da
  onu buradan okur. Sebep ve sayı eklenmez.
- **Denemeler görünmez:** kutu yalnız bir `Answer` döner, döngü de ekran da kaç deneme olduğunu
  bilmez.
- **445'in yeri:** bütün bir sözlü cevap geldikten sonra, döndürülmeden önce. Kontrolün isteği aynı
  `engine`'den gider, ret de bir hata gibi aynı beşlik sayaçtan düşer; `failed` o gün `"refused"`
  değerini kazanır. Bugün o satır yok, yalnız bir yorum yerini söyler.
- **Neden domain'de:** kaç deneme, neyin boş sayıldığı, Stop'un denenmediği bir testin tuttuğu
  kurallar; Stop'u da domain'in `Stops`'u bilir. `services/model/` CODE-STANDARD'a göre yalnız
  taşıma: bir istek, bir SSE akışı, bir araç çağrısı — `client.py` değişmez.
- **Bir deneme bedeli:** başarılı denemenin `usage`'ı sayılır. Boş gelip yeniden denenen bir
  denemenin harcadığı kayda geçmez.

### 2 · Döngü — `stream_answer.py`

- Her tur `ask(...)`'i sorar. Sözler artık parça parça `yield` edilmez: cevap bütün geliyor ve ekran
  onu tur bitmeden göstermiyor (3). `chunk` olayı kalkar.
- `usage` geldiyse eklenir ve `Progress` bugünkü gibi gider.
- **Stop:** her cevaptan sonra `Stops` kaydına sorulur; Stop istenmişse tur durur — kutunun koptuğu
  için boş döndüğü istek de, bütün gelip Stop'un tam o anda geldiği tur da. O anki istek atılır, araç
  çağrıları koşmaz. Yazılan mesajda **söz yok** — önceki turların sözleri de: tasarım
  215, *"no words"*. Adımlar (`calls`) ve doğan dosyalar kalır, `stopped=True`. Bekleyen izin kartı
  bugünkü gibi gider: Stop beklemeyi uyandırır, tur biter, ekran kartı kaldırır.
- **Başarısız cevap:** `answer.failed` ise tur biter, modele bir şey geri gitmez. Mesaj: `text` =
  hatanın kendi sözü, `failed="technical"`, o ana kadarki adımlar ve dosyalar, `usage` = biten
  turların harcadığı. Önceki turların sözleri yazılmaz.
- **Tur yazdı mı:** araçlar dosyalara `_Noting` üzerinden ulaşır — dosya deposunun turun gördüğü
  hâli, `write` çağrılınca bunu not eder. Bir düzine araç yazıyor (yeni dosya, düzenleme, senaryoya
  eklenen bir giriş) ve her birinin cevabına bakmak kırılgan olurdu; her yazının geçtiği tek kapıya
  sormak bir kural. Not `silence_is_an_answer`'a ve `append_message`'in `wrote`'una gider: söz ve yeni
  dosya olmadan var olanı değiştirip susan bir cevap da bir cevaptır, ve kayda adımlarıyla yazılır
  (`wrote` diske yazılmaz; adımlar onu zaten söylüyor).
- Kutu fırlatmadığı için `except Exception → EngineFailed` artık modelden değil, turun kendi kodundan
  — bir araç, disk — gelen bir hatayı akışın içinde söyler. Kalır; yorumu bunu söyler.

### 3 · Ekran — cevap bütün gelir *(tasarım 214)*

- Tur bitene kadar ekran bekleyişi tutar: adım kutusu, üç nokta, saat satırı (ya da canlı şerit),
  *creating file…*; izin kartında da. `streamingText` ve onun bloğu kalkar.
- Tur bitince kayıt okunur (bugünkü gibi) ve mesaj bekleyişin yerine bütün olarak gelir; **sözleri
  200 ms'de belirir**: o mesaj `msg--arrived` sınıfını taşır, ve `workspace.css`
  `.msg--arrived .msg__text { animation: fadeIn 0.2s ease both; }` der. `useChat` hangi mesajın
  az önce geldiğini (`arrived`, kaydın son mesajının sırası) tutar; sohbet açılınca ve yeni bir
  gönderimde sıfırlanır, yani yalnız bir kez belirir. Diskten açılan sohbet belirmez.
- **Bekleyiş görünür kalır:** artık her tur sözsüz bekliyor, ve bekleyiş büyürken — adım kutusu,
  canlı şerit, *creating file…* — sohbetin dibindeki okur onunla birlikte iner, bir zamanlar sözlerin
  çektiği gibi. Okur yukarıdaysa yerinde kalır (bugünkü 220 px kuralı).
- Denemeler ekranda hiç görünmez: sayaç yok, cevapta iz yok.

### 4 · Durdurulan tur *(tasarım 215)*

Durmuş turda yazı, sol çizgi ve maliyet yok; altında yalnız `Stopped` ve saat. Sıra tasarımınki:
adımlar, dosya kartları, `Stopped`, damga. Kayıt biten turların
harcadığını yine tutar (harcanan para gerçek); ekran onu durmuş bir cevapta çizmez.
`.msg--stopped .msg__text` kuralı ve `msg--stopped` sınıfı kalkar: yeni bir durmuş cevabın sözü yok,
ve tasarım çizgiyi kaldırdı. Eski kayıtlarda sözü olan durmuş cevaplar sözleriyle, çizgisiz görünür.

### 5 · Başarısız cevap *(tasarım 216 ve 221)*

- **Kayda yazılır:** mesaj `failed: "technical"` taşır (diskte yalnız doluysa, `stopped` gibi); kayıt
  okunurken `failed` her mesajda gelir (`""` ya da `"technical"`). Sayfa yenilenince ve sohbet yeniden
  açılınca durur.
- **Ekranda bugünkü kart:** `msg msg--ai msg--failed`; adımlar (varsa) kutularında, altında
  *"Couldn't get a response."* ve hatanın kendi sözü, doğan dosyaların kartları; **saati yok** —
  kartın saati yok, damga çizilmez. `.msg--failed .failure { align-self: stretch; }` kartı
  sütunun genişliğine yayar, dışarıdaki kart gibi.
- Kartın çizimi tek yerde: `FailureCard.jsx`, yeni. Geçici kartlar (`refused`, `error`) da onu
  kullanır.
- **Try again** yalnız o kart açık satırın son mesajıyken ve hiçbir tur sürmüyorken görünür.
  Arkasından bir mesaj gönderilirse kart düğmesiz kalır — gönderilen balon hemen son mesaj olur. Bir
  tur sürerken de düğmesiz: basışla kaydın yeniden okunması arasında, yavaş bir tünelde, ikinci bir
  basış ikinci bir tur başlatırdı.
- **Basınca:** `useChat`'in `answerAgain`'i — sözsüz istek, geçici kartların `retry`'ından ayrı bir
  ad: o, reddedilen bir cevabı yazı kutusundan yeniden gönderebilir; bu hiçbir zaman göndermez. İstek
  oturumun modunu taşır, bir gönderim gibi: Plan'da ya da Ask'ta sorulan bir soru Try again'le Edit'te
  koşup sormadan yazmamalı. Geçici kartların sözsüz Try again'i de modu artık taşır. Sunucu tavanı ilk
  sorar (bugünkü gibi); sonra açık satırın son mesajı başarısız bir cevapsa onu kayıttan çıkarır, soru yeniden
  cevaplanır. Yeni kullanım durumu: `usecases/drop_failed_answer.py`. Çıkan cevap bir kırpma işareti
  (`trimmed`) taşıyorsa işaret önündeki mesaja — sorusuna — geçer: dolu bir sohbette Continue here
  başarısız cevabı işaretlemiş olabilir, ve Try again kırpmayı silmemeli. Cevabın kendi adımları ve
  dosya kartları onunla gider; dosyalar diskte ve rail'de kalır.
- **Ekranda hemen gider:** akışın ilk olayı (`chat`) geldiğinde sunucu cevabı zaten çıkarmıştır;
  `useChat` kaydı sunucudan yeniden okur, kart gider, bekleyiş gelir. Hangi mesajın gittiği sunucunun
  kuralı, tarayıcı onu kopyalamaz (FOUNDATION, Karar 4). Sunucu reddederse (dolu sohbet) olay gelmez,
  kart durur, ret kartı altında görünür.

### 6 · Doluluğa sayılmaz

Başarısız cevap modele gitmez ve hiçbir şey tartmaz: `chat.py`'de `sent_messages` onu atlar,
`_size` da. Böylece gösterge (`chat_size`), tavan (`is_full`) ve Continue here'in kırpması
(`trim_point`) son gerçek cevabı okur. Bu uygulamada doluluk mesajların metninden ölçülüyor (Madde
337); tasarımın *"son gerçek cevabı okur"*'u burada *"başarısız cevabın metni sayılmaz"* demek.
Sonraki turda başarısız cevap modele gönderilmez: hatanın sözü bir cevap değil, ve kullanıcı *"modele
bir şey geri gitmez"* dedi.

## Sınırlar

- **Sessiz tur (Madde 38) değişmez.** Dosya yazıp — yeni ya da var olan — susan tur, sözsüz bir
  cevap olarak, adımları ve dosyalarıyla biter; yeniden denenmez, kart çıkmaz. Yalnız okuyup susan,
  ya da *"Already there"* alıp susan tur — hiçbir şey yazmadı — boş sayılır: yeniden denenir, beşi
  de boşsa başarısız cevapla biter.
- **Bir tur sürerken tarayıcı daha az şey duyar.** Sözler artık gitmiyor; bir turun içinde yalnız
  turun başındaki ve sonundaki `progress` gider. Bugün araç çağrısı yazan bir tur da bu kadar
  sessiz. İzin beklerken atılan `Waiting` değişmez.
- Denemeler arasında bekleme, deneme sayısının ayarı, denemelerin günlüğü yok.
- Ret kontrolü ve ret mesajı (*"The model returned an error. Try asking another way."*) 445'in.
- `client.py`, `model_engine.py`, `config.py`, `main.py` değişmez. queen-editor'e dokunulmaz, ve iki
  aracı bağlayan bir test yazılmaz.

## Değişen dosyalar

- `queen-agent/backend/features/workspace/domain/black_box.py` — yeni: `TRIES`, `NOTHING`, `TECHNICAL`,
  `Answer`, `ask`.
- `…/domain/usecases/drop_failed_answer.py` — yeni.
- `…/domain/usecases/stream_answer.py` — kutu; stop ve başarısız cevap; söz parçası yok; `_Noting`.
- `…/domain/chat.py` — `Message.failed`; `sent_messages` ve `_size` başarısız cevabı atlar;
  `with_open_line` — açık satırın kendi mesajlarını değiştirmenin tek yeri.
- `…/domain/usecases/append_message.py`, `trim_chat.py` — `failed`; `append_message`'e `wrote`;
  ikisinin satır yürüyüşü `with_open_line`'a.
- `…/domain/ports.py` — `Engine`'in belgesi kutuyu anar.
- `…/data/file_chat_store.py` — `failed` yazılır, okunur.
- `…/presentation/routes.py` — `failed` kayıtta; `chunk` yok; Try again `drop_failed_answer`'dan
  geçer; boş cevabın cümlesi `black_box.NOTHING`.
- `queen-agent/frontend/src/features/workspace/useChat.js` — `streamingText` yok; `arrived`; Try
  again'in ilk olayında kayıt yeniden okunur; `answerAgain`; sözsüz istek modu taşır.
- `…/ChatScreen.jsx` — bekleyiş ve onu izleyen kaydırma; `msg--arrived`; başarısız cevap kartı, tur
  sürerken düğmesiz; durmuş cevabın sırası ve damgası.
- `…/FailureCard.jsx` — yeni.
- `…/workspace.css` — `msg--arrived`, `msg--failed`; `msg--stopped` kuralı çıkar.
- `queen-agent/frontend/src/App.jsx` — `streamingText` yerine `arrived`; iki Try again oturumun
  modunu verir.
- `queen-agent/frontend/dist` — yeniden derlenir.
- Testler: `test_black_box.py` (yeni), `test_stream_answer.py`, `test_chats_api.py`, `test_chat.py`,
  `test_file_chat_store.py`, `test_append_message.py`; `ChatScreen.test.jsx`, `App.test.jsx`.

## Testler

**Kutu (`test_black_box.py`, yalnız sahte engine'lerle):** iyi cevap tek istekte döner, sözleri ve
çağrıları bütün; bir hatadan sonra aynı istek aynen yeniden gider; boş cevap (boşluk da) yeniden
gider, çağıran sessizliği cevap saydıysa gitmez; beş hatada beş istek ve
`failed="technical"`, metin son hatanın sözü; beş boşta metin `NOTHING`; anahtarsızlık da denenir;
Stop'ta koparsa ikinci istek gitmez, cevap boş; kutu hiçbir durumda fırlatmaz; `usage` son okumayı
tutar, engine bir şey demediyse `None`.

**Döngü (`test_stream_answer.py`):** söz parçası `yield` edilmez; bir hatadan sonra tur aynı cevapla
biter; dosya yazıp susan tur bugünkü gibi sözsüz bir cevapla biter ve yeniden sorulmaz (Madde 38'in
testleri olduğu gibi kalır), var olan bir dosyayı düzenleyip susan da; yalnız okuyup ya da *"Already
there"* alıp susan tur yeniden sorulur; beş hatada mesaj başarısız cevap — metin hatanın sözü,
adımlar ve dosyalar kalır, turun önceki
sözleri yazılmaz, modele başka istek gitmez; durmuş turda söz yok (`test_what_was_already_said_is_kept`
tersine döner), adımlar ve dosyalar kalır; Stop'ta kopan istek yeniden gitmez; başarısız cevap
sonraki turda modele gönderilmez.

**Sohbet (`test_chat.py`):** başarısız cevap `chat_size`'a, `is_full`'a ve `trim_point`'e sayılmaz;
`sent_messages` onu atlar.

**Kayıt (`test_file_chat_store.py`):** `failed` yazılır ve okunur; boşken diske yazılmaz.

**Mesaj (`test_append_message.py`):** bir dosyaya yazmış cevap sözsüz de kayda geçer.

**Kapı (`test_chats_api.py`):** kayıt her mesajda `failed` taşır; akışta `chunk` yok; beş hatadan
sonra akış `done` ile biter, `error` yok, kayıtta başarısız cevap; Try again başarısız cevabı çıkarıp
soruyu yeniden cevaplar; çıkan cevabın kırpma işareti sorusuna geçer; dolu sohbette Try again
tavanla reddedilir ve başarısız cevap kalır.

**Ekran (`ChatScreen.test.jsx`, `App.test.jsx`):** bekleyiş tur bitene kadar durur ve söz çizmez;
gelen cevabın mesajı `msg--arrived` taşır; başarısız cevap kart olarak, hatanın sözüyle, saatsiz
çizilir; Try again yalnız son mesajken, tur sürmüyorken ve yazı kutusundan değil; basınca soru
oturumun moduyla yeniden gider (Plan'da `mode: "plan"`) ve kart, kayıt yeniden okununca hemen gider;
durmuş cevap dosya kartları, `Stopped`, saat sırasıyla, damgası saat yalnız; dipteki okur büyüyen
bekleyişle iner, yukarıdaki yerinde kalır; mesajın parçaları kendi dosyalarından (`FailureCard`).

## Bitti sayılır

- Yukarıdaki testler yeşil, dört suite yeşil, `dist` yeniden derlenmiş.
- Kullanıcının denemesinde: HTTP hatası gelince istek yeniden gidiyor, ekranda deneme izi yok, cevap
  tamamlanınca tek seferde, sözleri belirerek görünüyor. Stop'ta yarım cevap kalmıyor, adımlar
  kalıyor, tur yalnız `Stopped` ve saatle işaretleniyor. Beş denemede olmazsa *"Couldn't get a
  response."* kartı hatanın kendi sözüyle; yenileyince duruyor, Try again yalnız son mesajken var ve
  soruyu yeniden cevaplatıyor, sohbetin doluluğu değişmiyor.
