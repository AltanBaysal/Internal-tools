"""Produce videos from the project's reference pool. Returns how many jobs the queue took.

Two things stop a run before it starts (madde 302), and the app says which: the engine that can read
references is not installed, or the pool is empty. Both are the app's to count -- H3 complains into
a Colab log the user never opens, and about an empty pool it would not complain at all.

Checked in the order a person would look: what is installed, then what they wrote, then what the
pool holds. Nothing is written until every one of them has passed.

What comes back are CARDS, not layers on frames that exist: one per prompt per variant, each born
from a video and holding no picture at all (madde 303). The gallery draws them because madde 292
taught it that a card is a box rather than a photo.
"""
from functools import partial

from backend.features.photo_generation.domain import layers, production_mode, references
from backend.features.photo_generation.domain.photo_name import frame_id
from backend.features.photo_generation.domain.prompt_list import parse_prompts
from backend.features.photo_generation.domain.usecases.list_references import list_references
from backend.features.photo_generation.domain.usecases.reference_files import reference_files
from backend.features.photo_generation.domain.usecases.run_queue import run_queue
from backend.features.photo_generation.domain.usecases.start_batch import (
    MAX_VARIANTS,
    InvalidVariants,
    ProjectMissing,
    next_number,
)

def plan_reference_cards(start, prompts, variants, new_seed):
    """[{"id", "type", "number", "variant", "prompt", …}] -- one video job per prompt per variant.

    plan_frames' twin, and deliberately not plan_frames with two more arguments: one makes photos
    from words and this makes cards from the pool, and a function that did both would be read twice
    to answer either question.

    Prompt-major like the photo batch (P0_0 P0_1 … P1_0), and the seed is drawn here for the same
    reason: the plan is what a resumed run reads back, so a card has to produce what it was planned
    to produce.

    The words ride on the line because the user wrote them. A video job usually carries none and a
    language model writes one when its turn comes -- and that writer leaves a line that has one.
    """
    return [{"id": frame_id(start + index, variant), "type": layers.VIDEO,
             "number": start + index, "variant": variant,
             "prompt": prompt, "negative": "", "seed": new_seed(), "model": "",
             "mode": production_mode.REFERENCE}
            for index, prompt in enumerate(prompts)
            for variant in range(variants)]


class NoReferenceProducer(Exception):
    """The installed video engine has no reference mode (message is user-facing)."""


def queue_references(runner, store, record, plan_store, order_store, pool, orders, producers,
                     new_seed, now, has_h3, project, prompts, variants,
                     log=None, writers=None, stills=None):
    """Returns how many cards the queue took."""
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    if not has_h3:
        # WAN has no such mode at all, so there is nothing to hand the pool to.
        raise NoReferenceProducer(
            "Referanstan üretim için H3 gerekiyor — bu oturumda başka bir video modeli kurulu.")
    written = parse_prompts(prompts)        # raises InvalidPrompts
    # bool is an int in Python, and True would silently mean "1 variant".
    if isinstance(variants, bool) or not isinstance(variants, int) \
            or not 1 <= variants <= MAX_VARIANTS:
        raise InvalidVariants(f"Varyant sayısı 1-{MAX_VARIANTS} arası bir tam sayı olmalı.")
    held = list_references(store, pool, orders, project)
    if not held:
        raise references.PoolLimit(
            "Havuzda referans yok — önce en az bir referans ekle.")
    cards = plan_reference_cards(next_number(store, plan_store, record, project),
                                 written, variants, new_seed)
    # Appended before the worker is asked to run, the way a photo batch does it: a run that dies
    # leaves behind what it meant to make, and a loop already in flight finds the cards on its next
    # turn.
    plan_store.append(project, cards)
    run_queue(runner, store, record, plan_store, producers, now, project, log,
              order_store=order_store, writers=writers, stills=stills,
              # The pool is read at each job's turn, not now: it is the user's to change while the
              # queue runs, and a card does not remember what it was made from (madde 304).
              references=partial(reference_files, store, pool, orders))
    return len(cards)
