import pytest

from backend.services.xai.client import NotConfigured, XaiClient


class FakeResponse:
    def __init__(self, payload=None, status_code=200, text=""):
        self._payload = payload
        self.status_code = status_code
        self.text = text or ""

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


class FakeHttp:
    """Records the one request the client makes and answers with what the test set up."""

    def __init__(self, response):
        self.response = response
        self.calls = []

    def post(self, url, headers=None, json=None, timeout=None):
        self.calls.append({"url": url, "headers": headers, "body": json, "timeout": timeout})
        return self.response


def answering(text):
    return FakeResponse({"choices": [{"message": {"content": text}}]})


def client(http, api_key="k-1"):
    return XaiClient(api_key, "grok-4.3", "https://api.x.ai/v1/chat/completions", http=http,
                     timeout=120)


def test_the_request_carries_the_model_the_instruction_and_the_prompt():
    http = FakeHttp(answering(" she turns her head slowly "))

    answer = client(http).complete("talimat", "kırmızı elbiseli kadın")

    assert answer == "she turns her head slowly"          # trimmed: the model pads its answers
    call = http.calls[0]
    assert call["url"] == "https://api.x.ai/v1/chat/completions"
    assert call["headers"]["Authorization"] == "Bearer k-1"
    assert call["timeout"] == 120
    assert call["body"] == {
        "model": "grok-4.3",
        "messages": [{"role": "system", "content": "talimat"},
                     {"role": "user", "content": "kırmızı elbiseli kadın"}],
    }


def test_an_http_error_is_raised_with_the_servers_own_body():
    http = FakeHttp(FakeResponse(status_code=401, text='{"error": "invalid key"}'))

    with pytest.raises(RuntimeError) as blew_up:
        client(http).complete("talimat", "prompt")

    assert "401" in str(blew_up.value)
    assert '{"error": "invalid key"}' in str(blew_up.value)


def test_an_answer_that_is_not_the_expected_shape_shows_what_came():
    http = FakeHttp(FakeResponse({"choices": []}, text='{"choices": []}'))

    with pytest.raises(RuntimeError) as blew_up:
        client(http).complete("talimat", "prompt")

    assert '{"choices": []}' in str(blew_up.value)


def test_an_empty_answer_is_a_failure_rather_than_an_empty_prompt():
    http = FakeHttp(answering("   "))

    with pytest.raises(RuntimeError):
        client(http).complete("talimat", "prompt")


def test_without_a_key_it_says_so_before_it_asks_anything():
    http = FakeHttp(answering("x"))

    with pytest.raises(NotConfigured):
        client(http, api_key="").complete("talimat", "prompt")

    assert http.calls == []


def test_the_key_reaches_the_header_without_the_whitespace_around_it():
    """A key pasted into Colab's secret store can carry a trailing newline, and a header reading
    `Bearer sk-...\\n` is what xAI answers 400 to. The client owns the shape of its own header."""
    http = FakeHttp(answering("x"))

    client(http, api_key="\n k-1 \n").complete("talimat", "prompt")

    assert http.calls[0]["headers"]["Authorization"] == "Bearer k-1"


def test_a_key_that_is_only_whitespace_counts_as_no_key():
    """There is a carefully written sentence for a missing key, and a single space must not slip
    past it into xAI's own 400 -- which says far less about what to do."""
    http = FakeHttp(answering("x"))

    with pytest.raises(NotConfigured):
        client(http, api_key="   ").complete("talimat", "prompt")

    assert http.calls == []
