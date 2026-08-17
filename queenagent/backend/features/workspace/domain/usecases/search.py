"""Search everything the workspace holds: names first, then what is inside the files.

There is no index. The whole workspace is a handful of small text files on one machine, and an
index would be a second copy of the truth that could fall behind it. If this ever gets slow, that
is the moment to build one -- not before.
"""
from backend.features.workspace.domain.hit import Hit
from backend.features.workspace.domain.usecases.list_files import list_files
from backend.features.workspace.domain.usecases.list_projects import list_projects
from backend.features.workspace.domain.usecases.list_recent_chats import list_recent_chats

LIMIT = 8


def search(project_store, chat_store, file_store, query, limit=LIMIT):
    needle = (query or "").strip().lower()
    if not needle:
        # Nothing was typed, so nothing is opened.
        return []

    projects = list_projects(project_store)
    names = {project.id: project.name for project in projects}

    # Four groups in a fixed order: a name is a stronger answer than a body, and the row the user
    # is most likely to want is the biggest thing that matched.
    hits = [
        Hit("project", project.name, project.id, "")
        for project in projects
        if needle in project.name.lower()
    ]
    hits += [
        Hit("chat", chat.title, project_id, names.get(project_id, ""), chat_id=chat.id)
        for project_id, chat in list_recent_chats(chat_store)
        if needle in chat.title.lower()
    ]

    by_name, by_content = [], []
    for project in projects:
        for file in list_files(file_store, project.id):
            row = Hit("file", file.name, project.id, project.name, file_name=file.name)
            if needle in file.name.lower():
                by_name.append(row)
            elif needle in (file_store.read(project.id, file.name) or "").lower():
                # Only files whose name missed are opened, so a file is never listed twice.
                by_content.append(row)

    return (hits + by_name + by_content)[:limit]
