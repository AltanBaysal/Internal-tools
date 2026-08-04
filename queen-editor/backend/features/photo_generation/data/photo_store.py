"""PhotoStore over DriveStorage -- photos live inside the project folder, named by
domain/photo_name.py.

Numbering never reuses a number: the next one is the highest on disk plus one, so a second run
appends instead of overwriting. Files that do not match the scheme (notes, the project's JSON
files) are ignored rather than guessed at. A deleted photo frees its name on disk but not its
number -- that claim is the record's to keep (see usecases/start_batch.next_number).

Listing the folder is deliberately not offered: which photos a project has is the photo record's
answer, and two ways to ask it would be two ways to disagree.
"""
from backend.features.photo_generation.domain.photo_name import number_of


class DrivePhotoStore:
    def __init__(self, storage):
        self._storage = storage

    def project_exists(self, project):
        return self._storage.dir_exists(project)

    def next_number(self, project):
        numbers = [n for n in (number_of(name) for name in self._storage.list_files(project))
                   if n is not None]
        return max(numbers) + 1 if numbers else 0

    def save(self, project, number, letter, data):
        filename = f"{number}_{letter}.png"
        self._storage.write_bytes(project, filename, data)
        return filename

    def delete(self, project, filename):
        self._storage.delete_file(project, filename)

    def photo_dir(self, project):
        return self._storage.dir_path(project)
