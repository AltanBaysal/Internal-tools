"""Let a project's folder be deleted with no run able to start in it.

This is the port the projects feature is handed for a delete, the way follow_rename is for a rename:
removing the folder is that feature's work, and the worker that might be inside it belongs to this
one. They meet only in main.py.
"""
from backend.features.photo_generation.domain.usecases.halt_project import halt_project


def follow_delete(runner, plan_store, interrupt, sleep, project, remove):
    """Stop the project's production, then run `remove`; what `remove` answered.

    The production first: the delete's confirm promises it is stopped, and a worker still writing
    into a folder that is being removed is the error that promise rules out (halt_project).

    Both under the project's write gate (madde 523), for the reason a rename takes it: every door
    that queues work writes its job and claims or joins the worker under that gate, so a press falls
    wholly before the halt -- its run stopped with the rest -- or wholly after the removal, and finds
    no project. Taken without, a press between the halt and the removal wrote its job, claimed the
    idle worker, and the folder then went from under its run.
    """
    with plan_store.held(project):
        halt_project(runner, interrupt, sleep, project)
        return remove()
