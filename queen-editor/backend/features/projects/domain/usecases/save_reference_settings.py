"""Store Referanstan's boxes as they were sent (madde 317).

save_settings' twin, and unvalidated for the same reason: the file exists to refill the boxes, and a
list the server refuses is still what the user typed. Reading needs no twin -- get_settings asks the
same question of whichever store it is handed.
"""
from backend.features.projects.domain.usecases.get_settings import ProjectMissing


def save_reference_settings(store, project, prompts, variants):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    store.write(project, {"prompts": prompts, "variants": variants})
