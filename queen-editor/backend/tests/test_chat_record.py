"""The agent's chats, kept with their project for good (madde 417).

One file in the project's folder that is only ever added to and is folded on read -- the photo
record's way: a session that dies mid-write loses at most the line it was adding. What 420's agent
will write, these tests write through the record's own methods.

The new module is imported inside the tests: it is written after this file, and an import at the
top would stop the whole collection instead of failing these questions.
"""
import os
import threading

import pytest

from backend.services.drive.storage import DriveStorage

ASKED = "2026-10-06T10:00:00+00:00"
LATER = "2026-10-06T10:05:00+00:00"
READING = ("3 numaralı kareyi okuyor…", "3 numaralı kareyi okudu")
LOOKING = ("Bir görsele bakıyor…", "Bir görsele baktı")
REFUSED = "Model hata döndü, farklı şekilde dene."


def record_at(path):
    from backend.features.agent.data.chat_record import DriveChatRecord
    return DriveChatRecord(DriveStorage(str(path)))


@pytest.fixture
def record(tmp_path):
    (tmp_path / "düğün").mkdir()
    return record_at(tmp_path)


def asked(record, chat=1, text="Kaç kare var?", at=ASKED):
    """A chat with one question on it."""
    record.add_chat("düğün", chat)
    record.add_question("düğün", chat, text, at)


def step(pair, finished):
    running, done = pair
    return {"running": running, "done": done, "finished": finished}


def test_a_project_with_no_chats_reads_none(record):
    assert record.chats("düğün") == []


def test_a_new_chat_reads_back_with_nothing_asked(record):
    record.add_chat("düğün", 1)

    assert record.chats("düğün") == [{"id": 1, "questions": []}]


def test_a_question_reads_back_with_its_steps_and_its_answer(record):
    asked(record)
    record.add_step("düğün", 1, *READING)
    record.finish_step("düğün", 1)
    record.add_step("düğün", 1, *LOOKING)
    record.finish_step("düğün", 1)
    record.answer("düğün", 1, "Projede 12 kare var.")

    assert record.chats("düğün") == [{"id": 1, "questions": [{
        "text": "Kaç kare var?", "askedAt": ASKED,
        "steps": [step(READING, True), step(LOOKING, True)],
        "outcome": {"kind": "answer", "text": "Projede 12 kare var."}}]}]


def test_a_step_still_going_on_reads_unfinished_and_its_question_has_no_outcome(record):
    """No outcome is what a question the agent is still working on looks like (420)."""
    asked(record)
    record.add_step("düğün", 1, *READING)

    question = record.chats("düğün")[0]["questions"][0]
    assert question["steps"] == [step(READING, False)]
    assert question["outcome"] is None


@pytest.mark.parametrize("text", [
    REFUSED,
    "HTTPSConnectionPool(host='api.deepseek.com', port=443): Read timed out. (read timeout=120)",
], ids=["refusal", "technical"])
def test_a_failure_keeps_its_own_text(record, text):
    """The screen draws both as one card (BEHAVIOUR.md, Agent panel); only the words differ."""
    asked(record)
    record.fail("düğün", 1, text)

    assert record.chats("düğün")[0]["questions"][0]["outcome"] == {"kind": "failure", "text": text}


def test_a_stopped_question_says_so(record):
    asked(record)
    record.add_step("düğün", 1, *READING)
    record.finish_step("düğün", 1)
    record.stop("düğün", 1)

    question = record.chats("düğün")[0]["questions"][0]
    assert question["outcome"] == {"kind": "stopped"}
    assert question["steps"] == [step(READING, True)]


def test_steps_and_outcomes_land_on_the_chats_latest_question(record):
    asked(record)
    record.answer("düğün", 1, "12 kare.")
    record.add_question("düğün", 1, "Hangisi hata verdi?", LATER)
    record.add_step("düğün", 1, *READING)
    record.finish_step("düğün", 1)
    record.answer("düğün", 1, "7 numaralı kare.")

    first, second = record.chats("düğün")[0]["questions"]
    assert first["steps"] == []
    assert first["outcome"] == {"kind": "answer", "text": "12 kare."}
    assert (second["text"], second["askedAt"]) == ("Hangisi hata verdi?", LATER)
    assert second["steps"] == [step(READING, True)]
    assert second["outcome"] == {"kind": "answer", "text": "7 numaralı kare."}


def test_two_chats_written_at_the_same_time_stay_apart(record):
    """Two chats may run at once (BEHAVIOUR.md, Agent panel), so their lines interleave. Each
    outcome finishes its own chat's step and no other (madde 420)."""
    record.add_chat("düğün", 1)
    record.add_chat("düğün", 2)
    record.add_question("düğün", 1, "Birinci", ASKED)
    record.add_question("düğün", 2, "İkinci", LATER)
    record.add_step("düğün", 2, *LOOKING)
    record.add_step("düğün", 1, *READING)
    record.answer("düğün", 1, "Bir.")
    record.fail("düğün", 2, REFUSED)

    one, two = record.chats("düğün")
    assert one == {"id": 1, "questions": [{
        "text": "Birinci", "askedAt": ASKED, "steps": [step(READING, True)],
        "outcome": {"kind": "answer", "text": "Bir."}}]}
    assert two == {"id": 2, "questions": [{
        "text": "İkinci", "askedAt": LATER, "steps": [step(LOOKING, True)],
        "outcome": {"kind": "failure", "text": REFUSED}}]}


def test_another_projects_chats_are_not_in_this_one(tmp_path, record):
    (tmp_path / "kına").mkdir()
    asked(record)

    assert record.chats("kına") == []


def test_the_record_is_one_file_in_the_projects_own_folder(tmp_path, record):
    """Inside the folder, so a renamed project carries its chats and a deleted one takes them."""
    asked(record)
    record.answer("düğün", 1, "12 kare.")

    assert os.listdir(tmp_path / "düğün") == ["chats.jsonl"]


def test_a_write_only_adds_to_the_end(tmp_path, record):
    """FOUNDATION 1: nothing already written is rewritten."""
    asked(record)
    path = tmp_path / "düğün" / "chats.jsonl"
    before = path.read_text(encoding="utf-8")

    record.answer("düğün", 1, "12 kare.")

    after = path.read_text(encoding="utf-8")
    assert after.startswith(before) and after != before


def test_a_half_written_last_line_hides_nothing_before_it(tmp_path, record):
    asked(record)
    with open(tmp_path / "düğün" / "chats.jsonl", "a", encoding="utf-8") as f:
        f.write('{"chat": 1, "event": "ans')

    assert record.chats("düğün")[0]["questions"][0]["text"] == "Kaç kare var?"


def test_a_fresh_record_reads_what_an_earlier_one_wrote(tmp_path, record):
    """A server restart: nothing is held in memory, the disk is the truth (FOUNDATION 2)."""
    asked(record)
    record.answer("düğün", 1, "12 kare.")

    assert record_at(tmp_path).chats("düğün") == [{"id": 1, "questions": [{
        "text": "Kaç kare var?", "askedAt": ASKED, "steps": [],
        "outcome": {"kind": "answer", "text": "12 kare."}}]}]


def test_a_project_is_its_folder(record):
    assert record.project_exists("düğün") is True
    assert record.project_exists("yok") is False


# --- Madde 420: what the agent writes ------------------------------------------------------------

@pytest.mark.parametrize("end, outcome", [
    (lambda record: record.answer("düğün", 1, "12 kare."), {"kind": "answer", "text": "12 kare."}),
    (lambda record: record.fail("düğün", 1, REFUSED), {"kind": "failure", "text": REFUSED}),
], ids=["answer", "failure"])
def test_an_answer_or_a_failure_finishes_the_step_going_on(record, end, outcome):
    """BEHAVIOUR.md, Agent panel: "An answer or a failure finishes the last step." The agent keeps a
    step going while the model reads what it brought."""
    asked(record)
    record.add_step("düğün", 1, *READING)
    record.finish_step("düğün", 1)
    record.add_step("düğün", 1, *LOOKING)

    end(record)

    question = record.chats("düğün")[0]["questions"][0]
    assert question["steps"] == [step(READING, True), step(LOOKING, True)]
    assert question["outcome"] == outcome


def test_a_stop_drops_the_step_going_on_and_keeps_the_finished_ones(record):
    """BEHAVIOUR.md, Agent panel: "Stopping keeps the finished steps and drops the one that was going
    on, since it did not finish." """
    asked(record)
    record.add_step("düğün", 1, *READING)
    record.finish_step("düğün", 1)
    record.add_step("düğün", 1, *LOOKING)

    record.stop("düğün", 1)

    question = record.chats("düğün")[0]["questions"][0]
    assert question["steps"] == [step(READING, True)]
    assert question["outcome"] == {"kind": "stopped"}


def test_a_line_for_a_project_whose_folder_is_gone_is_refused_and_makes_no_folder(tmp_path,
                                                                                    record):
    """An agent still at work when its project was renamed or deleted must not bring the folder back:
    every folder under the root is a project (madde 417)."""
    from backend.features.agent.domain.usecases.chats import ProjectMissing

    with pytest.raises(ProjectMissing) as refused:
        record.answer("taşındı", 1, "12 kare.")

    assert str(refused.value) == "Proje yok: taşındı"
    assert not (tmp_path / "taşındı").exists()


class HeldStorage:
    """A storage that holds the first line it is given half-written until the test lets it go, and
    notes whether a second line began while the first was still being written."""

    def __init__(self):
        self.lines = []
        self.writing = False
        self.overlapped = False
        self.first_in = threading.Event()
        self.let_go = threading.Event()

    def dir_exists(self, subdir):
        return True

    def append_line(self, subdir, name, line):
        if self.writing:
            self.overlapped = True
        self.writing = True
        if not self.first_in.is_set():
            self.first_in.set()
            self.let_go.wait(5)
        self.lines.append(line)
        self.writing = False


def test_two_writers_never_add_a_line_at_the_same_time():
    """Two agents, the door that asks and the door that stops all write to one chats.jsonl from
    their own threads; two appends at once can tear a line or lose one. The second writer is given a
    fifth of a second to start while the first line is held -- proving that it waited takes a wait."""
    from backend.features.agent.data.chat_record import DriveChatRecord
    storage = HeldStorage()
    record = DriveChatRecord(storage)
    first = threading.Thread(target=record.answer, args=("düğün", 1, "Bir."))
    first.start()
    assert storage.first_in.wait(5)
    second = threading.Thread(target=record.answer, args=("düğün", 2, "İki."))
    second.start()
    second.join(0.2)

    storage.let_go.set()
    first.join(5)
    second.join(5)

    assert storage.overlapped is False
    assert len(storage.lines) == 2
