"""Store -- file access under one root. Knows no project, chat or file concept."""
import os


class PathOutsideRoot(Exception):
    """A relative path would have escaped the store's root."""


class RootUnreachable(OSError):
    """The root cannot be reached, or is no longer where it was first found (Madde 490).

    An OSError, so it reaches the screen as a 503 like any other disk failure. Not a
    FileNotFoundError, on purpose, even when the root is missing: the callers read that one as "not
    there" -- a chat not found, no projects yet -- and a dropped Drive would become an empty answer.
    """


class Store:
    def __init__(self, root):
        self._root = os.path.abspath(root)
        # The root's device as the first check found it. Not stat'ed here: building the store
        # touches no disk, and the first operation is the server's read of projects.json at start.
        self._device = None

    def _full(self, rel):
        # The root is a jail. Today every caller is our own code, so this catches a bug; from Faz 8
        # on a filename comes from the model, and then the same rule catches an attack.
        if os.path.isabs(rel) or os.path.splitdrive(rel)[0]:
            raise PathOutsideRoot(rel)
        full = os.path.abspath(os.path.join(self._root, rel))
        if full != self._root and not full.startswith(self._root + os.sep):
            raise PathOutsideRoot(rel)
        return full

    def _reached(self):
        """Stat the root, once before every operation (Madde 490). On Colab the root is a Drive
        mount, and a mount that dropped answers with an error -- or, once a folder of the same name
        stands on Colab's own disk in its place, with another device."""
        try:
            device = os.stat(self._root).st_dev
        except OSError as error:
            raise RootUnreachable(f"The root cannot be reached: {error}") from error
        if self._device is None:
            # Two first checks at once both write what the same root answered.
            self._device = device
        elif device != self._device:
            raise RootUnreachable(
                f"The root is on another device than when it was first reached: "
                f"{self._root} (device {self._device}, now {device})"
            )

    def read_text(self, rel):
        full = self._full(rel)
        self._reached()
        with open(full, encoding="utf-8") as handle:
            return handle.read()

    def write_text(self, rel, text):
        # The target is never opened for writing: opening it would empty it, and a write that died
        # after that would take the user's work with it. It is replaced instead, which the operating
        # system does atomically -- either the old file stands or the new one does.
        full = self._full(rel)
        self._reached()
        self._into_folder(full, lambda: _replace_with(full, text))

    def list_dir(self, rel):
        full = self._full(rel)
        self._reached()
        # An empty directory is a normal state -- every screen starts with "nothing here yet" -- so
        # a missing one answers with the same emptiness instead of making every caller guard it.
        # A missing *file*, in contrast, is the caller's mistake and read_text lets it raise.
        try:
            return sorted(os.listdir(full))
        except FileNotFoundError:
            return []

    def move(self, src_rel, dst_rel):
        # A rename, not a copy: what is moved keeps its mtime, so a whole project can go to the
        # trash without every file inside it looking as if it had just been written.
        source, destination = self._full(src_rel), self._full(dst_rel)
        self._reached()
        self._into_folder(destination, lambda: os.replace(source, destination))

    def _into_folder(self, full, act):
        """Do `act`, making the folder `full` goes into only if it turns out to be missing (Madde 447).

        Tried first rather than made first: on Drive every call is a round trip, and the folder
        almost always is there. A missing source fails the second try just as it failed the first,
        so a move of nothing still raises. The root is never made (Madde 490): one missing here went
        after the check, and making it would put the write on Colab's own disk.
        """
        try:
            act()
        except FileNotFoundError:
            folder = os.path.dirname(full)
            if folder == self._root:
                raise
            # One level at a time from the root down, rather than os.makedirs, which would make the
            # root too: with the root gone the first mkdir fails instead.
            made = self._root
            for part in os.path.relpath(folder, self._root).split(os.sep):
                made = os.path.join(made, part)
                try:
                    os.mkdir(made)
                except FileExistsError:
                    pass  # there already, or made by another request a moment ago
            act()


def _replace_with(full, text):
    # Beside the target rather than in the system's temp directory: os.replace cannot cross a
    # filesystem, and the root is a Drive mount when the app runs on Colab while /tmp is that
    # machine's own disk. Named rather than random, so a directory left behind by a crash can still
    # be read by a person.
    temp = f"{full}.writing"
    try:
        with open(temp, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(temp, full)
    except BaseException:
        # Half a file is rubbish rather than evidence, and a person opening the folder on Drive would
        # take it for one of their own. KeyboardInterrupt leaves one too, so it is caught as well.
        try:
            os.remove(temp)
        except OSError:
            # The write's own error is the one that explains what happened; a failure to tidy up on
            # top of it would report the wrong cause.
            pass
        raise
