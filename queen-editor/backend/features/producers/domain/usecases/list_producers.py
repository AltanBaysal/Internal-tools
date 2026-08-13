"""What the Üreticiler panel draws: three rows, each with a name and an answer.

Installed means everything the producer declared is here: every model file on this machine, and
every library this process can import. A kind that declares neither is not installed -- which is the
rule the engine already applies when it refuses to dispatch a job type nobody can do. Counting only
the files was the one lie this panel told: sound's weights can sit on disk while the engine that
reads them is not installed at all.

A row can also carry what the worker is doing about it: `installing` while an install is really
running, naming the step it is on, or `error` with the last attempt's own words. Those two are
exclusive, and neither survives the run it belongs to -- the worker keeps its final state after it
finishes, and reporting that as progress left the card saying "kuruluyor" for good.
"""
from backend.features.producers.domain.producers import NAMES, ORDER


def list_producers(groups, files, running=None, libraries=None, lib=None):
    rows = []
    for kind in ORDER:
        group = groups.get(kind) or []
        libs = (libraries or {}).get(kind) or []
        installed = bool(group or libs) and all(
            files.exists(spec["folder"], spec["name"]) for spec in group) and all(
            lib.present(spec["module"]) for spec in libs)
        row = {"id": kind, "name": NAMES[kind], "installed": installed}
        if running and running.get("kind") == kind:
            if running.get("status") == "running":
                # The step, not a percentage: a group's files each restart the count, so a bar
                # over them was movement rather than information.
                row["installing"] = {"step": running.get("step")}
            elif running.get("status") == "error":
                row["error"] = running.get("error")
        rows.append(row)
    return rows
