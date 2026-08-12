import json

from backend.features.photo_generation.data.plan_store import DrivePlanStore
from backend.services.drive.storage import DriveStorage

FRAMES = [
    {"id": "P3_0", "number": 3, "variant": 0, "prompt": "kraliçe tahtta", "negative": "bulanık",
     "seed": 11, "model": "nova.safetensors"},
    {"id": "P4_0", "number": 4, "variant": 0, "prompt": "kraliçe balkonda", "negative": "bulanık",
     "seed": 22, "model": "nova.safetensors"},
]


def store_at(path):
    return DrivePlanStore(DriveStorage(str(path)))


def test_append_then_read_round_trips(tmp_path):
    store = store_at(tmp_path)
    store.append("düğün", FRAMES)
    assert store.read("düğün")["frames"] == FRAMES


def test_a_frame_planned_before_identities_keeps_the_one_it_was_born_with(tmp_path):
    # Renaming is never done, so the gallery order pointing at "0_a" has to keep finding it.
    (tmp_path / "düğün").mkdir()
    (tmp_path / "düğün" / "plan.json").write_text(json.dumps({"frames": [
        {"number": 0, "letter": "a", "prompt": "eski", "negative": "n", "seed": 1}]}),
        encoding="utf-8")

    assert store_at(tmp_path).read("düğün")["frames"][0]["id"] == "0_a"


def test_a_frame_planned_before_models_reads_back_without_one(tmp_path):
    # Empty means "the graph's own checkpoint" -- those frames render exactly as they always did.
    (tmp_path / "düğün").mkdir()
    (tmp_path / "düğün" / "plan.json").write_text(json.dumps({"frames": [
        {"number": 0, "letter": "a", "prompt": "eski", "negative": "n", "seed": 1}]}),
        encoding="utf-8")

    assert store_at(tmp_path).read("düğün")["frames"][0]["model"] == ""


def test_reading_a_project_without_a_plan_gives_no_frames(tmp_path):
    assert store_at(tmp_path).read("düğün") == {"negative": "", "frames": []}


def test_append_puts_frames_at_the_end_of_the_queue(tmp_path):
    store = store_at(tmp_path)
    store.append("düğün", FRAMES)
    store.append("düğün", [{"number": 9, "letter": "a", "prompt": "sonradan", "negative": "",
                            "seed": 1}])
    assert [f["prompt"] for f in store.read("düğün")["frames"]] == [
        "kraliçe tahtta", "kraliçe balkonda", "sonradan"]


def test_each_frame_keeps_its_own_negative(tmp_path):
    store = store_at(tmp_path)
    store.append("düğün", [{"number": 0, "letter": "a", "prompt": "p", "negative": "n1",
                            "seed": 1}])
    store.append("düğün", [{"number": 1, "letter": "a", "prompt": "p", "negative": "n2",
                            "seed": 2}])
    assert [f["negative"] for f in store.read("düğün")["frames"]] == ["n1", "n2"]


def test_a_plan_written_before_per_frame_negatives_falls_back_to_the_old_field(tmp_path):
    # What the projects already on Drive look like: one negative for the whole plan.
    (tmp_path / "düğün").mkdir()
    (tmp_path / "düğün" / "plan.json").write_text(json.dumps(
        {"negative": "eski", "frames": [{"number": 0, "letter": "a", "prompt": "p", "seed": 1}]}),
        encoding="utf-8")
    assert store_at(tmp_path).read("düğün")["frames"][0]["negative"] == "eski"


def test_max_number_is_the_highest_the_plan_reserved(tmp_path):
    store = store_at(tmp_path)
    store.append("düğün", FRAMES)
    assert store.max_number("düğün") == 4


def test_max_number_counts_everything_the_queue_ever_reserved(tmp_path):
    store = store_at(tmp_path)
    store.append("düğün", FRAMES)
    store.append("düğün", [{"number": 9, "letter": "a", "prompt": "p", "negative": "", "seed": 1}])
    assert store.max_number("düğün") == 9


def test_max_number_is_none_without_a_plan(tmp_path):
    assert store_at(tmp_path).max_number("düğün") is None


def test_an_unreadable_plan_reserves_nothing(tmp_path):
    (tmp_path / "düğün").mkdir()
    (tmp_path / "düğün" / "plan.json").write_text("{ yarım", encoding="utf-8")
    store = store_at(tmp_path)
    assert store.read("düğün") == {"negative": "", "frames": []}
    assert store.max_number("düğün") is None


def test_turkish_text_survives_the_round_trip(tmp_path):
    store = store_at(tmp_path)
    store.append("düğün", [{"number": 0, "letter": "a", "prompt": "kraliçe bahçede, şövalyeler",
                            "negative": "çirkin", "seed": 1}])
    assert store.read("düğün")["frames"][0]["prompt"] == "kraliçe bahçede, şövalyeler"
