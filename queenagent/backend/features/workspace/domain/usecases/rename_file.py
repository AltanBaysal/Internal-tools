"""Give a file a new name -- which is the name it has on disk, there being no second one."""
from backend.features.workspace.domain.errors import FileNotFound
from backend.features.workspace.domain.tools import safe_name


def rename_file(file_store, project_id, name, wanted):
    # A name typed by a person reaches the disk exactly as a name from the model does, so it is
    # cleaned by the same rule. The store's root is the second lock, not the only one.
    renamed = file_store.rename(project_id, name, safe_name(wanted))
    if renamed is None:
        raise FileNotFound(name)
    return renamed
