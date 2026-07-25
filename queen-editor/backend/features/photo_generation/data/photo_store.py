"""PhotoStore over DriveStorage -- the only place that knows photos are named "<n>_<letter>.png"
inside the project folder.

Numbering never reuses a number: the next one is the highest on disk plus one, so a second run
appends instead of overwriting. Files that do not match the scheme (notes, half-written names) are
ignored rather than guessed at.
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

    def list_photos(self, project):
        """Photo file names, newest number first, letters ascending inside a number.

        Sorted here rather than in the UI: the order is part of what the file names mean, and this
        is the only place that understands them.
        """
        numbered = [(number, name)
                    for number, name in ((_number_of(name), name)
                                         for name in self._storage.list_files(project))
                    if number is not None]
        numbered.sort(key=lambda item: (-item[0], item[1]))
        return [name for _number, name in numbered]

    def save(self, project, number, letter, data):
        filename = f"{number}_{letter}.png"
        self._storage.write_bytes(project, filename, data)
        return filename

    def photo_dir(self, project):
        return self._storage.dir_path(project)
