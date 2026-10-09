"""The wait for a local server to answer, run rather than read (madde 439).

ComfyUI and Flask are both waited for this way. The look and the clock are faked here, and the log is
a real file.
"""
import importlib
import io
import urllib.error
import urllib.request
from types import SimpleNamespace

import pytest

URL = "http://127.0.0.1:8188/system_stats"
REFUSED = urllib.error.URLError(ConnectionRefusedError(111, "Connection refused"))


@pytest.fixture
def wait():
    """The module. Imported here rather than at the top: a module that is not there yet fails each
    test on its own instead of the whole file."""
    return importlib.import_module("colab.wait")


@pytest.fixture
def log(tmp_path):
    path = tmp_path / "server.log"
    path.write_text("".join(f"log satırı {n}\n" for n in range(1, 41)), encoding="utf-8")
    return str(path)


class Clock:
    """The looks and the clock: `answers` is what each look gets -- True for an answer, an exception
    to raise -- the last one standing for every later one. Every look and sleep is remembered."""

    def __init__(self, monkeypatch, wait, answers):
        self.events, self._answers = [], list(answers)
        monkeypatch.setattr(wait.time, "sleep", lambda s: self.events.append(f"sleep {s}"))
        monkeypatch.setattr(urllib.request, "urlopen", self._urlopen)

    def _urlopen(self, url, timeout=None):
        self.events.append(f"look {url}")
        answer = self._answers.pop(0) if len(self._answers) > 1 else self._answers[0]
        if isinstance(answer, Exception):
            raise answer
        return io.BytesIO(b"{}")


def _process(events, polls):
    """A started process: each poll gets the next of `polls`, None while it runs."""
    polls = list(polls)

    def poll():
        events.append("poll")
        process.returncode = polls.pop(0) if len(polls) > 1 else polls[0]
        return process.returncode

    process = SimpleNamespace(returncode=None, poll=poll)
    return process


def test_a_server_that_answers_hands_back_how_long_it_took(wait, monkeypatch, log):
    clock = Clock(monkeypatch, wait, [REFUSED, REFUSED, True])

    assert wait.wait_for(URL, "ComfyUI", log) == 6
    assert clock.events == ["sleep 2", f"look {URL}"] * 3


def test_a_server_that_never_answers_stops_with_its_last_look_and_its_log(wait, monkeypatch, log):
    """Ninety seconds, in looks two seconds apart. The error is one piece, copied whole: our line,
    what the last look got in its own words, and the end of the server's log."""
    clock = Clock(monkeypatch, wait, [REFUSED])

    with pytest.raises(RuntimeError) as failure:
        wait.wait_for(URL, "Flask", log)

    said = str(failure.value)
    assert clock.events.count("sleep 2") == 45
    assert said.splitlines()[:3] == [f"❌ Flask 90 sn içinde cevap vermedi — {URL}",
                                     "URLError: <urlopen error [Errno 111] Connection refused>",
                                     f"--- {log} · son 30 satır ---"], f"Hata böyle:\n{said}"
    assert said.endswith("log satırı 40") and "log satırı 10\n" not in said


def test_an_answer_counts_only_while_the_process_runs(wait, monkeypatch, log):
    """Something answers, but the process the cell started has ended: what answered is not it."""
    clock = Clock(monkeypatch, wait, [True])
    process = _process(clock.events, [1])

    with pytest.raises(RuntimeError) as failure:
        wait.wait_for(URL, "ComfyUI", log, process)

    assert str(failure.value).startswith(f"❌ ComfyUI kapandı — exit 1\n--- {log} · son 30 satır ---")
    assert clock.events == ["sleep 2", f"look {URL}", "poll"], "Süreç bakıştan sonra sorulmadı"


def test_a_process_that_ends_while_starting_stops_the_wait_at_once(wait, monkeypatch, log):
    clock = Clock(monkeypatch, wait, [REFUSED])
    process = _process(clock.events, [None, 1])

    with pytest.raises(RuntimeError) as failure:
        wait.wait_for(URL, "ComfyUI", log, process)

    assert clock.events.count(f"look {URL}") == 2, "Kapanan süreç 90 sn beklenmemeli"
    assert str(failure.value).endswith("log satırı 40")
