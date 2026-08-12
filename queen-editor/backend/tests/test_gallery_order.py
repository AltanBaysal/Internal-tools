from backend.features.photo_generation.domain.gallery_order import apply_order


def rows(*frame_ids):
    return [{"id": fid, "prompt": "p"} for fid in frame_ids]


def ids(result):
    return [row["id"] for row in result]


def test_an_unordered_record_keeps_its_own_sequence():
    assert ids(apply_order(rows("2_a", "1_a"), [])) == ["2_a", "1_a"]


def test_a_stored_order_is_applied():
    result = apply_order(rows("2_a", "1_a", "0_a"), ["0_a", "2_a", "1_a"])
    assert ids(result) == ["0_a", "2_a", "1_a"]


def test_frames_the_order_never_heard_of_go_on_top():
    # The record is newest-first, so 4_a is newer than 3_a and stays above it.
    result = apply_order(rows("4_a", "3_a", "1_a", "0_a"), ["0_a", "1_a"])
    assert ids(result) == ["4_a", "3_a", "0_a", "1_a"]


def test_a_frame_the_record_does_not_know_is_ignored():
    assert ids(apply_order(rows("1_a"), ["silinmis", "1_a"])) == ["1_a"]


def test_a_repeated_identity_is_placed_once():
    result = apply_order(rows("1_a", "0_a"), ["1_a", "1_a", "0_a"])
    assert ids(result) == ["1_a", "0_a"]


def test_an_empty_record_returns_empty():
    assert apply_order([], ["1_a"]) == []
