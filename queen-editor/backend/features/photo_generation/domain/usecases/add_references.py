"""Put files in the project's reference pool. Returns the pool as it now stands.

The whole press is decided before a single file is written, the way a deletion decides it
(remove_frames): one file the pool cannot take refuses the upload, and a user who picked twelve
files does not get to find out that four of them landed.

Names are worked out in the same pass, so a second file called kedi.png already sees the first
-- whether the first arrived a moment ago or a week ago. The limits are weighed in that pass too,
against the pool and the rest of the press together (madde 298).
"""
from backend.features.photo_generation.domain import references
from backend.features.photo_generation.domain.usecases.list_references import list_references
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


class UnknownReference(Exception):
    """A file the pool cannot read (message is user-facing)."""


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


def add_references(store, pool, clips, project, files):
    """`files` is [(the name the browser sent, the bytes)]."""
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    held = list_references(store, pool, project)
    taken = [row["name"] for row in held]
    arriving, writing = [], []
    for name, data in files:
        kind = references.kind_of(name)
        if kind is None:
            raise UnknownReference(
                f"Bu dosya referans olamaz: {name} — fotoğraf, video ya da ses olmalı.")
        free = references.free_name(name, taken)
        taken.append(free)
        arriving.append({"name": free, "kind": kind,
                         "seconds": _length(clips, free, kind, data)})
        writing.append((free, data))
    references.check(held, arriving)
    # Nothing at all is written above, so a refusal leaves the pool exactly as it was.
    for name, data in writing:
        pool.save(project, name, data)
    return list_references(store, pool, project)
