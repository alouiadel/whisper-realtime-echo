import flet as ft
from ui.theme_lang import AppThemeLang


def configure_page(page: ft.Page):
    """Configure the main app page settings"""
    page.title = "Whisper Realtime Echo"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    page.window.center()
    page.window.width = 1000
    page.window.height = 900
    page.window.resizable = False
    page.window.maximizable = False
    page.bgcolor = AppThemeLang.BACKGROUND_COLOR


def toggle_theme(e):
    """Toggle between light and dark theme"""
    page = e.page

    is_dark_mode = e.control.data

    header_row = e.control.parent
    header_text = header_row.controls[0]

    if is_dark_mode:
        page.theme_mode = ft.ThemeMode.LIGHT
        e.control.icon = ft.icons.LIGHT_MODE
        e.control.icon_color = ft.colors.BLACK
        e.control.tooltip = "Switch to dark theme"
        header_text.color = ft.colors.BLACK
        page.bgcolor = AppThemeLang.LIGHT_BACKGROUND_COLOR
        AppThemeLang.BACKGROUND_COLOR = AppThemeLang.LIGHT_BACKGROUND_COLOR
        AppThemeLang.SURFACE_COLOR = AppThemeLang.LIGHT_SURFACE_COLOR
    else:
        page.theme_mode = ft.ThemeMode.DARK
        e.control.icon = ft.icons.DARK_MODE
        e.control.icon_color = ft.colors.WHITE
        e.control.tooltip = "Switch to light theme"
        header_text.color = ft.colors.WHITE
        page.bgcolor = AppThemeLang.DARK_BACKGROUND_COLOR
        AppThemeLang.BACKGROUND_COLOR = AppThemeLang.DARK_BACKGROUND_COLOR
        AppThemeLang.SURFACE_COLOR = AppThemeLang.DARK_SURFACE_COLOR

    e.control.data = not is_dark_mode
    page.update()


def create_header():
    """Create the app header with theme toggle"""
    return ft.Container(
        content=ft.Row(
            [
                ft.Text(
                    "Whisper Realtime Echo",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.IconButton(
                    icon=ft.icons.DARK_MODE,
                    icon_color=ft.colors.WHITE,
                    tooltip="Switch to light theme",
                    icon_size=24,
                    data=True,
                    on_click=toggle_theme,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        margin=ft.margin.only(bottom=20),
    )
