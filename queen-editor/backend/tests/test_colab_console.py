"""The notebook's shell call, run rather than read.

Every command the notebook's own code runs goes through run: the custom node installs, the curl and
aria2c downloads, and the sound engine's clone and pip install. Until madde 398 it held a command's
output until the command ended, and a pip install could sit silent for thirty minutes. The command
here is real -- a small Python program standing in for git, pip and curl -- and nothing reaches the
network.
"""
import importlib
import sys
import time

import pytest

# Writes a line without flushing, waits up to five seconds for the test to say it saw the line, and
# tells which way it went. pip is a Python program too, and into a pipe Python holds its lines in a
# buffer until it ends.
WAITS_FOR_ITS_LINE = """
import os, sys, time
print("first")
deadline = time.time() + 5
while not os.path.exists(sys.argv[1]) and time.time() < deadline:
    time.sleep(0.01)
print("seen" if os.path.exists(sys.argv[1]) else "not seen")
"""

# curl's progress line, redrawn in place.
PROGRESS = r"""
import sys
sys.stderr.buffer.write(b"10%\r50%\r100%\n")
sys.stderr.buffer.flush()
"""


@pytest.fixture
def console():
    """The module. Imported here rather than at the top: test_requirements.py reads every top level
    import under backend/ as a package pip installs, and colab/ is this repo's own folder."""
    return importlib.import_module("colab.console")


def _python(code, *args):
    return [sys.executable, "-c", code, *args]


class _Screen:
    """The cell's output, standing in for sys.stdout: it keeps what it is given, and creates the signal
    file once the command's first line has arrived."""

    def __init__(self, signal):
        self.text = ""
        self.signal = signal

    def write(self, text):
        self.text += text
        if "first" in self.text:
            self.signal.touch()
        return len(text)

    def flush(self):
        pass


def test_a_command_s_line_reaches_the_console_while_the_command_runs(console, monkeypatch, tmp_path):
    """The user's words (madde 398): "burda takıldı, output'ta bir şey de yok". A line that arrives
    only when the command ends cannot say where it hung."""
    screen = _Screen(tmp_path / "seen")
    monkeypatch.setattr(sys, "stdout", screen)

    console.run(_python(WAITS_FOR_ITS_LINE, str(tmp_path / "seen")), "canlı")

    assert screen.text.splitlines() == ["first", "seen"], \
        f"Komutun satırı komut sürerken konsola gelmedi: {screen.text!r}"


def test_the_command_s_error_stream_comes_to_the_same_console_in_order(console, capsys):
    """git, pip and curl write their progress and their errors to stderr, and where a command hangs is
    read from the order of the two streams."""
    console.run(_python("import sys\nprint('one')\nprint('two', file=sys.stderr)\nprint('three')"),
                "sıra")

    assert capsys.readouterr().out.splitlines() == ["one", "two", "three"], \
        "Komutun iki akışı konsola sırasıyla gelmedi"


def test_a_carriage_return_stays_a_carriage_return(console, capsys):
    """curl redraws its progress line with a carriage return, and Colab redraws it in place. Turned
    into a line break, a two-hour download prints a new line every second."""
    console.run(_python(PROGRESS), "ilerleme")

    assert "10%\r50%\r100%\n" in capsys.readouterr().out, \
        "Satırbaşı konsola satırbaşı olarak gelmedi"


def test_a_failed_command_says_its_own_last_lines(console):
    """NOTEBOOK-STANDARD, section 2: the error is the command's own words, never a guessed cause. The
    lines before the last few are on the console already."""
    with pytest.raises(RuntimeError) as failure:
        console.run(_python("import sys\nfor n in range(1, 9): print(f'line {n}')\nsys.exit(2)"),
                    "başarısız")

    message = str(failure.value)
    assert "başarısız" in message and "exit 2" in message, \
        f"Hata komutu ve çıkış kodunu söylemiyor: {message}"
    assert "line 8" in message and "line 1" not in message, \
        f"Hata komutun son satırlarını söylemiyor: {message}"


def test_a_log_s_tail_is_its_last_lines_under_its_name(console, tmp_path):
    """Where a server that did not come up says why: the last lines of its own log."""
    path = tmp_path / "server.log"
    path.write_text("".join(f"satır {n}\n" for n in range(1, 41)), encoding="utf-8")

    tail = console.log_tail(str(path))

    assert tail == f"--- {path} · son 30 satır ---\n" + "\n".join(f"satır {n}" for n in range(11, 41))


def test_a_command_past_its_time_is_stopped(console):
    """A hung command stops the run at its deadline instead of holding the cell for good."""
    start = time.monotonic()
    with pytest.raises(RuntimeError) as failure:
        console.run(_python("import time\ntime.sleep(60)"), "uyuyan", timeout=1)

    assert "uyuyan" in str(failure.value) and "timeout" in str(failure.value), \
        f"Hata komutu ve süreyi söylemiyor: {failure.value}"
    assert time.monotonic() - start < 30, "Süresi dolan komut durdurulmadı, bitmesi beklendi"
