"""What the Üreticiler panel draws: a row per producer, each with a name and an answer.

Installed means every row of the producer's declared group is answered. A row asks one of three
questions and its shape says which: a named row asks for that file, a row naming a kind asks
whether there is anything of that kind, and a row of alternatives asks whether one of them is here
whole. The photo group's model is the third sort: any checkpoint -- the user's pick since Madde 140
-- or every file of Krea 2 Turbo (madde 482). A kind with no group is not installed -- which is the
rule the engine already applies when it refuses to dispatch a job type nobody can do.

A row says nothing about installing, because the app does not install: the models come down in the
Colab notebook, before the app starts (FOUNDATION 9). Reading the disk is the whole of what this
answer is, so it cannot go stale while nobody is installing anything.
"""
from backend.features.producers.domain.producers import NAMES, ORDER, VIDEO, VIDEO_MODEL


def _here(spec, files):
    """Whether one row is answered on this machine. An alternative's rows are the two plain shapes,
    so the recursion is one level deep."""
    if "any" in spec:
        return any(all(_here(row, files) for row in rows) for rows in spec["any"])
    if "name" in spec:
        return files.exists(spec["folder"], spec["name"])
    return files.has_any(spec["folder"], spec["suffix"])


def list_producers(groups, files):
    """The video row names its model too, for the video panel's Model box (madde 247): H3, the one
    video model there is (madde 435)."""
    rows = []
    for kind in ORDER:
        group = groups.get(kind) or []
        installed = bool(group) and all(_here(spec, files) for spec in group)
        row = {"id": kind, "name": NAMES[kind], "installed": installed}
        if kind == VIDEO:
            row["model"] = VIDEO_MODEL
        rows.append(row)
    return rows
