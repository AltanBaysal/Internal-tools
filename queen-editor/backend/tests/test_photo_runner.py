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


def test_a_start_while_running_joins_this_projects_run_and_refuses_anothers():
    """One worker: another project's start is refused, and this project's joins the run rather than
    starting a second one (madde 511)."""
    jobs = []
    runner = PhotoRunner(spawn=jobs.append)
    assert runner.start("düğün", lambda: {"status": "done"}) is True
    assert runner.status()["status"] == "running"

    assert runner.start("başka", lambda: {"status": "done"}) is False
    assert runner.start("düğün", lambda: {"status": "done"}) is True

    assert len(jobs) == 1
    assert runner.named.now() == "düğün"


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


def deferred_runner():
    """A runner whose job waits until the test runs it, and what it told of the queue's end."""
    jobs, told = [], []
    return jobs, told, PhotoRunner(spawn=jobs.append, ended=told.append)


def test_work_joined_while_the_run_closes_is_looked_at_before_done():
    """Madde 511: the loop has found nothing owed and a job is queued before the runner says done.
    The run looks again rather than end, and the end is told once, after the look that found
    nothing."""
    jobs, told, runner = deferred_runner()
    passes = []

    def job():
        passes.append(len(passes) + 1)
        if len(passes) == 1:
            assert runner.start("düğün", lambda: {"status": "never run"}) is True
        return {"status": "done", "pass": len(passes)}

    runner.start("düğün", job)
    jobs.pop()()

    assert passes == [1, 2]
    assert jobs == []                                   # the join started no second worker
    assert told == [{"status": "done", "pass": 2, "project": "düğün"}]
    assert runner.status() == told[0]


@pytest.mark.parametrize("summary", [
    {"status": "done"},
    {"status": "paused"},
    {"status": "error", "error": "ComfyUI cevap vermedi."},
    {"status": "waiting", "waitingFor": "video"},
], ids=["done", "paused", "error", "waiting"])
def test_any_ending_a_job_joined_runs_again(summary):
    """A press means the same whenever it lands (madde 511): one that joined the run is answered as
    one made right after its end would be -- the loop runs again and says what it finds."""
    jobs, told, runner = deferred_runner()
    passes = []

    def job():
        passes.append(1)
        if len(passes) == 1:
            runner.start("düğün", lambda: {"status": "never run"})
        return summary

    runner.start("düğün", job)
    jobs.pop()()

    assert passes == [1, 1]
    assert runner.status() == {**summary, "project": "düğün"}
    assert len(told) == (0 if summary["status"] == "paused" else 1)


def test_a_join_leaves_a_stop_standing():
    """Durdur pressed, then a job queued before the run ended: the run comes back paused, as the loop
    does when the stop flag is up."""
    jobs, _told, runner = deferred_runner()
    seen = []

    def job():
        seen.append(runner.stop_requested())
        if len(seen) == 1:
            runner.request_stop()
            runner.start("düğün", lambda: {"status": "never run"})
        return {"status": "paused"}

    runner.start("düğün", job)
    jobs.pop()()

    assert seen == [False, True]


def test_a_run_renamed_under_it_ends_under_its_new_name():
    """The screen tells its own run by the status's project, so the end of a run whose project was
    renamed meanwhile is published under the name it has now."""
    jobs, told, runner = deferred_runner()

    runner.start("düğün", lambda: runner.rename("düğün", "nikah") or {"status": "done"})
    jobs.pop()()

    assert runner.status() == {"status": "done", "project": "nikah"}
    assert told == [{"status": "done", "project": "nikah"}]


def test_the_press_that_takes_the_worker_says_the_queue_started():
    """Madde 518: a page left open while the queue is idle hears the start. Said once the status
    reads running, so whoever hears it and asks reads running, and before the job begins."""
    jobs, told = [], []
    runner = PhotoRunner(spawn=jobs.append, started=lambda: told.append(runner.status()))

    runner.start("düğün", lambda: {"status": "done"})

    assert told == [{"status": "running", "project": "düğün"}]
    assert len(jobs) == 1                       # spawned, and not yet run


def test_a_start_after_the_run_ended_says_so_again():
    told = []
    runner = PhotoRunner(spawn=lambda fn: fn(), started=lambda: told.append("started"))

    runner.start("düğün", lambda: {"status": "done"})
    runner.start("düğün", lambda: {"status": "done"})

    assert told == ["started", "started"]


def test_a_join_and_a_refused_start_say_nothing():
    """A join lands while a run is going, and a refusal while another project's does: every page
    open is asking then already."""
    told = []
    runner = PhotoRunner(spawn=lambda fn: None, started=lambda: told.append("started"))
    runner.start("düğün", lambda: {"status": "done"})

    runner.start("düğün", lambda: {"status": "done"})
    runner.start("başka", lambda: {"status": "done"})

    assert told == ["started"]


def test_stop_requested_during_the_job_is_visible():
    runner = sync_runner()
    seen = []

    def job():
        runner.request_stop()
        seen.append(runner.stop_requested())
        return {"status": "stopped"}

    runner.start("düğün", job)
    assert seen == [True]
