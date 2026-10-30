import errno
import os
import time
from types import SimpleNamespace

import pytest

from backend.services.storage import storage as storage_module
from backend.services.storage.storage import TEMP_PREFIX, NameRefused, Storage, StorageError


def with_project(tmp_path, name="düğün"):
    """A root holding one project folder -- what every write needs, since no write opens one."""
    (tmp_path / name).mkdir(parents=True)
    return Storage(str(tmp_path))


def root_stat_fails(monkeypatch, root, error):
    """The root's stat answers with `error`; every other path is asked for real."""
    real = os.stat

    def stat(path, *args, **kwargs):
        if os.fspath(path) == root:
            raise error
        return real(path, *args, **kwargs)

    monkeypatch.setattr(storage_module.os, "stat", stat)


# --- the mount check --------------------------------------------------------------------------

def test_building_one_touches_nothing(tmp_path):
    # The composition root builds it at import, before anything asks: a root that is not there yet
    # is not an error until someone uses it.
    Storage(str(tmp_path / "yok"))


def test_a_root_that_is_not_there_stops_every_operation(tmp_path):
    storage = Storage(str(tmp_path / "yok"))

    with pytest.raises(StorageError) as caught:
        storage.list_dirs()

    # The OS's own sentence rides along -- never a guessed cause.
    assert "yok" in str(caught.value)


def test_a_dropped_mount_stops_a_save_and_leaves_nothing_behind(tmp_path, monkeypatch):
    """Errno 107 is what Colab's Drive mount answers once it has dropped (colabtools #3441)."""
    storage = with_project(tmp_path)
    root_stat_fails(monkeypatch, str(tmp_path),
                    OSError(errno.ENOTCONN, "Transport endpoint is not connected"))

    with pytest.raises(StorageError) as caught:
        storage.write_text("düğün", "order.json", "{}")

    assert "Transport endpoint is not connected" in str(caught.value)
    assert list((tmp_path / "düğün").iterdir()) == []


def test_a_dropped_mount_is_not_read_as_a_missing_file(tmp_path, monkeypatch):
    storage = with_project(tmp_path)
    root_stat_fails(monkeypatch, str(tmp_path),
                    OSError(errno.ENOTCONN, "Transport endpoint is not connected"))

    with pytest.raises(StorageError):
        storage.read_text("düğün", "plan.json")


def test_the_device_is_recorded_on_first_use_and_a_new_one_stops_the_work(tmp_path, monkeypatch):
    """A remount, or the path suddenly sitting on the machine's own disk, is a different device."""
    storage = with_project(tmp_path)
    storage.list_dirs()
    real = os.stat

    class Moved:
        def __init__(self, info):
            self.st_dev = info.st_dev + 1
            self.st_mode = info.st_mode

    def stat(path, *args, **kwargs):
        info = real(path, *args, **kwargs)
        return Moved(info) if os.fspath(path) == str(tmp_path) else info

    monkeypatch.setattr(storage_module.os, "stat", stat)

    with pytest.raises(StorageError) as caught:
        storage.write_text("düğün", "order.json", "{}")

    assert str(tmp_path) in str(caught.value)
    assert list((tmp_path / "düğün").iterdir()) == []


# --- the name boundary ------------------------------------------------------------------------

# Every public method, called once with names that are fine. Kept beside the rule that every one of
# them checks the mount, so a method added later fails the guard below until it is listed here.
CALLS = {
    "list_dirs": lambda storage, source: storage.list_dirs(),
    "make_dir": lambda storage, source: storage.make_dir("yeni"),
    "delete_dir": lambda storage, source: storage.delete_dir("düğün"),
    "remove_empty_dir": lambda storage, source: storage.remove_empty_dir(("düğün", "boş")),
    "rename_dir": lambda storage, source: storage.rename_dir("düğün", "nikah"),
    "dir_exists": lambda storage, source: storage.dir_exists("düğün"),
    "path": lambda storage, source: storage.path("düğün", "a.png"),
    "list_files": lambda storage, source: storage.list_files("düğün"),
    "read_bytes": lambda storage, source: storage.read_bytes("düğün", "a.png"),
    "read_text": lambda storage, source: storage.read_text("düğün", "a.png"),
    "read_lines": lambda storage, source: storage.read_lines("düğün", "a.png"),
    "stamp": lambda storage, source: storage.stamp("düğün", "a.png"),
    "write_bytes": lambda storage, source: storage.write_bytes("düğün", "b.png", b"PNG"),
    "write_text": lambda storage, source: storage.write_text("düğün", "b.json", "{}"),
    "save_file": lambda storage, source: storage.save_file("düğün", "01.mp4", source),
    "append_line": lambda storage, source: storage.append_line("düğün", "photos.jsonl", "{}"),
    "delete_file": lambda storage, source: storage.delete_file("düğün", "a.png"),
    "stage_bytes": lambda storage, source: storage.stage_bytes("düğün", b"PNG"),
    "rename_file": lambda storage, source: storage.rename_file("düğün", "a.png", "c.png"),
    "sweep_staged": lambda storage, source: storage.sweep_staged("düğün", 3600),
    "trash_dir": lambda storage, source: storage.trash_dir("düğün"),
    "sweep_trash": lambda storage, source: storage.sweep_trash(3600),
}


def test_every_public_method_is_in_the_mount_check_list():
    assert set(CALLS) == {name for name in dir(Storage) if not name.startswith("_")}


def everything_under(root):
    return {path.relative_to(root): None if path.is_dir() else path.read_bytes()
            for path in root.rglob("*")}


@pytest.mark.parametrize("method", sorted(CALLS))
def test_every_operation_stops_on_a_dropped_mount_and_touches_nothing(tmp_path, monkeypatch,
                                                                      method):
    drive = tmp_path / "drive"
    storage = with_project(drive)
    (drive / "düğün" / "a.png").write_bytes(b"PNG")
    source = tmp_path / "parça.mp4"
    source.write_bytes(b"MP4")
    before = everything_under(drive)
    root_stat_fails(monkeypatch, str(drive),
                    OSError(errno.ENOTCONN, "Transport endpoint is not connected"))

    with pytest.raises(StorageError) as caught:
        CALLS[method](storage, str(source))

    assert "Transport endpoint is not connected" in str(caught.value)
    assert everything_under(drive) == before


# --- the name boundary ------------------------------------------------------------------------

# ":" too: on Windows os.path.join(root, "C:") drops the root and lands on the drive itself.
BAD = ["", ".", "..", "a/b", "a\\b", "a\0b", "C:", "a:b"]


@pytest.mark.parametrize("name", BAD)
def test_a_folder_name_that_could_leave_the_root_is_refused(tmp_path, name):
    storage = with_project(tmp_path)

    with pytest.raises(NameRefused):
        storage.delete_dir(name)
    with pytest.raises(NameRefused):
        storage.write_text(name, "settings.json", "{}")
    with pytest.raises(NameRefused):
        storage.path(name)

    assert (tmp_path / "düğün").is_dir()


@pytest.mark.parametrize("name", BAD)
def test_a_part_of_a_deeper_folder_is_held_to_the_same_rule(tmp_path, name):
    storage = with_project(tmp_path)

    with pytest.raises(NameRefused):
        storage.write_bytes(("düğün", name), "a.png", b"PNG")

    assert list((tmp_path / "düğün").iterdir()) == []


@pytest.mark.parametrize("name", BAD)
def test_a_file_name_is_held_to_the_same_rule(tmp_path, name):
    storage = with_project(tmp_path)

    with pytest.raises(NameRefused):
        storage.write_bytes("düğün", name, b"PNG")
    with pytest.raises(NameRefused):
        storage.delete_file("düğün", name)


def test_a_drive_letter_cannot_take_a_write_off_the_root(tmp_path):
    """Why ":" is refused: on Windows a part like "C:" makes os.path.join start again at that drive,
    and the root it was joined onto is gone. Project names already forbid it; the door does too."""
    storage = with_project(tmp_path)

    with pytest.raises(NameRefused) as caught:
        storage.path("C:", "a.png")

    assert str(caught.value) == "Geçersiz ad: 'C:'"


def test_the_name_is_refused_before_the_disk_is_asked(tmp_path):
    # A root that is not there would stop the work too; refusing first means a bad name never costs
    # a trip to Drive.
    with pytest.raises(NameRefused) as caught:
        Storage(str(tmp_path / "yok")).delete_dir("..")

    assert str(caught.value) == "Geçersiz ad: '..'"


def test_a_refused_name_is_one_of_the_doors_refusals(tmp_path):
    """One kind of its own, so the screen can answer it as the client's error (400), and still an
    OSError like every other refusal of the door."""
    assert issubclass(NameRefused, StorageError)
    assert issubclass(StorageError, OSError)


def test_the_root_itself_cannot_be_deleted(tmp_path):
    storage = with_project(tmp_path)

    with pytest.raises(NameRefused):
        storage.delete_dir(())

    assert (tmp_path / "düğün").is_dir()


def test_a_rename_cannot_reach_below_or_above_the_root(tmp_path):
    storage = with_project(tmp_path)

    with pytest.raises(NameRefused):
        storage.rename_dir("düğün", "arsiv/düğün")
    with pytest.raises(NameRefused):
        storage.rename_dir("düğün", "..")

    assert (tmp_path / "düğün").is_dir()


# --- saving -----------------------------------------------------------------------------------

def test_write_text_round_trips(tmp_path):
    storage = with_project(tmp_path)

    storage.write_text("düğün", "settings.json", '{"negatif": "bulanık"}')

    assert storage.read_text("düğün", "settings.json") == '{"negatif": "bulanık"}'


def test_write_text_replaces_what_was_there(tmp_path):
    storage = with_project(tmp_path)
    storage.write_text("düğün", "settings.json", "eski")

    storage.write_text("düğün", "settings.json", "yeni")

    assert storage.read_text("düğün", "settings.json") == "yeni"
    assert [path.name for path in (tmp_path / "düğün").iterdir()] == ["settings.json"]


def test_a_save_that_fails_halfway_leaves_the_old_file_whole(tmp_path, monkeypatch):
    storage = with_project(tmp_path)
    storage.write_text("düğün", "order.json", "eski")

    def broken(*_args):
        raise OSError(errno.EIO, "Input/output error")

    monkeypatch.setattr(storage_module.os, "fsync", broken)

    with pytest.raises(OSError):
        storage.write_text("düğün", "order.json", "yeni")

    assert (tmp_path / "düğün" / "order.json").read_text(encoding="utf-8") == "eski"
    assert [path.name for path in (tmp_path / "düğün").iterdir()] == ["order.json"]


def test_a_save_goes_through_a_temporary_file_in_the_targets_own_folder(tmp_path, monkeypatch):
    storage = with_project(tmp_path)
    replaced = []
    real = os.replace

    def replace(source, target):
        replaced.append((os.path.dirname(source), os.path.basename(source), target))
        real(source, target)

    monkeypatch.setattr(storage_module.os, "replace", replace)

    storage.write_bytes("düğün", "0_a.png", b"PNG")

    [(folder, name, target)] = replaced
    assert folder == str(tmp_path / "düğün")
    assert name.startswith(TEMP_PREFIX)
    assert target == str(tmp_path / "düğün" / "0_a.png")


def test_a_left_over_temporary_file_is_not_listed(tmp_path):
    storage = with_project(tmp_path)
    (tmp_path / "düğün" / f"{TEMP_PREFIX}abc").write_bytes(b"half")
    storage.write_bytes("düğün", "0_a.png", b"PNG")

    assert storage.list_files("düğün") == ["0_a.png"]


def test_staged_bytes_are_hidden_until_they_are_given_a_name(tmp_path):
    """Madde 523: an upload writes its bytes before it knows the name they will carry."""
    storage = with_project(tmp_path)

    staged = storage.stage_bytes(("düğün", "referans"), b"PNG")

    assert staged.startswith(TEMP_PREFIX)
    assert storage.list_files(("düğün", "referans")) == []
    storage.rename_file(("düğün", "referans"), staged, "kedi.png")
    assert storage.list_files(("düğün", "referans")) == ["kedi.png"]
    assert (tmp_path / "düğün" / "referans" / "kedi.png").read_bytes() == b"PNG"


def test_staging_that_fails_halfway_leaves_nothing_behind(tmp_path, monkeypatch):
    storage = with_project(tmp_path)

    def broken(*_args):
        raise OSError(errno.EIO, "Input/output error")

    monkeypatch.setattr(storage_module.os, "fsync", broken)

    with pytest.raises(OSError):
        storage.stage_bytes("düğün", b"PNG")

    assert list((tmp_path / "düğün").iterdir()) == []


def test_a_sweep_takes_only_the_hidden_files_older_than_it_is_told(tmp_path):
    """A staged upload whose folder was renamed from under it, or whose server died, is never
    placed or discarded: hidden, but it holds its megabytes of Drive (madde 523's reviewer). One
    younger may be a write still on its way."""
    storage = with_project(tmp_path)
    folder = tmp_path / "düğün"
    for name in (f"{TEMP_PREFIX}eski", "eski.png", f"{TEMP_PREFIX}yeni"):
        (folder / name).write_bytes(b"x")
    two_hours_ago = os.path.getmtime(folder / "eski.png") - 7200
    for name in (f"{TEMP_PREFIX}eski", "eski.png"):
        os.utime(folder / name, (two_hours_ago, two_hours_ago))

    storage.sweep_staged("düğün", 3600)

    assert sorted(path.name for path in folder.iterdir()) == sorted(
        ["eski.png", f"{TEMP_PREFIX}yeni"])


def test_a_sweep_of_a_folder_that_is_not_there_is_nothing(tmp_path):
    with_project(tmp_path).sweep_staged(("düğün", "referans"), 3600)


def test_staging_never_opens_a_project_folder(tmp_path):
    storage = Storage(str(tmp_path))

    with pytest.raises(FileNotFoundError):
        storage.stage_bytes(("yok", "referans"), b"PNG")

    assert not (tmp_path / "yok").exists()


def test_save_file_brings_a_file_in_from_the_machine(tmp_path):
    storage = with_project(tmp_path / "drive")
    source = tmp_path / "parça.mp4"
    source.write_bytes(b"MP4")

    storage.save_file("düğün", "01.mp4", str(source))

    assert (tmp_path / "drive" / "düğün" / "01.mp4").read_bytes() == b"MP4"
    assert source.read_bytes() == b"MP4"


def test_append_line_creates_the_file_and_keeps_earlier_lines(tmp_path):
    storage = with_project(tmp_path)
    storage.append_line("düğün", "photos.jsonl", '{"file": "0_a.png"}')
    storage.append_line("düğün", "photos.jsonl", '{"file": "0_b.png"}')

    assert storage.read_lines("düğün", "photos.jsonl") == [
        '{"file": "0_a.png"}', '{"file": "0_b.png"}']


def test_an_appended_line_is_flushed_to_the_disk(tmp_path, monkeypatch):
    storage = with_project(tmp_path)
    synced = []
    monkeypatch.setattr(storage_module.os, "fsync", synced.append)

    storage.append_line("düğün", "chats.jsonl", "{}")

    assert len(synced) == 1


# --- no folder is opened by a write -----------------------------------------------------------

def test_no_write_opens_a_project_folder(tmp_path):
    storage = Storage(str(tmp_path))
    source = tmp_path / "parça.mp4"
    source.write_bytes(b"MP4")

    for write in (lambda: storage.write_text("yok", "settings.json", "{}"),
                  lambda: storage.write_bytes("yok", "0_a.png", b"PNG"),
                  lambda: storage.append_line("yok", "photos.jsonl", "{}"),
                  lambda: storage.save_file("yok", "01.mp4", str(source)),
                  lambda: storage.write_bytes(("yok", "referans"), "a.png", b"PNG")):
        with pytest.raises(FileNotFoundError):
            write()

    assert not (tmp_path / "yok").exists()


def test_a_write_into_a_missing_project_names_the_file_asked_for(tmp_path):
    """The screen prints the error as it is, so it names the file the user's save was for -- not
    the temporary file the save would have gone through."""
    storage = Storage(str(tmp_path))

    with pytest.raises(FileNotFoundError) as caught:
        storage.write_text("yok", "settings.json", "{}")

    assert caught.value.filename == str(tmp_path / "yok" / "settings.json")
    assert TEMP_PREFIX not in str(caught.value)
    assert isinstance(caught.value.__cause__, FileNotFoundError)


def test_a_folder_inside_a_project_is_opened_by_its_first_file(tmp_path):
    storage = with_project(tmp_path)

    storage.write_bytes(("düğün", "export", "2026-08-12 14-32", "foto"), "01.png", b"PNG")

    landed = tmp_path / "düğün" / "export" / "2026-08-12 14-32" / "foto" / "01.png"
    assert landed.read_bytes() == b"PNG"


def test_a_file_at_the_root_is_written_and_read(tmp_path):
    # arsiv.json sits beside the projects rather than inside one.
    storage = Storage(str(tmp_path))

    storage.write_text((), "arsiv.json", "{}")

    assert storage.read_text((), "arsiv.json") == "{}"


# --- the room check ---------------------------------------------------------------------------

def drive_has(monkeypatch, free):
    """The mount says `free` bytes are left -- on Colab, what DriveFS reports of the account's
    quota (madde 497). Returns the paths it was asked about."""
    asked = []

    def disk_usage(path):
        asked.append(os.fspath(path))
        return SimpleNamespace(total=10_000, used=10_000 - free, free=free)

    monkeypatch.setattr(storage_module.shutil, "disk_usage", disk_usage)
    return asked


SAVES = {
    "write_bytes": lambda storage, source: storage.write_bytes("düğün", "a.png", b"YENI-PNG"),
    "write_text": lambda storage, source: storage.write_text("düğün", "a.png", "YENI-PNG"),
    "save_file": lambda storage, source: storage.save_file("düğün", "a.png", source),
}


@pytest.mark.parametrize("save", sorted(SAVES))
def test_a_save_drive_has_no_room_for_stops_with_both_numbers_and_writes_nothing(
        tmp_path, monkeypatch, save):
    """Drive was full and nothing said so: the file never reached Drive while the screen showed it
    finished (madde 497). The refusal comes before the temporary file, so nothing is left behind."""
    drive = tmp_path / "drive"
    storage = with_project(drive)
    (drive / "düğün" / "a.png").write_bytes(b"ESKI")
    source = tmp_path / "parça.png"
    source.write_bytes(b"YENI-PNG")             # 8 bytes, like the other two saves
    drive_has(monkeypatch, 7)

    with pytest.raises(StorageError) as caught:
        SAVES[save](storage, str(source))

    said = str(caught.value)
    assert "Drive'da yer yok" in said
    assert "8 bayt" in said and "7 bayt" in said
    assert str(drive / "düğün" / "a.png") in said
    assert [path.name for path in (drive / "düğün").iterdir()] == ["a.png"]
    assert (drive / "düğün" / "a.png").read_bytes() == b"ESKI"


@pytest.mark.parametrize("save", sorted(SAVES))
def test_a_save_that_just_fits_is_written(tmp_path, monkeypatch, save):
    drive = tmp_path / "drive"
    storage = with_project(drive)
    source = tmp_path / "parça.png"
    source.write_bytes(b"YENI-PNG")
    asked = drive_has(monkeypatch, 8)

    SAVES[save](storage, str(source))

    assert (drive / "düğün" / "a.png").read_bytes() == b"YENI-PNG"
    # The root is asked: every folder under it sits on the same mount, the device check says so.
    assert asked == [str(drive)]


def test_a_line_drive_has_no_room_for_is_refused_and_the_record_stays_as_it_was(tmp_path,
                                                                                 monkeypatch):
    """An appended line is a write too: a failed render's line, a written prompt, a chat line --
    many follow no file save at all (madde 497)."""
    storage = with_project(tmp_path)
    (tmp_path / "düğün" / "photos.jsonl").write_text("ilk\n", encoding="utf-8")
    drive_has(monkeypatch, 2)                   # "{}" and its newline are 3 bytes

    with pytest.raises(StorageError) as caught:
        storage.append_line("düğün", "photos.jsonl", "{}")

    assert "3 bayt" in str(caught.value) and "2 bayt" in str(caught.value)
    assert (tmp_path / "düğün" / "photos.jsonl").read_text(encoding="utf-8") == "ilk\n"


def test_a_line_that_just_fits_is_appended(tmp_path, monkeypatch):
    storage = with_project(tmp_path)
    drive_has(monkeypatch, 3)

    storage.append_line("düğün", "photos.jsonl", "{}")

    assert storage.read_lines("düğün", "photos.jsonl") == ["{}"]


def test_a_room_check_that_fails_is_not_read_as_room(tmp_path, monkeypatch):
    storage = with_project(tmp_path)

    def broken(path):
        raise OSError(errno.EIO, "Input/output error")

    monkeypatch.setattr(storage_module.shutil, "disk_usage", broken)

    with pytest.raises(OSError) as caught:
        storage.write_bytes("düğün", "a.png", b"PNG")

    assert "Input/output error" in str(caught.value)
    assert list((tmp_path / "düğün").iterdir()) == []


# --- only FileNotFoundError is missing --------------------------------------------------------

def test_missing_reads_as_nothing(tmp_path):
    storage = with_project(tmp_path)

    assert storage.read_text("düğün", "settings.json") is None
    assert storage.read_bytes("düğün", "0_a.png") is None
    assert storage.read_lines("düğün", "photos.jsonl") == []
    assert storage.stamp("düğün", "photos.jsonl") is None
    assert storage.list_files(("düğün", "referans")) == []
    assert storage.dir_exists("yok") is False


def below_the_root_fails(real, root):
    """`real`, raising EIO for every path below the root. The root itself still answers, so the
    mount check passes and the failure is the file's own."""
    def broken(path, *args, **kwargs):
        if os.fspath(path) != root:
            raise OSError(errno.EIO, "Input/output error")
        return real(path, *args, **kwargs)
    return broken


def test_an_unreadable_file_is_not_read_as_missing(tmp_path, monkeypatch):
    storage = with_project(tmp_path)
    # The module's own name for open, so nothing outside the storage module is touched.
    monkeypatch.setattr(storage_module, "open", below_the_root_fails(open, str(tmp_path)),
                        raising=False)

    with pytest.raises(OSError):
        storage.read_text("düğün", "plan.json")
    with pytest.raises(OSError):
        storage.read_bytes("düğün", "0_a.png")


def test_an_unreadable_folder_is_not_listed_as_empty(tmp_path, monkeypatch):
    storage = with_project(tmp_path)
    monkeypatch.setattr(storage_module.os, "scandir",
                        below_the_root_fails(os.scandir, str(tmp_path)))

    with pytest.raises(OSError):
        storage.list_files("düğün")


def test_an_unreadable_folder_or_file_is_not_said_to_be_missing(tmp_path, monkeypatch):
    storage = with_project(tmp_path)
    monkeypatch.setattr(storage_module.os, "stat", below_the_root_fails(os.stat, str(tmp_path)))

    with pytest.raises(OSError):
        storage.dir_exists("düğün")
    with pytest.raises(OSError):
        storage.stamp("düğün", "photos.jsonl")


# --- folders ----------------------------------------------------------------------------------

def test_make_dir_creates_folder_and_returns_mtime(tmp_path):
    storage = Storage(str(tmp_path))
    mtime = storage.make_dir("düğün")
    assert mtime is not None and mtime > 0
    assert (tmp_path / "düğün").is_dir()


def test_make_dir_returns_none_when_name_taken(tmp_path):
    storage = Storage(str(tmp_path))
    storage.make_dir("düğün")
    assert storage.make_dir("düğün") is None


def test_renaming_a_folder_takes_everything_in_it(tmp_path):
    storage = with_project(tmp_path)
    storage.write_text("düğün", "plan.json", "bir satır")

    assert storage.rename_dir("düğün", "nikah") > 0

    assert storage.read_text("nikah", "plan.json") == "bir satır"
    assert not storage.dir_exists("düğün")


def test_renaming_onto_a_name_that_is_taken_moves_nothing(tmp_path):
    # Two answers because the caller has two different sentences for them: None is a clash, False is
    # a folder that was not there. The mtime that comes back on success is what make_dir answers.
    storage = Storage(str(tmp_path))
    storage.make_dir("düğün")
    storage.make_dir("nikah")

    assert storage.rename_dir("düğün", "nikah") is None
    assert storage.rename_dir("yok", "başka") is False

    assert storage.dir_exists("düğün")
    assert storage.dir_exists("nikah")


def test_a_folder_put_in_the_trash_is_gone_at_once_under_a_hidden_name(tmp_path):
    """Madde 523's QA: a removal over Drive takes tens of seconds, and a write landing in the folder
    meanwhile made it fail half way. One rename takes the name away first; listings skip the
    hidden one."""
    storage = with_project(tmp_path)
    storage.write_text(("düğün", "referans"), "a.png", "PNG")

    trash = storage.trash_dir("düğün")

    assert trash.startswith(TEMP_PREFIX)
    assert not storage.dir_exists("düğün")
    assert storage.list_dirs() == []
    assert (tmp_path / trash / "referans" / "a.png").read_text(encoding="utf-8") == "PNG"
    assert storage.trash_dir("düğün") is False


def test_a_folder_in_the_trash_is_not_there_for_anyone_who_asks_by_name(tmp_path):
    """Madde 523's reviewer: every project door asks dir_exists, and a URL naming the trash would
    otherwise queue, upload or export into it until it was swept. Hidden, as list_dirs hides it."""
    storage = with_project(tmp_path)
    trash = storage.trash_dir("düğün")

    assert storage.dir_exists(trash) is False
    assert storage.dir_exists((trash, "referans")) is False
    assert storage.rename_dir(trash, "geri") is False
    assert storage.trash_dir(trash) is False
    with pytest.raises(FileNotFoundError):
        storage.path((trash, "referans"), "a.png")
    assert (tmp_path / trash).is_dir()
    assert not (tmp_path / "geri").exists()


def test_a_sweep_of_the_trash_takes_only_what_was_put_there_long_enough_ago(tmp_path, monkeypatch):
    """Trash a removal could not finish, or a server died before; never another delete's own, put
    there a moment ago and still being removed."""
    storage = Storage(str(tmp_path))
    for name in ("eski", "yeni", "düğün"):
        storage.make_dir(name)
    now = time.time()
    monkeypatch.setattr(storage_module.time, "time", lambda: now - 7200)
    storage.trash_dir("eski")
    monkeypatch.setattr(storage_module.time, "time", lambda: now)
    fresh = storage.trash_dir("yeni")

    storage.sweep_trash(3600)

    assert sorted(path.name for path in tmp_path.iterdir()) == sorted([fresh, "düğün"])


def test_deleting_a_folder_takes_everything_in_it(tmp_path):
    storage = with_project(tmp_path)
    storage.write_bytes("düğün", "0_a.png", b"PNG")

    assert storage.delete_dir("düğün") is True
    assert storage.delete_dir("düğün") is False
    assert not (tmp_path / "düğün").exists()


def test_deleting_a_folder_inside_a_project(tmp_path):
    storage = with_project(tmp_path)
    storage.write_bytes(("düğün", "export", "2026-08-12 14-32"), "düğün.mp4", b"MP4")

    assert storage.delete_dir(("düğün", "export", "2026-08-12 14-32")) is True

    assert (tmp_path / "düğün" / "export").is_dir()
    assert not (tmp_path / "düğün" / "export" / "2026-08-12 14-32").exists()


def test_an_empty_folder_is_removed(tmp_path):
    storage = with_project(tmp_path)
    (tmp_path / "düğün" / "video").mkdir()

    assert storage.remove_empty_dir(("düğün", "video")) is True

    assert not (tmp_path / "düğün" / "video").exists()


def test_a_folder_holding_anything_is_left_as_it_is(tmp_path):
    """What is left in it is somebody's: a cleanup that took only its own files must not take
    the rest with the folder (madde 474)."""
    storage = with_project(tmp_path)
    (tmp_path / "düğün" / "foto").mkdir()
    (tmp_path / "düğün" / "foto" / "01.png").write_bytes(b"PNG")

    assert storage.remove_empty_dir(("düğün", "foto")) is False
    assert storage.remove_empty_dir("düğün") is False

    assert (tmp_path / "düğün" / "foto" / "01.png").read_bytes() == b"PNG"


def test_removing_a_folder_that_is_not_there_says_so(tmp_path):
    storage = with_project(tmp_path)

    assert storage.remove_empty_dir(("düğün", "yok")) is False


def test_the_root_itself_is_never_removed_even_empty(tmp_path):
    storage = Storage(str(tmp_path))

    with pytest.raises(NameRefused):
        storage.remove_empty_dir(())

    assert tmp_path.is_dir()


def test_list_dirs_returns_name_and_mtime(tmp_path):
    storage = Storage(str(tmp_path))
    storage.make_dir("düğün")
    storage.make_dir("kapak çekimi")
    entries = storage.list_dirs()
    assert sorted(name for name, _ in entries) == ["düğün", "kapak çekimi"]
    assert all(mtime > 0 for _, mtime in entries)


def test_list_dirs_skips_files(tmp_path):
    (tmp_path / "not-a-project.txt").write_text("x", encoding="utf-8")
    assert Storage(str(tmp_path)).list_dirs() == []


def test_dir_exists(tmp_path):
    storage = with_project(tmp_path)
    assert storage.dir_exists("düğün") is True
    assert storage.dir_exists("yok") is False


# --- files ------------------------------------------------------------------------------------

def test_write_bytes_then_list_files(tmp_path):
    storage = with_project(tmp_path)
    storage.write_bytes("düğün", "0_a.png", b"PNG")
    assert (tmp_path / "düğün" / "0_a.png").read_bytes() == b"PNG"
    assert storage.list_files("düğün") == ["0_a.png"]


def test_list_files_skips_directories(tmp_path):
    storage = with_project(tmp_path)
    (tmp_path / "düğün" / "altklasör").mkdir()
    storage.write_bytes("düğün", "0_a.png", b"PNG")
    assert storage.list_files("düğün") == ["0_a.png"]


def test_deleting_a_file_removes_it(tmp_path):
    storage = with_project(tmp_path)
    storage.write_bytes("düğün", "0_a.png", b"PNG")
    storage.delete_file("düğün", "0_a.png")
    assert storage.list_files("düğün") == []


def test_deleting_a_file_that_is_already_gone_is_not_an_error(tmp_path):
    with_project(tmp_path).delete_file("düğün", "yok.png")


def test_a_stamp_changes_when_the_file_does(tmp_path):
    # What a caller holding a parsed copy checks before trusting it. Length as well as time: an
    # append inside the same second still has to read as a change.
    storage = with_project(tmp_path)
    storage.append_line("düğün", "photos.jsonl", "bir")
    before = storage.stamp("düğün", "photos.jsonl")

    storage.append_line("düğün", "photos.jsonl", "iki")

    assert before is not None
    assert storage.stamp("düğün", "photos.jsonl") != before


def test_read_lines_skips_blank_lines(tmp_path):
    storage = with_project(tmp_path)
    storage.write_text("düğün", "photos.jsonl", "ilk\n\n   \nikinci\n")
    assert storage.read_lines("düğün", "photos.jsonl") == ["ilk", "ikinci"]


def test_path_is_the_folder_under_the_root(tmp_path):
    storage = with_project(tmp_path)

    assert storage.path("düğün") == str(tmp_path / "düğün")
    assert storage.path(("düğün", "referans"), "a.mp4") == str(
        tmp_path / "düğün" / "referans" / "a.mp4")
