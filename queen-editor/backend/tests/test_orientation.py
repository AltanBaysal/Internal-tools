"""Which way a generation stands (madde 476): yatay or dikey, asked per generation like the negative.

The rule's own module is imported inside its tests: written after this file, an import at the top
would stop the whole collection instead of failing these questions. The queue's fakes come from
test_photo_usecases.
"""
import pytest

from backend.features.photo_generation.domain import layers, production_mode
from backend.features.photo_generation.domain.usecases.queue_references import queue_references
from backend.features.photo_generation.domain.usecases.regenerate import regenerate
from backend.features.photo_generation.domain.usecases.resume_batch import resume_batch
from backend.features.photo_generation.domain.usecases.start_batch import plan_frames, start_batch
from backend.tests.test_photo_usecases import (
    FakeGenerator,
    FakeOrderStore,
    FakePlanStore,
    FakePool,
    FakeRecord,
    FakeReferenceOrders,
    FakeStore,
    queue_video,
    sync_runner,
    video_project,
)


def test_a_generation_asked_without_one_is_landscape():
    from backend.features.photo_generation.domain import orientation

    assert orientation.DEFAULT == orientation.LANDSCAPE == "yatay"


def test_a_line_planned_before_orientations_reads_as_portrait():
    """Every line planned before madde 476 was portrait, so a retry or a resume of an old frame
    renders the way it always did -- not the new default."""
    from backend.features.photo_generation.domain import orientation

    assert orientation.of({"id": "P0_0", "prompt": "a"}) == orientation.PORTRAIT == "dikey"


@pytest.mark.parametrize("value", ["yatay", "dikey"])
def test_a_line_reads_as_the_orientation_it_carries(value):
    from backend.features.photo_generation.domain import orientation

    assert orientation.of({orientation.FIELD: value}) == value


@pytest.mark.parametrize("value", ["yatay", "dikey"])
def test_both_orientations_pass_the_door(value):
    from backend.features.photo_generation.domain import orientation

    orientation.validate(value)


@pytest.mark.parametrize("value", ["landscape", "", None, 1, "Yatay"])
def test_anything_else_is_refused_in_turkish(value):
    from backend.features.photo_generation.domain import orientation

    with pytest.raises(orientation.InvalidOrientation) as refused:
        orientation.validate(value)

    assert "yatay" in str(refused.value) and "dikey" in str(refused.value)


# --- A photo batch ---------------------------------------------------------------------------------

def submit(generator, plan_store, **asked):
    """Kuyruğa ekle, two prompts with two variants each, run to completion."""
    return start_batch(sync_runner(), FakeStore(), FakeRecord(), plan_store,
                       {layers.PHOTO: generator}, lambda: 7, lambda: "t", "düğün",
                       '["a", "b"]', "neg", 2, **asked)


def test_a_batch_asked_without_an_orientation_is_landscape():
    """Until the screen sends one (madde 477), every new generation is landscape -- the item's
    default, and the known cost of splitting it."""
    generator, plan_store = FakeGenerator(), FakePlanStore()

    submit(generator, plan_store)

    assert [job["orientation"] for job in plan_store.appended[-1]] == ["yatay"] * 4
    assert generator.orientations == ["yatay"] * 4


def test_a_batch_carries_the_orientation_it_was_asked_in():
    generator, plan_store = FakeGenerator(), FakePlanStore()

    submit(generator, plan_store, orientation="dikey")

    assert [job["orientation"] for job in plan_store.appended[-1]] == ["dikey"] * 4
    assert generator.orientations == ["dikey"] * 4


def test_a_batch_in_an_unknown_orientation_is_refused_before_anything_is_planned():
    from backend.features.photo_generation.domain.orientation import InvalidOrientation
    generator, plan_store = FakeGenerator(), FakePlanStore()

    with pytest.raises(InvalidOrientation):
        submit(generator, plan_store, orientation="landscape")

    assert plan_store.appended == []
    assert generator.calls == []


def test_a_line_planned_before_orientations_is_made_portrait():
    """An old frame put back in line renders the way it always did."""
    generator = FakeGenerator()
    plan_store = FakePlanStore(frames=[{"number": 0, "letter": "a", "prompt": "p", "seed": 1}])

    resume_batch(sync_runner(), FakeStore(), FakeRecord(), plan_store, {layers.PHOTO: generator},
                 lambda: "t", "düğün")

    assert generator.orientations == ["dikey"]


def test_variants_of_two_orientations_are_not_made_in_one_batch():
    """A batch is one graph, made at one size: a variant standing the other way is made alone."""
    from backend.tests.test_variant_batch import BatchGenerator
    lines = plan_frames(0, [{"prompt": "a"}], "neg", 2, lambda: 11)
    lines[1]["orientation"] = "dikey"
    generator = BatchGenerator()

    resume_batch(sync_runner(), FakeStore(), FakeRecord(), FakePlanStore(frames=lines),
                 {layers.PHOTO: generator}, lambda: "t", "düğün")

    assert generator.batches == []
    assert generator.orientations == ["yatay", "dikey"]


def test_a_batch_is_made_in_its_variants_orientation():
    from backend.tests.test_variant_batch import BatchGenerator
    generator = BatchGenerator()

    submit(generator, FakePlanStore(), orientation="dikey")

    assert len(generator.batches) == 2
    assert generator.orientations == ["dikey", "dikey"]


# --- Yeniden üret ----------------------------------------------------------------------------------

def make_again(kind, **asked):
    store, record, plan_store = video_project((0, "a"))
    regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
               {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
               "düğün", "0_a", kind, "p", **asked)
    return plan_store.appended[-1][0]


def test_a_photo_made_again_asked_without_an_orientation_is_landscape():
    """The negative's way (ana ajan, 20 Ekim): from the request, the default when it says none --
    so until the screen sends one an old portrait photo made again comes out landscape."""
    assert make_again(layers.PHOTO)["orientation"] == "yatay"


def test_a_photo_made_again_carries_the_orientation_it_was_asked_in():
    assert make_again(layers.PHOTO, orientation="dikey")["orientation"] == "dikey"


def test_a_photo_made_again_in_an_unknown_orientation_is_refused():
    from backend.features.photo_generation.domain.orientation import InvalidOrientation
    store, record, plan_store = video_project((0, "a"))

    with pytest.raises(InvalidOrientation):
        regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
                   {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
                   "düğün", "0_a", layers.PHOTO, "p", orientation="yan")

    assert plan_store.appended == []


def test_a_video_made_again_carries_no_orientation():
    """A video follows the shape of its photo, so its line says nothing, whatever it is handed --
    the negative's rule for the layers over a photo."""
    assert "orientation" not in make_again(layers.VIDEO, orientation="dikey")


def test_a_video_hung_on_a_frame_carries_no_orientation():
    store, record, plan_store = video_project((0, "a"))

    _added, jobs = queue_video(store, record, plan_store, production_mode.STANDARD)

    assert jobs and all("orientation" not in job for job in jobs)


# --- Referanstan -----------------------------------------------------------------------------------

def from_the_pool(generator, plan_store, **asked):
    return queue_references(sync_runner(), FakeStore(), FakeRecord(), plan_store, FakeOrderStore(),
                            FakePool(), FakeReferenceOrders(), {layers.VIDEO: generator},
                            lambda: 7, lambda: "t", "düğün", '["gotik kız"]', 2, **asked)


def test_a_card_from_the_pool_asked_without_an_orientation_is_landscape():
    """No photo to follow, so the card is asked like every other generation (ana ajan, 20 Ekim)."""
    generator, plan_store = FakeGenerator(), FakePlanStore()

    from_the_pool(generator, plan_store)

    assert [job["orientation"] for job in plan_store.appended[-1]] == ["yatay", "yatay"]
    assert generator.orientations == ["yatay", "yatay"]


def test_a_card_from_the_pool_carries_the_orientation_it_was_asked_in():
    generator, plan_store = FakeGenerator(), FakePlanStore()

    from_the_pool(generator, plan_store, orientation="dikey")

    assert [job["orientation"] for job in plan_store.appended[-1]] == ["dikey", "dikey"]
    assert generator.orientations == ["dikey", "dikey"]


def test_a_card_from_the_pool_in_an_unknown_orientation_is_refused():
    from backend.features.photo_generation.domain.orientation import InvalidOrientation
    plan_store = FakePlanStore()

    with pytest.raises(InvalidOrientation):
        from_the_pool(FakeGenerator(), plan_store, orientation=None)

    assert plan_store.appended == []
