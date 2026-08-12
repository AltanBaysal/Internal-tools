import json

from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.services.drive.storage import DriveStorage


def record_at(path):
    return DrivePhotoRecord(DriveStorage(str(path)))


def entry(file, prompt="kraliçe tahtta"):
    return {"file": file, "prompt": prompt, "negative": "bulanık", "seed": 11,
            "createdAt": "2026-08-03T14:32:11+00:00"}


class CountingStorage(DriveStorage):
    """A real storage that says how many times the file was actually opened."""

    def __init__(self, root):
        super().__init__(root)
        self.reads = 0

    def read_lines(self, subdir, name):
        self.reads += 1
        return super().read_lines(subdir, name)


def test_a_project_without_a_record_lists_nothing(tmp_path):
    assert record_at(tmp_path).list("düğün") == []


def test_the_three_questions_cost_one_read(tmp_path):
    # The gallery asks all three on every poll, and the file is the same file. Opening and parsing
    # it once per question is what made a poll five Drive reads.
    storage = CountingStorage(str(tmp_path))
    record = DrivePhotoRecord(storage)
    record.append("düğün", entry("P0_0.png"))
    storage.reads = 0

    record.slots("düğün")
    record.list("düğün")
    record.prompts("düğün")

    assert storage.reads == 1


def test_a_changed_record_is_read_again(tmp_path):
    storage = CountingStorage(str(tmp_path))
    record = DrivePhotoRecord(storage)
    record.append("düğün", entry("P0_0.png"))
    record.slots("düğün")

    record.append("düğün", entry("P1_0.png"))

    assert [row["file"] for row in record.list("düğün")] == ["P1_0.png", "P0_0.png"]


def test_one_project_never_answers_for_another(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", entry("P0_0.png"))
    record.append("nişan", entry("P9_0.png"))

    assert [row["file"] for row in record.list("düğün")] == ["P0_0.png"]
    assert [row["file"] for row in record.list("nişan")] == ["P9_0.png"]


def test_prompts_are_folded_per_layer(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", {"file": "P0_0.png", "frame": "P0_0", "layer": "photo",
                            "status": "done", "prompt": "kırmızı elbise"})
    record.append("düğün", {"file": "P0_0_V1_0.mp4", "frame": "P0_0", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})

    assert record.prompts("düğün") == {"P0_0": {"photo": "kırmızı elbise",
                                                "video": "kadın dönüyor"}}


def test_a_failure_line_keeps_its_reason(tmp_path):
    # Why the slot is red travels with it: the detail page prints the renderer's own sentence.
    record = record_at(tmp_path)
    record.mark("düğün", "P0_0", "photo", "P0_0.png", "failed", "t", error="CUDA — 3 kez denendi")

    assert record.slots("düğün")["P0_0"]["photo"] == {
        "status": "failed", "file": "P0_0.png", "error": "CUDA — 3 kez denendi"}


def test_a_line_with_no_reason_carries_none(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", entry("P0_0.png"))

    assert record.slots("düğün")["P0_0"]["photo"] == {"status": "done", "file": "P0_0.png"}


def test_appended_photos_come_back_newest_first(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", entry("0_a.png"))
    record.append("düğün", entry("0_b.png"))
    assert [row["file"] for row in record.list("düğün")] == ["0_b.png", "0_a.png"]


def test_a_row_keeps_every_field_it_was_given(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", entry("0_a.png"))
    row = record.list("düğün")[0]
    # The frame the row belongs to is answered on the way out; nothing given is dropped.
    assert {key: row[key] for key in entry("0_a.png")} == entry("0_a.png")


def test_turkish_text_survives_the_round_trip(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", entry("0_a.png", prompt="kraliçe bahçede, şövalyeler"))
    assert record.list("düğün")[0]["prompt"] == "kraliçe bahçede, şövalyeler"


def test_a_half_written_last_line_does_not_hide_the_rest(tmp_path):
    # What a session death leaves behind: the line being appended is cut off.
    record = record_at(tmp_path)
    record.append("düğün", entry("0_a.png"))
    with open(tmp_path / "düğün" / "photos.jsonl", "a", encoding="utf-8") as f:
        f.write('{"file": "0_b.pn')
    assert [row["file"] for row in record.list("düğün")] == ["0_a.png"]


def test_a_deleted_photo_leaves_the_list_but_not_the_file(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", entry("0_a.png"))
    record.append("düğün", entry("0_b.png"))

    record.mark("düğün", "0_a", "photo", "0_a.png", "deleted", "2026-08-05T10:00:00+00:00")

    assert [row["file"] for row in record.list("düğün")] == ["0_b.png"]
    # The log is only ever appended to: the original row is still in the file.
    lines = (tmp_path / "düğün" / "photos.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3


def test_the_record_remembers_the_numbers_of_deleted_photos(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", entry("7_a.png"))
    record.mark("düğün", "7_a", "photo", "7_a.png", "deleted", "2026-08-05T10:00:00+00:00")

    assert record.max_number("düğün") == 7


def test_an_empty_record_claims_no_number(tmp_path):
    assert record_at(tmp_path).max_number("düğün") is None


def test_rows_without_a_file_name_are_skipped(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", {"prompt": "adı yok"})
    record.append("düğün", entry("0_a.png"))
    assert [row["file"] for row in record.list("düğün")] == ["0_a.png"]


def photo_statuses(record, project="düğün"):
    """{frame: photo slot status} -- the one slot most of these tests are about."""
    return {frame: cells["photo"]["status"]
            for frame, cells in record.slots(project).items() if "photo" in cells}


def test_the_latest_line_about_a_slot_wins(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", {**entry("0_a.png"), "status": "done"})
    record.mark("düğün", "1_a", "photo", "1_a.png", "failed", "t2", error="ComfyUI 500")
    record.mark("düğün", "0_a", "photo", "0_a.png", "deleted", "t3")

    assert photo_statuses(record) == {"0_a": "deleted", "1_a": "failed"}


def test_a_failure_line_carries_the_servers_own_words(tmp_path):
    record = record_at(tmp_path)
    record.mark("düğün", "1_a", "photo", "1_a.png", "failed", "t2",
                error="ComfyUI 500: out of memory")

    line = (tmp_path / "düğün" / "photos.jsonl").read_text(encoding="utf-8").splitlines()[0]
    assert json.loads(line)["error"] == "ComfyUI 500: out of memory"


def test_a_line_without_an_error_carries_no_error_field(tmp_path):
    record = record_at(tmp_path)
    record.mark("düğün", "1_a", "photo", "1_a.png", "removed", "t2")

    line = (tmp_path / "düğün" / "photos.jsonl").read_text(encoding="utf-8").splitlines()[0]
    assert "error" not in json.loads(line)


def test_lines_written_before_the_status_field_still_read(tmp_path):
    # What the projects already on Drive look like: a photo row and a deletion row, no status.
    record = record_at(tmp_path)
    record.append("düğün", entry("0_a.png"))
    record.append("düğün", entry("1_a.png"))
    record.append("düğün", {"file": "1_a.png", "deletedAt": "t3"})

    assert photo_statuses(record) == {"0_a": "done", "1_a": "deleted"}
    assert [row["file"] for row in record.list("düğün")] == ["0_a.png"]


def test_only_produced_frames_are_photos(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", {**entry("0_a.png"), "status": "done"})
    record.mark("düğün", "1_a", "photo", "1_a.png", "removed", "t2")
    record.mark("düğün", "2_a", "photo", "2_a.png", "failed", "t3")

    assert [row["file"] for row in record.list("düğün")] == ["0_a.png"]


def test_a_frame_pulled_out_of_the_queue_still_claims_its_number(tmp_path):
    record = record_at(tmp_path)
    record.mark("düğün", "7_a", "photo", "7_a.png", "removed", "t1")

    assert record.max_number("düğün") == 7


def test_a_video_line_does_not_answer_for_its_frames_photo(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", {**entry("0_a.png"), "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "failed"})

    # The photo is still there; only the video blew up.
    assert photo_statuses(record) == {"0_a": "done"}


def test_slots_fold_the_latest_line_per_frame_and_layer(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", {**entry("0_a.png"), "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})
    record.mark("düğün", "0_a", "video", "0_a_v0.mp4", "deleted", "t3")

    assert record.slots("düğün") == {
        "0_a": {"photo": {"status": "done", "file": "0_a.png"},
                "video": {"status": "deleted", "file": "0_a_v0.mp4"}}}


def test_two_frames_over_one_file_close_independently(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo",
                            "status": "done"})
    record.append("düğün", {"file": "0_a.png", "frame": "0_a_c1", "layer": "photo",
                            "status": "done"})
    record.mark("düğün", "0_a", "photo", "0_a.png", "deleted", "t3")

    slots = record.slots("düğün")
    assert slots["0_a"]["photo"]["status"] == "deleted"
    assert slots["0_a_c1"]["photo"]["status"] == "done"


def test_lines_without_a_frame_or_layer_are_photos_of_their_own_frame(tmp_path):
    # What the projects already on Drive look like: no frame field, no layer field.
    record = record_at(tmp_path)
    record.append("düğün", entry("0_a.png"))

    assert record.slots("düğün") == {"0_a": {"photo": {"status": "done", "file": "0_a.png"}}}


def test_the_photo_list_follows_the_frame_not_the_file(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo",
                            "status": "done"})
    record.append("düğün", {"file": "0_a.png", "frame": "0_a_c1", "layer": "photo",
                            "status": "done"})
    record.mark("düğün", "0_a", "photo", "0_a.png", "deleted", "t3")

    # One frame let go of the picture; the other still shows it.
    assert [row["frame"] for row in record.list("düğün")] == ["0_a_c1"]


def test_a_video_line_is_not_a_photo(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", {**entry("0_a.png"), "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})

    assert [row["file"] for row in record.list("düğün")] == ["0_a.png"]
