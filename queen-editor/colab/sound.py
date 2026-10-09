"""The sound engine for the notebook: MMAudio's library and its own weights (madde 438).

Sound runs inside the app's process rather than through ComfyUI (FOUNDATION 6), so the library has to
be importable there and its weights where the app will look. Not named mmaudio.py: that is MMAudio's
own package, which this module imports.
"""
import os
import sys

from colab.console import log, run

REPO = "https://github.com/hkchengrex/MMAudio.git"


def install_mmaudio(folder):
    """MMAudio cloned into `folder` when it is not there, and installed editable. A line as each stage
    starts says which one the cell is in (madde 398), and pip is not silenced: the install can take
    thirty minutes."""
    if not os.path.isdir(folder):
        log("MMAudio klonlanıyor…")
        run(["git", "clone", "--progress", "--depth", "1", REPO, folder], "clone MMAudio",
            timeout=300)
    log("MMAudio kuruluyor…")
    run(["pip", "install", "--progress-bar", "on", "-e", "."], "pip install MMAudio", cwd=folder,
        timeout=1800)
    log("MMAudio kütüphanesi kuruldu", "OK")


def fetch_mmaudio_weights(folder, app_dir):
    """MMAudio's base weights, ahead of the first sound job, which would otherwise stall on them.

    MMAudio resolves ./weights and ./ext_weights against the working directory, and the app is started
    from app_dir, so they come down there and the working directory is put back after. The clone goes
    on sys.path: `pip install -e .` registers it with a .pth file, which only a new process reads, and
    the kernel started long before."""
    if not os.path.isdir(app_dir):
        raise RuntimeError(f"❌ Uygulama klasörü yok: {app_dir} — önce klon hücresini çalıştır")
    if folder not in sys.path:
        sys.path.insert(0, folder)
    before = os.getcwd()
    os.chdir(app_dir)
    try:
        from mmaudio.eval_utils import all_model_cfg
        all_model_cfg["large_44k"].download_if_needed()
    finally:
        os.chdir(before)
    log(f"MMAudio ağırlıkları hazır → {app_dir}", "OK")
