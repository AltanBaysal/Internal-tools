"""The box every request to Queen AI goes through (madde 416), the check it puts every answer
through (madde 418), and the conversation with tools it carries for the agent (madde 419).

Tried with the real one-request client underneath, so the failures the box sees are the very ones the
client raises: the server answers each request with the next of a list -- the check's request among
them -- and the box is asked once.

The box is imported where it is used rather than at the top: a module that cannot be imported would
fail collection, and pytest stops the whole session on a collection error.
"""
import pytest
import requests

from backend.features.photo_generation.data.prompt_writer import H3VideoPromptWriter
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.usecases.resume_batch import resume_batch
from backend.services.deepseek.client import DeepSeekClient
from backend.tests.test_deepseek_client import URL, FakeResponse, answering
from backend.tests.test_photo_usecases import FakeGenerator, sync_runner, video_job_project

PHOTO = ("P0_0.png", b"PNGDATA")

# What the check says of an answer it lets through, and of one it does not (madde 418).
APPROVED = answering("APPROVED")
REFUSAL = answering("REFUSAL")
# A model declining, in the words DeepSeek uses.
SORRY = answering("I'm sorry, I can't help with that.")
# What the box tells its caller when the last try was refused (v9-3), letter for letter.
SENTENCE = "Model hata döndü, farklı şekilde dene."


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


def _check_instruction():
    from backend.services.deepseek.box import CHECK_INSTRUCTION
    return CHECK_INSTRUCTION


def test_a_good_answer_comes_back_as_it_is_once_the_check_approves_it():
    http = Answers([answering(" she turns "), APPROVED])

    answer = asking(http).ask("talimat", "Scenario: kraliçe dönüyor", [PHOTO])

    assert answer.text == "she turns"
    assert answer.failed is False
    # The answer's request, then its check: nothing more.
    assert len(http.calls) == 2


def test_an_http_error_sends_the_same_request_again():
    http = Answers([FakeResponse(status_code=500, text="iç hata"), answering("she turns"),
                    APPROVED])

    answer = asking(http).ask("talimat", "Scenario: kraliçe dönüyor", [PHOTO])

    assert answer.text == "she turns" and answer.failed is False
    # The same request, word for word and picture for picture: nothing about it was wrong.
    assert len(http.calls) == 3
    assert http.calls[1] == http.calls[0]
    assert http.calls[0]["body"]["messages"][1]["content"][0]["type"] == "image_url"


def test_a_malformed_answer_sends_the_request_again():
    http = Answers([FakeResponse({"choices": []}, text='{"choices": []}'),
                    answering("she turns"), APPROVED])

    answer = asking(http).ask("talimat", "", [PHOTO])

    assert answer.text == "she turns" and answer.failed is False
    assert len(http.calls) == 3


def test_an_empty_answer_sends_the_request_again():
    http = Answers([answering("   "), answering("she turns"), APPROVED])

    answer = asking(http).ask("talimat", "", [PHOTO])

    assert answer.text == "she turns" and answer.failed is False
    assert len(http.calls) == 3


def test_no_answer_at_all_sends_the_request_again():
    """No internet, a timeout: the owner's technical errors (v9-3) are tried again like an HTTP
    one."""
    http = Answers([requests.ConnectionError("Max retries exceeded with url: /chat/completions"),
                    answering("she turns"), APPROVED])

    answer = asking(http).ask("talimat", "", [PHOTO])

    assert answer.text == "she turns" and answer.failed is False
    assert len(http.calls) == 3


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


# --- Madde 418: the check ------------------------------------------------------------------------

def test_the_answer_is_checked_word_for_word_in_a_request_of_its_own():
    """The owner's words (v9-3): the text that came back goes to DeepSeek as it is, in a request of
    its own, to be checked. The check is shown the answer alone -- not the request, not the
    pictures."""
    said = ("integrated_multimodal_description: [Shot 1] she turns\n\n"
            "overall_soundscape: Silk rustles. No one speaks.")
    http = Answers([answering(said), APPROVED])

    answer = asking(http).ask("talimat", "Scenario: kraliçe dönüyor", [PHOTO])

    assert answer.text == said and answer.failed is False
    asked, check = http.calls
    assert check["url"] == asked["url"]
    assert check["headers"] == asked["headers"]
    assert check["timeout"] == asked["timeout"]
    assert check["body"] == {
        "model": "deepseek-flash",
        "messages": [{"role": "system", "content": _check_instruction()},
                     {"role": "user", "content": [{"type": "text", "text": said}]}],
    }


@pytest.mark.parametrize("verdict", ["REFUSAL", "I'm unable to review this content."],
                         ids=["refusal", "the-check-s-own-words"])
def test_anything_but_the_approval_sends_the_same_request_again(verdict):
    """Only an approval lets an answer through -- the owner's "onay verirse ... yoksa tekrardan
    istek atıyoruz". Anything else the check says, a check that will not judge included, is a
    refusal, and the request goes again as it was."""
    http = Answers([SORRY, answering(verdict), answering("she turns"), APPROVED])

    answer = asking(http).ask("talimat", "Scenario: kraliçe dönüyor", [PHOTO])

    assert answer.text == "she turns" and answer.failed is False
    assert len(http.calls) == 4
    assert http.calls[2] == http.calls[0]


def test_an_error_of_the_check_itself_is_a_try_and_the_request_goes_again():
    http = Answers([answering("she turns"), FakeResponse(status_code=503, text="meşgul"),
                    answering("she turns"), APPROVED])

    answer = asking(http).ask("talimat", "Scenario: kraliçe dönüyor", [PHOTO])

    assert answer.text == "she turns" and answer.failed is False
    assert len(http.calls) == 4
    assert http.calls[2] == http.calls[0]


def test_five_refusals_come_back_as_the_sentence_after_ten_requests():
    """The box never raises, refused or not: a caller that loops must not be broken by it (v9-3).
    A refusal is not passed on in the model's words -- the caller is told to ask another way."""
    http = Answers([SORRY, REFUSAL] * 5 + [answering("she turns"), APPROVED])

    answer = asking(http).ask("talimat", "", [PHOTO])

    assert len(http.calls) == 10
    assert answer.failed is True
    assert answer.text == SENTENCE


def test_errors_and_refusals_spend_the_same_five_tries_and_a_last_refusal_says_the_sentence():
    http = Answers([FakeResponse(status_code=503, text="meşgul")] * 4
                   + [SORRY, REFUSAL, answering("she turns"), APPROVED])

    answer = asking(http).ask("talimat", "", [PHOTO])

    assert len(http.calls) == 6
    assert answer.failed is True
    assert answer.text == SENTENCE


def test_a_last_try_that_failed_on_the_wire_comes_back_in_its_own_words_after_refusals():
    """The last try's kind decides what the caller is told: a technical failure in its own words,
    even after four refusals -- here the check's own error."""
    http = Answers([SORRY, REFUSAL] * 4
                   + [answering("she turns"), FakeResponse(status_code=503, text="meşgul"),
                      answering("she turns"), APPROVED])

    answer = asking(http).ask("talimat", "", [PHOTO])

    assert len(http.calls) == 10
    assert answer.failed is True
    assert answer.text == "DeepSeek HTTP 503\nmeşgul"


def test_the_check_text_asks_for_the_word_the_box_waits_for():
    text = _check_instruction()

    assert "APPROVED" in text and "REFUSAL" in text


def test_the_check_text_speaks_of_an_answer_to_a_request_and_nothing_of_queen_editor_s():
    """QueenAgent's box will send the same text word for word (v10-1b), where the answer is an
    agent's reply rather than a video prompt."""
    text = _check_instruction().lower()

    assert "video" not in text and "prompt" not in text


def test_a_run_whose_queen_ai_keeps_refusing_stops_as_today_with_the_sentence():
    """Madde 418 as its done-sentence says it: a refusal is never written on the card. The run
    loop's three attempts each hold the box's five tries of an answer and its check, and when they
    are spent the run stops the way it always did -- with the box's sentence on the error line, and
    the job still owed."""
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    store.files["0_a.png"] = b"PNGDATA"
    http = Answers([SORRY, REFUSAL] * 15)
    runner, generator = sync_runner(), FakeGenerator()

    resume_batch(runner, store, record, plan_store, {layers.VIDEO: generator}, lambda: "t",
                 "düğün", writers={layers.VIDEO: H3VideoPromptWriter(asking(http))})

    assert len(http.calls) == 30
    state = runner.status()
    assert state["status"] == "error"
    assert state["error"] == f"Aynı kare 3 kez denendi — üretim durduruldu\n{SENTENCE}"
    assert generator.calls == []
    assert record.written_prompts("düğün") == {}
    assert [row for row in record.rows if row.get("layer") == "video"] == []


# --- Madde 419: the conversation with tools ------------------------------------------------------

# A conversation the way the agent's loop holds it (madde 420): its instruction, the user's question,
# a tool call the model made and what the tool said back.
READ_FRAME = {"id": "call_1", "type": "function",
              "function": {"name": "read_frame", "arguments": '{"frame": 3}'}}
HISTORY = [{"role": "system", "content": "talimat"},
           {"role": "user", "content": "3 numaralı karede ne var?"},
           {"role": "assistant", "content": "", "tool_calls": [READ_FRAME]},
           {"role": "tool", "tool_call_id": "call_1", "content": "Kare 3: kırmızı elbiseli kadın"}]
TOOLS = [{"type": "function",
          "function": {"name": "read_frame", "description": "Reads one frame of the open project.",
                       "parameters": {"type": "object",
                                      "properties": {"frame": {"type": "integer"}},
                                      "required": ["frame"]}}}]
# The calls the model makes next.
LOOK = {"id": "call_2", "type": "function",
        "function": {"name": "look_at_frame", "arguments": '{"frame": 3}'}}
READ_NEXT = {"id": "call_3", "type": "function",
             "function": {"name": "read_frame", "arguments": '{"frame": 4}'}}
SAID = "Kare 3'te kırmızı elbiseli bir kadın var."


def calling(*calls, text=None):
    """DeepSeek answering with tool calls, the way it sends them: with no words, the content is
    null."""
    return FakeResponse({"choices": [{"message": {"role": "assistant", "content": text,
                                                  "tool_calls": list(calls)}}]})


def test_the_conversation_and_the_tools_go_to_deepseek_as_they_are():
    http = Answers([answering(SAID), APPROVED])

    asking(http).converse(HISTORY, TOOLS)

    asked = http.calls[0]
    assert asked["url"] == URL
    assert asked["headers"]["Authorization"] == "Bearer k-1"
    assert asked["timeout"] == 120
    assert asked["body"] == {"model": "deepseek-flash", "messages": HISTORY, "tools": TOOLS}


def test_without_tools_the_request_offers_none():
    """QueenAgent's last round is offered nothing to call, and 420 does what QueenAgent does at the
    step limit (v9-4)."""
    http = Answers([answering(SAID), APPROVED])

    asking(http).converse(HISTORY)

    assert http.calls[0]["body"] == {"model": "deepseek-flash", "messages": HISTORY}


def test_a_tool_call_comes_back_whole_and_unchecked():
    """Only words are checked (v9-3): an answer that calls a tool goes back with no check request."""
    http = Answers([calling(LOOK)])

    answer = asking(http).converse(HISTORY, TOOLS)

    assert answer.tool_calls == [LOOK]
    assert answer.text == ""
    assert answer.failed is False and answer.refused is False
    assert len(http.calls) == 1


def test_words_beside_tool_calls_come_back_with_them_unchecked():
    http = Answers([calling(LOOK, READ_NEXT, text=" Kareye bakıyorum. ")])

    answer = asking(http).converse(HISTORY, TOOLS)

    assert answer.text == "Kareye bakıyorum."
    assert answer.tool_calls == [LOOK, READ_NEXT]
    assert len(http.calls) == 1


def test_a_text_answer_is_checked_the_way_a_prompt_is():
    http = Answers([answering(SAID), APPROVED])

    answer = asking(http).converse(HISTORY, TOOLS)

    assert answer.text == SAID and answer.tool_calls == []
    assert answer.failed is False and answer.refused is False
    asked, check = http.calls
    assert check["url"] == asked["url"]
    assert check["headers"] == asked["headers"]
    assert check["timeout"] == asked["timeout"]
    assert check["body"] == {
        "model": "deepseek-flash",
        "messages": [{"role": "system", "content": _check_instruction()},
                     {"role": "user", "content": [{"type": "text", "text": SAID}]}],
    }


def test_a_refused_text_answer_sends_the_same_conversation_again():
    http = Answers([SORRY, REFUSAL, calling(LOOK)])

    answer = asking(http).converse(HISTORY, TOOLS)

    assert answer.tool_calls == [LOOK]
    assert answer.failed is False and answer.refused is False
    assert len(http.calls) == 3
    assert http.calls[2] == http.calls[0]


@pytest.mark.parametrize("failure", [
    FakeResponse(status_code=500, text="iç hata"),
    FakeResponse({"choices": []}, text='{"choices": []}'),
    FakeResponse({"choices": [{"message": {"role": "assistant", "content": None}}]},
                 text='{"choices": [{"message": {"role": "assistant", "content": null}}]}'),
    requests.ConnectionError("Max retries exceeded with url: /chat/completions"),
], ids=["http-error", "malformed", "neither-words-nor-calls", "no-answer-at-all"])
def test_a_failed_request_sends_the_same_conversation_again(failure):
    http = Answers([failure, calling(LOOK)])

    answer = asking(http).converse(HISTORY, TOOLS)

    assert answer.tool_calls == [LOOK] and answer.failed is False
    assert len(http.calls) == 2
    assert http.calls[1] == http.calls[0]


def test_five_refused_text_answers_come_back_as_the_sentence_marked_as_a_refusal():
    """The screen draws a refusal and a technical failure as two different error cards (madde 425),
    so the box says which one it gave up on."""
    http = Answers([SORRY, REFUSAL] * 5 + [calling(LOOK)])

    answer = asking(http).converse(HISTORY, TOOLS)

    assert len(http.calls) == 10
    assert answer.failed is True and answer.refused is True
    assert answer.text == SENTENCE
    assert answer.tool_calls == []


def test_five_technical_failures_come_back_in_their_own_words_and_not_as_a_refusal():
    busy = [FakeResponse(status_code=503, text=f"meşgul {n}") for n in range(1, 6)]
    http = Answers(busy + [calling(LOOK)])

    answer = asking(http).converse(HISTORY, TOOLS)

    assert len(http.calls) == 5
    assert answer.failed is True and answer.refused is False
    assert answer.text == "DeepSeek HTTP 503\nmeşgul 5"
    assert answer.tool_calls == []


def test_a_last_try_that_failed_on_the_wire_is_not_a_refusal_after_refusals():
    lost = requests.ConnectionError("Max retries exceeded with url: /chat/completions")
    http = Answers([SORRY, REFUSAL] * 4 + [lost, calling(LOOK)])

    answer = asking(http).converse(HISTORY, TOOLS)

    assert len(http.calls) == 9
    assert answer.failed is True and answer.refused is False
    assert answer.text == str(lost)


def test_without_a_key_nothing_is_sent_and_the_failure_is_technical():
    http = Answers([calling(LOOK)])

    answer = asking(http, api_key="").converse(HISTORY, TOOLS)

    assert http.calls == []
    assert answer.failed is True and answer.refused is False
    assert "DEEPSEEK_API_KEY" in answer.text


@pytest.mark.parametrize("answers, refused", [
    ([SORRY, REFUSAL] * 5, True),
    ([FakeResponse(status_code=503, text="meşgul")] * 5, False),
], ids=["refusal", "technical"])
def test_a_prompt_s_failure_says_whether_it_was_a_refusal_too(answers, refused):
    answer = asking(Answers(answers)).ask("talimat", "", [PHOTO])

    assert answer.failed is True
    assert answer.refused is refused
