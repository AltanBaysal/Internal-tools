# Madde 420 — Queen Editor'ün agent'ı, test turu

**Koşu:** [Queen Editor v9](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md) · **Dal:**
`feat/queen-editor-v9` · **Parça:** 420 · v9-4c · **Tur:** 1/2 — yalnız testler.
**Üstüne kurulduğu:** [m417 test turu](2026-10-06-queen-editor-m417-sohbet-kaydi-testler-design.md)
(sohbetlerin kaydı), [m419 test turu](2026-10-06-queen-editor-m419-aracli-istek-testler-design.md)
(kutunun araçlı isteği).

**Kullanıcıdan gereken — yok.** Madde hizalı; kararları yol haritasının *Maddelerin kararları → v9-4*
ve *v9-3* bölümlerinde, davranışları tasarımın `BEHAVIOUR.md`'sinin *Agent panel* bölümünde
*(queen-design `queen-editor-v2`, ana klasörün `tmp/queen-design-queen-editor-v2/`'sinde)*. Talimatı
Claude yazar ve commit'ler, kullanıcı sonra okur *(yol haritasının başı — "böyle olsun")*. Kapıların,
araçların ve koşucunun biçimi teknik kararlar, Claude'un.

## Kullanıcının sözü

*"sadec açık projeye erişebilir ve şuan şu özellikleri istiyorum queen agentc gibi agetnci
çalışabilsin projdeki promptları okuuabilisn projedeki görselleri görebilsin"*, *"projeyi bu arada
vard card yaplılı bir şekilde görmesi laızm bence kaliteli bir sonuç için ve sorduğum soruları
cevaplsın şimdilik bu kadar"*, *"yani bir değişilik yapamasın"*, *"agentic looptada sınır 32 olsun
aynı suffixi kullansın"* *(5 Ekim)*. Tasarım turunda: *"1, çalışmaya devam eder"*, *"O an ne yaptığı,
tek satır"*, *"Yazılır ama gitmez; durdurulur"*, *"queen agent ne yapıyorsa onu yapar"*.

## Bugün ne oluyor

417'nin kaydı bir sohbete soru, adım ve sonuç yazabiliyor *(`features/agent/data/chat_record.py`)*,
ama onları yazan kimse yok: sunucunun soruyu alan bir kapısı yok, agent yok. 419'un kutusu bir
konuşmayı araçlarla DeepSeek'e götürüp cevabı bütün döndürüyor *(`Box.converse`)*, ama onu çağıran
yok. Kayıt süren adımı `finished: false` olarak tutuyor ve onu düşürmenin yolu yok; iki iş parçacığı
aynı `chats.jsonl`'a aynı anda satır ekleyebilir, ve aralarında bir kilit yok.

## Kurallar

### Agent

1. **Yalnız açık proje.** Proje soru sorulduğu anda belli; agent'a yalnız o projenin karelerini
   okuyan ve görselini açan iki şey verilir, ve hiçbir araç proje adı almaz — iki aracın tek
   argümanı `frame`.
2. **Hiçbir şeyi değiştiremez.** Araçlar yalnız okur: `read_frame` ve `look_at_frame`. Agent'ın
   eline yazan bir şey verilmez; projenin dosyaları agent koştuktan sonra baytı baytına aynı.
3. **Agentic, en çok 32 tur.** Her tur kutudan bir `converse`. Model araç çağırırsa araçlar koşar,
   cevapları konuşmaya eklenir, ve sıradaki tur gider; sözle cevap verirse o cevaptır. **32. tur**
   QueenAgent'ınki gibi: son tur olduğu söylenir (`LAST_ROUND`, konuşmanın sonunda bir sistem
   mesajı), araç verilmez, ve sözleri cevaptır — sıradan bir cevap *(v9-4, Madde 137'nin yolu)*.
4. **Projeyi kart kart, yapılı görür.** Soru gelince agent önce projeye bakar: galerinin kartları
   okunur, ve konuşmada sorudan hemen önce bir sistem mesajı olarak durur — ilk satırı
   `prompt.FRAMES`, sonra her kare bir JSON satırı, 1 numaralı kareden başlayarak:
   `{"frame", "status", "layers", "owed", "failed"}`. **Karenin numarası galerinin rozetindeki
   numara:** en alttaki, en eski kare 1, en üstteki en büyük *(`Gallery.jsx` — rozet aşağıdan sayar)*.
   `read_frame(frame)` kareyi bütün verir — aynı alanlar, artı `errors`, `scene`, `prompts`.
   `look_at_frame(frame)` karenin fotoğrafını gösterir.
5. **Görsel nasıl gösterilir.** Aracın cevabı *"The photo of frame N is in the next message."*; o
   turun araç cevaplarından sonra bir kullanıcı mesajı gelir, her görsel için önce *"The photo of
   frame N:"* yazısı, sonra görsel — `data:` adresli bir `image_url`, prompt yazarlarının gösterdiği
   gibi *(DeepSeek sistem mesajında ve araç cevabında resim almıyor; yazarlar resmi kullanıcı
   mesajında gönderir)*. Fotoğrafı olmayan kare: *"Frame N has no photo."*, görsel yok.
6. **Iska.** Bilinmeyen araç (*"There is no tool called X."*), numara olmayan ya da çözülemeyen
   argüman (*"A frame is named by its number, counting from 1."*), olmayan kare (*"There is no frame
   N; the frames are numbered 1 to M."*): model cevabı okur, döngü sürer, **adım yazılmaz** — bir
   adım agent'ın okuduğu şeydir, ıska bir şey okumaz.
7. **Talimat.** İlk mesaj sistem mesajı: `prompt.INSTRUCTION + prompt.SYSTEM_PROMPT_SUFFIX` — İngilizce,
   Claude'un yazdığı metin, ve **QueenAgent'ın suffix'iyle biter, birebir** *(Madde 407'nin yolu: kopya
   QueenAgent'ın metnine sabitlenir; QueenAgent'ın metni değişince test kırmızıya düşer)*.
8. **Sohbetin geçmişi gider.** Aynı sohbetin önceki soruları kullanıcı mesajı, cevaplanmış olanların
   cevabı asistan mesajı olarak, sırayla, talimattan sonra ve kartlardan önce; hatası, durdurulması ya
   da sonucu olmayan sorunun yalnız sorusu gider. Adımlar ve araç cevapları gitmez — QueenAgent'ın
   yaptığı gibi.

### Adımlar

9. **Her adımın iki Türkçe cümlesi** — sürerken ve bitince:
   - projeye bakmak: *"Projeye bakıyor…"* / *"Projeye baktı"* — her sorunun ilk adımı;
   - `read_frame(N)`: *"N numaralı kareyi okuyor…"* / *"N numaralı kareyi okudu"*;
   - `look_at_frame(N)`: *"N numaralı karenin görseline bakıyor…"* / *"N numaralı karenin görseline
     baktı"*.
10. **Adım, sıradaki adım başlayana ya da soru bitene kadar sürer.** Yeni bir adım başlarken önceki
    bitirilir (`finish_step`, sonra `add_step`). Bir turun son adımı, model onun cevabını okurken —
    sıradaki tur sürerken — canlı kalır: *"3 numaralı kareyi okuyor…"* model kareyi okurken görünür.
11. **Kayıt, adımları tasarımın kuralıyla katlar** *(BEHAVIOUR.md — "An answer or a failure finishes
    the last step. Stopping keeps the finished steps and drops the one that was going on")*: cevap ve
    hata son adımı bitirir; durdurmak bitmemiş adımı düşürür, bitenler kalır.

### Sonuç

12. **Cevap** — tek seferde, sohbete `answer`. **Karesi olmayan proje:** *"Projeye bakıyor…"* adımı,
    sonra hiçbir istek gitmeden cevap: *"Projede henüz kare yok. Prompt'ları yazıp kuyruğa
    eklediğinde kareler galeride belirir; sonra sorularını kareler üzerinden cevaplayabilirim."*
    *(tasarımcının cümlesi, `sohbet.js`'in `EMPTY`'si)*.
13. **Cevap veremezse** — kutu `failed` döner: sohbete hata, kutunun metniyle birebir. Retse
    *"Model hata döndü, farklı şekilde dene."*, teknik hatada hatanın kendi metni. Kutu iki metni
    zaten ayrı veriyor; tasarım ikisini aynı kartla, metinleriyle çizer *(`sohbet.js` — tek `err`
    türü)*, yani 425'in ayırt etmesi gereken yalnız metin. Kayda ayrı bir bayrak yazılmaz.
14. **Agent'ın kendi hatası** — bir disk hatası, silinmiş bir proje: sohbete hata, hatanın kendi
    metniyle. Sebep uydurulmaz.

### Sunucuda çalışır

15. **Soru sorulur, kapı hemen döner.** Soru kayda yazılır, agent arka planda başlar, ve kapı sohbeti
    o anki hâliyle döner. Agent kapıdan, panelden, sayfadan bağımsız sürer: sayfa yenilenince sohbet
    sonucusuz ve agent'ı çalışıyor, cevap gelince sohbette.
16. **İki sohbet aynı anda çalışabilir** — bir projede ya da iki projede. **Çalışan sohbet ikinci
    soruyu almaz:** 409, *"Bu sohbette agent hâlâ çalışıyor."*, kayda hiçbir şey yazılmaz.
17. **Durdurmak hemen olur.** Kayda *"durduruldu"* o an yazılır, sohbet çalışmaz olur, ve agent'ın o
    sorudan sonra yazmak istediği her şey düşer — yarım cevap yazılmaz. Havadaki istek kesilemez
    (kutu beş denemeyle bekler); döndüğünde cevabı hiçbir yere yazılmaz ve yeni tur gitmez.
    Durdurulduktan sonra sohbet hemen yeni soru alır; eski agent'ın geç yazıları yeni soruya düşmez.
18. **Çalışmayan sohbeti durdurmak hiçbir şey yazmaz** — cevap gelirken basılan ■ cevabı
    *"durduruldu"* yapmaz.
19. **Yeniden başlama.** Çalışan agent sürecin belleğinde *(417 bunu kayda bilerek koymadı)*; sunucu
    yeniden başlayınca hiçbir sohbetin agent'ı çalışmıyor. Yarıda kalan soru **sonucusuz kalır**:
    kayda ne *"durduruldu"* ne bir hata yazılır, çünkü ne olduğunu bilen yok — yazılan her cümle bir
    sebep uydurur. Sohbet yeni soru alır. 425 sonucusuz ve çalışmayan soruyu cevapsız, açık adımını
    da sürmüyor diye çizer.

### Kayıt

20. **Satırlar karışmaz, kaybolmaz.** Sohbetlerin kaydını yazan tek nesne (`main.py`'nin
    `_chat_record`'u) satır eklerken kilit tutar: iki yazan aynı anda satır eklemez. Agent'ların,
    soru ve durdurma kapılarının ve 417'nin yeni sohbet kapısının hepsi o nesneden yazar.
21. **Klasörü olmayan projeye satır yazılmaz.** Agent çalışırken proje silinir ya da yeniden
    adlandırılırsa, eski adla yazılacak satır reddedilir (*"Proje yok: <ad>"*) ve klasör yeniden
    açılmaz — kökün her klasörü bir projedir *(417'nin 11. kuralı)*. Agent orada biter.

### Kapılar — 425'in çağıracakları

22. **Soru sor** — `POST /api/projects/<proje>/chats/<id>/questions`, gövde `{"text": "…"}` → 200,
    sohbet bütün *(417'nin biçimi; yeni soru sonunda, `outcome: null`)*. Metin olmayan ya da yalnız
    boşluk olan soru 400 *"Soru boş."*; çalışan sohbet 409 *"Bu sohbette agent hâlâ çalışıyor."*;
    olmayan proje / sohbet 404 *"Proje yok: …"* / *"Sohbet yok: …"*; disk hatası 500, sistemin kendi
    sözleri. Soru metni olduğu gibi saklanır.
23. **Durdur** — `POST /api/projects/<proje>/chats/<id>/stop` → 200, sohbet bütün. Çalışmayan
    sohbette de 200, sohbet olduğu gibi. 404'ler ve 500 aynı.
24. **Çalışanlar** — `GET /api/projects/<proje>/chats/working` → 200 `{"working": [1, 3]}` — projede
    agent'ı şu an çalışan sohbetlerin kimlikleri, küçükten büyüğe. Listenin canlı noktası ve açık
    sohbetin ■'i bunu okur. Olmayan proje 404.

## İki türlü okunabilen yerler — seçilenler

- **Projeyi görmek araç mı, mesaj mı?** Kartların özeti sorudan önce bir mesaj; tek kartın tamamı ve
  görseli araç. Seçilen, çünkü *"Projeye bakıyor…"* tasarımda her sorunun ilk adımı, karesiz projenin
  cevabı da ondan çıkıyor, ve modelin projeyi bulmak için bir tur harcaması gerekmiyor —
  QueenAgent'ın dosya adlarını her istekte vermesinin sebebi *(Madde 127)*. Özet sorunun anındaki
  hâl; araçlar da aynı okumadan cevap verir, yani numaralar bir soru boyunca kaymaz.
- **Bir adım ne kadar sürer?** Kural 10. Araç anında koşar, ama model cevabını sıradaki turda okur:
  adımı turun sonuna kadar canlı tutmak, tasarımın *"süren en altta ve canlı"*sını gerçek kılar ve
  BEHAVIOUR'ın *"cevap son adımı bitirir, durdurmak süren adımı düşürür"*üne oturur.
- **Karesiz proje modele sorulur mu?** Sorulmaz: okunacak bir şey yok, cevap sunucunun cümlesi
  (kural 12) — tasarım da her soruya aynı cevabı veriyor.
- **Ret ile teknik hata kayıtta ayrılır mı?** Ayrılmaz (kural 13).
- **"Çalışıyor" bilgisi nerede?** Ayrı bir kapıda (kural 24). 417'nin cevaplarına bir alan eklemek
  417'nin kapılarını ve testlerini değiştirirdi; ayrı kapı onlara dokunmaz.
- **Yeniden başlamada ne yazılır?** Hiçbir şey (kural 19).
- **Geçmiş gider mi?** Gider (kural 8): sohbet eski yerinden sürer *(BEHAVIOUR.md — "carries on where
  it stopped")*, ve ikinci soru ilkine dayanabilir.

## Arayüz — uygulama turunun vereceği

Hepsi `backend/features/agent/` altında; özellik başka bir özelliği import etmez. Agent'ın projeyi
okuyan iki şeyi **`main.py`'nin verdiği** fonksiyonlar: galerinin kartları
(`partial(list_frames, …)` — ekranın okuduğu cevap) ve bir dosyanın baytları (`_photo_store.read`).
Projeler özelliğine silme yetkisinin verilmesi gibi *(`main.py` — "handed the ability, not the
worker")*.

- **`domain/usecases/answer_question.py`** — `MAX_ROUNDS = 32`;
  `answer_question(box, frames, picture, run, project, earlier, question)`: `frames(project)` galerinin
  kartları, üstteki önce; `picture(project, file)` baytlar ya da `None`; `earlier` sohbetin önceki
  soruları (417'nin biçimi); `run` aşağıdaki.
- **`domain/tools.py`** — `TOOLS` (DeepSeek'in araç tanımları: `read_frame`, `look_at_frame`).
- **`domain/prompt.py`** — `INSTRUCTION`, `SYSTEM_PROMPT_SUFFIX`, `LAST_ROUND`, `FRAMES`.
- **`domain/ports.py`** — `Run`: `stopped()`, `add_step(running, done)`, `finish_step()`,
  `answer(text)`, `fail(text)`.
- **`runner.py`** — `AgentRunner(record, spawn=None)`: `start(project, chat_id, text, at, work) ->
  bool` (soruyu yazar, `work(run)`'ı arka planda başlatır; sohbet çalışıyorsa `False`, hiçbir şey
  yazmadan); `stop(project, chat_id)`; `working(project) -> list[int]`. `spawn` testlerde içeride
  koşar ya da bekletilir, üretimde bir iş parçacığı.
- **`domain/usecases/chats.py`** — `EmptyQuestion`, `AgentBusy`;
  `ask_question(record, runner, agent, now, project, chat_id, text)`,
  `stop_agent(record, runner, project, chat_id)`, `working_chats(record, runner, project)`.
- **`presentation/routes.py`** — `make_agent_blueprint(ask_question, stop_agent, working_chats)`.
- **`data/chat_record.py`** — kilit; klasörü olmayan projeye `ProjectMissing`; katlamanın iki kuralı.
- **`main.py`** — `_agent_runner`, `_agent` (kutu, kartlar, baytlar bağlı), kapılar.

## Nasıl kanıtlanıyor

Döngü sahte bir kutuyla, sahte kartlarla ve yazdıklarını not eden sahte bir `run`'la — ağ yok
*(CODE-STANDARD, Tests)*. Sahte kutu her isteği o anki hâliyle kopyalayıp saklar ve sırayla
`Answer`'lar döner; sıradaki cevabın yerine bir fonksiyon durabilir — istek havadayken olan bir şeyi
(durdurmayı) kurar. Koşucu sahte bir kayıtla ve bekletilen işlerle: `spawn` işi bir listeye koyar,
test onu istediği anda koşar — gerçek bekleme yok. Kapılar `main.py`'nin bağlamasıyla elle, geçici
klasörde gerçek kayıtla. `main.py`'nin bağlaması `test_composition_root.py`'de: kapılar ve agent'ın
kendisi gerçek DeepSeek istemcisiyle, `requests.post` sahte. Kaydın kilidi gerçek iş parçacıklarıyla:
ilk satırı yazılırken tutan bir sahte depo, ikinci yazana 0,2 saniyelik bir fırsat verir — eşzamanlılık
bekleme olmadan gösterilemiyor, ve bu suitin tek gerçek beklemesi. Yeni modüller testlerin içinde
import edilir.

## Yazılacak testler

### `backend/tests/test_agent_answer.py` — yeni; döngü, sahtelerle

Kartlar *(galerinin sırası, üstteki önce — `P2_0` 3 numaralı kare)*: `P2_0` bekliyor, fotoğrafı
kuyrukta; `P1_0` hazır, fotoğrafı var, videosu hata verdi (`ComfyUI: out of memory`), sahnesi ve iki
prompt'u var; `P0_0` hazır, fotoğrafı ve videosu var, sesi kuyrukta.

1. **Karesi olmayan proje, istek gitmeden cevap alır** — yazılanlar: *"Projeye bakıyor…"* adımı, sonra
   tasarımcının cümlesi; kutuya hiç soru gitmez.
2. **İlk istek: talimat, kartlar, soru** — mesajlar tam olarak: sistem `INSTRUCTION + SUFFIX`, sistem
   kartlar (ilk satır `FRAMES`, sonra 1, 2, 3 numaralı karelerin satırları — galerinin rozetiyle),
   kullanıcı sorusu; araçlar `TOOLS`. Kartlar ve görseller yalnız sorulan projeden istenir.
3. **Talimat QueenAgent'ın suffix'iyle biter** — QueenAgent'ın `prompt.py`'sinden yüklenen metinle;
   kopya da onunla birebir.
4. **Araçlar yalnız okur ve proje adı almaz** — adlar `read_frame`, `look_at_frame`; ikisinin de tek
   ve zorunlu argümanı tam sayı `frame`.
5. **Sözle gelen cevap cevaptır** — bir istek; yazılanlar: projeye bakma adımı, cevap. Adım ayrıca
   bitirilmez — cevap bitirir.
6. **`read_frame` kareyi bütün verir** — ikinci istekte asistanın çağrısı ve aracın cevabı (çağrının
   kimliğiyle); cevabın JSON'u 2 numaralı karenin tamamı. Yazılanlar: projeye bakma, bitir, *"2
   numaralı kareyi okuyor…"* / *"…okudu"*, cevap.
7. **`look_at_frame` fotoğrafı gösterir** — aracın cevabı *"The photo of frame 1 is in the next
   message."*; arkasından bir kullanıcı mesajı: *"The photo of frame 1:"* ve `data:image/png;base64,…`
   görseli; görsel `("düğün", "P0_0.png")` ile istendi; adımı *"1 numaralı karenin görseline
   bakıyor…"*.
8. **Fotoğrafı olmayan kareye bakmak bunu söyler** — parametreli: fotoğraf katmanı yok (3), dosyası
   diskte yok (2) → *"Frame N has no photo."*, görsel mesajı yok, adım yazılır.
9. **Iska adım yazmaz, modele sebebini söyler** — parametreli: bilinmeyen araç, JSON olmayan argüman,
   metin numara (`"3"`), 0, 4 → aracın cevabı kuralın cümlesi; döngü sürer, ve yazılanlar yalnız
   projeye bakma ve cevap.
10. **Bir turda birkaç çağrı, sırayla** — `read_frame(2)`, `look_at_frame(1)`: araç cevapları
    çağrıların sırasıyla, görsel mesajı ikisinden sonra; adımlar sırayla, her biri öncekini bitirerek.
11. **Sohbetin geçmişi gider** — önceki iki soru (biri cevaplı, biri hatalı): talimat, soru 1, cevap 1,
    soru 2, kartlar, yeni soru.
12. **32. tur son tur: söylenir, araç verilmez, sözleri cevaptır** — model hep okursa 32 istek; ilk
    31'i `TOOLS`'la, sonuncusu araçsız ve son mesajı `LAST_ROUND`; ilk 31'inde `LAST_ROUND` yok;
    sonuncunun sözleri cevap.
13. **Kutunun başarısızlığı sohbete kendi metniyle yazılır** — parametreli: ret cümlesi; teknik hatanın
    metni.
14. **Durdurulan agent yeni tur göndermez** — ilk tur havadayken durduruldu: tek istek, cevap ya da
    hata yazılmaz.

### `backend/tests/test_agent_runner.py` — yeni; koşucu, sahte kayıtla, bekletilen işlerle

15. **Başlatmak soruyu yazar, ve sohbet çalışıyor** — kayda soru; `working` `[1]`; iş bekliyor.
16. **Çalışan sohbet ikinci soruyu almaz** — ikinci `start` `False`; kayıtta tek soru, tek iş.
17. **İki sohbet aynı anda, bir projede ya da iki projede** — `düğün` 1 ve 2, `kına` 1: üçü de başlar;
    `working("düğün") == [1, 2]`, `working("kına") == [1]`.
18. **Cevap ya da hata işi bitirir** — parametreli: iş adım ve cevap / hata yazar; satırlar sırayla
    kayıtta; sohbet artık çalışmıyor.
19. **Fırlatan iş kendi sözleriyle hata yazar** — `OSError`'ın metni; sohbet çalışmıyor.
20. **Durdurmak hemen yazar, ve sonrası düşer** — `stop`: kayda `stop`, sohbet çalışmıyor; sonra koşan
    iş `stopped()`'ı doğru görür, adımı ve cevabı kayda düşmez.
21. **Çalışmayan sohbeti durdurmak hiçbir şey yazmaz** — parametreli: hiç başlamamış; cevabı gelmiş.
22. **Durdurulmuş sohbet yeni soru alır, eski iş ona yazmaz** — soru 1, durdur, soru 2: eski işin
    cevabı düşer, yeninin adımı ve cevabı yazılır.

### `backend/tests/test_agent_routes.py` — yeni; kapılar, elle bağlı, geçici klasörde gerçek kayıtla

23. **Sorulan soru agent'ın okumasıyla cevaplanır** — işler içeride koşar; `read_frame(2)`,
    `look_at_frame(1)`, sonra söz: 200, sohbette soru, adımlar *(Projeye baktı, 2 okudu, 1'in
    görseline baktı — hepsi bitti)*, cevap; açılan sohbet aynı.
24. **Kapı hemen döner, agent sürer, cevap sonra gelir** — işler bekletilir: POST → 200, sonucu
    `null`; `working` `[1]`; sayfa yenilenir gibi açılan sohbet hâlâ sonucusuz; iş koşar; sohbette
    cevap, `working` `[]`.
25. **Çalışan sohbet ikinci soruyu almaz** — 409, cümle; kayıtta tek soru.
26. **İki sohbet aynı anda çalışır** — `working` `[1, 2]`.
27. **Durdurmak bitmiş adımları ve "durduruldu"yu bırakır, yarım cevap yazmaz** — işler bekletilir;
    model 2 numaralı kareyi okur; ikinci tur havadayken ■ kapısına basılır; o turun sözleri düşer:
    sohbette *Projeye baktı*, süren *2 okuyor* düşmüş, sonuç *durduruldu*, cevap yok; iki istek;
    `working` `[]`.
28. **Durdurulmuş sohbet hemen yeni soru alır** — 200.
29. **Çalışmayan sohbeti durdurmak bir şey değiştirmez** — cevaplı sohbet: 200, sohbet aynı.
30. **Ret ve teknik hata sohbete hata olarak düşer** — parametreli: metinleri birebir.
31. **Karesi olmayan proje** — sohbette *Projeye baktı* ve tasarımcının cümlesi; kutuya istek yok.
32. **Yeniden başlayınca yarıda kalan soru sonucusuz, ve sohbet yeni soru alır** — eski uygulamada
    soru sorulur, iş hiç koşmaz; aynı klasör üstünde yeni uygulama: `working` `[]`, soru sonucusuz,
    yeni soru 200.
33. **Boş soru reddedilir** — parametreli: `""`, `"   "`, `text`'siz gövde, sayı → 400 *"Soru boş."*;
    kayıtta soru yok.
34. **Olmayan proje 404, ve klasör açılmaz** — parametreli: üç kapı, *"Proje yok: yok"*.
35. **Olmayan sohbet 404** — parametreli: soru ve durdur, *"Sohbet yok: 7"*.
36. **Disk hatası sistemin kendi sözleriyle** — parametreli: üç kapı, 500.

### `backend/tests/test_chat_record.py` — eklenen ve değişen

37. *Değişir — 417'nin 8. testi:* aynı anda yazılan iki sohbet; cevap ve hata artık son adımı bitirir,
    yani iki adım da `finished: true`.
38. **Cevap ve hata süren son adımı bitirir** — parametreli.
39. **Durdurmak süren adımı düşürür, bitenleri bırakır.**
40. **Klasörü gitmiş projeye satır yazılmaz, klasör açılmaz** — `ProjectMissing`, *"Proje yok: …"*.
41. **İki yazan aynı anda satır eklemez** — ilk satırı yazılırken tutan sahte depo: ikinci yazan
    bekler; iki satır da yazılır.

### `backend/tests/test_composition_root.py`

42. **Uygulama agent'ın kapılarını sunar** — iki video modeliyle: olmayan projede üç kapı 404,
    *"Proje yok: m420-yok"*.
43. **Agent açık projeyi kutudan okur, ve hiçbir şeyi değiştirmez** — geçici kökte bir kare (kaydı ve
    PNG'si); `requests.post` sahte: model `read_frame(1)` ve `look_at_frame(1)` çağırır, sonra söz,
    sonra kontrolün `APPROVED`'ı. Cevap yazılır; ilk istekte iki araç; ikinci istekte karenin prompt'u
    ve `data:image/png` görsel; projenin dosyaları önce ve sonra baytı baytına aynı.

## Kırmızı beklenen

- `test_agent_answer.py`, `test_agent_runner.py`, `test_agent_routes.py`: her test
  `ModuleNotFoundError` — yeni modüller yok.
- 37 ve 38: `finished` `False`; 39: süren adım yerinde; 40: yazı geçiyor ve klasör açılıyor; 41: iki
  satır üst üste yazılıyor.
- 42: kapılar yok — GET `index.html`'e düşer, POST 405; 43: `main`'in `_agent`'ı yok.
- Öteki her şey yeşil; öteki üç satır yeşil — iki vitest satırı bu çalışma ağacında başlayamayabilir
  (`node_modules` yok); bu madde ekrana dokunmuyor.

## Bilinçli olarak yapılmayan

- Ekran — 425; frontend ve `dist`; yol haritası; QueenAgent'ın kodu.
- Akış (stream), yeniden dene düğmesi, sohbet silme.
- Havadaki isteği kesmek: kutu tek bir isteği beş denemeyle bekler; durdurma onun cevabını düşürür.
- Yeniden başlamada yarıda kalan soruya bir sonuç yazmak (kural 19).
- Agent'ın yeni sohbet kapısıyla aynı kilidi tutması dışında bir kuyruk ya da süreç arası kilit: tek
  süreç, tek kayıt nesnesi.
- Proje yeniden adlandırılınca agent'ı yeni ada taşımak: agent biter (kural 21); fotoğraf
  koşucusunun `follow_rename`'i gibi bir yol, istenmemiş bir parça.
- Kare numarasında metin bağışlamak (`"3"`): model bir tur sonra numarayla yeniden ister.
