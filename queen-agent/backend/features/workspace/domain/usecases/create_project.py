"""Create a project -- the defaults a new project is born with."""
from backend.features.workspace.domain.project import Project

# The design never asks for a name up front: the project is born named and renamed afterwards.
#
# Since Madde 191 this is the stem rather than the whole name -- what is born is this and a number.
NEW_PROJECT_NAME = "New project"


def create_project(store, new_id, now):
    project = Project(id=new_id, name=_next_name(store.list_all()), created_at=now)
    store.add(project)
    return project


def _next_name(projects):
    """New project 1, and after that the lowest number nobody is using (Madde 191).

    Numbered from the first one. An unnumbered first would stay special forever, and the day
    somebody renamed it the numbering would carry a hole nobody could see.

    The lowest free number rather than one past the highest: New project 1, 3 and 4 reads like
    something went missing, and what the user did was delete a project.

    naming.unique_name is the precedent and this parts from it twice, both on purpose -- it leaves
    the first name alone and separates with a hyphen. A hyphen is a file name's mark, and what the
    sidebar shows is a title.
    """
    taken = {number for number in map(_numbered, projects) if number}
    number = 1
    while number in taken:
        number += 1
    return f"{NEW_PROJECT_NAME} {number}"


def _numbered(project):
    """Which number this project is holding, or None if it is holding none.

    Only a name that is the stem and a number holds one. A project called Thesis holds nothing --
    its name already tells it apart -- and so does New project 2 copy, for the same reason. One a
    person typed by hand does hold its number: two projects under one name is the single thing the
    number exists to prevent, and it does not matter which of them got there first.
    """
    stem, _, tail = str(project.name or "").partition(f"{NEW_PROJECT_NAME} ")
    return int(tail) if stem == "" and tail.isdigit() else None
