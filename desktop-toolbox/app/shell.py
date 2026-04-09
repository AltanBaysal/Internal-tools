"""Root shell view: NavigationRail on the left, empty content slot on the right.

The right-hand area is intentionally blank — when the user navigates to a
module route, that module's view is pushed on top of this shell view (Flet's
view stack model), so the shell only shows when nothing else is selected.
"""

from typing import Sequence

import flet as ft

from app.module import ModuleSpec


def build_shell_view(page: ft.Page, modules: Sequence[ModuleSpec]) -> ft.View:
    def on_rail_change(e: ft.ControlEvent) -> None:
        page.go(modules[e.control.selected_index].route)

    rail = ft.NavigationRail(
        selected_index=None,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=88,
        destinations=[
            ft.NavigationRailDestination(icon=m.icon, label=m.label) for m in modules
        ],
        on_change=on_rail_change,
    )

    return ft.View(
        route="/",
        controls=[
            ft.Row(
                expand=True,
                controls=[rail, ft.VerticalDivider(width=1), ft.Container(expand=True)],
            )
        ],
        padding=0,
    )
