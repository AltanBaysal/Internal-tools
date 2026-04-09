"""Root shell view: NavigationRail on the left, content slot on the right."""

from typing import Sequence

import flet as ft

from app.module import ModuleSpec
from app.theme import APP_TITLE


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

    welcome = ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(APP_TITLE, size=32, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Soldaki menüden bir araç seçin.",
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
            ],
        ),
    )

    return ft.View(
        route="/",
        controls=[
            ft.Row(
                expand=True,
                controls=[rail, ft.VerticalDivider(width=1), welcome],
            )
        ],
        padding=0,
    )
