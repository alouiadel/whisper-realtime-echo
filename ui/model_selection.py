import flet as ft
from ui.theme import AppTheme

class ModelSelector:
    def __init__(self, page, on_model_change):
        self.page = page
        self.on_model_change = on_model_change
        
        self.model_type = ft.Dropdown(
            label="Model Type",
            options=[
                ft.dropdown.Option("english_only", "English-only"),
                ft.dropdown.Option("multilingual", "Multilingual"),
            ],
            value="english_only",
            width=200,
            border_color=ft.Colors.GREY_700,
            focused_border_color=AppTheme.SECONDARY_COLOR,
            on_change=self._on_model_type_change,
        )
        
        self.model_size = ft.Dropdown(
            label="Model Size",
            options=[
                ft.dropdown.Option("tiny", "Tiny"),
                ft.dropdown.Option("base", "Base"),
                ft.dropdown.Option("small", "Small"),
                ft.dropdown.Option("medium", "Medium"),
                ft.dropdown.Option("large", "Large"),
                ft.dropdown.Option("turbo", "Turbo"),
            ],
            value="base",
            width=200,
            border_color=ft.Colors.GREY_700,
            focused_border_color=AppTheme.SECONDARY_COLOR,
            on_change=self._on_model_size_change,
        )
        
        self.device_dropdown = ft.Dropdown(
            label="Device",
            options=[
                ft.dropdown.Option("cpu", "CPU"),
                ft.dropdown.Option("cuda", "CUDA (GPU)"),
            ],
            value="cuda",
            width=200,
            border_color=ft.Colors.GREY_700,
            focused_border_color=AppTheme.SECONDARY_COLOR,
            on_change=lambda _: self.on_model_change(),
        )
        
        self.warning_banner = ft.Banner(
            bgcolor=AppTheme.SURFACE_COLOR,
            leading=ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=AppTheme.WARNING_COLOR, size=40),
            content=ft.Text(
                "Large and Turbo models are only available in multilingual versions",
                color=ft.Colors.WHITE,
            ),
            actions=[
                ft.TextButton("Switch to Multilingual", on_click=lambda e: self._switch_to_multilingual()),
                ft.TextButton("Dismiss", on_click=lambda e: self._close_banner()),
            ],
            visible=False,
        )
        
        self.page.banner = self.warning_banner
    
    def _close_banner(self):
        self.warning_banner.visible = False
        self.page.update()
    
    def _switch_to_multilingual(self):
        self.model_type.value = "multilingual"
        self.warning_banner.visible = False
        self.on_model_change()
        self.page.update()
    
    def _on_model_type_change(self, e):
        if self.model_type.value == "english_only" and self.model_size.value in ["large", "turbo"]:
            self.warning_banner.visible = True
        self.on_model_change()
        self.page.update()
    
    def _on_model_size_change(self, e):
        if self.model_type.value == "english_only" and self.model_size.value in ["large", "turbo"]:
            self.warning_banner.visible = True
        self.on_model_change()
        self.page.update()
    
    def get_model_name(self):
        if self.model_type.value == "english_only":
            if self.model_size.value in ["tiny", "base", "small", "medium"]:
                return f"{self.model_size.value}.en"
            else:
                return None
        else:
            return self.model_size.value
    
    def is_valid_model(self):
        return not (self.model_type.value == "english_only" and self.model_size.value in ["large", "turbo"])
    
    def get_memory_info(self):
        model_name = self.model_size.value
        memory_map = {
            "tiny": "~1 GB",
            "base": "~1 GB",
            "small": "~2 GB",
            "medium": "~5 GB",
            "large": "~10 GB",
            "turbo": "~6 GB"
        }
        return memory_map.get(model_name, "Unknown")
    
    def get_speed_info(self):
        model_name = self.model_size.value
        speed_map = {
            "tiny": "~10x",
            "base": "~7x",
            "small": "~4x",
            "medium": "~2x",
            "large": "1x",
            "turbo": "~8x"
        }
        return speed_map.get(model_name, "Unknown") 