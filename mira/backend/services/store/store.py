"""Store -- file access under one root. Knows no project, chat or file concept."""
import os


class PathOutsideRoot(Exception):
    """A relative path would have escaped the store's root."""


class Store:
    def __init__(self, root):
        self._root = os.path.abspath(root)

    def _full(self, rel):
        # The root is a jail. Today every caller is our own code, so this catches a bug; from Faz 8
        # on a filename comes from the model, and then the same rule catches an attack.
        if os.path.isabs(rel) or os.path.splitdrive(rel)[0]:
            raise PathOutsideRoot(rel)
        full = os.path.abspath(os.path.join(self._root, rel))
        if full != self._root and not full.startswith(self._root + os.sep):
            raise PathOutsideRoot(rel)
        return full

    def read_text(self, rel):
        with open(self._full(rel), encoding="utf-8") as handle:
            return handle.read()

    def write_text(self, rel, text):
        full = self._full(rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def list_dir(self, rel):
        # An empty directory is a normal state -- every screen starts with "nothing here yet" -- so
        # a missing one answers with the same emptiness instead of making every caller guard it.
        # A missing *file*, in contrast, is the caller's mistake and read_text lets it raise.
        try:
            return sorted(os.listdir(self._full(rel)))
        except FileNotFoundError:
            return []

    def exists(self, rel):
        return os.path.exists(self._full(rel))

    def mtime(self, rel):
        return os.path.getmtime(self._full(rel))

    def move(self, src_rel, dst_rel):
        destination = self._full(dst_rel)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        os.replace(self._full(src_rel), destination)
