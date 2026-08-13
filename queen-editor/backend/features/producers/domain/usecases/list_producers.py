"""What the Üreticiler panel draws: three rows, each with a name and an answer.

Installed means the producer's declared group is on this machine, file by file. A kind with no group
is not installed -- which is the rule the engine already applies when it refuses to dispatch a job
type nobody can do.

A row says nothing about installing, because the app does not install: the models come down in the
Colab notebook, before the app starts (FOUNDATION 9). Reading the disk is the whole of what this
answer is, so it cannot go stale while nobody is installing anything.
"""
from backend.features.producers.domain.producers import NAMES, ORDER


def list_producers(groups, files):
    rows = []
    for kind in ORDER:
        group = groups.get(kind) or []
        installed = bool(group) and all(
            files.exists(spec["folder"], spec["name"]) for spec in group)
        rows.append({"id": kind, "name": NAMES[kind], "installed": installed})
    return rows
