"""What every notebook cell prints and runs with.

The notebook imports these from its clone (madde 310). They were cells before, and a cell never runs
under pytest.
"""
import os
import subprocess
import time


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


def run(cmd, label, cwd=None, timeout=3600):
    """A shell call that fails loud, with the command's own last lines rather than a guessed cause."""
    try:
        r = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"{label}: timeout ({timeout}s)")
    if r.returncode != 0:
        tail = "\n".join((r.stderr or r.stdout or "").strip().splitlines()[-5:])
        raise RuntimeError(f"{label}: exit {r.returncode}\n{tail}")
    return r.stdout
