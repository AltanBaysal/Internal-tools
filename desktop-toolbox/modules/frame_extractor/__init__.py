"""Video Frame Extractor module — exposes its ModuleSpec for the app shell."""

import flet as ft

from app.module import ModuleSpec
from .controller import FrameExtractorController
from .service import FrameExtractorService
from .view import FrameExtractorView


def _factory(page: ft.Page) -> ft.View:
    service = FrameExtractorService()
    controller = FrameExtractorController(page, service)
    view = FrameExtractorView(controller)
    controller.bind(view)
    return view


module_spec = ModuleSpec(
    route="/frame-extractor",
    label="Frame Extractor",
    icon=ft.Icons.MOVIE,
    view_factory=_factory,
)
