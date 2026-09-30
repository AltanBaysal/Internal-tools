"""List projects: the pinned first, in the order they were pinned, then the most recently used.

The order All projects and the sidebar list them in -- the design's All projects (135, 167).
"""


def list_projects(store):
    projects = store.list_all()
    # By the pin's moment rather than by `pinned`: an archived project is not pinned, but it keeps
    # its place among the pins, and that is where its Undo line stands (Madde 382). The id breaks
    # ties so the order never wobbles.
    pinned = sorted(
        (project for project in projects if project.pinned_at),
        key=lambda project: (project.pinned_at, project.id),
    )
    recent = sorted(
        (project for project in projects if not project.pinned_at),
        key=lambda project: (project.last_activity, project.id),
        reverse=True,
    )
    return pinned + recent
