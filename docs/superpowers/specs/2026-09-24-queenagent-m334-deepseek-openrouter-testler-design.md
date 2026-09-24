# Madde 334 · test turu — DeepSeek istekleri şimdilik OpenRouter'dan, DeepSeek'in kendisine

**Kaynağı:** [v9 yol haritası](../roadmaps/2026-09-21-queen-agent-v9-roadmap.md), Madde 334.
**Dal:** `feat/queenagent-v9` · **Bu tur yalnız test yazar.**

---

## Kullanıcıdan gereken

**1 · Karar verildi — model adı** *(kullanıcı, 25 Eylül — "şuan deepsek 4.1 flasj kullanıyoruz")*.
İki menü satırı da OpenRouter'a **`deepseek/deepseek-v4.1-flash`** olarak gidiyor. DeepSeek'in kendi
API'si 14 Eylül'den beri iki satıra da V4.1 Flash ile cevap veriyordu *(BACKLOG.md, "Model menüsü
DeepSeek'in 10 Eylül değişikliğine göre yenilenecek")*; bu, bugünkü davranışı koruyor. Ad
OpenRouter'ın kendi model sayfasından doğrulandı *(25 Eylül: "DeepSeek: DeepSeek V4.1 Flash")*.
Madde 149'un tarihli adları kullanılmıyor.

**2 · Karar verildi — OpenRouter'da yalnız DeepSeek** *(kullanıcı, 25 Eylül — "Deepeseki direkt
deepsekiin kendin kullanalım open routerda deepseke biz ödeme yapan kadar olur mu", ardından "yap
devam")*. 24 Eylül'deki *"bir vendor ile sınırlaman gerek yok"* kararının yerine geçiyor. Aşağıda
*Sabitleme*.

**3 · Son deneme için (bu tur için değil):** `OPENROUTER_API_KEY` Colab Secrets'ta bu adla tanımlı ve
deftere erişimi açık; yerelde `python main.py`'den önce kabukta export edilmiş. Kullanıcı anahtarın
hazır olduğunu söyledi.

---

## Bugün ne oluyor

`config.MODELS`'in iki DeepSeek satırı `https://api.deepseek.com` adresine, `DEEPSEEK_API_KEY` ile
gidiyor. Hesapta kredi olmadığı için cevap gelmiyor. İstemci, satırın **anahtarını** (uygulamanın
id'sini) modelin adı olarak gönderiyor: `main.py` her `XaiClient`'ı `model` ile kuruyor. Gövdeye
satırdan gelen hiçbir alan girmiyor.

## Ne kurulacak

- İki DeepSeek satırı `https://openrouter.ai/api/v1` adresine, `OPENROUTER_API_KEY` ile gidiyor.
- `config.OPENROUTER_API_KEY` öteki iki anahtarın yolundan geliyor: çevreden.
- `engine_for` iki değer daha veriyor:
  - **dördüncü — sağlayıcıya söylenen ad.** DeepSeek çifti için `deepseek/deepseek-v4.1-flash`;
    kendi adını ayrıca söylemeyen satır *(Grok)* için id'nin kendisi.
  - **beşinci — satırın gövdeye eklediği alanlar.** DeepSeek çifti için
    `{"provider": {"order": ["deepseek"], "allow_fallbacks": False}}`; Grok için hiçbir şey.
- `XaiClient` bir `extra` alıyor ve iki yolda da *(tek seferlik yazım ve akış)* gövdeye katıyor —
  önce `extra`, sonra istemcinin kendi alanları.
- `main.py` her istemciyi dördüncü değerle kuruyor ve beşinciyi `extra` olarak veriyor.
- Defter `OPENROUTER_API_KEY`'i Secrets'tan okuyor, yoksa duruyor ve ne yapılacağını söylüyor,
  uygulamaya çevreden geçiriyor.
- **Değişmeyen:** `XaiEngine`, `stream_answer` ve yukarısı, ön yüzün tamamı *(menü, id'ler,
  varsayılan)*, Grok satırı ve onun isteği.

## Sabitleme

**İstek OpenRouter'da yalnız DeepSeek'e gidiyor; DeepSeek cevap vermezse hata görünüyor.** Bir hız ya
da fiyat tercihi değil, sözleşme seçimi: cevap veren sağlayıcının kullanım şartları geçerli, en az
birininki bu işi yasaklıyor, ve DeepSeek'inkiler doğrudan API'de bugüne kadar geçerli olanlarla aynı.

**Madde 149'un yolu, sağlayıcısı DeepSeek olarak** *(`27ff05d3`)*. 149 sabitlemeyi satırın `extra`
alanıyla gövdeye koymuştu: `{"provider": {"order": ["deepinfra"], "allow_fallbacks": False}}`. Aynı
biçim, `deepinfra` yerine `deepseek` ile. 149'un Colab denemesi bu biçimin tuttuğunu göstermişti —
429 hatası `provider_name: DeepInfra` diyordu.

**Test üç yerde, çünkü sabitleme üç katmandan geçiyor:**

- `config` — DeepSeek çiftinin beşinci değeri tam olarak o sözlük; Grok'unki boş. Sözleşme iddiası
  burada, çünkü hangi satırın neyi taşıdığı config'in kararı.
- `client` — `extra` iki yolda da gövdeye giriyor, ve istemcinin kendi alanları (`model`,
  `messages`, `stream`) onun üstüne yazılıyor. İstemci ne taşıdığını bilmiyor; yalnız taşıyor.
- `main.py` — beşinci değer istemciye veriliyor *(dosya okunarak)*.

**İstemcinin kendi alanları üstte.** Bir satır ekler, ele geçiremez: `extra` önce, istemcinin
alanları sonra yazılıyor. Bir yasak ad listesi yerine sıra — liste ikinci bir güncel tutulacak yer
olurdu ve geride kaldığı gün açık kalırdı. Sıra bedava; hangisi seçilecekse o seçiliyor, ve testi
güvenli olanı istiyor.

## Teknik kararlar ve gerekçeleri

**Menünün id'leri değişmiyor; sağlayıcıya söylenen ad satırda duruyor.** Reddedilen iki yol:

- *Id'leri OpenRouter'ın adına çevirmek.* Diskte `deepseek-v4-pro` yazan her mesaj bilinmeyen id olur
  ve varsayılana düşer. Ayrıca ön yüz, `dist` ve `DEFAULT_MODEL`/`PROMPT_MODEL` değişir, ve DeepSeek'e
  dönüşte hepsi bir daha değişir.
- *Adı istemcide çevirmek.* Bir servis model adı öğrenir; bir id'nin ne demek olduğu `config.py`'nin
  tablosunun işi *(FOUNDATION, Karar 6)*.

**Ad ve sabitleme iki ayrı değer, tek bir gövde sözlüğü değil.** Adı da `extra`'ya koymak bir değer
eksiltirdi, ama o zaman istemci bir modelle kurulup başka bir modeli gönderirdi, ve `extra`'nın
istemcinin alanlarını ezmesine izin vermek gerekirdi. İki ayrı değerde her bilginin tek evi var: ad
istemcinin `model`'i, sabitleme `extra`.

**Değerler `engine_for`'dan geliyor**, bileşim kökü tabloyu kendisi okumuyor: config'in kendi yorumu
*"engine_for is the one place"* diyor. Testler `engine_for` üzerinden soruyor, satırın alan adlarını
değil — alanların yazılışı uygulama turunun.

**`DEEPSEEK_API_KEY` yerinde kalıyor** — `config.py`'deki sabit de, defterin istediği sır da. Hiçbir
satır onu harcamayacak, ama madde **şimdilik** diyor ve dönüş ayrı bir madde. Emsal Madde 202: Grok
satırı kullanılmadığı hâlde dönüş yolu olarak bilerek tutuldu. Sırrı defterden düşürmek maddenin
istemediği görünür bir değişiklik olurdu; tutmanın bugün bedeli yok, sır zaten Secrets'ta.

**Defter `OPENROUTER_API_KEY`'i şart koşuyor.** Menüdeki iki model de ve kareyi yazan
(`PROMPT_MODEL`) de onu harcıyor; o anahtar olmadan açılan bir koşu hiçbir şeye cevap veremez.
146 ve 149'un kuralı.

**`x-grok-conv-id` için test yok.** İstemci o başlığı adreste `x.ai` geçiyorsa gönderiyor;
`openrouter.ai`'de geçmiyor. Test bugün yeşil olurdu ve olmayan bir durumu beklerdi.

**`extra` yokken gövdenin değişmediğine ayrı test yok.** Grok'un beşinci değerinin boş olduğu config'te
soruluyor; istemcinin bugünkü testleri `extra` vermeden kuruyor ve gövdeyi zaten soruyor.

## Testler

### `backend/tests/test_config.py`

1. **`test_the_openrouter_key_comes_from_the_environment`** *(yeni)* — çevreye konan değer
   `config.OPENROUTER_API_KEY` oluyor.
2. **`test_the_deepseek_pair_is_sent_under_openrouter_s_names`** *(yeni)* — iki satırın da
   `engine_for(...)[3]`'ü `deepseek/deepseek-v4.1-flash`.
3. **`test_grok_is_sent_under_its_own_id`** *(yeni)* — `engine_for("grok-4.3")[3] == "grok-4.3"`.
4. **`test_the_deepseek_pair_is_answered_by_deepseek_alone`** *(yeni)* — iki satırın da
   `engine_for(...)[4]`'ü `{"provider": {"order": ["deepseek"], "allow_fallbacks": False}}`.
5. **`test_grok_adds_nothing_to_its_body`** *(yeni)* — `engine_for("grok-4.3")[4]` boş, hangi
   biçimde olursa.

### `backend/tests/test_xai_client.py`

6. **`test_what_a_row_adds_reaches_a_one_shot_request`** *(yeni)* — `extra` ile kurulan istemcinin
   `write_once` gövdesinde `provider` alanı. Kareyi yazanın yolu.
7. **`test_what_a_row_adds_reaches_a_streamed_request_too`** *(yeni)* — aynısı `stream` için.
8. **`test_the_clients_own_fields_win_over_what_a_row_adds`** *(yeni)* — `extra` içinde `model`,
   `messages`, `stream`; gövdede istemcinin kendi değerleri.

### `backend/tests/test_composition.py`

9. **`test_each_client_is_built_with_the_name_its_provider_knows`** *(yeni)* — `main.py`'nin
   metninde `config.engine_for(model)[3]`.
10. **`test_each_client_is_handed_what_its_row_adds_to_the_body`** *(yeni)* — `main.py`'nin metninde
    `config.engine_for(model)[4]`.

İkisi de dosya okunarak, bu dosyanın kendi usulünce: `main.py`'yi içeri almak kullanıcının veri
köküne karşı gerçek bir uygulama kurar.

### `backend/tests/test_notebook.py`

11. **`test_the_openrouter_key_comes_from_secrets`** *(yeni)* — `userdata.get("OPENROUTER_API_KEY")`.
12. **`test_a_missing_openrouter_key_says_what_to_do`** *(yeni)* — bir hücrede
    `assert OPENROUTER_API_KEY`, ve Secrets ile anahtarın adını söylüyor.
13. **`test_the_openrouter_key_travels_to_the_app_in_the_environment`** *(yeni)* — Serve hücresinde
    `"OPENROUTER_API_KEY": OPENROUTER_API_KEY`.

## Değişen

Eski davranışı isteyen ya da gerekçesi bu maddeyle düşen mevcut testler:

| Test | Bugün istediği | Bu turdan sonra |
|---|---|---|
| `test_config.py` · `test_the_three_models_resolve_to_their_provider` | DeepSeek çifti `https://api.deepseek.com` | çift `https://openrouter.ai/api/v1`; Grok aynı. **Kırmızı.** |
| `test_config.py` · `test_each_model_names_the_key_it_spends` | çift `DEEPSEEK_API_KEY` | çift `OPENROUTER_API_KEY`; Grok aynı. **Kırmızı.** |
| `test_config.py` · `test_a_known_model_resolves_to_its_own_wiring` | üç değeri açıyor, adres `api.deepseek.com` | ilk iki değeri okuyor *(değer sayısına bağlanmıyor)*: id hâlâ uygulamanın, adres OpenRouter. **Kırmızı.** |
| `test_config.py` · `test_the_grok_row_is_kept_as_the_way_back` | yorumu defterin *"üç sırrını"* sayıyor | yorum sayı söylemiyor — sırlar dört oluyor. Yeşil. |
| `test_notebook.py` · `test_no_api_key_is_ever_printed` | iki anahtarın değeri basılmıyor | üçüncüsü de listede. Kilit: bugün de yarın da yeşil. |
| `test_notebook.py` · `test_a_missing_deepseek_key_says_what_to_do` | *"menü üç satır çiziyor"* gerekçesi | yalnız docstring: sır dönüş yolu olarak isteniyor. Yeşil. |

**Dokunulmayan ve hâlâ doğru olanlar:** `test_an_unknown_or_absent_model_falls_back_to_the_default`
(`[0]` okuyor), `test_the_deepseek_key_comes_from_the_environment`, defterin öteki DeepSeek testleri,
`test_xai_client.py`'nin `test_deepseek_is_not_sent_the_grok_conversation_header`'ı *(istemci her
adrese gidebiliyor, ve o adres dönüş yolu)*.

## Yeşil kalması gerekenler

- **`test_xai_client.py`'nin geri kalanı** — `extra` vermeden kurulan istemci bugünkü gövdeyi
  gönderiyor.
- **`test_xai_engine.py`, `test_stream_answer.py`, `test_chats_api.py`, `test_file_chat_store.py`** —
  hepsi uygulamanın id'leriyle konuşuyor ve id'ler değişmiyor.
- **Ön yüzün bütün takımı.** *"Menü aynı kalıyor"* sözünü `models.test.js`, `ModelPicker.test.jsx`
  ve öteki bileşen testleri zaten tutuyor; ön yüze yeni test yazılmıyor.
- **queen-editor** kımıldamıyor.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, birebir. queen-agent'ın arka ucunda **16 kırmızı**:

- `test_the_openrouter_key_comes_from_the_environment` — `config`'te `OPENROUTER_API_KEY` yok
  (`AttributeError`).
- `test_the_three_models_resolve_to_their_provider` — adres hâlâ `https://api.deepseek.com`.
- `test_each_model_names_the_key_it_spends` — anahtar hâlâ `DEEPSEEK_API_KEY`.
- `test_a_known_model_resolves_to_its_own_wiring` — adres hâlâ `https://api.deepseek.com`.
- `test_the_deepseek_pair_is_sent_under_openrouter_s_names`, `test_grok_is_sent_under_its_own_id` —
  dördüncü değer yok (`IndexError`).
- `test_the_deepseek_pair_is_answered_by_deepseek_alone`, `test_grok_adds_nothing_to_its_body` —
  beşinci değer yok (`IndexError`).
- `test_xai_client.py`'nin üçü — `XaiClient` `extra` almıyor (`TypeError: ... unexpected keyword argument
  'extra'`).
- `test_composition.py`'nin ikisi — `main.py` istemciyi `model` ile kuruyor, `engine_for(model)[3]`
  ve `[4]` metinde yok.
- Defterin üç testi — defterde `OPENROUTER_API_KEY` hiç geçmiyor.

Ön yüz ve queen-editor'de yeni kırmızı yok.

## Uygulama turuna kalanlar

Test edilmeyen, ama bu maddeyle yalan olacak yazılar:

- `models.js`'in *"An id is what the provider is told the model is called -- client.py sends it as
  the model field"* yorumu DeepSeek çifti için artık doğru değil. Yorum değişikliği; paket
  değişirse `dist` aynı commit'te.
- `config.py`'nin anahtar ve tablo yorumları, defterin CONFIG ve Serve hücrelerindeki *"iki anahtar"*
  / *"üç şey"* yorumları, ve CONFIG'in `print` satırındaki anahtar listesi.
- `README.md` yerel çalıştırmada yalnız `XAI_API_KEY`'i export ettiriyor.

## Bilerek kapsam dışı

- **DeepSeek'in kendi API'sine dönüş** — ayrı madde.
- **Menünün fiyatları ve BACKLOG'daki açık Pro sorusu** — menü aynı kalıyor *(madde metni)*.
- **OpenRouter'ın 429'u** — 149'un denemesinde görülmüştü; sabitlemeyle DeepSeek doluysa istek
  düşüyor ve hata görünüyor, kullanıcının istediği bu. Uygulama kendisi tekrar denemiyor.
- **İsteğin gerçekten cevap alması** — test söyleyemez; kullanıcının son denemesi söyler.
