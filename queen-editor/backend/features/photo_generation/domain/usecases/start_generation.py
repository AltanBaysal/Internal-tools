"""Start one photo: validate, reserve a number, hand a single step to the runner.

Pure: the seed comes from an injected `new_seed` callable (randomness would make this untestable),
and the runner/store/generator are ports. The exception messages are the user-facing Turkish text --
presentation maps them to status codes and forwards them untouched.
"""


class InvalidPrompt(Exception):
    """Empty prompt (message is user-facing)."""


class ProjectMissing(Exception):
    """No such project folder."""


class Busy(Exception):
    """A generation is already running."""


def start_generation(runner, store, generator, new_seed, project, prompt):
    if not prompt or not prompt.strip():
        raise InvalidPrompt("Prompt boş olamaz.")
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")

    number = store.next_number(project)
    seed = new_seed()

    def step():
        # One photo per job in Part 4; Part 5 hands the runner a list of these.
        data = generator.generate(prompt, seed)
        return store.save(project, number, "a", data)

    if not runner.start(project, step):
        raise Busy("Zaten bir üretim sürüyor.")
