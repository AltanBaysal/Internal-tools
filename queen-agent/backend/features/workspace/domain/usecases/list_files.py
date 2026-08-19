"""List a project's files, newest first -- a new file belongs at the top of both lists."""


def list_files(file_store, project_id):
    # The name breaks ties so two files written in the same millisecond keep a fixed order.
    return sorted(
        file_store.list_files(project_id),
        key=lambda file: (file.modified_at, file.name),
        reverse=True,
    )
