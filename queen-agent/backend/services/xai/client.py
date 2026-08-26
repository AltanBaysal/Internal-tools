"""XaiClient -- HTTP transport for xAI's OpenAI-compatible chat completions.

Knows no prompt, no chat and no file: it takes a message list and returns the assistant's message.
Built on urllib rather than a third-party client because one POST and one SSE stream do not earn a
dependency, an install step and a version to keep up with.
"""
import json
import urllib.error
import urllib.request


class XaiNotConfigured(Exception):
    """No API key. The app still starts; only asking for an answer fails."""


class XaiFailed(Exception):
    """The service answered with an error. Carries its own words, never a guessed cause."""


_DATA = b"data: "
_DONE = object()


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


def _spoken(frame):
    """What the model said in this frame: {"text": ...}, {"tool_calls": [...]}, or None.

    Two kinds of thing come down the same wire, so each piece names which it is rather than leaving
    the reader to guess from its type.
    """
    # An empty list is a frame with nothing to say, exactly as an empty delta is. The closing frame
    # that carries the counts comes that way, and reading it as though a choice were there would
    # end the whole answer rather than lose one number.
    choices = frame.get("choices") or []
    if not choices:
        return None
    delta = choices[0].get("delta", {})
    # A function call is documented to arrive whole in a single chunk, so there is nothing to
    # stitch together here.
    if delta.get("tool_calls"):
        return {"tool_calls": delta["tool_calls"]}
    if delta.get("content"):
        return {"text": delta["content"]}
    return None


def _spent(frame):
    """What the answer cost, in our own words rather than the service's, or None.

    Only one frame in a stream carries this, and only when the request asked for it: the service
    adds a closing frame just before the stream ends and leaves every other frame's usage null.
    Asked here of every frame anyway -- which frame it lands on is the service's business, and a
    reader that insisted on the last one would break the day it moved.

    `cached_tokens` sits inside the prompt rather than beside it, so it can never exceed `sent` and
    the difference is what was paid for a second time. Nothing here computes that difference: a
    number that restates two others goes stale on its own.
    """
    counts = frame.get("usage")
    if not counts:
        return None
    return {
        "sent": counts.get("prompt_tokens", 0),
        "cached": counts.get("prompt_tokens_details", {}).get("cached_tokens", 0),
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

    def complete(self, messages, tools=None):
        request = self._request({"messages": messages}, tools)
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
        return payload["choices"][0]["message"]

    def stream(self, messages, tools=None):
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
        )
        try:
            with self._opener(request) as response:
                for raw in response:
                    frame = _parsed(raw)
                    if frame is _DONE:
                        return
                    if frame is None:
                        continue
                    # One frame can carry both, and really does: the counts ride along with the
                    # words. Words first -- the counts are what those words cost, and a cost does
                    # not arrive before the thing it is for.
                    said = _spoken(frame)
                    if said:
                        yield said
                    counts = _spent(frame)
                    if counts:
                        yield {"usage": counts}
        except urllib.error.HTTPError as failure:
            body = failure.read().decode("utf-8", "replace")
            raise XaiFailed(f"{failure.code} {body}") from failure
        except urllib.error.URLError as failure:
            raise XaiFailed(str(failure.reason)) from failure

    def _request(self, body, tools):
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
        return urllib.request.Request(
            f"{self._base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
