from backend.features.photo_generation.domain.photo_name import (
    file_name,
    frame_id,
    frame_id_of,
    number_of,
)


def test_a_frames_identity_is_its_number_and_letter():
    assert frame_id(12, "a") == "12_a"


def test_a_photo_file_name_yields_its_frames_identity():
    assert frame_id_of("12_a.png") == "12_a"


def test_a_name_that_is_already_an_identity_comes_back_unchanged():
    # Order files written after this change store identities; both shapes have to read.
    assert frame_id_of("12_a") == "12_a"


def test_a_file_name_is_its_identity_plus_the_extension():
    assert file_name(12, "a") == f"{frame_id(12, 'a')}.png"


def test_number_comes_from_the_name():
    assert number_of("12_a.png") == 12


def test_a_name_outside_the_scheme_has_no_number():
    assert number_of("notlar.txt") is None
    assert number_of("photos.jsonl") is None
    assert number_of("12.png") is None
    assert number_of("12_ab.png") is None
    assert number_of("x_a.png") is None
