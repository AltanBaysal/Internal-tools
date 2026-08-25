"""The number a render is reproducible by.

One range for the whole app: a photo job is planned in it (start_batch), and a layer job -- which
plans none -- is given one out of it when its turn comes. A seed is a seed wherever it was born, and
the same range written out in three files is how it stops being the same range.

The ceiling is torch's: manual_seed takes a long, and 2**31 - 1 is the width every graph and every
sampler in this app agrees on.
"""
import random

MAX = 2**31 - 1


def random_seed():
    return random.randint(0, MAX)
