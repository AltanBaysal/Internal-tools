"""Every project, newest change first -- the order the projects screen shows."""


def list_projects(store):
    return sorted(store.list(), key=lambda p: p.modified_at, reverse=True)
