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
    # A function rather than a string: where the key comes from is the composition root's decision,
    # and the client is built so that changing it never reaches here.
    return XaiClient(lambda: api_key, "grok-4.5", "https://api.x.ai/v1", opener=opener)


def test_no_key_is_reported_before_anything_is_sent():
    sent = []
    with pytest.raises(XaiNotConfigured) as refused:
        _client(lambda request: sent.append(request), api_key="").complete(MESSAGES)
    assert sent == []
    # Deliberately does not name where a key would come from. The client is not told, and a sentence
    # that guessed would have been wrong twice already -- once when Settings replaced the
    # environment variable, and again in Madde 62 when the environment took it back.
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
    # Read per request rather than held: the client stays out of the question of where the key comes
    # from, so a source that can change mid-run costs it nothing.
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


# --- what the answer spent, read off the wire (Madde 68) -----------------------------------------


def _usage_line(prompt, cached, completion, text=None):
    """One frame the way xAI really sends it: counts at the top, content beside them.

    Verified against xAI's documentation (26 August) rather than written from memory -- usage rides
    on every chunk, no stream_options is needed to ask for it, and cached_tokens sits inside
    prompt_tokens_details.
    """
    frame = {
        "choices": [{"delta": {"content": text} if text else {}}],
        "usage": {
            "prompt_tokens": prompt,
            "completion_tokens": completion,
            "prompt_tokens_details": {"cached_tokens": cached},
        },
    }
    return b"data: " + json.dumps(frame).encode("utf-8")


def test_a_frame_carrying_counts_hands_them_over():
    # xAI's names are transport; the words the rest of the app uses are decided here, exactly as
    # delta.content already becomes "text".
    lines = [_usage_line(41, 12, 2), b"data: [DONE]"]
    assert list(_client(lambda request: _Lines(lines)).stream(MESSAGES)) == [
        {"usage": {"sent": 41, "cached": 12, "answered": 2}}
    ]


def test_a_frame_can_carry_both_words_and_counts():
    # The real stream does exactly this, and a frame that could only be one thing would drop
    # whichever half lost.
    lines = [_usage_line(41, 12, 2, text="Hi"), b"data: [DONE]"]
    assert list(_client(lambda request: _Lines(lines)).stream(MESSAGES)) == [
        {"text": "Hi"},
        {"usage": {"sent": 41, "cached": 12, "answered": 2}},
    ]


def test_counts_without_a_cache_breakdown_read_as_nothing_cached():
    frame = {"choices": [{"delta": {}}], "usage": {"prompt_tokens": 41, "completion_tokens": 2}}
    lines = [b"data: " + json.dumps(frame).encode("utf-8"), b"data: [DONE]"]
    assert list(_client(lambda request: _Lines(lines)).stream(MESSAGES)) == [
        {"usage": {"sent": 41, "cached": 0, "answered": 2}}
    ]


def test_a_streaming_request_asks_for_the_counts():
    # Madde 76: they do not arrive unless asked for. The API reference is plain about it -- without
    # this option every chunk's usage field comes back null, which is exactly what happened.
    seen = {}

    def opener(request):
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return _Lines([b"data: [DONE]"])

    list(_client(opener).stream(MESSAGES))
    assert seen["body"]["stream_options"] == {"include_usage": True}


def test_a_request_that_is_not_a_stream_does_not_ask():
    # There is nothing to stream an extra chunk into, and an endpoint that does not know the option
    # answers 400 rather than ignoring it. It belongs beside the stream flag, not above it.
    seen = {}

    def opener(request):
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return _Response({"choices": [{"message": {"content": "hi"}}]})

    _client(opener).complete(MESSAGES)
    assert "stream_options" not in seen["body"]


def test_the_closing_counts_frame_does_not_bring_the_answer_down():
    # The counts arrive in one extra frame before [DONE], and that frame has nothing to say -- its
    # choices list is empty. Reading it as though a choice were there ends the whole answer, not
    # just the number.
    frame = {
        "choices": [],
        "usage": {
            "prompt_tokens": 41,
            "completion_tokens": 2,
            "prompt_tokens_details": {"cached_tokens": 12},
        },
    }
    lines = [b"data: " + _delta_line("Hi"), b"data: " + json.dumps(frame).encode("utf-8"), b"data: [DONE]"]
    assert list(_client(lambda request: _Lines(lines)).stream(MESSAGES)) == [
        {"text": "Hi"},
        {"usage": {"sent": 41, "cached": 12, "answered": 2}},
    ]


def test_a_stream_that_says_nothing_about_counts_hands_over_nothing():
    # The guard on every fake engine in the suite: an engine that never mentions spending must not
    # start producing a third kind of piece.
    lines = [b"data: " + _delta_line("a"), b"data: [DONE]"]
    produced = list(_client(lambda request: _Lines(lines)).stream(MESSAGES))
    assert not any("usage" in piece for piece in produced)


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
