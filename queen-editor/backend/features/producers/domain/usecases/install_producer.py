"""Fetch whatever of a producer's group is missing, in the background.

The rule is the queue's own: work already done is not done again. Two things stop the run and say
so: a producer with no files declared, and a source whose key this process was not given. A group
half installed in silence would read as installed the next time anybody looked.

`auth` is {source word: headers} -- the keys, held by the composition root and passed in. This use
case never learns what a key is made of, only which sources it has one for.
"""
from backend.features.producers.domain.producers import NAMES


class Busy(Exception):
    """An install is already running (message is user-facing)."""


# A kind that declares nothing at all: there is nothing to install, and saying it finished would
# leave the panel claiming a producer with neither a file nor an engine behind it.
NO_FILES = "{name} için indirilecek dosya tanımlı değil."
# A row whose source wants a key, on a process that was given none. Named rather than skipped: a
# silently missing file reads as installed the next time anybody looks.
NO_KEY = "{name} indirilemiyor — {source} anahtarı yok."
# A library that installed but is still invisible here: pip wrote it, this process did not pick it
# up. Named rather than swallowed -- the weights would land next and the panel would call the
# producer installed while no job of that kind could actually run.
NO_IMPORT = "{name} kuruldu ama bu süreçte görünmüyor — uygulamayı yeniden başlat."


def install_producer(groups, files, fetcher, runner, auth, kind, libraries=None, lib=None):
    group = groups.get(kind) or []
    libs = (libraries or {}).get(kind) or []
    missing = [spec for spec in group if not files.exists(spec["folder"], spec["name"])]
    auth = auth or {}

    def job():
        if not group and not libs:
            return {"status": "error", "error": NO_FILES.format(name=NAMES[kind])}
        # Libraries before files: one is what makes the producer usable at all, and a failure there
        # is worth seeing before minutes of downloading.
        for spec in libs:
            if lib.present(spec["module"]):
                continue
            runner.report({"step": spec["name"]})
            lib.install(spec["repo"], spec["folder"], spec["module"])
            if not lib.present(spec["module"]):
                return {"status": "error", "error": NO_IMPORT.format(name=spec["name"])}
        for spec in missing:
            source = spec.get("auth")
            if source and source not in auth:
                return {"status": "error",
                        "error": NO_KEY.format(name=spec["name"], source=source)}
            # Named before the bytes start so the card has something to say from the first tick.
            runner.report({"step": spec["name"], "done": 0, "total": None})
            fetcher.fetch(
                spec["url"], files.path(spec["folder"], spec["name"]),
                headers=auth.get(source),
                on_progress=lambda done, total: runner.report({"done": done, "total": total}),
                cancelled=runner.cancelled)
        return {"status": "done"}

    if not runner.start(kind, job):
        raise Busy(f"{NAMES[kind]} zaten kuruluyor.")
