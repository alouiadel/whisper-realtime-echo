import flet as ft
from ui.theme import AppTheme

def configure_page(page: ft.Page):
    """Configure the main app page settings"""
    page.title = "Whisper Transcription App"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    page.window.center()
    page.window_width = 800
    page.window_height = 700
    page.bgcolor = AppTheme.BACKGROUND_COLOR

def create_header():
    """Create the app header"""
    return ft.Container(
        content=ft.Text(
            "Whisper Transcription App",
            size=30,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
        ),
        margin=ft.margin.only(bottom=20),
    ) 