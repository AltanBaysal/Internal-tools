"""Read and save the project's Mutlu son switch (madde 426).

The messages are user-facing Turkish; presentation forwards them untouched.
"""
from backend.features.photo_generation.domain import happy_ending
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def get_happy_ending(switches, project):
    """Whether the project's videos end happily: what was saved, or off when nothing usable was."""
    if not switches.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    return switches.read(project) is True


def save_happy_ending(switches, project, on):
    """The value is refused before the project is looked for: the cheap refusal comes first. The
    project must already exist -- writing would otherwise create one, and every folder under the root
    counts as a project."""
    happy_ending.check(on)
    if not switches.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    switches.write(project, on)
