"""Reusable UI components for the application."""
import flet as ft
from ui.theme_lang import AppThemeLang

def create_info_card(title, value, icon):
    """Create an info card with title, value and icon.
    
    Args:
        title: Card title text
        value: Card value text
        icon: Icon to display
        
    Returns:
        Card component
    """
    return ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=AppThemeLang.SECONDARY_COLOR),
                    ft.Text(title, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ]),
                ft.Text(value, size=16, color=ft.Colors.WHITE),
            ]),
            padding=10,
            border_radius=8,
        ),
        color=AppThemeLang.SURFACE_COLOR,
    )

def create_section_title(title):
    """Create a section title with consistent styling.
    
    Args:
        title: Title text
        
    Returns:
        Text component
    """
    return ft.Text(
        title,
        size=18,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE,
    )

def create_section_container(content, margin_bottom=20):
    """Create a container for a section with consistent styling.
    
    Args:
        content: Container content
        margin_bottom: Bottom margin in pixels
        
    Returns:
        Container component
    """
    return ft.Container(
        content=content,
        margin=ft.margin.only(bottom=margin_bottom),
    ) 