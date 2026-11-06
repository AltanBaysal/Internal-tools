"""What the Drive adapter asks of Drive: six calls, each one round trip.

The adapter speaks to this, never to Drive's library: GoogleDrive (google.py) is the real one, and
the tests hand in a fake that counts each call and injects Drive's errors (step 12). A query is
given by its parts, never as Drive's `q` text: the real client builds and escapes it, the fake
needs no parser.

Metadata comes back as Drive's JSON: from outside the process, so the adapter checks every field
it reads.
"""

from dataclasses import dataclass
from typing import Any, Protocol

FOLDER = "application/vnd.google-apps.folder"
# A listing's page at most; Drive "may return fewer than this value".
PAGE = 1000


class DriveError(Exception):
    """Drive answered with an error: its HTTP status, its `reason` and its words."""

    def __init__(self, status: int, reason: str, said: str) -> None:
        super().__init__(status, reason, said)
        self.status = status
        self.reason = reason
        self.said = said

    def __str__(self) -> str:
        return f"{self.status} {self.reason}: {self.said}"


class DriveLost(Exception):
    """No answer came: the connection dropped or timed out. A write may have been made or not."""

    def __init__(self, said: str) -> None:
        super().__init__(said)
        self.said = said

    def __str__(self) -> str:
        return self.said


@dataclass(frozen=True)
class Page:
    files: list[dict[str, Any]]
    next: str | None


class DriveApi(Protocol):
    def get(self, file_id: str, fields: str) -> dict[str, Any]: ...

    def download(self, file_id: str, most: int) -> bytes:
        """The file's bytes, at most `most` + 1 of them: one more than the caller's bound tells it
        the file is past it, and nothing larger is ever held."""
        ...

    def children(
        self,
        parent: str,
        fields: str,
        *,
        folders: bool | None = None,
        name: str | None = None,
        page: str | None = None,
    ) -> Page:
        """One page of what is in `parent` and not trashed, oldest first; only folders (True),
        only files (False) or both (None); with `name`, only that name."""
        ...

    def create(
        self, metadata: dict[str, Any], content: bytes | None, fields: str
    ) -> dict[str, Any]:
        """A file with `content`, or a folder with None, in one request."""
        ...

    def update(
        self, file_id: str, metadata: dict[str, Any], content: bytes | None, fields: str
    ) -> dict[str, Any]:
        """Metadata and, unless None, content in one request: both or neither (528, 2)."""
        ...

    def generate_ids(self, count: int) -> list[str]: ...
