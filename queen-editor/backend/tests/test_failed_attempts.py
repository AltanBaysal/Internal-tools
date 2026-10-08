"""Madde 433: what the queue does with an attempt that fell.

Every failed attempt says what was raised -- its type and its whole message -- on the server's live
log, the cell the notebook leaves open, so the first two of three are seen as well as the one the card
shows. And when ComfyUI gave no answer at all, the next attempt comes 45 seconds later rather than in
the same instant: three tries then span the 90 seconds the notebook gives a starting ComfyUI. The
wait is a second at a time, and Durdur ends it.

No test waits a real second: the loop is handed a sleep that writes down what it was asked for.
"""
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.run_loop import make_job
from backend.tests.test_photo_usecases import (
    FakePlanStore,
    FakeRecord,
    FakeStore,
    FrameFault,
    frame,
    sync_runner,
)


class NoAnswer(RuntimeError):
    """The shape ComfyUI's client raises when no answer came: unreachable, a 5xx, a request it did
    not answer in time. The mark is read through getattr, the way frame_level is."""

    no_answer = True


# What a refused connection says, many lines and all: the message is printed whole, not its first
# line.
REFUSED = ("ComfyUI'ye bağlanılamadı — http://127.0.0.1:8188\n"
           "HTTPConnectionPool(host='127.0.0.1', port=8188): Max retries exceeded with url: /prompt "
           "(Caused by NewConnectionError('Failed to establish a new connection: [Errno 111] "
           "Connection refused'))\n"
           "--- comfyui.log · son 30 satır ---\n"
           "Starting server")


class Falls:
    """A producer whose first calls raise the given errors, in order; after them it makes the
    picture."""

    def __init__(self, *errors):
        self.errors = list(errors)
        self.calls = 0

    def generate(self, prompt, negative, seed, model="", lora="", source=None, end=None,
                 references=(), seconds=None):
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return b"PNG"


def run(producer, runner=None, sleep=None):
    """One photo frame through the loop. Returns (summary, log lines, seconds slept, record)."""
    lines, waits, record = [], [], FakeRecord()
    summary = make_job(runner or sync_runner(), FakeStore(), record,
                       FakePlanStore(frames=[frame(0)]), {layers.PHOTO: producer},
                       lambda: "t", "düğün", log=lines.append,
                       sleep=sleep or waits.append)()
    return summary, lines, waits, record


def test_each_failed_attempt_prints_its_own_error_whole_on_the_live_log():
    _summary, lines, _waits, _record = run(Falls(*[NoAnswer(REFUSED)] * 3))

    assert len(lines) == 3, f"Her düşen deneme bir satır basmalı: {lines}"
    for attempt, line in enumerate(lines, start=1):
        assert line.startswith(f"⚠ 0_a.png · deneme {attempt}/3 düştü"), line
        assert f"\nNoAnswer: {REFUSED}" in line, "Satır hatanın türünü ve mesajının tamamını basmadı"


def test_a_comfyui_that_gave_no_answer_is_waited_for_45_seconds_before_each_retry():
    summary, _lines, waits, _record = run(Falls(*[NoAnswer(REFUSED)] * 3))

    # A second at a time, so Durdur is heard within one; nothing after the third attempt.
    assert waits == [1] * 90
    assert summary["status"] == "error"
    assert REFUSED in summary["error"]


def test_the_line_says_when_the_next_attempt_comes():
    _summary, lines, _waits, _record = run(Falls(*[NoAnswer(REFUSED)] * 3))

    heads = [line.splitlines()[0] for line in lines]
    assert heads == ["⚠ 0_a.png · deneme 1/3 düştü — 45 sn sonra yeniden denenecek",
                     "⚠ 0_a.png · deneme 2/3 düştü — 45 sn sonra yeniden denenecek",
                     "⚠ 0_a.png · deneme 3/3 düştü"]


def test_a_comfyui_that_comes_back_within_the_wait_gets_the_frame_made():
    producer = Falls(NoAnswer(REFUSED), NoAnswer(REFUSED))

    summary, _lines, waits, record = run(producer)

    assert producer.calls == 3
    assert sum(waits) == 90
    assert summary["status"] == "done"
    assert record.statuses("düğün") == {"0_a": "done"}


def test_a_frame_comfyui_reported_failed_is_tried_again_at_once():
    # ComfyUI answered: the graph failed on this frame, and waiting mends nothing.
    summary, lines, waits, record = run(Falls(*[FrameFault("node 41: p")] * 3))

    assert waits == []
    assert record.statuses("düğün") == {"0_a": "failed"}
    assert summary["status"] == "done"
    assert lines[0].splitlines()[0] == "⚠ 0_a.png · deneme 1/3 düştü — yeniden deneniyor"
    assert "\nFrameFault: node 41: p" in lines[0]


def test_anything_comfyui_did_not_mark_is_tried_again_at_once():
    # A prompt writer that did not answer, a 4xx, a render that ran out of time: no mark, no wait.
    # DeepSeek's box already tries five times on its own (madde 416).
    summary, lines, waits, _record = run(Falls(*[RuntimeError("DeepSeek: 503")] * 3))

    assert waits == []
    assert summary["status"] == "error"
    assert [line.splitlines()[1] for line in lines] == ["RuntimeError: DeepSeek: 503"] * 3


def test_a_render_cut_by_durdur_is_no_fall_and_prints_no_line():
    """Durdur interrupts the render in flight, and what that raises is the user's own pause, not a
    failed attempt: the log says nothing about it, and nothing is waited for."""
    runner = sync_runner()

    class CutByDurdur(Falls):
        def generate(self, *args, **kwargs):
            runner.request_stop()
            return super().generate(*args, **kwargs)

    producer = CutByDurdur(NoAnswer("Processing interrupted"))
    summary, lines, waits, _record = run(producer, runner=runner)

    assert [line for line in lines if line.startswith("⚠")] == []
    assert waits == []
    assert producer.calls == 1
    assert summary["status"] == "paused"


def test_durdur_cuts_the_wait_short():
    runner, waits = sync_runner(), []

    def sleep(seconds):
        waits.append(seconds)
        if len(waits) == 3:
            runner.request_stop()

    producer = Falls(*[NoAnswer(REFUSED)] * 3)
    summary, _lines, _waits, _record = run(producer, runner=runner, sleep=sleep)

    assert waits == [1, 1, 1]
    assert producer.calls == 1
    assert summary["status"] == "paused"
