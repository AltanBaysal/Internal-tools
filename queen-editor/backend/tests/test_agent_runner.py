"""Which chats' agents are working, and what a run may still write (madde 420).

The agent runs on the server: it goes on when the panel closes or the page reloads, two chats may
run at once, a working chat takes no second question, and a stop lands at once -- whatever the run
writes after it lands nowhere.

Tried with a fake record and with the work held back: `spawn` puts the work in a list and the test
runs it when it wants -- the moment a request would be out -- so nothing waits on a real thread.

The new module is imported inside the tests: it is written after this file, and an import at the top
would stop the whole collection instead of failing these questions.
"""
import pytest

ASKED = "2026-10-06T10:00:00+00:00"
READING = ("2 numaralı kareyi okuyor…", "2 numaralı kareyi okudu")
REFUSED = "Model hata döndü, farklı şekilde dene."


class FakeRecord:
    """Writes down every line, as (what, project, chat, *the rest)."""

    def __init__(self):
        self.lines = []

    def add_question(self, project, chat_id, text, at):
        self.lines.append(("question", project, chat_id, text, at))

    def add_step(self, project, chat_id, running, done):
        self.lines.append(("step", project, chat_id, running, done))

    def finish_step(self, project, chat_id):
        self.lines.append(("stepDone", project, chat_id))

    def answer(self, project, chat_id, text):
        self.lines.append(("answer", project, chat_id, text))

    def fail(self, project, chat_id, text):
        self.lines.append(("failure", project, chat_id, text))

    def stop(self, project, chat_id):
        self.lines.append(("stopped", project, chat_id))


@pytest.fixture
def record():
    return FakeRecord()


@pytest.fixture
def held():
    """The work started and not yet run."""
    return []


@pytest.fixture
def runner(record, held):
    from backend.features.agent.runner import AgentRunner
    return AgentRunner(record, spawn=held.append)


def working(runner, project):
    """The ids of the project's chats whose agent works, as the screen reads them."""
    return runner.now(project)["working"]


def asking(runner, project):
    """The changes the project's agents wait on, as the screen reads them (madde 480)."""
    return runner.now(project)["asking"]


def answers(text):
    """Work that reads a frame and answers."""
    def work(run):
        run.add_step(*READING)
        run.answer(text)
    return work


def test_starting_writes_the_question_and_the_chat_is_working(runner, record, held):
    assert runner.start("düğün", 1, "Kaç kare var?", ASKED, answers("3 kare.")) is True

    assert record.lines == [("question", "düğün", 1, "Kaç kare var?", ASKED)]
    assert working(runner, "düğün") == [1]
    assert len(held) == 1


def test_a_working_chat_takes_no_second_question(runner, record, held):
    runner.start("düğün", 1, "Kaç kare var?", ASKED, answers("3 kare."))

    assert runner.start("düğün", 1, "Peki 7?", ASKED, answers("7 hazır.")) is False

    assert record.lines == [("question", "düğün", 1, "Kaç kare var?", ASKED)]
    assert len(held) == 1


def test_two_chats_work_at_once_in_one_project_or_two(runner, held):
    for project, chat in (("düğün", 2), ("düğün", 1), ("kına", 1)):
        assert runner.start(project, chat, "Kaç kare var?", ASKED, answers("3 kare.")) is True

    assert working(runner, "düğün") == [1, 2]
    assert working(runner, "kına") == [1]
    assert len(held) == 3


@pytest.mark.parametrize("end, line", [
    (lambda run: run.answer("3 kare."), ("answer", "düğün", 1, "3 kare.")),
    (lambda run: run.fail(REFUSED), ("failure", "düğün", 1, REFUSED)),
], ids=["answer", "failure"])
def test_an_answer_or_a_failure_ends_the_work(runner, record, held, end, line):
    def work(run):
        run.add_step(*READING)
        run.finish_step()
        end(run)

    runner.start("düğün", 1, "Kaç kare var?", ASKED, work)
    held.pop()()

    assert record.lines[1:] == [("step", "düğün", 1, *READING), ("stepDone", "düğün", 1), line]
    assert working(runner, "düğün") == []


def test_work_that_raises_fails_in_its_own_words(runner, record, held):
    """A disk that went away, a project deleted under the agent: the error's own words, never a
    guessed cause."""
    def work(run):
        raise OSError("[Errno 107] Transport endpoint is not connected")

    runner.start("düğün", 1, "Kaç kare var?", ASKED, work)
    held.pop()()

    assert record.lines[-1] == ("failure", "düğün", 1,
                                "[Errno 107] Transport endpoint is not connected")
    assert working(runner, "düğün") == []


def test_a_stop_is_written_at_once_and_nothing_after_it_lands(runner, record, held):
    """The request out when the stop is pressed cannot be cut -- the box waits on it -- so what it
    brings back is dropped: no half an answer is ever written (BEHAVIOUR.md, Agent panel)."""
    seen = []

    def work(run):
        seen.append(run.stopped())
        run.add_step(*READING)
        run.answer("Yarım kalan cevap.")

    runner.start("düğün", 1, "Kaç kare var?", ASKED, work)
    runner.stop("düğün", 1)

    assert record.lines[-1] == ("stopped", "düğün", 1)
    assert working(runner, "düğün") == []

    held.pop()()

    assert seen == [True]
    assert record.lines == [("question", "düğün", 1, "Kaç kare var?", ASKED),
                            ("stopped", "düğün", 1)]


@pytest.mark.parametrize("answered", [False, True], ids=["never-asked", "already-answered"])
def test_stopping_a_chat_that_is_not_working_writes_nothing(runner, record, held, answered):
    """A ■ that lands as the answer arrives must not turn the answer into "Durduruldu"."""
    if answered:
        runner.start("düğün", 1, "Kaç kare var?", ASKED, answers("3 kare."))
        held.pop()()
    before = list(record.lines)

    runner.stop("düğün", 1)

    assert record.lines == before


def test_a_stopped_chat_takes_a_new_question_and_the_old_work_writes_nothing(runner, record, held):
    runner.start("düğün", 1, "Kaç kare var?", ASKED, answers("Eski cevap."))
    runner.stop("düğün", 1)

    assert runner.start("düğün", 1, "Peki 7?", ASKED, answers("7 hazır.")) is True

    old, new = held
    old()
    assert working(runner, "düğün") == [1]
    new()
    assert record.lines == [("question", "düğün", 1, "Kaç kare var?", ASKED),
                            ("stopped", "düğün", 1),
                            ("question", "düğün", 1, "Peki 7?", ASKED),
                            ("step", "düğün", 1, *READING),
                            ("answer", "düğün", 1, "7 hazır.")]
    assert working(runner, "düğün") == []


# --- the permission gate (madde 480) -------------------------------------------------------------
#
# A run that would change something waits for the user's answer. The wait is a real one, so these
# tests run the work on a thread of its own and look for the question the way the screen does --
# through `asking` -- for at most a few seconds; it is there in a moment.

CHANGE = {"title": "2 numaralı kare düzeltilecek",
          "details": [{"label": "Fotoğraf", "text": "Eski fotoğraf silinecek."}]}
# The largest whole number a JavaScript number holds exactly: the page reads a change's number as one.
EXACT_IN_JAVASCRIPT = 2 ** 53 - 1


@pytest.fixture
def asks(runner, held):
    """Starts a run in a chat that asks about CHANGE, on its own thread -- düğün's chat 1 unless
    named. Hands back (what permit() said -- filled once it returns, the thread)."""
    import threading

    def start(chat=1, project="düğün"):
        said = []
        runner.start(project, chat, "Düzelt", ASKED, lambda run: said.append(run.permit(CHANGE)))
        thread = threading.Thread(target=held.pop(), daemon=True)
        thread.start()
        return said, thread

    return start


def asked_id(runner, until, chat=1, project="düğün"):
    return until(lambda: [one["id"] for one in asking(runner, project) if one["chat"] == chat])[0]


@pytest.mark.parametrize("allow", [True, False], ids=["allowed", "rejected"])
def test_a_run_waits_for_the_answer_and_gets_it(runner, asks, until, ended, allow):
    said, thread = asks()

    number = asked_id(runner, until)
    assert runner.now("düğün") == {"working": [1],
                                   "asking": [{"chat": 1, "id": number, "change": CHANGE}]}
    assert said == []

    assert runner.reply("düğün", 1, number, allow) is True
    ended(thread)

    assert said == [allow]
    assert asking(runner, "düğün") == []


def test_an_answer_to_another_question_wakes_nothing(runner, asks, until, ended):
    """A second press, or a page that had not yet seen the next change, must not allow a change
    nobody saw."""
    said, thread = asks()
    number = asked_id(runner, until)

    assert runner.reply("düğün", 1, number + 1, True) is False
    assert runner.reply("düğün", 2, number, True) is False
    assert runner.reply("kına", 1, number, True) is False
    assert said == []
    assert asking(runner, "düğün")[0]["id"] == number

    assert runner.reply("düğün", 1, number, False) is True
    ended(thread)
    assert runner.reply("düğün", 1, number, True) is False
    assert said == [False]


def test_an_answer_with_nothing_asked_is_refused(runner, held):
    assert runner.reply("düğün", 1, 1, True) is False
    runner.start("düğün", 1, "Kaç kare var?", ASKED, answers("3 kare."))
    assert runner.reply("düğün", 1, 1, True) is False


def test_a_stop_while_asked_is_a_rejection_and_ends_the_run(runner, record, asks, until, ended):
    said, thread = asks()
    asked_id(runner, until)

    runner.stop("düğün", 1)
    ended(thread)

    assert said == [False]
    assert runner.now("düğün") == {"working": [], "asking": []}
    assert record.lines[-1] == ("stopped", "düğün", 1)


def test_a_run_already_stopped_asks_nothing(runner, record, held):
    said = []
    runner.start("düğün", 1, "Düzelt", ASKED, lambda run: said.append(run.permit(CHANGE)))
    runner.stop("düğün", 1)

    held.pop()()

    assert said == [False]
    assert asking(runner, "düğün") == []


def test_each_question_has_its_own_number_and_only_the_project_s_chats_are_listed(runner, asks,
                                                                                    until, ended):
    _said, first = asks(chat=1)
    _said, second = asks(chat=2)
    _said, third = asks(chat=1, project="kına")
    one, two = asked_id(runner, until, 1), asked_id(runner, until, 2)
    three = asked_id(runner, until, 1, "kına")

    assert len({one, two, three}) == 3
    assert [asked["chat"] for asked in asking(runner, "düğün")] == [1, 2]
    assert [asked["chat"] for asked in asking(runner, "kına")] == [1]

    for project, chat, number in (("düğün", 1, one), ("düğün", 2, two), ("kına", 1, three)):
        assert runner.reply(project, chat, number, False) is True
    for thread in (first, second, third):
        ended(thread)


@pytest.fixture
def paused(record, held):
    """A runner that tells the idle watch when its run waits on the user (madde 498): what was
    told, in order, and the runner."""
    from contextlib import contextmanager

    from backend.features.agent.runner import AgentRunner
    told = []

    @contextmanager
    def waiting():
        told.append("waits")
        try:
            yield
        finally:
            told.append("goes on")

    return told, AgentRunner(record, spawn=held.append, waiting=waiting)


@pytest.mark.parametrize("answer", ["reply", "stop"])
def test_a_run_waiting_on_the_user_is_paused_for_the_idle_watch(paused, held, until, ended,
                                                                 answer):
    """An agent waiting on İzin ver / Reddet is not work: the watch hears it pause for exactly as
    long as the question stands, and go on once it is answered -- or stopped."""
    import threading

    told, runner = paused
    runner.start("düğün", 1, "Düzelt", ASKED, lambda run: run.permit(CHANGE))
    thread = threading.Thread(target=held.pop(), daemon=True)
    thread.start()
    number = asked_id(runner, until)
    assert told == ["waits"]

    if answer == "reply":
        runner.reply("düğün", 1, number, True)
    else:
        runner.stop("düğün", 1)
    ended(thread)

    assert told == ["waits", "goes on"]


def test_a_change_s_number_is_one_the_page_reads_exactly(runner, asks, until, ended):
    """The page reads the number as a JavaScript number and sends it back: rounded, it would never
    match, and no change could be answered."""
    _said, thread = asks()

    assert 0 < asked_id(runner, until) <= EXACT_IN_JAVASCRIPT

    runner.stop("düğün", 1)
    ended(thread)
