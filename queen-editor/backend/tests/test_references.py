import pytest

from backend.features.photo_generation.domain import references


@pytest.mark.parametrize("name, kind", [
    ("kedi.png", references.PICTURE),
    ("kedi.JPG", references.PICTURE),
    ("dans.mp4", references.VIDEO),
    ("dans.MOV", references.VIDEO),
    ("rüzgar.wav", references.AUDIO),
    ("rüzgar.MP3", references.AUDIO),
])
def test_every_known_extension_says_which_kind_it_is(name, kind):
    """The pool's three words are H3's own labels -- Picture, Video, Audio -- because feeding them
    is what the pool is for. A card's layers are a different question (domain/layers.py)."""
    assert references.kind_of(name) == kind


@pytest.mark.parametrize("name", ["notlar.txt", "senaryo", "arşiv.zip", "kedi.png.txt"])
def test_an_extension_nobody_knows_has_no_kind(name):
    assert references.kind_of(name) is None


def test_a_free_name_is_the_users_own():
    # The user recognises their reference by its name, so it is kept as they gave it.
    assert references.free_name("kedi.png", []) == "kedi.png"


def test_a_taken_name_takes_the_next_number():
    """Never written over: what the user put in the pool is their own work (FOUNDATION 1)."""
    assert references.free_name("kedi.png", ["kedi.png"]) == "kedi-2.png"
    assert references.free_name("kedi.png", ["kedi.png", "kedi-2.png"]) == "kedi-3.png"


def test_a_name_cannot_climb_out_of_the_folder():
    """The name arrives from a browser, so it is not a name until this says it is."""
    assert references.free_name("../../gizli.png", []) == "gizli.png"
    assert references.free_name("C:\\işler\\kedi.png", []) == "kedi.png"


def item(name, kind, seconds=None):
    """One line of the pool, the shape the rule reads: what it is and how long it runs."""
    return {"name": name, "kind": kind, "seconds": seconds}


def pictures(count):
    return [item(f"{n}.png", references.PICTURE) for n in range(count)]


def refusal(pool, incoming):
    with pytest.raises(references.PoolLimit) as exc:
        references.check(pool, incoming)
    return str(exc.value)


def test_a_kind_that_is_full_refuses_the_next_one():
    """The app counts and refuses rather than leaving it to H3: that error lands in a Colab log the
    user never opens."""
    said = refusal(pictures(9), [item("onuncu.png", references.PICTURE)])

    assert "onuncu.png" in said and "9" in said


def test_a_clip_shorter_than_the_model_takes_is_refused():
    assert "kısa.mp4" in refusal([], [item("kısa.mp4", references.VIDEO, 1.0)])


def test_a_clip_longer_than_the_model_takes_is_refused():
    assert "uzun.mp4" in refusal([], [item("uzun.mp4", references.VIDEO, 20.0)])


def test_the_videos_together_cannot_pass_fifteen_seconds():
    # Each one is fine on its own; what the pool cannot take is the two of them.
    said = refusal([], [item("bir.mp4", references.VIDEO, 8.0),
                        item("iki.mp4", references.VIDEO, 8.0)])

    assert "15" in said


def test_sound_is_counted_apart_from_the_pictures_and_videos():
    pool = [item("bir.mp4", references.VIDEO, 15.0)]

    references.check(pool, [item("rüzgar.wav", references.AUDIO, 10.0)])


def test_a_picture_has_no_duration_to_count():
    """A picture is held by the count of pictures, never by a total of seconds -- it has none."""
    references.check([], pictures(9))


def test_what_is_already_in_the_pool_counts():
    pool = [item("bir.mp4", references.VIDEO, 7.0), item("iki.mp4", references.VIDEO, 7.0)]

    assert "15" in refusal(pool, [item("üç.mp4", references.VIDEO, 7.0)])


def video(name, seconds=4.0):
    return item(name, references.VIDEO, seconds)


def test_the_stored_order_gives_each_reference_its_slot():
    rows = [item("kuş.png", references.PICTURE), item("kedi.png", references.PICTURE)]

    placed = references.placed({references.PICTURE: ["kedi.png", "kuş.png"]}, rows)

    assert [(row["name"], row["slot"]) for row in placed] == [("kedi.png", 1), ("kuş.png", 2)]


def test_a_slot_whose_file_is_gone_stays_empty():
    """The heart of madde 300: deleting one does not move the others.

    H3 numbers references by their order and not by the slot they sit in, so a reference that
    slid up would quietly become the <Picture N> the prompt meant for another one.
    """
    order = {references.PICTURE: ["bir.png", "iki.png", "üç.png"]}

    placed = references.placed(order, [item("bir.png", references.PICTURE),
                                       item("üç.png", references.PICTURE)])

    assert [(row["name"], row["slot"]) for row in placed] == [("bir.png", 1), ("üç.png", 3)]


def test_a_file_the_order_never_heard_of_waits_at_the_end():
    order = {references.PICTURE: ["kedi.png"]}
    rows = [item("kedi.png", references.PICTURE), item("zebra.png", references.PICTURE),
            item("aslan.png", references.PICTURE)]

    placed = references.placed(order, rows)

    # By name among themselves, which is what a pool with no order at all reads as.
    assert [row["name"] for row in placed] == ["kedi.png", "aslan.png", "zebra.png"]


def test_with_no_stored_order_the_pool_reads_by_name():
    rows = [item("kuş.png", references.PICTURE), item("kedi.png", references.PICTURE)]

    placed = references.placed({}, rows)

    assert [(row["name"], row["slot"]) for row in placed] == [("kedi.png", 1), ("kuş.png", 2)]


def test_each_kind_counts_its_own_slots():
    order = {references.PICTURE: ["kedi.png"], references.VIDEO: ["dans.mp4"]}

    placed = references.placed(order, [item("kedi.png", references.PICTURE), video("dans.mp4")])

    assert [(row["name"], row["slot"]) for row in placed] == [("kedi.png", 1), ("dans.mp4", 1)]


def test_a_missing_slot_in_the_middle_is_a_gap():
    rows = [{"name": "bir.png", "kind": references.PICTURE, "slot": 1},
            {"name": "üç.png", "kind": references.PICTURE, "slot": 3}]

    assert references.gaps(rows) == [references.PICTURE]


def test_the_last_one_leaving_is_not_a_gap():
    # Dense from one is the whole rule; nothing has to come after the last reference.
    rows = [{"name": "bir.png", "kind": references.PICTURE, "slot": 1},
            {"name": "iki.png", "kind": references.PICTURE, "slot": 2}]

    assert references.gaps(rows) == []


def test_a_press_is_counted_as_a_whole():
    # Three videos is the limit, and this press is where the fourth would come from.
    pool = [item("bir.mp4", references.VIDEO, 3.0)]
    incoming = [item("iki.mp4", references.VIDEO, 3.0), item("üç.mp4", references.VIDEO, 3.0),
                item("dört.mp4", references.VIDEO, 3.0)]

    assert "3" in refusal(pool, incoming)
