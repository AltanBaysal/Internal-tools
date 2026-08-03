from backend.features.photo_generation.data.plan_store import DrivePlanStore
from backend.services.drive.storage import DriveStorage

FRAMES = [
    {"number": 3, "letter": "a", "prompt": "kraliçe tahtta", "seed": 11},
    {"number": 4, "letter": "a", "prompt": "kraliçe balkonda", "seed": 22},
]


def store_at(path):
    return DrivePlanStore(DriveStorage(str(path)))


def test_write_then_read_round_trips(tmp_path):
    store = store_at(tmp_path)
    store.write("düğün", "bulanık", FRAMES)
    assert store.read("düğün") == {"negative": "bulanık", "frames": FRAMES}


def test_reading_a_project_without_a_plan_gives_no_frames(tmp_path):
    assert store_at(tmp_path).read("düğün") == {"negative": "", "frames": []}


def test_a_new_plan_replaces_the_previous_one(tmp_path):
    store = store_at(tmp_path)
    store.write("düğün", "eski", FRAMES)
    store.write("düğün", "yeni", [{"number": 9, "letter": "a", "prompt": "x", "seed": 1}])
    assert store.read("düğün")["frames"] == [
        {"number": 9, "letter": "a", "prompt": "x", "seed": 1}]


def test_max_number_is_the_highest_the_plan_reserved(tmp_path):
    store = store_at(tmp_path)
    store.write("düğün", "", FRAMES)
    assert store.max_number("düğün") == 4


def test_max_number_is_none_without_a_plan(tmp_path):
    assert store_at(tmp_path).max_number("düğün") is None


def test_an_unreadable_plan_reserves_nothing(tmp_path):
    (tmp_path / "düğün").mkdir()
    (tmp_path / "düğün" / "plan.json").write_text("{ yarım", encoding="utf-8")
    store = store_at(tmp_path)
    assert store.read("düğün") == {"negative": "", "frames": []}
    assert store.max_number("düğün") is None
