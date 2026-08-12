"""Fetch whatever of a producer's group is missing, in the background.

The rule is the queue's own: work already done is not done again. A file that cannot be fetched
without credentials -- and a producer with no group of its own at all -- stops the run and says so.
A group half installed in silence would read as installed the next time anybody looked.
"""
from backend.features.producers.domain.producers import NAMES


class Busy(Exception):
    """An install is already running (message is user-facing)."""


NOTEBOOK_OWNS = "{name} uygulamadan indirilemiyor — bunu defterin kurulum hücresi kurar."


def install_producer(groups, files, fetcher, runner, kind):
    group = groups.get(kind) or []
    missing = [spec for spec in group if not files.exists(spec["folder"], spec["name"])]

    def job():
        if not group:
            return {"status": "error", "error": NOTEBOOK_OWNS.format(name=NAMES[kind])}
        for spec in missing:
            if spec["url"] is None:
                return {"status": "error", "error": NOTEBOOK_OWNS.format(name=spec["name"])}
            # Named before the bytes start so the card has something to say from the first tick.
            runner.report({"file": spec["name"], "done": 0, "total": None})
            fetcher.fetch(
                spec["url"], files.path(spec["folder"], spec["name"]),
                on_progress=lambda done, total: runner.report({"done": done, "total": total}),
                cancelled=runner.cancelled)
        return {"status": "done"}

    if not runner.start(kind, job):
        raise Busy(f"{NAMES[kind]} zaten kuruluyor.")
