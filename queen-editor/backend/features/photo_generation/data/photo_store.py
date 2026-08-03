"""PhotoStore over DriveStorage -- the only place that knows photos are named "<n>_<letter>.png"
inside the project folder.

Numbering never reuses a number: the next one is the highest on disk plus one, so a second run
appends instead of overwriting. Files that do not match the scheme (notes, the project's JSON
files) are ignored rather than guessed at.

Listing the folder is deliberately not offered: which photos a project has is the photo record's
answer, and two ways to ask it would be two ways to disagree.
"""


def _number_of(filename):
    """"12_a.png" -> 12; anything that does not fit the scheme -> None."""
    if not filename.endswith(".png"):
        return None
    number, _, letter = filename[: -len(".png")].partition("_")
    if not number.isdigit() or len(letter) != 1 or not letter.isalpha():
        return None
    return int(number)


class DrivePhotoStore:
    def __init__(self, storage):
        self._storage = storage

    def project_exists(self, project):
        return self._storage.dir_exists(project)

    def next_number(self, project):
        numbers = [n for n in (_number_of(name) for name in self._storage.list_files(project))
                   if n is not None]
        return max(numbers) + 1 if numbers else 0

    def save(self, project, number, letter, data):
        filename = f"{number}_{letter}.png"
        self._storage.write_bytes(project, filename, data)
        return filename

    def photo_dir(self, project):
        return self._storage.dir_path(project)
