"""FileProjectStore -- every project's metadata, in one file at the root, held in memory (Madde 447).

projects.json is read once, when the server starts. From then on every question about a project --
the list, one project, its chats' rows, its files' rows -- is answered from memory, and every change
is made in memory and written behind the request by one writer (queued_write.py). The server is the
file's only writer: a hand edit is seen after a restart, and one server runs per root.

What a chat or a file says stays in its own file; only what a list shows of it is here, and a chat's
settings -- its mode, since Madde 463: a setting is not something the chat said. Contents are
written before their entry, so an entry never names something not yet on disk. The other way round
-- an entry left naming what is gone, because a sudden death lost a delete's removal of it -- reads
as not found and deletes cleanly.

This is the only module that knows the shape of projects.json. The chat and file stores ask it for
their entries by name (put_chat, chat_mode, set_chat_mode, put_file, drop_file, chats, files, file).
"""
import json
import threading

from backend.features.workspace.data.queued_write import QueuedWrite
from backend.features.workspace.domain.chat import ChatSummary
from backend.features.workspace.domain.file import File, extension_of
from backend.features.workspace.domain.modes import DEFAULT, MODES
from backend.features.workspace.domain.naming import unique_name
from backend.features.workspace.domain.project import Project

PROJECTS_FILE = "projects.json"
# One trash for whole projects, beside them. It cannot collide with a project: an id is "p" plus
# twelve hex characters.
TRASH_DIR = "trash"
# A deleted project's entry, written beside its contents in the trash: leaving projects.json, it would
# otherwise take the project's name and times with it.
TRASHED_ENTRY = "project.json"


class ProjectIdTaken(Exception):
    """A project of this id already exists -- the user's work is never overwritten."""


class ProjectsUnreadable(Exception):
    """projects.json is there and cannot be read. The server does not start on it, and nothing is
    written to it: taking it as empty would write over every project the user has."""


class FileProjectStore:
    def __init__(self, store):
        self._store = store
        self._projects = _loaded(store)
        self._lock = threading.Lock()
        self._writes = QueuedWrite(store, PROJECTS_FILE, self._render)

    # ---- The port ----

    def add(self, project):
        # No folder yet: the first chat or file written into the project makes it, and a project
        # deleted before that has nothing on disk to move.
        def added(projects):
            # Asked inside the change, under the lock, so two adds of one id cannot both pass.
            if project.id in projects:
                raise ProjectIdTaken(project.id)
            projects[project.id] = {
                "name": project.name,
                "createdAt": project.created_at,
                "chats": [],
                "files": [],
            }

        self._change(added)

    def get(self, project_id):
        with self._lock:
            entry = self._projects.get(project_id)
            return None if entry is None else _as_project(project_id, entry)

    def list_all(self):
        with self._lock:
            return [_as_project(project_id, entry) for project_id, entry in self._projects.items()]

    def update(self, project_id, change):
        def changed(projects):
            entry = projects.get(project_id)
            if entry is None:
                return None
            edited = change(_as_project(project_id, entry))
            # The counts and the last use are read off the chats and files, so they are not the
            # change's to set; the birth is the project's history.
            entry["name"] = edited.name
            _keep_if(entry, "pinnedAt", edited.pinned_at)
            _keep_if(entry, "archived", edited.archived)
            return _as_project(project_id, entry)

        return self._change(changed)

    def delete(self, project_id):
        with self._lock:
            entry = self._projects.get(project_id)
            kept = None if entry is None else _text(entry)
        if kept is None:
            return None
        # The folder moves whole -- the chats and the files go with it rather than one by one -- and
        # a second project of the same id is numbered rather than written over. The entry follows it
        # into the trash before it leaves the list.
        trashed = unique_name(self._store.list_dir(TRASH_DIR), project_id)
        try:
            self._store.move(project_id, f"{TRASH_DIR}/{trashed}")
        except FileNotFoundError:
            # No folder to move: the project was never written into, or a delete already moved it
            # and a sudden death lost the row's removal. The row goes all the same -- left, it would
            # name something nothing could ever remove.
            pass
        self._store.write_text(f"{TRASH_DIR}/{trashed}/{TRASHED_ENTRY}", kept)
        self._change(lambda projects: projects.pop(project_id, None))
        return trashed

    # ---- The chat and file stores' entries. A put into a project that is not there does nothing ----

    def put_chat(self, project_id, chat):
        self._put(project_id, "chats", "id", _chat_row(chat))

    def chat_mode(self, project_id, chat_id):
        """The chat's mode (Madde 463), or None when no row names it. A row with none -- one written
        before chats had a mode, or one in Edit -- is in the default, and so is a value nobody knows:
        a hand edit is not worth refusing the whole file over. Edit picked on such a row is no
        change, and the stray value stays until another mode is picked."""
        with self._lock:
            row = _chat_row_of(self._projects, project_id, chat_id)
            return None if row is None else _mode_of(row)

    def set_chat_mode(self, project_id, chat_id, mode):
        """Put the mode on the chat's row; False when no row names it. The caller checked the name.

        The mode the chat is already in is no change, so the writer is not told: the picker answers
        a press on its checked row as on any other."""
        with self._lock:
            row = _chat_row_of(self._projects, project_id, chat_id)
            if row is None:
                return False
            if _mode_of(row) == mode:
                return True
            # Written only while it is not the default, like a pin: the common case is no key.
            _keep_if(row, "mode", "" if mode == DEFAULT else mode)
        # After the lock, as _change tells it: the writer takes the same lock to render.
        self._writes.changed()
        return True

    def put_file(self, project_id, name, modified_at):
        self._put(project_id, "files", "name", _file_row(name, modified_at))

    def take_in(self, moved):
        """Add projects found in the old layout -- (Project, chats, files) each -- in one change, so
        one write (Madde 448). An id already here is left as it is. Answers (id, error) for each
        project left out because the next start could not read its entry.

        Goes, with old_projects.py, once 448 is confirmed (BACKLOG).
        """

        def taken(projects):
            refused = []
            for project, chats, files in moved:
                if project.id in projects:
                    continue
                entry = {
                    "name": project.name,
                    "createdAt": project.created_at,
                    "chats": [_chat_row(chat) for chat in chats],
                    "files": [_file_row(file.name, file.modified_at) for file in files],
                }
                _keep_if(entry, "pinnedAt", project.pinned_at)
                _keep_if(entry, "archived", project.archived)
                # Read as the next start reads it, behind old_projects.py's own check of the times: an
                # entry it cannot read would make every start after this one refuse projects.json.
                try:
                    _as_project(project.id, entry)
                except (ValueError, KeyError, TypeError, AttributeError) as error:
                    refused.append((project.id, repr(error)))
                    continue
                projects[project.id] = entry
            return refused

        return self._change(taken)

    def drop_file(self, project_id, name):
        def dropped(projects):
            entry = projects.get(project_id)
            if entry is not None:
                entry["files"] = [row for row in entry["files"] if row["name"] != name]

        self._change(dropped)

    def chats(self, project_id):
        with self._lock:
            entry = self._projects.get(project_id)
            return [] if entry is None else _chats(entry)

    def files(self, project_id):
        with self._lock:
            entry = self._projects.get(project_id)
            return [] if entry is None else _files(entry)

    def file(self, project_id, name):
        return next((file for file in self.files(project_id) if file.name == name), None)

    # ---- Writing ----

    def flush(self):
        """Wait until the writer has put every change on disk."""
        self._writes.flush()

    def _change(self, change):
        # The one place the state changes. The writer is told after the lock is let go: it takes the
        # same lock to render, and a request never waits for the disk.
        with self._lock:
            answer = change(self._projects)
        self._writes.changed()
        return answer

    def _put(self, project_id, field, key, row):
        # The row of that key updated where it stands, or added at the end. Updated rather than
        # replaced: a chat's row also holds its settings (Madde 463), which writing what the chat
        # said must not take away.
        def put(projects):
            entry = projects.get(project_id)
            if entry is None:
                return
            rows = entry[field]
            for existing in rows:
                if existing[key] == row[key]:
                    existing.update(row)
                    return
            rows.append(row)

        self._change(put)

    def _render(self):
        with self._lock:
            return _text(self._projects)


def _loaded(store):
    try:
        # A byte-order mark is taken off, as utf-8-sig would: an editor on Windows may save one. The
        # server writes none.
        projects = json.loads(store.read_text(PROJECTS_FILE).removeprefix("﻿"))
        if not isinstance(projects, dict):
            raise ValueError("it is not an object of projects")
        # Every entry read once, the way the lists will read it: a broken one stops the start here
        # rather than failing every list later -- or, for a list that is not one, the first put.
        for project_id, entry in projects.items():
            for field in ("chats", "files"):
                if not isinstance(entry[field], list):
                    raise ValueError(f"project {project_id}: {field} is not a list")
            _as_project(project_id, entry)
            _chats(entry)
            _files(entry)
    except FileNotFoundError:
        # No projects yet. Nothing is written until there is one.
        return {}
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        # The decoder's or the reader's own words; UnicodeDecodeError is a ValueError too.
        raise ProjectsUnreadable(f"{PROJECTS_FILE} could not be read: {error!r}") from error
    return projects


def _as_project(project_id, entry):
    chats = entry["chats"]
    return Project(
        id=project_id,
        name=entry["name"],
        created_at=entry["createdAt"],
        chat_count=len(chats),
        file_count=len(entry["files"]),
        last_chat_at=max((chat["lastActivity"] for chat in chats), default=""),
        pinned_at=entry.get("pinnedAt", ""),
        archived=entry.get("archived", False),
    )


def _chats(entry):
    return [
        ChatSummary(
            id=chat["id"],
            title=chat["title"],
            created_at=chat["createdAt"],
            last_activity=chat["lastActivity"],
        )
        for chat in entry["chats"]
    ]


def _chat_row_of(projects, project_id, chat_id):
    # The row standing for this chat, or None -- _chat_row below builds one.
    entry = projects.get(project_id)
    if entry is None:
        return None
    return next((row for row in entry["chats"] if row["id"] == chat_id), None)


def _mode_of(row):
    # A row with no mode is in the default, and so is one holding a value nobody knows.
    mode = row.get("mode")
    return mode if mode in MODES else DEFAULT


def _files(entry):
    return [
        File(name=file["name"], ext=extension_of(file["name"]), modified_at=file["modifiedAt"])
        for file in entry["files"]
    ]


def _chat_row(chat):
    # What a list shows of a chat. Its last activity is the chat's own: the open line's newest
    # message, or its birth.
    return {
        "id": chat.id,
        "title": chat.title,
        "createdAt": chat.created_at,
        "lastActivity": chat.last_activity,
    }


def _file_row(name, modified_at):
    return {"name": name, "modifiedAt": modified_at}


def _keep_if(entry, key, value):
    # Pinned, archived and a chat's mode are written only while they stand: an absent key is the
    # common case.
    if value:
        entry[key] = value
    else:
        entry.pop(key, None)


def _text(value):
    # Indented and unescaped like every file of ours: a person can open it on Drive and read it.
    return json.dumps(value, ensure_ascii=False, indent=2)
