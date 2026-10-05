# Madde 419 — Kutunun araçlı isteği, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır, madde 419'un kendi dalında. Testler kırmızı hâliyle
> commit'li (`c4b43ef5`); bu tur yalnız kodu yazar, dört satırı koşar, yeşili görür ve commit'ler.

**Hedef:** Kutunun `converse(messages, tools=())`'u konuşmayı ve araçları DeepSeek'e olduğu gibi
gönderir, cevabı bütün döner — sözler ya da araç çağrıları —, araç çağrısını kontrolsüz geçirir,
sözleri 418'deki gibi kontrol eder; `Answer` başarısızlığın ret mi teknik mi olduğunu söyler.

**Mimari:** İstemcide `send` tek isteği atar ve `(sözler, çağrılar)` döner; `complete` onun üstünde.
Kutuda `ask` ve `converse` aynı özel `_tried` döngüsünden geçer.

**Araçlar:** Python, `dataclasses.field`.

**Spec:** [m419 uygulama turu](../specs/2026-10-06-queen-editor-m419-aracli-istek-uygulama-design.md),
[m419 test turu](../specs/2026-10-06-queen-editor-m419-aracli-istek-testler-design.md)

## Her yere geçerli kurallar

- Kod ve yorumlar İngilizce; kullanıcının gördüğü hata metinleri Türkçe ve bugünkü gibi.
- Yalnız commit'li testlerin anlattığı kod; testlere dokunulmaz.
- Yorum neden'i söyler, yalnız bugün doğru olanı.
- `prompt_writer.py`, `main.py`, ekran, `dist`, yol haritası değişmez.

---

## Görev 1: `backend/services/deepseek/client.py`

**Dosya:** Değiştir: `queen-editor/backend/services/deepseek/client.py`

**Arayüz:** Üretir — `DeepSeekClient.send(messages, tools=()) -> (str, list)`; `complete` aynen.

- [ ] **Adım 1: Modül belgesi.**

```python
"""DeepSeek chat transport -- an instruction, words and pictures, or a conversation and its tools,
in; the answer's words and the tool calls it makes, back.

One request, and a failure raised in the server's own words; sending it again is box.py's. Knows
nothing about video, prompts, frames or agents: what to ask is the caller's business (see
features/photo_generation/data/prompt_writer.py). `http` is injected so tests need no network.
"""
```

- [ ] **Adım 2: `complete` mesajlarını kurar ve `send`'e sorar; `send` bugünkü isteği atar ve
  cevabı okur.**

```python
    def complete(self, system, text="", images=()):
        """One system message + one user message of pictures and words -> the answer's text.

        `images` is [(name, bytes)]. They ride in the user message alone: DeepSeek answers 400 to a
        picture in the system message. No words means no text part at all, rather than an empty one.
        """
        said = [_picture(name, data) for name, data in images]
        if text:
            said.append({"type": "text", "text": text})
        answer, _ = self.send([{"role": "system", "content": system},
                               {"role": "user", "content": said}])
        return answer

    def send(self, messages, tools=()):
        """A conversation and the tools the model may call -> (the answer's words, its tool calls).

        Both go as they are: what they say is the caller's business. The words come back trimmed, ""
        when there are none, and the tool calls as DeepSeek sent them, [] when there are none. An
        answer with neither is an empty answer.
        """
        if not self._api_key:
            raise NotConfigured(
                "DEEPSEEK_API_KEY yok — Colab Secrets'a ekle ve notebook erişimini aç")
        body = {"model": self._model, "messages": messages}
        # Only when there are some: a question offered nothing to call -- every prompt writer's --
        # goes as it always did.
        if tools:
            body["tools"] = tools
        response = self._http.post(
            self._url,
            headers={"Authorization": f"Bearer {self._api_key}",
                     "Content-Type": "application/json"},
            json=body,
            timeout=self._timeout,
        )
        if response.status_code >= 400:
            # The server's own body, never a guessed cause: a refusal can be the picture, the model
            # name, the key or the balance, and only the body knows which.
            raise RuntimeError(f"DeepSeek HTTP {response.status_code}\n{response.text}")
        try:
            message = response.json()["choices"][0]["message"]
            # An answer that calls a tool comes with its content null.
            words = (message.get("content") or "").strip()
            calls = message.get("tool_calls") or []
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"DeepSeek cevabı beklenen biçimde değil ({type(exc).__name__})\n"
                               f"{response.text}") from None
        if not words and not calls:
            raise RuntimeError(f"DeepSeek boş cevap döndü:\n{response.text}")
        return words, calls
```

## Görev 2: `backend/services/deepseek/box.py`

**Dosya:** Değiştir: `queen-editor/backend/services/deepseek/box.py`

**Arayüz:** Tüketir — `DeepSeekClient.complete`, `DeepSeekClient.send`. Üretir —
`Box.converse(messages, tools=()) -> Answer`; `Answer(text, failed=False, refused=False,
tool_calls=[])`; `Box.ask` aynen.

- [ ] **Adım 1: Modül belgesi ve içe aktarma.**

```python
"""The black box every request to Queen AI goes through (madde 416, 418, 419).

The caller asks once and always gets an Answer back, never an exception. A request that came back
with an HTTP error, a malformed or an empty answer, or no answer at all is sent again as it was, up
to five tries in all. An answer that did come is checked before it goes back: its text is sent to
DeepSeek word for word, in a request of its own, and only an approval lets it through -- a refusal
sends the request again the way an error does, out of the same five tries (madde 418). When every
try failed, the Answer is marked as a failure and says what the last try met: the refusal sentence,
or the error's own text, and which of the two it was. It never raises because a caller that loops --
an agent -- must not be broken by the service (v9-3): what to do with the failure is the caller's
call.

Two kinds of request go through the same tries: a prompt writer's question -- an instruction, words
and pictures -- and the agent's conversation with its tools (madde 419), whose answer comes back
whole: its words, or the tool calls it makes. Only words are checked.

What one try is lives in client.py; this file decides how many there are and what comes back.
"""
from dataclasses import dataclass, field
```

- [ ] **Adım 2: `Answer` ve `Box`.** `TRIES`, `CHECK_INSTRUCTION`, `REFUSED` aynen.

```python
@dataclass(frozen=True)
class Answer:
    """The model's words and the tool calls it makes, or -- when `failed` -- why the box gave up, in
    the service's own words.

    `tool_calls` is DeepSeek's own list, [] when there are none; words beside the calls are in
    `text`. `refused` says a failure's last try was refused rather than failed on the wire: the
    screen draws the two as different error cards (madde 425).
    """

    text: str
    failed: bool = False
    refused: bool = False
    tool_calls: list = field(default_factory=list)


class Box:
    def __init__(self, client):
        self._client = client

    def ask(self, system, text="", images=()):
        """The client's question -- an instruction, words and pictures -- tried until its answer
        passes the check or five tries have failed. Every prompt writer asks this."""
        return self._tried(lambda: (self._client.complete(system, text, images), []))

    def converse(self, messages, tools=()):
        """A conversation and the tools the model may call, tried the same way, and its answer back
        whole (madde 419). The agent asks this."""
        return self._tried(lambda: self._client.send(messages, tools))

    def _tried(self, request):
        """`request` sends one try and returns its (words, tool calls); this tries it at most five
        times.

        A try is the request and, when words came alone, their check; a refusal and an error of
        either request each spend one. Every failure is tried again, a missing key included: the
        client refuses that one before anything is sent, so its tries cost nothing, and one rule is
        simpler than a list of the exceptions worth a second try.
        """
        for _ in range(TRIES):
            try:
                words, calls = request()
                # A tool call is not checked (v9-3): it asks for something rather than answers, and
                # the words beside it are what the agent says while it asks.
                if calls:
                    return Answer(words, tool_calls=calls)
                # Only the one word lets an answer through: anything else, a check that will not
                # judge included, has approved nothing (v9-3).
                if self._client.complete(CHECK_INSTRUCTION, words) == "APPROVED":
                    return Answer(words)
                said, refused = REFUSED, True
            except Exception as exc:
                said, refused = str(exc), False
        # Every try rewrites both, so what the caller is told is the last try's.
        return Answer(said, failed=True, refused=refused)
```

## Görev 3: Koşu — yeşil, commit

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: iki pytest satırı yeşil — `queen-editor`'ün 16 kırmızısı yeşil, öteki her şey yeşil
kalır. İki vitest satırı bu çalışma ağacında başlayamaz — `node_modules` yok; bu madde ekrana
dokunmuyor.

- [ ] **Adım 2: Commit** — kod, uygulama spec'i ve bu plan:

```powershell
git add docs/superpowers/specs/2026-10-06-queen-editor-m419-aracli-istek-uygulama-design.md docs/superpowers/plans/2026-10-06-queen-editor-m419-aracli-istek-uygulama-plan.md queen-editor/backend/services/deepseek/client.py queen-editor/backend/services/deepseek/box.py
git commit -m @'
feat(queen-editor): 419 -- the box in services/deepseek carries the agent's conversation too: Box.converse(messages, tools) sends them through the client's new send as they are, with no tools key when none are given, through the same five tries as ask; a tool call comes back whole and unchecked in Answer.tool_calls, words alone are checked as before; a failed Answer says in refused whether its last try was a refusal or technical; complete now asks through send, and prompt writing is unchanged

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
