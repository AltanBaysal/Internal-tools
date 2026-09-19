from backend.features.projects.data.project_store import DriveProjectStore
from backend.services.drive.storage import DriveStorage


def store_at(path):
    return DriveProjectStore(DriveStorage(str(path)))


def test_list_archived_on_a_root_that_never_archived_anything(tmp_path):
    """A fresh install has no archive folder, and that is not an error -- it is an empty archive."""
    assert store_at(tmp_path).list_archived() == []


def test_create_makes_folder_and_returns_project(tmp_path):
    created = store_at(tmp_path).create("kapak çekimi")
    assert created.name == "kapak çekimi"
    assert created.modified_at > 0
    assert (tmp_path / "kapak çekimi").is_dir()


def test_create_returns_none_when_folder_exists(tmp_path):
    store = store_at(tmp_path)
    store.create("düğün")
    assert store.create("düğün") is None


def test_list_returns_projects_for_every_folder(tmp_path):
    store = store_at(tmp_path)
    store.create("düğün")
    store.create("test")
    assert sorted(p.name for p in store.list()) == ["düğün", "test"]
    assert all(p.modified_at > 0 for p in store.list())


def test_an_archived_project_is_off_the_projects_list(tmp_path):
    """Which list a project is drawn in is the whole of what archiving changes (madde 227), so this
    is the one thing the mark has to do."""
    store = store_at(tmp_path)
    store.create("düğün")
    store.archive("düğün")

    assert [p.name for p in store.list()] == []


def test_the_archive_lists_what_was_put_in_it(tmp_path):
    store = store_at(tmp_path)
    store.create("düğün")
    store.create("test")
    store.archive("düğün")

    archived = store.list_archived()

    assert [p.name for p in archived] == ["düğün"]
    assert all(p.modified_at > 0 for p in archived)
    assert [p.name for p in store.list()] == ["test"]


def test_archiving_leaves_the_folder_exactly_where_it_was(tmp_path):
    """Madde 227. Archiving says which list a project is drawn in and nothing else -- the user asked
    for exactly that after using the moving version: the project has to go on working."""
    store = store_at(tmp_path)
    store.create("düğün")
    (tmp_path / "düğün" / "0_a.png").write_bytes(b"PNG")

    store.archive("düğün")

    assert (tmp_path / "düğün" / "0_a.png").read_bytes() == b"PNG"
    assert not (tmp_path / "arsiv").exists()


def test_restoring_brings_it_back(tmp_path):
    store = store_at(tmp_path)
    store.create("düğün")
    store.archive("düğün")

    store.restore("düğün")

    assert [p.name for p in store.list()] == ["düğün"]
    assert store.list_archived() == []


def test_restoring_only_lifts_the_mark(tmp_path):
    store = store_at(tmp_path)
    store.create("düğün")
    (tmp_path / "düğün" / "0_a.png").write_bytes(b"PNG")
    store.archive("düğün")

    store.restore("düğün")

    assert (tmp_path / "düğün" / "0_a.png").read_bytes() == b"PNG"


def test_an_archived_project_is_still_there_for_everything_that_asks_by_name(tmp_path):
    """The whole of madde 227 in one line. Nine use cases reach a project through dir_exists, and
    the moving version closed all nine at once -- which is what the user did not want."""
    storage = DriveStorage(str(tmp_path))
    store = DriveProjectStore(storage)
    store.create("düğün")

    store.archive("düğün")

    assert storage.dir_exists("düğün") is True


def test_renaming_an_archived_project_carries_the_mark_along(tmp_path):
    """The mark is no longer the disk itself, so it hangs on a name and has to follow it."""
    store = store_at(tmp_path)
    store.create("düğün")
    store.archive("düğün")

    store.rename("düğün", "kına")

    assert [p.name for p in store.list_archived()] == ["kına"]
    assert store.list() == []


def test_deleting_an_archived_project_drops_its_mark(tmp_path):
    """The quiet one: a leftover name breaks no list -- there is no folder under it -- right up
    until somebody makes a project with that name, which would then be born archived."""
    store = store_at(tmp_path)
    store.create("düğün")
    store.archive("düğün")

    store.delete("düğün")
    store.create("düğün")

    assert [p.name for p in store.list()] == ["düğün"]
    assert store.list_archived() == []


def test_an_unreadable_mark_file_reads_as_an_empty_archive(tmp_path):
    """settings.json's own rule: nothing unreadable may make the list impossible to draw."""
    store = store_at(tmp_path)
    store.create("düğün")
    (tmp_path / "arsiv.json").write_text("{bozuk", encoding="utf-8")

    assert [p.name for p in store.list()] == ["düğün"]
    assert store.list_archived() == []


def test_a_name_the_archive_holds_cannot_be_created(tmp_path):
    """Madde 223 asked for this against a moving archive. Since madde 227 the archived project sits
    in the root like any other, so the name is taken by the folder itself -- the rule holds without
    being written anywhere, and that is the point of asking it here."""
    store = store_at(tmp_path)
    store.create("düğün")
    store.archive("düğün")

    assert store.create("düğün") is None


def test_a_refused_name_does_not_touch_what_is_already_there(tmp_path):
    """A create that fails must leave the disk as it found it -- and what is under that name now is
    somebody's archived project, files and all."""
    store = store_at(tmp_path)
    store.create("düğün")
    (tmp_path / "düğün" / "0_a.png").write_bytes(b"PNG")
    store.archive("düğün")

    store.create("düğün")

    assert (tmp_path / "düğün" / "0_a.png").read_bytes() == b"PNG"


def test_a_project_cannot_be_renamed_onto_an_archived_name(tmp_path):
    """The same question from the other side: the target name is a folder that is really there."""
    store = store_at(tmp_path)
    store.create("düğün")
    store.archive("düğün")
    store.create("nikah")

    assert store.rename("nikah", "düğün") is None
    assert (tmp_path / "nikah").is_dir()


def test_a_name_the_archive_does_not_hold_is_still_created(tmp_path):
    store = store_at(tmp_path)
    store.create("düğün")
    store.archive("düğün")

    assert store.create("nikah").name == "nikah"


def test_is_archived_answers_both_ways(tmp_path):
    """Asked only when a create or a rename was refused: the two refusals have two sentences, and
    this is what tells them apart. On the happy path nobody asks -- over Drive every question is a
    round trip."""
    store = store_at(tmp_path)
    store.create("düğün")
    store.archive("düğün")
    store.create("nikah")

    assert store.is_archived("düğün") is True
    assert store.is_archived("nikah") is False
    assert store.is_archived("hiç olmadı") is False


def test_archiving_something_that_is_not_there_says_so(tmp_path):
    assert store_at(tmp_path).archive("yok") is False


def test_a_leftover_archive_folder_is_not_a_project(tmp_path):
    """Madde 221 moved archived projects into arsiv/, and an install from that time still has the
    folder. Nothing goes looking in it -- carrying those projects home is done by hand, in Drive
    (the user's call: keep the code simple) -- but the root's folders ARE the projects, so without
    this it would show up on the screen as one."""
    (tmp_path / "arsiv" / "düğün").mkdir(parents=True)
    store = store_at(tmp_path)
    store.create("nikah")

    assert [p.name for p in store.list()] == ["nikah"]


def test_restoring_something_the_archive_does_not_hold_says_so(tmp_path):
    assert store_at(tmp_path).restore("yok") is False
