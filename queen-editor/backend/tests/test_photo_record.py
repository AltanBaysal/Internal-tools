from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.services.drive.storage import DriveStorage


def record_at(path):
    return DrivePhotoRecord(DriveStorage(str(path)))


def entry(file, prompt="kraliçe tahtta"):
    return {"file": file, "prompt": prompt, "negative": "bulanık", "seed": 11,
            "createdAt": "2026-08-03T14:32:11+00:00"}


def test_a_project_without_a_record_lists_nothing(tmp_path):
    assert record_at(tmp_path).list("düğün") == []


def test_appended_photos_come_back_newest_first(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", entry("0_a.png"))
    record.append("düğün", entry("0_b.png"))
    assert [row["file"] for row in record.list("düğün")] == ["0_b.png", "0_a.png"]


def test_a_row_keeps_every_field_it_was_given(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", entry("0_a.png"))
    assert record.list("düğün")[0] == entry("0_a.png")


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

    record.mark_deleted("düğün", "0_a.png", "2026-08-05T10:00:00+00:00")

    assert [row["file"] for row in record.list("düğün")] == ["0_b.png"]
    # The log is only ever appended to: the original row is still in the file.
    lines = (tmp_path / "düğün" / "photos.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3


def test_the_record_remembers_the_numbers_of_deleted_photos(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", entry("7_a.png"))
    record.mark_deleted("düğün", "7_a.png", "2026-08-05T10:00:00+00:00")

    assert record.max_number("düğün") == 7


def test_an_empty_record_claims_no_number(tmp_path):
    assert record_at(tmp_path).max_number("düğün") is None


def test_rows_without_a_file_name_are_skipped(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", {"prompt": "adı yok"})
    record.append("düğün", entry("0_a.png"))
    assert [row["file"] for row in record.list("düğün")] == ["0_a.png"]
