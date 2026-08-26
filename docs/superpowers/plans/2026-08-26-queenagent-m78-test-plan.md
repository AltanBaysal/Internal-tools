# Madde 78 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-26-queenagent-m78-tool-satiri-testler-design.md](../specs/2026-08-26-queenagent-m78-tool-satiri-testler-design.md)
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Testlerin konuşacağı adlar

Madde 66'nın dersi: içe aktarılamayan bir ad `pytest`i toplama hatasına düşürüyor ve suite kırmızı
değil bozuk oluyor. İki ad bu turda doğar, ikisi de aynı adı taşır:

- **`ToolCall.outcome: str = ""`** — `tool` ve `target`'ın yanında. Boşken diske yazılmaz, taşımayan
  eski kayıt boş okunur. `calls`, `stopped` ve `usage` ile aynı kural, dördüncü kez.
- **`ToolResult`'ın `outcome` alanı** — `text`, `created`, `target`'ın yanında, varsayılanı `""`.
  Bir `namedtuple`, yani sonuncu olmak zorunda.

Bu turda yalnız adlar: alan var, kimse doldurmaz.

## Dosyalar

`backend/features/workspace/domain/chat.py` · `backend/features/workspace/domain/tools.py` *(yalnız
`ToolResult`'ın tanımı)*
`backend/tests/test_tools.py` · `test_stream_answer.py` · `test_file_chat_store.py` ·
`test_chats_api.py` · `frontend/src/features/workspace/ChatScreen.test.jsx`

## Testler

### `test_tools.py` — altı test

Var olan `_files`, `_with` ve `STRUCTURE` kullanılır. Bugünkü `_call` yardımcısı yalnız `.text`
döndürüyor, yani özet için çağrının kendisine bakan ikinci bir yardımcı gerekir.

Listeleme kaç dosya olduğunu söylüyor. Okuma kaç satır olduğunu söylüyor. Yaratma kaydedildiğini
söylüyor. Düzenleme değiştirildiğini söylüyor. Prompt kurma kaç prompt yazıldığını söylüyor. Ve
**reddedilen bir çağrı reddi söylüyor** — olmayan bir dosyayı okumak turun gerçekten yaptığı bir
şey, ve gizlenmiyor.

### `test_stream_answer.py` — bir test

Turun sakladığı çağrı özeti taşıyor. 66'nın testleri `ToolCall(tool, target)` biçiminde eşitlik
kuruyor ve üçüncü alan varsayılanlı olduğu için **kırılmıyorlar** — ama o testlerin hiçbiri özetin
kayda geçtiğini sormuyor, o yüzden bu ayrıca soruluyor.

### `test_file_chat_store.py` — iki test

Özet gidiş dönüş hayatta kalıyor. Boşken `outcome` diske hiç yazılmıyor.

### `test_chats_api.py` — bir test

Mesajın JSON'u her çağrının özetini taşıyor, boşken de — tarayıcı eline verilen şeyi çiziyor.

### `ChatScreen.test.jsx` — beş test

Satır `⏺` ile başlıyor ve aracın adını parantezli konusuyla yazıyor. Konusu olmayan çağrı parantez
taşımıyor. Özeti olan çağrı ikinci bir satır çiziyor ve o satır `⎿` taşıyor. Özeti olmayan çağrı
ikinci satır çizmiyor. Akan cevapta da aynı biçim.

## Beklenen kırmızı

| Dosya | Kırmızı | Doğduğu anda yeşil |
|---|---|---|
| `test_tools.py` | 7 | — araçlar özet üretmiyor |
| `test_stream_answer.py` | 1 | — |
| `test_file_chat_store.py` | 1 | 1 — depo `outcome` bilmiyor, yani yazmıyor da |
| `test_chats_api.py` | 1 | — |
| `ChatScreen.test.jsx` | 5 | — |

**Arka uçta 10 yeni kırmızı** *(defterin iki kırmızısı ayrı, toplam 12 failed / 432 passed)*,
**ön yüzde 5** *(5 failed / 492 passed)*.

**Koşuda çıkan iki düzeltme, ikisi de tahminde:**

- Listeleme iki test oldu, bir değil: "kaç dosya" ile "hiç dosya yok" ayrı cümleler, ve sıfırı
  saymak ikincisini söylemez.
- *"Özeti olmayan çağrı ikinci satır çizmiyor"* testini bekçi sanmıştım. Değil: aynı testte üst
  satırın çizildiği de soruluyor, ve o satır henüz yok. Bir yokluk iddiasının yanına konan varlık
  iddiası testi kırmızıya taşıyor.

**Ve bir biçim düzeltmesi.** İki test `querySelector(...).textContent` ile yazılmıştı, yani eleman
yokken `TypeError` veriyordu — ne aradığını söylemeyen bir başarısızlık. Metinle aranır hâle
getirildi; kayıp eleman artık kendi adıyla rapor ediliyor. Aynı hata Madde 68'de de yapılmıştı.

**Mekanik kırmızı beklenmiyor.** `ToolCall` bir alan kazanıyor ama varsayılanlı, ve 66'nın
eşitlik testleri iki tarafta da aynı varsayılanı görüyor. `ToolResult` bir `namedtuple` ve yeni
alan sona ekleniyor, yani konum sırasıyla kurulan hiçbir çağrı bozulmuyor. Düşen olursa mekanik
değil gerçek bir kırılmadır.

## Bu turda yapılmayan

Araçların özet üretmesi · `stream_answer`'ın özeti taşıması · deponun yazma/okuma yolları ·
`_chat_json`'ın alanı · `ChatScreen`'in iki katmanlı satırı · `workspace.css`. Hepsi ikinci tur.
`dist` derlenmez.
