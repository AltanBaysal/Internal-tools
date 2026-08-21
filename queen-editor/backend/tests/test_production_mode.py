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
