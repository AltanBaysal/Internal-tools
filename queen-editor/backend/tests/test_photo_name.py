from backend.features.photo_generation.domain.photo_name import (
    audio_file,
    frame_id,
    frame_id_of,
    legacy_frame_id,
    number_of,
    photo_file,
    video_file,
)


def test_a_new_frames_identity_carries_the_prompt_and_the_variant():
    assert frame_id(11, 3) == "P11_3"


def test_variants_count_from_zero():
    # The design's "a=0, b=1" rule with the letters taken out.
    assert frame_id(11, 0) == "P11_0"


def test_the_photo_file_is_the_identity_with_an_extension():
    assert photo_file("P11_3") == "P11_3.png"


def test_a_video_file_grows_the_identity_by_its_own_pair():
    assert video_file("P11_3", 1, 0) == "P11_3_V1_0.mp4"


def test_an_audio_file_grows_the_video_name():
    # Audio is mixed over one video, so its name says which one.
    assert audio_file("P11_3_V1_0", 1, 0) == "P11_3_V1_0_S1_0.wav"


def test_a_legacy_identity_keeps_its_letter():
    assert legacy_frame_id(11, "d") == "11_d"


def test_a_layer_file_belongs_to_the_frame_its_name_starts_with():
    assert frame_id_of("P11_3_V1_0.mp4") == "P11_3"
    assert frame_id_of("P11_3_V1_0_S1_0.wav") == "P11_3"


def test_a_photo_file_yields_its_frames_identity_in_both_schemes():
    assert frame_id_of("P11_3.png") == "P11_3"
    assert frame_id_of("11_d.png") == "11_d"


def test_a_name_that_is_already_an_identity_comes_back_unchanged():
    # Order files store identities; both shapes have to read.
    assert frame_id_of("P11_3") == "P11_3"
    assert frame_id_of("11_d") == "11_d"


def test_both_schemes_yield_the_same_number():
    assert number_of("P11_3.png") == 11
    assert number_of("11_d.png") == 11
    assert number_of("P11_3_V1_0.mp4") == 11
    assert number_of("P11_3_V1_0_S1_0.wav") == 11


def test_a_name_outside_both_schemes_has_no_number():
    assert number_of("notlar.txt") is None
    assert number_of("photos.jsonl") is None
    assert number_of("P.png") is None
    assert number_of("Px_3.png") is None
    assert number_of("12.png") is None
    assert number_of("12_ab.png") is None
    assert number_of("x_a.png") is None
