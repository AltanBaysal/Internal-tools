# Madde 467 · Mod tarayıcıda, bütün sohbetlerde tek — tasarım

**Tarih:** 10 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
467 · **Dal:** `feat/queenagent-v10`, ana klasörde · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Geri aldığı:** [463](2026-10-10-queen-agent-m463-mod-sohbetin-design.md) (mod sohbetin ayarı).

## Ne, neden

**Bugün** (463'ten beri) her sohbetin modu `projects.json`'daki satırında duruyor: seçici sohbetin modunu
çiziyor, seçim `POST …/chats/<c>/mode` ile gidiyor, tur modu her tool çağrısında satırdan okuyor, Allow
modu sunucuda Edit'e çeviriyor.

**Kullanıcı fikrini değiştirdi** (10 Ekim — *"abi mod sohbete ait olmasın, user en son ne seçtiyse o
kalsın bütün sohbetlerde, bunu düzeltelim, yanlış söyledim galiba sana"*; sunucu yeniden başlayınca ne
olsun sorusuna — *"abicim diskte vs kalmasın, frontend'de kalsın, her istekle gitsin, frontend her açılıp
kapandığında sıfırlanabilir, sıkıntı yok, basit tut"*).

**Olacak:**

- Mod tarayıcıda tek bir değer, `App.jsx`'in `mode`'u: kullanıcının en son seçtiği, bütün sohbetlerde
  ve taslakta aynı. Sohbet değişince aynı kalır.
- Yeni sayfa Edit'le açılır; sayfa yenilenince Edit'e döner.
- Seçici seçimi hemen çizer ve sunucuya hiçbir şey göndermez.
- Her mesaj, düzenleme ve Try again modu gövdesinde gönderir (`{mode}`).
- Sunucu modu istekten alır, tura parametre olarak verir ve hiçbir yere yazmaz: `projects.json`'da mod
  yok, sohbet dosyasında mod yok, cevaplarda mod yok, mod kapısı yok.
- Allow'a basınca tarayıcı modu Edit yapar; tur da kendi içinde Edit'e geçer, aynı turun sonraki
  yazmaları yeniden sorulmaz.

## Nasıl

Kısaca: 463'ün eklediklerinin çoğu gider, 463'ten önceki şekle dönülür; üstüne modun doğrulanması gelir.

### Backend

- **`domain/usecases/advance_chat.py`**: `mode` istekten gelir. `None` (gövdede yok ya da `null`) Edit
  demektir; `MODES` dışında bir değer (`"write"`, `""`, `5`) tutmadan önce `UnknownMode` ile reddedilir.
  Mod `run_turn`'e parametre olarak gider. Taslağın modunu satıra yazan kod gider.
- **`presentation/routes.py`**: `advance` `payload.get("mode")` geçirir; mesaj (düzenleme dahil) ve
  retry kapıları `UnknownMode`'u `400 {"error": "mode must be plan, ask or edit"}` yapar. `POST …/mode`
  gider. `_chat_state` modu taşımaz; izin kapısı yine `{turn}` döner ve `live.decide`'ı doğrudan çağırır.
- **`domain/usecases/run_turn.py`**: `mode` parametresi geri gelir, bu kez **zorunlu**: mod tek yerde,
  kapıda (`advance_chat`) belirlenir, tur bir kez alır; Allow'dan sonra `mode = EDIT` — turun kalanı
  Edit'te.
- **`domain/modes.py`**: `needs_permission`'ın bilinmeyen moda varsayılanı verme kuralı gider
  (`_WITHOUT_ASKING[mode]`): mod kapıda denetlenir, kapıdan denetlenmeden geçen bir mod hatadır.
  `MODES`, `_WITHOUT_ASKING`'in anahtarlarından okunur; kapının bildiği modlarla kuralın modları
  ayrılamaz.
- **Gidenler:** `pick_mode.py`, `answer_question.py`, `FileProjectStore.chat_mode/set_chat_mode`,
  `_chat_row_of`, `_mode_of`, `FileChatStore.mode_of/set_mode`, `ChatStore`'un iki portu,
  `LiveTurn.asks`, ve 463'ün `_put` değişikliği: satır yine **bütünüyle değiştirilir**. Yerinde
  güncellemek 463'ün `mode` yazdığı her satırı sonraki her `projects.json` yazısında diske geri
  yazardı — kullanıcının *"diskte vs kalmasın"*ına karşı — ve `_chat_row`'dan ya da `_file_row`'dan
  ileride çıkan bir alan eski satırlardan hiç gitmezdi.
- **Kalanlar:** `UnknownMode` (doğrulama için). **Göç yok:** 463'ün `mode` yazdığı satırlar okunur,
  anahtar okunmaz; sohbetin bir sonraki yazılışı satırı bütün yazar ve anahtar dosyadan çıkar.

### Frontend

- **`App.jsx`**: `draftMode` ve sohbetin modunu çizmek gider; tek `const [mode, setMode] =
  useState(DEFAULT_MODE)`. Seçici `mode`'u çizer, `onModeChange={setMode}`. `onSend`, `onRetry` ve
  `onAnswerAgain` `mode`'u geçirir. `onAllow` cevabı gönderir ve `setMode(EDIT)` yapar.
- **`useChat.js`**: `pickMode`, `picked`, `picks`, `shownMode` gider; `answer` cevaptan mod okumaz.
  `send(text, skill, mode, from)` ve `retry(mode)` modu gövdeye koyar. Varsayılanı yok: mod geçirmeyen
  bir çağrı onu gövdeye hiç koymaz, sunucu Edit okur (`""` gönderseydi 400 alırdı).
- **`modes.js`**: `EDIT` ihracı geri gelir (Allow kuralı onu kullanır).

### Kural dosyası

CODE-STANDARD'ın 463'te genişleyen iki yeri eski hâline döner: `projects.json` satırındaki "and each
chat's settings — today its mode (Madde 463)" ve "A chat's settings live here too — …" paragrafı.
Aynı commit'in FOUNDATION cümlesi ve SSE cümlesi kalır.

## Sınırlar

- **Tur sürerken seçilen mod o tura ulaşmaz.** Mod istekle gider ve tur onu bir kez alır; yeni seçim bir
  sonraki mesajda, düzenlemede ya da Try again'de geçerli. Canlı okumak sunucuda modun bir kopyasını
  (bellekte de olsa) ve onu değiştiren bir kapı demekti — kullanıcının "basit tut"una ve "her istekle
  gitsin"ine karşı.
- **Sekmeler birbirini görmez.** Her sekmenin kendi modu var; bir sekmede seçilen mod ötekine geçmez.
- **Sayfa yenilenince mod Edit'e döner** — kullanıcının kabul ettiği: *"frontend her açılıp kapandığında
  sıfırlanabilir"*.
- **Allow'dan sonra mod Edit**, bayat bir Allow'da da (tarayıcı yalnız tıklamayı bilir). Sunucuda bayat
  Allow hiçbir şeye izin vermez; tarayıcıdaki Edit kullanıcının "evet, çalış" demesidir.
- **Eski sekme:** 463'ün yüklediği sayfa sohbet mesajında ve retry'da mod göndermez; sunucu Edit okur.
  Taslağın ilk mesajında gönderdiği mod geçerli.

## Maliyet (Drive'da gidiş dönüş)

| İşlem | 463 | 467 |
|---|---|---|
| Mod seçmek | 1 istek; `projects.json` bir sıralı yazı | 0 istek, 0 disk |
| Mesaj, düzenleme, Try again | aynı + taslakta satıra mod | 463'ten önceki gibi; mod gövdede, diske gitmez |
| Tur sürerken mod | her tool çağrısında bellekte satır taraması, O(sohbet sayısı) | parametre, 0 |
| GET chat, 409, 202 | + bellekte mod okuması | mod okuması yok |
| İzin cevabı | Allow'da `projects.json` bir sıralı yazı | 0 disk |

Hiçbir işlem modu diske yazmaz; bütün işlemler projelerin, sohbetlerin ve dosyaların sayısından bağımsız.

## Bitti sayılır

- Modu seçip başka sohbete ve yeni sohbete geçince aynı mod duruyor.
- Yeni sayfa ve yenilenen sayfa Edit'te.
- Seçim sunucuya istek göndermiyor; mesaj, düzenleme ve Try again modu gönderiyor.
- `projects.json`'a, sohbet dosyasına ve cevaplara mod yazılmıyor; `POST …/mode` yok (405).
- Bilinmeyen mod üç kapıda da 400 *"mode must be plan, ask or edit"*, hiçbir şey tutulmadan; mod
  gönderilmezse Edit.
- Allow'dan sonra seçici Edit gösteriyor ve sonraki mesaj Edit'le gidiyor; aynı turun ikinci yazması
  yeniden sorulmuyor.
- 463'ün `mode` yazdığı satırlar taşımasız okunuyor, ve sohbetin bir sonraki yazılışında anahtar
  dosyadan çıkıyor.
- Dört test takımı yeşil. Tek istisna, dist sahnelenene kadar beklenen
  `test_the_page_asks_for_files_that_were_committed_with_it`.
