import itertools
import json
from contextlib import nullcontext
from types import SimpleNamespace

import pytest
import requests

from backend.services.comfy.client import ComfyClient
from backend.services.comfy.errors import ComfyExecutionError


class FakeResponse:
    def __init__(self, payload=None, status_code=200, content=b""):
        self._payload = payload if payload is not None else {}
        self.status_code = status_code
        self.text = "raw body"
        self.content = content

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeHttp:
    """Stands in for the requests module: records calls, replays queued responses."""

    def __init__(self, post=None, gets=(), refuse=False, log=None):
        self._post = post or FakeResponse({"prompt_id": "p1"})
        self._gets = list(gets)
        # Nobody listening on the port: what requests raises when ComfyUI is not up.
        self._refuse = refuse
        # One record, shared with the fake socket, of what happened in which order (madde 410).
        self._log = log
        self.posted = None
        self.post_calls = []
        self.get_calls = []

    def post(self, url, json=None, timeout=None, files=None, data=None):
        self.posted = (url, json)
        self.post_calls.append({"url": url, "json": json, "files": files, "data": data})
        if self._refuse:
            raise requests.ConnectionError(REFUSED)
        return self._post

    def get(self, url, timeout=None, params=None):
        self.get_calls.append((url, params))
        if self._log is not None:
            self._log.append("get")
        if self._refuse:
            raise requests.ConnectionError(REFUSED)
        return self._gets.pop(0) if self._gets else FakeResponse({})


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


# The sentence the user brought back from the session, word for word (madde 230).
REFUSED = ("HTTPConnectionPool(host='127.0.0.1', port=8188): Max retries exceeded with url: "
           "/upload/image (Caused by NewConnectionError('Failed to establish a new connection: "
           "[Errno 111] Connection refused'))")


def client_with(http, **kw):
    # A socket that opens and says nothing: no test reaches a real one, or the library itself. At
    # poll_interval=0 it is not even listened to, so these tests walk the path they walked before.
    kw.setdefault("websocket", FakeWebsocket())
    return ComfyClient("http://comfy:8188", http=http, poll_interval=0, sleep=lambda s: None, **kw)


def test_submit_returns_prompt_id_and_sends_workflow():
    http = FakeHttp()
    assert client_with(http).submit({"3": {}}) == "p1"
    url, body = http.posted
    assert url == "http://comfy:8188/prompt"
    assert body["prompt"] == {"3": {}} and body["client_id"]


def test_submit_raises_with_raw_body_on_http_error():
    http = FakeHttp(post=FakeResponse(status_code=400))
    with pytest.raises(RuntimeError) as exc:
        client_with(http).submit({})
    assert "400" in str(exc.value) and "raw body" in str(exc.value)


def test_submit_raises_on_node_errors():
    http = FakeHttp(post=FakeResponse({"prompt_id": "p1", "node_errors": {"3": "bad"}}))
    with pytest.raises(RuntimeError) as exc:
        client_with(http).submit({})
    assert "node_errors" in str(exc.value)


def _comfy_log(tmp_path, lines=40):
    path = tmp_path / "comfyui.log"
    path.write_text("".join(f"log satırı {n}\n" for n in range(1, lines + 1)), encoding="utf-8")
    return str(path)


def _refused_upload(tmp_path, log_path=None):
    """What an upload raises when nobody listens. The error class is looked up here rather than
    imported at the top: a name that does not exist yet would fail collection and take every other
    test in this file down with it."""
    client = client_with(FakeHttp(refuse=True), log_path=log_path or _comfy_log(tmp_path))
    with pytest.raises(Exception) as exc:
        client.upload_image("P0_0.png", b"PNG")
    return exc.value


def test_an_unreachable_server_is_named_in_the_first_line(tmp_path):
    error = _refused_upload(tmp_path)

    assert str(error).splitlines()[0] == "ComfyUI'ye bağlanılamadı — http://comfy:8188"


def test_the_connection_errors_own_words_are_kept_whole(tmp_path):
    # The cause is not guessed, so what requests really said has to stay: the user copies it out.
    assert REFUSED in str(_refused_upload(tmp_path))


def test_the_last_thirty_lines_of_the_comfy_log_ride_along(tmp_path):
    """Why ComfyUI was not there is only in its own log, and the log dies with the session. Read
    at the moment of failure, it is on the screen while it still exists."""
    text = str(_refused_upload(tmp_path))

    assert "--- comfyui.log · son 30 satır ---" in text
    assert "log satırı 11\n" in text and text.rstrip().endswith("log satırı 40")
    assert "log satırı 10\n" not in text


def test_an_unreadable_log_is_said_with_its_path_and_the_error_still_comes(tmp_path):
    missing = str(tmp_path / "yok.log")

    text = str(_refused_upload(tmp_path, log_path=missing))

    assert text.splitlines()[0] == "ComfyUI'ye bağlanılamadı — http://comfy:8188"
    assert missing in text


def test_waiting_on_history_names_an_unreachable_server_too(tmp_path):
    client = client_with(FakeHttp(refuse=True), log_path=_comfy_log(tmp_path))

    with pytest.raises(Exception) as exc:
        client.wait("p1", timeout=100)

    assert str(exc.value).splitlines()[0] == "ComfyUI'ye bağlanılamadı — http://comfy:8188"


def test_an_unreachable_server_is_the_runs_fault_not_the_frames(tmp_path):
    from backend.services.comfy.errors import ComfyUnreachable

    error = _refused_upload(tmp_path)

    assert isinstance(error, ComfyUnreachable)
    # No answer came at all, so no frame is to blame: the queue retries it and then stops.
    assert not getattr(error, "frame_level", False)


def test_wait_returns_entry_when_history_appears():
    entry = {"outputs": {}, "status": {"status_str": "success"}}
    http = FakeHttp(gets=[FakeResponse({}), FakeResponse({"p1": entry})])
    assert client_with(http).wait("p1", timeout=100) == entry


def test_wait_raises_comfy_error_on_failed_status():
    entry = {"status": {"status_str": "error", "messages": [
        ["execution_error", {"node_id": "9", "node_type": "CheckpointLoaderSimple",
                             "exception_type": "OSError", "exception_message": "no file"}]]}}
    http = FakeHttp(gets=[FakeResponse({"p1": entry})])
    with pytest.raises(ComfyExecutionError) as exc:
        client_with(http).wait("p1", timeout=100)
    assert "CheckpointLoaderSimple" in exc.value.text


def test_wait_times_out():
    # A clock that keeps going: the wait asks it while it listens too, not only at each look.
    ticks = itertools.count(0, 10)
    http = FakeHttp()
    with pytest.raises(TimeoutError):
        client_with(http, now=lambda: next(ticks)).wait("p1", timeout=15)


def test_fetch_output_downloads_the_single_output_image():
    entry = {"outputs": {"55": {"images": [
        {"filename": "a.png", "subfolder": "", "type": "output"},
        {"filename": "preview.png", "subfolder": "", "type": "temp"},
    ]}}}
    http = FakeHttp(gets=[FakeResponse(content=b"PNGDATA")])
    assert client_with(http).fetch_output(entry) == b"PNGDATA"
    _url, params = http.get_calls[0]
    assert params["filename"] == "a.png" and params["type"] == "output"


def test_fetch_output_refuses_when_not_exactly_one_output():
    entry = {"outputs": {"55": {"images": [
        {"filename": "a.png", "type": "output"}, {"filename": "b.png", "type": "output"}]}}}
    with pytest.raises(RuntimeError) as exc:
        client_with(FakeHttp()).fetch_output(entry)
    assert "Batch Size" in str(exc.value)


def test_upload_image_sends_the_file_and_returns_the_servers_name():
    http = FakeHttp(post=FakeResponse({"name": "P0_0.png"}))

    assert client_with(http).upload_image("P0_0.png", b"PNGDATA") == "P0_0.png"
    call = http.post_calls[0]
    assert call["url"] == "http://comfy:8188/upload/image"
    assert call["files"] == {"image": ("P0_0.png", b"PNGDATA")}
    # Overwrite: the same frame uploaded twice must not become "P0_0 (1).png", or LoadImage would
    # keep pointing at the first upload.
    assert call["data"] == {"overwrite": "true"}


def test_upload_image_raises_with_the_servers_own_body():
    http = FakeHttp(post=FakeResponse(status_code=413))

    with pytest.raises(RuntimeError) as blew_up:
        client_with(http).upload_image("P0_0.png", b"PNGDATA")

    assert "413" in str(blew_up.value) and "raw body" in str(blew_up.value)


def test_fetch_output_finds_a_video_among_the_graphs_outputs():
    # A video graph publishes under "gifs" and may carry a preview image node as well.
    entry = {"outputs": {"55": {"images": [{"filename": "a.png", "type": "output"}]},
                         "81": {"gifs": [{"filename": "v.mp4", "subfolder": "", "type": "output"}]}}}
    http = FakeHttp(gets=[FakeResponse(content=b"MP4DATA")])

    assert client_with(http).fetch_output(entry, extensions=(".mp4",)) == b"MP4DATA"
    _url, params = http.get_calls[0]
    assert params["filename"] == "v.mp4"


def test_fetch_output_finds_a_sound_wherever_the_node_published_it():
    # ComfyUI publishes sound under its own key; the extension is what picks the file.
    entry = {"outputs": {"90": {"audio": [{"filename": "s.wav", "subfolder": "",
                                           "type": "output"}]}}}
    http = FakeHttp(gets=[FakeResponse(content=b"WAVDATA")])

    assert client_with(http).fetch_output(entry, extensions=(".wav",)) == b"WAVDATA"


def test_fetch_output_says_what_came_when_no_output_has_the_wanted_extension():
    entry = {"outputs": {"81": {"gifs": [{"filename": "v.webm", "type": "output"}]}}}

    with pytest.raises(RuntimeError) as blew_up:
        client_with(FakeHttp()).fetch_output(entry, extensions=(".mp4",))

    assert "v.webm" in str(blew_up.value)


def test_fetch_output_names_the_wanted_extension_when_none_came():
    # Nothing matched, so the batch size is not the question -- the extension is (madde 245).
    entry = {"outputs": {"81": {"gifs": [{"filename": "v.webm", "type": "output"}]}}}

    with pytest.raises(RuntimeError) as blew_up:
        client_with(FakeHttp()).fetch_output(entry, extensions=(".mp4",))

    assert ".mp4" in str(blew_up.value)
    assert "Batch Size" not in str(blew_up.value)


def test_interrupt_posts_to_comfy():
    http = FakeHttp()
    client_with(http).interrupt()
    url, _body = http.posted
    assert url == "http://comfy:8188/interrupt"


def test_interrupt_raises_on_http_error():
    http = FakeHttp(post=FakeResponse(status_code=500))
    with pytest.raises(RuntimeError):
        client_with(http).interrupt()


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


# --- Madde 411: a prompt's variants in one batch -------------------------------------------------

def test_fetch_outputs_downloads_every_output_in_order():
    # SaveImage lists a batch's files in batch order; the comparer's previews are temp files under
    # keys of their own (rgthree's image_comparer.py).
    entry = {"outputs": {
        "50": {"images": [{"filename": "ComfyUI_00001_.png", "subfolder": "", "type": "output"},
                          {"filename": "ComfyUI_00002_.png", "subfolder": "", "type": "output"},
                          {"filename": "ComfyUI_00003_.png", "subfolder": "", "type": "output"}]},
        "57": {"a_images": [{"filename": "rgthree.compare._temp_00001_.png", "type": "temp"}],
               "b_images": [{"filename": "rgthree.compare._temp_00002_.png", "type": "temp"}]}}}
    http = FakeHttp(gets=[FakeResponse(content=b"ONE"), FakeResponse(content=b"TWO"),
                          FakeResponse(content=b"THREE")])

    assert client_with(http).fetch_outputs(entry, 3) == [b"ONE", b"TWO", b"THREE"]
    assert [params["filename"] for _url, params in http.get_calls] == [
        "ComfyUI_00001_.png", "ComfyUI_00002_.png", "ComfyUI_00003_.png"]


def test_fetch_outputs_stops_when_the_count_is_not_what_was_asked():
    entry = {"outputs": {"50": {"images": [{"filename": "a.png", "type": "output"},
                                           {"filename": "b.png", "type": "output"}]}}}

    with pytest.raises(RuntimeError) as exc:
        client_with(FakeHttp()).fetch_outputs(entry, 3)

    assert "3 çıktı bekleniyordu, 2 geldi" in str(exc.value)
    assert "b.png" in str(exc.value)


# What ComfyUI's /system_stats answers on Colab's T4 (server.py, system_stats).
STATS = {"system": {"os": "linux"},
         "devices": [{"name": "cuda:0 Tesla T4 : cudaMallocAsync", "type": "cuda", "index": 0,
                      "vram_total": 15828320256, "vram_free": 15512174592,
                      "torch_vram_total": 0, "torch_vram_free": 0}]}


def test_vram_total_is_the_card_comfyui_renders_on():
    http = FakeHttp(gets=[FakeResponse(STATS)])

    assert client_with(http).vram_total() == 15828320256
    assert http.get_calls[0][0] == "http://comfy:8188/system_stats"


def test_asking_about_the_card_names_an_unreachable_server_too(tmp_path):
    client = client_with(FakeHttp(refuse=True), log_path=_comfy_log(tmp_path))

    with pytest.raises(Exception) as exc:
        client.vram_total()

    assert str(exc.value).splitlines()[0] == "ComfyUI'ye bağlanılamadı — http://comfy:8188"
