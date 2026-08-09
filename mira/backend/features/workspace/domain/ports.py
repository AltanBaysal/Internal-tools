"""Ports the workspace domain depends on. Implementations live in data/."""
from typing import Protocol

from backend.features.workspace.domain.chat import Chat
from backend.features.workspace.domain.project import Project


class ProjectStore(Protocol):
    def add(self, project: Project) -> None:
        """Persist a new project. Raises if its id is already taken."""

    def list_all(self) -> list[Project]:
        """Every project, in no particular order."""

    def get(self, project_id: str) -> Project | None:
        """The project carrying this id, or None."""

    def replace(self, project: Project) -> None:
        """Overwrite an existing project's stored fields."""


class ChatStore(Protocol):
    def add(self, project_id: str, chat: Chat) -> None:
        """Persist a chat under its project."""

    def get(self, project_id: str, chat_id: str) -> Chat | None:
        """The chat carrying this id inside that project, or None."""

    def replace(self, project_id: str, chat: Chat) -> None:
        """Overwrite an existing chat."""

    def list_for(self, project_id: str) -> list[Chat]:
        """Every chat of the project, in no particular order."""

    def list_all(self) -> list[tuple[str, Chat]]:
        """Every chat in the workspace as (project_id, chat), in no particular order."""
