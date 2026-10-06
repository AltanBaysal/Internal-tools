"""The queue rule: the plan minus the jobs that already settled, type by type."""
from backend.features.photo_generation.domain import layers, production_mode, queue
from backend.features.photo_generation.domain.photo_name import frame_id
from backend.features.photo_generation.domain.usecases.retry_frame import retry_frame
from backend.tests.test_photo_usecases import (
    FakeGenerator,
    ask_again,
    drop_the_video,
    frame_with_a_photo,
    idle_runner,
    sync_runner,
)
from backend.tests.test_video_length import at, red_videos


def job(number, kind=layers.PHOTO, variant=0):
    return {"id": frame_id(number, variant), "type": kind, "number": number, "variant": variant,
            "prompt": "p", "negative": "", "seed": 1}


def slots(**pairs):
    """photo_P0_0="done" -> the record's own {frame: {slot: {"status", "file"}}} shape."""
    folded = {}
    for key, status in pairs.items():
        kind, _, frame = key.partition("_")
        folded.setdefault(frame, {})[kind] = {"status": status, "file": f"{frame}.x"}
    return folded


def test_a_job_with_no_line_is_still_owed():
    assert queue.open_jobs([job(0), job(1)], {}) == [job(0), job(1)]


def test_a_finished_job_is_not_owed_again():
    assert queue.open_jobs([job(0), job(1)], slots(photo_P0_0="done")) == [job(1)]


def test_a_failed_job_is_not_retried_on_its_own():
    assert queue.open_jobs([job(0)], slots(photo_P0_0="failed")) == []


def test_a_job_pulled_out_of_the_queue_is_not_owed():
    assert queue.open_jobs([job(0)], slots(photo_P0_0="removed")) == []


def test_a_deleted_photo_does_not_fall_back_into_the_queue():
    assert queue.open_jobs([job(0)], slots(photo_P0_0="deleted")) == []


def test_queued_reopens_a_settled_job():
    assert queue.open_jobs([job(0)], slots(photo_P0_0="queued")) == [job(0)]


def test_photos_come_before_videos():
    jobs = [job(0, layers.VIDEO), job(1, layers.PHOTO)]
    assert [j["type"] for j in queue.open_jobs(jobs, {})] == ["photo", "video"]


def test_videos_come_before_audio():
    jobs = [job(0, layers.AUDIO), job(1, layers.VIDEO)]
    assert [j["type"] for j in queue.open_jobs(jobs, {})] == ["video", "audio"]


def test_a_type_is_finished_before_the_next_one_starts():
    jobs = [job(0, layers.PHOTO), job(1, layers.VIDEO), job(2, layers.PHOTO)]
    assert queue.next_job(jobs, {})["id"] == "P0_0"
    assert queue.next_job(jobs, slots(photo_P0_0="done"))["id"] == "P2_0"
    done_photos = slots(photo_P0_0="done", photo_P2_0="done")
    assert queue.next_job(jobs, done_photos)["id"] == "P1_0"


def test_plan_order_is_kept_inside_a_type():
    assert [j["id"] for j in queue.open_jobs([job(1), job(0)], {})] == ["P1_0", "P0_0"]


def test_a_requeued_job_waits_behind_the_ones_that_never_ran():
    jobs = [job(0), job(1)]
    assert [j["id"] for j in queue.open_jobs(jobs, slots(photo_P0_0="queued"))] == \
        ["P1_0", "P0_0"]


def test_a_type_is_done_in_the_gallery_s_own_order_read_from_the_bottom():
    # The gallery is newest-first, so its bottom is what gets produced first.
    jobs = [job(0), job(1), job(2)]
    order = ["P1_0", "P0_0", "P2_0"]          # what the user dragged, top first

    owed = queue.open_jobs(jobs, {}, order)

    assert [j["id"] for j in owed] == ["P2_0", "P0_0", "P1_0"]


def test_a_job_the_order_file_never_heard_of_waits_at_the_end():
    jobs = [job(0), job(1), job(2)]

    owed = queue.open_jobs(jobs, {}, ["P1_0"])

    # P1_0 is placed; the other two keep the plan's own sequence behind it.
    assert [j["id"] for j in owed] == ["P1_0", "P0_0", "P2_0"]


def test_a_requeued_job_stays_behind_fresh_work_wherever_the_gallery_puts_it():
    jobs = [job(0), job(1)]
    order = ["P1_0", "P0_0"]                  # P0_0 sits at the foot, so it would go first

    owed = queue.open_jobs(jobs, slots(photo_P0_0="queued"), order)

    assert [j["id"] for j in owed] == ["P1_0", "P0_0"]


def test_the_gallery_cannot_pull_a_video_ahead_of_the_photos():
    jobs = [job(0, layers.PHOTO), job(1, layers.VIDEO)]

    owed = queue.open_jobs(jobs, {}, ["P0_0", "P1_0"])

    assert [j["type"] for j in owed] == ["photo", "video"]


def test_one_frames_slots_are_owed_separately():
    # The photo landed; the video that hangs on it is still owed.
    jobs = [{"id": "P0_0", "type": "photo"}, {"id": "P0_0", "type": "video"}]
    assert [j["type"] for j in queue.open_jobs(jobs, slots(photo_P0_0="done"))] == ["video"]


def test_a_job_without_a_type_is_a_photo_job():
    # What every plan on Drive holds today.
    assert queue.open_jobs([{"id": "P0_0"}], slots(photo_P0_0="done")) == []


def test_next_job_is_none_when_the_queue_is_empty():
    assert queue.next_job([job(0)], slots(photo_P0_0="done")) is None


def test_counts_are_read_from_the_slots():
    jobs = [job(0), job(1), job(2)]
    taken = slots(photo_P0_0="done", photo_P1_0="failed")
    assert queue.counts(jobs, taken) == {"total": 3, "done": 1, "failed": 1,
                                         "failures": ["P1_0.png"]}


# --- Each job counted once (madde 429) -----------------------------------------------------------

def test_a_job_planned_twice_is_counted_once():
    """Madde 429: a layer dropped and asked for again (madde 211), or a red video sent back at a new
    length (422), leaves two plan lines for one job. The engine makes it once, from its latest line,
    and the numbers count it once too. A frame's photo and its video stay two jobs."""
    jobs = [job(0), job(0, layers.VIDEO), job(0, layers.VIDEO)]
    taken = slots(photo_P0_0="done", video_P0_0="done")

    assert queue.counts(jobs, taken) == {"total": 2, "done": 2, "failed": 0, "failures": []}


def test_a_failed_job_planned_twice_is_one_failure():
    jobs = [job(0), job(0, layers.VIDEO), job(0, layers.VIDEO)]
    taken = slots(photo_P0_0="done", video_P0_0="failed")

    assert queue.counts(jobs, taken) == {"total": 2, "done": 1, "failed": 1,
                                         "failures": ["P0_0.png"]}


def numbers(runner):
    """What the queue panel is told once the run is through."""
    state = runner.status()
    return {key: state[key] for key in ("total", "done", "failed", "failures")}


def test_a_video_dropped_and_asked_for_again_is_counted_once():
    """Madde 211's steps: a video asked for, dropped while still owed, and a loop asked for in its
    place. The plan keeps the dropped one's line beside the new one."""
    store, record, plan_store = frame_with_a_photo()
    ask_again(store, record, plan_store, layers.VIDEO, FakeGenerator(), runner=idle_runner())
    drop_the_video(store, record, plan_store)
    runner = sync_runner()

    ask_again(store, record, plan_store, layers.VIDEO, FakeGenerator(),
              mode=production_mode.LOOP, runner=runner)

    assert numbers(runner) == {"total": 2, "done": 2, "failed": 0, "failures": []}


def test_a_red_video_sent_back_at_a_new_length_is_counted_once():
    """Madde 422: Tekrar dene writes a red video's line again at the project's length now."""
    store, record, plan_store = red_videos(0, seconds=4)
    runner = sync_runner()

    retry_frame(runner, store, record, plan_store, {layers.VIDEO: FakeGenerator()},
                lambda: "t", "düğün", "0_a", length=at(12))

    assert numbers(runner) == {"total": 2, "done": 2, "failed": 0, "failures": []}


def test_a_red_video_that_fails_again_at_a_new_length_is_one_failure():
    store, record, plan_store = red_videos(0, seconds=4)
    runner = sync_runner()

    retry_frame(runner, store, record, plan_store,
                {layers.VIDEO: FakeGenerator(fail_on=["kadın dönüyor"])},
                lambda: "t", "düğün", "0_a", length=at(12))

    assert numbers(runner) == {"total": 2, "done": 1, "failed": 1, "failures": ["0_a.png"]}
