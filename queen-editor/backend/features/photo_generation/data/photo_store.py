"""PhotoStore over Storage -- photos live inside the project folder under the name the domain
chose (see domain/photo_name.py).

Numbering never reuses a number: the next one is the highest on disk plus one, so a second run
appends instead of overwriting. Files that do not match the scheme (notes, the project's JSON
files) are ignored rather than guessed at. A deleted photo frees its name on disk but not its
number -- that claim is the record's to keep (see usecases/start_batch.next_number).

Listing the folder is deliberately not offered: which photos a project has is the photo record's
answer, and two ways to ask it would be two ways to disagree.

Drive is reached through the storage door alone, exports included. What an export cuts on the
machine's own disk -- its pieces, scaffolding thrown away again -- is the one thing here that is not
Drive, and the one thing handled with tempfile and shutil.
"""
import os
import shutil
import tempfile

from backend.features.photo_generation.domain.photo_name import number_of

# The pictures ride inside the export in a folder of their own, so the mp4s stay a bare sequence.
# Folders the user opens in Drive, so they read in Turkish like the rest of what the user sees
# (madde 283, their own naming). An export written before this keeps the folder it was written
# with: every export has a dated folder of its own.
PHOTOS_DIR = "foto"
VIDEOS_DIR = "video"


class DrivePhotoStore:
    def __init__(self, storage, exports):
        """`exports` names the folder beside the projects that every export lands in (madde 473)."""
        self._storage = storage
        self._exports = exports

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
        return self._storage.path(project)

    def file_path(self, project, filename):
        """One file's full path -- what a tool outside this process is handed."""
        return self._storage.path(project, filename)

    # --- export ------------------------------------------------------------------------------

    def export_dir(self):
        """Where exports land: one folder beside the projects, the same for every project, so they
        are found without opening a project first (madde 473). What the screen shows before a run;
        nothing is opened.

        Named here rather than in the domain, which knows nothing about paths. Exports written
        before madde 473 stay where they were, in the project's own export/ folder; nothing new is
        written there.
        """
        return self._storage.path(self._exports)

    def open_export(self, project, stamp):
        """Make ready where one export lands, and say where that is -- what the screen is told.

        The exports folder is opened here, once a run: it sits directly under the root, and no save
        opens a folder there (madde 472) -- a dropped mount would otherwise have it opened on the
        machine's own disk. make_dir checks the mount first, and one already there is left as it
        is. The dated folder inside is opened by its first file, like every folder in an export.

        Named date first and project after, down to the minute (design v3, madde 92): the newest
        exports stand together in Drive, and two exports of the same opening land in one folder
        where neither overwrites the other -- their file names never collide.
        """
        self._storage.make_dir(self._exports)
        return self._storage.path(self._dated(project, stamp))

    def copy_photo(self, project, photo, stamp, filename):
        """Put one picture in the export's photos folder, unless it is already there.

        Both export modes can run at once and a folder named down to the minute is one folder for
        both, so two threads asking for the same 01.png is the expected case rather than a corner
        one. Already there means nothing to do: the other mode has written the very same bytes, and
        writing them again buys nothing. Two threads that both find it missing both save it, and a
        save lands whole, so the last one leaves the same whole file.
        """
        photos = (*self._dated(project, stamp), PHOTOS_DIR)
        if self._storage.stamp(photos, filename) is not None:
            return
        self._storage.save_file(photos, filename, self._storage.path(project, photo))

    def copy_video(self, project, stamp, source, filename):
        """Bring one of a separate export's videos in from the machine's own disk, whole, into a
        folder of its own inside the dated one.

        The dated folder held one mp4 per frame beside the photos folder, and the user asked for
        them gathered (madde 283). ffmpeg cuts them on the machine now, not onto Drive's mount: what
        reaches Drive goes through the storage door, as one whole file (madde 472).
        """
        self._storage.save_file((*self._dated(project, stamp), VIDEOS_DIR), filename, source)

    def copy_export(self, project, stamp, source, filename):
        """Bring the merged file in from the machine's own disk, whole.

        ffmpeg writes the join locally: writing an encoded stream onto Drive's FUSE mount a piece at
        a time is a known Colab slowness, and the known answer is to write locally and copy at the
        end (madde 282). One save, so a half written file is never there to be seen -- a folder that
        looks finished is what madde 94 forbids.
        """
        self._storage.save_file(self._dated(project, stamp), filename, source)

    def remove_export(self, project, stamp):
        """Take a dated export folder and everything in it -- a run that failed or was cancelled
        (madde 94)."""
        self._storage.delete_dir(self._dated(project, stamp))

    def make_pieces_dir(self):
        """An empty folder on the machine's own disk, for files that are thrown away again.

        Every piece is cut here, in both modes: Drive is the slow disk the user watches (madde 235),
        and ffmpeg writing onto its mount a piece at a time is the slowness madde 282 took away from
        the join. A merged export's pieces are joined here; a separate export's are carried to
        Drive one by one.
        """
        return tempfile.mkdtemp(prefix="qe-export-")

    def piece_path(self, pieces, filename):
        return os.path.join(pieces, filename)

    def remove_pieces(self, pieces):
        """Take the machine's own folder of pieces. What it held is either on Drive or no longer
        wanted, so a file that will not go is not worth stopping for."""
        shutil.rmtree(pieces, ignore_errors=True)

    def _dated(self, project, stamp):
        return (self._exports, f"{stamp} {project}")
