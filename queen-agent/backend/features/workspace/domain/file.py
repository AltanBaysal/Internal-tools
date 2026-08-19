"""File -- a document a project holds."""
from dataclasses import dataclass

CHIP_LENGTH = 3


@dataclass(frozen=True)
class File:
    name: str
    ext: str
    modified_at: str


@dataclass(frozen=True)
class FileBody:
    """A file and what is inside it -- the reading panel's question."""

    file: File
    text: str

    @property
    def size(self):
        # Bytes as they sit on disk. The browser counts characters, so it would disagree on
        # anything that is not ASCII; it is told the number rather than asked for it.
        return len(self.text.encode("utf-8"))


def extension_of(name):
    """The design's chip: the first three letters of the extension."""
    return name.rpartition(".")[2][:CHIP_LENGTH].lower()
