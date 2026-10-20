import errno
import os

import pytest

from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.projects.domain import name_rules
from backend.services.storage.storage import TEMP_PREFIX, Storage, StorageError
from backend.tests.test_storage import root_stat_fails

STAMP = "2026-08-12 14-32"
# The folder main.py hands the store: the one the projects feature keeps from being a project.
EXPORTS = name_rules.EXPORTS_DIR


def store_at(path):
    return DrivePhotoStore(Storage(str(path)), EXPORTS)


def project_at(path):
    """A store over a root holding düğün -- a save never opens a project's folder."""
    (path / "düğün").mkdir()
    return store_at(path)


def test_project_exists_follows_the_folder(tmp_path):
    store = store_at(tmp_path)
    (tmp_path / "düğün").mkdir()
    assert store.project_exists("düğün") is True
    assert store.project_exists("yok") is False


def test_next_number_starts_at_zero(tmp_path):
    (tmp_path / "düğün").mkdir()
    assert store_at(tmp_path).next_number("düğün") == 0


def test_delete_removes_the_photo_from_the_project_folder(tmp_path):
    store = project_at(tmp_path)
    store.save("düğün", "P0_0.png", b"PNG")

    store.delete("düğün", "P0_0.png")

    assert list((tmp_path / "düğün").iterdir()) == []


def test_next_number_is_highest_plus_one(tmp_path):
    project = tmp_path / "düğün"
    project.mkdir()
    for name in ("0_a.png", "P7_2.png", "3_b.png", "notlar.txt", "_bozuk.png"):
        (project / name).write_bytes(b"x")
    # Both naming schemes claim numbers: the folder can hold frames from before and after.
    assert store_at(tmp_path).next_number("düğün") == 8


def test_a_layer_file_claims_its_frames_number(tmp_path):
    project = tmp_path / "düğün"
    project.mkdir()
    (project / "P4_0_V1_0.mp4").write_bytes(b"x")
    assert store_at(tmp_path).next_number("düğün") == 5


def test_save_writes_the_file_and_returns_its_name(tmp_path):
    assert project_at(tmp_path).save("düğün", "P4_0.png", b"PNG") == "P4_0.png"
    assert (tmp_path / "düğün" / "P4_0.png").read_bytes() == b"PNG"


def test_a_photo_is_never_saved_into_a_project_that_is_not_there(tmp_path):
    """A project deleted while its run was going must not come back as a folder with one photo."""
    with pytest.raises(FileNotFoundError):
        store_at(tmp_path).save("yok", "P4_0.png", b"PNG")

    assert not (tmp_path / "yok").exists()


def test_photo_dir_is_the_project_folder(tmp_path):
    assert project_at(tmp_path).photo_dir("düğün") == str(tmp_path / "düğün")


def test_a_photos_bytes_can_be_read_back(tmp_path):
    # What a video render hangs on: the picture itself, not its path.
    store = project_at(tmp_path)
    store.save("düğün", "P0_0.png", b"PNGDATA")

    assert store.read("düğün", "P0_0.png") == b"PNGDATA"
    assert store.read("düğün", "yok.png") is None


def export_folder(tmp_path):
    """Beside the projects rather than inside one, named date first and project after, so the
    newest exports stand together in Drive (madde 473)."""
    return tmp_path / EXPORTS / f"{STAMP} düğün"


def test_opening_an_export_opens_the_exports_folder_and_nothing_inside_it(tmp_path):
    """A save never opens a folder directly under the root (madde 472), so the exports folder is
    opened here, once a run. The dated folder is opened by the first file that goes into it."""
    store = project_at(tmp_path)

    assert store.open_export("düğün", STAMP) == str(export_folder(tmp_path))
    assert (tmp_path / EXPORTS).is_dir()
    assert list((tmp_path / EXPORTS).iterdir()) == []


def test_opening_an_export_leaves_the_exports_already_there_alone(tmp_path):
    store = project_at(tmp_path)
    earlier = tmp_path / EXPORTS / "2026-08-11 09-00 nikah"
    earlier.mkdir(parents=True)
    (earlier / "nikah.mp4").write_bytes(b"MP4")

    store.open_export("düğün", STAMP)

    assert (earlier / "nikah.mp4").read_bytes() == b"MP4"


def test_an_export_opened_while_the_mount_is_gone_opens_nothing(tmp_path, monkeypatch):
    """The mount check stands before the folder is made: a dropped mount must not leave an exports
    folder on the machine's own disk."""
    store = project_at(tmp_path)
    root_stat_fails(monkeypatch, str(tmp_path),
                    OSError(errno.ENOTCONN, "Transport endpoint is not connected"))

    with pytest.raises(StorageError):
        store.open_export("düğün", STAMP)

    monkeypatch.undo()
    assert not (tmp_path / EXPORTS).exists()


def test_the_screen_is_told_the_exports_folder_and_nothing_is_opened(tmp_path):
    """What the export screen shows before a run: where exports land. The run's own folder is named
    after the minute it starts, which is not known yet."""
    store = project_at(tmp_path)

    assert store.export_dir() == str(tmp_path / EXPORTS)
    assert not (tmp_path / EXPORTS).exists()


def test_a_save_never_opens_the_exports_folder_itself(tmp_path):
    """Why a run opens it first: it sits directly under the root, where no save opens a folder."""
    store = project_at(tmp_path)
    piece = tmp_path / "01.mp4"
    piece.write_bytes(b"MP4")

    with pytest.raises(FileNotFoundError):
        store.copy_video("düğün", STAMP, str(piece), "01.mp4")

    assert not (tmp_path / EXPORTS).exists()


def export_at(path):
    """A store over a root holding düğün, with an export of it opened the way a run opens one."""
    store = project_at(path)
    store.open_export("düğün", STAMP)
    return store


def test_an_export_lands_beside_the_projects_and_leaves_the_project_alone(tmp_path):
    """Madde 473: "Export dosyaları proje dosyalarının içine değil, ayrı bir klasöre kaydedilsin".
    Inside, nothing changed: foto/, and video/ or the merged file."""
    store = export_at(tmp_path)
    store.save("düğün", "0_a.png", b"PNG")
    piece = tmp_path / "01.mp4"
    piece.write_bytes(b"MP4")

    store.copy_video("düğün", STAMP, str(piece), "01.mp4")
    store.copy_photo("düğün", "0_a.png", STAMP, "01.png")

    assert sorted(path.name for path in export_folder(tmp_path).iterdir()) == ["foto", "video"]
    assert sorted(path.name for path in (tmp_path / "düğün").iterdir()) == ["0_a.png"]


def test_an_old_export_inside_the_project_is_left_where_it_is(tmp_path):
    """Exports written before madde 473 stay in the project's export/ folder: nothing is moved, and
    nothing new goes there."""
    old = tmp_path / "düğün" / "export" / "2026-08-01 10-00"
    (old / "foto").mkdir(parents=True)
    (old / "düğün.mp4").write_bytes(b"OLD")
    store = store_at(tmp_path)
    store.open_export("düğün", STAMP)
    joined = tmp_path / "düğün.mp4"
    joined.write_bytes(b"MP4")

    store.copy_export("düğün", STAMP, str(joined), "düğün.mp4")
    store.remove_export("düğün", STAMP, [], in_use=False)

    assert (old / "düğün.mp4").read_bytes() == b"OLD"
    assert [path.name for path in (tmp_path / "düğün" / "export").iterdir()] == [
        "2026-08-01 10-00"]


def test_a_photo_already_in_the_export_is_not_written_again(tmp_path):
    store = export_at(tmp_path)
    store.save("düğün", "0_a.png", b"PNG")

    store.copy_photo("düğün", "0_a.png", STAMP, "01.png")
    # The design lets a merged export and a separate one run side by side, and a folder named down
    # to the minute is one folder for both. The second one finds the picture already there.
    store.copy_photo("düğün", "0_a.png", STAMP, "01.png")

    # The name the user sees in Drive, so it reads in Turkish like the rest of what they see
    # (madde 283, their own naming). Older exports keep the folder they were written with.
    landed = export_folder(tmp_path) / "foto" / "01.png"
    assert landed.read_bytes() == b"PNG"
    assert [path.name for path in landed.parent.iterdir()] == ["01.png"]


def test_a_separate_exports_videos_get_a_folder_of_their_own(tmp_path):
    """The dated folder held 22 videos beside the photos folder, and the user asked for them
    gathered: "tekli ve çok videolar için klasör açalım" (madde 283). Each arrives from the machine
    whole, and nothing half written is left beside it."""
    store = export_at(tmp_path)
    piece = tmp_path / "01.mp4"
    piece.write_bytes(b"MP4")

    store.copy_video("düğün", STAMP, str(piece), "01.mp4")

    landed = export_folder(tmp_path) / "video" / "01.mp4"
    assert landed.read_bytes() == b"MP4"
    assert [path.name for path in landed.parent.iterdir()] == ["01.mp4"]


def test_the_merged_file_is_copied_into_the_export_folder(tmp_path):
    """The join is written on the machine's own disk and comes here whole (madde 282). Landing in
    one save matters more here than anywhere: Drive is slow, so the window in which a half written
    file could be seen is a real one, and a folder that looks finished is what madde 94 forbids."""
    store = export_at(tmp_path)
    joined = tmp_path / "düğün.mp4"
    joined.write_bytes(b"MP4")

    store.copy_export("düğün", STAMP, str(joined), "düğün.mp4")

    landed = export_folder(tmp_path) / "düğün.mp4"
    assert landed.read_bytes() == b"MP4"
    # Nothing half written and nothing left over: the folder holds the file and nothing else.
    assert [path.name for path in landed.parent.iterdir()] == ["düğün.mp4"]
    assert not any(path.name.startswith(TEMP_PREFIX) for path in landed.parent.iterdir())


def a_piece(tmp_path, name="01.mp4", data=b"MP4"):
    """A file standing where ffmpeg would leave one on the machine's own disk."""
    piece = tmp_path / name
    piece.write_bytes(data)
    return str(piece)


def half_separate_export(tmp_path):
    """An export store whose separate run has carried one video and one picture to Drive."""
    store = export_at(tmp_path)
    store.save("düğün", "0_a.png", b"PNG")
    store.copy_video("düğün", STAMP, a_piece(tmp_path), "01.mp4")
    store.copy_photo("düğün", "0_a.png", STAMP, "01.png")
    return store


def test_an_export_that_did_not_finish_alone_takes_its_folder_and_nothing_else(tmp_path):
    """Nobody else wrote into the folder, so nothing in it is anybody's: half an export is worse
    than none (madde 94)."""
    store = half_separate_export(tmp_path)

    store.remove_export("düğün", STAMP, ["01.mp4"], in_use=False)

    assert not export_folder(tmp_path).exists()
    # The exports folder is every export's, and stays.
    assert (tmp_path / EXPORTS).is_dir()
    assert (tmp_path / "düğün" / "0_a.png").read_bytes() == b"PNG"


def test_a_merged_export_that_did_not_finish_alone_leaves_nothing_behind(tmp_path):
    """A merged run has nothing of its own on Drive but the photos when it fails or is cancelled --
    its join goes up last, in one save -- and with nobody else in the folder they go too."""
    store = export_at(tmp_path)
    store.save("düğün", "0_a.png", b"PNG")
    store.copy_photo("düğün", "0_a.png", STAMP, "01.png")

    store.remove_export("düğün", STAMP, [], in_use=False)

    assert list((tmp_path / EXPORTS).iterdir()) == []


def test_a_failed_separate_export_leaves_the_merged_one_beside_it(tmp_path):
    """Madde 474: the two modes share a folder named down to the minute, and the cleanup used to
    take the whole of it. The merged file is the other export's, and the photos are the folder's:
    the merged export found them there and counts on them."""
    store = half_separate_export(tmp_path)
    store.copy_export("düğün", STAMP, a_piece(tmp_path, "birlesik.mp4", b"JOINED"), "düğün.mp4")

    store.remove_export("düğün", STAMP, ["01.mp4"], in_use=False)

    folder = export_folder(tmp_path)
    assert sorted(path.name for path in folder.iterdir()) == ["düğün.mp4", "foto"]
    assert (folder / "düğün.mp4").read_bytes() == b"JOINED"
    assert (folder / "foto" / "01.png").read_bytes() == b"PNG"


def test_a_failed_merged_export_leaves_the_separate_one_beside_it(tmp_path):
    """A merged run never has a file of its own on Drive when it fails -- its join goes up last, in
    one save -- so it takes nothing, and the separate export's videos say the photos are needed."""
    store = half_separate_export(tmp_path)

    store.remove_export("düğün", STAMP, [], in_use=False)

    folder = export_folder(tmp_path)
    assert (folder / "video" / "01.mp4").read_bytes() == b"MP4"
    assert (folder / "foto" / "01.png").read_bytes() == b"PNG"


def test_the_photos_stay_while_the_other_export_is_writing_into_the_folder(tmp_path):
    """A merged export still running has nothing on Drive but the photos it shares: only the
    runner knows it is there, and says so through in_use."""
    store = half_separate_export(tmp_path)

    store.remove_export("düğün", STAMP, ["01.mp4"], in_use=True)

    folder = export_folder(tmp_path)
    assert sorted(path.name for path in folder.iterdir()) == ["foto"]
    assert (folder / "foto" / "01.png").read_bytes() == b"PNG"


def test_the_pieces_are_cut_off_drive(tmp_path):
    """Drive is the slow disk, and the pieces are scaffolding -- so they are cut on the machine's
    own disk (madde 235), in both modes since 472."""
    store = project_at(tmp_path)

    pieces = store.make_pieces_dir()

    assert os.path.isdir(pieces)
    assert not pieces.startswith(str(tmp_path))
    assert store.piece_path(pieces, "01.mp4") == os.path.join(pieces, "01.mp4")
    store.remove_pieces(pieces)
    assert not os.path.exists(pieces)
