"""The project entity: a name and when its folder last changed."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    name: str
    modified_at: float
