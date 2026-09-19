"""Put a project out of the way, bring it back, and list what is out of the way.

Archiving is a MARK, not a move (the user's own decision, 16 September, after using the version that
moved): it says which of the two lists a project is drawn in and nothing else. The project stays
where it is and goes on working -- it opens, it renders, it exports.

That is why nothing is halted here, where deleting halts. Halting was the move's debt: a worker
writing into a folder on its way somewhere else left half a project here and half there. Nothing
moves, so there is nothing to stop -- and stopping it would take away the very thing this decision
was made to keep.

There is no name to collide with either, for the same reason: the archive is not a place a folder
could already be sitting in.
"""
from backend.features.projects.domain.usecases.get_settings import ProjectMissing


def archive_project(store, name):
    if store.archive(name) is False:
        raise ProjectMissing(f"Proje yok: {name}")


def restore_project(store, name):
    if store.restore(name) is False:
        raise ProjectMissing(f"Proje yok: {name}")


def list_archived_projects(store):
    """Newest change first -- one screen, one order (list_projects' own rule)."""
    return sorted(store.list_archived(), key=lambda p: p.modified_at, reverse=True)
