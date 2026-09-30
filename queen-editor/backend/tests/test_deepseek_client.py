"""The DeepSeek transport (madde 400): an instruction, words and pictures in, the answer's text out.

The client is imported where it is used rather than at the top: a module that is not there yet
would fail collection, and pytest stops the whole session on a collection error.
"""
import base64

import pytest

URL = "https://api.deepseek.com/chat/completions"
PHOTO = ("P0_0.png", b"PNGDATA")


def _module():
    from backend.services.deepseek import client
    return client


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
    return _module().DeepSeekClient(api_key, "deepseek-flash", URL, http=http, timeout=120)


def picture(media_type, data):
    """The part a picture travels as: a data URL, since the file is on this machine and nowhere a
    link could point at."""
    return {"type": "image_url",
            "image_url": {"url": f"data:{media_type};base64,{base64.b64encode(data).decode()}"}}


def test_the_request_carries_the_model_the_instruction_the_picture_and_the_words():
    http = FakeHttp(answering(" integrated_multimodal_description: [Shot 1] she turns "))

    answer = client(http).complete("talimat", "Scenario: kraliçe dönüyor", [PHOTO])

    assert answer == "integrated_multimodal_description: [Shot 1] she turns"
    call = http.calls[0]
    assert call["url"] == URL
    assert call["headers"]["Authorization"] == "Bearer k-1"
    assert call["timeout"] == 120
    # The picture rides in the user message alone: DeepSeek answers 400 to one in the system message.
    assert call["body"] == {
        "model": "deepseek-flash",
        "messages": [{"role": "system", "content": "talimat"},
                     {"role": "user", "content": [
                         picture("image/png", b"PNGDATA"),
                         {"type": "text", "text": "Scenario: kraliçe dönüyor"}]}],
    }


def test_the_picture_s_type_is_read_off_its_name():
    http = FakeHttp(answering("x"))

    client(http).complete("talimat", "söz", [("kare.jpg", b"JPGDATA")])

    assert http.calls[0]["body"]["messages"][1]["content"][0] == picture("image/jpeg", b"JPGDATA")


def test_with_no_words_the_user_message_holds_the_picture_alone():
    http = FakeHttp(answering("x"))

    client(http).complete("talimat", "", [PHOTO])

    assert http.calls[0]["body"]["messages"][1]["content"] == [picture("image/png", b"PNGDATA")]


def test_an_http_error_is_raised_with_the_servers_own_body():
    http = FakeHttp(FakeResponse(status_code=401, text='{"error": "invalid key"}'))

    with pytest.raises(RuntimeError) as blew_up:
        client(http).complete("talimat", "", [PHOTO])

    assert "401" in str(blew_up.value)
    assert '{"error": "invalid key"}' in str(blew_up.value)


def test_an_answer_that_is_not_the_expected_shape_shows_what_came():
    http = FakeHttp(FakeResponse({"choices": []}, text='{"choices": []}'))

    with pytest.raises(RuntimeError) as blew_up:
        client(http).complete("talimat", "", [PHOTO])

    assert '{"choices": []}' in str(blew_up.value)


def test_an_empty_answer_is_a_failure_rather_than_an_empty_prompt():
    http = FakeHttp(answering("   "))

    with pytest.raises(RuntimeError):
        client(http).complete("talimat", "", [PHOTO])


def test_without_a_key_it_says_so_before_it_asks_anything():
    http = FakeHttp(answering("x"))

    with pytest.raises(_module().NotConfigured) as refused:
        client(http, api_key="").complete("talimat", "", [PHOTO])

    assert http.calls == []
    assert "DEEPSEEK_API_KEY" in str(refused.value) and "Colab Secrets" in str(refused.value)


def test_the_key_reaches_the_header_without_the_whitespace_around_it():
    """A key pasted into Colab's secret store can carry a trailing newline, and the header is
    built here."""
    http = FakeHttp(answering("x"))

    client(http, api_key="\n k-1 \n").complete("talimat", "", [PHOTO])

    assert http.calls[0]["headers"]["Authorization"] == "Bearer k-1"


def test_a_key_that_is_only_whitespace_counts_as_no_key():
    http = FakeHttp(answering("x"))

    with pytest.raises(_module().NotConfigured):
        client(http, api_key="   ").complete("talimat", "", [PHOTO])

    assert http.calls == []
