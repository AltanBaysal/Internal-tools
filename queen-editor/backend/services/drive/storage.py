"""Folder operations under one root -- knows no project, no JSON, no schema.

On Colab `root` sits inside the mounted Drive (see app.ipynb); locally it is any folder.
A missing root is NOT created here: that would silently write to Colab's local disk when the
Drive mount failed, so the error must reach the caller.
"""
import os
import shutil


class DriveStorage:
    def __init__(self, root):
        self.root = root

    def list_dirs(self):
        """[(name, mtime)] for every direct subfolder of root. Files are skipped."""
        with os.scandir(self.root) as entries:
            return [(e.name, e.stat().st_mtime) for e in entries if e.is_dir()]

    def make_dir(self, name):
        """Create root/name. Returns its mtime, or None when the name is already taken."""
        path = os.path.join(self.root, name)
        try:
            os.mkdir(path)
        except FileExistsError:
            return None
        return os.stat(path).st_mtime

    def delete_dir(self, subdir):
        """Remove root/subdir and everything in it. Returns False when it was not there -- the
        caller decides whether a missing folder is an error, this layer only reports."""
        try:
            shutil.rmtree(os.path.join(self.root, subdir))
        except FileNotFoundError:
            return False
        return True

    def dir_exists(self, subdir):
        return os.path.isdir(os.path.join(self.root, subdir))

    def dir_path(self, subdir):
        """Absolute path of root/subdir -- for callers that hand a directory to someone else
        (Flask serves files straight from disk)."""
        return os.path.join(self.root, subdir)

    def list_files(self, subdir):
        """File names directly under root/subdir. A missing folder lists as empty: 'no files yet'
        and 'no folder yet' are the same answer to the caller, and the folder is created on write."""
        path = os.path.join(self.root, subdir)
        if not os.path.isdir(path):
            return []
        with os.scandir(path) as entries:
            return [e.name for e in entries if e.is_file()]

    def write_bytes(self, subdir, name, data):
        """Write root/subdir/name, creating the folder if needed."""
        path = os.path.join(self.root, subdir)
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, name), "wb") as f:
            f.write(data)

    def read_bytes(self, subdir, name):
        """Contents of root/subdir/name as bytes, or None when it is not there."""
        path = os.path.join(self.root, subdir, name)
        if not os.path.isfile(path):
            return None
        with open(path, "rb") as f:
            return f.read()

    def delete_file(self, subdir, name):
        """Remove root/subdir/name. A file that is already gone is not an error: deleting twice has
        to end where deleting once ends, so a retried request is safe."""
        try:
            os.remove(os.path.join(self.root, subdir, name))
        except FileNotFoundError:
            pass

    def read_text(self, subdir, name):
        """Contents of root/subdir/name, or None when it is not there.

        Missing is not an error: a project that was never saved and one whose file was removed are
        the same answer to the caller -- there is nothing to read.
        """
        path = os.path.join(self.root, subdir, name)
        if not os.path.isfile(path):
            return None
        with open(path, encoding="utf-8") as f:
            return f.read()

    def write_text(self, subdir, name, text):
        """Write root/subdir/name, creating the folder if needed. Replaces the whole file."""
        path = os.path.join(self.root, subdir)
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, name), "w", encoding="utf-8") as f:
            f.write(text)

    def append_line(self, subdir, name, line):
        """Add one line to the end of root/subdir/name, creating it if needed.

        Nothing already written is rewritten, so a session that dies mid-write can lose at most the
        line it was adding.
        """
        path = os.path.join(self.root, subdir)
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, name), "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def stamp(self, subdir, name):
        """(mtime, size) of root/subdir/name, or None when it is not there.

        What a caller holding a parsed copy checks before trusting it: asking a file's metadata is
        not the same cost as opening, reading and parsing it. Both numbers, not just the clock --
        an append inside the same second still changes the length.
        """
        try:
            info = os.stat(os.path.join(self.root, subdir, name))
        except OSError:
            return None
        return (info.st_mtime, info.st_size)

    def read_lines(self, subdir, name):
        """Non-blank lines of root/subdir/name; [] when it is not there."""
        text = self.read_text(subdir, name)
        if text is None:
            return []
        return [line for line in text.splitlines() if line.strip()]
