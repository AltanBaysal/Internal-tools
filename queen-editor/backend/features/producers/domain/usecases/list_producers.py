"""What the Üreticiler panel draws: three rows, each with a name and an answer.

Installed means the producer's declared model group is on this machine, file by file. A kind with
no group is not installed -- which is the rule the engine already applies when it refuses to
dispatch a job type nobody can do.
"""
from backend.features.producers.domain.producers import NAMES, ORDER


def list_producers(groups, files, running=None):
    rows = []
    for kind in ORDER:
        group = groups.get(kind) or []
        installed = bool(group) and all(
            files.exists(spec["folder"], spec["name"]) for spec in group)
        row = {"id": kind, "name": NAMES[kind], "installed": installed}
        if running and running.get("kind") == kind:
            row["installing"] = {key: running.get(key) for key in ("done", "total", "file")}
        rows.append(row)
    return rows
