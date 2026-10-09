"""Madde 447: one file on disk kept up to date with a state held in memory, from one thread.

The request that changes the state does not wait for the disk; the writer writes the newest state,
so changes that come in a row go out in one write. The user's words: "flask tak diye kapanırsa
kaybolsun sıkıntı yok" -- a sudden death may lose the last changes, which is why nothing here waits.
"""
import logging
import threading

import pytest

from backend.features.workspace.data.queued_write import RETRY_SECONDS, TRIES, QueuedWrite


class HeldStore:
    """A store whose writes can be held open, to see what arrives while one is under way."""

    def __init__(self):
        self.written = []
        self.hold = threading.Event()
        self.hold.set()
        self.started = threading.Event()
        # How many of the next writes fail.
        self.fail = 0

    def write_text(self, rel, text):
        self.started.set()
        self.hold.wait()
        if self.fail:
            self.fail -= 1
            raise OSError("[Errno 5] Input/output error")
        self.written.append((rel, text))


class State:
    def __init__(self):
        self.value = 0

    def render(self):
        return f"state {self.value}"


def _queue(pauses=None):
    store, state = HeldStore(), State()
    # The pause between tries is the test's own, so no test waits a real second.
    pause = (lambda seconds: pauses.append(seconds)) if pauses is not None else (lambda seconds: None)
    return store, state, QueuedWrite(store, "projects.json", state.render, pause=pause)


def _texts(store):
    return [text for _, text in store.written]


def test_changed_does_not_wait_for_the_disk():
    store, state, queue = _queue()
    store.hold.clear()
    state.value = 1
    queue.changed()  # would hang here if it wrote on the caller's thread
    assert store.started.wait(5), "Yazıcı başlamadı"
    store.hold.set()
    queue.flush()
    assert store.written == [("projects.json", "state 1")], "Durum diske yazılmadı"


def test_what_is_written_is_the_newest_state():
    store, state, queue = _queue()
    state.value = 3
    queue.changed()
    queue.flush()
    assert _texts(store)[-1] == "state 3", "Son durum yazılmadı"


def test_changes_that_come_during_a_write_go_out_in_one_write():
    store, state, queue = _queue()
    store.hold.clear()
    state.value = 1
    queue.changed()
    assert store.started.wait(5)
    # Three changes while the first write is held open: one more write carries all three.
    for value in (2, 3, 4):
        state.value = value
        queue.changed()
    store.hold.set()
    queue.flush()
    assert _texts(store) == ["state 1", "state 4"], (
        "Arka arkaya gelen değişiklikler tek yazmada toplanmadı"
    )


def test_the_state_it_was_built_on_is_not_written():
    # That is what the file already holds -- or no file, and nothing that needs one.
    store, state, queue = _queue()
    queue.changed()
    queue.flush()
    assert store.written == [], "Diskteki durum yeniden yazıldı"


def test_the_same_text_is_not_written_twice():
    store, state, queue = _queue()
    state.value = 1
    queue.changed()
    queue.flush()
    queue.changed()
    queue.flush()
    assert _texts(store) == ["state 1"], "Değişmeyen durum yeniden yazıldı"


def test_a_failed_write_is_tried_again_after_a_pause(caplog):
    # A change the user saw succeed must not wait for another change to reach the disk.
    pauses = []
    store, state, queue = _queue(pauses)
    store.fail = 2
    state.value = 1
    with caplog.at_level(logging.ERROR):
        queue.changed()
        queue.flush()
    assert _texts(store) == ["state 1"], "Başarısız yazma yeniden denenmedi"
    assert pauses == [RETRY_SECONDS, RETRY_SECONDS], "Denemeler arasında beklenmedi"
    errors = [record.getMessage() for record in caplog.records]
    assert errors == [
        f"projects.json was not written (try 1 of {TRIES}): [Errno 5] Input/output error",
        f"projects.json was not written (try 2 of {TRIES}): [Errno 5] Input/output error",
    ], "Her başarısız deneme işletim sisteminin sözüyle loglanmadı"


def test_a_retry_writes_the_newest_state():
    store, state, queue = _queue([])
    store.fail = 1
    state.value = 1

    def changed_meanwhile(seconds):
        state.value = 2

    queue._pause = changed_meanwhile
    queue.changed()
    queue.flush()
    assert _texts(store) == ["state 2"], "Yeniden deneme en son durumu yazmadı"


def test_the_tries_are_bounded_and_the_next_change_starts_again(caplog):
    store, state, queue = _queue([])
    store.fail = TRIES
    state.value = 1
    with caplog.at_level(logging.ERROR):
        queue.changed()
        queue.flush()
    assert store.written == [] and len(caplog.records) == TRIES, "Denemeler sınırlı değil"
    queue.changed()
    queue.flush()
    assert _texts(store) == ["state 1"], (
        "Denemeler bittikten sonraki değişiklik durumu yeniden yazmadı"
    )


def test_a_writer_that_cannot_start_does_not_hang_flush(monkeypatch):
    store, state, queue = _queue()

    def refused(self):
        raise RuntimeError("can't start new thread")

    monkeypatch.setattr(threading.Thread, "start", refused)
    state.value = 1
    with pytest.raises(RuntimeError):
        queue.changed()
    monkeypatch.undo()
    queue.flush()  # would wait for ever on a writer that never ran
    queue.changed()
    queue.flush()
    assert _texts(store) == ["state 1"], "Başlayamayan yazıcıdan sonra durum yazılmadı"


def test_the_writer_is_gone_once_there_is_nothing_to_write():
    store, state, queue = _queue()
    state.value = 1
    queue.changed()
    queue.flush()
    writers = [thread for thread in threading.enumerate() if thread.name == "write projects.json"]
    for thread in writers:
        thread.join(5)
    assert not any(thread.is_alive() for thread in writers), "Yazacak bir şey yokken yazıcı yaşıyor"


def test_the_writer_is_waited_for_on_exit():
    # Not a daemon: an ordinary exit, Ctrl+C included, waits for the last write.
    store, state, queue = _queue()
    store.hold.clear()
    state.value = 1
    queue.changed()
    assert store.started.wait(5)
    writer = next(thread for thread in threading.enumerate() if thread.name == "write projects.json")
    assert not writer.daemon, "Yazıcı daemon: normal kapanışta son yazma beklenmez"
    store.hold.set()
    queue.flush()


EXIT_SCRIPT = r"""
import sys, threading, time
from backend.features.workspace.data.queued_write import QueuedWrite

class SlowStore:
    def write_text(self, rel, text):
        time.sleep(1)
        open(sys.argv[1], "w").write(text)

state = {"value": 0}
queue = QueuedWrite(SlowStore(), "projects.json", lambda: f"state {state['value']}")

def request():
    # What a werkzeug request thread is: a daemon. A thread takes its daemon flag from its creator.
    state["value"] = 1
    queue.changed()

asked = threading.Thread(target=request, daemon=True)
asked.start()
asked.join()
# The main thread ends here, an ordinary exit, with the write still under way.
"""


def test_a_change_from_a_request_thread_still_lands_on_exit(tmp_path):
    # The real server calls changed() from werkzeug's request threads, which are daemons; a writer
    # that inherited that would be dropped by an ordinary exit (SIGTERM through main.py, Ctrl+C).
    import os
    import subprocess
    import sys

    landed = tmp_path / "landed.txt"
    queen_agent = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    finished = subprocess.run(
        [sys.executable, "-c", EXIT_SCRIPT, str(landed)],
        cwd=queen_agent,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert finished.returncode == 0, finished.stderr
    assert landed.exists() and landed.read_text() == "state 1", (
        "İstek iş parçacığından gelen değişiklik normal kapanışta yazılmadı"
    )


def test_flush_with_nothing_pending_returns_at_once():
    _, _, queue = _queue()
    queue.flush()
