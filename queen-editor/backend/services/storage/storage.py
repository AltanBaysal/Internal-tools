"""The one door to the persistent store: every read and write of a Drive root goes through here.

It knows folders and files under one root and nothing else -- no project, no JSON, no schema. A
second root is a second door: the projects' and the exports' are two (main.py). On Colab each root
sits inside the mounted Drive, which queeneditor.ipynb opens before the server starts; locally it
is any folder.

Its rules come from how Colab's Drive mount fails. A mount that drops mid-session (colabtools #3441)
answers Errno 107, or leaves the path empty, or comes back as another device -- and a write that
opened its own folders would then land on the machine's own disk while the screen said it was saved.
So:

- Before every operation the root is stat'ed once and its device compared with the one recorded on
  first use. Any of the three failures stops the operation with the OS's own words.
- Every write -- a save or an appended line -- first asks the mount how much room is left, and
  stops with the door's own sentence, carrying the two numbers the mount reported, when the bytes
  will not fit. Google's own flush_and_unmount shows a write can still be waiting to reach Google
  after it returned here, and on a full Drive files were lost with nothing said (madde 497). That
  DriveFS reports the account's quota as the mount's free space is unverified until the user's
  Colab trial. A push that fails after the write returned is not seen here.
- A save is whole or absent: written to a temporary file in the target's own folder, flushed to the
  mount, then moved over the target in one step. A save returning is what "saved" means.
- No write opens a root or a folder directly under it; only make_dir does. Folders below those are
  opened by their first file.
- Missing means FileNotFoundError and nothing else. Every other OSError is raised, never read as
  "nothing there".

And no name leaves the root: every folder part and file name is checked before it is joined, so a
name taken from a URL cannot reach above the root or across it.
"""
import errno
import os
import shutil
import stat
import tempfile
import time

# What a save writes before it moves into place. Listings skip it: a session that dies mid-save leaves
# one behind, and it is nobody's file.
TEMP_PREFIX = ".qe-tmp-"

# ":" with the separators: on Windows a part like "C:" makes os.path.join start again at that drive.
_FORBIDDEN = ("/", "\\", "\0", ":")


class StorageError(OSError):
    """The door's own refusal: the mount failed its check, or a name would leave the root.

    An OSError, so the one handler that puts a failure on screen (web/app.py) puts this on screen
    too.
    """


class NameRefused(StorageError):
    """A name that would leave its folder. The asker's error rather than the store's, so the screen
    answers it on a handler of its own (400)."""


def _checked(name):
    """One folder or file name, refused when joining it could leave its folder."""
    if (not isinstance(name, str) or name in ("", ".", "..")
            or any(mark in name for mark in _FORBIDDEN)):
        raise NameRefused(f"Geçersiz ad: {name!r}")
    return name


def _parts(folder):
    """A folder as its parts: a string is one folder under the root (a project), a tuple is a path of
    them, and () is the root itself.

    Given apart rather than as one joined path so that each part is checked on its own: a joined path
    could not tell a separator from a name that holds one.
    """
    parts = (folder,) if isinstance(folder, str) else tuple(folder)
    for part in parts:
        _checked(part)
    return parts


def _is_dir(path):
    try:
        info = os.stat(path)
    except FileNotFoundError:
        return False
    return stat.S_ISDIR(info.st_mode)


def _discard(temporary):
    """Remove a save's temporary file after the save failed.

    Its own failure is not raised: the save's error is the one the caller needs, and a file left
    behind carries the prefix every listing skips.
    """
    try:
        os.remove(temporary)
    except OSError:
        pass


class Storage:
    def __init__(self, root):
        # Nothing is asked of the disk here: the composition root builds this at import, before the
        # mount is anybody's question.
        self._root = root
        self._device = None

    # --- the gate ---------------------------------------------------------------------------

    def _check(self):
        """Stat the root once, and stop unless it is the device it was on first use."""
        try:
            device = os.stat(self._root).st_dev
        except OSError as exc:
            # The OS's words name the path, so the one sentence serves whichever root this is.
            raise StorageError(f"Kök klasöre ulaşılamıyor: {exc}") from exc
        if self._device is None:
            self._device = device
        elif device != self._device:
            raise StorageError(
                f"Kök klasör başka bir aygıtta: {self._root} ({self._device} → {device})")

    def _folder(self, folder):
        """The folder's absolute path: its names checked first, then the mount."""
        parts = _parts(folder)
        self._check()
        return os.path.join(self._root, *parts)

    def _file(self, folder, name):
        _checked(name)
        return os.path.join(self._folder(folder), name)

    # --- folders ----------------------------------------------------------------------------

    def list_dirs(self):
        """[(name, mtime)] for every folder directly under the root. Files are skipped."""
        with os.scandir(self._folder(())) as entries:
            return [(e.name, e.stat().st_mtime) for e in entries if e.is_dir()]

    def make_dir(self, name):
        """Create a folder directly under the root -- the one way a project folder, or an export's
        own, comes to be. Returns its mtime, or None when the name is already taken."""
        path = self._folder(_checked(name))
        try:
            os.mkdir(path)
        except FileExistsError:
            return None
        return os.stat(path).st_mtime

    def delete_dir(self, folder):
        """Remove the folder and everything in it. Returns False when it was not there -- the
        caller decides whether a missing folder is an error, this layer only reports."""
        if not _parts(folder):
            raise NameRefused("Kök klasör silinemez.")
        try:
            shutil.rmtree(self._folder(folder))
        except FileNotFoundError:
            return False
        return True

    def remove_empty_dir(self, folder):
        """Remove the folder only if nothing is in it. False when it holds something or is not
        there: what is left in a folder is somebody's, and this never takes it along."""
        if not _parts(folder):
            raise NameRefused("Kök klasör silinemez.")
        try:
            os.rmdir(self._folder(folder))
        except FileNotFoundError:
            return False
        except OSError as exc:
            # POSIX allows either number for a folder that is not empty.
            if exc.errno in (errno.ENOTEMPTY, errno.EEXIST):
                return False
            raise
        return True

    def rename_dir(self, old, new):
        """Move a folder directly under the root to another name there, with everything in it.

        Renamed and never copied: a project can hold thousands of files and a copy over Drive can be
        interrupted, which leaves two half folders and nobody able to say which is real. A rename is
        one operation that either happened or did not.

        Two ways to fail and the caller has a different sentence for each, so they come back apart:
        False when there was nothing to move, None when the new name is already something. The mtime
        comes back on success, the same answer make_dir gives.
        """
        _checked(old)
        _checked(new)
        root = self._folder(())
        source, target = os.path.join(root, old), os.path.join(root, new)
        if not _is_dir(source):
            return False
        try:
            os.stat(target)
            return None
        except FileNotFoundError:
            pass
        os.rename(source, target)
        return os.stat(target).st_mtime

    def dir_exists(self, folder):
        return _is_dir(self._folder(folder))

    def path(self, folder, name=None):
        """The absolute path of a folder, or of a file in it, for a reader outside this process --
        ffmpeg, ffprobe, Flask sending a file -- and for the screen to say where an export lands.

        The name and the mount are checked like any other operation: the path is only handed out
        while the root is the one it was.
        """
        return self._folder(folder) if name is None else self._file(folder, name)

    # --- files ------------------------------------------------------------------------------

    def list_files(self, folder):
        """File names directly in the folder. A folder that is not there lists as empty: 'no files
        yet' and 'no folder yet' are the same answer to the caller."""
        path = self._folder(folder)
        try:
            with os.scandir(path) as entries:
                return [e.name for e in entries
                        if e.is_file() and not e.name.startswith(TEMP_PREFIX)]
        except FileNotFoundError:
            return []

    def read_bytes(self, folder, name):
        """The file's bytes, or None when it is not there."""
        path = self._file(folder, name)
        try:
            with open(path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def read_text(self, folder, name):
        """The file's text, or None when it is not there.

        Missing is not an error: a project that was never saved and one whose file was removed are
        the same answer to the caller -- there is nothing to read.
        """
        path = self._file(folder, name)
        try:
            with open(path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def read_lines(self, folder, name):
        """Non-blank lines of the file; [] when it is not there."""
        text = self.read_text(folder, name)
        if text is None:
            return []
        return [line for line in text.splitlines() if line.strip()]

    def stamp(self, folder, name):
        """(mtime, size) of the file, or None when it is not there.

        What a caller holding a parsed copy checks before trusting it: asking a file's metadata is
        not the same cost as opening, reading and parsing it. Both numbers, not just the clock --
        an append inside the same second still changes the length.
        """
        try:
            info = os.stat(self._file(folder, name))
        except FileNotFoundError:
            return None
        return (info.st_mtime, info.st_size)

    def write_bytes(self, folder, name, data):
        self._save(folder, name, len(data), lambda opened: opened.write(data))

    def write_text(self, folder, name, text):
        self.write_bytes(folder, name, text.encode("utf-8"))

    def save_file(self, folder, name, source):
        """Bring in the file at `source` as one save: a piece ffmpeg cut on the machine's own disk,
        or a photo an export copies over from the projects' root, which is on the mount too.

        The source is opened once and its size read from the open handle, so a source on the mount
        costs one trip there rather than a stat and then an open.
        """
        with open(source, "rb") as handle:
            self._save(folder, name, os.fstat(handle.fileno()).st_size,
                       lambda opened: shutil.copyfileobj(handle, opened))

    def append_line(self, folder, name, line):
        """Add one line to the end of the file, creating the file but never its folder.

        Nothing already written is rewritten, so a session that dies mid-write can lose at most the
        line it was adding -- which is why the two records that grow line by line are appended to
        rather than saved whole. Asks for room first and is flushed to the mount before it returns,
        like a save.
        """
        path = self._file(folder, name)
        text = line + "\n"
        self._room(len(text.encode("utf-8")), path)
        with open(path, "a", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())

    def delete_file(self, folder, name):
        """Remove the file. One that is already gone is not an error: deleting twice has to end
        where deleting once ends, so a retried request is safe."""
        try:
            os.remove(self._file(folder, name))
        except FileNotFoundError:
            pass

    def stage_bytes(self, folder, data):
        """Write `data` under a hidden name in the folder and return that name -- for a caller that
        writes the bytes first and learns the name they will carry later (madde 523: a reference
        upload, whose free name is chosen under the project's gate, while the bytes go to Drive
        before it). Listings skip the name; rename_file moves it into place, delete_file takes it
        away. Written, flushed and opened in the folder as a save is.
        """
        parts = _parts(folder)
        directory = self._folder(parts)
        return os.path.basename(self._staged(parts, directory, len(data),
                                             lambda opened: opened.write(data)))

    def rename_file(self, folder, old, new):
        """Give a file in the folder another name there, in one step. Over whatever is under the new
        name, as a save is: the caller chooses a name that is free."""
        os.replace(self._file(folder, old), self._file(folder, new))

    def sweep_staged(self, folder, age):
        """Remove the hidden files in the folder last written more than `age` seconds ago: staged
        bytes nobody will place -- their folder was renamed from under them, or the server died --
        and half saves. Hidden from every listing, but each holds its bytes of Drive. A younger one
        may be a write still on its way, so it stays. A folder that is not there has none; a file
        that cannot be removed stays, hidden, as _discard leaves it.

        One listing of the folder, and a stat of each hidden file only.
        """
        path = self._folder(folder)
        oldest = time.time() - age
        try:
            with os.scandir(path) as entries:
                left = [entry.path for entry in entries
                        if entry.name.startswith(TEMP_PREFIX) and entry.is_file()
                        and entry.stat().st_mtime < oldest]
        except FileNotFoundError:
            return
        for leftover in left:
            _discard(leftover)

    def _save(self, folder, name, size, write):
        """Write `size` bytes through a temporary file beside the target, flush it to the mount, then
        move it over the target in one step: a reader sees the old file or the new one, never half of
        it. The room for them is asked first, so a save that cannot fit leaves nothing behind.

        os.replace rather than os.rename: on Windows rename refuses a target that is already there.
        """
        parts = _parts(folder)
        target = self._file(parts, name)
        temporary = self._staged(parts, target, size, write)
        try:
            os.replace(temporary, target)
        except BaseException:
            _discard(temporary)
            raise

    def _staged(self, parts, said, size, write):
        """The path of a hidden file in the folder of `parts`, holding `size` bytes `write` put in it
        and flushed to the mount. `said` is the path the errors name: the save's target, or the
        folder itself. The room for them is asked first, so a write that cannot fit leaves nothing
        behind, and neither does one that fails.

        The temporary file opens in its folder or not at all. A folder is opened only when that is
        why it failed, and only below the folder directly under the root: the root and that folder
        are never opened by a write, so one that is not there stays an error.
        """
        self._room(size, said)
        directory = os.path.join(self._root, *parts)
        try:
            handle, temporary = tempfile.mkstemp(prefix=TEMP_PREFIX, dir=directory)
        except FileNotFoundError as missing:
            if len(parts) < 2:
                # mkstemp names the temporary file it could not open; the screen prints the error
                # as it is, so it names the file the write was for.
                raise FileNotFoundError(missing.errno, missing.strerror, said) from missing
            self._open_inside(parts)
            handle, temporary = tempfile.mkstemp(prefix=TEMP_PREFIX, dir=directory)
        try:
            with os.fdopen(handle, "wb") as opened:
                write(opened)
                opened.flush()
                os.fsync(opened.fileno())
        except BaseException:
            _discard(temporary)
            raise
        return temporary

    def _room(self, size, target):
        """Stop unless the mount has `size` bytes free, before anything of `target` is written. The
        root is asked: every folder under it is on the same device, which the mount check has just
        confirmed. A failure to answer is raised as it is, never read as room."""
        free = shutil.disk_usage(self._root).free
        if free < size:
            raise StorageError(f"Drive'da yer yok: {target} için {size} bayt gerekiyor, "
                               f"Drive'ın bildirdiği boş yer {free} bayt")

    def _open_inside(self, parts):
        """Open the folders below the folder directly under the root, one level at a time. That
        folder is the first part and is never made here: when it is not there, the first mkdir says
        so."""
        path = os.path.join(self._root, parts[0])
        for part in parts[1:]:
            path = os.path.join(path, part)
            try:
                os.mkdir(path)
            except FileExistsError:
                pass
