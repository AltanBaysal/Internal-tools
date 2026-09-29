"""Project -- the workspace that owns a set of chats and a set of files."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    id: str
    name: str
    created_at: str
    # Derived from the directories at read time and never written back: the counts are the
    # directory's own answer, so storing them would be a second copy that can go stale.
    chat_count: int = 0
    file_count: int = 0
    # Read the same way, each from a file of its own beside project.json (Madde 339): each answers a
    # question of its own and is written at a moment of its own.
    pinned: bool = False
    archived: bool = False
