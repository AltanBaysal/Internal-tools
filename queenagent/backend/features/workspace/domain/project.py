"""Project -- the workspace that owns a set of chats and a set of files."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    id: str
    name: str
    hue: int
    created_at: str
    # Derived from the directories at read time and never written back: the counts are the
    # directory's own answer, so storing them would be a second copy that can go stale.
    chat_count: int = 0
    file_count: int = 0
