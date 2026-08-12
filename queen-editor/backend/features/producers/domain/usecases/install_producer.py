"""Fetch whatever of a producer's group is missing, in the background.

The rule is the queue's own: work already done is not done again. Three things stop the run and say
so: a file the app cannot fetch at all, a source whose key this process was not given, and a
producer with no group of its own. A group half installed in silence would read as installed the
next time anybody looked.

`auth` is {source word: headers} -- the keys, held by the composition root and passed in. This use
case never learns what a key is made of, only which sources it has one for.
"""
from backend.features.producers.domain.producers import NAMES


class Busy(Exception):
    """An install is already running (message is user-facing)."""


NOTEBOOK_OWNS = "{name} uygulamadan indirilemiyor — bunu defterin kurulum hücresi kurar."
# A row whose source wants a key, on a process that was given none. Named rather than skipped: a
# silently missing file reads as installed the next time anybody looks.
NO_KEY = "{name} indirilemiyor — {source} anahtarı yok."


def install_producer(groups, files, fetcher, runner, auth, kind):
    group = groups.get(kind) or []
    missing = [spec for spec in group if not files.exists(spec["folder"], spec["name"])]
    auth = auth or {}

    def job():
        if not group:
            return {"status": "error", "error": NOTEBOOK_OWNS.format(name=NAMES[kind])}
        for spec in missing:
            if spec["url"] is None:
                return {"status": "error", "error": NOTEBOOK_OWNS.format(name=spec["name"])}
            source = spec.get("auth")
            if source and source not in auth:
                return {"status": "error",
                        "error": NO_KEY.format(name=spec["name"], source=source)}
            # Named before the bytes start so the card has something to say from the first tick.
            runner.report({"file": spec["name"], "done": 0, "total": None})
            fetcher.fetch(
                spec["url"], files.path(spec["folder"], spec["name"]),
                headers=auth.get(source),
                on_progress=lambda done, total: runner.report({"done": done, "total": total}),
                cancelled=runner.cancelled)
        return {"status": "done"}

    if not runner.start(kind, job):
        raise Busy(f"{NAMES[kind]} zaten kuruluyor.")
