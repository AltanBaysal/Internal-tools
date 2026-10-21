"""Which runtime queeneditor.ipynb asks Colab for.

The notebook is read, never run. Colab reads the runtime a notebook wants from its metadata when it
opens the file, so that is the one place this choice lives. Krea 2 Turbo's int8 DiT alone is about
13.5 GB and does not fit a T4 (madde 482), so the notebook opens on an A100 and no cell sends the
user to a T4 (madde 487).

Its own file, because it asks about neither the producers nor the branch the notebook clones.
"""
import json
import os
import re

TOOL = os.path.dirname(          # queen-editor
    os.path.dirname(             # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests
NOTEBOOK = os.path.join(TOOL, "queeneditor.ipynb")


def _notebook():
    with open(NOTEBOOK, encoding="utf-8") as handle:
        return json.load(handle)


def test_the_notebook_asks_colab_for_an_a100():
    metadata = _notebook()["metadata"]

    assert metadata.get("accelerator") == "GPU"
    assert metadata.get("colab", {}).get("gpuType") == "A100"


def test_no_cell_sends_the_user_to_a_t4():
    cells = _notebook()["cells"]
    named = [cell.get("id") for cell in cells if re.search(r"\bT4\b", "".join(cell.get("source", "")))]

    assert named == []
