"""Pure UI for the Frame Extractor module. No business logic lives here."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

if TYPE_CHECKING:
    from .controller import FrameExtractorController


class FrameExtractorView(ft.View):
    def __init__(self, controller: "FrameExtractorController") -> None:
        super().__init__(route="/frame-extractor", padding=24)
        self.controller = controller

        # FilePickers — must be added to page.overlay before use (we attach
        # them in did_mount). They report the chosen path via on_result.
        self.input_picker = ft.FilePicker(on_result=controller.on_input_picked)
        self.output_picker = ft.FilePicker(on_result=controller.on_output_picked)

        # Widgets the controller's refresh() needs to update
        self.status = ft.Text(controller.status_text, size=13)
        self.progress_bar = ft.ProgressBar(value=0, width=520)
        self.input_label = ft.Text(
            "(seçilmedi)", size=12, color=ft.Colors.ON_SURFACE_VARIANT
        )
        self.output_label = ft.Text(
            "(seçilmedi)", size=12, color=ft.Colors.ON_SURFACE_VARIANT
        )
        self.format_radio = ft.RadioGroup(
            value=controller.fmt,
            on_change=controller.on_format_change,
            content=ft.Row(
                [
                    ft.Radio(value="jpg", label="JPG"),
                    ft.Radio(value="png", label="PNG"),
                ]
            ),
        )
        self.start_button = ft.FilledButton(
            text="Çıkar",
            icon=ft.Icons.PLAY_ARROW,
            on_click=controller.on_start,
        )

        self.controls = [
            ft.Column(
                spacing=18,
                controls=[
                    ft.Text("Video Frame Extractor", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "Bir klasördeki tüm videolardan ilk kareyi çıkarır.",
                        size=13,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    ft.Divider(height=1),
                    self._row(
                        "Giriş klasörü",
                        ft.OutlinedButton(
                            text="Seç...",
                            icon=ft.Icons.FOLDER_OPEN,
                            on_click=lambda _: self.input_picker.get_directory_path(),
                        ),
                        self.input_label,
                    ),
                    self._row(
                        "Çıkış klasörü",
                        ft.OutlinedButton(
                            text="Seç...",
                            icon=ft.Icons.FOLDER,
                            on_click=lambda _: self.output_picker.get_directory_path(),
                        ),
                        self.output_label,
                    ),
                    ft.Row(
                        [ft.Text("Format:", width=140), self.format_radio],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Row([self.start_button]),
                    ft.Divider(height=1),
                    self.progress_bar,
                    self.status,
                ],
            )
        ]

    @staticmethod
    def _row(label: str, button: ft.Control, value: ft.Control) -> ft.Row:
        return ft.Row(
            [ft.Text(label, width=140), button, value],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def did_mount(self) -> None:
        # Attach pickers to the page overlay so they can open native dialogs.
        self.page.overlay.extend([self.input_picker, self.output_picker])
        self.page.update()

    def will_unmount(self) -> None:
        for picker in (self.input_picker, self.output_picker):
            if picker in self.page.overlay:
                self.page.overlay.remove(picker)

    def refresh(self) -> None:
        c = self.controller
        self.status.value = c.status_text
        self.progress_bar.value = c.progress
        self.input_label.value = str(c.input_path) if c.input_path else "(seçilmedi)"
        self.output_label.value = str(c.output_dir) if c.output_dir else "(seçilmedi)"
        self.start_button.disabled = c.is_running
        if self.page is not None:
            self.update()
