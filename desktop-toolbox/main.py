"""Desktop Toolbox — Flet entry point.

Run from the desktop-toolbox/ folder:
    python main.py
"""

import flet as ft

from app.routes import MODULES, ROUTES
from app.shell import build_shell_view
from app.theme import APP_TITLE, WINDOW_HEIGHT, WINDOW_WIDTH


def run_app(page: ft.Page) -> None:
    page.title = APP_TITLE
    page.window_width = WINDOW_WIDTH
    page.window_height = WINDOW_HEIGHT
    page.padding = 0

    def on_route_change(_: ft.RouteChangeEvent) -> None:
        page.views.clear()
        page.views.append(build_shell_view(page, MODULES))
        spec = ROUTES.get(page.route)
        if spec is not None:
            page.views.append(spec.view_factory(page))
        page.update()

    def on_view_pop(_: ft.ViewPopEvent) -> None:
        if len(page.views) > 1:
            page.views.pop()
            page.go(page.views[-1].route)

    page.on_route_change = on_route_change
    page.on_view_pop = on_view_pop
    page.go(page.route or "/")


if __name__ == "__main__":
    ft.app(target=run_app)
