"""The machine's own packages, from apt (madde 438).

aria2 and ffmpeg: one for the downloads, the other for the app's export and ComfyUI's video nodes,
so neither belongs to the ComfyUI module.
"""
import subprocess

from colab.console import TAIL


def apt_install(*packages):
    """The package lists refreshed, then the packages installed. apt-get's own output stays off the
    console: hundreds of lines, and none of them is read on a good day. A failure stops the cell with
    apt's own last lines.

    The refresh comes first because a runtime's lists can be older than the archive they point at,
    and then the install asks for files that are gone."""
    _apt(["apt-get", "update", "-qq"])
    _apt(["apt-get", "install", "-y", *packages])


def _apt(cmd):
    # stderr joins stdout, as in console.run: the error comes last, where the tail is taken.
    done = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if done.returncode != 0:
        tail = "\n".join((done.stdout or "").strip().splitlines()[-TAIL:])
        raise RuntimeError(f"{' '.join(cmd)}: exit {done.returncode}\n{tail}")
