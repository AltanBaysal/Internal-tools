import pytest

from backend.features.photo_generation.runner import PhotoRunner


def sync_runner():
    """spawn=lambda fn: fn() runs the job inline -- the test needs no thread and no sleep."""
    return PhotoRunner(spawn=lambda fn: fn())


def test_starts_idle():
    assert PhotoRunner().status() == {"status": "idle"}


def test_the_jobs_summary_becomes_the_state():
    runner = sync_runner()
    assert runner.start("düğün", lambda: {"status": "done", "done": 6, "failed": 0, "total": 6}) is True
    assert runner.status() == {"status": "done", "project": "düğün",
                               "done": 6, "failed": 0, "total": 6}


def test_the_runner_follows_a_project_that_was_renamed_under_it():
    # The screen compares the status's project with its own, so a stale stamp would hide a run from
    # the very page watching it.
    runner = PhotoRunner(spawn=lambda fn: None)
    runner.start("düğün", lambda: {"status": "done"})

    runner.rename("düğün", "nikah")

    assert runner.status()["project"] == "nikah"


def test_report_updates_progress_while_the_job_runs():
    runner = sync_runner()
    seen = []

    def job():
        runner.report({"done": 0, "total": 2, "current": {"number": 3, "letter": "a"}})
        seen.append(runner.status())
        return {"status": "done", "done": 2, "failed": 0, "total": 2}

    runner.start("düğün", job)
    assert seen[0] == {"status": "running", "project": "düğün", "done": 0, "total": 2,
                       "current": {"number": 3, "letter": "a"}}


def test_report_after_the_job_ended_is_ignored():
    # A late report from a dead thread must not resurrect "running".
    runner = sync_runner()
    runner.start("düğün", lambda: {"status": "done", "done": 1, "failed": 0, "total": 1})
    runner.report({"done": 99})
    assert runner.status()["status"] == "done" and runner.status()["done"] == 1


def test_unexpected_exception_becomes_error_with_the_real_message():
    runner = sync_runner()

    def boom():
        raise RuntimeError("ComfyUI öldü")

    runner.start("düğün", boom)
    state = runner.status()
    assert state["status"] == "error" and state["error"] == "ComfyUI öldü"


def test_second_start_is_refused_while_running():
    runner = PhotoRunner(spawn=lambda fn: None)   # never runs -> stays "running"
    assert runner.start("düğün", lambda: {"status": "done"}) is True
    assert runner.status()["status"] == "running"
    assert runner.start("düğün", lambda: {"status": "done"}) is False


def test_a_finished_job_does_not_block_the_next_one():
    runner = sync_runner()
    runner.start("düğün", lambda: {"status": "done", "done": 1, "failed": 0, "total": 1})
    assert runner.start("düğün", lambda: {"status": "done", "done": 2, "failed": 0, "total": 2}) is True
    assert runner.status()["done"] == 2


def test_the_job_sees_the_stop_request():
    runner = sync_runner()
    runner.request_stop()
    seen = []

    def job():
        seen.append(runner.stop_requested())
        return {"status": "stopped"}

    runner.start("düğün", job)
    assert seen == [False], "start must clear a stale stop flag"


def ending_runner():
    """A runner that says when the queue ended (madde 509): what it said, each with the status the
    runner stood at as it said it, and the runner."""
    told = []
    runner = PhotoRunner(spawn=lambda fn: fn(),
                         ended=lambda state: told.append((state, runner.status())))
    return told, runner


def test_a_job_that_drained_the_queue_says_so_once_its_status_is_written():
    """The loop answers done only once nothing is owed. The status comes first, so a screen that
    hears the news and asks /api/status reads done."""
    told, runner = ending_runner()

    runner.start("düğün", lambda: {"status": "done", "done": 2, "failed": 0, "total": 2})

    done = {"status": "done", "project": "düğün", "done": 2, "failed": 0, "total": 2}
    assert told == [(done, done)]


@pytest.mark.parametrize("summary", [
    {"status": "error", "error": "ComfyUI cevap vermedi.\nTimeout"},
    {"status": "waiting", "waitingFor": "video"},
], ids=["error", "waiting"])
def test_a_queue_that_stopped_with_work_owed_says_so_too(summary):
    """The user, 29 Ekim -- "gelsin": a queue stopped by an error or by a producer that is not
    installed tells, with what it said."""
    told, runner = ending_runner()

    runner.start("düğün", lambda: summary)

    assert told == [({**summary, "project": "düğün"}, {**summary, "project": "düğün"})]


def test_a_job_that_raised_says_so_in_its_own_words():
    told, runner = ending_runner()

    def boom():
        raise RuntimeError("ComfyUI öldü")

    runner.start("düğün", boom)

    assert [state for state, _status in told] == [
        {"status": "error", "project": "düğün", "error": "ComfyUI öldü"}]


def test_a_pause_says_nothing():
    """Durdur: whoever pressed it is at the screen."""
    told, runner = ending_runner()

    runner.start("düğün", lambda: {"status": "paused"})

    assert told == []


def test_stop_requested_during_the_job_is_visible():
    runner = sync_runner()
    seen = []

    def job():
        runner.request_stop()
        seen.append(runner.stop_requested())
        return {"status": "stopped"}

    runner.start("düğün", job)
    assert seen == [True]
