"""Madde 447: every project's metadata in one file at the root, projects.json, held in memory.

The server reads it once when it starts and answers every list from memory; one writer behind it
keeps the file up to date. What a chat or a file says stays in its own file -- only what a list shows
of it is here.
"""
import json
from dataclasses import replace

import pytest

from backend.features.workspace.data.file_project_store import (
    PROJECTS_FILE,
    FileProjectStore,
    ProjectIdTaken,
    ProjectsUnreadable,
)
from backend.features.workspace.domain.chat import Chat, ChatSummary, Message
from backend.features.workspace.domain.file import File
from backend.features.workspace.domain.project import Project
from backend.services.store.store import Store

BORN = "2026-08-09T10:00:00.000+00:00"


def _at(day):
    return f"2026-08-{day:02d}T10:00:00.000+00:00"


def _project(pid="pabc", name="Thesis"):
    return Project(id=pid, name=name, created_at=BORN)


def _store(tmp_path):
    return FileProjectStore(Store(str(tmp_path)))


def _restarted(store, tmp_path):
    # What a restart does: the writer finishes, and a new store reads the file.
    store.flush()
    return _store(tmp_path)


def _stored(tmp_path):
    return json.loads(Store(str(tmp_path)).read_text(PROJECTS_FILE))


def _chat(chat_id, said_at=BORN, title="Hi"):
    return Chat(
        id=chat_id,
        title=title,
        created_at=BORN,
        messages=(Message(role="user", at=said_at, text="Hi"),),
    )


class CountingStore:
    """A Store that counts what it is asked, to see what goes to the disk."""

    def __init__(self, store):
        self._store = store
        self.calls = []

    def __getattr__(self, name):
        real = getattr(self._store, name)

        def counted(*args):
            self.calls.append(name)
            return real(*args)

        return counted


# ---- Starting ----


def test_no_file_is_no_projects_and_nothing_is_written(tmp_path):
    store = _store(tmp_path)
    store.flush()
    assert store.list_all() == []
    assert Store(str(tmp_path)).list_dir("") == [], "Proje yokken kök'e bir şey yazıldı"


@pytest.mark.parametrize(
    "text",
    [
        "{ not json",
        "[]",
        '{"pabc": {"createdAt": "2026-08-09T10:00:00.000+00:00"}}',
        '{"pabc": {"name": "Thesis", "createdAt": "x", "chats": [{"title": "no id"}]}}',
        # Objects where lists belong would load, and the first put would then crash a request.
        '{"pabc": {"name": "Thesis", "createdAt": "x", "chats": {}, "files": []}}',
        '{"pabc": {"name": "Thesis", "createdAt": "x", "chats": [], "files": {}}}',
        '{"pabc": {"name": "Thesis", "createdAt": "x", "chats": [], "files": "plan.md"}}',
        "\udcff",
    ],
)
def test_a_file_that_cannot_be_read_stops_the_start_and_is_left_alone(tmp_path, text):
    path = tmp_path / PROJECTS_FILE
    path.write_bytes(text.encode("utf-8", "surrogateescape"))
    with pytest.raises(ProjectsUnreadable) as unreadable:
        _store(tmp_path)
    assert PROJECTS_FILE in str(unreadable.value), "Hata hangi dosyanın okunamadığını söylemiyor"
    assert path.read_bytes() == text.encode("utf-8", "surrogateescape"), (
        "Okunamayan projects.json'ın üstüne yazıldı"
    )


def test_a_file_an_editor_saved_with_a_bom_still_loads(tmp_path):
    # Notepad and others put one in front; the server writes none.
    (tmp_path / PROJECTS_FILE).write_bytes(
        b"\xef\xbb\xbf"
        + json.dumps({"pabc": {"name": "Thesis", "createdAt": BORN, "chats": [], "files": []}}).encode()
    )
    store = _store(tmp_path)
    assert store.get("pabc") == _project(), "BOM'lu projects.json okunmadı"
    store.add(_project("pdef", "Harbour"))
    store.flush()
    assert not (tmp_path / PROJECTS_FILE).read_bytes().startswith(b"\xef\xbb\xbf"), (
        "projects.json BOM'la yazıldı"
    )


def test_the_file_is_read_once_and_nothing_after(tmp_path):
    seeded = _store(tmp_path)
    seeded.add(_project())
    seeded.put_chat("pabc", _chat("c1"))
    seeded.put_file("pabc", "plan.md", _at(3))
    seeded.flush()

    counting = CountingStore(Store(str(tmp_path)))
    store = FileProjectStore(counting)
    assert counting.calls == ["read_text"], "Açılışta projects.json bir kez okunmadı"
    store.get("pabc")
    store.get("nope")
    store.list_all()
    store.chats("pabc")
    store.files("pabc")
    store.file("pabc", "plan.md")
    assert counting.calls == ["read_text"], "Bellekten cevaplanacak bir soru diske gitti"


# ---- The file ----


def test_a_project_outlives_the_app(tmp_path):
    store = _store(tmp_path)
    store.add(_project())
    assert _restarted(store, tmp_path).list_all() == [_project()]


def test_a_new_project_is_its_entry_alone(tmp_path):
    # No folder until something is written into it: the first chat or file makes it.
    store = _store(tmp_path)
    store.add(_project())
    store.flush()
    assert Store(str(tmp_path)).list_dir("") == [PROJECTS_FILE]
    assert _stored(tmp_path) == {
        "pabc": {"name": "Thesis", "createdAt": BORN, "chats": [], "files": []}
    }, "projects.json'da yalnız gereken alanlar yok"


def test_an_existing_id_is_not_overwritten(tmp_path):
    store = _store(tmp_path)
    store.add(_project(name="First"))
    with pytest.raises(ProjectIdTaken):
        store.add(_project(name="Second"))
    assert store.get("pabc").name == "First"


def test_counts_and_last_use_are_not_written(tmp_path):
    store = _store(tmp_path)
    store.add(_project())
    store.put_chat("pabc", _chat("c1", said_at=_at(20)))
    store.put_file("pabc", "plan.md", _at(3))
    store.flush()
    entry = _stored(tmp_path)["pabc"]
    assert set(entry) == {"name", "createdAt", "chats", "files"}, (
        "Sayılar ya da son kullanım projects.json'a yazıldı"
    )


def test_pin_and_archive_are_written_only_while_they_stand(tmp_path):
    store = _store(tmp_path)
    store.add(_project())
    store.update("pabc", lambda project: replace(project, pinned_at=_at(5)))
    store.flush()
    assert _stored(tmp_path)["pabc"]["pinnedAt"] == _at(5)
    store.update("pabc", lambda project: replace(project, pinned_at="", archived=True))
    store.flush()
    entry = _stored(tmp_path)["pabc"]
    assert "pinnedAt" not in entry and entry["archived"] is True
    store.update("pabc", lambda project: replace(project, archived=False))
    store.flush()
    assert "archived" not in _stored(tmp_path)["pabc"], "Arşivden çıkan projede archived duruyor"


def test_everything_comes_back_after_a_restart(tmp_path):
    store = _store(tmp_path)
    store.add(_project())
    store.add(_project("pdef", "Harbour"))
    store.update("pabc", lambda project: replace(project, pinned_at=_at(5)))
    store.update("pdef", lambda project: replace(project, archived=True))
    store.put_chat("pabc", _chat("c1", said_at=_at(20)))
    store.put_file("pdef", "plan.md", _at(3))
    again = _restarted(store, tmp_path)
    assert again.list_all() == store.list_all()
    assert again.chats("pabc") == store.chats("pabc")
    assert again.files("pdef") == store.files("pdef")


# ---- What is read off the entries ----


def test_counts_and_last_use_come_from_the_entries(tmp_path):
    store = _store(tmp_path)
    store.add(_project())
    assert store.get("pabc").last_activity == BORN, "Sohbetsiz projenin son kullanımı doğuşu değil"
    store.put_chat("pabc", _chat("c1", said_at=_at(20)))
    store.put_chat("pabc", _chat("c2", said_at=_at(12)))
    store.put_file("pabc", "plan.md", _at(3))
    project = store.get("pabc")
    assert (project.chat_count, project.file_count) == (2, 1)
    assert project.last_activity == _at(20), "Son kullanım en yeni sohbetin anı değil"


def test_a_chat_is_put_by_its_id(tmp_path):
    store = _store(tmp_path)
    store.add(_project())
    store.put_chat("pabc", _chat("c1", said_at=_at(10)))
    store.put_chat("pabc", _chat("c2", said_at=_at(11)))
    store.put_chat("pabc", _chat("c1", said_at=_at(12)))
    assert store.chats("pabc") == [
        ChatSummary("c1", "Hi", BORN, _at(12)),
        ChatSummary("c2", "Hi", BORN, _at(11)),
    ], "Aynı sohbetin kaydı yenilenmedi ya da yenisi eklenmedi"


def test_a_file_is_put_by_its_name_and_dropped(tmp_path):
    store = _store(tmp_path)
    store.add(_project())
    store.put_file("pabc", "plan.md", _at(3))
    store.put_file("pabc", "notes.md", _at(4))
    store.put_file("pabc", "plan.md", _at(5))
    assert store.files("pabc") == [File("plan.md", "md", _at(5)), File("notes.md", "md", _at(4))]
    assert store.file("pabc", "plan.md") == File("plan.md", "md", _at(5))
    store.drop_file("pabc", "plan.md")
    assert store.files("pabc") == [File("notes.md", "md", _at(4))]
    assert store.file("pabc", "plan.md") is None


def test_a_put_into_a_project_that_is_not_there_does_nothing(tmp_path):
    store = _store(tmp_path)
    store.put_chat("nope", _chat("c1"))
    store.put_file("nope", "plan.md", _at(3))
    store.drop_file("nope", "plan.md")
    store.flush()
    assert store.list_all() == [] and store.chats("nope") == [] and store.files("nope") == []
    assert Store(str(tmp_path)).list_dir("") == [], "Olmayan projeye kayıt yazıldı"


def test_an_update_of_a_project_that_is_not_there_is_none(tmp_path):
    assert _store(tmp_path).update("nope", lambda project: project) is None


def test_an_update_keeps_only_name_pin_and_archive(tmp_path):
    store = _store(tmp_path)
    store.add(_project())
    store.put_chat("pabc", _chat("c1"))
    updated = store.update(
        "pabc",
        lambda project: Project(
            id="pabc", name="Renamed", created_at="2000-01-01", chat_count=99, archived=True
        ),
    )
    assert (updated.name, updated.archived, updated.created_at, updated.chat_count) == (
        "Renamed",
        True,
        BORN,
        1,
    ), "Değişiklik projenin ad, pin ve arşivden başka bir şeyini değiştirdi"


# ---- Deleting ----


def test_a_deleted_project_goes_to_the_trash_whole_with_its_entry(tmp_path):
    raw = Store(str(tmp_path))
    store = FileProjectStore(raw)
    store.add(_project())
    store.put_chat("pabc", _chat("c1"))
    raw.write_text("pabc/chats/c1.json", "{}")
    assert store.delete("pabc") == "pabc"
    store.flush()
    assert store.list_all() == [] and store.get("pabc") is None
    assert _stored(tmp_path) == {}
    # Nothing the user made is lost: the contents moved whole, and the entry -- the name, the
    # times, the lists -- lies beside them.
    assert raw.list_dir("trash/pabc") == ["chats", "project.json"]
    assert json.loads(raw.read_text("trash/pabc/project.json"))["name"] == "Thesis"


def test_the_same_id_deleted_twice_does_not_lose_the_first(tmp_path):
    raw = Store(str(tmp_path))
    store = FileProjectStore(raw)
    store.add(_project())
    store.delete("pabc")
    store.add(_project())
    assert store.delete("pabc") == "pabc-2"
    assert raw.list_dir("trash") == ["pabc", "pabc-2"]


def test_deleting_what_is_not_there_is_none(tmp_path):
    assert _store(tmp_path).delete("nope") is None


@pytest.mark.parametrize("why", ["never written into", "already in the trash"])
def test_a_project_whose_folder_is_not_there_still_deletes(tmp_path, why):
    # Never written into: no folder yet. Already in the trash: a delete whose row removal a sudden
    # death lost -- the folder moved, the row stayed. Either way the row must still go, or it names
    # something nothing can ever remove.
    raw = Store(str(tmp_path))
    store = FileProjectStore(raw)
    store.add(_project())
    if why == "already in the trash":
        raw.write_text("pabc/chats/c1.json", "{}")
        raw.move("pabc", "trash/pabc")
    trashed = store.delete("pabc")
    store.flush()
    assert store.get("pabc") is None and _stored(tmp_path) == {}, "Klasörü olmayan proje silinmedi"
    assert json.loads(raw.read_text(f"trash/{trashed}/project.json"))["name"] == "Thesis", (
        "Klasörü olmayan projenin kaydı çöpe yazılmadı"
    )


def test_two_adds_of_one_id_at_once_leave_one_project(tmp_path):
    # The id is checked inside the change, under the lock, so no second add slips between.
    import threading

    store = _store(tmp_path)
    taken = []

    def add(name):
        try:
            store.add(_project(name=name))
        except ProjectIdTaken:
            taken.append(name)

    threads = [threading.Thread(target=add, args=(f"n{index}",)) for index in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len(taken) == 7 and len(store.list_all()) == 1, "Aynı id iki kez eklendi"
