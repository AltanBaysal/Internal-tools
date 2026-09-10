"""Which branch queeneditor.ipynb clones.

The notebook is read, never run: a Colab cell cannot execute here. What text can answer is the one
thing the notebook alone decides -- where the code it serves comes from. Get that wrong and nothing
else in this suite notices: the app would be the right app, built from the wrong tree.

Its own file rather than the producer-group one next door, because it asks about neither the
producers nor the install -- and that file's name would become a promise it does not keep.

queen-agent carries the same guard (queen-agent/backend/tests/test_notebook.py); this is its other
half, and it exists because on 2026-09-11 main's notebook was still cloning feat/v6 long after that
work landed, with nothing here failing in between.
"""
import json
import os

TOOL = os.path.dirname(          # queen-editor
    os.path.dirname(             # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests
NOTEBOOK = os.path.join(TOOL, "queeneditor.ipynb")

# Released work lives on main, and a notebook handed to somebody else clones what is released. The
# exception is a run being tried out: its trials happen in Colab, Colab clones from GitHub, and a
# branch that is not named here cannot be reached at all.
#
# The name is written down in exactly two places, this constant and the notebook, and the test below
# fails the moment they part.
#
# BEFORE MERGING: this goes back to "main", and so does the notebook. A trial changes this line and
# the notebook's together and never one of them, and the change comes back the way it went in.
BRANCH = "main"


def _source():
    """Every cell's source as one blob.

    Parsed rather than read raw: the file is JSON, so a raw read would be searching escaped quotes
    and line breaks instead of the code the cell runs. Both questions below are about what the
    notebook says and not about which cell says it, so one blob is the whole helper needed.
    """
    with open(NOTEBOOK, encoding="utf-8") as handle:
        doc = json.load(handle)
    return "\n".join("".join(cell.get("source", "")) for cell in doc.get("cells", []))


def test_the_notebook_clones_the_branch_this_tool_is_served_from():
    assert f'BRANCH       = "{BRANCH}"' in _source(), (
        f"Defter {BRANCH} dalından klonlamıyor — CONFIG hücresindeki BRANCH satırı"
    )


def test_no_other_branch_name_is_left_lying_in_the_notebook():
    """One name, in one place: a second branch named anywhere in the notebook is a cell that clones
    one thing and a comment promising another."""
    named = {word.strip("\"',") for word in _source().split() if word.strip("\"',").startswith("feat/")}

    assert named <= {BRANCH}, f"Defterde başka bir dal adı var: {named - {BRANCH}}"
