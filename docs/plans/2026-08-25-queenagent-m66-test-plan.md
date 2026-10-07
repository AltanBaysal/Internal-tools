# Madde 66 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-25-queenagent-m66-tool-satiri-testler-design.md](../specs/2026-08-25-queenagent-m66-tool-satiri-testler-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Testlerin konuşacağı adlar

Testler yazılabilmek için adlara ihtiyaç duyuyor; ikinci tur bunları var edecek.

- **`ToolCall(tool, target)`** — `chat.py`'de donmuş bir dataclass. **Tek tip**, iki iş: akışta
  yayılan parça da bu, mesajda saklanan kayıt da. İkiye bölmek aynı şeyi iki adla anlatmak olurdu.
  `target` hedefsiz çağrıda `""`.
- **`Message.calls: tuple = ()`** — `files`'ın yanında, aynı kuralla.
- **`ToolResult`** üçüncü bir alan kazanır: `target`. Adın nasıl temizlendiği ve çakışmanın nasıl
  çözüldüğü `tools.py`'de yaşıyor; hedefi başka yerde hesaplamak o kuralın ikinci kopyası olurdu.
- **SSE olayı `call`**, gövdesi `{"tool": ..., "target": ...}` — `file` olayının komşusu.
- Diskte ve API'de: `{"tool": "read_file", "target": "aylin.json"}`; `target` boşken yazılmaz.

## Dosyalar

`backend/tests/test_tools.py` · `test_stream_answer.py` · `test_file_chat_store.py` ·
`test_chats_api.py` · `frontend/src/features/workspace/ChatScreen.test.jsx` ·
`frontend/src/features/workspace/useChat.test.jsx` *(yeni dosya — bugün yok)*

## Testler

### `test_tools.py` — dört test

`run_tool`'un döndürdüğü sonuç artık hedefini de söylüyor. `read_file` temizlenmiş adı;
`create_file` ad çakıştığında **yazılan** adı (`aylin.json` isteyip `aylin-2.json` olan);
`list_files` boş hedefi; `edit_file` ile `build_prompts` kendi adlarını.

### `test_stream_answer.py` — dört test

Var olan `ScriptedEngine` ve `call()` yardımcıları kullanılır, yenisi yazılmaz.

Araç çağıran bir tur, ürettiği sıraya her çağrı için bir `ToolCall` koyar; sıra ve içerik
doğrulanır. Tur bitince diske düşen cevap mesajı aynı çağrıları `calls` olarak taşır. Araç
çağırmayan cevabın `calls`'ı boş. Aynı dosya iki kez okunursa **iki** kayıt olur — `files`'taki
tekrar ayıklaması buraya taşınmaz, iki okuma iki adımdır.

### `test_file_chat_store.py` — iki test

Çağrısı olan mesaj `calls` ile yazılıyor, olmayanın JSON'unda alan **hiç yok**. `calls` taşımayan
bir sohbet dosyası okununca mesajlar boş `calls` ile geliyor.

### `test_chats_api.py` — iki test

Cevap akışı her çağrı için bir `call` olayı yayıyor ve olay araç adı ile hedefi taşıyor. Sohbetin
GET'i mesajların `calls` alanını döndürüyor.

### `ChatScreen.test.jsx` — üç test

Kayıtlı bir mesaj çağrılarını satır satır çiziyor; hedefi olan satır hedefi de yazıyor. Hedefsiz
çağrı yalnız araç adını yazıyor, arkasında boş bir ayraç bırakmıyor. Çağrısı olmayan mesaj hiçbir
kap çizmiyor.

### `App.test.jsx` — bir test

Akıştan gelen `call` olayı çiziliyor ve sunucunun kaydı geldiğinde **ikiye katlanmıyor**: kayıt aynı
çağrıyı taşıdığı için akıştan çizilenler bırakılıyor — dosya kartlarının bugün yaptığı devrin
aynısı. Dosyadaki `sseResponse` yardımcısı kullanılır.

*(Plan önce bunun için yeni bir `useChat.test.jsx` öngörüyordu. Gereksiz çıktı: `App.test.jsx`'te
hazır bir SSE sahtesi var ve testi gerçek `useChat` + gerçek `ChatScreen` üstünden koşturuyor, yani
sahte bir konak bileşenden daha doğrusunu söylüyor.)*

## Beklenen kırmızı

**Yirmi test kırmızı** — on altısı `pytest`, dördü `npm test`. Sebep tek: bugün ne `calls` alanı
var, ne `target` taşıyan bir sonuç, ne de bunları çizen bir satır.

**`ToolCall` tipi bu turda yazıldı.** Testler onu içe aktarıyor ve tip yokken `pytest` **toplama
hatası** veriyordu — yani suite hiç koşmuyor, geri kalan 385 testin durumu da görünmüyordu. Bozuk
bir suite kırmızı sayılmaz. Tip bir veri tanımı, davranış değil: yazılmasıyla birlikte testler
davranış üzerinde düşmeye başladı, ki kırmızının anlamlı olduğu yer orası.

**"Çağrısı olmayan mesaj hiçbir kap çizmiyor" testi bugün yeşil geçiyor** — ortada `.tool-calls`
diye bir şey yok. İkinci turdan sonra anlam kazanıyor: kap doğduğunda boş hâlinin çizilmediğini
tutan tek şey o.

## Bu turda yapılmayan

`tools.py`, `stream_answer.py`, `file_chat_store.py`, `routes.py`, `ChatScreen.jsx` ve `useChat.js`
— hiçbirine dokunulmaz. `chat.py`'ye yalnız `ToolCall` tipi girdi, `Message.calls` alanı girmedi.
`dist` derlenmez: ön yüz kaynağı değişmiyor.
