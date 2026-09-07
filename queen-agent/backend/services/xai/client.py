"""XaiClient -- HTTP transport for xAI's OpenAI-compatible chat completions.

Knows no prompt, no chat and no file: it takes a message list and returns the assistant's message.
Built on urllib rather than a third-party client because one POST and one SSE stream do not earn a
dependency, an install step and a version to keep up with.
"""
import http.client
import json
import socket
import urllib.error
import urllib.request


class XaiNotConfigured(Exception):
    """No API key. The app still starts; only asking for an answer fails."""


class XaiFailed(Exception):
    """The service answered with an error. Carries its own words, never a guessed cause."""


_DATA = b"data: "
_DONE = object()
# What an xAI address looks like. The conversation header is that service's own, so the base URL is
# asked before it is sent.
_IS_XAI = "x.ai"


def _parsed(raw):
    """One SSE line -> the frame it carries, the done sentinel, or None."""
    line = raw.strip()
    if not line.startswith(_DATA):
        return None  # keep-alives, blank separators and comments carry no content
    payload = line[len(_DATA) :]
    if payload == b"[DONE]":
        return _DONE
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        # One malformed frame must not bring the whole answer down.
        return None


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


def _delta(frame):
    """This frame's delta, or an empty one.

    An empty choices list is a frame with nothing to say, exactly as an empty delta is. The closing
    frame that carries the counts comes that way, and reading it as though a choice were there would
    end the whole answer rather than lose one number.
    """
    choices = frame.get("choices") or []
    if not choices:
        return {}
    return choices[0].get("delta", {})


def _said(frame):
    """The words in this frame, or None."""
    content = _delta(frame).get("content")
    return {"text": content} if content else None


def _fragments(frame):
    """The tool-call pieces in this frame, or None.

    Asked apart from the words since Madde 148. One frame can carry both, and while a single
    function answered for the two of them which one got through was decided by the order the checks
    happened to be written in.
    """
    return _delta(frame).get("tool_calls") or None


class _Calls:
    """Tool-call fragments, joined by index into whole calls (Madde 148).

    xAI sends a function call whole in one chunk and documents that it does. DeepSeek fragments it
    the way OpenAI does: the first piece names the tool, the rest only grow `arguments`. Forwarded
    raw, those later pieces reached the layers above as calls of their own and died on a missing
    name -- so the joining belongs here, where carrying the call is the job.

    `index` is what says which call a piece belongs to; it is absent on a call that arrived whole,
    and then there is exactly one and it is the first. It never reaches the finished record: what
    reads a call wants its id and its function, and the index is this file's own bookkeeping.
    """

    def __init__(self):
        self._by_index = {}
        # First-seen order rather than the index's own number: the field is an identity, not a
        # position, and nothing promises it counts up from zero.
        self._order = []

    def add(self, pieces):
        for piece in pieces:
            index = piece.get("index", 0)
            if index not in self._by_index:
                self._by_index[index] = {}
                self._order.append(index)
            held = self._by_index[index]
            for key, value in piece.items():
                if key == "index":
                    continue
                if key != "function":
                    held[key] = value
                    continue
                function = held.setdefault("function", {})
                for field, part in value.items():
                    # Arguments grow; everything else is stated once and repeated at most.
                    if field == "arguments":
                        function["arguments"] = function.get("arguments", "") + part
                    else:
                        function[field] = part

    def whole(self):
        return [self._by_index[index] for index in self._order]


def _spent(frame):
    """What the answer cost, in our own words rather than the service's, or None.

    Only one frame in a stream carries this, and only when the request asked for it: the service
    adds a closing frame just before the stream ends and leaves every other frame's usage null.
    Asked here of every frame anyway -- which frame it lands on is the service's business, and a
    reader that insisted on the last one would break the day it moved.

    `cached_tokens` sits inside the prompt rather than beside it, so it can never exceed `sent` and
    the difference is what was paid for a second time. Nothing here computes that difference: a
    number that restates two others goes stale on its own.

    Two shapes since Madde 146, because the two services answer the same question differently: xAI
    nests the figure under `prompt_tokens_details`, DeepSeek sends `prompt_cache_hit_tokens` flat
    beside the total and no details object at all. `sent` and `answered` they name alike. Read
    rather than chosen by provider: the frame says which shape it is, and asking it is one fact
    where a lookup by address would be two.
    """
    counts = frame.get("usage")
    if not counts:
        return None
    if "prompt_cache_hit_tokens" in counts:
        cached = counts["prompt_cache_hit_tokens"]
    else:
        cached = counts.get("prompt_tokens_details", {}).get("cached_tokens", 0)
    return {
        "sent": counts.get("prompt_tokens", 0),
        "cached": cached,
        "answered": counts.get("completion_tokens", 0),
    }


class XaiClient:
    def __init__(self, read_key, model, base_url, opener=urllib.request.urlopen):
        # A function rather than a string: where the key comes from is the composition root's
        # decision, and this class is built so that changing it never reaches here. It has changed
        # twice already -- an environment variable, then a settings file, then the environment
        # again -- and none of those touched this line.
        self._read_key = read_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        # The one line that reaches the network, and the one thing a test replaces.
        self._opener = opener

    def write_once(self, messages):
        """One question, answered in one piece: the words and what they cost (Madde 175).

        No tools and no stream. The model on the other end has a sentence to write and nothing to
        call, and there is nobody watching the words arrive -- the answer goes into a file rather
        than onto a screen.

        The same _spent reads the bill here as in the stream, off the payload instead of off a
        frame. Two services shape that figure two ways and one function knows both of them; a
        second reading here would part from that one the day either service moved.
        """
        request = self._request({"messages": messages}, None)
        try:
            with self._opener(request) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as failure:
            # The service's own words: a 401 is not necessarily an expired key, and a wrong model
            # name answers 404 too. Guessing a cause here would print a lie.
            body = failure.read().decode("utf-8", "replace")
            raise XaiFailed(f"{failure.code} {body}") from failure
        except urllib.error.URLError as failure:
            raise XaiFailed(str(failure.reason)) from failure
        message = payload["choices"][0]["message"]
        # Always a dict, even from a service that mentioned nothing: the caller adds this to a
        # total, and a shape that comes and goes is one every caller has to ask about.
        return {"text": message.get("content") or "", "spent": _spent(payload) or {}}

    def stream(self, messages, tools=None, on_open=None, conversation_id=""):
        # The counts come only if asked for, and only to a stream -- so the ask sits beside the
        # stream flag rather than in _request, which serves both roads. Without it every frame's
        # usage field comes back null and the answer costs nothing that anyone can read.
        request = self._request(
            {
                "messages": messages,
                "stream": True,
                "stream_options": {"include_usage": True},
            },
            tools,
            conversation_id=conversation_id,
        )
        try:
            with self._opener(request) as response:
                # Before a single line is read: the wait this hands a way out of is the wait before
                # the first word, and a cut offered after it would miss exactly that stretch.
                if on_open:
                    on_open(lambda: _cut(response))
                calls = _Calls()
                for raw in response:
                    frame = _parsed(raw)
                    if frame is _DONE:
                        # Broken rather than returned since Madde 148: the joined calls are handed
                        # over below, and returning here would drop them.
                        break
                    if frame is None:
                        continue
                    # One frame can carry all three, and really does: the counts ride along with the
                    # words. Words first -- the counts are what those words cost, and a cost does
                    # not arrive before the thing it is for.
                    said = _said(frame)
                    if said:
                        yield said
                    fragments = _fragments(frame)
                    if fragments:
                        calls.add(fragments)
                    counts = _spent(frame)
                    if counts:
                        yield {"usage": counts}
                # After the stream, because a call is whole only once it has stopped growing. Only
                # when something was asked for: an empty list is not "no tools" to the layer above,
                # which reads anything that is neither words nor counts as a call.
                #
                # Left behind on purpose when the stream raises: a cut turn is thrown away whole,
                # and half an `arguments` is not valid JSON anyway.
                whole = calls.whole()
                if whole:
                    yield {"tool_calls": whole}
        except urllib.error.HTTPError as failure:
            body = failure.read().decode("utf-8", "replace")
            raise XaiFailed(f"{failure.code} {body}") from failure
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

    def _request(self, body, tools, conversation_id=""):
        api_key = self._read_key()
        # Not a guessed cause: there is nothing to send, and that is something known here rather
        # than read off a 401 from the other end.
        if not api_key:
            raise XaiNotConfigured("No API key is set.")
        # One model, named once where this client is built. There used to be a per-call one that
        # won over it, back when a chat could pick its own.
        payload = {"model": self._model, **body}
        if tools:
            payload["tools"] = tools
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        # A header rather than a body field: the cache's key is the body's prefix, and an id inside
        # the body would change the very thing it is meant to route to. Only a real name goes -- an
        # empty one would file every caller with no conversation under the same entry.
        #
        # And only to xAI, since Madde 146: this is that service's own way of routing a request to
        # its conversation's cache. DeepSeek matches prefixes by itself and documents nothing of the
        # kind, so sending it there would be a made-up name on somebody else's wire. The address is
        # what decides, because the address is already what says which service this is -- a flag
        # beside it would be the same fact written twice.
        if conversation_id and _IS_XAI in self._base_url:
            headers["x-grok-conv-id"] = conversation_id
        return urllib.request.Request(
            f"{self._base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
