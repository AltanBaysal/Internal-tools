# Madde 81 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-26-queenagent-m81-durduruldu-yazar-testler-design.md](../specs/2026-08-26-queenagent-m81-durduruldu-yazar-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

**Ekrandaki kelime:** `Stopped`. İngilizce, çünkü QueenAgent'ın arayüzü bilerek İngilizce.

---

## Sıra

### 1. `test_append_message.py` — durdurulmuş cevap boş olabilir

`test_an_empty_message_is_refused_and_the_chat_is_untouched`'ın hemen altına:

```python
def test_a_stopped_answer_may_carry_nothing(tmp_path):
    # A message has to carry something, and a stop is something: it happened, and what happened gets
    # written down. The user's own message never carries this flag, so the empty one they type is
    # still refused -- the test above proves that and stays where it is.
    _, chats = _seeded(tmp_path)
    chat = append_message(
        chats, "p1", "c1", "", "2026-08-09T11:06:00.000+00:00", role="ai", stopped=True
    )
    assert chat.messages[-1].text == ""
    assert chat.messages[-1].stopped is True
```

Bugün kırmızı: `append_message` `EmptyMessage` fırlatıyor.

### 2. `test_stream_answer.py` — kelimeden önceki durdurma ters çevrilir

`test_stopping_before_a_word_writes_no_message` **tamamen** şununla değişiyor:

```python
def test_stopping_before_a_word_still_writes_that_it_was_stopped(tmp_path):
    # Nothing was said and nothing was made, but something happened: somebody stopped it. Written
    # down, because a press that leaves no trace reads as a press that did nothing -- and because
    # the chat's last word would otherwise still be the user's, which means owed an answer, which
    # means the browser asks for one again the moment the page is reloaded.
    chats, _, _, _ = _run(tmp_path, [[{"text": "never reached"}]], stops=StopsAfter(after=0))
    kept = chats.get("p1", "c1").messages
    assert [m.role for m in kept] == ["user", "ai"]
    assert kept[-1].text == ""
    assert kept[-1].stopped is True
```

Bugün kırmızı iki kere: mesaj hiç yazılmıyor.

**Testin adı da değişiyor.** Eski ad artık yalan söylüyor, ve yalan söyleyen bir ad testten daha
uzun yaşar.

### 3. `ChatScreen.test.jsx` — üç test

67'nin `a stopped answer is drawn as one` testinin **altına**, o dokunulmadan:

```jsx
test("a stopped answer says so in words", () => {
  // The grey rule down the side means something to whoever put it there. The word means the same
  // thing to everybody.
  const stopped = {
    ...CHAT,
    messages: [CHAT.messages[0], { ...CHAT.messages[1], text: "Half a", stopped: true }],
  };
  render(<ChatScreen project={PROJECT} chat={stopped} />);
  expect(screen.getByText("Stopped")).toBeTruthy();
});

test("an answer that ran to the end says nothing", () => {
  render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(screen.queryByText("Stopped")).toBeNull();
});

test("a stop before the first word is still a message on screen", () => {
  // Madde 81's own case. Nothing was said, so there is no text block to draw -- an empty one would
  // put the grey rule beside nothing at all.
  const stopped = {
    ...CHAT,
    messages: [CHAT.messages[0], { ...CHAT.messages[1], text: "", stopped: true }],
  };
  const { container } = render(<ChatScreen project={PROJECT} chat={stopped} />);
  expect(screen.getByText("Stopped")).toBeTruthy();
  expect(container.querySelector(".msg__text")).toBeNull();
});
```

Birinci ve üçüncü kırmızı; ikinci ilk günden yeşil ve bilerek yazılıyor — `Stopped`'ın her cevabın
altına düşmesini tutan tek şey o.

### 4. `workspace.css.test.js` — not kaydında olduğu

`the send button is a fixed square` testinin üstüne:

```js
test("the stopped line reads as a note, not as the answer", () => {
  // Same register as the steps above the answer and the count below it: all three are notes about
  // the text rather than the text itself.
  const line = rule(".msg__stopped");
  expect(line).toContain("var(--font-mono)");
  expect(line).toContain("color: var(--muted)");
});
```

Bugün kırmızı: `rule()` bulamayınca `expect(start).toBeGreaterThan(-1)` düşüyor — okunur bir
kırmızı, `TypeError` değil.

### 5. `App.test.jsx` — yenilemede yeniden sorulmuyor

`a stopped answer is not asked for all over again` testinin altına:

```jsx
test("a chat whose last word is a stopped answer is not asked again", () => {
  // Madde 81's payoff, and the reason the empty record is written at all. Before it, this chat's
  // last message was the user's -- owed an answer, and asked for one the moment the page came back.
  const stopped = {
    id: "c1",
    title: "hello",
    messages: [
      { role: "user", at: new Date().toISOString(), text: "hello" },
      { role: "ai", at: new Date().toISOString(), text: "", stopped: true },
    ],
  };
  const fetch = vi.fn().mockImplementation((path) => {
    if (String(path).endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => stopped });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  return waitFor(() => {
    expect(screen.getByText("Stopped")).toBeTruthy();
    expect(fetch.mock.calls.filter(([path]) => String(path).endsWith("/answer"))).toHaveLength(0);
  });
});
```

Bugün: `/answer` beklentisi geçiyor *(son mesaj `ai`, sohbet cevap borçlu değil)* ama `Stopped`
yok — yani **kırmızı**. Beklentinin ikisi de kalıyor: biri bugünkü deliği, öteki yarın kırılabilecek
olanı tutuyor.

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_append_message.py` | 1 |
| `test_stream_answer.py` | 1 |
| `ChatScreen.test.jsx` | 2 |
| `workspace.css.test.js` | 1 |
| `App.test.jsx` | 1 |

Arka uçta **4 failed, 441 passed** — ikisi bu maddenin, ikisi defterin dalı.
Ön yüzde **4 failed, 508 passed** — dört yeni testle toplam 512.

**Kırmızının okunabilir olması şart.** `container.querySelector(...).textContent` yolu eleman yoksa
`TypeError` veriyor ve testin ne beklediğini gizliyor; 68 ile 78'de iki kez oldu. Buradaki üç metin
beklentisi `screen.getByText(...)` ile yazılıyor.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `append_message.py`, `stream_answer.py`, `ChatScreen.jsx`, `workspace.css` bu
  turda açılmıyor.
- **`dist` derlenmez.**
- **67'nin testlerine dokunulmaz.** `.msg--stopped` çizgisini soran test, yarım metnin saklandığını
  soran test, kalan turların koşmadığını soran test — üçü de yerinde ve yeşil kalmalı.
- **Kullanıcının boş mesajını soran test değiştirilmez.** O kapı kapalı kalıyor ve kapalı kaldığını
  o test söylüyor.
