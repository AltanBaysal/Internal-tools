import pytest

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

    def __init__(self, post=None, gets=()):
        self._post = post or FakeResponse({"prompt_id": "p1"})
        self._gets = list(gets)
        self.posted = None
        self.get_calls = []

    def post(self, url, json=None, timeout=None):
        self.posted = (url, json)
        return self._post

    def get(self, url, timeout=None, params=None):
        self.get_calls.append((url, params))
        return self._gets.pop(0) if self._gets else FakeResponse({})


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


def test_interrupt_posts_to_comfy():
    http = FakeHttp()
    client_with(http).interrupt()
    url, _body = http.posted
    assert url == "http://comfy:8188/interrupt"


def test_interrupt_raises_on_http_error():
    http = FakeHttp(post=FakeResponse(status_code=500))
    with pytest.raises(RuntimeError):
        client_with(http).interrupt()
