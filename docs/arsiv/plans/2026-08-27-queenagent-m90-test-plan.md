# Madde 90 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-27-queenagent-m90-durdurma-baglantiyi-keser-testler-design.md](../specs/2026-08-27-queenagent-m90-durdurma-baglantiyi-keser-testler-design.md)
**Bu turda kod yazılmaz.** On bir yeni test kırmızıya döner, altı testin ölçüsü yeniden türetilir.
**Komutlar:** `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Sözleşme — testlerin varsaydığı imzalar

Bu turda **yazılmıyorlar**; testler onları çağırdığı için kırmızı oluyor. Uygulama turu bunları kurar.

```python
# backend/services/xai/client.py
def stream(self, messages, tools=None, on_open=None)   # on_open(cut) -- cevap açılır açılmaz
def _cut(response)                                     # modül fonksiyonu, sessizce vazgeçer

# backend/features/workspace/data/xai_engine.py
def stream(self, messages, tools=None, on_open=None)   # olduğu gibi aşağı geçirir

# backend/features/workspace/data/memory_stops.py
def hold(self, project_id, chat_id, cut)               # yeni
def want(self, project_id, chat_id)                    # artık kesiyor da
```

`stream_answer` `engine.stream(..., on_open=...)` diye çağırır ve `wanted`'ı **tur başına bir kere**
sorar. Bu turda yalnız sahteler o imzayı öğrenir.

---

## 1. `backend/tests/test_xai_client.py` — dört yeni test

Dosyanın başına `import http.client`, `import socket`, `import threading` girer.

### 1.1 Kesme yolu ilk satırdan önce teslim edilir

```python
def test_a_stream_hands_over_the_way_to_cut_it_before_it_reads_a_line():
    # Handed over the moment the response is open, not once words start arriving: the whole point
    # is the wait before the first word, and a cut offered after it would miss exactly that.
    order = []

    class _Watched(_Lines):
        def __iter__(self):
            order.append("read")
            return super().__iter__()

    list(_client(lambda request: _Watched([b"data: [DONE]"])).stream(
        MESSAGES, on_open=lambda cut: order.append("open")
    ))
    assert order == ["open", "read"]
```

### 1.2 Soket saklamayan bir cevabı kesmek sessizdir

```python
def test_cutting_a_response_that_hides_no_socket_is_quiet():
    # Every fake in this suite is such a response. The chain down to the socket is CPython's own
    # naming and nobody promised it -- so a link that is not there ends the attempt, not the run.
    held = []
    list(_client(lambda request: _Lines([b"data: [DONE]"])).stream(
        MESSAGES, on_open=held.append
    ))
    held[0]()
```

### 1.3 ve 1.4 — gerçek soketli iki test

Ortak yardımcı, dosyanın sonuna:

```python
def _silent_server():
    """A server that answers and then says nothing -- a model that is still thinking.

    Chunked on purpose: that is how xAI sends an SSE stream, and it is what decides how a cut comes
    back. The reader is left inside recv with no frame to come back for, which is the only place
    this can be tested from.
    """
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)

    def serve():
        connection, _ = listener.accept()
        connection.recv(65536)
        connection.sendall(
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/event-stream\r\n"
            b"Transfer-Encoding: chunked\r\n\r\n"
        )
        # Held open with nothing to say, until the test's own thread is gone.
        held.wait(10)
        connection.close()
        listener.close()

    held = threading.Event()
    threading.Thread(target=serve, daemon=True).start()
    return listener.getsockname()[1], held


def _blocked_read():
    """Start a real stream against the silent server and hand back what it takes to end it.

    The reading thread is daemon: if the cut fails to reach the socket it stays blocked forever,
    and the run must still be able to finish and report the failure.
    """
    port, done = _silent_server()
    client = XaiClient(lambda: "key", "grok-4.5", f"http://127.0.0.1:{port}")
    outcome = {}
    opened = threading.Event()

    def read():
        try:
            list(client.stream(MESSAGES, on_open=lambda cut: (outcome.setdefault("cut", cut),
                                                              opened.set())))
            outcome["ended"] = "quietly"
        except BaseException as failure:  # noqa: BLE001 -- the test is what names it
            outcome["ended"] = failure
        done.set()

    reader = threading.Thread(target=read, daemon=True)
    reader.start()
    assert opened.wait(5), "the response never opened"
    return reader, outcome
```

```python
def test_a_cut_wakes_a_read_that_is_blocked_on_the_socket():
    # The one thing no fake can answer: whether the cut really reaches the socket. `close()` would
    # not -- the buffered reader's lock belongs to the thread doing the reading, so closing waits
    # for the very read it means to interrupt. `shutdown` goes past the buffer.
    reader, outcome = _blocked_read()
    outcome["cut"]()
    reader.join(5)
    # Not `join()` on its own: a cut that never landed would hang the whole run rather than fail it.
    assert not reader.is_alive()


def test_a_stream_cut_in_the_middle_comes_back_as_a_failure():
    # xAI streams chunked, so a socket shut down between frames leaves a half-read body, and
    # http.client says so. It travels in the client's own currency, carrying Python's words rather
    # than a guessed cause -- who cut it is not something this layer knows.
    reader, outcome = _blocked_read()
    outcome["cut"]()
    reader.join(5)
    assert isinstance(outcome["ended"], XaiFailed)
```

> `_client` yardımcısı sahte `opener` istiyor; bu iki test gerçek `urllib`'i kullandığı için
> `XaiClient`'ı elle kuruyor.

---

## 2. `backend/tests/test_stops.py` — dört yeni test

Var olan beş test aynen kalır: `want`/`wanted`/`clear`'ın anlamı değişmiyor.

```python
def test_a_stop_cuts_the_connection_it_is_holding():
    # The whole item in one line: what the registry keeps is not a note saying somebody asked, it
    # is the connection itself.
    cuts = []
    stops = MemoryStops()
    stops.hold("p1", "c1", lambda: cuts.append("cut"))
    stops.want("p1", "c1")
    assert cuts == ["cut"]


def test_a_stop_asked_before_the_connection_exists_cuts_it_the_moment_it_arrives():
    # The reason this item exists: the press lands while the model is still thinking, and the
    # answer may not have opened its connection yet. Both orders end the same way.
    cuts = []
    stops = MemoryStops()
    stops.want("p1", "c1")
    stops.hold("p1", "c1", lambda: cuts.append("cut"))
    assert cuts == ["cut"]


def test_a_forgotten_connection_is_not_cut():
    # The answer ended and let go of its socket. A stop arriving after that has nothing to reach --
    # and the number it would reach for belongs to somebody else by now.
    cuts = []
    stops = MemoryStops()
    stops.hold("p1", "c1", lambda: cuts.append("cut"))
    stops.clear("p1", "c1")
    stops.want("p1", "c1")
    assert cuts == []


def test_one_chats_connection_is_cut_without_touching_its_neighbours():
    # Per chat, not per project: two chats in one project answer down two connections.
    cuts = []
    stops = MemoryStops()
    stops.hold("p1", "c1", lambda: cuts.append("c1"))
    stops.hold("p1", "c2", lambda: cuts.append("c2"))
    stops.want("p1", "c1")
    assert cuts == ["c1"]
```

---

## 3. `backend/tests/test_xai_engine.py` — bir yeni test

`FakeClient.stream` imzası `on_open`'ı öğrenir ve gördüğünü saklar:

```python
    def stream(self, messages, tools=None, on_open=None):
        self.seen = messages
        self.on_open = on_open
        return iter(["hi"])
```

`__init__`'e `self.on_open = None` girer.

```python
def test_the_way_to_cut_the_answer_travels_down_to_the_client():
    # The engine translates roles and nothing else -- and that includes not swallowing this. Only
    # the client holds a socket, so only the client can hand out a way to cut it.
    client = FakeClient()
    handed = lambda cut: None
    list(XaiEngine(client).stream(CONVERSATION, on_open=handed))
    assert client.on_open is handed
```

---

## 4. `backend/tests/test_stream_answer.py`

### 4.1 Sahteler

`ScriptedEngine`, `on_open`'ı öğrenir ve turun ortasında ölebilir hâle gelir:

```python
CUT = object()
"""Where the connection dies inside a round. In production it is a socket that was shut down and a
body that stopped mid-chunk; here it is a piece the engine refuses to get past."""


class ScriptedEngine:
    """Each round is a list of pieces the engine hands back."""

    def __init__(self, rounds, blow_up_after=None):
        self.rounds = list(rounds)
        self.blow_up_after = blow_up_after
        self.seen = []
        self.handed = []

    # No model since Madde 82: the engine is built knowing which one. A use case that still passed
    # one would die here rather than quietly working.
    def stream(self, messages, tools=None, on_open=None):
        self.seen.append(list(messages))
        if on_open:
            on_open(self._cut)
        if self.blow_up_after is not None and len(self.seen) > self.blow_up_after:
            raise RuntimeError("connection dropped")
        pieces = self.rounds.pop(0) if self.rounds else []
        for piece in pieces:
            if piece is CUT:
                # What http.client says when a chunked body stops in the middle. The words are
                # Python's, and nothing in them says who did it.
                raise RuntimeError("IncompleteRead(0 bytes read)")
            yield piece

    def _cut(self):
        self.handed.append("cut")
```

`NeverStops` `hold`'u öğrenir; `StopsAfter` yerini `Cut`'a bırakır:

```python
class NeverStops:
    """The stop registry as most tests need it: nobody ever asks."""

    def hold(self, project_id, chat_id, cut):
        pass

    def wanted(self, project_id, chat_id):
        return False

    def clear(self, project_id, chat_id):
        pass


NEVER = NeverStops()


class Cut:
    """The registry after a stop: however this answer ended, we are the ones who ended it.

    Replaces the round-counting fake this file used to carry. Nothing counts any more -- the flag
    is not asked frame by frame, so the only question left is whether the cut was ours.
    """

    def __init__(self):
        self.held = []
        self.cleared = []

    def hold(self, project_id, chat_id, cut):
        self.held.append((project_id, chat_id, cut))

    def wanted(self, project_id, chat_id):
        return True

    def clear(self, project_id, chat_id):
        self.cleared.append((project_id, chat_id))
```

### 4.2 İki yeni test

```python
def test_the_running_answer_hands_the_registry_a_way_to_cut_it(tmp_path):
    # The registry is reached from another thread and holds no socket of its own; this is the one
    # moment the two meet.
    stops = Cut()
    _, _, engine, _ = _run(tmp_path, [[{"text": "Hi"}]], stops=stops)
    assert [(p, c) for p, c, _ in stops.held] == [("p1", "c1")]
    stops.held[0][2]()
    assert engine.handed == ["cut"]


def test_a_connection_we_cut_is_a_stop_rather_than_a_failure(tmp_path):
    # Nothing in the failure says who ended it -- our own cut and a network that dropped arrive as
    # the same words. The registry is the only thing that knows, so it is asked before the failure
    # is believed.
    chats, _, _, _ = _run(tmp_path, [[{"text": "Half a "}, CUT]], stops=Cut())
    kept = chats.get("p1", "c1").messages[-1]
    assert kept.text == "Half a"
    assert kept.stopped is True
```

### 4.3 Ölçüsü yeniden türetilen altı test

`TWO_ROUNDS` **değişmiyor**. Bir stop artık turun sonunda okunuyor, ve `Cut()` "bu tur bizim
kestiğimiz tur" demek.

| Test | Bugün | Sonra | Neden aynı an |
|---|---|---|---|
| `test_a_stop_ends_the_answer_without_asking_the_model_again` | `StopsAfter(after=1)` | `Cut()` | 1. tur biter, kesen biziz, 2. tur hiç sorulmaz |
| `test_what_was_already_said_is_kept` | `StopsAfter(after=1)` | `Cut()` | 1. turun söylediği duruyor: `"Half a"` |
| `test_a_stopped_answer_says_it_was_stopped` | `StopsAfter(after=1)` | `Cut()` | aynı an, `stopped is True` |
| `test_stopping_before_a_word_still_writes_that_it_was_stopped` | `after=0`, `[[{"text": "never reached"}]]` | `Cut()`, `[[CUT]]` | kelime gelmeden kesilen bağlantı: tur hatayla ölür, kayıt boş ve `stopped` |
| `test_the_request_is_cleared_when_the_answer_ends` | `StopsAfter(after=1)` | `Cut()` | `cleared == [("p1", "c1")]` |
| `test_a_stopped_answer_still_says_what_it_spent` | `after=2` | `Cut()`, tur `[spent(1200, 900, 5), {"text": "Half a "}, CUT]` | sayı geldi, sonra kesildi — sayı korunuyor |
| `test_an_answer_stopped_before_the_counts_arrive_spent_nothing_it_knows_of` | `after=1` | `Cut()`, tur `[{"text": "Half a "}, CUT, spent(1200, 900, 5)]` | sayıya varmadan kesildi — `Usage()` |

Yedi satır, altı test artı `TWO_ROUNDS` üzerinden gidenlerin ortak sahtesi.

`test_a_stream_that_breaks_writes_nothing` **dokunulmadan** kalır: `blow_up_after=0` ile `NEVER`,
yani kesen biz değiliz, yani hâlâ `EngineFailed`. Bu maddenin en önemli bekçisi o.

### 4.4 `test_stopping_before_a_word...`'ün yeni hâli

```python
def test_stopping_before_a_word_still_writes_that_it_was_stopped(tmp_path):
    # Nothing was said and nothing was made, but something happened: somebody stopped it. Written
    # down, because a press that leaves no trace reads as a press that did nothing -- and because
    # the chat's last word would otherwise still be the user's, which means owed an answer, which
    # means the browser asks for one again the moment the page is reloaded.
    #
    # This is the press the item was written for: it lands while the model is still thinking, and
    # the connection dies before it has said a single word.
    chats, _, _, _ = _run(tmp_path, [[CUT]], stops=Cut())
    kept = chats.get("p1", "c1").messages
    assert [m.role for m in kept] == ["user", "ai"]
    assert kept[-1].text == ""
    assert kept[-1].stopped is True
```

---

## 5. `on_open`'ı öğrenen diğer sahte motorlar

Hiçbiri yeni test almıyor; imzaları uyuyor ki uygulama turu geldiğinde ölmesinler.

- `backend/tests/test_chats_api.py:30` ve `:48`
- `backend/tests/test_files_api.py:17`
- `backend/tests/test_projects_api.py:11`

Hepsinde tek değişiklik: `def stream(self, messages, tools=None, on_open=None):`

---

## Beklenen kırmızı

**On bir yeni test** ve **yeniden türetilen altısı** düşer. Sayıları koşarak değil şuradan
türetiyoruz: `on_open` diye bir parametre, `hold` diye bir söz, ve tur başına bir `wanted` henüz yok.

Düşmemesi gerekenler:

- `test_a_stream_that_breaks_writes_nothing` — arıza hâlâ arıza.
- Ön yüzün tamamı — bu madde ön yüze dokunmuyor.
- `test_stops.py`'nin var olan beş testi — `want`/`wanted`/`clear` aynı şeyi söylüyor.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `client.py`, `xai_engine.py`, `memory_stops.py`, `ports.py`, `stream_answer.py`
  bu turda açılmaz.
- **`/stop` ucuna dokunulmaz** — adresi ve cevabı değişmiyor, var olan üç testi yeşil kalıyor.
- **`dist` derlenmez.**
