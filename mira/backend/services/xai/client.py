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


class XaiClient:
    def __init__(self, api_key, model, base_url, opener=urllib.request.urlopen):
        self._api_key = api_key
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

    def _request(self, body, tools):
        if not self._api_key:
            raise XaiNotConfigured("XAI_API_KEY is not set")
        payload = {"model": self._model, **body}
        if tools:
            payload["tools"] = tools
        return urllib.request.Request(
            f"{self._base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
