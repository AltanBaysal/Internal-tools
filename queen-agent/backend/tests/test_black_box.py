"""The black box every request of the agent's loop goes through (Madde 440).

On fakes only, like every domain test: an engine's failure is whatever it raises, so plain
exceptions carrying the transport's kind of words stand in for it.
"""
from backend.features.workspace.domain.black_box import NOTHING, TECHNICAL, TRIES, Answer, ask
from backend.features.workspace.domain.chat import Usage

ASKED = [{"role": "user", "content": "hi"}]
TOOLS = [{"type": "function", "function": {"name": "read_file"}}]
CALL = {"id": "t1", "function": {"name": "read_file", "arguments": "{}"}}


class Tries:
    """An engine whose every try is written out: a list of pieces, or an exception it raises.

    A try past the script answers nothing, so a black box that asked too often meets an empty answer
    rather than a crash -- and the count of what it was asked says the rest.
    """

    def __init__(self, *tries):
        self.tries = list(tries)
        self.asked = []

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
    engine = Tries(RuntimeError("HTTP 502"), [{"text": "Done."}])
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
