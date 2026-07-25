"""Start a batch: validate, plan the frames, hand ONE job to the runner.

The loop lives here rather than in the runner: it is business behaviour (order, numbering, what a
failure costs), and here it is testable with a synchronous spawn -- no threads in a test.

Pure: the seed comes from an injected `new_seed`, and runner/store/generator are ports. The
exception messages are the user-facing Turkish text; presentation maps them to status codes and
forwards them untouched.
"""
from backend.features.photo_generation.domain import policy
from backend.features.photo_generation.domain.prompt_list import parse_prompts

LETTERS = "abcdefghijklmnopqrstuvwxyz"


class InvalidVariants(Exception):
    """Variant count outside 1..len(LETTERS) (message is user-facing)."""


class ProjectMissing(Exception):
    """No such project folder."""


class Busy(Exception):
    """A generation is already running."""


def plan_frames(start, prompts, variants):
    """[(number, letter, prompt)] in prompt-major order: 0_a 0_b … 1_a.

    Number = prompt, letter = variant -- nova-3dcg's meaning, kept so a photo's name still says
    which prompt produced it.
    """
    return [(start + index, LETTERS[variant], prompt)
            for index, prompt in enumerate(prompts)
            for variant in range(variants)]


def start_batch(runner, store, generator, new_seed, project, text, negative, variants):
    prompts = parse_prompts(text)          # raises InvalidPrompts
    # bool is an int in Python, and True would silently mean "1 variant".
    if isinstance(variants, bool) or not isinstance(variants, int) \
            or not 1 <= variants <= len(LETTERS):
        raise InvalidVariants(f"Varyant sayısı 1-{len(LETTERS)} arası bir tam sayı olmalı.")
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")

    frames = plan_frames(store.next_number(project), prompts, variants)
    total = len(frames)

    def job():
        done = failed = consecutive = 0
        for number, letter, prompt in frames:
            if runner.stop_requested():
                return {"status": "stopped", "done": done, "failed": failed, "total": total}
            runner.report({"done": done, "failed": failed, "total": total,
                           "current": {"number": number, "letter": letter, "prompt": prompt}})
            try:
                data = generator.generate(prompt, negative, new_seed())
            except Exception as exc:
                failed += 1
                consecutive += 1
                # getattr, not isinstance: domain must not import the ComfyUI service.
                reason = policy.stop_reason(consecutive, getattr(exc, "infra", False))
                if reason:
                    return {"status": "error", "error": f"{reason}\n{exc}",
                            "done": done, "failed": failed, "total": total}
                continue
            store.save(project, number, letter, data)
            done += 1
            consecutive = 0
        return {"status": "done", "done": done, "failed": failed, "total": total}

    if not runner.start(project, job):
        raise Busy("Zaten bir üretim sürüyor.")
