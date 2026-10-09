"""The machine's own packages, run rather than read (madde 438).

apt-get is faked here; what is asked of it and what it said are real.
"""
import importlib
import subprocess
from types import SimpleNamespace

import pytest


@pytest.fixture
def system():
    """The module. Imported here rather than at the top: a module that is not there yet fails each
    test on its own instead of the whole file."""
    return importlib.import_module("colab.system")


def _apt(monkeypatch, system, fails=None, said=""):
    """apt-get, faked: every call remembered with how it was asked for. The call whose subcommand is
    `fails` exits 100 having written `said`."""
    calls = []

    def run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        if cmd[1] == fails:
            return SimpleNamespace(returncode=100, stdout=said)
        return SimpleNamespace(returncode=0, stdout="Reading package lists...\n" * 200)

    monkeypatch.setattr(system.subprocess, "run", run)
    return calls


def test_the_lists_are_refreshed_then_the_packages_installed_off_the_console(system, monkeypatch,
                                                                             capsys):
    """apt-get writes hundreds of lines on a good day, and none of them reaches the console. A
    runtime's lists can be older than the archive, so they are refreshed first."""
    calls = _apt(monkeypatch, system)

    system.apt_install("aria2", "ffmpeg")

    assert [cmd for cmd, _ in calls] == [["apt-get", "update", "-qq"],
                                         ["apt-get", "install", "-y", "aria2", "ffmpeg"]], \
        f"apt-get böyle çağrılmadı: {calls}"
    for _, kwargs in calls:
        assert kwargs.get("stdout") == subprocess.PIPE and kwargs.get("stderr") == subprocess.STDOUT, \
            f"apt-get'in çıktısı konsola gidiyor ya da iki akış birleşmiyor: {kwargs}"
    assert capsys.readouterr().out == "", "Başarılı apt-get konsola bir şey bastı"


@pytest.mark.parametrize("step, command", [("update", "apt-get update -qq"),
                                           ("install", "apt-get install -y aria2 ffmpeg")])
def test_a_failed_step_stops_the_cell_with_all_apt_said(system, monkeypatch, step, command):
    """A missing ffmpeg would otherwise show up hours later, in an export. apt's output is not on the
    console, so the error carries all of it, as apt wrote it (madde 439)."""
    said = "".join(f"satır {n}\n" for n in range(1, 9)) + "E: Unable to locate package ffmpeg\n"
    calls = _apt(monkeypatch, system, fails=step, said=said)

    with pytest.raises(RuntimeError) as failure:
        system.apt_install("aria2", "ffmpeg")

    message = str(failure.value)
    assert message == f"{command}: exit 100\n{said}", f"Hata apt-get'in bütün çıktısı değil: {message}"
    assert calls[-1][0][1] == step, "Düşen adımdan sonra apt-get yine çağrıldı"
