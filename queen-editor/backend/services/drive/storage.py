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
