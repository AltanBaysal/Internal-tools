"""What every notebook cell prints and runs with.

The notebook imports these from its clone (madde 310). They were cells before, and a cell never runs
under pytest.
"""
import collections
import io
import os
import subprocess
import threading
import time


# The lines of a failed command its error carries: the ones before them are on the console already.
TAIL = 5
# The lines of a server's log the error carries when the server does not come up: the log is not on
# the console.
LOG_LINES = 30


def log(msg, level="INFO"):
    icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERR": "❌"}
    print(f"{icons.get(level, '·')} [{time.strftime('%H:%M:%S')}] {msg}")


def human(b):
    for u in ["B", "KB", "MB", "GB"]:
        if b < 1024:
            return f"{b:.1f}{u}"
        b /= 1024
    return f"{b:.1f}TB"


def head_text(path, limit=4000):
    """The start of a file as text: how a failed download shows what actually came down -- an error
    page, more often than not."""
    if not os.path.exists(path):
        return "(dosya yok)"
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        text = f.read(limit).decode("utf-8", errors="replace")
    return text + (f"\n… (+{human(size - limit)})" if size > limit else "")


def log_tail(path):
    """The last lines of a server's own log under its name, the one place that says why it did not
    come up."""
    with open(path, encoding="utf-8", errors="replace") as handle:
        tail = collections.deque(handle, maxlen=LOG_LINES)
    return f"--- {path} · son {LOG_LINES} satır ---\n" + "".join(tail).rstrip("\n")


def run(cmd, label, cwd=None, timeout=3600):
    """A shell call whose output reaches the cell as it comes, and that fails loud with the command's
    own last lines rather than a guessed cause.

    stderr joins stdout, so the two keep the order they were written in: git, pip and curl put their
    progress and their errors on stderr, and where a command hangs is read from that order. pip is a
    Python program, and into a pipe Python holds its lines until it ends; PYTHONUNBUFFERED makes it
    hand each one over as it is written. However this is left -- past the deadline, or the cell
    stopped by the user -- kill leaves nothing running behind the cell; a command that has ended is
    not signalled.

    Seeing no terminal, git and pip draw no progress of their own, so the calls ask for it:
    `git clone --progress` and `pip install --progress-bar on`. pip goes without -q, which hides the
    lines saying which package it is on (madde 439).

    The reader is waited for only when the command ended by itself. A killed pip can leave a child
    of its own holding the pipe, and waiting for that pipe to close would turn a timeout, or a
    stopped cell, into a cell that never returns.
    """
    proc = subprocess.Popen(cmd, shell=isinstance(cmd, str), cwd=cwd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, env={**os.environ, "PYTHONUNBUFFERED": "1"})
    tail = collections.deque(maxlen=TAIL)
    echo = threading.Thread(target=_echo, args=(proc.stdout, tail), daemon=True)
    echo.start()
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"{label}: timeout ({timeout}s)") from None
    finally:
        proc.kill()
        proc.wait()
    echo.join()
    if proc.returncode != 0:
        raise RuntimeError(f"{label}: exit {proc.returncode}\n" + "\n".join(tail))


def _echo(pipe, tail):
    """The command's output onto the cell piece by piece as it comes, its last lines kept for an error.

    newline="" leaves a carriage return as it came, so curl's progress line is redrawn in place rather
    than printed anew every second. errors="replace" shows a byte the locale cannot read as a
    replacement mark: raised, it would end this reader, the pipe would fill, and the command would sit
    blocked until its deadline.
    """
    for piece in io.TextIOWrapper(pipe, newline="", errors="replace"):
        print(piece, end="", flush=True)
        if piece.strip():
            tail.append(piece.rstrip())
