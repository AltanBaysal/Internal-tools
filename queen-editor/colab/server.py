"""Queen Editor's server for the notebook: Flask started and waited for, the cloudflared tunnel that
reaches it, its link, and its live log (madde 438).

This was the notebook's last cell, where no test could run it. What the app is told -- the QE_*
settings -- stays in the cell: they name CONFIG's values and what the boxes chose.
"""
import os
import re
import subprocess
import time

from colab.console import log_tail, run
from colab.wait import wait_for

CLOUDFLARED = "/content/cloudflared"
CLOUDFLARED_URL = ("https://github.com/cloudflare/cloudflared/releases/latest/download/"
                   "cloudflared-linux-amd64")
TUNNEL_LOG = "/content/cloudflared.log"
# Seconds, one look each, for cloudflared to print its link.
TUNNEL_LOOKS = 30
LINK = re.compile(r"https://[-\w.]+trycloudflare\.com")


def serve(app_dir, port, log_path, settings):
    """The server an earlier run left, and its tunnel, stopped; Flask started from app_dir with
    `settings` in its environment and its output in log_path; and once it answers, a tunnel opened to
    it. Returns the tunnel's link. Fails loud, with the log that says why, when either does not come
    up in time."""
    subprocess.run(["pkill", "-f", "backend.main"], check=False)
    subprocess.run(["pkill", "-f", "cloudflared"], check=False)
    time.sleep(2)
    _start_flask(app_dir, port, log_path, settings)
    return _open_tunnel(port)


def _start_flask(app_dir, port, log_path, settings):
    # Binary, both logs: only the process writes into it, through the descriptor it inherits.
    with open(log_path, "wb") as out:
        subprocess.Popen(["python", "-m", "backend.main"], cwd=app_dir,
                         env={**os.environ, **settings}, stdout=out, stderr=subprocess.STDOUT)
    took = wait_for(f"http://127.0.0.1:{port}/api/health", "Flask", log_path)
    print(f"✓ Flask ayakta ({took}s)")


def _open_tunnel(port):
    """Over http2, not cloudflared's default QUIC: QUIC rides on UDP, which Colab's network throttles.
    On 2026-08-24 the same photo took 17.74 s over the default tunnel and 0.18 s over this one.

    cloudflared writes into its log, not onto the console, so a tunnel without a link stops the cell
    with the end of that log."""
    if not os.path.isfile(CLOUDFLARED):
        # -nv rather than -q: no progress, but wget's error is still said.
        run(["wget", "-nv", "-O", CLOUDFLARED, CLOUDFLARED_URL], "wget cloudflared")
        os.chmod(CLOUDFLARED, 0o755)
    with open(TUNNEL_LOG, "wb") as out:
        subprocess.Popen([CLOUDFLARED, "tunnel", "--protocol", "http2",
                          "--url", f"http://127.0.0.1:{port}"],
                         stdout=out, stderr=subprocess.STDOUT)
    for _ in range(TUNNEL_LOOKS):
        time.sleep(1)
        found = LINK.search(_read(TUNNEL_LOG))
        if found:
            return found.group(0)
    raise RuntimeError(f"❌ cloudflared linki {TUNNEL_LOOKS} sn içinde alınamadı\n"
                       f"{log_tail(TUNNEL_LOG)}")


def _read(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def show_link(link, took):
    """The link, and above it how long the cell took to reach it (madde 312): the cell never ends, so
    the timer's own line never comes."""
    print(f"✓ Link {took}'de hazır")
    print(f"\n🔗 Queen Editor: {link}\n")
    print("⬆️  Linke gir → projeye tıkla → prompt yaz → Üret.\n")


def follow(log_path):
    """The server's live log, from its first line, for as long as the cell runs. Stopping the cell
    stops the tail, never the server."""
    print("📡 Sunucu çalışıyor — BU HÜCREYİ KAPATMA. Canlı log:\n")
    try:
        subprocess.run(["tail", "-n", "+1", "-f", log_path])
    except KeyboardInterrupt:
        print("Hücre durduruldu — Flask hâlâ arka planda (yeni link için tekrar çalıştır).")
