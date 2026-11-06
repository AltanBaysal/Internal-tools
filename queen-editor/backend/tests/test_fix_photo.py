"""The agent's fix of a mixed-up photo, as photo generation does it (madde 481).

The frame's photo is made again from corrected words, and the new photo stands exactly where the old
frame stood: the same place in the gallery, the same place in the queue. It is a new identity in that
place rather than the old one made again -- the old name's bytes are cached for good, and a copy frame
may share the old file.

The use case is imported inside the tests: written after this file, an import at the top would stop
the whole collection instead of failing these questions. The queue's fakes come from
test_photo_usecases.
"""
import pytest

from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.features.photo_generation.runner import PhotoRunner
from backend.tests.test_photo_usecases import (
    FakeGenerator,
    FakeOrderStore,
    FakePlanStore,
    FakeRecord,
    FakeStore,
    sync_runner,
)

NOW = "2026-10-20T12:00:00+00:00"
MIXED_PROMPT = "1girl, 1boy, white hair, black hair"
FIXED_PROMPT = "1girl, 1boy, black hair"


def line(fid, prompt, **fields):
    """A photo's plan line, the way start_batch writes one."""
    number, variant = (int(part) for part in fid[1:].split("_"))
    return {"id": fid, "type": "photo", "number": number, "variant": variant, "prompt": prompt,
            "negative": "lowres", "seed": 41 + number, "model": "nova.safetensors",
            "lora": "slime.safetensors", "orientation": "yatay", **fields}


def made(fid, prompt, file=None, negative="lowres", seed=None):
    """The record's row for a photo that landed."""
    return {"file": file or f"{fid}.png", "frame": fid, "layer": "photo", "status": "done",
            "prompt": prompt, "negative": negative, "seed": seed, "createdAt": "t"}


class Project:
    """düğün: three frames planned and made, P0_0 at the foot of the gallery and P2_0 on top. P1_0 is
    the mixed-up one."""

    def __init__(self, lines=None, rows=None, order=("P2_0", "P1_0", "P0_0"), next_no=3):
        self.store = FakeStore(next_no=next_no)
        self.record = FakeRecord()
        lines = lines if lines is not None else [
            line("P0_0", "a"), line("P1_0", MIXED_PROMPT, scene="Kadın döner."), line("P2_0", "c")]
        self.plan_store = FakePlanStore(frames=lines)
        self.order_store = FakeOrderStore(order)
        self.generator = FakeGenerator()
        for row in rows if rows is not None else [made(entry["id"], entry["prompt"],
                                                       seed=entry["seed"]) for entry in lines]:
            self.record.append("düğün", row)

    def gallery(self):
        return list_frames(self.record, self.store, self.plan_store, self.order_store, "düğün")

    def card(self, fid):
        return next(frame for frame in self.gallery() if frame["id"] == fid)

    def fix(self, seen, prompt=FIXED_PROMPT, negative="lowres, white hair on girl",
            runner=None, project="düğün"):
        from backend.features.photo_generation.domain.usecases.fix_photo import fix_photo
        return fix_photo(runner or sync_runner(), self.store, self.record, self.plan_store,
                         self.order_store, {layers.PHOTO: self.generator}, lambda: NOW,
                         project, seen, prompt, negative)


def test_the_new_photo_stands_in_the_old_frame_s_place_made_from_the_new_words():
    """The user: "eski fotoğraflar aynı yerde olur sırası yeni bir yer geçmez". New words are a new
    prompt, so it takes the next number (madde 99); the gallery keeps its place."""
    project = Project()

    said = project.fix(project.card("P1_0"))

    assert said == "fixed"
    assert [frame["id"] for frame in project.gallery()] == ["P2_0", "P3_0", "P0_0"]
    assert project.order_store.order == ["P2_0", "P3_0", "P0_0"]
    new = project.card("P3_0")
    assert new["status"] == "done"
    assert new["prompts"]["photo"] == FIXED_PROMPT
    assert new["negative"] == "lowres, white hair on girl"


def test_only_the_words_change_the_frame_s_own_settings_go_with_them():
    """No seed change (the user: "seed değiştirmek kurtarmıyor"): the seed, the model, the lora, the
    orientation and the scene are the frame's own; the prompt and the negative are the fix."""
    project = Project()

    project.fix(project.card("P1_0"))

    (planned,) = project.plan_store.appended
    assert planned == [{"id": "P3_0", "type": "photo", "number": 3, "variant": 0,
                        "prompt": FIXED_PROMPT, "negative": "lowres, white hair on girl",
                        "seed": 42, "model": "nova.safetensors", "lora": "slime.safetensors",
                        "orientation": "yatay", "scene": "Kadın döner."}]
    assert project.generator.calls == [(FIXED_PROMPT, "lowres, white hair on girl", 42,
                                        "nova.safetensors")]
    assert project.generator.loras == ["slime.safetensors"]
    assert project.generator.orientations == ["yatay"]


def test_a_krea_frame_s_fix_records_no_negative():
    """Krea takes no negative (madde 486), so a line saying it was fixed with one would name words
    the picture was never drawn from. The prompt is the fix; Krea's own lora stays."""
    project = Project(lines=[line("P0_0", "a"),
                             line("P1_0", MIXED_PROMPT, model="krea2", lora="snofs", negative=""),
                             line("P2_0", "c")])

    project.fix(project.card("P1_0"))

    (planned,) = project.plan_store.appended
    assert (planned[0]["prompt"], planned[0]["negative"], planned[0]["lora"]) == \
        (FIXED_PROMPT, "", "snofs")


def test_the_old_photo_is_deleted_and_its_frame_leaves_the_gallery():
    project = Project()

    project.fix(project.card("P1_0"))

    assert project.store.deleted == ["P1_0.png"]
    assert project.record.slots("düğün")["P1_0"]["photo"] == {"status": "deleted",
                                                              "file": "P1_0.png"}
    assert "P1_0" not in [frame["id"] for frame in project.gallery()]


def test_the_new_photo_is_made_where_the_old_one_stood_in_the_queue():
    """The queue reads the gallery from its foot up: the fixed frame's photo comes between its two
    neighbours, as the old one would have."""
    lines = [line("P0_0", "a"), line("P1_0", MIXED_PROMPT), line("P2_0", "c")]
    # P0_0 and P2_0 are still owed; P1_0 is made.
    project = Project(lines=lines, rows=[made("P1_0", MIXED_PROMPT, seed=42)])
    runner = PhotoRunner(spawn=lambda fn: None)       # this project's run holds the worker
    runner.start("düğün", lambda: None)

    project.fix(project.card("P1_0"), runner=runner)

    owed = queue.open_jobs(project.plan_store.read("düğün")["frames"],
                           project.record.slots("düğün"), project.order_store.read("düğün"))
    assert [job["id"] for job in owed] == ["P0_0", "P3_0", "P2_0"]


def test_a_fix_of_the_negative_alone_is_the_next_variant_of_the_family():
    """The same words are another variant of the same prompt's family (madde 99)."""
    project = Project()

    project.fix(project.card("P1_0"), prompt=MIXED_PROMPT)

    assert [frame["id"] for frame in project.gallery()] == ["P2_0", "P1_1", "P0_0"]
    assert project.plan_store.appended[0][0]["prompt"] == MIXED_PROMPT


def test_a_photo_another_frame_holds_stays_on_disk():
    """A copy frame shares its source's picture (madde 102): the fixed frame lets go of the file, and
    the other one keeps it."""
    rows = [made("P0_0", "a", seed=41), made("P1_0", MIXED_PROMPT, seed=42),
            made("P2_0", "c", seed=43), made("C1_P1_0", MIXED_PROMPT, file="P1_0.png", seed=42)]
    project = Project(rows=rows, order=("C1_P1_0", "P2_0", "P1_0", "P0_0"))

    project.fix(project.card("P1_0"))

    assert project.store.deleted == []
    assert project.card("C1_P1_0")["layers"] == {"photo": "P1_0.png"}


def test_a_copy_frame_is_made_with_the_settings_of_the_frame_that_made_its_picture():
    """A copy's card is read from the record, which keeps no model, lora or orientation: they are on
    the plan line of the frame whose picture it holds -- deleted or not, the plan keeps it."""
    rows = [made("P0_0", "a", seed=41), made("P2_0", "c", seed=43),
            made("C1_P1_0", MIXED_PROMPT, file="P1_0.png", seed=42)]
    project = Project(rows=rows, order=("C1_P1_0", "P2_0", "P0_0"))
    # The source, P1_0, was deleted: its plan line stays and its photo is held by the copy alone.
    project.record.mark("düğün", "P1_0", "photo", "P1_0.png", "deleted", "t", seen=None)

    project.fix(project.card("C1_P1_0"))

    (planned,) = project.plan_store.appended
    assert (planned[0]["seed"], planned[0]["model"], planned[0]["lora"],
            planned[0]["orientation"]) == (42, "nova.safetensors", "slime.safetensors", "yatay")
    assert project.store.deleted == ["P1_0.png"]
    assert [frame["id"] for frame in project.gallery()] == ["P3_0", "P2_0", "P0_0"]


def test_a_same_words_fix_of_a_copy_is_the_next_variant_of_its_source_s_family():
    """A twin's name carries its source's family (photo_name: the copy prefix comes off), so the
    negative alone fixed on C1_P1_0 is the next variant of P1."""
    rows = [made("P0_0", "a", seed=41), made("P1_0", MIXED_PROMPT, seed=42),
            made("P2_0", "c", seed=43), made("C1_P1_0", MIXED_PROMPT, file="P1_0.png", seed=42)]
    project = Project(rows=rows, order=("C1_P1_0", "P2_0", "P1_0", "P0_0"))

    project.fix(project.card("C1_P1_0"), prompt=MIXED_PROMPT)

    assert [frame["id"] for frame in project.gallery()] == ["P1_1", "P2_0", "P1_0", "P0_0"]
    assert project.store.deleted == []


def test_a_variant_made_in_a_batch_is_fixed_with_its_own_line_s_seed():
    """A batch renders every variant from its head's seed (madde 411), so a variant's own line seed
    was never used. The fix keeps the line's seed all the same: what fixes a mix-up is the words,
    not a reseed (the user: "seed değiştirmek kurtarmıyor"), and the picture is made alone."""
    lines = [line("P0_0", "a"), line("P1_0", MIXED_PROMPT), line("P1_1", MIXED_PROMPT, seed=99)]
    # Both variants of P1 were made in one batch, from P1_0's seed.
    rows = [made("P0_0", "a", seed=41), made("P1_0", MIXED_PROMPT, seed=42),
            made("P1_1", MIXED_PROMPT, seed=42)]
    project = Project(lines=lines, rows=rows, order=("P1_1", "P1_0", "P0_0"))

    project.fix(project.card("P1_1"))

    assert project.plan_store.appended[0][0]["seed"] == 99
    assert project.generator.calls[0][2] == 99


def test_a_frame_a_queued_linked_video_ends_on_is_left_alone():
    """Another frame's video waits in the queue to arrive at this frame's photo (madde 402): deleting
    the photo would make that video fail on a frame it can no longer find."""
    project = Project()
    project.plan_store.frames.append({"id": "P0_0", "type": "video", "number": 0, "variant": 0,
                                      "prompt": "", "negative": "", "seed": None, "model": "",
                                      "mode": "linked", "linkedTo": "P1_0"})
    rows, order = list(project.record.rows), list(project.order_store.order)

    said = project.fix(project.card("P1_0"))

    assert said == "linked"
    assert project.plan_store.appended == []
    assert project.record.rows == rows
    assert project.order_store.order == order
    assert project.store.deleted == []


def test_a_frame_a_made_linked_video_ended_on_is_fixed():
    """A video already made arrived at the picture it was handed; nothing waits on this photo."""
    project = Project()
    project.plan_store.frames.append({"id": "P0_0", "type": "video", "number": 0, "variant": 0,
                                      "prompt": "", "negative": "", "seed": None, "model": "",
                                      "mode": "linked", "linkedTo": "P1_0"})
    project.record.append("düğün", {"file": "P0_0_V1_0.mp4", "frame": "P0_0", "layer": "video",
                                    "status": "done", "endsOn": "P1_0.png"})

    assert project.fix(project.card("P1_0")) == "fixed"


def test_a_frame_planned_before_any_setting_is_made_as_it_was():
    """A frame from before the plan kept models, loras and orientations: the graph's own model, no
    lora, and portrait -- what it was made in (orientation.of)."""
    rows = [made("P0_0", MIXED_PROMPT, seed=7)]
    project = Project(lines=[], rows=rows, order=(), next_no=1)

    project.fix(project.card("P0_0"))

    (planned,) = project.plan_store.appended
    assert (planned[0]["seed"], planned[0]["model"], planned[0]["lora"],
            planned[0]["orientation"]) == (7, "", "", "dikey")
    assert [frame["id"] for frame in project.gallery()] == ["P1_0"]


def test_a_failed_video_goes_with_the_old_frame():
    """No video was made, so the frame was fixable; its red slot would otherwise keep the old card in
    the gallery beside the new one."""
    project = Project()
    project.record.mark("düğün", "P1_0", "video", "P1_0_V1_0.mp4", "failed", "t",
                        seen=None, error="OOM")

    project.fix(project.card("P1_0"))

    assert project.record.slots("düğün")["P1_0"]["video"]["status"] == "deleted"
    assert [frame["id"] for frame in project.gallery()] == ["P2_0", "P3_0", "P0_0"]


def test_a_video_made_is_never_deleted_here():
    """The agent never asks to fix a frame with a video. Were it ever asked, the video stays: only the
    photo and red slots close."""
    project = Project()
    project.record.append("düğün", {"file": "P1_0_V1_0.mp4", "frame": "P1_0", "layer": "video",
                                    "status": "done", "prompt": "she turns"})

    project.fix(project.card("P1_0"))

    assert project.record.slots("düğün")["P1_0"]["video"]["status"] == "done"
    assert "P1_0_V1_0.mp4" not in project.store.deleted


def changed_prompt(project):
    project.record.append("düğün", made("P1_0", "someone else's words", seed=42))


def changed_negative(project):
    project.record.append("düğün", made("P1_0", MIXED_PROMPT, negative="other", seed=42))
    project.plan_store.frames[1]["negative"] = "other"


def video_landed(project):
    project.record.append("düğün", {"file": "P1_0_V1_0.mp4", "frame": "P1_0", "layer": "video",
                                    "status": "done", "prompt": "she turns"})


def video_queued(project):
    project.plan_store.frames.append({"id": "P1_0", "type": "video", "number": 1, "variant": 0,
                                      "prompt": "", "negative": "", "seed": None, "model": ""})


def photo_gone(project):
    project.record.mark("düğün", "P1_0", "photo", "P1_0.png", "deleted", "t", seen="done")


@pytest.mark.parametrize("change", [changed_prompt, changed_negative, video_landed, video_queued,
                                    photo_gone],
                         ids=["prompt", "negative", "video-landed", "video-queued", "frame-gone"])
def test_a_frame_that_changed_since_it_was_seen_is_left_alone(change):
    """The user may answer minutes after the change was shown (madde 480): a fix of a frame that is
    no longer what the user allowed changes nothing."""
    project = Project()
    seen = project.card("P1_0")
    change(project)
    rows, order = list(project.record.rows), list(project.order_store.order)

    said = project.fix(seen)

    assert said == "changed"
    assert project.plan_store.appended == []
    assert project.record.rows == rows
    assert project.order_store.order == order
    assert project.store.deleted == []
    assert project.generator.calls == []


def test_a_project_that_is_gone_changes_nothing():
    project = Project()
    seen = project.card("P1_0")

    assert project.fix(seen, project="silinmiş") == "changed"
    assert project.plan_store.appended == []


def test_a_fix_while_another_project_runs_waits_in_the_queue():
    """There is one worker: the fix is made all the same, and the new photo is owed until this
    project's queue runs."""
    project = Project()
    runner = PhotoRunner(spawn=lambda fn: None)
    runner.start("başka", lambda: None)

    said = project.fix(project.card("P1_0"), runner=runner)

    assert said == "waiting"
    assert project.store.deleted == ["P1_0.png"]
    assert project.card("P3_0")["owed"] == ["photo"]


def test_the_new_photo_is_planned_and_placed_before_the_old_one_is_deleted():
    """Written before what it replaces is taken: a delete that fails leaves the old frame whole,
    beside the new one, and nothing lost."""
    project = Project()

    def unreachable(_project, _file):
        raise OSError(107, "Transport endpoint is not connected")

    project.store.delete = unreachable

    with pytest.raises(OSError):
        project.fix(project.card("P1_0"))

    assert [entry["id"] for entry in project.plan_store.appended[0]] == ["P3_0"]
    assert project.order_store.order == ["P2_0", "P3_0", "P0_0"]
    assert project.record.slots("düğün")["P1_0"]["photo"]["status"] == "done"
    assert {"P1_0", "P3_0"} <= {frame["id"] for frame in project.gallery()}
