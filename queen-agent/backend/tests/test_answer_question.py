"""Answering a running turn's question (Madde 463): an Allow puts the chat in Edit -- the server's rule,
in one place -- and does so before the turn wakes, so the turn's next call reads Edit."""
from backend.features.workspace.domain.usecases.answer_question import answer_question


class Live:
    """A turn asking question 3, noting what is done to it in the order it is done."""

    def __init__(self, said):
        self.said = said

    def asks(self, turn_id, wait):
        return (turn_id, wait) == ("t1", 3)

    def decide(self, turn_id, wait, allowed, reason):
        self.said.append(("decide", turn_id, wait, allowed, reason))


class Turns:
    def __init__(self, live=None):
        self.live = live

    def get(self, project_id, chat_id):
        return self.live


class Rows:
    def __init__(self, said):
        self.said = said

    def set_mode(self, project_id, chat_id, mode):
        self.said.append(("mode", project_id, chat_id, mode))
        return True


def _answered(turn_id, wait, allowed, reason=""):
    said = []
    live = Live(said)
    answered = answer_question(Turns(live), Rows(said), "p1", "c1", turn_id, wait, allowed, reason)
    assert answered is live
    return said


def test_an_allow_puts_the_chat_in_edit_before_the_turn_wakes():
    # The other order leaves a second call of the same round free to read Ask and ask again.
    assert _answered("t1", 3, True) == [("mode", "p1", "c1", "edit"), ("decide", "t1", 3, True, "")]


def test_a_refusal_leaves_the_mode_as_it_is():
    assert _answered("t1", 3, False, "not that") == [("decide", "t1", 3, False, "not that")]


def test_a_stale_allow_leaves_the_mode_as_it_is():
    # Another turn, or a question already answered: nothing was allowed, so nothing changes.
    for turn_id, wait in (("t-earlier", 3), ("t1", 2), (None, None)):
        assert _answered(turn_id, wait, True) == [("decide", turn_id, wait, True, "")]


def test_with_nothing_running_nothing_is_done():
    said = []
    assert answer_question(Turns(), Rows(said), "p1", "c1", "t1", 3, True, "") is None
    assert said == []
