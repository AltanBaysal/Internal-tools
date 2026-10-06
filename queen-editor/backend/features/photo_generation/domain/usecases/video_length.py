"""Read and save how long the project's H3 videos run (madde 422).

The messages are user-facing Turkish; presentation forwards them untouched.
"""
from backend.features.photo_generation.domain import video_length
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def get_video_length(lengths, project):
    """The project's length in seconds: what was saved, or 8 when nothing usable was."""
    if not lengths.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    saved = lengths.read(project)
    return saved if saved in video_length.LENGTHS else video_length.DEFAULT


def save_video_length(lengths, project, seconds):
    """The value is refused before the project is looked for: the cheap refusal comes first. The
    project must already exist -- writing would otherwise create one, and every folder under the root
    counts as a project."""
    video_length.check(seconds)
    if not lengths.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    lengths.write(project, seconds)
