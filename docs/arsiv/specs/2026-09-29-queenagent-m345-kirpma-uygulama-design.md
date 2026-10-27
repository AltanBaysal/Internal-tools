# Madde 345 — Sohbet baştan kırpılabilir · uygulama turu

**Kaynak:** [yol haritasının 345'i](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) — v9-1b.
**Testler:** [test turunun spec'i](2026-09-29-queenagent-m345-kirpma-testler-design.md); kırmızı
commit `8afa8342`. Davranış, kesimin yeri ve kapının sözleri orada; burada yalnız nasıl yapıldığı.

**Kullanıcıdan gereken:** hiçbir şey.

## Parçalar

Kural alanda, kapı sunumda, alanın şeması veride — CODE-STANDARD'ın üç katmanı. Yeni dosya bir tane:
use case.

**`domain/chat.py`** — kuralın evi:

- `Message.trimmed: int = 0` — bu mesaj satırın son mesajıyken sohbet kırpıldı, ve satırın baştan bu
  kadar mesajı modele gitmez oldu. Sıfır: kırpılmadı.
- `TRIM_KEEPS = 10_000` — kırpmanın bıraktığı en çok; kullanıcının sayısı.
- `sent_from(chat)` — açık satırda kesim taşıyan son mesajın `trimmed`'ı; yoksa 0. Sondan geriye
  yürür, ilk bulduğunu döner.
- `sent_messages(chat)` — `active_messages(chat)[sent_from(chat):]`: modele sohbetten giden.
- `chat_size` `sent_messages`'ı ölçer. Harf toplamı küçük bir `_size(messages)`'e çıkar, çünkü
  `trim_point` de aynı ölçüyü kullanır — iki kopya ölçü, ilk değişiklikte ayrılır.
- `trim_point(chat)` — açık satırda, `index > 0` ve `role == "user"` olan ilk mesaj ki
  `_size(said[index:]) <= TRIM_KEEPS`; hiçbiri değilse bu soruların sonuncusu; hiç soru yoksa 0.
  Önceki kesimi bilmesi gerekmez: dolu bir sohbette önceki kesimden öncesi 50.000'in üstündedir, ve
  ölçü kesim ilerledikçe yalnız küçülür.

**`domain/errors.py`** — `ChatNotFull`: dolmamış sohbet kırpılmaz.

**`domain/usecases/trim_chat.py`** — `trim_chat(chat_store, project_id, chat_id)`: sohbeti okur
(`ChatNotFound`), dolu değilse `ChatNotFull`; açık satırın son mesajını `trimmed=trim_point(chat)` ile
değiştirip yazar, ve güncel sohbeti döner. Son mesajı değiştirmek `append_message`'ın `_with`'inin
eşi: kök satırsa `messages`'ın sonu, sürümse o sürümün `messages`'ının sonu.

**`domain/usecases/stream_answer.py`** — `_conversation` `sent_messages`'ı gönderir. Skill ve model
hâlâ `active_messages`'tan okunur: son soru her zaman kesimin ardında.

**`data/file_chat_store.py`** — `"trimmed"` yalnız sıfır değilse yazılır; okurken yoksa 0.

**`presentation/routes.py`** — `POST /api/projects/<p>/chats/<c>/trim`: `404 chat not found`,
`400 this chat is not full`, yoksa `{}`. `_chat_json`'a `"trimmed": sent_from(chat)`. Rotaların
başındaki *There is no PATCH here* yorumu yeni kapıyı da sayar.

**`CODE-STANDARD.md`** — `chats/<id>.json` satırının *Written when*'ine *and on Continue here*.

## Dokunulmayan

Açılan dosyalar kutusu (`context_box.py`) `active_messages`'ı okumaya devam eder: kutu mesaj değil,
ve kırpma onun sorusu değil. Ön uç: v9-1c ve v9-1d'nin. `dist` bu turda derlenmez; birleştiren derler.

## Nasıl görülür

Dört satır; on altı kırmızı yeşile döner, öteki her şey yeşil kalır.
