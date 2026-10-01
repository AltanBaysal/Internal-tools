"""Madde 406: Grok and its key are gone from Queen Editor, and this is what keeps them gone.

The proof of a deletion is an absence, and only a test that looks for it sees one -- QueenAgent's
madde 383 keeps the same watch over its own folder. This file is the one place the words are
written, because it cannot look for them without naming them.
"""
import os
import re

_QUEEN_EDITOR = os.path.dirname(          # queen-editor
    os.path.dirname(                      # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests
_THIS = os.path.abspath(__file__)

RETIRED = re.compile(r"grok|xai|x\.ai", re.IGNORECASE)
# Built, fetched or left behind on disk rather than written by anyone.
_SKIPPED_DIRS = {"dist", "node_modules", "__pycache__"}
# An integrity hash, where the letters meet by chance; and the backlog, which keeps the user's words
# and the state of the day they were said.
_SKIPPED_FILES = {"package-lock.json", "BACKLOG.md"}


def _written():
    for folder, dirs, files in os.walk(_QUEEN_EDITOR):
        dirs[:] = [name for name in dirs if name not in _SKIPPED_DIRS and not name.startswith(".")]
        for name in files:
            path = os.path.join(folder, name)
            if name not in _SKIPPED_FILES and os.path.abspath(path) != _THIS:
                yield path


def test_the_sweep_reads_the_tool():
    # Asked so the two below cannot pass by walking nothing.
    assert any(path.endswith("config.py") for path in _written())


def test_no_path_names_the_retired_provider():
    named = [
        os.path.relpath(path, _QUEEN_EDITOR)
        for path in _written()
        if RETIRED.search(os.path.relpath(path, _QUEEN_EDITOR))
    ]
    assert named == [], f"Adında hâlâ geçiyor: {named}"


def test_no_file_mentions_the_retired_provider():
    found = []
    for path in _written():
        with open(path, encoding="utf-8", errors="replace") as handle:
            for number, line in enumerate(handle, 1):
                if RETIRED.search(line):
                    found.append(f"{os.path.relpath(path, _QUEEN_EDITOR)}:{number}")
    assert found == [], f"Hâlâ geçiyor: {found}"
