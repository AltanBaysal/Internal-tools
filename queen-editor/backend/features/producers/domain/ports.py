"""What this feature needs from a producer -- and it is one question.

Deliberately not the photo feature's PhotoGenerator: this feature never imports another, and what
it holds is whatever the composition root hands it.
"""
from typing import Protocol


class Producer(Protocol):
    def installed(self) -> bool:
        """Is this producer's model group on this machine?

        Only asked of a producer that declares no group of its own: the notebook sets that one up,
        so the renderer is a truer witness than a list of file names we do not own.
        """


class ModelFiles(Protocol):
    def exists(self, folder: str, name: str) -> bool:
        """Is this file already on this machine?"""

    def path(self, folder: str, name: str) -> str:
        """Where it goes -- the folders are created by whoever writes it."""

    def remove(self, folder: str, name: str) -> None:
        """Throw away a file."""


class Fetcher(Protocol):
    def fetch(self, url: str, path: str, on_progress=None, cancelled=None) -> None:
        """Move one file from a URL onto disk, reporting bytes as they land."""
