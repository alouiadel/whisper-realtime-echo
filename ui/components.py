import flet as ft
from ui.theme import AppTheme

def create_info_card(title, value, icon):
    return ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=AppTheme.SECONDARY_COLOR),
                    ft.Text(title, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ]),
                ft.Text(value, size=16, color=ft.Colors.WHITE),
            ]),
            padding=10,
            border_radius=8,
        ),
        color=AppTheme.SURFACE_COLOR,
    )

def create_section_title(title):
    return ft.Text(
        title,
        size=18,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE,
    )

def create_section_container(content, margin_bottom=20):
    return ft.Container(
        content=content,
        margin=ft.margin.only(bottom=margin_bottom),
    ) 