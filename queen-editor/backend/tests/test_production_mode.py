"""How a video job says where it ends.

The three names live in the domain because the queue writes them, the engine reads them and the
screen only labels them. What the user sees in Turkish is the frontend's business; nothing here
knows those words.
"""
from backend.features.photo_generation.domain import production_mode


def test_a_job_that_names_a_mode_has_that_mode():
    assert production_mode.of({"mode": production_mode.STANDARD}) == production_mode.STANDARD
    assert production_mode.of({"mode": production_mode.LOOP}) == production_mode.LOOP
    assert production_mode.of({"mode": production_mode.LINKED}) == production_mode.LINKED


def test_a_job_that_names_no_mode_is_a_plain_one():
    """Every video job planned before this madde carries no mode, and each of them has to go on
    rendering exactly as it does today. Standard is not a tolerance here, it is the right answer."""
    assert production_mode.of({"type": "video"}) == production_mode.STANDARD


def test_a_mode_nobody_knows_is_read_as_the_plain_one():
    """A hand-edited plan or a newer client is not a reason to stop a run: the queue refuses an
    unknown mode at the door (queue_layer), and by the time a job is being rendered the only honest
    reading left is the plain one."""
    assert production_mode.of({"mode": "kelebek"}) == production_mode.STANDARD


def test_the_three_modes_are_the_whole_list():
    # ALL is what the queue validates against; a mode missing from it could never be asked for.
    assert production_mode.ALL == (production_mode.STANDARD, production_mode.LOOP,
                                   production_mode.LINKED)


def gallery(*rows):
    """Frames as list_frames hands them over: newest first, so the film runs from the foot up."""
    return [{"id": fid, "status": status} for fid, status in rows]


def test_a_linked_video_ends_on_the_frame_above_it():
    """The film's sequence, not the gallery's reading order: the export stitches the gallery
    reversed, so the frame that plays next is the one above."""
    assert production_mode.frame_after(gallery(("1_a", "done"), ("0_a", "done")), "0_a") == "1_a"


def test_the_frame_at_the_top_of_the_gallery_has_nothing_after_it():
    # The film's last frame. Two use cases read this: the queue drops that job, the detail page
    # closes the option.
    assert production_mode.frame_after(gallery(("1_a", "done"), ("0_a", "done")), "1_a") is None


def test_a_next_frame_with_no_picture_yet_is_no_target():
    # There is nothing to end on: the same emptiness as having no next at all, seen from closer up.
    assert production_mode.frame_after(gallery(("1_a", "pending"), ("0_a", "done")), "0_a") is None
