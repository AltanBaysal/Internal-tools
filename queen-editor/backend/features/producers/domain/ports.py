"""What this feature needs from the outside world, stated by the side that uses it.

Two kinds of thing a producer can need before it works: model files on disk, and a library inside
this process. They are separate ports because "is it here" is a different question for each -- one
is answered by looking at a folder, the other by asking the import system.

Deliberately no port for the renderers themselves: this feature never imports another, and what a
producer can do is the other feature's business.
"""
from typing import Protocol


class ModelFiles(Protocol):
    def exists(self, folder: str, name: str) -> bool:
        """Is this file already on this machine?"""

    def path(self, folder: str, name: str) -> str:
        """Where it goes -- the folders are created by whoever writes it."""

    def remove(self, folder: str, name: str) -> None:
        """Throw away a file."""


class Fetcher(Protocol):
    def fetch(self, url: str, path: str, headers=None, on_progress=None, cancelled=None) -> None:
        """Move one file from a URL onto disk, reporting bytes as they land. `headers` is what a
        gated source wants; this feature holds no key of its own."""


class Libraries(Protocol):
    def present(self, module: str) -> bool:
        """Can this process import `module`? Asked on every panel poll, so it stays cheap and never
        runs the module itself."""

    def install(self, repo: str, folder: str, module: str) -> None:
        """Fetch the library and install it. Raises with the tool's own output on failure -- that
        sentence is what the panel shows."""
