"""What the settings feature needs from the outside, stated as a Protocol."""
from typing import Protocol

from backend.features.settings.domain.settings import Settings


class SettingsStore(Protocol):
    def get(self) -> Settings: ...

    def replace(self, settings: Settings) -> None: ...
