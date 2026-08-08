"""Ports this feature needs. Implemented in data/, faked in tests -- domain stays pure."""
from typing import Protocol


class PhotoGenerator(Protocol):
    def generate(self, prompt: str, negative: str, seed: int) -> bytes:
        """Render one photo and return its bytes."""
        ...


class PhotoStore(Protocol):
    def project_exists(self, project: str) -> bool:
        ...

    def next_number(self, project: str) -> int:
        """Highest existing number + 1, so nothing is ever overwritten."""
        ...

    def save(self, project: str, number: int, letter: str, data: bytes) -> str:
        """Persist the photo; returns the file name it was stored under."""
        ...

    def delete(self, project: str, filename: str) -> None:
        """Remove the photo from the project folder; a missing file is not an error."""
        ...

    def photo_dir(self, project: str) -> str:
        """Absolute folder the photos live in -- presentation serves files from it."""
        ...


class PlanStore(Protocol):
    def read(self, project: str) -> dict:
        """{"negative", "frames"} -- the queue as stored, every frame carrying its negative."""
        ...

    def append(self, project: str, frames: list) -> None:
        """Put frames at the end of the queue, in render order."""
        ...

    def max_number(self, project: str) -> int | None:
        """Highest number the stored plan reserved; None when there is no plan."""
        ...


class PhotoRecord(Protocol):
    def append(self, project: str, entry: dict) -> None:
        """Add one produced photo's row."""
        ...

    def list(self, project: str) -> list:
        """Every photo that still exists, newest first."""
        ...

    def mark(self, project: str, file: str, status: str, at: str,
             error: str | None = None) -> None:
        """Append a line for an event that produced no photo."""
        ...

    def statuses(self, project: str) -> dict:
        """{file name: latest status} for every frame the log has seen."""
        ...

    def max_number(self, project: str) -> int | None:
        """Highest number the record has ever seen, whatever became of the frame."""
        ...


class OrderStore(Protocol):
    def read(self, project: str) -> list:
        """The stored gallery order as file names; empty when there is none."""
        ...

    def write(self, project: str, order: list) -> None:
        """Replace the project's gallery order."""
        ...
