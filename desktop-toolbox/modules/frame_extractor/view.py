"""Pure UI for the Frame Extractor module. No business logic lives here."""

from __future__ import annotations

from typing import TYPE_CHECKING

import flet as ft

from .controller import Stage

if TYPE_CHECKING:
    from .controller import FrameExtractorController


CARD_WIDTH = 560


class FrameExtractorView(ft.View):
    def __init__(self, controller: "FrameExtractorController") -> None:
        super().__init__(
            route="/frame-extractor",
            padding=24,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
        )
        self.controller = controller

        # FilePicker for input — added to page.overlay in did_mount.
        # Save destination is hardcoded to ~/Downloads/photos/<input-name>/
        # so no save picker is needed.
        self.input_picker = ft.FilePicker(on_result=controller.on_input_picked)

        # Widgets the controller's refresh() needs to update
        self.status = ft.Text(
            controller.status_text,
            size=13,
            text_align=ft.TextAlign.CENTER,
        )
        self.progress_bar = ft.ProgressBar(value=0, width=CARD_WIDTH, visible=False)
        self.input_field = ft.TextField(
            value="",
            hint_text="Klasör yolunu yazın veya yapıştırın",
            expand=True,
            dense=True,
            on_change=controller.on_input_text_change,
        )
        self.browse_button = ft.IconButton(
            icon=ft.Icons.FOLDER_OPEN,
            tooltip="Klasör seç",
            on_click=lambda _: self.input_picker.get_directory_path(),
        )
        self.format_radio = ft.RadioGroup(
            value=controller.fmt,
            on_change=controller.on_format_change,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Radio(value="jpg", label="JPG"),
                    ft.Radio(value="png", label="PNG"),
                ],
            ),
        )
        self.action_button = ft.FilledButton(
            text="Başla",
            icon=ft.Icons.PLAY_ARROW,
            on_click=controller.on_start,
            disabled=True,
            height=44,
        )

        card = ft.Container(
            width=CARD_WIDTH,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=22,
                controls=[
                    ft.Text(
                        "Video Frame Extractor",
                        size=26,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Bir klasördeki tüm videolardan ilk kareyi çıkarır.",
                        size=13,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(height=1),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                        spacing=8,
                        controls=[
                            ft.Text(
                                "Giriş klasörü",
                                size=12,
                                weight=ft.FontWeight.W_500,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Row(
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[self.input_field, self.browse_button],
                            ),
                        ],
                    ),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Text(
                                "Format",
                                size=12,
                                weight=ft.FontWeight.W_500,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                            self.format_radio,
                        ],
                    ),
                    ft.Divider(height=1),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[self.action_button],
                    ),
                    self.progress_bar,
                    self.status,
                ],
            ),
        )

        self.controls = [
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=card,
            )
        ]

    def did_mount(self) -> None:
        self.page.overlay.append(self.input_picker)
        self.page.update()

    def will_unmount(self) -> None:
        if self.input_picker in self.page.overlay:
            self.page.overlay.remove(self.input_picker)

    def refresh(self) -> None:
        c = self.controller
        stage = c.stage

        self.status.value = c.status_text
        self.progress_bar.value = c.progress
        self.progress_bar.visible = stage is Stage.EXTRACTING
        if self.input_field.value != c.input_path_text:
            self.input_field.value = c.input_path_text

        if stage is Stage.IDLE:
            self.action_button.text = "Başla"
            self.action_button.icon = ft.Icons.PLAY_ARROW
            self.action_button.on_click = c.on_start
            self.action_button.disabled = not (c.input_path or c.input_path_text.strip())
        elif stage is Stage.EXTRACTING:
            self.action_button.text = "Yükleniyor..."
            self.action_button.icon = None
            self.action_button.on_click = None
            self.action_button.disabled = True
        elif stage is Stage.EXTRACTED:
            self.action_button.text = "Kaydet"
            self.action_button.icon = ft.Icons.SAVE
            self.action_button.on_click = c.on_save
            self.action_button.disabled = False
        elif stage is Stage.SAVING:
            self.action_button.text = "Kaydediliyor..."
            self.action_button.icon = None
            self.action_button.on_click = None
            self.action_button.disabled = True
        elif stage is Stage.SAVED:
            self.action_button.text = "Kaydedildi ✓"
            self.action_button.icon = ft.Icons.CHECK
            self.action_button.on_click = None
            self.action_button.disabled = True

        if self.page is not None:
            self.update()
