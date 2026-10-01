# Madde 410 — ComfyUI'nin bitti bildirimi, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `ComfyClient.wait`'in ComfyUI'nin soketini dinlediğini — işi gönderen id'yle, ilk bakıştan
önce açılan, bu prompt'un bitti bildirimiyle hemen biten, en çok bir aralık dinlenen, kopunca ya da
açılmayınca bugünkü bakış aralığına dönen ve her durumda kapanan bir soket — anlatan testler.

**Yaklaşım:** Kütüphane `http=requests` gibi enjekte edilir (`websocket=`). Testler sahte bir modül
verir; sahte soket mesajları sırayla verir, bitince zaman aşımı atar. Saat sahte, yalnız bekleyen
bir şey ilerletir. Bağlanma, `/history` bakışı ve `recv` tek günlüğe yazılır.

**Araçlar:** pytest (`parametrize`), stdlib `json`, `itertools`, `types.SimpleNamespace`,
`contextlib.nullcontext`.

**Spec:** [m410 test turu](../specs/2026-10-01-queen-editor-m410-bitti-bildirimi-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**; dosyanın bugünkü üslubu gibi assert'ler mesajsız.
- Testler dört satırla koşulur; `skip` / `xfail` yok. Bu turda kaynak kod değişmiyor.
- Hiçbir test gerçek bir soket açmaz, gerçek bir saniye beklemez; `client_with` de sahte soket verir.

**Arayüz — uygulama turunun vereceği:**
- `ComfyClient(base_url, http=requests, poll_interval=5, sleep=time.sleep, now=time.monotonic,
  log_path="", websocket=None)` — `websocket` websocket-client modülünün yerine geçen nesne;
  verilmezse kütüphanenin kendisi, ilk kullanımda içe aktarılır.
- Kullandığı: `websocket.create_connection(url, timeout=...)` → bağlantı; bağlantıda
  `settimeout(seconds)`, `recv()` → `str` | `bytes`, `close()`; istisnalar
  `websocket.WebSocketTimeoutException` (zaman aşımı) ve `websocket.WebSocketException` (taban), ve
  `OSError`.
- URL: `ws://comfy:8188/ws?clientId=<client_id>`.

---

## Görev 1: `test_comfy_client.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_comfy_client.py`

- [ ] **Adım 1: İçe aktarmalar.** Dosyanın başı:

```python
import itertools
import json
from contextlib import nullcontext
from types import SimpleNamespace

import pytest
import requests

from backend.services.comfy.client import ComfyClient
from backend.services.comfy.errors import ComfyExecutionError
```

- [ ] **Adım 2: `FakeHttp` günlük alır.** `__init__`'e `log=None`, ve `get`'in başında:

```python
    def __init__(self, post=None, gets=(), refuse=False, log=None):
        ...
        # One record, shared with the fake socket, of what happened in which order (madde 410).
        self._log = log

    def get(self, url, timeout=None, params=None):
        self.get_calls.append((url, params))
        if self._log is not None:
            self._log.append("get")
        ...
```

- [ ] **Adım 3: Sahte soket, sahte modül, saat** — `FakeHttp`'nin altına:

```python
class FakeSocketError(Exception):
    """websocket-client's WebSocketException: everything it raises comes from this."""


class FakeSocketTimeout(FakeSocketError):
    """Its WebSocketTimeoutException: recv waited out its timeout and nothing came."""


class FakeSocketClosed(FakeSocketError):
    """Its WebSocketConnectionClosedException: the other end went away."""


class Clock:
    """The wait's clock, moved only by what takes time: a sleep, or a socket waiting."""

    def __init__(self):
        self.now = 0
        self.sleeps = []

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


class FakeSocket:
    """A connection the way websocket-client hands it back.

    Gives the queued messages in order -- a str is a text frame, bytes a preview, an exception is
    raised -- and once they run out it behaves like a socket nothing more comes over: it waits out
    its timeout and raises. Each message moves the clock by `step` seconds.
    """

    def __init__(self, messages=(), log=None, clock=None, step=0):
        self._messages = list(messages)
        self._log = log if log is not None else []
        self._clock = clock
        self._step = step
        self.timeouts = []
        self.closed = False

    def settimeout(self, seconds):
        self.timeouts.append(seconds)

    def recv(self):
        self._log.append("recv")
        if not self._messages:
            if self._clock is not None and self.timeouts:
                self._clock.now += self.timeouts[-1]
            raise FakeSocketTimeout("timed out")
        if self._clock is not None:
            self._clock.now += self._step
        message = self._messages.pop(0)
        if isinstance(message, Exception):
            raise message
        return message

    def close(self):
        self.closed = True


class FakeWebsocket:
    """Stands in for the websocket-client module: hands out its one socket, or refuses."""

    WebSocketException = FakeSocketError
    WebSocketTimeoutException = FakeSocketTimeout

    def __init__(self, socket=None, refuse=False, log=None):
        self.socket = socket if socket is not None else FakeSocket()
        self._refuse = refuse
        self._log = log
        self.urls = []
        self.timeouts = []

    def create_connection(self, url, timeout=None):
        self.urls.append(url)
        self.timeouts.append(timeout)
        if self._log is not None:
            self._log.append("connect")
        if self._refuse:
            raise ConnectionRefusedError(111, "Connection refused")
        return self.socket
```

- [ ] **Adım 4: `client_with` susan bir soket verir.**

```python
def client_with(http, **kw):
    # A socket that opens and says nothing: no test reaches a real one, or the library itself. At
    # poll_interval=0 it is not even listened to, so these tests walk the path they walked before.
    kw.setdefault("websocket", FakeWebsocket())
    return ComfyClient("http://comfy:8188", http=http, poll_interval=0, sleep=lambda s: None, **kw)
```

- [ ] **Adım 5: `test_wait_times_out`'un saati durmaz.**

```python
def test_wait_times_out():
    # A clock that keeps going: the wait asks it while it listens too, not only at each look.
    ticks = itertools.count(0, 10)
    http = FakeHttp()
    with pytest.raises(TimeoutError):
        client_with(http, now=lambda: next(ticks)).wait("p1", timeout=15)
```

- [ ] **Adım 6: Dosyanın sonuna on bir test** *(10'u iki durumla parametreli)*.

```python
# --- Madde 410: ComfyUI's done notice -----------------------------------------------------------

ENTRY = {"outputs": {}, "status": {"status_str": "success"}}
FAILED = {"status": {"status_str": "error", "messages": [
    ["execution_error", {"node_id": "9", "node_type": "CheckpointLoaderSimple",
                         "exception_type": "OSError", "exception_message": "no file"}]]}}


def notice(kind, **data):
    """A text frame the way ComfyUI's server sends one: {"type": ..., "data": {...}}."""
    return json.dumps({"type": kind, "data": data})


# What ComfyUI's prompt worker sends once the prompt's /history entry is written -- after a success,
# a failure and an interrupt alike (ComfyUI's main.py, prompt_worker).
DONE = notice("executing", node=None, prompt_id="p1")


def listening(messages=(), gets=(), refuse=False, step=0):
    """A client that listens: a five second interval, a socket that gives `messages`, and /history
    answering `gets` in turn. One log holds what happened in order, and the clock moves only when
    something waits."""
    log, clock = [], Clock()
    socket = FakeSocket(messages, log=log, clock=clock, step=step)
    websocket = FakeWebsocket(socket, refuse=refuse, log=log)
    http = FakeHttp(gets=[FakeResponse(answer) for answer in gets], log=log)
    client = ComfyClient("http://comfy:8188", http=http, poll_interval=5, sleep=clock.sleep,
                         now=clock, websocket=websocket)
    return SimpleNamespace(client=client, log=log, clock=clock, socket=socket,
                           websocket=websocket, http=http)


def test_the_socket_opens_under_the_id_the_prompt_was_sent_with():
    """ComfyUI sends a prompt's notices only to the client_id it was submitted with."""
    run = listening(gets=[{"p1": ENTRY}])

    run.client.submit({"3": {}})
    run.client.wait("p1", timeout=100)

    assert run.websocket.urls == [f"ws://comfy:8188/ws?clientId={run.client.client_id}"]
    assert run.http.posted[1]["client_id"] == run.client.client_id


def test_the_socket_opens_before_the_first_look_at_history():
    """A notice sent while no socket is open under the id is dropped (ComfyUI's server.py,
    send_json). Opened first, the socket hears a prompt that ends after the look, and the look finds
    one that ended before it."""
    run = listening(gets=[{"p1": ENTRY}])

    run.client.wait("p1", timeout=100)

    assert run.log[:2] == ["connect", "get"]


def test_the_done_notice_ends_the_wait_at_once():
    """The item itself (madde 410): a finished prompt is fetched when ComfyUI says it is done, not at
    the next look five seconds on."""
    run = listening(messages=[DONE], gets=[{}, {"p1": ENTRY}])

    assert run.client.wait("p1", timeout=100) == ENTRY
    assert run.log == ["connect", "get", "recv", "get"]
    assert run.clock.now == 0 and run.clock.sleeps == []


def test_only_this_prompts_done_notice_ends_the_wait():
    """While a prompt runs the socket carries a progress for every step, an executing for every node
    and binary previews; another prompt's done notice is not this one's."""
    run = listening(messages=[notice("progress", value=3, max=30, prompt_id="p1", node="3"),
                              notice("executing", node="3", prompt_id="p1"),
                              notice("executing", node=None, prompt_id="p0"),
                              b"\x00\x00\x00\x01preview",
                              DONE],
                    gets=[{}, {"p1": ENTRY}])

    assert run.client.wait("p1", timeout=100) == ENTRY
    assert run.log == ["connect", "get"] + ["recv"] * 5 + ["get"]


def test_after_the_notice_history_still_says_what_happened():
    """The notice comes after a failure too; what failed is read where it was read before."""
    run = listening(messages=[DONE], gets=[{}, {"p1": FAILED}])

    with pytest.raises(ComfyExecutionError) as failed:
        run.client.wait("p1", timeout=100)

    assert "CheckpointLoaderSimple" in failed.value.text


def test_a_silent_socket_looks_at_history_once_the_interval_passes():
    """A notice that never comes costs the interval, as before madde 410 -- and no sleep on top: the
    socket did the waiting. Opening it waits no longer than that either."""
    run = listening(gets=[{}, {"p1": ENTRY}])

    assert run.client.wait("p1", timeout=100) == ENTRY
    assert run.log == ["connect", "get", "recv", "get"]
    assert run.socket.timeouts == [5]
    assert 0 < run.websocket.timeouts[0] <= 5
    assert run.clock.sleeps == []


def test_the_socket_is_never_listened_to_past_the_interval():
    """Messages do not stop while a prompt runs. Listening until they did would never look at
    /history again if the notice were missed, and the stall guard is checked between the looks."""
    progress = notice("progress", value=1, max=30, prompt_id="p1", node="3")
    run = listening(messages=[progress] * 20, gets=[{}, {"p1": ENTRY}], step=1)

    assert run.client.wait("p1", timeout=100) == ENTRY
    heard = run.log[2:].index("get")
    assert 1 <= heard <= 5
    assert all(seconds <= 5 for seconds in run.socket.timeouts)


def test_a_dropped_socket_is_let_go_and_the_interval_is_slept():
    """ComfyUI going away mid-prompt costs the speed-up for the rest of this prompt, never the
    prompt: the looks go on five seconds apart, as before."""
    run = listening(messages=[FakeSocketClosed("Connection to remote host was lost.")],
                    gets=[{}, {}, {"p1": ENTRY}])

    assert run.client.wait("p1", timeout=100) == ENTRY
    assert run.log.count("recv") == 1
    assert run.socket.closed
    assert run.clock.sleeps and set(run.clock.sleeps) == {5}


def test_a_socket_that_does_not_open_leaves_the_wait_as_it_was():
    """No socket, no notice: look, sleep the interval, look -- the wait before madde 410."""
    run = listening(refuse=True, gets=[{}, {"p1": ENTRY}])

    assert run.client.wait("p1", timeout=100) == ENTRY
    assert "recv" not in run.log
    assert run.clock.sleeps == [5]


@pytest.mark.parametrize("answer, ends", [
    (ENTRY, nullcontext()),
    (FAILED, pytest.raises(ComfyExecutionError)),
], ids=["done", "failed"])
def test_the_socket_is_closed_when_the_wait_ends(answer, ends):
    """One socket per wait: the next prompt opens its own."""
    run = listening(gets=[{"p1": answer}])

    with ends:
        run.client.wait("p1", timeout=100)

    assert run.socket.closed


def test_the_stall_guard_still_stops_a_prompt_that_never_ends():
    """RENDER_TIMEOUT and VIDEO_TIMEOUT stay what they were: the guard against a prompt that never
    comes back, checked between the looks, in the words it had."""
    run = listening(gets=[])

    with pytest.raises(TimeoutError) as stalled:
        run.client.wait("p1", timeout=12)

    assert str(stalled.value) == "prompt p1: 12s içinde bitmedi"
    assert run.socket.closed
```

## Görev 2: Koşu ve commit

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-editor` pytest'inde `test_comfy_client.py`'nin tamamı kırmızı, hepsi
`TypeError: ComfyClient.__init__() got an unexpected keyword argument 'websocket'` ile. Öteki her
şey yeşil — `test_composition_root.py` ve `test_requirements.py` dahil. Öteki üç satır yeşil.

- [ ] **Adım 2: Commit, kırmızı** — testler, spec ve bu plan:

```powershell
git add queen-editor/backend/tests/test_comfy_client.py docs/superpowers/specs/2026-10-01-queen-editor-m410-bitti-bildirimi-testler-design.md docs/superpowers/plans/2026-10-01-queen-editor-m410-bitti-bildirimi-testler-plan.md
git commit -m @'
test(queen-editor): Madde 410 red -- ComfyClient.wait listens on ComfyUI's socket under the id it submits with, opened before the first look at /history; this prompt's executing with no node ends the wait at once, nothing else does, and /history still says what happened; the socket is listened to for one interval at most, a dropped or refused one leaves the five second looks as they were, and it is closed however the wait ends; the stall guard keeps its words

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
