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
    return XaiClient(api_key, "grok-4.5", "https://api.x.ai/v1", opener=opener)


def test_no_key_is_reported_before_anything_is_sent():
    sent = []
    with pytest.raises(XaiNotConfigured):
        _client(lambda request: sent.append(request), api_key="").complete(MESSAGES)
    assert sent == []


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


def test_a_dead_connection_is_reported_too():
    def opener(request):
        raise urllib.error.URLError("connection refused")

    with pytest.raises(XaiFailed) as failure:
        _client(opener).complete(MESSAGES)
    assert "connection refused" in str(failure.value)
