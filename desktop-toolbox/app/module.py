"""ModuleSpec — the contract every toolbox module must satisfy."""

from dataclasses import dataclass
from typing import Callable

import flet as ft


@dataclass(frozen=True)
class ModuleSpec:
    """A self-contained tool module the shell can mount.

    Adding a new module = create `modules/<name>/` exposing a `module_spec`,
    then append it to `MODULES` in `app/routes.py`. Nothing else changes.
    """

    route: str
    label: str
    icon: str
    view_factory: Callable[[ft.Page], ft.View]
