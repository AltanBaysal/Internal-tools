"""The number a job is rendered with, when the job carries none.

One range for every seed in the app: a photo job is planned in it, and a layer job is given one out
of it when its turn comes. A seed is a seed wherever it was born, and three copies of the same
range in three files is how they stop being the same range.
"""
from backend.features.photo_generation.domain import seed


def test_a_seed_is_inside_the_range_a_photo_job_is_planned_in():
    for _ in range(50):
        number = seed.random_seed()
        assert 0 <= number <= seed.MAX


def test_two_seeds_are_not_the_same_number():
    """Not a claim about randomness -- a generator that answered 7 every time would pass every other
    test in this run and make every variant of a frame identical."""
    assert len({seed.random_seed() for _ in range(20)}) > 1
