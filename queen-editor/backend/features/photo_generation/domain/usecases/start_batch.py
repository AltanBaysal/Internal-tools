"""Submit a batch: validate, plan the frames, put them at the end of the queue, run the queue.

Adding work and running it are separate acts (see run_queue), which is what lets a batch be sent
while another one renders.

Pure: the seed comes from an injected `new_seed`, and runner/store/generator are ports. The
exception messages are the user-facing Turkish text; presentation maps them to status codes and
forwards them untouched.
"""
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.photo_name import frame_id
from backend.features.photo_generation.domain.prompt_list import parse_prompts
from backend.features.photo_generation.domain.usecases.run_queue import Busy, run_queue  # noqa: F401

# Where the ceiling comes from: it was the alphabet's length while variants were letters, and it
# stayed when they became numbers -- the design turning them into numbers is not a decision to lift
# the ceiling.
MAX_VARIANTS = 26


class InvalidVariants(Exception):
    """Variant count outside 1..MAX_VARIANTS (message is user-facing)."""


class ProjectMissing(Exception):
    """No such project folder."""


def plan_frames(start, prompts, negative, variants, new_seed, model=""):
    """[{"id", "type", "number", "variant", "prompt", …}] photo jobs in prompt-major order.

    Prompt-major means P0_0 P0_1 … P1_0. Number = prompt, variant = which of its variants -- the
    prompt number is kept so a photo's name still says what produced it.

    The identity is written down here rather than computed later, and that is the point: it is the
    one thing about a frame that must never change. A computed identity would have moved under every
    frame on Drive the moment the naming scheme changed, and the gallery order the user dragged into
    place points at exactly these strings.

    The negative and the model ride on the frame rather than on the plan: a live queue holds
    batches submitted under different settings, and a frame has to render with the ones it was
    submitted under.

    Seeds are drawn here, when the frames are planned, rather than when a frame renders: the plan is
    what a resumed run reads back, so a frame has to produce the image it was planned to produce.
    """
    return [{"id": frame_id(start + index, variant), "type": layers.PHOTO,
             "number": start + index, "variant": variant,
             "prompt": prompt, "negative": negative, "seed": new_seed(), "model": model}
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


def start_batch(runner, store, record, plan_store, producers, new_seed, now,
                project, text, negative, variants, model="", log=None):
    prompts = parse_prompts(text)          # raises InvalidPrompts
    # bool is an int in Python, and True would silently mean "1 variant".
    if isinstance(variants, bool) or not isinstance(variants, int) \
            or not 1 <= variants <= MAX_VARIANTS:
        raise InvalidVariants(f"Varyant sayısı 1-{MAX_VARIANTS} arası bir tam sayı olmalı.")
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")

    # The model is not checked against what is installed: whether it can be loaded is the
    # renderer's answer to give, at render time, in its own words (Madde 8's rule).
    frames = plan_frames(next_number(store, plan_store, record, project), prompts, negative,
                         variants, new_seed, model)
    # Appended before the worker is asked to run: a run that dies leaves behind what it meant to
    # make, and a loop already in flight finds the frames on its next turn.
    plan_store.append(project, frames)
    run_queue(runner, store, record, plan_store, producers, now, project, log)
    # How many frames the queue really took. The panel's own "12 prompt × 4 varyant" line is a
    # preview it is not allowed to enforce, so the confirmation card quotes this instead.
    return len(frames)
