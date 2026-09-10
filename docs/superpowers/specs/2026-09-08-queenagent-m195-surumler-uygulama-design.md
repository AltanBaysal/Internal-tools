# Madde 195 · uygulama turu — düzenlenen mesaj sohbeti sürümler

**Kaynağı:** [test turu](2026-09-08-queenagent-m195-surumler-testler-design.md), ve onun
kaynağı [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 195.

Kırmızı: arka uçta 25, ön yüzde 8.

---

## Alan — `chat.py`

`Version(id, parent, at, messages)` ve `Chat`'e iki alan: `versions`, `active`.

```python
def active_messages(chat):
    return _line(chat, chat.active)
```

`_line` özyineli: adı boş olan ya da bilinmeyen çizgi `chat.messages`; bir sürüm ise
`_line(parent)[:at] + messages`. Bilinmeyen adın ilk çizgiye düşmesi elle düzenlenmiş bir dosyanın
çökmemesi için, ve `FileChatStore`'un alan alan okumasıyla aynı gerekçe.

`last_activity`, `is_owed_an_answer`, `last_context` bu işlevden okuyor. `chat_title` okumuyor:
başlık ilk mesajın ve kımıldamıyor.

`variants_of(chat)` açık çizginin her sırası için `{"index", "of", "versions"}` üretiyor. Bir
sıradaki taban çizgi, o sırayı **kendi mesajıyla** dolduran çizgi: açık zincirde o sırayı taşıyan
çizgi tam orada ayrılıyorsa tabanı ebeveyni, değilse kendisi. Seçenekler tabanla başlıyor, ardından
`chat.versions` sırasıyla o noktadan ayrılanlar — yani doğuş sırası, ve okların yönü bu.

## Diskte — `file_chat_store.py`

`versions` ve `active` yalnız doluyken yazılıyor; okurken `raw.get(...)` ile boşa düşüyor. Bir
sürümün mesajları `_message_json`'ın aynısından geçiyor, çünkü aynı `Message`.

## Kural — `append_message.py`

`branch_at=None, line_id=""`. Verildiğinde: mesaj **yeni bir sürümün ilk mesajı**, `parent` sohbetin
açık çizgisi, `at` verilen sıra, ve `active` yeni sürüm. Verilmediğinde mesaj **açık çizginin**
sonuna gidiyor — ilk çizginin değil, ki bir sürümün sorusunu cevap kendi çizgisinde bulsun.

Boş metin kontrolü ikisinin de önünde: reddedilen bir cümle ardında ne sohbet ne sürüm bırakıyor.

## Kapılar — `routes.py`

- `POST /messages` gövdesinde `from` taşıyabiliyor: sürüm açan sıradır, ve akış ile bütün
  reddedişler olduğu gibi kalıyor.
- `POST /chats/<id>/version`, gövdesi `{"version": ...}`. Bilinmeyen ad **404**, ve açık olan
  kımıldamıyor. `stop` ve `permission`'ın kardeşi.
- `_chat_json`'ın `messages`'ı **açık çizgi**, ve her mesaj `variants` taşıyor.
- *"Bir sohbet yazıldıktan sonra hiçbir şeyi değişmez"* yorumu artık doğru değil: açık sürüm
  değişiyor. Yorum düzeltiliyor.

## Ekran

- **`Composer`** `filled` alıyor: `{text, token}`. `token` değişince kutuya o metin düşüyor —
  aynı mesaja iki kez basmak da çalışsın diye, metnin kendisi değil damgası izleniyor.
- **`ChatScreen`** `editing` tutuyor *(hangi sıra ve hangi metin)*. Kullanıcı mesajında
  **Edit message**; gönderim `onSend(text, editing?.index ?? null)`.
- **Sürüm şeridi** `of > 1` olan mesajın altında: `‹`, `2/2`, `›` — adları `Previous version` ve
  `Next version`, uçlarda kapalı. Basınca `onVersion(id)`.
- **`useChat`** `send`'e sıra ekliyor *(gövdeye `from`)*, ve `version(id)` diye bir çağrı: kapıya
  yazıyor, sonra kaydı yeniden okuyor.
- **`App`** ikisini bağlıyor.

## Yeşilin nasıl görüleceği

Dört sabit satır. Arka uçta 917, ön yüzde 630 — 33 kırmızının hepsi yeşile dönüyor, ve
`queen-editor` **739 · 591** yerinde. `dist` bu commit'in içinde.
