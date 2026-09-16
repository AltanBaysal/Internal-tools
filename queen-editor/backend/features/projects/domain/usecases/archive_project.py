"""Put a project out of the way, bring it back, and list what is out of the way.

Archiving is a MOVE, not a mark (the user's own decision, 16 September): the folder goes one level
down, into the archive. Everything else follows from that by itself and no second rule was written
for any of it -- the project stops being listed because it is no longer where projects are, and it
stops being openable because that is how generation and export look one up. A flag would have
needed all of that spelled out, and each spelling is a place to forget one.

`halt` is the same port delete_project uses, and it is called for the same reason: a worker writing
into a folder that is being moved leaves the project half here and half there. What is behind it is
not this feature's business.

Restoring needs no halt -- a project in the archive has nothing running, because nothing could
reach it to start.
"""
from backend.features.projects.domain.usecases.create_project import NameTaken
from backend.features.projects.domain.usecases.get_settings import ProjectMissing


def archive_project(store, halt, name):
    halt(name)
    answer = store.archive(name)
    # `is` and not truthiness: the two failures are two different sentences.
    if answer is None:
        # Not "that name is taken": the collision is inside the archive, and a user reading the
        # usual sentence would go looking among their projects for something that is not there.
        raise NameTaken(f"Arşivde zaten {name} adlı bir proje var. Önce onu geri al ya da adını "
                        f"değiştir.")
    if answer is False:
        raise ProjectMissing(f"Proje yok: {name}")


def restore_project(store, name):
    answer = store.restore(name)
    if answer is None:
        # Here the collision IS among the projects, so it is the sentence every other screen uses.
        raise NameTaken("Bu ad zaten kullanılıyor. Başka bir ad dene.")
    if answer is False:
        raise ProjectMissing(f"Proje yok: {name}")


def list_archived_projects(store):
    """Newest change first -- one screen, one order (list_projects' own rule)."""
    return sorted(store.list_archived(), key=lambda p: p.modified_at, reverse=True)
