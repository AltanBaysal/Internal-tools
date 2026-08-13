"""Installing a model is the app's job; the notebook installs code only.

A leftover download cell is not a broken import -- it is a second way of installing the same files,
and the two only disagree on a fresh machine, where nobody is looking.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKIP_DIRS = {".git", "dist", "node_modules", "__pycache__"}
# This file names them on purpose. EKSIKLER.md is the findings list: it records what was wrong on
# the day it was written, the way the specs under docs/ do, so it is read as history rather than as
# a claim about the code.
SKIP_FILES = {os.path.basename(__file__), "EKSIKLER.md"}
GONE = ("CIVITAI_MODELS", "OPEN_MODELS", "civitai_probe")

NOTEBOOK = os.path.join(ROOT, "app.ipynb")
# The sound engine is a library rather than a model file, so it was the last thing the notebook
# still installed on a producer's behalf. Leaving that cell in would break nothing -- it would
# quietly become a second way of installing the same engine, and the two only disagree on a fresh
# machine, where nobody is looking.
ENGINE = "MMAudio"


def _mentions():
    found = []
    for folder, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if name in SKIP_FILES or not name.endswith((".py", ".md", ".json", ".ipynb", ".jsx",
                                                        ".js", ".txt")):
                continue
            path = os.path.join(folder, name)
            with open(path, encoding="utf-8", errors="ignore") as handle:
                text = handle.read()
            found += [(os.path.relpath(path, ROOT), word) for word in GONE if word in text]
    return found


def test_the_notebook_downloads_no_models():
    assert _mentions() == []


def test_the_notebook_installs_no_producer_engine():
    with open(NOTEBOOK, encoding="utf-8") as handle:
        assert ENGINE not in handle.read()
