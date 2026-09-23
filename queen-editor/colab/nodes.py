"""Custom node installs for the notebook: each node cloned into ComfyUI's custom_nodes and its own
requirements installed, save the lines in SKIPPED.

The list of nodes stays in the notebook, where it is counted against the heading over it; what is here
is how one node comes in, which a cell could not test (madde 314).
"""
import os

from colab.console import log, run

# Impact-Pack's list ends with sam2 straight from GitHub. It has no ready package: pip builds it on the
# machine, and its build asks for torch, which pip installs again -- CUDA libraries and all -- in a
# build environment of its own. Impact-Pack took 3 dk 13 sn of a 6 dk 2 sn cell on the user's run. Our
# photo graph loads SAM's first version through segment-anything, and Impact-Pack imports sam2 only
# when it is installed.
SKIPPED = {"git+https://github.com/facebookresearch/sam2"}


def _kept(req, name):
    """The list pip is handed: the node's own, or a copy of it without the lines in SKIPPED. The copy
    sits beside the original because pip resolves a -r or -c inside a list from where the list is."""
    with open(req, encoding="utf-8") as f:
        lines = f.read().splitlines()
    skipped = [line.strip() for line in lines if line.strip() in SKIPPED]
    if not skipped:
        return req
    for line in skipped:
        log(f"{name}: {line} kurulmuyor — grafiklerimiz kullanmıyor (madde 314)")
    kept = os.path.join(os.path.dirname(req), "requirements.queen-editor.txt")
    with open(kept, "w", encoding="utf-8") as f:
        f.write("".join(f"{line}\n" for line in lines if line.strip() not in SKIPPED))
    return kept


def install_node(name, url, folder):
    """One node into folder/name: cloned shallow with its submodules, and its requirements installed.
    A node already there is left alone, so a second Run all costs nothing. The line a node starts with
    carries the time, and the gap to the next one is how long the node took."""
    target = os.path.join(folder, name)
    if os.path.exists(target) and os.listdir(target):
        log(f"{name}: zaten var")
        return
    log(f"{name}: cloning...")
    run(["git", "clone", "--depth", "1", "--recurse-submodules", url, target], f"clone {name}",
        timeout=180)
    if not os.listdir(target):
        raise RuntimeError(f"{name}: klon sonrası klasör boş")
    req = os.path.join(target, "requirements.txt")
    if os.path.exists(req):
        run(["pip", "install", "-q", "-r", _kept(req, name)], f"pip install {name}", timeout=300)
