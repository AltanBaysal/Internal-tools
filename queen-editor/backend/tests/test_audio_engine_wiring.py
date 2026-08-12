"""The sound engine moved out of ComfyUI; these guard the parts a unit test cannot see.

A leftover reference is not a broken import -- it is a document telling somebody to export a graph
that nothing reads, and that only shows up when they try.
"""
import os

from backend import config

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKIP_DIRS = {".git", "dist", "node_modules", "__pycache__"}
# This file names both of them on purpose; it is the one place they are allowed to appear.
SKIP_FILES = {os.path.basename(__file__)}
GONE = ("workflow_audio_api", "ComfyAudioGenerator")


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


def test_nothing_still_asks_for_the_comfy_sound_graph():
    assert _mentions() == []


def test_the_settings_no_longer_carry_a_sound_graph_or_its_timeout():
    """Both belonged to waiting on a ComfyUI job; an in-process call has neither a graph to load nor
    a deadline anybody enforces, and a setting nobody reads is a promise nobody keeps."""
    assert not hasattr(config, "AUDIO_WORKFLOW_PATH")
    assert not hasattr(config, "AUDIO_TIMEOUT")
