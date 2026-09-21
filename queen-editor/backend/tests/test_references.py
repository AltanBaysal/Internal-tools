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
