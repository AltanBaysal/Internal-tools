"""The notebook's ComfyUI start, run rather than read (madde 433).

It was the ComfyUI cell's own code, where no test could run it, and it said hazır whenever anything
answered on the port: it never asked the process it had started. The machine under it is faked here
-- pkill, the port, the process, ComfyUI's answer and the clock -- and the log is a real file, which
the fake process writes into the way ComfyUI does.
"""
import importlib
import io
import subprocess
import urllib.error
import urllib.request
from types import SimpleNamespace

import pytest

COMMAND = ["python", "main.py", "--listen", "127.0.0.1", "--port", "8188"]
TERM = "pkill -TERM -f python main.py"
KILL = "pkill -KILL -f python main.py"
# What ComfyUI writes while it starts: forty lines, so the tail shows where it is cut.
LOG = "".join(f"comfy satırı {n}\n" for n in range(1, 41))
REFUSED = urllib.error.URLError(ConnectionRefusedError(111, "Connection refused"))


@pytest.fixture
def comfy():
    """The module. Imported here rather than at the top: a module that is not there yet fails each
    test on its own instead of the whole file."""
    return importlib.import_module("colab.comfy")


class Machine:
    """The machine under the cell.

    `taken` is what each look at the port finds, in order -- True when something still accepts a
    connection there -- and the port is free once the list runs out. `answers` is what each look at
    /system_stats gets: True for an answer, an exception to raise. `polls` is what each question to
    the started process gets: None while it runs, its exit code once it ended. The last item of
    `answers` and `polls` stands for every later one.
    """

    def __init__(self, monkeypatch, comfy, taken=(), answers=(True,), polls=(None,)):
        self.events, self.slept, self.started, self.urls = [], [], [], []
        self._taken, self._answers, self._polls = list(taken), list(answers), list(polls)
        monkeypatch.setattr(comfy.subprocess, "run", self._run)
        monkeypatch.setattr(comfy.subprocess, "Popen", self._popen)
        monkeypatch.setattr(urllib.request, "urlopen", self._urlopen)
        monkeypatch.setattr(comfy.socket, "create_connection", self._connect)
        monkeypatch.setattr(comfy.time, "sleep", self.slept.append)

    @staticmethod
    def _next(items):
        return items.pop(0) if len(items) > 1 else items[0]

    def _run(self, cmd, **kwargs):
        self.events.append(" ".join(cmd))
        return SimpleNamespace(returncode=0)

    def _popen(self, cmd, cwd=None, stdout=None, stderr=None):
        self.events.append("popen")
        self.started.append({"cmd": cmd, "cwd": cwd, "stderr": stderr})
        # Bytes, the way ComfyUI writes them through the descriptor it inherits.
        stdout.write(LOG.encode("utf-8"))
        stdout.flush()
        machine = self

        class Process:
            pid = 4242
            returncode = None

            def poll(self):
                machine.events.append("poll")
                self.returncode = machine._next(machine._polls)
                return self.returncode

        return Process()

    def _urlopen(self, url, timeout=None):
        self.events.append("look")
        self.urls.append(url)
        answer = self._next(self._answers)
        if isinstance(answer, Exception):
            raise answer
        return io.BytesIO(b'{"devices": []}')

    def _connect(self, address, timeout=None):
        self.events.append("port?")
        if self._taken and self._taken.pop(0):
            return SimpleNamespace(close=lambda: None)
        raise ConnectionRefusedError(111, "Connection refused")


def _start(comfy, tmp_path):
    return comfy.start_comfy("/content/ComfyUI", 8188, str(tmp_path / "comfyui.log"))


def _failure(comfy, tmp_path):
    with pytest.raises(RuntimeError) as exc:
        _start(comfy, tmp_path)
    return str(exc.value)


def test_comfyui_is_ready_once_the_process_it_started_answers(comfy, monkeypatch, tmp_path,
                                                              capsys):
    machine = Machine(monkeypatch, comfy, answers=[REFUSED, REFUSED, True])

    process = _start(comfy, tmp_path)

    assert machine.started == [{"cmd": COMMAND, "cwd": "/content/ComfyUI",
                                "stderr": subprocess.STDOUT}]
    assert machine.urls[-1] == "http://127.0.0.1:8188/system_stats"
    assert process.pid == 4242
    out = capsys.readouterr().out
    assert "ComfyUI başlatıldı (PID 4242)" in out
    assert "ComfyUI hazır (6s)" in out
    # Its output goes to the log, which the app reads when it cannot reach ComfyUI (madde 230).
    assert (tmp_path / "comfyui.log").read_text(encoding="utf-8") == LOG


def test_the_old_comfyui_is_gone_before_the_new_one_starts(comfy, monkeypatch, tmp_path):
    """While the old one holds the port it is what answers, and the new one cannot take it."""
    machine = Machine(monkeypatch, comfy, taken=[True, True])

    _start(comfy, tmp_path)

    assert machine.events[:5] == [TERM, "port?", "port?", "port?", "popen"]
    assert machine.slept[:2] == [1, 1]


def test_a_first_start_with_nothing_on_the_port_waits_for_nothing(comfy, monkeypatch, tmp_path):
    machine = Machine(monkeypatch, comfy)

    _start(comfy, tmp_path)

    assert machine.events[:3] == [TERM, "port?", "popen"]
    assert machine.slept == [2]


def test_an_old_comfyui_that_does_not_go_is_killed(comfy, monkeypatch, tmp_path):
    machine = Machine(monkeypatch, comfy, taken=[True] * 30)

    _start(comfy, tmp_path)

    assert [event for event in machine.events if event.startswith("pkill")] == [TERM, KILL]
    assert machine.events.index(KILL) == 31
    assert machine.slept[:30] == [1] * 30
    assert "popen" in machine.events


def test_a_port_that_never_frees_fails_the_cell_before_anything_starts(comfy, monkeypatch,
                                                                       tmp_path):
    machine = Machine(monkeypatch, comfy, taken=[True] * 60)

    said = _failure(comfy, tmp_path)

    assert machine.started == []
    assert "8188" in said and "60 sn" in said


def test_it_never_says_ready_for_a_comfyui_it_did_not_start(comfy, monkeypatch, tmp_path, capsys):
    """Something answers on the port, but the process this cell started has ended: whatever
    answered is not the ComfyUI it started."""
    Machine(monkeypatch, comfy, answers=[True], polls=[1])

    said = _failure(comfy, tmp_path)

    assert said.splitlines()[0] == "❌ ComfyUI kapandı — exit 1"
    assert "hazır" not in capsys.readouterr().out


def test_a_comfyui_that_ends_while_starting_fails_the_cell_at_once_with_its_own_log(
        comfy, monkeypatch, tmp_path):
    machine = Machine(monkeypatch, comfy, answers=[REFUSED], polls=[None, 1])

    said = _failure(comfy, tmp_path)

    assert machine.events.count("look") == 2, "Kapanan süreç 90 sn beklenmemeli"
    assert said.splitlines()[0] == "❌ ComfyUI kapandı — exit 1"
    assert "comfy satırı 11\n" in said and said.rstrip().endswith("comfy satırı 40")
    assert "comfy satırı 10\n" not in said


def _commands(monkeypatch, comfy, fails=None):
    """console.run, faked: each command remembered with the folder it ran in. The command whose
    subcommand is `fails` raises the way console.run does, with the command's own last line."""
    commands = []

    def run(cmd, label, cwd=None, timeout=3600):
        commands.append((cmd, cwd))
        if cmd[1] == fails:
            raise RuntimeError(f"{label}: exit 1\nfatal: git said no")

    monkeypatch.setattr(comfy, "run", run)
    return commands


def test_comfyui_is_cloned_when_it_is_not_there_and_then_set_up(comfy, monkeypatch, tmp_path):
    """Cloned, pulled, and its requirements and the extras installed, in that order, each in
    ComfyUI's own folder but the clone. The clone and pip are asked for their progress, and pip is
    not quiet (madde 439)."""
    root = str(tmp_path / "ComfyUI")
    commands = _commands(monkeypatch, comfy)

    comfy.install_comfy(root)

    assert commands == [
        (["git", "clone", "--progress", "https://github.com/comfyanonymous/ComfyUI.git", root], None),
        (["git", "pull", "-q"], root),
        (["pip", "install", "--progress-bar", "on", "-r", "requirements.txt"], root),
        (["pip", "install", "--progress-bar", "on", "opencv-python", "imageio", "imageio-ffmpeg"],
         root),
    ], f"ComfyUI böyle kurulmadı: {commands}"


def test_a_comfyui_already_there_is_pulled_rather_than_cloned(comfy, monkeypatch, tmp_path):
    """Run all twice in one session: the second pass takes the new commits and clones nothing."""
    root = tmp_path / "ComfyUI"
    root.mkdir()
    commands = _commands(monkeypatch, comfy)

    comfy.install_comfy(str(root))

    assert [cmd[:2] for cmd, _ in commands] == [["git", "pull"], ["pip", "install"],
                                                ["pip", "install"]], \
        f"Yerinde duran ComfyUI yeniden klonlandı: {commands}"


def test_a_pull_that_fails_says_what_git_said_and_the_install_goes_on(comfy, monkeypatch, tmp_path,
                                                                      capsys):
    """A second Run all can find the clone where git will not pull -- a detached HEAD, local changes
    -- and the ComfyUI already there still works."""
    root = tmp_path / "ComfyUI"
    root.mkdir()
    commands = _commands(monkeypatch, comfy, fails="pull")

    comfy.install_comfy(str(root))

    out = capsys.readouterr().out
    assert "git pull ComfyUI: exit 1\nfatal: git said no" in out and "⚠️" in out, \
        f"Konsol git'in ne dediğini uyarı olarak basmadı:\n{out}"
    assert [cmd[:2] for cmd, _ in commands][1:] == [["pip", "install"], ["pip", "install"]], \
        f"Düşen pull'dan sonra kurulum sürmedi: {commands}"


def test_a_clone_that_fails_stops_the_cell(comfy, monkeypatch, tmp_path):
    """Without a clone there is no ComfyUI to go on with."""
    commands = _commands(monkeypatch, comfy, fails="clone")

    with pytest.raises(RuntimeError) as failure:
        comfy.install_comfy(str(tmp_path / "ComfyUI"))

    assert str(failure.value).startswith("clone ComfyUI: exit 1"), f"Hata böyle: {failure.value}"
    assert len(commands) == 1, f"Düşen klondan sonra komut koştu: {commands}"


def test_a_comfyui_that_never_answers_fails_after_ninety_seconds_with_what_the_port_said(
        comfy, monkeypatch, tmp_path):
    machine = Machine(monkeypatch, comfy, answers=[REFUSED])

    said = _failure(comfy, tmp_path)

    assert machine.events.count("look") == 45
    assert machine.slept[-45:] == [2] * 45
    assert said.splitlines()[0] == \
        "❌ ComfyUI 90 sn içinde cevap vermedi — http://127.0.0.1:8188/system_stats"
    assert "URLError: <urlopen error [Errno 111] Connection refused>" in said
    assert said.rstrip().endswith("comfy satırı 40")
