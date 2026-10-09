"""Project -- the workspace that owns a set of chats and a set of files."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    id: str
    name: str
    created_at: str
    # Counted off the project's lists of chats and files when it is read, and never written as
    # numbers of their own: a second copy of a count is one that can go stale (Madde 447).
    chat_count: int = 0
    file_count: int = 0
    # Read the same way (Madde 346): the newest last activity among the project's chats, empty while
    # it has none -- the chats already say it, so it is stored nowhere.
    last_chat_at: str = ""
    # When the project was pinned, empty while it is not (Madde 339); the pinned are listed in that
    # order.
    pinned_at: str = ""
    archived: bool = False

    @property
    def last_activity(self):
        # A project nobody has talked in yet was last used when it was made.
        return self.last_chat_at or self.created_at

    @property
    def pinned(self):
        # An archived project is never pinned (Madde 384), whatever its entry says.
        return bool(self.pinned_at) and not self.archived
