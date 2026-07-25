"""Folder operations under one root -- knows no project, no JSON, no schema.

On Colab `root` sits inside the mounted Drive (see app.ipynb); locally it is any folder.
A missing root is NOT created here: that would silently write to Colab's local disk when the
Drive mount failed, so the error must reach the caller.
"""
import os


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
