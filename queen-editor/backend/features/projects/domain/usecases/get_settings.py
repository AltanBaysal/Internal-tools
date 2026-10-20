"""What the panel shows when the project opens.

The message is user-facing Turkish; presentation forwards it untouched.

A reserved folder is not a project (name_rules): a URL naming it finds none, here and in the two
saves beside this.
"""
from backend.features.projects.domain import name_rules


class ProjectMissing(Exception):
    """No such project folder (message is the user-facing text)."""


def get_settings(store, project):
    if name_rules.is_reserved(project) or not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    return store.read(project)
