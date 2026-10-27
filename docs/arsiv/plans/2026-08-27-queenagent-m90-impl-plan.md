# Madde 90 · Tur 2 (kod) — Plan

**Tasarım:** [2026-08-27-queenagent-m90-durdurma-baglantiyi-keser-uygulama-design.md](../specs/2026-08-27-queenagent-m90-durdurma-baglantiyi-keser-uygulama-design.md)
**Bu turda yeni test yazılmaz.** `ef57801`'in on beş kırmızısı yeşile döner.
**Komutlar:** `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## 1. `backend/services/xai/client.py`

`import http.client` ve `import socket` girer.

`_parsed`'in yanına, modül düzeyinde:

```python
def _cut(response):
    """Wake a read blocked on this response's socket, from the thread that wants it to end.

    Not `response.close()`: the buffered reader's lock belongs to the thread doing the reading, so
    closing from another thread waits for exactly the read it is trying to interrupt. This goes
    past the buffer, to the socket.

    Both calls, because the two roads QueenAgent runs on wake on different ones -- measured on 27
    August rather than assumed. Windows leaves a blocked read sitting through a `shutdown` and
    comes back only once the handle is really closed; Linux is the other way round. And the closing
    goes through `detach`, because the socket's own `close` would not close anything: the file the
    response reads through holds a count on it, and the handle outlives the call.

    urllib does not hand the socket out, so this walks down to it through CPython's own naming.
    Nobody promised that shape, and a link that is not there ends the attempt rather than the run.
    """
    sock = getattr(getattr(getattr(response, "fp", None), "raw", None), "_sock", None)
    if sock is None:
        return
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        # Already gone. The answer finishing on its own and the press landing really do race.
        pass
    try:
        handle = sock.detach()
        if handle != -1:
            socket.socket(fileno=handle).close()
    except OSError:
        pass
```

> Bu gövde plan yazıldığında yalnız `shutdown` idi. Testler kırmızı kaldı, ölçüldü, ve iki
> platformun iki farklı çağrıyla uyandığı çıktı. Uygulama tasarımındaki tablo bunu taşıyor.

`stream` bir parametre ve iki satır kazanıyor:

```python
    def stream(self, messages, tools=None, on_open=None):
        ...
        try:
            with self._opener(request) as response:
                # Before a single line is read: the wait this hands a way out of is the wait before
                # the first word, and a cut offered after it would miss exactly that stretch.
                if on_open:
                    on_open(lambda: _cut(response))
                for raw in response:
                    ...
        except urllib.error.HTTPError as failure:
            ...
        except urllib.error.URLError as failure:
            raise XaiFailed(str(failure.reason)) from failure
        except http.client.IncompleteRead as failure:
            # A chunked body that stopped in the middle -- one of the two shapes a cut socket
            # leaves behind. Python's own words: who cut it is not something this layer knows.
            raise XaiFailed(str(failure)) from failure
        except OSError as failure:
            # The other shape: a handle closed under a read that was waiting on it. Also what a
            # connection dropping mid-answer looks like, and the two are not told apart here.
            raise XaiFailed(str(failure)) from failure
```

`OSError` en sona geliyor: `urllib.error.URLError` onun bir alt sınıfı, ve kendi dalını yukarıda
tutuyor.

`complete` açılmıyor.

## 2. `backend/features/workspace/data/xai_engine.py`

```python
    def stream(self, messages, tools=None, on_open=None):
        return self._client.stream(self._for_xai(messages), tools=tools, on_open=on_open)
```

## 3. `backend/features/workspace/data/memory_stops.py`

Modülün başlığı bugün *"kimin durdurulması istendiği"* diyor; artık bağlantının kendisini de
tuttuğu için o cümle güncelleniyor.

```python
class MemoryStops:
    def __init__(self):
        self._wanted = set()
        # How to cut the connection each running answer is reading. Held only while it runs.
        self._cuts = {}
        self._lock = threading.Lock()

    def hold(self, project_id, chat_id, cut):
        # Which of the two comes first is nobody's to arrange: the press can land before the
        # connection exists, and that is the very case this item was written for.
        with self._lock:
            self._cuts[(project_id, chat_id)] = cut
            asked = (project_id, chat_id) in self._wanted
        if asked:
            cut()

    def want(self, project_id, chat_id):
        with self._lock:
            self._wanted.add((project_id, chat_id))
            cut = self._cuts.get((project_id, chat_id))
        if cut:
            cut()

    def wanted(self, project_id, chat_id):
        with self._lock:
            return (project_id, chat_id) in self._wanted

    def clear(self, project_id, chat_id):
        # Discard rather than remove: every answer clears on its way out, and most were never
        # stopped. The connection goes too -- a stop arriving later would reach a socket number
        # that belongs to somebody else by then.
        with self._lock:
            self._wanted.discard((project_id, chat_id))
            self._cuts.pop((project_id, chat_id), None)
```

Kesme kilidin **dışında** çağrılıyor. `shutdown` tek sistem çağrısı ve okuyan thread bu kilide hiç
dokunmuyor, ama kesme yolunun ne yaptığı bu sınıfın bilgisi değil: kilidi tutarken yabancı bir kod
çağırmak, o kodun bir gün kilidi isteyeceği ihtimalini açık bırakıyor. Sözlükten okumak kilit
altında, çağırmak dışında.

## 4. `backend/features/workspace/domain/ports.py`

`Engine.stream` imzası `on_open=None` alıyor ve şu cümle ekleniyor:

```
        `on_open` is handed a callable that cuts the connection this answer is reading, as soon as
        there is one to cut. An engine with no connection to cut never calls it.
```

`Stops` protokolü:

```python
class Stops(Protocol):
    """The one cancel. What is held is the running answer's connection, never a note on disk."""

    def hold(self, project_id: str, chat_id: str, cut) -> None:
        """Take the way to cut this answer's connection. Cuts at once if a stop is already waiting."""

    def want(self, project_id: str, chat_id: str) -> None:
        """Stop the answer running for this chat, by cutting the connection it is reading."""

    def wanted(self, project_id: str, chat_id: str) -> bool:
        """Was this answer's connection cut by us. The only thing that tells a stop from a fault."""

    def clear(self, project_id: str, chat_id: str) -> None:
        """Forget the request and the connection both."""
```

## 5. `backend/features/workspace/domain/usecases/stream_answer.py`

Kare başına soru düşüyor, akış döngüsünün etrafına bir `try` giriyor, ve tur sonunda tek soru
kalıyor.

```python
        for _ in range(MAX_ROUNDS):
            spoken, calls = [], []
            # This round's bill so far. None until the engine says anything about it, so an engine
            # that measures nothing leaves the total alone rather than adding zeroes to it.
            round_spent = None
            try:
                for piece in engine.stream(
                    conversation,
                    tools=TOOL_SPECS,
                    # Only the transport holds a socket, so only it can hand out a way to cut one.
                    on_open=lambda cut: stops.hold(project_id, chat_id, cut),
                ):
                    if "text" in piece:
                        spoken.append(piece["text"])
                        said.append(piece["text"])
                        yield piece["text"]
                    elif "usage" in piece:
                        # Replaced rather than added. Today the engine says this once, as the
                        # stream closes, so the rule idles -- but a figure is a total for the call
                        # rather than a share since the last, and an engine that reported as it
                        # went would have its bill multiplied by the number of pieces if these
                        # were summed.
                        round_spent = piece["usage"]
                    else:
                        calls.extend(piece["tool_calls"])
            except Exception:
                # A connection that died because we cut it is a stop; the same words from a network
                # that dropped are a fault. Nothing in the failure says which, so the record is
                # asked before it is believed.
                if not stops.wanted(project_id, chat_id):
                    raise
                cut_short = True

            # After the round however it ended, because a round that was cut short still sent its
            # whole conversation and was still charged for it. The window is narrow -- the engine
            # reports as the stream closes, so a cut answer usually never hears the figure at all
            # -- but what did arrive was really spent, and dropping it here would throw it away.
            # Rounds add where pieces replaced: each round is its own call and its own bill, and
            # that growth is the thing this number exists to show.
            if round_spent:
                spent = Usage(
                    spent.sent + round_spent["sent"],
                    spent.cached + round_spent["cached"],
                    spent.answered + round_spent["answered"],
                )

            # Asked once, at the end, rather than before every frame: since Madde 90 a stop cuts
            # the connection, so a round that was stopped is already over by the time this runs.
            # This is the round that ended quietly with the press landing just as it did.
            if not cut_short and stops.wanted(project_id, chat_id):
                cut_short = True

            # Reaching a stop is an end, not a failure -- the same way the round limit is.
            if cut_short or not calls:
                break
```

Dış `try`/`except Exception`/`finally` olduğu gibi kalıyor: iç `except`'in yukarı bıraktığı arıza
orada `EngineFailed` oluyor, araç koşarken çıkan bir hata da öyle.

`stream_answer`'ın başındaki docstring ve dosyanın geri kalanı açılmıyor.

## Beklenen yeşil

`ef57801`'in on beş kırmızısının hepsi. **İki kırmızı kalır ve bu maddenin değildir:**
`test_notebook`'un ikisi. Ön yüz 516/516 kalır.

Yeşilin en çok şey söyleyeni `test_a_cut_wakes_a_read_that_is_blocked_on_the_socket`: gerçek soket,
gerçek bloke okuma. Düşerse `_cut`'ın zinciri ya da `shutdown` bu platformda uyandırmıyor demektir,
ve madde orada durur.

## Bilerek yapılmayanlar

- **Yeni test yazılmaz.**
- **`routes.py` açılmaz** — `/stop` ucu aynı.
- **`complete` yolu açılmaz.**
- **Ön yüz açılmaz, `dist` derlenmez.**
- **`ports.py`'deki `Engine.complete`'in eski `model` parametresine dokunulmaz** — Madde 82'den
  kalma ve kendi turunu bekliyor.
