"""PhotoStore over DriveStorage -- photos live inside the project folder under the name the domain
chose (see domain/photo_name.py).

Numbering never reuses a number: the next one is the highest on disk plus one, so a second run
appends instead of overwriting. Files that do not match the scheme (notes, the project's JSON
files) are ignored rather than guessed at. A deleted photo frees its name on disk but not its
number -- that claim is the record's to keep (see usecases/start_batch.next_number).

Listing the folder is deliberately not offered: which photos a project has is the photo record's
answer, and two ways to ask it would be two ways to disagree.
"""
import os
import shutil
import tempfile

from backend.features.photo_generation.domain.photo_name import number_of

# The project folder's own export area; a run makes a dated folder inside it (design v3, madde 92).
EXPORT_DIR = "export"
# The pictures ride inside the export in a folder of their own, so the mp4s stay a bare sequence.
PHOTOS_DIR = "photos"


class DrivePhotoStore:
    def __init__(self, storage):
        self._storage = storage

    def project_exists(self, project):
        return self._storage.dir_exists(project)

    def next_number(self, project):
        numbers = [n for n in (number_of(name) for name in self._storage.list_files(project))
                   if n is not None]
        return max(numbers) + 1 if numbers else 0

    def save(self, project, filename, data):
        self._storage.write_bytes(project, filename, data)
        return filename

    def read(self, project, filename):
        """The file's own bytes -- what an image-to-video render hangs on."""
        return self._storage.read_bytes(project, filename)

    def delete(self, project, filename):
        self._storage.delete_file(project, filename)

    def photo_dir(self, project):
        return self._storage.dir_path(project)

    def file_path(self, project, filename):
        """One file's full path -- what a tool outside this process is handed."""
        return os.path.join(self._storage.dir_path(project), filename)

    def make_export_folder(self, project, stamp):
        """A fresh folder for one export opening, named after the moment it started.

        Down to the minute (design v3, madde 92), so two exports of the same opening land in one
        folder and neither overwrites the other -- their file names never collide.
        """
        folder = os.path.join(self.export_dir(project), stamp)
        os.makedirs(folder, exist_ok=True)
        return folder

    def export_path(self, folder, filename):
        return os.path.join(folder, filename)

    def remove_dir(self, path):
        """Take a folder and everything in it. Used on a failed or cancelled export."""
        shutil.rmtree(path, ignore_errors=True)

    def copy_photo(self, source, folder, filename):
        """Put one picture in the export's photos folder, unless it is already there.

        Both export modes can run at once and a folder named down to the minute is one folder for
        both, so two threads asking for the same 01.png is the expected case rather than a corner
        one. Which is why there are two answers here and not one.

        Already there means nothing to do: the other mode has written the very same bytes, and
        writing them again buys nothing.

        And the write itself lands in one move. Two threads can both find the target missing and
        both start writing; two copies into one path is a half file. Copying to a name of its own
        and then moving it over means the target is never seen half written, whichever thread gets
        there last. os.replace rather than os.rename: on Windows rename refuses a target that is
        already there, and the two have to behave alike.
        """
        photos = os.path.join(folder, PHOTOS_DIR)
        os.makedirs(photos, exist_ok=True)
        target = os.path.join(photos, filename)
        if os.path.exists(target):
            return
        handle, temporary = tempfile.mkstemp(dir=photos)
        os.close(handle)
        shutil.copyfile(source, temporary)
        os.replace(temporary, target)

    def export_dir(self, project):
        """Where an export lands: one folder inside the project, next to its photos.

        Named here rather than in the domain, which knows nothing about paths. The folder is not
        created -- an export run makes its own dated one inside it when it starts.
        """
        return os.path.join(self._storage.dir_path(project), EXPORT_DIR)
