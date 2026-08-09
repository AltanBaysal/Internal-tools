"""File -- a document a project holds."""
from dataclasses import dataclass

CHIP_LENGTH = 3


@dataclass(frozen=True)
class File:
    name: str
    ext: str
    modified_at: str


def extension_of(name):
    """The design's chip: the first three letters of the extension."""
    return name.rpartition(".")[2][:CHIP_LENGTH].lower()
