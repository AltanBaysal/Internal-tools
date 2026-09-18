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

    def __init__(self, post=None, gets=(), refuse=False):
        self._post = post or FakeResponse({"prompt_id": "p1"})
        self._gets = list(gets)
        # Nobody listening on the port: what requests raises when ComfyUI is not up.
        self._refuse = refuse
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
        if self._refuse:
            raise requests.ConnectionError(REFUSED)
        return self._gets.pop(0) if self._gets else FakeResponse({})


# The sentence the user brought back from the session, word for word (madde 230).
REFUSED = ("HTTPConnectionPool(host='127.0.0.1', port=8188): Max retries exceeded with url: "
           "/upload/image (Caused by NewConnectionError('Failed to establish a new connection: "
           "[Errno 111] Connection refused'))")


def client_with(http, **kw):
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
    ticks = iter([0, 10, 20, 30])
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
