"""What the live turns promise (Madde 461). Nothing here touches the disk: a turn lives in memory."""
import threading

from backend.features.workspace.data.live_turns import LiveTurns
from backend.features.workspace.domain.chat import Chat, Message, ToolCall
from backend.features.workspace.domain.errors import EngineFailed
from backend.features.workspace.domain.permission import Decision, PermissionWanted
from backend.features.workspace.domain.turn import Progress

AT = "2026-10-10T10:00:00.000+00:00"
CHAT = Chat(id="c1", title="hi", created_at=AT, messages=(Message(role="user", at=AT, text="hi"),))


def _asked(turn):
    """The turn, paused on a question: what the runner does when the loop yields one."""
    turn.apply(PermissionWanted("create_file", "{}"))
    return turn.snapshot().permission.wait


def _ended(turn):
    """Wait for the turn's end the way a listener does, and hand back its last snapshot."""
    seen = turn.snapshot()
    while not seen.ended:
        seen = turn.changed_since(seen.version, 5)
    return seen


# --- one turn in a chat ----------------------------------------------------------------------------


def test_a_free_chat_can_be_taken_and_the_turn_has_an_id():
    turn = LiveTurns().reserve("p1", "c1")
    assert turn is not None and turn.id


def test_a_chat_with_a_turn_cannot_be_taken_again():
    turns = LiveTurns()
    turns.reserve("p1", "c1")
    assert turns.reserve("p1", "c1") is None


def test_one_chat_running_does_not_hold_its_neighbour():
    turns = LiveTurns()
    turns.reserve("p1", "c1")
    assert turns.reserve("p1", "c2") is not None
    assert turns.reserve("p2", "c1") is not None


def test_of_requests_arriving_together_exactly_one_wins():
    # Item 458's test, kept: two presses landing at once are two threads, and the lock is what leaves
    # all but one of them refused.
    turns = LiveTurns()
    start = threading.Barrier(8)
    won = []

    def press():
        start.wait()
        won.append(turns.reserve("p1", "c1") is not None)

    threads = [threading.Thread(target=press) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert sorted(won) == [False] * 7 + [True]


def test_a_released_chat_can_be_taken_again_and_each_turn_is_its_own():
    turns = LiveTurns()
    first = turns.reserve("p1", "c1")
    turns.release("p1", "c1", first)
    assert turns.get("p1", "c1") is None
    second = turns.reserve("p1", "c1")
    assert second is not None and second.id != first.id


def test_a_late_release_does_not_let_go_of_the_next_turn():
    turns = LiveTurns()
    first = turns.reserve("p1", "c1")
    turns.release("p1", "c1", first)
    second = turns.reserve("p1", "c1")
    turns.release("p1", "c1", first)
    assert turns.get("p1", "c1") is second


def test_a_project_knows_whether_any_of_its_chats_is_answering():
    turns = LiveTurns()
    turns.reserve("p1", "c1")
    assert turns.any_in("p1") is True
    assert turns.any_in("p2") is False


# --- the stop, bound to its turn -------------------------------------------------------------------


def test_a_stop_for_this_turn_cuts_its_request():
    turn = LiveTurns().reserve("p1", "c1")
    cut = []
    turn.hold(lambda: cut.append("cut"))
    turn.stop(turn.id)
    assert turn.stopped() and cut == ["cut"]


def test_a_stop_before_the_request_opens_cuts_it_as_it_opens():
    # A model that thinks for minutes before its first word is the very case this is for.
    turn = LiveTurns().reserve("p1", "c1")
    turn.stop(turn.id)
    cut = []
    turn.hold(lambda: cut.append("cut"))
    assert cut == ["cut"]


def test_a_stop_naming_another_turn_does_nothing():
    # A late press: it was meant for the turn before this one.
    turn = LiveTurns().reserve("p1", "c1")
    cut = []
    turn.hold(lambda: cut.append("cut"))
    turn.stop("t-earlier")
    assert not turn.stopped() and cut == []


def test_a_new_turn_starts_unstopped_whatever_the_last_one_heard():
    turns = LiveTurns()
    first = turns.reserve("p1", "c1")
    first.stop(first.id)
    turns.release("p1", "c1", first)
    assert not turns.reserve("p1", "c1").stopped()


# --- the question, bound to its turn and to itself -------------------------------------------------


def test_the_answer_to_the_question_standing_is_what_the_wait_returns():
    turn = LiveTurns().reserve("p1", "c1")
    wait = _asked(turn)
    turn.decide(turn.id, wait, False, "not that one")
    assert turn.decision() == Decision(False, "not that one")
    # Answered, the card goes.
    assert turn.snapshot().permission is None


def test_an_answer_left_before_the_question_is_not_kept():
    # Kept, it would let the next write through without anybody being asked.
    turn = LiveTurns().reserve("p1", "c1")
    turn.decide(turn.id, 1, True, "")
    wait = _asked(turn)
    assert turn.snapshot().permission.wait == wait
    turn.stop(turn.id)
    assert turn.decision() is None


def test_an_answer_to_another_question_or_another_turn_does_nothing():
    turn = LiveTurns().reserve("p1", "c1")
    wait = _asked(turn)
    turn.decide(turn.id, wait - 1, True, "")
    turn.decide("t-earlier", wait, True, "")
    assert turn.snapshot().permission.wait == wait
    turn.decide(turn.id, wait, True, "")
    assert turn.decision() == Decision(True, "")


def test_a_wait_with_nobody_answering_waits_until_it_is_answered():
    # No tick, no limit (the user: "sonsuza kadar beklesin"): only an answer or a stop ends it.
    turn = LiveTurns().reserve("p1", "c1")
    wait = _asked(turn)
    got = []
    waiting = threading.Thread(target=lambda: got.append(turn.decision()))
    waiting.start()
    waiting.join(0.2)
    assert waiting.is_alive()
    turn.decide(turn.id, wait, True, "")
    waiting.join(5)
    assert got == [Decision(True, "")]


def test_a_stop_ends_the_wait_without_a_decision_and_takes_the_card_down():
    turn = LiveTurns().reserve("p1", "c1")
    _asked(turn)
    got = []
    waiting = threading.Thread(target=lambda: got.append(turn.decision()))
    waiting.start()
    turn.stop(turn.id)
    waiting.join(5)
    assert got == [None]
    assert turn.snapshot().permission is None


# --- the runner ------------------------------------------------------------------------------------


def test_a_started_turn_runs_on_its_own_and_hands_its_record_over():
    turns = LiveTurns()
    turn = turns.reserve("p1", "c1")
    answered = Chat(id="c1", title="hi", created_at=AT, messages=CHAT.messages + (Message("ai", AT, "Done."),))

    def pieces():
        yield Progress(1, 32, 0)
        yield ToolCall("read_file", "a.md", "1 line")
        yield answered

    turns.start("p1", turn, CHAT, pieces())
    last = _ended(turn)
    assert (last.progress, last.calls, last.error) == (Progress(1, 32, 0), (ToolCall("read_file", "a.md", "1 line"),), "")
    assert turn.record() == answered


def test_the_record_is_handed_before_the_turn_runs():
    # A reload during the turn reads it here, off no disk.
    turns = LiveTurns()
    turn = turns.reserve("p1", "c1")
    gate = threading.Event()

    def pieces():
        gate.wait(5)
        yield Progress(1, 32, 0)

    turns.start("p1", turn, CHAT, pieces())
    assert turn.record() == CHAT
    gate.set()
    _ended(turn)


def test_a_turn_lets_go_of_its_chat_before_it_says_it_has_ended():
    # Whoever hears the end may send the next message at once, and has to find the chat free.
    turns = LiveTurns()
    turn = turns.reserve("p1", "c1")
    free_when_ended = []
    ending = turn.end

    def end(error):
        # Asked at the moment the end is said, not after: afterwards the order no longer shows.
        free_when_ended.append(turns.get("p1", "c1") is None)
        ending(error)

    turn.end = end
    turns.start("p1", turn, CHAT, iter([]))
    _ended(turn)
    assert free_when_ended == [True]


def test_a_turn_whose_own_code_breaks_ends_with_its_words_and_lets_go():
    turns = LiveTurns()
    turn = turns.reserve("p1", "c1")

    def pieces():
        yield Progress(1, 32, 0)
        raise EngineFailed("the disk went away")

    turns.start("p1", turn, CHAT, pieces())
    assert _ended(turn).error == "the disk went away"
    assert turns.get("p1", "c1") is None


def test_the_turn_runs_on_a_daemon_thread():
    # A turn waiting on a question nobody answers must not keep the process from stopping.
    turns = LiveTurns()
    turn = turns.reserve("p1", "c1")
    seen = []
    gate = threading.Event()

    def pieces():
        seen.append(threading.current_thread().daemon)
        gate.set()
        yield Progress(1, 32, 0)

    turns.start("p1", turn, CHAT, pieces())
    gate.wait(5)
    _ended(turn)
    assert seen == [True]


def test_a_listener_hears_nothing_new_when_nothing_moved():
    turn = LiveTurns().reserve("p1", "c1")
    assert turn.changed_since(turn.snapshot().version, 0.01).version == 0
