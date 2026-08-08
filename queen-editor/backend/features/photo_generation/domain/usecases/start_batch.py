"""Submit a batch: validate, plan the frames, put them at the end of the queue, run the queue.

Adding work and running it are separate acts (see run_queue), which is what lets a batch be sent
while another one renders.

Pure: the seed comes from an injected `new_seed`, and runner/store/generator are ports. The
exception messages are the user-facing Turkish text; presentation maps them to status codes and
forwards them untouched.
"""
from backend.features.photo_generation.domain.prompt_list import parse_prompts
from backend.features.photo_generation.domain.usecases.run_queue import Busy, run_queue  # noqa: F401

LETTERS = "abcdefghijklmnopqrstuvwxyz"


class InvalidVariants(Exception):
    """Variant count outside 1..len(LETTERS) (message is user-facing)."""


class ProjectMissing(Exception):
    """No such project folder."""


def plan_frames(start, prompts, negative, variants, new_seed, model=""):
    """[{"number", "letter", "prompt", "negative", "seed", "model"}] in prompt-major order.

    Prompt-major means 0_a 0_b … 1_a. Number = prompt, letter = variant -- nova-3dcg's meaning,
    kept so a photo's name still says which prompt produced it.

    The negative and the model ride on the frame rather than on the plan: a live queue holds
    batches submitted under different settings, and a frame has to render with the ones it was
    submitted under.

    Seeds are drawn here, when the frames are planned, rather than when a frame renders: the plan is
    what a resumed run reads back, so a frame has to produce the image it was planned to produce.
    """
    return [{"number": start + index, "letter": LETTERS[variant], "prompt": prompt,
             "negative": negative, "seed": new_seed(), "model": model}
            for index, prompt in enumerate(prompts)
            for variant in range(variants)]


def next_number(store, plan_store, record, project):
    """The first number a new batch may use.

    Three things can claim a number: a file already on disk, a frame the plan reserved but never
    produced, and a name the record has seen -- deleted photos and frames pulled out of the queue
    included, which disk no longer remembers. All are honoured: reusing a number would bind one file
    name to two prompts, and a browser holding the old photo under an immutable cache header would
    keep showing the old image.
    """
    claims = [store.next_number(project)]
    reserved = plan_store.max_number(project)
    if reserved is not None:
        claims.append(reserved + 1)
    seen = record.max_number(project)
    if seen is not None:
        claims.append(seen + 1)
    return max(claims)


def start_batch(runner, store, record, plan_store, generator, new_seed, now,
                project, text, negative, variants, model=""):
    prompts = parse_prompts(text)          # raises InvalidPrompts
    # bool is an int in Python, and True would silently mean "1 variant".
    if isinstance(variants, bool) or not isinstance(variants, int) \
            or not 1 <= variants <= len(LETTERS):
        raise InvalidVariants(f"Varyant sayısı 1-{len(LETTERS)} arası bir tam sayı olmalı.")
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")

    # The model is not checked against what is installed: whether it can be loaded is the
    # renderer's answer to give, at render time, in its own words (Madde 8's rule).
    frames = plan_frames(next_number(store, plan_store, record, project), prompts, negative,
                         variants, new_seed, model)
    # Appended before the worker is asked to run: a run that dies leaves behind what it meant to
    # make, and a loop already in flight finds the frames on its next turn.
    plan_store.append(project, frames)
    run_queue(runner, store, record, plan_store, generator, now, project)
    # How many frames the queue really took. The panel's own "12 prompt × 4 varyant" line is a
    # preview it is not allowed to enforce, so the confirmation card quotes this instead.
    return len(frames)
