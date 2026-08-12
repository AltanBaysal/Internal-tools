from backend.features.photo_generation.domain.copy_frame import next_id
from backend.features.photo_generation.domain.photo_name import (
    audio_file,
    frame_id,
    frame_id_of,
    layer_file,
    legacy_frame_id,
    number_of,
    photo_file,
    variant_of,
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


def test_a_layers_file_is_named_by_what_it_is():
    assert layer_file("photo", "P11_3") == "P11_3.png"
    # The first (and only) video of a frame: round 1, variant 0 -- a second video is a new frame.
    assert layer_file("video", "P11_3") == "P11_3_V1_0.mp4"


def test_a_sounds_file_grows_the_videos_name():
    assert layer_file("audio", "P11_3", video="P11_3_V1_0.mp4") == "P11_3_V1_0_S1_0.wav"


def test_a_sound_with_no_video_falls_back_to_the_frames_own_name():
    # Should not happen -- sound is never in scope without a video -- but a name is still a name.
    assert layer_file("audio", "P11_3") == "P11_3_S1_0.wav"


def test_a_name_says_which_variant_it_is():
    assert variant_of("P11_3.png") == 3
    assert variant_of("P11_3_V1_0.mp4") == 3
    # a=0, b=1: the letter scheme's variants are the same numbers written differently.
    assert variant_of("11_d.png") == 3
    assert variant_of("11_a.png") == 0


def test_a_name_outside_both_schemes_has_no_variant():
    assert variant_of("kapak.png") is None
    assert variant_of("12.png") is None
    assert variant_of("Px_3.png") is None


def test_a_copy_takes_the_next_variant_of_its_source():
    assert next_id({"P11_0", "P11_1", "P4_9"}, 11) == "P11_2"


def test_a_copy_of_a_letter_named_frame_joins_the_same_family():
    # 11_d is variant 3 written the old way: the copy is the family's next, not its second.
    assert next_id({"11_a", "11_d"}, 11) == "P11_4"


def test_a_gap_left_by_a_deleted_variant_is_not_reused():
    # The deleted frame keeps its line in the record, so its name stays claimed.
    assert next_id({"P11_0", "P11_2"}, 11) == "P11_3"


def test_the_first_copy_of_an_untouched_number_is_variant_zero():
    assert next_id({"P4_0"}, 11) == "P11_0"
