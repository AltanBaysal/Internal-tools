"""Hit -- one row of a search result."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Hit:
    kind: str  # project | chat | file -- the word on the row's chip
    label: str
    project_id: str
    project_name: str
    chat_id: str = ""
    file_name: str = ""
