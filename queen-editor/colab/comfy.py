"""ComfyUI's start for the notebook: the old one stopped, the new one started, and hazır said only for
the process this call started, once it answers (madde 433).

This was the ComfyUI cell's own code, where no test could run it. It looked at the port and never at
its process, so an old ComfyUI still on the port could answer for a new one that had already ended.
"""
import socket
import subprocess
import time
import urllib.request
from collections import deque

from colab.console import log

# The 90 seconds the cell has always given ComfyUI to start, in looks two seconds apart.
LOOKS = 45
STEP = 2
# Seconds an old ComfyUI is given to let go of the port, after each of the two signals.
FREE = 30
LOG_LINES = 30


def start_comfy(root, port, log_path):
    """Start ComfyUI from `root` on `port`, its output in `log_path`, and return the process once
    ComfyUI answers. Fails loud -- with the exit code or what the port said, and the tail of
    ComfyUI's own log -- when it ends or does not answer in time."""
    _free(port)
    # Binary: only ComfyUI writes into it, through the descriptor it inherits.
    with open(log_path, "wb") as out:
        process = subprocess.Popen(
            ["python", "main.py", "--listen", "127.0.0.1", "--port", str(port)],
            cwd=root, stdout=out, stderr=subprocess.STDOUT)
    log(f"ComfyUI başlatıldı (PID {process.pid}), log: {log_path}")
    said = None
    for look in range(1, LOOKS + 1):
        time.sleep(STEP)
        said = _asked(f"http://127.0.0.1:{port}/system_stats")
        # Asked after the look, so an answer counts only while this process is alive: the port was
        # free when it started, and nothing but it can be what answered.
        if process.poll() is not None:
            raise RuntimeError(f"❌ ComfyUI kapandı — exit {process.returncode}\n{_tail(log_path)}")
        if said is None:
            log(f"ComfyUI hazır ({look * STEP}s)", "OK")
            return process
    raise RuntimeError(f"❌ ComfyUI {LOOKS * STEP} sn içinde cevap vermedi\n{said}\n{_tail(log_path)}")


def _free(port):
    """The ComfyUI an earlier run started is stopped and waited for until the port refuses: while it
    holds the port it is what answers there, and the new one cannot take it. Asked to end, then
    killed; a port still taken after both stops the cell before anything starts."""
    for signal in ("TERM", "KILL"):
        subprocess.run(["pkill", f"-{signal}", "-f", "python main.py"], check=False)
        for _ in range(FREE):
            if _refused(port):
                return
            time.sleep(1)
    raise RuntimeError(f"❌ {port} portu {2 * FREE} sn sonra hâlâ bağlantı kabul ediyor — yeni "
                       "ComfyUI bu portu alamaz")


def _refused(port):
    """Whether the port turns a connection away. Only a refusal is free: a socket that is still open
    -- a dying process's too -- is accepted by the kernel, and a look that times out proves
    nothing."""
    try:
        socket.create_connection(("127.0.0.1", port), timeout=1).close()
    except ConnectionRefusedError:
        return True
    except OSError:
        return False
    return False


def _asked(url):
    """None when ComfyUI answers at `url`, otherwise what the look raised, as `Type: message`."""
    try:
        with urllib.request.urlopen(url, timeout=2):
            return None
    except Exception as e:
        return f"{type(e).__name__}: {e}"


def _tail(path):
    """The last lines of ComfyUI's own log, the one place that says why it ended."""
    with open(path, encoding="utf-8", errors="replace") as handle:
        tail = deque(handle, maxlen=LOG_LINES)
    return f"--- {path} · son {LOG_LINES} satır ---\n" + "".join(tail).rstrip("\n")
