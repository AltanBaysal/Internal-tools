"""Ports the workspace domain depends on. Implementations live in data/."""
from typing import Protocol

from backend.features.workspace.domain.project import Project


class ProjectStore(Protocol):
    def add(self, project: Project) -> None:
        """Persist a new project. Raises if its id is already taken."""

    def list_all(self) -> list[Project]:
        """Every project, in no particular order."""
