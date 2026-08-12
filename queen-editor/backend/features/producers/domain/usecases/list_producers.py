"""What the Üreticiler panel draws: three rows, each with a name and an answer.

Installed means the producer's declared model group is on this machine, file by file. A kind with
no group is not installed -- which is the rule the engine already applies when it refuses to
dispatch a job type nobody can do.

A row can also carry what the worker is doing about it: `installing` while a download is really
running, naming the file that is coming down, or `error` with the last attempt's own words. Those
two are exclusive, and neither survives the run it belongs to -- the worker keeps its final state
after it finishes, and reporting that as progress left the card saying "kuruluyor" for good.
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
            if running.get("status") == "running":
                # The file, not a percentage: a group's files each restart the count, so a bar
                # over them was movement rather than information.
                row["installing"] = {"file": running.get("file")}
            elif running.get("status") == "error":
                row["error"] = running.get("error")
        rows.append(row)
    return rows
