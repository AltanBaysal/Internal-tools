"""Put files in the project's reference pool. Returns the pool as it now stands.

The whole press is decided before a single file lands, the way a deletion decides it
(remove_frames): one file the pool cannot take refuses the upload, and a user who picked twelve
files does not get to find out that four of them landed.

Names are worked out in the same pass, so a second file called kedi.png already sees the first
-- whether the first arrived a moment ago or a week ago. The limits are weighed in that pass too,
against the pool and the rest of the press together (madde 298).

Each file goes in at the end of its own row, and that row is written into the order as it then
stands (madde 414). The order is what places a file: one it does not name waits among the others by
name (references.placed), so an upload left out of it would stand wherever its name sorts -- in
front of the reference already there whenever it sorts first. A second kedi.png, stored as
kedi-2.png, always would: "-" sorts before ".".

In two steps (madde 523). What needs only the bytes in hand comes first, outside the project's
write gate: each file's kind, its length (ffprobe), the limits the press breaks on its own, and the
bytes written to Drive under hidden names no listing sees. Then, under the gate, what needs the
pool: the free names, the limits against the pool, each file renamed into place, the order. The
names are chosen from the pool as read and the order is written back whole, so a second upload,
removal or drag landing in between would take the same name or drop the other's from the order;
held, they come one after another, and a rename or a delete falls wholly before or after (522). The
first step is kept out of it because it is the long one -- ffprobe and tens of megabytes to Drive --
and every press on the project waits for the gate. A refused or failed upload takes its hidden files
away again; what outlives one -- moved with the folder by a rename before its gate, or left by a
server that died -- is swept by a later upload under the gate, once it is an hour old.
"""
from backend.features.photo_generation.domain import references
from backend.features.photo_generation.domain.usecases.list_references import list_references
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


class UnknownReference(Exception):
    """A file the pool cannot read, or one picked into another kind's row (message is
    user-facing)."""


def _length(clips, name, kind, data):
    """How long this file runs, or None for something with no length.

    A clip whose length cannot be read is refused rather than taken in: every limit counted after
    it would be unanswerable, and ffprobe's own sentence is what says why.
    """
    if kind == references.PICTURE or clips is None:
        return None
    try:
        return clips.seconds(data)
    except Exception as exc:
        raise references.PoolLimit(f"{name} havuza giremez — süresi okunamadı: {exc}") from exc


def _weighed(clips, files, row):
    """[(the name the browser sent, {"name", "kind", "seconds"}, bytes)] -- the press, decided as far
    as the bytes in hand allow. A name here is free only among the press itself: the pool's own are
    known under the gate. The limits a press breaks with no pool at all are said here, before a byte
    goes to Drive."""
    taken, weighed = [], []
    for name, data in files:
        kind = references.kind_of(name)
        if kind is None:
            raise UnknownReference(
                f"Bu dosya referans olamaz: {name} — fotoğraf, video ya da ses olmalı.")
        if row is not None and kind != row:
            raise UnknownReference(f"{name} {references.SAID[row]} yuvasına giremez — "
                                   f"bu dosya {references.SAID[kind]}.")
        said = references.free_name(name, taken)
        taken.append(said)
        weighed.append((name, {"name": said, "kind": kind,
                               "seconds": _length(clips, said, kind, data)}, data))
    references.check([], [one for _name, one, _data in weighed])
    return weighed


def add_references(store, pool, orders, clips, plan_store, project, files, row=None):
    """`files` is [(the name the browser sent, the bytes)].

    `row` is the kind of the row whose Ekle card the files were picked from (madde 320). The user
    asked for them in that row, so a file of another kind is refused there rather than quietly filed
    under its own. Without a row, each file goes to its own kind's.
    """
    # Looked at before the bytes go too: written into a project that is not there, they would fail
    # in the OS's words rather than the screen's.
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    weighed = _weighed(clips, files, row)
    staged = []
    try:
        try:
            for _name, _one, data in weighed:
                staged.append(pool.stage(project, data))
        except FileNotFoundError:
            # The project was taken away -- deleted or renamed -- since the look above: the bytes
            # had no folder to go to. Asked rather than guessed, and said in the screen's words.
            if not store.project_exists(project):
                raise ProjectMissing(f"Proje yok: {project}") from None
            raise
        with plan_store.held(project):
            if not store.project_exists(project):
                raise ProjectMissing(f"Proje yok: {project}")
            pool.sweep(project)
            held = list_references(store, pool, orders, project)
            taken = [one["name"] for one in held]
            arriving = []
            for name, one, _data in weighed:
                free = references.free_name(name, taken)
                taken.append(free)
                arriving.append({**one, "name": free})
            references.check(held, arriving)
            for one, hidden in zip(arriving, list(staged)):
                pool.place(project, hidden, one["name"])
                staged.remove(hidden)
            # After the files, so the order never names one that did not land. The row is rebuilt
            # from what the pool holds, so a name whose file was deleted by hand in Drive drops out
            # of it here.
            order = orders.read(project)
            for kind in {one["kind"] for one in arriving}:
                order[kind] = [one["name"] for one in held + arriving if one["kind"] == kind]
            orders.write(project, order)
            # The answer from what was listed and what was placed, not a second listing: each clip
            # listed is an ffprobe, and every press on the project waits for the gate (QA).
            return references.placed(order, held + arriving)
    finally:
        # Whatever was not placed: a refusal under the gate, or a failure on the way.
        for hidden in staged:
            pool.discard(project, hidden)
