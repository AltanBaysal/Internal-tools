"""Custom node installs for the notebook: each node cloned into ComfyUI's custom_nodes, from the
branch BRANCHES names or else its default one, and its own requirements installed, save the lines in
SKIPPED.

The list of nodes stays in the notebook, where it is counted against the heading over it; what is here
is how the nodes come in, which a cell could not test (madde 314, and the loop over the list since
madde 438).
"""
import os

from colab.console import log, run

# Impact-Pack's list ends with sam2 straight from GitHub. It has no ready package: pip builds it on the
# machine, and its build asks for torch, which pip installs again -- CUDA libraries and all -- in a
# build environment of its own. Impact-Pack took 3 dk 13 sn of a 6 dk 2 sn cell on the user's run. Our
# photo graph loads SAM's first version through segment-anything, and Impact-Pack imports sam2 only
# when it is installed.
SKIPPED = {"git+https://github.com/facebookresearch/sam2"}

# The branch a node is cloned from when its default branch is not the code we run, by clone address.
# On 2026-10-15 rgthree made `dev` its default branch: a tree of 2023 without Power Lora Loader,
# whose patch of ComfyUI's execution module fails the import. Its current code is on `main`
# (madde 470).
BRANCHES = {"https://github.com/rgthree/rgthree-comfy.git": "main"}


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


def install_nodes(nodes, folder):
    """The notebook's (name, url) list into folder, in its order, and a line counting them."""
    for name, url in nodes:
        install_node(name, url, folder)
    log(f"{len(nodes)} custom node hazır", "OK")


def install_node(name, url, folder):
    """One node into folder/name: cloned shallow with its submodules, from the branch BRANCHES names
    or else its default one, and its requirements installed. A node already there is left alone, so
    a second Run all costs nothing. The line a node starts with carries the time, and the gap to the
    next one is how long the node took."""
    target = os.path.join(folder, name)
    if os.path.exists(target) and os.listdir(target):
        log(f"{name}: zaten var")
        return
    log(f"{name}: cloning...")
    branch = ["--branch", BRANCHES[url]] if url in BRANCHES else []
    run(["git", "clone", "--progress", "--depth", "1", "--recurse-submodules", *branch, url, target],
        f"clone {name}", timeout=180)
    if not os.listdir(target):
        raise RuntimeError(f"{name}: klon sonrası klasör boş")
    req = os.path.join(target, "requirements.txt")
    if os.path.exists(req):
        run(["pip", "install", "--progress-bar", "on", "-r", _kept(req, name)], f"pip install {name}",
            timeout=300)
