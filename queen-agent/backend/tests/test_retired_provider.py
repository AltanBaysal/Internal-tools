"""Madde 383: Grok and its key are gone from QueenAgent, and this is what keeps them gone.

The proof of a deletion is an absence, and only a test that looks for it sees one -- test_skills.py's
DELETED list keeps the same watch over the skills Madde 94 removed. This file is the one place the
words are written, because it cannot look for them without naming them.
"""
import os
import re

_QUEEN_AGENT = os.path.dirname(          # queen-agent
    os.path.dirname(                     # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests
_THIS = os.path.abspath(__file__)

RETIRED = re.compile(r"grok|xai|x\.ai", re.IGNORECASE)
# Built, fetched or left behind on disk rather than written by anyone.
_SKIPPED_DIRS = {"dist", "node_modules", "__pycache__"}
# An integrity hash, where the letters meet by chance.
_SKIPPED_FILES = {"package-lock.json"}


def _written():
    for folder, dirs, files in os.walk(_QUEEN_AGENT):
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
        os.path.relpath(path, _QUEEN_AGENT)
        for path in _written()
        if RETIRED.search(os.path.relpath(path, _QUEEN_AGENT))
    ]
    assert named == [], f"Adında hâlâ geçiyor: {named}"


def test_no_file_mentions_the_retired_provider():
    found = []
    for path in _written():
        with open(path, encoding="utf-8", errors="replace") as handle:
            for number, line in enumerate(handle, 1):
                if RETIRED.search(line):
                    found.append(f"{os.path.relpath(path, _QUEEN_AGENT)}:{number}")
    assert found == [], f"Hâlâ geçiyor: {found}"
