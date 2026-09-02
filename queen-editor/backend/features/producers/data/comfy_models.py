"""ModelFiles over the ComfyUI folder -- the only place that knows that layout."""
import os


class ComfyModelFiles:
    def __init__(self, root):
        self._root = root

    def path(self, folder, name):
        return os.path.join(self._root, "models", folder, name)

    def exists(self, folder, name):
        return os.path.exists(self.path(folder, name))

    def has_any(self, folder, suffix):
        """Is there a file of this kind in the folder?

        scandir rather than listdir: it stops at the first match, and is_file() comes off the entry
        instead of a second stat call.

        A missing folder answers False rather than raising. The notebook creates these on startup,
        but the app also comes up on a machine where nothing was ever installed, and for the panel
        "no folder" and "empty folder" are the same answer -- not installed.
        """
        directory = os.path.join(self._root, "models", folder)
        try:
            return any(entry.name.endswith(suffix) and entry.is_file()
                       for entry in os.scandir(directory))
        except FileNotFoundError:
            return False

    def remove(self, folder, name):
        try:
            os.remove(self.path(folder, name))
        except FileNotFoundError:
            pass
