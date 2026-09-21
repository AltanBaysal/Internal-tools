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


def test_a_press_is_counted_as_a_whole():
    # Three videos is the limit, and this press is where the fourth would come from.
    pool = [item("bir.mp4", references.VIDEO, 3.0)]
    incoming = [item("iki.mp4", references.VIDEO, 3.0), item("üç.mp4", references.VIDEO, 3.0),
                item("dört.mp4", references.VIDEO, 3.0)]

    assert "3" in refusal(pool, incoming)
