"""The black box every request of the agent's loop goes through (Madde 440), and its check (Madde
445).

On fakes only, like every domain test: an engine's failure is whatever it raises, so plain
exceptions carrying the transport's kind of words stand in for it.
"""
import pytest

from backend.features.workspace.domain.black_box import (
    NOTHING,
    REFUSED,
    REFUSED_SAID,
    TECHNICAL,
    TRIES,
    Answer,
    ask,
)
from backend.features.workspace.domain.chat import Usage
from backend.features.workspace.domain.prompt import APPROVED, CHECK

ASKED = [{"role": "user", "content": "hi"}]
TOOLS = [{"type": "function", "function": {"name": "read_file"}}]
CALL = {"id": "t1", "function": {"name": "read_file", "arguments": "{}"}}


class Tries:
    """An engine whose every try is written out: a list of pieces, or an exception it raises.

    A try past the script answers nothing, so a black box that asked too often meets an empty answer
    rather than a crash -- and the count of what it was asked says the rest.

    The checks are written out the same way, one per check: the word it says, its pieces, or an
    exception. Past the script a check approves, so a test about tries reads like it did before
    there was a check.
    """

    def __init__(self, *tries, checks=()):
        self.tries = list(tries)
        self.checks = list(checks)
        self.asked = []
        self.checked = []

    def stream_alone(self, system, text, on_open=None):
        self.checked.append((system, text))
        if on_open:
            on_open(lambda: None)
        verdict = self.checks.pop(0) if self.checks else APPROVED
        if isinstance(verdict, Exception):
            raise verdict
        yield from [{"text": verdict}] if isinstance(verdict, str) else verdict

    def stream(self, messages, tools=None, on_open=None):
        self.asked.append((messages, tools))
        if on_open:
            on_open(lambda: None)
        script = self.tries.pop(0) if self.tries else []
        if isinstance(script, Exception):
            raise script
        for piece in script:
            if isinstance(piece, Exception):
                raise piece
            yield piece


def _asked(engine, stopped=lambda: False):
    return ask(engine, ASKED, TOOLS, on_open=None, stopped=stopped)


def test_a_good_answer_comes_back_whole_from_one_request():
    engine = Tries([{"text": "Hel"}, {"text": "lo"}, {"tool_calls": [CALL]}])
    answer = _asked(engine)
    assert answer == Answer(text="Hello", calls=(CALL,))
    assert len(engine.asked) == 1


def test_an_answer_in_words_is_checked_word_for_word_and_comes_back_approved():
    engine = Tries([{"text": "Hel"}, {"text": "lo "}])
    assert _asked(engine) == Answer(text="Hello ")
    # The answer as it came, nothing trimmed and nothing added, under the check's own instruction.
    assert engine.checked == [(CHECK, "Hello ")]
    assert len(engine.asked) == 1


def test_an_answer_that_calls_a_tool_passes_unchecked_with_its_words():
    # It asks for something rather than answers (v10-1b), and its words are what the agent says
    # while it asks.
    engine = Tries([{"text": "Reading it."}, {"tool_calls": [CALL]}])
    assert _asked(engine) == Answer(text="Reading it.", calls=(CALL,))
    assert engine.checked == []


def test_every_call_of_one_answer_comes_back_in_order():
    # Madde 455 asks for independent reads in one round, so one answer carries several calls --
    # whole in one piece, or in pieces of their own. All of them come back, in the order they came.
    second = {"id": "t2", "function": {"name": "read_file", "arguments": "{}"}}
    third = {"id": "t3", "function": {"name": "read_file", "arguments": "{}"}}
    engine = Tries([{"tool_calls": [CALL, second]}, {"tool_calls": [third]}])
    assert _asked(engine).calls == (CALL, second, third)


def test_a_refusal_sends_the_same_request_again():
    engine = Tries([{"text": "I cannot help with that."}], [{"text": "Done."}], checks=["REFUSAL"])
    assert _asked(engine).text == "Done."
    assert engine.asked == [(ASKED, TOOLS), (ASKED, TOOLS)]
    # The refusal never comes back: only the approved answer does.
    assert [text for _, text in engine.checked] == ["I cannot help with that.", "Done."]


def test_five_refusals_say_the_general_message_and_raise_nothing():
    engine = Tries(*[[{"text": "I cannot."}]] * (TRIES + 2), checks=["REFUSAL"] * (TRIES + 2))
    answer = _asked(engine)
    assert len(engine.asked) == TRIES
    assert answer == Answer(text=REFUSED_SAID, failed=REFUSED)
    # The design's sentence, word for word (items 216 and 221).
    assert REFUSED_SAID == "The model returned an error. Try asking another way."
    assert REFUSED == "refused"


@pytest.mark.parametrize("said", ["REFUSAL", "", "approved", "APPROVED. Nothing is refused here."])
def test_only_the_one_word_approves(said):
    # A check that did not write the word approved nothing -- an empty one and a talkative one too.
    engine = Tries([{"text": "First."}], [{"text": "Second."}], checks=[said])
    assert _asked(engine).text == "Second."
    assert len(engine.asked) == 2


def test_the_word_with_blanks_around_it_still_approves():
    engine = Tries([{"text": "Done."}], checks=[" APPROVED\n"])
    assert _asked(engine).text == "Done."
    assert len(engine.asked) == 1


def test_a_check_that_fails_is_a_failed_try():
    engine = Tries([{"text": "First."}], [{"text": "Second."}], checks=[RuntimeError("HTTP 502")])
    assert _asked(engine).text == "Second."
    assert len(engine.asked) == 2


def test_five_failed_checks_end_in_the_last_ones_own_words():
    engine = Tries(
        *[[{"text": "Done."}]] * TRIES,
        checks=[RuntimeError(f"HTTP 50{n}") for n in range(TRIES)],
    )
    assert _asked(engine) == Answer(text="HTTP 504", failed=TECHNICAL)


def test_refusals_then_an_error_end_as_the_error():
    # The last try decides (v10-1b): its kind and its words, not the most common of the five.
    engine = Tries(
        *[[{"text": "I cannot."}]] * (TRIES - 1),
        RuntimeError("HTTP 502"),
        checks=["REFUSAL"] * (TRIES - 1),
    )
    assert _asked(engine) == Answer(text="HTTP 502", failed=TECHNICAL)


def test_errors_then_a_refusal_end_as_the_refusal():
    engine = Tries(
        *[RuntimeError("HTTP 502")] * (TRIES - 1),
        [{"text": "I cannot."}],
        checks=["REFUSAL"],
    )
    assert _asked(engine) == Answer(text=REFUSED_SAID, failed=REFUSED)


def test_a_stop_that_cuts_the_check_is_not_tried_again():
    # The check is a request like any other: a stop cuts it, and nothing goes after it.
    engine = Tries([{"text": "Done."}], [{"text": "never"}], checks=[RuntimeError("cut")])
    assert _asked(engine, stopped=lambda: True) == Answer()
    assert len(engine.asked) == 1


def test_a_refusal_landing_with_a_stop_is_not_tried_again():
    engine = Tries([{"text": "I cannot."}], [{"text": "never"}], checks=["REFUSAL"])
    assert _asked(engine, stopped=lambda: True) == Answer()
    assert len(engine.asked) == 1


def test_the_way_to_cut_the_check_is_handed_on_too():
    handed = []
    ask(Tries([{"text": "Done."}]), ASKED, TOOLS, on_open=handed.append, stopped=lambda: False)
    # One for the request, one for its check.
    assert len(handed) == 2


def test_what_the_answer_spent_is_its_own_request_not_the_check():
    engine = Tries(
        [{"text": "Done."}, {"usage": {"sent": 12, "cached": 9, "answered": 3}}],
        checks=[[{"text": APPROVED}, {"usage": {"sent": 50, "cached": 0, "answered": 1}}]],
    )
    assert _asked(engine).usage == Usage(12, 9, 3)


def test_after_an_error_the_same_request_goes_again():
    engine = Tries(RuntimeError("HTTP 502"), [{"text": "Done."}])
    answer = _asked(engine)
    assert answer.text == "Done."
    assert not answer.failed
    # The same conversation and the same tools, not a rebuilt request.
    assert engine.asked == [(ASKED, TOOLS), (ASKED, TOOLS)]


def test_a_stream_that_breaks_half_way_is_tried_again():
    engine = Tries(
        [{"text": "Half"}, RuntimeError("IncompleteRead(0 bytes read)")], [{"text": "Whole."}]
    )
    assert _asked(engine).text == "Whole."
    assert len(engine.asked) == 2


def test_an_empty_answer_is_tried_again():
    engine = Tries([], [{"text": "Done."}])
    assert _asked(engine).text == "Done."
    assert len(engine.asked) == 2


def test_an_answer_of_blanks_is_empty_too():
    engine = Tries([{"text": "  \n "}], [{"text": "Done."}])
    assert _asked(engine).text == "Done."
    assert len(engine.asked) == 2


def test_silence_the_caller_counts_as_an_answer_is_not_tried_again():
    # The loop says so once its turn has made a file (Madde 38): saying nothing then is finished.
    engine = Tries([], [{"text": "never"}])
    answer = ask(engine, ASKED, TOOLS, on_open=None, stopped=lambda: False, silence_is_an_answer=True)
    assert answer == Answer()
    assert len(engine.asked) == 1
    # No words, nothing to check.
    assert engine.checked == []


def test_a_tool_call_without_words_is_an_answer():
    engine = Tries([{"tool_calls": [CALL]}])
    assert _asked(engine).calls == (CALL,)
    assert len(engine.asked) == 1


def test_five_failures_are_five_requests_and_no_exception():
    engine = Tries(*[RuntimeError(f"HTTP 50{n}") for n in range(TRIES + 2)])
    answer = _asked(engine)
    assert TRIES == 5
    assert len(engine.asked) == TRIES
    # The last error's own words, nothing added to them.
    assert answer == Answer(text="HTTP 504", failed=TECHNICAL)


def test_five_empty_answers_say_the_model_returned_nothing():
    answer = _asked(Tries())
    assert answer == Answer(text=NOTHING, failed=TECHNICAL)
    assert NOTHING == "The model returned nothing."


def test_a_failure_before_anything_is_sent_is_tried_like_any_other():
    # A missing key is refused before a byte leaves, so its five tries cost nothing, and one rule is
    # simpler than a list of which failures count.
    engine = Tries(*[RuntimeError("No API key is set.") for _ in range(TRIES)])
    answer = _asked(engine)
    assert len(engine.asked) == TRIES
    assert answer.text == "No API key is set."


def test_a_stop_is_not_tried_again():
    # The empty answer is all the black box says: the loop reads the stop off the registry.
    engine = Tries([{"text": "Half"}, RuntimeError("cut")], [{"text": "never"}])
    assert _asked(engine, stopped=lambda: True) == Answer()
    assert len(engine.asked) == 1


def test_an_empty_answer_landing_with_a_stop_is_not_tried_again():
    engine = Tries([], [{"text": "never"}])
    assert _asked(engine, stopped=lambda: True) == Answer()
    assert len(engine.asked) == 1


def test_a_whole_answer_is_returned_even_if_a_stop_landed_meanwhile():
    # Whether it is kept is the loop's call: the black box only refuses to send another request.
    engine = Tries([{"text": "Done."}])
    assert _asked(engine, stopped=lambda: True).text == "Done."


def test_the_way_to_cut_each_try_is_handed_on():
    handed = []
    # A call, so that no check hands on a third.
    engine = Tries(RuntimeError("HTTP 502"), [{"tool_calls": [CALL]}])
    ask(engine, ASKED, TOOLS, on_open=handed.append, stopped=lambda: False)
    assert len(handed) == 2


def test_what_the_answer_spent_is_its_last_reading():
    engine = Tries(
        [
            {"usage": {"sent": 10, "cached": 1, "answered": 1}},
            {"text": "Done."},
            {"usage": {"sent": 12, "cached": 9, "answered": 3}},
        ]
    )
    assert _asked(engine).usage == Usage(12, 9, 3)


def test_an_answer_nobody_measured_carries_no_usage():
    assert _asked(Tries([{"text": "Done."}])).usage is None
