"""Madde 448: projects in the old layout move into projects.json once, at start.

The old layout is the one before Madde 447 (89b5ca77): a folder per project with its own
project.json, an empty `pinned` whose mtime is the pin's moment, an empty `archived`, chats/*.json and
files/. It is written out by hand here, as it sits on the user's Drive. All of this goes once 448 is
confirmed (BACKLOG).
"""
import json
import logging
import os
from datetime import datetime, timezone

import pytest

from backend.features.workspace.data.file_project_store import PROJECTS_FILE, FileProjectStore
from backend.features.workspace.data.old_projects import move_old_projects
from backend.features.workspace.domain.chat import ChatSummary
from backend.features.workspace.domain.file import File
from backend.features.workspace.domain.project import Project
from backend.features.workspace.domain.usecases.list_projects import list_projects
from backend.services.store.store import Store

BORN = "2026-08-09T10:00:00.000+00:00"


def _iso(seconds):
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat(timespec="milliseconds")


def _at(day):
    return f"2026-08-{day:02d}T10:00:00.000+00:00"


def _put(root, rel, text, seconds=None):
    path = os.path.join(str(root), *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    if seconds is not None:
        os.utime(path, (seconds, seconds))


def _old_chat(title, *said_at, created=BORN):
    return json.dumps(
        {
            "title": title,
            "createdAt": created,
            "messages": [{"role": "user", "at": at, "text": "hi"} for at in said_at],
        }
    )


def _old(root, pid, name="Thesis", pinned=None, archived=False, chats=(), files=()):
    """One project as the old layout wrote it."""
    _put(root, f"{pid}/project.json", json.dumps({"name": name, "createdAt": BORN, "hue": 94}))
    if pinned is not None:
        _put(root, f"{pid}/pinned", "", seconds=pinned)
    if archived:
        _put(root, f"{pid}/archived", "")
    for chat_id, text in chats:
        _put(root, f"{pid}/chats/{chat_id}.json", text)
    for file_name, seconds in files:
        _put(root, f"{pid}/files/{file_name}", "body", seconds=seconds)


class CountingStore:
    """A Store that counts what it is asked, to see what goes to the disk."""

    def __init__(self, store):
        self._store = store
        self.calls = []

    def __getattr__(self, name):
        real = getattr(self._store, name)

        def counted(*args):
            self.calls.append((name, args[0]))
            return real(*args)

        return counted


def _start(root, store=None):
    """What main.py does at start: the store, then the move."""
    store = store or Store(str(root))
    projects = FileProjectStore(store)
    move_old_projects(store, projects)
    projects.flush()
    return projects


def _everything(root):
    # Every file under the root but projects.json, with its bytes and its mtime.
    seen = {}
    for folder, _, names in os.walk(str(root)):
        for name in names:
            path = os.path.join(folder, name)
            if name.startswith(PROJECTS_FILE):
                continue
            with open(path, "rb") as handle:
                seen[path] = (handle.read(), os.path.getmtime(path))
    return seen


# ---- What is moved ----


def test_an_old_project_moves_with_everything_it_had(tmp_path):
    _old(
        tmp_path,
        "p1",
        pinned=1_000_000_000,
        chats=[("c1", _old_chat("First", _at(10), _at(12))), ("c2", _old_chat("Empty"))],
        files=[("plan.md", 1_000_000_500)],
    )
    _put(tmp_path, "p1/chats/notes.txt", "not a chat")
    projects = _start(tmp_path)
    assert projects.get("p1") == Project(
        id="p1",
        name="Thesis",
        created_at=BORN,
        chat_count=2,
        file_count=1,
        last_chat_at=_at(12),
        pinned_at=_iso(1_000_000_000),
    ), "Eski proje adı, doğuşu, pini, sayıları ya da son kullanımıyla taşınmadı"
    assert sorted(projects.chats("p1"), key=lambda chat: chat.id) == [
        # The last use is the chat's newest message, the meaning 447 gave it; a chat with none
        # was last used when it was made.
        ChatSummary("c1", "First", BORN, _at(12)),
        ChatSummary("c2", "Empty", BORN, BORN),
    ], "Sohbet satırları eski sohbetlerden kurulmadı"
    assert projects.files("p1") == [File("plan.md", "md", _iso(1_000_000_500))], (
        "Dosya satırları adlarından ve mtime'larından kurulmadı"
    )


def test_an_archived_project_moves_archived_and_an_old_pin_beside_it_is_dropped(tmp_path):
    # Madde 384: an archive made before it could leave the pin file behind; the archive wins.
    _old(tmp_path, "p1", pinned=1_000_000_000, archived=True)
    _old(tmp_path, "p2", archived=True)
    projects = _start(tmp_path)
    for pid in ("p1", "p2"):
        project = projects.get(pid)
        assert (project.archived, project.pinned_at) == (True, ""), "Arşivli proje pinle taşındı"
    entry = json.loads(Store(str(tmp_path)).read_text(PROJECTS_FILE))["p1"]
    assert "pinnedAt" not in entry and entry["archived"] is True


def test_the_move_survives_a_restart(tmp_path):
    _old(tmp_path, "p1", chats=[("c1", _old_chat("First", _at(10)))])
    moved = _start(tmp_path)
    again = FileProjectStore(Store(str(tmp_path)))
    assert again.list_all() == moved.list_all() and again.chats("p1") == moved.chats("p1")


def test_everything_moves_in_one_write(tmp_path):
    for index in range(3):
        _old(tmp_path, f"p{index}", chats=[("c1", _old_chat("Hi", _at(10)))], files=[("a.md", 1)])
    counting = CountingStore(Store(str(tmp_path)))
    _start(tmp_path, counting)
    writes = [rel for name, rel in counting.calls if name == "write_text"]
    assert writes == [PROJECTS_FILE], "Taşıma projects.json'ı tek seferde yazmadı"


# ---- Every start after ----


def test_the_second_start_moves_nothing_and_reads_only_the_root(tmp_path):
    _old(tmp_path, "p1", chats=[("c1", _old_chat("Hi", _at(10)))], files=[("a.md", 1)])
    _put(tmp_path, "trash/pold/project.json", json.dumps({"name": "Gone", "createdAt": BORN}))
    first = _start(tmp_path)
    counting = CountingStore(Store(str(tmp_path)))
    second = _start(tmp_path, counting)
    assert counting.calls == [("read_text", PROJECTS_FILE), ("list_dir", "")], (
        "İkinci açılış kökü listelemekten fazlasını yaptı"
    )
    assert second.list_all() == first.list_all()


def test_a_project_already_in_projects_json_is_kept_as_it_is(tmp_path):
    # A v10 project, and one an interrupted move already took in: both stand, and an old folder of
    # the same id does not write over either. What is missing is moved -- the interrupted move goes on.
    v10 = _start(tmp_path)
    v10.add(Project(id="p1", name="New in v10", created_at=_at(1)))
    v10.flush()
    _old(tmp_path, "p1", name="Old of the same id")
    _old(tmp_path, "p2", name="Old")
    projects = _start(tmp_path)
    assert projects.get("p1").name == "New in v10", "projects.json'daki proje eskisiyle ezildi"
    assert projects.get("p2").name == "Old", "Eksik eski proje taşınmadı"


def test_the_old_files_are_left_untouched(tmp_path):
    _old(
        tmp_path,
        "p1",
        pinned=1_000_000_000,
        archived=True,
        chats=[("c1", _old_chat("Hi", _at(10)))],
        files=[("plan.md", 1_000_000_500)],
    )
    before = _everything(tmp_path)
    _start(tmp_path)
    _start(tmp_path)
    assert _everything(tmp_path) == before, "Taşıma eski dosyalara dokundu"


def test_what_is_not_an_old_project_is_skipped(tmp_path):
    _old(tmp_path, "p1")
    # A deleted project in the trash, a stray file, a folder with no project.json in it.
    _put(tmp_path, "trash/pold/project.json", json.dumps({"name": "Deleted", "createdAt": BORN}))
    _put(tmp_path, "notes.txt", "a person's own note")
    _put(tmp_path, "stray/readme.md", "not a project")
    assert [project.id for project in _start(tmp_path).list_all()] == ["p1"]


# ---- What cannot be read ----


def test_an_old_project_that_cannot_be_read_is_skipped_and_said(tmp_path, caplog):
    _put(tmp_path, "p1/project.json", "{ not json")
    _put(tmp_path, "p2/project.json", json.dumps({"createdAt": BORN}))
    _old(tmp_path, "p3", chats=[("c1", "{ not a chat")])
    _old(tmp_path, "p4", name="Fine")
    before = _everything(tmp_path)
    with caplog.at_level(logging.ERROR):
        projects = _start(tmp_path)
    assert [project.id for project in projects.list_all()] == ["p4"], (
        "Okunamayan eski proje taşındı ya da sağlam olan taşınmadı"
    )
    said = caplog.text
    for where in ("p1/project.json", "p2/project.json", "p3/chats/c1.json"):
        assert where in said, f"Okunamayan {where} log'da söylenmedi"
    assert "JSONDecodeError" in said and "KeyError" in said, "Okuyucunun kendi sözü log'da yok"
    assert _everything(tmp_path) == before, "Okunamayan eski proje değiştirildi"


def test_a_project_skipped_once_moves_when_it_can_be_read(tmp_path):
    _put(tmp_path, "p1/project.json", "{ not json")
    _start(tmp_path)
    _put(tmp_path, "p1/project.json", json.dumps({"name": "Fixed", "createdAt": BORN}))
    assert _start(tmp_path).get("p1").name == "Fixed"


def test_a_disk_error_in_one_old_project_skips_only_that_one(tmp_path, caplog):
    # An mtime the disk refuses -- EIO on Drive, or a file gone since its folder was listed -- is
    # outside the readers' guard; it must not stop the start.
    class Flaky(Store):
        def mtime(self, rel):
            if rel.startswith("p1/"):
                raise OSError(5, "Input/output error", rel)
            return super().mtime(rel)

    _old(tmp_path, "p1", files=[("a.md", 1)])
    _old(tmp_path, "p2", files=[("a.md", 1)])
    with caplog.at_level(logging.ERROR):
        projects = _start(tmp_path, Flaky(str(tmp_path)))
    assert [project.id for project in projects.list_all()] == ["p2"], (
        "Diskin hatası açılışı durdurdu ya da sağlam proje taşınmadı"
    )
    assert "p1" in caplog.text and "Input/output error" in caplog.text, "Diskin hatası log'da yok"


@pytest.mark.parametrize(
    "project, chat",
    [
        # A single chat: max() over one value does not fail, so only the type says it.
        ({"name": "Odd", "createdAt": BORN}, _old_chat("Hi", 12345)),
        ({"name": "Odd", "createdAt": BORN}, _old_chat("Hi", created=5)),
        ({"name": "Odd", "createdAt": 5}, None),
        ({"name": "Odd", "createdAt": None}, None),
    ],
    ids=["numeric message time", "numeric chat birth", "numeric project birth", "null project birth"],
)
def test_an_old_project_with_a_time_that_is_not_one_is_skipped(tmp_path, caplog, project, chat):
    # Moved in, a number or null among the times fails every list on every start after.
    _put(tmp_path, "p1/project.json", json.dumps(project))
    if chat:
        _put(tmp_path, "p1/chats/c1.json", chat)
    _old(tmp_path, "p2", name="Fine", chats=[("c1", _old_chat("Hi", _at(10)))])
    with caplog.at_level(logging.ERROR):
        _start(tmp_path)
    assert "p1" in caplog.text and "not a time" in caplog.text, "Zamanı bozuk proje log'da söylenmedi"
    again = FileProjectStore(Store(str(tmp_path)))
    assert [project.id for project in list_projects(again)] == ["p2"], (
        "Zamanı bozuk proje taşındı ya da sonraki açılışta liste cevap vermiyor"
    )


def test_take_in_leaves_out_what_the_next_start_could_not_read(tmp_path):
    # The second line behind the move's own check: two last uses that cannot be compared.
    projects = FileProjectStore(Store(str(tmp_path)))
    odd = [ChatSummary("c1", "Hi", BORN, BORN), ChatSummary("c2", "Hi", BORN, 5)]
    refused = projects.take_in(
        [
            (Project(id="p1", name="Odd", created_at=BORN), odd, []),
            (Project(id="p2", name="Fine", created_at=BORN), [], []),
        ]
    )
    assert [project_id for project_id, _ in refused] == ["p1"] and "TypeError" in refused[0][1]
    projects.flush()
    assert [project.id for project in FileProjectStore(Store(str(tmp_path))).list_all()] == ["p2"]


def test_the_moving_start_says_so_once_and_a_later_one_not_at_all(tmp_path, capsys):
    # It reaches the notebook's log while the server is not answering yet.
    for index in range(3):
        _old(tmp_path, f"p{index}")
    _start(tmp_path)
    said = capsys.readouterr().err
    assert said.count("Moving projects of the old layout") == 1, "Taşıma bir kez söylenmedi"
    _start(tmp_path)
    assert capsys.readouterr().err == "", "Taşıyacak bir şey yokken de söylendi"


def test_a_start_with_only_unreadable_old_projects_says_nothing_of_moving(tmp_path, capsys):
    # Tried again at every start, so a line here would be said on every start with nothing moved.
    _put(tmp_path, "p1/project.json", "{ not json")
    _put(tmp_path, "p2/project.json", json.dumps({"name": "Odd", "createdAt": 5}))
    _old(tmp_path, "p3", chats=[("c1", _old_chat("Hi", 12345))])
    for _ in range(2):
        _start(tmp_path)
        assert "Moving projects" not in capsys.readouterr().err, "Hiçbir şey taşınmazken söylendi"
