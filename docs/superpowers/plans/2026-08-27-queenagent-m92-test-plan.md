# Madde 92 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-27-queenagent-m92-baglamin-tavani-testler-design.md](../specs/2026-08-27-queenagent-m92-baglamin-tavani-testler-design.md)
**Bu turda kod yazılmaz.** On beş test kırmızıya döner.
**Komutlar:** `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Sözleşme — testlerin varsaydığı isimler

Bu turda **yazılmıyorlar**; testler onları çağırdığı için kırmızı oluyor.

```python
# backend/features/workspace/domain/chat.py
CONTEXT_CEILING = 50_000
def last_sent(chat) -> int      # son cevabın usage.sent'i, yoksa 0
def is_full(chat) -> bool       # last_sent(chat) >= CONTEXT_CEILING
```

```
# GET /api/projects/<p>/chats/<c>
"context": {"sent": 41000, "ceiling": 50000}

# POST /api/projects/<p>/messages -- dolmuş sohbette
400 {"error": "this chat has reached its context ceiling -- start a new chat to keep going"}
```

```jsx
// frontend/src/features/workspace/ContextGauge.jsx
<ContextGauge sent={41000} ceiling={50000} />
// -> <span role="img" class="context-gauge" style="--filled: 0.82"
//          title="82% of the context ceiling" aria-label="82% of the context ceiling" />
// sent 0 veya ceiling yok -> hiçbir şey

// Composer yeni bir yuva alıyor: gauge, foot'un önünde, .composer__gauge içinde
<Composer gauge={...} foot={...} action="Send" />
```

Doluluk bir SVG yayı değil bir CSS değişkeni: `--filled`. Çizim `conic-gradient`'in işi, ve test
dairenin **ne karar verdiğini** okuyor, nasıl çizdiğini değil.

---

## 1. `backend/tests/test_chat.py` — dört test

`is_owed_an_answer` testindeki gerekçe burada da geçerli: **isimler test içinde import ediliyor**,
çünkü henüz olmayan bir isim dosyanın toplanmasını düşürür ve o turun bütün kırmızıları görünmez
olur.

Dosyanın başına, `Usage`'ı da alacak şekilde:

```python
from backend.features.workspace.domain.chat import Chat, Message, Usage
```

```python
# --- the ceiling on a chat's context (Madde 92) --------------------------------------------------

AT = "2026-08-09T11:04:00.000+00:00"


def _answered(sent):
    """A chat whose one answer sent this many tokens."""
    return Chat(
        id="c1",
        title="hi",
        created_at=AT,
        messages=(
            Message(role="user", at=AT, text="hi"),
            Message(role="ai", at=AT, text="Done.", usage=Usage(sent, 0, 5)),
        ),
    )


def test_the_ceiling_is_read_off_the_last_answer():
    # A turn's size is only known once the answer comes back, so the ceiling reads the previous
    # one -- one turn stale on purpose. Which means the record does not always end with the answer
    # it has to read: a question whose answer never came can be sitting on the end, and a question
    # has no number.
    from backend.features.workspace.domain.chat import last_sent

    chat = _answered(41_000)
    asked_again = replace(chat, messages=chat.messages + (Message(role="user", at=AT, text="more"),))
    assert last_sent(chat) == 41_000
    assert last_sent(asked_again) == 41_000


def test_a_chat_with_no_answer_yet_has_sent_nothing():
    # Zero is what unknown looks like here, and Madde 76 already settled that: an answer from
    # before the counting existed reads back as zero too, and nothing is drawn for either.
    from backend.features.workspace.domain.chat import last_sent

    assert last_sent(Chat(id="c1", title="hi", created_at=AT)) == 0
    assert last_sent(
        Chat(id="c1", title="hi", created_at=AT, messages=(Message(role="user", at=AT, text="hi"),))
    ) == 0


def test_the_ceiling_is_fifty_thousand():
    # The reason is quality rather than capacity: the window is 256k, so this is a fifth of it.
    # Models get worse as the input grows and what sits in the middle goes unread -- fitting is not
    # the same as being read.
    from backend.features.workspace.domain.chat import CONTEXT_CEILING

    assert CONTEXT_CEILING == 50_000


def test_a_chat_is_full_at_the_ceiling_and_not_before():
    from backend.features.workspace.domain.chat import CONTEXT_CEILING, is_full

    assert not is_full(_answered(CONTEXT_CEILING - 1))
    assert is_full(_answered(CONTEXT_CEILING))
```

## 2. `backend/tests/test_chats_api.py` — üç test

Harcamayı söyleyen motor `ScriptedEngine`, ve istemciye kurulurken veriliyor — o yüzden bu üç test
kendi istemcisini kuruyor. Dosyanın sonuna:

```python
# --- the ceiling on a chat's context (Madde 92) --------------------------------------------------


def _spending(tmp_path, sent):
    """A client whose one answer reports having sent this many tokens."""
    engine = ScriptedEngine([[{"text": "Done."}, {"usage": {"sent": sent, "cached": 0, "answered": 5}}]])
    return _client(tmp_path, engine)


def test_a_full_chat_refuses_a_new_sentence(tmp_path):
    # The ceiling is what stops the turn, and it stops it before anything is written: a refused
    # sentence that reached the disk would leave the chat waiting for an answer nobody can give.
    client = _spending(tmp_path, 60_000)
    pid, cid = _started(client)
    before = len(_record(client, pid, cid)["messages"])
    refused = client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "and more"})
    assert refused.status_code == 400
    assert "ceiling" in refused.get_json()["error"]
    assert len(_record(client, pid, cid)["messages"]) == before


def test_a_full_chat_refuses_a_second_attempt_too(tmp_path):
    # Trying again is sending the same oversized request a second time. The reason has to be the
    # ceiling rather than anything else the door might have said first -- otherwise the screen
    # tells the user something true and useless.
    client = _spending(tmp_path, 60_000)
    pid, cid = _started(client)
    refused = client.post(f"/api/projects/{pid}/messages", json={"chat": cid})
    assert refused.status_code == 400
    assert "ceiling" in refused.get_json()["error"]


def test_the_record_says_how_much_of_the_ceiling_it_has_used(tmp_path):
    # Both numbers, because the gauge draws a share and a share needs its denominator. A second
    # copy of the ceiling in the browser is the thing that would go stale.
    from backend.features.workspace.domain.chat import CONTEXT_CEILING

    client = _spending(tmp_path, 41_000)
    pid, cid = _started(client)
    assert _record(client, pid, cid)["context"] == {"sent": 41_000, "ceiling": CONTEXT_CEILING}
```

> `ScriptedEngine` ve `_client(tmp_path, engine)` dosyada var; `_spending` yalnız ikisini
> birleştiriyor.

## 3. `frontend/src/features/workspace/ContextGauge.test.jsx` — yeni dosya, dört test

```jsx
import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import ContextGauge from "./ContextGauge.jsx";

// Madde 92. A gauge, not a control: it is read and never pressed, which is also why it sits at the
// far end of the foot from the three things that are pressed.

test("it fills by what the last answer sent", () => {
  render(<ContextGauge sent={41000} ceiling={50000} />);
  expect(screen.getByRole("img").style.getPropertyValue("--filled")).toBe("0.82");
});

test("a chat that has sent nothing draws no gauge", () => {
  // Not an empty circle: an empty circle is a mark that is always there and says nothing. The
  // gauge is born when the first answer comes back.
  const { container } = render(<ContextGauge sent={0} ceiling={50000} />);
  expect(container.firstChild).toBeNull();
});

test("past the ceiling it is full rather than overfull", () => {
  // A circle cannot fill past full, and drawing the excess would draw a lie.
  render(<ContextGauge sent={60000} ceiling={50000} />);
  expect(screen.getByRole("img").style.getPropertyValue("--filled")).toBe("1");
});

test("resting on it reads the share in words", () => {
  // The circle shows the share; this is what makes it readable.
  render(<ContextGauge sent={41000} ceiling={50000} />);
  expect(screen.getByRole("img").getAttribute("title")).toBe("82% of the context ceiling");
});
```

## 4. `frontend/src/features/workspace/Composer.test.jsx` — bir test

Var olan iki foot testinin altına:

```jsx
// Madde 92: the foot grows a second end. Skills, the model's name and Send have been on the right
// since karar 1; the gauge goes to the other one, because it is read rather than pressed and
// sitting among the three would make it look like a fourth thing to press.
test("the gauge stands at the far end of the foot from Send", () => {
  const { container } = render(
    <Composer action="Send" gauge={<span data-testid="gauge" />} foot={<button type="button">Grok 4.5</button>} />,
  );
  const foot = container.querySelector(".composer__foot");
  expect(foot.firstChild.className).toBe("composer__gauge");
  expect(foot.querySelector('[data-testid="gauge"]')).toBeTruthy();
});
```

`with nothing to put there the foot is Send alone` testi olduğu gibi kalıyor ve taslak ekranın
hâlini zaten koruyor: `gauge` verilmeyince yuva hiç çizilmiyor.

## 5. `frontend/src/features/workspace/ChatScreen.test.jsx` — bir test

```jsx
// --- the context gauge (Madde 92) ----------------------------------------------------------------

test("the chat screen draws the gauge from the record it read", () => {
  // The same number the stamp under the answer shows, read from the one place the record's shape
  // is built. Nothing measures anything a second time.
  render(
    <ChatScreen project={PROJECT} chat={{ ...CHAT, context: { sent: 41000, ceiling: 50000 } }} />,
  );
  expect(screen.getByRole("img").style.getPropertyValue("--filled")).toBe("0.82");
});
```

## 6. `frontend/src/features/workspace/ProjectScreen.test.jsx` — bir test

```jsx
// Madde 92: the composer is the same component on both screens, but there is no chat here and so
// nothing to measure. An empty circle would be a mark that is always there and reads as nothing.
test("the draft screen has no gauge", () => {
  render(<ProjectScreen project={PROJECT} />);
  expect(screen.queryByRole("img")).toBeNull();
});
```

## 7. `frontend/src/features/workspace/workspace.css.test.js` — bir test

```js
test("the gauge pushes the rest of the foot to the far end", () => {
  // Madde 92. Not `space-between` on the foot: Skills, the model's name and Send are three
  // separate items in that row, and spreading them would put the whole row's gaps between them.
  const start = CSS.indexOf("\n.composer__gauge {");
  expect(start).toBeGreaterThan(-1);
  expect(CSS.slice(start, CSS.indexOf("}", start))).toContain("margin-right: auto");
});
```

---

## Beklenen kırmızı

**On beş test.** Sayıyı koşarak değil şuradan türetiyoruz: `CONTEXT_CEILING`, `last_sent`,
`is_full`, `context` alanı, `ContextGauge` dosyası, `gauge` yuvası ve `.composer__gauge` kuralı —
hiçbiri yok.

`ProjectScreen`'in testi bugün de yeşil olabilir *(ekranda `role="img"` yok)*; kırmızıya dönmesi
beklenmiyor, ve uygulama turunda daire eklendiğinde yeşil kalması onun işi. Kalan on dördü düşer.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `chat.py`, `routes.py`, `Composer.jsx`, `ChatScreen.jsx`, `workspace.css`
  bu turda açılmaz, `ContextGauge.jsx` yaratılmaz.
- **`stream_answer` açılmaz** — tavan kapıda duruyor.
- **Özetleme yok.**
- **`dist` derlenmez.**
