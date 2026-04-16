"""Holds Frame Extractor UI state and orchestrates the service.

Single-button stage flow:
  IDLE → EXTRACTING → EXTRACTED → SAVING → SAVED
  (changing input or format resets to IDLE)

The save destination is fixed to ~/Downloads/extractor-photos/<input-name>/.
The 'extractor-photos' namespace avoids colliding with any user-managed
~/Downloads/photos folder.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

import flet as ft

from .service import ExtractedFrame, ExtractionResult, FrameExtractorService, SaveResult

if TYPE_CHECKING:
    from .view import FrameExtractorView


class Stage(str, Enum):
    IDLE = "idle"
    EXTRACTING = "extracting"
    EXTRACTED = "extracted"
    SAVING = "saving"
    SAVED = "saved"


class FrameExtractorController:
    def __init__(self, page: ft.Page, service: FrameExtractorService) -> None:
        self.page = page
        self.service = service
        self.view: "FrameExtractorView | None" = None

        # Mutable UI state
        self.input_path: Path | None = None
        self.input_path_text: str = ""
        self.fmt: str = "jpg"
        self.is_running: bool = False
        self.is_saving: bool = False
        self.progress: float = 0.0
        self.frames: list[ExtractedFrame] | None = None
        self.status_text: str = "Bir giriş klasörü seçin."
        self._just_saved: bool = False

        # Set in on_save when target is known
        self._save_target: Path | None = None

    # Wiring -----------------------------------------------------------------
    def bind(self, view: "FrameExtractorView") -> None:
        self.view = view

    def _refresh(self) -> None:
        if self.view is not None:
            self.view.refresh()

    @property
    def stage(self) -> Stage:
        if self.is_running:
            return Stage.EXTRACTING
        if self.is_saving:
            return Stage.SAVING
        if self._just_saved:
            return Stage.SAVED
        if self.frames:
            return Stage.EXTRACTED
        return Stage.IDLE

    # Event handlers ---------------------------------------------------------
    def on_input_picked(self, e: ft.FilePickerResultEvent) -> None:
        if e.path:
            self.input_path = Path(e.path)
            self.input_path_text = str(self.input_path)
            self.frames = None
            self.progress = 0.0
            self._just_saved = False
            self.status_text = f"Giriş: {self.input_path}"
            self._refresh()

    def on_input_text_change(self, e: ft.ControlEvent) -> None:
        new_text = e.control.value or ""
        self.input_path_text = new_text
        # If the user is editing the field away from the picker's value,
        # invalidate the cached picker path so on_start re-resolves from text.
        if self.input_path is not None and new_text.strip() != str(self.input_path):
            self.input_path = None
            self.frames = None
            self._just_saved = False
        self._refresh()

    def on_format_change(self, e: ft.ControlEvent) -> None:
        self.fmt = e.control.value
        self._just_saved = False
        if self.frames is not None:
            self.frames = None
            self.progress = 0.0
            self.status_text = "Format değişti."
        self._refresh()

    def on_start(self, e: ft.ControlEvent) -> None:
        if self.is_running or self.is_saving:
            return
        # If we only have text (no resolved path), validate it now.
        if self.input_path is None and self.input_path_text.strip():
            candidate = Path(self.input_path_text.strip()).expanduser()
            if not candidate.exists():
                self.status_text = f"Klasör bulunamadı: {candidate}"
                self._refresh()
                return
            if not candidate.is_dir():
                self.status_text = f"Klasör değil: {candidate}"
                self._refresh()
                return
            self.input_path = candidate
        if self.input_path is None:
            self.status_text = "Önce giriş klasörünü seçin."
            self._refresh()
            return
        self.is_running = True
        self.frames = None
        self.progress = 0.0
        self._just_saved = False
        self.status_text = "Hazırlanıyor..."
        self._refresh()
        self.page.run_task(self._run_extraction)

    def on_save(self, e: ft.ControlEvent) -> None:
        if self.is_running or self.is_saving:
            return
        if not self.frames or self.input_path is None:
            return
        self._save_target = (
            Path.home() / "Downloads" / "extractor-photos" / self.input_path.name
        )
        self.is_saving = True
        self.status_text = str(self._save_target)
        self._refresh()
        self.page.run_task(self._run_save)

    # Background work --------------------------------------------------------
    async def _run_extraction(self) -> None:
        assert self.input_path is not None
        try:
            result = await self.service.extract_all(
                self.input_path,
                self.fmt,
                progress_cb=self._on_progress,
            )
            self._finish_extract(result)
        except Exception as exc:
            self.status_text = f"Hata: {exc}"
            self.is_running = False
            self._refresh()

    async def _on_progress(self, done: int, total: int, current: str) -> None:
        self.progress = done / total if total else 0.0
        self.status_text = f"İşleniyor ({done}/{total}): {current}"
        self._refresh()

    def _finish_extract(self, result: ExtractionResult) -> None:
        self.is_running = False
        self.progress = 1.0 if result.total else 0.0
        self.frames = result.frames
        if result.total == 0:
            self.status_text = "Klasörde video bulunamadı."
        else:
            extra = f" • {result.failed} hatalı" if result.failed else ""
            self.status_text = f"{result.succeeded} frame çıkarıldı{extra}."
        self._refresh()

    async def _run_save(self) -> None:
        assert self.frames is not None and self._save_target is not None
        try:
            result = await self.service.save_frames(self.frames, self._save_target)
            self._finish_save(result)
        except Exception as exc:
            self.status_text = f"Kaydetme hatası: {exc}"
            self.is_saving = False
            self._refresh()

    def _finish_save(self, result: SaveResult) -> None:
        self.is_saving = False
        self._just_saved = True
        self.status_text = f"{result.written} dosya kaydedildi: {result.target_dir}"
        self._refresh()
