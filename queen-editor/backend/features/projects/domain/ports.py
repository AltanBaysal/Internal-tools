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

    def list_archived(self) -> list[Project]:
        """Every archived project. Order is not guaranteed -- the use case sorts."""
        ...

    def archive(self, name: str) -> Project | None | bool:
        """Move the project into the archive. None when the archive already holds that name,
        False when there was nothing to move."""
        ...

    def restore(self, name: str) -> Project | None | bool:
        """Move it back out. None when a project of that name exists now, False when the archive
        does not hold it."""
        ...


class SettingsStore(Protocol):
    def project_exists(self, project: str) -> bool:
        ...

    def read(self, project: str) -> dict:
        """{"prompts": str, "negative": str, "variants": int | None} -- empty when never saved."""
        ...

    def write(self, project: str, settings: dict) -> None:
        """Replace the stored settings with this dict."""
        ...
