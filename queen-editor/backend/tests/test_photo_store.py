import os

import pytest

from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.services.storage.storage import TEMP_PREFIX, Storage

STAMP = "2026-08-12 14-32"


def store_at(path):
    return DrivePhotoStore(Storage(str(path)))


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
    return tmp_path / "düğün" / "export" / STAMP


def test_naming_the_export_folder_opens_nothing(tmp_path):
    """The screen is told where the export lands before anything is written; the folder is opened
    by the first file that goes into it."""
    store = project_at(tmp_path)

    assert store.export_folder("düğün", STAMP) == str(export_folder(tmp_path))
    assert store.export_dir("düğün") == str(tmp_path / "düğün" / "export")
    assert not (tmp_path / "düğün" / "export").exists()


def test_a_photo_already_in_the_export_is_not_written_again(tmp_path):
    store = project_at(tmp_path)
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
    store = project_at(tmp_path)
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
    store = project_at(tmp_path)
    joined = tmp_path / "düğün.mp4"
    joined.write_bytes(b"MP4")

    store.copy_export("düğün", STAMP, str(joined), "düğün.mp4")

    landed = export_folder(tmp_path) / "düğün.mp4"
    assert landed.read_bytes() == b"MP4"
    # Nothing half written and nothing left over: the folder holds the file and nothing else.
    assert [path.name for path in landed.parent.iterdir()] == ["düğün.mp4"]
    assert not any(path.name.startswith(TEMP_PREFIX) for path in landed.parent.iterdir())


def test_an_export_that_did_not_finish_takes_its_folder_and_nothing_else(tmp_path):
    store = project_at(tmp_path)
    store.save("düğün", "0_a.png", b"PNG")
    store.copy_photo("düğün", "0_a.png", STAMP, "01.png")

    store.remove_export("düğün", STAMP)

    assert not export_folder(tmp_path).exists()
    assert (tmp_path / "düğün" / "0_a.png").read_bytes() == b"PNG"


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
