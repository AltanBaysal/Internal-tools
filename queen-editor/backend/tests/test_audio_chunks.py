import pytest

from backend.features.photo_generation.domain.audio_chunks import MAXIMUM, TARGET, chunks


def test_a_video_the_model_was_trained_for_is_one_piece():
    assert chunks(8.0) == [(0, 8.0)]


def test_the_limit_itself_is_still_one_piece():
    """10s is the ceiling, not the first split: the rule is "longer than", so the boundary stays
    whole and a 5-second frame -- what this version makes -- never touches the chunker."""
    assert chunks(MAXIMUM) == [(0, MAXIMUM)]
    assert chunks(5.0) == [(0, 5.0)]


def test_a_long_video_is_split_towards_the_length_the_model_knows():
    assert chunks(24.0) == [(0, 8.0), (8.0, 8.0), (16.0, 8.0)]


def test_the_split_prefers_the_target_over_the_fewest_pieces():
    """20s would fit in two 10s pieces, but two 10s pieces drift from the 8s the model was trained
    on; three under-8s pieces do not. The rule takes whichever count is larger."""
    assert len(chunks(20.0)) == 3


def test_no_piece_is_longer_than_the_limit():
    for total in (11.0, 17.5, 31.0, 47.3):
        assert all(duration <= MAXIMUM for _start, duration in chunks(total))


def test_the_pieces_add_up_to_the_whole_video():
    for total in (8.0, 13.0, 24.0, 47.3):
        pieces = chunks(total)
        assert pieces[0][0] == 0
        assert sum(duration for _start, duration in pieces) == pytest.approx(total)
        # Each piece starts where the one before it ended -- no gap, no overlap.
        for (start, duration), (next_start, _) in zip(pieces, pieces[1:]):
            assert start + duration == pytest.approx(next_start)


def test_the_defaults_are_the_ones_the_model_was_trained_with():
    assert (TARGET, MAXIMUM) == (8.0, 10.0)
