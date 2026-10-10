"""Reading a chat with its running turn (Madde 462), with fake turns and a fake store."""
from backend.features.workspace.domain.chat import Chat, Message
from backend.features.workspace.domain.turn import Snapshot
from backend.features.workspace.domain.usecases.read_chat import read_chat

AT = "2026-10-10T10:00:00.000+00:00"
ON_DISK = Chat(id="c1", title="hi", created_at=AT, messages=(Message("user", AT, "hi"),))
HELD = Chat(id="c1", title="hi", created_at=AT, messages=(Message("user", AT, "held"),))


class Disk:
    def __init__(self):
        self.reads = 0

    def get(self, project_id, chat_id):
        self.reads += 1
        return ON_DISK if chat_id == "c1" else None


class Live:
    """A turn that notes the order it was asked in."""

    def __init__(self, record, asked):
        self._record = record
        self.asked = asked

    def snapshot(self):
        self.asked.append("snapshot")
        return Snapshot(id="t1")

    def record(self):
        self.asked.append("record")
        return self._record


class Turns:
    def __init__(self, live=None):
        self.live = live

    def get(self, project_id, chat_id):
        return self.live


def test_with_nothing_running_the_chat_is_read_off_the_disk():
    disk = Disk()
    assert read_chat(Turns(), disk, "p1", "c1") == (ON_DISK, None)
    assert disk.reads == 1


def test_a_running_turn_hands_its_record_and_the_disk_is_not_read():
    disk, asked = Disk(), []
    assert read_chat(Turns(Live(HELD, asked)), disk, "p1", "c1") == (HELD, Snapshot(id="t1"))
    assert disk.reads == 0


def test_a_turn_not_yet_handed_its_record_leaves_the_chat_to_the_disk():
    # Held while its question is being written: running, and the disk has the chat.
    disk = Disk()
    assert read_chat(Turns(Live(None, [])), disk, "p1", "c1") == (ON_DISK, Snapshot(id="t1"))
    assert disk.reads == 1


def test_the_turn_is_looked_at_before_its_record():
    # A turn ending between the two reads then reads as running on its final record -- the browser
    # listens and hears the end at once. The other order would pair an ended turn with the record
    # from before its answer: a question shown unanswered, with nothing left to listen to.
    asked = []
    read_chat(Turns(Live(HELD, asked)), Disk(), "p1", "c1")
    assert asked == ["snapshot", "record"]


def test_a_chat_that_is_not_there_is_none():
    assert read_chat(Turns(), Disk(), "p1", "nope") == (None, None)
