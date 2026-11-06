"""ReferenceStore over Storage -- the pool is a folder inside the project.

Turkish, because the user opens this folder in Drive with their own eyes, like the export's foto and
video folders (madde 283, their own naming).

Beside the photos rather than among them: the project's own files sit at its root and next_number
reads them, and a subfolder is not a file -- so the pool never touches numbering.

Read by name, which is the one order the disk can really promise. The order the files were written
in cannot be had: a timestamp is coarser than the writes, so two files of one upload sometimes share
one and sometimes do not, and the pool would read back differently on two machines. The order the
USER wants is a different question anyway, and it gets a document of its own (madde 300).
"""
from backend.features.photo_generation.domain import references

# The project folder's own reference area.
REFERENCE_DIR = "referans"
# How old a staged upload is before a sweep takes it, in seconds: far past the time an upload's
# bytes spend between their staging and the gate -- the upload's own wait for the gate.
STAGED_FOR = 3600


class DriveReferenceStore:
    def __init__(self, storage, clips=None):
        self._storage = storage
        self._clips = clips

    def stage(self, project, data):
        """Write an upload's bytes into the pool under a hidden name, which comes back; no listing
        sees it. An upload writes its files before the project's gate and names them under it
        (add_references, madde 523)."""
        return self._storage.stage_bytes(self._subdir(project), data)

    def place(self, project, staged, name):
        """Give a staged file the name it is stored under, which must be free."""
        self._storage.rename_file(self._subdir(project), staged, name)

    def discard(self, project, staged):
        """Take away a staged file that was never placed. Never raises: it is called on the way out
        of a failed upload, whose own error is the one worth telling, and a file left behind is
        hidden from every listing."""
        try:
            self._storage.delete_file(self._subdir(project), staged)
        except OSError:
            pass

    def sweep(self, project):
        """Take away what earlier uploads left staged in the pool and nobody will place (madde
        523): the folder renamed between their staging and their gate, which moved the files with
        it out of their discard's reach, or a server that died. Only files older than STAGED_FOR:
        a younger one may be another upload's, still waiting for the gate."""
        self._storage.sweep_staged(self._subdir(project), STAGED_FOR)

    def items(self, project):
        """[(name, seconds)] -- the length read off the file, never remembered from the day it
        arrived. A reference the user replaced in Drive is counted as what it now is.

        Only a clip is asked: a picture has no length, and ffprobe on one would be a question with
        no answer. Nothing is read into memory either -- the file is asked at its own path.
        """
        subdir = self._subdir(project)
        return [(name, self._seconds(subdir, name))
                for name in sorted(self._storage.list_files(subdir))]

    def read(self, project, name):
        """One reference's bytes -- what a REF2VA render is handed (madde 304)."""
        return self._storage.read_bytes(self._subdir(project), name)

    def delete(self, project, name):
        self._storage.delete_file(self._subdir(project), name)

    def dir_path(self, project):
        """Absolute folder the pool lives in -- presentation serves files straight from it."""
        return self._storage.path(self._subdir(project))

    def _seconds(self, subdir, name):
        if self._clips is None or references.kind_of(name) in (None, references.PICTURE):
            return None
        # ffprobe reads the file where it lies, so its path is the door's to hand out.
        return self._clips.seconds_at(self._storage.path(subdir, name))

    def _subdir(self, project):
        return (project, REFERENCE_DIR)
