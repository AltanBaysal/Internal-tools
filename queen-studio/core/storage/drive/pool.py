"""Reserved ids: every new file is made at one, so a create tried again makes no second file
(step 4, Değerlendirme 2). `generateIds` gives a thousand a call, kept here and handed out; most
takes are no call at all.

Reserved ids may expire (528, 6: the 1, 3 and 7 day looks are due): Drive's 400 on one drops the
whole pool, since the others were reserved with it, and the create is tried once more at a new id.
"""

import threading
from collections.abc import Callable

from core.clock.clock import Clock
from core.storage.drive.api import DriveApi
from core.storage.drive.head import DRIVE_ID
from core.storage.drive.retry import Missing, Unusable, read
from core.storage.port import MOST_RESERVED, Rejected


class Pool:
    def __init__(self, api: DriveApi, clock: Clock) -> None:
        self._api = api
        self._clock = clock
        self._lock = threading.Lock()
        self._ids: list[str] = []

    def take(self, count: int) -> list[str]:
        """Mostly once round: another thread may take the new ones first."""
        while True:
            with self._lock:
                if len(self._ids) >= count:
                    taken, self._ids = self._ids[:count], self._ids[count:]
                    return taken
            try:
                ids = read(self._clock, lambda: self._api.generate_ids(MOST_RESERVED))
            except Missing as missing:
                raise Rejected(f"Drive gave no ids: {missing}") from None
            # They go into head files, whose reader takes only this shape; and a short answer
            # would never fill the pool.
            if len(ids) != MOST_RESERVED or not all(DRIVE_ID.fullmatch(each) for each in ids):
                raise Rejected("Drive gave ids this core cannot use.")
            with self._lock:
                self._ids += ids

    def drop(self) -> None:
        """Drive refused one of these ids: the rest were reserved with it."""
        with self._lock:
            self._ids.clear()

    def make(self, create: Callable[[str], object], first: str | None = None) -> str:
        """Runs `create` at a reserved id — `first`, else one from the pool — and gives the id it
        was made at. On Unusable the pool is dropped and one new id tried."""
        made = first if first is not None else self.take(1)[0]
        try:
            create(made)
            return made
        except Unusable:
            self.drop()
        made = self.take(1)[0]
        try:
            create(made)
        except Unusable as unusable:
            raise Rejected(unusable.said, unusable.code) from None
        return made
