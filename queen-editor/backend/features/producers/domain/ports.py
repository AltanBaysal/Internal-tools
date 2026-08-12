"""What this feature needs from a producer -- and it is one question.

Deliberately not the photo feature's PhotoGenerator: this feature never imports another, and what
it holds is whatever the composition root hands it.
"""
from typing import Protocol


class Producer(Protocol):
    def installed(self) -> bool:
        """Is this producer's model group on this machine?"""
