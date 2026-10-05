"""The box every request to Queen AI goes through (madde 416).

Tried with the real one-request client underneath, so the failures the box sees are the very ones the
client raises: the server answers each request with the next of a list, and the box is asked once.

The box is imported where it is used rather than at the top: a module that cannot be imported would
fail collection, and pytest stops the whole session on a collection error.
"""
import requests

from backend.features.photo_generation.data.prompt_writer import H3VideoPromptWriter
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.usecases.resume_batch import resume_batch
from backend.services.deepseek.client import DeepSeekClient
from backend.tests.test_deepseek_client import URL, FakeResponse, answering
from backend.tests.test_photo_usecases import FakeGenerator, sync_runner, video_job_project

PHOTO = ("P0_0.png", b"PNGDATA")


class Answers:
    """DeepSeek's server, answering each request with the next of `answers` -- a response, or an
    exception the transport raises -- and with the last one again once they run out. Records every
    request."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = []

    def post(self, url, headers=None, json=None, timeout=None):
        self.calls.append({"url": url, "headers": headers, "body": json, "timeout": timeout})
        answer = self.answers[min(len(self.calls), len(self.answers)) - 1]
        if isinstance(answer, Exception):
            raise answer
        return answer


def asking(http, api_key="k-1"):
    """Queen AI as main.py builds it: the box around the one-request client."""
    from backend.services.deepseek.box import Box
    return Box(DeepSeekClient(api_key, "deepseek-flash", URL, http=http, timeout=120))


def test_a_good_answer_comes_back_as_it_is_after_one_request():
    http = Answers([answering(" she turns ")])

    answer = asking(http).ask("talimat", "Scenario: kraliçe dönüyor", [PHOTO])

    assert answer.text == "she turns"
    assert answer.failed is False
    assert len(http.calls) == 1


def test_an_http_error_sends_the_same_request_again():
    http = Answers([FakeResponse(status_code=500, text="iç hata"), answering("she turns")])

    answer = asking(http).ask("talimat", "Scenario: kraliçe dönüyor", [PHOTO])

    assert answer.text == "she turns" and answer.failed is False
    # The same request, word for word and picture for picture: nothing about it was wrong.
    assert len(http.calls) == 2
    assert http.calls[1] == http.calls[0]
    assert http.calls[0]["body"]["messages"][1]["content"][0]["type"] == "image_url"


def test_a_malformed_answer_sends_the_request_again():
    http = Answers([FakeResponse({"choices": []}, text='{"choices": []}'),
                    answering("she turns")])

    answer = asking(http).ask("talimat", "", [PHOTO])

    assert answer.text == "she turns" and answer.failed is False
    assert len(http.calls) == 2


def test_an_empty_answer_sends_the_request_again():
    http = Answers([answering("   "), answering("she turns")])

    answer = asking(http).ask("talimat", "", [PHOTO])

    assert answer.text == "she turns" and answer.failed is False
    assert len(http.calls) == 2


def test_no_answer_at_all_sends_the_request_again():
    """No internet, a timeout: the owner's technical errors (v9-3) are tried again like an HTTP
    one."""
    http = Answers([requests.ConnectionError("Max retries exceeded with url: /chat/completions"),
                    answering("she turns")])

    answer = asking(http).ask("talimat", "", [PHOTO])

    assert answer.text == "she turns" and answer.failed is False
    assert len(http.calls) == 2


def test_five_tries_at_most_then_the_last_error_s_own_text():
    """The box never raises: a caller that loops must not be broken by it (v9-3). What it says is
    the service's own words -- no cause is guessed."""
    busy = [FakeResponse(status_code=503, text=f"meşgul {n}") for n in range(1, 6)]
    http = Answers(busy + [answering("she turns")])

    answer = asking(http).ask("talimat", "", [PHOTO])

    assert len(http.calls) == 5
    assert answer.failed is True
    assert answer.text == "DeepSeek HTTP 503\nmeşgul 5"


def test_when_the_last_try_found_no_server_its_own_words_come_back():
    lost = requests.ConnectionError("Max retries exceeded with url: /chat/completions")
    http = Answers([FakeResponse(status_code=500, text="iç hata")] * 4 + [lost])

    answer = asking(http).ask("talimat", "", [PHOTO])

    assert answer.failed is True
    assert answer.text == str(lost)


def test_without_a_key_nothing_is_sent_and_the_sentence_comes_back_as_a_failure():
    http = Answers([answering("she turns")])

    answer = asking(http, api_key="").ask("talimat", "", [PHOTO])

    assert http.calls == []
    assert answer.failed is True
    assert "DEEPSEEK_API_KEY" in answer.text and "Colab Secrets" in answer.text


def test_a_run_whose_queen_ai_keeps_failing_stops_as_today_after_fifteen_requests():
    """Madde 416 as its done-sentence says it: the run loop's three attempts stay, each holding the
    box's five, and when they are spent the run stops the way it always did -- with the box's text
    on the error line, and the job still owed."""
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    store.files["0_a.png"] = b"PNGDATA"
    http = Answers([FakeResponse(status_code=503, text="meşgul")])
    runner, generator = sync_runner(), FakeGenerator()

    resume_batch(runner, store, record, plan_store, {layers.VIDEO: generator}, lambda: "t",
                 "düğün", writers={layers.VIDEO: H3VideoPromptWriter(asking(http))})

    assert len(http.calls) == 15
    state = runner.status()
    assert state["status"] == "error"
    assert state["error"] == ("Aynı kare 3 kez denendi — üretim durduruldu\n"
                              "DeepSeek HTTP 503\nmeşgul")
    assert generator.calls == []
    assert record.written_prompts("düğün") == {}
    assert [row for row in record.rows if row.get("layer") == "video"] == []
