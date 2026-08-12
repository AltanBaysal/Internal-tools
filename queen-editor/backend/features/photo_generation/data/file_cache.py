"""Parse a file once, and only again once it has changed.

The gallery is asked for on every poll, and the record answers three of its questions -- which
layer is where, which photos still stand, what each layer was made from. Each one opened the same
file and parsed it again, which is why one gallery request cost five Drive reads for four files.

Kept by the file's own stamp (its change time and its length). Our own appends grow the file, and
an edit made outside the app moves one or the other, so "truth lives on disk" (FOUNDATION 2) still
holds -- we only stop asking disk the same question five times a second. Asking for a stamp is a
metadata call; opening, reading and parsing is not.
"""


class FileCache:
    def __init__(self, storage):
        self._storage = storage
        self._held = {}         # (project, name) -> (stamp, parsed value)

    def parsed(self, project, name, parse):
        """`parse(lines) -> value`, called only when the file is not the one already parsed.

        The value is handed back as it is, so callers must read it rather than change it: it is the
        same object the next caller gets.
        """
        stamp = self._storage.stamp(project, name)
        held = self._held.get((project, name))
        if held is not None and held[0] == stamp:
            return held[1]
        value = parse(self._storage.read_lines(project, name))
        self._held[(project, name)] = (stamp, value)
        return value
