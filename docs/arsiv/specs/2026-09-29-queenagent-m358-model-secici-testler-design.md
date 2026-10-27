# Madde 358 — Model seçici kalkar, ve model hiçbir yerde görünmez · test turu

**Kaynak:** [yol haritasının 358'i (v9-4b)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), *29
Eylül'de değişti*; kararları v9-4'ün. Kullanıcının sözü *(28 Eylül, tasarım turunda)*: "Queen Flash,
bunu kaldıralım, vazgeçtim, beğenmedim, görünmesin model". Tasarımı queen-design'ın `queen-agent-v3`
dalında 136 ve 157 — 157: *"Mesaj kutusunun ayağında model adı yok"*; `BEHAVIOUR.md`: *"No page draws a
message's skill or model"*; `DESIGN-STANDARD.md`'nin *Not on screen*'i `.model-label`'ı çizilmeyen
kural sayıyor. **Mimari:** FOUNDATION'ın 6. kararı aynı parçada güncellenir — modellerin adlarını ve
fiyatlarını `models.js`'ten okuyan kimse kalmıyor.

**Kullanıcıdan gereken:** hiçbir şey. Madde hizalı; tasarım seçicinin de adın da gittiğini söylüyor.
Aşağıdaki sunucu kararı teknik bir karar, davranış değil.

## Ne kanıtlanacak

Bugün yazma kutusunun ayağında `Edit⌄ Skills⌄ Queen Flash⌄ ↑` duruyor; `Queen Flash` bir seçici,
açılınca `MODELS` başlığı altında tek satır, `$0.22 / $0.66 per 1M`. Seçilen model `send(text, skill,
mode, model, from)` ile her mesaja `model` alanı olarak biniyor, sunucu onu mesaja yazıyor ve turu o
modele gönderiyor. Olacak:

- **Ayakta seçici de ad da yok:** `Edit⌄ Skills⌄ ↑` — üç düğme: Mode, Skills, Send (süren cevapta
  Stop). Sohbet yüklenirken kapalı olan seçiciler ikiye iner.
- **Ekranın hiçbir yerinde model yok:** ne `Queen Flash`, ne `MODELS` menüsü; taslakta da, açık
  sohbette de. Eski bir mesajın kaydındaki model (`grok-4.3` gibi) da çizilmez.
- **Tarayıcı model göndermez:** mesajın gövdesinde `model` alanı yok — yeni sohbetin doğuşunda da.
- **`models.js` ve `ModelPicker` gider**, testleriyle; stil sayfasında modelin adını çizen kural
  (`.model-label`, 82'den beri kimsenin çizmediği) de gider.

**Mimari kararı — sunucu tarayıcıdan model beklemez.** Tek model kalınca hangi modelin cevap verdiği
bir kural, ve kuralın tek evi sunucu *(FOUNDATION, Karar 4)*. Tarayıcı bir kimlik göndermeye devam
etseydi `models.js` `config.py`'nin `DEFAULT_MODEL`'ini elle kopyalamak zorunda kalırdı — iki dilde tek
değer, ve ikisini birbirine bağlayan tek şey bir yorum cümlesi. Bu yüzden:

- Yol `model` alanını okumaz; `append_message` `model` almaz.
- `config.engine_for` varsayılana düşmez: tek çağıranı `main.py`, tablonun kendi kimlikleriyle.
- `stream_answer` mesajın modelini okumaz; `Engine.stream` `model` almaz. Her tur `XaiEngine`'in
  varsayılanına, yani `config.DEFAULT_MODEL`'e gider. Prompt yazan rol (`write_once`,
  `PROMPT_MODEL`) değişmez.
- `Message.model` **kalır**: 146 ile 358 arasında yazılan mesajlar hangi modelle gönderildiklerini
  diskte taşıyor. Okunur ve sohbet yeniden yazılınca olduğu gibi geri yazılır — kayıt silinmez
  *(FOUNDATION, İlke 1 ve 2)* —, ama ne bir turu yönlendirir ne tarayıcıya gider. Kaldırmak, kaydı ilk
  yazımda geri dönülmez biçimde silerdi; tutmak bir alan ve üç satır.
- Sohbetin JSON'undaki mesajlarda `model` alanı yok: okuyan kalmadı, ve "hiçbir yerde görünmez".

Tasarımın 157'si *"uygulama onu her mesajla gönderir"* diyor; bu, prototipin paylaşılan verisinin
anlatımı, bir davranış değil — ekranda hiçbir fark yok. Rapora açık nokta olarak yazılır.

## Testler ne tutar, ne tutmaz

**Tutar** — `queen-agent/frontend/src/App.test.jsx`:

| # | Ne |
|---|---|
| 1 | Açık sohbette `Queen Flash` yok, `/Queen Flash/` adlı düğme yok *(yeni)* |
| 2 | Taslaktan doğan sohbetin mesaj gövdesinde `model` alanı yok *(bugünkü "born naming the model" yerine)* |
| 3 | `/api/model` hiç sorulmaz — bugünkü test, `Queen Flash`'ı beklemek yerine sohbetin açılmasını bekler |
| — | Silinir: "picking a model asks the server for nothing", "Queen Pro is on offer nowhere", "the model menu takes the one picker slot", "a draft says which model will answer it" |

**Tutar** — `ChatScreen.test.jsx`:

| # | Ne |
|---|---|
| 4 | Ayak `Edit⌄Skills⌄↑`, üç düğme, üçüncüsünün adı `Send` |
| 5 | Süren cevapta ayak `Edit⌄Skills⌄⏹`, üç düğme, üçüncüsü `Stop` |
| 6 | Sohbet yüklenirken ayaktaki seçiciler `[true, true]` kapalı |
| 7 | Ayağın seçici adları `["Plan", "Skills"]` |
| 8 | Kaydında `model: "grok-4.3"` taşıyan mesaj ekranda modeli çizmez *(yeni; bugün de yeşil — bir yokluğu tutar)* |
| — | Silinir: "offers the choice of model", "model picker shows what it is handed", "picking a model is passed up", "whether the model menu is open" |

**Tutar** — `workspace.css.test.js`:

| # | Ne |
|---|---|
| 9 | Stil sayfasında `.model-label` yok |

**Silinir** — `ModelPicker.test.jsx` ve `models.test.js`, kaldırılan davranışla birlikte.

**Tutar** — `queen-agent/backend/tests/test_chats_api.py`:

| # | Ne |
|---|---|
| 10 | `FakeEngine.stream` ve `ScriptedEngine.stream` `model` almaz: yolun motoru bir modelle çağırması her akış testini düşürür |
| 11 | `model: "grok-4.3"` ile gelen mesaj, sohbetin JSON'unda `model` alanı taşımaz *(yeni)* |
| 12 | Diskte `model: "deepseek-v4-pro"` taşıyan eski mesaj, sohbetin JSON'unda `model` alanı taşımaz *(yeni)* |
| — | Silinir: "asked with the model the turn named", "named no model asks for none", "carries no model but its messages do" |

**Tutar** — `test_stream_answer.py`:

| # | Ne |
|---|---|
| 13 | `ScriptedEngine.stream` `model` almaz; "the engine is asked without a model" testi yeniden gerçek olur |
| 14 | Açık satırın en yeni sorusundan yalnız skill okunur *(bugünkü "skill and model" testi skill'e iner)* |
| — | Silinir: Madde 146'nın bölümü (`_answered_by` ve üç testi) |

**Tutar** — `test_xai_engine.py`:

| # | Ne |
|---|---|
| 15 | `XaiEngine.stream`'in parametrelerinde `model` yok *(yeni)* |
| 16 | Her tur varsayılana gider: haritada iki istemci varken `stream` varsayılanınkini konuşturur |
| — | Silinir: "spoken by the model it names", "unknown or absent model is spoken by the default" |

**Tutar** — `test_config.py`:

| # | Ne |
|---|---|
| 17 | `engine_for` tablonun tutmadığı bir kimlikte `KeyError` verir *(varsayılana düşme, silinen bir modeli adlandıran kayıt içindi; artık hiçbir kayıt turu yönlendirmiyor, ve tek çağıran `main.py` tablonun kendisini geziyor)* |
| — | Silinir: "an unknown or absent model falls back to the default" |

`test_last_activity.py`'nin sahte motoru da `model` almaz.

**Yerinde kalır:** `test_chat.py`'nin `Message.model` testleri ve `test_file_chat_store.py`'nin gidiş
dönüş testleri — eski kayıt okunur ve geri yazılır. Yorumları bugünü söyleyecek biçimde düzelir.
`test_config.py`'nin ve `test_notebook.py`'nin `models.js`'e ve kutudaki satırlara dair yorumları
düzelir; iddiaları değişmez.

**Tutmaz:** ayağın tarayıcıda nasıl durduğunu — jsdom yerleşim yapmaz; tarayıcıda görülür.

## Bu turda yazılmayanlar

- Kaynak kodun hiçbiri — `ModelPicker.jsx`, `models.js`, `App.jsx`, `ChatScreen.jsx`, `useChat.js`,
  `workspace.css`, yol, use case'ler, motor, `FOUNDATION.md`, defterin yorumu — uygulama turunda.
- `dist` derlenmez: yöneten birleştirirken bir kez derler.

## Nasıl görülür

CLAUDE.md'deki dört satır, paralel. `npm test --prefix queen-agent/frontend` 1, 2, 4–7 ve 9'da kırmızı;
3 ve 8 bugün de yeşil. `python -m pytest queen-agent -q` 10–15 ve 17'de kırmızı — 10 ve 13 bütün akış
testlerini `TypeError`'la düşürür, çünkü bugünkü kod motora `model` geçiriyor. 16 bugün de yeşil.
queen-editor'ün iki satırı yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m358-model-secici-testler-plan.md).
