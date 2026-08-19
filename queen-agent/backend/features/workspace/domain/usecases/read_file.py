"""Read one file: the panel wants the text and the file's own particulars in the same breath."""
from backend.features.workspace.domain.errors import FileNotFound


def read_file(file_store, project_id, name):
    body = file_store.read_body(project_id, name)
    if body is None:
        raise FileNotFound(name)
    return body
