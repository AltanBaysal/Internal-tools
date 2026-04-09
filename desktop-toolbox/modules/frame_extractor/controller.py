"""Holds Frame Extractor UI state and orchestrates the service.

The view talks to the controller. The controller talks to the service. The
service talks to the core. Each layer only knows about the one directly below.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import flet as ft

from .service import ExtractionResult, FrameExtractorService

if TYPE_CHECKING:
    from .view import FrameExtractorView


class FrameExtractorController:
    def __init__(self, page: ft.Page, service: FrameExtractorService) -> None:
        self.page = page
        self.service = service
        self.view: "FrameExtractorView | None" = None

        # Mutable UI state
        self.input_path: Path | None = None
        self.output_dir: Path | None = None
        self.fmt: str = "jpg"
        self.is_running: bool = False
        self.progress: float = 0.0
        self.status_text: str = "Bir giriş klasörü ve çıkış klasörü seçin."

    # Wiring -----------------------------------------------------------------
    def bind(self, view: "FrameExtractorView") -> None:
        self.view = view

    def _refresh(self) -> None:
        if self.view is not None:
            self.view.refresh()

    # Event handlers ---------------------------------------------------------
    def on_input_picked(self, e: ft.FilePickerResultEvent) -> None:
        if e.path:
            self.input_path = Path(e.path)
            self.status_text = f"Giriş: {self.input_path}"
            self._refresh()

    def on_output_picked(self, e: ft.FilePickerResultEvent) -> None:
        if e.path:
            self.output_dir = Path(e.path)
            self.status_text = f"Çıkış: {self.output_dir}"
            self._refresh()

    def on_format_change(self, e: ft.ControlEvent) -> None:
        self.fmt = e.control.value
        self._refresh()

    def on_start(self, e: ft.ControlEvent) -> None:
        if self.is_running:
            return
        if self.input_path is None or self.output_dir is None:
            self.status_text = "Önce giriş ve çıkış klasörlerini seçin."
            self._refresh()
            return
        self.is_running = True
        self.progress = 0.0
        self.status_text = "Çıkarma başlatıldı..."
        self._refresh()
        self.page.run_task(self._run_extraction)

    # Background work --------------------------------------------------------
    async def _run_extraction(self) -> None:
        assert self.input_path is not None and self.output_dir is not None
        try:
            result = await self.service.extract_all(
                self.input_path,
                self.output_dir,
                self.fmt,
                progress_cb=self._on_progress,
            )
            self._finish(result)
        except Exception as exc:
            self.status_text = f"Hata: {exc}"
            self.is_running = False
            self._refresh()

    async def _on_progress(self, done: int, total: int, current: str) -> None:
        self.progress = done / total if total else 0.0
        self.status_text = f"İşleniyor ({done}/{total}): {current}"
        self._refresh()

    def _finish(self, result: ExtractionResult) -> None:
        self.is_running = False
        self.progress = 1.0 if result.total else 0.0
        if result.total == 0:
            self.status_text = "Klasörde video bulunamadı."
        else:
            self.status_text = (
                f"Tamamlandı — {result.succeeded} başarılı, {result.failed} hatalı. "
                f"Çıkış: {result.output_dir}"
            )
        self._refresh()
