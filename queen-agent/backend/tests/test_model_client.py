import io
import json
import socket
import threading
import time
import urllib.error

import pytest

from backend.services.model.client import ModelClient, ModelFailed, ModelNotConfigured

MESSAGES = [{"role": "user", "content": "hello"}]
MODEL = "deepseek-flash"
BASE_URL = "https://api.deepseek.com"
# Short, so a test that waits for the limit waits a fraction of a second rather than config's 180.
IDLE = 0.3


class _Lines:
    def __init__(self, lines):
        self._lines = lines

    def __iter__(self):
        return iter(self._lines)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def _client(opener, api_key="key"):
    # A function rather than a string: where the key comes from is the composition root's decision,
    # and the client is built so that changing it never reaches here.
    #
    # The fakes below take the request alone: the silence limit means something only to a real
    # socket, and the tests that hold it run against one (Madde 460).
    return ModelClient(
        lambda: api_key, MODEL, BASE_URL, IDLE, opener=lambda request, timeout: opener(request)
    )


def test_no_key_is_reported_before_anything_is_sent():
    sent = []
    with pytest.raises(ModelNotConfigured) as refused:
        list(_client(lambda request: sent.append(request), api_key="").stream(MESSAGES))
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
        return _Lines([b"data: [DONE]"])

    client = ModelClient(
        lambda: keys.pop(0), MODEL, BASE_URL, IDLE, opener=lambda request, timeout: opener(request)
    )
    list(client.stream(MESSAGES))
    list(client.stream(MESSAGES))
    # Read per request rather than held: the client stays out of the question of where the key comes
    # from, so a source that can change mid-run costs it nothing.
    assert seen == ["Bearer first", "Bearer second"]


def test_the_request_carries_the_model_the_messages_and_the_bearer():
    seen = {}

    def opener(request):
        seen["url"] = request.full_url
        seen["auth"] = request.headers["Authorization"]
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return _Lines([b"data: [DONE]"])

    list(_client(opener).stream(MESSAGES))
    assert seen["url"] == "https://api.deepseek.com/chat/completions"
    assert seen["auth"] == "Bearer key"
    assert seen["body"]["model"] == MODEL
    assert seen["body"]["messages"] == MESSAGES
    # Nothing empty is sent along: tools appear only when there are tools.
    assert "tools" not in seen["body"]


def test_a_stream_carries_the_configured_model_too():
    # Madde 82: the model is what the client was built with, on both roads. There is no per-call
    # one to override it -- passing one would die on the signature.
    seen = {}

    def opener(request):
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return io.BytesIO(b"data: [DONE]\n")

    list(_client(opener).stream(MESSAGES))
    assert seen["body"]["model"] == MODEL


def test_tools_are_sent_when_given():
    seen = {}

    def opener(request):
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return io.BytesIO(b"data: [DONE]\n")

    list(_client(opener).stream(MESSAGES, tools=[{"type": "function"}]))
    assert seen["body"]["tools"] == [{"type": "function"}]


def test_an_http_error_carries_the_services_own_words():
    def opener(request):
        raise urllib.error.HTTPError(
            request.full_url, 401, "Unauthorized", {}, io.BytesIO(b'{"error":"bad key"}')
        )

    with pytest.raises(ModelFailed) as failure:
        list(_client(opener).stream(MESSAGES))
    # A 401 is not necessarily an expired key, so the message repeats what came back.
    assert "401" in str(failure.value)
    assert "bad key" in str(failure.value)


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
    # The protocol allows a call to come whole in a single chunk, with no index beside it, and then
    # there is nothing to stitch back together.
    call = {"id": "t1", "function": {"name": "list_files", "arguments": "{}"}}
    frame = json.dumps({"choices": [{"delta": {"tool_calls": [call]}}]}).encode("utf-8")
    lines = [b"data: " + frame, b"data: [DONE]"]
    assert list(_client(lambda request: _Lines(lines)).stream(MESSAGES)) == [
        {"tool_calls": [call]}
    ]


# --- a tool call that arrives in pieces (Madde 148) ----------------------------------------------
#
# A call that comes whole is the easy case. DeepSeek does not send it that way: it fragments the
# call the way OpenAI documents, and only the first piece carries the name. Forwarded
# raw, the later pieces reached stream_answer as calls of their own and `call["function"]["name"]`
# died with a bare KeyError -- which is the whole of what the user saw.
#
# The fix belongs here rather than above: the layers above expect a whole call and are right to,
# because fragmentation is a detail of carrying one.


def _piece_line(index, arguments, call_id=None, name=None):
    """One fragment the way DeepSeek really sends it: the first names the tool, the rest only grow
    the arguments. `index` is what says which call a fragment belongs to."""
    function = {"arguments": arguments}
    if name is not None:
        function["name"] = name
    piece = {"index": index, "function": function}
    if call_id is not None:
        piece["id"] = call_id
    frame = {"choices": [{"delta": {"tool_calls": [piece]}}]}
    return b"data: " + json.dumps(frame).encode("utf-8")


def test_a_call_split_across_frames_comes_out_whole():
    lines = [
        _piece_line(0, "", call_id="t1", name="create_file"),
        _piece_line(0, '{"na'),
        _piece_line(0, 'me": "plan.md"}'),
        b"data: [DONE]",
    ]
    assert list(_client(lambda request: _Lines(lines)).stream(MESSAGES)) == [
        {"tool_calls": [{"id": "t1", "function": {"name": "create_file", "arguments": '{"name": "plan.md"}'}}]}
    ]


def test_two_calls_in_one_turn_do_not_mix():
    # Joined by index rather than by arrival: the field exists for this, and two tools asked for in
    # one round interleave their fragments on the wire.
    lines = [
        _piece_line(0, "", call_id="t1", name="read_file"),
        _piece_line(1, "", call_id="t2", name="create_file"),
        _piece_line(0, '{"a": 1}'),
        _piece_line(1, '{"b": 2}'),
        b"data: [DONE]",
    ]
    assert list(_client(lambda request: _Lines(lines)).stream(MESSAGES)) == [
        {
            "tool_calls": [
                {"id": "t1", "function": {"name": "read_file", "arguments": '{"a": 1}'}},
                {"id": "t2", "function": {"name": "create_file", "arguments": '{"b": 2}'}},
            ]
        }
    ]


def test_words_still_arrive_as_they_are_said_and_the_call_closes_the_stream():
    # A model may speak before it reaches for a tool. The words must not wait for the call to be
    # finished -- they are what the user is watching.
    lines = [
        b"data: " + _delta_line("Right"),
        _piece_line(0, "", call_id="t1", name="create_file"),
        _piece_line(0, "{}"),
        b"data: [DONE]",
    ]
    assert list(_client(lambda request: _Lines(lines)).stream(MESSAGES)) == [
        {"text": "Right"},
        {"tool_calls": [{"id": "t1", "function": {"name": "create_file", "arguments": "{}"}}]},
    ]


def test_a_stream_that_called_nothing_says_nothing_about_tools():
    # An empty list is not "no tools": stream_answer reads anything that is not text or usage as a
    # call, so an empty one would be taken for a round that asked for something.
    lines = [b"data: " + _delta_line("just words"), b"data: [DONE]"]
    assert list(_client(lambda request: _Lines(lines)).stream(MESSAGES)) == [{"text": "just words"}]


# --- what the answer spent, read off the wire (Madde 68) -----------------------------------------


def _usage_line(prompt, cached, completion, text=None):
    """One frame in the OpenAI-compatible shape: counts at the top, content beside them, and
    cached_tokens inside prompt_tokens_details."""
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
    # The service's names are transport; the words the rest of the app uses are decided here,
    # exactly as delta.content already becomes "text".
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


def _deepseek_usage_line(prompt, hit, miss, completion):
    """One frame the way DeepSeek really sends it (Madde 146).

    Read off DeepSeek's own documentation (2 September) rather than written from memory: the two
    cache counts sit flat beside prompt_tokens rather than nested, and there is no
    prompt_tokens_details at all. `sent` and `answered` are named as in the shape above.
    """
    frame = {
        "choices": [{"delta": {}}],
        "usage": {
            "prompt_tokens": prompt,
            "completion_tokens": completion,
            "prompt_cache_hit_tokens": hit,
            "prompt_cache_miss_tokens": miss,
        },
    }
    return b"data: " + json.dumps(frame).encode("utf-8")


def test_deepseeks_cache_hit_is_read_as_cached():
    # The same question in two shapes -- what did not have to be paid for a second time. Left
    # unread, a DeepSeek run would report nothing cached forever and the prefix cache could never
    # be told from a cold one.
    lines = [_deepseek_usage_line(1200, 900, 300, 40), b"data: [DONE]"]
    assert list(_client(lambda request: _Lines(lines)).stream(MESSAGES)) == [
        {"usage": {"sent": 1200, "cached": 900, "answered": 40}}
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

    with pytest.raises(ModelFailed) as failure:
        list(_client(opener).stream(MESSAGES))
    assert "connection refused" in str(failure.value)


# --- cutting a stream that is still open (Madde 90) ----------------------------------------------


def test_a_stream_hands_over_the_way_to_cut_it_before_it_reads_a_line():
    # Handed over the moment the response is open, not once words start arriving: the whole point
    # of this item is the wait before the first word, and a cut offered after it would miss exactly
    # the stretch it was written for.
    order = []

    class _Watched(_Lines):
        def __iter__(self):
            order.append("read")
            return super().__iter__()

    list(
        _client(lambda request: _Watched([b"data: [DONE]"])).stream(
            MESSAGES, on_open=lambda cut: order.append("open")
        )
    )
    assert order == ["open", "read"]


def test_cutting_a_response_that_hides_no_socket_is_quiet():
    # Every fake in this suite is such a response. The way down to the socket is CPython's own
    # naming and nobody promised it, so a link that is not there ends the attempt rather than the
    # run.
    held = []
    list(_client(lambda request: _Lines([b"data: [DONE]"])).stream(MESSAGES, on_open=held.append))
    held[0]()


# Chunked on purpose: that is how an SSE stream really arrives, and it is what decides how a cut comes
# back.
HEAD = b"HTTP/1.1 200 OK\r\nContent-Type: text/event-stream\r\nTransfer-Encoding: chunked\r\n\r\n"
END = b"0\r\n\r\n"


def _chunk(line):
    """One SSE line as one chunk of the body."""
    data = line + b"\n\n"
    return f"{len(data):x}\r\n".encode() + data + b"\r\n"


def _service(*replies):
    """A model service on a local socket that answers each connection with the next reply.

    A reply is a list of steps: bytes are sent, a number is a pause in seconds. Whatever a reply leaves
    unsaid is silence -- an empty one never even sends its headers -- and the connection is held until
    the client lets go of it, so the next one is accepted only then. `[HEAD]` is a model that is still
    thinking: it leaves the reader inside recv with no frame to come back for.
    """
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(len(replies))

    def serve():
        with listener:
            for reply in replies:
                connection, _ = listener.accept()
                with connection:
                    # Only so that a test that fails leaves nothing running behind it.
                    connection.settimeout(10)
                    connection.recv(65536)
                    for step in reply:
                        if isinstance(step, bytes):
                            connection.sendall(step)
                        else:
                            time.sleep(step)
                    try:
                        while connection.recv(65536):
                            pass
                    except OSError:
                        pass  # a client that let go abruptly has let go all the same

    threading.Thread(target=serve, daemon=True).start()
    return listener.getsockname()[1]


def _blocked_read():
    """Start a real stream against a service still thinking and hand back what it takes to end it.

    The reading thread is a daemon: a cut that never reaches the socket leaves it blocked for good,
    and the run still has to be able to finish and say so.
    """
    port = _service([HEAD])
    # A limit far past the deadlines below: what ends the read here has to be the cut, on a socket
    # that carries a timeout as every real request does since Madde 460.
    client = ModelClient(lambda: "key", MODEL, f"http://127.0.0.1:{port}", 30)
    outcome = {}
    opened = threading.Event()

    def hand_over(cut):
        outcome["cut"] = cut
        opened.set()

    def read():
        try:
            list(client.stream(MESSAGES, on_open=hand_over))
            outcome["ended"] = "quietly"
        except BaseException as failure:
            outcome["ended"] = failure

    reader = threading.Thread(target=read, daemon=True)
    reader.start()
    # Carries whatever went wrong instead of just saying it did: what the reading thread hit is the
    # only thing that explains why nothing was ever handed over.
    assert opened.wait(5), f"the response never opened: {outcome.get('ended')}"
    return reader, outcome


def test_a_cut_wakes_a_read_that_is_blocked_on_the_socket():
    # The one thing no fake can answer: whether the cut really reaches the socket. Which call does
    # the waking is not the same on every platform, and this is what measured it -- so a run on a
    # machine where it is different fails here rather than in front of somebody pressing stop.
    reader, outcome = _blocked_read()
    outcome["cut"]()
    # A deadline rather than a plain join: a cut that never landed has to fail the run, not hang it.
    reader.join(5)
    assert not reader.is_alive()


def test_a_stream_cut_in_the_middle_comes_back_as_a_failure():
    # A socket shut down between frames leaves a half-read chunked body, and Python says so. It
    # travels in the client's own currency and carries Python's words: who cut it is not something
    # this layer knows, so it does not say.
    reader, outcome = _blocked_read()
    outcome["cut"]()
    reader.join(5)
    assert isinstance(outcome["ended"], ModelFailed)


# --- a request that goes silent is cut (Madde 460) -----------------------------------------------
#
# Against a real socket, because what is held is what the socket does with urllib's timeout: it bounds
# each wait on its own -- the connect, the wait for the headers, every read of the stream -- so it
# measures silence rather than the answer's length. That the black box counts the failure as one
# try is test_black_box.py's: any exception is.


def _local(port):
    return ModelClient(lambda: "key", MODEL, f"http://127.0.0.1:{port}", IDLE)


def _ended(run):
    """What `run` came to, on a thread of its own -- or a failed test if it is still going after five
    seconds, which is how a request that is never cut shows here instead of a run that hangs."""
    outcome = {}

    def target():
        try:
            outcome["value"] = run()
        except BaseException as failure:
            outcome["value"] = failure

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(5)
    assert not thread.is_alive(), "the request was never cut"
    return outcome["value"]


@pytest.mark.parametrize("reply", [[], [HEAD]], ids=["before-the-headers", "after-the-headers"])
def test_a_request_that_goes_silent_is_cut_in_the_sockets_own_words(reply):
    # Two waits and two roads out: silence before the headers ends inside urlopen, silence after them
    # inside the read of the stream. Both come out as the client's failure, carrying the socket's
    # words. A plain socket's, here: over TLS, as every real service is, they read "The read
    # operation timed out", and that is what the chat's card prints then.
    port = _service(reply)
    ended = _ended(lambda: list(_local(port).stream(MESSAGES)))
    assert isinstance(ended, ModelFailed)
    assert str(ended) == "timed out"


def test_an_answer_that_keeps_talking_is_not_cut():
    # Silence, not length: ten words a tenth of a second apart run past three times the limit, and no
    # wait between them comes near it.
    words = [step for _ in range(10) for step in (0.1, _chunk(b"data: " + _delta_line("a")))]
    port = _service([HEAD, *words, _chunk(b"data: [DONE]"), END])
    assert _ended(lambda: list(_local(port).stream(MESSAGES))) == [{"text": "a"}] * 10
