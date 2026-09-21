"""ReferenceStore over DriveStorage -- the pool is a folder inside the project.

Turkish, because the user opens this folder in Drive with their own eyes, like the export's foto and
video folders (madde 283, their own naming).

Beside the photos rather than among them: the project's own files sit at its root and next_number
reads them, and a subfolder is not a file -- so the pool never touches numbering.

Read by name, which is the one order the disk can really promise. The order the files were written
in cannot be had: a timestamp is coarser than the writes, so two files of one upload sometimes share
one and sometimes do not, and the pool would read back differently on two machines. The order the
USER wants is a different question anyway, and it gets a document of its own (madde 300).
"""
import os

# The project folder's own reference area.
REFERENCE_DIR = "referans"


class DriveReferenceStore:
    def __init__(self, storage):
        self._storage = storage

    def save(self, project, name, data):
        self._storage.write_bytes(self._subdir(project), name, data)

    def names(self, project):
        return sorted(self._storage.list_files(self._subdir(project)))

    def delete(self, project, name):
        self._storage.delete_file(self._subdir(project), name)

    def dir_path(self, project):
        """Absolute folder the pool lives in -- presentation serves files straight from it."""
        return self._storage.dir_path(self._subdir(project))

    def _subdir(self, project):
        return os.path.join(project, REFERENCE_DIR)
