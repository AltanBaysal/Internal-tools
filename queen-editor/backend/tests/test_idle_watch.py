"""The idle watch: "orada mısın?" once nothing has worked for ten minutes (madde 498).

Work tells the watch when it starts and ends by running on the threads the watch spawns; the last
end opens a countdown, and any start cancels it. The countdown runs out into the question, which the
screen hears through one held ask.

Most of these move a fake clock and ask with no wait, so nothing sleeps. The few that need a real
wait -- a held ask woken by work, by Buradayım or by the countdown -- use the real clock and wait a
fraction of a second at most.
"""
import threading
import time

import pytest

WAIT = 600


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def watch(clock):
    from backend.features.idle.watch import IdleWatch
    return IdleWatch(wait=WAIT, clock=clock)


def look(watch):
    """What a screen hears asking with no version: at once, as it stands."""
    return watch.changed_since(None, 0)


class Held:
    """Work on one of the watch's threads, kept going until the test lets it end."""

    def __init__(self, watch, body=None):
        self.go_on = threading.Event()

        def work():
            if body:
                body()
            self.go_on.wait(5)

        self.thread = watch.spawn(work)

    def end(self):
        self.go_on.set()
        self.thread.join(5)
        assert not self.thread.is_alive()


# --- the countdown ------------------------------------------------------------------------------

def test_with_nothing_running_it_asks_ten_minutes_after_it_came_up(watch, clock):
    clock.now += WAIT - 1
    assert look(watch) == {"version": 0, "asking": False}

    clock.now += 1
    assert look(watch) == {"version": 1, "asking": True}


def test_it_asks_again_every_ten_minutes_while_nothing_runs(watch, clock):
    clock.now += WAIT
    assert look(watch)["version"] == 1

    clock.now += WAIT - 1
    assert look(watch)["version"] == 1
    clock.now += 1
    assert look(watch) == {"version": 2, "asking": True}


def test_buradayim_closes_the_question_and_starts_the_ten_minutes_again(watch, clock):
    clock.now += WAIT
    look(watch)
    clock.now += 100

    assert watch.here() == {"version": 2, "asking": False}

    clock.now += WAIT - 1
    assert look(watch) == {"version": 2, "asking": False}
    clock.now += 1
    assert look(watch) == {"version": 3, "asking": True}


def test_buradayim_while_work_runs_opens_no_countdown(watch, clock):
    """Every page open is a Buradayım: one opened while the queue runs must not start ten minutes
    that run out in the middle of the work."""
    held = Held(watch)

    watch.here()
    clock.now += 3 * WAIT
    assert look(watch)["asking"] is False

    held.end()
    clock.now += WAIT - 1
    assert look(watch)["asking"] is False
    clock.now += 1
    assert look(watch)["asking"] is True


def test_buradayim_with_nothing_asked_moves_nothing_but_the_countdown(watch, clock):
    clock.now += WAIT - 1

    assert watch.here() == {"version": 0, "asking": False}

    clock.now += 1
    assert look(watch)["asking"] is False


# --- work ---------------------------------------------------------------------------------------

def test_nothing_is_asked_while_work_runs_and_the_count_starts_when_it_ends(watch, clock):
    held = Held(watch)
    clock.now += 3 * WAIT
    assert look(watch) == {"version": 0, "asking": False}

    held.end()
    clock.now += WAIT - 1
    assert look(watch)["asking"] is False
    clock.now += 1
    assert look(watch)["asking"] is True


@pytest.mark.filterwarnings("ignore::pytest.PytestUnhandledThreadExceptionWarning")
def test_work_that_raises_still_ends(watch, clock):
    """The runners catch their work's failures themselves; the watch does not count on it."""
    def work():
        raise RuntimeError("ComfyUI öldü")

    watch.spawn(work).join(5)

    clock.now += WAIT
    assert look(watch)["asking"] is True


def test_the_count_starts_when_the_last_of_two_works_ends(watch, clock):
    first, second = Held(watch), Held(watch)

    first.end()
    clock.now += WAIT
    assert look(watch)["asking"] is False

    second.end()
    clock.now += WAIT
    assert look(watch)["asking"] is True


def test_work_that_starts_closes_the_question(watch, clock):
    clock.now += WAIT
    assert look(watch)["version"] == 1

    held = Held(watch)

    assert look(watch) == {"version": 2, "asking": False}
    held.end()


def test_work_waiting_on_the_user_is_not_work(watch, clock):
    """An agent waiting on İzin ver / Reddet waits on the user: counted as work, it would keep the
    question away for as long as nobody is there to answer."""
    asked, answered = threading.Event(), threading.Event()

    def ask_the_user():
        with watch.waiting():
            asked.set()
            answered.wait(5)

    held = Held(watch, ask_the_user)
    assert asked.wait(5)
    clock.now += WAIT
    assert look(watch)["asking"] is True

    # The answer came: the agent goes on, and that is work again -- the question it had closes.
    said, thread = held_ask(watch, look(watch)["version"])
    answered.set()
    thread.join(5)
    assert said[0]["asking"] is False
    held.end()


def test_waiting_off_the_watchs_threads_changes_nothing(watch, clock):
    """A test that runs a runner's work inline has no watched thread to pause."""
    with watch.waiting():
        clock.now += WAIT
    assert look(watch)["asking"] is True


# --- the held ask --------------------------------------------------------------------------------

def test_an_ask_for_the_version_it_has_waits_out_its_limit_and_answers_as_it_stands(watch):
    started = time.monotonic()

    said = watch.changed_since(0, 0.2)

    assert said == {"version": 0, "asking": False}
    assert time.monotonic() - started >= 0.2


def test_an_ask_for_an_old_version_is_answered_at_once(watch, clock):
    clock.now += WAIT
    look(watch)

    assert watch.changed_since(0, 30) == {"version": 1, "asking": True}


@pytest.fixture
def real_watch():
    """The real clock, and a countdown of a fraction of a second."""
    from backend.features.idle.watch import IdleWatch
    return IdleWatch(wait=0.2)


def held_ask(watch, version):
    said = []
    thread = threading.Thread(target=lambda: said.append(watch.changed_since(version, 5)),
                              daemon=True)
    thread.start()
    return said, thread


def test_a_held_ask_hears_the_countdown_run_out(real_watch):
    started = time.monotonic()
    said, thread = held_ask(real_watch, 0)

    thread.join(5)

    assert said == [{"version": 1, "asking": True}]
    assert time.monotonic() - started < 2


def asked(watch):
    """Wait out the fraction-of-a-second countdown: the question stands."""
    said, thread = held_ask(watch, 0)
    thread.join(5)
    assert said[0] == {"version": 1, "asking": True}


def test_a_held_ask_hears_buradayim_at_once(real_watch):
    asked(real_watch)
    said, thread = held_ask(real_watch, 1)

    real_watch.here()
    thread.join(1)

    assert said == [{"version": 2, "asking": False}]


def test_a_held_ask_hears_work_start_at_once(real_watch):
    asked(real_watch)
    said, thread = held_ask(real_watch, 1)

    held = Held(real_watch)
    thread.join(1)

    assert said == [{"version": 2, "asking": False}]
    held.end()


def test_a_held_ask_waits_for_the_countdown_work_opened_on_ending(real_watch):
    """The ask fell asleep with work running and no countdown at all; the end opens one, and the
    ask must wake to it rather than sleep out its whole limit."""
    held = Held(real_watch)
    started = time.monotonic()
    said, thread = held_ask(real_watch, 0)

    held.end()
    thread.join(5)

    assert said == [{"version": 1, "asking": True}]
    assert time.monotonic() - started < 2
