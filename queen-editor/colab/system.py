"""The machine's own packages, from apt (madde 438).

aria2 and ffmpeg: one for the downloads, the other for the app's export and ComfyUI's video nodes,
so neither belongs to the ComfyUI module.
"""
import subprocess


def apt_install(*packages):
    """The package lists refreshed, then the packages installed. apt-get's own output stays off the
    console: hundreds of lines, and none of them is read on a good day. A failure stops the cell with
    all of it, as apt wrote it: none of it is on the console yet (madde 439).

    The refresh comes first because a runtime's lists can be older than the archive they point at,
    and then the install asks for files that are gone."""
    _apt(["apt-get", "update", "-qq"])
    _apt(["apt-get", "install", "-y", *packages])


def _apt(cmd):
    # stderr joins stdout, as in console.run: apt's errors stay where it wrote them among its lines.
    done = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if done.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)}: exit {done.returncode}\n{done.stdout}")
