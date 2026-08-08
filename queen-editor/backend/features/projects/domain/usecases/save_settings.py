"""Store the panel's content as it was submitted.

Deliberately unvalidated: the file exists to refill the boxes, and text the generator rejected is
still what the user typed. The project folder must already exist -- writing would otherwise create
one, and every folder under the root counts as a project.
"""
from backend.features.projects.domain.usecases.get_settings import ProjectMissing


def save_settings(store, project, prompts, negative, variants, model=""):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    store.write(project, {"prompts": prompts, "negative": negative, "variants": variants,
                          "model": model})
