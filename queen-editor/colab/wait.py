"""The wait for a server the notebook started on this machine -- ComfyUI, Flask -- to answer
(madde 439).

Both were waited for the same way in their own modules, and Flask's wait swallowed what its looks
got.
"""
import time
import urllib.request

from colab.console import log_tail

# 90 seconds, in looks two seconds apart.
LOOKS = 45
STEP = 2


def wait_for(url, name, log_path, process=None):
    """The seconds it took `url` to answer. A server that does not answer in time stops the cell with
    the address asked, what the last look got and the end of its log at `log_path`.

    With `process`, an answer counts only while it is alive: it is asked after each look, and the
    wait stops as soon as it has ended."""
    said = None
    for look in range(1, LOOKS + 1):
        time.sleep(STEP)
        said = _asked(url)
        if process is not None and process.poll() is not None:
            raise RuntimeError(
                f"❌ {name} kapandı — exit {process.returncode}\n{log_tail(log_path)}")
        if said is None:
            return look * STEP
    raise RuntimeError(
        f"❌ {name} {LOOKS * STEP} sn içinde cevap vermedi — {url}\n{said}\n{log_tail(log_path)}")


def _asked(url):
    """None when something answers at `url`, otherwise what the look raised, as `Type: message`."""
    try:
        with urllib.request.urlopen(url, timeout=2):
            return None
    except Exception as e:
        return f"{type(e).__name__}: {e}"
