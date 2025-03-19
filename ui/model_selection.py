"""Model selection UI components and logic."""
import flet as ft
from ui.theme_lang import AppThemeLang

class ModelSelector:
    """Manages UI and logic for Whisper model selection."""
    
    def __init__(self, page, on_model_change):
        """Initialize model selector with UI components.
        
        Args:
            page: Parent flet page
            on_model_change: Callback when model selection changes
        """
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
            focused_border_color=AppThemeLang.SECONDARY_COLOR,
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
            value="tiny",
            width=200,
            border_color=ft.Colors.GREY_700,
            focused_border_color=AppThemeLang.SECONDARY_COLOR,
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
            focused_border_color=AppThemeLang.SECONDARY_COLOR,
            on_change=lambda _: self.on_model_change(),
        )
        
        language_options = [
            ft.dropdown.Option("auto", "Auto-detect"),
        ]
        
        language_options.extend([
            ft.dropdown.Option(code, name)
            for code, name in sorted(
                [(k, v) for k, v in AppThemeLang.LANGUAGE_CODES.items() if k != "auto"],
                key=lambda x: x[1]
            )
        ])
        
        self.language_dropdown = ft.Dropdown(
            label="Language",
            options=language_options,
            value="en",
            width=200,
            border_color=ft.Colors.GREY_700,
            focused_border_color=AppThemeLang.SECONDARY_COLOR,
            on_change=lambda _: self.on_model_change(),
            disabled=True,
        )
        
        self.warning_banner = ft.Banner(
            bgcolor=AppThemeLang.SURFACE_COLOR,
            leading=ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=AppThemeLang.WARNING_COLOR, size=40),
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
        """Hide the warning banner."""
        self.warning_banner.visible = False
        self.page.update()
    
    def _switch_to_multilingual(self):
        """Switch model type to multilingual and hide banner."""
        self.model_type.value = "multilingual"
        self.warning_banner.visible = False
        self.on_model_change()
        self.page.update()
    
    def _on_model_type_change(self, e):
        """Handle model type change event."""
        if self.model_type.value == "english_only" and self.model_size.value in ["large", "turbo"]:
            self.warning_banner.visible = True
            
        if self.model_type.value == "english_only":
            self.language_dropdown.value = "en"
            self.language_dropdown.disabled = True
        else:
            self.language_dropdown.value = "auto"
            self.language_dropdown.disabled = False
            
        self.on_model_change()
        self.page.update()
    
    def _on_model_size_change(self, e):
        """Handle model size change event."""
        if self.model_type.value == "english_only" and self.model_size.value in ["large", "turbo"]:
            self.warning_banner.visible = True
        self.on_model_change()
        self.page.update()
    
    def get_model_name(self):
        """Get the formatted model name based on current selections.
        
        Returns:
            String model name or None if invalid combination
        """
        if self.model_type.value == "english_only":
            if self.model_size.value in ["tiny", "base", "small", "medium"]:
                return f"{self.model_size.value}.en"
            else:
                return None
        else:
            return self.model_size.value
    
    def is_valid_model(self):
        """Check if current model selection is valid.
        
        Returns:
            Boolean indicating if selection is valid
        """
        return not (self.model_type.value == "english_only" and self.model_size.value in ["large", "turbo"])
    
    def get_memory_info(self):
        """Get estimated VRAM usage for current model.
        
        Returns:
            String representation of VRAM usage
        """
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
        """Get estimated relative speed for current model.
        
        Returns:
            String representation of relative speed
        """
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