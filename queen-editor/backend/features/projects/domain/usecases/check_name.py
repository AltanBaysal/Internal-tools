"""Would this name be accepted? Asked while the user is still typing.

Creating is what decides; this only answers. It exists so the modal can warn as the name is typed
without keeping a copy of the rules -- one rule, one owner, one Turkish sentence
(backend/features/projects/domain/name_rules.py).

Deliberately storeless: a name already taken is a clash, not a broken rule, and the design does not
ask for it while typing. Keeping the disk out also means this can be asked as often as typing needs.
"""
from backend.features.projects.domain import name_rules


def check_name(name):
    """The rules' own message, or None when the name is usable."""
    return name_rules.validate(name)
