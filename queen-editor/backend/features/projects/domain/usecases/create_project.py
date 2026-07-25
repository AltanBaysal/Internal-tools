"""Create one project: validate the name, then let the store settle the conflict.

Both exception messages are user-facing Turkish -- presentation forwards them untouched, so the
rules and their wording live in exactly one place.
"""
from backend.features.projects.domain import name_rules


class InvalidName(Exception):
    """The name broke a rule (message is the user-facing text)."""


class NameTaken(Exception):
    """A project with this name already exists."""


def create_project(store, name):
    error = name_rules.validate(name)
    if error:
        raise InvalidName(error)
    project = store.create(name)
    if project is None:
        raise NameTaken("Bu ad zaten kullanılıyor. Başka bir ad dene.")
    return project
