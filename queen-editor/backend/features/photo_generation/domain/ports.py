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

    def list_photos(self, project: str) -> list:
        """Photo file names for the gallery, newest first."""
        ...

    def photo_dir(self, project: str) -> str:
        """Absolute folder the photos live in -- presentation serves files from it."""
        ...
