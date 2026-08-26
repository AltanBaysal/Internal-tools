# Madde 81 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-26-queenagent-m81-durduruldu-yazar-uygulama-design.md](../specs/2026-08-26-queenagent-m81-durduruldu-yazar-uygulama-design.md)
**Kırmızı testler:** `1bc84f5` — arka uçta 2, ön yüzde 4.
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Sıra

### 1. `append_message.py` — kural üçüncü şıkkını alır

Şart ve üstündeki açıklama birlikte değişiyor:

```python
    # A message has to carry something -- a word said, a file made, or a stop. The user's own
    # message never carries a file or that flag, so an empty one they typed is still refused. The
    # second case is the answer of a model that worked without speaking, and what it made is the
    # answer; the third is an answer somebody cut before it said anything, and the cut is what
    # happened. Calls are deliberately not on this list: looking at files and saying nothing is not
    # an answer.
    if not trimmed and not files and not stopped:
        raise EmptyMessage()
```

*Yeşile döner:* `test_a_stopped_answer_may_carry_nothing`.
*Yeşil kalır:* `test_an_empty_message_is_refused_and_the_chat_is_untouched` — çağrısı `stopped`
taşımıyor.

### 2. `stream_answer.py` — erken dönüş silinir

Şu blok gidiyor:

```python
if cut_short and not "".join(said).strip() and not born:
    yield chat_store.get(project_id, chat_id)
    return
```

Altındaki `append_message` çağrısı zaten her yolu karşılıyor; blok kalsaydı yeni kapıya hiçbir zaman
ulaşılmazdı. Kayıt yine gönderiliyor — o `append_message`'ın kendi dönüşü.

*Yeşile döner:* `test_stopping_before_a_word_still_writes_that_it_was_stopped`.

### 3. `ChatScreen.jsx` — `Stopped` satırı

Metin bloğu şarta bağlanıyor ve altına yeni satır geliyor:

```jsx
{message.role === "user" ? (
  <div className="msg__bubble">{message.text}</div>
) : message.text ? (
  <div className="msg__text">
    <Markdown text={message.text} />
  </div>
) : null}
{/* Where the text stops and why. Above the cards and the count -- those are notes about the turn,
    this is the end of the sentence. Nobody but the user can stop an answer, so the word says what
    happened and invents no cause for it. */}
{message.stopped ? <div className="msg__stopped">Stopped</div> : null}
```

Boş metinli cevap yalnız durdurulanlarda olabiliyor, yani şart bir şey kaybettirmiyor — ve boş bir
`.msg__text` gri sol çizgiyi hiçbir şeyin yanına koyardı.

*Yeşile döner:* `ChatScreen.test.jsx`'in ikisi, `App.test.jsx`'in biri.
*Yeşil kalır:* 67'nin `.msg--stopped` testi ve `an answer that ran to the end says nothing`.

### 4. `workspace.css` — `.msg__stopped` not kaydında

`.token-count`'un hemen üstüne:

```css
/* Where the answer stopped. The same register as the steps above it and the count below: all three
   are notes about the text rather than the text itself. */
.msg__stopped {
  margin-top: 6px;
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: var(--muted);
}
```

*Yeşile döner:* `workspace.css.test.js`'in biri.

### 5. `dist` derlenir

`npm run build --prefix queen-agent/frontend`, kaynakla **aynı commit'e**.

## Beklenen yeşil

Ön yüzde **512**. Arka uçta **2 failed, 443 passed** — ikisi defterin dalı.

**Bu maddenin asıl sınavı düşmeyen dört test:**

| Ne | Neyi kanıtlıyor |
|---|---|
| `test_an_empty_message_is_refused_and_the_chat_is_untouched` | Kullanıcının boş mesajı hâlâ reddediliyor |
| `test_what_was_already_said_is_kept` | Yarım metin hâlâ saklanıyor |
| `test_a_stop_ends_the_answer_without_asking_the_model_again` | Kalan turlar hâlâ koşmuyor |
| `ChatScreen.test.jsx` — `a stopped answer is drawn as one` | Gri çizgi duruyor |

Biri düşerse esneyen kural, esnemesi gereken yerden fazlasını esnetmiş demektir — ve o zaman **kod
düzelir, test değil**.

## Bilerek yapılmayanlar

- **`useChat`'e dokunulmuyor.** Yenilemedeki yeniden başlama boş kayıt yazılınca kendiliğinden
  kapanıyor; `stopped` bayrağı da duruyor, çünkü basma anıyla kaydın gelişi arasındaki pencereyi
  hâlâ o tutuyor.
- **`file_chat_store` ve `routes.py` açılmıyor.** İkisi de `stopped`'ı zaten taşıyor, boş metni de
  olduğu gibi yazıp okuyorlar. Göç yok.
- **Role bakan bir şart yazılmıyor.** Kapıyı `stopped` açıyor: kaydı hak ettiren şey kimin
  konuştuğu değil, ne olduğu.
- **Sebep uydurulmuyor.** Tek kelime: `Stopped`.
