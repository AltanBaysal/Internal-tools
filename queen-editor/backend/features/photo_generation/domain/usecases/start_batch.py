"""Start a batch: validate, plan the frames, hand ONE job to the runner.

The loop lives here rather than in the runner: it is business behaviour (order, numbering, what a
failure costs), and here it is testable with a synchronous spawn -- no threads in a test.

Pure: the seed comes from an injected `new_seed`, and runner/store/generator are ports. The
exception messages are the user-facing Turkish text; presentation maps them to status codes and
forwards them untouched.
"""
from backend.features.photo_generation.domain.run_loop import make_job
from backend.features.photo_generation.domain.prompt_list import parse_prompts

LETTERS = "abcdefghijklmnopqrstuvwxyz"


class InvalidVariants(Exception):
    """Variant count outside 1..len(LETTERS) (message is user-facing)."""


class ProjectMissing(Exception):
    """No such project folder."""


class Busy(Exception):
    """A generation is already running."""


def plan_frames(start, prompts, variants, new_seed):
    """[{"number", "letter", "prompt", "seed"}] in prompt-major order: 0_a 0_b … 1_a.

    Number = prompt, letter = variant -- nova-3dcg's meaning, kept so a photo's name still says
    which prompt produced it.

    Seeds are drawn here, when the run is planned, rather than when a frame renders: the plan is
    what a resumed run reads back, so a frame has to produce the image it was planned to produce.
    """
    return [{"number": start + index, "letter": LETTERS[variant], "prompt": prompt,
             "seed": new_seed()}
            for index, prompt in enumerate(prompts)
            for variant in range(variants)]


def next_number(store, plan_store, record, project):
    """The first number a new run may use.

    Three things can claim a number: a file already on disk, a frame an earlier plan reserved but
    never produced, and a photo that has since been deleted -- the record remembers those even
    though disk no longer does. All are honoured: reusing a number would bind one file name to two
    prompts, and a browser holding the deleted photo under an immutable cache header would keep
    showing the old image.
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
                project, text, negative, variants):
    prompts = parse_prompts(text)          # raises InvalidPrompts
    # bool is an int in Python, and True would silently mean "1 variant".
    if isinstance(variants, bool) or not isinstance(variants, int) \
            or not 1 <= variants <= len(LETTERS):
        raise InvalidVariants(f"Varyant sayısı 1-{len(LETTERS)} arası bir tam sayı olmalı.")
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")

    frames = plan_frames(next_number(store, plan_store, record, project), prompts, variants,
                         new_seed)
    # Written before the first render, so a run that dies leaves behind what it meant to make.
    plan_store.write(project, negative, frames)

    job = make_job(runner, store, record, generator, now, project, negative, frames)
    if not runner.start(project, job):
        raise Busy("Zaten bir üretim sürüyor.")
