"""What this feature needs from the outside world, stated by the side that uses it.

One port, two questions -- is this file here, and is anything of this kind here. The second one
exists because a group row can name a kind instead of a file (see model_groups). Nothing here
writes, fetches or deletes: installing is the notebook's job (FOUNDATION 9), and a port for it
would be a promise this app no longer keeps.
"""
from typing import Protocol


class ModelFiles(Protocol):
    def exists(self, folder: str, name: str) -> bool:
        """Is this file already on this machine?"""

    def has_any(self, folder: str, suffix: str) -> bool:
        """Is there a file of this kind here? What a group asks when which one is the user's pick."""

    def path(self, folder: str, name: str) -> str:
        """Where it sits, whether or not it is there yet."""
