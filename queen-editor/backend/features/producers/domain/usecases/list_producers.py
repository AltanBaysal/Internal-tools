"""What the Üreticiler panel draws: three rows, each with a name and an answer.

Installed means every row of the producer's declared group is answered. A row asks one of two
questions and its shape says which: a named row asks for that file, a row naming a kind asks
whether there is anything of that kind. The photo group's checkpoint is the second sort, because
which model is on the machine has been the user's pick since Madde 140. A kind with no group is not
installed -- which is the rule the engine already applies when it refuses to dispatch a job type
nobody can do.

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
            files.exists(spec["folder"], spec["name"]) if "name" in spec
            else files.has_any(spec["folder"], spec["suffix"])
            for spec in group)
        rows.append({"id": kind, "name": NAMES[kind], "installed": installed})
    return rows
