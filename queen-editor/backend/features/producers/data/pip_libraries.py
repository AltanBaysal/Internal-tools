"""git + pip: the notebook's own way of installing MMAudio, moved into the app.

No tests, like the ComfyUI client and the ffmpeg exporter -- a fake subprocess would only be testing
the fake. Everything decidable above it (the order, what is skipped, where it stops, what the screen
says) is domain, and is covered there.

The method is copied rather than improved: shallow clone, `pip install -e .`, then import it in a
separate process to prove the install. `-e` is why the clone folder is named at all -- the package
stays where it was cloned, so updating it is a `git pull`.
"""
import importlib.util
import os
import subprocess
import sys


class PipLibraries:
    def __init__(self, root):
        self._root = root

    def present(self, module):
        # No invalidate_caches() here: the panel asks this on every poll, and dropping the import
        # system's caches that often taxes every later import. The install does it once, at the one
        # moment the answer can have changed.
        return importlib.util.find_spec(module) is not None

    def install(self, repo, folder, module):
        path = os.path.join(self._root, folder)
        if not os.path.isdir(path) or not os.listdir(path):
            _run(["git", "clone", "--depth", "1", repo, path], timeout=180)
        _run([sys.executable, "-m", "pip", "install", "-q", "-e", "."], cwd=path, timeout=900)
        # A package written after this process started stays invisible until the finders drop the
        # directory listings they cached.
        importlib.invalidate_caches()
        # The notebook's fail-loud import, kept: a broken dependency says so here, in the tool's own
        # words, rather than forty minutes later inside a render. Its own process, so a half-loaded
        # module cannot poison this one.
        _run([sys.executable, "-c", f"import {module}"], timeout=600)


def _run(cmd, cwd=None, timeout=900):
    """Run it; a non-zero exit or a timeout raises with the command's own last lines. The message
    reaches the panel, so it carries what really happened rather than a guess at it."""
    try:
        done = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"{' '.join(cmd)}: timeout ({timeout}s)")
    if done.returncode != 0:
        tail = "\n".join((done.stderr or done.stdout or "").strip().splitlines()[-5:])
        raise RuntimeError(f"{' '.join(cmd)}: exit {done.returncode}\n{tail}")
