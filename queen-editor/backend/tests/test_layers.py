from backend.features.photo_generation.domain import layers, queue


def test_an_empty_slot_can_be_produced_into():
    assert layers.can_produce({}, layers.VIDEO) is True


def test_a_produced_layer_cannot_be_overwritten():
    assert layers.can_produce({layers.VIDEO: queue.DONE}, layers.VIDEO) is False


def test_a_failed_layer_counts_as_present():
    # The user's call: a red layer stays out of the panel's scope and is rescued by Tekrar dene.
    assert layers.can_produce({layers.VIDEO: queue.FAILED}, layers.VIDEO) is False


def test_a_deleted_layer_frees_the_slot():
    assert layers.can_produce({layers.VIDEO: queue.DELETED}, layers.VIDEO) is True


def test_a_requeued_layer_frees_the_slot():
    assert layers.can_produce({layers.VIDEO: queue.QUEUED}, layers.VIDEO) is True


def test_audio_needs_a_video_under_it():
    assert layers.can_produce({}, layers.AUDIO) is False
    assert layers.can_produce({layers.VIDEO: queue.DONE}, layers.AUDIO) is True


def test_a_taken_audio_slot_is_refused_like_any_other():
    assert layers.can_produce({layers.VIDEO: queue.DONE,
                               layers.AUDIO: queue.DONE}, layers.AUDIO) is False


def test_a_photo_slot_needs_nothing_under_it():
    assert layers.can_produce({}, layers.PHOTO) is True


def cell(file, status=queue.DONE):
    return {"status": status, "file": file}


def test_a_closed_slots_file_is_unlinked():
    slots = {"12_a": {layers.PHOTO: cell("12_a.png")}}
    assert layers.files_to_unlink(slots, {("12_a", layers.PHOTO)}) == {"12_a.png"}


def test_a_file_another_frame_still_holds_stays():
    # An audio variant shares its source's video (design v3, madde 102).
    slots = {"12_a": {layers.PHOTO: cell("12_a.png"), layers.VIDEO: cell("shared.mp4")},
             "13_a": {layers.PHOTO: cell("13_a.png"), layers.VIDEO: cell("shared.mp4")}}
    closing = {("12_a", layers.PHOTO), ("12_a", layers.VIDEO)}
    assert layers.files_to_unlink(slots, closing) == {"12_a.png"}


def test_the_last_holder_takes_the_shared_file_with_it():
    slots = {"12_a": {layers.VIDEO: cell("shared.mp4")},
             "13_a": {layers.VIDEO: cell("shared.mp4")}}
    closing = {("12_a", layers.VIDEO), ("13_a", layers.VIDEO)}
    assert layers.files_to_unlink(slots, closing) == {"shared.mp4"}


def test_an_empty_slot_unlinks_nothing():
    # A frame pulled out of the queue never had a file, so closing it deletes nothing.
    slots = {"12_a": {layers.PHOTO: cell("12_a.png", queue.REMOVED)}}
    assert layers.files_to_unlink(slots, {("12_a", layers.PHOTO)}) == set()


def test_closing_nothing_unlinks_nothing():
    slots = {"12_a": {layers.PHOTO: cell("12_a.png")}}
    assert layers.files_to_unlink(slots, set()) == set()
