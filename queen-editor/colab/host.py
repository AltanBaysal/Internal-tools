"""Queen Editor — Colab host helpers.

The thin host.ipynb imports this module and calls these functions, so build/tunnel
logs and the public URL stream live into the notebook cell. All the real work lives
here (repo = how-to); the notebook is just the caller (Colab = run + watch).

Usage from the notebook (after clone):
    import sys; sys.path.insert(0, f"{DEST}/queen-editor/colab")
    import host
    host.ensure_cloudflared(); host.build()   # setup cell (finishes)
    host.serve_with_tunnel()                   # run cell (stays alive, streams logs + URL)
"""

import http.server
import shutil
import socket
import subprocess
import threading
import time
from functools import partial
from pathlib import Path

# === Paths (resolved from this file, not the cwd) ===
QE = Path(__file__).resolve().parents[1]      # queen-editor/
FRONTEND = QE / "frontend"
DIST = FRONTEND / "dist"
PORT = 8080


def run(cmd, cwd=None, timeout=900):
    """Run a command; non-zero exit or timeout -> RuntimeError with output tail (fail-loud)."""
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"❌ {' '.join(cmd)}: timeout ({timeout}s)")
    if r.returncode != 0:
        raise RuntimeError(f"❌ {' '.join(cmd)}:\n" + (r.stderr or r.stdout)[-1500:])
    return r.stdout


def ensure_cloudflared():
    """Install cloudflared once (idempotent)."""
    if shutil.which("cloudflared"):
        print("✅ cloudflared zaten kurulu")
        return
    print("⏳ cloudflared kuruluyor...")
    deb = "/tmp/cloudflared.deb"
    run(["wget", "-qO", deb, "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"])
    run(["dpkg", "-i", deb])
    print("✅ cloudflared hazır")


def build(force=False):
    """Build the frontend if dist/ is missing (or force=True). Reuses committed package-lock.json."""
    if (DIST / "index.html").exists() and not force:
        print(f"✅ Build zaten var: {DIST}")
        return
    print("⏳ npm ci...")
    run(["npm", "ci"], cwd=str(FRONTEND))
    print("⏳ npm run build...")
    run(["npm", "run", "build"], cwd=str(FRONTEND))
    if not (DIST / "index.html").exists():
        raise RuntimeError("❌ Build çıktısı yok (dist/index.html)")
    print(f"✅ Build hazır: {DIST}")


def _tunnel_thread(port):
    """Wait for the local server, open a cloudflared tunnel, and stream its logs live.
    Mirrors comfyui_colab.ipynb but prints every line so the tunnel is observable."""
    while True:
        time.sleep(0.5)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                break
    print("\n⏳ cloudflared tüneli açılıyor...\n")
    p = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", f"http://127.0.0.1:{port}"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    for raw in p.stdout:
        line = raw.decode(errors="ignore").rstrip()
        print(line, flush=True)                      # stream raw cloudflared logs to the cell
        if "trycloudflare.com" in line and "https" in line:
            url = line[line.find("https"):].split()[0]
            print("\n" + "=" * 60 + f"\n🌐 Queen Editor: {url}\n" + "=" * 60 + "\n", flush=True)


def serve_with_tunnel(port=PORT):
    """Open the cloudflared tunnel (background) and serve dist/ in the foreground.
    Blocks — keep this cell running to keep the tunnel alive."""
    if not (DIST / "index.html").exists():
        raise RuntimeError("❌ dist/ yok — önce build() çağır")
    threading.Thread(target=_tunnel_thread, args=(port,), daemon=True).start()
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"▶ Statik sunucu: http://127.0.0.1:{port}  (dist: {DIST})")
    httpd.serve_forever()


if __name__ == "__main__":
    # Fallback: `!python host.py` does everything in one process.
    ensure_cloudflared()
    build()
    serve_with_tunnel()
