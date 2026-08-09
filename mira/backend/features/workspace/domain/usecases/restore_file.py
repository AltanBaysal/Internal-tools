"""Put a deleted file back under the name it had."""
from backend.features.workspace.domain.errors import FileNotFound, NameTaken


def restore_file(file_store, project_id, trashed, name):
    restored = file_store.restore(project_id, trashed, name)
    if restored is None:
        raise FileNotFound(trashed)
    if restored is False:
        # Refused rather than renamed: the user pressed Undo, and anything other than the old name
        # would not be the thing they asked for. Overwriting would cost them a file outright.
        raise NameTaken(name)
