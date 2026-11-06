"""MuteStore over Storage -- the only place that knows the turned-off sounds' file name and shape.

A file of its own (CODE-STANDARD, Separation of concerns): it answers which frames' sound is off,
written when the frame page's icon is pressed (madde 510). Frames by identity: a copy can share its
source's sound file, and what is turned off is one video's sound.

Strict where the project's switches are lenient: a list that cannot be read is not an empty one.
The export reads it, and would put every turned-off sound back; a press writes it back, and would
turn every other frame's sound on again. So both stop with the reason, and the file stays as it is.
"""
import json
import threading

FILE = "muted.json"


def _parse(raw):
    """The identities in the file; [] when there is none. ValueError when it is not this store's."""
    if raw is None:
        return []
    data = json.loads(raw)
    frames = data.get("frames") if isinstance(data, dict) else None
    if not isinstance(frames, list) or not all(isinstance(fid, str) for fid in frames):
        raise ValueError('"frames" kimlik listesi değil')
    return frames


class DriveMuteStore:
    def __init__(self, storage):
        self._storage = storage
        # A press reads the list, changes it and writes it back: two at once would each write the
        # list they read, and the first one's frame would be lost. One process serves every press.
        self._lock = threading.Lock()

    def project_exists(self, project):
        return self._storage.dir_exists(project)

    def read(self, project):
        try:
            return _parse(self._storage.read_text(project, FILE))
        except ValueError as exc:
            raise OSError(f"{project}/{FILE} okunamıyor: {exc}") from exc

    def put(self, project, frame, on):
        """The new list, written; nothing written when it would come out the same."""
        with self._lock:
            held = self.read(project)
            if (frame in held) == on:
                return held
            frames = held + [frame] if on else [fid for fid in held if fid != frame]
            self._storage.write_text(project, FILE, json.dumps({"frames": frames}))
            return frames
