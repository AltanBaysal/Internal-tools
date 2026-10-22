"""Where queeneditor.ipynb puts the exports: a root of their own beside the projects' (madde 494).

The notebook is read, never run. The server never opens a root -- a mount that dropped would have
it opened on the machine's own disk (madde 472) -- so the notebook opens both, right after the
mount, and hands each over. An exports' root nobody opened is an export that fails on Colab, and the
config's fallback would hide a root nobody handed over.

Its own file, because it asks about neither the producers nor the branch the notebook clones.
"""
import json
import os
import re

TOOL = os.path.dirname(          # queen-editor
    os.path.dirname(             # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests
NOTEBOOK = os.path.join(TOOL, "queeneditor.ipynb")


def _cell(marker):
    with open(NOTEBOOK, encoding="utf-8") as handle:
        cells = json.load(handle)["cells"]
    sources = ["".join(cell.get("source", "")) for cell in cells]
    return next(source for source in sources if marker in source)


def test_config_names_the_exports_folder():
    """Named in CONFIG beside the projects' folder, where renaming either is one line."""
    assert re.search(r'^EXPORT_FOLDER\s*= "\w+"$', _cell("# === CONFIG ==="), re.M)


def test_the_mount_cell_opens_the_exports_root():
    mount = _cell("drive.mount(")

    assert 'EXPORT_ROOT = f"/content/drive/MyDrive/{EXPORT_FOLDER}"' in mount
    assert "os.makedirs(EXPORT_ROOT, exist_ok=True)" in mount


def test_the_server_is_handed_the_exports_root():
    assert '"QE_EXPORT_ROOT": EXPORT_ROOT' in _cell("serve(APP_DIR")
