from backend.features.photo_generation.runner import PhotoRunner


def sync_runner():
    """spawn=lambda fn: fn() runs the job inline -- the test needs no thread and no sleep."""
    return PhotoRunner(spawn=lambda fn: fn())


def test_starts_idle():
    assert PhotoRunner().status() == {"status": "idle"}


def test_done_carries_the_saved_file_name():
    runner = sync_runner()
    assert runner.start("düğün", lambda: "0_a.png") is True
    assert runner.status() == {"status": "done", "project": "düğün", "file": "0_a.png"}


def test_failure_becomes_error_with_the_real_message():
    runner = sync_runner()

    def boom():
        raise RuntimeError("ComfyUI öldü")

    runner.start("düğün", boom)
    state = runner.status()
    assert state["status"] == "error" and state["error"] == "ComfyUI öldü"


def test_second_start_is_refused_while_running():
    runner = PhotoRunner(spawn=lambda fn: None)   # never runs -> stays "running"
    assert runner.start("düğün", lambda: "0_a.png") is True
    assert runner.status()["status"] == "running"
    assert runner.start("düğün", lambda: "1_a.png") is False


def test_a_finished_job_does_not_block_the_next_one():
    runner = sync_runner()
    runner.start("düğün", lambda: "0_a.png")
    assert runner.start("düğün", lambda: "1_a.png") is True
    assert runner.status()["file"] == "1_a.png"
