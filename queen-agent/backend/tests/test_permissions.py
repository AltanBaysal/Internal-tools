"""The registry a paused turn reads its answer from.

Its sibling is MemoryStops and the shape is deliberately the same: held in memory, keyed by chat,
reached by two threads at once. The waits here are measured in hundredths of a second -- the tick
is the caller's, and only the app passes fifteen.
"""
import threading
import time

TICK = 0.01


def _registry():
    from backend.features.workspace.data.memory_permissions import MemoryPermissions

    return MemoryPermissions()


def test_an_answer_left_before_the_question_is_picked_up_at_once():
    # The race hold() exists for, on this side of the app: which of the two comes first is nobody's
    # to arrange, and a decision that landed early must not be lost.
    permissions = _registry()
    permissions.answer("p1", "c1", True, "")
    assert permissions.wait("p1", "c1", TICK).allowed


def test_waiting_with_no_answer_comes_back_with_nothing():
    permissions = _registry()
    assert permissions.wait("p1", "c1", TICK) is None


def test_an_answer_wakes_whoever_is_waiting():
    # Read off the clock rather than the value: what is claimed is that the wait ended when the
    # answer arrived, not that it ran out of tick.
    permissions = _registry()
    threading.Timer(TICK, lambda: permissions.answer("p1", "c1", True, "")).start()
    began = time.monotonic()
    decision = permissions.wait("p1", "c1", 5)
    assert decision.allowed
    assert time.monotonic() - began < 1


def test_a_wake_ends_the_wait_without_a_decision():
    # How a stop gets out. There is no socket to cut while a turn waits here -- the xAI request
    # closed before the tool call was ever read -- so the wait itself is what a stop has to reach.
    permissions = _registry()
    threading.Timer(TICK, lambda: permissions.wake("p1", "c1")).start()
    assert permissions.wait("p1", "c1", 5) is None


def test_one_chat_is_answered_without_answering_its_neighbour():
    permissions = _registry()
    permissions.answer("p1", "c1", True, "")
    assert permissions.wait("p1", "c2", TICK) is None


def test_the_reason_travels_with_a_refusal():
    permissions = _registry()
    permissions.answer("p1", "c1", False, "that file is mine")
    decision = permissions.wait("p1", "c1", TICK)
    assert (decision.allowed, decision.reason) == (False, "that file is mine")


def test_an_answer_is_spent_once():
    # A turn may ask twice, and the second question is a question -- not something the first answer
    # already settled. This is also why there is no separate "open a question" call: the answer
    # being consumed is what keeps the two apart.
    permissions = _registry()
    permissions.answer("p1", "c1", True, "")
    permissions.wait("p1", "c1", TICK)
    assert permissions.wait("p1", "c1", TICK) is None


def test_clearing_forgets_the_answer():
    # Every turn clears on its way out. Left standing, an answer would settle the next turn's
    # question before anybody was asked.
    permissions = _registry()
    permissions.answer("p1", "c1", True, "")
    permissions.clear("p1", "c1")
    assert permissions.wait("p1", "c1", TICK) is None
