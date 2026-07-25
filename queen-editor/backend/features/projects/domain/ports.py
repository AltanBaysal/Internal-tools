"""Ports this feature needs. Implemented in data/, faked in tests -- domain stays pure."""
from typing import Protocol

from backend.features.projects.domain.project import Project


class ProjectStore(Protocol):
    def list(self) -> list[Project]:
        """Every project. Order is not guaranteed -- the use case sorts."""
        ...

    def create(self, name: str) -> Project | None:
        """Create the project; None means the name is already taken."""
        ...
