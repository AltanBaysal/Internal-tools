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

    def photo_dir(self, project: str) -> str:
        """Absolute folder the photos live in -- presentation serves files from it."""
        ...


class PlanStore(Protocol):
    def write(self, project: str, negative: str, frames: list) -> None:
        """Replace the project's plan with this run's frames, in render order."""
        ...

    def max_number(self, project: str) -> int | None:
        """Highest number the stored plan reserved; None when there is no plan."""
        ...


class PhotoRecord(Protocol):
    def append(self, project: str, entry: dict) -> None:
        """Add one produced photo's row."""
        ...

    def list(self, project: str) -> list:
        """Every recorded photo, newest first."""
        ...


class OrderStore(Protocol):
    def read(self, project: str) -> list:
        """The stored gallery order as file names; empty when there is none."""
        ...

    def write(self, project: str, order: list) -> None:
        """Replace the project's gallery order."""
        ...
