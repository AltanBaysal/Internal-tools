# Madde 419 — Kutunun araçlı isteği, test turu

**Koşu:** Queen Editor v9 — `roadmaps/2026-10-05-queen-editor-v9-roadmap.md` · **Dal:**
`feat/queen-editor-v9` · **Parça:** 419 · v9-4a · **Tur:** 1/2 — yalnız testler.
**Üstüne kurulduğu:** [m416 test turu](2026-10-06-queen-editor-m416-kara-kutu-testler-design.md),
[m416 uygulama turu](2026-10-06-queen-editor-m416-kara-kutu-uygulama-design.md),
[m418 test turu](2026-10-06-queen-editor-m418-ret-kontrolu-testler-design.md),
[m418 uygulama turu](2026-10-06-queen-editor-m418-ret-kontrolu-uygulama-design.md).

**Kullanıcıdan gereken — yok.** Madde 5 Ekim'de hizalandı; kararları yol haritasının *Maddelerin
kararları → v9-3* ve *v9-4* bölümlerinde, kullanıcının sözleriyle. Kutunun yeni yolunun biçimi teknik
bir karar, Claude'un. Ekran değişmez: başarısızlığı hata kartı olarak çizen 425.

## Kullanıcının sözü

*"agent bizim kara kutumuza istek atıyor agenta kara kuturmuz isteği dönüyor gibi düşün"*, *"kara
kutur düzgün cevap gelirse direkt zatne geri dönderiyor"*; *"Agenta gitmez dediğim kara kutu model red
verirse şey dönsün model hata döndü farklı şekilde dene tarzı gerçekten bir hata varsa teknik no
internet veya internal erro onlarıda direkt önderebilir"*, *"yani agetna bir şye dönsün yoksa agentic
döngü kırılır"*; cevabın onaylanınca tek seferde görünmesine: *"evet zaten şuan adım adım yazma
olayını ui da kapattık diye iliyorum bakarsın sen"* *(5 Ekim)*. Claude'un hizalamadaki kararı: kontrol
yalnız metin cevaplara bakar, araç çağrısı kontrolsüz geçer *(v9-3)*.

## Bugün ne oluyor

İstemci *([client.py](../../../queen-editor/backend/services/deepseek/client.py))* DeepSeek'e yalnız bir
talimat ve bir kullanıcı mesajı gönderebiliyor — araçsız, geçmişsiz —, ve cevabın yalnız metnini
okuyor. Kutu *([box.py](../../../queen-editor/backend/services/deepseek/box.py))* bu tek soruyu beş
denemeyle sorar, her metni kontrol ettirir, ve `Answer(text, failed)` döner. Başarısız bir `Answer`'ın
ret mi teknik bir hata mı olduğunu yalnız metni söylüyor. 420'nin agent'ı konuşmanın o ana kadarki
hâlini ve araçlarını gönderecek, ve cevabı bir metin ya da araç çağrıları olacak: bugün bunu taşıyan
bir yol yok.

## Kurallar

1. **Kutu konuşmayı ve araçları da alır:** mesajlar ve araçlar DeepSeek'e olduğu gibi gider — aynı
   istemciden, aynı model, adres, anahtar ve zaman aşımıyla. Mesajların ne olduğu çağıranın işi:
   sistem mesajı da onların içinde.
2. **Araç verilmezse istekte `tools` hiç olmaz.** QueenAgent döngünün son turunda araç vermiyor, ve
   420 adım sınırında onun yaptığını yapacak *(v9-4 — "queen agent ne yapıyorsa onu yapar")*.
3. **Cevap bütün döner:** metni — kırpılmış, yoksa boş — ve araç çağrıları, DeepSeek'in gönderdiği
   gibi ve gönderdiği sırayla; çağrı yoksa boş liste. Akış yok: cevap onaylanınca tek seferde döner.
4. **Araç çağrısı olan cevap kontrolsüz geçer** *(v9-3, Claude'un kararı)* — yanında metin olsa da:
   kontrol isteği gitmez. **İki türlü okunabilen yer, ve seçilen:** çağrının yanındaki metin de
   kontrol edilebilirdi; edilmez, çünkü o metin cevap değil, agent'ın çağrıyı yaparken söylediği bir
   ara söz, ve araç çağrısı olan cevabı geçirmek tek kural.
5. **Araç çağrısı olmayan metin 418'deki gibi kontrol edilir:** aynı `CHECK_INSTRUCTION`, metin
   birebir, kendi isteğinde, resimsiz ve araçsız; yalnız tam `APPROVED` geçirir.
6. **Hata da ret de aynı konuşmayı aynen yeniden gönderir**, aynı beş denemeden: HTTP hatası, bozuk
   cevap, ne metni ne araç çağrısı olan cevap, hiç gelmeyen cevap, ret, kontrolün kendi hatası.
7. **Beşi de olmazsa kutu yine fırlatmaz**, ve 418'deki gibi son deneme konuşur: retse *"Model hata
   döndü, farklı şekilde dene."*, teknik bir hataysa hatanın kendi metni.
8. **Başarısız cevap ret mi teknik mi olduğunu söyler** — iki yolda da, bugünkü soruda da:
   `refused` son deneme retse `True`, teknik bir hataysa `False`. Ekran (425) ikisini ayrı hata
   kartı olarak çizer. Anahtar yoksa hiçbir istek gitmez, ve bu teknik bir başarısızlık.
9. **Bugünkü prompt yazımı aynen çalışır:** `ask`'ın sorusu, istekleri ve cevabı değişmez; yazarlar,
   testleri, istemcinin testleri, `main.py` aynen.

**Değişmeyen:** `ask`'ın imzası; `Answer`'ın `text` ve `failed`'ı; `CHECK_INSTRUCTION`; `REFUSED`;
`TRIES`; yazarlar; `main.py`; döngü; ekran; QueenAgent.

## Arayüz — uygulama turunun vereceği

- `Box.converse(messages, tools=()) -> Answer` — 420'nin soracağı. `messages` DeepSeek'in mesaj
  listesi (`role`, `content`, gerekirse `tool_calls` ve `tool_call_id`), `tools` DeepSeek'in araç
  tanımları.
- `Answer(text, failed=False, refused=False, tool_calls=[])`:
  - **araç çağrısı:** `tool_calls` dolu — her biri `{"id", "type", "function": {"name",
    "arguments"}}`, DeepSeek'in gönderdiği gibi —, `text` yanındaki söz ya da `""`;
  - **metin:** `text` onaylanmış cevap, `tool_calls == []`;
  - **başarısızlık:** `failed` `True`, `text` cümle ya da hatanın kendi metni, `refused` hangisi
    olduğunu söyler, `tool_calls == []`.
- `Box.ask(system, text="", images=())` aynen; `Answer`'ı yeni alanları da taşır.

## Nasıl kanıtlanıyor

416 ve 418'deki gibi: kutu **gerçek istemciyle**, `test_deepseek_box`'ın `Answers`'ı — sırayla cevap
veren, her isteği not eden sahte HTTP — ile sınanır; böylece giden gövde ve okunan cevap istemcinin
gerçekten gönderdiği ve okuduğu. Araç çağrılı cevap DeepSeek'in biçiminde: `choices[0].message`'da
`content` `null` ve `tool_calls` listesi. `converse` bugün yok: testler onu çağırdıkları yerde
kırmızıya düşer, toplanırken değil.

## Yazılacak testler

### `backend/tests/test_deepseek_box.py` — dosyanın sonuna, *Madde 419* başlığıyla

Sabitler: agent'ın döngüsünün tutacağı biçimde bir konuşma — talimat, kullanıcının sorusu, modelin bir
araç çağrısı ve aracın cevabı —, bir araç tanımı, iki yeni araç çağrısı, ve DeepSeek'in araç çağrılı
cevabını kuran `calling(*çağrılar, text=None)`.

1. **Konuşma ve araçlar DeepSeek'e olduğu gibi gider** — metin cevap + `APPROVED`: ilk isteğin
   adresi, anahtarı, zaman aşımı istemcininki; gövdesi tam olarak `{"model", "messages": konuşma,
   "tools": araçlar}`.
2. **Araçsız konuşmada istekte `tools` yok** — gövde tam olarak `{"model", "messages": konuşma}`.
3. **Araç çağrısı bütün ve kontrolsüz döner** — tek çağrı, metinsiz: `tool_calls` o çağrı, `text`
   `""`, `failed` ve `refused` değil; tek istek.
4. **Çağrıların yanındaki söz de onlarla, kontrolsüz döner** — iki çağrı ve ` Kareye bakıyorum. `:
   `text` kırpılmış söz, `tool_calls` iki çağrı aynı sırayla; tek istek.
5. **Metin cevap prompt gibi kontrol edilir** — metin + `APPROVED`: metin döner, `tool_calls` `[]`;
   ikinci isteğin adresi, başlıkları, zaman aşımı ilkinin, gövdesi `CHECK_INSTRUCTION` ve yalnız
   metin — araç yok.
6. **Reddedilen metin aynı konuşmayı yeniden gönderir** — ret + `REFUSAL`, sonra araç çağrısı: çağrı
   döner, `failed` ve `refused` değil; üç istek, üçüncüsü ilkinin birebir aynısı.
7. **Başarısız istek aynı konuşmayı yeniden gönderir** — parametreli: HTTP `500`; bozuk cevap
   (`{"choices": []}`); ne metni ne çağrısı olan cevap (`content` `null`, `tool_calls` yok); bağlantı
   hatası. Sonra araç çağrısı: çağrı döner; iki istek, ikincisi ilkinin birebir aynısı.
8. **Beş ret cümle olarak, ret diye işaretli döner** — beş kez ret + `REFUSAL`, arkasında bir çağrı
   bekliyor: on istek; `failed`, `refused`, metin cümle, `tool_calls` `[]`.
9. **Beş teknik hata kendi sözleriyle, ret değil diye döner** — beş ayrı `503` (`meşgul 1` …
   `meşgul 5`), arkasında bir çağrı bekliyor: beş istek; `failed`, `refused` değil, metin
   `DeepSeek HTTP 503\nmeşgul 5`.
10. **Retlerden sonra son deneme teknikse ret değil** — dört kez ret + `REFUSAL`, sonra bağlantı
    hatası: dokuz istek; `failed`, `refused` değil, metin hatanın kendi sözleri.
11. **Anahtar yoksa istek gitmez, ve başarısızlık teknik** — sıfır istek; `failed`, `refused` değil;
    metinde `DEEPSEEK_API_KEY`.
12. **Prompt sorusunun başarısızlığı da ret mi teknik mi söyler** — parametreli, `ask`: beş kez ret
    + `REFUSAL` → `refused`; beş `503` → `refused` değil. İkisinde de `failed`.

## Kırmızı beklenen

- 1 – 11 (7'nin dört durumu dahil): `AttributeError` — kutunun `converse`'i yok.
- 12'nin iki durumu: `AttributeError` — `Answer`'ın `refused`'ı yok.
- 416 ve 418'in testleri, `test_deepseek_client.py`, `test_video_prompt_writer.py`,
  `test_composition_root.py` aynen yeşil; öteki her şey yeşil.

## Bilinçli olarak yapılmayan

- Agent, araçları, talimatı, sohbete yazdıkları — 420; ekran — 425; frontend ve `dist`.
- Akış (stream): cevap tek seferde döner.
- Mesajların ve araçların biçimini denetlemek: DeepSeek'e olduğu gibi gider; yanlışı DeepSeek'in
  kendi sözüyle teknik bir hata olarak döner.
- Denemeler arasında bekleme, deneme sayısının ayarı, günlük.
- İstemciye `converse` için ayrı test dosyası: kutu gerçek istemciyle sınandığı için giden gövde ve
  okunan cevap kutunun testlerinde görünüyor.
