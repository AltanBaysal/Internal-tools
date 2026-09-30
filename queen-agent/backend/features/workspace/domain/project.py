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
    # Read the same way (Madde 346): when a chat of this project was last written, empty while it
    # has none -- the chats already say it, so it is stored nowhere.
    last_chat_at: str = ""
    # Each read from a file of its own beside project.json (Madde 339): each answers a question of
    # its own and is written at a moment of its own. pinned_at is the pin file's mtime, empty when
    # there is none. An archive leaves the file (Madde 382): its moment is the project's place among
    # the pins, which Undo gives back -- but an archived project is not pinned.
    pinned_at: str = ""
    archived: bool = False

    @property
    def last_activity(self):
        # A project nobody has talked in yet was last used when it was made.
        return self.last_chat_at or self.created_at

    @property
    def pinned(self):
        return bool(self.pinned_at) and not self.archived
