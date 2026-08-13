"""What this feature needs from the outside world, stated by the side that uses it.

One port, one question: is this file on the machine? Nothing here writes, fetches or deletes --
installing is the notebook's job (FOUNDATION 9), and a port for it would be a promise this app no
longer keeps.
"""
from typing import Protocol


class ModelFiles(Protocol):
    def exists(self, folder: str, name: str) -> bool:
        """Is this file already on this machine?"""

    def path(self, folder: str, name: str) -> str:
        """Where it sits, whether or not it is there yet."""
