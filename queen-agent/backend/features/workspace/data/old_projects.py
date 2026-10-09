"""Move projects of the old layout into projects.json, once, at start (Madde 448).

The old layout is the one before Madde 447: a folder per project holding its own project.json, an
empty `pinned` whose mtime was the pin's moment, an empty `archived`, chats/*.json and files/. The
user's projects on Drive are in it, and 447 did not read them. Every start lists the root once and
moves each old folder whose id projects.json does not hold yet -- not only when projects.json is
missing, since a v10 tried in the same root makes one.

Only read: the old files stay as they are. This whole module goes once the user has seen the move
work (BACKLOG, "448'in taşıma kodu ve eski proje dosyaları silinecek"), with take_in, Store.mtime
and its one line in main.py; the notebook's Serve cell then needs no wait as long as its cap.
"""
import json
import logging
import sys
from datetime import datetime, timezone

from backend.features.workspace.data.file_chat_store import _as_chat
from backend.features.workspace.data.file_project_store import PROJECTS_FILE, TRASH_DIR
from backend.features.workspace.domain.chat import ChatSummary
from backend.features.workspace.domain.file import File, extension_of
from backend.features.workspace.domain.project import Project

# The old layout's names, all of them here: that layout is frozen as it sits on Drive, and the
# current stores' names are free to change.
OLD_PROJECT_FILE = "project.json"
PINNED_FILE = "pinned"
ARCHIVED_FILE = "archived"
CHATS_DIR = "chats"
CHAT_SUFFIX = ".json"
FILES_DIR = "files"

log = logging.getLogger(__name__)


class _Unreadable(Exception):
    """A file of an old project that cannot be read, named by its path."""


def move_old_projects(store, projects):
    moved = []
    for name in store.list_dir(""):
        # projects.json and its .writing by name, the trash by name -- a deleted project in there
        # keeps its old project.json -- and whatever projects.json already holds by a lookup: after
        # the first start that is every old folder, so a start reads nothing but the root.
        if name.startswith(PROJECTS_FILE) or name == TRASH_DIR or projects.get(name) is not None:
            continue
        try:
            found = _old_project(store, name)
        except (_Unreadable, OSError) as unreadable:
            # Skipped whole, and tried again at the next start: half a project moved would never be
            # moved again, and what it left out would be lost from the list. An OSError here is the
            # disk's own -- a listing or an mtime refused, or a file gone since the folder was listed.
            log.error("Old project %s was not moved: %s", name, unreadable)
            continue
        if found is None:
            continue
        if not moved:
            # The moving start is the long one -- on Drive about 20 file operations a project, before
            # the server answers anything -- so its log says why it is not up yet.
            print("Moving projects of the old layout into projects.json; this start takes longer.",
                  file=sys.stderr)
        moved.append(found)
    # One change, so one write of projects.json.
    if moved:
        for project_id, error in projects.take_in(moved):
            log.error("Old project %s was not moved: %s", project_id, error)


def _old_project(store, project_id):
    """(Project, chat summaries, files) for an old project's folder, or None when it is not one."""
    try:
        listed = store.list_dir(project_id)
    except NotADirectoryError:
        return None  # a file beside the projects
    if OLD_PROJECT_FILE not in listed:
        return None  # anything else living under the root is not ours to read
    path = f"{project_id}/{OLD_PROJECT_FILE}"
    raw = _read(path, lambda: json.loads(store.read_text(path)))
    name, created_at = _read(path, lambda: (raw["name"], _time(raw["createdAt"], "createdAt")))
    # Madde 384: an archived project is never pinned, and an archive made before that rule could
    # leave the pin file beside it.
    archived = ARCHIVED_FILE in listed
    pinned = PINNED_FILE in listed and not archived
    project = Project(
        id=project_id,
        name=name,
        created_at=created_at,
        pinned_at=_stamp(store, f"{project_id}/{PINNED_FILE}") if pinned else "",
        archived=archived,
    )
    chats = []
    for entry in store.list_dir(f"{project_id}/{CHATS_DIR}"):
        if not entry.endswith(CHAT_SUFFIX):
            continue  # anything else in the folder was not a chat then either
        chat_id, chat_path = entry[: -len(CHAT_SUFFIX)], f"{project_id}/{CHATS_DIR}/{entry}"
        raw_chat = _read(chat_path, lambda: json.loads(store.read_text(chat_path)))
        # The chat store's own reader, so the last activity means what 447 gave it; only the four
        # fields of the row are kept, not every message of every chat until the write.
        chats.append(_read(chat_path, lambda: _summary(_as_chat(chat_id, raw_chat))))
    files = [
        File(
            name=file,
            ext=extension_of(file),
            modified_at=_stamp(store, f"{project_id}/{FILES_DIR}/{file}"),
        )
        for file in store.list_dir(f"{project_id}/{FILES_DIR}")
    ]
    return project, chats, files


def _summary(chat):
    return ChatSummary(
        chat.id,
        chat.title,
        _time(chat.created_at, "createdAt"),
        _time(chat.last_activity, "a message's at"),
    )


def _time(value, field):
    # Every time the move copies must be a string: the list sorts projects and chats by them, and a
    # hand-edited number or null, once in projects.json, fails every list on every start -- though the
    # old app showed such a project. The pin's and the files' times are stamped here from mtimes and
    # are strings already.
    if not isinstance(value, str):
        raise TypeError(f"{field} is {value!r}, not a time")
    return value


def _read(path, read):
    try:
        return read()
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        # The reader's own words beside the path: a JSONDecodeError says where, a KeyError says what.
        raise _Unreadable(f"{path}: {error!r}") from error


def _stamp(store, path):
    # The shape every moment is stamped in -- UTC, to the millisecond -- as the old store read it.
    return datetime.fromtimestamp(store.mtime(path), timezone.utc).isoformat(timespec="milliseconds")
