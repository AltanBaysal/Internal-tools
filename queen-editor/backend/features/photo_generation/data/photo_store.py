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
# Folders the user opens in Drive, so they read in Turkish like the rest of what the user sees
# (madde 283, their own naming). An export written before this keeps the folder it was written
# with: every export has a dated folder of its own.
PHOTOS_DIR = "foto"
VIDEOS_DIR = "video"


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
        """Take a folder and everything in it. Used on a failed or cancelled export, and on the
        pieces of a merged one."""
        shutil.rmtree(path, ignore_errors=True)

    def make_pieces_dir(self):
        """An empty folder on the machine's own disk, for files that are thrown away again.

        A merged export cuts one piece per frame only to join them: the pieces are scaffolding, and
        Drive is the slow disk the user watches (madde 235). They also never collide with the other
        export mode's files this way -- the two modes share one dated folder on Drive.
        """
        return tempfile.mkdtemp(prefix="qe-export-")

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

    def make_videos_dir(self, folder):
        """Where a separate export writes its videos: a folder of its own inside the dated one.

        The dated folder held one mp4 per frame beside the photos folder, and the user asked for
        them gathered (madde 283). Unlike the pieces of a merged export, these are the export
        itself -- they stay on Drive, and nothing takes them away again.
        """
        videos = os.path.join(folder, VIDEOS_DIR)
        os.makedirs(videos, exist_ok=True)
        return videos

    def copy_export(self, source, folder, filename):
        """Bring the merged file in from the machine's own disk, whole.

        ffmpeg writes the join locally now: writing an encoded stream onto Drive's FUSE mount a
        piece at a time is a known Colab slowness, and the known answer is to write locally and
        copy at the end -- the call madde 235 made for the pieces, applied to the output (282).

        One move, like copy_photo: Drive is slow enough that the window in which a half written
        file could be seen is a real one, and a folder that looks finished is what madde 94 forbids.
        os.replace rather than os.rename, so Windows behaves like Linux over a target that exists.

        No "already there" answer here: the pieces' folder is this run's own, and a second run of
        the same mode is refused by ExportRunner.
        """
        handle, temporary = tempfile.mkstemp(dir=folder)
        os.close(handle)
        shutil.copyfile(source, temporary)
        os.replace(temporary, os.path.join(folder, filename))

    def export_dir(self, project):
        """Where an export lands: one folder inside the project, next to its photos.

        Named here rather than in the domain, which knows nothing about paths. The folder is not
        created -- an export run makes its own dated one inside it when it starts.
        """
        return os.path.join(self._storage.dir_path(project), EXPORT_DIR)
