"""Ports this feature needs. Implemented in data/, faked in tests -- domain stays pure."""
from typing import Protocol


class PhotoGenerator(Protocol):
    def generate(self, prompt: str, negative: str, seed: int, model: str = "") -> bytes:
        """Render one photo and return its bytes. An empty model means the graph's own default."""
        ...

    def models(self) -> list:
        """Which models can render right now -- asked of the renderer, never kept here."""
        ...


class PromptWriter(Protocol):
    def write(self, prompts: dict) -> str:
        """The prompt a job of this type should be produced with.

        `prompts` is what the frame already says: {"photo": …} today, plus the video's own when
        audio joins. Raising is a failure like any other -- the loop's three attempts and its
        frame-fault rule apply to it unchanged.
        """
        ...


class PhotoStore(Protocol):
    def project_exists(self, project: str) -> bool:
        ...

    def next_number(self, project: str) -> int:
        """Highest existing number + 1, so nothing is ever overwritten."""
        ...

    def save(self, project: str, filename: str, data: bytes) -> str:
        """Persist the photo under the name the domain chose; returns that name."""
        ...

    def read(self, project: str, filename: str) -> bytes | None:
        """The file's bytes; None when it is not there."""
        ...

    def delete(self, project: str, filename: str) -> None:
        """Remove the photo from the project folder; a missing file is not an error."""
        ...

    def photo_dir(self, project: str) -> str:
        """Absolute folder the photos live in -- presentation serves files from it."""
        ...


class PlanStore(Protocol):
    def read(self, project: str) -> dict:
        """{"negative", "frames"} -- the queue as stored, every frame carrying its identity and its
        negative."""
        ...

    def append(self, project: str, frames: list) -> None:
        """Put frames at the end of the queue, in render order."""
        ...

    def max_number(self, project: str) -> int | None:
        """Highest number the stored plan reserved; None when there is no plan."""
        ...


class PhotoRecord(Protocol):
    def append(self, project: str, entry: dict) -> None:
        """Add one produced layer's row."""
        ...

    def list(self, project: str) -> list:
        """Every photo that still exists, newest first."""
        ...

    def mark(self, project: str, frame: str, layer: str, file: str, status: str, at: str,
             error: str | None = None) -> None:
        """Append a line for an event that produced no layer."""
        ...

    def slots(self, project: str) -> dict:
        """{frame: {slot: {"status", "file"}}} -- the latest line per (frame, slot)."""
        ...

    def prompts(self, project: str) -> dict:
        """{frame: {layer: prompt}} -- what each layer was made from; the latest line wins."""
        ...

    def max_number(self, project: str) -> int | None:
        """Highest number the record has ever seen, whatever became of the frame."""
        ...


class OrderStore(Protocol):
    def read(self, project: str) -> list:
        """The stored gallery order as frame identities; empty when there is none."""
        ...

    def write(self, project: str, order: list) -> None:
        """Replace the project's gallery order."""
        ...
