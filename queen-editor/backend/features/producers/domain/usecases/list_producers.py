"""What the Üreticiler panel draws: three rows, each with a name and an answer.

A kind with no producer object at all is not installed -- the same rule the engine already applies
when it refuses to dispatch a job type nobody can do. A producer that cannot answer at all is not
quietly called missing: the error travels up, because "not installed" would invite a download that
would fix nothing.
"""
from backend.features.producers.domain.producers import NAMES, ORDER


def list_producers(producers):
    return [{"id": kind, "name": NAMES[kind],
             "installed": bool(producers.get(kind)) and producers[kind].installed()}
            for kind in ORDER]
