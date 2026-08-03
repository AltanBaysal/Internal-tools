"""What the panel shows when the project opens.

The message is user-facing Turkish; presentation forwards it untouched.
"""


class ProjectMissing(Exception):
    """No such project folder (message is the user-facing text)."""


def get_settings(store, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    return store.read(project)
