"""ModelFiles over the ComfyUI folder -- the only place that knows that layout."""
import os


class ComfyModelFiles:
    def __init__(self, root):
        self._root = root

    def path(self, folder, name):
        return os.path.join(self._root, "models", folder, name)

    def exists(self, folder, name):
        return os.path.exists(self.path(folder, name))

    def remove(self, folder, name):
        try:
            os.remove(self.path(folder, name))
        except FileNotFoundError:
            pass
