"""Queen Editor's server and its tunnel, run rather than read (madde 438).

This was the notebook's last cell, where no test could run it. The machine under it is faked here --
pkill, the two processes, the health check, wget, tail and the clock -- and the logs are real files,
which the fake processes write into the way Flask and cloudflared do.
"""
import importlib
import io
import os
import subprocess
import urllib.error
from types import SimpleNamespace

import pytest

LINK = "https://queen-bee-test.trycloudflare.com"
REFUSED = urllib.error.URLError(ConnectionRefusedError(111, "Connection refused"))
FLASK_LOG = "".join(f"flask satırı {n}\n" for n in range(1, 41))
SETTINGS = {"QE_DRIVE_ROOT": "/content/drive/MyDrive/kök", "QE_DEEPSEEK_API_KEY": "sk-test"}


@pytest.fixture
def server(monkeypatch, tmp_path):
    """The module, cloudflared and its log moved into the test's own tmp dir. Imported here rather
    than at the top: a module that is not there yet fails each test on its own instead of the whole
    file."""
    module = importlib.import_module("colab.server")
    monkeypatch.setattr(module, "CLOUDFLARED", str(tmp_path / "cloudflared"))
    monkeypatch.setattr(module, "TUNNEL_LOG", str(tmp_path / "cloudflared.log"))
    return module


class Machine:
    """The machine under the cell. `answers` is what each look at /api/health gets -- True for an
    answer, an exception to raise -- and its last item stands for every later one. `tunnel` is what
    cloudflared writes into its log."""

    def __init__(self, monkeypatch, server, tmp_path, answers=(True,), tunnel=f"INF {LINK}\n",
                 cloudflared=True):
        self.events, self.started, self.slept = [], [], []
        self._answers, self._tunnel = list(answers), tunnel
        if cloudflared:
            (tmp_path / "cloudflared").write_bytes(b"\x7fELF")
        monkeypatch.setattr(server.subprocess, "run", self._run)
        monkeypatch.setattr(server.subprocess, "Popen", self._popen)
        monkeypatch.setattr(server.urllib.request, "urlopen", self._urlopen)
        monkeypatch.setattr(server.time, "sleep", self.slept.append)
        monkeypatch.setattr(server, "run", self._wget)

    def _run(self, cmd, **kwargs):
        self.events.append(" ".join(cmd))
        return SimpleNamespace(returncode=0)

    def _popen(self, cmd, cwd=None, env=None, stdout=None, stderr=None):
        self.events.append("popen " + os.path.basename(cmd[0]))
        self.started.append({"cmd": cmd, "cwd": cwd, "env": env, "stderr": stderr})
        # Bytes, the way a process writes through the descriptor it inherits.
        stdout.write((self._tunnel if "tunnel" in cmd else FLASK_LOG).encode("utf-8"))
        stdout.flush()
        return SimpleNamespace(pid=4242)

    def _urlopen(self, url, timeout=None):
        self.events.append("look " + url)
        answer = self._answers.pop(0) if len(self._answers) > 1 else self._answers[0]
        if isinstance(answer, Exception):
            raise answer
        return io.BytesIO(b'{"ok": true}')

    def _wget(self, cmd, label, cwd=None, timeout=3600):
        self.events.append(" ".join(cmd[:2]))
        with open(cmd[cmd.index("-O") + 1], "wb") as handle:
            handle.write(b"\x7fELF")


def _serve(server, tmp_path):
    return server.serve("/content/Internal-tools/queen-editor", 8000, str(tmp_path / "flask.log"),
                        SETTINGS)


def _failure(server, tmp_path):
    with pytest.raises(RuntimeError) as exc:
        _serve(server, tmp_path)
    return str(exc.value)


def test_the_old_server_and_tunnel_go_before_flask_starts(server, monkeypatch, tmp_path):
    machine = Machine(monkeypatch, server, tmp_path)

    _serve(server, tmp_path)

    assert machine.events[:3] == ["pkill -f backend.main", "pkill -f cloudflared", "popen python"]
    assert machine.slept[0] == 2


def test_flask_starts_from_the_app_with_the_notebook_s_settings(server, monkeypatch, tmp_path):
    """The settings are how the app learns what the notebook chose and where things are; the rest of
    the environment comes along, PATH included."""
    machine = Machine(monkeypatch, server, tmp_path)

    _serve(server, tmp_path)

    flask = machine.started[0]
    assert flask["cmd"] == ["python", "-m", "backend.main"]
    assert flask["cwd"] == "/content/Internal-tools/queen-editor"
    assert flask["env"] == {**os.environ, **SETTINGS}, \
        "Flask'ın ortamı notebook'un ayarlarını taşımıyor"
    assert flask["stderr"] == subprocess.STDOUT
    assert (tmp_path / "flask.log").read_text(encoding="utf-8") == FLASK_LOG


def test_flask_is_up_once_its_health_answers(server, monkeypatch, tmp_path, capsys):
    machine = Machine(monkeypatch, server, tmp_path, answers=[REFUSED, REFUSED, True])

    _serve(server, tmp_path)

    looks = [event for event in machine.events if event.startswith("look")]
    assert looks == ["look http://127.0.0.1:8000/api/health"] * 3
    assert "✓ Flask ayakta (6s)" in capsys.readouterr().out


def test_the_tunnel_is_opened_over_tcp_rather_than_quic_and_hands_back_its_link(
        server, monkeypatch, tmp_path):
    """cloudflared speaks QUIC by default, and QUIC rides on UDP. Colab's network throttles UDP and
    leaves TCP alone: on 2026-08-24 the same photo took 17.74 s over the default tunnel and 0.18 s
    over one started with this flag -- same machine, same minute, ninety times apart."""
    machine = Machine(monkeypatch, server, tmp_path)

    link = _serve(server, tmp_path)

    assert machine.started[1]["cmd"] == [str(tmp_path / "cloudflared"), "tunnel", "--protocol",
                                         "http2", "--url", "http://127.0.0.1:8000"]
    assert link == LINK


def test_cloudflared_is_fetched_only_when_it_is_not_there(server, monkeypatch, tmp_path):
    machine = Machine(monkeypatch, server, tmp_path, cloudflared=False)
    made = []
    monkeypatch.setattr(server.os, "chmod", lambda path, mode: made.append((path, mode)))

    _serve(server, tmp_path)
    _serve(server, tmp_path)

    assert machine.events.count("wget -q") == 1, f"cloudflared böyle indirildi: {machine.events}"
    assert machine.events.index("wget -q") < machine.events.index("popen cloudflared")
    assert made == [(str(tmp_path / "cloudflared"), 0o755)], \
        f"cloudflared çalıştırılabilir yapılmadı: {made}"


def test_a_flask_that_never_answers_fails_after_ninety_seconds_with_its_log(server, monkeypatch,
                                                                            tmp_path, capsys):
    machine = Machine(monkeypatch, server, tmp_path, answers=[REFUSED])

    said = _failure(server, tmp_path)

    assert machine.slept[1:] == [2] * 45
    assert said == "❌ Flask 90 sn içinde /api/health'e cevap vermedi — yukarıdaki log'a bak"
    out = capsys.readouterr().out
    assert "flask satırı 11\n" in out and "flask satırı 40" in out and "flask satırı 10\n" not in out
    assert "popen cloudflared" not in machine.events, "Flask açılmadan tünel açıldı"


def test_a_tunnel_without_a_link_fails_after_thirty_seconds_with_its_log(server, monkeypatch,
                                                                         tmp_path, capsys):
    machine = Machine(monkeypatch, server, tmp_path, tunnel="x" * 1500 + "ERR failed to connect\n")

    said = _failure(server, tmp_path)

    assert machine.slept[-30:] == [1] * 30
    assert said == "❌ cloudflared linki 30 sn içinde alınamadı"
    out = capsys.readouterr().out
    assert out.rstrip().endswith("ERR failed to connect") and "x" * 1000 not in out, \
        f"Tünelin log'unun sonu basılmadı:\n{out[-200:]}"


def test_the_link_says_how_long_it_took_right_above_it(server, capsys):
    """The line reads "Link 14 sn'de hazır", right above the link (madde 312)."""
    server.show_link(LINK, "14 sn")

    lines = [line for line in capsys.readouterr().out.splitlines() if line]
    assert lines[:2] == ["✓ Link 14 sn'de hazır", f"🔗 Queen Editor: {LINK}"], f"Satırlar: {lines}"
    assert lines[2].startswith("⬆️  Linke gir")


def test_the_live_log_is_followed_from_its_first_line(server, monkeypatch, capsys):
    asked = []
    monkeypatch.setattr(server.subprocess, "run", lambda cmd, **kwargs: asked.append(cmd))

    server.follow("/content/flask.log")

    assert asked == [["tail", "-n", "+1", "-f", "/content/flask.log"]]
    assert "📡 Sunucu çalışıyor — BU HÜCREYİ KAPATMA. Canlı log:" in capsys.readouterr().out


def test_stopping_the_cell_says_flask_is_still_running(server, monkeypatch, capsys):
    def tail(cmd, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(server.subprocess, "run", tail)

    server.follow("/content/flask.log")

    assert capsys.readouterr().out.rstrip().endswith(
        "Hücre durduruldu — Flask hâlâ arka planda (yeni link için tekrar çalıştır).")
