from backend.features.photo_generation.domain.photo_name import number_of


def test_number_comes_from_the_name():
    assert number_of("12_a.png") == 12


def test_a_name_outside_the_scheme_has_no_number():
    assert number_of("notlar.txt") is None
    assert number_of("photos.jsonl") is None
    assert number_of("12.png") is None
    assert number_of("12_ab.png") is None
    assert number_of("x_a.png") is None
