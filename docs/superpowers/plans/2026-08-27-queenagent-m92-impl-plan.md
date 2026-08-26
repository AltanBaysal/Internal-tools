# Madde 92 · Tur 2 (kod) — Plan

**Tasarım:** [2026-08-27-queenagent-m92-baglamin-tavani-uygulama-design.md](../specs/2026-08-27-queenagent-m92-baglamin-tavani-uygulama-design.md)
**Bu turda yeni test yazılmaz.** `c574515`'in on dört kırmızısı yeşile döner.
**Komutlar:** `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
`npm run build --prefix queen-agent/frontend`

---

## 1. `backend/features/workspace/domain/chat.py`

`is_owed_an_answer`'ın altına:

```python
CONTEXT_CEILING = 50_000
"""How much one chat may send before it stops taking new turns.

Not a capacity limit -- the window is 256k, so this is a fifth of it. It is a quality one: models
get worse as the input grows and what sits in the middle of a long request goes unread, so fitting
is not the same as being read. Above 200k the input also costs twice as much.
"""


def last_sent(chat):
    """What the most recent answer sent to the model, or 0 if none ever did.

    A turn's size is only known once its answer comes back, so this is one turn stale on purpose --
    a request is stopped by the size of the one before it. At this ceiling the difference does not
    matter: no single turn is large enough to cross it on its own.

    Walked from the end rather than read off the last message: a question whose answer never came
    can be sitting there, and a question has no number of its own.
    """
    for message in reversed(chat.messages):
        if message.role == "ai":
            return message.usage.sent
    return 0


def is_full(chat):
    """Whether this chat has reached the ceiling and may not take another turn."""
    return last_sent(chat) >= CONTEXT_CEILING
```

`TITLE_LIMIT` dosyanın başında duruyor; `CONTEXT_CEILING` okuyucularının yanında duruyor, çünkü tek
başına bir sayı değil bir kuralın parçası.

## 2. `backend/features/workspace/presentation/routes.py`

Import satırı `is_full`'ü de alıyor:

```python
from backend.features.workspace.domain.chat import ToolCall, is_full, is_owed_an_answer
```

`post_message`'ın başı — okuma yukarı çıkıyor ve bir kere yapılıyor:

```python
    def post_message(project_id):
        payload = request.get_json(silent=True) or {}
        wanted = payload.get("chat", "")
        # Read once, up here: both roads out of this door are stopped by the same ceiling, and the
        # road without text was doing this lookup anyway.
        existing = chat_store.get(project_id, wanted) if wanted else None
        # Asked before anything else this door might refuse for. A full chat that is also already
        # answered is both, and what the user needs to hear is the one that stops them.
        if existing is not None and is_full(existing):
            return jsonify(
                {"error": "this chat has reached its context ceiling -- start a new chat to keep going"}
            ), 400
        # Absent is not blank. A blank sentence is somebody leaning on the space bar and is
        # refused; no sentence at all means they are asking for the answer, not sending one.
        if "text" in payload:
            ...  # unchanged
        else:
            chat = existing
            if chat is None:
                return jsonify({"error": "there is nothing here to answer"}), 400
            if not is_owed_an_answer(chat):
                return jsonify({"error": "this chat has already been answered"}), 400
```

Metinsiz yoldaki `chat = chat_store.get(project_id, wanted) if wanted else None` satırı
`chat = existing` oluyor — aynı okuma iki kere yapılmıyor.

`_chat_json`'a bir alan, `_chat_summary`'nin üstüne serptiği alanların yanına:

```python
def _chat_json(chat):
    return {
        **_chat_summary(chat),
        # The ceiling travels with the number: the gauge draws a share, and a share needs its
        # denominator. A second copy of the ceiling living in the browser is what would go stale.
        "context": {"sent": last_sent(chat), "ceiling": CONTEXT_CEILING},
        "messages": [...],  # unchanged
    }
```

Import buna göre: `from ...chat import CONTEXT_CEILING, ToolCall, is_full, is_owed_an_answer,
last_sent`.

`_chat_summary` açılmıyor.

## 3. `frontend/src/features/workspace/ContextGauge.jsx` — yeni

```jsx
// Madde 92. A gauge, not a control: it is read and never pressed, which is why it sits at the far
// end of the composer's foot from the three things that are.
//
// The share is settled here and the drawing is left to one CSS rule. Not for testability -- for
// truth: how full the circle is, is a number, and the arc is only one way of saying it.
export default function ContextGauge({ sent, ceiling }) {
  // Nothing measured yet, so there is nothing to read. An empty circle would be a mark that is
  // always there and says nothing -- the gauge is born when the first answer comes back.
  if (!sent || !ceiling) return null;
  // A circle cannot fill past full, and drawing the excess would draw a lie.
  const filled = Math.min(sent / ceiling, 1);
  const share = `${Math.round(filled * 100)}% of the context ceiling`;
  return (
    <span
      className="context-gauge"
      style={{ "--filled": String(filled) }}
      /* Drawn rather than written, so it needs a name -- and the same sentence serves a mouse
         resting on it and a screen reader reaching it. */
      role="img"
      title={share}
      aria-label={share}
    />
  );
}
```

## 4. `frontend/src/features/workspace/Composer.jsx`

Prop listesine `gauge`, ve ayağın başına yuva:

```jsx
export default function Composer({ rows, placeholder, action, gauge, foot, running, onStop, onSubmit }) {
```

```jsx
      <div className="composer__foot">
        {/* The foot's other end since Madde 92. Empty on the draft screen, where there is no chat
            to measure -- and then the slot is not drawn at all and the row stays as it was. */}
        {gauge ? <div className="composer__gauge">{gauge}</div> : null}
        {foot}
```

Başlıktaki yorum bugün *"`foot` is what stands to the left of the button"* diyor; ayağın artık iki
ucu olduğu için o paragraf `gauge`'i de anlatacak şekilde güncelleniyor.

## 5. `frontend/src/features/workspace/ChatScreen.jsx`

`ContextGauge` import ediliyor, ve `Composer`'a yuva veriliyor:

```jsx
          <Composer
            rows={2}
            placeholder="Reply..."
            action="Send"
            /* Read off the record like everything else on this screen: the number is the same one
               the stamp under the last answer shows, and nothing counts it a second time. */
            gauge={<ContextGauge sent={chat.context?.sent} ceiling={chat.context?.ceiling} />}
```

`?.` çünkü ekran testlerinin çoğu `context` taşımayan bir sohbetle çiziyor, ve taşımayan bir kayıt
gerçek de: 92'den önce yazılmış hiçbir cevap onu getirmiyor. O hâlde daire çizilmiyor.

## 6. `frontend/src/features/workspace/workspace.css`

`.composer__foot`'un hemen altına:

```css
/* The foot's other end. Not `justify-content: space-between` on the foot itself: Skills, the
   model's name and Send are three separate items in that row, and spreading the row would put its
   whole width between them. */
.composer__gauge {
  display: inline-flex;
  align-items: center;
  margin-right: auto;
}

/* Reads at a glance and takes no room: the same orange the app already uses, filling clockwise
   from the top. `--filled` is a share between 0 and 1 and the component is what settles it. */
.context-gauge {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: conic-gradient(
    var(--accent) calc(var(--filled) * 360deg),
    #ded7cd calc(var(--filled) * 360deg)
  );
}
```

`#ded7cd` uygulamanın devre dışı yüzeyi — `app.css`'te gönder düğmesinin sönük hâlinin yanında aynı
ton duruyor.

## Beklenen yeşil

`c574515`'in on dört kırmızısının hepsi, ve `ProjectScreen`'in daireyi hâlâ bulamaması.

**İki kırmızı kalır ve bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` derlenip **aynı commit'e** giriyor.

## Bilerek yapılmayanlar

- **Yeni test yazılmaz.**
- **`_chat_summary` açılmaz** — liste satırında okuyanı yok.
- **`stream_answer` açılmaz** — tavan kapıda.
- **Composer taslak ekranda değişmez** — yuva boş, ayak eski hâlinde.
- **Özetleme yok.**
