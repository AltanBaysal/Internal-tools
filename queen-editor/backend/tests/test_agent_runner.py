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


def answers(text):
    """Work that reads a frame and answers."""
    def work(run):
        run.add_step(*READING)
        run.answer(text)
    return work


def test_starting_writes_the_question_and_the_chat_is_working(runner, record, held):
    assert runner.start("düğün", 1, "Kaç kare var?", ASKED, answers("3 kare.")) is True

    assert record.lines == [("question", "düğün", 1, "Kaç kare var?", ASKED)]
    assert runner.working("düğün") == [1]
    assert len(held) == 1


def test_a_working_chat_takes_no_second_question(runner, record, held):
    runner.start("düğün", 1, "Kaç kare var?", ASKED, answers("3 kare."))

    assert runner.start("düğün", 1, "Peki 7?", ASKED, answers("7 hazır.")) is False

    assert record.lines == [("question", "düğün", 1, "Kaç kare var?", ASKED)]
    assert len(held) == 1


def test_two_chats_work_at_once_in_one_project_or_two(runner, held):
    for project, chat in (("düğün", 2), ("düğün", 1), ("kına", 1)):
        assert runner.start(project, chat, "Kaç kare var?", ASKED, answers("3 kare.")) is True

    assert runner.working("düğün") == [1, 2]
    assert runner.working("kına") == [1]
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
    assert runner.working("düğün") == []


def test_work_that_raises_fails_in_its_own_words(runner, record, held):
    """A disk that went away, a project deleted under the agent: the error's own words, never a
    guessed cause."""
    def work(run):
        raise OSError("[Errno 107] Transport endpoint is not connected")

    runner.start("düğün", 1, "Kaç kare var?", ASKED, work)
    held.pop()()

    assert record.lines[-1] == ("failure", "düğün", 1,
                                "[Errno 107] Transport endpoint is not connected")
    assert runner.working("düğün") == []


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
    assert runner.working("düğün") == []

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
    assert runner.working("düğün") == [1]
    new()
    assert record.lines == [("question", "düğün", 1, "Kaç kare var?", ASKED),
                            ("stopped", "düğün", 1),
                            ("question", "düğün", 1, "Peki 7?", ASKED),
                            ("step", "düğün", 1, *READING),
                            ("answer", "düğün", 1, "7 hazır.")]
    assert runner.working("düğün") == []
