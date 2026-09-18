"""The notebook has to stay small enough for the tools that edit it to read it in one go.

The Read tool takes 25,000 tokens, and at 25,071 nothing could touch the notebook any more
(madde 238). Tokens are not countable here, so the characters of every cell's source stand in for
them: the notebook held 48,527 when it sat at the limit, and the ceiling is 60% of that -- about
15,000 tokens, well under it. Raising the number is a decision, never something that happens by
itself.
"""
import json
import os

TOOL = os.path.dirname(          # queen-editor
    os.path.dirname(             # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests
NOTEBOOK = os.path.join(TOOL, "queeneditor.ipynb")

CEILING = 29_000


def _size():
    """Characters across every cell's source, however the file stores it -- one string or a list
    of lines is the same text."""
    with open(NOTEBOOK, encoding="utf-8") as handle:
        doc = json.load(handle)
    return sum(len("".join(cell.get("source", ""))) for cell in doc.get("cells", []))


def test_the_notebook_stays_well_under_what_the_tools_can_read():
    size = _size()

    assert size <= CEILING, (f"Defter {size} karakter, tavan {CEILING} — defterde yorum yok, "
                             f"yalnız bölüm başlıkları (madde 239)")
