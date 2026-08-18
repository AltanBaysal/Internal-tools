import io
import json
import urllib.error

import pytest

from backend.services.xai.client import XaiClient, XaiFailed, XaiNotConfigured

MESSAGES = [{"role": "user", "content": "hello"}]


class _Response:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def _client(opener, api_key="key"):
    # A function rather than a string: the key is settled in the app's own settings and can change
    # while it runs, so it is read at the moment it is needed.
    return XaiClient(lambda: api_key, "grok-4.5", "https://api.x.ai/v1", opener=opener)


def test_no_key_is_reported_before_anything_is_sent():
    sent = []
    with pytest.raises(XaiNotConfigured) as refused:
        _client(lambda request: sent.append(request), api_key="").complete(MESSAGES)
    assert sent == []
    # The old sentence named an environment variable that no longer exists.
    assert "No API key is set" in str(refused.value)


def test_the_key_is_read_at_every_request():
    keys = ["first", "second"]
    seen = []

    def opener(request):
        seen.append(request.headers["Authorization"])
        return _Response({"choices": [{"message": {"role": "assistant", "content": "hi"}}]})

    client = XaiClient(lambda: keys.pop(0), "grok-4.5", "https://api.x.ai/v1", opener=opener)
    client.complete(MESSAGES)
    client.complete(MESSAGES)
    # Held as a string, saving a key in Settings would need a restart to be worth anything.
    assert seen == ["Bearer first", "Bearer second"]


def test_the_answer_is_the_assistant_message():
    opener = lambda request: _Response({"choices": [{"message": {"role": "assistant", "content": "hi"}}]})
    assert _client(opener).complete(MESSAGES) == {"role": "assistant", "content": "hi"}


def test_the_request_carries_the_model_the_messages_and_the_bearer():
    seen = {}

    def opener(request):
        seen["url"] = request.full_url
        seen["auth"] = request.headers["Authorization"]
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return _Response({"choices": [{"message": {"content": "hi"}}]})

    _client(opener).complete(MESSAGES)
    assert seen["url"] == "https://api.x.ai/v1/chat/completions"
    assert seen["auth"] == "Bearer key"
    assert seen["body"]["model"] == "grok-4.5"
    assert seen["body"]["messages"] == MESSAGES
    # Nothing empty is sent along: tools appear only when there are tools.
    assert "tools" not in seen["body"]


def test_a_model_given_for_the_call_replaces_the_configured_one():
    seen = {}

    def opener(request):
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return _Response({"choices": [{"message": {"content": "hi"}}]})

    _client(opener).complete(MESSAGES, model="grok-4.3")
    assert seen["body"]["model"] == "grok-4.3"


def test_streaming_carries_its_own_model_too():
    seen = {}

    def opener(request):
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return io.BytesIO(b"data: [DONE]\n")

    list(_client(opener).stream(MESSAGES, model="grok-build-0.1"))
    assert seen["body"]["model"] == "grok-build-0.1"


def test_tools_are_sent_when_given():
    seen = {}

    def opener(request):
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return _Response({"choices": [{"message": {"content": "hi"}}]})

    _client(opener).complete(MESSAGES, tools=[{"type": "function"}])
    assert seen["body"]["tools"] == [{"type": "function"}]


def test_an_http_error_carries_the_services_own_words():
    def opener(request):
        raise urllib.error.HTTPError(
            request.full_url, 401, "Unauthorized", {}, io.BytesIO(b'{"error":"bad key"}')
        )

    with pytest.raises(XaiFailed) as failure:
        _client(opener).complete(MESSAGES)
    # A 401 is not necessarily an expired key, so the message repeats what came back.
    assert "401" in str(failure.value)
    assert "bad key" in str(failure.value)


class _Lines:
    def __init__(self, lines):
        self._lines = lines

    def __iter__(self):
        return iter(self._lines)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def _delta_line(text):
    return json.dumps({"choices": [{"delta": {"content": text}}]}).encode("utf-8")


def test_a_stream_becomes_text_pieces():
    lines = [b"data: " + _delta_line("He"), b"data: " + _delta_line("llo"), b"data: [DONE]"]
    assert list(_client(lambda request: _Lines(lines)).stream(MESSAGES)) == [
        {"text": "He"},
        {"text": "llo"},
    ]


def test_the_stream_stops_at_done_even_if_more_follows():
    lines = [b"data: " + _delta_line("a"), b"data: [DONE]", b"data: " + _delta_line("b")]
    assert list(_client(lambda request: _Lines(lines)).stream(MESSAGES)) == [{"text": "a"}]


def test_a_broken_frame_is_skipped_rather_than_dropping_the_stream():
    lines = [b"data: {oops", b": keep-alive", b"", b"data: " + _delta_line("a"), b"data: [DONE]"]
    assert list(_client(lambda request: _Lines(lines)).stream(MESSAGES)) == [{"text": "a"}]


def test_a_tool_call_arrives_whole_in_one_frame():
    # xAI documents it plainly: a function call is returned in whole in a single chunk, so there is
    # nothing to stitch back together here.
    call = {"id": "t1", "function": {"name": "list_files", "arguments": "{}"}}
    frame = json.dumps({"choices": [{"delta": {"tool_calls": [call]}}]}).encode("utf-8")
    lines = [b"data: " + frame, b"data: [DONE]"]
    assert list(_client(lambda request: _Lines(lines)).stream(MESSAGES)) == [
        {"tool_calls": [call]}
    ]


def test_streaming_asks_for_a_stream():
    seen = {}

    def opener(request):
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return _Lines([b"data: [DONE]"])

    list(_client(opener).stream(MESSAGES))
    assert seen["body"]["stream"] is True


def test_a_dead_connection_is_reported_too():
    def opener(request):
        raise urllib.error.URLError("connection refused")

    with pytest.raises(XaiFailed) as failure:
        _client(opener).complete(MESSAGES)
    assert "connection refused" in str(failure.value)
