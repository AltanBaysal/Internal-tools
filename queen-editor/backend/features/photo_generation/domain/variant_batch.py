"""Which of the owed photos one render makes together (madde 411).

A prompt's variants are planned as frames of their own -- P3_0, P3_1, ... -- that share everything a
picture is made from and differ only in their seed. ComfyUI makes them as one batch from one seed,
so the variants standing together at the head of the queue go to it as one job.
"""
from backend.features.photo_generation.domain import layers, queue

# What a picture is made from beside its seed: variants that agree on all of it render alike.
MADE_FROM = ("prompt", "negative", "model", "lora")


def _variant_of(job, head):
    """Whether `job` is a photo of the prompt `head` was planned from."""
    return (queue.type_of(job) == layers.PHOTO and job.get("number") == head.get("number")
            and all(job.get(key) == head.get(key) for key in MADE_FROM))


def _fresh(job, slots):
    """Never had a turn: nothing was ever written about its picture. A photo sent back with Tekrar
    dene has its line, and is made alone with its own seed, the way it always was."""
    return layers.PHOTO not in slots.get(job["id"], {})


def together(owed, slots):
    """The head of the queue and the variants of its prompt standing right behind it.

    Right behind it, never gathered from further down: the gallery's order is the order work is done
    in, so a variant dragged elsewhere is made where it stands. Only a photo: a video's variants each
    start from a picture of their own.
    """
    head = owed[0]
    if not (_variant_of(head, head) and _fresh(head, slots)):
        return [head]
    group = [head]
    for job in owed[1:]:
        if not (_variant_of(job, head) and _fresh(job, slots)):
            break
        group.append(job)
    return group


def asked(jobs, head):
    """How many variants the plan asked of `head`'s prompt: the batch a card has to hold."""
    return len({job["id"] for job in jobs if _variant_of(job, head)})
