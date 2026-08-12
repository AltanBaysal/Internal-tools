"""What the Üreticiler panel draws: three rows, each with a name and an answer.

Two ways to be installed, and which one applies is the group's own doing:
  * a producer with a declared model group is installed when every file of it is on this machine,
  * a producer with no group answers for itself -- the photo one is set up by the notebook, and
    which checkpoint it holds is the user's choice, so a list of file names we do not own would be
    a worse question than asking the renderer.

A kind with neither is not installed, which is the rule the engine already applies when it refuses
to dispatch a job type nobody can do. A producer that cannot answer at all is not quietly called
missing: the error travels up, because "not installed" would invite a download that would fix
nothing.
"""
from backend.features.producers.domain.producers import NAMES, ORDER


def list_producers(groups, files, producers, running=None):
    rows = []
    for kind in ORDER:
        group = groups.get(kind) or []
        if group:
            installed = all(files.exists(spec["folder"], spec["name"]) for spec in group)
        else:
            producer = producers.get(kind)
            installed = bool(producer) and producer.installed()
        row = {"id": kind, "name": NAMES[kind], "installed": installed}
        if running and running.get("kind") == kind:
            row["installing"] = {key: running.get(key) for key in ("done", "total", "file")}
        rows.append(row)
    return rows
